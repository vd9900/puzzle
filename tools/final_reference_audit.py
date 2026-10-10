import json

from PIL import Image

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle18"
FINAL_PHRASES = [
    "wewontgiveawaythepassword",
    "itsinfrontofyoureyesbutyourenotseeingit",
    "verylaststepisatruegiveawaypromised",
]


def preserved_clauses():
    path = ROOT / "research/artifacts/cycle11/hint-instruction-order.json"
    hint = json.loads(path.read_text())
    binary = hint["binary_hint"]
    decoded = binary["decoded_public_text"]
    clauses = [entry for entry in binary["phrase_regions"] if entry["phrase"] in FINAL_PHRASES]
    if [entry["phrase"] for entry in clauses] != FINAL_PHRASES:
        raise ValueError("Unexpected frozen final-clause order")
    for entry in clauses:
        start, end = entry["decoded_span_zero_based_half_open"]
        if decoded[start:end] != entry["phrase"]:
            raise ValueError("Frozen decoded clause source span differs")
    return {
        "frozen_source": source(path), "original_creator_source": binary["source"],
        "original_header": binary["source_header"], "classification": binary["classification"],
        "clauses": clauses,
        "decoded_source_span_zero_based_half_open": [62, 161],
        "password_is_lexically_named_before_it": True,
        "it_has_no_explicit_page_image_or_stage_name": True,
        "verylaststep_is_not_assigned_to_a_named_container": True,
        "giveaway_lexical_echo_is_not_an_algorithm_or_output_format": True,
        "spaced_sentence_punctuation_is_not_encoded": True,
        "no_hint_binary_decoding_repeated": True,
    }


