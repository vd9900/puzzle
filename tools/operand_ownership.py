import json

from tools.instruction_graphs import ROOT, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle17"
INPUTS = {
    "graph": "research/artifacts/cycle10/instruction-graphs-v3.json",
    "hint": "research/artifacts/cycle11/hint-instruction-order.json",
    "trailer": "research/artifacts/cycle11/trailer-referents.json",
    "boundary": "research/artifacts/cycle15/label-boundary-audit.json",
    "speech": "research/artifacts/cycle16/speech-operand-audit.json",
    "deictic": "research/artifacts/cycle16/deictic-source-audit-v2.json",
}
INTERFACES = [
    ("matrix-operand", "matrixsumlist", ["object_identity", "operation_or_label_role", "representation", "order_rule"]),
    ("Architect-selection", "lastwordsbeforearchichoice", ["source_identity", "choice_anchor", "word_count", "word_boundaries"]),
    ("this-binding", "thispassword", ["antecedent_identity", "backward_or_forward_scope"]),
    ("first-hash-input", "first-shabef", ["input_identity", "input_representation", "output_consumer"]),
    ("container-answer", "embedded-container", ["processing_rule", "output_identity"]),
    ("answer-hash-input", "second-shabef", ["answer_identity", "answer_representation", "output_consumer"]),
    ("parallel-join", "residual-and-Bifid", ["input_roles", "join_operation", "output_type", "consumer"]),
]
GRAPHS = [
    {
        "id": "C17-LOCAL-BACKWARD", "prior_ids": ["C10-G01", "C10-G06", "C11-T01"],
        "hypothesis": "Architect last words are the backward antecedent of thispassword before a local hash/container/answer-hash sequence",
        "interfaces": ["Architect-selection", "this-binding", "first-hash-input", "container-answer", "answer-hash-input"],
        "edges": [
            ("Architect-selection", "thispassword", "INFERRED_BACKWARD_REFERENCE"),
            ("thispassword", "first-shabef", "INFERRED_OPERAND_OWNERSHIP"),
            ("first-shabef", "embedded-container", "SOURCE_ADJACENCY_NOT_EXECUTION"),
            ("embedded-container", "answer-object", "UNRESOLVED_PROCESSING"),
            ("answer-object", "second-shabef", "INFERRED_ANS_REFERENCE"),
            ("second-shabef", "next-consumer", "UNKNOWN_DESTINATION"),
        ],
        "independent_constraints": ["z-delimited lastwords/thispassword adjacency", "two local shabef prefixes bracket the embedded container", "adapted speech supplies conditional reinsertion-before-selection wording"],
        "assumptions": ["this refers backward to selected words", "source reading order expresses local execution order", "ans names the intervening output"],
        "contradictions": ["No fixed Architect source/choice anchor/count", "thispassword has no explicit antecedent assignment", "No independently identified answer object or next consumer"],
        "confidence": "MEDIUM local grammar; UNKNOWN executable construction",
    },
    {
        "id": "C17-SUMLIST-SELECTOR", "prior_ids": ["C10-G03", "C11-T03"],
        "hypothesis": "matrixsumlist supplies ordering or selection information for an Architect-word object, rather than being literal selected text",
        "interfaces": ["matrix-operand", "Architect-selection", "this-binding", "first-hash-input"],
        "edges": [
            ("prime-color-object", "matrixsumlist", "ORDERED_MENTIONS_NOT_DATAFLOW"),
            ("matrixsumlist", "selection-rule", "UNKNOWN_OUTPUT_TYPE"),
            ("selection-rule", "Architect-selection", "UNKNOWN_SOURCE_AND_COUNT_BINDING"),
            ("Architect-selection", "thispassword", "INFERRED_BACKWARD_REFERENCE"),
            ("thispassword", "first-shabef", "INFERRED_OPERAND_OWNERSHIP"),
        ],
        "independent_constraints": ["one creator-attributed decoded hint mentions prime/color then matrixsumlist then lastwords", "primary matrixsumlist encoding also carries historical marker data", "lastwords and thispassword are neighboring decoded labels"],
        "assumptions": ["mention order implies dependence", "sumlist object supplies a selector", "a source-owned choice anchor and count exist"],
        "contradictions": ["No list definition, operand, order or positional rule", "Completed image/numeric routing realizations remain negative", "New dialogue roles and baseline gaps do not supply indices"],
        "confidence": "MEDIUM ordered clue association; LOW executable selector",
    },
    {
        "id": "C17-PARALLEL-OWNERSHIP", "prior_ids": ["C10-G02", "C10-G04", "C15-BOUNDARY-OBJECT"],
        "hypothesis": "dbbi supports parallel marker/residual and source-keyed Bifid roles, while matrixsumlist labels or joins an object without discarding its encoded data",
        "interfaces": ["matrix-operand", "parallel-join", "Architect-selection"],
        "edges": [
            ("dbbi91", "residual-object", "FROZEN_CONDITIONAL_TRANSFORM_NOT_INTENT"),
            ("dbbi91", "source-square", "FROZEN_TRANSFORM_NOT_INTENT"),
            ("faed570", "Bifid-object", "FROZEN_TRANSFORM_NOT_INTENT"),
            ("source-square", "Bifid-object", "FROZEN_TRANSFORM_NOT_INTENT"),
            ("residual-object", "join-object", "UNKNOWN_JOIN"),
            ("Bifid-object", "join-object", "UNKNOWN_JOIN"),
            ("matrixsumlist", "join-object", "UNKNOWN_LABEL_OR_OPERATION_OWNERSHIP"),
            ("join-object", "Architect-selection", "UNKNOWN_CONSUMER"),
        ],
        "independent_constraints": ["same dbbi source participates in two reproduced public transforms", "matrixsumlist source symbols support decoded-label and marker-data roles", "faed570 remains a distinct adjacent source object"],
        "assumptions": ["parallel reproduced transforms are intentional", "encoded label data may retain a role after label decoding", "an authored join explains the complete outputs"],
        "contradictions": ["Bifid is absent from primary instructions and ordered hint", "btcseed prefix depends on only eight source coordinates", "No join type or operand ownership specified; source dependencies are not independent intent evidence"],
        "confidence": "HIGH preserved dependencies; UNKNOWN intended join",
    },
    {
        "id": "C17-COMMAND-ROLE", "prior_ids": ["C10-G05", "C17-LOCAL-BACKWARD"],
        "hypothesis": "first-hint/last-command recalls an operation on a newly selected object, not necessarily the literal text of the earlier hint",
        "interfaces": ["Architect-selection", "this-binding", "first-hash-input", "answer-hash-input"],
        "edges": [
            ("HASHTHETEXT", "first-hint-reference", "INFERRED_COMMAND_RECALL"),
            ("first-hint-reference", "first-shabef", "OPERATION_ASSOCIATION_NOT_INPUT_BINDING"),
            ("Architect-selection", "thispassword", "INFERRED_BACKWARD_REFERENCE"),
            ("thispassword", "first-shabef", "UNKNOWN_TEXT_ARGUMENT"),
            ("answer-object", "second-shabef", "INFERRED_ANS_REFERENCE"),
        ],
        "independent_constraints": ["primary shabef prefix maps locally to SHA256", "ordinary remaining words say first hint/last command", "preserved audio says HASHTHETEXT without an argument"],
        "assumptions": ["first refers to an operative hint, not chronological earliest publication", "last-command refers to a reused operation", "a separate text object is the argument"],
        "contradictions": ["Audio hint is not explicitly identified by ourfirsthint", "January2021 echo is Deleted Account, not creator authentication", "Operation recognition alone does not bind input representation or output consumer"],
        "confidence": "MEDIUM-LOW command-role interpretation; UNKNOWN argument",
    },
]


