import json
import re
from datetime import datetime

from PIL import Image

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle17"
DOOR_HEADER = "=== [01.04.2021 01:57:38 UTC-05:00] Jrk Bgrt"
RAB_HEADER = "=== [01.04.2021 08:29:41 UTC-05:00] Jrk Bgrt"
CONTEXT_HEADERS = [
    "=== [01.04.2021 02:50:36 UTC-05:00] Deleted Account",
    "=== [01.04.2021 03:15:19 UTC-05:00] omaru",
    "=== [01.04.2021 03:34:22 UTC-05:00] Jrk Bgrt",
    "=== [16.03.2024 06:34:59 UTC-05:00] Deleted Account",
]


def fixed_records():
    creator_body, creator_location = record_by_header(CREATOR, DOOR_HEADER)
    chat_body, chat_location = record_by_header(CHAT, DOOR_HEADER)
    rab_body, rab_location = record_by_header(CREATOR, RAB_HEADER)
    original_rab_body, original_rab_location = record_by_header(CHAT, RAB_HEADER)
    if creator_body != chat_body or rab_body != original_rab_body:
        raise ValueError("Creator and original-chat source bodies differ")
    if creator_body != 'Hint: "another door might be found on {1 },{4} ,{21}"':
        raise ValueError("Unexpected original door-hint spacing")
    document = CREATOR.read_text()
    start = creator_location["character_span_zero_based_half_open"][0]
    groups = []
    for match in re.finditer(r"\{([^}]*)\}", creator_body):
        groups.append({
            "literal": match.group(), "interior": match.group(1),
            "numeric_value": int(match.group(1)),
            **text_location(document, start + match.start(), start + match.end()),
        })
    if [entry["numeric_value"] for entry in groups] != [1, 4, 21]:
        raise ValueError("Unexpected fixed brace numbers")
    parsed = datetime.fromisoformat(creator_location["archived_utc_timestamp"])
    context = []
    for header in CONTEXT_HEADERS:
        body, location = record_by_header(CHAT, header)
        context.append({"record": location, "classification": "CREATOR_ATTRIBUTED_CONTEXT_NOT_REPLY_BINDING" if header.endswith("Jrk Bgrt") else "COMMUNITY_INTERPRETATION_OR_QUESTION", "short_public_text": body, "reply_target_metadata_preserved": False})
    elapsed = datetime.fromisoformat(rab_location["archived_utc_timestamp"]) - parsed
    return {
        "creator_record": creator_location, "original_chat_record": chat_location,
        "exact_public_hint": creator_body, "brace_groups": groups,
        "same_bodies_in_both_exports": True,
        "archived_UTC_date": parsed.date().isoformat(),
        "day_month_shortyear_components": [parsed.day, parsed.month, parsed.year % 100],
        "brace_values_match_archived_day_month_shortyear": [entry["numeric_value"] for entry in groups] == [parsed.day, parsed.month, parsed.year % 100],
        "month_day_reading_is_valid_but_not_selected": "2021-01-04",
        "author_timezone_not_proven_from_archive_offset": True,
        "rab_creator_record": rab_location, "rab_original_chat_record": original_rab_location,
        "rab_exact_body": rab_body, "seconds_door_to_rab": int(elapsed.total_seconds()),
        "rab_message_is_distinct_not_same_hint": True,
        "context": context,
        "December2021_reiteration_rules_out_dismissing_door_only_as_a_joke": True,
        "reiteration_does_not_select_date_coordinates_or_indexing": True,
    }


