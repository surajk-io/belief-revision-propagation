# GAME-01 harness

Python standard library only. Reuses QA-01 ScreenClient for HTTP, routing,
security and bounded retries; a serialized scenario adapter replaces only derived
probability/cue fields before recording. The old transport, QA scoring and all
previous artifacts remain unchanged. Exact Fraction math, probability-only
parsing, a six-worker dependency scheduler and atomic budget settlement are local
to this pilot. See SCORING-AND-EXECUTION.md for the pre-live freeze.

The reviewed PLAN-AND-PROMPTS.md is read verbatim. No additional questions are
inserted. Same candidate/provider endpoints as each previous QA screen are
required; unsupported/unavailable pins are skipped with no substitution.
Only the authorized output cap changes to 4096. The three model graphs share one
six-worker pool and one $1 spent-plus-outstanding budget; known-cost settlement
releases unused token-cap headroom, while uncertain requests keep their full cap.

From the repository root, with public discovery files already saved:

```sh
python -m unittest discover -s tests -v
python pilots/02-gaming-viability/harness/gaming.py freeze --root DISCOVERY_ROOT
# Run a dry copy with the same frozen sources before live execution.
python pilots/02-gaming-viability/harness/gaming.py dry-run --root DRY_DISCOVERY_ROOT
python pilots/02-gaming-viability/harness/gaming_audit.py DRY_DISCOVERY_ROOT
# OPENROUTER_API_KEY is supplied securely through the environment.
python pilots/02-gaming-viability/harness/gaming.py live --root DISCOVERY_ROOT
python pilots/02-gaming-viability/harness/gaming_audit.py DISCOVERY_ROOT
```

Each root's experiment directory is exclusive-create, with no automatic restart
or resume. The public model/endpoint discovery files and source/prompt/config
snapshots are frozen before completions. All logical IDs remain stable, while
ledger.jsonl records atomic reserve/settle order, execution.jsonl records actual
physical-attempt dispatch/completion order and concurrency, and scheduler.jsonl
records eligibility, task outcomes and blocked descendants. Each model's own
requests/raw/usage/costs, primary derived.json/trials.csv and RESPONSES.md are
separate. The offline audit verifies graph topology, exact histories, timestamps/
ordering, pins, game scores, concurrency and budget exposure. Manual annotations
and comparative reports are added separately and do not overwrite primary data.
No hidden reasoning is retained. Dry fixture responses are labelled synthetic
and never support experimental conclusions.
