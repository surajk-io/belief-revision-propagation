# QA-01 smoke harness

Python 3.12, standard library only. This implements only the reviewed QA-01 smoke
scope, not the eight-case pilot in PLAN.md. PROMPTS.md is read without edits.

From the repository root:

```sh
python -m unittest discover -s tests -v
python pilots/01-viability/harness/smoke.py dry-run --output /tmp/qa01-dry-unique
python pilots/01-viability/harness/audit.py /tmp/qa01-dry-unique
# OPENROUTER_API_KEY must already be securely supplied in the environment.
python pilots/01-viability/harness/smoke.py live --output pilots/01-viability/runs/DATE-COMMIT-smoke
python pilots/01-viability/harness/audit.py pilots/01-viability/runs/DATE-COMMIT-smoke
```

A run directory must not exist. No automatic resume, model substitution, provider
fallback, additional scenarios or response-dependent reruns. Live execution is an
explicit CLI mode. The key is never a CLI argument or saved header. The harness
uses HTTPS to openrouter.ai with redirects disabled. Discovery is public and
free. Live costs are bounded by a $1 conservative local reservation ledger plus
request token and provider price ceilings; unused reservations are not released.
The safety budget applies to one invocation; do not start additional live runs.

SCORING.md fixes the interpretation and conservative parser before execution.
Approximate/ranged/conditional or multiple distinct estimates remain missing;
all responses remain available for manual audit. The initial and intervention
assistant messages are the only model outputs reused as history. Each baseline,
post-intervention and control measurement branches independently.

Artifacts:

- `manifest.json`: timestamps, source hashes, frozen config, model/provider
  discovery, pricing, run status, token totals, cost completeness and reserves.
- `prompts.json`, `frozen_config.json`, `source_*.json`: exact frozen inputs/code.
- `discovery.jsonl`: raw public model and endpoint availability metadata.
- `requests.jsonl`: durably recorded before each attempt; excludes auth headers.
- `raw.jsonl`: every response/error, exact request config, raw visible response
  envelope, parsed JSON, provider/model metadata, usage, actual/estimated cost,
  parsing flags and branch parent. Hidden reasoning fields are excluded if any
  provider unexpectedly supplies them; omissions are marked.
- `derived.json`, `trials.csv`: unfiltered per-condition observations, change/error
  metrics, missingness, explicit-control accuracy and baseline-correct subsets.
- `RESPONSES.md`: all verbatim visible answers and automatic scores.
- `audit.json`: offline graph, provenance, budget and score-replay verification.

Dry-run responses are synthetic fixtures labelled as such and have no reported
usage or costs. No scientific observations may be inferred from them. Failed or
incomplete live runs are retained. The harness does not interpret internal state
or compute significance, equivalence or causal effects.
