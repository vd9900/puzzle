import bisect
import json
import re
from datetime import datetime

from tools.instruction_graphs import HEADER, PRIMARY, ROOT, primary_layout, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle13"
ARTIFACT_NAME = "checkpoint-referents-v2.json"
CHECKPOINT_HEADERS = [
    "=== [06.08.2023 07:12:13 UTC-05:00] Jrk Bgrt",
    "=== [28.04.2025 11:57:17 UTC-05:00] Jrk Bgrt",
    "=== [28.04.2025 12:01:36 UTC-05:00] Jrk Bgrt",
]
CHECKPOINT_QUOTES = [
    'Once you hit a "ying yang", you\'ll be able to solve it the same day.',
    "Did anyone found yingyang? I don't think so, you guys are so smart, when yingyang is reached, 2 hours max.",
    "It’s the next phase, but I await the day someone finally gets there.",
]


def exact_checkpoint_records():
    document = CREATOR.read_text()
    records = []
    for header, quote in zip(CHECKPOINT_HEADERS, CHECKPOINT_QUOTES):
        body, creator_location = record_by_header(CREATOR, header)
        chat_body, chat_location = record_by_header(CHAT, header)
        start, end = creator_location["character_span_zero_based_half_open"]
        if quote not in body or body != chat_body:
            raise ValueError("Original checkpoint wording differs across dated exports")
        quote_start = document.index(quote, start, end)
        records.append({
            "creator_labeled_export": creator_location,
            "full_transcript": chat_location,
            "exact_public_quote": quote,
            "quote_location": text_location(document, quote_start, quote_start + len(quote)),
            "matching_exports_are_not_independent_authentication": True,
            "reply_target_metadata_preserved": False,
        })
    return records


def next_phase_context():
    document = CHAT.read_text()
    headers = list(HEADER.finditer(document))
    indices = [index for index, header in enumerate(headers) if header.group() == CHECKPOINT_HEADERS[2]]
    if len(indices) != 1:
        raise ValueError("Expected one original next-phase response")
    index = indices[0]
    nearby = []
    for offset, header in enumerate(headers[index - 4:index + 2], start=-4):
        body, evidence = record_by_header(CHAT, header.group())
        nearby.append({"relative_message_index": offset, "location": evidence, "body_not_republished": True})
    question, question_location = record_by_header(CHAT, headers[index - 4].group())
    if question != "is yinyang found after decoding an AES ciphertext?":
        raise ValueError("The bounded conversation's antecedent question differs")
    question_time = datetime.fromisoformat(question_location["archived_utc_timestamp"])
    response, response_location = record_by_header(CHAT, CHECKPOINT_HEADERS[2])
    response_time = datetime.fromisoformat(response_location["archived_utc_timestamp"])
    return {
        "public_question": question,
        "question_location": question_location,
        "response_location": response_location,
        "elapsed_question_to_response_seconds": int((response_time - question_time).total_seconds()),
        "intervening_messages": 3,
        "intervening_roles": ["Creator asks Que?", "Another participant quotes a bunny-page comment", "Another participant says the comment has been there for a while"],
        "window": nearby,
        "response_can_refer_to_question_or_intervening_page_discussion": True,
        "no_authenticated_reply_binding": True,
        "no_container_identified_by_the_question_or_response": True,
    }


def literal_occurrences():
    document = CREATOR.read_text()
    headers = list(HEADER.finditer(document))
    starts = [header.start() for header in headers]
    terms = {}
    for literal in ("yinyang", "yingyang", "ying yang", "Cosmic Duality", "SMALL", "small"):
        entries = []
        pattern = r"(?<![A-Za-z])" + re.escape(literal) + r"(?![A-Za-z])"
        flags = re.I if literal not in ("SMALL", "small") else 0
        for match in re.finditer(pattern, document, flags):
            header_index = bisect.bisect_right(starts, match.start()) - 1
            entries.append({"literal": match.group(), "header": headers[header_index].group(), **text_location(document, match.start(), match.end())})
        terms[literal] = {"case_matching": "CASE_INSENSITIVE" if flags else "CASE_SENSITIVE", "exact_word_occurrences": len(entries), "distinct_original_messages": len({entry["header"] for entry in entries}), "locations": entries}
    return {
        "source": source(CREATOR),
        "message_count": len(headers),
        "terms": terms,
        "scope": "Literal whole-word matches in this creator-labeled text export only; the separately verified encoded hint is not plain-text absence evidence",
        "no_semantic_or_creator_authentication_claim_from_counts": True,
    }


