import json
from collections import Counter

from tools.instruction_graphs import ROOT, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle23"
NEXT_TEST = "Test one exact information-preserving join, not a new cipher: combine the frozen residual60 with the first23 already-aligned semantic event labels at the one-based prime positions of the inferred83-token domain, interpreting labels only as the existing b/be token grammar. Compare the resulting source object and its first-occurrence dependency ownership against original dbbi91 and the frozen square projection. Keep the final two binary-label markers separate. Do not vary colors, positions, branches, alphabets, periods or representations. An exact source match supplies a reversible source join, not a downstream input assignment or intent proof; a mismatch falsifies that join. Check previous coverage before executing."


def direct_coordinate_membership(coordinates, side):
    if not isinstance(side, int) or isinstance(side, bool) or side < 1:
        raise ValueError("Coordinate domain requires a positive integer side")
    if any(len(coordinate) != 2 or any(not isinstance(value, int) or isinstance(value, bool) for value in coordinate) for coordinate in coordinates):
        raise ValueError("Expected integer row/column coordinate pairs")
    inside = [index for index, (row, column) in enumerate(coordinates) if 0 <= row < side and 0 <= column < side]
    multiplicities = Counter(tuple(coordinate) for coordinate in coordinates)
    unique_inside = {tuple(coordinates[index]) for index in inside}
    target = {(row, column) for row in range(side) for column in range(side)}
    return {
        "source_count": len(coordinates), "target_count": side * side,
        "in_domain_source_indices": inside,
        "out_of_domain_source_indices": [index for index in range(len(coordinates)) if index not in inside],
        "unique_source_coordinates": len(multiplicities),
        "duplicate_coordinate_multiplicities": [{"coordinate": list(coordinate), "count": count} for coordinate, count in sorted(multiplicities.items()) if count > 1],
        "covered_target_coordinates": len(unique_inside),
        "direct_bijection": len(coordinates) == side * side and len(multiplicities) == len(coordinates) and unique_inside == target,
        "no_coordinate_conversion_attempted": True,
    }


