# Archived method source snapshots

`paired_snapshot/powercaselab/` contains the frozen relation expansion, input checks, and numerical modules selected from the six-pair continuation archive. `paired_snapshot/formal_cases_v1.py` records the paired-study wrapper, including its additional common-factor command equations. The wrapper has orchestration dependencies outside this curated source selection; it is not a stand-alone run command.

`source_load_snapshot/` contains selected numerical source files from the historical export relevant to generation–load construction. These are a separate source context, not a replacement for the paired-study files.

The source files are included to make implementation choices inspectable. No full simulator adapter, service configuration, credential, or commercial model is supplied. `docs/provenance.json` records the selected source hashes. Public copies may redact a private local filesystem root, but numerical rules are not changed during packaging.

Do not use this directory as evidence that a new PowerFactory run has been reproduced. The offline verification and figure scripts at the repository root require no simulator or model-service connection.

A repository-wide software license has not been selected in this prepared distribution. The authors should confirm ownership and applicable permissions before assigning one.
