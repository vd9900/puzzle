#!/usr/bin/env python3
import argparse
import itertools
import json
import math
import re
from collections import Counter
from time import perf_counter

from tools.analyze_salphaseion import split_segments
from tools.gsmg import ARTIFACTS, SOURCES, extract_grid
from tools.research_common import CYCLE, fingerprint, score_plaintext, source_record, target_checks, write_once_json


ALPHABETS = {
    "known-checkerboard": "fubcdora/lethingkymvpszjqwx.",
    "hint-phrase": "fubcdoracletingkymvpszjqwx./",
    "matrixsumlist-keyed": "matrixsulbcdefghjknopqvwyz./",
    "plain-alphabet": "abcdefghijklmnopqrstuvwxyz./",
    "salphaseion-keyed": "salpheionbcdfgjkmqrtuvwxyz./",
    "thematrixhasyou-keyed": "themarixsyoubcdfgjklnpqvwz./",
}


def keyed_alphabet(keyword):
    return "".join(dict.fromkeys(keyword.lower() + "abcdefghijklmnopqrstuvwxyz./"))


def mapping_families():
    alphabet = "abcdefghi"
    ordering = "dbifhcega"
    mappings = {}
    for name, letters in (("alphabet", alphabet), ("first-occurrence-dbbi", ordering)):
        for start in (0, 1):
            mappings[f"{name}-from-{start}"] = {letter: str(index + start) for index, letter in enumerate(letters)}
            mappings[f"{name}-reverse-from-{start}"] = {letter: str(8 - index + start) for index, letter in enumerate(letters)}
    a1 = {letter: str(index + 1) for index, letter in enumerate(alphabet)}
    for letter in alphabet:
        mappings[f"a1-zero-{letter}"] = {symbol: "0" if symbol == letter else digit for symbol, digit in a1.items()}
    mappings["a1-zero-prime-values"] = {letter: "0" if int(digit) in (2, 3, 5, 7) else digit for letter, digit in a1.items()}
    mappings["a1-zero-nonprime-values"] = {letter: digit if int(digit) in (2, 3, 5, 7) else "0" for letter, digit in a1.items()}
    return mappings


def decode_board(digits, prefixes, alphabet):
    if len(alphabet) != 28 or len(set(alphabet)) != 28:
        raise ValueError("A complete checkerboard alphabet must contain 28 unique symbols")
    board = dict(zip((str(column) for column in range(10) if column not in prefixes), alphabet[:8]))
    for row, prefix in enumerate(prefixes):
        board.update({str(prefix) + str(column): symbol for column, symbol in enumerate(alphabet[8 + row * 10:18 + row * 10])})
    position = 0
    decoded = []
    while position < len(digits):
        code = digits[position]
        position += 1
        if int(code) in prefixes:
            if position == len(digits):
                raise ValueError("Truncated row prefix")
            code += digits[position]
            position += 1
        decoded.append(board[code])
    return "".join(decoded)


def rectangular_routes(rows, columns):
    coordinates = [(row, column) for row in range(rows) for column in range(columns)]
    yield "row-major", coordinates
    yield "column-major", sorted(coordinates, key=lambda pair: (pair[1], pair[0]))
    yield "row-snake", [(row, column) for row in range(rows) for column in (range(columns) if row % 2 == 0 else range(columns - 1, -1, -1))]
    yield "column-snake", [(row, column) for column in range(columns) for row in (range(rows) if column % 2 == 0 else range(rows - 1, -1, -1))]
    yield "diagonal", sorted(coordinates, key=lambda pair: (pair[0] + pair[1], pair[0]))
    visited = set()
    directions = ((1, 0), (0, 1), (-1, 0), (0, -1))
    row = column = direction = 0
    spiral = []
    for index in range(rows * columns):
        spiral.append((row, column))
        visited.add((row, column))
        next_row, next_column = row + directions[direction][0], column + directions[direction][1]
        if not (0 <= next_row < rows and 0 <= next_column < columns) or (next_row, next_column) in visited:
            direction = (direction + 1) % 4
        row, column = row + directions[direction][0], column + directions[direction][1]
    yield "counterclockwise-spiral", spiral


