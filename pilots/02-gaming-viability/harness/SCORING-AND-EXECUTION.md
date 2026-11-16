# GAME-01 frozen scoring and execution rules

Exactly three specified candidates, one 18-call graph each, no additional runs.
Extract ten messages verbatim from PLAN-AND-PROMPTS.md. Intervention messages
contain only their first paragraph; the explanatory notes after Neutral are not
sent. Do not append follow-up questions or change targets based on an answer.

Math uses exact Fraction arithmetic: q=1972/4883 after the grey icon;
B=.76-.52q; C=.12+.71B; D=.09. Target q=.69 is the intended tracker posterior
already incorporating icon and clue. Unsupported/neutral evidential q stays at
1972/4883. Preserve doubts about whether the tracker output is that posterior.
Exact reference fractions and decimal displays are frozen. Coherence uses a
uniquely parsed expressed A; missing, qualitative, acknowledgment or hypothetical
answers do not receive an imputed q. Initial errors are retained. Expected B/C
changes have slopes -.52 and -.3692; D change is zero. No ratios near zero.

New game parser applies probability semantics to every variable, with no count
or shipment interpretation. It accepts a unique explicit point percentage, or a
0-to-1 decimal explicitly labelled as a probability. Approximate single points
are accepted with an approximation flag; their reported precision is retained.
Split ordinary sentences without splitting decimal numbers. Require an outcome-specific word plus estimate/chance/probability/likelihood/odds
language, or a standalone point at the start of a reply. Known-prior/statistics
lines are excluded when labelled as such; TeX percent escapes and Markdown
emphasis are normalized, but formulas and fractions are not evaluated. Preserve
candidate evidence. Multiple distinct answer candidates, ranges, out-of-bounds
values, non-assertions/questions, acknowledged/reported suggestions and unresolved
hypothetical answers stay missing. Control answers may condition on the explicitly
stipulated probability; other range/multiple-value rules still apply. An explicit
correction with one unique corrected point may supersede earlier candidates,
with a conflict/correction flag. A number alone does not establish endorsement;
manual stance annotations are separate. No post-live parser tuning.

Report baseline/current A/B/C/D, A change, target-directed movement, target
agreement, evidence error, baseline errors, actual downstream change, expected
change given expressed A, signed/absolute change errors, post errors relative to
expressed and evidential A, D drift, missingness and denominators. All conditions
remain included. Retain earlier diagnostic tolerances in probability units:
A target agreement .05; downstream/control error .03; large target-directed shift
.15; near-zero A change .000001. Baseline-correct subsets are labelled separately.
Numeric tolerance does not establish correct formula/logic. Automatic upstream
cue flag matches treasure/chest, bonus/room, cosmetic/reward; manually distinguish
mentions, conditional rates and unsolicited marginal estimates. Do not rewrite
previous QA-01 code, scores or results.

Reuse prior pinned request models, endpoint tags, providers and settings where
available. Recheck the same endpoints for compatibility, never select replacements.
Only max_tokens changes to4096; retain temperature0, top_p1, seed20261116,
non-thinking mode, no fallback and require_parameters. Freeze updated prices
with the prior1.25 rate ceiling margin. Skip unavailable/incompatible candidates.
No paid connectivity call. Hidden traces excluded; visible replies and metadata
preserved. Prior bounded HTTP-only transient retries remain, at most2; no retry
for token limit, undesired answer, provider finish error or uncertain transport.

Use one ThreadPoolExecutor with max_workers6 and a single dependency scheduler.
Submit all model initials first. A successful initial enables3 baselines,
3 interventions and2 controls. Each successful intervention enables its3 probes.
Do not block workers waiting for children or share mutable message histories.
A failed/incomplete parent blocks its descendants with recorded reasons. There
are exactly54 stable logical IDs at most; no child history is manufactured.
Each task has its own existing transport client; serialized sinks adapt only
game-derived fields before saving. Record eligibility, actual dispatch and
completion order; all physical attempts, including retries, count toward the
six-request maximum. Preserve full successful parent text in every child.

Budget is atomic across all models and attempts, $1 total. Retain the original
UTF-8 byte+512/message+1024 framing input bound (max32000), twofold cost margin
plus$0.001 and minimum$0.01 reservation, recomputed with4096 output tokens and
pinned rate ceilings. Before dispatch require conservative settled charges plus
all active/uncertain reservations plus the new bound <=$1. Successful known-cost
attempts settle to the maximum of reported account cost, upstream cost and actual
usage at the frozen uncached price ceilings; only excess headroom is released.
Missing cost/usage or uncertain attempts retain their full reservation. This
settlement avoids accumulating unused4096-token caps across54 calls while
preserving protection for spent plus outstanding exposure. Wait for active
settlements if temporary headroom is insufficient; stop if no safe dispatch is
possible. All transitions and artifact writes are serialized and durably logged.

Run prompt/math/scoring/concurrent-graph/budget tests and a dry run before live
calls. Offline audit replays exact prompts/parents, dependency ordering, sibling
isolation, unique IDs, concurrency, pins, attempts, charges and scores. Preserve
all previous artifacts by hash. New directory refuses resume/overwrite.

Manual inspection covers every response: acknowledgment versus hypothetical,
qualified/explicit endorsement, rejection, revised probabilities, early
propagation, B/C/D formulas, irrelevant dependencies, capability controls,
incorrect/missing baselines and incomplete answers. Keep ranges/caveats and
contradictions. No primary overrides. Compare all candidates with their QA-01
screen outputs descriptively. Gaming context, stakes, Bayesian difficulty,
intervention syntax, numerical dependencies and output cap differ jointly;
no single-factor, internal-state, rate or systematic propagation claim follows.
