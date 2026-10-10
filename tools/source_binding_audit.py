import json
from datetime import datetime

from tools.instruction_graphs import HEADER, ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle14"
RECORDS = [
    ("first-piece", "=== [14.01.2020 05:38:06 UTC-05:00] Jrk Bgrt", ["Yellow has a number and so does Blue.", "Go back to the first puzzle piece without further ado."]),
    ("first-or-zero", "=== [21.05.2020 01:12:59 UTC-05:00] Jrk Bgrt", ["First or zero"]),
    ("prime-part", "=== [01.03.2021 06:34:42 UTC-05:00] Jrk Bgrt", ["You are at the prime part already???"]),
    ("prime-aside", "=== [01.03.2021 06:35:15 UTC-05:00] Jrk Bgrt", ["Oh wait, shouldn't have said that. That might have been a hint"]),
    ("prime-and-zeroing", "=== [26.12.2021 15:18:32 UTC-05:00] Jrk Bgrt", ["prime numbers being mentioned", "some characters need to be 'zeroed out'"]),
    ("prime-importance", "=== [09.01.2023 05:10:46 UTC-05:00] Jrk Bgrt", ["At least prime number is very important to get any further."]),
]


def original_records():
    document = CREATOR.read_text()
    mapped = []
    for name, header, phrases in RECORDS:
        body, creator_location = record_by_header(CREATOR, header)
        chat_body, chat_location = record_by_header(CHAT, header)
        if body != chat_body:
            raise ValueError("Original dated instruction exports disagree")
        start, end = creator_location["character_span_zero_based_half_open"]
        locations = []
        for phrase in phrases:
            offset = document.index(phrase, start, end)
            locations.append({"literal": phrase, **text_location(document, offset, offset + len(phrase))})
        mapped.append({"name": name, "creator_labeled_export": creator_location, "full_transcript": chat_location, "phrases": locations, "matching_exports_are_not_independent_authentication": True})
    times = [datetime.fromisoformat(entry["creator_labeled_export"]["archived_utc_timestamp"]) for entry in mapped]
    if times != sorted(times):
        raise ValueError("Original instruction chronology differs")
    return mapped


def bounded_context(header, before, after):
    document = CHAT.read_text()
    headers = list(HEADER.finditer(document))
    indices = [index for index, entry in enumerate(headers) if entry.group() == header]
    if len(indices) != 1:
        raise ValueError("Expected one original context target")
    index = indices[0]
    if index < before or index + after >= len(headers):
        raise ValueError("Fixed source window exceeds transcript")
    mapped = []
    for relative in range(-before, after + 1):
        unused_body, location = record_by_header(CHAT, headers[index + relative].group())
        mapped.append({"relative_message_index": relative, "location": location, "body_not_republished": True})
    return mapped


def context_evidence():
    first = bounded_context(RECORDS[1][1], 3, 0)
    question, question_location = record_by_header(CHAT, first[-2]["location"]["header"])
    if question != "Do you mean the answer to another door from the 1st piece?":
        raise ValueError("The first/zero antecedent question differs")
    stage_body, unused_stage_location = record_by_header(CHAT, first[0]["location"]["header"])
    if not stage_body.startswith("first piece is a zero piece?"):
        raise ValueError("The preserved piece-numbering discussion differs")
    prime = bounded_context(RECORDS[2][1], 3, 3)
    prime_question, unused_prime_location = record_by_header(CHAT, prime[0]["location"]["header"])
    if prime_question != "just say which primes 2,3,5,7 we need use" or prime[-1]["location"]["header"] != RECORDS[3][1]:
        raise ValueError("The bounded prime question/aside context differs")
    sumlist = bounded_context(RECORDS[-1][1], 1, 0)
    sum_question, unused_sum_location = record_by_header(CHAT, sumlist[0]["location"]["header"])
    if sum_question != "sumlist matrix -contains prime numbers ? xD":
        raise ValueError("The community sumlist question differs")
    def elapsed(window):
        return int((datetime.fromisoformat(window[-1]["location"]["archived_utc_timestamp"]) - datetime.fromisoformat(window[0]["location"]["archived_utc_timestamp"])).total_seconds())
    return {
        "first_or_zero": {"window": first, "public_question": question, "question_location": question_location, "question_to_response_seconds": elapsed(first[-2:]), "best_supported_referent": "first/zero puzzle-piece numbering", "not_a_defined_array_origin_or_bit_operator": True, "no_reply_identifier_preserved": True},
        "prime_part": {"window": prime, "public_community_question": prime_question, "question_to_prime_response_seconds": elapsed(prime[:4]), "confirms_prime_relevance_not_the_community_prime_values": True, "no_source_mask_axis_or_operand_specified": True},
        "sumlist_response": {"window": sumlist, "public_community_question": sum_question, "question_to_response_seconds": elapsed(sumlist), "generic_prime_importance_not_a_yes_to_prime_valued_sumlist": True, "no_reply_identifier_preserved": True},
    }


