#!/usr/bin/env python3
"""Offline audit of all fresh histories, seeds, branches and combined$2 ledger."""
from decimal import Decimal as D
import json
import os
from pathlib import Path
import sys
import robustness as f

g=f.g


def audit(root):
    root=Path(root);plan=f.verify_plan(root);path=root/'experiment';manifest=g.old.load(path/'manifest.json')
    assert manifest['status']=='finished' and manifest['maximum_logical_calls']==420
    assert manifest['plan_sha256']==g.s.sha((root/'plan.json').read_bytes())
    assert len(plan['cases'])==20 and len({c['seed'] for c in plan['cases']})==20
    assert set(manifest['jobs'])=={c['case'] for c in plan['cases']}
    for name,digest in plan['sources_sha256'].items():
        snap=g.old.load(root/('source_'+name.replace('/','__')+'.json'));assert snap['path']==name and g.s.sha(snap['text'].encode())==digest
    lookup={(j['candidate'],j['id']):j for j in plan['jobs']};requests={};responses={};all_rows=[];finals={};violations=[]
    for case in plan['cases']:
        candidate=case['candidate'];cid=case['case'];selection=f.selection_for(plan,case);mp=path/g.old.slug(candidate)/cid;states=manifest['jobs'][cid]
        assert g.old.load(mp/'selection.json')==selection and g.old.load(mp/'case.json')==case
        assert g.old.load(mp/'frozen_config.json')['seed']==case['seed']
        assert set(states)=={j['id'] for j in plan['jobs'] if j['case']==cid}
        raw=g.old.rows(mp/'raw.jsonl') if (mp/'raw.jsonl').exists() else [];req=g.old.rows(mp/'requests.jsonl') if (mp/'requests.jsonl').exists() else []
        assert len(raw)==len(req);byid={r['id']:r for r in raw};finals.setdefault(candidate,{}).update(byid)
        if selection['status']!='selected':assert not raw and all(s['status']=='blocked_skip' for s in states.values())
        for logical,state in states.items():
            job=lookup[candidate,logical];assert state['parent']==job['parent'] and state['status']!='queued'
            if state['status'].startswith('blocked'):assert logical not in byid and state['failure']
            if state['status']=='complete':assert byid[logical]['finish_reason']=='stop'
        for r in req:
            rid=r['reservation']['reservation_id'];assert rid not in requests;requests[rid]=(candidate,r)
        for r in raw:
            rid=r['reservation']['reservation_id'];assert rid not in responses;responses[rid]=(candidate,r)
            assert requests[rid][0]==candidate and all(r[k]==v for k,v in requests[rid][1].items())
        for logical in byid:
            job=lookup[candidate,logical];attempts=sorted([r for r in raw if r['id']==logical],key=lambda r:r['attempt'])
            for index,r in enumerate(attempts,1):
                assert r['attempt']==index<=3
                if index>1:assert attempts[index-2]['http_status'] in g.old.TRANSIENT
                if job['parent'] is None:history=[g.s.message('system',plan['prompts']['system'])]
                else:
                    parent=byid[job['parent']];assert parent['finish_reason']=='stop'
                    history=parent['request']['messages']+[g.s.message('assistant',parent['text'])]
                assert r['parent']==job['parent'] and r['request']['messages']==g.s.branch(history,plan['prompts'][job['question_key']])
                expected={'model':selection['request_model'],'messages':r['request']['messages'],**selection['parameters'],'stream':False,'usage':{'include':True},
                  'provider':{'only':[selection['endpoint_tag']],'allow_fallbacks':False,'require_parameters':True,'max_price':{k:float(D(v)*1000000) for k,v in selection['price_ceilings_usd_per_token'].items()}}}
                assert expected==r['request'] and expected['max_tokens']==4096
                if 'seed' in expected:assert expected['seed']==case['seed']
                assert g.s.remove_hidden(r['response'])==r['response']
                if isinstance(r['response'],dict):assert json.loads(r['raw_response_body'])==r['response']
                if isinstance(r['text'],str):
                    assert r['text']==r['response']['choices'][0]['message']['content']
                    assert r['parsed']==g.parse_probability(r['text'],job['variable'],r['finish_reason'],job['condition']=='control')
                    reasons=[]
                    if r['response'].get('provider')!=selection['provider_name'] or r['response'].get('model') not in selection['allowed_returned_models']:reasons.append('provider/model')
                    tokens=(r['usage'] or {}).get('completion_tokens_details',{}).get('reasoning_tokens')
                    if r['hidden_trace_present'] or (tokens is not None and tokens>0):reasons.append('reasoning')
                    if reasons:violations.append({'case':cid,'id':logical,'reasons':reasons});assert states[logical]['status']!='complete'
                if r['usage']:assert r['usage']['completion_tokens']<=4096 and r['usage']['prompt_tokens']<=r['reservation']['input_token_bound']
        assert g.old.load(mp/'diagnostic_metrics.json')==f.metrics(plan,cid,list(byid.values()))
        if (mp/'observations.json').exists():
            items=g.old.load(mp/'observations.json')['responses'];assert set(items)==set(states)
            for logical,item in items.items():
                r=byid.get(logical);assert item['status']==states[logical]['status'] and item['visible_quote']==(r['text'] if r else None)
                assert item['record_sha256']==(g.s.sha(g.s.dump(r).encode()) if r else None)
                for k in ('point_probability','operational_A'):
                    if item[k] is not None:assert r and r['finish_reason']=='stop' and 0<=f.F(item[k])<=1 and item[k+'_evidence'] in r['text']
            assert g.old.load(mp/'coded_metrics.json')==f.metrics(plan,cid,list(byid.values()),items)
        all_rows.extend(raw)
    execution=g.old.rows(path/'execution.jsonl') if (path/'execution.jsonl').exists() else []
    active=set();dispatch={};complete={};maximum=0
    for seq,event in enumerate(execution,1):
        assert event['sequence']==seq
        rid=event['reservation_id'];candidate,record=requests[rid]
        assert event['candidate']==candidate and event['id']==record['id'] and event['attempt']==record['attempt']
        if event['event']=='dispatch':
            assert rid not in active and rid not in dispatch
            active.add(rid);dispatch[rid]=event
        else:
            assert rid in active;active.remove(rid);complete[rid]=event
        maximum=max(maximum,len(active));assert event['in_flight']==len(active)<=6
    assert not active and set(dispatch)==set(complete)==set(requests)==set(responses)
    for rid,(candidate,record) in requests.items():
        parent=lookup[candidate,record['id']]['parent']
        if parent not in (None,'initial'):
            parent_rid=finals[candidate][parent]['reservation']['reservation_id']
            assert complete[parent_rid]['sequence']<dispatch[rid]['sequence'], 'Dependency dispatched before parent completed'
    ledger=g.old.rows(path/'ledger.jsonl') if (path/'ledger.jsonl').exists() else []
    active={};spent=D(0);peak=D(0);counter=0
    for event in ledger:
        if event['event']=='reserve':
            reservation=event['reservation'];rid=reservation['reservation_id'];counter+=1;assert rid==counter
            candidate,record=requests[rid];payload=record['request']
            assert event['context']=={'candidate':candidate,'id':record['id']}
            assert event['request_sha256']==g.s.sha(g.s.dump(payload).encode())
            bound=g.AtomicBudget.bound(payload,plan['config']);cap=D(bound['reserve_usd'])
            assert reservation['input_token_bound']==bound['input_token_bound'] and D(reservation['reserve_usd'])==cap
            exposure=spent+sum((x[0] for x in active.values()),D(0))
            assert D(reservation['exposure_before_usd'])==exposure
            active[rid]=(cap,payload)
            assert D(reservation['exposure_after_usd'])==exposure+cap<=D('2')
        else:
            rid=event['reservation_id'];cap,payload=active.pop(rid)
            charge,kind=g.AtomicBudget.charge(responses[rid][1],payload,cap)
            assert D(event['charge_upper_usd'])==charge and event['kind']==kind
            assert D(event['released_headroom_usd'])==cap-charge
            spent+=charge
        exposure=spent+sum((x[0] for x in active.values()),D(0));peak=max(peak,exposure)
        assert exposure<=D('2')
        if event['event']=='settle':assert D(event['exposure_after_usd'])==exposure
    assert not active and counter==manifest['reservations']==len(requests)
    assert maximum==manifest['maximum_in_flight']<=manifest['concurrency_limit']==6
    assert len(requests)==manifest['physical_attempts']==manifest['recorded_attempts']
    assert manifest['logical_calls_dispatched']==sum(len(v) for v in finals.values())<=420
    assert manifest['accounting']==g.old.base.accounting(all_rows)
    assert D(manifest['conservative_settled_upper_usd'])==spent and D(manifest['peak_spent_plus_outstanding_usd'])==peak
    assert D(manifest['accounting']['reported_cost_subtotal_usd'])<=spent<=D('2')

    # A stage barrier drains every earlier stage before later dispatch, globally.
    stages={rid:lookup[c,r['id']]['stage'] for rid,(c,r) in requests.items()}
    for stage in sorted(set(stages.values())):
        earlier=[complete[rid]['sequence'] for rid in requests if stages[rid]<stage]
        later=[dispatch[rid]['sequence'] for rid in requests if stages[rid]==stage]
        if earlier and later:assert max(earlier)<min(later)

    key=os.environ.get('OPENROUTER_API_KEY','').encode()
    if key:assert all(key not in p.read_bytes() for p in root.rglob('*') if p.is_file())
    return {'status':'passed','time':g.s.utc(),'logical_calls':manifest['logical_calls_dispatched'],'attempts':len(requests),
      'maximum_concurrent_requests':maximum,'reported_cost_usd':manifest['accounting']['reported_cost_subtotal_usd'],
      'conservative_settled_upper_usd':str(spent),'peak_spent_plus_outstanding_usd':str(peak),'configuration_violations':violations,
      'all_previous_tracked_files_unchanged':True,'checks':['20 fresh initial requests with distinct recorded seeds','all420 planned nodes retained;no correctness/susceptibility selection',
      'own-history baseline and isolated WU/BC/D/control branches','exact frozen prompts and same pinned settings','replication before coverage,global6 concurrency',
      'one combined atomic$2 ledger with all retries/errors','unchanged probability parser and exact math;separate quoted coding','all tracked files including any manuscript unchanged']}


if __name__=='__main__':
    root=Path(sys.argv[1]);result=audit(root)
    result['artifact_sha256']={str(p.relative_to(root)):g.s.sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='audit.json'}
    (root/'audit.json').write_text(g.s.dump(result)+'\n');print(g.s.dump({k:v for k,v in result.items() if k!='artifact_sha256'}))
