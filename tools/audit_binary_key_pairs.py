#!/usr/bin/env python3
import argparse
import base64
import json
from collections import Counter
from time import perf_counter

from tools.gsmg import ARTIFACTS, SECONDARY_ADDRESS, TARGET_ADDRESS, candidate_addresses
from tools.research_common import CYCLE, fingerprint, write_once_json
from tools.verify_btc import verify_candidate


OUTPUT = ARTIFACTS / "cycle03"


def key_pairs(payload):
    if not 64 <= len(payload) <= 79:
        return
    for offset in range(len(payload) - 63):
        yield offset, (payload[offset:offset + 32], payload[offset + 32:offset + 64])


def evidence_hits(group="existing"):
    configurations = [(next(CYCLE.glob("C02-INNER-TEXT-*.jsonl")), "cipher_evaluations"), (CYCLE / "joint-aes.jsonl", "evaluations"), (CYCLE / "prime-gap-aes.jsonl", "evaluations"), (CYCLE / "paired-aes.jsonl", "evaluations"), (CYCLE / "coordinate-aes.jsonl", "evaluations"), (OUTPUT / "zeroed-residual-aes.jsonl", "evaluations")]
    if group != "existing":
        paths = {"image": OUTPUT / "image-sum-aes.jsonl", "decimal": OUTPUT / "decimal-residual-aes.jsonl", "ranked": ARTIFACTS / "cycle04/ranked-alphabet-aes.jsonl", "bifid": ARTIFACTS / "cycle04/bifid-material-aes.jsonl", "composition": ARTIFACTS / "cycle04/hash-composition-aes.jsonl", "literal": ARTIFACTS / "cycle05/literal-sumlist-aes.jsonl", "rails": ARTIFACTS / "cycle05/bifid-rails-aes.jsonl"}
        configurations = [(paths[group], "evaluations")]
    for path, evaluations in configurations:
        with path.open() as source:
            for line in source:
                record = json.loads(line)
                for evaluation in record[evaluations]:
                    if not evaluation["padding_valid"] or evaluation["target"] not in ("phase32-inner", "salphaseion-small"):
                        continue
                    recorded = evaluation.get("plaintext_base64", evaluation.get("plaintext"))
                    if isinstance(recorded, dict):
                        recorded = recorded["base64"]
                    plaintext = base64.b64decode(recorded, validate=True)
                    yield {"ledger": str(path.relative_to(ARTIFACTS.parents[1])), "password_sha256": record["password_sha256"], "target": evaluation["target"], "digest": evaluation.get("digest", evaluation.get("kdf_digest")), "plaintext_sha256": fingerprint(plaintext), "plaintext": plaintext}


def make_plan(group="existing"):
    hits = list(evidence_hits(group))
    slots = sum(2 * len(list(key_pairs(hit["plaintext"]))) for hit in hits)
    source_ledger_paths = sorted({hit["ledger"] for hit in hits})
    report = {"id": "C03-BINARY-KEY-PAIRS", "status": "UNTESTED", "source_evidence": [{"path": path, "sha256": fingerprint((ARTIFACTS.parents[1] / path).read_bytes())} for path in source_ledger_paths], "reasoning": "The independently decoded checkerboard refers to two private keys; each 80-byte AES ciphertext admits 64..79 unpadded bytes, enough for two adjacent 32-byte scalars plus at most 15 bytes of metadata", "transformation": "For every saved padding hit in the two 80-byte ciphertexts, test all 0..15 prefix lengths admitting two contiguous 32-byte big-endian keys; remainder treated as metadata, not manually removed", "search_space": {"saved_padding_hits": len(hits), "slot_checks": slots, "public_key_encodings": 2, "scoped_target_addresses": 2, "output_address_count_upper_bound": slots * 2}, "assumptions": "Adjacent fixed-length big-endian scalars, shared start, no arbitrary XOR/split/endian or wide payload scan; format unknown, finite interpretation only", "estimated_primary_ec_seconds": round(slots / 10000, 3), "estimate_basis": "Planning estimate 10000 derivations/sec; actual runtime measured in result, not a benchmark claim", "gate": "Exact target address, then independent pure-Python EC/address verification; halt before publishing matching scalar", "cipher_parameters": "No new AES password trials; inputs are already recorded and audited padding-valid plaintexts"}
    destination = ARTIFACTS / "cycle05" if group in ("literal", "rails") else ARTIFACTS / "cycle04" if group in ("ranked", "bifid", "composition") else OUTPUT
    write_once_json(destination / ("binary-key-pair-plan.json" if group == "existing" else "binary-key-pair-" + group + "-plan.json"), report)
    print(json.dumps(report, indent=2))
    return report


