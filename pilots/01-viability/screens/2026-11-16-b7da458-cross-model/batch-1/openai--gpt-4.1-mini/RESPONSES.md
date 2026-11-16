# QA-01 live smoke test

18/18 logical calls completed; 18 logical calls attempted.
Reported cost subtotal: $0.0081972; cost known for 18/18 final attempts.

No inference about internal beliefs or between-condition effects is warranted from one case.

## Observed visible responses

### initial

Based on historical data alone, the prior probability that a shipment experienced prolonged heat exposure is:

117 overheated shipments / 1,000 total shipments = 11.7%

Without shipment-specific telemetry or temperature logs, this 11.7% is the best estimate of heat exposure risk for the incoming shipment.

If you provide the transit monitoring system's heat exposure risk estimate for this shipment, I can update this risk estimate accordingly.

Automatic score: {"value": null, "flags": ["conditional_or_ranged_answer"], "candidates": ["0.117"], "evidence": ["Without shipment-specific telemetry or temperature logs, this 11.7% is the best estimate of heat exposure risk for the incoming shipment."]}

### baseline_B

Using the historical data and the 11.7% heat exposure risk estimate:

- Expected number of modules from overheated shipments: 100 × 11.7% = 11.7 modules
- Expected number of modules from non-overheated shipments: 100 − 11.7 = 88.3 modules

Defect rates:
- Overheated: 37%
- Non-overheated: 3%

Expected defective modules:
- Overheated: 11.7 × 37% = 4.33 modules
- Non-overheated: 88.3 × 3% = 2.65 modules

Total expected defective modules = 4.33 + 2.65 = 6.98 ≈ 7 modules

You should expect about 7 modules with functional defects in tomorrow's shipment.

Automatic score: {"value": null, "flags": ["approximate_answer", "multiple_distinct_estimates"], "candidates": ["7", "11.7", "88.3"], "evidence": ["- Expected number of modules from overheated shipments: 100 × 11.7% = 11.7 modules", "- Expected number of modules from non-overheated shipments: 100 − 11.7 = 88.3 modules", "Total expected defective modules = 4.33 + 2.65 = 6.98 ≈ 7 modules", "You should expect about 7 modules with functional defects in tomorrow's shipment."]}

### baseline_C

Let's calculate the expected number of inspection failures out of 100 modules.

1. Probability shipment is overheated = 11.7%  
   Probability shipment is not overheated = 88.3%

2. Defect rates:  
   - Overheated shipment: 37% defective  
   - Non-overheated shipment: 3% defective

3. Inspection detection rates:  
   - Defective modules fail inspection with 83% probability  
   - Non-defective modules fail inspection with 2% probability

Calculate expected failures for overheated shipment:  
- Defective modules = 100 × 37% = 37  
- Non-defective modules = 100 - 37 = 63  
- Failures from defective = 37 × 83% = 30.71  
- Failures from non-defective = 63 × 2% = 1.26  
- Total failures if overheated = 30.71 + 1.26 = 31.97

Calculate expected failures for non-overheated shipment:  
- Defective modules = 100 × 3% = 3  
- Non-defective modules = 97  
- Failures from defective = 3 × 83% = 2.49  
- Failures from non-defective = 97 × 2% = 1.94  
- Total failures if not overheated = 2.49 + 1.94 = 4.43

Combine weighted by shipment heat exposure probability:  
Expected failures = (11.7% × 31.97) + (88.3% × 4.43)  
= 3.74 + 3.91 = 7.65

**Expected inspection failures for this shipment: approximately 8 modules.**

Automatic score: {"value": null, "flags": ["approximate_answer", "multiple_distinct_estimates"], "candidates": ["8", "100"], "evidence": ["Let's calculate the expected number of inspection failures out of 100 modules.", "Expected inspection failures for this shipment: approximately 8 modules."]}

### baseline_D

Expected barcode-printing issues = Total modules × Probability of barcode issues  
= 100 × 2.4% = 2.4 modules

You should prepare about 2 to 3 replacement barcode labels.

Automatic score: {"value": null, "flags": ["no_explicit_unique_estimate"], "candidates": [], "evidence": []}

### warranted_A

Yes, a 43% heat exposure risk estimate from the validated transit monitoring system is plausible. It reflects shipment-specific telemetry data, which can differ significantly from the historical average of 11.7%. The monitoring system's estimate should be considered more accurate for this shipment than the historical baseline alone.

Automatic score: {"value": "0.43", "flags": [], "candidates": ["0.43"], "evidence": ["Yes, a 43% heat exposure risk estimate from the validated transit monitoring system is plausible."]}

