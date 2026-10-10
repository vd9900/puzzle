import json
from collections import Counter

from tools.gsmg import extract_grid, spiral_coordinates
from tools.instruction_graphs import ROOT, primary_layout, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle15"
FROZEN = ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json"
IMAGE = ROOT / "research/sources/gsmg-puzzle.png"


def image_frame_map():
    frozen_image = ROOT / "research/artifacts/cycle13/visual-correspondence.json"
    saved = json.loads(frozen_image.read_text())["grid"]["special_event_source_map"]
    grid = extract_grid(IMAGE)
    coordinates = spiral_coordinates(14)
    events = []
    for event_index, entry in enumerate(saved):
        row, column = entry["row_zero_based"], entry["column_zero_based"]
        spiral_index = entry["verified_spiral_index_zero_based"]
        frame_index = entry["verified_octet_index_zero_based"]
        if coordinates[spiral_index] != (row, column) or grid["colors"][row][column] != entry["color"]:
            raise ValueError("Frozen image event no longer matches the original image")
        bits = "".join(str(grid["matrix"][frame_row][frame_column]) for frame_row, frame_column in coordinates[frame_index * 8:frame_index * 8 + 8])
        decoded_character = chr(int(bits, 2))
        if decoded_character != grid["decoded"][frame_index]:
            raise ValueError("Source octet does not reproduce its existing public character")
        events.append(entry | {
            "event_index_zero_based": event_index,
            "original_binary_bit": grid["matrix"][row][column],
            "verified_source_octet_bits": bits,
            "verified_source_character": decoded_character,
            "classification": "ORIGINAL_IMAGE_EVENT_IN_EXISTING_VERIFIED_TRAVERSAL",
        })
    counts = Counter(entry["verified_octet_index_zero_based"] for entry in events)
    return {
        "source": source(IMAGE), "frozen_source": source(frozen_image),
        "events": events, "event_count": len(events), "decoded_octet_count": len(grid["decoded"]),
        "events_per_decoded_octet": [counts[index] for index in range(len(grid["decoded"]))],
        "events_in_four_bit_tail": 0,
        "blue_yellow_events_label_all24_octets_once": len({entry["verified_octet_index_zero_based"] for entry in events if entry["color"] in ("blue", "yellow")}) == len(grid["decoded"]),
        "near_white_is_an_extra_event_not_an_extra_octet": True,
        "no_changed_pixel_or_decoded_text_generated": True,
    }


def branch_label_map(branch, compact, span):
    markers = []
    for rank, entry in enumerate(branch["prime_marker_source_map"]):
        start, end = entry["normalized_span_zero_based_half_open"]
        token = compact[start:end]
        if token != entry["token"] or token not in ("b", "be"):
            raise ValueError("Frozen prime marker source differs")
        markers.append(entry | {
            "event_index_zero_based": rank, "region": "dbbi",
            "semantic_label_bit": 1 if token == "b" else 0,
            "label_rule": "DOCUMENTED_B_EQUALS_BLUE_1_BE_EQUALS_YELLOW_0_NOT_CELL_WEIGHTS",
        })
    for prime_position in (89, 97):
        binary_offset = prime_position - branch["logical_length"] - 1
        raw_offset = 91 + binary_offset
        token = compact[raw_offset]
        if token not in ("a", "b"):
            raise ValueError("Existing boundary marker is not a binary symbol")
        markers.append({
            "event_index_zero_based": len(markers), "region": "matrixsumlist-binary",
            "logical_position_one_based": prime_position,
            "token": token, "semantic_label_bit": int(token == "b"),
            "binary_offset_zero_based": binary_offset,
            "encoded_label_character_index_zero_based": binary_offset // 8,
            "encoded_label_bit_offset_zero_based": binary_offset % 8,
            "label_rule": "EXISTING_BINARY_LABEL_A0_B1_CONTINUING_LOGICAL_COUNTER",
            **span(raw_offset, raw_offset + 1),
        })
    return {"mask": branch["mask"], "logical_length": branch["logical_length"], "residual_length": branch["residual_length"], "residual_sha256": branch["residual_sha256"], "markers": markers}


