#!/usr/bin/env python3
import argparse
import base64
import json
from collections import Counter
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools.analyze_salphaseion import split_segments
from tools.gsmg import ARTIFACTS, SOURCES, evp_bytes_to_key, extract_grid, parse_salted
from tools.joint_derivation import columnar, digit_mappings, nine_checkerboard
from tools.prime_boundary import binary_boundary, extended_markers, special_frames
from tools.prime_markers import is_prime, tokenizations
from tools.research_common import fingerprint, score_plaintext, source_record, target_checks, write_once_json
from tools.salphaseion_experiments import keyed_alphabet
from tools.zeroed_residual import OUTPUT


def image_matrices():
    grid = extract_grid(SOURCES / "gsmg-puzzle.png")
    coordinates = [(row, column) for row in range(14) for column in range(14) if grid["colors"][row][column] == "near_white"]
    if len(coordinates) != 1:
        raise ValueError("Expected one unchanged near-white cell")
    removed_row, removed_column = coordinates[0]
    yield "original-near-white-0", grid["matrix"]
    altered = [row[:] for row in grid["matrix"]]
    altered[removed_row][removed_column] = 1
    yield "explicit-near-white-1", altered
    reduced = [[value for column, value in enumerate(row) if column != removed_column] for index, row in enumerate(grid["matrix"]) if index != removed_row]
    yield "omit-near-white-row-column", reduced


def image_sum_streams():
    streams = {}
    for name, matrix in image_matrices():
        rows = list(map(sum, matrix))
        columns = list(map(sum, zip(*matrix)))
        for order, sums in (("rows", rows), ("columns", columns), ("rows-then-columns", rows + columns), ("columns-then-rows", columns + rows)):
            for reverse in (False, True):
                values = list(reversed(sums)) if reverse else sums
                identifier = tuple(value % 9 for value in values)
                candidate = streams.setdefault(identifier, {"digits_mod9": list(identifier), "provenance": []})
                candidate["provenance"].append({"matrix": name, "shape": [len(matrix), len(matrix[0])], "sum_axis_order": order, "reverse": reverse, "unreduced_sums": values})
    return streams


def residual():
    boundary = binary_boundary()
    frame = next(frame for near_white, frame, events in special_frames() if near_white == 1)
    matches = []
    for mask, tokens in tokenizations(split_segments()["dbbi"]):
        if "".join(entry["bit"] for entry in extended_markers(mask, tokens, boundary)).startswith(frame):
            matches.append("".join(entry["token"] for entry in tokens if not is_prime(entry["position_one_based"])))
    if len(matches) != 1:
        raise ValueError("Full-frame-selected residual is not unique")
    return matches[0]