def visible_regions():
    image_path = ROOT / "research/sources/gsmg-puzzle.png"
    with Image.open(image_path) as picture:
        dimensions = list(picture.size)
    regions = [
        ("GRID_AND_RABBIT", [0, 0, 1048, 1048], "Original14x14 colored/achromatic grid with central rabbit"),
        ("CHALLENGE_TITLE_AND_LOGO", [0, 1065, 1048, 1275], "Visible challenge title and logo beneath the grid"),
        ("QR_AND_PUBLIC_IDENTIFIER", [0, 1275, 1048, 1556], "Visible QR symbol and public identifier, not decoded or used for matching"),
    ]
    if dimensions != [1048, 1556]:
        raise ValueError("Unexpected original image dimensions")
    for unused_name, (left, top, right, bottom), unused_description in regions:
        if not 0 <= left < right <= dimensions[0] or not 0 <= top < bottom <= dimensions[1]:
            raise ValueError("Image region locator outside original bounds")
    layout = json.loads((ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json").read_text())["primary_layout"]
    return {
        "original_image_source": source(image_path), "original_dimensions": dimensions,
        "human_visual_region_locators": [{"region": name, "approximate_pixel_rectangle_xyxy": rectangle, "description": description} for name, rectangle, description in regions],
        "locators_are_not_exact_OCR_boxes_or_selection_masks": True,
        "all_regions_are_simultaneously_visible_not_a_unique_look_here_selector": True,
        "current_primary_page_headings": layout["headings"],
        "current_primary_literal_SMALL": layout["small_literal_present"],
        "current_primary_literal_HASHTHETEXT": layout["hashtext_literal_present"],
        "no_qr_or_identifier_decoding_matching_or_use": True,
        "no_new_pixel_variant_traversal_or_selected_text": True,
    }


def secondary_visible_text_interpretation():
    path = ROOT / "research/sources/maintained-README.md"
    document = path.read_text()
    literal = "Using everything we have so far, it points us back to the original image to hash the text on the image"
    if document.count(literal) != 1:
        raise ValueError("Unexpected secondary entry-route explanation")
    start = document.index(literal)
    graph = json.loads((ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json").read_text())
    hashtext = graph["corroboration"]["hashtext"]
    return {
        "source": source(path), "short_public_literal": literal,
        "source_location": text_location(document, start, start + len(literal)),
        "classification": "SECONDARY_DOCUMENTED_ENTRY_ROUTE_ARGUMENT_INTERPRETATION",
        "earlier_audio_command_argument_not_encoded": hashtext["argument_not_encoded_in_this_instruction"],
        "an_earlier_entry_route_does_not_identify_a_later_selected_object": True,
        "old_entry_transform_not_reexecuted": True,
    }


def separate_btc_question():
    header = "=== [03.08.2023 14:51:33 UTC-05:00] Jrk Bgrt"
    creator_body, location = record_by_header(CREATOR, header)
    chat_body, chat_location = record_by_header(CHAT, header)
    if creator_body != chat_body or creator_body != "Are you really looking for just the btc...?":
        raise ValueError("Unexpected separate creator-attributed question")
    return {
        "creator_record": location, "original_chat_record": chat_location,
        "exact_public_question": creator_body,
        "classification": "CREATOR_ATTRIBUTED_QUESTION_NOT_EXPLICIT_BIFID_VALIDATION",
        "does_not_literally_name_Bifid_residual_or_btcseed": True,
        "no_reply_target_or_recipe_confirmation": True,
        "separate_date_and_wording_not_the_final_hint_clause": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle18/template-format-scope.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C18-TEMPLATE-FORMAT-SCOPE" or "fixed spatial-reference audit" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding frozen task")
    evidence = [source(path) for path in (
        ROOT / "research/artifacts/cycle11/hint-instruction-order.json",
        ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json",
        ROOT / "research/sources/gsmg-puzzle.png", ROOT / "research/sources/maintained-README.md",
        CHAT, CREATOR, preceding,
    )]
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:711", "research/evidence/cycle02/_work__creator_jrk.txt:745", "research/sources/maintained-README.md:158", "research/sources/gsmg-puzzle.png", "research/sources/salphaseion.html:17"]
    hypotheses = []
    for suffix, hypothesis, confidence, assumptions, contradictions in [
        ("FINAL-REFERENCE-VISIBLE", "The final it-in-front-of-your-eyes clause asks the solver to recognize an existing visible object rather than generate new transformations", "MEDIUM lexical recognition cue; UNKNOWN object", ["It refers to the named password object", "Visibility is literal or structural, not a new cipher family"], ["No image/page/stage named", "Several primary image/page regions are simultaneously visible", "Recognition cue supplies no exact source/count/format"]),
        ("FINAL-REFERENCE-STRUCTURAL", "In-front-of-your-eyes refers to an already derived intermediate structure or label relationship rather than original image footer text", "LOW-MEDIUM compatible structural reference", ["Visibility may be figurative after reconstructing a known intermediate", "A later exact construction resolves the pronoun"], ["No intermediate is explicitly named", "A Bifid prefix or partial language match cannot validate the complete object", "No stated bridge from label structure to final output"]),
        ("FINAL-REFERENCE-PROMISE", "Very-last-step true-giveaway is a final-stage promise, not an instruction defining output encoding or a selection algorithm", "HIGH lexical promise observation; UNKNOWN final operation", ["Promised qualifies stage difficulty/recognizability rather than an operator", "Giveaway repeats narrative language, not a named cipher"], ["Could encode a secondary clue implicitly", "No exact final-stage boundaries/consumer supplied", "A separate btc question does not validate Bifid or fix the output type"]),
    ]:
        hypotheses.append({
            "id": "C18-" + suffix, "status": "INCONCLUSIVE", "hypothesis": hypothesis,
            "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions,
            "operation_order": ["map frozen final clause positions", "compare bounded visible/structural referent", "retain missing source and output identity without extraction"],
            "input": "Original public final-hint clauses and preserved image/page layout",
            "output": "A referent/recognition constraint, not a selected text object",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Audit the full original first-piece multiple-door warning plus later second/extra-door statements as topology constraints, reusing completed checkpoint semantics rather than repeating reached/hit analysis",
        })
    return {
        "id": "C18-FINAL-REFERENCE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Final visibility/giveaway wording uniquely identifies an existing source object and final consumer",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Only fixed preserved clauses/layout and a separate dated question are compared", "Human region locators are approximate visual aids, not pixel extraction rules", "Earlier documented entry-route argument cannot be silently reused as a final argument"],
        "operation_order": ["validate frozen referent task", "reuse three original clause maps", "locate three original-image regions and current page headings", "map one secondary entry-route interpretation", "cross-check separate creator question", "compare three finite referents without selected text"],
        "input": "Public decoded clue/source maps and original visible artifacts",
        "output": "Exact clause provenance and bounded referent ambiguity audit",
        "confidence": "HIGH source/clause identity; UNKNOWN intended visible object",
        "clauses": preserved_clauses(), "visible_regions": visible_regions(),
        "secondary_entry_interpretation": secondary_visible_text_interpretation(),
        "separate_question": separate_btc_question(), "hypotheses": hypotheses,
        "result": "Frozen final clauses name password before it, but no image/page/stage or selection/count rule. Original image has simultaneously visible grid/rabbit, title/logo and QR/public-identifier regions; no unique object chosen. Current primary headings do not literally name SMALL or HASHTHETEXT. Secondary entry-route visible-text interpretation is not a final-argument binding. Separate August2023 btc question does not name Bifid/residual/btcseed. Recognition/structural/promise readings survive without new extraction.",
        "contradictions": ["A spatial pronoun with no named source cannot uniquely select an object", "Visibility and giveaway promises do not define serialization or final consumer", "Separate creator question is not exact recipe confirmation"],
        "next_test": "Map the full creator-attributed January2020 first-piece/multiple-door warning and dated May/August2020 second/extra-door statements. Compare only serial-stage, alternative-entrance and thematic-door graph roles, reusing already frozen April/December2021 door references. Do not infer a branch count, identify containers from adjacency or repeat existing checkpoint analyses.",
        "review_correction": "First snapshot's prospective checkpoint-grammar task overlapped completed cycle13 semantics. Preserve that snapshot; current v2 instead follows the unexamined full first-piece multiple-door warning as a topology question.",
        "search_space": {"frozen_final_clauses": 3, "original_visible_image_regions": 3, "secondary_entry_prose_anchors": 1, "separate_creator_question_cross_checked": 1, "finite_referent_hypotheses": 3, "new_pixel_or_text_selections": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "final-reference-audit-v2.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "source_object_uniquely_bound": False, "new_pixel_or_text_selections": 0, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