def load_inputs():
    documents = {name: json.loads((ROOT / path).read_text()) for name, path in INPUTS.items()}
    preceding = documents["deictic"]
    if preceding["id"] != "C16-DEICTIC-SOURCE-AUDIT" or "operand-ownership preflight" not in preceding["next_test"]:
        raise ValueError("Unexpected preceding frozen task")
    return documents


def source_objects(documents):
    regions = documents["boundary"]["regions"]
    names = {region["name"]: region for region in regions}
    layout = documents["graph"]["primary_layout"]
    if names["matrixsumlist"]["decoded"] != "matrixsumlist" or names["thispassword"]["decoded"] != "thispassword":
        raise ValueError("Unexpected frozen labels")
    result = []
    for region in regions:
        result.append({
            "object": region["name"], "role": region["grammar_type"],
            "source": region["source"],
            "source_span": {key: region[key] for key in ("normalized_span_zero_based_half_open", "character_span_zero_based_half_open", "utf8_byte_span_zero_based_half_open", "line_one_based", "column_one_based")},
            "decoded_label": region.get("decoded"),
            "role_does_not_bind_an_argument": True,
        })
    for phrase in layout["command_subphrases"]:
        result.append({"object": phrase["name"], "role": "LOCAL_OPERATOR" if phrase["name"].endswith("shabef") else "ORDINARY_COMMAND_WORDING", "source": layout["source"], "source_span": phrase, "role_does_not_bind_an_argument": True})
    residuals = documents["graph"]["derived_source_maps"]["branches"]
    bifid = documents["graph"]["derived_source_maps"]["source_bifid"]
    result.extend([
        {"object": "residual-object", "role": "CONDITIONAL_RESEARCH_DERIVED_OBJECT", "source_owner": "dbbi91", "frozen_branch_lengths": [entry["residual_length"] for entry in residuals], "new_transformation": False},
        {"object": "Bifid-object", "role": "REPRODUCED_TRANSFORM_NOT_CREATOR_INTENT", "source_owners": ["dbbi91", "faed570"], "frozen_length": bifid["output_length"], "prefix_input_indices": bifid["prefix_input_indices"], "prefix_does_not_bind_output_consumer": True, "new_transformation": False},
        {"object": "SMALL", "role": "SECONDARY_CONTAINER_NAME", "source_owner": ["small-container-first-part", "small-container-second-part"], "primary_literal_present": layout["small_literal_present"], "container_is_input_not_known_answer": True},
        {"object": "HASHTHETEXT", "role": "PRESERVED_PUBLIC_AUDIO_COMMAND", "source": documents["graph"]["corroboration"]["hashtext"]["source"], "argument_bound": False},
    ])
    return result


