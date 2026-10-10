#!/usr/bin/env python3
import json

from tools.audit_cycle import audit_ledgers
from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint, write_once_json
from tools.zeroed_residual import audit


OUTPUT = ARTIFACTS / "cycle04"


def run():
    audit("ranked")
    audit("bifid")
    audit("composition")
    configurations = [(OUTPUT / (stem + "-aes.jsonl"), "evaluations", "digest", "key", "iv", "salt", stem + "-results.json", "aes_trials") for stem in ("ranked-alphabet", "bifid-material", "hash-composition")]
    report = audit_ledgers(configurations, OUTPUT / "aes-ledger-audit.json")
    previous = json.loads((ARTIFACTS / "cycle03/cumulative-aes-audit.json").read_text())
    all_ledgers = previous["audited_ledgers"] + report["audited_ledgers"]
    identifiers = set()
    for ledger in all_ledgers:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("Audited historical ledger changed")
        with path.open() as source:
            identifiers.update(json.loads(line)["password_sha256"] for line in source)
    cumulative = {"id": "C04-CUMULATIVE-AES-AUDIT", "audited_ledgers": all_ledgers, "unique_passwords": len(identifiers), "trial_records": sum(ledger["trials"] for ledger in all_ledgers), "distinct_target_kdf_trials": len(identifiers) * 6, "padding_hit_records": sum(ledger["padding_hits"] for ledger in all_ledgers), "status": "CONFIRMED", "meaning": "Exact cumulative candidate-set overlap accounting. Each ledger has six distinct target/KDF pairs; baseline732 excluded. Audit confirms reproduction, not final private key."}
    write_once_json(OUTPUT / "cumulative-aes-audit.json", cumulative)
    print(json.dumps({key: value for key, value in cumulative.items() if key != "audited_ledgers"}, indent=2))
    return cumulative


if __name__ == "__main__":
    run()
