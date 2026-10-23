# Case examples

The files contain selected recorded model outputs discussed in the paper. They illustrate the relationship between the requested electrical conditions and the generated constraints.

- **T2:** `T2_specification.json` retains the fixed load L1 in the reduction-group total. The resulting load and voltage values appear in the corresponding result tables.
- **N-T2:** the B and P input files give the supplied requirements, instructions, and examples with record-identification fields omitted for the two expression schemes; the response files preserve their generated answers. B adds an equal-factor condition for L2 and L5 despite the free-allocation requirement and stops before numerical solution. P passes the checks. This comparison does not establish global infeasibility under the additional condition.
- **S-V:** `S-V_response.json` applies proportional load growth at every accepted state although it was requested only at the final state. The specification is rejected before numerical or power-flow calculation. The requested final targets were a 2 MW increase in the sum of per-machine generator settings and a Jinx230 voltage reduction of 0.00015–0.00020 p.u.

Recorded model outputs retain their original identifiers and wording. The N-T2 input files include the supplied syntax examples; these are part of the experimental inputs, not additional case results.
