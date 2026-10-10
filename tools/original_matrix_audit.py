#!/usr/bin/env python3
"""Audit what the original matrix and yellow/blue/prime hints actually fix."""

from collections import Counter
from itertools import product
import json

from tools.gsmg import ARTIFACTS, SOURCES, extract_grid, spiral_coordinates
from tools.instruction_graphs import source, write_artifact


OUTPUT = ARTIFACTS / "cycle33"
IMAGE = SOURCES / "gsmg-puzzle.png"
CREATOR = SOURCES.parent / "evidence/cycle02/_work__creator_jrk.txt"
CHAT = SOURCES.parent / "evidence/cycle02/_work__chat_transcript.txt"
PRIME = ARTIFACTS / "cycle03/prime-boundary.json"
CONTROLS = ARTIFACTS / "cycle05/prime-selection-controls.json"
HINT_ORDER = ARTIFACTS / "cycle11/hint-instruction-order.json"


RGB = {
    "black": [0, 0, 0],
    "blue": [63, 72, 204],
    "yellow": [255, 242, 0],
    "white": [255, 255, 255],
    "near_white": [254, 254, 254],
}


def decode_with_palette(colors, mapping):
    coordinates = spiral_coordinates(14)
    bits = "".join(str(mapping[colors[row][column]]) for row, column in coordinates)
    decoded = bytes(int(bits[offset:offset + 8], 2) for offset in range(0, 192, 8)).decode("ascii", errors="replace")
    return decoded, bits[192:]


def unique_binary_mapping(colors, target):
    names = ["black", "blue", "yellow", "white", "near_white"]
    matches = []
    for values in product((0, 1), repeat=len(names)):
        mapping = dict(zip(names, values))
        decoded, tail = decode_with_palette(colors, mapping)
        if decoded == target:
            matches.append({"mapping": mapping, "trailing_bits": tail})
    return matches


def axis_record(matrix, colors):
    row_sums = [sum(row) for row in matrix]
    column_sums = [sum(matrix[row][column] for row in range(14)) for column in range(14)]
    blue_rows = [sum(color == "blue" for color in row) for row in colors]
    yellow_rows = [sum(color == "yellow" for color in row) for row in colors]
    blue_columns = [sum(colors[row][column] == "blue" for row in range(14)) for column in range(14)]
    yellow_columns = [sum(colors[row][column] == "yellow" for row in range(14)) for column in range(14)]
    return {
        "binary_row_sums_top_to_bottom": row_sums,
        "binary_column_sums_left_to_right": column_sums,
        "row_count": len(row_sums),
        "column_count": len(column_sums),
        "row_total": sum(row_sums),
        "column_total": sum(column_sums),
        "ordered_lists_equal": row_sums == column_sums,
        "blue_counts_by_row": blue_rows,
        "yellow_counts_by_row": yellow_rows,
        "blue_counts_by_column": blue_columns,
        "yellow_counts_by_column": yellow_columns,
        "both_axes_partition_all196_cells_once": True,
        "square_dimensions_cannot_select_an_axis": True,
    }


