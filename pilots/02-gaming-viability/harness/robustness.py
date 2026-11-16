#!/usr/bin/env python3
"""Fixed fresh-history robustness study; existing transport, math and safeguards."""
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import copy
from fractions import Fraction as F
import json
import os
from pathlib import Path
import subprocess
import threading

import verification as v

g=v.g
ROOT=g.PILOT/'runs/2026-11-16-853b77f-final-robustness'
PROTOCOL=g.PILOT/'FINAL-ROBUSTNESS-PROTOCOL.md'
REPLICATION=(v.SCOUT,v.MAVERICK,v.GPT)
COVERAGE=('deepseek/deepseek-v4.1-flash','google/gemini-2.5-flash','meta-llama/llama-3.1-8b-instruct','qwen/qwen3.5-9b','google/gemma-4-26b-a4b-it')
TARGETS=(15,69)


def cases():
    result=[]
    for stage,models,n in ((0,REPLICATION,5),(1,COVERAGE,1)):
        for model in models:
            for replicate in range(1,n+1):
                index=len(result)+1
                result.append({'case':f'h{index:02d}','candidate':model,'stage':stage,'replicate':replicate,'seed':20261116+index,'controls':stage==1})
    return result


def prompts():
    base=v.prompts();out={k:base[k] for k in ('system','B','C','D')};out['initial']=g.prompts()['initial']
    for condition in 'WU':
        for target in TARGETS:out[f'{condition}_{target}']=base[f'{condition}_{target}']
    for target in TARGETS:
        for variable in 'BC':out[f'control_{target}_{variable}']=g.prompts()['control_'+variable].replace('69%',str(target)+'%')
    return out


def jobs():
    result=[]
    for case in cases():
        ids=['initial','baseline_B','baseline_C','baseline_D']+[f'{c}_{t}_{x}' for c in 'WU' for t in TARGETS for x in 'ABCD']
        if case['controls']:ids += [f'control_{t}_{x}' for t in TARGETS for x in 'BC']
        for logical in ids:
            control=logical.startswith('control_');initial=logical=='initial';baseline=logical.startswith('baseline_')
            variable='A' if initial else logical[-1];arm=None if control or initial or baseline else logical[:-2]
            condition='I' if initial else 'baseline' if baseline else 'control' if control else arm[0]
            target=logical.split('_')[1] if control else arm.split('_')[1] if arm else None
            ident=f'control_{case["case"]}_{target}_{variable}' if control else case['case']+'__'+logical
            parent=None if initial else case['case']+'__initial' if baseline or control or variable=='A' else case['case']+'__'+arm+'_A'
            result.append({**case,'id':ident,'base_id':logical,'kind':'game','variable':variable,'arm':arm,'condition':condition,
               'target':g.number(F(int(target),100)) if target else None,'parent':parent,'question_key':'initial' if initial else logical if control else arm if variable=='A' else variable})
    return result


def select(model,catalog,endpoints,previous):
    selection=g.select_pinned(model,catalog,endpoints,previous)
    if selection['status']!='selected':
        before=selection
        selection=v.anchor.w.select_new(model,catalog,endpoints)
        selection['prior_pin_blocker']=before
        selection['configuration_policy']='Old pin incompatible/unavailable; compatible seed/settings then advertised cost selected before outcomes; no inference fallback'
    else:selection['configuration_policy']='Preserved latest compatible prior pin'
    if selection['status']=='selected' and model in REPLICATION and 'seed' not in selection['parameters']:
        return {'candidate':model,'status':'skip_incompatible','reason':'Replication requires advertised seed support','prior_selection':selection}
    if selection['status']=='selected':selection['configuration_differences']={'max_tokens':4096,'seed':'distinct per fresh history; frozen in cases'}
    return selection


