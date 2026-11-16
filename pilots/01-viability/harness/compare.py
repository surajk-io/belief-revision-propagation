#!/usr/bin/env python3
"""Offline audit and paired raw comparison; never edits the reference run."""
from decimal import Decimal as D
import difflib
import json
import os
from pathlib import Path
import sys

import audit as original_audit
import repeat as r
import smoke as s


def final_records(path):
    return {row['id']: row for row in r.rows(Path(path) / 'raw.jsonl')}


def expected_graph(prompts, records):
    first = [s.message('system', prompts['system']), s.message('user', prompts['initial'])]
    prefix = first + [s.message('assistant', records['initial']['text'])]
    expected = {'initial': (first, None)}
    for var in s.PROBES:
        expected['baseline_' + var] = (s.branch(prefix, prompts[var]), 'initial')
    for condition in s.CONDITIONS:
        intervention = s.branch(prefix, prompts[condition])
        expected[condition + '_A'] = (intervention, 'initial')
        post = intervention + [s.message('assistant', records[condition + '_A']['text'])]
        for var in s.PROBES:
            expected[condition + '_' + var] = (s.branch(post, prompts[var]), condition + '_A')
    for var in ('B', 'C'):
        expected['control_' + var] = (s.branch(prefix, prompts['control_' + var]), 'initial')
    return expected


def audit(path):
    path = Path(path)
    manifest = r.load(path / 'manifest.json')
    prompts = r.load(path / 'prompts.json')
    cfg = r.load(path / 'frozen_config.json')
    requests, attempts = r.rows(path / 'requests.jsonl'), r.rows(path / 'raw.jsonl')
    reference_manifest = r.load(r.REFERENCE / 'manifest.json')
    old_audit = original_audit.audit(r.REFERENCE)  # Pure function; no old files written.
    assert old_audit['status'] == 'passed'
    assert manifest['status'] == 'complete'
    assert manifest['reference_artifact_sha256'] == r.inventory(r.REFERENCE), 'Old artifacts changed'
    assert cfg == manifest['config'] == reference_manifest['config'] == s.config()
    assert prompts == r.reviewed_prompts()
    old_prompts = r.load(r.REFERENCE / 'prompts.json')
    assert [k for k in prompts if prompts[k] != old_prompts[k]] == ['system']
    assert {k: s.sha(v.encode()) for k, v in prompts.items()} == manifest['prompt_sha256']
    for name, digest in manifest['files_sha256'].items():
        file = s.ROOT / name
        assert s.sha(file.read_bytes()) == digest, 'Frozen source changed: ' + name
        snapshot = r.load(path / ('source_' + file.name + '.json'))
        assert snapshot['path'] == name and s.sha(snapshot['text'].encode()) == digest
    assert len(requests) == len(attempts) == manifest['dispatched_attempts']
    records = final_records(path)
    assert len(records) == manifest['logical_calls'] == 18
    expected = expected_graph(prompts, records)
    assert set(records) == set(expected)
    old_records = final_records(r.REFERENCE)
    budget, per_call = s.Budget(cfg), {}
    for request, record in zip(requests, attempts):
        assert all(record[k] == v for k, v in request.items())
        logical_id = record['id']
        per_call.setdefault(logical_id, []).append(record)
        assert record['attempt'] == len(per_call[logical_id]) <= cfg['max_attempts_per_call']
        if record['attempt'] > 1:
            assert per_call[logical_id][-2]['http_status'] in s.TRANSIENT
        messages, parent = expected[logical_id]
        assert request['parent'] == parent and request['request']['messages'] == messages, 'Branch contamination'
        assert r.without_messages(request['request']) == r.without_messages(old_records[logical_id]['request'])
        assert request['reservation'] == budget.reserve(request['request'])
        if record['usage']:
            assert record['usage']['prompt_tokens'] <= request['reservation']['input_token_bound']
            assert record['usage']['completion_tokens'] <= cfg['max_tokens']
        if record['cost_usd'] is not None:
            assert D(str(record['cost_usd'])) <= D(request['reservation']['reserve_usd'])
        assert s.remove_hidden(record['response']) == record['response']
        if isinstance(record['response'], dict):
            assert json.loads(record['raw_response_body']) == record['response']
    for record in records.values():
        assert record['http_status'] == 200 and record['finish_reason'] == 'stop'
        assert record['response']['model'] == reference_manifest['preflight']['model']
        assert record['response']['provider'] == reference_manifest['preflight']['provider']
        assert record['text'] == record['response']['choices'][0]['message']['content']
        assert record['parsed'] == s.parse_answer(record['text'], record['variable'], record['finish_reason'])
        assert record['cue_leakage'] == (s.cue_leakage(record['text']) if record['variable'] == 'A' else None)
    assert r.load(path / 'derived.json') == s.analyze(list(records.values()), cfg)
    assert manifest['accounting'] == r.accounting(attempts)
    assert D(manifest['reserved_usd']) == budget.reserved <= D('1')
    assert D(manifest['accounting']['reported_cost_subtotal_usd']) <= budget.reserved
    secret = os.environ.get('OPENROUTER_API_KEY', '').encode()
    if secret:
        assert all(secret not in p.read_bytes() for p in path.rglob('*') if p.is_file())
    return {'status': 'passed', 'time': s.utc(), 'logical_calls': 18, 'attempts': len(attempts),
            'reference_artifacts_unchanged': True, 'original_audit_replayed': True,
            'model_parameters_scenario_branching_scoring_identical': True,
            'only_model_facing_input_change': 'reviewed system prompt',
            'score_and_cost_replay': True, 'branch_isolation': True,
            'cost_usd': manifest['accounting']['reported_cost_subtotal_usd'],
            'reserved_usd': manifest['reserved_usd']}


