import json

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.trailer_referents import alphabetic_source_map


OUTPUT = ROOT / "research/artifacts/cycle13"
ANCHORS = [
    "returntothesourcecodes", "thecodeyouhopefullycarry", "reinsertingtheprimebasics",
    "afterwhich", "selectfrom", "overtwentythreeciphers", "sixteenencryptions",
    "andorsevenintertwinedpasswords",
]


def mapped_directives():
    frozen_path = ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json"
    frozen = json.loads(frozen_path.read_text())
    speech_path = ROOT / "research/artifacts/phase32-beaufort.txt"
    speech = speech_path.read_text().strip()
    spacing_path = ROOT / "research/sources/community-README.md"
    spacing = spacing_path.read_text()
    start = spacing.index("YOUR LIFE IS THE SUM")
    end = spacing.index("```", start)
    normalized, positions = alphabetic_source_map(spacing, start, end)
    if normalized != speech or len(speech) != 1539:
        raise ValueError("Existing verified speech and secondary spacing differ")
    reference = frozen["speech"]["anchors"][0]
    speech_reference_start = reference["character_span_zero_based_half_open"][0]
    encoded_start = reference["encoded_byte_span_zero_based_half_open"][0] - speech_reference_start
    mapped = []
    for phrase in ANCHORS:
        if speech.count(phrase) != 1:
            raise ValueError("Expected a unique fixed directive anchor")
        offset = speech.index(phrase)
        raw_start, raw_end = positions[offset], positions[offset + len(phrase) - 1] + 1
        mapped.append({
            "normalized_phrase": phrase,
            "verified_decoded_span_zero_based_half_open": [offset, offset + len(phrase)],
            "encoded_fixture_byte_span_zero_based_half_open": [encoded_start + offset, encoded_start + offset + len(phrase)],
            "archived_spacing": spacing[raw_start:raw_end],
            "secondary_spacing_location": text_location(spacing, raw_start, raw_end),
        })
    return {
        "sources": [source(speech_path), source(spacing_path), source(frozen_path)],
        "all1539_letters_match": True,
        "existing_verified_decoding_not_a_new_trial": True,
        "word_boundaries_are_secondary": True,
        "mapped_anchors": mapped,
        "literal_choice_in_speech": "choice" in speech,
        "typed_numeric_phrases": [
            {"value": 23, "qualifier": "over", "noun": "ciphers"},
            {"value": 16, "qualifier": None, "noun": "encryptions"},
            {"value": 7, "qualifier": "and or", "noun": "intertwined passwords"},
        ],
        "numbers_are_not_an_algorithm_list_or_position_selector": True,
    }


def report():
    mapped = mapped_directives()
    evidence = mapped["sources"] + [source(ROOT / "research/artifacts/cycle11/hint-instruction-order.json"), source(ROOT / "research/artifacts/cycle12/source-join-preflight-v2.json")]
    locations = ["research/artifacts/phase32-beaufort.txt:1", "research/sources/community-README.md:314", "research/sources/community-README.md:315", "research/sources/community-README.md:316", "research/artifacts/phase32.txt:5"]
    variants = []
    for suffix, referent, support, limitation in [
        ("IMAGE", "original image/color-coded information", "Separate creator-attributed color hint explicitly returns to first puzzle piece", "No rule binds prime basics to a particular color value, source cell or textual operand"),
        ("HTML", "original puzzle source documents or encoded source strings", "Verified directive literally names source codes; primary page preserves encoded instruction objects", "No exact source file, byte boundary or reinsertion object is named"),
        ("SYMBOLS", "source symbol stream and its carried information", "Existing dbbi prime/nonprime partitions and source-keyed Bifid expose multiple source-derived objects", "No directive explicitly names dbbi, residual60, faed570, Bifid or an insertion coordinate"),
    ]:
        variants.append({
            "id": "C13-DIRECTIVE-" + suffix, "status": "INCONCLUSIVE",
            "hypothesis": "source codes refers to " + referent,
            "source_evidence": evidence, "source_locations": locations,
            "assumptions": ["The speech's relational language is an operative instruction rather than narrative", "The proposed source object is what the creator intended", "A separate source rule specifies prime basics and the reinsertion site"],
            "operation_order": ["return to proposed source object", "reinsert prime-related information", "after which select from described objects"],
            "input": referent + " plus an unspecified carried object",
            "output": "An unspecified reconstructed source object available for a later selection",
            "confidence": "LOW-MEDIUM for this referent; MEDIUM-HIGH for reinsertion-before-selection conditional on operative reading",
            "support": support,
            "contradictions": [limitation, "No unique choice anchor or selected-word count", "No numerical cipher-family enumeration follows from the stated nouns"],
            "next_test": "Find an exact source-authored operand/site binding before applying any reinsertion, extraction or cryptographic operation",
        })
    return {
        "id": "C13-RELATIONAL-DIRECTIVES", "date": "2026-09-30", "status": "INCONCLUSIVE",
        "hypothesis": "The modified speech constrains instruction order and operand types more strongly than a loose choice-quote interpretation",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["After which has its ordinary local antecedent in the reinserting phrase", "The relational language may be operative but creator intent is not established", "Archived word spacing is only corroboration of the verified compact text"],
        "operation_order": ["use existing verified decoded fixture", "map eight fixed relational anchors to encoded and spaced sources", "parse only explicit local dependencies and typed numeric phrases", "retain three finite source-object interpretations without executing them"],
        "input": "Verified1539-letter speech and preserved whole-speech secondary spacing",
        "output": "Exact local dependency graph and three unresolved source-object bindings",
        "confidence": "HIGH for positions/wording; MEDIUM-HIGH for conditional local order; UNKNOWN for operand/site/consumer",
        "directives": mapped,
        "conditional_operation_graph": {
            "nodes": ["return-to-source", "carried-code", "reinsert-prime-basics", "select-from-described-objects"],
            "edges": [["return-to-source", "reinsert-prime-basics", "LOCAL_GRAMMATICAL_ORDER_OPERATIVE_READING_UNPROVED"], ["carried-code", "reinsert-prime-basics", "POSSIBLE_ARGUMENT_BINDING_NOT_EXPLICIT"], ["reinsert-prime-basics", "select-from-described-objects", "EXPLICIT_AFTER_WHICH_LOCAL_ANTECEDENT"]],
        },
        "hypotheses": variants,
        "result": "After which locally places selection after reinserting prime basics under an operative reading. The text says select from described objects, not take letters at23/16/7, and supplies no cipher-family list. Source object, carried data, insertion position and connection to matrixsumlist remain unbound.",
        "contradictions": ["Narrative is not proof of executable protocol", "Numeric nouns do not identify specific algorithm families or indexing", "Source-keyed Bifid and prime residual are not explicitly named by these directives", "No unique Architect choice anchor exists in the verified modified speech"],
        "next_test": "Audit preserved original-puzzle and prime/zeroing hint chronology for an explicit binding of prime basics, carried code and source object. Use exact source spans and typed referents, not new selector variants or a cipher search.",
        "search_space": {"fixed_directive_anchors": 8, "source_object_hypotheses": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "relational-directives.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "fixed_directive_anchors": len(document["directives"]["mapped_anchors"]), "finite_source_referents": len(document["hypotheses"]), "operand_binding_verified": False, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
