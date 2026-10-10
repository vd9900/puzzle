#!/usr/bin/env python3
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb

from tools.analyze_salphaseion import split_segments
from tools.gsmg import ARTIFACTS, SOURCES
from tools.prime_boundary import binary_boundary, extended_markers, special_frames
from tools.prime_markers import is_prime, tokenizations
from tools.research_common import source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle05"


def subsequence_selections(frame, markers):
    if len(markers) > len(frame):
        return
    for omitted in combinations(range(len(frame)), len(frame) - len(markers)):
        selected = [index for index in range(len(frame)) if index not in omitted]
        if "".join(frame[index] for index in selected) == markers:
            yield omitted, selected


def count_shuffled_frames(patterns, ordinary_ones, ordinary_zeros, fixed_offset, fixed_bit):
    length = ordinary_ones + ordinary_zeros + 1
    if not 0 <= fixed_offset < length or fixed_bit not in "01" or not patterns or any(set(pattern) - set("01") for pattern in patterns):
        raise ValueError("Expected binary patterns and one fixed near-white event")

    @lru_cache(maxsize=None)
    def count(position, ones_left, zeros_left, progress):
        if position == length:
            return int(any(matched == len(pattern) for matched, pattern in zip(progress, patterns)))
        total = 0
        options = [(fixed_bit, ones_left, zeros_left)] if position == fixed_offset else []
        if position != fixed_offset:
            if ones_left:
                options.append(("1", ones_left - 1, zeros_left))
            if zeros_left:
                options.append(("0", ones_left, zeros_left - 1))
        for bit, remaining_ones, remaining_zeros in options:
            following = tuple(matched + int(matched < len(pattern) and pattern[matched] == bit) for matched, pattern in zip(progress, patterns))
            total += count(position + 1, remaining_ones, remaining_zeros, following)
        return total

    matched = count(0, ordinary_ones, ordinary_zeros, tuple(0 for pattern in patterns))
    total = comb(ordinary_ones + ordinary_zeros, ordinary_ones)
    return matched, total


def analyze():
    source = split_segments()["dbbi"]
    branches = []
    for mask, tokens in tokenizations(source):
        markers = [entry for entry in tokens if is_prime(entry["position_one_based"])]
        if any(entry["token"] not in ("b", "be") for entry in markers):
            continue
        branches.append({"mask": mask, "logical_tokens": len(tokens), "marker_bits": "".join("1" if entry["token"] == "b" else "0" for entry in markers), "marker_counts": dict(Counter(entry["token"] for entry in markers)), "residual": "".join(entry["token"] for entry in tokens if not is_prime(entry["position_one_based"])), "tokens": tokens})
    results = []
    for near_white_bit, frame, events in special_frames():
        matches = []
        for branch in branches:
            for omitted, selected in subsequence_selections(frame, branch["marker_bits"]):
                byte_indices = [events[index]["spiral_index_zero_based"] // 8 for index in selected]
                matches.append({"mask": branch["mask"], "logical_tokens": branch["logical_tokens"], "omitted_event_ordinals_one_based": [index + 1 for index in omitted], "represented_byte_ordinals_one_based": sorted({index + 1 for index in byte_indices}), "one_event_per_distinct_byte": len(set(byte_indices)) == len(selected), "exact_first_23_bytes": sorted(byte_indices) == list(range(23))})
        fixed_offset = next(index for index, event in enumerate(events) if event["color"] == "near_white")
        counts = Counter(event["color"] for event in events)
        matched, total = count_shuffled_frames(tuple(branch["marker_bits"] for branch in branches), counts["blue"], counts["yellow"], fixed_offset, str(near_white_bit))
        probability = Fraction(matched, total)
        results.append({"near_white_hypothesis_bit": near_white_bit, "frame": frame, "matches": matches, "conditional_shuffle_null": {"fixed_near_white_offset_zero_based": fixed_offset, "ordinary_blue_count": counts["blue"], "ordinary_yellow_count": counts["yellow"], "matched_frames": matched, "total_distinct_frames": total, "probability_numerator": probability.numerator, "probability_denominator": probability.denominator, "probability_decimal": float(probability), "definition": "Uniformly reorder ordinary blue/yellow event colors while fixing near-white position and comparing either of the two observed marker patterns as a subsequence. Does not account for historical selection of marker rule, patterns or image traversal."}})
    boundary = binary_boundary()
    continuation = []
    for near_white_bit, frame, events in special_frames():
        for branch in branches:
            markers = extended_markers(branch["mask"], branch["tokens"], boundary)
            if "".join(entry["bit"] for entry in markers).startswith(frame):
                continuation.append({"mask": branch["mask"], "near_white_hypothesis_bit": near_white_bit, "added_binary_markers": [{name: entry[name] for name in ("position_one_based", "binary_offset_zero_based", "bit")} for entry in markers[:len(frame)] if entry["region"] != "dbbi"]})
    lowercase = range(ord("a"), ord("z") + 1)
    first_bit_ones = sum(bool(code & 4) for code in lowercase)
    second_bit_zeros = sum(not code & 4 for code in lowercase)
    tail_probability = Fraction(first_bit_ones * second_bit_zeros, 26 ** 2)
    report = {"id": "C05-PRIME-SELECTION-CONTROL", "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png"), source_record(SOURCES / "salphaseion.html"), source_record(SOURCES.parent / "evidence/cycle05/fork-_work__prime_host_delta_2026-09-17__RELATORIO.md", "Secondary claim of five selections and branch ambiguity; reproduced locally, not trusted as proof")], "search_space": {"optional_be_tokenizations": 1024, "valid_prime_branches": len(branches), "near_white_interpretations": 2, "subsequence_comparisons": len(branches) * 2 * comb(25, 23), "shuffle_count_method": "Exact memoized binary-subsequence automaton, not Monte Carlo", "binary_tail_character_pairs": 26 ** 2}, "branches": [{name: value for name, value in branch.items() if name != "tokens"} for branch in branches], "frame_comparisons": results, "continuous_counter_matches": continuation, "binary_tail_control": {"offsets_zero_based": [5, 13], "ascii_bit_masks": [4, 4], "required_bits": [1, 0], "uniform_lowercase_first_two_chars_matches": first_bit_ones * second_bit_zeros, "total_char_pairs": 26 ** 2, "probability_decimal": float(tail_probability), "limits": "Illustrative independence control for two lowercase ASCII characters; real words and historically selected boundary are not uniformly random"}, "status": "CONFIRMED", "result": "Five color subsequences reproduce: two L84/mask505 and three L83/mask1017. One-event-per-byte admits one match from each branch, so it does not uniquely select L84. Requiring exactly bytes1..23 additionally selects L84 but is an unsupported extra condition. Continuous-counter full match still uniquely selects L83 within that separate explicit rule.", "limits": "Confirms bounded structural comparisons only. Neither branch nor next-stage key is authenticated. All probabilities are conditional controls, not universal creator-intent odds."}
    write_once_json(OUTPUT / "prime-selection-controls.json", report)
    print(json.dumps({name: value for name, value in report.items() if name != "source_evidence"}, indent=2))
    return report


if __name__ == "__main__":
    analyze()
