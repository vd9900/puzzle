import json

from tools.instruction_graphs import ROOT, source, text_location, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle20"
PRIMARY_ANCHORS = (
    ("research/sources/phase2.html", "--> parts 1..7 --> sha-256 -> dgst is the password to enter Phase 3.", "EXPLICIT_LOCAL_AGGREGATE_AND_CONSUMER"),
    ("research/artifacts/phase3.txt", "The thinker's 1name behind all of that would grant you access to the next step (of humanity).", "RIDDLE_OUTPUT_ROLE_NOT_LATER_CARRIED_OBJECT"),
    ("research/artifacts/phase3.txt", "just add giveit in front of the answer", "EXPLICIT_LOCAL_PREFIX_OPERATION"),
    ("research/artifacts/phase3.txt", "3.The fundamental limit to the precision with which certain pairs of physical properties are know.", "LOCAL_RIDDLE_NOT_NAMED_CARRIED_OBJECT"),
    ("research/artifacts/phase3.txt", "Phase 3.2 is ciphered with aes-256-cbc base64 and a sha256 pw, yet again.", "EXPLICIT_NEXT_CONTAINER_FORMAT_NOT_FINAL_OPERAND"),
)
PREFIX_ANCHORS = (
    ("some of my answers", "LOCAL_SPEAKER_ANSWERS_NOT_AN_EXPLICIT_PREVIOUS_RIDDLE_AGGREGATE"),
    ("your first question", "LOCAL_DIALOGUE_QUESTION_NOT_A_GLOBAL_SELECTOR"),
    ("... am I here? Wake up, you...", "LOCAL_DIALOGUE_AND_TRANSFORM_HINT_NOT_A_NAMED_CARRIED_OBJECT"),
    ("I've designed you a beautiful strategic position.", "POSITION_REFERENCE_WITHOUT_TYPED_SOURCE_ASSIGNMENT"),
)
NEXT_TEST = "Audit the exact primary phrase as wide as the first one seen as a source-reference/type constraint. Compare only the already documented first14x14 grid, earlier eight-file image page, earlier chess/FEN object and current decimal codebook column domain. Require matching object type, width definition and an authored antecedent; do not resize boards, reroute symbols, rebuild alphabets or decode new candidates."


def mapped_literal(path, literal, role, ascii_prefix_limit=None):
    payload = path.read_bytes()
    document = payload[:ascii_prefix_limit].decode("ascii") if ascii_prefix_limit else payload.decode("utf-8")
    if document.count(literal) != 1:
        raise ValueError("Expected one fixed carry-ownership anchor")
    start = document.index(literal)
    return {"source": source(path), "literal": literal, "role": role, **text_location(document, start, start + len(literal))}


def named_edges():
    return [
        {"source_object": "Phase2 local parts1..7", "consumer": "Phase3 entry", "binding": "EXPLICIT_PRIMARY_AGGREGATE", "later_carried_object_identity": "NOT_ASSIGNED"},
        {"source_object": "Phase3 thinker-name answer", "consumer": "next-step riddle context", "binding": "EXPLICIT_LOCAL_ACCESS_ROLE", "later_carried_object_identity": "NOT_ASSIGNED"},
        {"source_object": "Phase3 middle answer", "consumer": "giveit-prefixed local answer", "binding": "EXPLICIT_PRIMARY_PREFIX", "later_carried_object_identity": "NOT_ASSIGNED"},
        {"source_object": "Phase3 precision-limit riddle answer", "consumer": "Phase3.2 local entry context", "binding": "LOCAL_ORDER_WITHOUT_EXPLICIT_CONCATENATION_SYNTAX", "later_carried_object_identity": "NOT_ASSIGNED"},
        {"source_object": "Phase3.2 my answers / first question", "consumer": "local dialogue", "binding": "LOCAL_SPEAKER_ROLE", "later_carried_object_identity": "NOT_ASSIGNED"},
        {"source_object": "speech code you hopefully carry", "consumer": "prime-basics reinsertion then selection", "binding": "CONDITIONAL_OPERATIVE_ROLE_WITHOUT_INPUT_IDENTITY", "later_carried_object_identity": "NOT_ASSIGNED"},
    ]


