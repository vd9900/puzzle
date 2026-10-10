#!/usr/bin/env python3
"""Audit independently specified receivers for a hypothetical matrixsumlist output."""

import json

from tools.gsmg import ARTIFACTS
from tools.instruction_graphs import source, write_artifact


OUTPUT = ARTIFACTS / "cycle35"
ARCHITECTURE = ARTIFACTS / "cycle22/architecture-reconstruction-v3.json"
WIDTH = ARTIFACTS / "cycle24/matrix-width-interface.json"
OWNERSHIP = ARTIFACTS / "cycle17/operand-ownership.json"
HINT_ORDER = ARTIFACTS / "cycle11/hint-instruction-order.json"
WORDING = ARTIFACTS / "cycle34/matrixsumlist-wording-audit.json"


def report():
    architecture = json.loads(ARCHITECTURE.read_text())
    width = json.loads(WIDTH.read_text())
    ownership = json.loads(OWNERSHIP.read_text())
    hint = json.loads(HINT_ORDER.read_text())
    wording = json.loads(WORDING.read_text())

    objects = [
        {
            "id": item["id"],
            "size": item["exact_object"]["length"],
            "unit": item["exact_object"]["unit"],
            "type": item["type"],
            "known_downstream_consumers": item["known_downstream_consumers"],
        }
        for item in architecture["object_inventory"]
    ]
    exact14 = [item for item in objects if item["size"] == 14]
    matrixsumlist_object = next(item for item in objects if item["id"] == "matrixsumlist")
    if exact14 or matrixsumlist_object["known_downstream_consumers"]:
        raise ValueError("Recovered receiver inventory changed")

    observed = width["observed"]
    fixed_shapes = [
        {
            "candidate": "original grid row or column slots",
            "shape": [14, 14],
            "slot_counts": [14, 14],
            "independently_downstream_of_matrixsumlist": False,
            "explicit_input_contract": False,
            "classification": "UPSTREAM/SELF-DOMAIN, NOT A RECEIVER",
            "reason": "The grid is the proposed operand domain itself; no authored feedback edge consumes a derived list.",
        },
        {
            "candidate": "joined dbbi/raw-label panel",
            "shape": observed["joined_source_panel_shape"],
            "slot_counts": observed["joined_source_panel_shape"],
            "independently_downstream_of_matrixsumlist": False,
            "explicit_input_contract": False,
            "classification": "INFERRED UPSTREAM LAYOUT, NOT A RECEIVER",
            "reason": "The13x15 panel is an analyst reconstruction and matrixsumlist is part of its source material.",
        },
        {
            "candidate": "faed570 matrix",
            "shape": observed["faed_shape"],
            "slot_counts": observed["faed_shape"],
            "independently_downstream_of_matrixsumlist": False,
            "explicit_input_contract": False,
            "classification": "NO DIRECT14-SLOT CONTRACT",
            "reason": "Its derived axes are38 and15. Source adjacency supplies no add/select/reorder operation.",
        },
        {
            "candidate": "Bifid coordinate planes",
            "shape": observed["bifid_coordinate_plane_shapes"][0],
            "copies": len(observed["bifid_coordinate_plane_shapes"]),
            "slot_counts": observed["bifid_coordinate_plane_shapes"][0],
            "independently_downstream_of_matrixsumlist": False,
            "explicit_input_contract": False,
            "classification": "NO DIRECT14-SLOT CONTRACT",
            "reason": "Each plane has19 rows and15 columns. The recovered Bifid transform consumes faed plus its fixed square, not a sum list.",
        },
        {
            "candidate": "source-keyed Bifid square",
            "shape": [5, 5],
            "slot_counts": [25],
            "independently_downstream_of_matrixsumlist": False,
            "explicit_input_contract": True,
            "classification": "OCCUPIED INPUT CONTRACT",
            "reason": "The square is already deterministically supplied by dbbi first-occurrence order; replacing it would discard the verified dependency.",
        },
    ]

    interface_by_name = {item["interface"]: item for item in ownership["interfaces"]}
    architect = interface_by_name["Architect-selection"]
    first_hash = interface_by_name["first-hash-input"]
    answer_hash = interface_by_name["answer-hash-input"]
    typed_password = next(item for item in architecture["typed_compatibility"] if item["consumer"] == "password API or hash input")
    if any(item["input_ready"] for item in (architect, first_hash, answer_hash)):
        raise ValueError("Previously unresolved variable receiver became input-ready")

    variable_receivers = [
        {
            "candidate": "lastwordsbeforearchichoice / Architect selection",
            "accepts_variable_count_or_indices": True,
            "independent_source_identity": False,
            "explicit_matrixsumlist_binding": False,
            "unresolved_contract": architect["unresolved_bindings"],
            "support": "It is the next named clue in the verified February2023 mention order.",
            "classification": "WEAK/UNKNOWN POSSIBLE SEMANTIC RECEIVER",
        },
        {
            "candidate": "first SHA input",
            "accepts_variable_bytes": True,
            "independent_source_identity": False,
            "explicit_matrixsumlist_binding": False,
            "unresolved_contract": first_hash["unresolved_bindings"],
            "support": "A local SHA operator exists later in the primary source.",
            "classification": "TYPE-COMPATIBLE, NOT BOUND",
        },
        {
            "candidate": "answer SHA input",
            "accepts_variable_bytes": True,
            "independent_source_identity": False,
            "explicit_matrixsumlist_binding": False,
            "unresolved_contract": answer_hash["unresolved_bindings"],
            "support": "A second local SHA operator exists after the embedded container.",
            "classification": "TYPE-COMPATIBLE, NOT BOUND",
        },
        {
            "candidate": "password/hash byte API",
            "accepts_variable_bytes": True,
            "independent_source_identity": False,
            "explicit_matrixsumlist_binding": False,
            "unresolved_contract": ["input identity", "representation", "target association"],
            "support": typed_password["reason"],
            "classification": typed_password["status"],
        },
        {
            "candidate": "yinyang",
            "accepts_variable_bytes": None,
            "independent_source_identity": False,
            "explicit_matrixsumlist_binding": False,
            "unresolved_contract": ["object type", "input type", "operation", "consumer"],
            "support": "It follows the Architect clue in mention order but has no recovered typed interface.",
            "classification": "UNTYPED LABEL, NOT A RECEIVER CONTRACT",
        },
    ]

    next_after_matrixsumlist = hint["strongest_supported_clue_sequence"][2]
    if next_after_matrixsumlist != "lastwordsbeforearchichoice":
        raise ValueError("Ordered-hint successor changed")
    if wording["classification"]["cell_domain"] != "UNKNOWN" or wording["classification"]["numeric_interpretation"] != "UNKNOWN" or wording["classification"]["summation_axis"] != "UNKNOWN":
        raise ValueError("Cycle34 missing bindings changed")

    fixed_direct14 = [entry for entry in fixed_shapes if entry["independently_downstream_of_matrixsumlist"] and 14 in entry["slot_counts"]]
    variable_explicit = [entry for entry in variable_receivers if entry["explicit_matrixsumlist_binding"]]
    if fixed_direct14 or variable_explicit:
        raise ValueError("Unexpected independently specified receiver")

    return {
        "id": "C35-MATRIXSUMLIST-RECEIVER-AUDIT",
        "date": "2026-10-02",
        "status": "REJECTED",
        "hypothesis": "At least one recovered object independently specifies a receiver contract for a matrixsumlist output, including a14-value list or a genuinely bound variable-length input.",
        "invariant": "A receiver must be downstream independently of the proposed producer and specify accepted type/cardinality plus assignment semantics; equal size or a generic variable-byte API is insufficient.",
        "source_evidence": [source(path) for path in (ARCHITECTURE, WIDTH, OWNERSHIP, HINT_ORDER, WORDING)],
        "recovered_objects": {
            "count": len(objects),
            "objects": objects,
            "exact_size14_objects": exact14,
            "matrixsumlist_known_downstream_consumers": matrixsumlist_object["known_downstream_consumers"],
        },
        "fixed_shape_candidates": fixed_shapes,
        "fixed_shape_independent_direct14_receivers": fixed_direct14,
        "variable_length_candidates": variable_receivers,
        "variable_length_explicitly_bound_receivers": variable_explicit,
        "ordered_hint_successor": {
            "from": "matrixsumlist",
            "to": next_after_matrixsumlist,
            "relationship": "VERIFIED MENTION ORDER",
            "receiver_edge": "UNKNOWN",
            "reason": "The next clue names a word-selection problem but supplies no source, choice anchor, count, boundaries, or mapping from a numeric list.",
        },
        "faed_bifid_assessment": {
            "faed_shape": observed["faed_shape"],
            "bifid_plane_shapes": observed["bifid_coordinate_plane_shapes"],
            "fifteen_column_structure_verified": True,
            "fourteen_value_input_contract": False,
            "variable_length_input_contract": False,
            "matrixsumlist_binding": False,
            "classification": "STRUCTURALLY FIXED MATRICES, NOT INDEPENDENTLY SPECIFIED RECEIVERS",
        },
        "classification": {
            "recovered_exact14_receiver": "REJECTED",
            "faed_or_bifid_as_direct14_receiver": "REJECTED",
            "faed_or_bifid_as_forced15_receiver": "REJECTED without a source-defined15-value producer and operation",
            "Architect_words_as_receiver": "WEAK/UNKNOWN; strongest semantic candidate from mention order only",
            "hash_or_password_api_as_receiver": "TYPE-COMPATIBLE NOT BOUND",
            "independently_specified_receiver": "REJECTED within the preserved corpus",
            "matrixsumlist_output_consumer": "UNKNOWN",
        },
        "result": "No recovered object independently specifies a receiver for matrixsumlist output. There is no exact14-item recovered receiver. FAED/Bifid have fixed15-column geometry but no14-value port, no variable-length port, and no authored operation. Architect-word selection is the strongest semantic successor, yet all four of its source/count/boundary bindings remain missing. Hash/password APIs accept arbitrary bytes and therefore cannot discriminate the intended output.",
        "graph_effect": "Keep matrixsumlist -> unknown consumer. Retain a dashed WEAK mention-order edge to lastwordsbeforearchichoice; remove any asserted matrixsumlist -> FAED/Bifid or14->15 edge.",
        "next_test": "No further receiver test is justified from current objects. Resume only if new source evidence names a receiver or supplies an input contract; then test that single edge without dimension-forcing or cryptographic execution.",
        "numeric_sum_vectors_calculated": 0,
        "numeric_mapping_trials": 0,
        "candidate_material_generated": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "matrixsumlist-receiver-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({
        "status": document["status"],
        "exact14_receivers": len(document["fixed_shape_independent_direct14_receivers"]),
        "bound_variable_receivers": len(document["variable_length_explicitly_bound_receivers"]),
        "best_semantic_candidate": "lastwordsbeforearchichoice (WEAK/UNKNOWN)",
        "consumer": document["classification"]["matrixsumlist_output_consumer"],
        "cryptographic_operations": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
