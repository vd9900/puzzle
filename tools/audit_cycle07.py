#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint, write_once_json
from tools.secret_safe_aes import audit, load_candidates


OUTPUT = ARTIFACTS / "cycle07"


def run():
    audited = audit("numeric-routing")
    previous = json.loads((ARTIFACTS / "cycle06/cumulative-aes-audit.json").read_text())
    identifiers = set()
    for ledger in previous["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("Historical audited ledger changed")
        with path.open() as source:
            identifiers.update(json.loads(line)[ledger.get("candidate_identifier_field", "password_sha256")] for line in source)
    if len(identifiers) != previous["unique_passwords"]:
        raise ValueError("Historical candidate union differs from its audited count")
    original, candidates, duplicates = load_candidates("numeric-routing")
    if identifiers & set(candidates):
        raise ValueError("Numeric-routing experiment repeats a historical candidate")
    identifiers.update(candidates)
    ledger = {"ledger": str((OUTPUT / "numeric-routing-aes.jsonl").relative_to(ARTIFACTS.parents[1])), "ledger_sha256": audited["ledger_sha256"], "records": audited["unique_passwords"], "trials": audited["aes_trials"], "padding_hits": audited["padding_hits"], "candidate_identifier_field": "password_fingerprint", "recomputed": "Every exact numeric route/provenance, AES/KDF fingerprint, padding, score/structure and local Boolean target/raw-key gate; no secret bytes stored"}
    report = {"id": "C07-CUMULATIVE-AES-AUDIT", "audited_ledgers": previous["audited_ledgers"] + [ledger], "unique_passwords": len(identifiers), "trial_records": previous["trial_records"] + audited["aes_trials"], "distinct_target_kdf_trials": previous["distinct_target_kdf_trials"] + audited["aes_trials"], "padding_hit_records": previous["padding_hit_records"] + audited["padding_hits"], "new_passwords": len(candidates), "previously_tested_passwords_skipped": duplicates, "TARGET_MATCH": audited["TARGET_MATCH"], "status": "CONFIRMED", "meaning": "Exact cumulative union across15 local ledgers; baseline732 separate. No secondary campaign counts or guessed evidence included. Reproduction is not a solved puzzle."}
    write_once_json(OUTPUT / "cumulative-aes-audit.json", report)
    print(json.dumps({name: value for name, value in report.items() if name != "audited_ledgers"}, indent=2))
    return report


if __name__ == "__main__":
    run()