def report():
    preceding = ROOT / "research/artifacts/cycle19/earliest-hint-reference.json"
    prior = json.loads(preceding.read_text())
    if prior["id"] != "C19-EARLIEST-HINT-REFERENCE" or "explicitly carried forward" not in prior["next_test"]:
        raise ValueError("Unexpected frozen carry-forward task")
    archive_pairs = (
        ("research/artifacts/phase3.txt", "research/sources/maintained-phase2-assets__phase3.txt"),
        ("research/artifacts/phase32.txt", "research/sources/maintained-phase3-assets__phase3.2.txt"),
    )
    for fixture, archive in archive_pairs:
        if (ROOT / fixture).read_bytes() != (ROOT / archive).read_bytes():
            raise ValueError("Public fixture/archive mismatch")
    relational_path = ROOT / "research/artifacts/cycle13/relational-directives.json"
    relational = json.loads(relational_path.read_text())
    delta_path = ROOT / "research/artifacts/cycle14/speech-delta.json"
    delta = json.loads(delta_path.read_text())
    branch_path = ROOT / "research/artifacts/cycle12/source-join-preflight-v2.json"
    branch = json.loads(branch_path.read_text())["source_paragraph_roles"]
    namespace_path = ROOT / "research/artifacts/cycle18/notation-namespace.json"
    namespace = json.loads(namespace_path.read_text())
    directives = relational["directives"]["mapped_anchors"]
    if len(directives) != 8 or branch["paragraphs"][2]["byte_span_zero_based_half_open"] != [447, 1986]:
        raise ValueError("Unexpected frozen speech/branch mapping")
    primary = [mapped_literal(ROOT / relative, literal, role) for relative, literal, role in PRIMARY_ANCHORS]
    prefix_path = ROOT / "research/artifacts/phase32.txt"
    prefix = [mapped_literal(prefix_path, literal, role, 443) for literal, role in PREFIX_ANCHORS]
    phase3_text = (ROOT / "research/artifacts/phase3.txt").read_bytes().decode()
    answer_names = {name: name.casefold() in phase3_text.casefold() for name in ("Jacque Fresco", "Heisenberg")}
    paths = [preceding, relational_path, delta_path, branch_path, namespace_path, ROOT / "research/sources/phase2.html", ROOT / "research/artifacts/phase32-beaufort.txt"]
    paths += [ROOT / relative for pair in archive_pairs for relative in pair]
    evidence = [source(path) for path in paths]
    locations = [f'{entry["source"]["path"]}:{entry["line_one_based"]}' for entry in primary + prefix]
    locations += ["research/artifacts/cycle13/relational-directives.json", "research/artifacts/cycle14/speech-delta.json", "research/artifacts/cycle12/source-join-preflight-v2.json", "research/artifacts/cycle18/notation-namespace.json"]
    variants = [
        {"id": "C20-CARRY-PREVIOUS-ANSWERS", "hypothesis": "The code you hopefully carry is the aggregate of earlier Phase3 riddle outputs", "assumptions": ["Carry refers to a retained earlier-stage input", "The earlier riddle aggregate survives its local entry use as a later object"], "confidence": "LOW later operand ownership", "contradictions": ["Speech names no earlier answer, aggregate or source span", "My answers in the prefix belongs to the current speaker", "Earlier explicit local consumers do not assign this later carried object"]},
        {"id": "C20-CARRY-NARRATIVE", "hypothesis": "Current answers/question and carried-code references primarily retain local Architect dialogue roles without assigning an earlier riddle aggregate", "assumptions": ["Local dialogue antecedents are read ordinarily", "Puzzle-specific noun edits need separate operative bindings"], "confidence": "MEDIUM local grammatical ownership; UNKNOWN concealed operation", "contradictions": ["Codes/hopefully/basics and selection nouns are mapped puzzle edits", "A narrative reading alone does not explain the intended end-stage construction"]},
        {"id": "C20-CARRY-SOURCE-OBJECT", "hypothesis": "The carried code is another source-derived object, potentially from the initial-image/prime/sumlist branch rather than earlier riddle answers", "assumptions": ["Return-to-source is operative", "An unassigned source object is carried into the speech instructions"], "confidence": "MEDIUM source-return association; LOW exact object identity", "contradictions": ["No directive names dbbi, residual, faed or a specific image region", "No insertion site, count or consumer assigned", "Reproduced transformations do not authenticate a cross-stage carry edge"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["reuse local riddle output roles", "compare original current dialogue references", "retain unassigned carried object before reinsertion/selection"],
        "input": "Original stage instructions and frozen speech/source maps; no derived entry material",
        "output": "A symbolic cross-stage ownership interpretation with the missing input edge explicit",
        "next_test": NEXT_TEST,
    } for entry in variants]
    return {
        "id": "C20-CARRY-FORWARD-OWNERSHIP", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Original stage instructions explicitly carry a named earlier answer object into the later speech's reinsertion/selection construction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["An earlier local entry input is not automatically a later retained operand", "Names supplied by secondary solutions are not original source labels", "Previously mapped prefix, speech delta and codecs are controls, not rerun experiments"],
        "operation_order": ["validate frozen next task", "verify two fixture/archive pairs", "map five primary local-object anchors and four original-prefix anchors", "reuse eight directive maps and six paragraph roles", "compare six cross-stage ownership interfaces", "retain three finite carried-object readings without deriving input"],
        "input": "Public Phase2/Phase3/Phase3.2 instructions, existing speech delta/directives and branch maps",
        "output": "Exact local named-object scope, six symbolic interfaces and three unresolved carry hypotheses",
        "confidence": "HIGH local primary wording and frozen maps; UNKNOWN intended carried object",
        "primary_local_anchors": primary, "current_prefix_anchors": prefix,
        "fixture_archive_pairs_verified": [list(pair) for pair in archive_pairs],
        "earlier_names_not_literal_in_primary_phase3": answer_names,
        "frozen_controls": {
            "speech_directives": {"source": source(relational_path), "anchors": directives},
            "speech_delta": {"source": source(delta_path), "segments": delta["alignment"]["segments"], "no_baseline_realignment": True},
            "branch_roles": {"source": source(branch_path), "roles": branch},
            "local_namespace": {"source": source(namespace_path), "phase2_domain": namespace["namespaces"]["phase2_explicit_domain"]},
        },
        "ownership_interfaces": named_edges(), "explicit_later_carried_input_identities": 0,
        "hypotheses": hypotheses,
        "result": "Earlier parts1..7 have an explicit local Phase3 consumer; Phase3 riddle output roles and prefix operation are local to entry. Current my-answers/first-question references belong to Architect dialogue, not an explicit previous-answer aggregate. Frozen carried-code/reinsertion/selection wording does not name an earlier output or branch object. Six ownership interfaces leave the later carried identity unassigned. This rejects promoting an earlier local entry input into a later carry edge, not all possible intended reuse.",
        "contradictions": ["No named prior-output equality or carry assignment occurs in the audited primary clauses", "Generic answer/code vocabulary does not establish data identity", "Speech edits may be operative even when the original dialogue is narrative"],
        "next_test": NEXT_TEST,
        "search_space": {"fixture_archive_pairs": 2, "primary_local_anchors": 5, "original_prefix_anchors": 4, "frozen_directive_maps": 8, "frozen_paragraph_roles": 6, "cross_stage_ownership_interfaces": 6, "declared_carry_readings": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "carry-forward-ownership.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "ownership_interfaces": 6, "explicit_later_carried_inputs": 0, "new_trial_inputs": 0}, indent=2))


if __name__ == "__main__":
    main()
