#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint


OUTPUT = ARTIFACTS / "cycle05"


def log_results():
    root = ARTIFACTS.parents[1]
    configurations = [
        ("C05-LITERAL-SUMLIST", "literal-sumlist-results.json", "Literal image-axis sums as AES material", "Execute unchanged C04 plan and require downstream structure/scoped target, not padding", "python3 -m tools.zeroed_residual audit --family literal", ARTIFACTS / "cycle04/next-literal-sumlist-plan.json"),
        ("C05-BIFID-RAILS", "bifid-rails-results.json", "Exact Bifid coordinate rails as binary/quinary byte material", "Derive both rails from source halves without truncation; test only explicit serialization/order alternatives", "python3 -m tools.zeroed_residual audit --family rails", OUTPUT / "bifid-rails-plan.json"),
        ("C05-PRIME-SELECTION-CONTROL", "prime-selection-controls.json", "Prime/color branch ambiguity and conditional null controls", "Reproduce new secondary claim of five color selections and distinguish subsequence vs continuous-counter assumptions", "python3 -m tools.prime_selection_controls", None),
        ("C05-DIRECT-SOURCE-KEYS", "direct-source-keys-results.json", "Audited source-password exact32/hex64 materials as direct Bitcoin scalars", "Close a hard-oracle gap without inventing new scalar ranges or derivation rules", "python3 -m tools.direct_source_keys audit", OUTPUT / "direct-source-keys-plan.json"),
        ("C05-CUMULATIVE-AES-AUDIT", "cumulative-aes-audit.json", "Reconciled cumulative distinct AES space", "Do not inflate unique candidates or combine unaudited secondary negative counts with local experiments", "python3 -m tools.audit_cycle05", None),
        ("C05-NEXT-MISSING-CELL", "next-missing-cell-plan.json", "195 annotated symbols occupy all image cells except the actual near-white anomaly", "The length deficit, unique anomaly, zeroing clue and sum-list wording motivate a bounded missing-slot construction absent from inspected endpoint-padding code", "python3 -m tools.plan_missing_cell", OUTPUT / "next-missing-cell-plan.json"),
    ]
    for group in ("literal", "rails"):
        configurations.append(("C05-BINARY-KEY-PAIRS-" + group.upper(), "binary-key-pair-" + group + "-results.json", "Adjacent raw-key check on " + group + " small-blob padding hits", "Verify exact target even if bytes are not readable; zero padding hits imply zero slots, not a fresh binary-format elimination", "python3 -m tools.audit_binary_key_pairs audit --group " + group, OUTPUT / ("binary-key-pair-" + group + "-plan.json")))
    path = root / "research/candidates.jsonl"
    existing = {entry["id"]: entry for entry in (json.loads(line) for line in path.read_text().splitlines())}
    added = 0
    with path.open("a") as output:
        for identifier, filename, description, reasoning, command, plan_path in configurations:
            artifact = OUTPUT / filename
            document = json.loads(artifact.read_text())
            plan = json.loads(plan_path.read_text()) if plan_path else document
            result = document.get("result", document.get("meaning", document.get("limits")))
            if document["status"] == "UNTESTED":
                result = "Frozen plan and source-conservation checks only; no AES/private-key trial from this plan has executed"
            sources = plan.get("source_evidence", [])
            entry = {"id": identifier, "description": description, "source_evidence": sources, "reasoning": reasoning, "transformation": description, "search_space": plan.get("search_space", {key: document[key] for key in ("unique_passwords", "distinct_target_kdf_trials", "trial_records", "padding_hit_records") if key in document}), "result": result, "status": document["status"], "confidence": "high for bounded local reproduction; intended final construction remains unknown", "reproduction_command": command, "artifact": str(artifact.relative_to(root)), "artifact_sha256": fingerprint(artifact.read_bytes()), "date": "2026-09-30", "candidate_details": "Exact sources, transforms, provenance, KEY/IV, padding/plaintext scores and hard target gates reside in the linked plan/ledgers. Secondary claims are not added to locally tested totals."}
            if identifier == "C05-LITERAL-SUMLIST":
                entry["executes_plan"] = "C04-NEXT-LITERAL-SUMLIST"
            if identifier in existing:
                if existing[identifier] == entry:
                    continue
                entry["supersedes"] = identifier
                entry["id"] = identifier + ":" + fingerprint(json.dumps(entry, sort_keys=True).encode())[:16]
                if entry["id"] in existing:
                    continue
            output.write(json.dumps(entry, sort_keys=True) + "\n")
            added += 1
    print(f"Appended {added} cycle05 records")


if __name__ == "__main__":
    log_results()
