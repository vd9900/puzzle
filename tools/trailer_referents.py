import json
import re

from tools.instruction_graphs import HEADER, ROOT, source, text_location, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle11"


def alphabetic_source_map(document, start, end):
    positions = [index for index in range(start, end) if document[index].isascii() and document[index].isalpha()]
    return "".join(document[index].lower() for index in positions), positions


def speech_wording():
    path = ROOT / "research/sources/community-README.md"
    document = path.read_text()
    start = document.index("YOUR LIFE IS THE SUM")
    end = document.index("```", start)
    normalized, positions = alphabetic_source_map(document, start, end)
    speech_path = ROOT / "research/artifacts/phase32-beaufort.txt"
    speech = speech_path.read_text().strip()
    if normalized != speech:
        raise ValueError("Archived spacing does not reproduce the complete verified speech")
    anchors = []
    for phrase in ["sourcecodes", "reinsertingtheprimebasics", "afterwhich", "selectfrom"]:
        offset = speech.index(phrase)
        raw_start = positions[offset]
        raw_end = positions[offset + len(phrase) - 1] + 1
        anchors.append({"normalized_phrase": phrase, "verified_speech_span_zero_based_half_open": [offset, offset + len(phrase)], "archived_spacing": document[raw_start:raw_end], **text_location(document, raw_start, raw_end)})
    chosen = next(anchor for anchor in anchors if anchor["normalized_phrase"] == "reinsertingtheprimebasics")
    word_matches = list(re.finditer(r"[A-Za-z]+", document[slice(*chosen["character_span_zero_based_half_open"])]))
    words = [{"word": match.group(), **text_location(document, chosen["character_span_zero_based_half_open"][0] + match.start(), chosen["character_span_zero_based_half_open"][0] + match.end())} for match in word_matches]
    return {
        "source": source(path), "verified_speech_source": source(speech_path), "all1539_letters_match": True,
        "source_word_boundaries_are_secondary": True, "primary_decoded_text_has_no_spaces": True,
        "anchors": anchors, "pre_select_phrase_words": words, "pre_select_phrase_letter_count": len("reinsertingtheprimebasics"),
        "literal_choice_in_verified_speech": False, "selected_word_count_is_not_specified": True,
        "the_phrase_is_already_tested_material_and_not_a_new_trial_input": True,
    }


def choice_quote():
    path = ROOT / "research/evidence/cycle02/_work__chat_transcript.txt"
    document = path.read_text()
    begin = "The Architect: Which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning, and end."
    first = document.index(begin)
    end = document.index("Neo walks to the door on his left", first)
    raw = document[first:end]
    normalized, positions = alphabetic_source_map(document, first, end)
    headers = list(HEADER.finditer(document, 0, first))
    phrases = []
    for literal in ["There are two doors.", "The door to your right leads to the source", "the problem is choice."]:
        offset = document.index(literal, first, end)
        normalized_literal = "".join(symbol.lower() for symbol in literal if symbol.isascii() and symbol.isalpha())
        normalized_offset = normalized.index(normalized_literal)
        phrases.append({"literal": literal, "normalized_span_in_quoted_passage_zero_based_half_open": [normalized_offset, normalized_offset + len(normalized_literal)], **text_location(document, offset, offset + len(literal))})
    verified = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
    comparison = []
    for phrase in ["whichbringsusatlasttothemomentoftruth", "therearetwodoors", "theproblemischoice", "reinsertingtheprimebasics", "selectfrom"]:
        comparison.append({"normalized_phrase": phrase, "in_verified_modified_speech": phrase in verified, "in_quoted_community_passage": phrase in normalized})
    return {
        "source": source(path), "archived_header": headers[-1].group(), **text_location(document, first, end),
        "classification": "COMMUNITY_MOVIE_QUOTATION_NOT_PRIMARY_PUZZLE_TEXT",
        "exact_raw_passage_length": len(raw), "mapped_anchors": phrases, "phrase_presence_comparison": comparison,
        "choice_quote_cannot_be_silently_substituted_for_modified_speech": True,
        "original_movie_source_not_independently_preserved_or_authenticated": True,
    }


