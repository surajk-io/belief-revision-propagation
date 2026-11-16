#!/usr/bin/env python3
"""Scope correction: directed controls on15 completed replication initials only."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
from decimal import Decimal as D
import os
from pathlib import Path
import threading

import robustness as f

g=f.g
ROOT=g.PILOT/'runs/2026-11-16-853b77f-replication-controls'
AMENDMENT=g.PILOT/'REPLICATION-ONLY-AMENDMENT.md'


def source_state():
    plan=f.verify_plan(f.ROOT);path=f.ROOT/'experiment';active={};spent=D(0)
    for event in g.old.rows(path/'ledger.jsonl'):
        if event['event']=='reserve':active[event['reservation']['reservation_id']]=D(event['reservation']['reserve_usd'])
        else:spent+=D(event['charge_upper_usd']);active.pop(event['reservation_id'])
    histories={}
    for case in plan['cases'][:15]:
        rows=g.old.rows(path/g.old.slug(case['candidate'])/case['case']/'raw.jsonl')
        initial=next(r for r in rows if r['id']==case['case']+'__initial')
        assert initial['finish_reason']=='stop'
        histories[case['case']]={'messages':initial['request']['messages']+[g.s.message('assistant',initial['text'])],'record_sha256':g.s.sha(g.s.dump(initial).encode())}
    return plan,histories,spent+sum(active.values(),D(0)),len(active)


def freeze(root):
    root=Path(root);root.mkdir(exist_ok=True)
    if (root/'plan.json').exists():raise FileExistsError('Controls plan already frozen')
    original,histories,exposure,active=source_state();assert active<=2
    cases=[{**c,'controls':True} for c in original['cases'][:15]]
    jobs=[{**c,'id':f'control_{c["case"]}_{t}_{v}','base_id':f'control_{t}_{v}','kind':'game','variable':v,'parent':c['case']+'__initial','question_key':f'control_{t}_{v}',
      'condition':'control','arm':None,'target':g.number(f.F(t,100))} for c in cases for t in (15,69) for v in 'BC']
    plan={'frozen_at':g.s.utc(),'original_plan_sha256':g.s.sha((f.ROOT/'plan.json').read_bytes()),'opening_conservative_exposure_usd':str(exposure),
      'original_active_requests_at_freeze':active,'concurrency':4,'budget_usd':'2','cases':cases,'jobs':jobs,'histories':histories,
      'selection':original['selection'],'prompts':original['prompts'],'config':original['config'],
      'sources_sha256':{str(p.relative_to(g.ROOT)):g.s.sha(p.read_bytes()) for p in (Path(__file__),AMENDMENT,g.ROOT/'tests/test_replication_controls.py')}}
    (root/'plan.json').write_text(g.s.dump(plan)+'\n');return plan


def verify(root):
    root=Path(root);plan=g.old.load(root/'plan.json');f.verify_plan(f.ROOT)
    assert plan['original_plan_sha256']==g.s.sha((f.ROOT/'plan.json').read_bytes())
    for p,digest in plan['sources_sha256'].items():assert g.s.sha((g.ROOT/p).read_bytes())==digest
    assert len(plan['jobs'])==60
    return plan


def run(root,live):
    root=Path(root);plan=verify(root);key=os.environ.get('OPENROUTER_API_KEY','') if live else ''
    if live and not key:raise RuntimeError('API key missing')
    a=g.LockedArtifacts(root/'experiment',key);budget=g.AtomicBudget(a,plan['config']);budget.spent_upper=D(plan['opening_conservative_exposure_usd']);budget.peak_exposure=budget.spent_upper
    tracker=g.OrderTracker(a,4);setups={};states={c['case']:{} for c in plan['cases']};rows={c['case']:[] for c in plan['cases']}
    for case in plan['cases']:
        s=f.selection_for(plan,case);cfg=copy.deepcopy(plan['config']);cfg.update(model_family=case['candidate'],provider=s['provider_name'],seed=case['seed'])
        ma=g.GameArtifacts(a.path/g.old.slug(case['candidate'])/case['case'],key,budget,tracker,case['candidate']);ma.prompts=plan['prompts']
        ma.write('history.json',plan['histories'][case['case']]);ma.write('selection.json',s);setups[case['case']]=(s,cfg,ma,threading.Event())
    started=g.s.utc()
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={}
        for job in plan['jobs']:
            s,cfg,ma,halt=setups[job['case']];effective=copy.deepcopy(job)
            if not live:effective['condition']='W'
            futures[pool.submit(f.v.task,effective,s,cfg,ma,budget,halt,plan['histories'][job['case']]['messages'],live,{})]=job
        for future in as_completed(futures):
            job=futures[future];r=future.result();states[job['case']][job['id']]={'status':r['status'],'failure':r['failure'],'parent':job['parent']}
            if r['record']:rows[job['case']].append(r['record'])
    raw=[]
    for c,(_,_,ma,_) in setups.items():
        path=ma.path/'raw.jsonl'
        if path.exists():raw+=g.old.rows(path)
    result={'status':'finished','started':started,'ended':g.s.utc(),'mode':'live' if live else 'dry-run','plan_sha256':g.s.sha((root/'plan.json').read_bytes()),'jobs':states,
      'opening_conservative_exposure_usd':plan['opening_conservative_exposure_usd'],'physical_attempts':tracker.dispatches,'maximum_in_flight':tracker.maximum,
      'accounting':g.old.base.accounting(raw),'combined_conservative_upper_usd':str(budget.spent_upper),'peak_combined_exposure_usd':str(budget.peak_exposure)}
    a.write('manifest.json',result);print('Replication controls finished',result['physical_attempts'],result['accounting'])
    return result


def audit(root):
    root=Path(root);plan=verify(root);path=root/'experiment';m=g.old.load(path/'manifest.json');req={};raw={};lookup={j['id']:j for j in plan['jobs']}
    for case in plan['cases']:
        p=path/g.old.slug(case['candidate'])/case['case'];selection=f.selection_for(plan,case)
        for r in g.old.rows(p/'requests.jsonl'):req[r['reservation']['reservation_id']]=r
        for r in g.old.rows(p/'raw.jsonl'):
            rid=r['reservation']['reservation_id'];raw[rid]=r;job=lookup[r['id']]
            assert r['request']['messages']==g.s.branch(plan['histories'][case['case']]['messages'],plan['prompts'][job['question_key']])
            assert r['request']['seed']==case['seed'] and r['request']['provider']['only']==[selection['endpoint_tag']]
            assert r['parsed']==g.parse_probability(r['text'],job['variable'],r['finish_reason'],True)
            assert r['response']['provider']==selection['provider_name'] and r['response']['model'] in selection['allowed_returned_models']
            assert r['usage']['completion_tokens_details']['reasoning_tokens']==0
    assert set(req)==set(raw) and len({r['id'] for r in raw.values()})==60
    spent=D(plan['opening_conservative_exposure_usd']);active={};peak=spent
    for e in g.old.rows(path/'ledger.jsonl'):
        if e['event']=='reserve':
            r=e['reservation'];rid=r['reservation_id'];assert e['request_sha256']==g.s.sha(g.s.dump(req[rid]['request']).encode())
            assert r['input_token_bound']==g.AtomicBudget.bound(req[rid]['request'],plan['config'])['input_token_bound']
            active[rid]=D(r['reserve_usd'])
        else:
            rid=e['reservation_id'];cap=active.pop(rid);charge,kind=g.AtomicBudget.charge(raw[rid],req[rid]['request'],cap);assert charge==D(e['charge_upper_usd']);spent+=charge
        peak=max(peak,spent+sum(active.values(),D(0)));assert peak<=D(2)
    assert not active and spent==D(m['combined_conservative_upper_usd']) and peak==D(m['peak_combined_exposure_usd'])
    events=g.old.rows(path/'execution.jsonl');active=set();maximum=0
    for e in events:
        rid=e['reservation_id']
        if e['event']=='dispatch':active.add(rid)
        else:active.remove(rid)
        maximum=max(maximum,len(active));assert len(active)<=4
    assert not active and maximum==m['maximum_in_flight']
    return {'status':'passed','calls':len(raw),'maximum_controls_concurrency':maximum,'combined_conservative_upper_usd':str(spent),'original_exposure_including_inflight_held':True,'all_histories_own_initials':True}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','dry-run','live','audit'));p.add_argument('--root',type=Path,default=ROOT);args=p.parse_args()
    if args.mode=='freeze':print(freeze(args.root)['opening_conservative_exposure_usd'])
    elif args.mode=='audit':print(g.s.dump(audit(args.root)))
    else:run(args.root,args.mode=='live')
