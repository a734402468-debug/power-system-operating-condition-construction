# Evidence map

## Supplement sections

| Section | Subject | Source label retained in LaTeX |
|---|---|---|
| S1 | Reference load inputs and acceptance precision | `app:catalogue` |
| S2 | Outcome and evidence accounting | `app:accounting` |
| S3 | Sensitivity preparation and power-flow settings | `app:settings` |
| S4 | Additional operating requirements: evaluation and execution | `app:new-requirements` |
| S5 | Development study of linked requirement expressions | `app:development-pairs` |
| S6 | Detailed model results and repeated runs | `app:model-details` |
| S7 | Codex supplement protocol | `app:codex-protocol` |
| S8 | Incremental execution costs | `app:costs` |

The previous appendix figure of API results is Figure S1 in the standalone supplement. Main-manuscript references in the supplement use descriptive names to avoid changing their meaning when the main text's tables are renumbered.

## Main results and files

| Result | Entry points |
|---|---|
| T2 generated relationships and numerical expansion | `data/T2_generated_complete.json`, `data/T2_generated_excerpt.json`, `data/T2_result_excerpt.json` |
| Twelve main requests and evaluation references | `data/main_requests/<task>/original_requirements.txt`, `context.json`, `isolated_correct_specification.json` |
| Primary and three-API completion | `data/main_api/case_results_summary.json`, `data/api_comparison/case_results.json` |
| Load allocation and voltage-band comparison | `scripts/figure_data.json`, `data/main_api/preservation_local_effect.json` |
| Six new B/P pairs | `data/new_requirements/case_results.json`, `paired_results.json`, `task_definitions.json` |
| New-pair prompts and final answers | `data/new_requirements/trajectories/<case>_<scheme>/http_request_body.utf8`, `answer.json` |
| New-pair independent observations and sharing | `data/new_requirements/physical_observation_ledger.json`, `electrical_acceptance.csv`, `restoration_summary.csv` |
| New-pair token comparison | `data/new_requirements/paired_results.json`, `paired_usage.csv` |
| Generation–load results and correction | `data/source_load/case_results.json`, `correction_policy.json`, `data/source_load_plot_data.json` |
| Codex main/repeated results | `data/codex/case_results.json`, `repeatability_results.json` |
| Codex prompts and final answers | `data/codex/trajectories/<run>/generation_1/messages.json`, `answer.json` |
| Codex physical reuse | `data/codex/physical_observation_ledger.csv`, per-run `shared_physical_evidence.json` |
| Verified solver settings | `data/settings/config_records_public.json` |
| L4 retained strict failure | `data/codex/L4_physical_failure_detail.json` |
| Figure regeneration | `scripts/make_figures.py`, `scripts/make_source_load_figure.py` |

Not every trajectory contains a physical record. A requirement mismatch stops before numerical/physical execution; a shared observation is identified by its reuse record. Neither absence should be replaced by a fabricated or newly inferred result.