def construction_hypotheses(evidence, locations):
    shared = {
        "source_evidence": evidence,
        "source_locations": locations,
        "input": "Unknown output/intermediate from the unresolved public construction",
        "status": "INCONCLUSIVE",
    }
    return [
        shared | {
            "id": "C13-CHECKPOINT-LITERAL",
            "hypothesis": "yin-yang is a literal recognizable output token or named text checkpoint",
            "assumptions": ["The quoted name is intended as literal text", "Creator's ying spelling does not specify a different cipher alphabet", "An as-yet-unverified operation supplies the complete checkpoint"],
            "operation_order": ["prime/color instruction", "matrixsumlist object or operation", "Architect-related selection", "recognizable text checkpoint"],
            "output": "A public text object recognizably naming yin-yang, not merely a partial yang substring",
            "confidence": "LOW-MEDIUM; literal wording permits this but does not require it",
            "contradictions": ["hit/reached are also stage/object language", "No quoted exact required bytes or output format", "ying yang and yingyang differ from the decoded February2023 yinyang"],
            "next_test": "Accept a literal test only for an independently source-derived complete text object; do not generate spellings or anagrams to fit the name",
        },
        shared | {
            "id": "C13-CHECKPOINT-VISUAL",
            "hypothesis": "yin-yang denotes a recognizable visual or structural object rather than a required substring",
            "assumptions": ["The attributed cover contributes a visual recognition clue", "The object arises downstream of the ordered instructions", "Its source-to-output construction remains to be specified"],
            "operation_order": ["prime/color instruction", "matrixsumlist object or operation", "Architect-related selection", "recognizable dual object"],
            "output": "A structured public object with a justified yin-yang interpretation",
            "confidence": "MEDIUM for recognition semantics; LOW for any specific visual transformation",
            "contradictions": ["No explicit rendering or pixel mapping instruction", "Existing cover resemblance is already visible and does not establish a newly reached checkpoint", "Opposite-color appearance alone does not select residual/Bifid halves or routing"],
            "next_test": "Require an exact source-backed construction and a consumer; do not treat the already visible cover itself as proof of reaching the checkpoint",
        },
        shared | {
            "id": "C13-CHECKPOINT-PHASE",
            "hypothesis": "yin-yang denotes a later phase/object, with Cosmic Duality a possible but unverified label",
            "assumptions": ["The next-phase reply refers to the earlier yin-yang question rather than the intervening page comment", "Primary Cosmic Duality heading names the relevant later object", "Primary heading order reflects traversal, not merely parallel publication"],
            "operation_order": ["resolve an upstream construction", "reach a later public phase/object", "recognize the yin-yang checkpoint"],
            "output": "A later public puzzle object; no specific container binding is established",
            "confidence": "MEDIUM for later-stage semantics; LOW for identifying Cosmic Duality or a particular container",
            "contradictions": ["Three intervening messages and no reply ID leave the next-phase antecedent ambiguous", "Original SalPhaseIon and Cosmic Duality objects are already adjacent on one page", "No creator-attributed wording identifies SMALL, the inner container, residual60 or Bifid as this checkpoint's direct predecessor"],
            "next_test": "Audit only source-authored entrance/exit labels or exact cross-references that bind the named public phase to an upstream object; preserve parallel versus sequential ambiguity",
        },
    ]


