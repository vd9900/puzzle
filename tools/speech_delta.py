import json

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle14"
BASELINE_HEADERS = [
    "=== [02.09.2023 03:41:03 UTC-05:00] Deleted Account",
    "=== [26.11.2023 02:52:19 UTC-05:00] Jerry",
]
SEGMENTS = [
    ("INHERITED", "The function of the", "thefunctionofthe"),
    ("REPLACEMENT", "One", "you"),
    ("INHERITED", "is now to return to the source", "isnowtoreturntothesource"),
    ("INSERTION", "", "codes"),
    ("INHERITED", "allowing a temporary dissemination of the code you", "allowingatemporarydisseminationofthecodeyou"),
    ("INSERTION", "", "hopefully"),
    ("INHERITED", "carry, reinserting the prime", "carryreinsertingtheprime"),
    ("REPLACEMENT", "program", "basics"),
    ("INHERITED", "After which you will be required to select from", "afterwhichyouwillberequiredtoselectfrom"),
    ("REPLACEMENT", "the matrix", "over"),
    ("REPLACEMENT", "23 individuals", "twentythreeciphers"),
    ("REPLACEMENT", "16 female", "sixteenencryptionsandor"),
    ("REPLACEMENT", "7 male", "sevenintertwinedpasswords"),
]


def normalize_with_positions(document, start, end):
    positions = [offset for offset in range(start, end) if document[offset].isascii() and document[offset].isalnum()]
    return "".join(document[offset].lower() for offset in positions), positions


def mapped_alignment():
    document = CHAT.read_text()
    baseline, first_location = record_by_header(CHAT, BASELINE_HEADERS[0])
    repeated, repeat_location = record_by_header(CHAT, BASELINE_HEADERS[1])
    if baseline != repeated:
        raise ValueError("The two preserved baseline quotes differ")
    speech_path = ROOT / "research/artifacts/phase32-beaufort.txt"
    speech = speech_path.read_text().strip()
    body_start, body_end = first_location["character_span_zero_based_half_open"]
    normalized, positions = normalize_with_positions(document, body_start, body_end)
    baseline_start = normalized.index("thefunctionoftheone")
    baseline_end = normalized.index("torebuildzion", baseline_start)
    puzzle_start = speech.index("thefunctionoftheyou")
    puzzle_end = puzzle_start + sum(len(puzzle) for unused_kind, unused_original, puzzle in SEGMENTS)
    expected_baseline = "".join(normalize_with_positions(original, 0, len(original))[0] for unused_kind, original, unused_puzzle in SEGMENTS)
    expected_puzzle = "".join(puzzle for unused_kind, unused_original, puzzle in SEGMENTS)
    if normalized[baseline_start:baseline_end] != expected_baseline or speech[puzzle_start:puzzle_end] != expected_puzzle:
        raise ValueError("Fixed segment alignment does not cover the exact source text")
    mapped = []
    baseline_offset, puzzle_offset = baseline_start, puzzle_start
    for kind, original, puzzle in SEGMENTS:
        original_normalized = normalize_with_positions(original, 0, len(original))[0]
        original_end = baseline_offset + len(original_normalized)
        if original_normalized:
            raw_start, raw_end = positions[baseline_offset], positions[original_end - 1] + 1
        else:
            raw_start = raw_end = positions[baseline_offset]
        mapped.append({
            "kind": kind,
            "baseline_phrase": original,
            "puzzle_phrase_normalized": puzzle,
            "baseline_normalized_span_zero_based_half_open": [baseline_offset, original_end],
            "baseline_quote_source_location": text_location(document, raw_start, raw_end),
            "puzzle_decoded_span_zero_based_half_open": [puzzle_offset, puzzle_offset + len(puzzle)],
            "puzzle_encoded_fixture_span_zero_based_half_open": [447 + puzzle_offset, 447 + puzzle_offset + len(puzzle)],
            "insertion_is_zero_width_in_baseline": not original_normalized,
        })
        baseline_offset, puzzle_offset = original_end, puzzle_offset + len(puzzle)
    if baseline_offset != baseline_end or puzzle_offset != puzzle_end:
        raise ValueError("Fixed segments leave uncovered source characters")
    return {
        "baseline_records": [first_location, repeat_location],
        "same_preserved_quote_in_two_messages": True,
        "baseline_classification": "COMMUNITY_MOVIE_QUOTATION_NOT_AUTHENTICATED_ORIGINAL_SCRIPT",
        "baseline_reposts_not_independent_corroboration": True,
        "normalization": "ASCII alphanumeric characters only, lowercase; original23/16/7 digits retained, not silently converted",
        "puzzle_decoded_span_zero_based_half_open": [puzzle_start, puzzle_end],
        "baseline_normalized_span_zero_based_half_open": [baseline_start, baseline_end],
        "segments": mapped,
        "kind_counts": {kind: sum(segment["kind"] == kind for segment in mapped) for kind in ("INHERITED", "REPLACEMENT", "INSERTION")},
        "full_selected_span_round_trip": True,
        "unaligned_remainder_not_extracted_or_interpreted": True,
    }


