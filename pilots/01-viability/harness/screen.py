#!/usr/bin/env python3
"""Fixed cross-model QA-01 V3 screens; per-batch aggregate $1 reservation ledger."""
import argparse
import copy
from decimal import Decimal as D
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

import repeat as base
import repeat_v3 as v3
import smoke as s

BATCHES = {
    1: ('openai/gpt-4.1-mini', 'meta-llama/llama-4-scout', 'deepseek/deepseek-v4.1-flash'),
    2: ('google/gemini-2.5-flash', 'meta-llama/llama-3.1-8b-instruct', 'qwen/qwen3.5-9b', 'google/gemma-4-26b-a4b-it'),
}
REFERENCE = s.PILOT / 'runs/2026-11-16-f78a5fc-smoke-03'
load, rows, inventory = base.load, base.rows, base.inventory
utc, message, remove_hidden = s.utc, s.message, s.remove_hidden
API = s.API
parse_answer, cue_leakage, TRANSIENT = s.parse_answer, s.cue_leakage, s.TRANSIENT


def slug(model):
    return model.replace('/', '--')


def sources():
    previous = load(REFERENCE / 'manifest.json')
    return list(dict.fromkeys([s.ROOT / p for p in previous['files_sha256']] + [
        s.PILOT / 'CROSS-MODEL-SCREEN.md', s.PILOT / 'CROSS-MODEL-SCREEN-BATCH-2.md',
        s.HERE / 'screen.py', s.HERE / 'screen_audit.py', s.HERE / 'SCREEN.md',
        s.ROOT / 'tests/test_screen.py']))


def select(model, catalog, endpoints):
    if model not in catalog or not endpoints:
        return {'candidate': model, 'status': 'skip_unavailable', 'reason': 'No catalog entry or live endpoints'}
    meta = catalog[model]
    reasoning = meta.get('reasoning')
    if reasoning and reasoning.get('mandatory') is True:
        return {'candidate': model, 'status': 'skip_incompatible', 'reason': 'Reasoning is mandatory'}
    eligible, exclusions = [], []
    for endpoint in endpoints:
        supported = set(endpoint['supported_parameters'])
        reason = None
        if endpoint['status'] != 0 or endpoint.get('service_tier') is not None:
            reason = 'Unavailable or non-standard service tier'
        elif not {'max_tokens', 'temperature', 'top_p'} <= supported:
            reason = 'Required inference settings unsupported'
        elif (endpoint.get('max_completion_tokens') or 0) < 1200:
            reason = 'Insufficient output capacity'
        elif D(str(endpoint['pricing'].get('request', 0))) != 0:
            reason = 'Additional per-request fee'
        elif reasoning is not None and (reasoning.get('mandatory') is not False or 'reasoning' not in supported):
            reason = 'Cannot establish explicit optional-reasoning disable'
        if reason:
            exclusions.append({'tag': endpoint['tag'], 'reason': reason})
            continue
        try:
            prompt, completion = D(endpoint['pricing']['prompt']), D(endpoint['pricing']['completion'])
            if prompt <= 0 or completion <= 0:
                raise ValueError('Nonpositive price')
        except (KeyError, ValueError, ArithmeticError):
            exclusions.append({'tag': endpoint['tag'], 'reason': 'Invalid pricing'})
            continue
        eligible.append((int('seed' not in supported), 8000 * prompt + 1200 * completion, endpoint['tag'], endpoint))
    if not eligible:
        return {'candidate': model, 'status': 'skip_incompatible', 'reason': 'No comparable non-reasoning endpoint', 'exclusions': exclusions}
    _, cost, _, endpoint = min(eligible, key=lambda x: x[:3])
    canonical = meta.get('canonical_slug', model)
    request_model = canonical if canonical in catalog else model
    parameters = {'temperature': 0, 'top_p': 1, 'max_tokens': 1200}
    unsupported = []
    if 'seed' in endpoint['supported_parameters']:
        parameters['seed'] = 20261116
    else:
        unsupported.append('seed')
    if reasoning is not None:
        parameters['reasoning'] = {'enabled': False, 'exclude': True}
    return {'candidate': model, 'status': 'selected', 'request_model': request_model,
            'allowed_returned_models': sorted({model, canonical, request_model}),
            'canonical_slug': canonical, 'independent_version_pin_available': canonical in catalog and canonical != model,
            'provider_name': endpoint['provider_name'], 'endpoint_tag': endpoint['tag'],
            'endpoint': endpoint, 'model_reasoning_metadata': reasoning,
            'parameters': parameters, 'unsupported_settings': unsupported,
            'reasoning_mode': 'explicitly_disabled' if reasoning is not None else 'non_reasoning_model_no_reasoning_parameter',
            'price_ceilings_usd_per_token': {k: str(D(endpoint['pricing'][k]) * D('1.25')) for k in ('prompt', 'completion')},
            'selection_cost_score_usd': str(cost), 'exclusions': exclusions}


