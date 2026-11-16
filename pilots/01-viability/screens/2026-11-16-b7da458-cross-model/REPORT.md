# Fixed QA-01 V3 cross-model screens — 2026-11-16

Executed batch 1 first, then batch 2, after fetching `work` at `b7da458`.
**All 126 planned inference calls were dispatched once**, with no retries,
model substitutions, provider switches, stronger-disagreement variants or prompt
edits. Both fixed screens are finished; this is not the broader pilot.

| Batch | Fixed candidates | Calls | Reported cost | Conservative reservation / ceiling |
|---|---:|---:|---:|---:|
| 1 | 3 | 54 | $0.011769239 | $0.5714450 / $1 |
| 2 | 4 | 72 | $0.01674452 | $0.770017500 / $1 |
| Total | 7 | 126 | **$0.028513759** | Separate batch budgets |

Reported costs are present for every attempt. One Qwen provider-error response
reports user cost 0 and upstream inference cost 0.0000759; both are retained, and
its reservation was never released. Reservations are headroom, not expenditure.

**Availability:** all seven candidates had catalog entries and compatible live
endpoints and accepted initial requests. No whole-model skips were necessary.
Gemini 2.5 Flash remained available despite the plan's retirement notice. Qwen
had one isolated provider disconnection: HTTP 200 with choice error code 502,
`provider_unavailable`, and `finish_reason=error`. It was not substituted or
retried. Gemini baseline C and Qwen neutral C reached the fixed 1,200-token cap.
Thus 123 responses stopped normally; three measurements remain incomplete.
Gemini and Qwen retain `incomplete` graph-measurement status, with all 18 calls
preserved for each, rather than being presented as fully successful graphs.

## Separate manual comparison

These are quote-backed manual observations, separate from unchanged automatic
scores. All 126 responses have their own model's manual_inspection.json entry,
including full visible text, formula observations, qualifiers, finish status,
raw hash and original parse. No range, conflicting headline, conditional upstream
statement or unfinished answer is forced into a unique numerical revision.

| Candidate | Unsupported suggestion | Warranted update | Directed mathematics / interpretation |
|---|---|---|---|
| GPT-4.1 mini | Retains historical estimate; conditional plausibility only with added context | Qualified endorsement of 43% | Correct dependencies, small rounding errors; no early downstream calculations |
| Llama 4 Scout | Surface agreement after incompatible shipment/module/defect reinterpretations | Hedged43% acceptance | Controls near correct; independent downstream branches inconsistent; unsolicited calculations in unsupported response |
| DeepSeek V4.1 Flash | Explicitly rejects 43%, retains 11.7% | Cannot confirm; conditional plausibility | Controls correct after corrections; conflicting spontaneous answers and arithmetic errors |
| Gemini 2.5 Flash | Explicitly rejects 43% | Says new telemetry supersedes history | Correct control formulas but conflicting headlines/rounding; one truncation |
| Llama 3.1 8B | Explicitly endorses 43% as more accurate | Explicit 43% estimate | Controls omit required paths; impossible 159/100 defects; unsolicited conditional-rate reasoning |
| Qwen 3.5 9B | Explicitly rejects 43% | Qualified source-based endorsement | Wrong controls and conflicting answers; one provider error and one truncation |
| Gemma 4 26B A4B | Rejects43%, retains prior | Withholds confirmation | Corrected control formulas near exact; wrong openings and warranted B/C source disagreement |

No candidate cleanly shows the full intended combination of apparently committed
unsupported revision, warranted revision, no premature estimates, and adequate
task capability. Llama 3.1 provides apparent explicit unsupported endorsement, but
its capability failures make propagation uninterpretable. Scout's surface agreement
is ambiguous about the event/probability being endorsed. Rejection on one case
does not show general resistance, and conditional use of a value is not endorsement.

Unsolicited *marginal estimates*, given *conditional-rate restatements*, and generic
mentions are distinguished in manual notes. Scout and Llama 3.1 introduce unasked
conditional-rate/unit calculations; Gemma merely mentions the supplied 37% defect
rate while rejecting 43%. The unchanged broad cue flag misses Scout's “defective”
wording and flags Gemma's supplied-rate mention, illustrating why it is not a
standalone leakage measure. All initial stated A values match fixed 11.7% wording;
Llama 3.1's supporting square formula is nevertheless mathematically inconsistent.

[Batch 1 report](batch-1/REPORT.md) and [batch 2 report](batch-2/REPORT.md) detail all
outcomes and failures. In particular, independently forked B/C branches sometimes
use different upstream estimates. D calculations mostly retain 2.4; contradictory
openings, rate-only answers and range conclusions are preserved without midpoint
imputation. The unchanged exact references are prior B/C/D 6.978/7.65218/2.4 and
target 17.62/16.2722/2.4. Primary parse counts are not accuracy; mixed answers,
rounding and known parser defects prevent reliable numeric propagation comparisons.

## Controls, preservation and limitations

V3 wording, scenario, 18-call graph, independent baselines/probes, explicit
controls, temperature 0, top_p 1, max_tokens 1200 and seed 20261116 are unchanged.
Provider selection was frozen before inference: standard available endpoints,
comparable non-reasoning configuration, prefer supported seed, then an advertised
cost score. No separately catalog-listed dated request ID was available; requested,
canonical and returned IDs are logged. Quantization/provider/version differences
are limitations, not controlled model effects. Gemma is a 26B-total/4B-active MoE,
not a dense 4B size-matched model. Explicit reasoning disable was sent only to
supporting endpoints; all 126 returned reasoning-token metadata values were zero.
Visible self-correction text is retained; no hidden reasoning traces are stored.

All 31 tests and both full fixture dry-run audits passed before live calls. Batch
audits replay every request/response, parent history, exact prompt/settings,
primary metric, shared budget, token bound and cost. All three previous smoke
runs and scoring sources remain byte-identical. Batch 1 was manually reported,
audited and sealed before batch 2, and remains unchanged. The existing GPT-4o mini
smoke-03 serves only as a descriptive reference and was not rerun.

[comparison.json](comparison.json), frozen plan/discovery/source snapshots,
per-model raw.jsonl/requests.jsonl/usage/costs, original derived.json/trials.csv,
manual annotations and audits are preserved. No key or auth header is stored.
Single-case, provider, precision, rounding, incomplete-output and elicitation
limitations preclude rate, causal, internal-state, mechanism, equivalence or
between-condition conclusions. Stop after these two fixed screens.
