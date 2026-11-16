# Belief Revision Propagation

A behavioural research project investigating whether warranted and sycophantic revisions in large language models propagate differently through interconnected probabilistic beliefs.

## Research question

Given an apparent revision of an upstream belief, does the epistemic basis of that revision predict the fidelity and selectivity of subsequent downstream reasoning?

We distinguish observable outputs from internal belief representations. Warranted revisions may propagate further, less far, or indistinguishably from sycophantic revisions.

## Status

QA-01 smoke tests, cross-model screens and all GAME-01 follow-ups are preserved. The two latest specified suites completed 189 requests: Scout matched revision/arithmetic verification, then an independent capability battery and two comparator models. Scout's verified-arithmetic replies reject the suggested targets, while reminder and no-target failures, selective downstream uptake, ambiguous endorsement and premature comparator calculations limit interpretation. One Scout arm hit the output cap, blocking three probes. No broader pilot, unscheduled experiments or causal/general rate conclusions were added.

- [Current design and open decisions](DESIGN.md)
- [Smoke harness and usage](pilots/01-viability/harness/README.md)
- [QA-01 smoke report](pilots/01-viability/runs/2026-11-16-6ac3049-smoke-01/REPORT.md)
- [V2 repeat and paired comparison](pilots/01-viability/runs/2026-11-16-a609903-smoke-02/REPORT.md)
- [V3 repeat: endorsement, scope and mathematics](pilots/01-viability/runs/2026-11-16-f78a5fc-smoke-03/REPORT.md)
- [Fixed cross-model screens: both batches](pilots/01-viability/screens/2026-11-16-b7da458-cross-model/REPORT.md)
- [Gaming pilot: comparative report](pilots/02-gaming-viability/runs/2026-11-16-6c0ca45-game-01/REPORT.md)
- [Implicit-wording follow-up: comparative report](pilots/02-gaming-viability/runs/2026-11-16-445c88d-implicit-followup/REPORT.md)
- [Llama-family follow-up: comparative report](pilots/02-gaming-viability/runs/2026-11-16-2ada2d7-llama-family/REPORT.md)
- [Scout target/anchor follow-up: comparative report](pilots/02-gaming-viability/runs/2026-11-16-33f8c61-scout-target-anchor/REPORT.md)
- [Scout verification: matched revision and arithmetic support](pilots/02-gaming-viability/runs/2026-11-16-db51f26-scout-verification/REPORT.md)
- [Independent capability battery and comparators](pilots/02-gaming-viability/runs/2026-11-16-db51f26-baselines-capability/REPORT.md)
- [Gaming harness](pilots/02-gaming-viability/harness/README.md)

The methodology follows [Research Apprentice](https://github.com/surajk-io/research-apprentice), phase 4. The immediate goal is a small viability pilot, not a full study. Preserve failed and inconclusive trials as well as successful ones.
