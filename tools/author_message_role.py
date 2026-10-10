import json

from PIL import Image

from tools.instruction_graphs import ROOT, source, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle21"
MESSAGE = "Oh... and before I fall asleep. I want to assume it is quite clear I held quite a secret in my head which I seriously wanted to share with the planet... for those who can understand what I meant..."
TALKS_HEADER = "=== [06.08.2023 05:44:39 UTC-05:00] Jrk Bgrt"
NEXT_TEST = "Compare only the exact original creator quote Globally supporting my generation with its four-word initials and the original public GSMG source/title labels. Determine whether a source-authored acronym/meaning association supports a communicative object without assigning an algorithm, extracted answer, final consumer or personal fact. Use fixed primary/secondary locations only; no acronym permutations, dictionaries, hash trials or external access."


def report():
    preceding = ROOT / "research/artifacts/cycle21/contextual-hint-provenance.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C21-CONTEXTUAL-HINT-PROVENANCE" or "companion preserved July12 2026" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen companion-message task")
    image = ROOT / "research/sources/maintained-hints__2026-07-12-other-msg.png"
    manifest_path = ROOT / "research/sources/manifest.json"
    captured = json.loads(manifest_path.read_text())[image.name]
    if image.stat().st_size != captured["bytes"] or source(image)["sha256"] != captured["sha256"]:
        raise ValueError("Companion screenshot differs from manifest")
    with Image.open(image) as picture:
        dimensions = list(picture.size)
    creator_body, creator_location = record_by_header(CREATOR, TALKS_HEADER)
    chat_body, chat_location = record_by_header(CHAT, TALKS_HEADER)
    if creator_body != chat_body or creator_body != "The puzzle talks for me.":
        raise ValueError("Unexpected creator communicative-role statement")
    name_path = ROOT / "research/artifacts/cycle20/phase-name-semantics.json"
    name = json.loads(name_path.read_text())
    readme_path = ROOT / "research/sources/maintained-README.md"
    readme = readme_path.read_text()
    readme_literal = "![July 2026 other message](hints/2026-07-12-other-msg.png)"
    if readme.count(readme_literal) != 1:
        raise ValueError("Unexpected companion README ownership")
    evidence = [source(path) for path in (preceding, image, manifest_path, readme_path, CHAT, CREATOR, name_path)]
    locations = ["research/sources/maintained-hints__2026-07-12-other-msg.png", "research/sources/maintained-README.md:424", "research/evidence/cycle02/_work__creator_jrk.txt:775", "research/evidence/cycle02/_work__chat_transcript.txt:22661", "research/artifacts/cycle20/phase-name-semantics.json"]
    variants = [
        {"id": "C21-MESSAGE-COMMUNICATIVE", "hypothesis": "The puzzle contains an intended author message whose meaning is part of successful interpretation", "assumptions": ["Talks for me and wanted to share have their ordinary communicative sense", "Meaning may complement the reproduced technical stages"], "confidence": "MEDIUM-HIGH communicative-role wording; UNKNOWN actual message object", "contradictions": ["No stage, container or complete text object is named", "Message may be thematic framing rather than an executable instruction"]},
        {"id": "C21-MESSAGE-THEMATIC", "hypothesis": "Author-message wording is thematic motivation without assigning a distinct decoded-message object", "assumptions": ["Statements about meaning need not add data-flow nodes", "Creator commentary can frame the puzzle without an exact output requirement"], "confidence": "MEDIUM conservative role; UNKNOWN hidden message scope", "contradictions": ["Original talks-for-me statement is explicit", "Companion suggests something intentionally shared to be understood", "Theme alone does not explain the remaining encoded construction"]},
        {"id": "C21-MESSAGE-PRIVATE-OPERAND", "hypothesis": "Secret in my head implies an unavailable private fact must be used as a technical operand", "assumptions": ["Personal wording means inaccessible input", "Such input would be required for construction rather than interpretation"], "confidence": "LOW; technical prerequisite not stated", "contradictions": ["Wanted to share with the planet points toward communicated meaning", "No private fact, input representation or technical consumer specified", "Public-only scope excludes searching private facts or contacts"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["identify author body and clipped reply preview", "compare original talks-for-me statement with frozen name/feeling evidence", "retain message-role ambiguity without operand assignment"],
        "input": "One preserved companion screenshot, one original creator body and frozen name/context evidence",
        "output": "One bounded communicative-object interpretation, not recovered text or a private-data dependency",
        "next_test": NEXT_TEST,
    } for entry in variants]
    return {
        "id": "C21-AUTHOR-MESSAGE-ROLE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Preserved author statements establish a communicative object distinct from a technical secret operand",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Screenshot text is human-observed, not independently archived original message text", "Clipped reply previews are not complete primary instructions", "No lower screenshot financial material is transcribed or analyzed"],
        "operation_order": ["validate frozen task", "verify captured image bytes", "locate author-message body apart from reply preview", "cross-check one original talks-for-me body in two exports", "reuse previous contextual coverage and name-role maps", "compare three finite message roles"],
        "input": "Public companion screenshot and exact original creator communication statement",
        "output": "Authorship/region distinction and three unresolved communicative-role hypotheses",
        "confidence": "HIGH original talks-for-me body; MEDIUM screenshot attribution; UNKNOWN named message or operand",
        "screenshot": {"source": source(image), "dimensions": dimensions, "visible_sender_admin_label": "Jrk Bgrt/Admin", "author_body": {"human_visual_locator_xyxy": [54, 87, 504, 173], "public_text": MESSAGE}, "clipped_reply_preview": {"human_visual_locator_xyxy": [54, 39, 504, 82], "visible_sender_fragment": "Σ...", "preview_is_truncated_not_reconstructed": True, "not_author_body_or_complete_instruction": True}, "visible_author_body_time": "07:08 PM", "date_and_timezone_visible": False, "lower_financial_message_out_of_scope_not_transcribed": True, "locators_are_not_OCR_or_extraction_masks": True},
        "original_communication": {"public_text": creator_body, "creator_record": creator_location, "original_chat_record": chat_location, "matching_exports_are_not_independent_identity_authentication": True},
        "transcript_exact_companion_phrase_counts": [{"source": source(path), "count": path.read_text().count(MESSAGE)} for path in (CREATOR, CHAT)],
        "coverage_reused": {"source": source(preceding), "ranges": frozen["original_transcript_coverage"], "absence_not_a_disproof_of_later_screenshot": True},
        "name_role_reused": {"source": source(name_path), "creator_name_record": name["creator_name_record"], "no_name_or_checkpoint_audit_repeated": True},
        "no_narrowed_stage_or_ciphertext_consumer": True,
        "hypotheses": hypotheses,
        "result": "Companion author body says a thought was intended to be shared with people who understand its meaning. Its clipped reply preview belongs to another speaker and cannot be reconstructed as an instruction. Original2023 The puzzle talks for me matches both exports. Together they support a communicative/meaning role, not a named ciphertext, input, literal message format or private-fact prerequisite. Later screenshot date/timezone and exact message archive remain unverified; no financial material analyzed.",
        "contradictions": ["Communicative purpose does not identify the construction's source/argument/consumer", "Screenshot reply preview is clipped and original reply metadata unavailable", "Private-head phrasing cannot establish a private technical prerequisite"],
        "next_test": NEXT_TEST,
        "search_space": {"companion_screenshots": 1, "human_author_and_preview_regions": 2, "original_creator_bodies_cross_checked": 1, "fixed_companion_phrase_presence_patterns": 1, "declared_message_role_readings": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "personal_data_queries": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "author-message-role.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "message_role_readings": 3, "named_message_or_operand": False, "personal_data_queries": 0}, indent=2))


if __name__ == "__main__":
    main()