def report():
    hint_path = ROOT / "research/artifacts/cycle11/hint-instruction-order.json"
    hint = json.loads(hint_path.read_text())
    visual_path = OUTPUT / "visual-correspondence.json"
    visual = json.loads(visual_path.read_text())
    if visual["id"] != "C13-VISUAL-CORRESPONDENCE":
        raise ValueError("Unexpected visual preflight")
    layout, unused_compact, unused_span = primary_layout()
    evidence = [source(CREATOR), source(CHAT), source(PRIMARY), source(hint_path), source(visual_path)]
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:804", "research/evidence/cycle02/_work__creator_jrk.txt:1186", "research/evidence/cycle02/_work__creator_jrk.txt:1198", "research/evidence/cycle02/_work__chat_transcript.txt:110453", "research/evidence/cycle02/_work__chat_transcript.txt:110465", "research/sources/salphaseion.html:19"]
    hypotheses = construction_hypotheses(evidence, locations)
    graphs = {
        hypotheses[0]["id"]: {"nodes": ["unresolved-construction", "complete-literal-object"], "edges": [["unresolved-construction", "complete-literal-object", "HYPOTHESIS_LITERAL_FORMAT_NOT_SPECIFIED"]]},
        hypotheses[1]["id"]: {"nodes": ["unresolved-construction", "recognizable-visual-object"], "edges": [["unresolved-construction", "recognizable-visual-object", "HYPOTHESIS_NO_SOURCE_RENDERING_RULE"]]},
        hypotheses[2]["id"]: {"nodes": ["upstream-object", "later-phase", "Cosmic-Duality-label"], "edges": [["upstream-object", "later-phase", "HYPOTHESIS_AMBIGUOUS_REPLY_ANTECEDENT"], ["later-phase", "Cosmic-Duality-label", "HYPOTHESIS_NOT_A_CREATOR_BINDING"]]},
    }
    return {
        "id": "C13-CHECKPOINT-REFERENTS", "revision": 2, "date": "2026-09-30", "status": "INCONCLUSIVE",
        "hypothesis": "Original checkpoint wording can distinguish a required literal token from a recognizable object or later phase",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Original dated text and context are faithfully preserved", "Speaker labels are attribution, not signed authentication", "No omitted reply metadata may be invented"],
        "operation_order": ["map three original dated checkpoint records", "separate repeated words from distinct messages", "map the six-message next-phase context", "compare primary headings with the frozen ordered hint", "retain three finite referent graphs"],
        "input": "Three original dated statements, one fixed context window, primary headings and existing ordered hint",
        "output": "Exact phrase/source maps, bounded contextual inference and three non-executed construction hypotheses",
        "confidence": "HIGH for wording/timing; MEDIUM for recognition or later-stage semantics; UNKNOWN for the complete construction",
        "records": exact_checkpoint_records(),
        "context": next_phase_context(),
        "literal_inventory": literal_occurrences(),
        "primary_headings": layout["headings"],
        "primary_small_literal_present": layout["small_literal_present"],
        "ordered_hint_phrases": hint["strongest_supported_clue_sequence"],
        "hypotheses": hypotheses,
        "data_flow_graphs": graphs,
        "eliminated_requirement": "Exact literal yinyang/yingyang text is not an established necessary gate for every possible public construction; unchanged literal extraction remains a bounded negative only",
        "result": "hit/reached and next-phase language support recognition or later-stage semantics, but do not specify output format or a named container. The next-phase response follows the AES question by84 seconds with three intervening messages and no reply binding. Cosmic Duality is a plausible public label, not a verified destination.",
        "contradictions": ["No unique literal/output-format requirement", "No authenticated reply target for next phase", "Cover relevance does not specify a decoding", "No new clue connects source-keyed Bifid/residual60 to a particular checkpoint object"],
        "next_test": "Audit exact source-authored relational wording in the modified Architect speech and adjacent instruction paragraphs: identify named inputs/outputs and whether prime reinsertion precedes selection. Do not extract new trial strings until an operand, selector and order are supported.",
        "search_space": {"original_checkpoint_messages": 3, "context_window_messages": 6, "finite_referent_hypotheses": 3, "cryptographic_trials": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / ARTIFACT_NAME, (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "original_checkpoint_messages": len(document["records"]), "finite_referent_hypotheses": len(document["hypotheses"]), "unique_literal_format_required": False, "specific_container_binding_verified": False, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
