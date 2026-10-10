#!/usr/bin/env python3
"""Test the fixed matrix-to-sum-list interface without downstream execution."""

import json

from tools.analyze_salphaseion import split_segments
from tools.matrix_width_interface import chunks, report as width_report
from tools.prime_boundary import binary_boundary
from tools.gsmg import ARTIFACTS


COLUMN_SUMS = [69, 58, 49, 59, 53, 74, 60, 0, 13, 13, 7, 6, 6, 3, 8]
ROW_SUMS = [32, 33, 36, 47, 34, 48, 34, 33, 31, 41, 32, 48, 29]


def report():
    segments = split_segments()
    dbbi = segments["dbbi"]
    faed = segments["faed"]
    boundary = binary_boundary()
    width = width_report()
    join = json.loads((ARTIFACTS / "cycle23/residual-frame-join.json").read_text())

    dbbi_rows = chunks(dbbi, 7)
    bit_rows = chunks(boundary["bits"], 8)
    matrix = [
        [ord(symbol) - ord("a") + 1 for symbol in left] + [int(bit) for bit in right]
        for left, right in zip(dbbi_rows, bit_rows)
    ]
    row_sums = [sum(row) for row in matrix]
    column_sums = [sum(row[column] for row in matrix) for column in range(15)]
    transpose_row_sums = [sum(column) for column in zip(*matrix)]
    if row_sums != ROW_SUMS or column_sums != COLUMN_SUMS or transpose_row_sums != column_sums:
        raise ValueError("Fixed typed matrix sums changed")
    if sum(row_sums) != sum(column_sums):
        raise ValueError("Row and column sum conservation failed")

    accounting = join["information_accounting"]
    prime_raw_cells = accounting["semantic_one_tokens"] + 2 * accounting["semantic_zero_tokens_expanding_to_be"]
    ownership = {
        "residual_dbbi_cells": accounting["residual_tokens"],
        "first23_event_expanded_dbbi_cells": prime_raw_cells,
        "final2_event_cells_in_raw_label": accounting["final_binary_region_labels_kept_separate"],
        "other_raw_label_cells": len(boundary["bits"]) - accounting["final_binary_region_labels_kept_separate"],
    }
    if sum(ownership.values()) != 195 or ownership["residual_dbbi_cells"] + ownership["first23_event_expanded_dbbi_cells"] != 91:
        raise ValueError("Panel ownership does not close")

    downstream_shapes = {
        "faed": [38, 15],
        "faed_upper_half": [19, 15],
        "faed_lower_half": [19, 15],
        "bifid_even_coordinate_plane": width["faed_bifid_interface"]["even_coordinate_plane_shape"],
        "bifid_odd_coordinate_plane": width["faed_bifid_interface"]["odd_coordinate_plane_shape"],
    }
    if any(shape[1] != len(column_sums) for shape in downstream_shapes.values()):
        raise ValueError("The fixed sum list does not align to every downstream column domain")
    if any(len(row_sums) in shape for shape in downstream_shapes.values()):
        raise ValueError("The competing 13-value direction unexpectedly matches a downstream axis")

    return {
        "id": "C24-MATRIX-SUM-INTERFACE",
        "date": "2026-10-02",
        "status": "PROMISING",
        "hypothesis": "matrixsumlist names a typed interface: sum the13 rows of the fixed13x15 dbbi-plus-raw-label panel to obtain one value for each of the15 aligned faed/Bifid columns.",
        "preconditions": [
            "Use only the exact13x15 layout established by C24-MATRIX-WIDTH-INTERFACE.",
            "Interpret dbbi a through i as1 through9, following the page-adjacent decimal/A1Z26 convention.",
            "Retain the raw label's established binary type a=0 and b=1.",
            "Do not apply the resulting list to any downstream object.",
        ],
        "input": "The exact13x15 public panel and fixed downstream15-column matrix types",
        "operation": "Sum each of the15 columns across all13 rows; transpose-equivalently, sum each row of the15x13 orientation.",
        "observed": {
            "matrix_shape": [13, 15],
            "column_sum_list": column_sums,
            "column_sum_count": len(column_sums),
            "row_sum_list": row_sums,
            "row_sum_count": len(row_sums),
            "conserved_total": sum(column_sums),
            "transpose_invariant": transpose_row_sums == column_sums,
            "downstream_shapes": downstream_shapes,
            "fifteen_value_list_matches_every_downstream_column_domain": True,
            "thirteen_value_list_matches_any_downstream_axis": False,
        },
        "information_accounting": ownership | {
            "panel_cells_accounted": sum(ownership.values()),
            "panel_cells_expected": 195,
            "all25_event_labels_represented": True,
        },
        "architecture_discriminator": {
            "sum_across13_to_list15": "STRONGLY SUPPORTED structurally: the list has exactly one value per column in faed, both faed halves, and both Bifid coordinate planes.",
            "sum_across15_to_list13": "WEAK as a downstream interface: its13 values match the label-row count but no fixed axis of the19x15 or38x15 downstream matrices.",
            "how_list15_operates_on_downstream_columns": "UNKNOWN: addition, subtraction, ordering, selection, or another operation would be an unsupported new choice.",
        },
        "graph_effect": "Add a PROMISING typed edge (residual60 + all25 event labels + untouched label bits) -> public13x15 panel -> sum-list15, with a dimensionally exact but operation-free alignment to faed/Bifid columns.",
        "result": "The fixed mixed-type panel produces a unique orientation-invariant15-value sum list aligned to every downstream15-column representation. This identifies a plausible matrixsumlist output type but does not specify how that list is consumed.",
        "limits": [
            "Applying the page-adjacent a1z26 convention to dbbi is source-supported but not explicitly commanded for this panel.",
            "The rowwise dbbi/label join remains an inferred layout.",
            "Dimensional alignment is not proof that any arithmetic action on faed is intended.",
        ],
        "new_cryptographic_trials": 0,
        "new_trial_inputs": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
