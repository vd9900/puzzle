import json

from tools.instruction_graphs import ROOT, source, text_location, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle17"
SCOPES = [
    {
        "id": "C17-THIS-BACKWARD", "scope": "BACKWARD_RESULT",
        "hypothesis": "thispassword refers backward to the object described by lastwordsbeforearchichoice",
        "tree": {"antecedent_description": "lastwordsbeforearchichoice", "reference_label": "thispassword", "subsequent_operation": "first-shabef"},
        "missing_grammar": ["assignment or copula linking the two segments", "fixed Architect source and choice/count", "binding of subsequent hash to that object"],
        "assumptions": ["Adjacent last-word description supplies the antecedent of this", "z separates recipe fragments rather than independent labels", "the following operator consumes that described object"],
        "confidence": "MEDIUM local referential economy; UNKNOWN intended ownership",
        "contradictions": ["No literal equals, is, or an input identifier is encoded between the segments", "Secondary walkthrough lists decoded labels but does not assign their outputs", "Backward reference does not determine which words or representation"],
    },
    {
        "id": "C17-THIS-FORWARD", "scope": "FORWARD_RECIPE_LABEL",
        "hypothesis": "thispassword labels the following first-hint/hash recipe rather than the preceding last-word result",
        "tree": {"prior_independent_instruction": "lastwordsbeforearchichoice", "recipe_label": "thispassword", "following_recipe": ["first-shabef", "ourfirsthintisyourlastcommand"]},
        "missing_grammar": ["colon or title boundary after thispassword", "explicit recipe argument", "link from preceding last-word description to later consumer"],
        "assumptions": ["z separates an instruction from a forward-pointing label", "the following hash/reference wording defines a recipe", "a later operation consumes the last-word object separately"],
        "confidence": "LOW-MEDIUM heading-like compatibility; UNKNOWN intended ownership",
        "contradictions": ["No literal colon/title syntax is encoded", "The preserved walkthrough does not label a following computation as thispassword", "First-hint words do not uniquely identify an operand or literal text"],
    },
]


