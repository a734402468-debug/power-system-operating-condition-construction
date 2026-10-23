"""Check reported aggregates against archived records, without new experiments.

This checks accounting and transcription only. It does not call an LLM,
solve a new construction problem, or independently run AC power flow.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


main = read("data/main_api/case_results_summary.json")
require(len(main["cases"]) == 12, "Primary denominator differs from 12")
main_counts = [sum(bool(r[k]) for r in main["cases"])
               for k in ["strict_first_success", "strict_final_success"]]
require(main_counts == [7, 8], "Primary completion counts differ")

new = read("data/new_requirements/case_results.json")
require(len(new["cases"]) == 12, "New-pair trajectory count differs")
new_counts = {m: sum(bool(r["strict_complete"]) for r in new["cases"] if r["method"] == m)
              for m in ["B", "P"]}
require(new_counts == {"B": 5, "P": 6}, "New-pair completion counts differ")

paired = read("data/new_requirements/paired_results.json")
qualified = [r for r in paired["pairs"] if r["both_semantic_qualified"]]
require(len(qualified) == 5, "The token comparison must contain five qualified pairs")
usage = {m: {t: sum(r[f"{m}_{t}_tokens"] for r in qualified)
             for t in ["input", "output", "total"]} for m in ["B", "P"]}
require(usage["B"] == {"input": 29538, "output": 9864, "total": 39402}, "B token sums differ")
require(usage["P"] == {"input": 25955, "output": 4290, "total": 30245}, "P token sums differ")
reductions = {t: 100 * (1 - usage["P"][t] / usage["B"][t]) for t in ["output", "total"]}
require(round(reductions["output"], 2) == 56.51, "Output reduction differs")
require(round(reductions["total"], 2) == 23.24, "Total reduction differs")
ledger = read("data/new_requirements/physical_observation_ledger.json")
require(len(ledger["observations"]) == 6 and len(ledger["sharing"]) == 5,
        "Independent/shared observation counts differ")
require(ledger["AC"] == 18 and ledger["historical_reuse"] is False,
        "New-pair AC accounting differs")

codex = read("data/codex/case_results.json")
codex_main = [r for r in codex["cases"] if r["scope"] == "main"]
repeats = read("data/codex/repeatability_results.json")
unique_codex = {r["id"] for r in codex["cases"] + repeats["runs"]}
require(len(unique_codex) == 18 and len(codex_main) == 12 and len(repeats["runs"]) == 9,
        "Codex denominators differ")
codex_counts = [sum(bool(r[k]) for r in codex_main)
               for k in ["first_strict_success", "final_strict_success"]]
require(codex_counts == [11, 11], "Codex completion counts differ")
require(codex["summary"]["new_independent_observations"] == 2 and
        codex["summary"]["historical_reuse_trajectories"] == 16, "Codex reuse counts differ")

source = read("data/source_load/case_results.json")
require(len(source["cases"]) == 3 and sum(bool(r["strict_complete"]) for r in source["cases"]) == 2,
        "Generation-load completion differs")
require(source["first_call_no_numerical_correction_strict_success"] == 0,
        "Generation-load initial completion differs")

provenance = read("docs/provenance.json")
for row in provenance["files"]:
    p = ROOT / row["file"]
    require(p.is_file(), "Missing distributed evidence: " + row["file"])
    require(hashlib.sha256(p.read_bytes()).hexdigest() == row["public_sha256"],
            "Changed distributed evidence: " + row["file"])

print(json.dumps({
    "status": "passed",
    "scope": "offline record accounting and selected-file integrity only",
    "primary_completion": main_counts,
    "new_pairs_completion": new_counts,
    "qualified_pairs": len(qualified),
    "output_token_reduction_percent": round(reductions["output"], 2),
    "total_token_reduction_percent": round(reductions["total"], 2),
    "new_pair_independent_observations": len(ledger["observations"]),
    "new_pair_shared_observations": len(ledger["sharing"]),
    "codex_completion": codex_counts,
    "generation_load_completion": "2/3",
    "selected_evidence_files_checked": len(provenance["files"]),
    "new_model_calls": 0,
    "new_construction_solves": 0,
    "new_AC_calculations": 0,
}, indent=2))
