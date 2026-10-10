import json
from datetime import datetime

from PIL import Image

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle18"
RECORDS = [
    ("FIRST_PIECE_MULTIPLE_DOOR_WARNING", "=== [14.01.2020 05:38:06 UTC-05:00] Jrk Bgrt", ["Go back to the first puzzle piece without further ado.", "It might have shown you only one door, beware that the rabbits nest may contain a whole lot more."]),
    ("SECOND_DOOR_STATEMENT", "=== [11.05.2020 15:31:25 UTC-05:00] Jrk Bgrt", ["who knows what you'll find after opening the 2nd door"]),
    ("EXTRA_DOOR_STATEMENT", "=== [02.08.2020 11:56:20 UTC-05:00] Jrk Bgrt", ["Really nobody managed to find the extra door"]),
]


def mapped_records():
    document = CREATOR.read_text()
    mapped = []
    for name, header, phrases in RECORDS:
        body, location = record_by_header(CREATOR, header)
        original_body, original_location = record_by_header(CHAT, header)
        if body != original_body:
            raise ValueError("Creator-attributed body differs between exports")
        start = location["character_span_zero_based_half_open"][0]
        anchors = []
        for phrase in phrases:
            offset = start + body.index(phrase)
            anchors.append({"literal": phrase, **text_location(document, offset, offset + len(phrase))})
        mapped.append({
            "name": name, "creator_record": location, "original_chat_record": original_location,
            "phrase_maps": anchors,
            "matching_exports_are_not_independent_authentication": True,
            "no_explicit_source_url_container_or_branch_count": True,
        })
    times = [datetime.fromisoformat(entry["creator_record"]["archived_utc_timestamp"]) for entry in mapped]
    if times != sorted(times):
        raise ValueError("Unexpected original door chronology")
    return {
        "records": mapped,
        "first_warning_precedes_May_and_August_statements": True,
        "whole_lot_more_is_not_an_exact_door_count": True,
        "second_and_extra_are_not_explicitly_equal_references": True,
        "first_piece_is_named_but_the_word_matrix_is_not_in_the_warning": True,
        "no_index_origin_or_traversal_defined": True,
    }


def warning_screenshot():
    path = ROOT / "research/sources/maintained-hints__2020-01-14-roses-are-red.png"
    with Image.open(path) as picture:
        dimensions = list(picture.size)
    return {
        "source": source(path), "dimensions": dimensions,
        "human_visual_locator_xyxy": [67, 118, 521, 163],
        "visible_public_warning": "It might have shown you only one door, beware that the rabbits nest may contain a whole lot more.",
        "visible_speaker_admin_label": "Jrk Bgrt/admin",
        "visible_warning_below_first_piece_return_instruction": True,
        "complete_warning_visible_not_only_three_color_lines": True,
        "screenshot_displayed_time_0338_timezone_not_given": True,
        "locator_not_OCR_or_source_selection_rule": True,
    }


def declared_topologies():
    return [
        {"id": "C18-DOOR-ALTERNATIVE-ENTRANCES", "hypothesis": "The first-piece/rabbits-nest warning allows more than one entrance or derivation associated with an original source object", "edges": [["first-puzzle-piece", "known-entry", "ALREADY_DOCUMENTED_ROUTE"], ["first-puzzle-piece", "unidentified-other-entry", "POSSIBLE_MULTIPLE_ENTRANCE_NOT_DERIVED"]], "assumptions": ["The first warning describes source-associated alternatives rather than later stages", "An alternate entrance can coexist with the known route"], "confidence": "MEDIUM first-warning grammar; UNKNOWN entrance identity", "contradictions": ["No operation or other-entry location is named", "The original source object could be broader than the14x14 matrix", "Completed variants/routes remain negative and are not reopened"]},
        {"id": "C18-DOOR-SERIAL-STAGES", "hypothesis": "Second/extra doors describe later serial stage entrances rather than a fork in the initial artifact", "edges": [["known-entry", "unidentified-second-stage", "POSSIBLE_SERIAL_STAGE"], ["unidentified-second-stage", "unidentified-later-stage", "UNKNOWN_SERIALITY"]], "assumptions": ["Door is a stage-entrance metaphor", "Second denotes local progression, not source alternatives"], "confidence": "MEDIUM later-stage wording; LOW unique serial placement", "contradictions": ["First-piece warning explicitly returns to an earlier source", "Extra is not explicitly assigned to second or a later stage", "No original statement names the embedded containers in this graph"]},
        {"id": "C18-DOOR-THEMATIC", "hypothesis": "Door language is a thematic warning about hidden puzzle structure without specifying a graph operation", "edges": [["door-metaphor", "unspecified-puzzle-structure", "THEMATIC_REFERENCE_WITHOUT_EXECUTABLE_EDGE"]], "assumptions": ["The metaphor need not define source dependency edges", "Further exact instructions may be needed to operationalize it"], "confidence": "MEDIUM conservative semantic reading; UNKNOWN intended structure", "contradictions": ["Repeated source-return and extra-door statements may be operative", "The December2021 reiteration preserves another-door relevance", "A thematic reading does not explain the numeric door groups"]},
    ]


