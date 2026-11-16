import sys
from decimal import Decimal as D
sys.path.insert(0,'pilots/02-gaming-viability/harness');import robustness as f

g=f.g;root=f.ROOT;plan=f.verify_plan(root);path=root/'experiment';manifest=g.old.load(path/'manifest.json')
requests=[];raw=[];states={c['case']:{} for c in plan['cases']};events=g.old.rows(path/'scheduler.jsonl');last={}
for e in events:
    if 'case' in e and 'id' in e:last[e['case'],e['id']]=e
for case in plan['cases']:
    p=path/g.old.slug(case['candidate'])/case['case'];rows=g.old.rows(p/'raw.jsonl') if (p/'raw.jsonl').exists() else [];raw+=rows
    req=g.old.rows(p/'requests.jsonl') if (p/'requests.jsonl').exists() else [];requests+=req
    byid={r['id']:r for r in rows}
    for job in [j for j in plan['jobs'] if j['case']==case['case']]:
        r=byid.get(job['id']);e=last.get((case['case'],job['id']),{})
        if r:
            status=e.get('status') if e.get('event')=='task_finished' else 'complete' if r['finish_reason']=='stop' else 'incomplete'
            reason=e.get('failure') or (None if status=='complete' else 'Recorded response incomplete/failed')
        else:
            status=e.get('status') if e.get('event')=='blocked' else 'canceled_user_scope'
            reason=e.get('failure') or 'Coverage canceled by user; no request dispatched'
        states[case['case']][job['id']]={'status':status,'parent':job['parent'],'stage':job['stage'],'failure':reason}
    (p/'diagnostic_metrics.json').write_text(g.s.dump(f.metrics(plan,case['case'],rows))+'\n')
    lines=['# '+case['candidate']+' / '+case['case'], '','Replication history' if case['stage']==0 else 'CANCELED partial coverage; excluded from primary analysis','']
    for job in [j for j in plan['jobs'] if j['case']==case['case']]:
        r=byid.get(job['id']);lines+=['## '+job['base_id'],'',r['text'] if r and r.get('text') else '[No response: '+states[case['case']][job['id']]['status']+']','']
    (p/'RESPONSES.md').write_text('\n'.join(lines))
assert len(requests)==len(raw)
ledger=g.old.rows(path/'ledger.jsonl');active={};spent=D(0);peak=D(0)
for e in ledger:
    if e['event']=='reserve':active[e['reservation']['reservation_id']]=D(e['reservation']['reserve_usd'])
    else:spent+=D(e['charge_upper_usd']);active.pop(e['reservation_id'])
    peak=max(peak,spent+sum(active.values(),D(0)))
assert not active
execution=g.old.rows(path/'execution.jsonl');assert sum(1 if e['event']=='dispatch' else -1 for e in execution)==0
manifest.update(status='finished',ended=max(r['ended'] for r in raw),interrupted_for_user_scope_change=True,
  jobs=states,logical_calls_dispatched=len({(r['request']['model'],r['id']) for r in raw}),physical_attempts=len(raw),recorded_attempts=len(raw),reservations=len(requests),
  maximum_in_flight=max(e['in_flight'] for e in execution),accounting=g.old.base.accounting(raw),conservative_settled_upper_usd=str(spent),peak_spent_plus_outstanding_usd=str(peak),budget_halted=False)
(path/'manifest.json').write_text(g.s.dump(manifest)+'\n')
(root/'scope-recovery.json').write_text(g.s.dump({'reason':'User canceled Experiment2 after replication complete and coverage already dispatched. Scheduler interrupted; only already dispatched requests finished. No lost raw attempt, no regenerated call.',
 'replication_calls':sum(case['stage']==0 for r in raw for case in plan['cases'] if case['case'] in r['id']),
 'statuses_reconstructed_from':'Durable scheduler, requests/raw, execution and budget ledgers; only missing coverage nodes marked canceled. Original frozen plan retained.',
 'request_count':len(requests),'raw_count':len(raw),'original_conservative_settled_usd':str(spent)})+'\n')
print('Original run finalized:',len(raw),manifest['accounting'],'incomplete',[(r['id'],r['finish_reason'],r['http_status']) for r in raw if r['finish_reason']!='stop'])
