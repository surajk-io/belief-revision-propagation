#!/usr/bin/env python3
"""Prespecified two-model Llama extension; unchanged GAME-01 components and scores."""
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import copy
import os
from pathlib import Path
import subprocess
import threading

import gaming as g
import wording_followup as w

SOURCE=g.PILOT/'LLAMA-FAMILY-FOLLOWUP.md'
REFERENCE=g.PILOT/'runs/2026-11-16-445c88d-implicit-followup'
REFERENCE_COMMIT='d71f845a982e34c0c9671e9c7f8806354c8dd867'
MODELS=('meta-llama/llama-4-maverick','meta-llama/llama-3.3-70b-instruct')
MAX_CALLS=36


def prompts():
    for path in (g.SOURCE,w.SOURCE):
        expected=subprocess.check_output(['git','show',REFERENCE_COMMIT+':'+str(path.relative_to(g.ROOT))],cwd=g.ROOT)
        if path.read_bytes()!=expected:raise RuntimeError('Reviewed prompt source differs from reference commit')
    result=w.prompts()
    if result!=g.old.load(REFERENCE/'plan.json')['prompts']:raise RuntimeError('Historical prompt mismatch')
    return result


def select(candidate,catalog,endpoints,scout):
    # Reuse compatibility, non-thinking, seed, price and version checks unchanged.
    preferred=[ep for ep in endpoints if ep['provider_name']==scout['provider_name'] and ep.get('quantization')==scout['endpoint'].get('quantization')]
    result=w.select_new(candidate,catalog,preferred)
    matched=result['status']=='selected'
    if not matched:result=w.select_new(candidate,catalog,endpoints)
    result['scout_configuration_preferred']=matched
    result['selection_rule']='Compatible Scout provider+quantization first; then '+result.get('selection_rule','compatible settings and advertised cost; no substitution')
    result['scout_reference']={'provider_name':scout['provider_name'],'endpoint_tag':scout['endpoint_tag'],'quantization':scout['endpoint'].get('quantization')}
    if result['status']=='selected':
        result['routing_differences_from_scout']={k:{'before':scout[k],'after':result[k]} for k in ('candidate','request_model','canonical_slug','endpoint_tag','provider_name') if scout[k]!=result[k]}
        if scout['parameters']!=result['parameters']:result['routing_differences_from_scout']['parameters']={'before':scout['parameters'],'after':result['parameters']}
    return result


def freeze(root):
    root=Path(root)
    if (root/'plan.json').exists():raise FileExistsError('Llama plan already frozen')
    original=w.verify_plan(REFERENCE)
    catalog={m['id']:m for m in g.old.load(root/'models-raw.json')['data']}
    scout=next(c for c in original['choices'] if c['candidate']=='meta-llama/llama-4-scout')
    choices=[select(m,catalog,g.old.load(root/(g.old.slug(m)+'-endpoints.json')).get('data',{}).get('endpoints',[]),scout) for m in MODELS]
    files=list(dict.fromkeys([g.ROOT/name for name in original['sources_sha256']]+[
        g.HERE/'gaming_audit.py',SOURCE,g.HERE/'llama_followup.py',g.HERE/'llama_audit.py',g.HERE/'LLAMA-EXECUTION.md',g.ROOT/'tests/test_llama_followup.py']))
    cfg=copy.deepcopy(original['config']);cfg['scope']='GAME-01 Llama family extension; two fresh18-call graphs;36 calls maximum'
    previous=dict(original['previous_artifacts']);previous[str(REFERENCE.relative_to(g.ROOT))]=g.old.inventory(REFERENCE)
    plan={'frozen_at':g.s.utc(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=g.ROOT,text=True).strip(),
          'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=g.ROOT)),
          'choices':choices,'config':cfg,'prompts':prompts(),'references':g.references(),'reference_commit':REFERENCE_COMMIT,
          'sources_sha256':{str(p.relative_to(g.ROOT)):g.s.sha(p.read_bytes()) for p in files},
          'discovery_sha256':{p.name:g.s.sha(p.read_bytes()) for p in sorted(root.iterdir()) if p.is_file()},
          'previous_artifacts':previous,'maximum_new_calls':MAX_CALLS,'scope':'Two fixed candidates; full own initial/baselines/W/U/N/controls; implicit unsupported only; no historical reruns'}
    (root/'plan.json').write_text(g.s.dump(plan)+'\n')
    for path in files:
        relative=str(path.relative_to(g.ROOT))
        (root/('source_'+relative.replace('/','__')+'.json')).write_text(g.s.dump({'path':relative,'text':path.read_text()})+'\n')
    return plan


def verify_plan(root):
    root=Path(root);plan=g.old.load(root/'plan.json')
    for name,digest in plan['sources_sha256'].items():
        if g.s.sha((g.ROOT/name).read_bytes())!=digest:raise RuntimeError('Frozen source changed: '+name)
    for name,digest in plan['discovery_sha256'].items():
        if g.s.sha((root/name).read_bytes())!=digest:raise RuntimeError('Discovery changed')
    for name,hashes in plan['previous_artifacts'].items():
        if g.old.inventory(g.ROOT/name)!=hashes:raise RuntimeError('Prior artifacts changed: '+name)
    if plan['prompts']!=prompts() or plan['references']!=g.references():raise RuntimeError('Prompt/math freeze mismatch')
    if [c['candidate'] for c in plan['choices']]!=list(MODELS) or plan['maximum_new_calls']!=MAX_CALLS:raise RuntimeError('Scope mismatch')
    return plan