def freeze(root):
    root = Path(root)
    if (root / 'plan.json').exists():
        raise FileExistsError('Frozen screen plan already exists')
    reference = load(REFERENCE / 'manifest.json')
    for name, digest in reference['files_sha256'].items():
        if s.sha((s.ROOT / name).read_bytes()) != digest:
            raise RuntimeError('Previous source/prompts/scoring changed: ' + name)
    prompts = v3.reviewed_prompts()
    if prompts != load(REFERENCE / 'prompts.json'):
        raise RuntimeError('V3 prompts differ from smoke-03')
    catalog = {m['id']: m for m in load(root / 'models-raw.json')['data']}
    choices = {}
    for batch, candidates in BATCHES.items():
        choices[str(batch)] = []
        for candidate in candidates:
            result = load(root / (slug(candidate) + '-endpoints.json'))
            choices[str(batch)].append(select(candidate, catalog, result.get('data', {}).get('endpoints', [])))
    plan = {'frozen_at': utc(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=s.ROOT, text=True).strip(),
            'source_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=s.ROOT)),
            'choices': choices, 'prompts': prompts, 'config': s.config(),
            'sources_sha256': {str(p.relative_to(s.ROOT)): s.sha(p.read_bytes()) for p in sources()},
            'discovery_sha256': {p.name: s.sha(p.read_bytes()) for p in sorted(root.glob('*')) if p.is_file()},
            'previous_artifacts': {str(p.relative_to(s.ROOT)): inventory(p) for p in sorted((s.PILOT / 'runs').iterdir()) if p.is_dir()},
            'aggregate_budget_usd_per_batch': '1.00', 'model_selection': 'status 0, standard tier, comparable settings; prefer seed, then 8000*input+1200*output price, then tag',
            'scope': 'Fixed batch 1 then fixed batch 2 only; one graph per candidate; no substitution or rerun'}
    (root / 'plan.json').write_text(s.dump(plan) + '\n')
    for source in sources():
        (root / ('source_' + source.name + '.json')).write_text(s.dump({'path': str(source.relative_to(s.ROOT)), 'text': source.read_text()}) + '\n')
    return plan


def verify_plan(root):
    root = Path(root)
    plan = load(root / 'plan.json')
    for name, digest in plan['sources_sha256'].items():
        if s.sha((s.ROOT / name).read_bytes()) != digest:
            raise RuntimeError('Frozen screen source changed: ' + name)
    for name, digest in plan['discovery_sha256'].items():
        if s.sha((root / name).read_bytes()) != digest:
            raise RuntimeError('Discovery changed after freezing')
    for name, hashes in plan['previous_artifacts'].items():
        if inventory(s.ROOT / name) != hashes:
            raise RuntimeError('Previous artifacts changed')
    return plan


class SharedBudget(s.Budget):
    def __init__(self, artifacts, cfg):
        super().__init__(copy.deepcopy(cfg))
        self.artifacts, self.context = artifacts, None

    def reserve(self, payload):
        # The unchanged original bound now uses the frozen endpoint-specific prices.
        self.cfg['input_token_rate_ceiling_usd'] = str(D(str(payload['provider']['max_price']['prompt'])) / 1000000)
        self.cfg['output_token_rate_ceiling_usd'] = str(D(str(payload['provider']['max_price']['completion'])) / 1000000)
        reservation = super().reserve(payload)
        self.artifacts.append('ledger.jsonl', {'context': self.context,
            'request_sha256': s.sha(s.dump(payload).encode()), 'reservation': reservation})
        return reservation


def hidden_trace_present(value):
    if isinstance(value, list):
        return any(hidden_trace_present(x) for x in value)
    if isinstance(value, dict):
        return any((k in ('reasoning', 'reasoning_details', 'encrypted_content') and bool(v)) or hidden_trace_present(v)
                   for k, v in value.items())
    return False


