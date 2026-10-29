# Results and evaluation

The [experimental setup](../experimental_setup.md) describes the calculation environments, model settings, and equipment labels. These CSV files are reported result tables; their display names follow the paper, while archived case and object identifiers are retained for cross-referencing.

| Files | Content |
|---|---|
| `model_comparison.csv` | Twelve main cases for each of the four API model configurations |
| `repeated_runs.csv` | Three runs each for Cases 2, 7, and 11 (archived as T2, V3, and L3); run 1 is included in the main results |
| `load_adjustments.csv`, `bus_voltages.csv`, `line_loading.csv` | Numerical and AC results for the main examples and load-allocation comparison |
| `paired_requirements.csv`, `paired_tokens.csv` | Outcomes and token usage for the six additional B/P pairs (Cases 13–18) |
| `paired_load_adjustments.csv`, `paired_voltages.csv`, `paired_electrical_checks.csv` | Load settings, voltages, and requirement checks for the eleven accepted specifications |
| `generation_load_results.csv`, `generation_load_values.csv` | Generation–load outcomes and electrical values, including the initial and corrected results for Case 19 (S-T) |
| `L4_boundary.csv` | The line-loading boundary failure in Case 12 (L4) |
| `power_flow_settings.csv` | Recorded simulator options used for sensitivity preparation and power-flow verification |
| [`numerical_precision.csv`](numerical_precision.csv), [`numerical_precision.md`](numerical_precision.md) | Fixed-candidate results at 1, 0.1, and 0.01 kVA nodal tolerances |
| [`computational_costs.md`](computational_costs.md) | Generation usage and numerical calculation counts |

## Table notation

B denotes basic constraints and P linked requirements. In the load-allocation comparison, E denotes generated requirements, D the reference requirements, and R the prescribed proportional patterns. `H1` and `H2` identify the two loading targets; `basic` and `voltage` identify the basic and tighter voltage conditions, respectively. Archived case identifiers are retained in the filenames and tables to connect these records with the original task inputs.

`True` and `False` denote the recorded result of a check. `certified` denotes an accepted requirement specification; `passed` denotes successful physical verification. Empty cells indicate that a quantity was not reported or a stage was not reached. `no_candidate` means that the local numerical problem produced no candidate; it does not establish global AC infeasibility.

## Requirement checks

In `paired_requirements.csv`, `automatic_semantic` preserves the original automated score, while `semantic` includes an additional equivalence check before numerical construction. This check compares normalized generated and reference constraints under the existing equivalence rules. For the six load-growth responses, loads already required to remain fixed retain their reference Q/P when both active and reactive inputs are fixed. Recognizing this implication under the prescribed tolerances accounts for the differences between the two columns. The generated answers were unchanged.

Case 20 (S-V) failed the requirement check and did not proceed to numerical adjustment or AC verification.

## Physical observations and token counts

In the paired results, `shared=True` identifies reuse of the other expression's physical observation when the same request produced identical device settings. The eleven accepted specifications are supported by six independent new physical observations and five paired reuses.

The eighteen GPT-6.1-SOL runs used two new independent physical observations and sixteen historical observations. Repeated model generations and shared observations are counted separately from independent power-flow calculations.

The paired token comparison uses the five requests for which both expressions passed the requirement check; Case 14 (N-T2) is excluded. Reductions are calculated from summed token counts. Input and output tokens are service-reported usage, rather than measurements of monetary cost or human effort.

## Electrical quantities

In `generation_load_values.csv`, generator setting values are per machine, whereas actual generator outputs are aggregate values. Column units distinguish MW, Mvar, p.u., loading percentages, and changes in percentage points.