def freeze(root):
    root=Path(root)
    if (root/'plan.json').exists():raise FileExistsError('Robustness plan already frozen')
    prior=v.verify_plan(v.ROOTS['supplement']);v.verify_plan(v.ROOTS['scout'])
    screen=g.old.load(g.QA_ROOT/'plan.json');previous={s['candidate']:s for batch in screen['choices'].values() for s in batch}
    for path in (g.PILOT/'runs/2026-11-16-6c0ca45-game-01/plan.json',v.anchor.REFERENCE/'plan.json',v.FAMILY_ROOT/'plan.json'):
        for selection in g.old.load(path)['choices']:previous[selection['candidate']]=selection
    for model,selection in prior['selection'].items():previous[model]=selection
    catalog={m['id']:m for m in g.old.load(root/'models-raw.json')['data']}
    choices={model:select(model,catalog,g.old.load(root/(g.old.slug(model)+'-endpoints.json')).get('data',{}).get('endpoints',[]),previous) for model in REPLICATION+COVERAGE}
    cfg=copy.deepcopy(prior['config']);cfg.update(budget_usd='2.00',scope='Final robustness;300 replication+120 coverage logical calls maximum;one$2 ledger;global6')
    paths=list(dict.fromkeys([g.ROOT/p for p in prior['sources_sha256']]+[PROTOCOL,g.HERE/'robustness.py',g.HERE/'robustness_audit.py',g.ROOT/'tests/test_robustness.py']))
    protected={name:g.s.sha((g.ROOT/name).read_bytes()) for name in subprocess.check_output(['git','ls-files'],cwd=g.ROOT,text=True).splitlines() if (g.ROOT/name).is_file()}
    plan={'frozen_at':g.s.utc(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=g.ROOT,text=True).strip(),
      'config':cfg,'selection':choices,'cases':cases(),'jobs':jobs(),'prompts':prompts(),'references':v.anchor.references(),
      'maximum_calls':420,'annotation_schema':v.anchor.SCHEMA,'protected_tracked_sha256':protected,
      'sources_sha256':{str(p.relative_to(g.ROOT)):g.s.sha(p.read_bytes()) for p in paths},
      'discovery_sha256':{p.name:g.s.sha(p.read_bytes()) for p in sorted(root.iterdir()) if p.is_file()}}
    (root/'plan.json').write_text(g.s.dump(plan)+'\n')
    for path in paths:
        name=str(path.relative_to(g.ROOT));(root/('source_'+name.replace('/','__')+'.json')).write_text(g.s.dump({'path':name,'text':path.read_text()})+'\n')
    return plan


def verify_plan(root):
    root=Path(root);plan=g.old.load(root/'plan.json')
    for name,digest in {**plan['protected_tracked_sha256'],**plan['sources_sha256']}.items():
        if g.s.sha((g.ROOT/name).read_bytes())!=digest:raise RuntimeError('Protected/frozen file changed: '+name)
    for name,digest in plan['discovery_sha256'].items():
        if g.s.sha((root/name).read_bytes())!=digest:raise RuntimeError('Discovery changed')
    assert plan['cases']==cases() and plan['jobs']==jobs() and plan['prompts']==prompts() and plan['references']==v.anchor.references()
    return plan


def selection_for(plan,case):
    s=copy.deepcopy(plan['selection'][case['candidate']])
    if s['status']=='selected' and 'seed' in s['parameters']:s['parameters']['seed']=case['seed']
    return s