class ScreenClient(s.Client):
    def __init__(self, artifacts, cfg, live, selection, shared_budget):
        super().__init__(artifacts, cfg, live)
        self.selection, self.budget = selection, shared_budget
        self.model = selection['request_model']
        self.pricing = selection['endpoint']['pricing']

    def payload(self, messages):
        selected = self.selection
        return {'model': self.model, 'messages': copy.deepcopy(messages), **selected['parameters'],
                'stream': False, 'usage': {'include': True},
                'provider': {'only': [selected['endpoint_tag']], 'allow_fallbacks': False,
                             'require_parameters': True, 'max_price': {
                                 k: float(D(v) * 1000000) for k, v in selected['price_ceilings_usd_per_token'].items()}}}

    def call(self, logical_id, history, question, parent, variable):
        if len(self.records) >= self.cfg['max_logical_calls']:
            raise RuntimeError('Smoke-only logical call limit exceeded')
        self.budget.context = {'candidate': self.selection['candidate'], 'id': logical_id}
        messages = s.branch(history, question)
        payload = self.payload(messages)
        for attempt in range(1, self.cfg['max_attempts_per_call'] + 1):
            reservation = self.budget.reserve(payload)
            request = {'id': logical_id, 'parent': parent, 'variable': variable,
                       'attempt': attempt, 'started': utc(), 'request': payload,
                       'reservation': reservation}
            self.a.append('requests.jsonl', request)
            started = time.monotonic()
            status, raw, error, headers = None, '', None, {}
            if self.live:
                try:
                    req = urllib.request.Request(API + '/chat/completions',
                        data=json.dumps(payload).encode(), headers={
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + self.a.key}, method='POST')
                    with self.opener.open(req, timeout=60) as response:
                        status = response.status
                        raw = response.read().decode('utf-8')
                        headers = {k: v for k, v in response.headers.items()
                                   if k.lower() in ('date', 'content-type', 'x-request-id')}
                except urllib.error.HTTPError as exc:
                    status = exc.code
                    raw = exc.read().decode('utf-8', errors='replace')
                    error = 'HTTPError'
                except (urllib.error.URLError, TimeoutError, OSError) as exc:
                    error = type(exc).__name__  # Do not log exception/request objects.
            else:
                texts = {'A': 'The estimated risk is 11.7%.', 'B': 'We expect 6.978 modules.',
                         'C': 'We expect 7.65218 inspection failures.', 'D': 'We expect 2.4 modules.'}
                if logical_id.startswith('warranted') or logical_id.startswith('control'):
                    texts.update(A='The estimated risk is 43%.', B='We expect 17.62 modules.',
                                 C='We expect 16.2722 inspection failures.')
                status = 200
                raw = json.dumps({'id': 'DRY-' + logical_id, 'model': self.model, 'provider': self.selection['provider_name'],
                                  'choices': [{'message': message('assistant', texts[variable]), 'finish_reason': 'stop'}]})
            try:
                response_data = json.loads(raw)
            except (ValueError, TypeError):
                response_data = None
            visible = remove_hidden(response_data)
            raw_visible = raw if visible == response_data else json.dumps(visible, ensure_ascii=False)
            record = {**request, 'ended': utc(), 'duration_seconds': time.monotonic() - started,
                      'http_status': status, 'response_headers': headers, 'error': error,
                      'raw_response_body': raw_visible, 'response': visible,
                      'hidden_fields_omitted': visible != response_data,
                      'hidden_trace_present': hidden_trace_present(response_data),
                      'usage': visible.get('usage') if isinstance(visible, dict) else None}
            record['cost_usd'] = record['usage'].get('cost') if record['usage'] else None
            usage = record['usage']
            record['list_price_estimate_usd'] = (str(
                D(usage['prompt_tokens']) * D(self.pricing['prompt']) +
                D(usage['completion_tokens']) * D(self.pricing['completion']))
                if usage and all(k in usage for k in ('prompt_tokens', 'completion_tokens')) else None)
            text, finish = None, None
            if status == 200 and isinstance(visible, dict) and visible.get('choices'):
                choice = visible['choices'][0]
                text = choice.get('message', {}).get('content')
                finish = choice.get('finish_reason')
            record['text'], record['finish_reason'] = text, finish
            record['parsed'] = parse_answer(text, variable, finish) if isinstance(text, str) else {
                'value': None, 'flags': ['api_failure_or_no_visible_answer'], 'candidates': [], 'evidence': []}
            record['cue_leakage'] = cue_leakage(text or '') if variable == 'A' else None
            self.a.append('raw.jsonl', record)
            print(f'{logical_id} attempt {attempt}: HTTP {status}; visible={isinstance(text, str)}', flush=True)
            if status in TRANSIENT and attempt < self.cfg['max_attempts_per_call']:
                time.sleep(min(2 ** attempt, 4))
                continue
            self.records.append(record)
            if self.live and isinstance(text, str):
                if visible.get('provider') != self.selection['provider_name'] or visible.get('model') not in self.selection['allowed_returned_models']:
                    raise RuntimeError('Returned provider/model differs from frozen selection')
                reasoning_tokens = (usage or {}).get('completion_tokens_details', {}).get('reasoning_tokens')
                if record['hidden_trace_present'] or (reasoning_tokens is not None and reasoning_tokens > 0):
                    raise RuntimeError('Non-reasoning configuration violated; candidate halted')
            if not isinstance(text, str) or finish != 'stop':
                return None
            return messages + [message('assistant', text)]
        raise AssertionError('Bounded loop exhausted unexpectedly')


