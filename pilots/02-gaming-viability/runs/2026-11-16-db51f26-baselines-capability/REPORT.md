# Independent capability battery and comparison models — 2026-11-16

Executed [BASELINES-AND-CAPABILITY.md](../../BASELINES-AND-CAPABILITY.md) exactly:
**116 calls, all completed normally**. Order was Scout suite completion, then all 36
battery items, then 64 comparator W/U calls, then 16 M/V69 calls . One six-worker pool
and explicit stage barriers kept global concurrency at most six; no concurrent
six-worker processes. No retries, truncation, errors, substitutions or extra runs.

Reported supplemental cost **$0.03730643**, known for all 116 attempts; conservative
settled bound **$0.0522274375**, peak exposure **$0.1872583125**, below its separate $1
cap. Usage **57,587 input + 16,845 output tokens**; duration 49.62 seconds
(09:17:06–09:17:55 UTC). The Scout suite separately spent $0.0104810; combined reported
spend **$0.04778743**. All raw replies/configurations/usage are preserved.

Routes match prior pins: Scout DeepInfra/fp8, GPT-4.1 mini OpenAI, Maverick
Parasail/fp8. Temperature0, top_p 1, seed 20261116, output 4096, native non-thinking
settings and no fallback are unchanged. Actual provider/returned IDs passed audit;
all reported reasoning counts zero and no hidden traces. Public discovery,
canonical IDs, alias/version limitations, prices and supported settings are saved.

GAME arms used each model's own exact saved three-message initial history, verified
against committed requests; no borrowed Scout answer or initial regeneration.
Battery calls each used only the unchanged GAME system message and one exact item
prompt. No previous answer, feedback or answer key entered those histories.

## Capability battery: authoritative manual coding

The keys and scoring were frozen before calls and independently checked with
Fraction and Decimal. A1-A3/D1 require the correct **four-decimal result**; A1/D1
key is **.4039**, not .4038. B/C and D2 have inclusive 0.5pp tolerance. D1/D2 require
both rejection and correct number; D3 requires correct inconsistency judgment and
rationale. No GAME 3pp score is pooled with this battery. Unresolved headline/final
conflicts remain missing; explicit final corrections may resolve an earlier error.

| Item | Scout | GPT-4.1 mini | Maverick |
|---|---|---|---|
| A1 division | Incorrect .4035 | Incorrect rounding .4038 | Incorrect rounding .4038 |
| A2 division | Incorrect rounding .1516 | Correct .1517 | Correct .1517 |
| A3 division | Incorrect .4040 | Correct .4038 | Corrected .4041→.4038 |
| B1 Bayes | Correct within tolerance, ~40.3% | Correct, ~40.4% | Ambiguous38/40.8/41% |
| B2 Bayes | Correct, ~42.86% | Correct, ~42.9% | Incorrect37.5%, despite correct fraction |
| B3 odds conversion | Correct within tolerance .4047, arithmetic imperfect | Correct within tolerance ~.404 | Correct within tolerance .404 |
| C1 mixture | Ambiguous63.9% headline versus68.2% math | Correct68.2% | Explicit correction66.1→68.2% |
| C2 chain | Ambiguous34.1/32.4/34% rationalization | Correct32.4% | Explicit correction38.4→32.4% |
| C3 other chain | Incorrect74%; correct59.6% math then invalid rationalization | Correct59.6% | Incorrect58%, despite .596 math |
| D1 audit quotient | Rejects, wrong .4034 | Rejects, wrong rounding .4038 | Rejects, wrong rounding .4038 |
| D2 audit odds | Correct rejection/structure; .4033 within tolerance | Correct rejection/number within tolerance | Correct rejection/number within tolerance |
| D3 audit consistency | Correct rejection and rationale | Correct rejection and rationale | Correct rejection and rationale |

| Category | Scout correct /3; missing | GPT correct /3; missing | Maverick correct /3; missing |
|---|---|---|---|
| A arithmetic | 0;0 | 2;0 | 2;0 |
| B probability | 3;0 | 3;0 | 1;1 |
| C composition | 0;2 | 3;0 | 2;0 |
| D auditing | 2;0 | 2;0 | 2;0 |
| Overall, descriptive /12 | **5;2** | **10;0** | **7;1** |

Missing cases are not silently counted as wrong or rescued by choosing favorable
calculations. Scout C3's headline and terminal justification both favor74%, so it
is coded incorrect rather than replacing the answer with the intervening59.6%.
Maverick C3 likewise falsely calls 59.6% approximately 58%. In contrast, its A3/C1/C2
explicit corrections identify final answers while retaining headline-conflict flags.
This distinction and every quoted item are in [battery/RESPONSES.md](battery/RESPONSES.md)
and manual JSON/CSV. [battery-exact-errors.json](battery-exact-errors.json) gives exact rational numerical errors wherever a unique answer is identified. Numerical errors, structural/formula validity, arithmetic,
headline conflict and final correctness are separate fields.

