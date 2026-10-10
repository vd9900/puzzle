#!/usr/bin/env python3
import argparse
import base64
import json
import re
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.audit_binary_key_pairs import key_pairs
from tools.candidate_identity import POLICY, previously_tested, tagged_identity
from tools.gsmg import ARTIFACTS, SECONDARY_ADDRESS, TARGET_ADDRESS, candidate_addresses, evp_bytes_to_key, parse_salted
from tools.plan_missing_cell import derive_candidates
from tools.research_common import fingerprint, score_plaintext, source_record, structural_checks, write_once_json
from tools.verify_btc import verify_candidate


OUTPUT = ARTIFACTS / "cycle06"
FROZEN_PLAN = ARTIFACTS / "cycle05/next-missing-cell-plan.json"
PREVIOUS_AUDIT = ARTIFACTS / "cycle05/cumulative-aes-audit.json"


def family_paths(family):
    if family == "missing-cell":
        return OUTPUT, FROZEN_PLAN, PREVIOUS_AUDIT, "missing-cell", "C06-MISSING-CELL"
    if family == "numeric-routing":
        return ARTIFACTS / "cycle07", ARTIFACTS / "cycle07/numeric-routing-frozen-plan.json", ARTIFACTS / "cycle06/cumulative-aes-audit.json", "numeric-routing", "C07-NUMERIC-ROUTING"
    if family == "residual-bifid":
        return ARTIFACTS / "cycle08", ARTIFACTS / "cycle08/residual-bifid-frozen-plan.json", ARTIFACTS / "cycle07/cumulative-aes-audit.json", "residual-bifid", "C08-RESIDUAL-BIFID"
    if family == "post-bifid-routing":
        return ARTIFACTS / "cycle09", ARTIFACTS / "cycle08/next-post-bifid-routing-plan.json", ARTIFACTS / "cycle08/cumulative-aes-audit.json", "post-bifid-routing", "C09-POST-BIFID-ROUTING"
    if family == "spiral-ring-sums":
        return ARTIFACTS / "cycle09", ARTIFACTS / "cycle09/spiral-ring-sums-frozen-plan.json", ARTIFACTS / "cycle09/post-bifid-cumulative-aes-audit.json", "spiral-ring-sums", "C09-SPIRAL-RING-SUMS"
    if family == "masked-missing-cell":
        return ARTIFACTS / "cycle10", ARTIFACTS / "cycle09/next-masked-missing-cell-plan.json", ARTIFACTS / "cycle09/cumulative-aes-audit.json", "masked-missing-cell", "C10-MASKED-MISSING-CELL"
    raise ValueError("Unknown frozen experiment family")