def report():
    preceding = OUTPUT / "source-binding-audit.json"
    frozen = json.loads(preceding.read_text())
    if "movie-dialogue quotations" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding analysis task")
    alignment = mapped_alignment()
    evidence = [source(CHAT), source(ROOT / "research/artifacts/phase32-beaufort.txt"), source(ROOT / "research/artifacts/phase32.txt"), source(preceding), source(ROOT / "research/artifacts/cycle13/relational-directives.json")]
    locations = ["research/evidence/cycle02/_work__chat_transcript.txt:33097", "research/evidence/cycle02/_work__chat_transcript.txt:45259", "research/artifacts/phase32-beaufort.txt:1", "research/artifacts/phase32.txt:5"]
    constraints = [
        {"feature": "prime noun and reinsertion-before-selection scaffold", "baseline_has_feature": True, "puzzle_specific_change": "program becomes basics", "inference_limit": "Creator retained this scaffolding; it is not independent evidence for a newly designed reinsertion algorithm"},
        {"feature": "23/16/7 numeric values", "baseline_has_feature": True, "puzzle_specific_change": "individuals/female/male become ciphers/encryptions/intertwined passwords; over and and/or added", "inference_limit": "Values are inherited; target nouns/modifiers change. Neither exact cipher counts nor letter positions are specified"},
        {"feature": "source referent", "baseline_has_feature": True, "puzzle_specific_change": "codes is inserted after source", "inference_limit": "This strengthens a code/source-object reading but does not select HTML, an encoded string or a specific operand"},
        {"feature": "carried object", "baseline_has_feature": True, "puzzle_specific_change": "hopefully is inserted", "inference_limit": "Object remains the code; no bytes, length or source name is supplied"},
    ]
    hypotheses = []
    for suffix, hypothesis, confidence, order, contradictions in [
        ("DELTA-OPERATIVE", "Puzzle-specific codes/basics/noun edits redirect retained movie wording into an operative instruction graph", "MEDIUM for deliberate edits; LOW for any exact operation", ["identify inserted/replaced wording", "bind edited nouns to exact existing objects", "only then apply the retained relational order"], ["No explicit source object or insertion site", "The surrounding grammar and numeric values are inherited", "Deliberate edits do not prove a particular numerical algorithm"]),
        ("DELTA-RECAP", "The modified speech recaps or foreshadows puzzle objects rather than providing a direct reinsertion algorithm", "MEDIUM for compatible narrative interpretation; UNKNOWN for exact placement", ["locate source/prime/numeric wording", "compare with already known public objects", "require separate explicit entrance/exit links"], ["Edits may be operational despite narrative scaffolding", "No creator-attributed record settles recap versus command", "No verified join from speech to matrixsumlist"]),
    ]:
        hypotheses.append({"id": "C14-" + suffix, "status": "INCONCLUSIVE", "hypothesis": hypothesis, "source_evidence": evidence, "source_locations": locations, "assumptions": ["The community quote faithfully represents a useful baseline", "Identical reposts are not independent original-script authentication"], "operation_order": order, "input": "Exact mapped puzzle-specific edits and retained scaffold", "output": "A competing semantic graph, not newly extracted trial material", "confidence": confidence, "contradictions": contradictions, "next_test": "Prioritize exact cross-references for edited nouns source codes/prime basics; do not infer a reinsertion site or cipher list from inherited wording"})
    return {
        "id": "C14-SPEECH-DELTA", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "A source-mapped baseline comparison distinguishes puzzle-specific instruction edits from inherited movie scaffolding",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["The preserved baseline is secondary community quotation, not authenticated movie source", "Fixed segments are a comparison protocol, not creator-provided word boundaries", "Retained grammar may still be intentional but supplies less independent evidence"],
        "operation_order": ["bind two exact original dated baseline quotations", "map13 fixed contiguous comparison segments", "verify complete selected-span coverage", "separate five inherited spans from eight edit spans", "compare operative versus recap hypotheses"],
        "input": "One repeated community baseline quote and one existing verified public speech",
        "output": "Exact comparison/source maps and adjusted independence/type constraints",
        "confidence": "HIGH for exact preserved text differences; MEDIUM for instruction significance; UNKNOWN for complete intended construction",
        "alignment": alignment, "constraint_independence": constraints, "hypotheses": hypotheses,
        "result": "Prime reinsertion/order and23/16/7 values already occur in the preserved movie baseline. Puzzle-specific edits include codes, hopefully, basics, over and changed target nouns. These edits may redirect the speech, but no operand/site/cipher list is established; inherited numbers/order are not independent construction evidence.",
        "contradictions": ["Baseline is not creator-authenticated or independently sourced", "Shared scaffold is not a newly discovered algorithm", "Codes/basics remain ambiguous object labels", "No direct source-keyed Bifid or residual60 binding"],
        "next_test": "Audit the preserved original image/frame-to-prime-marker labeling as a typed object correspondence, especially the near-white event's role, without weighting cells, changing a route or performing new cryptographic trials. Determine whether the missing link is object identity rather than another sum algorithm.",
        "search_space": {"preserved_quote_records": 2, "distinct_baseline_texts": 1, "fixed_contiguous_segments": 13, "finite_semantic_hypotheses": 2},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "speech-delta.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "mapped_segments": len(document["alignment"]["segments"]), "inherited_span_count": document["alignment"]["kind_counts"]["INHERITED"], "baseline_is_community_quote": True, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
