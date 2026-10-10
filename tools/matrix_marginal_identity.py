#!/usr/bin/env python3
"""Compare the fixed matrix sum list with canonical downstream marginals.

This is a structural identity test.  It uses the already recovered public
objects and the reversible source-keyed Bifid representation, but performs no
AES operation, candidate generation, encrypted-data trial, or Bitcoin-key
operation.
"""

import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.matrix_sum_interface import report as matrix_sum_report
from tools.prime_boundary import binary_boundary


WIDTH = 15


def column_sums(values, width=WIDTH):
    if width < 1 or len(values) % width:
        raise ValueError("Values must tile exactly at the requested width")
    return [sum(values[column::width]) for column in range(width)]


def coordinate_signatures(text, square, prefix):
    """Return the direct row, column, and row+column marginals at both origins."""
    coordinates = [divmod(square.index(symbol), 5) for symbol in text]
    rows = len(text) // WIDTH
    if rows * WIDTH != len(text):
        raise ValueError("Downstream object does not have width 15")
    signatures = {}
    for origin in (0, 1):
        row_values = [row + origin for row, _ in coordinates]
        column_values = [column + origin for _, column in coordinates]
        signatures[f"{prefix}.row_coordinate.origin{origin}"] = column_sums(row_values)
        signatures[f"{prefix}.column_coordinate.origin{origin}"] = column_sums(column_values)
        signatures[f"{prefix}.coordinate_pair_total.origin{origin}"] = column_sums(
            [row + column + 2 * origin for row, column in coordinates]
        )
    return signatures


