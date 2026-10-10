#!/usr/bin/env python3
import base64
import json
from collections import Counter
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.gsmg import ARTIFACTS, SOURCES, parse_salted, evp_bytes_to_key
from tools.research_common import CYCLE, fingerprint, score_plaintext, target_checks, write_once_json


def audit_ledgers(configurations=None, output_path=None):
    default_configurations = [
        (next(CYCLE.glob("C02-INNER-TEXT-*.jsonl")), "cipher_evaluations", "kdf_digest", "derived_key_hex", "iv_hex", "salt_hex", "inner-search-results.json", "total_trials"),
        (CYCLE / "joint-aes.jsonl", "evaluations", "kdf_digest", "key", "iv", "salt", "joint-results.json", "aes_trials"),
        (CYCLE / "prime-gap-aes.jsonl", "evaluations", "digest", "key_hex", "iv_hex", "salt_hex", "prime-gap-results.json", "trials"),
        (CYCLE / "paired-aes.jsonl", "evaluations", "digest", "key", "iv", "salt", "paired-results.json", "aes_trials"),
        (CYCLE / "coordinate-aes.jsonl", "evaluations", "digest", "key", "iv", "salt", "coordinate-results.json", "aes_trials"),
    ]
    if configurations is None:
        configurations = default_configurations
    if output_path is None:
        output_path = CYCLE / "ledger-audit.json"
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in ("phase32-inner", "salphaseion-small", "cosmic-duality")}
    audited = []
    all_identifiers = set()
    for path, evaluations_name, digest_name, key_name, iv_name, salt_name, summary_name, total_name in configurations:
        records = 0
        trials = 0
        hits = 0
        targets = Counter()
        candidate_ids = set()
        with path.open() as source:
            for line in source:
                record = json.loads(line)
                password = base64.b64decode(record["password_base64"], validate=True)
                if fingerprint(password) != record["password_sha256"]:
                    raise ValueError(f"Password fingerprint mismatch in {path.name}")
                if record["password_sha256"] in candidate_ids:
                    raise ValueError(f"Duplicate candidate in {path.name}")
                candidate_ids.add(record["password_sha256"])
                records += 1
                if len(record[evaluations_name]) != 6:
                    raise ValueError("Every candidate must have exactly three targets and two KDFs")
                if {(evaluation["target"], evaluation[digest_name]) for evaluation in record[evaluations_name]} != {(target, digest) for target in blobs for digest in ("md5", "sha256")}:
                    raise ValueError("Missing or duplicated target/KDF pair")
                for evaluation in record[evaluations_name]:
                    trials += 1
                    target = evaluation["target"]
                    targets[target] += 1
                    salt, ciphertext = blobs[target]
                    key, initialization_vector = evp_bytes_to_key(password, salt, evaluation[digest_name])
                    if key.hex() != evaluation[key_name] or initialization_vector.hex() != evaluation[iv_name] or salt.hex() != evaluation[salt_name]:
                        raise ValueError(f"Cipher parameter mismatch in {path.name}")
                    padded = AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext)
                    try:
                        plaintext = unpad(padded, 16)
                    except ValueError:
                        if evaluation["padding_valid"]:
                            raise ValueError("Reported padding hit does not reproduce")
                        continue
                    if not evaluation["padding_valid"]:
                        raise ValueError("Unreported padding-valid trial")
                    hits += 1
                    if isinstance(evaluation.get("plaintext"), dict):
                        recorded = base64.b64decode(evaluation["plaintext"]["base64"], validate=True)
                    else:
                        recorded = base64.b64decode(evaluation.get("plaintext_base64", evaluation.get("plaintext")), validate=True)
                    if recorded != plaintext:
                        raise ValueError("Recorded plaintext bytes do not reproduce")
                    if evaluation["score"] != score_plaintext(plaintext):
                        raise ValueError("Recorded score does not reproduce")
                    validity = target_checks(plaintext)
                    if validity["structures"] != evaluation["structural_validity"] or validity != evaluation["downstream_validity"]:
                        raise ValueError("Recorded structural/target gate does not reproduce")
        summary = json.loads((path.parent / summary_name).read_text())
        if summary[total_name] != trials or summary["padding_hits"] != hits or summary["unique_passwords"] != records:
            raise ValueError(f"Summary mismatch in {summary_name}")
        all_identifiers.update(candidate_ids)
        audited.append({"ledger": str(path.relative_to(SOURCES.parents[1])), "ledger_sha256": fingerprint(path.read_bytes()), "records": records, "trials": trials, "padding_hits": hits, "targets": dict(targets), "recomputed": "Every password, KEY/IV/salt, padding status, hit plaintext, score and structural/target gate"})
    report = {"id": "C02-LEDGER-AUDIT", "audited_ledgers": audited, "unique_passwords": len(all_identifiers), "total_trials": sum(row["trials"] for row in audited), "padding_hits": sum(row["padding_hits"] for row in audited), "status": "CONFIRMED", "meaning": "Confirms reproducibility and ledger accounting, not a solution or exhaustive rejection of other hypotheses"}
    write_once_json(output_path, report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    audit_ledgers()