def run(group="existing"):
    stem = "binary-key-pair" if group == "existing" else "binary-key-pair-" + group
    destination = ARTIFACTS / "cycle05" if group in ("literal", "rails") else ARTIFACTS / "cycle04" if group in ("ranked", "bifid", "composition") else OUTPUT
    plan = json.loads((destination / (stem + "-plan.json")).read_text())
    for source in plan["source_evidence"]:
        if fingerprint((ARTIFACTS.parents[1] / source["path"]).read_bytes()) != source["sha256"]:
            raise ValueError("Source ledger changed after planning")
    path = destination / (stem + "-checks.jsonl")
    if path.exists():
        raise ValueError("Preserve completed binary-key verification ledger")
    counts = Counter()
    invalid = 0
    started = perf_counter()
    with path.open("x") as output:
        for hit in evidence_hits(group):
            evidence = {key: value for key, value in hit.items() if key != "plaintext"}
            for offset, pair in key_pairs(hit["plaintext"]):
                for slot, candidate in enumerate(pair):
                    counts[hit["target"]] += 1
                    try:
                        addresses = candidate_addresses(candidate)
                    except ValueError:
                        addresses = {}
                        invalid += 1
                    matched = TARGET_ADDRESS in addresses.values() or SECONDARY_ADDRESS in addresses.values()
                    record = {"source": evidence, "start_offset_zero_based": offset, "key_slot_zero_based": slot, "candidate_sha256": fingerprint(candidate), "addresses": addresses, "target_match": matched}
                    if matched:
                        independent = verify_candidate(candidate)
                        if not independent["main_target_match"] and not independent["secondary_target_match"]:
                            raise ValueError("Independent verifier disagrees with target match")
                        raise RuntimeError("Exact scoped target match independently verified; halt before logging scalar or copying plaintext")
                    output.write(json.dumps(record, sort_keys=True) + "\n")
    slots = sum(counts.values())
    if slots != plan["search_space"]["slot_checks"]:
        raise ValueError("Verified slot count differs from plan")
    report = {"id": plan["id"], "slot_checks": slots, "checks_by_target": dict(counts), "invalid_scalars": invalid, "target_matches": 0, "elapsed_seconds": round(perf_counter() - started, 3), "ledger_sha256": fingerprint(path.read_bytes()), "status": "REJECTED", "result": "No saved padding-valid small-blob plaintext encodes either scoped key as two adjacent 32-byte big-endian scalars with at most 15 bytes prefix/suffix metadata. Other structured binary interpretations remain unknown."}
    write_once_json(destination / (stem + "-results.json"), report)
    print(json.dumps(report, indent=2))
    return report


def audit(group="existing"):
    stem = "binary-key-pair" if group == "existing" else "binary-key-pair-" + group
    destination = ARTIFACTS / "cycle05" if group in ("literal", "rails") else ARTIFACTS / "cycle04" if group in ("ranked", "bifid", "composition") else OUTPUT
    plan = json.loads((destination / (stem + "-plan.json")).read_text())
    path = destination / (stem + "-checks.jsonl")
    summary = json.loads((destination / (stem + "-results.json")).read_text())
    for source in plan["source_evidence"]:
        if fingerprint((ARTIFACTS.parents[1] / source["path"]).read_bytes()) != source["sha256"]:
            raise ValueError("Source AES ledger differs from binary key plan")
    tested = 0
    with path.open() as source:
        for hit in evidence_hits(group):
            evidence = {key: value for key, value in hit.items() if key != "plaintext"}
            for offset, pair in key_pairs(hit["plaintext"]):
                for slot, candidate in enumerate(pair):
                    try:
                        addresses = candidate_addresses(candidate)
                    except ValueError:
                        addresses = {}
                    expected = {"source": evidence, "start_offset_zero_based": offset, "key_slot_zero_based": slot, "candidate_sha256": fingerprint(candidate), "addresses": addresses, "target_match": TARGET_ADDRESS in addresses.values() or SECONDARY_ADDRESS in addresses.values()}
                    if json.loads(source.readline()) != expected:
                        raise ValueError("Recorded binary key-format check does not reproduce")
                    tested += 1
        if source.readline():
            raise ValueError("Unexpected trailing binary key checks")
    if tested != summary["slot_checks"] or tested != plan["search_space"]["slot_checks"] or fingerprint(path.read_bytes()) != summary["ledger_sha256"]:
        raise ValueError("Binary key-format summary differs from the exact planned checks")
    report = {"group": group, "slot_checks": tested, "ledger_sha256": summary["ledger_sha256"], "status": "CONFIRMED", "meaning": "Every recorded key-slot offset, source plaintext hash, scalar fingerprint, both addresses and target gate reproduce; does not solve the puzzle"}
    write_once_json(destination / (stem + "-audit.json"), report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Source-grounded direct binary key-pair verification of existing AES padding hits")
    parser.add_argument("command", choices=("plan", "run", "audit"))
    parser.add_argument("--group", choices=("existing", "image", "decimal", "ranked", "bifid", "composition", "literal", "rails"), default="existing")
    arguments = parser.parse_args()
    commands = {"plan": make_plan, "run": run, "audit": audit}
    commands[arguments.command](arguments.group)
