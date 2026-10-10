#!/usr/bin/env python3
import json
import random
from collections import Counter
from fractions import Fraction

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS, SOURCES
from tools.prime_markers import is_prime, tokenizations
from tools.research_common import fingerprint, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle08"
SHUFFLES = 10000
SEED = 2026093008


def branch_templates():
    source = split_segments()["dbbi"]
    branches = {}
    for mask, tokens in tokenizations(source):
        if mask not in (505, 1017):
            continue
        template = [entry["token"] if is_prime(entry["position_one_based"]) else None for entry in tokens]
        residual = [entry["token"] for entry in tokens if not is_prime(entry["position_one_based"])]
        if any(len(symbol) != 1 for symbol in residual) or rebuild(template, residual) != source:
            raise ValueError("Prime template and residual must preserve every source symbol")
        branches[mask] = (template, residual)
    if set(branches) != {505, 1017}:
        raise ValueError("Expected exactly the two documented prime branches")
    return branches


def rebuild(template, residual):
    if sum(symbol is None for symbol in template) != len(residual):
        raise ValueError("Residual length differs from the fixed prime template")
    pending = iter(residual)
    return "".join(next(pending) if symbol is None else symbol for symbol in template)


def prefix_for_source_key(source, keyword, width=7):
    if len(source) % 2 or len(source) < width * 2:
        raise ValueError("Expected the existing even-length full-period Bifid source")
    square = key_square(keyword)
    midpoint = len(source) // 2
    first_coordinates = [coordinate for symbol in source[:(width + 1) // 2] for coordinate in divmod(square.index(symbol), 5)]
    second_coordinates = [coordinate for symbol in source[midpoint:midpoint + (width + 1) // 2] for coordinate in divmod(square.index(symbol), 5)]
    return "".join(square[row * 5 + column] for row, column in zip(first_coordinates[:width], second_coordinates[:width]))


def control(shuffles=SHUFFLES, seed=SEED):
    segments = split_segments()
    source = segments["faed"]
    original_square = key_square(segments["dbbi"])
    if prefix_for_source_key(source, segments["dbbi"]) != bifid(source, original_square, 570)[:7]:
        raise ValueError("The bounded prefix check differs from exact full-period Bifid")
    reports = []
    for mask, (template, residual) in branch_templates().items():
        generator = random.Random(seed + mask)
        letters = residual[:]
        prefixes = Counter()
        squares = Counter()
        prefix_matches = 0
        source_square_matches = 0
        nonoriginal_prefix_matches = 0
        for trial in range(shuffles):
            generator.shuffle(letters)
            candidate = rebuild(template, letters)
            square = key_square(candidate)
            prefix = prefix_for_source_key(source, candidate)
            squares[square] += 1
            prefixes[prefix] += 1
            match = prefix == "btcseed"
            prefix_matches += match
            source_square_matches += square == original_square
            nonoriginal_prefix_matches += match and square != original_square
        reports.append({
            "mask": mask, "logical_tokens": len(template), "residual_symbols": len(residual),
            "residual_multiset": dict(sorted(Counter(residual).items())),
            "shuffles": shuffles, "seed": seed + mask, "distinct_source_keyed_squares": len(squares),
            "btcseed_prefix_matches": prefix_matches, "original_square_matches": source_square_matches,
            "nonoriginal_square_prefix_matches": nonoriginal_prefix_matches,
            "observed_prefix_match_frequency": prefix_matches / shuffles,
            "add_one_monte_carlo_tail_estimate": (prefix_matches + 1) / (shuffles + 1),
            "distinct_prefixes": len(prefixes),
            "null": "Uniformly permuted exact residual-symbol multiset, reinserted into fixed logical nonprime positions; preserve every prime b/be token, color order, total source length and symbol counts; faed source held fixed",
            "limits": "Conditional Monte Carlo control, not an exact probability or a multiple-hypothesis corrected global p-value; alternative-key controls never become password candidates and no AES is run",
        })
    unconstrained = Fraction(8, 362880)
    return {
        "id": "C08-PRIME-CONDITIONED-BIFID-CONTROL", "status": "CONFIRMED",
        "source_evidence": [source_record(SOURCES / "salphaseion.html"), source_record(ARTIFACTS / "cycle04/bifid-square-control.json"), source_record(ARTIFACTS / "cycle03/prime-boundary.json")],
        "original_prefix_reproduced": prefix_for_source_key(source, segments["dbbi"]) == "btcseed",
        "controls": reports, "unconstrained_square_fraction": {"numerator": unconstrained.numerator, "denominator": unconstrained.denominator, "meaning": "Earlier8 prefix-producing first-nine permutations among9!; not the appropriate conditional prime-grammar null"},
        "new_passwords": 0, "new_aes_trials": 0,
        "result": "Quantifies dependence between the prime/color template and the source-keyed Bifid prefix without optimizing plaintext or selecting a password. Confirmation refers to the reproducible control, not creator intent or a reward key",
    }


def main():
    report = control()
    write_once_json(OUTPUT / "prime-conditioned-bifid-control.json", report)
    print(json.dumps({name: value for name, value in report.items() if name != "source_evidence"}, indent=2))


if __name__ == "__main__":
    main()
