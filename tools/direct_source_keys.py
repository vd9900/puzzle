#!/usr/bin/env python3
import argparse
import base64
import json
import re
from time import perf_counter

from tools.gsmg import ARTIFACTS, SECONDARY_ADDRESS, TARGET_ADDRESS, candidate_addresses
from tools.research_common import fingerprint, source_record, write_once_json
from tools.verify_btc import verify_candidate


OUTPUT = ARTIFACTS / "cycle05"


def derive_candidates():
    cumulative = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
    candidates = {}
    for ledger in cumulative["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("An audited source password ledger changed")
        with path.open() as source:
            for line in source:
                entry = json.loads(line)
                password = base64.b64decode(entry["password_base64"], validate=True)
                if fingerprint(password) != entry["password_sha256"]:
                    raise ValueError("Source password fingerprint differs")
                representations = []
                if len(password) == 32:
                    representations.append(("exact-raw32", password))
                if re.fullmatch(rb"[0-9a-fA-F]{64}", password):
                    representations.append(("exact-hex64", bytes.fromhex(password.decode("ascii"))))
                for representation, scalar in representations:
                    candidate = candidates.setdefault(fingerprint(scalar), {"scalar": scalar, "provenance": []})
                    candidate["provenance"].append({"ledger": ledger["ledger"], "password_sha256": entry["password_sha256"], "representation": representation})
    return candidates


def make_plan():
    candidates = derive_candidates()
    report = {"id": "C05-DIRECT-SOURCE-KEYS", "status": "UNTESTED", "source_evidence": [source_record(OUTPUT / "cumulative-aes-audit.json"), source_record(ARTIFACTS / "phase32-checkerboard.txt", "Decoded instruction explicitly references private keys")], "hypothesis": "One of the already source-derived exact32-byte/hex64 password materials is itself the Bitcoin scalar, rather than an AES password", "invariant": "No arbitrary scalar enumeration, additional hashing, truncated windows, endian variants or derivation paths. Every candidate traces to an audited source-clue password.", "search_space": {"distinct_source_scalars": len(candidates), "public_key_encodings": ["compressed", "uncompressed"], "scoped_addresses": [TARGET_ADDRESS, SECONDARY_ADDRESS], "address_derivations": len(candidates) * 2, "new_aes_trials": 0}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(candidate["scalar"] for candidate in candidates.values()))), "candidate_fingerprints": sorted(candidates), "estimated_primary_ec_seconds": round(len(candidates) / 1000, 3), "estimate_basis": "Planning estimate1000 scalars/second based on earlier recorded adjacent-key runs; actual runtime recorded separately", "gate": "Exact target match, then independent pure-Python EC/address verification; halt before logging a matching scalar", "limits": "Only exact source formats already tested as AES passphrases. Does not reject other interpretations, transformed keys, or full puzzle pipeline. Secondary address association remains community-attributed."}
    write_once_json(OUTPUT / "direct-source-keys-plan.json", report)
    print(json.dumps({name: value for name, value in report.items() if name != "candidate_fingerprints"}, indent=2))
    return report


def load_plan():
    plan = json.loads((OUTPUT / "direct-source-keys-plan.json").read_text())
    for evidence in plan["source_evidence"]:
        if fingerprint((ARTIFACTS.parents[1] / evidence["path"]).read_bytes()) != evidence["sha256"]:
            raise ValueError("Direct-key plan source changed")
    candidates = derive_candidates()
    if sorted(candidates) != plan["candidate_fingerprints"] or len(candidates) != plan["search_space"]["distinct_source_scalars"] or fingerprint(b"\x00".join(sorted(candidate["scalar"] for candidate in candidates.values()))) != plan["candidate_set_sha256"]:
        raise ValueError("Direct-key candidate set changed after planning")
    return plan, candidates


def evaluate(identifier, candidate):
    try:
        addresses = candidate_addresses(candidate["scalar"])
    except ValueError:
        addresses = {}
    match = TARGET_ADDRESS in addresses.values() or SECONDARY_ADDRESS in addresses.values()
    if match:
        independent = verify_candidate(candidate["scalar"])
        if not independent["main_target_match"] and not independent["secondary_target_match"]:
            raise ValueError("Target gate disagrees with independent verifier")
        raise RuntimeError("Verified scoped target match; halt before logging candidate material")
    return {"candidate_sha256": identifier, "provenance": candidate["provenance"], "addresses": addresses, "valid_scalar": bool(addresses), "target_match": False}


def run():
    plan, candidates = load_plan()
    path = OUTPUT / "direct-source-keys-checks.jsonl"
    started = perf_counter()
    invalid = 0
    with path.open("x") as output:
        for identifier, candidate in sorted(candidates.items()):
            entry = evaluate(identifier, candidate)
            invalid += not entry["valid_scalar"]
            output.write(json.dumps(entry, sort_keys=True) + "\n")
    report = {"id": plan["id"], "scalar_checks": len(candidates), "invalid_scalars": invalid, "target_matches": 0, "elapsed_seconds": round(perf_counter() - started, 3), "ledger_sha256": fingerprint(path.read_bytes()), "status": "REJECTED", "result": "No exact32-byte/hex64 material from the audited source-password ledgers derives either scoped target in compressed or uncompressed P2PKH form. This rejects only the stated direct-key family."}
    write_once_json(OUTPUT / "direct-source-keys-results.json", report)
    print(json.dumps(report, indent=2))
    return report


def audit():
    plan, candidates = load_plan()
    path = OUTPUT / "direct-source-keys-checks.jsonl"
    with path.open() as source:
        for identifier, candidate in sorted(candidates.items()):
            if json.loads(source.readline()) != evaluate(identifier, candidate):
                raise ValueError("Recorded direct-key provenance/address gate does not reproduce")
        if source.readline():
            raise ValueError("Unexpected trailing direct-key records")
    summary = json.loads((OUTPUT / "direct-source-keys-results.json").read_text())
    if summary["scalar_checks"] != len(candidates) or summary["ledger_sha256"] != fingerprint(path.read_bytes()):
        raise ValueError("Direct-key summary changed")
    report = {"id": "C05-DIRECT-SOURCE-KEYS-AUDIT", "scalar_checks": len(candidates), "ledger_sha256": summary["ledger_sha256"], "status": "CONFIRMED", "meaning": "Every source-derived scalar fingerprint, representation provenance, address pair and target gate reproduces. Independent EC verification is required on a positive gate, not performed for every negative."}
    write_once_json(OUTPUT / "direct-source-keys-audit.json", report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Source-derived direct Bitcoin scalar gap check, never a private-key range search")
    parser.add_argument("command", choices=("plan", "run", "audit"))
    arguments = parser.parse_args()
    {"plan": make_plan, "run": run, "audit": audit}[arguments.command]()