def report():
    preceding = ROOT / "research/artifacts/cycle18/final-reference-audit-v2.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C18-FINAL-REFERENCE" or "multiple-door warning" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen topology task")
    door = ROOT / "research/artifacts/cycle17/door-reference-audit.json"
    saved_door = json.loads(door.read_text())
    evidence = [source(path) for path in (
        CHAT, CREATOR, ROOT / "research/sources/maintained-hints__2020-01-14-roses-are-red.png",
        ROOT / "research/artifacts/cycle17/operand-ownership.json", door, preceding,
    )]
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:195", "research/evidence/cycle02/_work__creator_jrk.txt:199", "research/evidence/cycle02/_work__creator_jrk.txt:363", "research/evidence/cycle02/_work__creator_jrk.txt:411", "research/evidence/cycle02/_work__chat_transcript.txt:3941", "research/evidence/cycle02/_work__chat_transcript.txt:9450", "research/evidence/cycle02/_work__chat_transcript.txt:10401", "research/sources/maintained-hints__2020-01-14-roses-are-red.png"]
    hypotheses = [topology | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["map complete first-piece warning", "compare dated second/extra wording", "retain only declared topology without identifying an entrance"],
        "input": "Original public door statements and one full-warning screenshot",
        "output": "A finite topology interpretation, not a derived alternate entrance",
        "next_test": "Audit preserved primary page/image references for the exact domain of first-piece and rabbits-nest; distinguish original image, containing webpage and later page labels before any new transformation",
    } for topology in declared_topologies()]
    return {
        "id": "C18-DOOR-TOPOLOGY", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Full creator-attributed door statements select serial versus alternative-entrance topology for the intended construction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Repeated metaphor and chronology are constraints, not complete executable graph definitions", "Only three declared topology readings are compared", "First-piece source domain may be broader than one matrix representation"],
        "operation_order": ["validate frozen topology task", "cross-check three original dated bodies", "map four exact public phrase anchors", "identify the full-warning screenshot region", "reuse later door relevance without repeating its date audit", "compare three finite topology readings"],
        "input": "Full original first-piece warning, later second/extra-door statements and preserved image",
        "output": "Exact source-bound topology constraints and three unresolved semantic graphs",
        "confidence": "HIGH statement/screenshot identity; UNKNOWN unique intended topology",
        "chronology": mapped_records(), "warning_screenshot": warning_screenshot(),
        "later_door_source_reused": {"source": source(door), "December_reiteration_preserves_relevance": saved_door["records"]["December2021_reiteration_rules_out_dismissing_door_only_as_a_joke"], "no_numeric_door_interpretation_retested": True},
        "hypotheses": hypotheses,
        "result": "Full January2020 warning returns to the first puzzle piece and says it may have shown only one door while the rabbits nest may contain more. May second-door and August extra-door statements are later, unnamed and not explicitly the same entrance. Screenshot visibly contains the full warning. This weakens an assumed single serial chain but does not prove a fork or identify source/object/operation/count. Alternative-entrance, serial-stage and thematic readings survive; no alternate source route or container binding derived.",
        "contradictions": ["A repeated door metaphor does not define an executable source transformation", "Second and extra are not explicitly co-referent", "No named source domain identifies matrix versus image/page", "Missing topology edges cannot be supplied by completed search negatives"],
        "next_test": "Perform one bounded primary-source domain audit for first-puzzle-piece/rabbits-nest: exact original webpage image references, preserved original-image region ownership and separate later page headings. Determine which sources are explicitly named or merely inferred; no hidden-system access, image edits, route trials or trial-text generation.",
        "search_space": {"creator_bodies_cross_checked": 3, "fixed_public_phrase_anchors": 4, "complete_warning_screenshots": 1, "declared_topology_readings": 3, "new_alternate_entry_trials": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "door-topology.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "declared_topology_readings": 3, "unique_topology_or_entrance_bound": False, "new_alternate_entry_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
