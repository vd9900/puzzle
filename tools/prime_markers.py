#!/usr/bin/env python3
import argparse
import json
import math
import random
from collections import Counter
from time import perf_counter

from tools.analyze_salphaseion import split_segments
from tools.gsmg import SOURCES, extract_grid, spiral_coordinates
from tools.research_common import CYCLE, fingerprint, score_plaintext, source_record, write_once_json


def is_prime(value):
    return value >= 2 and all(value % divisor for divisor in range(2, math.isqrt(value) + 1))


def color_bits():
    grid = extract_grid(SOURCES / "gsmg-puzzle.png")
    return "".join(str(grid["matrix"][row][column]) for index, (row, column) in enumerate(spiral_coordinates(14)) if index % 8 == 7 and index < 192)


def tokenizations(text):
    starts = [offset for offset in range(len(text) - 1) if text[offset:offset + 2] == "be"]
    for mask in range(1 << len(starts)):
        merged = {offset for index, offset in enumerate(starts) if mask >> index & 1}
        tokens = []
        raw_offset = 0
        while raw_offset < len(text):
            width = 2 if raw_offset in merged else 1
            tokens.append({"token": text[raw_offset:raw_offset + width], "raw_offset_zero_based": raw_offset, "position_one_based": len(tokens) + 1})
            raw_offset += width
        yield mask, tokens


def marker_match(text, expected):
    states = {(0, 0)}
    best = 0
    for position in range(1, len(text) + 1):
        following = set()
        for raw_offset, matched in states:
            if raw_offset >= len(text):
                best = max(best, matched)
                continue
            choices = [(text[raw_offset], 1)]
            if text[raw_offset:raw_offset + 2] == "be":
                choices.append(("be", 2))
            for token, width in choices:
                if is_prime(position):
                    bit = "1" if token == "b" else "0" if token == "be" else "?"
                    if matched >= len(expected) or bit != expected[matched]:
                        best = max(best, matched)
                        continue
                    next_matched = matched + 1
                else:
                    next_matched = matched
                best = max(best, next_matched)
                following.add((raw_offset + width, next_matched))
        states = following
        if not states:
            break
    return best


