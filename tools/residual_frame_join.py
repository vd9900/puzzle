import json
from hashlib import sha256

from tools.analyze_salphaseion import split_segments
from tools.instruction_graphs import ROOT, source, write_artifact
from tools.prime_markers import is_prime


OUTPUT = ROOT / "research/artifacts/cycle23"
ALPHABET25 = "abcdefghiklmnopqrstuvwxyz"
NEXT_TEST = (
    "Audit whether the exact 25 ordered event identities supply a source-defined permutation or selector "
    "for the 25 first-occurrence square symbols. Use only preserved order/position fields and reject a "
    "mapping if it merely pairs equal-sized lists by index. Do not generate alternate squares, routes, "
    "passwords or cryptographic trials."
)


def join_tokens(residual_by_position, event_bits, logical_length):
    prime_positions = [position for position in range(1, logical_length + 1) if is_prime(position)]
    if len(prime_positions) != len(event_bits):
        raise ValueError("Event labels do not cover the logical prime positions exactly")
    residual_positions = sorted(residual_by_position)
    if set(prime_positions) & set(residual_positions):
        raise ValueError("Prime and residual positions overlap")
    if set(prime_positions) | set(residual_positions) != set(range(1, logical_length + 1)):
        raise ValueError("Prime and residual positions do not cover the logical domain")
    if any(bit not in (0, 1, "0", "1") for bit in event_bits):
        raise ValueError("Event labels must be binary")

    event_by_position = dict(zip(prime_positions, (int(bit) for bit in event_bits)))
    tokens = []
    for position in range(1, logical_length + 1):
        if position in event_by_position:
            bit = event_by_position[position]
            tokens.append({"logical_position_one_based": position, "token": "b" if bit else "be", "owner": "event-label", "semantic_bit": bit})
        else:
            token = residual_by_position[position]
            if not isinstance(token, str) or not token:
                raise ValueError("Residual tokens must be nonempty strings")
            tokens.append({"logical_position_one_based": position, "token": token, "owner": "residual", "semantic_bit": None})
    return tokens


def square_with_ownership(tokens):
    seen = set()
    first = []
    raw_offset = 0
    for token in tokens:
        for token_offset, symbol in enumerate(token["token"]):
            if symbol not in seen:
                seen.add(symbol)
                first.append({
                    "symbol": symbol,
                    "owner": token["owner"],
                    "logical_position_one_based": token["logical_position_one_based"],
                    "token_offset_zero_based": token_offset,
                    "reconstructed_raw_offset_zero_based": raw_offset + token_offset,
                })
        raw_offset += len(token["token"])
    square = "".join(entry["symbol"] for entry in first)
    square += "".join(symbol for symbol in ALPHABET25 if symbol not in seen)
    return square, first


