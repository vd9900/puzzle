#!/usr/bin/env python3
import base64
import json
from hashlib import sha256
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.gsmg import ARTIFACTS, parse_salted, evp_bytes_to_key
from tools.plan_zeroed_residual import planned_forms
from tools.research_common import CYCLE, fingerprint, score_plaintext, target_checks, write_once_json


OUTPUT = ARTIFACTS / "cycle03"


def load_frozen_plan(family="zeroed"):
    plan_paths = {"zeroed": CYCLE / "next-zeroed-residual-plan.json", "decimal": OUTPUT / "next-decimal-residual-plan.json", "ranked": OUTPUT / "next-ranked-alphabet-plan.json", "bifid": ARTIFACTS / "cycle04/bifid-material-plan.json", "composition": ARTIFACTS / "cycle04/hash-composition-plan.json", "literal": ARTIFACTS / "cycle04/next-literal-sumlist-plan.json", "rails": ARTIFACTS / "cycle05/bifid-rails-plan.json"}
    path = plan_paths[family]
    plan = json.loads(path.read_text())
    if family == "rails":
        from tools.plan_bifid_rails import derive_candidates

        expected_forms, derived = derive_candidates()
    elif family == "literal":
        from tools.plan_literal_sumlist import derive_candidates

        lists, expected_forms, derived = derive_candidates()
    elif family == "composition":
        from tools.plan_hash_composition import derive_candidates

        hints, answers, expected_forms, derived = derive_candidates()
    elif family == "bifid":
        from tools.plan_bifid_material import derive_candidates

        expected_forms, derived = derive_candidates()
    elif family == "ranked":
        from tools.plan_ranked_alphabet import derive_candidates

        alphabets, expected_forms, derived = derive_candidates()
        if alphabets != plan["alphabets"]:
            raise ValueError("Ranked alphabets differ from the frozen image-sum plan")
    elif family == "decimal":
        from tools.plan_decimal_residual import forms, passwords_from_forms

        expected_forms = list(forms())
        derived = passwords_from_forms(expected_forms)
    else:
        expected_forms = list(planned_forms())
        derived = {}
        for entry in expected_forms:
            if entry["decoded"] is None:
                continue
            payload = entry["decoded"].encode("ascii")
            for representation, password in (("raw", payload), ("sha256-lowerhex", sha256(payload).hexdigest().encode()), ("sha256-raw", sha256(payload).digest())):
                candidate = derived.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                candidate["provenance"].append({**entry["parameters"], "representation": representation})
    if plan["forms"] != expected_forms:
        raise ValueError("Exact forms differ from the frozen plan")
    if derived != plan["passwords"]:
        raise ValueError("Planned passwords no longer derive from the exact source forms")
    passwords = sorted(bytes.fromhex(candidate["password_hex"]) for candidate in plan["passwords"].values())
    if fingerprint(b"\x00".join(passwords)) != plan["candidate_set_sha256"]:
        raise ValueError("Candidate-set fingerprint differs from the frozen plan")
    for identifier, candidate in plan["passwords"].items():
        if identifier != fingerprint(bytes.fromhex(candidate["password_hex"])):
            raise ValueError("Planned password identifier is invalid")
    return path, plan


def decoded_forms(plan):
    if all("decoded" in entry for entry in plan["forms"]):
        return [{"parameters": entry["parameters"], "decoded": entry["decoded"], "error": entry["error"], "score": None if entry["decoded"] is None else score_plaintext(entry["decoded"].encode())} for entry in plan["forms"]]
    return plan["forms"]


def result_summary(family, stem, plan_path, plan, path, trials, hits, elapsed_seconds):
    meaning = {"zeroed": "Literal single-symbol zero replacement followed by the known-prefix checkerboard", "decimal": "Source-supported radix10 integer/byte/hex representations of unchanged residual/faed", "ranked": "Stable-ranked original-image axis sums as a checkerboard alphabet", "bifid": "Exact Bifid output/suffix/parity rails and bounded passphrase representations", "composition": "First-hint and source-answer sha256 digest composition", "literal": "Literal image-axis sums and exact words before choice as passphrase material", "rails": "Exact source-keyed Bifid coordinate rails with strict binary/quinary byte interpretations"}[family]
    identifier = ("C05-" if family in ("literal", "rails") else "C04-" if family in ("ranked", "bifid", "composition") else "C03-") + stem.upper()
    return {"id": identifier, "plan": str(plan_path.relative_to(ARTIFACTS.parents[1])), "candidate_set_sha256": plan["candidate_set_sha256"], "unique_passwords": len(plan["passwords"]), "aes_trials": trials, "padding_hits": len(hits), "structure_hits": sum(bool(hit["structural_validity"]) for hit in hits), "target_matches": 0, "max_hit_printable_ratio": max((hit["score"]["printable_ratio"] for hit in hits), default=0), "elapsed_seconds": elapsed_seconds, "ledger_sha256": fingerprint(path.read_bytes()), "status": "INCONCLUSIVE", "result": meaning + " supplies no recognized structure or scoped target match; finite negative only"}


