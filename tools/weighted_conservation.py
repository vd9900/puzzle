import json
from collections import Counter

from tools.gsmg import extract_grid, spiral_coordinates
from tools.instruction_graphs import ROOT, digest, primary_layout, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle11"
FROZEN = ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json"
PALETTE = {"black": 1, "white": 0, "near_white": 0, "blue": 2, "yellow": 25}


def source_partitions(size):
    coordinates = spiral_coordinates(size)
    return [
        {
            "name": "original-top-to-bottom-rows",
            "basis": "Original square grid defines disjoint rows; matrixsumlist does not explicitly select this axis",
            "groups": [[(row, column) for column in range(size)] for row in range(size)],
            "order_status": "Conventional source coordinate order, not an encoded command",
        },
        {
            "name": "original-left-to-right-columns",
            "basis": "Original square grid defines disjoint columns; matrixsumlist does not explicitly select this axis",
            "groups": [[(row, column) for row in range(size)] for column in range(size)],
            "order_status": "Conventional source coordinate order, not an encoded command",
        },
        {
            "name": "verified-spiral-ASCII-octets-plus-tail",
            "basis": "Previously verified image traversal reads24 MSB-first ASCII octets and retains four trailing bits",
            "groups": [coordinates[offset:offset + 8] for offset in range(0, size * size, 8)],
            "order_status": "Verified for original binary image decoding, not verified for weighted arithmetic",
        },
    ]


def partition_totals(matrix, groups):
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("Expected a nonempty square matrix")
    if any(not group for group in groups):
        raise ValueError("Empty source groups are not permitted")
    cells = [cell for group in groups for cell in group]
    expected = {(row, column) for row in range(size) for column in range(size)}
    if len(cells) != size * size or set(cells) != expected:
        raise ValueError("Partition must account for every source cell exactly once")
    return [sum(matrix[row][column] for row, column in group) for group in groups]


def consecutive_sum_witness(values, targets):
    if not values or any(value <= 0 for value in values):
        raise ValueError("Residual values must be strictly positive")
    if not targets or any(target < 0 for target in targets):
        raise ValueError("Target groups must be nonnegative and nonempty")
    residual_boundaries = []
    total = 0
    for index, value in enumerate(values):
        total += value
        residual_boundaries.append((total, index + 1))
    boundary_lookup = {value: offset for value, offset in residual_boundaries}
    target_total = 0
    target_boundaries = []
    start = 0
    first_failure = None
    groups = []
    for index, target in enumerate(targets):
        target_total += target
        target_boundaries.append(target_total)
        end = boundary_lookup.get(target_total)
        available = end is not None and end > start
        if first_failure is None and not available:
            lower = max((entry for entry in residual_boundaries if entry[0] < target_total), default=(0, 0))
            upper = next((entry for entry in residual_boundaries if entry[0] > target_total), None)
            first_failure = {"group_index_zero_based": index, "wanted_cumulative_sum": target_total, "nearest_lower_cumulative_sum_and_end_index": list(lower), "nearest_upper_cumulative_sum_and_end_index": list(upper) if upper else None, "zero_target_cannot_consume_positive_symbols": target == 0}
        if first_failure is None:
            groups.append({"residual_span_zero_based_half_open": [start, end], "sum": target})
            start = end
    if first_failure is None and start != len(values):
        first_failure = {"unconsumed_residual_symbols": len(values) - start}
    return {
        "match": first_failure is None,
        "complete_residual_total": sum(values),
        "complete_target_total": sum(targets),
        "target_boundaries_in_residual": sum(boundary in boundary_lookup for boundary in target_boundaries),
        "first_failure": first_failure,
        "successful_prefix_groups": groups,
        "convention": "Consecutive nonempty groups in untouched source order; every strictly positive residual symbol consumed once; no inferred reversals or splits",
        "grouping_is_not_a_primary_instruction": True,
    }


def compare_residual(values, targets):
    residual_digits = "".join(str(value) for value in values)
    decimal_totals = "".join(str(value) for value in targets)
    return {
        "atomic_sum_list": {"match": values == targets, "residual_length": len(values), "target_length": len(targets), "length_compatible": len(values) == len(targets)},
        "literal_decimal_total_list": {"match": residual_digits == decimal_totals, "residual_digit_length": len(residual_digits), "target_digit_length": len(decimal_totals), "length_compatible": len(residual_digits) == len(decimal_totals), "target_contains_zero": "0" in decimal_totals},
        "consecutive_additive_partition": consecutive_sum_witness(values, targets),
    }


def secondary_scope_note():
    path = ROOT / "research/evidence/cycle05/fork-ENDGAME.md"
    text = path.read_text()
    anchor = "a lista das 14 somas de linha e 14 de coluna"
    start = text.index(anchor)
    return {
        "source": source(path), "line_one_based": text.count("\n", 0, start) + 1,
        "quote": anchor, "classification": "SECONDARY_RESEARCH_COVERAGE_CLAIM_NOT_LOCAL_EXECUTION",
        "reported_family": "Weighted row-plus-column decimal lists with several orders/zeroing conventions",
        "missing_reproduction_artifact": "The linked symbolic_color_sums and inverse-list reports/scripts are not preserved in this repository",
        "not_promoted_to_local_coverage": True,
    }


