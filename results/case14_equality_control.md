# Case 14: effect of an additional equal-factor constraint

The original task transfers 0.20 MW from loads L2, L3, and L5 to loads L1, L4, and L6. L3 remains fixed, and L2 and L5 may be adjusted independently. The Basic response introduced an unrequested equal-factor relationship and was rejected by the requirement check.

This numerical comparison starts from the accepted Linked problem. Condition A reproduces that problem; condition B adds only the hard equality $\alpha_2=\alpha_5$. Both use the same inputs, reference state, response coefficients, bounds, objective, and numerical solver. Both obtain a candidate from the exact-relation branch, without tolerance fallback.

| Quantity | A: Linked problem | B: additional equality |
|---|---:|---:|
| L2 factor | 0.9974420644 | 0.9963742421 |
| L5 factor | 0.9957339699 | 0.9963742421 |
| Sum of squared relative load changes | 2.6229843705 × 10⁻⁵ | 2.7780036697 × 10⁻⁵ |
| Original requirements in AC power flow | Passed | Passed |

The objective is the sum of squared changes in the load multipliers from their reference values. Adding the equality increases this dimensionless objective by 5.9100%. Relative to A, B reduces the active input of L2 by a further 0.02207918 MW and increases that of L5 by the same amount; the other four multipliers remain unchanged. Active and reactive inputs retain each load's reference Q/P relationship.

The additional equality therefore changes the allocation and objective value without preventing construction of a point satisfying the original task. The historical Basic 5/6 and Linked 6/6 completion counts retain their original definition, including requirement consistency. This controlled numerical comparison does not alter those scores.

A exactly reproduces the historical candidate and uses its matching AC result. B has a new AC verification. Its commanded equal factors have zero difference; the factors recovered from PowerFactory inputs differ by 3.20054 × 10⁻⁸. This read-back difference is reported separately from the exact command equality. Input and calculation-setting restoration passed, with zero difference in the checked reference results.

## Data

- [Comparison summary](case14_equality_control.csv): solver branch, objective, factors, and AC outcomes.
- [Load adjustments](case14_load_adjustments.csv): all six load factors and commanded/read-back P and Q inputs, in MW and Mvar.
- [Bus voltages](case14_voltages.csv): predicted and AC-calculated voltages, in p.u.; V1–V6 refer to IEEE buses 100–105.

The additional calculation counts are included in [Computational costs](computational_costs.md).
