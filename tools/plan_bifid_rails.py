#!/usr/bin/env python3
import base64
import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS, SOURCES
from tools.research_common import fingerprint, score_plaintext, source_record, target_checks, write_once_json


OUTPUT = ARTIFACTS / "cycle05"


def coordinate_rails(source, square):
    if not source or len(source) % 2:
        raise ValueError("Full-period coordinate rails require a nonempty even-length input")
    plaintext = bifid(source, square, len(source))
    source_coordinates = [divmod(square.index(symbol), 5) for symbol in source]
    midpoint = len(source) // 2
    rails = {}
    for name, parity, axis, radix in (("binary-row", 0, 0, 2), ("quinary-column", 1, 1, 5)):
        coordinates = [divmod(square.index(symbol), 5) for symbol in plaintext[parity::2]]
        expected = [(first[axis], second[axis]) for first, second in zip(source_coordinates[:midpoint], source_coordinates[midpoint:])]
        if coordinates != expected or any(value >= radix for pair in coordinates for value in pair):
            raise ValueError("Rail coordinates do not match their source halves/radix")
        rails[name] = {"coordinates": coordinates, "radix": radix, "parity_zero_based": parity}
    return rails


def serialize_digits(digits, radix, representation):
    if radix not in (2, 5) or not digits or any(value < 0 or value >= radix for value in digits):
        raise ValueError("Expected a nonempty binary/quinary digit stream")
    if representation == "ascii-digits":
        return "".join(str(value) for value in digits).encode("ascii")
    if representation == "raw-digit-bytes":
        return bytes(digits)
    if representation == "minimal-integer-big-endian":
        number = int("".join(str(value) for value in digits), radix)
        return number.to_bytes((number.bit_length() + 7) // 8, "big")
    if representation == "strict-byte-chunks":
        width = 8 if radix == 2 else 3
        if len(digits) % width:
            raise ValueError("Incomplete byte chunk; no tail dropping or invented padding")
        return bytes(int("".join(str(value) for value in digits[start:start + width]), radix) for start in range(0, len(digits), width))
    raise ValueError("Unknown rail serialization")


def derive_candidates():
    segments = split_segments()
    rails = coordinate_rails(segments["faed"], key_square(segments["dbbi"]))
    forms = []
    passwords = {}
    for name, rail in rails.items():
        for coordinate_order in ("row-column", "column-row"):
            digits = [value for pair in rail["coordinates"] for value in (pair if coordinate_order == "row-column" else pair[::-1])]
            for reverse in (False, True):
                ordered = digits[::-1] if reverse else digits
                for representation in ("ascii-digits", "raw-digit-bytes", "minimal-integer-big-endian", "strict-byte-chunks"):
                    parameters = {"rail": name, "radix": rail["radix"], "coordinate_order": coordinate_order, "reverse_digits": reverse, "serialization": representation, "digit_count": len(ordered), "integer_leading_zero_policy": "Minimal integer bytes only; no invented leading zeros", "chunk_policy": "Binary8/quinary3 digits per byte, exact divisibility required"}
                    form = {"parameters": parameters, "digits": "".join(str(value) for value in ordered), "decoded_base64": None, "error": None, "score": None, "downstream_validity": None}
                    try:
                        payload = serialize_digits(ordered, rail["radix"], representation)
                    except ValueError as error:
                        form["error"] = str(error)
                        forms.append(form)
                        continue
                    validity = target_checks(payload)
                    if validity["target_match"]:
                        raise RuntimeError("Scoped target match; halt before logging candidate material")
                    form.update({"decoded_base64": base64.b64encode(payload).decode(), "score": score_plaintext(payload), "downstream_validity": validity})
                    forms.append(form)
                    for transform, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
                        candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                        candidate["provenance"].append(parameters | {"password_transform": transform})
    return forms, passwords


def plan():
    forms, passwords = derive_candidates()
    report = {"id": "C05-BIFID-RAILS", "status": "UNTESTED", "source_evidence": [source_record(SOURCES / "salphaseion.html", "Exact dbbi91 keyword/faed570; no source edits"), source_record(ARTIFACTS / "cycle04/bifid-evidence.json", "Forced even-parity alphabet bcde")], "hypothesis": "Source-keyed Bifid separates binary row coordinates from quinary column coordinates, which may encode bytes rather than direct English", "justification": "Bifid inversion proves even plaintext coordinates are paired source-row halves and odd coordinates paired source-column halves. The first nine square positions restrict rows to0/1. Minimal big-endian integer decoding already works on neighboring z-segments; strict packing and ASCII/raw digits are explicit alternative serializations, not proven instructions.", "invariant": "All coordinates are retained; each rail independently reconstructs its exact source-coordinate halves. No truncation, bit offset sweep, square permutations or guessed tail padding.", "search_space": {"rails": 2, "coordinate_orders": 2, "directions": 2, "serializations": 4, "decode_forms": len(forms), "decode_errors": sum(form["error"] is not None for form in forms), "password_transforms": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 4), "gate": "Recognized independently justified next-stage structure or exact scoped Bitcoin target; adjacent raw-key pairs checked separately", "limits": "Rail factorization is mathematically forced and is not itself evidence of another intended layer. Big-integer leading zeros are a stated interpretation. No private-key keyspace search or production network access.", "forms": forms, "passwords": passwords}
    write_once_json(OUTPUT / "bifid-rails-plan.json", report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("forms", "passwords")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