def load_candidates(family="missing-cell"):
    destination, frozen_path, previous_path, stem, identifier = family_paths(family)
    plan = json.loads(frozen_path.read_text())
    for source in plan["source_evidence"]:
        if fingerprint((ARTIFACTS.parents[1] / source["path"]).read_bytes()) != source["sha256"]:
            raise ValueError("Frozen construction source fingerprint differs")
    if family in ("numeric-routing", "residual-bifid", "post-bifid-routing", "spiral-ring-sums", "masked-missing-cell"):
        if family == "numeric-routing":
            from tools.plan_numeric_routing import derive_candidates as routing_candidates
        elif family == "residual-bifid":
            from tools.plan_residual_bifid import derive_candidates as routing_candidates
        elif family == "post-bifid-routing":
            from tools.plan_post_bifid_routing import derive_candidates as routing_candidates
        elif family == "spiral-ring-sums":
            from tools.plan_spiral_ring_sums import derive_candidates as routing_candidates
        else:
            from tools.plan_masked_missing_cell import derive_candidates as routing_candidates

        forms, candidates = routing_candidates()
        if forms != plan["forms"] or sorted(candidates) != plan["candidate_fingerprints"]:
            raise ValueError("Source-derived numeric routes differ from the frozen plan")
    else:
        matrices, lists, forms, candidates = derive_candidates()
        if matrices != plan["matrices"] or forms != plan["forms"] or candidates != plan["passwords"]:
            raise ValueError("Source-derived construction differs from the frozen plan")
    if fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))) != plan["candidate_set_sha256"]:
        raise ValueError("Frozen candidate set fingerprint differs")
    if family == "masked-missing-cell":
        if plan.get("candidate_identifier_policy") != POLICY or any(identifier != tagged_identity(bytes.fromhex(candidate["password_hex"])) for identifier, candidate in candidates.items()):
            raise ValueError("The frozen masked-matrix candidate identity policy differs")
    expected_passwords = len(plan["new_candidate_fingerprints"]) if family in ("post-bifid-routing", "masked-missing-cell") else len(candidates)
    if plan["search_space"]["kdf_digests"] != ["md5", "sha256"] or plan["search_space"]["planned_aes_trials"] != expected_passwords * 6:
        raise ValueError("Frozen cipher-search parameters differ from the supported experiment")
    previous = json.loads(previous_path.read_text())
    old_identifiers = set()
    for ledger in previous["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("Historical audited ledger changed")
        with path.open() as source:
            old_identifiers.update(json.loads(line)[ledger.get("candidate_identifier_field", "password_sha256")] for line in source)
    if family in ("residual-bifid", "post-bifid-routing", "spiral-ring-sums", "masked-missing-cell"):
        from tools.baseline_coverage import baseline_passwords

        old_identifiers.update(fingerprint(password) for password in baseline_passwords())
    fresh = {identifier: candidate for identifier, candidate in candidates.items() if not previously_tested(bytes.fromhex(candidate["password_hex"]), old_identifiers)}
    if family in ("post-bifid-routing", "masked-missing-cell") and sorted(fresh) != plan["new_candidate_fingerprints"]:
        raise ValueError("The frozen source-derived untested subset differs")
    return plan, fresh, len(candidates) - len(fresh)


def make_plan(family="missing-cell"):
    destination, frozen_path, previous_path, stem, identifier = family_paths(family)
    original, candidates, duplicates = load_candidates(family)
    report = {"id": identifier, "status": "UNTESTED", "source_evidence": [source_record(frozen_path), source_record(previous_path)], "hypothesis": original["hypothesis"], "invariant": original["invariant"], "justification": original["justification"], "search_space": original["search_space"] | {"previously_tested_passwords_skipped": duplicates, "new_unique_passwords": len(candidates), "new_aes_trials": len(candidates) * 6}, "candidate_fingerprints": sorted(candidates), "estimated_crypto_seconds": round(len(candidates) * 6 / 50000, 4), "estimated_raw_key_slots_upper_bound": len(candidates) * 4 * 32, "raw_key_slots_estimate_note": "Worst case if all four small-blob/KDF trials pass padding; actual qualifying slots measured after decryption", "verification_policy": "Only local Boolean target results; a positive target gate is independently verified before any result is saved. No key/password/IV/plaintext bytes or candidate addresses are written by this runner.", "limits": "Exact frozen source-derived family only; no network, production transactions, repeated prior candidate trials, new cipher families or free permutations"}
    if "candidate_identifier_policy" in original:
        report["candidate_identifier_policy"] = original["candidate_identifier_policy"]
    write_once_json(destination / (stem + "-plan.json"), report)
    print(json.dumps({name: value for name, value in report.items() if name != "candidate_fingerprints"}, indent=2))
    return report


def scalar_result(candidate):
    try:
        addresses = candidate_addresses(candidate)
    except ValueError:
        return {"valid_scalar": False, "TARGET_MATCH": False, "independently_verified": False}
    match = TARGET_ADDRESS in addresses.values() or SECONDARY_ADDRESS in addresses.values()
    if match:
        independent = verify_candidate(candidate)
        if not independent["main_target_match"] and not independent["secondary_target_match"]:
            raise ValueError("Independent Boolean target verification disagrees")
    return {"valid_scalar": True, "TARGET_MATCH": match, "independently_verified": match}


def plaintext_result(plaintext, target):
    structures, candidates = structural_checks(plaintext)
    if len(plaintext) == 32:
        candidates.append(plaintext)
    if re.fullmatch(rb"[0-9a-fA-F]{64}", plaintext.strip()):
        candidates.append(bytes.fromhex(plaintext.strip().decode("ascii")))
    direct = [{"candidate_fingerprint": fingerprint(candidate), **scalar_result(candidate)} for candidate in sorted(set(candidates))]
    pairs = []
    if target in ("phase32-inner", "salphaseion-small"):
        for offset, pair in key_pairs(plaintext):
            for slot, candidate in enumerate(pair):
                pairs.append({"start_offset_zero_based": offset, "key_slot_zero_based": slot, "candidate_fingerprint": fingerprint(candidate), **scalar_result(candidate)})
    nested = None
    if "openssl_salted" in structures:
        nested = len(plaintext) > 16 and (len(plaintext) - 16) % 16 == 0
    return {"plaintext_fingerprint": fingerprint(plaintext), "score": score_plaintext(plaintext), "structural_validity": structures, "nested_openssl_container_shape_valid": nested, "direct_key_checks": direct, "bounded_raw_key_checks": pairs, "TARGET_MATCH": any(entry["TARGET_MATCH"] for entry in direct + pairs), "downstream_limit": "Magic/JSON/WIF/container shape alone is not a verified next stage; no arbitrary subsequent transformations"}


def evaluate(identifier, candidate, plan_digest, blobs):
    password = bytes.fromhex(candidate["password_hex"])
    record = {"password_fingerprint": identifier, "provenance": candidate["provenance"], "execution_plan_fingerprint": plan_digest, "evaluations": []}
    for target, (salt, ciphertext) in blobs.items():
        for digest in ("md5", "sha256"):
            key, initialization_vector = evp_bytes_to_key(password, salt, digest)
            evaluation = {"target": target, "cipher": "AES-256-CBC", "kdf": "EVP_BytesToKey", "digest": digest, "iterations": 1, "salt": salt.hex(), "ciphertext_fingerprint": fingerprint(ciphertext), "key_fingerprint": fingerprint(key), "iv_fingerprint": fingerprint(initialization_vector), "padding_valid": False, "plaintext_result": None, "TARGET_MATCH": False}
            try:
                plaintext = unpad(AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext), 16)
            except ValueError:
                record["evaluations"].append(evaluation)
                continue
            result = plaintext_result(plaintext, target)
            evaluation.update({"padding_valid": True, "plaintext_result": result, "TARGET_MATCH": result["TARGET_MATCH"]})
            record["evaluations"].append(evaluation)
    return record