def source_grammar():
    frozen = json.loads((ROOT / "research/artifacts/cycle15/label-boundary-audit.json").read_text())
    layout = json.loads((ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json").read_text())["primary_layout"]
    document = (ROOT / "research/sources/salphaseion.html").read_text()
    regions = {region["name"]: region for region in frozen["regions"]}
    segments = []
    for name in ("lastwordsbeforearchichoice", "thispassword", "first-command"):
        region = regions[name]
        start, end = region["character_span_zero_based_half_open"]
        raw = document[start:end]
        compact = "".join(raw.split())
        if len(compact) != region["length"]:
            raise ValueError("Frozen source segment length changed")
        segments.append({
            "name": name, "source": region["source"],
            "encoded_source_span": {key: region[key] for key in ("normalized_span_zero_based_half_open", "character_span_zero_based_half_open", "utf8_byte_span_zero_based_half_open", "line_one_based", "column_one_based")},
            "decoded_or_literal": region.get("decoded", region.get("literal")),
            "encoded_character_spacing_is_not_decoded_word_spacing": all(len(token) == 1 for token in raw.split()),
            "immediately_preceding_source_window": document[start - 4:start],
            "immediately_following_source_window": document[end:end + 4],
            "literal_assignment_punctuation_present": any(character in raw for character in "=:()"),
        })
    if [entry["decoded_or_literal"] for entry in segments[:2]] != ["lastwordsbeforearchichoice", "thispassword"]:
        raise ValueError("Unexpected decoded label names")
    return {
        "segments": segments, "z_delimiters": frozen["z_delimiters"],
        "command_subphrases": layout["command_subphrases"],
        "decoded_word_spacing_is_not_primary_authored": True,
        "decoded_phrase1_phrase2_are_separate_z_delimited_units": True,
        "scope_assignment_verb_or_punctuation_is_missing": True,
        "first_command_begins_with_complete_shabef_not_four": True,
        "literal_label_is_not_the_object_described": True,
    }


def secondary_grammar():
    path = ROOT / "research/sources/community-README.md"
    document = path.read_text()
    literals = [
        'Next, we see two occurances of "shabef", and the English text "our first hint is your last command".',
        "We notice that \"z\" seems to be a separator for various segments",
        "1. [lastwordsbeforearchichoice]", "2. [thispassword]",
        "### AES Blob",
    ]
    mapped = []
    for literal in literals:
        if document.count(literal) != 1:
            raise ValueError("Expected one exact local secondary passage")
        start = document.index(literal)
        mapped.append({"literal": literal, "source": source(path), **text_location(document, start, start + len(literal))})
    if not all(mapped[index]["character_span_zero_based_half_open"][0] < mapped[index + 1]["character_span_zero_based_half_open"][0] for index in range(len(mapped) - 1)):
        raise ValueError("Secondary local passage order changed")
    return {
        "mapped_passages": mapped,
        "classification": "SECONDARY_DECODING_EXPLANATION_NOT_EXECUTION_PROOF",
        "lastword_and_this_labels_are_separate_numbered_list_items": True,
        "listed_labels_do_not_define_antecedent_or_recipe_scope": True,
        "hash_operator_recognition_is_not_an_argument_binding": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle17/operand-ownership.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C17-OPERAND-OWNERSHIP" or "grammatical-scope experiment" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding frozen task")
    evidence = [source(path) for path in (
        ROOT / "research/sources/salphaseion.html", ROOT / "research/sources/community-README.md",
        ROOT / "research/artifacts/cycle15/label-boundary-audit.json",
        ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json", preceding,
    )]
    locations = ["research/sources/salphaseion.html:17", "research/sources/community-README.md:381", "research/sources/community-README.md:390", "research/sources/community-README.md:391", "research/artifacts/cycle17/operand-ownership.json:1"]
    hypotheses = [scope | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["preserve three original z-delimited segments", "map local operator prefix separately from ordinary words", "compare only declared reference scope", "require a source-owned antecedent and consumer before extraction"],
        "input": "Frozen decoded labels, original encoded source boundaries and local secondary explanation",
        "output": "A grammatical reference tree, not selected words or a trial input",
        "next_test": "Map the earliest preserved trailer-decoding evidence against the creator zeroing hint chronology to distinguish already-decoded numeric-zero labels from unresolved source-object instructions; no new mask or extraction",
    } for scope in SCOPES]
    return {
        "id": "C17-THISPASSWORD-SCOPE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Exact original and secondary grammar uniquely selects backward-result versus forward-recipe scope for thispassword",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Compare only the two frozen grammatical scopes", "No missing copula, colon or argument is silently supplied", "A decoder's numbered list is not creator-authored execution syntax"],
        "operation_order": ["load the frozen two-scope task", "map three original segments and local SHA subphrases", "map five exact secondary local passages", "retain missing syntax for both reference trees"],
        "input": "Original public encoded text and preserved local walkthrough wording",
        "output": "Two finite scope trees and exact primary/secondary syntax audit",
        "confidence": "HIGH exact grammar/source positions; UNKNOWN unique intended scope",
        "primary_grammar": source_grammar(), "secondary_grammar": secondary_grammar(),
        "hypotheses": hypotheses, "scope_count": len(hypotheses),
        "best_local_reading": "BACKWARD_RESULT_IS_MORE_ECONOMICAL_NOT_PROVEN",
        "unique_scope_established": False,
        "result": "Both declared scopes survive. Three primary z-delimited segments have per-encoded-character spacing but no assignment punctuation or decoded word boundaries. Secondary list items preserve lastwords and thispassword as separate decoded labels and do not bind either a backward result or a forward recipe. Backward reference is locally more economical; neither reading identifies a source, word count, hash argument or consumer. No words or trial strings extracted.",
        "contradictions": ["Decoder-added word spacing and list punctuation cannot be promoted to primary syntax", "Description/label decoding does not instantiate the selected object", "Hash operator recognition does not choose literal instruction text as its input"],
        "next_test": "Perform one fixed source-availability/chronology audit of earliest preserved lastwords/thispassword decoding versus the dated creator some-characters-zeroed-out hint. Distinguish locally encoded numeric zero from an unbound transformation requirement; do not re-run decoding experiments, generate masks or infer zeroing/reinsertion inverses.",
        "search_space": {"reference_scopes": 2, "primary_segments": 3, "local_command_subphrases": 4, "secondary_exact_passages": 5, "new_extractions": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "thispassword-scope.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "reference_scopes": document["scope_count"], "unique_scope_established": document["unique_scope_established"], "new_extractions": 0}, indent=2))


if __name__ == "__main__":
    main()
