#!/usr/bin/env python3
import argparse
import base64
import json
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.analyze_salphaseion import split_segments
from tools.gsmg import ARTIFACTS, SOURCES, evp_bytes_to_key, parse_salted
from tools.joint_derivation import columnar, digit_mappings, nine_checkerboard
from tools.research_common import CYCLE, fingerprint, score_plaintext, source_record, target_checks, write_once_json
from tools.salphaseion_experiments import keyed_alphabet


def sum_streams():
    text = split_segments()["dbbi"]
    streams = {}
    for name, mapping in digit_mappings().items():
        values = [mapping[letter] for letter in text]
        for width in (7, 13):
            rows = [values[offset:offset + width] for offset in range(0, len(values), width)]
            sums = {"rows": [sum(row) % 9 for row in rows], "columns": [sum(column) % 9 for column in zip(*rows)]}
            for axis, numbers in sums.items():
                for reverse in (False, True):
                    parameters = {"source_segment": "dbbi", "mapping": name, "rectangle_rows": len(rows), "rectangle_columns": width, "sum_axis": axis, "modulus": 9, "reverse": reverse}
                    stream = numbers[::-1] if reverse else numbers
                    identifier = tuple(stream)
                    if identifier not in streams:
                        streams[identifier] = {"stream": stream, "provenance": []}
                    streams[identifier]["provenance"].append(parameters)
    return streams


def candidates():
    text = split_segments()["faed"]
    routes = [("identity", text), ("reversed", text[::-1])]
    for keyword in ("theseedisplanted", "lastwordsbeforearchichoicethispassword"):
        for decrypt in (False, True):
            routes.append((f"columnar:{keyword}:{decrypt}", columnar(text, keyword, decrypt)))
    alphabets = {name: keyed_alphabet(name).replace("j", "").replace(".", "").replace("/", "") for name in ("matrixsumlist", "lastwordsbeforearchichoicethispassword", "fubcdoralthingkymvps")}
    passwords = {}
    decode_trials = 0
    for route_name, routed in routes:
        for mapping_name, mapping in digit_mappings().items():
            values = [mapping[letter] for letter in routed]
            prefixes = tuple(sorted((mapping["b"], mapping["e"])))
            for stream_record in sum_streams().values():
                stream = stream_record["stream"]
                for operation in ("add", "subtract"):
                    combined = [(value + (1 if operation == "add" else -1) * stream[index % len(stream)]) % 9 for index, value in enumerate(values)]
                    parameters = {"faed_route": route_name, "faed_mapping": mapping_name, "key_stream": stream_record, "operation_mod9": operation}
                    number = int("".join(map(str, combined)), 9)
                    outputs = [("base9-bytes", number.to_bytes(max(1, (number.bit_length() + 7) // 8), "big"))]
                    for alphabet_name, alphabet in alphabets.items():
                        try:
                            decoded = nine_checkerboard(combined, alphabet, prefixes).encode()
                            outputs.append(("checkerboard:" + alphabet_name, decoded))
                        except ValueError:
                            outputs.append(("checkerboard:" + alphabet_name, None))
                    for decoder, payload in outputs:
                        decode_trials += 1
                        if payload is None:
                            continue
                        variants = {"raw": payload, "sha256-hex": fingerprint(payload).encode(), "sha256-raw": bytes.fromhex(fingerprint(payload))}
                        for representation, password in variants.items():
                            identifier = fingerprint(password)
                            if identifier not in passwords:
                                passwords[identifier] = {"password": password, "provenance": []}
                            passwords[identifier]["provenance"].append(parameters | {"decoder": decoder, "password_representation": representation, "decoded_base64": base64.b64encode(payload).decode(), "decode_score": score_plaintext(payload)})
    return passwords, decode_trials


def plan():
    passwords, decode_trials = candidates()
    result = {"id": "C02-PAIRED-SUMSTREAM", "dbbi_sum_streams": len(sum_streams()), "faed_routes": 6, "faed_mappings": 3, "operations_mod9": 2, "decoders": 4, "decode_trials": decode_trials, "unique_passwords": len(passwords), "aes_trials": len(passwords) * 6, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in passwords.values()))), "hypothesis": "The clue matrixsumlist instructs summing the 7x13/13x7 dbbi digit matrix; resulting row/column sums repeated modulo nine remove faed over-encryption before byte/checkerboard decoding.", "source_evidence": [source_record(SOURCES / "salphaseion.html", "dbbi 91 letters / matrixsumlist / faed 570 letters"), {"path": "research/evidence/cycle02/FINDINGS.md", "classification": "SECONDARY_RESEARCH", "warning": "Key/payload role and modulo-nine cipher are interpretations, not hard facts"}], "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 3), "throughput_basis": "Earlier measured benchmark, not a runtime guarantee"}
    write_once_json(CYCLE / "paired-plan.json", result)
    print(json.dumps(result, indent=2))


def run():
    passwords, decode_trials = candidates()
    specification = json.loads((CYCLE / "paired-plan.json").read_text())
    if specification["candidate_set_sha256"] != fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in passwords.values()))):
        raise ValueError("Candidate space changed since plan")
    path = CYCLE / "paired-aes.jsonl"
    if path.exists():
        raise ValueError("Preserving prior ledger")
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in ("phase32-inner", "salphaseion-small", "cosmic-duality")}
    hits = []
    started = perf_counter()
    with path.open("x") as output:
        for identifier, candidate in sorted(passwords.items()):
            row = {"password_sha256": identifier, "password_base64": base64.b64encode(candidate["password"]).decode(), "source_evidence": specification["source_evidence"], "provenance": candidate["provenance"], "evaluations": []}
            for target, (salt, ciphertext) in blobs.items():
                for digest in ("md5", "sha256"):
                    key, initialization_vector = evp_bytes_to_key(candidate["password"], salt, digest)
                    evaluation = {"target": target, "kdf": "EVP_BytesToKey", "digest": digest, "iterations": 1, "cipher": "AES-256-CBC", "salt": salt.hex(), "key": key.hex(), "iv": initialization_vector.hex(), "padding_valid": False, "plaintext": None, "score": None, "structural_validity": None, "downstream_validity": None}
                    padded = AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext)
                    try:
                        plaintext = unpad(padded, 16)
                        validity = target_checks(plaintext)
                        if validity["target_match"]:
                            raise RuntimeError("Target match: stop without exposing secret")
                        evaluation.update({"padding_valid": True, "plaintext": base64.b64encode(plaintext).decode(), "score": score_plaintext(plaintext), "structural_validity": validity["structures"], "downstream_validity": validity})
                        hits.append(evaluation)
                    except ValueError:
                        pass
                    row["evaluations"].append(evaluation)
            output.write(json.dumps(row, sort_keys=True) + "\n")
    result = {"id": specification["id"], "unique_passwords": len(passwords), "aes_trials": len(passwords) * 6, "decode_trials": decode_trials, "padding_hits": len(hits), "max_printable_ratio": max((hit["score"]["printable_ratio"] for hit in hits), default=0), "structure_hits": sum(bool(hit["structural_validity"]) for hit in hits), "target_matches": 0, "elapsed_seconds": round(perf_counter() - started, 3), "status": "INCONCLUSIVE", "result": "No demonstrated solution from the fixed paired-matrix sum-stream family"}
    write_once_json(CYCLE / "paired-results.json", result)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Paired dbbi matrixsumlist -> faed mod-nine over-encryption hypothesis")
    parser.add_argument("command", choices=("plan", "run"))
    arguments = parser.parse_args()
    plan() if arguments.command == "plan" else run()


if __name__ == "__main__":
    main()
