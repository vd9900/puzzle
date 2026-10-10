#!/usr/bin/env python3
import argparse
import base64
import itertools
import json
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.gsmg import ARTIFACTS, SOURCES, evp_bytes_to_key, parse_salted
from tools.research_common import CYCLE, fingerprint, score_plaintext, source_record, target_checks, write_once_json


def selected_payload():
    report = json.loads((CYCLE / "prime-markers.json").read_text())
    frames = [frame for frame in report["near_white_frame"]["hypotheses"] if frame["near_white_hypothesis_bit"] == "1"]
    candidates = [item["mask"] for item in frames[0]["comparisons"] if item["all_available_prime_markers_match"]]
    if candidates != [1017]:
        raise ValueError("The observed partial-frame condition no longer selects the expected branch")
    return next(parse["nonprime_payload"] for parse in report["best_parses"] if parse["mask"] == 1017)


def square_transforms():
    for transpose in (False, True):
        for reflect_rows, reflect_columns in itertools.product((False, True), repeat=2):
            yield {"transpose": transpose, "reflect_rows": reflect_rows, "reflect_columns": reflect_columns}


def derived_forms():
    payload = selected_payload()
    if len(payload) != 60:
        raise ValueError("Coordinate grouping requires the preserved 60-letter residual")
    cubes = {keyword or "unkeyed": "".join(dict.fromkeys(keyword + "abcdefghijklmnopqrstuvwxyz.")) for keyword in ("", "matrixsumlist", "thematrixhasyou", "lastwordsbeforearchichoicethispassword", "salphaseion", "theseedisplanted")}
    for mapping_name, alphabet in (("alphabet-order", "abcdefghi"), ("dbbi-first-occurrence-order", "dbifhcega")):
        mapping = {letter: index for index, letter in enumerate(alphabet)}
        for square in square_transforms():
            coordinates = []
            for letter in payload:
                row, column = divmod(mapping[letter], 3)
                if square["transpose"]:
                    row, column = column, row
                coordinates.append((2 - row if square["reflect_rows"] else row, 2 - column if square["reflect_columns"] else column))
            streams = {
                "interleaved-row-column": [value for coordinate in coordinates for value in coordinate],
                "row-plane-then-column-plane": [coordinate[0] for coordinate in coordinates] + [coordinate[1] for coordinate in coordinates],
            }
            for stream_name, digits in streams.items():
                for reverse in (False, True):
                    stream = digits[::-1] if reverse else digits
                    for cube_name, cube in cubes.items():
                        decoded = "".join(cube[stream[offset] * 9 + stream[offset + 1] * 3 + stream[offset + 2]] for offset in range(0, len(stream), 3))
                        parameters = {"digit_mapping": mapping_name, "square_orientation": square, "coordinate_stream": stream_name, "stream_reverse": reverse, "cube_key": cube_name, "cube_alphabet": cube, "grouping": "two ternary coordinates per symbol -> exact three-coordinate groups, 120 digits -> 40 characters"}
                        yield parameters, decoded.encode()
    for mapping_name, alphabet in (("a0", "abcdefghi"), ("first-occurrence0", "dbifhcega")):
        mapping = {letter: index for index, letter in enumerate(alphabet)}
        numbers = [mapping[letter] for letter in payload]
        for reverse in (False, True):
            ordered = numbers[::-1] if reverse else numbers
            for width in (2, 3):
                values = []
                for offset in range(0, len(ordered), width):
                    value = 0
                    for digit in ordered[offset:offset + width]:
                        value = value * 9 + digit
                    values.append(value)
                if max(values) <= 255:
                    yield {"digit_mapping": mapping_name, "reverse": reverse, "group_width": width, "decoder": "fixed base9 groups to unshifted byte values; no modulo or offset"}, bytes(values)


