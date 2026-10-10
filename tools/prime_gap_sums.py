#!/usr/bin/env python3
import argparse
import base64
import json
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.gsmg import ARTIFACTS, SOURCES, evp_bytes_to_key, parse_salted
from tools.prime_markers import is_prime
from tools.research_common import CYCLE, fingerprint, score_plaintext, source_record, target_checks, write_once_json


def derive_candidates():
    report = json.loads((CYCLE / "prime-markers.json").read_text())
    candidates = {}
    lists = []
    mappings = {"a1": {letter: index + 1 for index, letter in enumerate("abcdefghi")}, "a0": {letter: index for index, letter in enumerate("abcdefghi")}, "first-occurrence0": {letter: index for index, letter in enumerate("dbifhcega")}}
    for parse in report["best_parses"]:
        if parse["invalid_prime_tokens"]:
            continue
        tokens = parse["tokens"]
        boundaries = [index for index, token in enumerate(tokens) if is_prime(token["position_one_based"])]
        gaps = ["".join(token["token"] for token in tokens[left + 1:right]) for left, right in zip([-1] + boundaries, boundaries + [len(tokens)])]
        for mapping_name, mapping in mappings.items():
            sums = [sum(mapping[letter] for letter in gap) for gap in gaps]
            for include_tail in (False, True):
                values = sums if include_tail else sums[:-1]
                entry = {"mask": parse["mask"], "mapping": mapping_name, "include_tail": include_tail, "gaps": gaps if include_tail else gaps[:-1], "sums": values}
                lists.append(entry)
                transformed = {"gap-sums": values, "gap-sums-reversed": values[::-1], "gap-sums-mod9": [value % 9 for value in values], "gap-sums-mod26-a0": [value % 26 for value in values]}
                for transform, numbers in transformed.items():
                    forms = {"raw-byte-list": bytes(numbers), "decimal-concat": "".join(map(str, numbers)).encode(), "decimal-space-list": " ".join(map(str, numbers)).encode(), "decimal-comma-list": ",".join(map(str, numbers)).encode(), "hex-lowercase-list": bytes(numbers).hex().encode()}
                    if transform == "gap-sums-mod26-a0":
                        forms["a0z25-letters"] = "".join(chr(97 + value) for value in numbers).encode()
                    for representation, material in forms.items():
                        for password_mode in ("raw", "sha256-hex", "sha256-raw"):
                            password = material if password_mode == "raw" else fingerprint(material).encode() if password_mode == "sha256-hex" else bytes.fromhex(fingerprint(material))
                            identifier = fingerprint(password)
                            if identifier not in candidates:
                                candidates[identifier] = {"password": password, "provenance": []}
                            candidates[identifier]["provenance"].append({"prime_parse": entry, "transformation": transform, "representation": representation, "password_mode": password_mode})
    return candidates, lists


def plan():
    candidates, lists = derive_candidates()
    report = {"id": "C02-PRIME-GAP-SUMS", "parse_sum_lists": len(lists), "unique_passwords": len(candidates), "aes_trials": len(candidates) * 6, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in candidates.values()))), "source": source_record(SOURCES / "salphaseion.html", "dbbi prime-marker gaps"), "justification": "Only fully prime-marked parses among the maximum 20-color-bit prefix matches; matrixsumlist motivates literal sums of nonprime gaps; raw and SHA256 variants follow prior puzzle stages. Tail inclusion is explicit, not silently discarded.", "estimated_crypto_seconds": round(len(candidates) * 6 / 50000, 4), "throughput_basis": "Prior measured local legacy-AES throughput exceeds 50000 trials/s, excluding ledger/scoring overhead", "limits": "No arbitrary offsets, extra character edits or keyword fitting"}
    write_once_json(CYCLE / "prime-gap-plan.json", report)
    print(json.dumps(report, indent=2))


def run():
    candidates, lists = derive_candidates()
    specification = json.loads((CYCLE / "prime-gap-plan.json").read_text())
    if specification["candidate_set_sha256"] != fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in candidates.values()))):
        raise ValueError("Candidate set differs from planned space")
    path = CYCLE / "prime-gap-aes.jsonl"
    if path.exists():
        raise ValueError("Preserving existing experiment ledger")
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in ("phase32-inner", "salphaseion-small", "cosmic-duality")}
    hits = []
    started = perf_counter()
    with path.open("x") as output:
        for identifier, candidate in sorted(candidates.items()):
            row = {"id": specification["id"] + ":" + identifier, "source": specification["source"], "password_base64": base64.b64encode(candidate["password"]).decode(), "password_sha256": identifier, "provenance": candidate["provenance"], "evaluations": []}
            for target, (salt, ciphertext) in blobs.items():
                for digest in ("md5", "sha256"):
                    key, initialization_vector = evp_bytes_to_key(candidate["password"], salt, digest)
                    evaluation = {"target": target, "cipher": "AES-256-CBC", "salt_hex": salt.hex(), "key_hex": key.hex(), "iv_hex": initialization_vector.hex(), "kdf": "EVP_BytesToKey", "digest": digest, "iterations": 1, "padding": "PKCS#7", "padding_valid": False, "plaintext": None, "score": None, "structural_validity": None, "downstream_validity": None}
                    padded = AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext)
                    try:
                        plaintext = unpad(padded, 16)
                        validity = target_checks(plaintext)
                        if validity["target_match"]:
                            raise RuntimeError("Target match: stop without exposing candidate")
                        evaluation.update({"padding_valid": True, "plaintext": base64.b64encode(plaintext).decode(), "score": score_plaintext(plaintext), "structural_validity": validity["structures"], "downstream_validity": validity})
                        hits.append(evaluation | {"password_sha256": identifier})
                    except ValueError:
                        pass
                    row["evaluations"].append(evaluation)
            output.write(json.dumps(row, sort_keys=True) + "\n")
    result = {"id": specification["id"], "unique_passwords": len(candidates), "trials": len(candidates) * 6, "sum_lists": lists, "padding_hits": len(hits), "hits": hits, "structural_hits": sum(bool(hit["structural_validity"]) for hit in hits), "target_matches": 0, "elapsed_seconds": round(perf_counter() - started, 3), "status": "INCONCLUSIVE", "result": "Literal prime-gap sum list family yields no demonstrated target solution"}
    write_once_json(CYCLE / "prime-gap-results.json", result)
    print(json.dumps({key: value for key, value in result.items() if key not in ("sum_lists", "hits")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Literal matrixsumlist interpretation using verified prime gaps")
    parser.add_argument("command", choices=("plan", "run"))
    arguments = parser.parse_args()
    plan() if arguments.command == "plan" else run()


if __name__ == "__main__":
    main()
