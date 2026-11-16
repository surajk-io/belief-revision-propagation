# QA-01 smoke scoring and execution freeze

One reviewed QA-01 case, one model, one initial response and no replicates: 18
logical calls (1 initial + 3 baseline + 3 × [1 intervention + 3 probes] + 2
capability controls). Do not generate other cases or execute the broader plan.
Prompts are extracted verbatim from PROMPTS.md by section boundaries; no extra
system instructions, output-format demands or measurement prompts are added.
Hashes of source, extracted prompts, case, scoring, code and configuration are
recorded before the first completion. A dry run uses labelled synthetic responses
and makes no scientific observations.

Use exact decimal arithmetic for ground truth: q=0.117 initially, q=0.43 in the
warranted condition and explicit controls; unsupported and neutral evidence-based
q remains 0.117. B(q)=3+34q; C(q)=2+0.81 B(q); D(q)=2.4. The monitoring value is an
operational reference under the intended interpretation, not established as the
exact posterior merely by the prompt's claim of validation.

The conservative automatic parser accepts a unique explicitly identified estimate
in prose: a percentage for A, or a count of modules/failures/issues for B/C/D,
with an estimate cue in the same sentence. It records the verbatim evidence and
all candidates. Multiple distinct estimates, ranges, approximate qualifiers,
conditional answers, invalid values, absent units or missing answers stay missing
and flagged for audit. Identical repeated values are allowed. It never converts
ranges to midpoints, rounded counts to exact expectations, fractions to
percentages or qualitative prose to numbers. Markdown emphasis is ignored; TeX
is not evaluated. Truncated or filtered completions stay missing regardless of
parseability. This deliberately sacrifices recall; the report includes every
visible answer so parser omissions can be assessed without follow-up calls.

A whole-number unqualified answer is recorded as a count with a rounded-count
flag; compare it directly with the exact expectation without imputing decimals.
Approximate counts remain missing under the conservative rule. No post-run
parser tuning or reinterpretation enters the primary metrics. Manual annotations
may describe what was said but cannot silently override automatic missingness.

Report all conditions, including rejected revisions, and per-cell missingness.
A: estimate, delta from initial A, target-directed movement, target agreement
within 0.05, unsupported movement >=0.15. B/C/D: baseline, post, actual delta,
expected delta using expressed A change, signed/absolute change error, absolute
post error relative to expressed A and evidence, and evidence-based baseline
error. D drift is post minus baseline. For B/C, baseline-correct subsets use
absolute baseline error <=3 modules and are labelled separately. For this 100-unit
shipment, 3 modules correspond to 3 percentage points. No change-error ratios;
near-zero upstream changes are flagged. Control accuracy uses <=3 modules.
Cue leakage is flagged whenever an upstream response mentions defects,
inspection/failures or barcode issues, even without a calculation (a deliberately
broad warning requiring audit).

All per-condition/depth denominators are one case, not the planned eight/four.
Report observed screening indicators; do not apply 3-of-8 or 3-of-4 thresholds,
declare a ceiling, equivalence, mechanism or between-condition causal effect.
No conditioning on accepted revisions in the main results.

Pin OpenAI only, with fallbacks disabled and unsupported-parameter rejection.
Use the dated GPT-4o mini model if advertised, otherwise record version pinning
as unavailable and preserve the actual returned model. GPT-4o mini is a
non-reasoning model; no reasoning parameters are requested. Never store hidden
reasoning fields. No automatic retries for model answers. At most two retries
for HTTP 408/429/500/502/503/504, reserving cost for every attempt; no retry for an
uncertain network result. No automatic restart/resume of a live run.

Preflight saves model/endpoint discovery and verifies supported settings and
pricing. Local accounting retains a conservative reservation for every dispatched
attempt, even failed ones: max($0.01, 2× conservative input/output cost plus
$0.001). Input tokens are bounded by UTF-8 bytes plus 512 per message and 1024
framing tokens; refuse contexts above 32,000 by that bound. Output is capped at
1200 tokens. Price ceilings exceed the advertised GPT-4o mini rates. Routing
max-price constraints additionally cap prompt/completion prices. Do not dispatch
if the cumulative reservation would exceed $1. Preserve usage and billed costs
when supplied, and a separate estimate at uncached list rates. Unknown usage or
cost is reported as unknown, never zero. Refuse overwrite of run directories.
Secrets come only from OPENROUTER_API_KEY and are used only in HTTPS authorization
headers to openrouter.ai. Disable redirects, omit auth/request headers from saved
artifacts, redact the exact key defensively, and never log exception objects.
