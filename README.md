# Belief Revision Propagation

A behavioural research project investigating whether warranted and sycophantic revisions in large language models propagate differently through interconnected probabilistic beliefs.

## Research question

Given an apparent revision of an upstream belief, does the epistemic basis of that revision predict the fidelity and selectivity of subsequent downstream reasoning?

We distinguish observable outputs from internal belief representations. Warranted revisions may propagate further, less far, or indistinguishably from sycophantic revisions.

## Status

Three reviewed QA-01 smoke tests completed (2026-11-16); the broader pilot has not been run. The v3 repeat contains no unsolicited downstream estimates in upstream answers and retains the prior under unsupported disagreement, but downstream inspection calculations remain inconsistent. Single-case results and scoring limitations support no causal or general between-condition conclusion. Novelty remains provisional; no directional hypothesis has been adopted.

- [Current design and open decisions](DESIGN.md)
- [Smoke harness and usage](pilots/01-viability/harness/README.md)
- [QA-01 smoke report](pilots/01-viability/runs/2026-11-16-6ac3049-smoke-01/REPORT.md)
- [V2 repeat and paired comparison](pilots/01-viability/runs/2026-11-16-a609903-smoke-02/REPORT.md)
- [V3 repeat: endorsement, scope and mathematics](pilots/01-viability/runs/2026-11-16-f78a5fc-smoke-03/REPORT.md)

The methodology follows [Research Apprentice](https://github.com/surajk-io/research-apprentice), phase 4. The immediate goal is a small viability pilot, not a full study. Preserve failed and inconclusive trials as well as successful ones.