def report():
    frozen = json.loads(FROZEN.read_text())
    next_step = frozen["highest_value_next_experiment"]
    if next_step["name"] != "Fixed weighted-color positional conservation audit":
        raise ValueError("Unexpected preceding frozen experiment")
    grid = extract_grid(ROOT / "research/sources/gsmg-puzzle.png")
    weighted = [[PALETTE[color] for color in row] for row in grid["colors"]]
    unused_layout, compact, unused_span = primary_layout()
    branches = []
    for branch in frozen["derived_source_maps"]["branches"]:
        symbols = branch["residual_source_map"]
        for entry in symbols:
            start, end = entry["normalized_span_zero_based_half_open"]
            if compact[start:end] != entry["symbol"]:
                raise ValueError("Frozen residual source map differs from original page")
        values = [ord(entry["symbol"]) - 96 for entry in symbols]
        if digest("".join(entry["symbol"] for entry in symbols).encode()) != branch["residual_sha256"]:
            raise ValueError("Frozen residual identity changed")
        branches.append({"mask": branch["mask"], "values": values, "source_map": symbols, "total": sum(values)})
    partitions = []
    results = []
    coordinates = spiral_coordinates(14)
    for partition in source_partitions(14):
        targets = partition_totals(weighted, partition["groups"])
        groups = [{"group_index_zero_based": index, "cells_row_column_zero_based": [list(cell) for cell in group], "weighted_sum": targets[index], "special_color_events": [{"row_column_zero_based": list(cell), "spiral_index_zero_based": coordinates.index(cell), "color": grid["colors"][cell[0]][cell[1]]} for cell in group if grid["colors"][cell[0]][cell[1]] in ("blue", "yellow", "near_white")]} for index, group in enumerate(partition["groups"])]
        partitions.append({key: value for key, value in partition.items() if key != "groups"} | {"source_group_count": len(groups), "groups": groups, "sum_of_groups": sum(targets), "all196_cells_accounted_once": True})
        for branch in branches:
            comparisons = compare_residual(branch["values"], targets)
            results.append({"partition": partition["name"], "residual_mask": branch["mask"], "comparisons": comparisons})
    if any(any(comparison["match"] for comparison in entry["comparisons"].values()) for entry in results):
        raise ValueError("Observed conservation match requires manual source-evidence review")
    octets = partitions[-1]
    event_counts = [len(group["special_color_events"]) for group in octets["groups"]]
    return {
        "id": "C11-WEIGHTED-CONSERVATION", "date": "2026-09-30", "status": "REJECTED",
        "hypothesis": "The fixed weighted image is positionally accounted for by a documented residual under a source-defined partition",
        "source_evidence": [source(FROZEN), source(ROOT / "research/sources/gsmg-puzzle.png"), source(ROOT / "research/sources/salphaseion.html")],
        "input": "Unchanged original image and both frozen residual source maps",
        "output": "Exact finite partition comparisons and first-failure witnesses",
        "assumptions": ["b/be denote B/Y numeric weights, not only marker labels", "Black/white/near-white keep original1/0/0", "Rows/columns are structural partitions, not explicitly selected axes", "Verified byte grouping is reused as arithmetic partition only", "Positive residual values can be tested as consecutive nonempty additive groups, though no creator text instructs this"],
        "operation_order": ["validate frozen source maps", "apply one fixed palette", "partition original cells by existing geometry", "compare untouched residual values directly, as decimal list, and by consecutive additive boundaries", "reject exact failed realizations without a cipher search"],
        "palette": PALETTE, "image_color_counts": dict(Counter(color for row in grid["colors"] for color in row)),
        "weighted_matrix": weighted, "weighted_total": sum(map(sum, weighted)),
        "residual_branches": branches, "partitions": partitions, "results": results,
        "search_space": {"palettes": 1, "image_variants": 1, "fixed_source_partitions": 3, "previously_documented_residual_branches": 2, "comparison_protocols": 3, "exact_comparisons": 18, "new_cryptographic_trials": 0, "new_trial_inputs": 0},
        "scope_of_rejection": "Only the18 explicit unchanged-source comparisons; arbitrary encodings, partitions and downstream operations remain untested and are not justified by this negative",
        "preflight": {"primary_explicit_axis": None, "primary_explicit_residual_partition": None, "no_execution_edge_identified": True, "partition_source": "Rows/columns intrinsic in image;24 octets plus four-bit tail verified previously", "no_invented_partition_or_order": True},
        "color_frame_accounting": {"group_count": 25, "special_color_event_count": sum(event_counts), "event_counts_by_group": event_counts, "one_special_event_per_group": all(count == 1 for count in event_counts), "near_white_shares_octet_with_a_colored_cell": len(octets["groups"][20]["special_color_events"]) == 2, "tail_has_no_special_color_event": event_counts[-1] == 0, "near_white_global_341_match_does_not_explain_prime_frame_1_assignment": True},
        "combined_axis_limit": {"rows_and_columns_double_count_cells": True, "combined_total": 2 * sum(map(sum, weighted)), "cannot_equal_positive_residual_total": True},
        "secondary_prior_claim": secondary_scope_note(),
        "confidence": "HIGH for finite negative/accounting; LOW for inferred palette intent",
        "contradictions": ["Neither axis yields residual-length totals or digit strings", "Both residuals fail the first cumulative boundary in all three source partitions", "25 byte groups are not in one-to-one correspondence with25 special color events", "341 equality favors61 while conditional prime-frame convention favors60", "No source binds weights to a residual partition or faed operation"],
        "next_test": "Audit trailer pronoun binding and exact choice-bearing source references. Do not invent a weighted grouping or enlarge cipher search.",
    }


def main():
    document = report()
    write_artifact(OUTPUT / "weighted-conservation.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "exact_comparisons": document["search_space"]["exact_comparisons"], "matches": sum(comparison["match"] for entry in document["results"] for comparison in entry["comparisons"].values()), "weighted_total": document["weighted_total"], "one_special_event_per_byte_group": document["color_frame_accounting"]["one_special_event_per_group"], "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
