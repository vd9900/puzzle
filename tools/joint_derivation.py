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
from tools.research_common import CYCLE, fingerprint, score_plaintext, source_record, target_checks, write_once_json
from tools.salphaseion_experiments import keyed_alphabet


def columnar(text, keyword, decrypt=True):
    width = len(keyword)
    if not width:
        raise ValueError("Nonempty transposition key required")
    order = sorted(range(width), key=lambda index: (keyword[index], index))
    if not decrypt:
        return "".join(text[column::width] for column in order)
    rows, remainder = divmod(len(text), width)
    columns = {}
    position = 0
    for column in order:
        size = rows + int(column < remainder)
        columns[column] = text[position:position + size]
        position += size
    return "".join(columns[column][row] for row in range(rows + bool(remainder)) for column in range(width) if row < len(columns[column]))


def nine_checkerboard(digits, alphabet, prefixes):
    if len(alphabet) != 25 or len(set(alphabet)) != 25:
        raise ValueError("Nine-column checkerboard requires 25 distinct symbols")
    board = dict(zip((column for column in range(9) if column not in prefixes), alphabet[:7]))
    board.update({(prefix, column): symbol for row, prefix in enumerate(prefixes) for column, symbol in enumerate(alphabet[7 + row * 9:16 + row * 9])})
    position = 0
    decoded = []
    while position < len(digits):
        code = digits[position]
        position += 1
        if code in prefixes:
            if position == len(digits):
                raise ValueError("Incomplete checkerboard row prefix; no truncation allowed")
            code = (code, digits[position])
            position += 1
        decoded.append(board[code])
    return "".join(decoded)


def root_variants():
    segments = split_segments()
    marker_report = json.loads((CYCLE / "prime-markers.json").read_text())
    marker_payloads = sorted({parse["nonprime_payload"] for parse in marker_report["best_parses"] if parse["invalid_prime_tokens"] == 0})
    roots = {"dbbi": segments["dbbi"], "faed": segments["faed"]}
    roots.update({f"prime-remainder-{len(payload)}": payload for payload in marker_payloads})
    for name, text in roots.items():
        yield name, text, {"route": "identity"}
        yield name, text[::-1], {"route": "reverse"}
        if name == "dbbi":
            keywords = ("matrixsumlist",)
        elif name == "faed":
            keywords = ("theseedisplanted", "lastwordsbeforearchichoicethispassword")
        else:
            keywords = ()
        for keyword in keywords:
            for decrypt in (False, True):
                transposed = columnar(text, keyword, decrypt)
                for reverse in (False, True):
                    yield name, transposed[::-1] if reverse else transposed, {"route": "keyed-columnar", "key": keyword, "decrypt": decrypt, "reverse": reverse, "duplicate_key_order": "stable alphabetical sort then original column index"}


def digit_mappings():
    return {
        "a0": {letter: index for index, letter in enumerate("abcdefghi")},
        "a1mod9": {letter: (index + 1) % 9 for index, letter in enumerate("abcdefghi")},
        "first-occurrence0": {letter: index for index, letter in enumerate("dbifhcega")},
    }


def keystreams():
    matrix = extract_grid(SOURCES / "gsmg-puzzle.png")["matrix"]
    rows = [sum(row) % 9 for row in matrix]
    columns = [sum(column) % 9 for column in zip(*matrix)]
    streams = {"none": None, "image-row-sums-mod9": rows, "image-column-sums-mod9": columns, "image-row-sums-reversed-mod9": rows[::-1], "image-column-sums-reversed-mod9": columns[::-1]}
    return streams