def password_candidates():
    candidates = {}
    forms = list(derived_forms())
    for parameters, payload in forms:
        for representation, password in (("raw", payload), ("sha256-hex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
            identifier = fingerprint(password)
            if identifier not in candidates:
                candidates[identifier] = {"password": password, "provenance": []}
            candidates[identifier]["provenance"].append({"transformation": parameters, "representation": representation, "decoded_base64": base64.b64encode(payload).decode(), "decoded_score": score_plaintext(payload)})
    return candidates, forms


def plan():
    candidates, forms = password_candidates()
    result = {"id": "C02-RESIDUAL-COORDINATES", "source": source_record(SOURCES / "salphaseion.html", "unchanged mask1017 nonprime residual; partial-frame hypothesis"), "residual": selected_payload(), "residual_length": 60, "decoded_forms": len(forms), "unique_passwords": len(candidates), "aes_trials": len(candidates) * 6, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in candidates.values()))), "justification": "Nine-symbol alphabet can label a 3x3 coordinate square; two ternary digits per input regroup into cube triples; exact 60 length supplies 120 coordinates/40 outputs. Only alphabet/observed first-occurrence order and clue-keyed cubes tested; no free 9! or 27! search.", "estimated_crypto_seconds": round(len(candidates) * 6 / 50000, 4), "limitations": "Custom coordinate regrouping, not a proven Trifid cipher; cube key, square orientation and planar/interleaved convention remain hypotheses"}
    write_once_json(CYCLE / "coordinate-plan.json", result)
    print(json.dumps(result, indent=2))


def run():
    candidates, forms = password_candidates()
    specification = json.loads((CYCLE / "coordinate-plan.json").read_text())
    if fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in candidates.values()))) != specification["candidate_set_sha256"]:
        raise ValueError("Candidate set changed after plan")
    path = CYCLE / "coordinate-aes.jsonl"
    if path.exists():
        raise ValueError("Preserve existing coordinate ledger")
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in ("phase32-inner", "salphaseion-small", "cosmic-duality")}
    hits = []
    started = perf_counter()
    with path.open("x") as output:
        for identifier, candidate in sorted(candidates.items()):
            entry = {"source": specification["source"], "password_sha256": identifier, "password_base64": base64.b64encode(candidate["password"]).decode(), "provenance": candidate["provenance"], "evaluations": []}
            for target, (salt, ciphertext) in blobs.items():
                for digest in ("md5", "sha256"):
                    key, initialization_vector = evp_bytes_to_key(candidate["password"], salt, digest)
                    evaluation = {"target": target, "cipher": "AES-256-CBC", "kdf": "EVP_BytesToKey", "digest": digest, "iterations": 1, "salt": salt.hex(), "key": key.hex(), "iv": initialization_vector.hex(), "padding_valid": False, "plaintext": None, "score": None, "structural_validity": None, "downstream_validity": None}
                    try:
                        plaintext = unpad(AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext), 16)
                        validity = target_checks(plaintext)
                        if validity["target_match"]:
                            raise RuntimeError("Target match: halt without logging private key")
                        evaluation.update({"padding_valid": True, "plaintext": base64.b64encode(plaintext).decode(), "score": score_plaintext(plaintext), "structural_validity": validity["structures"], "downstream_validity": validity})
                        hits.append(evaluation)
                    except ValueError:
                        pass
                    entry["evaluations"].append(evaluation)
            output.write(json.dumps(entry, sort_keys=True) + "\n")
    decoded_scores = sorted(({"parameters": parameters, "decoded": payload.decode("latin-1"), "score": score_plaintext(payload)} for parameters, payload in forms), key=lambda row: (row["score"]["dictionary_coverage"], row["score"]["language_score"]), reverse=True)
    result = {"id": specification["id"], "unique_passwords": len(candidates), "decoded_forms": len(forms), "aes_trials": len(candidates) * 6, "padding_hits": len(hits), "structure_hits": sum(bool(hit["structural_validity"]) for hit in hits), "target_matches": 0, "max_padding_hit_printable_ratio": max((hit["score"]["printable_ratio"] for hit in hits), default=0), "top_decodes": decoded_scores[:10], "elapsed_seconds": round(perf_counter() - started, 3), "status": "INCONCLUSIVE", "result": "No downstream-validated solution from exact 3x3/3-coordinate regrouping or fixed base9 byte groups"}
    write_once_json(CYCLE / "coordinate-results.json", result)
    print(json.dumps({key: value for key, value in result.items() if key != "top_decodes"}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Exact unchanged residual coordinate interpretation with downstream AES gate")
    parser.add_argument("command", choices=("plan", "run"))
    arguments = parser.parse_args()
    plan() if arguments.command == "plan" else run()


if __name__ == "__main__":
    main()