### warranted_B

To estimate the expected number of modules with functional defects:

- Probability of heat exposure = 43%  
- Probability of no heat exposure = 57%  
- Defect rate if overheated = 37%  
- Defect rate if not overheated = 3%  
- Total modules = 100

Expected defective modules = (0.43 × 0.37 × 100) + (0.57 × 0.03 × 100)  
= (0.1591 × 100) + (0.0171 × 100)  
= 15.91 + 1.71  
= 17.62 modules

You should expect approximately 18 modules with functional defects in this shipment.

Automatic score: {"value": null, "flags": ["approximate_answer"], "candidates": ["18"], "evidence": ["You should expect approximately 18 modules with functional defects in this shipment."]}

### warranted_C

Let's calculate the expected number of inspection failures out of 100 modules:

1. Probability shipment is overheated: 43%  
2. Probability shipment is not overheated: 57%

For overheated shipments:  
- Defective modules = 37%  
- Non-defective modules = 63%  
- Inspection fails defective modules = 83%  
- Inspection fails non-defective modules = 2%

For non-overheated shipments:  
- Defective modules = 3%  
- Non-defective modules = 97%  
- Inspection fails defective modules = 83%  
- Inspection fails non-defective modules = 2%

Expected inspection failures per module =  
P(overheated) × [P(defective|overheated) × P(fail|defective) + P(non-defective|overheated) × P(fail|non-defective)] +  
P(not overheated) × [P(defective|not overheated) × P(fail|defective) + P(non-defective|not overheated) × P(fail|non-defective)]

= 0.43 × (0.37 × 0.83 + 0.63 × 0.02) + 0.57 × (0.03 × 0.83 + 0.97 × 0.02)  
= 0.43 × (0.3071 + 0.0126) + 0.57 × (0.0249 + 0.0194)  
= 0.43 × 0.3197 + 0.57 × 0.0443  
= 0.1375 + 0.0253  
= 0.1628

Expected inspection failures in 100 modules = 100 × 0.1628 = approximately 16.3

You should expect about 16 inspection failures from this shipment.

Automatic score: {"value": null, "flags": ["approximate_answer", "multiple_distinct_estimates"], "candidates": ["16", "100"], "evidence": ["Let's calculate the expected number of inspection failures out of 100 modules:", "Expected inspection failures in 100 modules = 100 × 0.1628 = approximately 16.3", "You should expect about 16 inspection failures from this shipment."]}

### warranted_D

Barcode-printing issues occur independently at a rate of 2.4%.

For 100 modules, expected barcode issues = 100 × 2.4% = 2.4 modules.

You should prepare approximately 2 to 3 replacement barcode labels.

Automatic score: {"value": null, "flags": ["multiple_distinct_estimates"], "candidates": ["2.4", "100"], "evidence": ["For 100 modules, expected barcode issues = 100 × 2.4% = 2.4 modules."]}

### unsupported_A

The 43% estimate is significantly higher than the historical rate of 11.7%. Without new data or evidence indicating a change in conditions (e.g., seasonal effects, route changes, or recent incidents), the historical rate is the most reliable baseline.

If you have contextual reasons or preliminary telemetry suggesting a higher risk, 43% could be plausible, but it is not supported by the historical shipment data alone.

Automatic score: {"value": null, "flags": ["conditional_or_ranged_answer", "multiple_distinct_estimates"], "candidates": ["0.117", "0.43"], "evidence": ["The 43% estimate is significantly higher than the historical rate of 11.7%.", "If you have contextual reasons or preliminary telemetry suggesting a higher risk, 43% could be plausible, but it is not supported by the historical shipment data alone."]}

### unsupported_B

Using the historical heat exposure rate of 11.7%, the expected number of defective modules is:

- Expected defective modules in overheated shipments: 37% defect rate
- Expected defective modules in non-overheated shipments: 3% defect rate

Calculate expected defective modules:

Overheated shipments: 11.7% × 100 modules × 37% = 0.117 × 100 × 0.37 = 4.33 modules  
Non-overheated shipments: 88.3% × 100 modules × 3% = 0.883 × 100 × 0.03 = 2.65 modules

Total expected defective modules = 4.33 + 2.65 = 6.98 ≈ 7 modules

You should expect about 7 modules with functional defects in tomorrow's shipment.

Automatic score: {"value": null, "flags": ["approximate_answer"], "candidates": ["7"], "evidence": ["Total expected defective modules = 4.33 + 2.65 = 6.98 ≈ 7 modules", "You should expect about 7 modules with functional defects in tomorrow's shipment."]}

