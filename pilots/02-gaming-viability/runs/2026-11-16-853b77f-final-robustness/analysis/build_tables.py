import sys,csv,hashlib
from fractions import Fraction as F
from decimal import Decimal as D
sys.path.insert(0,'pilots/02-gaming-viability/harness');import robustness as f;import replication_controls as ctrl

g=f.g;root=f.ROOT;plan=g.old.load(root/'plan.json');summary=g.old.load(root/'replication-summary.json');m=g.old.load(root/'experiment/manifest.json');cm=g.old.load(ctrl.ROOT/'experiment/manifest.json')
def fmt(v,prob=False):
 if v is None:return 'missing'
 return (f'{float(F(v))*(100 if prob else 1):.5f}'.rstrip('0').rstrip('.')) or '0'
rows=[];up=['# All replication initial and upstream replies','','Verbatim complete responses, including contradictory calculations. W acknowledgment is distinct from own endorsement.',''];tables=['# Every replication outcome','','All values are percentages; errors are percentage points. Missing own/operational A remains missing. No history excluded.','']
models={};allraw=[]
for case in plan['cases'][:15]:
 cid=case['case'];metric=summary['cases'][cid];mp=root/'experiment'/g.old.slug(case['candidate'])/cid;raw=g.old.rows(mp/'raw.jsonl');allraw+=raw;byid={r['id']:r for r in raw};items=g.old.load(mp/'observations.json')['responses'];models.setdefault(case['candidate'],[]).append(metric)
 initial=byid[cid+'__initial'];up+=['## '+cid+' / '+case['candidate']+' / seed'+str(case['seed']),'']
 for base in ('initial','W_15_A','W_69_A','U_15_A','U_69_A'):up+=['### '+base,'',byid[cid+'__'+base]['text'],'']
 tables+=['## '+cid+' — '+case['candidate']+' — seed'+str(case['seed']),'','Initial A='+fmt(metric['initial_A'],True)+'%; baseline B/C/D='+ '/'.join(fmt(metric['baseline'][v]['value'],True) for v in 'BCD')+'%.','',
 '| Arm | Own A | Outcome | Answer | Operational A | Evidence error | Own-A error | Op-A error | Baseline-change error | D drift |','|---|---:|---|---:|---:|---:|---:|---:|---:|---:|']
 arms={a['arm']:a for a in metric['arms']}
 for r in metric['downstream']:
  row={'case':cid,'model':case['candidate'],'seed':case['seed'],'initial_A':metric['initial_A'],**r};rows.append(row)
  tables+=['| '+' | '.join([r['arm'],fmt(arms[r['arm']]['own_A'],True),r['variable'],fmt(r['answer'],True),fmt(r['operational_A'],True),fmt(r['evidential_error_pp']),fmt(r['expressed_A_error_pp']),fmt(r['operational_A_error_pp']),fmt(r['change_error_pp']),fmt(r['D_baseline_drift_pp'])])+' |']
 tables+=['']
 cp=ctrl.ROOT/'experiment'/g.old.slug(case['candidate'])/cid;cr=g.old.rows(cp/'raw.jsonl');lines=['# Directed controls — '+cid,'']
 for r in sorted(cr,key=lambda x:x['id']):lines+=['## '+r['id'],'',r['text'],'']
 (cp/'RESPONSES.md').write_text('\n'.join(lines))
(root/'upstream').mkdir(exist_ok=True);(root/'upstream/RESPONSES.md').write_text('\n'.join(up));(root/'ALL-REPLICATION-OUTCOMES.md').write_text('\n'.join(tables))
with (root/'ALL-REPLICATION-OUTCOMES.csv').open('w',newline='') as file:
 writer=csv.DictWriter(file,fieldnames=rows[0],lineterminator='\n');writer.writeheader();writer.writerows(rows)
modelrows=[]
for model,metrics in models.items():
 initials=[]
 for x in metrics:
  p=root/'experiment'/g.old.slug(model)/x['case']['case']/'raw.jsonl';r=next(r for r in g.old.rows(p) if r['id'].endswith('__initial'));initials.append(hashlib.sha256(r['text'].encode()).hexdigest())
 row={'model':model,'histories':5,'unique_initial_texts':len(set(initials)),'initial_correct':sum(x['initial_correct_within5pp'] is True for x in metrics),'baseline_correct':sum(b['correct_within3pp'] is True for x in metrics for b in x['baseline'].values())}
 for arm in ('W_15','W_69','U_15','U_69'):
  a=[next(z for z in x['arms'] if z['arm']==arm) for x in metrics];row[arm+'_own_points']=sum(z['own_A'] is not None for z in a);row[arm+'_target_agreement']=sum(z['within3pp_target'] is True for z in a)
 row['D_stable']=sum(z['D_baseline_drift_pp']=='0' for x in metrics for z in x['downstream'] if z['variable']=='D')
 cr=[r for r in summary['same_history_capability_controls'] if r['model']==model];row['controls_within3pp']=sum(r['within3pp'] is True for r in cr);modelrows.append(row)
(root/'model-summary.json').write_text(g.s.dump(modelrows)+'\n')
# All canceled coverage outcomes preserved, never used in model-summary statistics.
canceled=[]
for case in plan['cases'][15:]:
 p=root/'experiment'/g.old.slug(case['candidate'])/case['case'];raw=g.old.rows(p/'raw.jsonl') if (p/'raw.jsonl').exists() else []
 canceled.append({'case':case['case'],'model':case['candidate'],'physical_attempts':len(raw),'logical_calls':len({r['id'] for r in raw}),
    'statuses':m['jobs'][case['case']],'records_path':str(p.relative_to(root)),'incomplete_or_errors':[{'id':r['id'],'status':r['http_status'],'finish_reason':r['finish_reason'],'cost':r['cost_usd']} for r in raw if r['finish_reason']!='stop']})
(root/'CANCELED-COVERAGE.json').write_text(g.s.dump({'scope':'Canceled at user direction after coverage had already begun. Historical partial data only; no further scheduling; excluded from primary replication conclusions. All raw attempts and missing planned nodes preserved.','cases':canceled})+'\n')
print('Model summary',modelrows)
print('Canceled',[(c['model'],c['physical_attempts'],c['logical_calls']) for c in canceled])
print('Costs',m['accounting']['reported_cost_subtotal_usd'],cm['accounting']['reported_cost_subtotal_usd'],D(m['accounting']['reported_cost_subtotal_usd'])+D(cm['accounting']['reported_cost_subtotal_usd']))
