#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint


OUTPUT = ARTIFACTS / "cycle09"


def log_results():
    root = ARTIFACTS.parents[1]
    specifications = [
        ("post-bifid-routing-results.json", "Exact frozen post-Bifid header/body numeric routing", "python3 -m tools.secret_safe_aes audit --family post-bifid-routing", ARTIFACTS / "cycle08/next-post-bifid-routing-plan.json"),
        ("post-bifid-routing-audit.json", "Reproduce post-Bifid AES/structure/raw-key Boolean gates", "python3 -m tools.secret_safe_aes audit --family post-bifid-routing", ARTIFACTS / "cycle08/next-post-bifid-routing-plan.json"),
        ("exact-prime-bifid-control.json", "Exact prime-conditioned Bifid first-occurrence prefix probability", "python3 -m tools.exact_prime_bifid_control", None),
        ("spiral-ring-sums-results.json", "Verified spiral concentric-ring sums as existing password representations", "python3 -m tools.secret_safe_aes audit --family spiral-ring-sums", OUTPUT / "spiral-ring-sums-frozen-plan.json"),
        ("spiral-ring-sums-audit.json", "Reproduce spiral-ring AES/structure/raw-key Boolean gates", "python3 -m tools.secret_safe_aes audit --family spiral-ring-sums", OUTPUT / "spiral-ring-sums-frozen-plan.json"),
        ("sumlist-codec-preflight.json", "Exact residual-to-fixed-image-sumlist semantic comparison", "python3 -m tools.sumlist_codec_preflight", None),
        ("cumulative-aes-audit.json", "Exact18-ledger union with separately audited baseline identities", "python3 -m tools.audit_cycle09", None),
        ("next-masked-missing-cell-plan.json", "Frozen actual-anomaly-hole placement/image-zeroing/axis-sum construction", "python3 -m tools.plan_masked_missing_cell", None),
    ]
    ledger = root / "research/candidates.jsonl"
    existing = {entry["id"]: entry for entry in (json.loads(line) for line in ledger.read_text().splitlines())}
    added = 0
    with ledger.open("a") as output:
        for filename, description, command, plan_path in specifications:
            path = OUTPUT / filename
            document = json.loads(path.read_text())
            plan = json.loads(plan_path.read_text()) if plan_path else document
            entry = {
                "id": document["id"], "description": description, "status": document["status"],
                "source_evidence": plan.get("source_evidence", []),
                "reasoning": plan.get("justification", document.get("result", document.get("meaning"))),
                "transformation": description, "search_space": plan.get("search_space", {name: document[name] for name in ("unique_passwords", "new_aes_trials", "new_passwords") if name in document}),
                "result": document.get("result", document.get("meaning", "Frozen source-derived family; no AES executed")),
                "confidence": "Exact bounded local reproduction only; intermediate structure/statistical evidence is not reward-key verification",
                "artifact": str(path.relative_to(root)), "artifact_sha256": fingerprint(path.read_bytes()),
                "reproduction_command": command, "date": "2026-09-30",
                "secret_policy": "No private-key, AES key/IV, candidate address or decrypted secret byte sequence included; local Boolean result and fingerprint metadata only",
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
    print(f"Appended {added} cycle09 records")


if __name__ == "__main__":
    log_results()