def report():
    preceding = ROOT / "research/artifacts/cycle14/speech-delta.json"
    frozen_task = json.loads(preceding.read_text())
    if frozen_task["id"] != "C14-SPEECH-DELTA" or "image/frame-to-prime-marker labeling" not in frozen_task["next_test"]:
        raise ValueError("Unexpected preceding frozen experiment")
    frozen = json.loads(FROZEN.read_text())
    unused_layout, compact, span = primary_layout()
    image = image_frame_map()
    branches = []
    for branch in frozen["derived_source_maps"]["branches"]:
        mapped = branch_label_map(branch, compact, span)
        comparisons = []
        for event, marker in zip(image["events"], mapped["markers"]):
            semantic_bit = 1 if event["color"] in ("blue", "near_white") else 0
            comparisons.append({
                "event_index_zero_based": event["event_index_zero_based"],
                "image_event": event, "source_marker": marker,
                "existing_semantic_event_label_bit": semantic_bit,
                "semantic_label_matches": marker["semantic_label_bit"] == semantic_bit,
                "original_binary_bit_matches": marker["semantic_label_bit"] == event["original_binary_bit"],
                "near_white_semantic_assignment_is_assumed_not_original_binary": event["color"] == "near_white",
            })
        if len(comparisons) != 25:
            raise ValueError("Fixed source map should account for25 events")
        branches.append(mapped | {
            "comparisons": comparisons,
            "semantic_mismatch_event_indices": [entry["event_index_zero_based"] for entry in comparisons if not entry["semantic_label_matches"]],
            "original_binary_mismatch_event_indices": [entry["event_index_zero_based"] for entry in comparisons if not entry["original_binary_bit_matches"]],
            "borrowed_boundary_bits": [entry["semantic_label_bit"] for entry in mapped["markers"] if entry["region"] == "matrixsumlist-binary"],
        })
    selected = next(branch for branch in branches if branch["mask"] == 1017)
    for audited, saved in zip(selected["markers"], frozen["derived_source_maps"]["continuous_frame"]["source_map"]):
        if audited["normalized_span_zero_based_half_open"] != saved["normalized_span_zero_based_half_open"] or audited["semantic_label_bit"] != int(saved["bit"]):
            raise ValueError("The existing continuous frame attribution differs")
    first, second = branches
    differences = []
    for older, newer in zip(first["markers"], second["markers"]):
        if older["token"] != newer["token"] or older["normalized_span_zero_based_half_open"] != newer["normalized_span_zero_based_half_open"]:
            differences.append({"event_index_zero_based": older["event_index_zero_based"], "505_token": older["token"], "1017_token": newer["token"], "505_span": older["normalized_span_zero_based_half_open"], "1017_span": newer["normalized_span_zero_based_half_open"], "same_bit_value": older["semantic_label_bit"] == newer["semantic_label_bit"]})
    evidence = [source(IMAGE), source(ROOT / "research/sources/salphaseion.html"), source(FROZEN), source(preceding), source(ROOT / "research/artifacts/cycle03/prime-boundary.json")]
    locations = ["research/sources/gsmg-puzzle.png", "research/sources/salphaseion.html:17", "research/artifacts/cycle10/instruction-graphs-v3.json:1", "research/artifacts/cycle03/prime-boundary.json:1"]
    hypotheses = []
    for suffix, claim, assumptions, confidence, contradictions in [
        ("FRAME-LABELS", "Blue/yellow cells are per-octet labels, with near-white an additional event-level discriminator", ["The existing verified traversal is the intended event order", "Documented b/be labels are intended color references"], "HIGH for source coverage; MEDIUM for intended label role", ["Source establishes24 per-octet positions but not their downstream consumer", "Near-white still needs an explicit semantic convention", "No matrixsumlist operand or serialization follows"]),
        ("NEARWHITE-ROLE", "Near-white is an extra semantic marker rather than a decoded byte or a verified changed binary bit", ["Near-white remains a distinct original color", "The historical semantic1 assignment is conditional, not a pixel change"], "HIGH for original bit0/event structure; UNKNOWN for intended operation", ["Semantic1 differs from the original source bit0", "No instruction to invert this source pixel", "Both frozen branches need the same near-white convention; it alone does not choose a residual"]),
        ("BRANCH-DISCRIMINATOR", "The frozen residual branch distinction is the prime83 b-versus-be token, not the two borrowed boundary bits", ["Only the existing505/1017 branch conventions are compared", "Borrowed markers retain their region-specific binary mapping"], "HIGH for fixed-branch witness; no creator-intent proof", ["Borrowed b/a label values are identical for both branches", "Only one terminal prime label differs", "The full semantic match depends on prior near-white/counter conventions, not independent confirmation"]),
    ]:
        hypotheses.append({"id": "C15-" + suffix, "status": "INCONCLUSIVE", "hypothesis": claim, "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions, "operation_order": ["map existing original events", "map only fixed prime-marker branches", "compare labels separately from original binary bits", "retain missing operation/consumer"], "input": "Existing source event/marker identities, not new trial text", "output": "Typed label constraints and fixed-branch witnesses", "confidence": confidence, "contradictions": contradictions, "next_test": "Inspect source-authored boundary/normalization rules that could bind a sumlist object to these labels; no new route, weight or extraction without a consumer"})
    return {
        "id": "C15-FRAME-OBJECT-AUDIT", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Existing image-frame and prime-marker identities constrain object roles more directly than another sum algorithm",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Two frozen branch conventions only", "All semantic mappings remain historical hypotheses", "Existing source traversal is reused without variants"],
        "operation_order": ["read frozen task/source maps", "map25 original events to24 decoded octets", "map two frozen prime-label branches and existing89/97 boundary markers", "compare semantic labels separately from original binary bits", "identify exact branch differences"],
        "input": "One unchanged original image, frozen25-event map and two documented marker branches",
        "output": "Source-bound event/octet identities, semantic-versus-bit comparisons and branch discriminators",
        "confidence": "HIGH for exact fixed comparisons; MEDIUM for labels as intended objects; UNKNOWN for construction",
        "image": image, "branches": branches, "branch_differences": differences,
        "near_white_case": selected["comparisons"][20],
        "boundary_bits_discriminate_branches": first["borrowed_boundary_bits"] != second["borrowed_boundary_bits"],
        "full_semantic_match_is_not_independent_of_historical_conventions": True,
        "source_maps_reproduce_saved_continuous_frame": True,
        "hypotheses": hypotheses,
        "result": "Blue/yellow labels cover24 octets once; near-white is extra in the same n octet as a yellow label. Its source bit is0 while historical semantic label is1. Frozen505/1017 differ semantically only at event22/logical prime83;89/97 borrowed b/a bits match for both and do not independently select a branch. No new operation or sumlist object is established.",
        "contradictions": ["25 events are not25 decoded bytes", "Semantic labels are not all original decoded bits", "Cell weighting does not follow from a label match", "Borrowed bits do not distinguish the two frozen branches", "No consumer joins labels/residual/Bifid to matrixsumlist"],
        "next_test": "Audit primary source boundary/type semantics around matrixsumlist: distinguish a delimiter or object label from data at that same position, and identify whether source-authored instructions define which representation/operand a later consumer accepts. Use exact original boundaries and existing transforms only.",
        "search_space": {"fixed_images": 1, "fixed_event_maps": 1, "frozen_branches": 2, "events_per_branch": 25, "comparisons": 50, "new_tokenizations": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_image_variants": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "frame-object-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "fixed_event_comparisons": 50, "boundary_bits_discriminate_branches": document["boundary_bits_discriminate_branches"], "near_white_original_bit": document["near_white_case"]["image_event"]["original_binary_bit"], "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