def ownership_interfaces():
    return [{
        "interface": name, "instruction_or_object": owner,
        "required_bindings": required,
        "explicit_source_bindings": [],
        "unresolved_bindings": required,
        "input_ready": False,
        "absence_of_explicit_binding_is_not_impossibility_proof": True,
    } for name, owner, required in INTERFACES]


def graph_preflight(graph, interfaces):
    requirements = {entry["interface"]: entry for entry in interfaces}
    unresolved = {name: requirements[name]["unresolved_bindings"] for name in graph["interfaces"]}
    return graph | {
        "status": "INCONCLUSIVE", "symbolic_only": True,
        "unresolved_interfaces": unresolved,
        "unresolved_binding_count": sum(len(fields) for fields in unresolved.values()),
        "source_bound_executable_construction": False,
        "new_extracted_texts": 0, "new_cryptographic_trials": 0,
        "edges": [{"from": start, "to": end, "evidence_type": kind, "newly_executed": False} for start, end, kind in graph["edges"]],
    }


def report():
    documents = load_inputs()
    evidence = [source(ROOT / path) for path in INPUTS.values()]
    locations = ["research/sources/salphaseion.html:17", "research/artifacts/cycle11/hint-instruction-order.json:1", "research/artifacts/cycle11/trailer-referents.json:1", "research/artifacts/cycle16/speech-operand-audit.json:1", "research/artifacts/cycle16/deictic-source-audit-v2.json:1"]
    interfaces = ownership_interfaces()
    graphs = [graph_preflight(graph, interfaces) for graph in GRAPHS]
    hypotheses = [{
        "id": graph["id"], "status": graph["status"], "hypothesis": graph["hypothesis"],
        "source_evidence": evidence, "source_locations": locations, "assumptions": graph["assumptions"],
        "operation_order": [edge["from"] + " -> " + edge["to"] + " (" + edge["evidence_type"] + ")" for edge in graph["edges"]],
        "input": "Frozen public object/source maps; no newly extracted material",
        "output": "A symbolic graph with explicitly unresolved operand interfaces",
        "confidence": graph["confidence"], "contradictions": graph["contradictions"],
        "next_test": "Compare the two surviving thispassword reference scopes against the original unspaced segment grammar and exact secondary walkthrough wording; predeclare backward-result versus forward-recipe boundaries, with no candidate text or cryptographic execution",
    } for graph in graphs]
    speech = documents["speech"]
    return {
        "id": "C17-OPERAND-OWNERSHIP", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Existing typed source constraints select an intended operand-ownership graph without new transformations",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Only the four declared evidence-backed symbolic graph families are compared", "Mention order, lexical labels and argument assignment are separate claims", "Missing explicit bindings weaken executable interpretations without disproving implicit puzzle constructions"],
        "operation_order": ["load six frozen public-analysis reports", "retain exact primary typed object maps", "declare seven operand interfaces", "propagate current speech/baseline/attribution limits", "preflight four symbolic graphs without executing them"],
        "input": "Frozen public source/layout/dependency and speech-reference reports",
        "output": "Four symbolic construction graphs, seven unresolved interfaces and exact source ownership",
        "confidence": "HIGH source-constraint accounting; UNKNOWN intended execution graph",
        "source_objects": source_objects(documents), "interfaces": interfaces, "graphs": graphs, "hypotheses": hypotheses,
        "speech_constraints_propagated": {
            "baseline_covered_letters": speech["coverage"]["selected_baseline_coverage_letters"],
            "baseline_uncovered_letters": speech["coverage"]["uncovered_letters"],
            "question_repetition_not_a_selector": speech["dialogue_roles"]["double_you_not_independently_an_extraction_command"],
            "literal_choice": documents["trailer"]["speech_wording"]["literal_choice_in_verified_speech"],
            "word_count_unspecified": documents["trailer"]["speech_wording"]["selected_word_count_is_not_specified"],
            "deictic_antecedent_not_uniquely_bound": True,
        },
        "ordered_mentions_not_execution": documents["hint"]["strongest_supported_clue_sequence"],
        "thispassword_scope_survivors": ["BACKWARD_REFERENCE_TO_SELECTED_OBJECT", "FORWARD_LABEL_FOR_FOLLOWING_RECIPE"],
        "enter_role": {"fragment_lengths": documents["hint"]["enter_formatting"]["embedded_fragment_lengths"], "formatting_not_processing": True},
        "result": "Four symbolic graphs remain INCONCLUSIVE. All seven source/operand/consumer interfaces retain missing bindings. Local lastwords/thispassword adjacency is the strongest lexical handoff but permits backward-result or forward-recipe scope. A SHA operator is identifiable without identifying its argument; first-hint command recall is not literal-text ownership. SMALL names a source container, not a known answer. Frozen residual/Bifid dependencies do not supply a join. No graph is executable or selected by the new evidence alone.",
        "contradictions": ["Source adjacency cannot assign an operand by itself", "Decoding a label does not create the object it names", "A known operator and a repeated hash command do not identify an input or next consumer", "Prefix structure and overlapping source evidence cannot replace a complete join"],
        "next_test": "Perform one exact grammatical-scope experiment on the original z-delimited lastwordsbeforearchichoice / thispassword / shabefourfirsthintisyourlastcommand sequence. Compare only backward-result and forward-recipe reference scopes against the preserved secondary walkthrough wording and source punctuation/spacing. Do not extract candidate words, generate trial strings or repeat broader first-hint/source searches.",
        "search_space": {"frozen_reports": len(INPUTS), "symbolic_graphs": len(graphs), "operand_interfaces": len(interfaces), "declared_edges": sum(len(graph["edges"]) for graph in graphs), "thispassword_reference_scopes": 2, "new_transformations": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "operand-ownership.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "symbolic_graphs": len(document["graphs"]), "unresolved_operand_interfaces": len(document["interfaces"]), "source_bound_graphs": sum(graph["source_bound_executable_construction"] for graph in document["graphs"]), "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
