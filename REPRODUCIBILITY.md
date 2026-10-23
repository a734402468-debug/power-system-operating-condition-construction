# Reproducibility and evidence boundaries

## Available checks

1. Read each request together with its generated specification and its recorded requirement check. Reference specifications are explicitly evaluation-only.
2. Recalculate the reported completion counts and the token reductions for the five mutually consistent new pairs using `scripts/verify_reported_results.py`.
3. Inspect the full candidate settings and the available AC acceptance records. The observation ledgers distinguish newly executed candidates from reuse of an identical previously checked condition.
4. Regenerate the manuscript data figures using the two figure scripts. These scripts plot archived values; they do not calculate a new operating condition.
5. Inspect the archived relation-expansion and numerical source snapshots in `code/`. They are provided for method inspection, not as a complete simulator automation installation.

## What these checks do not establish

Successful offline checking does not establish a new independent AC result, reproduce a language-model generation, prove global AC feasibility, or validate an untested request. The published counts must not be increased by replaying a result file or regenerating a plot. Repeated LLM generations and shared physical observations are different units of evidence.

## Conditions for a new simulation run

A new physical run requires the original CG or NJ project with its baseline inputs, equipment mapping, study case, controls, and calculation options; PowerFactory 15.2 and its compatible Python interface; and the task-specific permissions and acceptance conditions. The reported host used Python 3.11 and an isolated Python 3.4.1 interface. The complete network projects are not included in this distribution. CG is an imported network with 118 terminals; equivalence to a standard IEEE case has not been established. NJ contains 200 in-service buses and 33 loads.

The archived experiment configurations are distinct. In particular, common-factor command equations used by the paired-expression studies should not be assumed to have been imposed in every main or Codex task. The source snapshots and archived candidates retain their study identities.

## Numerical interpretation

Task acceptance tolerances, simulator input-storage precision, and load-flow convergence settings serve different purposes. Original target bounds and pass/fail decisions are preserved here. A load-flow convergence residual is not automatically an error bound on every branch result. Fine numerical boundary discrepancies should therefore be interpreted under the recorded protocol and settings, rather than as evidence of a practically significant operating violation. The read-only configuration audit in `data/settings/config_records_public.json` documents the 1 kVA node-equation tolerance and preserves other raw fields without claiming unverified field-to-UI mappings. The older `data/study_settings.json` is retained as a historical extract; its note about unavailable option descriptions predates this limited documentation audit.

## Publication copies

The repository contains selected publication copies rather than every file from the development workspace. Private machine roots are replaced by neutral placeholders, preserving project-relative record locations where possible. Credential/account checks, runtime command lines, event streams, simulator installation files, and complete project files are omitted. `docs/provenance.json` distinguishes source hashes from distribution hashes, and `docs/redactions.json` records affected files without publishing the removed values.

The historical primary case file is distributed as a summary-field extraction to avoid publishing nested live-model snapshots. This extraction is identified in its filename and provenance entry. Scientific values and completion decisions are retained; no model response is corrected during packaging.

Some historical files refer to source-archive paths that are not included in this selected distribution. Those references describe historical provenance, not files guaranteed to be present in the repository. The curated entry points are listed in `docs/EVIDENCE_MAP.md`.

## Remaining author confirmations

- Establish the sources and permitted sharing arrangements for both complete network models.
- Confirm which software and data license applies before assigning a repository-wide license.
- Identify the final publication tag/commit and any archival DOI.
- Use the verified configuration records supplied with the final release when interpreting the simulator option fields; historical extracts may preserve earlier notes about missing field documentation.

These confirmations do not change the recorded experimental outcomes. They concern attribution, access, and reproducibility.