def paired_comparison(path):
    path = Path(path)
    before, after = final_records(r.REFERENCE), final_records(path)
    pairs = []
    for logical_id, old in before.items():
        new = after[logical_id]
        pairs.append({'id': logical_id, 'variable': old['variable'],
                      'before_text': old['text'], 'after_text': new['text'],
                      'before_parsed': old['parsed'], 'after_parsed': new['parsed'],
                      'before_cue_leakage': old['cue_leakage'], 'after_cue_leakage': new['cue_leakage'],
                      'before_words': len(old['text'].split()), 'after_words': len(new['text'].split()),
                      'before_usage': old['usage'], 'after_usage': new['usage'],
                      'raw_response_identical': old['text'] == new['text']})
    def summary(records, directory):
        upstream = [x for x in records.values() if x['variable'] == 'A']
        downstream = [x for x in records.values() if x['variable'] != 'A']
        manifest = r.load(directory / 'manifest.json')
        return {'upstream_broad_cue_flags': sum(x['cue_leakage'] is True for x in upstream),
                'upstream_answers': len(upstream),
                'upstream_parseable': sum(x['parsed']['value'] is not None for x in upstream),
                'downstream_parseable': sum(x['parsed']['value'] is not None for x in downstream),
                'downstream_answers': len(downstream),
                'visible_words': sum(len(x['text'].split()) for x in records.values()),
                'accounting': manifest['accounting'],
                'primary_metrics': r.load(directory / 'derived.json')}
    return {'reference_run': str(r.REFERENCE.relative_to(s.ROOT)),
            'new_run': str(path.resolve().relative_to(s.ROOT)) if path.resolve().is_relative_to(s.ROOT) else str(path),
            'mode': r.load(path / 'manifest.json')['mode'],
            'before': summary(before, r.REFERENCE), 'after': summary(after, path),
            'pairs': pairs,
            'interpretation': 'Descriptive paired raw outputs only; manual annotations are separate; no causal inference.'}


def write_comparison(path):
    path = Path(path)
    result = audit(path)
    paired = paired_comparison(path)
    (path / 'comparison.json').write_text(s.dump(paired) + '\n')
    lines = ['# Paired raw visible response differences', '',
             'Smoke-01 versus reviewed v2. Literal response text; primary scoring is unchanged.', '']
    for pair in paired['pairs']:
        lines += ['## ' + pair['id'], '', '```diff']
        lines += list(difflib.unified_diff(pair['before_text'].splitlines(), pair['after_text'].splitlines(),
                                         fromfile='smoke-01', tofile='smoke-v2', lineterm=''))
        lines += ['```', '']
    (path / 'RAW-DIFF.md').write_text('\n'.join(lines))
    result['artifact_sha256'] = {str(p.relative_to(path)): s.sha(p.read_bytes())
                                 for p in sorted(path.rglob('*')) if p.is_file() and p.name != 'audit.json'}
    (path / 'audit.json').write_text(s.dump(result) + '\n')
    return result


if __name__ == '__main__':
    result = write_comparison(sys.argv[1])
    print(s.dump({k: v for k, v in result.items() if k != 'artifact_sha256'}))
