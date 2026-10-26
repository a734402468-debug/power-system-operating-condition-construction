# Experimental setup

## Simulation environment

The study uses DIgSILENT PowerFactory 2025 SP2 and Python 3.11. The test systems are the IEEE 118-bus system and a real-world sending-end regional power system located in Northwest China. Recorded power-flow options are provided in [power_flow_settings.csv](results/power_flow_settings.csv).

The four language-model configurations use the same equipment data, local response coefficients, numerical adjustment procedure, and AC acceptance checks. Load sensitivities use separate factor perturbations of 0.005 from the reference condition. The generation–load cases also use 0.5 MW per-machine setting perturbations for the two permitted generator elements. Generator settings are per machine; reported generator outputs are aggregate values. Each of these generator elements represents two machines.

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

G1 retains constant-reactive-power control and G2 retains voltage control. Original responses and request excerpts retain their recorded labels. Reported tables retain record identifiers for cross-referencing. In older records, CG denotes the IEEE 118-bus system and NJ denotes the regional system.

## Language-model settings

DeepSeek-V4-Pro is the primary model. The main comparison also includes Qwen3.5-122B-A10B, Qwen3.5-35B-A3B, and GPT-6.1-SOL. All four models are accessed through APIs.

| Setting | DeepSeek and Qwen | GPT-6.1-SOL |
|---|---|---|
| Temperature | 0 | Not explicitly set |
| Top-p | 1 | Not explicitly set |
| Reasoning | Disabled in the request | Medium effort |
| Output-token limit | 4096 tokens | Not explicitly set |
| Requested response | JSON specification | JSON specification |

Output-token limits refer to explicit client-side settings. GPT-6.1-SOL was not given a client-side token limit. The prompt requests a JSON response; JSON formatting is not enforced through an API schema. Each task starts with an independent request. Checking references are withheld from model generation and revision feedback.

## Case schedule and evaluation

Cases 1–12 form the main comparison. Cases 2, 7, and 11 each have three runs per model, with the main run counted as the first. Main cases allow at most one specification revision using the prescribed diagnostic feedback and one AC trial for an accepted specification; they do not allow numerical correction.

Cases 13–18 compare basic constraints (B) and linked requirements (P), using one independent DeepSeek response per expression. These paired cases allow neither specification revision nor numerical correction. Cases 19–21 extend the adjustments to generation and load, allowing one format or adjustment-permission revision where applicable. Case 19 additionally permits one numerical correction after the first AC trial.

Completion requires both a requirement-consistent specification and satisfaction of the original electrical conditions in AC power flow. Repeated model generations, independent AC observations, and reused observations are reported separately in [Results and evaluation](results/README.md).
