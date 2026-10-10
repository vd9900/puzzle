#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import re
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.gsmg import ARTIFACTS, SOURCES, PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE, parse_salted, textareas, evp_bytes_to_key
from tools.analyze_salphaseion import split_segments
from tools.research_common import CYCLE, fingerprint, score_plaintext, source_record, target_checks, write_once_json


def material_sources():
    materials = []
    for name in ("phase2", "phase3", "phase32", "phase32-beaufort", "phase32-checkerboard"):
        path = ARTIFACTS / f"{name}.txt"
        payload = path.read_bytes()
        materials.append((name, payload, source_record(path), "exact artifact bytes"))
    phase32 = (ARTIFACTS / "phase32.txt").read_bytes()
    chunks = phase32.split(b"\r\n\r\n")
    for index, chunk in enumerate(chunks[:-1]):
        materials.append((f"phase32-section-{index}", chunk, source_record(ARTIFACTS / "phase32.txt", f"CRLF paragraph {index}"), "paragraph boundary extraction"))
    speech = (ARTIFACTS / "phase32-beaufort.txt").read_text().strip()
    anchor = "yourlifeisthesumofaremainderofanunbalancedequation"
    for name, text in (("speech-first-sentence-anchor", anchor), ("speech-pre-choice", speech.split("afterwhichyouwillberequiredtoselect", 1)[0]), ("speech-before-choice-last-words", "reinsertingtheprimebasics"), ("speech-post-choice", speech.split("afterwhichyouwillberequiredtoselect", 1)[1]), ("speech-1141-suffix", speech[1141:])):
        materials.append((name, text.encode(), source_record(ARTIFACTS / "phase32-beaufort.txt"), "explicit speech wording/1141 clue boundary"))
    for name, text in (("phase3-preimage", PHASE3_PREIMAGE), ("phase32-preimage", PHASE32_PREIMAGE), ("image-route-preimage", SALPHASEION_PREIMAGE), ("audio-clue", "HASHTHETEXT"), ("beaufort-key", "THEMATRIXHASYOU"), ("checkerboard-alphabet", "fubcdora/lethingkymvpszjqwx.")):
        materials.append((name, text.encode(), {"path": "tools/gsmg.py", "locator": name}, "baseline verified preimage/clue"))
    salphaseion = textareas((SOURCES / "salphaseion.html").read_text())[0]
    materials.append(("salphaseion-entire-textarea", salphaseion.encode(), source_record(SOURCES / "salphaseion.html", "textarea:0"), "exact textarea"))
    for name, text in split_segments().items():
        materials.append((f"salphaseion-{name}", text.encode(), source_record(SOURCES / "salphaseion.html", name), "structurally bounded segment"))
    for name, text in (("matrixsumlist", "matrixsumlist"), ("enter", "enter"), ("lastwordsbeforearchichoice", "lastwordsbeforearchichoice"), ("thispassword", "thispassword"), ("token-concat", "matrixsumlistenterlastwordsbeforearchichoicethispassword"), ("token-concat-repeat", "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"), ("half-and-better-half", "halfandbetterhalf")):
        materials.append((name, text.encode(), source_record(SOURCES / "salphaseion.html") if name != "half-and-better-half" else source_record(ARTIFACTS / "phase32-checkerboard.txt"), "literal clue tokens, not established passphrase"))
    return materials


def text_transforms(payload):
    variants = {"exact": payload, "strip-terminal-whitespace": payload.strip(), "lowercase": payload.lower(), "uppercase": payload.upper(), "reverse-bytes": payload[::-1]}
    variants["lf-normalization"] = payload.replace(b"\r\n", b"\n")
    variants["collapse-whitespace"] = b" ".join(payload.split())
    variants["remove-whitespace"] = b"".join(payload.split())
    variants["ascii-alphanumeric-only"] = bytes(byte for byte in payload if 48 <= byte <= 57 or 65 <= byte <= 90 or 97 <= byte <= 122)
    variants["ascii-letters-only"] = bytes(byte for byte in payload if 65 <= byte <= 90 or 97 <= byte <= 122)
    variants["reverse-whitespace-words"] = b" ".join(reversed(payload.split()))
    variants["remove-whitespace-reverse"] = b"".join(payload.split())[::-1]
    variants["letters-only-lowercase"] = variants["ascii-letters-only"].lower()
    variants["letters-only-uppercase"] = variants["ascii-letters-only"].upper()
    variants["letters-only-reversed"] = variants["ascii-letters-only"][::-1]
    return variants


def derive_passwords():
    derived = {}
    hash_algorithms = ("md5", "sha1", "sha224", "sha256", "sha384", "sha512")
    for source_name, payload, evidence, extraction in material_sources():
        for transform, material in text_transforms(payload).items():
            if not material:
                continue
            representations = {"raw": material, "bytes-hex-lowercase": material.hex().encode(), "bytes-base64": base64.b64encode(material)}
            for algorithm in hash_algorithms:
                digest = hashlib.new(algorithm, material).digest()
                representations[f"{algorithm}-digest-raw"] = digest
                representations[f"{algorithm}-digest-hex-lowercase"] = digest.hex().encode()
                representations[f"{algorithm}-digest-hex-uppercase"] = digest.hex().upper().encode()
                representations[f"{algorithm}-digest-base64"] = base64.b64encode(digest)
            for representation, password in representations.items():
                identifier = fingerprint(password)
                provenance = {"source": evidence, "source_name": source_name, "extraction": extraction, "transformation": transform, "representation": representation}
                if identifier not in derived:
                    derived[identifier] = {"password": password, "provenance": []}
                derived[identifier]["provenance"].append(provenance)
    return derived