def screenshot_identity():
    path = ROOT / "research/sources/maintained-hints__2021-04-01-april_fool.png"
    with Image.open(path) as screenshot:
        dimensions = list(screenshot.size)
    return {
        "source": source(path), "dimensions": dimensions,
        "visual_reading": "Jrk Bgrt/admin; R=18, A=1, B=2; Could also be21 or1812 bit; displayed07:29 AM",
        "visually_matches_distinct_rab_message": True,
        "does_not_display_braced_door_hint": True,
        "time_display_timezone_not_encoded": True,
        "displayed_time_does_not_override_archived_timestamp": True,
        "secondary_filename_april_fool_is_not_creator_authentication": True,
        "visual_reading_is_human_not_machine_OCR": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle17/zeroing-chronology.json"
    task = json.loads(preceding.read_text())
    if task["id"] != "C17-ZEROING-CHRONOLOGY" or "exact prior another-door hint" not in task["next_test"]:
        raise ValueError("Unexpected preceding frozen experiment")
    evidence = [source(path) for path in (
        CHAT, CREATOR, ROOT / "research/sources/maintained-hints__2021-04-01-april_fool.png",
        ROOT / "research/artifacts/cycle14/source-binding-audit.json", preceding,
    )]
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:534", "research/evidence/cycle02/_work__chat_transcript.txt:16719", "research/evidence/cycle02/_work__creator_jrk.txt:540", "research/evidence/cycle02/_work__chat_transcript.txt:16782", "research/sources/maintained-hints__2021-04-01-april_fool.png"]
    hypotheses = []
    for suffix, hypothesis, confidence, assumptions, contradictions in [
        ("DOOR-DATE", "Brace groups1/4/21 reference the archived April1 2021 date rather than a literal data index", "MEDIUM exact date correspondence; UNKNOWN location/consumer", ["The hint intentionally encodes a date", "Day/month/short-year convention is intended"], ["Month/day convention yields another valid date", "Community March31 publication claim has no preserved author-timezone proof", "December reiteration does not establish how a date finds a door"]),
        ("DOOR-COORDINATES", "Brace groups refer to source coordinates or indexed objects but require an independently defined source and origin", "LOW without dimension/source/origin", ["Braces group selectors rather than date fields", "An external source schema fixes three coordinate roles"], ["No source, dimensions, coordinate units or indexing origin is named", "21 cannot be a direct row or column of the14x14 image", "Different source types could accommodate21 but no type is selected"]),
        ("DOOR-NAMED-OBJECTS", "Brace groups identify stage/object labels rather than arithmetic or a new traversal", "LOW without an authored label namespace", ["Puzzle objects have an intended numbering scheme", "Stage and object labels can be distinguished without trying permutations"], ["No explicit three-part namespace or stage map supplied", "Primary numeric labels elsewhere may have different roles", "Same-day R/A/B message and screenshot are distinct, not a definition of the door braces"]),
    ]:
        hypotheses.append({
            "id": "C17-" + suffix, "status": "INCONCLUSIVE", "hypothesis": hypothesis,
            "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions,
            "operation_order": ["bind exact original brace wording", "preserve timestamp convention and same-day context", "compare only the declared semantic reading", "require authored source and units before interpreting selectors"],
            "input": "Public door-hint text, preserved timestamp and distinct screenshot/message",
            "output": "A semantic reference hypothesis, not a new route, selection or trial string",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Compare fixed numeric/name-selector notation in preserved earlier public phase text with the door braces; require matching grammatical roles before assigning any source indices",
        })
    return {
        "id": "C17-DOOR-REFERENCE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Exact previous-door wording selects a date, coordinate or named-object interpretation for the unresolved construction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Archived offsets establish preserved dates, not the author's original timezone", "A secondary screenshot filename cannot authenticate an April-Fools-only interpretation", "Same-day co-occurrence is weaker than explicit definition or reply binding"],
        "operation_order": ["bind two exact creator messages in two exports", "map three brace source spans", "compare four fixed context records", "identify the screenshot as the distinct R/A/B message", "retain three semantic interpretations without selection"],
        "input": "Original public text, archived creator/context records and one preserved image",
        "output": "Exact punctuation/date/image correspondence and three finite door-reference hypotheses",
        "confidence": "HIGH original wording/distinct screenshot identity; UNKNOWN intended source selectors",
        "records": fixed_records(), "screenshot": screenshot_identity(), "hypotheses": hypotheses,
        "result": "Original {1 },{4} ,{21} values match April1 2021 in the preserved day/month/year timestamp. This supports a date reading but does not define a door location; author timezone and month/day ambiguity remain. Screenshot depicts a distinct R/A/B message23523 seconds later, not the braced hint. December reiteration prevents dismissing the hint solely as an April-Fools joke. Coordinate/object readings require missing source/schema/origin; no route or indices tested.",
        "contradictions": ["Date coincidence does not supply an operation or source", "Same-day screenshot is not the earlier door-hint image", "21 is incompatible only with a direct14x14 row/column, not all possible object indices", "Reiteration does not affirm an exact date/index interpretation"],
        "next_test": "Perform a fixed public-text notation comparison: earlier phase2/phase3 numeric name selectors and existing brace punctuation versus the door's1/4/21 groups. Determine whether a shared grammatical namespace is actually authored; do not invent numbering, choose a new traversal or extract trial material.",
        "search_space": {"creator_messages_cross_checked": 2, "fixed_context_records": 4, "brace_groups": 3, "source_screenshots": 1, "finite_semantic_hypotheses": 3, "new_index_or_route_trials": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "door-reference-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "brace_values_match_archived_date": document["records"]["brace_values_match_archived_day_month_shortyear"], "screenshot_is_distinct_message": True, "source_indices_defined": False, "new_index_or_route_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