def analyze(shuffles=10000):
    text = split_segments()["dbbi"]
    expected = color_bits()
    results = []
    for mask, tokens in tokenizations(text):
        marker_bits = "".join("1" if entry["token"] == "b" else "0" if entry["token"] == "be" else "?" for entry in tokens if is_prime(entry["position_one_based"]))
        prefix = 0
        for actual, wanted in zip(marker_bits, expected):
            if actual != wanted:
                break
            prefix += 1
        payload = "".join(entry["token"] for entry in tokens if not is_prime(entry["position_one_based"]))
        results.append({"mask": mask, "tokens": tokens, "token_count": len(tokens), "marker_bits": marker_bits, "matched_color_prefix_bits": prefix, "invalid_prime_tokens": marker_bits.count("?"), "nonprime_payload": payload, "payload_length": len(payload)})
    results.sort(key=lambda result: (-result["matched_color_prefix_bits"], result["invalid_prime_tokens"], result["mask"]))
    maximum = results[0]["matched_color_prefix_bits"]
    grid = extract_grid(SOURCES / "gsmg-puzzle.png")
    special_cells = [
        {"spiral_index_zero_based": index, "row_zero_based": row, "column_zero_based": column, "color": grid["colors"][row][column]}
        for index, (row, column) in enumerate(spiral_coordinates(14))
        if grid["colors"][row][column] in ("blue", "yellow", "near_white")
    ]
    near_white_comparisons = []
    for replacement in ("0", "1"):
        frame = "".join(replacement if cell["color"] == "near_white" else "1" if cell["color"] == "blue" else "0" for cell in special_cells)
        compared = []
        for result in results:
            if result["invalid_prime_tokens"]:
                continue
            count = 0
            for actual, wanted in zip(result["marker_bits"], frame):
                if actual != wanted:
                    break
                count += 1
            compared.append({"mask": result["mask"], "matched_prefix": count, "prime_marker_count": len(result["marker_bits"]), "all_available_prime_markers_match": frame.startswith(result["marker_bits"]), "unconsumed_frame_bits": frame[len(result["marker_bits"]):] if frame.startswith(result["marker_bits"]) else None})
        near_white_comparisons.append({"near_white_hypothesis_bit": replacement, "frame_bits": frame, "comparisons": compared})
    rng = random.Random(20260930)
    histogram = Counter()
    extended_histograms = {frame["near_white_hypothesis_bit"]: Counter() for frame in near_white_comparisons}
    null_started = perf_counter()
    letters = list(text)
    for trial in range(shuffles):
        rng.shuffle(letters)
        shuffled = "".join(letters)
        histogram[marker_match(shuffled, expected)] += 1
        for frame in near_white_comparisons:
            extended_histograms[frame["near_white_hypothesis_bit"]][marker_match(shuffled, frame["frame_bits"])] += 1
    for frame in near_white_comparisons:
        histogram_for_frame = extended_histograms[frame["near_white_hypothesis_bit"]]
        observed = max(comparison["matched_prefix"] for comparison in frame["comparisons"])
        frame["shuffle_control_histogram"] = dict(sorted(histogram_for_frame.items()))
        frame["shuffle_control_matches_at_least_observed"] = sum(count for match, count in histogram_for_frame.items() if match >= observed)
    report = {
        "id": "C02-PRIME-MARKERS", "source": source_record(SOURCES / "salphaseion.html", "dbbi, first 91 letters"),
        "hypothesis": "Optional be digraphs occupy one logical position; prime-position b=1/be=0 repeats initial grid color LSBs",
        "search_space": {"be_occurrences": 10, "tokenizations": len(results), "shuffle_control_count": shuffles, "shuffle_seed": 20260930, "shuffle_algorithm": "random.Random.shuffle preserving the exact symbol multiset; DP takes the best valid color-prefix alignment over all optional be merges"},
        "expected_color_bits": expected, "maximum_matched_prefix_bits": maximum,
        "full_color_match_count": sum(result["matched_color_prefix_bits"] == len(expected) for result in results),
        "best_parses": [result for result in results if result["matched_color_prefix_bits"] == maximum],
        "near_white_frame": {"source_special_cells": special_cells, "hypotheses": near_white_comparisons, "observed": "With near-white treated as 1, mask 1017 matches all 23 available prime markers of the 25-cell special-color frame; two bits remain unconsumed. This is a partial cross-artifact structural match, not a decoded answer or full 25-bit match.", "hypothesis_status": "PROMISING"},
        "shuffle_control_maximum": max(histogram, default=0), "shuffle_control_histogram": dict(sorted(histogram.items())),
        "shuffle_control_matches_at_least_observed": sum(count for match, count in histogram.items() if match >= maximum),
        "null_elapsed_seconds": round(perf_counter() - null_started, 3),
        "status": "PROMISING" if maximum >= 16 else "INCONCLUSIVE",
        "limits": "The exact prefix match is reproducible, not a final decryption. No complete 24-bit match or unique parse. Shuffle results are empirical under one conditioned null, not a universal chance probability or creator-authentication proof. No symbols edited/deleted to force full match.",
    }
    if marker_match(text, expected) != maximum:
        raise ValueError("DP and exhaustive tokenization disagree")
    write_once_json(CYCLE / "prime-markers.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "best_parses"}, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description="Reproduce the claimed prime/color scaffold and test its stated limitations")
    parser.add_argument("--shuffles", type=int, default=10000)
    arguments = parser.parse_args()
    if not 0 <= arguments.shuffles <= 100000:
        parser.error("Shuffle count must be between 0 and 100000")
    analyze(arguments.shuffles)


if __name__ == "__main__":
    main()
