# Proportional-group constraints in mixed adjustment

For a load group, the required multiplier spread is max(αᵢ) − min(αᵢ) ≤ ε. With xᵢ = (αᵢ − 1)/sᵢ, the equivalent linear constraints are −ε ≤ sᵢxᵢ − sⱼxⱼ ≤ ε for every pair i < j. The tolerance remains in multiplier units.

The mixed-adjustment implementation now assembles these pairwise bounds. Its exact-relation priority retains the original independent equations linking each member to the first member. The objective, bounds, final acceptance function, and other constraint types are unchanged. See the [implementation patch](../checks/proportional_constraints.patch).

The archived implementation bounded each multiplier's difference from the first member. For three or more members, this can permit a full-group spread above ε in the tolerance fallback. Final acceptance already used the full-group condition. The correction was made after the reported experiments; archived code, results, and scores are retained. In the reported mixed-adjustment cases, Case 19 uses free load allocation, Case 21 fixes the loads, and Case 20 stops before numerical solution.

The [offline checks](proportional_constraint_checks.csv) exercise the actual constraint assembly. All 13 checks passed, covering a three-member counterexample, valid combinations, two-member equivalence, unequal normalization scales, the unchanged acceptance rule, and preservation of the independent priority equations and other problem fields. A synthetic problem produced a common factor of 1.02 on the exact-relation branch. These checks use ε = 0.001 to test assembly and do not change the experiment tolerances.

The correction used one synthetic numerical solve, with no LLM call, PowerFactory connection, AC calculation, or historical-candidate recalculation. It adds implementation evidence, not an electrical case or a new construction score.
