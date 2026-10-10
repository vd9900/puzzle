import json
from datetime import datetime, timezone

from PIL import Image

from tools.instruction_graphs import HEADER, ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR


OUTPUT = ROOT / "research/artifacts/cycle21"
FRIENDS = "My close friends have the best chance of solving it (a few tried). But they don't have the skills some of you do."
NOTE = "NOTE: that is a hint."
README_LITERALS = ("## 2026-07-12 hint", "![July 2026 Hint](hints/2026-07-12-official-hint.png)", "> @Jrk Bgrk", FRIENDS, NOTE)
NEXT_TEST = "Audit only the companion preserved July12 2026 screenshot's author-message/understanding wording and its reply-preview boundary. Compare it with the exact original creator statement The puzzle talks for me and frozen phase-name wording. Determine whether a communicative object is explicitly intended, without inferring a ciphertext consumer, personal fact, literal answer or algorithm. No external access, payout analysis, trial text or cryptographic search."


def exact_readme_maps():
    path = ROOT / "research/sources/maintained-README.md"
    document = path.read_text()
    mapped = []
    for literal in README_LITERALS:
        if document.count(literal) != 1:
            raise ValueError("Unexpected fixed contextual-hint README anchor")
        start = document.index(literal)
        mapped.append({"source": source(path), "literal": literal, **text_location(document, start, start + len(literal))})
    return mapped