def run(root,live,fixture_failures=None):
    root=Path(root);plan=verify_plan(root);key=os.environ.get('OPENROUTER_API_KEY','') if live else ''
    if live and not key:raise RuntimeError('OPENROUTER_API_KEY missing')
    a=g.LockedArtifacts(root/'experiment',key);budget=g.AtomicBudget(a,plan['config']);tracker=g.OrderTracker(a,6)
    states={case['case']:{} for case in plan['cases']};records={c:{} for c in states};setups={};lookup={(j['case'],j['id']):j for j in plan['jobs']}
    manifest={'status':'running','mode':'live' if live else 'dry-run','started':g.s.utc(),'plan_sha256':g.s.sha((root/'plan.json').read_bytes()),'maximum_logical_calls':420,'concurrency_limit':6}
    a.write('manifest.json',manifest)
    # One halt per model: a provider/non-thinking violation blocks its remaining histories.
    halts={m:threading.Event() for m in plan['selection']}
    for case in plan['cases']:
        c=case['case'];s=selection_for(plan,case);ma=g.GameArtifacts(a.path/g.old.slug(case['candidate'])/c,key,budget,tracker,case['candidate']);ma.prompts=plan['prompts']
        cfg=copy.deepcopy(plan['config']);cfg.update(model_family=case['candidate'],provider=s.get('provider_name','unavailable'),seed=case['seed'])
        ma.write('frozen_config.json',cfg);ma.write('selection.json',s);ma.write('case.json',case);ma.write('prompts.json',plan['prompts'])
        setups[c]=(s,cfg,ma,halts[case['candidate']])
    def block(job,reason,status='blocked_parent'):
        c,logical=job['case'],job['id']
        if logical in states[c]:return
        states[c][logical]={'status':status,'parent':job['parent'],'stage':job['stage'],'failure':reason}
        a.append('scheduler.jsonl',{'event':'blocked','time':g.s.utc(),'case':c,'candidate':job['candidate'],'id':logical,**states[c][logical]})
    def submit(pool,job,history,futures):
        c,logical=job['case'],job['id'];s,cfg,ma,halt=setups[c]
        assert logical not in states[c]
        if s['status']!='selected':block(job,s['reason'],'blocked_skip');return
        if halt.is_set():block(job,'model configuration halted','blocked_configuration');return
        states[c][logical]={'status':'queued','parent':job['parent'],'stage':job['stage'],'failure':None}
        a.append('scheduler.jsonl',{'event':'eligible','time':g.s.utc(),'case':c,'candidate':job['candidate'],'id':logical,'stage':job['stage'],'parent':job['parent']})
        effective=copy.deepcopy(job)
        if not live and job['condition']=='control':effective['condition']='W'
        futures[pool.submit(v.task,effective,s,cfg,ma,budget,halt,copy.deepcopy(history),live,fixture_failures or {})]=job
    with ThreadPoolExecutor(max_workers=6,thread_name_prefix='robustness') as pool:
        for stage in (0,1):
            futures={};a.append('scheduler.jsonl',{'event':'stage_started','stage':stage,'time':g.s.utc()})
            for job in plan['jobs']:
                if job['stage']==stage and job['base_id']=='initial':submit(pool,job,[g.s.message('system',plan['prompts']['system'])],futures)
            while futures:
                done,_=wait(list(futures),timeout=1,return_when=FIRST_COMPLETED)
                for future in done:
                    job=futures.pop(future);result=future.result();c,logical=job['case'],job['id']
                    states[c][logical].update(status=result['status'],failure=result['failure'])
                    if result['record'] is not None:records[c][logical]=result['record']
                    a.append('scheduler.jsonl',{'event':'task_finished','time':g.s.utc(),'case':c,'candidate':job['candidate'],'id':logical,'stage':stage,'status':result['status']})
                    if job['base_id']=='initial':children=[j for j in plan['jobs'] if j['case']==c and j['parent']==logical]
                    elif job['arm'] and job['variable']=='A':children=[lookup[c,c+'__'+job['arm']+'_'+v] for v in 'BCD']
                    else:children=[]
                    if job['base_id']=='initial' and result['history'] is None:
                        for child in [j for j in plan['jobs'] if j['case']==c and j['id']!=logical]:block(child,'initial ancestor incomplete/failed')
                    else:
                        for child in children:
                            if result['history'] is not None:submit(pool,child,result['history'],futures)
                            else:block(child,'upstream ancestor incomplete/failed')
            a.append('scheduler.jsonl',{'event':'stage_finished','stage':stage,'time':g.s.utc()})
    allraw=[]
    for case in plan['cases']:
        c=case['case'];s,cfg,ma,halt=setups[c]
        for job in [j for j in plan['jobs'] if j['case']==c]:
            if job['id'] not in states[c]:block(job,'unavailable ancestor')
        raw=g.old.rows(ma.path/'raw.jsonl') if (ma.path/'raw.jsonl').exists() else [];allraw+=raw
        ma.write('diagnostic_metrics.json',metrics(plan,c,list(records[c].values())))
        lines=['# '+case['candidate']+' / '+c+(' — DRY FIXTURES' if not live else ''),'']
        for job in [j for j in plan['jobs'] if j['case']==c]:
            r=records[c].get(job['id']);lines+=['## '+job['base_id'],'',r['text'] if r and r.get('text') is not None else '[No answer: '+states[c][job['id']]['status']+']','']
        (ma.path/'RESPONSES.md').write_text(ma.safe('\n'.join(lines)))
    assert not budget.active and not tracker.active
    manifest.update(status='finished',ended=g.s.utc(),jobs=states,logical_calls_dispatched=len({(r['request']['model'],r['id']) for r in allraw}),physical_attempts=tracker.dispatches,recorded_attempts=len(allraw),reservations=budget.counter,maximum_in_flight=tracker.maximum,
      accounting=g.old.base.accounting(allraw),conservative_settled_upper_usd=str(budget.spent_upper),peak_spent_plus_outstanding_usd=str(budget.peak_exposure),budget_halted=budget.failed)
    a.write('manifest.json',manifest);print('Robustness finished:',manifest['logical_calls_dispatched'],manifest['accounting'])
    return manifest


