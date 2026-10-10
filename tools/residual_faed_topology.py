#!/usr/bin/env python3
"""Distinguish serial residual->FAED flow from convergence at Bifid."""

import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS
from tools.matrix_width_interface import chunks


def constant_source_columns(entries, source_column):
    constant = []
    signatures = []
    for target_column in range(15):
        values = [source_column(entry) for entry in entries[target_column::15]]
        signatures.append(values)
        if len(set(values)) == 1:
            constant.append(target_column)
    return constant, signatures


def report():
    join = json.loads((ARTIFACTS / "cycle23/residual-frame-join.json").read_text())
    maps = json.loads((ARTIFACTS / "cycle10/instruction-graphs-v3.json").read_text())
    branch = next(entry for entry in maps["derived_source_maps"]["branches"] if entry["mask"] == 1017)
    residual_entries = branch["residual_source_map"]
    residual = "".join(entry["symbol"] for entry in residual_entries)
    if len(residual) != 60 or join["information_accounting"]["residual_tokens"] != 60:
        raise ValueError("Frozen residual changed")

    segments = split_segments()
    dbbi = segments["dbbi"]
    faed = segments["faed"]
    square = key_square(dbbi)
    output = bifid(faed, square, len(faed))
    if square != join["square_dependency"]["derived_square"]:
        raise ValueError("Residual/event reconstruction no longer reaches the used square")

    residual_rows = chunks(residual, 15)
    downstream = {
        "faed38x15": chunks(faed, 15),
        "bifid_rendered38x15": chunks(output, 15),
        "bifid_even19x15": chunks(output[::2], 15),
        "bifid_odd19x15": chunks(output[1::2], 15),
    }
    row_matches = {
        name: [
            {"residual_row_zero_based": left_index, "downstream_row_zero_based": right_index}
            for left_index, left in enumerate(residual_rows)
            for right_index, right in enumerate(rows)
            if left == right
        ]
        for name, rows in downstream.items()
    }
    substring_offsets = {
        "faed570": faed.find(residual),
        "bifid570": output.find(residual),
        "bifid_even285": output[::2].find(residual),
        "bifid_odd285": output[1::2].find(residual),
    }

    raw7_constant, raw7_signatures = constant_source_columns(
        residual_entries,
        lambda entry: entry["normalized_span_zero_based_half_open"][0] % 7,
    )
    raw15_constant, raw15_signatures = constant_source_columns(
        residual_entries,
        lambda entry: entry["normalized_span_zero_based_half_open"][0] % 15,
    )
    logical15_constant, logical15_signatures = constant_source_columns(
        residual_entries,
        lambda entry: (entry["logical_position_one_based"] - 1) % 15,
    )

    first = join["square_dependency"]["first_occurrences"]
    owner_counts = {
        owner: sum(entry["owner"] == owner for entry in first)
        for owner in ("residual", "event-label")
    }
    if owner_counts != {"residual": 7, "event-label": 2}:
        raise ValueError("First-occurrence ownership changed")

    direct_identity = (
        any(offset >= 0 for offset in substring_offsets.values())
        or any(matches for matches in row_matches.values())
    )
    if direct_identity:
        raise ValueError("Expected direct residual/downstream identity rejection changed")

    edges = [
        {"from": "residual60 + first23 event labels", "to": "dbbi91", "status": "VERIFIED conditionally", "basis": "Exact83-token and91-letter reconstruction under the frozen mask1017/near-white convention."},
        {"from": "dbbi91", "to": "source-keyed square25", "status": "VERIFIED", "basis": "Deterministic first-occurrence key-square construction."},
        {"from": "source-keyed square25 + faed570", "to": "Bifid570", "status": "VERIFIED mechanically", "basis": "Exact reversible full-period transform."},
        {"from": "residual60", "to": "faed570", "status": "UNKNOWN as an intended direct transform", "basis": "No authored operator; direct substring, exact-row, and inherited-axis forms fail."},
        {"from": "raw matrixsumlist104", "to": "current Bifid570 dependency graph", "status": "UNKNOWN semantic role; zero raw bits consumed", "basis": "The final two event markers lie in the label region but are explicitly excluded from dbbi/square reconstruction."},
        {"from": "Bifid570", "to": "btcseed prefix", "status": "VERIFIED observation", "basis": "Exact serialized prefix."},
        {"from": "Bifid570 body", "to": "downstream receiver", "status": "UNKNOWN", "basis": "No receiver or action is authored."},
    ]

    return {
        "id": "C27-RESIDUAL-FAED-TOPOLOGY",
        "date": "2026-10-02",
        "status": "CONFIRMED",
        "hypothesis": "The recovered objects form a convergent Bifid architecture: residual/event data reconstruct the square source while FAED is an independent text input; a serial residual60-to-FAED570 transform is not required by the known flow.",
        "invariant": "A serial direct edge needs an exact identity, preserved source axis, or authored transform. A convergent edge must reproduce the exact square and Bifid output from independently typed inputs.",
        "residual_width15_preflight": {
            "shape": [4, 15],
            "rows": residual_rows,
            "whole_residual_substring_offsets_minus_one_means_absent": substring_offsets,
            "exact_downstream_row_matches": row_matches,
            "source_axis_checks": {
                "original_dbbi7_constant_target_columns": raw7_constant,
                "original_raw15_constant_target_columns": raw15_constant,
                "logical_domain15_constant_target_columns": logical15_constant,
                "original_dbbi7_signatures": raw7_signatures,
                "original_raw15_signatures": raw15_signatures,
                "logical_domain15_signatures": logical15_signatures,
            },
            "interpretation": "The4x15 reshape preserves residual order but does not inherit a15-column source axis; only one of15 target columns happens to keep one original dbbi7 column.",
        },
        "convergent_dependency": {
            "residual_tokens": 60,
            "event_labels_used_to_reconstruct_dbbi": 23,
            "reconstructed_dbbi_letters": 91,
            "square_first_occurrences_owned_by_residual": owner_counts["residual"],
            "square_first_occurrences_owned_by_events": owner_counts["event-label"],
            "fixed_alphabet_supplement_symbols": len(square) - len(first),
            "faed_symbols_consumed": len(faed),
            "bifid_symbols_produced": len(output),
            "raw_label_bits_consumed_by_current_bifid_graph": 0,
            "derived_square_matches_used_square": True,
            "bifid_round_trip": bifid(output, square, len(output), False) == faed,
        },
        "edges": edges,
        "architecture_discriminator": {
            "serial_residual_to_faed": "WEAK and unneeded by the reproduced flow; direct identity/row/axis-preserving forms are REJECTED, broader authored transform remains UNKNOWN.",
            "parallel_convergence_at_bifid": "STRONGLY SUPPORTED; the residual/event branch supplies the exact square and FAED supplies the exact text input.",
            "location_of_missing_data_flow": "After decoding matrixsumlist semantics and after the complete Bifid570 output, not between residual60 and FAED570 in the reproduced graph.",
        },
        "graph_effect": "Replace the assumed serial residual60 -> faed570 edge with two branches converging at Bifid. Preserve UNKNOWN edges from matrixsumlist semantics and the full Bifid output to a downstream receiver.",
        "result": "Residual60 already reaches Bifid through exact dbbi/square reconstruction. Its4x15 reflow has no exact downstream identity and no inherited15-column source axis. FAED570 is the separate Bifid text input. The remaining missing edge is the consumer of matrixsumlist semantics and/or full Bifid570, not a required residual-to-FAED conversion.",
        "next_test": "No further parameter-free transform is licensed. Require an authored consumer for matrixsumlist or the full Bifid output before executing another operation.",
        "new_cryptographic_trials": 0,
        "new_trial_inputs": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
