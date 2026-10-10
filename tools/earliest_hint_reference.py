import bisect
import json
import re
from datetime import datetime

from tools.first_piece_domain import exact_anchor
from tools.instruction_graphs import HEADER, ROOT, source, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle19"
NEXT_TEST = "Compare only the preserved original phase3.2 instruction prefix and edited speech's named source codes/basics/selection nouns against the original phase3 riddle outputs and two separately authored source branches. Determine whether any named earlier object is explicitly carried forward or is merely a movie-reference scaffold. Reuse existing transforms/maps; do not extract word/index trial inputs or run ciphers."


def earliest_rabbit_report():
    document = CHAT.read_text()
    matches = list(re.finditer("follow the white rabbit", document, re.I))
    if not matches:
        raise ValueError("No preserved rabbit wording")
    headers = list(HEADER.finditer(document))
    positions = [entry.start() for entry in headers]
    first = matches[0]
    header = headers[bisect.bisect_right(positions, first.start()) - 1].group()
    expected = "=== [20.04.2019 02:18:49 UTC-05:00] Ewout"
    if header != expected:
        raise ValueError("Unexpected earliest preserved exact rabbit wording")
    body, location = record_by_header(CHAT, header)
    if body != "What can he mean with follow the white rabbit?":
        raise ValueError("Unexpected rabbit reference body")
    acknowledgement_header = "=== [20.04.2019 11:18:49 UTC-05:00] Jrk Bgrt"
    creator_body, creator_location = record_by_header(CREATOR, acknowledgement_header)
    chat_body, chat_location = record_by_header(CHAT, acknowledgement_header)
    if creator_body != chat_body or creator_body != "Ok.. somebody has cracked the first code.":
        raise ValueError("Unexpected first-code acknowledgement")
    elapsed = int((datetime.fromisoformat(chat_location["archived_utc_timestamp"]) - datetime.fromisoformat(location["archived_utc_timestamp"])).total_seconds())
    return {
        "case_insensitive_exact_phrase_occurrences_in_preserved_chat": len(matches),
        "earliest_record": location, "earliest_body": body,
        "earliest_phrase": exact_anchor(CHAT, body),
        "first_code_acknowledgement": {"creator_record": creator_location, "original_chat_record": chat_location},
        "rabbit_reference_precedes_code_acknowledgement_seconds": elapsed,
        "earliest_reference_is_a_community_question_not_creator_instruction": True,
        "earliest_preserved_occurrence_is_not_original_publication_date": True,
        "other_occurrences_counted_not_interpreted_as_independent_hints": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle19/png-source-structure.json"
    saved = json.loads(preceding.read_text())
    if saved["id"] != "C19-PNG-SOURCE-STRUCTURE" or "firsthint/lastcommand" not in saved["next_test"]:
        raise ValueError("Unexpected frozen earliest-hint reference task")
    graph_path = ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json"
    graph = json.loads(graph_path.read_text())
    binding_path = ROOT / "research/artifacts/cycle14/source-binding-audit.json"
    binding = json.loads(binding_path.read_text())
    commands = graph["primary_layout"]["command_subphrases"]
    if [entry["literal"] for entry in commands] != ["shabef", "ourfirsthintisyourlastcommand", "shabef", "anstoo"]:
        raise ValueError("Unexpected frozen local command wording")
    notebook = ROOT / "research/sources/maintained-phase0.ipynb"
    approximation = 'The first hint given was something along the lines of \\"follow the white rabbit\\".'
    secondary = [
        exact_anchor(ROOT / "research/sources/maintained-README.md", '* "Follow the white rabbit"'),
        exact_anchor(notebook, approximation),
        exact_anchor(ROOT / "research/sources/community-README.md", 'the English text "our first hint is your last command"'),
    ]
    evidence = [source(path) for path in (preceding, graph_path, binding_path, CHAT, CREATOR, notebook, ROOT / "research/sources/maintained-README.md", ROOT / "research/sources/community-README.md", ROOT / "research/sources/salphaseion.html")]
    locations = ["research/evidence/cycle02/_work__chat_transcript.txt:32", "research/evidence/cycle02/_work__chat_transcript.txt:107", "research/evidence/cycle02/_work__creator_jrk.txt:2", "research/sources/maintained-README.md:87", "research/sources/maintained-phase0.ipynb:18", "research/sources/community-README.md:381", "research/sources/salphaseion.html:17", "research/artifacts/cycle14/source-binding-audit.json"]
    interpretations = [
        {"id": "C19-FIRSTHINT-RABBIT", "hypothesis": "Ourfirsthint recalls the initial rabbit/source-following instruction rather than the later audio instruction", "assumptions": ["First is a chronological or initial-source reference", "Early community question accurately reports an earlier clue"], "confidence": "MEDIUM earliest-reference chronology; LOW creator-authenticated wording and final operation", "contradictions": ["Earliest exact report is a question by Ewout, not the creator", "Maintained notebook explicitly gives approximate wording", "Following an initial source does not itself specify a final argument or algorithm"]},
        {"id": "C19-FIRSTHINT-COMMAND", "hypothesis": "Ourfirsthint recalls an earlier operative command such as HASHTHETEXT, independently of earliest chronological hint wording", "assumptions": ["First is local to the alternate-path command context", "The object to be acted on must be assigned separately"], "confidence": "MEDIUM-LOW local command grammar; UNKNOWN hint antecedent", "contradictions": ["No primary firsthint phrase explicitly names the audio clue", "The earliest preserved rabbit reference precedes known later audio reporting", "Command recognition does not select a literal input"]},
        {"id": "C19-FIRSTHINT-LITERAL", "hypothesis": "Ourfirsthint supplies the literal wording of an earlier hint as a text object instead of recalling its operation", "assumptions": ["Command permits a metonymic text-input reading", "One hint has exact creator-authored wording and a uniquely identified scope"], "confidence": "LOW exact operand binding", "contradictions": ["Earlier rabbit wording is only approximately attributed", "Lastcommand lexically names an operation rather than an argument", "First/zero is already bound to piece context, not to literal hint text"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["reuse exact local operator/reference segmentation", "locate earliest preserved rabbit wording", "separate chronological reference from command and argument identity"],
        "input": "Frozen command/source maps and fixed primary/secondary public references",
        "output": "One bounded firsthint referent reading without selected text, hash or route",
        "next_test": NEXT_TEST,
    } for entry in interpretations]
    return {
        "id": "C19-EARLIEST-HINT-REFERENCE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Early source-reference provenance distinguishes chronological first-hint wording from the later command's operand identity",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Earliest exact preserved phrase is not necessarily earliest publication", "Frozen First/zero context and current command segmentation are reused without re-experimentation", "Only three referent roles are declared"],
        "operation_order": ["validate preceding task", "reuse exact primary command map and First/zero context", "count one exact rabbit phrase in preserved chat", "bind earliest occurrence to its original speaker/body", "cross-check first-code acknowledgement in two exports", "map three fixed secondary attributions", "distinguish source, command and literal input roles"],
        "input": "Preserved chat, three fixed secondary phrases and existing source/command maps",
        "output": "Exact early provenance/timing plus three unresolved firsthint referent hypotheses",
        "confidence": "HIGH original record/chronology; UNKNOWN exact authored first-hint and final binding",
        "earliest_rabbit": earliest_rabbit_report(), "secondary_attributions": secondary,
        "commands_reused": {"source": source(graph_path), "subphrases": commands, "no_decoding_or_segment_variants": True},
        "First_zero_context_reused": {"source": source(binding_path), "record": binding["records"][1], "original_piece_return_supported": binding["operation_constraints"]["original_piece_return_supported"], "no_index_origin_or_literal_hint_operand_derived": True},
        "hypotheses": hypotheses,
        "result": "Earliest preserved exact follow-the-white-rabbit phrase is Ewout's April20 2019 question, nine hours before creator-attributed first-code acknowledgement. Notebook labels the phrase approximate. This supports an early initial-source association but not creator-authenticated wording or a final literal operand. Original shabef/ourfirsthint reference/second-shabef/anstoo segmentation and First/zero piece context remain unchanged. Chronological rabbit recall, local command recall and literal-hint argument readings remain distinct; none binds a final input or consumer.",
        "contradictions": ["Community reporting cannot authenticate the original hint text", "Preserved chronology cannot identify firsthint's intended local domain", "Repeated First/zero and rabbit themes do not specify an extraction or hash argument"],
        "next_test": NEXT_TEST,
        "search_space": {"exact_chat_phrase_patterns": 1, "earliest_phrase_records_mapped": 1, "creator_acknowledgements_cross_checked": 1, "fixed_secondary_attributions": 3, "frozen_command_subphrases": 4, "declared_referent_readings": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "earliest-hint-reference.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "earliest_rabbit_speaker": "Ewout", "seconds_before_code_acknowledgement": document["earliest_rabbit"]["rabbit_reference_precedes_code_acknowledgement_seconds"], "unique_command_or_argument": False, "new_trial_inputs": 0}, indent=2))


if __name__ == "__main__":
    main()
