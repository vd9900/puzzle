#!/usr/bin/env python3
import argparse
import json
import random
import re
from collections import Counter
from fractions import Fraction
from math import prod
from time import perf_counter

from tools.analyze_salphaseion import split_segments
from tools.gsmg import ARTIFACTS, SOURCES
from tools.research_common import fingerprint, score_plaintext, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle04"


def key_square(keyword):
    if not re.fullmatch(r"[a-z]*", keyword):
        raise ValueError("Expected lowercase alphabetic keyword")
    return "".join(dict.fromkeys(keyword.replace("j", "i") + "abcdefghiklmnopqrstuvwxyz"))


def bifid(text, square, period, decrypt=True):
    if len(square) != 25 or len(set(square)) != 25 or period < 1:
        raise ValueError("Expected a 25-symbol square and positive period")
    if any(symbol not in square for symbol in text):
        raise ValueError("Every input symbol must belong to the square")
    decoded = []
    for start in range(0, len(text), period):
        chunk = text[start:start + period]
        coordinates = [divmod(square.index(symbol), 5) for symbol in chunk]
        if decrypt:
            stream = [value for coordinate in coordinates for value in coordinate]
            pairs = zip(stream[:len(chunk)], stream[len(chunk):])
        else:
            stream = [row for row, column in coordinates] + [column for row, column in coordinates]
            pairs = zip(stream[::2], stream[1::2])
        decoded.extend(square[row * 5 + column] for row, column in pairs)
    return "".join(decoded)


def prefix_domains(prefix, square, length):
    constraints = {}
    for output_index, symbol in enumerate(prefix):
        row, column = divmod(square.index(symbol), 5)
        for stream_index, wanted in ((output_index, row), (length + output_index, column)):
            source_index, coordinate_axis = divmod(stream_index, 2)
            constraint = constraints.setdefault(source_index, {})
            constraint[coordinate_axis] = wanted
    return {index: [symbol for symbol in "abcdefghi" if all(divmod(square.index(symbol), 5)[axis] == wanted for axis, wanted in axes.items())] for index, axes in sorted(constraints.items())}


def exact_shuffle_probability(text, domains, fixed_prefix=""):
    if text[:len(fixed_prefix)] != fixed_prefix:
        raise ValueError("Fixed prefix differs from source")
    for index, allowed in domains.items():
        if index < len(fixed_prefix) and fixed_prefix[index] not in allowed:
            return Fraction(0, 1)
    counts = Counter(text[len(fixed_prefix):])
    remaining = len(text) - len(fixed_prefix)
    pending = [allowed for index, allowed in domains.items() if index >= len(fixed_prefix)]

    def probability(position, population):
        if position == len(pending):
            return Fraction(1, 1)
        total = Fraction(0, 1)
        for symbol in pending[position]:
            count = counts[symbol]
            if count == 0:
                continue
            counts[symbol] -= 1
            total += Fraction(count, population) * probability(position + 1, population - 1)
            counts[symbol] += 1
        return total

    return probability(0, remaining)


def prefix_match(text, domains):
    return all(text[index] in allowed for index, allowed in domains.items())


def analyze(shuffles=10000):
    segments = split_segments()
    square = key_square(segments["dbbi"])
    source = segments["faed"]
    started = perf_counter()
    plaintext = bifid(source, square, len(source))
    if bifid(plaintext, square, len(source), False) != source:
        raise ValueError("Bifid decode does not round-trip to exact source")
    prefix = "btcseed"
    domains = prefix_domains(prefix, square, len(source))
    controls = []
    for fixed in ("", source[:4]):
        probability = exact_shuffle_probability(source, domains, fixed)
        rng = random.Random(2026093004)
        letters = list(source[len(fixed):])
        hits = 0
        for trial in range(shuffles):
            rng.shuffle(letters)
            shuffled = fixed + "".join(letters)
            hits += prefix_match(shuffled, domains)
        controls.append({"fixed_prefix": fixed, "shuffle_count": shuffles, "seed": 2026093004, "matches": hits, "exact_probability_numerator": probability.numerator, "exact_probability_denominator": probability.denominator, "exact_probability_decimal": float(probability), "expected_matches": float(probability) * shuffles, "null": "Uniformly permuted exact source-symbol multiset, without replacement; fixed prefix excluded from shuffled pool"})
    transcript_path = SOURCES.parent / "evidence/cycle02/_work__chat_transcript.txt"
    transcript = transcript_path.read_text()
    claim = re.search(r'Generated Bifid Key.*?Result:\s*"([a-z]+)"', transcript, re.S)
    first_rows = [symbol for symbol in square if symbol in "abcdefghi"]
    expected_even_alphabet = "".join(square[index] for index in (0, 1, 5, 6))
    if len(source) % 4 == 2 and not set(plaintext[::2]).issubset(set(expected_even_alphabet)):
        raise ValueError("Derived parity constraint unexpectedly fails")
    report = {"id": "C04-BIFID-EVIDENCE", "source_evidence": [source_record(SOURCES / "salphaseion.html", "exact dbbi91 keyword and faed570 ciphertext"), source_record(transcript_path, "2025-06-25 07:49:43 and 15:10:20 creator-unauthenticated community claims")], "search_space": {"square_keys": 1, "periods": [570], "directions": ["decode", "encode round-trip"], "shuffle_nulls": 2, "shuffles_per_null": shuffles, "exact_probability_assignments_upper_bound": prod(len(allowed) for allowed in domains.values())}, "square": square, "period": len(source), "output_sha256": fingerprint(plaintext.encode()), "plaintext": plaintext, "score": score_plaintext(plaintext.encode()), "claimed_full_output_matches_primary_derived": bool(claim and claim.group(1) == plaintext), "prefix": {"observed": plaintext[:7], "domains": domains, "source_letters_at_constrained_positions": {index: source[index] for index in domains}, "sufficient_eight_source_letters": source[:4] + source[len(source) // 2:len(source) // 2 + 4]}, "parity": {"even_offsets_zero_based_alphabet": "".join(sorted(set(plaintext[::2]))), "predicted_even_alphabet": expected_even_alphabet, "odd_offsets_zero_based_alphabet": "".join(sorted(set(plaintext[1::2]))), "explanation": "All input symbols occupy square positions0..8. With even period570, even plaintext positions combine two row coordinates limited0/1; therefore exactly square indices0,1,5,6 are possible. This restriction is forced by input/square, not evidence of a second cipher or null instruction."}, "shuffle_controls": controls, "status": "PROMISING", "result": "Exact source-derived Bifid decode reproduces btcseed prefix and archived full output, but remainder is not natural language or a verified next stage. Fixed-key/fixed-data shuffle probabilities are conditional comparisons, not universal odds after all community searches.", "elapsed_seconds": round(perf_counter() - started, 3), "limits": "No inferred intended plaintext or target key. Prefix depends on eight source characters and chosen source-key/period; extensive uncounted key/period searches and post-selection invalidate the simple1/26^7 claim. Round-trip verifies implementation only."}
    write_once_json(OUTPUT / "bifid-evidence.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "plaintext"}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce source-keyed Bifid claim and quantify its actual conditional prefix evidence")
    parser.add_argument("--shuffles", type=int, default=10000)
    arguments = parser.parse_args()
    if not 0 <= arguments.shuffles <= 100000:
        parser.error("Shuffle count must lie between0 and100000")
    analyze(arguments.shuffles)