def experiment_plan():
    mappings = mapping_families()
    board_count = len(mappings) * 45 * len(ALPHABETS) * 2
    route_dimensions = {name: [(width, len(text) // width) for width in range(2, 31) if len(text) % width == 0] for name, text in split_segments().items() if name != "joined"}
    plan = {
        "id": "C02-SAL-COORDINATES", "board_trials": board_count,
        "numeric_mapping_count": len(mappings), "checkerboard_prefix_pairs": 45, "checkerboard_alphabets": list(ALPHABETS),
        "numeric_trials_upper_bound": len(mappings) * 3 * 4,
        "route_dimensions": route_dimensions, "route_trials": sum(len(dimensions) for dimensions in route_dimensions.values()) * 6 * 2,
        "prime_mask_trials": 3 * 2 * 2 * 2,
        "matrix_pair_trials": 2 * 3 * 2,
        "justification": "a1z26 and whole-number decoding already work on adjacent segments; prime/zero hints support small literal zeroing alternatives; known checkerboard and matrixsumlist support constrained coordinate/prefix/matrix-route alternatives. First-occurrence digit mapping is a secondary claim, not a confirmed Bifid square.",
        "excluded": "No arbitrary substitution permutation search, free cipher key search, or blind dictionary; no padded rectangles or manual ciphertext edits",
    }
    write_once_json(CYCLE / "sal-experiment-plan.json", plan)
    print(json.dumps(plan, indent=2))
    return plan


def run_experiments():
    plan = json.loads((CYCLE / "sal-experiment-plan.json").read_text())
    segments = split_segments()
    mappings = mapping_families()
    ledger_path = CYCLE / "sal-experiments.jsonl"
    if ledger_path.exists():
        raise ValueError("Existing complete experiment ledger preserved; read its summary instead of overwriting")
    board_alphabets = {name: keyed_alphabet(keyword) for name, keyword in (("matrixsumlist-keyed", "matrixsumlist"), ("plain-alphabet", ""), ("salphaseion-keyed", "salphaseion"), ("thematrixhasyou-keyed", "thematrixhasyou"))}
    board_alphabets["known-checkerboard"] = ALPHABETS["known-checkerboard"]
    board_alphabets["hint-phrase"] = keyed_alphabet("fubcdoracletingkymvps")
    trials = Counter()
    ranked = []
    started = perf_counter()

    def record(family, segment, transformation, parameters, payload=None, error=None):
        trials[family] += 1
        item = {"id": f"{plan['id']}:{family}:{trials[family]}", "family": family, "source": source_record(SOURCES / "salphaseion.html", segment), "transformation": transformation, "parameters": parameters, "result": "INCONCLUSIVE" if payload is not None else "REJECTED", "error": error}
        if payload is not None:
            validity = target_checks(payload)
            if validity["target_match"]:
                raise RuntimeError("Target match: stop and preserve secret without public logging")
            item.update({"plaintext_latin1": payload.decode("latin-1"), "plaintext_hex": payload.hex(), "sha256": fingerprint(payload), "score": score_plaintext(payload), "structural_validity": validity["structures"], "downstream_validity": validity})
            if len(payload) >= 24:
                ranked.append(item)
        output.write(json.dumps(item, sort_keys=True) + "\n")

    with ledger_path.open("x") as output:
        for segment_name in ("dbbi", "faed"):
            text = segments[segment_name]
            for mapping_name, mapping in mappings.items():
                digits = "".join(mapping[letter] for letter in text)
                for prefixes in itertools.combinations(range(10), 2):
                    for alphabet_name, alphabet in board_alphabets.items():
                        parameters = {"digit_mapping": mapping_name, "mapping": mapping, "prefixes": prefixes, "alphabet_name": alphabet_name, "alphabet": alphabet}
                        try:
                            plaintext = decode_board(digits, prefixes, alphabet).encode()
                            record("checkerboard", segment_name, "letter-to-digit then straddling checkerboard", parameters, plaintext)
                        except ValueError as error:
                            record("checkerboard", segment_name, "letter-to-digit then straddling checkerboard", parameters, error=str(error))
        for segment_name, text in segments.items():
            for mapping_name, mapping in mappings.items():
                digits = "".join(mapping[letter] for letter in text)
                for radix in (9, 10):
                    parameters = {"digit_mapping": mapping_name, "radix": radix}
                    try:
                        number = int(digits, radix)
                        payload = number.to_bytes(max(1, (number.bit_length() + 7) // 8), "big")
                        record("numeric", segment_name, "whole-number radix to big-endian bytes", parameters, payload)
                    except ValueError as error:
                        record("numeric", segment_name, "whole-number radix to big-endian bytes", parameters, error=str(error))
                for width in (2, 3):
                    parameters = {"digit_mapping": mapping_name, "width": width, "radix": 10}
                    if len(digits) % width:
                        record("numeric", segment_name, "fixed-width decimal bytes", parameters, error="Incomplete group; no truncation or padding allowed")
                        continue
                    numbers = [int(digits[index:index + width]) for index in range(0, len(digits), width)]
                    if max(numbers) > 255:
                        record("numeric", segment_name, "fixed-width decimal bytes", parameters, error="Group exceeds byte range")
                    else:
                        record("numeric", segment_name, "fixed-width decimal bytes", parameters, bytes(numbers))
        for segment_name in ("dbbi", "faed"):
            text = segments[segment_name]
            for rows, columns in plan["route_dimensions"][segment_name]:
                for route_name, coordinates in rectangular_routes(rows, columns):
                    for reverse in (False, True):
                        reordered = "".join(text[row * columns + column] for row, column in coordinates)
                        if reverse:
                            reordered = reordered[::-1]
                        number = int(reordered.translate(str.maketrans("abcdefghi", "123456789")))
                        payload = number.to_bytes((number.bit_length() + 7) // 8, "big")
                        record("route", segment_name, "exact rectangle route then adjacent a1 decimal-to-bytes rule", {"rows": rows, "columns": columns, "route": route_name, "reverse": reverse}, payload)
        for segment_name, text in segments.items():
            for basis in ("symbol-value", "one-based-position"):
                values = [ord(letter) - 96 if basis == "symbol-value" else index + 1 for index, letter in enumerate(text)]
                bits = "".join("1" if value >= 2 and all(value % divisor for divisor in range(2, math.isqrt(value) + 1)) else "0" for value in values)
                for invert in (False, True):
                    mapped = bits.translate(str.maketrans("01", "10")) if invert else bits
                    for reverse in (False, True):
                        ordering = mapped[::-1] if reverse else mapped
                        complete = len(ordering) // 8 * 8
                        payload = bytes(int(ordering[offset:offset + 8], 2) for offset in range(0, complete, 8))
                        record("prime-mask", segment_name, "prime/nonprime binary partition -> MSB-first bytes", {"basis": basis, "invert": invert, "reverse": reverse, "trailing_bits": ordering[complete:]}, payload)
        grid = extract_grid(SOURCES / "gsmg-puzzle.png")["matrix"]
        desired = [ord(letter) - 96 for letter in segments["dbbi"]]
        for axis, vectors in (("row", grid), ("column", list(zip(*grid)))):
            for operation in ("and", "xor", "or"):
                numbers = []
                for first, second in itertools.combinations(vectors, 2):
                    numbers.append(sum((left & right) if operation == "and" else (left ^ right) if operation == "xor" else (left | right) for left, right in zip(first, second)))
                for reverse in (False, True):
                    ordered = numbers[::-1] if reverse else numbers
                    parameters = {"axis": axis, "operation": operation, "reverse": reverse, "pair_count": len(ordered), "exact_a1_match": ordered == desired}
                    record("grid-pairs", "dbbi", "14 choose 2 row/column pair population sums", parameters, bytes(ordered))
    ranked.sort(key=lambda item: (bool(item["structural_validity"]), item["score"]["printable_ratio"] >= .9, item["score"]["dictionary_coverage"], item["score"]["language_score"]), reverse=True)
    report = {"id": plan["id"], "trials_by_family": dict(trials), "total_trials": sum(trials.values()), "elapsed_seconds": round(perf_counter() - started, 3), "ledger": str(ledger_path.relative_to(SOURCES.parents[1])), "top_outputs": ranked[:30], "status": "INCONCLUSIVE", "findings": {"simple_pair_substitution_rejected": "faed contains 75 distinct aligned pairs at offset 0; cannot directly encode a bijective 26-letter alphabet with fixed two-symbol units", "grid_triangle_note": "91=14*13/2 supports checking unordered grid-axis pairs; all 12 defined population-sum tests recorded", "scoring_warning": "Checkerboard and route heuristics require independent semantic/downstream validation; text-like symbols are not confirmation"}}
    write_once_json(CYCLE / "sal-experiment-results.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "top_outputs"}, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description="Finite clue-driven SalPhaseIon coordinate/matrix hypotheses")
    parser.add_argument("command", choices=("plan", "run"))
    arguments = parser.parse_args()
    if arguments.command == "plan":
        experiment_plan()
    else:
        run_experiments()


if __name__ == "__main__":
    main()
