# QA-01 V3 — cross-model viability screen, batch 2

Status: additional exploratory candidates chosen in discussion, separate from CROSS-MODEL-SCREEN.md. Do not rerun or amend batch 1.

## Fixed candidates

- google/gemini-2.5-flash — previously proposed comparison model. OpenRouter's model page announced retirement on October 20, 2026; live endpoint availability must be checked, and the model skipped if unavailable.
- meta-llama/llama-3.1-8b-instruct — older but widely used small dense open-weight baseline; prior research motivated screening for susceptibility to unsupported disagreement.
- qwen/qwen3.5-9b — newer small dense open-weight candidate, non-thinking mode.
- google/gemma-4-26b-a4b-it — newer open-weight Gemma family candidate, non-thinking mode. Approximately 26B total / 4B active parameters (MoE); not a size-matched dense 4B model. No task-specific susceptibility is assumed for Qwen or Gemma.

Verify live endpoint availability and comparable non-reasoning configuration before completion calls. If unavailable, skip and document; no model substitutions without a separately authorized plan.

## Execution

Inherit the exact QA-01 V3 prompts, branching, controls, inference settings where supported, endpoint selection/pinning, no-fallback policy, preservation and audit requirements, scoring and separate manual inspection requirements from CROSS-MODEL-SCREEN.md. One 18-call graph per candidate; at most 72 logical completion calls, plus bounded transient retries. Use a separate aggregate $1 budget for batch 2, including retries, with conservative budget protection. Preserve prior results and record any configuration differences. Do not run stronger-disagreement or other prompt variants. Do not cherry-pick or modify prompts to elicit agreement. Compare all completed candidates and report all skips, failures, endorsement/conditional acceptance, leakage and mathematical capability issues. Stop after the fixed screen.

Selection of newer open-weight models is motivated by model-family diversity and potential future interpretability access, not demonstrated sycophancy in this task. One case per model is a feasibility probe, not a rate estimate.