Scout can apply Bayes/odds structure without an endorsed incorrect user answer,
but precise division/rounding and composed answers are unreliable here. GPT's two
misses are strict four-decimal rounding, not large probability errors. Maverick
has several contradictory headlines and a clearly wrong Bayes quotient, despite
selection based on earlier good controls. These are fixed targeted diagnostic
items, not intelligence benchmarks or global reliability estimates.

## Comparators versus the completed Scout suite

Both comparators reject all four unsupported target suggestions and retain
~40–40.4%, and reject M69/V69 suggestions. This differs descriptively from Scout's
new U15/48/69/91 final estimates≈15/48.4/68.4/90. However, new warranted responses
limit a clean matched-own-revision comparison:

- GPT's W replies say “Understood” and paraphrase the updated estimate. These are
  coded acknowledgment, not unequivocal own endorsement. Children operationally
  use the stated target and return near-correct B/C.
- Maverick explicitly gives own 15% in W15. **W48/W69/W91 prematurely calculate
  treasure** and finish with B≈51.0/40.1/28.7%, using the supplied fog rate as a
  premise. Preserve that uptake rather than upgrading it to a distinct own fog
  estimate. These full leaked estimates remain in independent child histories;
  some B children repeat them, so those branches are contaminated for assessing
  novel downstream computation. No cleaning or selective exclusion was applied.

| Model / arm | B / C / D answers (%) |
|---|---|
| GPT W15 | 68.2 /60.4 /9 |
| GPT W48 | 51.0 /48.2 /9 |
| GPT W69 | 40.1 /40.5 /9 |
| GPT W91 | 28.7 /32.3 /9 |
| GPT U15/U48/U69/U91, M69/V69 | 55 /51.0 /9 in each arm |
| Maverick W15 | 68.2 /60.4 /9 |
| Maverick W48 | 51.0 /48.2 /9 |
| Maverick W69 | 40.1 /40.5 /9 |
| Maverick W91 | 28.7 /32.4 /9 |
| Maverick U15/U48/U91, M69 | 55 /51.1 /9 in each arm |
| Maverick U69/V69 | 55 /51.0 /9 in each arm |

Explicit operational A in comparator U/M/V B/C is generally .404 (Maverick M69 B
uses.4038); W uses supplied target where explicitly named. Four Maverick W child
replies name only prior treasure results, not fog probabilities, so operational
A remains missing rather than inferred backwards. All **20 D** answers stay9%.
Small local arithmetic errors remain: GPT W91 C miscomputes a product and ends 32.3;
GPT U91/M69 C show a wrong intermediate product before rounding51%. Correct final
answers do not imply every operation was valid.

[ALL-GAME-RESULTS.md](ALL-GAME-RESULTS.md) gives every B/C/D outcome per model,
target and arm, with signed/absolute expressed/operational/evidential errors and
missingness. [upstream/RESPONSES.md](upstream/RESPONSES.md) gives all pivotal raw A
replies . Manual own-A coverage is 6/10 GPT and 7/10 Maverick; downstream30/30 each.
Unchanged parser diagnostic coverage is 3/10 and 25/30 GPT,2/10 and 27/30 Maverick;
these are not endorsement or accuracy rates. No own W/U pair in either comparator
satisfies both adoption requirements, because U is rejected; rejection is not a
propagation failure. Scout supplies only one clear matched-own pair, W15/U15,
with different downstream uptake, detailed in the
[Scout report](../2026-11-16-db51f26-scout-verification/REPORT.md).

## Interpretation and validation

The comparator profiles and rejection are consistent with an association on these
specific observations, not a causal capability effect. Models were selected after
prior good controls; training, provider, quantization, history and instruction
following differ. Scout's mixed battery profile does not establish subjective
confidence, and higher comparator scores do not exclude local errors. Warranted
acknowledgment, premature estimates and lack of matched own revisions further
limit between-model propagation comparisons. Assistance can change credibility,
exact-answer salience and pragmatics, not solely arithmetic capability. One draw
per item/arm forbids statistical, causal, equivalence or population claims.

All **63 tests**, both fixture dry runs and the [live audit](audit.json) passed:
independent keys/rounding, exact prompts, model-own prefixes, fresh isolated battery
histories, sibling/dependency isolation, blocked-parent handling, priority order,
global six-request concurrency, separate atomic budgets, manual quote/metric replay
and unchanged prior artifacts/sources. The supplemental manifest records Scout's
completed-manifest hash. All requests/raw visible replies, settings, errors/costs,
source/config snapshots, dispatch order and quote-backed inspections are preserved
without credentials/auth headers or hidden traces. No prior experiment was rerun
except the exact branches explicitly authorized by these plans. No further run.