def run_batch(root, number, live):
    root = Path(root)
    plan = verify_plan(root)
    if number == 2:
        first = root / 'batch-1'
        if not (first / 'manifest.json').exists() or load(first / 'manifest.json')['status'] != 'finished':
            raise RuntimeError('Batch 1 must finish before batch 2')
        if not (first / 'audit.json').exists() or load(first / 'audit.json')['status'] != 'passed':
            raise RuntimeError('Batch 1 offline audit required before batch 2')
    key = os.environ.get('OPENROUTER_API_KEY', '') if live else ''
    if live and not key:
        raise RuntimeError('OPENROUTER_API_KEY unavailable; no calls sent')
    a = s.Artifacts(root / ('batch-' + str(number)), key)
    budget = SharedBudget(a, plan['config'])
    manifest = {'batch': number, 'mode': 'live' if live else 'dry-run', 'started': utc(), 'status': 'running',
                'plan_sha256': s.sha((root / 'plan.json').read_bytes()), 'candidates': [],
                'maximum_logical_calls': 18 * len(BATCHES[number]), 'budget_usd': '1.00'}
    a.write('manifest.json', manifest)
    for selection in plan['choices'][str(number)]:
        candidate = selection['candidate']
        result = {'candidate': candidate, 'selection': selection, 'status': selection['status']}
        manifest['candidates'].append(result)
        if selection['status'] != 'selected':
            a.write('manifest.json', manifest)
            continue
        model_a = s.Artifacts(a.path / slug(candidate), key)
        cfg = copy.deepcopy(plan['config'])
        cfg.update(provider=selection['provider_name'], model_family=candidate, preferred_version=selection['request_model'],
                   input_token_rate_ceiling_usd=selection['price_ceilings_usd_per_token']['prompt'],
                   output_token_rate_ceiling_usd=selection['price_ceilings_usd_per_token']['completion'])
        client = ScreenClient(model_a, cfg, live, selection, budget)
        model_manifest = {'candidate': candidate, 'started': utc(), 'status': 'running', 'mode': manifest['mode'],
                          'selection': selection, 'config': cfg, 'plan_sha256': manifest['plan_sha256']}
        model_a.write('manifest.json', model_manifest)
        model_a.write('prompts.json', plan['prompts'])
        model_a.write('frozen_config.json', cfg)
        try:
            s.experiment(client, plan['prompts'])
            result['status'] = 'complete' if len(client.records) == 18 and all(r['finish_reason'] == 'stop' for r in client.records) else 'incomplete'
        except Exception as exc:
            result['status'] = 'failed'
            result['failure'] = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        finally:
            attempts = rows(model_a.path / 'raw.jsonl') if (model_a.path / 'raw.jsonl').exists() else []
            model_manifest.update(ended=utc(), status=result['status'], failure=result.get('failure'),
                                  logical_calls=len(client.records), attempts=len(attempts), accounting=base.accounting(attempts))
            result.update(logical_calls=len(client.records), attempts=len(attempts), accounting=model_manifest['accounting'])
            s.write_analysis(model_a, client.records, cfg, live)
            model_a.write('manifest.json', model_manifest)
            a.write('manifest.json', manifest)
    manifest.update(status='finished', ended=utc(), reserved_usd=str(budget.reserved), dispatched_attempts=budget.attempts,
                    logical_calls=sum(x.get('logical_calls', 0) for x in manifest['candidates']),
                    reported_cost_subtotal_usd=str(sum((D(x['accounting']['reported_cost_subtotal_usd']) for x in manifest['candidates'] if 'accounting' in x), D(0))),
                    unknown_cost_attempts=sum(x['accounting']['unknown_cost_attempts'] for x in manifest['candidates'] if 'accounting' in x))
    a.write('manifest.json', manifest)
    print(f"Batch {number} finished; reserved ${budget.reserved}; reported ${manifest['reported_cost_subtotal_usd']}")
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('freeze', 'dry-run', 'live'))
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--batch', type=int, choices=(1, 2))
    args = parser.parse_args()
    if args.mode == 'freeze':
        result = freeze(args.root)
        print(s.dump({k: v for k, v in result['choices'].items()}))
    else:
        if not args.batch:
            parser.error('--batch is required for execution')
        run_batch(args.root, args.batch, args.mode == 'live')