def run(family="zeroed"):
    plan_path, plan = load_frozen_plan(family)
    plan_digest = fingerprint(plan_path.read_bytes())
    stem = {"zeroed": "zeroed-residual", "decimal": "decimal-residual", "ranked": "ranked-alphabet", "bifid": "bifid-material", "composition": "hash-composition", "literal": "literal-sumlist", "rails": "bifid-rails"}[family]
    destination = ARTIFACTS / "cycle05" if family in ("literal", "rails") else ARTIFACTS / "cycle04" if family in ("ranked", "bifid", "composition") else OUTPUT
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / (stem + "-aes.jsonl")
    if path.exists():
        raise ValueError("Existing ledger is preserved; use the audit command instead")
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in plan["search_space"]["targets"]}
    hits = []
    trials = 0
    started = perf_counter()
    with path.open("x") as output:
        for identifier, candidate in sorted(plan["passwords"].items()):
            password = bytes.fromhex(candidate["password_hex"])
            entry = {"password_sha256": identifier, "password_base64": base64.b64encode(password).decode(), "source": plan.get("source", plan.get("source_evidence")), "plan_sha256": plan_digest, "provenance": candidate["provenance"], "evaluations": []}
            for target, (salt, ciphertext) in blobs.items():
                for digest in plan["search_space"]["kdf_digests"]:
                    trials += 1
                    key, initialization_vector = evp_bytes_to_key(password, salt, digest)
                    evaluation = {"target": target, "ciphertext_sha256": fingerprint(ciphertext), "cipher": "AES-256-CBC", "kdf": "EVP_BytesToKey", "digest": digest, "iterations": 1, "salt": salt.hex(), "key": key.hex(), "iv": initialization_vector.hex(), "padding_valid": False, "plaintext": None, "score": None, "structural_validity": None, "downstream_validity": None}
                    try:
                        plaintext = unpad(AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext), 16)
                    except ValueError:
                        entry["evaluations"].append(evaluation)
                        continue
                    validity = target_checks(plaintext)
                    if validity["target_match"]:
                        raise RuntimeError("Scoped target match; halt before public plaintext logging")
                    evaluation.update({"padding_valid": True, "plaintext": base64.b64encode(plaintext).decode(), "score": score_plaintext(plaintext), "structural_validity": validity["structures"], "downstream_validity": validity})
                    hits.append(evaluation)
                    entry["evaluations"].append(evaluation)
            output.write(json.dumps(entry, sort_keys=True) + "\n")
    write_once_json(destination / (stem + "-decodes.json"), decoded_forms(plan))
    report = result_summary(family, stem, plan_path, plan, path, trials, hits, round(perf_counter() - started, 3))
    if trials != plan["search_space"]["planned_aes_trials"]:
        raise ValueError("Completed trial count differs from the frozen plan")
    write_once_json(destination / (stem + "-results.json"), report)
    print(json.dumps(report, indent=2))
    return report