def report():
    segments = split_segments()
    dbbi = segments["dbbi"]
    faed = segments["faed"]
    boundary = binary_boundary()
    bits = boundary["bits"]
    fixed = matrix_sum_report()["observed"]["column_sum_list"]

    dbbi_values = [ord(symbol) - ord("a") + 1 for symbol in dbbi]
    bit_values = [int(symbol) for symbol in bits]
    left = column_sums(dbbi_values, 7)
    right = column_sums(bit_values, 8)
    if left + right != fixed:
        raise ValueError("The fixed list no longer decomposes as its two source fields")
    bit_rows = [bits[offset:offset + 8] for offset in range(0, len(bits), 8)]
    if any(row[0] != "0" for row in bit_rows) or right[0] != 0:
        raise ValueError("Expected the zero high-bit column of lowercase ASCII")

    square = key_square(dbbi)
    output = bifid(faed, square, len(faed))
    objects = {
        "faed.full38x15": faed,
        "faed.upper19x15": faed[:285],
        "faed.lower19x15": faed[285:],
        "bifid.rendered38x15": output,
        "bifid.even19x15": output[::2],
        "bifid.odd19x15": output[1::2],
    }
    signatures = {}
    for name, text in objects.items():
        signatures.update(coordinate_signatures(text, square, name))

    ordered_matches = sorted(name for name, values in signatures.items() if values == fixed)
    multiset_matches = sorted(name for name, values in signatures.items() if sorted(values) == sorted(fixed))
    if ordered_matches or multiset_matches:
        raise ValueError("The expected direct-marginal rejection no longer holds")

    # These equalities are forced by the full-period Bifid fold: even output
    # coordinates receive the two source row coordinates, while odd output
    # coordinates receive the two source column coordinates.
    conservation = {
        "source_full_rows_equal_even_pair_totals_origin0":
            signatures["faed.full38x15.row_coordinate.origin0"]
            == signatures["bifid.even19x15.coordinate_pair_total.origin0"],
        "source_full_columns_equal_odd_pair_totals_origin0":
            signatures["faed.full38x15.column_coordinate.origin0"]
            == signatures["bifid.odd19x15.coordinate_pair_total.origin0"],
        "source_full_rows_equal_even_pair_totals_origin1":
            signatures["faed.full38x15.row_coordinate.origin1"]
            == signatures["bifid.even19x15.coordinate_pair_total.origin1"],
        "source_full_columns_equal_odd_pair_totals_origin1":
            signatures["faed.full38x15.column_coordinate.origin1"]
            == signatures["bifid.odd19x15.coordinate_pair_total.origin1"],
    }
    if not all(conservation.values()):
        raise ValueError("Expected Bifid coordinate conservation failed")

    return {
        "id": "C25-MATRIX-MARGINAL-IDENTITY",
        "date": "2026-10-02",
        "status": "REJECTED",
        "hypothesis": "The fixed15-value upstream sum list is already an ordered or reorder-only canonical column marginal of a fixed downstream FAED/Bifid representation.",
        "invariant": "A parameter-free marginal edge must reproduce the exact15 values using only the established source-keyed square, fixed width15, ordinary row/column coordinates, and an explicit zero- or one-based origin.",
        "input": "The exact public13x7 dbbi field,13x8 raw-label bit field, FAED38x15 panels, and recovered Bifid output planes",
        "upstream_type_analysis": {
            "sum_list": fixed,
            "left_field": {
                "width": 7,
                "source_type": "dbbi symbol rank a=1 through i=9",
                "column_sums": left,
                "per_cell_domain": [1, 9],
            },
            "right_field": {
                "width": 8,
                "source_type": "raw matrixsumlist ASCII bit a=0 or b=1",
                "column_sums": right,
                "per_cell_domain": [0, 1],
                "zero_column_offset_within_field": 0,
                "zero_column_reason": "All thirteen decoded lowercase ASCII characters have a zero most-significant bit.",
            },
            "common_row_count": 13,
            "common_numeric_scale_authored": False,
            "consequence": "The apparent list15 is a reversible concatenation of a rank-sum7 and a bit-count8, not one source-defined homogeneous measurement.",
        },
        "downstream_marginal_test": {
            "objects": {name: [len(text) // WIDTH, WIDTH] for name, text in objects.items()},
            "coordinate_origins": [0, 1],
            "marginals_per_object_and_origin": ["row_coordinate", "column_coordinate", "coordinate_pair_total"],
            "signatures_checked": len(signatures),
            "ordered_exact_matches": ordered_matches,
            "reorder_only_multiset_matches": multiset_matches,
            "signatures": signatures,
        },
        "verified_bifid_conservation": conservation,
        "classification": {
            "shared_width15_geometry": "STRONGLY SUPPORTED",
            "homogeneous_sum_list15": "WEAK",
            "direct_downstream_coordinate_marginal": "REJECTED",
            "parameterized_downstream_operation": "UNKNOWN",
            "two_field_7_plus_8_interface": "STRONGLY SUPPORTED dimensionally; consumer UNKNOWN",
        },
        "graph_effect": "Delete the direct panel-sum15 -> downstream coordinate-marginal edge. Retain the exact two-field7|8 geometry and an unknown parameterized consumer edge.",
        "result": "None of36 canonical downstream coordinate marginals equals the fixed list in order or as a multiset. The Bifid conservation controls pass, so the negative is not caused by a coordinate implementation error. The prior claim of a homogeneous downstream sum-list interface is weakened: only the shared width and7|8 field geometry survive.",
        "exact_remaining_unknown": "No public instruction binds the rank-sum7 or bit-count8 field to a downstream target, action, normalization, or field-wise consumer. Testing any such operation would add an unauthored rule.",
        "next_test": "Require a new creator-authored clue or independently fixed rule naming the target and action. Without it, no further parameter-free structural consumer is available and no cryptographic execution is justified.",
        "limits": [
            "The test rejects exact ordered and reorder-only coordinate-marginal identity, not every possible arithmetic transform.",
            "The13x15 rowwise source join remains inferred rather than creator-authored.",
            "Zero- and one-based Bifid coordinate conventions are both covered; no modulus, offset, ranking, sign, or fitted mapping is introduced.",
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
