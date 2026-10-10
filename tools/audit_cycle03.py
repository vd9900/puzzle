#!/usr/bin/env python3
import base64
import json

from tools.audit_cycle import audit_ledgers
from tools.gsmg import ARTIFACTS
from tools.image_sum_derivation import candidates
from tools.research_common import CYCLE, fingerprint, write_once_json
from tools.zeroed_residual import OUTPUT, audit as audit_zeroed


def run():
    audit_zeroed()
    if (OUTPUT / "decimal-residual-aes.jsonl").exists():
        audit_zeroed("decimal")
    passwords, forms = candidates()
    plan = json.loads((OUTPUT / "image-sum-plan.json").read_text())
    if fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))) != plan["candidate_set_sha256"] or json.loads((OUTPUT / "image-sum-decodes.json").read_text()) != forms:
        raise ValueError("Image-sum password set or full decoding ledger does not derive from source")
    with (OUTPUT / "image-sum-aes.jsonl").open() as source:
        identifiers = set()
        for line in source:
            entry = json.loads(line)
            identifier = entry["password_sha256"]
            if identifier not in passwords or identifier in identifiers:
                raise ValueError("Unplanned/duplicate image-sum candidate")
            identifiers.add(identifier)
            if base64.b64decode(entry["password_base64"], validate=True).hex() != passwords[identifier]["password_hex"] or entry["provenance"] != passwords[identifier]["provenance"]:
                raise ValueError("Image-sum derivation/provenance changed")
        if identifiers != set(passwords):
            raise ValueError("Incomplete image-sum password coverage")
    configurations = [(OUTPUT / "zeroed-residual-aes.jsonl", "evaluations", "digest", "key", "iv", "salt", "zeroed-residual-results.json", "aes_trials"), (OUTPUT / "image-sum-aes.jsonl", "evaluations", "digest", "key", "iv", "salt", "image-sum-results.json", "aes_trials")]
    if (OUTPUT / "decimal-residual-aes.jsonl").exists():
        configurations.append((OUTPUT / "decimal-residual-aes.jsonl", "evaluations", "digest", "key", "iv", "salt", "decimal-residual-results.json", "aes_trials"))
    report = audit_ledgers(configurations, OUTPUT / "aes-ledger-audit.json")
    previous = json.loads((CYCLE / "ledger-audit.json").read_text())
    all_ledgers = previous["audited_ledgers"] + report["audited_ledgers"]
    identifiers = set()
    for ledger in all_ledgers:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("Audited ledger changed")
        with path.open() as source:
            identifiers.update(json.loads(line)["password_sha256"] for line in source)
    cumulative = {"id": "C03-CUMULATIVE-AES-AUDIT", "audited_ledgers": all_ledgers, "unique_passwords": len(identifiers), "trial_records": sum(ledger["trials"] for ledger in all_ledgers), "distinct_target_kdf_trials": len(identifiers) * 6, "padding_hit_records": sum(ledger["padding_hits"] for ledger in all_ledgers), "status": "CONFIRMED", "meaning": "Exact cumulative distinct-space accounting across cycle02/03; every ledger covers the same six target/KDF pairs. Baseline 732 trials excluded. Reproduction does not solve the puzzle."}
    write_once_json(OUTPUT / "cumulative-aes-audit.json", cumulative)
    print(json.dumps({key: value for key, value in cumulative.items() if key != "audited_ledgers"}, indent=2))
    return cumulative


if __name__ == "__main__":
    run()