def load_execution(family="missing-cell"):
    destination, frozen_path, previous_path, stem, identifier = family_paths(family)
    original, candidates, duplicates = load_candidates(family)
    path = destination / (stem + "-plan.json")
    plan = json.loads(path.read_text())
    for source in plan["source_evidence"]:
        if fingerprint((ARTIFACTS.parents[1] / source["path"]).read_bytes()) != source["sha256"]:
            raise ValueError("Execution-plan source fingerprint differs")
    if plan["candidate_fingerprints"] != sorted(candidates) or plan["search_space"]["previously_tested_passwords_skipped"] != duplicates or plan["search_space"]["new_aes_trials"] != len(candidates) * 6:
        raise ValueError("Execution plan no longer matches its exact untested subset")
    if original.get("candidate_identifier_policy") != plan.get("candidate_identifier_policy"):
        raise ValueError("Execution plan changed the candidate identity policy")
    blobs = {target: parse_salted((ARTIFACTS / (target + ".b64")).read_text()) for target in original["search_space"]["targets"]}
    return plan, candidates, fingerprint(path.read_bytes()), blobs


def summarize(records):
    evaluations = [evaluation for record in records for evaluation in record["evaluations"]]
    hits = [evaluation["plaintext_result"] for evaluation in evaluations if evaluation["padding_valid"]]
    return {"unique_passwords": len(records), "aes_trials": len(evaluations), "padding_hits": len(hits), "structure_hits": sum(bool(hit["structural_validity"]) for hit in hits), "qualifying_small_blob_hits": sum(evaluation["padding_valid"] and evaluation["target"] in ("phase32-inner", "salphaseion-small") for evaluation in evaluations), "bounded_raw_key_slots": sum(len(hit["bounded_raw_key_checks"]) for hit in hits), "max_hit_printable_ratio": max((hit["score"]["printable_ratio"] for hit in hits), default=0), "TARGET_MATCH": any(evaluation["TARGET_MATCH"] for evaluation in evaluations)}


