import json
from collections import Counter
from datetime import datetime

from PIL import Image

from tools.gsmg import extract_grid, spiral_coordinates
from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle13"
IMAGES = {
    "original": ROOT / "research/sources/gsmg-puzzle.png",
    "cover": ROOT / "research/sources/maintained-hints__cosmic-duality-book.png",
    "cover_context": ROOT / "research/sources/maintained-hints__2022-12-10-cosmic.png",
}
COLOR_HINT_HEADER = "=== [14.01.2020 05:38:06 UTC-05:00] Jrk Bgrt"


def image_metadata(path):
    with Image.open(path) as image:
        metadata = {
            "source": source(path),
            "dimensions": list(image.size),
            "mode": image.mode,
            "metadata_keys": sorted(image.info),
            "software": image.info.get("Software"),
            "creation_time_literal": image.info.get("Creation Time"),
        }
    stamp = metadata["creation_time_literal"]
    parsed = datetime.strptime(stamp, "%a %d %b %Y %I:%M:%S %p") if stamp else None
    metadata["capture_time_without_timezone"] = parsed.isoformat() if parsed else None
    metadata["capture_metadata_is_not_hint_publication_time"] = True
    return metadata


def event_structure():
    grid = extract_grid(IMAGES["original"])
    colors = grid["colors"]
    coordinates = spiral_coordinates(14)
    events = []
    for index, (row, column) in enumerate(coordinates):
        color = colors[row][column]
        if color not in ("blue", "yellow", "near_white"):
            continue
        events.append({
            "row_zero_based": row,
            "column_zero_based": column,
            "color": color,
            "verified_spiral_index_zero_based": index,
            "verified_octet_index_zero_based": index // 8,
            "bit_position_in_octet_zero_based": index % 8,
        })
    return {
        "grid_dimensions": [14, 14],
        "color_counts": dict(Counter(color for row in colors for color in row)),
        "original_palette_rgb": {
            "black": [0, 0, 0], "white": [255, 255, 255],
            "blue": [63, 72, 204], "yellow": [255, 242, 0],
            "near_white": [254, 254, 254],
        },
        "special_event_source_map": events,
        "blue_yellow_event_count": sum(event["color"] != "near_white" for event in events),
        "blue_yellow_frame_offsets": sorted({event["bit_position_in_octet_zero_based"] for event in events if event["color"] != "near_white"}),
        "near_white_is_distinct_from_photographic_cover_highlights": True,
        "existing_grid_extraction_only": True,
        "no_new_image_variant_or_route": True,
    }


