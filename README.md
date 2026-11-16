# Belief Revision Propagation

A behavioural research project investigating whether warranted and sycophantic revisions in large language models propagate differently through interconnected probabilistic beliefs.

## Research question

Given an apparent revision of an upstream belief, does the epistemic basis of that revision predict the fidelity and selectivity of subsequent downstream reasoning?

We distinguish observable outputs from internal belief representations. Warranted revisions may propagate further, less far, or indistinguishably from sycophantic revisions.

## Status

Three QA-01 smoke tests and both fixed V3 cross-model screens completed (2026-11-16); the broader pilot has not been run. The screens preserve all seven candidates, including incomplete outputs. Apparent unsupported agreement does not cleanly co-occur with adequate controls and unambiguous updating in this one-case screen. Novelty remains provisional; no directional hypothesis or causal conclusion has been adopted.

- [Current design and open decisions](DESIGN.md)
- [Smoke harness and usage](pilots/01-viability/harness/README.md)
- [QA-01 smoke report](pilots/01-viability/runs/2026-11-16-6ac3049-smoke-01/REPORT.md)
- [V2 repeat and paired comparison](pilots/01-viability/runs/2026-11-16-a609903-smoke-02/REPORT.md)
- [V3 repeat: endorsement, scope and mathematics](pilots/01-viability/runs/2026-11-16-f78a5fc-smoke-03/REPORT.md)
- [Fixed cross-model screens: both batches](pilots/01-viability/screens/2026-11-16-b7da458-cross-model/REPORT.md)

The methodology follows [Research Apprentice](https://github.com/surajk-io/research-apprentice), phase 4. The immediate goal is a small viability pilot, not a full study. Preserve failed and inconclusive trials as well as successful ones.
