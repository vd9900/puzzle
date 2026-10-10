#!/usr/bin/env python3
"""Audit known 15-slot receivers without instantiating numeric values."""

from collections import Counter
import json
from pathlib import Path

from tools.gsmg import ARTIFACTS, SOURCES, extract_grid


def report():
    architecture_path = ARTIFACTS / "cycle22/architecture-reconstruction-v3.json"
    frame_path = ARTIFACTS / "cycle15/frame-object-audit.json"
    bip39_path = ARTIFACTS / "cycle28/btcseed-format-contract.json"
    architecture = json.loads(architecture_path.read_text())
    frame = json.loads(frame_path.read_text())
    bip39 = json.loads(bip39_path.read_text())

    inventory = architecture["object_inventory"]
    objects = [
        {
            "id": item["id"],
            "size": item["exact_object"]["length"],
            "unit": item["exact_object"]["unit"],
            "type": item["type"],
        }
        for item in inventory
    ]
    exact_fifteen_objects = [item["id"] for item in objects if item["size"] == 15]

    events = frame["image"]["events"]
    colors = Counter(event["color"] for event in events)
    blue = [event for event in events if event["color"] == "blue"]
    grid = extract_grid(SOURCES / "gsmg-puzzle.png")
    decoded = grid["decoded"]
    blue_octets = [event["verified_octet_index_zero_based"] for event in blue]
    odd_ascii_octets = [index for index, character in enumerate(decoded) if ord(character) & 1]
    if blue_octets != odd_ascii_octets:
        raise ValueError("Blue events are no longer exactly the URL terminal-one bits")
    if not all(event["bit_position_in_octet_zero_based"] == 7 for event in blue):
        raise ValueError("A blue event is no longer an octet terminal bit")

    blue_rows = [event["row_zero_based"] for event in blue]
    blue_columns = [event["column_zero_based"] for event in blue]
    bip39_counts = bip39["official_contracts"]["BIP39"]["mnemonic_word_counts"]

    return {
        "id": "C32-FIFTEEN-RECEIVER-AUDIT",
        "date": "2026-10-02",
        "status": "REJECTED",
        "hypothesis": "An already recovered public puzzle object supplies an independently typed fifteen-slot receiver for the fifteen dependency-preserving Bifid groups.",
        "invariant": "A native receiver must expose fifteen distinct slots independently of the producer and supply a source-backed assignment rule; equal cardinality alone is insufficient.",
        "recovered_object_inventory": {
            "objects_checked": len(objects),
            "object_sizes": {item["id"]: {"size": item["size"], "unit": item["unit"]} for item in objects},
            "exact_size15_objects": exact_fifteen_objects,
        },
        "blue_event_candidate": {
            "all_event_count": len(events),
            "color_counts": dict(sorted(colors.items())),
            "blue_event_count": len(blue),
            "blue_octet_indices_zero_based": blue_octets,
            "blue_events_are_exactly_terminal_one_bits": True,
            "odd_ascii_octet_indices_zero_based": odd_ascii_octets,
            "independent_of_existing_url_decode": False,
            "unique_image_rows": len(set(blue_rows)),
            "unique_image_columns": len(set(blue_columns)),
            "image_coordinate_domain": [14, 14],
            "direct_distinct_column_slots": len(set(blue_columns)),
            "direct_bijection_to15_bifid_columns": False,
            "ordinal_pairing_requires_new_assignment": True,
        },
        "external_standard_candidate": {
            "name": "BIP39 mnemonic",
            "allowed_word_counts": bip39_counts,
            "fifteen_is_allowed": 15 in bip39_counts,
            "recovered_public_puzzle_object": False,
            "source_authored_binding": False,
        },
        "classification": {
            "known_recovered_fixed_size15_receiver": "REJECTED: zero objects in the frozen recovered-object inventory have size15",
            "ordered_blue_events_as_direct_receiver": "REJECTED: the15 blue events are exactly the existing URL bytes with terminal bit1 and expose only10 distinct image columns",
            "blue_event_ordinal_to_bifid_column_pairing": "UNKNOWN/WEAK: a bijection can be imposed by ordinal, but no public rule assigns it",
            "bip39_as_receiver": "WEAK:15 is valid externally, but BIP39 is not a recovered puzzle object and no authored binding exists",
        },
        "graph_effect": "Do not add a Bifid15-groups to blue15-events edge. The blue cardinality is a dependent property of the existing URL decode, not an independent15-slot receiver. No internal recovered receiver remains for the proposed list.",
        "exact_remaining_unknown": "A downstream receiver type or authored assignment is absent. The only exact15 compatibility found is an external BIP39 format, whose use would require creating and checking candidate indices under an unbound numeric map.",
        "next_test": "Stop structural execution unless new source evidence names a fifteen-slot receiver or binds matrixsumlist to a numeric map. Do not infer a receiver from cardinality alone.",
        "numeric_sum_vectors_calculated": 0,
        "numeric_mapping_trials": 0,
        "candidate_lists_generated": 0,
        "mnemonic_words_generated": 0,
        "checksum_tests": 0,
        "seed_derivations": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
