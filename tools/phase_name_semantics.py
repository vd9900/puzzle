import json
import re

from PIL import Image

from tools.carry_forward_ownership import mapped_literal
from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle20"
HEADER = "=== [14.03.2021 04:45:01 UTC-05:00] Jrk Bgrt"
CLAUSES = (
    "When people progress in salphation it might be cracked pretty soon.",
    "Breaking salphation, should be giving the feeling of the phase's name.",
    "Won't be easy but I've noticed how clever most of you are",
)
NEXT_TEST = "Audit one bounded original August3 2023 context window around creator-attributed you guys got really really far already and actually the hardest part is done. Determine the named prior community object and preserved reply metadata, distinguishing progress acknowledgement from confirmation of a transformation. Compare only frozen stage/name/checkpoint constraints; no broad phrase sweep, cryptographic trial or new input extraction."


def creator_name_record():
    body, location = record_by_header(CREATOR, HEADER)
    original_body, original_location = record_by_header(CHAT, HEADER)
    if body != original_body:
        raise ValueError("Creator phase-name statement differs between exports")
    document = CREATOR.read_text()
    offset = location["character_span_zero_based_half_open"][0]
    clauses = []
    for clause in CLAUSES:
        if body.count(clause) != 1:
            raise ValueError("Expected one fixed phase-name clause")
        start = offset + body.index(clause)
        clauses.append({"literal": clause, **text_location(document, start, start + len(clause))})
    return {
        "creator_record": location, "original_chat_record": original_location, "clauses": clauses,
        "salphation_spelling_occurrences_in_this_record": body.count("salphation"),
        "phase_name_is_linked_to_feeling_not_an_explicit_output_string": True,
        "matching_exports_are_not_independent_identity_authentication": True,
        "no_explicit_algorithm_source_argument_or_container": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle20/board-width-reference.json"
    prior = json.loads(preceding.read_text())
    if prior["id"] != "C20-BOARD-WIDTH-REFERENCE" or "feeling of the phase's name" not in prior["next_test"]:
        raise ValueError("Unexpected frozen phase-name task")
    page = ROOT / "research/sources/salphaseion.html"
    headings = [mapped_literal(page, literal, "EXACT_PRIMARY_HEADING_NOT_A_GENERATED_NAME_VARIANT")
                for literal in ("<h1> SalPhaseIon </h1>", "<h1> Cosmic Duality </h1>")]
    checkpoint_path = ROOT / "research/artifacts/cycle13/checkpoint-referents-v2.json"
    checkpoint = json.loads(checkpoint_path.read_text())
    trailer_path = ROOT / "research/artifacts/cycle11/trailer-referents.json"
    trailer = json.loads(trailer_path.read_text())
    quote = trailer["choice_quote"]
    document = CHAT.read_text()
    start, end = quote["character_span_zero_based_half_open"]
    matches = list(re.finditer(r"\bsalvation\b", document[start:end], re.I))
    if len(matches) != 1:
        raise ValueError("Unexpected salvation word in fixed secondary passage")
    match = matches[0]
    salvation = {"source": source(CHAT), "literal": match.group(), "classification": quote["classification"],
                 **text_location(document, start + match.start(), start + match.end())}
    picture_path = ROOT / "research/sources/maintained-hints__2021-03-14.png"
    with Image.open(picture_path) as picture:
        dimensions = list(picture.size)
    evidence = [source(path) for path in (preceding, CREATOR, CHAT, page, picture_path, checkpoint_path, trailer_path)]
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:510", "research/evidence/cycle02/_work__chat_transcript.txt:15661", "research/sources/salphaseion.html:16", "research/sources/salphaseion.html:19", "research/sources/maintained-hints__2021-03-14.png", f'research/evidence/cycle02/_work__chat_transcript.txt:{salvation["line_one_based"]}', "research/artifacts/cycle13/checkpoint-referents-v2.json"]
    readings = [
        {"id": "C20-NAME-AFFECTIVE", "hypothesis": "The phase-name remark describes the feeling or recognition associated with completing SalPhaseIon rather than a literal output format", "assumptions": ["Feeling is used in its ordinary affective sense", "Salphation refers to the current phase, without requiring a spelling transformation"], "confidence": "MEDIUM-HIGH exact feeling grammar; UNKNOWN intended concealed meaning", "contradictions": ["The phrase may be deliberately suggestive", "Affective recognition alone cannot identify the construction's input or output"]},
        {"id": "C20-NAME-THEMATIC-SALVATION", "hypothesis": "The phase name evokes salvation/source-return themes present in secondary Architect dialogue", "assumptions": ["A semantic association is intended", "The secondary movie passage supplies thematic context, not replacement puzzle text"], "confidence": "MEDIUM thematic compatibility; LOW creator-authenticated interpretation", "contradictions": ["Creator statement uses salphation, not literal salvation", "Primary heading says SalPhaseIon", "Secondary salvation passage is absent from verified modified speech and cannot define a selector"]},
        {"id": "C20-NAME-LITERAL-GATE", "hypothesis": "The phase name or a name-derived string must occur literally in the correct output", "assumptions": ["Feeling of the name is an exact text-output requirement", "A source-authored spelling/representation rule exists"], "confidence": "LOW; literal gate not established", "contradictions": ["Primary statement names a feeling, not plaintext bytes", "Heading and chat spelling are distinct observations, not a prescribed normalization", "Frozen checkpoint wording does not establish a universal literal-output gate"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["map exact creator statement", "compare authored headings and fixed secondary thematic word", "reuse checkpoint-format uncertainty without new output trials"],
        "input": "One original phase-name statement, two exact headings and existing thematic/checkpoint evidence",
        "output": "One bounded name-role interpretation, not a generated name, output gate or algorithm",
        "next_test": NEXT_TEST,
    } for entry in readings]
    return {
        "id": "C20-PHASE-NAME-SEMANTICS", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "The creator-attributed phase-name remark constrains the intended construction's object role or output more tightly than arbitrary cipher trials",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Exact original wording is distinct from a later thematic interpretation", "Human screenshot locator is not OCR/extraction geometry", "Name spelling is recorded without generating transformations"],
        "operation_order": ["validate frozen task", "cross-check one original body in two exports", "map three fixed name/feeling clauses", "map two exact primary headings", "identify full statement screenshot", "reuse frozen checkpoint records", "map one thematic word in the fixed secondary passage", "compare three finite name roles"],
        "input": "Original public name/feeling statement, heading markup, preserved screenshot and frozen checkpoint/movie maps",
        "output": "Exact provenance and three unresolved phase-name role hypotheses",
        "confidence": "HIGH original wording/record/screenshot association; UNKNOWN intended hidden semantic role",
        "creator_name_record": creator_name_record(), "primary_headings": headings,
        "screenshot": {"source": source(picture_path), "dimensions": dimensions, "human_visual_locator_xyxy": [67, 251, 516, 291], "visible_clause": CLAUSES[1], "visible_speaker_admin_label": "Jrk Bgrt/admin", "displayed_0345AM_timezone_not_given": True, "locator_not_OCR_or_text_selection_rule": True},
        "checkpoint_reused": {"source": source(checkpoint_path), "records": checkpoint["records"], "literal_format_not_a_universal_necessary_gate": True, "no_checkpoint_or_cover_experiment_repeated": True},
        "secondary_salvation": salvation,
        "secondary_passage_not_substituted_for_verified_speech": True,
        "hypotheses": hypotheses,
        "result": "Creator-attributed March2021 statement and full screenshot explicitly associate breaking salphation with a feeling of the phase's name. Primary heading is SalPhaseIon; Cosmic Duality is separately headed. Fixed secondary movie passage mentions salvation but is not primary puzzle text. Affective/name recognition and thematic source/salvation readings remain possible; no exact string, algorithm, input or universal output gate is prescribed.",
        "contradictions": ["Name association does not identify the carried object or final consumer", "Secondary movie source is not creator-authenticated baseline", "A name-derived spelling or literal output requirement would be an extra assumption"],
        "next_test": NEXT_TEST,
        "search_space": {"original_creator_bodies_cross_checked": 1, "fixed_name_clauses": 3, "primary_headings": 2, "statement_screenshots": 1, "secondary_thematic_words": 1, "frozen_checkpoint_records": 3, "declared_name_role_readings": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_name_variants": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "phase-name-semantics.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "name_role_readings": 3, "exact_output_gate": False, "new_name_variants": 0}, indent=2))


if __name__ == "__main__":
    main()