def decoded_forms():
    alphabets = {
        "matrixsumlist": keyed_alphabet("matrixsumlist").replace("j", "").replace("/", "").replace(".", ""),
        "enter": keyed_alphabet("enter").replace("j", "").replace("/", "").replace(".", ""),
        "salphaseion": keyed_alphabet("salphaseion").replace("j", "").replace("/", "").replace(".", ""),
        "lastwordsbeforearchichoicethispassword": keyed_alphabet("lastwordsbeforearchichoicethispassword").replace("j", "").replace("/", "").replace(".", ""),
        "known-checkerboard-IJ-merge": keyed_alphabet("fubcdorale thingky mvps".replace(" ", "")).replace("j", "").replace("/", "").replace(".", ""),
    }
    for name, text, route in root_variants():
        for mapping_name, mapping in digit_mappings().items():
            original = [mapping[letter] for letter in text]
            prefixes = tuple(sorted((mapping["b"], mapping["e"])))
            for stream_name, stream in keystreams().items():
                for operation in (("none",) if stream is None else ("add", "subtract")):
                    digits = original if stream is None else [(digit + (1 if operation == "add" else -1) * stream[index % len(stream)]) % 9 for index, digit in enumerate(original)]
                    parameters = {"root": name, "route": route, "digit_mapping": mapping_name, "keystream": stream_name, "operation_mod9": operation}
                    digit_text = "".join(str(digit) for digit in digits)
                    number = int(digit_text, 9)
                    yield parameters | {"decoder": "whole-base9-big-endian-bytes"}, number.to_bytes(max(1, (number.bit_length() + 7) // 8), "big"), None
                    for alphabet_name, alphabet in alphabets.items():
                        try:
                            payload = nine_checkerboard(digits, alphabet, prefixes).encode()
                            yield parameters | {"decoder": "nine-column-checkerboard", "alphabet_name": alphabet_name, "alphabet": alphabet, "prefixes": prefixes}, payload, None
                        except ValueError as error:
                            yield parameters | {"decoder": "nine-column-checkerboard", "alphabet_name": alphabet_name, "alphabet": alphabet, "prefixes": prefixes}, None, str(error)


def password_set():
    candidates = {}
    forms = list(decoded_forms())
    for parameters, payload, error in forms:
        if payload is None:
            continue
        variants = {"raw": payload, "sha256-hex": fingerprint(payload).encode(), "sha256-raw": bytes.fromhex(fingerprint(payload))}
        if parameters["decoder"] == "nine-column-checkerboard":
            variants["uppercase"] = payload.upper()
            variants["uppercase-sha256-hex"] = fingerprint(payload.upper()).encode()
            variants["uppercase-sha256-raw"] = bytes.fromhex(fingerprint(payload.upper()))
        for representation, password in variants.items():
            identifier = fingerprint(password)
            if identifier not in candidates:
                candidates[identifier] = {"password": password, "provenance": []}
            candidates[identifier]["provenance"].append(parameters | {"password_representation": representation})
    return candidates, forms


def plan():
    candidates, forms = password_set()
    report = {
        "id": "C02-JOINT-MOD9", "roots_and_routes": len(list(root_variants())), "digit_mappings": len(digit_mappings()),
        "keystream_variants": 9, "decoders": 6, "decode_forms": len(forms), "unique_passwords": len(candidates),
        "aes_trials": len(candidates) * 3 * 2, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in candidates.values()))),
        "justification": "Preserved primary colors/primes, matrixsumlist 13-char key matching 91=7*13, 38-char adjacent clue matching 570=15*38, nine-symbol coordinate family and known checkerboard precedent. Mod9 stream mechanism is a secondary interpretation; no claim of intended cipher.",
        "cipher_parameters": "AES-256-CBC, EVP_BytesToKey MD5/SHA256 count=1, observed salts, PKCS#7",
        "estimated_crypto_seconds": round(len(candidates) * 6 / 50000, 3),
        "throughput_basis": "Earlier local legacy-EVP/AES benchmark exceeded 50000 trials/s; ledger and candidate construction add overhead",
        "limits": "Tests this specific joint family only; no free alphabet, unknown transposition key, autokey or variable arithmetic search",
    }
    write_once_json(CYCLE / "joint-plan.json", report)
    print(json.dumps(report, indent=2))
    return report


