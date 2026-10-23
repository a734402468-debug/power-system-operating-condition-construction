# Supplementary materials for operating-condition construction

Supporting materials for **Constraint-guided construction of power-system operating conditions from natural-language requirements**.

The study translates written electrical requirements into linked constraints, calculates permitted load and generator adjustments, and checks the resulting steady-state condition by AC power flow. Requirement consistency is checked against separately prepared references. The materials document the reported experiments; preparing this repository did not add model calls, numerical construction experiments, or power-flow runs.

## Start here

- [Supplementary methods](supplement.pdf), with source in [supplement.tex](supplement.tex): supporting settings, evaluation rules, and evidence accounting, Sections S1–S8.
- [Reproducibility](REPRODUCIBILITY.md): what can be checked offline and what requires the original simulation environment.
- [Evidence map](docs/EVIDENCE_MAP.md): manuscript results and their corresponding files.
- [Publication copies and redactions](docs/redactions.json): private filesystem roots and any credential values are removed from distribution copies. Original scientific records are not rescored.
- [Verified configuration records](data/settings/config_records_public.json): archived solver fields and the scope of their documented interpretation.
- [Source provenance](docs/provenance.json): source and distribution hashes for selected archived files.

## Repository contents

| Directory | Contents |
|---|---|
| `docs/` | Supplementary text, evidence map, and provenance |
| `data/main_requests/` | Twelve main requests, supplied contexts, and evaluation-only reference specifications |
| `data/main_api/`, `data/api_comparison/` | Historical main and three-API outcomes and selected responses |
| `data/new_requirements/` | Six later B/P pairs, requests, generated answers, candidates, checks, and physical-observation accounting |
| `data/source_load/`, `data/supplement/` | Generation–load extension and supplementary result extracts |
| `data/codex/` | Separate Codex configuration, twelve main runs, six additional runs, and physical reuse records |
| `data/T2_*` | Existing T2 example: generated expression and verified construction |
| `code/` | Archived relation-expansion and numerical source snapshots; see `code/README.md` |
| `scripts/` | Offline result checks and regeneration of the manuscript data figures |

The `isolated_correct_specification.json` files are evaluation references. They were withheld from the language model and from answer revision. Their presence in this public package must not be interpreted as model input. Requests and answers may be in Chinese, as used in the recorded studies.

## Reported scope

The primary DeepSeek configuration completed 7/12 requests initially and 8/12 after the permitted revision. The two Qwen configurations completed 6/12→7/12 and 2/12→3/12. The separate Codex configuration completed 11/12, with all twelve requirement descriptions accepted. These are evaluated configurations, not a strict cross-protocol model ranking.

The six new pairs completed 5/6 with basic expressions and 6/6 with linked expressions. The only difference was an unrequested proportionality constraint. All eleven admitted specifications passed their electrical checks, supported by six independent new physical observations and five within-pair reuses. For the five mutually consistent pairs, output tokens decreased from 9,864 to 4,290 and total input-plus-output tokens from 39,402 to 30,245. The percentages describe this comparison of complete expression schemes; they do not establish a general accuracy or engineering-effort advantage.

The generation–load extension completed two of three requests within its stated budgets. S-T required one numerical correction, S-L one specification revision and a matching historical observation, and S-V failed requirement interpretation. The very small L4 boundary discrepancy remains a strict failure under the original acceptance rules.

## Important availability limits

This repository supports inspection of requirements, generated specifications, recorded candidates, evaluations, and plotted results. It does **not** contain complete CG/NJ PowerFactory network projects, a PowerFactory installation, proprietary manuals, or service credentials. Re-running the AC calculations requires the original models, compatible licensed software, and matching controls and calculation settings. Recorded local sensitivities and selected device data do not reconstruct the complete networks.

Exact hosted model snapshots were not returned in the archived evidence. Fresh generations may differ from the recorded responses. The Codex calling protocol differs from the original API protocol. Network-model origin and redistribution permissions, and the software/data license for the repository, must be confirmed by the authors before describing a public release as fully reproducible.

## Offline use

```bash
python scripts/verify_reported_results.py
python -m pip install -r requirements-figures.txt
python scripts/make_figures.py
python scripts/make_source_load_figure.py
```

The verification and figure commands use archived files only. They do not contact a language-model service or a simulator. The figure scripts write their output into `figures/`.

Compile the supplement from the repository root with `latexmk -pdf supplement.tex` in an environment with the standard packages listed in its preamble. The repository release accompanying the paper should be identified by a fixed tag or commit. No release DOI is assigned in this prepared package.
