#!/usr/bin/env python3
import json

from tools.gsmg import SOURCES
from tools.image_sum_derivation import image_matrices, residual
from tools.analyze_salphaseion import split_segments
from tools.salphaseion_experiments import decode_board
from tools.research_common import fingerprint, source_record, write_once_json
from tools.zeroed_residual import OUTPUT


def ranked_alphabets():
    reduced = dict(image_matrices())["omit-near-white-row-column"]
    rows = list(map(sum, reduced))
    columns = list(map(sum, zip(*reduced)))
    alphabets = {}
    letters = "abcdefghijklmnopqrstuvwxyz"
    for row_reverse in (False, True):
        for column_reverse in (False, True):
            row_values = rows[::-1] if row_reverse else rows
            column_values = columns[::-1] if column_reverse else columns
            for axis_order, values in (("rows-then-columns", row_values + column_values), ("columns-then-rows", column_values + row_values)):
                for descending in (False, True):
                    order = sorted(range(26), key=lambda index: ((-1 if descending else 1) * values[index], index))
                    rank = [0] * 26
                    for position, index in enumerate(order):
                        rank[index] = position
                    for interpretation, indices in (("sorted-original-indices", order), ("stable-rank-vector", rank)):
                        alphabet = "".join(letters[index] for index in indices) + "/."
                        provenance = {"matrix": "13x13 reduced image, unchanged source", "row_reverse": row_reverse, "column_reverse": column_reverse, "axis_order": axis_order, "sums": values, "descending": descending, "ties": "original index ascending", "interpretation": interpretation, "punctuation": "append /. as explicitly observed checkerboard symbols"}
                        alphabets.setdefault(alphabet, []).append(provenance)
    return alphabets


def derive_candidates():
    alphabets = ranked_alphabets()
    decoded_forms = []
    passwords = {}
    segments = {"prime-residual60": residual(), "faed570": split_segments()["faed"]}
    for segment, text in segments.items():
        for zeroed in ("none-a0", "none-a1") + tuple("abcdefghi"):
            mapping = {symbol: str(index if zeroed == "none-a0" else index + 1) for index, symbol in enumerate("abcdefghi")}
            if zeroed in "abcdefghi":
                mapping[zeroed] = "0"
            for reverse in (False, True):
                digits = "".join(mapping[symbol] for symbol in text)
                if reverse:
                    digits = digits[::-1]
                for alphabet, provenance in alphabets.items():
                    parameters = {"segment": segment, "zero_rule": zeroed, "reverse_digits": reverse, "alphabet": alphabet, "alphabet_provenance": provenance, "prefixes": [1, 4]}
                    form = {"parameters": parameters, "decoded": None, "error": None}
                    try:
                        form["decoded"] = decode_board(digits, (1, 4), alphabet)
                    except ValueError as error:
                        form["error"] = str(error)
                    decoded_forms.append(form)
                    if form["decoded"] is None:
                        continue
                    payload = form["decoded"].encode()
                    for representation, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
                        candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                        candidate["provenance"].append(parameters | {"representation": representation})
    return alphabets, decoded_forms, passwords


def plan():
    alphabets, decoded_forms, passwords = derive_candidates()
    report = {"id": "C03-NEXT-RANKED-ALPHABET", "status": "UNTESTED", "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png"), source_record(SOURCES / "salphaseion.html"), source_record(OUTPUT / "prime-boundary.json")], "hypothesis": "matrixsumlist produces a 26-letter permutation for a checkerboard, rather than a password or additive mod9 key", "justification": "Removing actual anomaly axes gives 13x13 matrix; 13 row sums+13 column sums supply exactly26 entries, matching26-letter lastwordsbeforearchichoice clue. Stable numeric ranking can map repeated sums to a complete permutation. Its cipher/key role remains unverified.", "search_space": {"numeric_order_forms": 32, "unique_alphabets": len(alphabets), "segments": 2, "digit_rules": 11, "directions": 2, "decode_forms": len(decoded_forms), "parse_failures": sum(form["error"] is not None for form in decoded_forms), "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 3), "gate": "Recognized independently supported next-stage structure or exact scoped address; inspect small-blob hits as bounded raw-key pairs", "limits": "Plan only, no AES executed; numeric list may not be an alphabet. Ties use fixed original order, no 26! search, arbitrary key, automatic hill climbing or tail repair.", "alphabets": alphabets, "forms": decoded_forms, "passwords": passwords}
    write_once_json(OUTPUT / "next-ranked-alphabet-plan.json", report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("alphabets", "forms", "passwords")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
