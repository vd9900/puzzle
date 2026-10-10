import json
from itertools import combinations

from tools.architecture_reconstruction import NEXT_TEST
from tools.instruction_graphs import ROOT, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle22"


def rectangle_witnesses(matrix, protected):
    size = len(matrix)
    if size < 2 or any(len(row) != size for row in matrix):
        raise ValueError("Expected a square source matrix with at least two rows")
    if any(not isinstance(value, int) or value < 0 for row in matrix for value in row):
        raise ValueError("Expected nonnegative integer source values")
    if any(not 0 <= row < size or not 0 <= column < size for row, column in protected):
        raise ValueError("Protected source coordinate lies outside the matrix")
    witnesses = []
    checked = 0
    for top, bottom in combinations(range(size), 2):
        for left, right in combinations(range(size), 2):
            checked += 1
            cells = ((top, left), (top, right), (bottom, left), (bottom, right))
            if any(cell in protected for cell in cells):
                continue
            values = [matrix[row][column] for row, column in cells]
            if values not in ([0, 1, 1, 0], [1, 0, 0, 1]):
                continue
            deltas = [1 - 2 * value for value in values]
            if deltas[0] + deltas[1] or deltas[2] + deltas[3] or deltas[0] + deltas[2] or deltas[1] + deltas[3]:
                raise ValueError("Rectangle certificate does not preserve both axes")
            witnesses.append({"source_cells_row_column_zero_based": [list(cell) for cell in cells],
                              "original_values": values, "symbolic_balance_deltas": deltas,
                              "all_four_cells_are_non_event_black_white": True,
                              "both_row_and_column_totals_preserved": True,
                              "all25_event_values_coordinates_and_identities_unchanged": True})
    return {"rectangles_checked": checked, "ambiguity_certificates": len(witnesses),
            "first_deterministic_certificate": witnesses[0] if witnesses else None,
            "no_changed_matrix_or_image_constructed": True,
            "no_witness_does_not_prove_uniqueness": True}


def report():
    preceding = ROOT / "research/artifacts/cycle22/architecture-reconstruction-v3.json"
    reconstruction = json.loads(preceding.read_text())
    if reconstruction["id"] != "C22-ARCHITECTURAL-RECONSTRUCTION":
        raise ValueError("Unexpected architecture checkpoint")
    matrix_path = ROOT / "research/artifacts/cycle11/weighted-conservation.json"
    frame_path = ROOT / "research/artifacts/cycle15/frame-object-audit.json"
    frozen = json.loads(matrix_path.read_text())
    frame = json.loads(frame_path.read_text())
    matrix = frozen["weighted_matrix"]
    protected = {(entry["row_zero_based"], entry["column_zero_based"]) for entry in frame["image"]["events"]}
    if len(matrix) != 14 or len(protected) != 25:
        raise ValueError("Unexpected frozen original matrix/event domains")
    result = rectangle_witnesses(matrix, protected)
    if result["first_deterministic_certificate"] is None:
        raise ValueError("No expected fixed-axis ambiguity certificate found")
    evidence = [source(path) for path in (preceding, matrix_path, frame_path, ROOT / "research/sources/gsmg-puzzle.png", ROOT / "research/sources/salphaseion.html")]
    return {
        "id": "C22-SUMLIST-INFORMATION", "date": "2026-10-01", "status": "REJECTED",
        "hypothesis": "Both literal original-image axis-sum lists and the complete25-event frame uniquely encode the original matrix without any other object",
        "source_evidence": evidence,
        "source_locations": ["research/artifacts/cycle11/weighted-conservation.json", "research/artifacts/cycle15/frame-object-audit.json", "research/sources/salphaseion.html:17", "research/sources/gsmg-puzzle.png"],
        "assumptions": ["Both original row and column sum vectors are available, stronger than a single axis", "All25 special event values, colors, coordinates and ordered identities are fixed", "Remaining black/white cells are binary and not fixed by an additional output constraint", "No original image text decoding or alternate image is performed"],
        "operation_order": ["reuse frozen original matrix and event tuples", "enumerate exactly8281 source-coordinate rectangles", "exclude any protected event cell", "recognize existing alternating binary rectangles", "verify four symbolic row/column balance equations", "record only a losslessness counterexample certificate"],
        "input": "Untouched frozen14x14 matrix plus25 protected original event coordinates",
        "output": "A deterministic four-cell ambiguity certificate; no transformed data or trial input",
        "confidence": "HIGH narrow non-uniqueness proof; UNKNOWN intended operator role",
        "expected_observable": "If uniquely encoded, no distinct binary assignment can preserve both sum vectors and all protected events",
        "falsification_condition": "A non-event alternating2x2 rectangle supplies a distinct valid assignment with unchanged sums/frame",
        "certificate": result,
        "result": "REJECTED narrowly: a four-cell balance certificate preserves every row/column sum and all25 fixed events while allowing distinct non-event binary values. Literal sums plus the complete event frame are not a lossless original-matrix codec. This does not reject sums as metadata, selectors or constraints supplemented by another object.",
        "graph_effect": "Delete the direct axis-sums-plus-frame -> unique-original-matrix edge; retain lossy metadata and explicitly constrained reconstruction alternatives",
        "contradictions": ["Additional source text/ASCII constraints could distinguish the assignments but are not part of this claim", "Non-uniqueness does not identify the intended consumer", "Other weighted colors or matrix sources require separate source ownership; no variants tested"],
        "next_test": NEXT_TEST,
        "search_space": {"original_matrices": 1, "protected_event_cells": 25, "source_coordinate_rectangles": 8281, "graph_edge_hypotheses": 1},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_image_variants": 0,
        "hypotheses": [],
    }


def main():
    document = report()
    write_artifact(OUTPUT / "sumlist-information.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "rectangles_checked": document["certificate"]["rectangles_checked"], "ambiguity_certificates": document["certificate"]["ambiguity_certificates"], "new_image_variants": 0}, indent=2))


if __name__ == "__main__":
    main()