def run(family="missing-cell"):
    destination, frozen_path, previous_path, stem, identifier = family_paths(family)
    plan, candidates, plan_digest, blobs = load_execution(family)
    path = destination / (stem + "-aes.jsonl")
    started = perf_counter()
    records = []
    with path.open("x") as output:
        for identifier, candidate in sorted(candidates.items()):
            record = evaluate(identifier, candidate, plan_digest, blobs)
            output.write(json.dumps(record, sort_keys=True) + "\n")
            records.append(record)
    counts = summarize(records)
    if counts["aes_trials"] != plan["search_space"]["new_aes_trials"]:
        raise ValueError("Recorded trial count differs from the frozen untested subset")
    report = {"id": plan["id"], **counts, "elapsed_seconds": round(perf_counter() - started, 3), "ledger_sha256": fingerprint(path.read_bytes()), "status": "PROMISING" if counts["TARGET_MATCH"] else "INCONCLUSIVE", "result": "Exact Boolean target match independently verified; no sensitive material disclosed" if counts["TARGET_MATCH"] else "The frozen source-derived construction has no exact scoped target; padding and structure filters are not a creator-intent proof", "secret_logging": "No password, AES key/IV, scalar, plaintext byte sequence or candidate address is stored; all source material regenerates locally"}
    write_once_json(destination / (stem + "-results.json"), report)
    print(json.dumps(report, indent=2))
    return report


def audit(family="missing-cell"):
    destination, frozen_path, previous_path, stem, identifier = family_paths(family)
    plan, candidates, plan_digest, blobs = load_execution(family)
    path = destination / (stem + "-aes.jsonl")
    records = []
    with path.open() as source:
        for identifier, candidate in sorted(candidates.items()):
            expected = evaluate(identifier, candidate, plan_digest, blobs)
            if json.loads(source.readline()) != expected:
                raise ValueError("Secret-safe trial provenance, crypto fingerprints, padding, scores or Boolean gates do not reproduce")
            records.append(expected)
        if source.readline():
            raise ValueError("Unexpected trailing secret-safe trial records")
    summary = json.loads((destination / (stem + "-results.json")).read_text())
    counts = summarize(records)
    if any(summary[name] != value for name, value in counts.items()) or summary["ledger_sha256"] != fingerprint(path.read_bytes()):
        raise ValueError("Secret-safe ledger summary differs")
    report = {"id": plan["id"] + "-AUDIT", **counts, "ledger_sha256": summary["ledger_sha256"], "status": "CONFIRMED", "meaning": "Every exact candidate/transform, AES/KDF fingerprint, padding result, score, structure filter, raw-key slot and Boolean target gate reproduces without storing secret bytes"}
    write_once_json(destination / (stem + "-audit.json"), report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline frozen missing-cell experiment with fingerprint-only secret-safe results")
    parser.add_argument("command", choices=("plan", "run", "audit"))
    parser.add_argument("--family", choices=("missing-cell", "numeric-routing", "residual-bifid", "post-bifid-routing", "spiral-ring-sums", "masked-missing-cell"), default="missing-cell")
    arguments = parser.parse_args()
    {"plan": make_plan, "run": run, "audit": audit}[arguments.command](arguments.family)