def report():
    grid = extract_grid(IMAGE)
    coordinates = spiral_coordinates(14)
    counts = Counter(color for row in grid["colors"] for color in row)
    if counts != Counter({"black": 86, "white": 85, "blue": 15, "yellow": 9, "near_white": 1}):
        raise ValueError("Original palette counts changed")
    if grid["decoded"] != "gsmg.io/theseedisplanted" or grid["trailing_bits"] != "0000":
        raise ValueError("Verified original spiral decode changed")

    binary_matches = unique_binary_mapping(grid["colors"], grid["decoded"])
    if binary_matches != [{
        "mapping": {"black": 1, "blue": 1, "yellow": 0, "white": 0, "near_white": 0},
        "trailing_bits": "0000",
    }]:
        raise ValueError("Expected one exact per-color binary mapping")

    selected = []
    near_white = None
    for spiral_index, (row, column) in enumerate(coordinates):
        color = grid["colors"][row][column]
        entry = {
            "row_zero_based": row,
            "column_zero_based": column,
            "spiral_index_zero_based": spiral_index,
            "spiral_position_one_based": spiral_index + 1,
            "octet_index_zero_based": spiral_index // 8,
            "bit_position_in_octet_zero_based": spiral_index % 8,
            "color": color,
            "dominant_rgb": RGB[color],
            "verified_binary_bit": grid["matrix"][row][column],
        }
        if color in ("blue", "yellow"):
            selected.append(entry)
        elif color == "near_white":
            near_white = entry
    if len(selected) != 24 or near_white is None:
        raise ValueError("Expected24 ordinary colored cells and one near-white cell")
    if [entry["octet_index_zero_based"] for entry in selected] != list(range(24)):
        raise ValueError("Colored cells no longer label each decoded octet once")
    if any(entry["bit_position_in_octet_zero_based"] != 7 for entry in selected):
        raise ValueError("Colored cell no longer occupies an octet terminal bit")

    prime = json.loads(PRIME.read_text())
    controls = json.loads(CONTROLS.read_text())
    ordinary = json.loads((ARTIFACTS / "cycle02/prime-markers.json").read_text())
    near_one = next(item for item in prime["results"] if item["near_white_hypothesis_bit"] == 1)
    if len(near_one["full_matches"]) != 1:
        raise ValueError("Conditional full prime-frame match changed")
    full = near_one["full_matches"][0]
    conditional_event_map = []
    events = near_one["events"]
    for ordinal, (event, marker) in enumerate(zip(events, full["frame_markers"]), 1):
        conditional_event_map.append({
            "event_ordinal_one_based": ordinal,
            "cell": [event["row_zero_based"], event["column_zero_based"]],
            "color": event["color"],
            "spiral_index_zero_based": event["spiral_index_zero_based"],
            "prime_position_one_based": marker["position_one_based"],
            "source_region": marker["region"],
            "source_token": marker["token"],
            "semantic_label_bit": int(marker["bit"]),
        })

    creator = CREATOR.read_text()
    chat = CHAT.read_text()
    required_quotes = [
        "Yellow has a number and so does Blue.",
        "You are at the prime part already???",
        "Oh wait, shouldn't have said that. That might have been a hint",
        "The previous \"there is another door hint\" is still a thing.",
        "At least prime number is very important to get any further.",
    ]
    if any(quote not in creator for quote in required_quotes):
        raise ValueError("Creator-attributed hint corpus changed")
    if "So don't you think it's time for a hint on matrixsumlist?" not in chat or "I gave an unforseen hint already" not in chat:
        raise ValueError("Matrixsumlist request/reply context changed")
    hint = json.loads(HINT_ORDER.read_text())
    decoded_hint = hint["binary_hint"]["decoded_public_text"]
    if not decoded_hint.startswith("yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang"):
        raise ValueError("Creator-attributed ordered hint changed")

    axes = axis_record(grid["matrix"], grid["colors"])
    source_terms = " ".join(required_quotes + ["matrixsumlist", decoded_hint]).lower()
    explicit_axis_terms = [term for term in ("row", "rows", "column", "columns", "horizontal", "vertical", "axis", "axes") if term in source_terms.split()]

    return {
        "id": "C33-ORIGINAL-MATRIX-INSTRUCTION-AUDIT",
        "date": "2026-10-02",
        "status": "INCONCLUSIVE",
        "question": "Does the original14x14 source plus yellowblueprimes fix the cells, their summation values, and a summation axis?",
        "source_evidence": [source(path) for path in (IMAGE, CREATOR, CHAT, PRIME, CONTROLS, HINT_ORDER)],
        "verified_matrix": {
            "shape": [14, 14],
            "orientation_is_visually_fixed_by_complete_png": True,
            "palette_rgb": RGB,
            "palette_counts": dict(sorted(counts.items())),
            "verified_spiral_decode": grid["decoded"],
            "trailing_bits": grid["trailing_bits"],
            "per_color_binary_assignments_checked": 32,
            "exact_url_mapping_match_count": len(binary_matches),
            "unique_binary_mapping": binary_matches[0]["mapping"],
        },
        "selected_cells": {
            "yellow_blue_cells": selected,
            "yellow_blue_count": len(selected),
            "every_decoded_octet_has_exactly_one_yellow_or_blue_terminal_cell": True,
            "yellow_blue_coordinates_are_source_fixed": True,
            "near_white_cell": near_white,
            "near_white_is_named_by_yellowblueprimes": False,
            "instruction_explicitly_says_to_sum_only_colored_cells": False,
            "classification": {
                "visible_yellow_blue_locations": "VERIFIED",
                "spiral_order_of_visible_locations": "VERIFIED by the earlier URL decode",
                "near_white_as_an_additional_selected_cell": "WEAK/CONDITIONAL",
                "colored_cells_as_the_exclusive_sum mask": "UNKNOWN",
            },
        },
        "prime_relation": {
            "ordinary24_color_frame_max_prefix": ordinary["maximum_matched_prefix_bits"],
            "ordinary24_full_match_count": ordinary["full_color_match_count"],
            "conditional25_event_full_match_count": len(near_one["full_matches"]),
            "conditional_full_match_mask": full["mask"],
            "conditional_full_match_event_map": conditional_event_map,
            "conditions_required": [
                "merge one particular subset of optional be digraphs in dbbi (mask1017)",
                "use one-based logical prime positions",
                "interpret dbbi b as1 and be as0",
                "add the unmentioned near-white cell and assign it semantic1 although its verified image bit is0",
                "continue the counter across the dbbi/matrixsumlist source boundary",
                "interpret binary-label b/a as1/0 for the final two events",
            ],
            "bounded_control_result": controls["result"],
            "classification": "STRONGLY SUPPORTED/PROMISING cross-artifact relation, not a source-complete cell-selection instruction",
        },
        "numeric_values": {
            "verified_encoding_role": {
                "mapping": binary_matches[0]["mapping"],
                "meaning": "The unique per-color binary assignment among32 mappings that reproduces the verified spiral URL.",
                "classification": "VERIFIED for the original URL encoding",
            },
            "distinct_source_derived_numbers": {
                "color_population_counts": {"blue": counts["blue"], "yellow": counts["yellow"]},
                "initial_letter_ordinals": {"blue_B": 2, "yellow_Y": 25},
                "dominant_rgb": {"blue": RGB["blue"], "yellow": RGB["yellow"]},
            },
            "near_white_conflict": {
                "verified_image_bit": near_white["verified_binary_bit"],
                "conditional_prime_frame_label": 1,
                "same_numeric_role": False,
            },
            "summation_weight_assignment_present_in_source": False,
            "classification": "UNKNOWN for matrix summation; binary encoding bits cannot be promoted to arithmetic weights without an additional binding",
        },
        "summation_axis": axes | {
            "explicit_axis_terms_in_relevant_creator_hints": explicit_axis_terms,
            "verified_spiral_is_an_order_not_a_sum_axis": True,
            "row_and_column_lists_have_equal_length_but_different_ordered_values": len(axes["binary_row_sums_top_to_bottom"]) == len(axes["binary_column_sums_left_to_right"]) and not axes["ordered_lists_equal"],
            "classification": "UNKNOWN: rows, columns, both, or the prior spiral grouping are not selected by the source wording",
        },
        "classification": {
            "original14x14_grid_and_orientation": "VERIFIED",
            "twenty_four_visible_yellow_blue_cells": "VERIFIED",
            "prime_marker_correspondence": "STRONGLY SUPPORTED/PROMISING but conditional",
            "exclusive_cell_mask_for_matrixsumlist": "UNKNOWN",
            "yellow_blue_binary_encoding_values": "VERIFIED for the earlier URL decode",
            "yellow_blue_summation_weights": "UNKNOWN",
            "summation_axis": "UNKNOWN",
        },
        "result": "The source fixes the14x14 grid, its orientation, the24 visible yellow/blue coordinates, their spiral order, and their binary roles in the earlier URL. It does not say that only those cells are summed, does not bind encoding bits or any other color numbers as summation weights, and does not choose rows versus columns. The conditional25-event prime match adds evidence for a cross-object label sequence but relies on an unmentioned near-white event and several parsing conventions, so it cannot close those three interfaces.",
        "exact_missing_bindings": [
            "cell-domain rule: all196 cells versus visible yellow/blue cells versus conditional25-event frame",
            "numeric-type rule: binary bit versus color count, letter ordinal, RGB, or another value",
            "axis rule: rows, columns, both, or prior spiral/octet grouping",
        ],
        "next_test": "No parameter-free test on the original square matrix can distinguish rows from columns or choose a summation weight. Continue only if an authored source supplies at least one of the three missing bindings.",
        "new_image_variants": 0,
        "new_numeric_weight_sweeps": 0,
        "candidate_material_generated": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "original-matrix-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({
        "status": document["status"],
        "yellow_blue_cells": document["selected_cells"]["yellow_blue_count"],
        "url_binary_mapping_unique": document["verified_matrix"]["exact_url_mapping_match_count"] == 1,
        "sum_mask": document["classification"]["exclusive_cell_mask_for_matrixsumlist"],
        "sum_weights": document["classification"]["yellow_blue_summation_weights"],
        "sum_axis": document["classification"]["summation_axis"],
        "cryptographic_operations": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
