# Power-flow precision check

[numerical_precision.csv](numerical_precision.csv) reports fixed-input recalculations for the two tightened-voltage solutions, Case 12, and the initial and corrected candidates of Case 19. No candidate was re-optimized.

The archived PowerFactory 15.2.10 setup was used with nodal equation tolerances of 1, 0.1 and 0.01 kVA. Each candidate was calculated once at 1 and 0.1 kVA and three times at 0.01 kVA. Before each repetition, the reference inputs were restored and the previous calculation results were reset; initialization options were unchanged. The model-equation tolerance remained approximately 0.1%.

The pass/fail results use the original reference quantities, absolute bounds and acceptance tolerances. The reference was also recalculated at each nodal tolerance to distinguish changes in absolute values from changes caused by the device adjustments.

| Candidate | 1 kVA | 0.1 kVA | 0.01 kVA, three runs |
|---|---|---|---|
| Loading target 1, tightened voltage | Pass | Pass | Pass in all three |
| Loading target 2, tightened voltage | Pass | Pass | Pass in all three |
| Case 12 | Fail | Fail | Fail in all three |
| Case 19, initial candidate | Fail | Pass | Pass in all three |
| Case 19, corrected candidate | Pass | Pass | Pass in all three |

For the initial Case 19 candidate, the tighter settings raise the reference line flow by approximately 0.000113741 MW. The unchanged candidate consequently crosses the original absolute lower bound. Relative to the reference recalculated at the same tolerance, its line-flow increment is 0.449969679 MW; the corrected candidate gives 0.450030343 MW. These increments remain on opposite sides of the 0.45 MW target. The original construction outcomes are unchanged.

The three runs at 0.01 kVA give identical recorded results for each candidate. All calculations converge, and all input and setting restoration checks pass. The check uses 60 AC calculations: 25 candidate calculations, 25 corresponding reference calculations, five initial reference calculations and five final restoration calculations.

In the CSV, `lower_margin` is the candidate value minus the original lower bound, and `upper_margin` is the original upper bound minus the candidate value. Negative margins indicate a bound violation. Loading values are percentages; their differences and margins are in percentage points. `all_requirements_satisfied` records the complete original acceptance decision, while the numerical columns show the boundary quantity examined for that candidate.