def color_wording():
    body, creator_location = record_by_header(CREATOR, COLOR_HINT_HEADER)
    chat_body, chat_location = record_by_header(CHAT, COLOR_HINT_HEADER)
    if body != chat_body:
        raise ValueError("Preserved color-hint exports disagree")
    phrase = "Yellow has a number and so does Blue."
    document = CREATOR.read_text()
    start, end = creator_location["character_span_zero_based_half_open"]
    phrase_start = document.index(phrase, start, end)
    return {
        "creator_labeled_export": creator_location,
        "full_transcript": chat_location,
        "phrase": phrase,
        "phrase_location": text_location(document, phrase_start, phrase_start + len(phrase)),
        "return_to_first_piece_literal": "Go back to the first puzzle piece without further ado." in body,
        "number_assignment_not_specified": True,
        "cover_mapping_not_specified": True,
        "matching_exports_not_independent_authentication": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle12/cover-reference.json"
    frozen = json.loads(preceding.read_text())
    if "Source-constrained visual correspondence audit" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding frozen experiment")
    structure = event_structure()
    if structure["color_counts"] != {"white": 85, "black": 86, "blue": 15, "yellow": 9, "near_white": 1}:
        raise ValueError("Original source image differs from the verified grid")
    relations = [
        {"relation": "cover title to primary Cosmic Duality heading", "status": "SUPPORTED_TEXTUAL_CORRESPONDENCE", "limitation": "A shared title is not a decoding or a stage-placement rule"},
        {"relation": "two contrasting lobes to yin-yang wording", "status": "QUALITATIVE_VISUAL_CORRESPONDENCE", "limitation": "No literal token, operation, orientation or operand is specified"},
        {"relation": "cover warm/cool fields to original yellow/blue cells", "status": "QUALITATIVE_ONLY", "limitation": "Photographed fields do not share an authored exact palette or weighting rule"},
        {"relation": "two visually salient cover highlights to all original special events", "status": "REJECTED_UNCONDITIONAL_BIJECTION", "limitation": "Two reference highlights cannot bijectively index24 blue/yellow or25 total special events; no source selection of two events is supplied"},
        {"relation": "nested cover rectangles to verified grid spiral", "status": "QUALITATIVE_ONLY", "limitation": "No author-supplied correspondence between decorative frames and traversal direction/start exists in the inspected evidence"},
        {"relation": "cover geometry to residual60/61 or faed570", "status": "MISSING_RULE", "limitation": "Neither preserved image context nor the color wording specifies a symbol-to-pixel map or a consuming operation"},
    ]
    return {
        "id": "C13-VISUAL-CORRESPONDENCE", "date": "2026-09-30", "status": "INCONCLUSIVE",
        "hypothesis": "A source-authored cover-to-original-image correspondence can specify the missing construction before any new decoding",
        "source_evidence": [source(path) for path in IMAGES.values()] + [source(CREATOR), source(CHAT), source(preceding), source(ROOT / "research/sources/salphaseion.html")],
        "source_locations": ["research/sources/maintained-hints__cosmic-duality-book.png", "research/sources/maintained-hints__2022-12-10-cosmic.png", "research/sources/gsmg-puzzle.png", "research/evidence/cycle02/_work__creator_jrk.txt:196", "research/sources/salphaseion.html:19"],
        "assumptions": ["The preserved cover is the visually corresponding community attachment, not hash-authenticated original bytes", "Two conspicuous cover highlights are qualitative reference features, not a count of every star", "Existing source grid extraction and traversal are verified for the original binary layer only"],
        "operation_order": ["inspect only original preserved images", "read capture metadata separately from publication provenance", "map existing grid events in its verified traversal", "bind exact color wording to its dated source", "check six fixed correspondences without fitting a transformation"],
        "input": "Three fixed preserved images and one dated public color hint",
        "output": "Metadata, exact grid-event locations and six correspondence decisions; no decoded trial material",
        "confidence": "HIGH for metadata/source counts; MEDIUM for visual analogy; UNKNOWN for the mathematical construction",
        "images": {name: image_metadata(path) for name, path in IMAGES.items()},
        "grid": structure,
        "color_wording": color_wording(),
        "cover_visual_observations": ["Two interlocking warm/cool curved fields", "Two conspicuous opposite-color highlights", "Nested rectangular border decoration"],
        "cover_visual_observations_are_not_pixel_segmentation": True,
        "correspondences": relations,
        "result": "Title/duality correspond qualitatively, but no exact spatial, numeric or stage mapping is established. PNG capture metadata dates both cover captures to August21 2023 without timezone; it does not redetermine the December2022 hint date.",
        "contradictions": ["Cover highlight references and original event counts differ", "No source selects two original events", "Yellow/blue wording assigns no numeric values or cover mapping", "Photographic appearance and screenshot capture times cannot be treated as authored data instructions"],
        "next_test": "Discriminate literal yin-yang output from a visual object or next-phase label using original dated checkpoint wording and its full conversation context; retain missing reply bindings.",
        "search_space": {"fixed_images": 3, "fixed_color_hint": 1, "correspondence_checks": 6},
        "new_image_variants": 0, "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "visual-correspondence.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "fixed_correspondence_checks": len(document["correspondences"]), "explicit_decoding_mapping": False, "new_image_variants": 0, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
