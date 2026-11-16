# QA-01 v2 smoke repeat protocol

Authorized scope: one 18-call smoke test with PROMPTS-v2.md, compared with
2026-11-16-6ac3049-smoke-01. No other scenarios, replicates, prompt edits or pilot.

Reuse smoke.py's Client, experiment, Budget, ground, parse_answer, cue_leakage,
analyze and write_analysis without modifications. Preserve config.json,
SCORING.md and tests/test_smoke.py byte for byte. The repeat runner checks their
hashes against the original manifest before dispatch. It requires the exact
previous dated model, provider and complete request settings (excluding messages)
to match; version unavailability stops the run without model substitution.
Extract all ten reviewed v2 messages verbatim; only the system message may differ
from the original. Use the original graph, seed, temperature, top_p, output cap,
transient retry policy and $1 conservative budget. No paid connectivity call.

Freeze source, prompts, config and all old artifact hashes before live dispatch.
No changes to automatic scoring after observing new responses. New artifacts
are written to a separate exclusive-create run directory. Failed attempts and
all usage/cost metadata are retained by the original Client. Offline comparison
and audits make no inference requests and never rewrite the original run.

Report broad automatic cue_leakage flags unchanged. Separately inspect all four
upstream answers in each run for volunteered downstream estimates, preserving
verbatim evidence. Generic mentions of inspection, defects or barcodes are
not themselves numeric downstream estimates; label these distinctions in manual
annotations rather than altering automatic flags. Do not equate a planning
recommendation with a probability estimate.

Manually inspect every paired visible answer. Record exact quotations, stated
point/range/conditional/qualitative status, displayed calculations, and any
interpretive uncertainty in manual_inspection.json. A single approximate point
may be described as such in the manual comparison. Do not force ranges to
midpoints, erase caveats, or turn conditional hypothetical answers into committed
revisions. Primary numeric missingness is retained unchanged. Any descriptive
arithmetic on manually transcribed points is labelled supplementary, with the
source quotes and no change to derived.json or trials.csv.

Pair raw responses by logical call ID and save comparison.json plus RAW-DIFF.md.
Compare upstream adoption/rejection, observed downstream pattern, D stability,
capability controls, response length, cue leakage, parsing completeness and costs.
The two single-case runs cannot establish a causal system-prompt effect,
mechanism, equivalence or reliable viability rate; seed and temperature do not
ensure deterministic providers. Preserve inconclusive outcomes. Stop after the
smoke test, report the comparison, commit and push.
