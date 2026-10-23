# Result tables

| Files | Content |
|---|---|
| `model_comparison.csv` | Twelve main cases for each of the three API models and the separate Codex configuration |
| `repeated_runs.csv` | Three runs each for T2, V3, and L3; run 1 is already included in the main results |
| `load_adjustments.csv`, `bus_voltages.csv`, `line_loading.csv` | Numerical and AC results for the main examples and load-allocation comparison |
| `paired_requirements.csv`, `paired_tokens.csv` | Outcomes and token usage for the six additional B/P pairs |
| `paired_load_adjustments.csv`, `paired_voltages.csv`, `paired_electrical_checks.csv` | Load settings, voltages, and requirement checks for the eleven admitted specifications |
| `generation_load_results.csv`, `generation_load_values.csv` | Generation–load outcomes and electrical values, including the initial and corrected S-T results |
| `L4_boundary.csv` | The retained line-loading boundary failure |
| `power_flow_settings.csv` | Recorded simulator options; their interpretation is discussed in Supplementary Section S3 |

## Reading the tables

B denotes basic constraints and P linked requirements. In the load-allocation comparison, E denotes generated requirements, D the reference requirements, and R the prescribed proportional patterns. `H1` and `H2` identify the two loading targets; `basic` and `voltage` identify the basic and tighter voltage conditions, respectively.

`True` and `False` denote the recorded result of a check. `certified` denotes an accepted requirement specification; `passed` denotes successful physical verification. Empty cells indicate that a quantity was not reported or a stage was not reached. `no_candidate` refers to the local numerical problem, not a proof of global AC infeasibility.

In `paired_requirements.csv`, `automatic_semantic` retains the original automated check and `semantic` the subsequent assessment under the existing equivalence rules. Their difference for the load-growth requests is explained in Supplementary Section S4. No generated answer was changed. `shared=True` identifies use of the other expression's physical observation for identical settings on the same request. Eleven admitted specifications are supported by six independent new physical observations and five paired reuses.

The API and Codex configurations have different calling conditions and are reported separately. The Codex study used two new independent physical observations and sixteen historical observations across its eighteen runs. Repeated generations and shared observations are not independent power-flow repetitions.

The paired token comparison uses the five requests for which both expressions passed the requirement check; N-T2 is excluded. The reductions are calculated from summed tokens. Input and output tokens are service-reported counts and do not measure monetary cost or human effort.

In `generation_load_values.csv`, generator setting values are per machine; actual generator outputs are aggregate values. S-V failed the requirement check and has no numerical or AC result in this study. Its earlier reference-only observation is not included in these results.

Columns containing units identify MW, Mvar, p.u., loading percentages, or changes in percentage points.