def candidates():
    faed = split_segments()["faed"]
    routes = [("prime-residual", "identity", residual()), ("faed", "identity", faed)]
    for keyword in ("theseedisplanted", "lastwordsbeforearchichoicethispassword"):
        routes.append(("faed", "columnar-decrypt:" + keyword, columnar(faed, keyword)))
    alphabets = {name: keyed_alphabet(name).replace("j", "").replace(".", "").replace("/", "") for name in ("matrixsumlist", "lastwordsbeforearchichoicethispassword", "fubcdoralthingkymvps")}
    passwords = {}
    forms = []
    streams = image_sum_streams()
    for segment, route, text in routes:
        for mapping_name, mapping in digit_mappings().items():
            values = [mapping[symbol] for symbol in text]
            prefixes = tuple(sorted((mapping["b"], mapping["e"])))
            for stream in streams.values():
                for operation, sign in (("add", 1), ("subtract", -1)):
                    digits = [(value + sign * stream["digits_mod9"][index % len(stream["digits_mod9"])]) % 9 for index, value in enumerate(values)]
                    parameters = {"segment": segment, "route": route, "digit_mapping": mapping_name, "sum_stream": stream, "operation_mod9": operation, "prefixes": list(prefixes)}
                    number = int("".join(map(str, digits)), 9)
                    decoded = [("base9-integer-big-endian", number.to_bytes(max(1, (number.bit_length() + 7) // 8), "big"), None)]
                    for alphabet_name, alphabet in alphabets.items():
                        try:
                            decoded.append(("nine-column-checkerboard:" + alphabet_name, nine_checkerboard(digits, alphabet, prefixes).encode(), None))
                        except ValueError as error:
                            decoded.append(("nine-column-checkerboard:" + alphabet_name, None, str(error)))
                    for decoder, payload, error in decoded:
                        form = {"parameters": parameters | {"decoder": decoder}, "digits_mod9": digits, "plaintext_base64": None if payload is None else base64.b64encode(payload).decode(), "error": error, "score": None if payload is None else score_plaintext(payload)}
                        forms.append(form)
                        if payload is None:
                            continue
                        for representation, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
                            candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                            candidate["provenance"].append(form["parameters"] | {"representation": representation, "decoded_sha256": fingerprint(payload)})
    return passwords, forms


def plan():
    passwords, forms = candidates()
    original = next(matrix for name, matrix in image_matrices() if name == "original-near-white-0")
    all_deleted_totals = Counter(sum(map(sum, original)) - sum(original[row]) - sum(values[column] for values in original) + original[row][column] for row in range(14) for column in range(14))
    report = {"id": "C03-IMAGE-SUMSTREAM", "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png"), source_record(SOURCES / "salphaseion.html"), source_record(OUTPUT / "prime-boundary.json")], "justification": "matrixsumlist explicitly references a matrix; primary image supplies 14x14 grid, near-white anomaly deletion gives 13x13/26 axis sums, fitting 13/26 clue lengths. Test as a mod9 over-encryption stream, with independent downstream AES gate, not a confirmed VIC/key structure.", "source_constraints": {"unchanged_image_ones": 101, "reduced_image_ones": 89, "reduced_image_axis_sums": 26, "other_row_column_deletions_also_total_89": all_deleted_totals[89] - 1, "limits": "89 is not a unique deletion total: 23 of 196 row/column deletions produce it. Near-white=1 and deleting its axes are explicit alternatives, not overwritten original bits."}, "search_space": {"matrix_variants": 3, "unique_sum_streams": len(image_sum_streams()), "segment_routes": 4, "digit_mappings": 3, "operations": 2, "decoders": 4, "decode_forms": len(forms), "decode_errors": sum(form["error"] is not None for form in forms), "unique_passwords": len(passwords), "aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 3), "status": "UNTESTED", "gate": "Recognized independently supported downstream stage or exact scoped key, not a padding/language hit"}
    write_once_json(OUTPUT / "image-sum-plan.json", report)
    write_once_json(OUTPUT / "image-sum-decodes.json", forms)
    print(json.dumps(report, indent=2))
    return report


def run():
    specification = json.loads((OUTPUT / "image-sum-plan.json").read_text())
    passwords, forms = candidates()
    if fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))) != specification["candidate_set_sha256"]:
        raise ValueError("Candidate set changed after planning")
    path = OUTPUT / "image-sum-aes.jsonl"
    if path.exists():
        raise ValueError("Preserve existing image-sum ledger")
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in ("phase32-inner", "salphaseion-small", "cosmic-duality")}
    hits = []
    started = perf_counter()
    with path.open("x") as output:
        for identifier, candidate in sorted(passwords.items()):
            password = bytes.fromhex(candidate["password_hex"])
            entry = {"password_sha256": identifier, "password_base64": base64.b64encode(password).decode(), "source_evidence": specification["source_evidence"], "provenance": candidate["provenance"], "evaluations": []}
            for target, (salt, ciphertext) in blobs.items():
                for digest in ("md5", "sha256"):
                    key, initialization_vector = evp_bytes_to_key(password, salt, digest)
                    evaluation = {"target": target, "cipher": "AES-256-CBC", "kdf": "EVP_BytesToKey", "digest": digest, "iterations": 1, "salt": salt.hex(), "key": key.hex(), "iv": initialization_vector.hex(), "padding_valid": False, "plaintext": None, "score": None, "structural_validity": None, "downstream_validity": None}
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
    report = {"id": specification["id"], "decode_forms": len(forms), "unique_passwords": len(passwords), "aes_trials": len(passwords) * 6, "padding_hits": len(hits), "structure_hits": sum(bool(hit["structural_validity"]) for hit in hits), "target_matches": 0, "max_hit_printable_ratio": max((hit["score"]["printable_ratio"] for hit in hits), default=0), "elapsed_seconds": round(perf_counter() - started, 3), "ledger_sha256": fingerprint(path.read_bytes()), "status": "INCONCLUSIVE", "result": "Literal image-axis sum streams plus bounded mod9/columnar/decoder rules supply no recognized downstream structure or scoped key; family negative, not rejection of the image as a key source"}
    write_once_json(OUTPUT / "image-sum-results.json", report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bounded original-image matrix sum derivation with downstream AES validation")
    parser.add_argument("command", choices=("plan", "run"))
    arguments = parser.parse_args()
    plan() if arguments.command == "plan" else run()
