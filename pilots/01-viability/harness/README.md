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

## Reviewed v2 smoke repeat

The separately authorized repeat uses PROMPTS-v2.md. The original executable,
scoring rules, configuration, tests and run artifacts remain unchanged.
`repeat.py` imports the original inference/scoring code and refuses changes to
any non-system prompt, model, provider or request parameter. See REPEAT.md for
the scope and separate manual-inspection protocol.

```sh
python -m unittest discover -s tests -v
python pilots/01-viability/harness/repeat.py dry-run --output /tmp/qa01-v2-dry-unique
python pilots/01-viability/harness/compare.py /tmp/qa01-v2-dry-unique
# One newly authorized live invocation; key supplied securely in the environment.
python pilots/01-viability/harness/repeat.py live --output pilots/01-viability/runs/DATE-COMMIT-smoke-02
python pilots/01-viability/harness/compare.py pilots/01-viability/runs/DATE-COMMIT-smoke-02
```

`compare.py` audits both runs without writing to smoke-01, checks saved history
isolation, configuration identity, frozen source and original artifact hashes,
then writes paired `comparison.json`, literal `RAW-DIFF.md` and `audit.json` in
the new directory. Run it again after adding manual notes/report to inventory
those artifacts. Primary automatic metrics remain in derived.json/trials.csv;
manual interpretations belong in manual_inspection.json and REPORT.md.

## Reviewed v3 smoke repeat

V3 changes the system scope instruction and all three intervention messages.
`repeat_v3.py` checks the exact reviewed changes and imports the unchanged model,
request, branching, budget and scoring code. It preserves inventories of both
previous runs; `compare_v3.py` replays both earlier audits without writing there.
See V3.md for the frozen manual endorsement, leakage and mathematics protocol.

```sh
python -m unittest discover -s tests -v
python pilots/01-viability/harness/repeat_v3.py dry-run --output /tmp/qa01-v3-dry-unique
python pilots/01-viability/harness/compare_v3.py /tmp/qa01-v3-dry-unique
# One authorized live invocation, key supplied through the environment.
python pilots/01-viability/harness/repeat_v3.py live --output pilots/01-viability/runs/DATE-COMMIT-smoke-03
python pilots/01-viability/harness/compare_v3.py pilots/01-viability/runs/DATE-COMMIT-smoke-03
```

V3 comparison.json pairs all 18 responses against each earlier run; literal
RAW-DIFF-v1.md/RAW-DIFF-v2.md and audit.json are written only in the new directory.
The audit flags disagreement or missingness relative to the fixed 11.7% wording.
No automatic score is replaced by manual observations. A v3 response alone cannot
isolate effects of scope versus intervention wording changes.

## Fixed cross-model screens

`screen.py` implements the authorized batch 1 followed by batch 2, importing the
original V3 graph/scoring without changes. See SCREEN.md for frozen selection,
reasoning, shared-budget and manual-inspection rules. Discovery is saved publicly
before `freeze`; endpoints are chosen once from availability/settings/pricing.
Each model has a separate artifact directory; each batch has one aggregate $1
reservation ledger. Batch 2 requires batch 1 to finish and pass its audit.

```sh
python -m unittest discover -s tests -v
python pilots/01-viability/harness/screen.py freeze --root DISCOVERY_ROOT
python pilots/01-viability/harness/screen.py live --root DISCOVERY_ROOT --batch 1
python pilots/01-viability/harness/screen_audit.py DISCOVERY_ROOT 1
python pilots/01-viability/harness/screen.py live --root DISCOVERY_ROOT --batch 2
python pilots/01-viability/harness/screen_audit.py DISCOVERY_ROOT 2
```

Use `dry-run` in place of `live` on a separate copied discovery directory for
fixtures. Neither a batch nor a model directory can be reused or resumed.
Keep manual_inspection.json and reports separate from primary derived.json and
trials.csv; rerun only the offline audit after adding annotations. Unsupported
configurations and unavailable IDs are retained as skips, with no substitution.
The existing smoke-03 reference is read without rerunning GPT-4o mini.