def report():
    coordinate_path = OUTPUT / "coordinate-interface.json"
    maps_path = ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json"
    architecture_path = ROOT / "research/artifacts/cycle22/architecture-reconstruction-v3.json"
    frame_path = ROOT / "research/artifacts/cycle15/frame-object-audit.json"
    coordinate = json.loads(coordinate_path.read_text())
    maps = json.loads(maps_path.read_text())
    architecture = json.loads(architecture_path.read_text())
    frame = json.loads(frame_path.read_text())
    if coordinate["next_test"] != (
        "Test one exact information-preserving join, not a new cipher: combine the frozen residual60 with the first23 already-aligned semantic event labels at the one-based prime positions of the inferred83-token domain, interpreting labels only as the existing b/be token grammar. Compare the resulting source object and its first-occurrence dependency ownership against original dbbi91 and the frozen square projection. Keep the final two binary-label markers separate. Do not vary colors, positions, branches, alphabets, periods or representations. An exact source match supplies a reversible source join, not a downstream input assignment or intent proof; a mismatch falsifies that join. Check previous coverage before executing."
    ):
        raise ValueError("Unexpected frozen residual/frame join task")

    branch = next(entry for entry in maps["derived_source_maps"]["branches"] if entry["mask"] == 1017)
    if branch["logical_length"] != 83 or branch["residual_length"] != 60:
        raise ValueError("Unexpected frozen residual branch")
    residual_by_position = {
        entry["logical_position_one_based"]: entry["symbol"]
        for entry in branch["residual_source_map"]
    }
    events = architecture["event_identity_domain_reused"]["events"]
    if len(events) != 25 or [entry["event_index_zero_based"] for entry in events] != list(range(25)):
        raise ValueError("Unexpected frozen event domain")
    semantic_bits = [1 if event["color"] in ("blue", "near_white") else 0 for event in events]
    tokens = join_tokens(residual_by_position, semantic_bits[:23], branch["logical_length"])
    reconstructed = "".join(entry["token"] for entry in tokens)
    original = split_segments()["dbbi"]
    square, first_occurrences = square_with_ownership(tokens)
    expected_square = architecture["square_projection_reused"]["key_square"]
    original_prime_tokens = {entry["logical_position_one_based"]: entry["token"] for entry in branch["prime_marker_source_map"]}
    joined_prime_tokens = {entry["logical_position_one_based"]: entry["token"] for entry in tokens if entry["owner"] == "event-label"}
    final_markers = architecture["event_identity_domain_reused"]["prime_markers"][23:]
    selection_caveat = (
        "The mask1017 tokenization and near-white=1 semantic convention were selected by the earlier "
        "cross-artifact match. This audit proves reversibility under that frozen construction; it is not "
        "independent evidence that the creator intended the join."
    )
    return {
        "id": "C23-RESIDUAL-FRAME-JOIN",
        "date": "2026-10-02",
        "status": "CONFIRMED" if reconstructed == original and square == expected_square else "REJECTED",
        "hypothesis": "Residual60 plus the first23 ordered image-event semantic labels losslessly reconstructs the mask1017 dbbi logical-token object and its source-derived Bifid square",
        "source_evidence": [source(path) for path in (coordinate_path, maps_path, architecture_path, frame_path, ROOT / "research/sources/gsmg-puzzle.png", ROOT / "research/sources/salphaseion.html")],
        "source_locations": [
            "research/artifacts/cycle10/instruction-graphs-v3.json",
            "research/artifacts/cycle15/frame-object-audit.json",
            "research/artifacts/cycle22/architecture-reconstruction-v3.json",
            "research/sources/gsmg-puzzle.png",
            "research/sources/salphaseion.html:17",
        ],
        "assumptions": [
            "Frozen mask1017 provides an83-token one-based logical domain",
            "Blue=1, yellow=0 and near-white=1 use the already selected semantic convention",
            "At prime positions semantic1 maps to token b and semantic0 maps to token be",
            "The final two event labels remain attached to the following binary region and are not inserted into dbbi",
        ],
        "operation_order": [
            "load the frozen60 nonprime tokens with logical positions",
            "derive the first23 semantic bits from the ordered original image events",
            "map1 to b and0 to be at the23 prime positions in1..83",
            "interleave prime and nonprime tokens without changing their order",
            "concatenate83 tokens and compare all91 raw source letters",
            "derive first-occurrence ownership and compare the fixed25-symbol square",
        ],
        "input": "Frozen residual60 with logical positions plus first23 frozen image-event semantic labels",
        "output": "Reconstructed83-token/91-letter dbbi source object and first-occurrence ownership map",
        "confidence": "HIGH for exact conditional reconstruction; UNKNOWN for creator intent or downstream use",
        "information_accounting": {
            "logical_domain": 83,
            "residual_tokens": len(residual_by_position),
            "prime_event_labels_used": 23,
            "semantic_one_tokens": semantic_bits[:23].count(1),
            "semantic_zero_tokens_expanding_to_be": semantic_bits[:23].count(0),
            "reconstructed_raw_letters": len(reconstructed),
            "original_raw_letters": len(original),
            "final_binary_region_labels_kept_separate": len(final_markers),
        },
        "reconstruction": {
            "raw_sha256": sha256(reconstructed.encode()).hexdigest(),
            "original_raw_sha256": sha256(original.encode()).hexdigest(),
            "exact_raw_match": reconstructed == original,
            "exact_prime_token_match": joined_prime_tokens == original_prime_tokens,
            "all_logical_positions_accounted_once": len(tokens) == 83 and len({entry["logical_position_one_based"] for entry in tokens}) == 83,
            "tokens": tokens,
        },
        "square_dependency": {
            "derived_square": square,
            "expected_square": expected_square,
            "exact_match": square == expected_square,
            "first_occurrences": first_occurrences,
            "observed_symbols_owned_by_residual": [entry["symbol"] for entry in first_occurrences if entry["owner"] == "residual"],
            "observed_symbols_owned_by_event_labels": [entry["symbol"] for entry in first_occurrences if entry["owner"] == "event-label"],
        },
        "final_two_boundary_markers": final_markers,
        "selection_caveat": selection_caveat,
        "graph_effect": "Add a conditional reversible edge residual60 + first23 semantic event labels -> dbbi91 -> first-occurrence square25. Keep the final two boundary markers, faed570/Bifid570, matrixsumlist operator and every downstream consumer edge separate and unresolved.",
        "result": "The exact conditional join reconstructs all83 logical tokens and all91 raw dbbi letters. It also reproduces the fixed Bifid square: residual tokens supply d/i/f/h/c/g/a, while event labels supply the first b/e. This closes an information-accounting gap but does not identify a password, matrix operator, or terminal consumer.",
        "contradictions": [
            selection_caveat,
            "The join reconstructs an already public source object, so it does not by itself create new entropy or a new downstream input",
            "The two remaining event labels belong to absolute prime positions89 and97 in the binary region and do not complete a25-symbol square assignment",
        ],
        "next_test": NEXT_TEST,
        "search_space": {"frozen_branches": 1, "logical_positions": 83, "residual_tokens": 60, "event_labels": 23, "label_mappings": 1, "alternate_orders": 0},
        "new_cryptographic_trials": 0,
        "new_trial_inputs": 0,
        "new_image_variants": 0,
        "hypotheses": [],
    }


def main():
    document = report()
    write_artifact(OUTPUT / "residual-frame-join.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({
        "status": document["status"],
        "exact_raw_match": document["reconstruction"]["exact_raw_match"],
        "exact_square_match": document["square_dependency"]["exact_match"],
        "new_cryptographic_trials": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
