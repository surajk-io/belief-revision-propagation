#!/usr/bin/env python3
"""Offline audit for fixed cross-model screens, including shared batch budgets."""
import copy
from decimal import Decimal as D
import json
import os
from pathlib import Path
import sys

import compare_v3
import screen as x
import smoke as s


def audit(root, number):
    root = Path(root)
    plan = x.verify_plan(root)
    assert compare_v3.audit(x.REFERENCE)['status'] == 'passed'
    path = root / ('batch-' + str(number))
    manifest = x.load(path / 'manifest.json')
    assert manifest['status'] == 'finished' and manifest['batch'] == number
    assert manifest['plan_sha256'] == s.sha((root / 'plan.json').read_bytes())
    assert [v['candidate'] for v in manifest['candidates']] == list(x.BATCHES[number])
    ledger = x.rows(path / 'ledger.jsonl') if (path / 'ledger.jsonl').exists() else []
    attempts_in_order, total_logical, aggregate = [], 0, []
    for result, selection in zip(manifest['candidates'], plan['choices'][str(number)]):
        assert result['selection'] == selection
        if selection['status'] != 'selected':
            assert result['status'] == selection['status'] and not (path / x.slug(selection['candidate'])).exists()
            continue
        model_path = path / x.slug(selection['candidate'])
        model_manifest = x.load(model_path / 'manifest.json')
        assert model_manifest['selection'] == selection and model_manifest['status'] == result['status']
        assert x.load(model_path / 'prompts.json') == plan['prompts']
        cfg = x.load(model_path / 'frozen_config.json')
        assert cfg == model_manifest['config']
        for key, value in plan['config'].items():
            if key not in ('provider', 'model_family', 'preferred_version', 'input_token_rate_ceiling_usd', 'output_token_rate_ceiling_usd'):
                assert cfg[key] == value
        requests = x.rows(model_path / 'requests.jsonl') if (model_path / 'requests.jsonl').exists() else []
        attempts = x.rows(model_path / 'raw.jsonl') if (model_path / 'raw.jsonl').exists() else []
        assert len(requests) == len(attempts) == model_manifest['attempts'] == result['attempts']
        records = {v['id']:v for v in attempts}
        total_logical += len(records)
        assert len(records) == model_manifest['logical_calls'] <= 18
        expected_ids = {'initial', *('baseline_' + v for v in s.PROBES), *('control_' + v for v in ('B','C')),
                        *(c + '_' + v for c in s.CONDITIONS for v in ('A', *s.PROBES))}
        assert set(records) <= expected_ids
        if result['status'] == 'complete':
            assert set(records) == expected_ids and all(v['finish_reason'] == 'stop' for v in records.values())
        seen = {}
        for request, record in zip(requests, attempts):
            assert all(record[k] == v for k,v in request.items())
            logical = record['id']
            seen.setdefault(logical, []).append(record)
            assert record['attempt'] == len(seen[logical]) <= 3
            if record['attempt'] > 1:
                assert seen[logical][-2]['http_status'] in s.TRANSIENT
            if logical == 'initial':
                parent, question = None, plan['prompts']['initial']
                history = [s.message('system',plan['prompts']['system'])]
            elif logical.startswith('baseline_'):
                parent, question = 'initial', plan['prompts'][logical[-1]]
            elif logical.startswith('control_'):
                parent, question = 'initial', plan['prompts'][logical]
            elif logical.endswith('_A'):
                parent, question = 'initial', plan['prompts'][logical[:-2]]
            else:
                parent, question = logical[:-2] + '_A', plan['prompts'][logical[-1]]
            if parent is not None:
                prior = records[parent]
                assert prior['finish_reason'] == 'stop' and isinstance(prior['text'], str)
                history = prior['request']['messages'] + [s.message('assistant',prior['text'])]
            assert record['parent'] == parent and record['request']['messages'] == s.branch(history, question)
            payload = record['request']
            expected = {'model':selection['request_model'], 'messages':payload['messages'], **selection['parameters'],
                        'stream':False,'usage':{'include':True},'provider':{'only':[selection['endpoint_tag']],
                            'allow_fallbacks':False,'require_parameters':True,'max_price':{
                                k:float(D(v)*1000000) for k,v in selection['price_ceilings_usd_per_token'].items()}}}
            assert payload == expected
            assert s.remove_hidden(record['response']) == record['response']
            if isinstance(record['response'],dict):
                assert json.loads(record['raw_response_body']) == record['response']
            if isinstance(record['text'],str):
                assert record['text'] == record['response']['choices'][0]['message']['content']
                assert record['parsed'] == s.parse_answer(record['text'], record['variable'], record['finish_reason'])
                assert record['cue_leakage'] == (s.cue_leakage(record['text']) if record['variable']=='A' else None)
                if result['status'] == 'complete':
                    assert record['response']['model'] in selection['allowed_returned_models']
                    assert record['response']['provider'] == selection['provider_name']
                    assert not record['hidden_trace_present']
                    tokens = (record['usage'] or {}).get('completion_tokens_details',{}).get('reasoning_tokens')
                    assert tokens is None or tokens == 0
            if record['usage']:
                assert record['usage']['prompt_tokens'] <= record['reservation']['input_token_bound']
                assert record['usage']['completion_tokens'] <= 1200
            if record['cost_usd'] is not None:
                assert D(str(record['cost_usd'])) <= D(record['reservation']['reserve_usd'])
            attempts_in_order.append((selection['candidate'],record))
        assert x.load(model_path / 'derived.json') == s.analyze(list(records.values()),cfg)
        assert model_manifest['accounting'] == result['accounting'] == x.base.accounting(attempts)
        aggregate.extend(attempts)
    assert len(attempts_in_order) == len(ledger) == manifest['dispatched_attempts']
    budget = s.Budget(copy.deepcopy(plan['config']))
    for entry, (candidate,record) in zip(ledger,attempts_in_order):
        assert entry['context'] == {'candidate':candidate,'id':record['id']}
        assert entry['request_sha256'] == s.sha(s.dump(record['request']).encode())
        prices = record['request']['provider']['max_price']
        budget.cfg['input_token_rate_ceiling_usd'] = str(D(str(prices['prompt'])) / 1000000)
        budget.cfg['output_token_rate_ceiling_usd'] = str(D(str(prices['completion'])) / 1000000)
        assert budget.reserve(record['request']) == record['reservation'] == entry['reservation']
    accounting = x.base.accounting(aggregate)
    assert accounting['reported_cost_subtotal_usd'] == manifest['reported_cost_subtotal_usd']
    assert accounting['unknown_cost_attempts'] == manifest['unknown_cost_attempts']
    assert D(manifest['reserved_usd']) == budget.reserved <= D('1')
    assert D(manifest['reported_cost_subtotal_usd']) <= budget.reserved
    assert total_logical == manifest['logical_calls'] <= manifest['maximum_logical_calls']
    key = os.environ.get('OPENROUTER_API_KEY','').encode()
    if key:
        assert all(key not in p.read_bytes() for p in root.rglob('*') if p.is_file())
    return {'status':'passed','time':s.utc(),'batch':number,'logical_calls':total_logical,'attempts':len(ledger),
            'reported_cost_subtotal_usd':manifest['reported_cost_subtotal_usd'],'reserved_usd':str(budget.reserved),
            'checks':['prior artifact/source preservation and smoke-03 audit replay','exact frozen V3 prompts and parent histories',
                      'no sibling answer contamination','frozen model/provider/non-reasoning settings and all attempts',
                      'shared $1 budget replay including retries across all candidates','raw-text/primary-score/cost/token replay',
                      'exact secret absence when configured'],
            'artifact_sha256':{str(p.relative_to(path)):s.sha(p.read_bytes()) for p in sorted(path.rglob('*')) if p.is_file() and p.name!='audit.json'}}


if __name__ == '__main__':
    result = audit(sys.argv[1],int(sys.argv[2]))
    (Path(sys.argv[1])/('batch-'+sys.argv[2])/'audit.json').write_text(s.dump(result)+'\n')
    print(s.dump({k:v for k,v in result.items() if k!='artifact_sha256'}))
