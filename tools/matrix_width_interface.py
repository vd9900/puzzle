#!/usr/bin/env python3
"""Audit the exact 15-column interface across the public SalPhaseIon objects.

This module performs only deterministic parsing, reshaping, and the already
reproduced classical Bifid transform.  It does not derive passwords, invoke
AES, construct Bitcoin scalars, or query a network.
"""

import json
from hashlib import sha256

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.prime_boundary import binary_boundary


def chunks(text, width):
    if width < 1 or len(text) % width:
        raise ValueError("Object does not tile at the requested width")
    return [text[offset:offset + width] for offset in range(0, len(text), width)]


def digest(text):
    return sha256(text.encode("ascii")).hexdigest()


def report():
    segments = split_segments()
    dbbi = segments["dbbi"]
    faed = segments["faed"]
    boundary = binary_boundary()
    label = boundary["decoded"]
    bits = boundary["bits"]

    if label != "matrixsumlist" or len(label) != 13 or len(bits) != 104:
        raise ValueError("Unexpected public matrixsumlist label")

    # One decoded label character supplies one eight-bit row.  Since DBBI has
    # 91 symbols, it supplies seven symbols for each of those same 13 rows.
    dbbi_rows = chunks(dbbi, 7)
    bit_rows = chunks(bits, 8)
    if len(dbbi_rows) != len(label) or len(bit_rows) != len(label):
        raise ValueError("The 13-row source interface does not close")
    if "".join(chr(int(row, 2)) for row in bit_rows) != label:
        raise ValueError("Eight-bit rows do not reconstruct matrixsumlist")
    header_rows = [left + right for left, right in zip(dbbi_rows, bit_rows)]
    if any(len(row) != 15 for row in header_rows):
        raise ValueError("The joined public rows are not width 15")

    # The following 570-character object is exactly 38 rows at that same
    # width.  Its two Bifid halves are therefore two 19x15 panels.
    faed_rows = chunks(faed, 15)
    upper, lower = chunks(faed[:285], 15), chunks(faed[285:], 15)
    if len(faed_rows) != 38 or len(upper) != 19 or len(lower) != 19:
        raise ValueError("FAED does not form the expected exact panels")

    square = key_square(dbbi)
    output = bifid(faed, square, len(faed))
    even_plane = chunks(output[::2], 15)
    odd_plane = chunks(output[1::2], 15)

    cell_checks = []
    for index, (top_symbol, bottom_symbol) in enumerate(zip(faed[:285], faed[285:])):
        top_row, top_column = divmod(square.index(top_symbol), 5)
        bottom_row, bottom_column = divmod(square.index(bottom_symbol), 5)
        expected = square[top_row * 5 + bottom_row] + square[top_column * 5 + bottom_column]
        actual = output[2 * index:2 * index + 2]
        cell_checks.append(actual == expected)
    if not all(cell_checks):
        raise ValueError("Bifid output is not the exact cellwise two-panel fold")

    output_rows = chunks(output, 15)
    prefix = output[:7]
    body = output[7:]
    if prefix != "btcseed" or body != output_rows[0][7:] + "".join(output_rows[1:]):
        raise ValueError("The visible prefix does not align with the 7|8 matrix field")

    return {
        "id": "C24-MATRIX-WIDTH-INTERFACE",
        "date": "2026-10-02",
        "status": "PROMISING",
        "hypothesis": "The public dbbi, raw matrixsumlist encoding, faed, and full-period Bifid objects share a 15-cell matrix width; the apparent seven-character Bifid header is the first 7-cell field rather than an isolated linear object.",
        "input": "Exact public dbbi91, raw104 a/b label, decoded matrixsumlist, faed570, and the fixed source-keyed full-period Bifid transform",
        "operation_order": [
            "decode the 104 a/b symbols as thirteen unchanged eight-bit rows",
            "reshape dbbi91 as thirteen unchanged seven-symbol rows",
            "join corresponding 7-cell and 8-cell rows into a 13x15 panel",
            "reshape faed570 as 38x15 and split it at the exact Bifid midpoint into two 19x15 panels",
            "verify all 285 Bifid output digraphs are cellwise functions of corresponding panel cells",
            "reshape the 570-character Bifid output as 38x15 and test the exact 7|8 first-row boundary",
        ],
        "verified_equalities": {
            "dbbi": "91 = 13 * 7",
            "raw_label": "104 = 13 * 8",
            "joined_panel": "195 = 13 * (7 + 8) = 13 * 15",
            "faed": "570 = 38 * 15 = 2 * 19 * 15",
            "bifid_coordinate_planes": "285 = 19 * 15 for each of the even and odd output rails",
            "remaining_body": "563 = 8 + 37 * 15",
        },
        "label_interface": {
            "decoded_label": label,
            "decoded_characters": len(label),
            "dbbi_rows": len(dbbi_rows),
            "dbbi_columns": 7,
            "bit_rows": len(bit_rows),
            "bit_columns": 8,
            "joined_rows": len(header_rows),
            "joined_columns": 15,
            "all_label_bytes_reconstructed": True,
            "dbbi_round_trip": "".join(dbbi_rows) == dbbi,
            "raw_label_round_trip": "".join(bit_rows) == bits,
            "joined_panel_sha256": digest("".join(header_rows)),
        },
        "faed_bifid_interface": {
            "faed_rows": len(faed_rows),
            "faed_columns": 15,
            "half_panel_rows": len(upper),
            "half_panel_columns": 15,
            "cellwise_pairs_checked": len(cell_checks),
            "cellwise_pairs_matching": sum(cell_checks),
            "even_coordinate_plane_shape": [len(even_plane), len(even_plane[0])],
            "odd_coordinate_plane_shape": [len(odd_plane), len(odd_plane[0])],
            "faed_round_trip": "".join(faed_rows) == faed,
            "bifid_interleave_round_trip": "".join(a + b for a, b in zip(output[::2], output[1::2])) == output,
            "output_sha256": digest(output),
        },
        "prefix_boundary": {
            "first_output_row": output_rows[0],
            "left_field_width": 7,
            "left_field": prefix,
            "right_field_width": 8,
            "right_field": output_rows[0][7:],
            "remaining_full_rows": len(output_rows) - 1,
            "remaining_body_length": len(body),
            "body_decomposition_exact": len(body) == 8 + 37 * 15,
            "linear_cut_splits_a_bifid_digraph": len(prefix) % 2 == 1,
        },
        "architecture_discriminator": {
            "linear_header_body": "WEAK: the seven-letter recognition has no source separator and cuts a natural Bifid digraph; treating the other563 symbols as an opaque string loses the exact source-derived tiling.",
            "matrix_field": "STRONGLY SUPPORTED structurally: thirteen 7|8 source rows derive width15 independently, faed and both Bifid coordinate planes tile exactly at that width, and btcseed fills the first seven-cell field.",
            "intended_sum_or_list_operation": "UNKNOWN: the geometry fixes data types and boundaries but supplies no value map, axis, aggregation rule, or downstream consumer.",
        },
        "requested_edge_classification": [
            {
                "edge": "dbbi91 -> matrixsumlist",
                "classification": "UNKNOWN",
                "reason": "The source boundary and the new 13-row 7|8 interface are exact, but neither object is shown to produce the other and no operator is specified.",
            },
            {
                "edge": "matrixsumlist -> 25-event prime/color structure",
                "classification": "WEAK",
                "reason": "Two continued prime markers occupy the raw label region, but the creator-attributed mention order runs yellowblueprimes before matrixsumlist and supplies no forward transform in this direction.",
            },
            {
                "edge": "25-event prime/color structure -> residual60",
                "classification": "STRONGLY SUPPORTED",
                "reason": "Under the frozen mask1017 and near-white=1 convention, the first23 ordered event labels select the prime markers and their exact complement is the60-token residual; creator intent remains unverified.",
            },
            {
                "edge": "residual60 -> faed570",
                "classification": "UNKNOWN",
                "reason": "No lossless transform, operand binding, or source-authored consumer connects these objects.",
            },
            {
                "edge": "faed570 -> source-keyed Bifid570",
                "classification": "STRONGLY SUPPORTED",
                "reason": "The fixed square and period570 transform is exact and reversible and yields the recognized prefix, but the Bifid instruction is community-derived rather than primary-authored.",
            },
            {
                "edge": "source-keyed Bifid570 -> btcseed prefix",
                "classification": "VERIFIED",
                "reason": "The deterministic output begins with the exact seven letters btcseed.",
            },
            {
                "edge": "btcseed prefix -> remaining Bifid body",
                "classification": "UNKNOWN",
                "reason": "The prefix does not define an operation on the remainder. The new geometry makes them fields of one 38x15 object rather than proving a header-driven transform.",
            },
            {
                "edge": "remaining Bifid body -> downstream interface",
                "classification": "UNKNOWN",
                "reason": "No authored axis, value mapping, aggregation rule, or receiving object is known.",
            },
        ],
        "result": "A previously unrecorded exact width15 interface joins the recovered public objects. It replaces the opaque563-body model with an 8-cell first-row remainder plus37 complete rows, and represents Bifid as a cellwise fold of two19x15 FAED panels. This is a structural bridge, not proof of the intended matrixsumlist operation.",
        "coverage_comparison": {
            "previously_recorded": "Prior campaigns reshaped dbbi91 and faed570 separately, tried width15/38 FAED grids, and padded the combined195-symbol dbbi-plus-label source to14x14 with one added cell.",
            "new_here": "The exact native label-byte join dbbi13x7 plus label13x8, its derived width15, the two19x15 FAED halves, and the resulting 8+37x15 body accounting were not found in preserved reports or scripts.",
            "not_repeated": "No sum list, route, text score, password transform, encrypted-container test, or key test was run.",
        },
        "limits": [
            "Exact dimensional closure and reversible cell mapping do not prove creator intent.",
            "Joining the adjacent dbbi and raw-label blocks row by row is an inferred matrix layout; no primary instruction explicitly chooses this orientation.",
            "No row sum, column sum, numeric symbol map, route, selector, password, cipher-container operation, or key interpretation is inferred.",
            "The experiment does not choose a downstream consumer for either 19x15 coordinate plane or the 38x15 rendered output.",
        ],
        "next_test": "Use the fixed 13x15/19x15/38x15 types to look only for an authored axis and operand binding for matrixsumlist. Without such a binding, do not compute arbitrary sums or turn any output into cryptographic trial material.",
        "new_cryptographic_trials": 0,
        "new_trial_inputs": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
