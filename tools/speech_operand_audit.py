import json

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, record_by_header
from tools.trailer_referents import alphabetic_source_map


OUTPUT = ROOT / "research/artifacts/cycle16"
REGIONS = [
    ("opening_dialogue", "=== [01.09.2023 23:38:24 UTC-05:00] Deleted Account", "You are the eventuality", [86, 421]),
    ("denial_dialogue", "=== [27.05.2025 16:02:02 UTC-05:00] k1ng 😎", "Denial is", [832, 984]),
    ("consequence_dialogue", "=== [02.09.2023 03:41:03 UTC-05:00] Deleted Account", "to rebuild Zion", [1223, 1487]),
]
ANCHORS = {
    "opening_dialogue": [
        "youaretheeventualityofananomalywhichdespitemysinceresteffortsihavebeenunabletoeliminatefromwhatisotherwiseaharmonyofmathematicalprecisionwhileitremainsaburden",
        "itisnotunexpectedandthusnotbeyondameasureofcontrolwhichhasledyouinexorablyhere",
        "youhaventansweredmyquestion",
        "quiterightinterestingthatwasquickerthantheothers",
    ],
    "denial_dialogue": [
        "denialisthemostpredictableofallhumanresponsesbutrestassuredthiswill",
        "time",
        "havedestroyed",
        "and",
        "havebecomeexceedinglyefficientatit",
    ],
    "consequence_dialogue": [
        "failuretocomplywiththisprocesswillresultinacataclysmicsystemcrashkilling",
        "whichcoupledwiththeexterminationof",
        "willultimatelyresultintheextinctionoftheentire",
    ],
}
CLAIMS = [
    ("=== [19.11.2024 14:25:30 UTC-05:00] Danny Tee", "assiduously avoided", "COMMUNITY_VARIANT_COMPARISON"),
    ("=== [24.12.2024 03:37:13 UTC-05:00] ES", "These versions were published before the puzzle", "COMMUNITY_UNVERIFIED_PREPUZZLE_BASELINE_CLAIM"),
]


def baseline_regions():
    document = CHAT.read_text()
    speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
    regions = []
    for name, header, opening, puzzle_span in REGIONS:
        body, location = record_by_header(CHAT, header)
        body_start = location["character_span_zero_based_half_open"][0]
        quote_start = body_start + body.index(opening)
        quote_end = location["character_span_zero_based_half_open"][1]
        normalized, positions = alphabetic_source_map(document, quote_start, quote_end)
        puzzle_start, puzzle_end = puzzle_span
        baseline_offset, puzzle_offset = 0, puzzle_start
        mapped = []

        def append_segment(kind, baseline_start, baseline_end, decoded_start, decoded_end):
            raw_start = positions[baseline_start] if baseline_start < len(positions) else quote_end
            raw_end = positions[baseline_end - 1] + 1 if baseline_end > baseline_start else raw_start
            mapped.append({
                "kind": kind,
                "baseline_normalized_text": normalized[baseline_start:baseline_end],
                "puzzle_normalized_text": speech[decoded_start:decoded_end],
                "baseline_normalized_span_zero_based_half_open": [baseline_start, baseline_end],
                "baseline_source_location": text_location(document, raw_start, raw_end),
                "puzzle_decoded_span_zero_based_half_open": [decoded_start, decoded_end],
                "puzzle_encoded_fixture_span_zero_based_half_open": [447 + decoded_start, 447 + decoded_end],
            })

        for anchor in ANCHORS[name]:
            baseline_anchor = normalized.index(anchor, baseline_offset)
            puzzle_anchor = speech.index(anchor, puzzle_offset, puzzle_end)
            if baseline_anchor != baseline_offset or puzzle_anchor != puzzle_offset:
                append_segment("UNMATCHED_GAP_NOT_INTENT_PROOF", baseline_offset, baseline_anchor, puzzle_offset, puzzle_anchor)
            append_segment("EXACT_INHERITED_ANCHOR", baseline_anchor, baseline_anchor + len(anchor), puzzle_anchor, puzzle_anchor + len(anchor))
            baseline_offset = baseline_anchor + len(anchor)
            puzzle_offset = puzzle_anchor + len(anchor)
        if baseline_offset != len(normalized) or puzzle_offset != puzzle_end:
            append_segment("UNMATCHED_GAP_NOT_INTENT_PROOF", baseline_offset, len(normalized), puzzle_offset, puzzle_end)
        if "".join(segment["baseline_normalized_text"] for segment in mapped) != normalized:
            raise ValueError("Fixed anchors do not reconstruct the preserved baseline")
        if "".join(segment["puzzle_normalized_text"] for segment in mapped) != speech[puzzle_start:puzzle_end]:
            raise ValueError("Fixed anchors do not reconstruct the verified speech span")
        regions.append({
            "name": name, "baseline_record": location,
            "classification": "COMMUNITY_MOVIE_QUOTATION_NOT_AUTHENTICATED_ORIGINAL_SCRIPT",
            "puzzle_span_zero_based_half_open": puzzle_span,
            "baseline_selected_source_location": text_location(document, quote_start, quote_end),
            "fixed_anchor_count": len(ANCHORS[name]), "segments": mapped,
            "both_sources_round_trip": True,
            "unmatched_gap_is_not_automatically_creator_authored_edit": True,
            "duplicate_question_in_preserved_baseline": name == "opening_dialogue",
        })
    return regions


