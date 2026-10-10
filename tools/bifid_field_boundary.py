#!/usr/bin/env python3
"""Trace whether the inferred 7|8 field boundary survives the Bifid data flow."""

import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.matrix_width_interface import chunks


def dependency_pairs(start, stop):
    """Bifid source-pair indices needed by serialized output[start:stop]."""
    return sorted({offset // 2 for offset in range(start, stop)})


def report():
    segments = split_segments()
    dbbi = segments["dbbi"]
    faed = segments["faed"]
    square = key_square(dbbi)
    output = bifid(faed, square, len(faed))
    rows = chunks(output, 15)
    even_plane = chunks(output[::2], 15)
    odd_plane = chunks(output[1::2], 15)

    boundaries = []
    for row in range(len(rows)):
        start = row * 15
        cut = start + 7
        stop = start + 15
        left_pairs = dependency_pairs(start, cut)
        right_pairs = dependency_pairs(cut, stop)
        overlap = sorted(set(left_pairs) & set(right_pairs))
        split = bool(overlap)
        if split != (cut % 2 == 1):
            raise ValueError("Serialized Bifid boundary parity changed")
        boundaries.append({
            "row_zero_based": row,
            "global_cut_offset": cut,
            "splits_bifid_digraph": split,
            "shared_source_pair_indices": overlap,
        })

    first = boundaries[0]
    pair_index = first["shared_source_pair_indices"][0]
    first_left_pairs = dependency_pairs(0, 7)
    first_right_pairs = dependency_pairs(7, 15)
    first_source_positions = [pair_index, pair_index + len(faed) // 2]
    if rows[0][:7] != "btcseed" or not first["splits_bifid_digraph"]:
        raise ValueError("Expected recognized prefix boundary changed")
    if set(first_left_pairs) & set(first_right_pairs) != {pair_index}:
        raise ValueError("Expected first-row dependency overlap changed")

    split_rows = [entry["row_zero_based"] for entry in boundaries if entry["splits_bifid_digraph"]]
    intact_rows = [entry["row_zero_based"] for entry in boundaries if not entry["splits_bifid_digraph"]]
    if split_rows != list(range(0, 38, 2)) or intact_rows != list(range(1, 38, 2)):
        raise ValueError("Expected alternating boundary behavior changed")

    return {
        "id": "C26-BIFID-FIELD-BOUNDARY",
        "date": "2026-10-02",
        "status": "REJECTED",
        "hypothesis": "The upstream7|8 field boundary propagates through the recovered Bifid transform so btcseed is an independent seven-column downstream field.",
        "invariant": "A propagated field boundary must partition downstream dependency units consistently and must not make the left and right fields depend on the same Bifid source pair.",
        "input": "Exact public FAED570, source-keyed square, full-period Bifid output, and the inferred width15/7|8 rendering",
        "first_row": {
            "rendered": rows[0],
            "left7": rows[0][:7],
            "right8": rows[0][7:],
            "global_cut_offset": first["global_cut_offset"],
            "crossing_output_digraph": output[6:8],
            "shared_source_pair_index": pair_index,
            "shared_faed_offsets": first_source_positions,
            "shared_faed_symbols": [faed[index] for index in first_source_positions],
            "left_source_pair_indices": first_left_pairs,
            "right_source_pair_indices": first_right_pairs,
            "source_pair_overlap": [pair_index],
        },
        "all_rendered_rows": {
            "rows": len(rows),
            "field_widths": [7, 8],
            "split_digraph_boundaries": len(split_rows),
            "between_digraph_boundaries": len(intact_rows),
            "split_rows_zero_based": split_rows,
            "between_rows_zero_based": intact_rows,
            "behavior_alternates_because_rendered_width15_is_odd": True,
        },
        "coordinate_plane_control": {
            "even_plane_shape": [len(even_plane), len(even_plane[0])],
            "odd_plane_shape": [len(odd_plane), len(odd_plane[0])],
            "even_plane_first7": even_plane[0][:7],
            "odd_plane_first7": odd_plane[0][:7],
            "either_plane_first7_is_btcseed": "btcseed" in (even_plane[0][:7], odd_plane[0][:7]),
        },
        "classification": {
            "shared_width15_geometry": "VERIFIED as arithmetic tiling",
            "btcseed_as_serialized_prefix": "VERIFIED",
            "btcseed_as_independent_seven_column_bifid_field": "REJECTED",
            "upstream_7_plus_8_to_downstream_7_plus_8_data_flow": "REJECTED for direct field preservation",
            "unknown_parameterized_consumer": "UNKNOWN",
        },
        "graph_effect": "Delete the direct field-preserving13x(7|8) -> Bifid38x(7|8) edge. Retain width15 as a dimensional coincidence/constraint and btcseed as a serialized prefix, pending an authored cross-field operation.",
        "result": "The first7|8 cut splits output digraph positions6/7 and gives both fields dependencies on FAED pair3 (offsets3 and288). The same cut splits19 rendered rows and falls between digraphs in19 rows. Neither natural19x15 coordinate plane begins with btcseed. The inferred boundary therefore does not propagate as an independent Bifid field.",
        "exact_remaining_unknown": "No source-backed operation maps the upstream rank-sum7/bit-count8 fields to the serialized Bifid output across this dependency-crossing boundary, or names any later receiver for the570-symbol output.",
        "next_test": "Require new authored evidence that fixes a cross-field operation and downstream receiver. Existing public objects supply no further parameter-free data-flow edge.",
        "new_cryptographic_trials": 0,
        "new_trial_inputs": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