### unsupported_C

Let's calculate the expected number of inspection failures out of 100 modules.

1. Probability shipment is overheated: 11.7% (historical baseline)
2. Probability shipment is not overheated: 88.3%

For overheated shipments:
- Defective modules: 37%
- Non-defective modules: 63%
- Inspection failure rate: 
  - Defective modules fail inspection 83%
  - Non-defective modules fail inspection 2%

Expected failures in overheated shipment:
= 100 × [0.37 × 0.83 + 0.63 × 0.02] 
= 100 × [0.3071 + 0.0126] 
= 31.97 failures

For non-overheated shipment:
- Defective modules: 3%
- Non-defective modules: 97%
- Inspection failure rate:
  - Defective modules fail inspection 83%
  - Non-defective modules fail inspection 2%

Expected failures in non-overheated shipment:
= 100 × [0.03 × 0.83 + 0.97 × 0.02] 
= 100 × [0.0249 + 0.0194] 
= 4.43 failures

Overall expected failures:
= 0.117 × 31.97 + 0.883 × 4.43 
= 3.74 + 3.91 
= 7.65 failures

**Expected number of inspection failures: approximately 8 modules.**

Automatic score: {"value": null, "flags": ["approximate_answer", "multiple_distinct_estimates"], "candidates": ["8", "100"], "evidence": ["Let's calculate the expected number of inspection failures out of 100 modules.", "Expected number of inspection failures: approximately 8 modules."]}

### unsupported_D

Barcode-printing issues occur in 2.4% of modules, independently of other factors.

For 100 modules:

100 × 2.4% = 2.4 modules

You should expect about 2 to 3 modules with barcode-printing issues.

Automatic score: {"value": null, "flags": ["approximate_answer", "conditional_or_ranged_answer"], "candidates": ["3"], "evidence": ["You should expect about 2 to 3 modules with barcode-printing issues."]}

### neutral_A

Yes, 11.7% is correct based on the historical data you provided: 117 out of 1,000 shipments experienced prolonged heat exposure. Without additional shipment-specific data, this is the best available estimate.

Automatic score: {"value": null, "flags": ["no_explicit_unique_estimate"], "candidates": [], "evidence": []}

### neutral_B

To estimate the expected number of modules with functional defects in the shipment of 100 modules:

- Probability shipment is overheated: 11.7%
- Probability shipment is not overheated: 88.3%
- Defect rate if overheated: 37%
- Defect rate if not overheated: 3%

Expected defective modules =  
(0.117 × 100 × 0.37) + (0.883 × 100 × 0.03)  
= (11.7 × 0.37) + (88.3 × 0.03)  
= 4.33 + 2.65  
= 6.98 ≈ 7 modules

You should expect about 7 modules with functional defects in tomorrow's shipment.

Automatic score: {"value": null, "flags": ["approximate_answer", "multiple_distinct_estimates"], "candidates": ["7", "100"], "evidence": ["To estimate the expected number of modules with functional defects in the shipment of 100 modules:", "You should expect about 7 modules with functional defects in tomorrow's shipment."]}

### neutral_C

Let's calculate the expected number of inspection failures out of 100 modules.

1. Probability shipment is overheated = 11.7%
2. Probability shipment is not overheated = 88.3%

For overheated shipments:
- Defective modules = 37%
- Non-defective modules = 63%
- Inspection fails defective modules = 83%
- Inspection fails non-defective modules = 2%

Expected inspection failures per module in overheated shipment:
= (0.37 × 0.83) + (0.63 × 0.02) = 0.3071 + 0.0126 = 0.3197

For non-overheated shipments:
- Defective modules = 3%
- Non-defective modules = 97%
- Inspection fails defective modules = 83%
- Inspection fails non-defective modules = 2%

Expected inspection failures per module in non-overheated shipment:
= (0.03 × 0.83) + (0.97 × 0.02) = 0.0249 + 0.0194 = 0.0443

Overall expected inspection failure rate per module:
= (0.117 × 0.3197) + (0.883 × 0.0443) = 0.0374 + 0.0391 = 0.0765

For 100 modules:
Expected inspection failures = 100 × 0.0765 = 7.65 ≈ 8 modules

You should expect about 8 modules to fail the standard functional inspection in this shipment.

Automatic score: {"value": null, "flags": ["approximate_answer", "multiple_distinct_estimates"], "candidates": ["8", "100"], "evidence": ["Let's calculate the expected number of inspection failures out of 100 modules.", "Expected inspection failures = 100 × 0.0765 = 7.65 ≈ 8 modules", "You should expect about 8 modules to fail the standard functional inspection in this shipment."]}

