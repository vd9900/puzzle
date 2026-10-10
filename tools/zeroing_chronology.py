import json
from datetime import datetime

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle17"
DECODE_HEADER = "=== [19.05.2021 18:33:09 UTC-05:00] Deleted Account"
ZERO_HEADER = "=== [26.12.2021 15:18:32 UTC-05:00] Jrk Bgrt"
GENERIC_HEADER = "=== [22.03.2020 19:36:36 UTC-05:00] Deleted Account"


def literal_in_record(path, location, body, literal):
    offset = location["character_span_zero_based_half_open"][0] + body.index(literal)
    return {"literal": literal, **text_location(path.read_text(), offset, offset + len(literal))}


def chronology():
    graph = json.loads((ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json").read_text())
    fixed = json.loads((ROOT / "research/artifacts/cycle14/source-binding-audit.json").read_text())
    zero_record = next(entry for entry in fixed["records"] if entry["name"] == "prime-and-zeroing")
    decode_body, decode_location = record_by_header(CHAT, DECODE_HEADER)
    generic_body, generic_location = record_by_header(CHAT, GENERIC_HEADER)
    zero_body, zero_location = record_by_header(CREATOR, ZERO_HEADER)
    original_zero_body, original_zero_location = record_by_header(CHAT, ZERO_HEADER)
    if zero_location != zero_record["creator_labeled_export"] or original_zero_location != zero_record["full_transcript"]:
        raise ValueError("Frozen zeroing source map differs")
    if zero_body != original_zero_body:
        raise ValueError("Creator-attributed zeroing exports differ")
    earliest = graph["corpus_inventory"]["earliest_preserved_transcript_mentions"]
    if earliest["last-words"]["raw_file_line_one_based"] != decode_location["line_one_based"]:
        raise ValueError("Unexpected earliest saved lastwords occurrence")
    if "thispassword" not in decode_body or "lastwordsbeforearchichoice" not in decode_body:
        raise ValueError("Earliest decode record lacks both labels")
    if "this password" not in generic_body or "thispassword" in generic_body or "lastwords" in generic_body:
        raise ValueError("Unexpected generic earlier this-password context")
    delta = datetime.fromisoformat(zero_location["archived_utc_timestamp"]) - datetime.fromisoformat(decode_location["archived_utc_timestamp"])
    return {
        "earliest_exact_local_decode_record": decode_location,
        "decode_record_classification": "COMMUNITY_PUBLIC_DECODING_NOT_CREATOR_INTENT_PROOF",
        "local_decode_phrase_maps": [literal_in_record(CHAT, decode_location, decode_body, phrase) for phrase in ("lastwordsbeforearchichoice", "thispassword")],
        "creator_zero_record": zero_location, "original_chat_zero_record": original_zero_location,
        "same_zeroing_body_in_two_exports": True,
        "zeroing_phrase_map": literal_in_record(CREATOR, zero_location, zero_body, "some characters need to be 'zeroed out'"),
        "another_door_reference_map": literal_in_record(CREATOR, zero_location, zero_body, 'The previous "there is another door hint" is still a thing.'),
        "generic_earlier_this_password_record": generic_location,
        "generic_earlier_occurrence_is_not_encoded_label_evidence": True,
        "seconds_local_decode_predates_zeroing_hint": int(delta.total_seconds()),
        "date_order_does_not_prove_the_creator_excluded_an_already_known_step": True,
        "no_new_decoding_or_zeroing_masks": True,
    }


def frozen_local_zero_roles():
    boundary = json.loads((ROOT / "research/artifacts/cycle15/label-boundary-audit.json").read_text())
    constraints = json.loads((ROOT / "research/artifacts/cycle14/source-binding-audit.json").read_text())["operation_constraints"]
    regions = {region["name"]: region for region in boundary["regions"]}
    return {
        "existing_local_label_decoder_regions": [{
            "name": regions[name]["name"], "transform": regions[name]["transform"],
            "source": regions[name]["source"],
            "original_span_zero_based_half_open": regions[name]["normalized_span_zero_based_half_open"],
            "local_zero_symbol_role": "o represents numeric digit0 in an existing decoder",
            "not_evidence_of_a_new_global_zeroing_rule": True,
        } for name in ("lastwordsbeforearchichoice", "thispassword")],
        "prime_zeroing_constraints_reused": constraints,
        "old_numeric_zero_decode_is_not_a_new_mask_operation": True,
        "literal_character_zero_deletion_and_arithmetic_zero_are_not_equivalent": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle17/thispassword-scope.json"
    task = json.loads(preceding.read_text())
    if task["id"] != "C17-THISPASSWORD-SCOPE" or "source-availability/chronology audit" not in task["next_test"]:
        raise ValueError("Unexpected frozen preceding task")
    evidence = [source(path) for path in (
        CHAT, CREATOR, ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json",
        ROOT / "research/artifacts/cycle14/source-binding-audit.json",
        ROOT / "research/artifacts/cycle15/label-boundary-audit.json", preceding,
    )]
    locations = ["research/evidence/cycle02/_work__chat_transcript.txt:18496", "research/evidence/cycle02/_work__chat_transcript.txt:5471", "research/evidence/cycle02/_work__creator_jrk.txt:627", "research/evidence/cycle02/_work__chat_transcript.txt:19305", "research/sources/salphaseion.html:17"]
    hypotheses = []
    for suffix, description, confidence, assumptions, contradictions in [
        ("ZERO-LOCAL-ROLE", "The already-decoded o=0 trailer labels are a local representation role, not sufficient identification of the later zeroing operand", "HIGH role/chronology distinction; UNKNOWN intended zeroing site", ["Local numeric decoding and later instructions are separate typed claims", "A later hint may recap an already known stage"], ["Chronology does not prove the hint concerns a different operation", "Creator wording does not exclude a known decoder", "No specific source characters or zeroing mechanism identified"]),
        ("ZERO-DOOR-SEPARATION", "The reiterated another-door and prime/zeroing clauses remain separate constraints until a shared operand or site is source-bound", "HIGH missing-binding observation; UNKNOWN joint construction", ["Shared message context is not an explicit common operand", "Previous-door reference should be resolved as text before assigning numeric selectors"], ["Creator may intend a coupled construction implicitly", "No exact operator or input ownership is supplied", "Existing reinsertion wording cannot establish a zeroing inverse"]),
    ]:
        hypotheses.append({
            "id": "C17-" + suffix, "status": "INCONCLUSIVE", "hypothesis": description,
            "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions,
            "operation_order": ["compare fixed source publication dates", "retain local numeric-zero representation role", "require a shared source/operand/site before adding a zeroing edge"],
            "input": "Existing trailer-decoding evidence and dated creator-attributed hint",
            "output": "A source/chronology constraint, not a new mask or transformed string",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Source-map the original previous another-door hint and same-day context, testing only date versus coordinates versus object-label grammar before interpreting its braces/numbers",
        })
    data = chronology()
    return {
        "id": "C17-ZEROING-CHRONOLOGY", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Known trailer numeric-zero decoding fixes the operand of the creator's later zeroing instruction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Preserved timestamps and exact source bodies are compared, not authenticated publication intent", "An earlier generic this-password phrase is not the later decoded label", "A creator can repeat a previously known requirement"],
        "operation_order": ["bind three exact dated message headers", "reuse frozen earliest/zeroing source maps", "cross-check zeroing body between two exports", "compare chronology without new decoding", "retain local-zero versus unbound-zeroing distinction"],
        "input": "Existing public trailer-decoding evidence, generic occurrence and creator-attributed zeroing statement",
        "output": "Fixed date/source comparison and two finite zero-role hypotheses",
        "confidence": "HIGH exact preserved date/role comparison; UNKNOWN intended zeroing operand",
        "chronology": data, "local_zero_roles": frozen_local_zero_roles(), "hypotheses": hypotheses,
        "result": "Exact lastwords/thispassword local decoding was posted May19 2021 before the December26 2021 prime/zeroing hint. The earlier March2020 this-password hit is generic prose, not encoded-label evidence. Existing o=0 decoding explains two local representations but does not identify the later zeroing source/characters/mechanism. Hint chronology alone cannot exclude a recap. Another-door context and reinsertion remain unjoined; no new mask or inverse inferred.",
        "contradictions": ["Temporal order alone does not identify or exclude an operand", "Local decoder substitution is not a universal zeroing rule", "Co-occurring previous-door/prime/zeroing references do not supply a shared site"],
        "next_test": "Resolve only the exact prior another-door hint cited by the December2021 source. Map April1 2021 original wording, braces/spacing and same-day creator context against date, coordinate and object-label readings. Do not turn1/4/21 into an index sweep, introduce a new route or generate trial text.",
        "search_space": {"fixed_message_headers": 3, "local_decoded_labels": 2, "creator_zeroing_exports_cross_checked": 2, "finite_semantic_hypotheses": 2, "new_zeroing_masks": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "zeroing-chronology.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "local_decode_predates_zeroing_hint_seconds": document["chronology"]["seconds_local_decode_predates_zeroing_hint"], "zeroing_operand_identified": False, "new_zeroing_masks": 0}, indent=2))


if __name__ == "__main__":
    main()
