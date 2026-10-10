#!/usr/bin/env python3
"""Audit whether the two width-15 structures form a columnwise data-flow edge."""

import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.prime_boundary import binary_boundary


def chunks(text, width):
    if width < 1 or len(text) % width:
        raise ValueError("Object does not tile at requested width")
    return [text[offset:offset + width] for offset in range(0, len(text), width)]


def first_occurrences(text):
    seen = set()
    result = []
    for offset, symbol in enumerate(text):
        if symbol not in seen:
            seen.add(symbol)
            result.append({
                "symbol": symbol,
                "offset_zero_based": offset,
                "row_zero_based": offset // 7,
                "panel_column_zero_based": offset % 7,
            })
    return result


def report():
    segments = split_segments()
    dbbi = segments["dbbi"]
    faed = segments["faed"]
    boundary = binary_boundary()
    bits = boundary["bits"]
    if boundary["decoded"] != "matrixsumlist":
        raise ValueError("Frozen decoded label changed")

    dbbi_rows = chunks(dbbi, 7)
    bit_rows = chunks(bits, 8)
    joined_rows = [left + right for left, right in zip(dbbi_rows, bit_rows)]
    if len(joined_rows) != 13 or any(len(row) != 15 for row in joined_rows):
        raise ValueError("Frozen13x15 source panel changed")

    square = key_square(dbbi)
    observed = first_occurrences(dbbi)
    observed_symbols = "".join(item["symbol"] for item in observed)
    if observed_symbols != square[:len(observed)] or len(observed) != 9:
        raise ValueError("Source-keyed square derivation changed")
    key_source_columns = sorted({item["panel_column_zero_based"] for item in observed})

    output = bifid(faed, square, len(faed))
    even_plane = output[::2]
    odd_plane = output[1::2]
    faed_columns = [faed[column::15] for column in range(15)]
    paired_output_columns = [
        even_plane[column::15] + odd_plane[column::15]
        for column in range(15)
    ]
    if any(set(column) != set("abcdefghi") for column in faed_columns):
        raise ValueError("A FAED source column no longer contains all nine input symbols")

    dependencies = []
    for column, (source_group, output_group) in enumerate(zip(faed_columns, paired_output_columns)):
        dependencies.append({
            "downstream_group_zero_based": column,
            "local_faed_source_column_zero_based": column,
            "faed_input_alphabet_size": len(set(source_group)),
            "faed_input_alphabet": "".join(sorted(set(source_group))),
            "global_dbbi_key_source_columns_zero_based": key_source_columns,
            "raw_label_bit_source_columns_zero_based": [],
            "output_alphabet_size": len(set(output_group)),
        })

    global_patterns = {
        tuple(item["global_dbbi_key_source_columns_zero_based"])
        for item in dependencies
    }
    exclusive_same_index = sum(
        item["global_dbbi_key_source_columns_zero_based"] == [item["downstream_group_zero_based"]]
        for item in dependencies
    )

    return {
        "id": "C31-MATRIX-BIFID-DEPENDENCY-JOIN",
        "date": "2026-10-02",
        "status": "REJECTED",
        "hypothesis": "The upstream13x15 dbbi-plus-label panel flows column by column into the fifteen dependency-preserving post-Bifid groups.",
        "invariant": "A direct columnwise edge requires downstream group c to depend specifically on upstream panel column c, rather than on a separate FAED column plus one global key dependency shared by every group.",
        "upstream_panel": {
            "shape": [13, 15],
            "dbbi_columns_zero_based": list(range(7)),
            "raw_label_bit_columns_zero_based": list(range(7, 15)),
            "decoded_label": boundary["decoded"],
            "rowwise_join_round_trip": "".join(row[:7] for row in joined_rows) == dbbi and "".join(row[7:] for row in joined_rows) == bits,
        },
        "square_dependency": {
            "observed_first_occurrence_symbols": observed_symbols,
            "observed_first_occurrences": observed,
            "dbbi_panel_columns_contributing_first_occurrences_zero_based": key_source_columns,
            "dbbi_panel_columns_without_first_occurrence_zero_based": sorted(set(range(7)) - set(key_source_columns)),
            "fixed_alphabet_supplement_symbols": square[len(observed):],
            "fixed_alphabet_supplement_count": len(square) - len(observed),
        },
        "downstream_dependency_groups": {
            "local_faed_source_columns_zero_based": [
                item["local_faed_source_column_zero_based"] for item in dependencies
            ],
            "faed_input_alphabet_in_every_group": "abcdefghi",
            "global_dbbi_key_source_columns_in_every_group_zero_based": key_source_columns,
            "raw_label_bit_source_columns_in_every_group_zero_based": [],
            "output_alphabet_sizes_by_group": [item["output_alphabet_size"] for item in dependencies],
        },
        "dependency_summary": {
            "groups": len(dependencies),
            "groups_with_all_nine_faed_input_symbols": sum(item["faed_input_alphabet_size"] == 9 for item in dependencies),
            "distinct_global_dbbi_key_column_patterns": len(global_patterns),
            "shared_global_dbbi_key_columns_zero_based": key_source_columns,
            "groups_with_any_raw_label_bit_dependency": sum(bool(item["raw_label_bit_source_columns_zero_based"]) for item in dependencies),
            "groups_with_exclusive_same_index_upstream_panel_dependency": exclusive_same_index,
            "groups_with_exact_local_faed_column_lineage": sum(item["local_faed_source_column_zero_based"] == index for index, item in enumerate(dependencies)),
        },
        "classification": {
            "rowwise_13x15_join_geometry": "VERIFIED",
            "dbbi_to_global_square_to_all_bifid_groups": "VERIFIED mechanically",
            "faed_column_c_to_paired_bifid_group_c": "VERIFIED mechanically",
            "raw_matrixsumlist_bits_to_bifid_transform": "REJECTED as a data dependency in the recovered transform",
            "upstream_panel_column_c_to_downstream_group_c": "REJECTED: zero groups have exclusive same-index panel lineage",
            "decoded_matrixsumlist_label_as_operation": "UNKNOWN: it may instruct a later operation, but the operation and receiver are not specified",
        },
        "graph_effect": "Separate shared width from data flow. dbbi91 supplies one global square, FAED supplies fifteen local source columns, and raw label bits only decode the instruction name. Any matrixsumlist-to-Bifid edge must be a semantic control edge added after decoding, not inherited columnwise data.",
        "exact_remaining_unknown": "The public objects do not specify what matrix is to be summed, the symbol weights, or the receiver of a resulting list. Width15 and source lineage alone cannot supply those semantics.",
        "next_test": "No further parameter-free structural operation is licensed. Require source evidence binding matrixsumlist to the paired Bifid planes and defining either weights or a non-cryptographic receiver invariant.",
        "numeric_sum_vectors_calculated": 0,
        "numeric_mapping_trials": 0,
        "candidate_lists_generated": 0,
        "mnemonic_words_generated": 0,
        "checksum_tests": 0,
        "seed_derivations": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
