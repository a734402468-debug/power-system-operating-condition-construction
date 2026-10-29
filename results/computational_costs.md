# Computational costs

The counts below refer to the reported study blocks. AC calculations include reference and restoration calculations as well as candidate verification. Reused results do not add AC calculations.

| Study block | Known generation tokens | Adjustment calculations | New candidate verifications | New AC calculations |
|---|---:|---:|---:|---:|
| Main DeepSeek cases (Cases 1–12) | 95,206 | 9 | 9 | 27 |
| Additional load-allocation comparisons | 18,538 | 2 | 4 | 12 |
| Additional Qwen configurations and API repeat runs | 395,864 | 21 | 1 | 3 |
| GPT configuration: main cases and repeats | 284,355 | 18 | 2 | 6 |
| Generation–load cases (Cases 19–21) | 30,520 | 3 | 2 | 6 |
| Paired formulation cases (Cases 13–18) | 87,215 | 11 | 6 | 18 |
| Numerical-precision check | 0 | 0 | 25 | 60 |
| Case 14 equal-factor comparison | 0 | 2 | 1 | 3 |

The main DeepSeek cases use 13 generation requests, including specification revision. The additional allocation comparison uses two new generation requests; its four new candidate verifications include two proportional-allocation results. First-level observations shared with the main cases are reused.

The additional Qwen and repeat-run block records 51 formal requests and two compatibility probes. Two requests have unknown token usage, so the table gives the known total. This block excludes the original DeepSeek main cases.

The GPT block contains eighteen runs: twelve main runs and six additional repeats. Its formal usage comprises 264,924 input tokens and 19,431 output tokens, including 1,516 reasoning tokens. Two separate compatibility probes use 36,737 tokens and are excluded from the table. Sixteen candidate results reuse matching historical observations; two require new AC verification.

The generation–load block records four formal generation requests. A separate probe uses 21 tokens. The three adjustment calculations comprise the initial and corrected Case 19 candidates and the Case 21 candidate. Case 21 reuses a matching AC result. Earlier preparation records contain three incomplete calls with unknown token usage and 21 AC calculations; these are separate from the completed study block shown above.

The paired formulation block contains twelve completed requests, with 69,420 input and 17,795 output tokens. One preceding request returned no answer; its usage is unknown. Six reference adjustment calculations prepared the tasks before generation and are separate from the eleven calculations driven by accepted responses. The eleven accepted specifications use six new candidate verifications and five paired reuses.

The numerical-precision check recalculates five fixed candidates in 25 trials. Its 60 AC calculations comprise 25 candidate calculations, 25 corresponding reference calculations, five initial reference checks, and five restoration checks. It uses no new generation or optimization.

The Case 14 comparison uses two adjustment calculations and no new model generation. Condition A reproduces the historical Linked candidate and reuses its matching AC result. Condition B adds one independent candidate verification; its three AC calculations comprise the reference, candidate, and restoration calculations. These counts are additional to the original paired formulation block.

## Sensitivity preparation

The IEEE 118-bus response preparation records eleven AC calculations. Regional-system load responses use a six-calculation session: one reference, four separate load perturbations, and one restoration. Voltage and line-loading sensitivities come from the same perturbations. These preparation calculations are separate from the study blocks above.

## Recorded durations

| Study block | Generation duration (s) | PowerFactory-session duration (s) |
|---|---:|---:|
| Main DeepSeek cases | 305.5 | 2,650.6 |
| Additional load-allocation comparisons | 46.8 | 1,448.5 |
| Additional Qwen configurations and API repeat runs | 2,058.6 | 517.3 |
| Paired formulation cases | 503.9 | 3,020.7 |

The API-extension generation duration covers formal calls. PowerFactory-session durations include connection, checks, extraction, and restoration. The paired block's overall execution duration is 3,529.8 s. Component durations can overlap and are not added to the overall duration. Monetary charges and human preparation time were not measured.