def audit(family="zeroed", recover_summary=False):
    plan_path, plan = load_frozen_plan(family)
    plan_digest = fingerprint(plan_path.read_bytes())
    stem = {"zeroed": "zeroed-residual", "decimal": "decimal-residual", "ranked": "ranked-alphabet", "bifid": "bifid-material", "composition": "hash-composition", "literal": "literal-sumlist", "rails": "bifid-rails"}[family]
    destination = ARTIFACTS / "cycle05" if family in ("literal", "rails") else ARTIFACTS / "cycle04" if family in ("ranked", "bifid", "composition") else OUTPUT
    path = destination / (stem + "-aes.jsonl")
    hits = 0
    hit_records = []
    trials = 0
    identifiers = set()
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in plan["search_space"]["targets"]}
    expected_pairs = {(target, digest) for target in blobs for digest in plan["search_space"]["kdf_digests"]}
    with path.open() as source:
        for line in source:
            entry = json.loads(line)
            identifier = entry["password_sha256"]
            if identifier in identifiers or identifier not in plan["passwords"]:
                raise ValueError("Unplanned or duplicated candidate")
            identifiers.add(identifier)
            password = base64.b64decode(entry["password_base64"], validate=True)
            expected = plan["passwords"][identifier]
            if password.hex() != expected["password_hex"] or entry["provenance"] != expected["provenance"] or entry["plan_sha256"] != plan_digest:
                raise ValueError("Candidate/provenance no longer matches its frozen plan")
            if len(entry["evaluations"]) != 6 or {(evaluation["target"], evaluation["digest"]) for evaluation in entry["evaluations"]} != expected_pairs:
                raise ValueError("Missing or duplicated target/digest pair")
            for evaluation in entry["evaluations"]:
                trials += 1
                if evaluation["cipher"] != "AES-256-CBC" or evaluation["kdf"] != "EVP_BytesToKey" or evaluation["iterations"] != 1:
                    raise ValueError("Recorded cipher/KDF metadata differs from the planned implementation")
                salt, ciphertext = blobs[evaluation["target"]]
                key, initialization_vector = evp_bytes_to_key(password, salt, evaluation["digest"])
                if evaluation["key"] != key.hex() or evaluation["iv"] != initialization_vector.hex() or evaluation["salt"] != salt.hex() or evaluation["ciphertext_sha256"] != fingerprint(ciphertext):
                    raise ValueError("Recorded cipher parameters do not reproduce")
                try:
                    plaintext = unpad(AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext), 16)
                except ValueError:
                    if evaluation["padding_valid"]:
                        raise ValueError("Invalid reported padding hit")
                    continue
                hits += 1
                validity = target_checks(plaintext)
                if validity["target_match"]:
                    raise RuntimeError("Scoped target match; halt before public summary writing")
                if not evaluation["padding_valid"] or base64.b64decode(evaluation["plaintext"], validate=True) != plaintext or evaluation["score"] != score_plaintext(plaintext) or evaluation["structural_validity"] != validity["structures"] or evaluation["downstream_validity"] != validity:
                    raise ValueError("Plaintext/score/gate does not reproduce")
                hit_records.append(evaluation)
    if identifiers != set(plan["passwords"]) or trials != plan["search_space"]["planned_aes_trials"]:
        raise ValueError("Ledger is incomplete or differs from the frozen candidate set")
    summary_path = destination / (stem + "-results.json")
    if recover_summary:
        if summary_path.exists():
            raise ValueError("An existing summary is preserved; use audit without recovery")
        recovered = result_summary(family, stem, plan_path, plan, path, trials, hit_records, None)
        recovered["recovery"] = {"method": "Recompute every preserved trial and verify complete frozen-plan coverage before creating the missing summary", "elapsed_seconds": "Original execution runtime was not recorded; unknown, not inferred from audit time", "ledger_overwritten": False}
        write_once_json(destination / (stem + "-decodes.json"), decoded_forms(plan))
        write_once_json(summary_path, recovered)
    summary = json.loads(summary_path.read_text())
    if identifiers != set(plan["passwords"]) or summary["aes_trials"] != trials or summary["padding_hits"] != hits or summary["ledger_sha256"] != fingerprint(path.read_bytes()):
        raise ValueError("Summary or ledger differs from the exact planned experiment")
    identifier = ("C05-" if family in ("literal", "rails") else "C04-" if family in ("ranked", "bifid", "composition") else "C03-") + stem.upper()
    report = {"id": identifier + "-AUDIT", "unique_passwords": len(identifiers), "aes_trials": trials, "padding_hits": hits, "ledger_sha256": fingerprint(path.read_bytes()), "status": "CONFIRMED", "meaning": "Every planned candidate, provenance, six distinct target/KDF pairs, KEY/IV, padding outcome, plaintext and score/gate reproduced; this does not solve the puzzle"}
    write_once_json(destination / (stem + "-audit.json"), report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Execute or audit the already frozen zeroed-residual plan")
    parser.add_argument("command", choices=("run", "audit"))
    parser.add_argument("--family", choices=("zeroed", "decimal", "ranked", "bifid", "composition", "literal", "rails"), default="zeroed")
    parser.add_argument("--recover-summary", action="store_true", help="Audit complete preserved trials before creating an absent summary; never overwrite an existing summary")
    arguments = parser.parse_args()
    if arguments.recover_summary and arguments.command != "audit":
        parser.error("Summary recovery requires the audit command")
    run(arguments.family) if arguments.command == "run" else audit(arguments.family, arguments.recover_summary)