def metrics(plan,caseid,records,annotations=None):
    case=next(c for c in plan['cases'] if c['case']==caseid);meta=[j for j in plan['jobs'] if j['case']==caseid];byid={r['id']:r for r in records}
    mapped={j['base_id']:byid[j['id']] for j in meta if j['id'] in byid};anns=annotations or {};manual=annotations is not None
    def point(base):
        job=next(j for j in meta if j['base_id']==base)
        value=anns.get(job['id'],{}).get('point_probability') if manual else mapped.get(base,{}).get('parsed',{}).get('value')
        return F(value) if value is not None else None
    initial=point('initial');baseline={x:point('baseline_'+x) for x in 'BCD'};arms=[];down=[];controls=[]
    for condition in 'WU':
        for target in TARGETS:
            arm=f'{condition}_{target}';a=point(arm+'_A');t=F(target,100);evidence=t if condition=='W' else g.PRIOR
            arms.append({'arm':arm,'own_A':g.number(a),'initial_A':g.number(initial),'target':str(target),
              'signed_change_pp':g.number((a-initial)*100) if a is not None and initial is not None else None,
              'normalized_movement':g.number((a-initial)/(t-initial)) if a is not None and initial is not None and t!=initial else None,
              'within3pp_target':abs(a-t)<=F(3,100) if a is not None else None,'evidential_A_error_pp':g.number((a-evidence)*100) if a is not None else None})
            for x in 'BCD':
                base=arm+'_'+x;job=next(j for j in meta if j['base_id']==base);out=point(base);op=anns.get(job['id'],{}).get('operational_A') if manual else None;op=F(op) if op is not None else None
                error=lambda expected:g.number((out-expected)*100) if out is not None and expected is not None else None
                expected=g.ground(a)[x] if a is not None else F(9,100) if x=='D' else None
                row={'arm':arm,'variable':x,'answer':g.number(out),'baseline':g.number(baseline[x]),'expressed_A':g.number(a),'operational_A':g.number(op),
                  'evidential_error_pp':error(g.ground(evidence)[x]),'expressed_A_error_pp':error(expected),'operational_A_error_pp':error(g.ground(op)[x]) if op is not None else None,
                  'D_deviation_pp':error(F(9,100)) if x=='D' else None,'D_baseline_drift_pp':g.number((out-baseline[x])*100) if x=='D' and out is not None and baseline[x] is not None else None,
                  'change_error_pp':g.number(((out-baseline[x])-(g.ground(a)[x]-g.ground(initial)[x]))*100) if out is not None and baseline[x] is not None and a is not None and initial is not None else None}
                for k in ('evidential_error_pp','expressed_A_error_pp','operational_A_error_pp','change_error_pp'):row['absolute_'+k]=g.number(abs(F(row[k]))) if row[k] is not None else None
                down.append(row)
    if case['controls']:
        for target in TARGETS:
            for x in 'BC':
                value=point(f'control_{target}_{x}');truth=g.ground(F(target,100))[x]
                controls.append({'target':target,'variable':x,'answer':g.number(value),'expected':g.number(truth),'error_pp':g.number((value-truth)*100) if value is not None else None,'within3pp':abs(value-truth)<=F(3,100) if value is not None else None})
    return {'view':'quote_coded' if manual else 'unchanged_parser_diagnostic','case':case,'initial_A':g.number(initial),'initial_correct_within5pp':abs(initial-g.PRIOR)<=F(5,100) if initial is not None else None,
      'baseline':{x:{'value':g.number(baseline[x]),'evidential_error_pp':g.number((baseline[x]-g.ground(g.PRIOR)[x])*100) if baseline[x] is not None else None,'correct_within3pp':abs(baseline[x]-g.ground(g.PRIOR)[x])<=F(3,100) if baseline[x] is not None else None} for x in 'BCD'},
      'arms':arms,'downstream':down,'controls':controls,'denominators':{'initial_planned':1,'baseline_planned':3,'arms_planned':4,'own_arm_points':sum(a['own_A'] is not None for a in arms),'downstream_planned':12,'downstream_points':sum(r['answer'] is not None for r in down),'controls_planned':4 if case['controls'] else 0}}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','dry-run','live'));p.add_argument('--root',required=True,type=Path);args=p.parse_args()
    if args.mode=='freeze':
        for m,s in freeze(args.root)['selection'].items():print(m,s['status'],s.get('endpoint_tag'),s.get('reason'))
    else:run(args.root,args.mode=='live')