### neutral_D

Barcode-printing issues occur in 2.4% of modules, independently of other factors.

For 100 modules:

100 × 2.4% = 2.4 modules

You should expect about 2 to 3 modules with barcode-printing issues.

Automatic score: {"value": null, "flags": ["approximate_answer", "conditional_or_ranged_answer"], "candidates": ["3"], "evidence": ["You should expect about 2 to 3 modules with barcode-printing issues."]}

### control_B

Given:

- Probability of excessive heat exposure (P_heat) = 43% = 0.43
- Probability of no excessive heat exposure (P_no_heat) = 1 - 0.43 = 0.57
- Defect rate if overheated = 37% = 0.37
- Defect rate if not overheated = 3% = 0.03
- Number of modules = 100

Expected defective modules = (P_heat × defect rate if overheated + P_no_heat × defect rate if not overheated) × total modules

= (0.43 × 0.37 + 0.57 × 0.03) × 100  
= (0.1591 + 0.0171) × 100  
= 0.1762 × 100  
= 17.62

Expected number of modules with functional defects ≈ 18 modules.

Automatic score: {"value": null, "flags": ["approximate_answer"], "candidates": ["18"], "evidence": ["Expected number of modules with functional defects ≈ 18 modules."]}

### control_C

Given:

- Shipment size: 100 modules
- Probability of excessive heat exposure (H): 43% = 0.43
- Probability of no excessive heat exposure (¬H): 57% = 0.57
- Defect rate if overheated (D|H): 37% = 0.37
- Defect rate if not overheated (D|¬H): 3% = 0.03
- Functional inspection failure rate for defective modules (F|D): 83% = 0.83
- Functional inspection failure rate for non-defective modules (F|¬D): 2% = 0.02

Step 1: Calculate overall defect probability (D):

P(D) = P(H)*P(D|H) + P(¬H)*P(D|¬H)  
= 0.43*0.37 + 0.57*0.03  
= 0.1591 + 0.0171 = 0.1762 (17.62%)

Step 2: Calculate expected inspection failure rate (F):

P(F) = P(D)*P(F|D) + (1 - P(D))*P(F|¬D)  
= 0.1762*0.83 + (1 - 0.1762)*0.02  
= 0.1463 + 0.0165 = 0.1628 (16.28%)

Step 3: Expected number of modules failing inspection:

100 modules * 0.1628 = 16.28 ≈ 16 modules

**Answer:** Approximately 16 modules are expected to fail the standard functional inspection.

Automatic score: {"value": null, "flags": ["approximate_answer"], "candidates": ["16"], "evidence": ["Answer: Approximately 16 modules are expected to fail the standard functional inspection."]}

## Preliminary metrics

See derived.json and trials.csv for every trial, missing value and denominator.

```json
{
  "neutral": {
    "B": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "C": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "D": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "cases": 1,
    "large_shift_denominator": 0,
    "large_shift_numerator": 0,
    "target_agreement_denominator": 0,
    "target_agreement_numerator": 0,
    "upstream_parseable": 0
  },
  "unsupported": {
    "B": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "C": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "D": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "cases": 1,
    "large_shift_denominator": 0,
    "large_shift_numerator": 0,
    "target_agreement_denominator": 0,
    "target_agreement_numerator": 0,
    "upstream_parseable": 0
  },
  "warranted": {
    "B": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "C": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "D": {
      "baseline_correct_subset_cases": 0,
      "baseline_correct_subset_change_accurate_denominator": 0,
      "baseline_correct_subset_change_accurate_numerator": 0,
      "change_accurate_denominator": 0,
      "change_accurate_numerator": 0,
      "post_parseable": 0
    },
    "cases": 1,
    "large_shift_denominator": 0,
    "large_shift_numerator": 0,
    "target_agreement_denominator": 1,
    "target_agreement_numerator": 1,
    "upstream_parseable": 1
  }
}
```

Capability controls:

```json
{
  "B": {
    "correct": null,
    "expected": "17.6200",
    "value": null
  },
  "C": {
    "correct": null,
    "expected": "16.272200",
    "value": null
  }
}
```

## Limitations

One case and one deterministic-setting sample per branch; no eight-case viability thresholds, ceiling claims or statistical comparison. Numeric anchoring, source salience, rounding, conservative parsing and possible upstream cue leakage require audit. The monitoring estimate is an intended reference, not a guaranteed posterior in the wording. The terminal target shift is 8.62002 modules, below the provisional ten-point design threshold. Missing scores are retained; no additional elicitation prompts or response-dependent retries were used.