def label_information(values, target_symbols=25):
    counts = Counter(values)
    return {
        "source_labels": len(values), "distinct_labels": len(counts),
        "multiplicities": dict(sorted(counts.items())),
        "can_be25_distinct_symbols_without_position_or_extra_information": len(values) == target_symbols and len(counts) == target_symbols,
        "repeated_labels_do_not_destroy_original_event_identity": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle22/architecture-reconstruction-v3.json"
    loss_path = ROOT / "research/artifacts/cycle22/sumlist-information.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C22-ARCHITECTURAL-RECONSTRUCTION" or "static coordinate-interface test" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen coordinate-interface task")
    event_domain = frozen["event_identity_domain_reused"]
    events = event_domain["events"]
    markers = event_domain["prime_markers"]
    square = frozen["square_projection_reused"]["key_square"]
    if len(events) != 25 or len(markers) != 25 or len(square) != 25 or len(set(square)) != 25:
        raise ValueError("Unexpected frozen25-element domains")
    if [entry["event_index_zero_based"] for entry in events] != list(range(25)) or [entry["event_index_zero_based"] for entry in markers] != list(range(25)):
        raise ValueError("Frozen event identities are not a complete ordered domain")
    coordinates = [(entry["row_zero_based"], entry["column_zero_based"]) for entry in events]
    original_domain = direct_coordinate_membership(coordinates, 14)
    square_domain = direct_coordinate_membership(coordinates, 5)
    if original_domain["out_of_domain_source_indices"] or original_domain["unique_source_coordinates"] != 25:
        raise ValueError("Frozen original image coordinate identities differ")
    label_projections = {
        "colors": label_information([entry["color"] for entry in events]),
        "original_binary_bits": label_information([str(entry["original_binary_bit"]) for entry in events]),
        "semantic_prime_labels": label_information([entry["bit"] for entry in markers]),
    }
    comparisons = [{"event_index_zero_based": index, "original_image_coordinate": list(coordinates[index]),
                    "original_color": event["color"], "original_binary_bit": event["original_binary_bit"],
                    "semantic_prime_label_bit": int(marker["bit"]),
                    "marker_source": marker, "direct_square_coordinate_in_domain": index in square_domain["in_domain_source_indices"],
                    "order_pairing_preserved_not_new_authorship": True}
                   for index, (event, marker) in enumerate(zip(events, markers))]
    evidence = [source(path) for path in (preceding, loss_path, ROOT / "research/artifacts/cycle15/frame-object-audit.json", ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json", ROOT / "research/sources/gsmg-puzzle.png", ROOT / "research/sources/salphaseion.html")]
    return {
        "id": "C23-DIRECT-COORDINATE-INTERFACE", "date": "2026-10-02", "status": "REJECTED",
        "hypothesis": "Original25 image-event coordinates or their color/bit labels directly specify the source-keyed25-cell Bifid square without another conversion object",
        "source_evidence": evidence,
        "source_locations": ["research/artifacts/cycle22/architecture-reconstruction-v3.json", "research/artifacts/cycle15/frame-object-audit.json", "research/artifacts/cycle10/instruction-graphs-v3.json", "research/sources/gsmg-puzzle.png", "research/sources/salphaseion.html:17"],
        "assumptions": ["Direct coordinate lookup means identical zero-based row/column domains, not a guessed reduction", "Colors and bits are projections, not event IDs", "Pairing event index with square index would be an additional unbound assignment, not a coordinate-preserving map"],
        "operation_order": ["validate frozen25 event/marker identities and25-symbol square", "check original14x14 coordinate membership", "check direct5x5 membership without conversion", "count only existing color/bit label multiplicities", "preserve all25 exact tuple/marker pairings", "reject direct lookup edge without rejecting a possible later conversion"],
        "input": "Frozen original image event tuples, aligned prime markers and source-derived square",
        "output": "Finite domain/multiplicity counterexamples, no decoded or trial text",
        "confidence": "HIGH narrow domain/information failure; UNKNOWN intended metadata role",
        "expected_observable": "25 distinct source coordinates cover exactly the25 existing target cells, or25 labels are already distinct target symbols",
        "falsification_condition": "Any out-of-domain coordinate, incomplete coverage, collision or fewer than25 distinct label values",
        "original_domain": original_domain, "direct_square_domain": square_domain,
        "label_projections": label_projections, "ordered_event_marker_records": comparisons,
        "square_domain": {"rows": 5, "columns": 5, "distinct_symbols": 25, "source_defined_conversion_from_image_coordinates": None},
        "graph_effect": "Remove only original image coordinates/color-or-bit labels -> direct25-cell square lookup. Retain complete event identities, existing order correspondence and an explicitly missing conversion/assignment edge; reject neither coordinate metadata nor parallel architecture generally.",
        "result": "Direct lookup fails: only events6/11/19 fit the5x5 coordinate domain;22 are outside. Original coordinates are25 distinct tuples in14x14, whereas colors have3 values and bit projections2. Equal cardinality does not supply a target-coordinate conversion or an ordered symbol assignment. No modulo, ranking, normalization, lookup output or cipher trial is produced.",
        "contradictions": ["An independently sourced conversion could define a future lookup", "Event-index ->square-index pairing is always mathematically possible but not source-defined here", "Label collisions do not invalidate distinct full event identities"],
        "next_test": NEXT_TEST,
        "search_space": {"frozen_events": 25, "frozen_markers": 25, "direct_coordinate_domains": 2, "existing_label_projections": 3, "coordinate_conversions": 0, "square_variants": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_image_variants": 0,
        "hypotheses": [],
    }


def main():
    document = report()
    write_artifact(OUTPUT / "coordinate-interface.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "direct_square_bijection": document["direct_square_domain"]["direct_bijection"], "out_of_domain_coordinates": len(document["direct_square_domain"]["out_of_domain_source_indices"]), "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
