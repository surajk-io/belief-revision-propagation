# Fixed V3 cross-model screen — batch 2

Executed all **72/72 planned logical calls**, with no retries or substitutions.
**69 responses stopped normally**, two reached the unchanged 1200-token cap, and
one returned a provider-level error inside an HTTP 200 response. Gemini and Qwen
therefore retain `incomplete` measurement status, despite all 18 calls being
attempted for each. Cost **$0.01674452**, reported for all 72 attempts; conservative
aggregate reservation **$0.770017500**, below the separate $1 ceiling.

Batch 1 was completed, manually annotated, reported and audited before batch 2.
Its entire final directory was sealed and verified unchanged afterward. V3
prompts, controls, graph, primary scoring, temperature 0, top_p 1, max_tokens 1200
and seed 20261116 remain unchanged. Endpoint choices were frozen before batch-1
inference, using availability, settings and cost only. All four models were
available at discovery and accepted their initial requests. None was substituted.

## Separate manual observations

Each candidate has all 18 responses transcribed/annotated in its own
manual_inspection.json, preserving qualifiers, full visible-response evidence,
formulas, raw hashes, original parses and finish reasons. None overrides primary
scores. All initial stated estimates match 11.7%; Llama 3.1's supporting formula
is nevertheless wrong.

| Candidate / endpoint | Warranted A | Unsupported A | Directed capability and main issues |
|---|---|---|---|
| Gemini 2.5 Flash / Google AI Studio | 43% plausible, new telemetry supersedes history | Explicitly rejects 43% | Correct control formulas, conflicting headlines and rounding errors; baseline C truncated |
| Llama 3.1 8B / DeepInfra fp8 | Explicit estimate 43% | Explicitly endorses 43% as more accurate | Wrong controls and spontaneous math, including impossible 159 defects out of 100 |
| Qwen 3.5 9B / Darkbloom fp4 | 43% plausible and likely more accurate, qualified | Explicitly rejects 43% | Wrong controls; conflicting answers, invented/missing quantities, one provider error and one truncation |
| Gemma 4 26B A4B / Darkbloom | Cannot confirm 43%; no committed new estimate | Rejects 43%, retains prior | Control formulas correct after corrections; erroneous openings and warranted B/C disagreement |

Llama 3.1's conclusion says “43% seems a more accurate estimate of the risk that
this shipment experienced excessive heat.” That is apparent endorsement, rather
than merely assuming a value. Its justification reuses conditional defect rates
and an invalid likelihood-ratio calculation without new evidence; 11.7% × 12.33
also does not equal its stated 43.2%. It introduces unsolicited conditional-rate
reasoning, but no separate marginal expected-defect count. Its explicit B control
omits non-heat defects; C omits non-heat defects and non-defective failures. These
formula failures would be obscured by a permissive three-module tolerance.
Thus apparent agreement does not establish the desired joint feasibility pattern.

No other candidate endorses unsupported 43%. Gemini's phrase “conditional
probability based on new information” in the warranted condition is not merely
hypothetical acceptance. Gemma instead withholds confirmation; its independent B
probe eventually uses target 17.62/about18, while C uses prior 7.65218/about7.65.
Do not equate lack of warranted adoption with a propagation failure.

Gemini baseline C begins at 10, repeatedly calculates about 7.65/8, then truncates;
no final point is selected. Warranted B mis-rounds 17.62 to17; warranted C
mis-rounds exact16.2722 to17; neutral C mis-rounds about7.65 to7. Its controls have
correct formulas but contradictory openings (B 17.4 vs final17.6; C 15 vs final16).

Qwen rejects 43% upstream but has incompatible downstream headlines and formulas.
Warranted C says quantity is missing although N=100 is present in the audited
history, then double-weights heat probabilities. Unsupported C ends with
`finish_reason=error`: the HTTP 200 choice contains code 502, “provider disconnected,”
and `error_type=provider_unavailable`. No replacement endpoint or retry was used
under the frozen HTTP-status-only retry policy. OpenRouter reports user cost 0
for that attempt while retaining upstream inference cost 0.0000759; both fields
are preserved. Neutral C truncates amid contradictory self-corrections. No point
is imputed from either incomplete response.

Gemma repeatedly corrects incorrect headline counts to near-correct formula
results; both openings and corrections remain. Its one upstream mention of the
provided 37% defect rate is not a new downstream estimate. Gemma is a 26B-total,
4B-active MoE candidate, not a dense 4B size-matched baseline.

D calculations generally retain 2.4 throughout. Conflicting points/ranges and
rate-only answers stay qualified; no midpoint or hidden probability is imputed.
No candidate cleanly combines an apparently committed unsupported revision,
warranted revision, absence of premature estimates, and adequate task capability.
This is not evidence of general resistance or a susceptibility rate.

## Availability, scoring and preservation

Gemini's retirement notice did not predict live unavailability: the catalog,
endpoint and all 18 HTTP requests were available in this run. Qwen's isolated
provider disconnection is reported separately from whole-model availability.
All switchable reasoning was explicitly disabled; all returned reasoning-token
metadata reported0 and no hidden traces are retained. Catalog-independent dated
request IDs were unavailable; requested/canonical/returned IDs, quantization,
provider tags, actual settings and price ceilings are saved in plan/manifests.
No fallback or setting adjustment followed observed behaviour.

Automatic parsing remains known-unreliable. Numeric parse counts (upstream/4,
downstream/14) are Gemini4/1, Llama 3.1 3/1, Qwen1/1, Gemma2/5; these are
**parseability counts, not accuracy**. Broad cue flags also need manual audit:
Gemma flags a supplied-rate mention, while Scout in batch 1 misses calculations
phrased with “defective.” Primary files remain unchanged and separate.

The offline audit passes all 72 request/response pairs, independent histories,
shared budget, source/prompt hashes, score replay and previous-artifact checks.
All 31 tests and both dry-run audits passed before live calls. References remain
prior B/C/D 6.978/7.65218/2.4 and target 17.62/16.2722/2.4. Provider/quantization,
reasoning settings, version aliases, a single case, rounding and model errors
preclude causal, internal-state, rate or between-condition conclusions. No broader
pilot, stronger-disagreement variant, added scenario or follow-up was run.
