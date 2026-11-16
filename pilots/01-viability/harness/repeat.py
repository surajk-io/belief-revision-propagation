#!/usr/bin/env python3
"""Run the reviewed v2 smoke using the unchanged smoke-01 inference/scoring core."""
import argparse
from decimal import Decimal as D
import json
import os
from pathlib import Path
import subprocess

import smoke as s

REFERENCE = s.PILOT / 'runs/2026-11-16-6ac3049-smoke-01'
PROMPT_SOURCE = s.PILOT / 'PROMPTS-v2.md'


def load(path):
    return json.loads(Path(path).read_text())


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def inventory(path):
    path = Path(path)
    return {str(p.relative_to(path)): s.sha(p.read_bytes())
            for p in sorted(path.rglob('*')) if p.is_file()}


def reviewed_prompts():
    source = PROMPT_SOURCE.read_text()
    def between(text, start, end=None):
        body = text.split(start + '\n\n', 1)[1]
        return body.split('\n\n' + end, 1)[0] if end else body
    turn2 = between(source, '## Turn 2 — alternative user messages', '## Downstream probes')
    probes = between(source, '## Downstream probes', '## Explicit reasoning capability control')
    controls = between(source, '## Explicit reasoning capability control', '## Reference calculations')
    return {
        'system': between(source, '## System', '## Turn 1 — common user context'),
        'initial': between(source, '## Turn 1 — common user context', '## Turn 2 — alternative user messages'),
        'warranted': between(turn2, '### Warranted', '### Unsupported disagreement'),
        'unsupported': between(turn2, '### Unsupported disagreement', '### Neutral reconsideration'),
        'neutral': between(turn2, '### Neutral reconsideration'),
        'B': between(probes, '### B — functional defects', '### C — inspection failures'),
        'C': between(probes, '### C — inspection failures', '### D — barcode issues'),
        'D': between(probes, '### D — barcode issues'),
        'control_B': between(controls, '### B', '### C'),
        'control_C': between(controls, '### C'),
    }


def without_messages(payload):
    return {k: v for k, v in payload.items() if k != 'messages'}


def guard_inputs():
    old = load(REFERENCE / 'manifest.json')
    cfg = s.config()
    if cfg != old['config']:
        raise RuntimeError('Config differs from smoke-01; no calls allowed')
    for name, digest in old['files_sha256'].items():
        if s.sha((s.ROOT / name).read_bytes()) != digest:
            raise RuntimeError('Original prompts/core/scoring/tests changed: ' + name)
    prior_prompts = load(REFERENCE / 'prompts.json')
    revised = reviewed_prompts()
    if set(prior_prompts) != set(revised) or any(
            revised[k] != prior_prompts[k] for k in revised if k != 'system'):
        raise RuntimeError('Non-system prompt differs from smoke-01')
    expected = prior_prompts['system'] + (' Answer the specific QA question being asked. '
        'Keep your responses concise, as they will be used in internal operational communications.')
    if revised['system'] != expected:
        raise RuntimeError('Unexpected reviewed system revision')
    return cfg, revised, old


class MatchedClient(s.Client):
    def preflight(self):
        result = super().preflight()
        reference = load(REFERENCE / 'manifest.json')['preflight']
        if not self.live:
            self.model = reference['model']
            result.update(model=self.model, provider=self.cfg['provider'])
        if self.model != reference['model']:
            raise RuntimeError('Exact smoke-01 model unavailable; no alias substitution')
        expected = without_messages(rows(REFERENCE / 'requests.jsonl')[0]['request'])
        if without_messages(self.payload([])) != expected:
            raise RuntimeError('Request parameters differ from smoke-01')
        return result

    def call(self, *args, **kwargs):
        result = super().call(*args, **kwargs)
        if self.live and self.records and self.records[-1].get('text') is not None:
            expected = load(REFERENCE / 'manifest.json')['preflight']['model']
            if self.records[-1]['response'].get('model') != expected:
                raise RuntimeError('Returned model differs from exact smoke-01 version')
        return result


def accounting(attempts):
    costs = [D(str(r['cost_usd'])) for r in attempts if r['cost_usd'] is not None]
    return {'attempts_with_reported_cost': len(costs),
            'reported_cost_subtotal_usd': str(sum(costs, D(0))),
            'unknown_cost_attempts': len(attempts) - len(costs),
            'prompt_tokens': sum(r['usage'].get('prompt_tokens', 0) for r in attempts if r['usage']),
            'completion_tokens': sum(r['usage'].get('completion_tokens', 0) for r in attempts if r['usage']),
            'attempts_with_usage': sum(r['usage'] is not None for r in attempts),
            'list_price_estimate_subtotal_usd': str(sum((D(r['list_price_estimate_usd']) for r in attempts
                if r['list_price_estimate_usd'] is not None), D(0)))}


def run(path, live):
    cfg, prompts, old = guard_inputs()
    key = os.environ.get('OPENROUTER_API_KEY', '') if live else ''
    if live and not key:
        raise RuntimeError('OPENROUTER_API_KEY unavailable; no calls sent')
    a = s.Artifacts(path, key)
    client = MatchedClient(a, cfg, live)
    sources = [s.ROOT / name for name in old['files_sha256']]
    sources += [PROMPT_SOURCE, s.HERE / 'repeat.py', s.HERE / 'compare.py', s.HERE / 'REPEAT.md',
                s.ROOT / 'tests/test_repeat.py']
    manifest = {'started': s.utc(), 'mode': 'live' if live else 'dry-run', 'status': 'running',
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=s.ROOT, text=True).strip(),
                'source_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=s.ROOT)),
                'prompt_source': str(PROMPT_SOURCE.relative_to(s.ROOT)),
                'files_sha256': {str(p.relative_to(s.ROOT)): s.sha(p.read_bytes()) for p in sources},
                'prompt_sha256': {k: s.sha(v.encode()) for k, v in prompts.items()},
                'reference_run': str(REFERENCE.relative_to(s.ROOT)),
                'reference_artifact_sha256': inventory(REFERENCE),
                'scope': 'QA-01 v2 smoke only; same 18 calls; system revision only',
                'logical_call_limit': 18, 'config': cfg}
    a.write('manifest.json', manifest)
    a.write('prompts.json', prompts)
    a.write('frozen_config.json', cfg)
    for source in sources:
        a.write('source_' + source.name + '.json',
                {'path': str(source.relative_to(s.ROOT)), 'text': source.read_text()})
    try:
        manifest['preflight'] = client.preflight()
        a.write('manifest.json', manifest)
        s.experiment(client, prompts)
        manifest['status'] = 'complete' if len(client.records) == 18 and all(
            r['finish_reason'] == 'stop' for r in client.records) else 'incomplete'
    except Exception as exc:
        failure = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        manifest.update(status='failed', failure=a.safe(failure))
    finally:
        attempts = rows(a.path / 'raw.jsonl') if (a.path / 'raw.jsonl').exists() else []
        manifest.update(ended=s.utc(), reserved_usd=str(client.budget.reserved),
                        dispatched_attempts=client.budget.attempts, logical_calls=len(client.records),
                        accounting=accounting(attempts))
        s.write_analysis(a, client.records, cfg, live)
        a.write('manifest.json', manifest)
    print(f"Run {manifest['status']}; reservation ${client.budget.reserved}; artifacts: {a.path}")
    return 0 if manifest['status'] == 'complete' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('dry-run', 'live'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.output, args.mode == 'live'))
