import json
from datetime import datetime

from tools.instruction_graphs import HEADER, ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle20"
START_HEADER = "=== [03.08.2023 15:18:17 UTC-05:00] Deleted Account"
END_HEADER = "=== [03.08.2023 15:36:22 UTC-05:00] Zil"
ACK_HEADER = "=== [03.08.2023 15:33:50 UTC-05:00] Jrk Bgrt"
HARD_HEADER = "=== [03.08.2023 15:34:24 UTC-05:00] Jrk Bgrt"
NEXT_TEST = "Audit only the preserved July12 2026 close-friends hint screenshot and its fixed README attribution against an exact matching original creator/chat record if present. Establish text, sender/date attribution and the object referred to by it without investigating personal contacts. Determine whether the statement directly favors thematic/contextual recognition over an algorithmic operand; no external access, personal-data search, dictionaries or cryptographic trials."


def mapped_window():
    document = CHAT.read_text()
    headers = list(HEADER.finditer(document))
    first = next(index for index, entry in enumerate(headers) if entry.group() == START_HEADER)
    last = next(index for index, entry in enumerate(headers) if entry.group() == END_HEADER)
    if last - first + 1 != 16:
        raise ValueError("Unexpected fixed progress-context size")
    records = []
    for index in range(first, last + 1):
        entry = headers[index]
        end = headers[index + 1].start() if index + 1 < len(headers) else len(document)
        body_start = entry.end()
        while body_start < end and document[body_start].isspace():
            body_start += 1
        body_end = end
        while body_end > body_start and document[body_end - 1].isspace():
            body_end -= 1
        records.append({
            "header": entry.group(), "speaker": entry.group(5), "public_body": document[body_start:body_end],
            "source": source(CHAT), **text_location(document, body_start, body_end),
            "reply_target_metadata_preserved": False,
        })
    bodies = {entry["header"]: entry for entry in records}
    if bodies[ACK_HEADER]["public_body"] != "I saw that you guys got really really far already." or bodies[HARD_HEADER]["public_body"] != "Actually, the hardest part is done.":
        raise ValueError("Unexpected progress acknowledgement bodies")
    cross_checked = []
    for header in (ACK_HEADER, HARD_HEADER):
        creator_body, creator_location = record_by_header(CREATOR, header)
        chat_body, chat_location = record_by_header(CHAT, header)
        if creator_body != chat_body:
            raise ValueError("Progress body differs between exports")
        cross_checked.append({"creator_record": creator_location, "original_chat_record": chat_location})
    question_header = "=== [03.08.2023 15:32:00 UTC-05:00] Deleted Account"
    question_body, question_location = record_by_header(CHAT, question_header)
    if question_body != "But you can confirm if there is indeed a 3rd door that is yet to be found right?":
        raise ValueError("Unexpected prior third-door question")
    question_time = datetime.fromisoformat(question_location["archived_utc_timestamp"])
    ack_time = datetime.fromisoformat(cross_checked[0]["original_chat_record"]["archived_utc_timestamp"])
    hard_time = datetime.fromisoformat(cross_checked[1]["original_chat_record"]["archived_utc_timestamp"])
    return {
        "records": records, "creator_bodies_cross_checked": cross_checked,
        "nearest_prior_question": question_location,
        "third_door_question_to_acknowledgement_seconds": int((ack_time - question_time).total_seconds()),
        "acknowledgement_to_hardest_statement_seconds": int((hard_time - ack_time).total_seconds()),
        "community_matrix_and_prime_then_double_hash_then_nothing_are_separate_records": True,
        "no_cipher_recipe_output_or_named_operand_in_fixed_window": True,
        "flat_export_order_does_not_recover_reply_targets": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle20/phase-name-semantics.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C20-PHASE-NAME-SEMANTICS" or "hardest part is done" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen progress-context task")
    reference_path = ROOT / "research/artifacts/cycle18/final-reference-audit-v2.json"
    reference = json.loads(reference_path.read_text())["separate_question"]
    checkpoint_path = ROOT / "research/artifacts/cycle13/checkpoint-referents-v2.json"
    checkpoint = json.loads(checkpoint_path.read_text())
    evidence = [source(path) for path in (preceding, CREATOR, CHAT, reference_path, checkpoint_path)]
    locations = ["research/evidence/cycle02/_work__chat_transcript.txt:21154", "research/evidence/cycle02/_work__chat_transcript.txt:21187", "research/evidence/cycle02/_work__chat_transcript.txt:21190", "research/evidence/cycle02/_work__chat_transcript.txt:21193", "research/evidence/cycle02/_work__chat_transcript.txt:21199", "research/evidence/cycle02/_work__creator_jrk.txt:757", "research/evidence/cycle02/_work__creator_jrk.txt:760", "research/artifacts/cycle18/final-reference-audit-v2.json"]
    readings = [
        {"id": "C20-PROGRESS-GENERAL", "hypothesis": "The creator acknowledges aggregate community progress without confirming a particular transformation", "assumptions": ["You guys refers to the collective solver group", "Hardest part is a qualitative progress assessment"], "confidence": "MEDIUM-HIGH exact general wording; UNKNOWN completed object", "contradictions": ["The immediately preceding question asks about a third door", "Unpreserved reply targets might have narrowed the context"]},
        {"id": "C20-PROGRESS-THIRD-DOOR", "hypothesis": "The acknowledgement responds to the nearest prior third-door question", "assumptions": ["Flat adjacency indicates reply scope despite missing reply identifiers", "General progress wording indirectly answers the door question"], "confidence": "LOW-MEDIUM adjacency; LOW exact confirmation", "contradictions": ["No yes/no, door count or named entrance is confirmed", "No reply-target metadata preserved", "The statement may refer to aggregate earlier progress"]},
        {"id": "C20-PROGRESS-MATRIX-HASH", "hypothesis": "The acknowledgement validates the preceding community matrix/primes/double-hash interpretation", "assumptions": ["Multiple separate earlier messages form the creator's intended reply target", "General progress acknowledgement confirms an algorithm"], "confidence": "LOW; no recipe/output binding", "contradictions": ["Community double-hash message is followed by And nothing", "No exact recipe, output, input or affirmative algorithm reference", "Nearest preceding question is about a third door, not that method"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["map fixed context", "cross-check acknowledgement bodies", "distinguish progress claim from exact recipe confirmation"],
        "input": "Sixteen original flat-export records and two preserved creator bodies",
        "output": "One bounded acknowledgement-scope interpretation without algorithm promotion",
        "next_test": NEXT_TEST,
    } for entry in readings]
    return {
        "id": "C20-PROGRESS-ACKNOWLEDGEMENT", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "The original hardest-part-is-done acknowledgement confirms a specific constructed puzzle object or operation",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Only one declared16-record window is inspected", "Chronological adjacency is not authenticated reply scope", "A progress statement is not an exact transformation/output oracle"],
        "operation_order": ["validate frozen context task", "map sixteen exact original bodies", "cross-check two creator acknowledgements", "measure nearest-question and acknowledgement timing", "reuse earlier separate question and checkpoint limits", "compare three acknowledgement scopes"],
        "input": "One fixed original August2023 window plus existing source/name/checkpoint evidence",
        "output": "Exact public context maps, timing and three unresolved acknowledgement referents",
        "confidence": "HIGH bodies/order/timing; UNKNOWN reply scope and acknowledged object",
        "context": mapped_window(),
        "earlier_question_reused": {"source": source(reference_path), "question": reference, "no_btc_question_retested_or_reinterpreted_as_Bifid_confirmation": True},
        "checkpoint_reused": {"source": source(checkpoint_path), "no_specific_container_binding_derived": True, "no_literal_gate_or_checkpoint_experiment_repeated": True},
        "hypotheses": hypotheses,
        "result": "Fixed window shows separate community Matrix and prime numbers, Double hash and And nothing messages, then later third-door question. Creator's general progress acknowledgement follows that question110s later, hardest-part statement34s after. Neither names a method, output, operand, exact door or container; reply IDs are not preserved. Aggregate progress is best supported grammatically, while narrower reply scopes remain unverified. No Bifid, residual or double-hash validation follows.",
        "contradictions": ["No explicit recipe/output confirmation in the audited context", "Flat transcript cannot authenticate reply relationships", "General progress does not identify which missing construction edge is solved"],
        "next_test": NEXT_TEST,
        "search_space": {"fixed_context_windows": 1, "original_context_records": 16, "creator_acknowledgement_bodies_cross_checked": 2, "declared_acknowledgement_scopes": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "progress-acknowledgement.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "context_records": 16, "exact_method_or_output_confirmed": False, "new_trial_inputs": 0}, indent=2))


if __name__ == "__main__":
    main()
