# Experimental setup

## Test systems and calculation environment

The test systems are the IEEE 118-bus system and a real-world sending-end regional power system in Northwest China. The regional model has 200 in-service buses and 33 loads. Six loads in the IEEE system and four in the regional system are selected for adjustment.

The archived case results were calculated with DIgSILENT PowerFactory 15.2.10.0. The numerical-precision check replays the fixed candidates in that environment. The implementation has subsequently been migrated to PowerFactory 2025 SP2 and Python 3.11.4; the migrated environment does not replace the calculation settings associated with the archived results. Recorded load-flow options are provided in [power_flow_settings.csv](results/power_flow_settings.csv).

## Reference inputs and adjustment bounds

The following reference load inputs are rounded for display. Calculations and acceptance checks use the stored values at full precision. Load identifiers are local to each network.

| System | Load | Active input (MW) | Reactive input (Mvar) |
|---|---|---:|---:|
| IEEE 118-bus | L1 | 160.000000 | 18.000000 |
| IEEE 118-bus | L2 | 20.676830 | 15.000000 |
| IEEE 118-bus | L3 | 5.012950 | 3.000000 |
| IEEE 118-bus | L4 | 21.871719 | 16.000000 |
| IEEE 118-bus | L5 | 34.484051 | 25.000000 |
| IEEE 118-bus | L6 | 28.408331 | 26.000000 |
| Regional | L1 | 258.899994 | 84.500000 |
| Regional | L2 | 71.400002 | 48.799999 |
| Regional | L3 | 51.000000 | 10.700000 |
| Regional | L4 | 32.000000 | −3.600000 |

Load factors lie in [0.99, 1.02] for redistribution and line-loading studies. For load-growth studies, the bounds are [1, 1.20] in the IEEE system and [1, 1.02] in the regional system. Each load retains its own reference Q/P ratio. Fixed loads retain their reference active and reactive inputs.

The generation–load cases use two non-slack generator elements, each representing two machines. Editable active-power setpoints are per machine; reported generator outputs are aggregate values. The permitted setting change is at most 5% of its reference value, capped at 10 MW per machine and restricted by the model bounds. The resulting intervals are [166.25, 183.75] MW per machine for G1 and [159.6, 176.4] MW per machine for G2. Selected actual generator P/Q outputs are checked against the recorded model limits. The balancing-source bounds are ±20 MW and ±20 Mvar about its reference output. Generator reactive-power and voltage setpoints, control modes, and equipment status remain unchanged.

## Local responses and acceptance precision

Load sensitivities use separate factor perturbations of 0.005 from the reference condition, scaling active and reactive inputs together. The generation–load cases also use 0.5 MW per-machine perturbations for G1 and G2. The mixed adjustment scales are 0.02 for load factors and 2 MW per machine for generator settings. These response coefficients and scales remain fixed during candidate calculation and the single numerical correction in Case 19.

The original node-equation convergence tolerance is 1 kVA; the model-equation tolerance is approximately 0.1%. The [numerical-precision check](results/numerical_precision.md) also evaluates nodal tolerances of 0.1 and 0.01 kVA. These convergence settings are separate from the task acceptance tolerances below.

| Acceptance quantity | IEEE 118-bus system | Regional system |
|---|---:|---:|
| Active-input total or transfer error (MW) | 1.3636184692382813 × 10⁻⁵ | 2.388818359375 × 10⁻⁵ |
| Per-load Q − (Q⁰/P⁰)P residual (Mvar) | 3.3364502601314728 × 10⁻⁶ | 9.794873805516215 × 10⁻⁶ |
| Factor read-back error | 10⁻⁷ | 10⁻⁷ |
| Within-group factor spread | 2 × 10⁻⁷ | 2 × 10⁻⁷ |

Fixed inputs are checked against their exact reference values. Voltage and line-loading bounds have no additional endpoint allowance. Each transfer side and the retained total are checked separately. The input-storage allowances are already included in these tolerances, and results are checked before presentation rounding.

## Equipment labels

The following correspondence applies to the regional system. Load and bus identifiers are local to each test system. IEEE 118-bus numbers and names retain their conventional form.

| Device | Label used in the paper and reported tables | Original name | Record identifier |
|---|---|---|---|
| Load | Load 1 (L1) | Shuf_lod; Shuf | L1 |
| Load | Load 2 (L2) | Jinx_lod; Jinx | L2 |
| Load | Load 3 (L3) | Aoy_load; Aoy | L3 |
| Load | Load 4 (L4) | Seli_lod; Seli | L4 |
| Bus | Bus 1 | Shuf115 | V1 |
| Bus | Bus 2 | Jinx230 | V2 |
| Bus | Bus 3 | Aoy115 | V3 |
| Bus | Bus 4 | Seli230 | V4 |
| Line | Line 1 | Yonga-Jinx | E1 |
| Line | Line 2 | Jinl-Seli | E2 |
| Generator element | G1 | Yonga_PHS | G1 |
| Generator element | G2 | Shenk_FE | G2 |

G1 retains constant-reactive-power control and G2 retains voltage control. Original responses and request excerpts retain their recorded labels. Reported tables retain record identifiers for cross-referencing. In the original records, CG denotes the IEEE 118-bus system and NJ denotes the regional system.

## Language-model configurations

DeepSeek-V4-Pro is the primary model. Cases 1–12 also use Qwen3.5-122B-A10B, Qwen3.5-35B-A3B, and GPT-6.1-SOL. All four models are accessed through APIs. DeepSeek and both Qwen configurations use temperature 0, top-p 1, disabled reasoning, and a 4096-token output limit. GPT-6.1-SOL uses medium reasoning effort.

Each task starts independently. The prompt requests a JSON specification, without an API-enforced JSON schema. Checking references are withheld from model generation and revision feedback. All configurations use the same equipment data, response coefficients, adjustment procedure, and AC acceptance criteria.

## Case schedule and evaluation

The researchers prepare a task-specific checking specification during task design, recording equipment, adjustable variables, input relationships, bounds, tolerances, and applicable states. Generated specifications are compared with this reference before numerical solution. Candidate settings are calculated from the accepted generated constraints.


Cases 1–12 form the main comparison. Cases 2, 7, and 11 each have three runs per model, including the main run. These cases allow at most one specification revision using the prescribed diagnostic feedback and one AC trial for an accepted specification.

Cases 13–18 compare basic constraints (B) and linked requirements (P), using one independent DeepSeek response per expression with the respective instructions and examples. These paired cases allow neither specification revision nor numerical correction. Cases 19–21 extend the adjustments to generation and load, allowing one format or adjustment-permission revision where applicable. Case 19 also permits one numerical correction after the first AC trial.

Completion requires both a requirement-consistent specification and satisfaction of the original electrical conditions in AC power flow. An AC result is reused only when complete candidate and reference inputs, reference results, network settings, calculation options, and controls match. Each generated specification is checked independently. [Results and evaluation](results/README.md) distinguishes repeated generation, independent candidate verifications, and shared results.

## Power-flow sign conventions

Positive generator and balancing-source active or reactive output denotes injection into the modelled network. The reported output changes are differences from the reference values. Line 2 active power is read at its first terminal (`m:P:bus1`), with positive flow directed into the line.
