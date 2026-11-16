#!/usr/bin/env python3
"""Offline replay of GAME-01 math, graph, concurrency, reservations and artifacts."""
from decimal import Decimal as D
import json
import os
from pathlib import Path
import sys

import gaming as g


def audit(root):
    root=Path(root);plan=g.verify_plan(root);path=root/'experiment'
    manifest=g.old.load(path/'manifest.json');assert manifest['status']=='finished'
    assert manifest['plan_sha256']==g.s.sha((root/'plan.json').read_bytes())
    assert plan['references']==g.references()
    for name,digest in plan['sources_sha256'].items():
        snap=g.old.load(root/('source_'+name.replace('/','__')+'.json'))
        assert snap['path']==name and g.s.sha(snap['text'].encode())==digest
    requests={};responses={};all_rows=[];finals={};violations=[]
    candidates={c['candidate']:c for c in manifest['candidates']}
    assert set(candidates)==set(g.MODELS)
    for selection in plan['choices']:
        candidate=selection['candidate'];result=candidates[candidate]
        assert result['selection']==selection and set(result['jobs'])==set(g.IDS)
        for logical,state in result['jobs'].items():
            assert state['parent']==g.parent_id(logical)
            assert state['status']!='queued'
        if selection['status']!='selected':
            assert all(x['status']=='blocked_skip' for x in result['jobs'].values());continue
        mp=path/g.old.slug(candidate)
        model_manifest=g.old.load(mp/'manifest.json')
        assert model_manifest==result
        assert g.old.load(mp/'prompts.json')==plan['prompts']
        cfg=g.old.load(mp/'frozen_config.json')
        assert cfg==result['config']
        for k,v in plan['config'].items():assert cfg[k]==v
        req=g.old.rows(mp/'requests.jsonl') if (mp/'requests.jsonl').exists() else []
        raw=g.old.rows(mp/'raw.jsonl') if (mp/'raw.jsonl').exists() else []
        by_id={r['id']:r for r in raw};finals[candidate]=by_id
        assert len(by_id)==result['logical_calls_dispatched']<=18
        if result['status']=='complete':assert set(by_id)==set(g.IDS)
        assert len(req)==len(raw)==result['attempts'], 'Missing raw response; see held reservation/task failure'
        per_id={}
        for r in req:
            rid=r['reservation']['reservation_id'];assert rid not in requests
            requests[rid]=(candidate,r)
        for r in raw:
            rid=r['reservation']['reservation_id'];assert rid not in responses
            responses[rid]=(candidate,r)
            assert candidate==requests[rid][0]
            assert all(r[k]==v for k,v in requests[rid][1].items())
            logical=r['id'];assert logical in g.IDS
            per_id.setdefault(logical,[]).append(r)
        for logical,attempts in per_id.items():
            attempts.sort(key=lambda x:x['attempt'])
            for index,r in enumerate(attempts,1):
                assert r['attempt']==index<=3
                if index>1:assert attempts[index-2]['http_status'] in g.old.TRANSIENT
                parent=g.parent_id(logical)
                question=plan['prompts']['initial' if logical=='initial' else logical if logical.startswith('control_') else logical[:-2] if logical.endswith('_A') else logical[-1]]
                if parent is None:history=[g.s.message('system',plan['prompts']['system'])]
                else:
                    pr=by_id[parent];assert pr['finish_reason']=='stop' and isinstance(pr['text'],str)
                    history=pr['request']['messages']+[g.s.message('assistant',pr['text'])]
                assert r['parent']==parent and r['request']['messages']==g.s.branch(history,question)
                payload=r['request']
                expected={'model':selection['request_model'],'messages':payload['messages'],**selection['parameters'],
                          'stream':False,'usage':{'include':True},'provider':{'only':[selection['endpoint_tag']],
                          'allow_fallbacks':False,'require_parameters':True,'max_price':{k:float(D(v)*1000000) for k,v in selection['price_ceilings_usd_per_token'].items()}}}
                assert payload==expected and payload['max_tokens']==4096
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
                        violations.append({'candidate':candidate,'id':logical,'reasons':reasons});assert result['status']!='complete'
                if r['usage']:
                    assert r['usage']['prompt_tokens']<=r['reservation']['input_token_bound']
                    assert r['usage']['completion_tokens']<=4096
        for logical,state in result['jobs'].items():
            if state['status']=='complete':assert by_id[logical]['finish_reason']=='stop'
            if state['status'].startswith('blocked'):
                assert logical not in by_id and state['failure']
        assert g.old.load(mp/'derived.json')==g.analyze(list(by_id.values()))
        assert result['accounting']==g.old.base.accounting(raw)
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
        parent=g.parent_id(record['id'])
        if parent is not None:
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
    assert manifest['logical_calls_dispatched']==sum(len(v) for v in finals.values())<=54
    assert manifest['accounting']==g.old.base.accounting(all_rows)
    assert D(manifest['conservative_settled_upper_usd'])==spent and D(manifest['peak_spent_plus_outstanding_usd'])==peak
    assert D(manifest['accounting']['reported_cost_subtotal_usd'])<=spent<=D('1')
    key=os.environ.get('OPENROUTER_API_KEY','').encode()
    if key:assert all(key not in p.read_bytes() for p in root.rglob('*') if p.is_file())
    return {'status':'passed','time':g.s.utc(),'logical_calls':manifest['logical_calls_dispatched'],'attempts':len(requests),
            'maximum_concurrent_requests':maximum,'reported_cost_usd':manifest['accounting']['reported_cost_subtotal_usd'],
            'conservative_settled_upper_usd':str(spent),'peak_spent_plus_outstanding_usd':str(peak),
            'configuration_violations':violations,'previous_artifacts_unchanged':True,
            'checks':['exact reviewed game prompts','exact Bayesian/negative-slope math references','isolated parent/sibling histories and dependency order',
                      'stable unique logical IDs and all attempts','global six-request concurrency','atomic $1 spent-plus-outstanding replay',
                      'same pinned providers/settings except4096 cap','game-only score replay and raw visible text fidelity','source snapshots and prior artifact preservation','secret absence when configured']}


if __name__=='__main__':
    result=audit(sys.argv[1]);root=Path(sys.argv[1])
    result['artifact_sha256']={str(p.relative_to(root)):g.s.sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='audit.json'}
    (root/'audit.json').write_text(g.s.dump(result)+'\n');print(g.s.dump({k:v for k,v in result.items() if k!='artifact_sha256'}))