def preserved_transcript_coverage(path):
    document = path.read_text()
    records = list(HEADER.finditer(document))
    if not records:
        raise ValueError("No original transcript headers")
    times = [datetime.strptime(".".join(entry.group(index) for index in (1, 2, 3)) + " " + entry.group(4), "%d.%m.%Y %H:%M:%S UTC%z") for entry in records]
    maximum = max(range(len(times)), key=times.__getitem__)
    latest = times[maximum].astimezone(timezone.utc)
    return {
        "source": source(path), "original_header_records": len(records),
        "latest_chronological_header": records[maximum].group(), "latest_archived_UTC": latest.isoformat(),
        "latest_header_line_one_based": document.count("\n", 0, records[maximum].start()) + 1,
        "exact_friends_phrase_occurrences": document.count(FRIENDS),
        "exact_note_phrase_occurrences": document.count(NOTE),
        "latest_record_precedes_secondary_July12_label": latest.date().isoformat() < "2026-07-12",
        "absence_not_contradiction_when_snapshot_ends_before_labeled_hint": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle20/progress-acknowledgement.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C20-PROGRESS-ACKNOWLEDGEMENT" or "July12 2026 close-friends" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen contextual-hint task")
    image = ROOT / "research/sources/maintained-hints__2026-07-12-official-hint.png"
    manifest_path = ROOT / "research/sources/manifest.json"
    manifest = json.loads(manifest_path.read_text())[image.name]
    if image.stat().st_size != manifest["bytes"] or source(image)["sha256"] != manifest["sha256"]:
        raise ValueError("Contextual-hint source differs from manifest")
    with Image.open(image) as picture:
        dimensions = list(picture.size)
    maps = exact_readme_maps()
    evidence = [source(path) for path in (preceding, image, manifest_path, ROOT / "research/sources/maintained-README.md", CHAT, CREATOR)]
    locations = ["research/sources/maintained-hints__2026-07-12-official-hint.png", "research/sources/manifest.json"]
    locations += [f'{entry["source"]["path"]}:{entry["line_one_based"]}' for entry in maps]
    readings = [
        {"id": "C21-FRIENDS-CONTEXTUAL", "hypothesis": "Familiarity with the creator's ideas or intended meaning may help identify the intended construction without replacing its technical stages", "assumptions": ["Best chance may reflect shared context rather than private data", "Technical skills and recognition can be independent requirements"], "confidence": "MEDIUM contrast grammar; UNKNOWN specific idea or operation", "contradictions": ["Hint does not name any shared idea, source or phase", "Friends may have another advantage", "Best chance is not a necessary condition or proof of a textual operand"]},
        {"id": "C21-FRIENDS-ACCESS", "hypothesis": "Close friends have additional knowledge or access unavailable in the public artifacts", "assumptions": ["Best chance reflects information asymmetry", "The missing information would be needed to distinguish intended meaning"], "confidence": "LOW exact access claim; UNKNOWN advantage", "contradictions": ["No private access, private datum or inaccessible input is stated", "Best chance does not say only friends can solve it", "Current public-only scope excludes investigating people or contacts"]},
        {"id": "C21-FRIENDS-GENERAL", "hypothesis": "The hint comments on solver familiarity and complementary abilities without assigning any operative text input", "assumptions": ["It refers generally to the puzzle", "The note marks intentional guidance but not an algorithm"], "confidence": "MEDIUM-HIGH literal scope; UNKNOWN construction consequence", "contradictions": ["Explicit NOTE says the contrast is a hint", "A deliberately contextual reference may constrain intended meaning more than encouragement alone"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["map preserved screenshot and README attribution", "bound original transcript coverage", "distinguish relative advantage from source/operand assignment"],
        "input": "One public screenshot, five fixed secondary anchors and two preserved original transcript ranges",
        "output": "One bounded contextual-hint interpretation without a personal-data or algorithm search",
        "next_test": NEXT_TEST,
    } for entry in readings]
    return {
        "id": "C21-CONTEXTUAL-HINT-PROVENANCE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "The preserved close-friends hint directly identifies contextual recognition as the missing construction requirement",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Visible sender/admin labels are attribution evidence, not signed authorship", "README date and filename are secondary labels, not original message timestamps", "No personal contacts or private data need to be investigated"],
        "operation_order": ["validate frozen task", "verify exact source bytes against manifest", "map five fixed README anchors", "record human-observed screenshot text/sender/time", "bound two original transcript ranges and exact phrase presence", "compare three finite contextual roles"],
        "input": "Public contextual-hint screenshot, preserved README, manifest and transcript ranges",
        "output": "Exact attribution/coverage constraints and three unresolved contextual roles",
        "confidence": "HIGH visible wording and captured bytes; MEDIUM sender attribution; UNKNOWN original date/antecedent/operation",
        "screenshot": {"source": source(image), "dimensions": dimensions, "human_visual_regions": [{"rectangle_xyxy": [53, 32, 482, 74], "public_text": FRIENDS}, {"rectangle_xyxy": [52, 91, 218, 114], "public_text": NOTE}], "visible_sender_admin_label": "Jrk Bgrt/Admin", "visible_times": ["06:51 PM", "06:51 PM"], "date_and_timezone_visible": False, "locators_are_not_OCR_or_extraction_masks": True},
        "readme_maps": maps, "sender_spelling_discrepancy": {"screenshot": "Jrk Bgrt", "README": "Jrk Bgrk", "typo_does_not_alone_disprove_screenshot_attribution": True},
        "original_transcript_coverage": [preserved_transcript_coverage(path) for path in (CREATOR, CHAT)],
        "date_provenance": {"July12_2026_is_filename_and_README_label": True, "capture_UTC": manifest["retrieved_at_utc"], "capture_time_not_original_publication": True, "original_message_timestamp_unverified": True},
        "instruction_scope": {"it_has_no_named_stage_source_container_or_object": True, "best_chance_is_not_only_possible_solver_group": True, "skills_comparison_does_not_define_a_cipher_family": True, "NOTE_marks_hint_not_an_operation_or_argument": True},
        "hypotheses": hypotheses,
        "result": "Screenshot visibly attributes a relative solving advantage to close friends and contrasts their skills with public solvers; separate NOTE marks it a hint. No stage, object, private input or algorithm is named. README/filename supply July12 label but screenshot has no date/timezone; README sender spelling differs. Original creator/chat snapshots end in May/June2026 and contain neither exact phrase, so missing transcript corroboration is a coverage limit, not contradiction. Contextual recognition is plausible, not an identified operand or a public-only impossibility claim.",
        "contradictions": ["No exact advantage, shared idea or operand is specified", "Relative best chance cannot establish secret prerequisite or unique contextual solution", "Original message date/body is not independently preserved in the available transcript range"],
        "next_test": NEXT_TEST,
        "search_space": {"preserved_hint_screenshots": 1, "fixed_README_anchors": 5, "original_transcript_ranges": 2, "exact_phrase_presence_patterns": 2, "declared_context_readings": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "personal_data_queries": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "contextual-hint-provenance.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "screenshot_date_visible": False, "transcripts_end_before_labeled_hint": True, "named_operand": False, "personal_data_queries": 0}, indent=2))


if __name__ == "__main__":
    main()
