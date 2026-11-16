#!/usr/bin/env python3
"""Offline verification of persisted run topology, scoring, provenance and costs."""
from decimal import Decimal as D
import json
import os
from pathlib import Path
import sys

import smoke as s


def audit(path):
    path = Path(path)
    manifest = json.loads((path / 'manifest.json').read_text())
    prompts = json.loads((path / 'prompts.json').read_text())
    cfg = json.loads((path / 'frozen_config.json').read_text())
    requests = [json.loads(line) for line in (path / 'requests.jsonl').read_text().splitlines()]
    attempts = [json.loads(line) for line in (path / 'raw.jsonl').read_text().splitlines()]
    assert manifest['status'] == 'complete', 'Run incomplete'
    assert cfg == manifest['config'], 'Configuration mismatch'
    assert s.prompts() == prompts, 'Reviewed prompts differ from frozen run'
    for name, digest in manifest['files_sha256'].items():
        source = s.ROOT / name
        assert s.sha(source.read_bytes()) == digest, f'Current source differs: {name}'
        snapshot = json.loads((path / ('source_' + source.name + '.json')).read_text())
        assert snapshot['path'] == name and s.sha(snapshot['text'].encode()) == digest, f'Bad snapshot: {name}'
    assert {k: s.sha(v.encode()) for k, v in prompts.items()} == manifest['prompt_sha256']
    assert len(requests) == len(attempts) == manifest['dispatched_attempts']
    ids = ['initial'] + ['baseline_' + v for v in s.PROBES]
    ids += [c + '_' + v for c in s.CONDITIONS for v in ('A', *s.PROBES)]
    ids += ['control_B', 'control_C']
    by_id = {r['id']: r for r in attempts}
    assert set(by_id) == set(ids) and len(by_id) == 18
    initial = [s.message('system', prompts['system']), s.message('user', prompts['initial'])]
    prefix = initial + [s.message('assistant', by_id['initial']['text'])]
    expected = {'initial': (initial, None)}
    for var in s.PROBES:
        expected['baseline_' + var] = (prefix + [s.message('user', prompts[var])], 'initial')
    for condition in s.CONDITIONS:
        intervention = prefix + [s.message('user', prompts[condition])]
        expected[condition + '_A'] = (intervention, 'initial')
        post = intervention + [s.message('assistant', by_id[condition + '_A']['text'])]
        for var in s.PROBES:
            expected[condition + '_' + var] = (post + [s.message('user', prompts[var])], condition + '_A')
    for var in ('B', 'C'):
        expected['control_' + var] = (prefix + [s.message('user', prompts['control_' + var])], 'initial')
    budget = s.Budget(cfg)
    per_call = {}
    for request, record in zip(requests, attempts):
        for key, value in request.items():
            assert record[key] == value, f'Request/response mismatch: {key}'
        logical_id = request['id']
        per_call.setdefault(logical_id, []).append(record)
        assert request['attempt'] == len(per_call[logical_id]) <= 3
        if request['attempt'] > 1:
            assert per_call[logical_id][-2]['http_status'] in s.TRANSIENT
        messages, parent = expected[logical_id]
        assert request['request']['messages'] == messages, f'Branch contaminated: {logical_id}'
        assert request['parent'] == parent
        pin = request['request']['provider']
        assert pin['only'] == ['OpenAI'] and pin['allow_fallbacks'] is False and pin['require_parameters'] is True
        assert request['request']['model'] == manifest['preflight'].get('model', cfg['model_family'])
        assert request['reservation'] == budget.reserve(request['request'])
        assert not {'Authorization', 'authorization', 'api_key'} & request['request'].keys()
        if record['usage']:
            assert record['usage']['prompt_tokens'] <= record['reservation']['input_token_bound']
            assert record['usage']['completion_tokens'] <= cfg['max_tokens']
        if record['cost_usd'] is not None:
            assert D(str(record['cost_usd'])) <= D(record['reservation']['reserve_usd'])
        assert s.remove_hidden(record['response']) == record['response']
        if isinstance(record['response'], dict):
            assert json.loads(record['raw_response_body']) == record['response']
    assert str(budget.reserved) == manifest['reserved_usd'] and budget.reserved <= D('1')
    for record in by_id.values():
        assert record['finish_reason'] == 'stop'
        assert record['response']['provider'] == 'OpenAI'
        assert record['response']['model'].startswith('openai/gpt-4o-mini')
        assert record['response']['choices'][0]['message']['content'] == record['text']
        assert s.parse_answer(record['text'], record['variable'], record['finish_reason']) == record['parsed']
    derived = s.analyze(list(by_id.values()), cfg)
    assert derived == json.loads((path / 'derived.json').read_text()), 'Derived metrics do not replay'
    cost = sum((D(str(r['cost_usd'])) for r in attempts if r['cost_usd'] is not None), D(0))
    assert str(cost) == manifest['accounting']['reported_cost_subtotal_usd']
    assert cost <= budget.reserved <= D('1')
    secret = os.environ.get('OPENROUTER_API_KEY', '').encode()
    files = [f for f in path.iterdir() if f.is_file() and f.name != 'audit.json']
    if secret:
        assert all(secret not in f.read_bytes() for f in files), 'Secret detected; do not commit'
    return {'status': 'passed', 'time': s.utc(), 'logical_calls': 18, 'attempts': len(attempts),
            'reported_cost_subtotal_usd': str(cost), 'reserved_usd': str(budget.reserved),
            'checks': ['reviewed prompt fidelity and source/snapshot hashes',
                       'all baseline, intervention and control parent histories',
                       'independent B/C/D branches with no sibling responses',
                       'exact request/response pairing and bounded retries',
                       'provider/model pin, token bounds, per-attempt cost and $1 ceiling',
                       'visible response fidelity and absence of hidden reasoning',
                       'deterministic score and metric replay', 'exact secret absence when configured'],
            'artifact_sha256': {f.name: s.sha(f.read_bytes()) for f in sorted(files)}}


if __name__ == '__main__':
    result = audit(sys.argv[1])
    (Path(sys.argv[1]) / 'audit.json').write_text(s.dump(result) + '\n')
    print(s.dump({k: v for k, v in result.items() if k != 'artifact_sha256'}))
