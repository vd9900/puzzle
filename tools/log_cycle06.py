#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint


OUTPUT = ARTIFACTS / "cycle06"


def log_results():
    root = ARTIFACTS.parents[1]
    configurations = [
        ("C06-LITERAL-REVALIDATION", ARTIFACTS / "cycle05/literal-sumlist-audit.json", "Exact historical literal sum-list plan corresponds to preserved completed execution", "Read frozen generator and reproduce24 lists/4 representations/3 wording compositions without relaunching completed search; saved5184 trials and480 raw-key slots audit", "python3 -m tools.zeroed_residual audit --family literal", ARTIFACTS / "cycle04/next-literal-sumlist-plan.json"),
        ("C06-MISSING-CELL", OUTPUT / "missing-cell-results.json", "Actual near-white-hole annotated matrix axis sums as AES material", "195 source symbols,196 image cells, one anomaly, zeroing clue and sum-list wording fix a finite source-preserving construction; no historical candidate duplicates", "python3 -m tools.secret_safe_aes audit", OUTPUT / "missing-cell-plan.json"),
        ("C06-MISSING-CELL-AUDIT", OUTPUT / "missing-cell-audit.json", "Secret-safe complete trial and raw-key-gate reproduction", "Recompute exact provenance, KEY/IV fingerprints, padding/plaintext fingerprints/scores and local Boolean gates; no secret bytes or candidate addresses in new logs", "python3 -m tools.secret_safe_aes audit", OUTPUT / "missing-cell-plan.json"),
        ("C06-CUMULATIVE-AES-AUDIT", OUTPUT / "cumulative-aes-audit.json", "Exact current cumulative candidate union and trial accounting", "Verify all historical ledger fingerprints and exclude duplicate candidate identifiers before adding the576 new candidates; no secondary campaign counts", "python3 -m tools.audit_cycle06", None),
    ]
    path = root / "research/candidates.jsonl"
    existing = {entry["id"]: entry for entry in (json.loads(line) for line in path.read_text().splitlines())}
    added = 0
    with path.open("a") as output:
        for identifier, artifact, description, reasoning, command, plan_path in configurations:
            document = json.loads(artifact.read_text())
            plan = json.loads(plan_path.read_text()) if plan_path else document
            space = plan.get("search_space", {name: document[name] for name in ("unique_passwords", "distinct_target_kdf_trials", "trial_records", "padding_hit_records") if name in document})
            result = document.get("result", document.get("meaning"))
            if identifier == "C06-LITERAL-REVALIDATION":
                result = "Previously completed864 passwords/5184 AES trials/17 padding hits reproduce; no recognized structure or target.480 qualifying adjacent-key slots also audited; no new search trials."
            entry = {"id": identifier, "description": description, "source_evidence": plan.get("source_evidence", []), "reasoning": reasoning, "transformation": description, "search_space": space, "result": result, "status": document["status"], "confidence": "high for exact bounded local reproduction; no final intended construction established", "reproduction_command": command, "artifact": str(artifact.relative_to(root)), "artifact_sha256": fingerprint(artifact.read_bytes()), "date": "2026-09-30", "TARGET_MATCH": document.get("TARGET_MATCH", False), "candidate_details": "Exact source-derived transformations reproduce locally. New records contain fingerprints/scores/Boolean results only, never candidate private keys, AES key/IV, plaintext bytes or candidate addresses."}
            if identifier == "C06-MISSING-CELL":
                entry["executes_plan"] = "C05-NEXT-MISSING-CELL"
            if identifier in existing:
                if existing[identifier] == entry:
                    continue
                entry["supersedes"] = identifier
                entry["id"] = identifier + ":" + fingerprint(json.dumps(entry, sort_keys=True).encode())[:16]
                if entry["id"] in existing:
                    continue
            output.write(json.dumps(entry, sort_keys=True) + "\n")
            added += 1
    print(f"Appended {added} cycle06 records")


if __name__ == "__main__":
    log_results()
