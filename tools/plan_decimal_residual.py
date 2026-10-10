#!/usr/bin/env python3
import base64
import json

from tools.analyze_salphaseion import split_segments
from tools.image_sum_derivation import residual
from tools.research_common import fingerprint, score_plaintext, source_record, write_once_json
from tools.gsmg import SOURCES
from tools.zeroed_residual import OUTPUT


def forms():
    segments = {"prime-residual60": residual(), "faed570": split_segments()["faed"]}
    for segment, text in segments.items():
        for ordering in ("abcdefghi", "dbifhcega"):
            for start in (0, 1):
                for zeroed_symbol in ("none",) + tuple("abcdefghi"):
                    mapping = {symbol: str(index + start) for index, symbol in enumerate(ordering)}
                    if zeroed_symbol != "none":
                        mapping[zeroed_symbol] = "0"
                    for reverse in (False, True):
                        digits = "".join(mapping[symbol] for symbol in text)
                        if reverse:
                            digits = digits[::-1]
                        number = int(digits, 10)
                        payload = number.to_bytes(max(1, (number.bit_length() + 7) // 8), "big")
                        yield {"parameters": {"segment": segment, "ordering": ordering, "first_digit": start, "zeroed_symbol": zeroed_symbol, "reverse_digits": reverse, "radix": 10, "byte_order": "big", "leading_zero_policy": "Minimal integer bytes, exactly as adjacent solved z-segments; no recovered padding invented"}, "digits": digits, "decoded_base64": base64.b64encode(payload).decode(), "score": score_plaintext(payload)}


def passwords_from_forms(decoded_forms):
    passwords = {}
    for form in decoded_forms:
        payload = base64.b64decode(form["decoded_base64"], validate=True)
        materials = {"decoded-bytes": payload, "decimal-digits-ascii": form["digits"].encode(), "decoded-hex-ascii": payload.hex().encode()}
        for material_name, material in materials.items():
            for representation, password in (("raw", material), ("sha256-lowerhex", fingerprint(material).encode()), ("sha256-raw", bytes.fromhex(fingerprint(material)))):
                candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                candidate["provenance"].append(form["parameters"] | {"material": material_name, "representation": representation})
    return passwords


def plan():
    decoded_forms = list(forms())
    passwords = passwords_from_forms(decoded_forms)
    report = {"id": "C03-NEXT-DECIMAL-RESIDUAL", "source_evidence": [source_record(SOURCES / "salphaseion.html", "a-i segments adjacent to independently decoded decimal integer -> big-endian byte z-regions"), source_record(OUTPUT / "prime-boundary.json")], "status": "UNTESTED", "reasoning": "Adjacent z-regions already use a1/o0 decimal-to-byte conversion. Apply that established family to the unchanged frame-selected residual and faed, including a finite literal zeroing alternative. Prior base9/mod9/coordinate trials do not cover exact radix10 on this selected residual.", "search_space": {"segments": 2, "digit_orders": 2, "zero_or_one_based": 2, "zero_choices_including_none": 10, "directions": 2, "decode_forms": len(decoded_forms), "material_representations": 3, "password_hash_representations": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 3), "throughput_basis": "Conservative 50000 trials/sec measured in cycle02; excludes candidate generation/I/O/scoring", "gate": "Recognized independent downstream structure or exact scoped-address match; small blobs additionally checked as two adjacent raw keys with <=15 metadata bytes", "limits": "Decoding/material plan only; no AES trials run here. No free substitution/columnar key search, truncation, tail repair, data edit or unbounded password dictionary. Score is recorded, not treated as a correctness oracle.", "forms": decoded_forms, "passwords": passwords}
    write_once_json(OUTPUT / "next-decimal-residual-plan.json", report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("forms", "passwords")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