def report():
    preceding = ROOT / "research/artifacts/cycle13/relational-directives.json"
    frozen = json.loads(preceding.read_text())
    if "prime/zeroing hint chronology" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding frozen task")
    records = original_records()
    evidence = [source(CREATOR), source(CHAT), source(preceding), source(ROOT / "research/sources/maintained-hints__2021-03-01-primes.png")]
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:195", "research/evidence/cycle02/_work__creator_jrk.txt:375", "research/evidence/cycle02/_work__creator_jrk.txt:486", "research/evidence/cycle02/_work__creator_jrk.txt:489", "research/evidence/cycle02/_work__creator_jrk.txt:627", "research/evidence/cycle02/_work__creator_jrk.txt:672", "research/evidence/cycle02/_work__chat_transcript.txt:9802", "research/evidence/cycle02/_work__chat_transcript.txt:20073"]
    hypotheses = []
    for suffix, claim, order, limits, confidence in [
        ("FIRST-PIECE", "First/zero points back to the original puzzle piece rather than prescribing zero-based array indexing", ["identify original piece", "return to its information", "retain unspecified consuming operation"], ["No reply ID proves the antecedent", "A stage reference does not specify source pixels, text or reinsertion"], "MEDIUM-HIGH for local piece-numbering interpretation; UNKNOWN for data operation"),
        ("ZEROING-SEPARATE", "Zeroing and prime reinsertion are separately constrained operations until a common operand/site is established", ["retain required prime relevance", "retain some-character zeroing at an unspecified point", "retain speech reinsertion-before-selection only conditionally"], ["No creator wording binds zeroed characters to prime positions", "No wording equates zeroing with deletion or says reinsertion reverses it", "Separate operations may eventually share a construction, but this is not established"], "HIGH for missing binding; UNKNOWN for intended relation"),
        ("SUMLIST-PRIMES", "The January2023 response establishes prime importance but does not establish that a sumlist contains prime-valued entries", ["map community sumlist question", "map generic creator-attributed response", "retain operand/type uncertainty"], ["Community question and creator response have different assertion strength", "No yes/no, sums, list entries, axis or container supplied"], "HIGH for wording distinction; UNKNOWN for sumlist content"),
    ]:
        hypotheses.append({"id": "C14-" + suffix, "status": "INCONCLUSIVE", "hypothesis": claim, "source_evidence": evidence, "source_locations": locations, "assumptions": ["Chronology and labels are faithfully preserved", "No unpreserved reply metadata may be inferred"], "operation_order": order, "input": "The fixed original dated wording and its bounded context", "output": "A typed constraint, not a generated construction or trial string", "confidence": confidence, "contradictions": limits, "next_test": "Compare preserved baseline dialogue with puzzle-specific speech edits before counting these constraints as independent creator choices"})
    return {
        "id": "C14-SOURCE-BINDING-AUDIT", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Original-piece/prime/zeroing chronology supplies a source, operand or insertion site for the speech's local dependency",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Speaker labels are preserved attribution, not authentication", "Ordinary stage language does not by itself define a bit/index operation", "Prime and zeroing wording must not be strengthened beyond the source"],
        "operation_order": ["bind six exact dated creator-labeled records", "verify corresponding full-chat locations", "map three fixed antecedent windows", "separate constraints on stages from constraints on operands/operations"],
        "input": "Six dated public records, three bounded source windows and the frozen speech audit",
        "output": "Source-mapped chronology, three finite assertion-strength hypotheses and missing binding fields",
        "confidence": "HIGH for words/source spans; MEDIUM-HIGH for local piece reference; UNKNOWN for complete intended construction",
        "records": records, "contexts": context_evidence(), "hypotheses": hypotheses,
        "operation_constraints": {"original_piece_return_supported": True, "prime_relevance_explicit": True, "some_character_zeroing_explicit": True, "zeroing_means_deletion": "NOT_SPECIFIED", "zeroing_equals_inverse_of_reinsertion": "NOT_SPECIFIED", "same_operand_or_site": "NOT_SPECIFIED", "prime_mask_values_axis_and_order": "NOT_SPECIFIED", "carried_code_object": "NOT_SPECIFIED", "reinsertion_site": "NOT_SPECIFIED"},
        "result": "First/zero has direct puzzle-piece numbering context; prime relevance is explicit, but neither the March2021 question nor January2023 sumlist question is a creator-specified prime selection. Prime zeroing/reinsertion remains unbound; no new transformation is justified.",
        "contradictions": ["No exact operand/site supplied", "Generic importance is not confirmation of a community construction", "Co-occurrence of prime and zeroing does not specify a shared mask or inverse operation", "Inherited dialogue scaffolding must be separated from puzzle-specific edits"],
        "next_test": "Source-map preserved movie-dialogue quotations against verified modified speech, distinguish inherited prime/order/numeric scaffolding from puzzle-specific edits, and retain baseline attribution limits.",
        "search_space": {"dated_creator_records": 6, "fixed_context_windows": 3, "context_messages": 13, "finite_assertion_hypotheses": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "source-binding-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "dated_records": len(document["records"]), "context_windows": 3, "source_operand_site_binding_verified": False, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
