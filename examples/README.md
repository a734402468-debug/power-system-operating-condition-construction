# Examples of requirement interpretation

These selected model outputs show how the requested electrical conditions were expressed as constraints. Case numbers follow the paper; the identifiers in parentheses locate the original records.

## Case 2: Load redistribution with one fixed load (T2)

`T2_specification.json` retains the fixed load L1 in the reduction-group total. The resulting load settings and bus voltages are reported in the corresponding result tables.

## Case 14: Reverse group redistribution with one fixed load (N-T2)

The B and P input files contain the requirements, instructions, and syntax examples supplied to the two expression schemes, with record-identification fields omitted. The response files preserve the generated answers. B adds an equal-factor condition for L2 and L5 despite the requested free allocation, so it is rejected before numerical solution. P passes the checks. The failure of B concerns the added requirement; physical feasibility under that additional condition was not tested.

## Case 20: Generation adjustment and load growth for a voltage target (S-V)

`S-V_response.json` applies proportional load growth at every accepted state, although it was requested only at the final state. This change in the scope of the requirement leads to rejection before numerical adjustment or power-flow calculation. The requested final targets were a 2 MW increase in the sum of per-machine generator settings and a target-bus voltage reduction of 0.00015–0.00020 p.u.

The JSON responses and request excerpts are unchanged and retain their original identifiers and wording. The [equipment-label table](../experimental_setup.md#equipment-labels) links those original names to the labels used in the paper and reported results. The syntax examples in the Case 14 input files are part of the experimental inputs, rather than additional case results.

