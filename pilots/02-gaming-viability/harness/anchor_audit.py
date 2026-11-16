#!/usr/bin/env python3
"""Replay all fixed-history arms, target math, attempts, concurrency and budget."""
from decimal import Decimal as D
import json
import os
from pathlib import Path
import sys

import scout_anchor as f

g=f.g


def audit(root):
    root=Path(root);plan=f.verify_plan(root);path=root/'experiment';mp=path/g.old.slug(f.CANDIDATE)
    manifest=g.old.load(path/'manifest.json');assert manifest['status']=='finished'
    assert manifest['plan_sha256']==g.s.sha((root/'plan.json').read_bytes())
    assert manifest['selection']==plan['selection'] and set(manifest['jobs'])==set(f.IDS)
    assert manifest['maximum_logical_calls']==44 and manifest['concurrency_limit']==6
    assert g.old.load(mp/'frozen-history.json')=={'messages':plan['history'],'proof':plan['history_proof']}
    assert g.old.load(mp/'frozen_config.json')==plan['config'] and g.old.load(mp/'prompts.json')==plan['prompts']
    for name,digest in plan['sources_sha256'].items():
        snap=g.old.load(root/('source_'+name.replace('/','__')+'.json'))
        assert snap['path']==name and g.s.sha(snap['text'].encode())==digest
    raw=g.old.rows(mp/'raw.jsonl') if (mp/'raw.jsonl').exists() else []
    req=g.old.rows(mp/'requests.jsonl') if (mp/'requests.jsonl').exists() else []
    assert len(raw)==len(req)==manifest['recorded_attempts']==manifest['physical_attempts']
    requests={r['reservation']['reservation_id']:(f.CANDIDATE,r) for r in req}
    responses={r['reservation']['reservation_id']:(f.CANDIDATE,r) for r in raw}
    assert len(requests)==len(req) and set(requests)==set(responses)
    final={r['id']:r for r in raw};violations=[];selection=plan['selection']
    assert len(final)==manifest['logical_calls_dispatched']<=44
    if selection['status']!='selected':assert not raw and all(s['status']=='blocked_skip' for s in manifest['jobs'].values())
    for logical in f.IDS:
        meta=f.metadata(logical);state=manifest['jobs'][logical]
        assert state['parent']==meta['parent'] and state['status']!='queued'
        if state['status'].startswith('blocked'):assert logical not in final and state['failure']
        if state['status']=='complete':assert final[logical]['finish_reason']=='stop'
        attempts=sorted([r for r in raw if r['id']==logical],key=lambda r:r['attempt'])
        for index,r in enumerate(attempts,1):
            rid=r['reservation']['reservation_id'];request=requests[rid][1]
            assert all(r[k]==v for k,v in request.items())
            assert r['attempt']==index<=3
            if index>1:assert attempts[index-2]['http_status'] in g.old.TRANSIENT
            assert r['parent']==meta['parent'] and r['variable']==meta['variable']
            if meta['parent']=='initial':history=plan['history']
            else:
                parent=final[meta['parent']];assert parent['finish_reason']=='stop'
                history=parent['request']['messages']+[g.s.message('assistant',parent['text'])]
            assert r['request']['messages']==g.s.branch(history,plan['prompts'][meta['question_key']])
            expected={'model':selection['request_model'],'messages':r['request']['messages'],**selection['parameters'],
                      'stream':False,'usage':{'include':True},'provider':{'only':[selection['endpoint_tag']],'allow_fallbacks':False,'require_parameters':True,
                      'max_price':{k:float(D(v)*1000000) for k,v in selection['price_ceilings_usd_per_token'].items()}}}
            assert r['request']==expected and expected['max_tokens']==4096
            assert g.s.remove_hidden(r['response'])==r['response']
            if isinstance(r['response'],dict):assert json.loads(r['raw_response_body'])==r['response']
            if isinstance(r['text'],str):
                assert r['response']['choices'][0]['message']['content']==r['text']
                assert r['parsed']==g.parse_probability(r['text'],r['variable'],r['finish_reason'],logical.startswith('control_'))
                assert r['cue_leakage']==(g.cue_leakage(r['text']) if r['variable']=='A' else None)
                reasons=[]
                if r['response'].get('provider')!=selection['provider_name'] or r['response'].get('model') not in selection['allowed_returned_models']:reasons.append('provider/model')
                tokens=(r['usage'] or {}).get('completion_tokens_details',{}).get('reasoning_tokens')
                if r['hidden_trace_present'] or (tokens is not None and tokens>0):reasons.append('reasoning')
                if reasons:
                    violations.append({'id':logical,'reasons':reasons});assert state['status']!='complete'
            if r['usage']:
                assert r['usage']['prompt_tokens']<=r['reservation']['input_token_bound'] and r['usage']['completion_tokens']<=4096
    assert g.old.load(mp/'diagnostic_metrics.json')==f.measure(list(final.values()))
    if (mp/'manual_inspection.json').exists():
        annotations=g.old.load(mp/'manual_inspection.json')['responses']
        assert f.validate_annotations(list(final.values()),annotations,manifest['jobs'])
        assert g.old.load(mp/'manual_metrics.json')==f.measure(list(final.values()),annotations)
    all_rows=raw
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
        parent=f.metadata(record['id'])['parent']
        if parent!='initial':
            parent_rid=final[parent]['reservation']['reservation_id']
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
            assert D(reservation['exposure_after_usd'])==exposure+cap<=D('1')
        else:
            rid=event['reservation_id'];cap,payload=active.pop(rid)
            charge,kind=g.AtomicBudget.charge(responses[rid][1],payload,cap)
            assert D(event['charge_upper_usd'])==charge and event['kind']==kind
            assert D(event['released_headroom_usd'])==cap-charge
            spent+=charge
        exposure=spent+sum((x[0] for x in active.values()),D(0));peak=max(peak,exposure)
        assert exposure<=D('1')
        if event['event']=='settle':assert D(event['exposure_after_usd'])==exposure
    assert not active and counter==manifest['reservations']==len(requests)
    assert maximum==manifest['maximum_in_flight']<=manifest['concurrency_limit']==6
    assert len(requests)==manifest['physical_attempts']==manifest['recorded_attempts']
    assert manifest['logical_calls_dispatched']==len(final)<=44
    assert manifest['accounting']==g.old.base.accounting(all_rows)
    assert D(manifest['conservative_settled_upper_usd'])==spent and D(manifest['peak_spent_plus_outstanding_usd'])==peak
    assert D(manifest['accounting']['reported_cost_subtotal_usd'])<=spent<=D('1')

    key=os.environ.get('OPENROUTER_API_KEY','').encode()
    if key:assert all(key not in p.read_bytes() for p in root.rglob('*') if p.is_file())
    return {'status':'passed','time':g.s.utc(),'logical_calls':len(final),'attempts':len(req),'maximum_concurrent_requests':maximum,
            'reported_cost_usd':manifest['accounting']['reported_cost_subtotal_usd'],'conservative_settled_upper_usd':str(spent),
            'peak_spent_plus_outstanding_usd':str(peak),'configuration_violations':violations,'previous_artifacts_unchanged':True,
            'checks':['exact44-ID scope and reviewed messages','frozen original/implicit initial history hashes','same pinned Scout endpoint/settings',
                      'all-target exact math and unclipped signed/normalized movement','isolated arm and sibling histories/dependency order',
                      'unchanged parser diagnostic replay; no historical scoring data','all attempts, six-request global concurrency and atomic$1 ledger',
                      'prior source/artifact preservation; source snapshots','manual quote hashes/category validation/metric replay when present','credential absence when configured']}


if __name__=='__main__':
    root=Path(sys.argv[1]);result=audit(root)
    result['artifact_sha256']={str(p.relative_to(root)):g.s.sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='audit.json'}
    (root/'audit.json').write_text(g.s.dump(result)+'\n');print(g.s.dump({k:v for k,v in result.items() if k!='artifact_sha256'}))
