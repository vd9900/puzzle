import json

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, record_by_header
from tools.trailer_referents import alphabetic_source_map


OUTPUT = ROOT / "research/artifacts/cycle15"
HEADERS = [
    "=== [01.09.2023 23:38:24 UTC-05:00] Deleted Account",
    "=== [24.01.2026 14:14:49 UTC-05:00] Black&White",
]
PREFIX = "Your life is the sum of a remainder of an unbalanced equation inherent to the programming of "


def opening_comparison():
    document = CHAT.read_text()
    speech_path = ROOT / "research/artifacts/phase32-beaufort.txt"
    speech = speech_path.read_text().strip()
    common, unused_common_positions = alphabetic_source_map(PREFIX, 0, len(PREFIX))
    if speech[:76] != common or speech[76:86] != "thispuzzle":
        raise ValueError("Existing verified speech opening differs")
    records = []
    for header in HEADERS:
        body, location = record_by_header(CHAT, header)
        body_offset = body.index(PREFIX)
        raw_start = location["character_span_zero_based_half_open"][0] + body_offset
        raw_end = raw_start + len(PREFIX) + len("the matrix")
        normalized, positions = alphabetic_source_map(document, raw_start, raw_end)
        if normalized != common + "thematrix":
            raise ValueError("Preserved community opening is not the fixed baseline")
        boundary = positions[len(common)]
        records.append({
            "record": location,
            "quoted_opening_source_location": text_location(document, raw_start, raw_end),
            "shared_prefix_source_location": text_location(document, raw_start, positions[len(common) - 1] + 1),
            "changed_referent_source_location": text_location(document, boundary, positions[-1] + 1),
            "baseline_normalized_length": len(normalized),
            "baseline_referent": "thematrix",
            "classification": "COMMUNITY_MOVIE_QUOTATION_NOT_AUTHENTICATED_ORIGINAL_SCRIPT",
        })
    anchors = []
    for phrase in ("yourlife", "sum", "remainder", "unbalancedequation", "thispuzzle"):
        offset = speech.index(phrase, 0, 86)
        anchors.append({
            "phrase": phrase,
            "verified_decoded_span_zero_based_half_open": [offset, offset + len(phrase)],
            "encoded_fixture_byte_span_zero_based_half_open": [447 + offset, 447 + offset + len(phrase)],
            "inherited_from_preserved_baseline": phrase != "thispuzzle",
        })
    return {
        "records": records,
        "baseline_normalized_openings_equal": True,
        "matching_secondary_quotations_not_independent_authentication": True,
        "shared_prefix_length": 76,
        "puzzle_opening_length": 86,
        "puzzle_opening_span_zero_based_half_open": [0, 86],
        "puzzle_encoded_opening_span_zero_based_half_open": [447, 533],
        "changed_puzzle_referent_span_zero_based_half_open": [76, 86],
        "changed_puzzle_referent": "thispuzzle",
        "anchors": anchors,
        "explicit_sum_operator_operand_or_list_format": False,
        "literal_matrixsumlist_in_opening": False,
    }


def report():
    preceding = OUTPUT / "label-boundary-audit.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C15-LABEL-BOUNDARY-AUDIT" or "sum/remainder opening" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding scoped task")
    comparison = opening_comparison()
    evidence = [source(CHAT), source(ROOT / "research/artifacts/phase32-beaufort.txt"), source(ROOT / "research/artifacts/phase32.txt"), source(preceding)]
    locations = ["research/evidence/cycle02/_work__chat_transcript.txt:32774", "research/evidence/cycle02/_work__chat_transcript.txt:164325", "research/artifacts/phase32-beaufort.txt:1", "research/artifacts/phase32.txt:5"]
    hypotheses = []
    for suffix, hypothesis, confidence, assumptions, contradictions in [
        ("SUM-NAMED-OBJECT", "matrixsumlist identifies the modified Architect speech by its recognizable sum/remainder opening", "MEDIUM-LOW for lexical recognition; UNKNOWN for exact object binding", ["The label is a reference rather than a numeric operation", "The creator intended the retained movie phrase to identify this exact source"], ["No word list or label equality specified", "The source is a speech paragraph, while the community recipe used another paragraph", "Inherited wording alone does not prove a creator-authored navigation rule"]),
        ("SUM-ARITHMETIC", "The retained sum/remainder language prescribes an arithmetic operation on a puzzle-derived remainder", "LOW without an operand or output format", ["Narrative wording is operative", "A separately specified remainder maps to a numeric representation"], ["Sum/remainder phrase is already in the preserved baseline", "The edited referent thispuzzle is not a list definition", "No values, axis, grouping or consuming object supplied", "Completed literal and weighted constructions are not reopened"]),
    ]:
        hypotheses.append({
            "id": "C15-" + suffix, "status": "INCONCLUSIVE", "hypothesis": hypothesis,
            "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions,
            "operation_order": ["locate exact modified-speech opening", "distinguish inherited phrase from edited referent", "require an explicit object or operand binding before further transformation"],
            "input": "Existing source opening and encoded matrixsumlist label",
            "output": "A finite semantic interpretation, not an extracted trial string",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Audit only unexamined puzzle-specific edits elsewhere in the preserved speech for an exact named object/consumer; require source anchors and count rules before extracting last words",
        })
    return {
        "id": "C15-SUM-REMAINDER-AUDIT", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "The modified speech's sum/remainder opening defines an intended sumlist object or arithmetic operand",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Preserved movie quotations are secondary baselines, not authenticated scripts", "Lexical recognition is weaker than an executable object/operand binding"],
        "operation_order": ["bind two original dated community quotes", "map the shared76-letter opening prefix", "map the changed referent and five fixed source anchors", "separate recognition from arithmetic interpretations"],
        "input": "Existing86-letter modified-speech opening and two preserved baseline quotations",
        "output": "Exact source maps, inherited-versus-edited wording and two bounded semantic hypotheses",
        "confidence": "HIGH for exact preserved-text comparison; UNKNOWN for complete intended construction",
        "comparison": comparison, "hypotheses": hypotheses,
        "result": "The76-letter sum/remainder scaffold is shared with both preserved movie quotations; only thematrix becomes thispuzzle at76:86. It supports possible recognition of an Architect object but supplies no sum operator, numeric operand, list serialization or residual60/faed570 join.",
        "contradictions": ["No explicit matrixsumlist name or numeric data in this opening", "Inherited phrase is not independent operation evidence", "Secondary quotations do not authenticate a full baseline", "No exact connection to prime residual, source-keyed Bifid or downstream text"],
        "next_test": "Audit preserved baseline coverage and unexamined puzzle-specific speech edits beyond the opening and reinsertion clause. Determine whether a named object/consumer can bind lastwordsbeforearchichoice; do not invent a choice anchor, word count, arithmetic grouping or new trial string.",
        "search_space": {"preserved_baseline_records": 2, "distinct_normalized_baseline_openings": 1, "fixed_opening_anchors": 5, "finite_semantic_hypotheses": 2},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "sum-remainder-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "shared_baseline_prefix_length": 76, "explicit_operand_or_list_format": False, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