def run():
    candidates, forms = password_set()
    specification = json.loads((CYCLE / "joint-plan.json").read_text())
    if fingerprint(b"\x00".join(sorted(candidate["password"] for candidate in candidates.values()))) != specification["candidate_set_sha256"]:
        raise ValueError("Planned candidate set changed")
    decoding_path = CYCLE / "joint-decodings.jsonl"
    results_path = CYCLE / "joint-aes.jsonl"
    if results_path.exists() or decoding_path.exists():
        raise ValueError("Existing experiment logs preserved; inspect results or explicitly choose a new cycle")
    root_source = source_record(SOURCES / "salphaseion.html", "dbbi/faed/prime-marker remainder")
    with decoding_path.open("x") as output:
        for parameters, payload, error in forms:
            row = {"source": root_source, "parameters": parameters, "error": error, "plaintext": None if payload is None else base64.b64encode(payload).decode(), "score": None if payload is None else score_plaintext(payload)}
            output.write(json.dumps(row, sort_keys=True) + "\n")
    blobs = {name: parse_salted((ARTIFACTS / f"{name}.b64").read_text()) for name in ("phase32-inner", "salphaseion-small", "cosmic-duality")}
    padding_hits = []
    started = perf_counter()
    with results_path.open("x") as output:
        for identifier, candidate in sorted(candidates.items()):
            row = {"password_sha256": identifier, "password_base64": base64.b64encode(candidate["password"]).decode(), "source": root_source, "provenance": candidate["provenance"], "evaluations": []}
            for target, (salt, ciphertext) in blobs.items():
                for digest in ("md5", "sha256"):
                    key, initialization_vector = evp_bytes_to_key(candidate["password"], salt, digest)
                    evaluation = {"target": target, "cipher": "AES-256-CBC", "kdf_digest": digest, "iterations": 1, "salt": salt.hex(), "key": key.hex(), "iv": initialization_vector.hex(), "padding_valid": False, "plaintext_base64": None, "structural_validity": None, "downstream_validity": None}
                    padded = AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext)
                    try:
                        plaintext = unpad(padded, 16)
                        verification = target_checks(plaintext)
                        if verification["target_match"]:
                            raise RuntimeError("Target match: halt without publishing recovered secret")
                        evaluation.update({"padding_valid": True, "plaintext_base64": base64.b64encode(plaintext).decode(), "plaintext_sha256": fingerprint(plaintext), "score": score_plaintext(plaintext), "structural_validity": verification["structures"], "downstream_validity": verification})
                        padding_hits.append({"password_sha256": identifier, "provenance": candidate["provenance"], **evaluation})
                    except ValueError:
                        pass
                    row["evaluations"].append(evaluation)
            output.write(json.dumps(row, sort_keys=True) + "\n")
    report = {"id": specification["id"], "unique_passwords": len(candidates), "decode_forms": len(forms), "aes_trials": len(candidates) * 6, "padding_hits": len(padding_hits), "padding_hits_by_target": dict(Counter(hit["target"] for hit in padding_hits)), "max_printable_ratio": max((hit["score"]["printable_ratio"] for hit in padding_hits), default=0), "structure_hits": sum(bool(hit["structural_validity"]) for hit in padding_hits), "target_matches": 0, "elapsed_seconds": round(perf_counter() - started, 3), "top_hits": sorted(padding_hits, key=lambda hit: hit["score"]["printable_ratio"], reverse=True)[:15], "status": "INCONCLUSIVE", "result": "No demonstrated target solution from this fixed joint family; high-entropy outputs are not proven failures of every intermediate interpretation."}
    write_once_json(CYCLE / "joint-results.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "top_hits"}, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description="Joint source-grounded transposition/mod9/checkerboard -> AES test")
    parser.add_argument("command", choices=("plan", "run"))
    arguments = parser.parse_args()
    if arguments.command == "plan":
        plan()
    else:
        run()


if __name__ == "__main__":
    main()