def run(root,live,fixture_failures=None):
    root=Path(root);plan=verify_plan(root);cfg=plan['config']
    key=os.environ.get('OPENROUTER_API_KEY','') if live else ''
    if live and not key:raise RuntimeError('OPENROUTER_API_KEY unavailable; no calls sent')
    a=g.LockedArtifacts(root/'experiment',key)
    budget=g.AtomicBudget(a,cfg);tracker=g.OrderTracker(a,cfg['max_concurrent_requests'])
    plan_sha=g.s.sha((root/'plan.json').read_bytes());mode='live' if live else 'dry-run'
    manifest={'started':g.s.utc(),'status':'running','mode':mode,'plan_sha256':plan_sha,'maximum_logical_calls':MAX_CALLS,
              'concurrency_limit':cfg['max_concurrent_requests'],'candidates':[]}
    a.write('manifest.json',manifest)
    setups={};states={};records={};futures={};fixture_failures=fixture_failures or {}
    for choice in plan['choices']:
        candidate=choice['candidate'];states[candidate]={};records[candidate]={}
        if choice['status']!='selected':
            states[candidate]={logical:{'status':'blocked_skip','parent':g.parent_id(logical),'failure':choice['reason']} for logical in g.IDS}
            manifest['candidates'].append({'candidate':candidate,'selection':choice,'status':choice['status'],'jobs':states[candidate]})
            continue
        halt=threading.Event()
        ma=g.GameArtifacts(a.path/g.old.slug(candidate),key,budget,tracker,candidate);ma.prompts=plan['prompts']
        model_cfg=copy.deepcopy(cfg);model_cfg.update(model_family=candidate,provider=choice['provider_name'])
        ma.write('prompts.json',plan['prompts']);ma.write('frozen_config.json',model_cfg)
        setups[candidate]=(choice,model_cfg,ma,halt)
    def blocked(candidate,logical,parent,reason):
        if logical not in states[candidate]:
            states[candidate][logical]={'status':'blocked_parent','parent':parent,'failure':reason}
            a.append('scheduler.jsonl',{'event':'blocked','time':g.s.utc(),'candidate':candidate,'id':logical,'parent':parent,'reason':reason})
    def submit(pool,candidate,logical,parent,history):
        assert logical in g.IDS and logical not in states[candidate]
        choice,model_cfg,ma,halt=setups[candidate]
        if halt.is_set():blocked(candidate,logical,parent,'model configuration halted');return
        states[candidate][logical]={'status':'queued','parent':parent,'failure':None}
        a.append('scheduler.jsonl',{'event':'eligible','time':g.s.utc(),'candidate':candidate,'id':logical,'parent':parent})
        future=pool.submit(g.task,choice,model_cfg,ma,budget,halt,logical,copy.deepcopy(history),parent,live,fixture_failures)
        futures[future]=(candidate,logical)
    with ThreadPoolExecutor(max_workers=cfg['max_concurrent_requests'],thread_name_prefix='game') as pool:
        for candidate in setups:submit(pool,candidate,'initial',None,[g.s.message('system',plan['prompts']['system'])])
        while futures:
            done,_=wait(list(futures),timeout=1,return_when=FIRST_COMPLETED)
            for future in done:
                candidate,logical=futures.pop(future);result=future.result()
                states[candidate][logical].update(status=result['status'],failure=result['failure'])
                if result['record'] is not None:records[candidate][logical]=result['record']
                a.append('scheduler.jsonl',{'event':'task_finished','time':g.s.utc(),'candidate':candidate,'id':logical,'status':result['status']})
                if logical=='initial':
                    children=('baseline_B','baseline_C','baseline_D','warranted_A','unsupported_A','neutral_A','control_B','control_C')
                    if result['history'] is not None:
                        for child in children:submit(pool,candidate,child,'initial',result['history'])
                    else:
                        for child in g.IDS[1:]:blocked(candidate,child,g.parent_id(child),'initial ancestor failed or incomplete')
                elif logical.endswith('_A'):
                    children=tuple(logical[:-2]+'_'+v for v in g.s.PROBES)
                    for child in children:
                        if result['history'] is not None:submit(pool,candidate,child,logical,result['history'])
                        else:blocked(candidate,child,logical,'intervention parent failed or incomplete')
    for candidate,(choice,model_cfg,ma,halt) in setups.items():
        for logical in g.IDS:
            if logical not in states[candidate]:blocked(candidate,logical,g.parent_id(logical),'unavailable ancestor or halted configuration')
        result=g.save_model(ma,choice,model_cfg,states[candidate],list(records[candidate].values()),mode,plan_sha)
        manifest['candidates'].append(result)
    assert not tracker.active and not budget.active
    raw_all=[]
    for candidate in setups:
        path=a.path/g.old.slug(candidate)/'raw.jsonl'
        if path.exists():raw_all.extend(g.old.rows(path))
    manifest.update(status='finished',ended=g.s.utc(),logical_calls_dispatched=len({(r['request']['model'],r['id']) for r in raw_all}),
                    physical_attempts=tracker.dispatches,recorded_attempts=len(raw_all),reservations=budget.counter,maximum_in_flight=tracker.maximum,
                    accounting=g.old.base.accounting(raw_all),conservative_settled_upper_usd=str(budget.spent_upper),
                    peak_spent_plus_outstanding_usd=str(budget.peak_exposure),budget_halted=budget.failed)
    a.write('manifest.json',manifest)
    print('GAME-01 Llama follow-up finished:',manifest['logical_calls_dispatched'],'logical calls;',manifest['physical_attempts'],'attempts; peak concurrency',tracker.maximum,'; reported cost',manifest['accounting']['reported_cost_subtotal_usd'])
    return manifest


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('freeze','dry-run','live'))
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='freeze':
        plan=freeze(args.root)
        for choice in plan['choices']:print(choice['candidate'],choice['status'],choice.get('endpoint_tag'),choice.get('parameters'),choice.get('reason'))
    else:run(args.root,args.mode=='live')