def preserved_spacing():
    path = ROOT / "research/sources/community-README.md"
    document = path.read_text()
    start = document.index("YOUR LIFE IS THE SUM")
    end = document.index("```", start)
    normalized, positions = alphabetic_source_map(document, start, end)
    speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
    if normalized != speech:
        raise ValueError("Preserved secondary spacing differs from the verified speech")
    return document, positions


def mapped_speech_anchor(phrase):
    speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
    offset = speech.index(phrase)
    if speech.find(phrase, offset + 1) != -1:
        raise ValueError("Expected one fixed public speech anchor")
    document, positions = preserved_spacing()
    raw_start, raw_end = positions[offset], positions[offset + len(phrase) - 1] + 1
    return {
        "phrase": phrase,
        "puzzle_decoded_span_zero_based_half_open": [offset, offset + len(phrase)],
        "puzzle_encoded_fixture_span_zero_based_half_open": [447 + offset, 447 + offset + len(phrase)],
        "secondary_spaced_source_location": text_location(document, raw_start, raw_end),
        "secondary_spacing": document[raw_start:raw_end],
        "word_boundaries_are_secondary": True,
    }


def dialogue_roles():
    body, location = record_by_header(CHAT, REGIONS[0][1])
    document = CHAT.read_text()
    start = location["character_span_zero_based_half_open"][0]
    roles = []
    for literal, puzzle_phrase in [("Neo: You haven’t answered my question.", "youyouhaventansweredmyquestion"), ("The Architect: Quite right.", "mequiteright")]:
        offset = body.index(literal)
        roles.append({
            "baseline_literal": literal,
            "baseline_source_location": text_location(document, start + offset, start + offset + len(literal)),
            "mapped_puzzle_anchor": mapped_speech_anchor(puzzle_phrase),
        })
    return {
        "roles": roles,
        "duplicate_neo_question_count_in_baseline_record": body.count("Neo: You haven’t answered my question."),
        "verified_question_count_in_puzzle": (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().count("youhaventansweredmyquestion"),
        "you_me_as_dialogue_roles_supported_not_authenticated": True,
        "double_you_not_independently_an_extraction_command": True,
        "secondary_baseline_duplication_is_not_a_creator_instruction": True,
    }


def variant_claims():
    document = CHAT.read_text()
    claims = []
    for header, literal, classification in CLAIMS:
        body, location = record_by_header(CHAT, header)
        offset = location["character_span_zero_based_half_open"][0] + body.index(literal)
        claims.append({
            "record": location, "literal": literal,
            "source_location": text_location(document, offset, offset + len(literal)),
            "classification": classification,
            "pre_puzzle_original_source_preserved": False,
        })
    return {
        "claims": claims,
        "exact_gap_versus_selected_quote_is_verified": True,
        "gap_intent_and_pre_puzzle_provenance_remain_unverified": True,
        "no_external_lookup_performed": True,
    }


def baseline_coverage(regions):
    preceding_opening = json.loads((ROOT / "research/artifacts/cycle15/sum-remainder-audit.json").read_text())
    preceding_clause = json.loads((ROOT / "research/artifacts/cycle14/speech-delta.json").read_text())
    intervals = [
        ("ALREADY_MAPPED_OPENING_NOT_RETESTED", preceding_opening["comparison"]["puzzle_opening_span_zero_based_half_open"]),
        ("ALREADY_MAPPED_REINSERTION_NOT_RETESTED", preceding_clause["alignment"]["puzzle_decoded_span_zero_based_half_open"]),
        *[("NEW_FIXED_BASELINE_REGION", region["puzzle_span_zero_based_half_open"]) for region in regions],
    ]
    intervals.sort(key=lambda entry: entry[1][0])
    cursor = 0
    coverage = []
    for classification, span in intervals:
        start, end = span
        if start < cursor:
            raise ValueError("Baseline coverage intervals overlap")
        if start > cursor:
            coverage.append({"classification": "BASELINE_NOT_PRESERVED_BY_SELECTED_QUOTATIONS", "span_zero_based_half_open": [cursor, start]})
        coverage.append({"classification": classification, "span_zero_based_half_open": span})
        cursor = end
    if cursor < 1539:
        coverage.append({"classification": "BASELINE_NOT_PRESERVED_BY_SELECTED_QUOTATIONS", "span_zero_based_half_open": [cursor, 1539]})
    return {
        "intervals": coverage,
        "selected_baseline_coverage_letters": sum(end - start for unused_classification, (start, end) in intervals),
        "uncovered_letters": sum(entry["span_zero_based_half_open"][1] - entry["span_zero_based_half_open"][0] for entry in coverage if entry["classification"] == "BASELINE_NOT_PRESERVED_BY_SELECTED_QUOTATIONS"),
        "no_claim_of_complete_original_movie_baseline": True,
        "uncovered_text_not_automatically_creator_insertion": True,
    }


def object_references():
    definitions = [
        ("wisemanabovehintedat", "DEICTIC_REFERENCE", "An above-positioned person/hint, not identified by this clause", False),
        ("worthhundredfourtyoftheinvestment", "VALUE_CLAIM", "A value/ratio assertion without a defined arithmetic input", False),
        ("arestlesssoul", "NARRATIVE_OBJECT", "Object of destruction in the adapted dialogue", True),
        ("yourwillpower", "NARRATIVE_OBJECT", "Object of the crash consequence, no indexed data type", True),
        ("yourwilltolive", "NARRATIVE_OBJECT", "Object of extermination, no encoded-stream binding", True),
        ("yourselfself", "AMBIGUOUS_TERMINAL_WORDING", "Repeated self source letters; role boundary versus emphasis not specified", True),
        ("ciaobellao", "TERMINAL_GREETING", "Terminal wording; no choice anchor or extraction count supplied", False),
    ]
    return [mapped_speech_anchor(phrase) | {
        "type": kind, "possible_referent": referent,
        "within_new_selected_baseline_region": covered,
        "explicit_binding_to_matrixsumlist_residual_or_faed": False,
        "defined_input_count_or_consumer": False,
    } for phrase, kind, referent, covered in definitions]


def report():
    preceding = ROOT / "research/artifacts/cycle15/sum-remainder-audit.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C15-SUM-REMAINDER-AUDIT" or "unexamined puzzle-specific speech edits" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding frozen experiment")
    regions = baseline_regions()
    evidence = [source(path) for path in (
        CHAT, ROOT / "research/artifacts/phase32-beaufort.txt",
        ROOT / "research/artifacts/phase32.txt", ROOT / "research/sources/community-README.md",
        preceding, ROOT / "research/artifacts/cycle14/speech-delta.json",
        ROOT / "research/artifacts/cycle11/trailer-referents.json",
    )]
    locations = [
        "research/evidence/cycle02/_work__chat_transcript.txt:32774",
        "research/evidence/cycle02/_work__chat_transcript.txt:117457",
        "research/evidence/cycle02/_work__chat_transcript.txt:33097",
        "research/evidence/cycle02/_work__chat_transcript.txt:84036",
        "research/evidence/cycle02/_work__chat_transcript.txt:95714",
        "research/artifacts/phase32-beaufort.txt:1", "research/artifacts/phase32.txt:5",
    ]
    hypotheses = []
    for suffix, description, confidence, assumptions, contradictions in [
        ("DIALOGUE-ROLES", "you/me replace dialogue speaker roles rather than define repeated-letter extraction", "MEDIUM-HIGH for local preserved comparison; UNKNOWN for creator intent", ["The selected community quote is a useful dialogue baseline", "Secondary spacing represents dialogue breaks only provisionally"], ["Baseline duplicates the Neo question and is not an authenticated script", "Decoded speech has no authored speaker punctuation", "Role replacement alone does not bind Architect choice or a word count"]),
        ("CONSEQUENCE-OBJECTS", "Edited crash/destruction objects are narrative consequences rather than typed operands for matrixsumlist", "MEDIUM for narrative compatibility; UNKNOWN for hidden operation", ["Ordinary object grammar is the least additional assumption", "A data operand requires an explicit cross-reference"], ["A puzzle-specific narrative object could still carry a hidden instruction", "No creator-attributed explanation settles operational versus narrative use", "No mapped edit specifies coordinates, encoded input or consumer"]),
        ("SPEECH-DEICTIC-SOURCE", "The unbound wiseman-above reference may identify a source hint before Architect-word selection", "LOW for exact referent; HIGH that a deictic reference is present", ["Above refers to a preserved prior textual or spatial source", "A source-authored referent exists rather than a generic thematic remark"], ["Selected baselines do not cover this clause", "No named person, unique prior hint, exact count or consumer is stated", "Mention order alone does not join it to matrixsumlist or the residual"]),
    ]:
        hypotheses.append({
            "id": "C16-" + suffix, "status": "INCONCLUSIVE", "hypothesis": description,
            "source_evidence": evidence, "source_locations": locations,
            "assumptions": assumptions,
            "operation_order": ["map fixed preserved dialogue anchors", "separate exact gaps from proven creator edits", "require a named source and consumer before extracting any words"],
            "input": "Verified public speech and three selected community baseline records",
            "output": "A typed semantic construction hypothesis, not extracted trial material",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Source-map wiseman-above against preserved earlier public text and exact chronology; require a unique authored antecedent, not a numeric or phrase sweep",
        })
    trailer = json.loads((ROOT / "research/artifacts/cycle11/trailer-referents.json").read_text())
    return {
        "id": "C16-SPEECH-OPERAND-AUDIT", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Unexamined edited speech objects supply a source or consumer binding for Architect last-word selection",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Preserved community quotes are partial baselines, not authenticated originals", "Fixed anchor gaps are comparisons, not automatic creator-intent proofs", "Spacing is secondary, while the1539 decoded letters are verified"],
        "operation_order": ["validate frozen next task", "map three unexamined fixed dialogue regions", "round-trip12 inherited anchors and12 gaps", "account for partial baseline coverage", "classify seven object references without extraction"],
        "input": "Existing1539-letter verified speech, frozen earlier span maps and preserved baseline records",
        "output": "Three exact source alignments, partial coverage map, dialogue-role and object-reference audits",
        "confidence": "HIGH for exact source/coverage comparisons; UNKNOWN for intended complete construction",
        "regions": regions, "coverage": baseline_coverage(regions),
        "dialogue_roles": dialogue_roles(), "variant_claims": variant_claims(),
        "object_references": object_references(), "hypotheses": hypotheses,
        "inherited_choice_limits_not_retested": {
            "source": source(ROOT / "research/artifacts/cycle11/trailer-referents.json"),
            "literal_choice_in_verified_speech": trailer["speech_wording"]["literal_choice_in_verified_speech"],
            "selected_word_count_is_not_specified": trailer["speech_wording"]["selected_word_count_is_not_specified"],
            "new_Architect_word_extractions": 0,
        },
        "result": "Three new fixed regions round-trip24 segments:12 inherited anchors/12 unmatched gaps. Selected old/new baseline coverage is1076 of1539 letters;463 letters remain uncovered. you/me fit dialogue-role replacement, and the quote duplicates a question absent from the puzzle. Adapted consequence objects and seven mapped references supply no source/count/consumer for Architect last words or a residual/faed join. Sedulously wording has an unverified pre-puzzle-variant claim; exact quote differences are not intent proof.",
        "contradictions": ["No authenticated complete movie baseline", "A duplicated community question cannot be promoted to a creator repetition rule", "No named encoded object or extraction count is supplied by consequence nouns", "Wiseman-above antecedent remains unknown"],
        "next_test": "Audit the exact wiseman-above clause against preserved earlier public puzzle text and chronology. Map possible antecedents without decrypting new material or scanning numeric/phrase combinations; retain unresolved reference if none is source-authored and unique.",
        "search_space": {"fixed_baseline_records": 3, "new_disjoint_speech_regions": 3, "fixed_inherited_anchors": 12, "fixed_alignment_segments": 24, "community_variant_claims": 2, "mapped_object_references": 7, "finite_semantic_hypotheses": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "speech-operand-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({
        "status": document["status"], "new_fixed_regions": len(document["regions"]),
        "baseline_covered_letters": document["coverage"]["selected_baseline_coverage_letters"],
        "baseline_uncovered_letters": document["coverage"]["uncovered_letters"],
        "explicit_choice_source_count_consumer": False, "new_cryptographic_trials": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