def report():
    speech = speech_wording()
    quoted = choice_quote()
    hypotheses = [
        {
            "id": "C11-T01", "hypothesis": "lastwordsbeforearchichoice selects words before selectfrom in the modified puzzle speech",
            "source_evidence": ["Verified speech contains sourcecodes -> reinsertingtheprimebasics -> afterwhich -> selectfrom", "Archived spaced walkthrough matches all1539 letters"],
            "source_locations": ["research/artifacts/phase32-beaufort.txt:1", "research/sources/community-README.md:315", "research/sources/salphaseion.html:18"],
            "assumptions": ["Archi names this modified Architect speech", "choice refers semantically to selectfrom", "Secondary spacing preserves intended words", "thispassword binds backward to those words"],
            "operation_order": ["identify modified speech", "identify semantic selection point", "identify unspecified preceding words", "interpret trailer thispassword and adjacent SHA command"],
            "input": "Verified modified speech and decoded trailer", "output": "Unresolved selected word object", "confidence": "MEDIUM for speech identity; LOW for boundary/count",
            "contradictions": ["No literal choice", "No word count", "Already tested pre-select phrase cannot be treated as a new experiment"],
            "next_test": "Require an explicit source position/count selector linking the earlier prime/sumlist objects to words", "status": "INCONCLUSIVE",
        },
        {
            "id": "C11-T02", "hypothesis": "lastwordsbeforearchichoice selects a literal choice-bearing Architect passage from the movie quotation",
            "source_evidence": ["Community quoted passage contains two doors, source/salvation and the problem is choice", "Later hint explicitly names lastwordsbeforearchichoice before yinyang"],
            "source_locations": ["research/evidence/cycle02/_work__chat_transcript.txt:26070", "research/evidence/cycle02/_work__creator_jrk.txt:711"],
            "assumptions": ["External/movie quotation is the intended referent rather than decoded puzzle speech", "The preserved community quotation is accurate", "Choice refers to one exact phrase or event"],
            "operation_order": ["choose literal choice-bearing quoted source", "bind exact choice anchor and unspecified last-word count", "resolve preceding sumlist relation"],
            "input": "Preserved community quotation, not a new fetched source", "output": "Unknown word object", "confidence": "LOW-MEDIUM for thematic reference; LOW for source authority",
            "contradictions": ["Choice passage absent from creator-modified verified speech", "No creator-attributed source explicitly specifies this movie passage", "No exact word count or index instruction"],
            "next_test": "Compare source attribution and positional references before extracting any candidate phrase", "status": "INCONCLUSIVE",
        },
        {
            "id": "C11-T03", "hypothesis": "The hint sequence makes matrixsumlist a selector or intermediate operation leading to Architect words, not necessarily the selected words themselves",
            "source_evidence": ["Exact later hint orders yellowblueprimes -> matrixsumlist -> lastwordsbeforearchichoice -> yinyang", "Primary labels and first-SHA command retain the same adjacency"],
            "source_locations": ["research/evidence/cycle02/_work__creator_jrk.txt:711", "research/sources/salphaseion.html:18"],
            "assumptions": ["Ordered clue mentions imply a dependency", "Sumlist result supplies positions or ordering rather than literal trial material", "An Architect source and choice anchor can be fixed independently"],
            "operation_order": ["prime/color object", "sumlist object or operation", "source-coordinate join with Architect words", "yin-yang recognition checkpoint"],
            "input": "Already preserved numeric/text objects and a source-fixed Architect passage", "output": "An unknown positionally selected intermediate",
            "confidence": "MEDIUM for clue order; LOW for executable join", "contradictions": ["No selection verb, axis or coordinate convention", "Earlier numeric-routing tests do not verify this graph", "Weighted341 equality has no positional reconstruction"],
            "next_test": "Build only the exact fixed join implied by a located source selector; if none exists, keep the edge unknown rather than enumerate routes", "status": "PROMISING",
        },
    ]
    return {
        "id": "C11-TRAILER-REFERENTS", "date": "2026-09-30", "status": "INCONCLUSIVE",
        "scope": "Offline public text source binding only",
        "speech_wording": speech, "choice_quote": quoted, "hypotheses": hypotheses,
        "result": "Both Architect referents survive, but choice-bearing community quotation and verified modified speech are different objects. Secondary spacing verifies a four-word pre-select phrase without proving a selector or word count.",
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
        "next_test": "Source-coordinate join preflight: seek an explicit selector or alignment in preserved primary/hint formatting linking prime/sumlist data to a fixed Architect source. Reject unconstrained window or route enumeration.",
    }


def main():
    document = report()
    write_artifact(OUTPUT / "trailer-referents.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "archived_speech_all1539_letters_match": document["speech_wording"]["all1539_letters_match"], "referent_hypotheses": len(document["hypotheses"]), "literal_choice_in_verified_speech": False, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
