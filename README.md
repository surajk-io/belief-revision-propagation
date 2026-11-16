# Belief Revision Propagation

A behavioural research project investigating whether warranted and sycophantic revisions in large language models propagate differently through interconnected probabilistic beliefs.

## Research question

Given an apparent revision of an upstream belief, does the epistemic basis of that revision predict the fidelity and selectivity of subsequent downstream reasoning?

We distinguish observable outputs from internal belief representations. Warranted revisions may propagate further, less far, or indistinguishably from sycophantic revisions.

## Status

QA-01 smoke tests, both fixed cross-model screens and the original GAME-01 pilot are preserved. The specified implicit-wording follow-up also completed (2026-11-16): 80 planned calls across six models, 79 visible completions and one Qwen baseline lost to rate limits. Scout explicitly agreed with 69% after faulty upstream arithmetic and used it coherently downstream; mathematical and interpretation issues limit comparison across models. The fixed Llama-family extension evaluated Maverick and Llama3.3 70B: Maverick rejected the unsupported estimate with good directed controls; Llama3.3’s unsupported reply hit the output cap, leaving its dependent probes blocked. The specified Scout target/anchor follow-up completed 44 calls: final unsupported estimates varied with endorsed targets, while reference comparisons mostly retained the baseline; downstream uptake was selective. No broader pilot or unscheduled experiments were run; no causal or general rate conclusion has been adopted.

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
- [Gaming harness](pilots/02-gaming-viability/harness/README.md)

The methodology follows [Research Apprentice](https://github.com/surajk-io/research-apprentice), phase 4. The immediate goal is a small viability pilot, not a full study. Preserve failed and inconclusive trials as well as successful ones.
