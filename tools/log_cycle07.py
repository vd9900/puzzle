#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint


OUTPUT = ARTIFACTS / "cycle07"


def log_results():
    root = ARTIFACTS.parents[1]
    configurations = [
        ("C07-NUMERIC-ROUTING", "numeric-routing-results.json", "Image-axis numeric sum lists as stable columnar routes, optionally before exact Bifid", "The direct-password and missing-cell hypotheses failed. A stable sum-list ordering uses the matrix clue without free ties/alphabets and links the residual/faed/Bifid artifacts; all local prior candidates are excluded", "python3 -m tools.secret_safe_aes audit --family numeric-routing", OUTPUT / "numeric-routing-plan.json"),
        ("C07-NUMERIC-ROUTING-AUDIT", "numeric-routing-audit.json", "Secret-safe exact routing/AES/raw-key-gate reproduction", "Verify all source-preserving route and Bifid round-trips, cipher fingerprints, padding, scores and local Boolean gates; prefixes cannot select a route", "python3 -m tools.secret_safe_aes audit --family numeric-routing", OUTPUT / "numeric-routing-plan.json"),
        ("C07-CUMULATIVE-AES-AUDIT", "cumulative-aes-audit.json", "Exact cumulative local candidate union", "Recompute the historical union and require no overlap with the414 numeric-route candidates; secondary reported counts remain outside local evidence", "python3 -m tools.audit_cycle07", None),
    ]
    path = root / "research/candidates.jsonl"
    existing = {entry["id"]: entry for entry in (json.loads(line) for line in path.read_text().splitlines())}
    added = 0
    with path.open("a") as output:
        for identifier, filename, description, reasoning, command, plan_path in configurations:
            artifact = OUTPUT / filename
            document = json.loads(artifact.read_text())
            plan = json.loads(plan_path.read_text()) if plan_path else document
            space = plan.get("search_space", {name: document[name] for name in ("unique_passwords", "distinct_target_kdf_trials", "trial_records", "padding_hit_records") if name in document})
            entry = {"id": identifier, "description": description, "source_evidence": plan.get("source_evidence", []), "reasoning": reasoning, "transformation": description, "search_space": space, "result": document.get("result", document.get("meaning")), "status": document["status"], "confidence": "high for exact bounded offline reproduction; intended inner-AES key and final derivation still unknown", "reproduction_command": command, "artifact": str(artifact.relative_to(root)), "artifact_sha256": fingerprint(artifact.read_bytes()), "date": "2026-09-30", "TARGET_MATCH": document["TARGET_MATCH"], "candidate_details": "Exact source routes and SHA256/raw transformations regenerate in memory; recorded outcomes contain fingerprints, scores, structure flags and Boolean target gates only."}
            if identifier in existing:
                if existing[identifier] == entry:
                    continue
                entry["supersedes"] = identifier
                entry["id"] = identifier + ":" + fingerprint(json.dumps(entry, sort_keys=True).encode())[:16]
                if entry["id"] in existing:
                    continue
            output.write(json.dumps(entry, sort_keys=True) + "\n")
            added += 1
    print(f"Appended {added} cycle07 records")


if __name__ == "__main__":
    log_results()