def estimate_space():
    candidates = derive_passwords()
    trials = len(candidates) * 2 * 3
    salt, ciphertext = parse_salted((ARTIFACTS / "phase32-inner.b64").read_text())
    sample = list(candidates.values())[:256]
    started = perf_counter()
    for candidate in sample:
        key, initialization_vector = evp_bytes_to_key(candidate["password"], salt, "sha256")
        AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext)
    elapsed = perf_counter() - started
    throughput = len(sample) / max(elapsed, 1e-9)
    report = {"experiment": "C02-INNER-TEXT", "material_sources": len(material_sources()), "unique_passwords": len(candidates), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "trials": trials, "benchmark_trials": len(sample), "benchmark_trials_per_second": round(throughput, 1), "estimated_crypto_seconds": round(trials / throughput, 2), "scope": "Only existing exact artifacts, explicit wording boundaries, case/whitespace/reversal/hash/representation transforms. No arbitrary dictionary or cipher/keyspace brute force.", "candidate_set_sha256": fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in candidates.values())))}
    write_once_json(CYCLE / "inner-search-plan.json", report)
    print(json.dumps(report, indent=2))
    return report


def run_search():
    candidates = derive_passwords()
    plan = json.loads((CYCLE / "inner-search-plan.json").read_text())
    if len(candidates) != plan["unique_passwords"]:
        raise ValueError("Candidate set changed since the search-space calculation")
    target_blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in plan["targets"]}
    identifier = "C02-INNER-TEXT-" + plan["candidate_set_sha256"][:16]
    ledger = CYCLE / f"{identifier}.jsonl"
    completed = set()
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            completed.add(json.loads(line)["password_sha256"])
    padding_hits = []
    tested = 0
    started = perf_counter()
    with ledger.open("a") as output:
        for password_hash, candidate in sorted(candidates.items()):
            if password_hash in completed:
                continue
            password = candidate["password"]
            record = {"id": identifier + ":" + password_hash, "password_sha256": password_hash, "password_base64": base64.b64encode(password).decode(), "password_bytes": len(password), "provenance": candidate["provenance"], "cipher_evaluations": []}
            for target, (salt, ciphertext) in target_blobs.items():
                for digest in plan["kdf_digests"]:
                    key, initialization_vector = evp_bytes_to_key(password, salt, digest)
                    padded = AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext)
                    evaluation = {"target": target, "cipher": "AES-256-CBC", "kdf": "EVP_BytesToKey", "kdf_digest": digest, "iterations": 1, "salt_hex": salt.hex(), "derived_key_hex": key.hex(), "iv_hex": initialization_vector.hex(), "padding": "PKCS#7", "padding_valid": False, "plaintext": None, "structural_validity": None, "downstream_validity": None}
                    tested += 1
                    try:
                        plaintext = unpad(padded, 16)
                    except ValueError:
                        record["cipher_evaluations"].append(evaluation)
                        continue
                    scores = score_plaintext(plaintext)
                    validity = target_checks(plaintext)
                    if validity["target_match"]:
                        raise RuntimeError("Target-matching candidate detected: halt public logging and preserve secret locally before further verification")
                    name = f"inner-hit-{target}-{digest}-{password_hash[:16]}.bin"
                    (CYCLE / name).write_bytes(plaintext)
                    evaluation.update({"padding_valid": True, "plaintext": {"artifact": name, "base64": base64.b64encode(plaintext).decode(), "sha256": fingerprint(plaintext)}, "score": scores, "structural_validity": validity["structures"], "downstream_validity": validity, "status": "INCONCLUSIVE"})
                    padding_hits.append({"password_sha256": password_hash, "source": candidate["provenance"][0], **evaluation})
                    record["cipher_evaluations"].append(evaluation)
            output.write(json.dumps(record, sort_keys=True) + "\n")
    all_hits = []
    total_trials = 0
    with ledger.open() as source:
        for line in source:
            record = json.loads(line)
            total_trials += len(record["cipher_evaluations"])
            for evaluation in record["cipher_evaluations"]:
                if evaluation["padding_valid"]:
                    all_hits.append({"password_sha256": record["password_sha256"], "provenance": record["provenance"], **evaluation})
    ranked = sorted(all_hits, key=lambda hit: (bool(hit["structural_validity"]), hit["score"]["printable_ratio"] >= 0.9, hit["score"]["language_score"], hit["score"]["longest_printable_run"]), reverse=True)
    report = {"id": identifier, "ledger": str(ledger.relative_to(SOURCES.parents[1])), "candidate_set_sha256": plan["candidate_set_sha256"], "unique_passwords": len(candidates), "total_trials": total_trials, "new_trials_this_run": tested, "padding_hits": len(all_hits), "elapsed_seconds_this_run": round(perf_counter() - started, 3), "structural_hits": sum(bool(hit["structural_validity"]) for hit in all_hits), "target_matches": 0, "top_hits": ranked[:20], "status": "INCONCLUSIVE", "result": "No solution claimed. Inspect high-ranked hits; readable scores/magic bytes are filters, not creator-intent evidence."}
    write_once_json(CYCLE / "inner-search-results.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "top_hits"}, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description="Source-traced finite passphrase derivation; calculate space before searching")
    parser.add_argument("command", choices=("plan", "run"))
    arguments = parser.parse_args()
    if arguments.command == "plan":
        estimate_space()
    else:
        run_search()


if __name__ == "__main__":
    main()
