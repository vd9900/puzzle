#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint


OUTPUT = ARTIFACTS / "cycle08"


def log_results():
    root = ARTIFACTS.parents[1]
    specifications = [
        ("baseline-identity-audit.json", "Exact preserved baseline candidate identities and overlap", "python3 -m tools.baseline_coverage"),
        ("instruction-order.json", "Primary byte-mapped command sequencing and evidence attribution", "python3 -m tools.instruction_order"),
        ("residual-bifid-results.json", "Prime residual as the one existing Bifid keyword", "python3 -m tools.secret_safe_aes audit --family residual-bifid"),
        ("residual-bifid-audit.json", "Reproduce all secret-safe residual-Bifid AES/Boolean gates", "python3 -m tools.secret_safe_aes audit --family residual-bifid"),
        ("prime-conditioned-bifid-control.json", "Condition source-keyed Bifid prefix control on the prime grammar", "python3 -m tools.prime_bifid_controls"),
        ("cumulative-aes-audit.json", "Exact16-ledger union plus separately bounded baseline identities", "python3 -m tools.audit_cycle08"),
        ("next-post-bifid-routing-plan.json", "Frozen post-Bifid header-preserving matrix-sum route", "python3 -m tools.plan_post_bifid_routing"),
    ]
    ledger = root / "research/candidates.jsonl"
    existing = {entry["id"]: entry for entry in (json.loads(line) for line in ledger.read_text().splitlines())}
    added = 0
    with ledger.open("a") as output:
        for filename, description, command in specifications:
            path = OUTPUT / filename
            document = json.loads(path.read_text())
            plan = json.loads((OUTPUT / "residual-bifid-frozen-plan.json").read_text()) if document["id"].startswith("C08-RESIDUAL-BIFID") else document
            entry = {
                "id": document["id"], "description": description, "status": document["status"],
                "source_evidence": plan.get("source_evidence", []),
                "reasoning": plan.get("justification", document.get("result", document.get("meaning"))),
                "transformation": description, "search_space": plan.get("search_space", {name: document[name] for name in ("passwords", "unique_passwords", "new_aes_trials", "new_passwords") if name in document}),
                "result": document.get("result", document.get("meaning", "Frozen source-derived family; no AES executed")),
                "confidence": "Exact local reproduction only; intermediate prefix/structure is not intended-key verification",
                "artifact": str(path.relative_to(root)), "artifact_sha256": fingerprint(path.read_bytes()),
                "reproduction_command": command, "date": "2026-09-30",
                "secret_policy": "No private-key, AES key/IV, candidate address or decrypted secret byte sequence included; local result and fingerprint metadata only",
            }
            if "TARGET_MATCH" in document:
                entry["TARGET_MATCH"] = document["TARGET_MATCH"]
            if entry["id"] in existing:
                if existing[entry["id"]] == entry:
                    continue
                entry["supersedes"] = entry["id"]
                entry["id"] += ":" + fingerprint(json.dumps(entry, sort_keys=True).encode())[:16]
                if entry["id"] in existing:
                    continue
            output.write(json.dumps(entry, sort_keys=True) + "\n")
            added += 1
    print(f"Appended {added} cycle08 records")


if __name__ == "__main__":
    log_results()
