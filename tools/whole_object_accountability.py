import json

from tools.instruction_graphs import ROOT, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle21"
ALIASES = {
    "dbbi91": {"dbbi91", "source-square", "residual-object"},
    "matrixsumlist": {"matrixsumlist"},
    "faed570": {"faed570", "Bifid-object"},
    "lastwordsbeforearchichoice": {"Architect-selection"},
    "thispassword": {"thispassword"},
    "first-command": {"first-shabef", "first-hint-reference"},
    "small-container-first-part": {"embedded-container"},
    "enter": set(),
    "small-container-second-part": {"embedded-container"},
    "answer-command": {"second-shabef"},
}
NEXT_TEST = "Examine only frozen source-keyed Bifid output structure and full dependency map as a public text object: exact length/alphabet/repetitions, boundary at the recognized seven-letter prefix, and any independently sourced instruction that specifies the remaining563-letter body's role. Reuse the existing full output without alternate squares, periods, routes, normalization, trial inputs or cryptographic searches. Distinguish complete-object structure from prefix recognition and preserve previous statistical controls."


def report():
    preceding = ROOT / "research/artifacts/cycle21/source-name-association.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C21-SOURCE-NAME-ASSOCIATION" or "whole-object accountability audit" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen whole-object task")
    boundary_path = ROOT / "research/artifacts/cycle15/label-boundary-audit.json"
    boundary = json.loads(boundary_path.read_text())
    ownership_path = ROOT / "research/artifacts/cycle17/operand-ownership.json"
    ownership = json.loads(ownership_path.read_text())
    maps_path = ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json"
    maps = json.loads(maps_path.read_text())
    regions = boundary["regions"]
    if {entry["name"] for entry in regions} != set(ALIASES):
        raise ValueError("Unexpected frozen source-region names")
    intervals = [entry["normalized_span_zero_based_half_open"] for entry in regions + boundary["z_delimiters"]]
    intervals.sort()
    offset = 0
    for start, end in intervals:
        if start != offset or end <= start:
            raise ValueError("Frozen source regions do not form exact partition")
        offset = end
    if offset != 1075 or sum(entry["length"] for entry in regions) != 1072:
        raise ValueError("Unexpected full source accounting")
    role_rows = []
    for graph in ownership["graphs"]:
        nodes = {edge[side] for edge in graph["edges"] for side in ("from", "to")}
        rows = []
        for region in regions:
            aliases = sorted(ALIASES[region["name"]] & nodes)
            rows.append({
                "source_region": region["name"], "length": region["length"],
                "mapped_symbolic_nodes": aliases,
                "region_represented_in_this_fragment": bool(aliases),
                "mapping_is_analyst_role_alias_not_authored_assignment": True,
                "source_bound_end_to_end_consumer": False,
            })
        role_rows.append({
            "graph_id": graph["id"], "region_role_rows": rows,
            "graph_is_a_partial_symbolic_fragment_not_a_complete_claim": True,
            "absent_regions_do_not_by_themselves_reject_partial_graph": True,
            "complete_source_bound_execution": graph["source_bound_executable_construction"],
        })
    bifid = maps["derived_source_maps"]["source_bifid"]
    if bifid["output_length"] != 570 or bifid["prefix_input_indices"] != [0, 1, 2, 3, 285, 286, 287, 288]:
        raise ValueError("Unexpected frozen Bifid dependency accounting")
    evidence = [source(path) for path in (preceding, boundary_path, ownership_path, maps_path, ROOT / "research/sources/salphaseion.html")]
    locations = ["research/sources/salphaseion.html:17", "research/artifacts/cycle15/label-boundary-audit.json", "research/artifacts/cycle17/operand-ownership.json", "research/artifacts/cycle10/instruction-graphs-v3.json"]
    readings = [
        {"id": "C21-ACCOUNT-FULL-CONSTRUCTION", "hypothesis": "The intended construction ultimately assigns roles to the full source objects rather than validating only recognized fragments", "assumptions": ["Apparent data regions are purposeful unless source evidence supports decoration", "Mechanical decoding and a downstream consumer are different requirements"], "confidence": "MEDIUM puzzle-design constraint; HIGH current missing-consumer accounting", "contradictions": ["No explicit instruction says every symbol is independently operative", "Some region roles may be formatting or deliberate redundancy", "Partial graphs are not themselves invalid for being incomplete"]},
        {"id": "C21-ACCOUNT-DUAL-ROLE", "hypothesis": "The encoded matrixsumlist region retains a data role in addition to its decoded label, supporting a later full-object construction", "assumptions": ["Frozen continued marker use is intentional", "Decoded label does not license discarding its original104 encoded symbols"], "confidence": "HIGH frozen dual-use positions; UNKNOWN intended remaining-data consumer", "contradictions": ["Historical marker convention is not an authored operation", "Dual use does not specify a join or output role", "No new reinsertion or routing follows from retained data"]},
        {"id": "C21-ACCOUNT-PREFIX-ONLY", "hypothesis": "Recognizing the Bifid prefix is sufficient to identify the intended output while its remaining body can be ignored", "assumptions": ["A source instruction licenses retaining only seven output letters", "The remaining563-letter object has no downstream role"], "confidence": "LOW; no source-authorized discard or prefix consumer", "contradictions": ["Full output is570 letters and eight input coordinates determine the prefix", "No discard rule or complete-output consumer is authored", "Prior conditional statistical controls do not prove full construction"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["reuse exact source partition", "account for ten regions across four partial graphs", "separate mechanical coverage from whole-output consumer binding"],
        "input": "Frozen public primary-region, symbolic-graph and Bifid dependency maps",
        "output": "A bounded whole-object role interpretation without discarding or transforming source data",
        "next_test": NEXT_TEST,
    } for entry in readings]
    return {
        "id": "C21-WHOLE-OBJECT-ACCOUNTABILITY", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Existing instruction graph fragments account for all original source material and full derived outputs in an intended construction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Ten source regions plus three delimiters are a frozen partition", "Analyst graph aliases do not create primary input assignments", "Fragments cannot be used to claim a complete graph"],
        "operation_order": ["validate frozen task", "reuse source regions and delimiter coverage", "compare forty region/graph symbolic roles", "reuse full Bifid/prefix dependency accounting", "distinguish partial graph and complete construction requirements", "retain three finite accountability readings"],
        "input": "Original source partition and four existing symbolic graph fragments",
        "output": "Full region coverage ledger and whole-output completeness constraints",
        "confidence": "HIGH source/graph/dependency counts; UNKNOWN intended roles and consumer",
        "frozen_primary_partition": {"source": source(boundary_path), "regions": regions, "delimiters": boundary["z_delimiters"], "region_characters": 1072, "delimiter_characters": 3, "total_characters": 1075, "no_partition_or_codec_recomputed": True},
        "graph_accountability": role_rows,
        "Bifid_object_reused": {"source": source(maps_path), "full_output_length": 570, "recognized_prefix_length": 7, "remaining_body_length": 563, "prefix_input_indices": bifid["prefix_input_indices"], "all570_dependencies_already_mapped": len(bifid["coordinate_source_map"]) == 570, "recognized_prefix_is_not_full_output_or_instruction": True, "complete_output_consumer_authored": False, "no_Bifid_transform_or_statistical_control_repeated": True},
        "hypotheses": hypotheses,
        "result": "Frozen ten regions1072 characters plus three delimiters cover1075 exactly. Forty symbolic region/graph comparisons show partial fragments with unresolved consumers, not complete constructions; missing fragment regions alone are not rejection. Full Bifid output570 and its563-letter body remain distinct from recognized prefix determined by eight source coordinates. Mechanical full mapping and partial recognition do not authenticate a whole-output consumer or license source discard.",
        "contradictions": ["No graph currently supplies complete source-bound input/output ownership", "Recognition of a seven-letter prefix leaves full-object role unknown", "A whole-object design expectation is not itself an authored extraction instruction"],
        "next_test": NEXT_TEST,
        "search_space": {"frozen_primary_regions": 10, "frozen_delimiters": 3, "existing_graph_fragments": 4, "symbolic_region_graph_comparisons": 40, "frozen_full_Bifid_output_length": 570, "declared_accountability_readings": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_source_transformations": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "whole-object-accountability.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "region_graph_comparisons": 40, "complete_source_bound_graphs": 0, "full_output_consumer": False, "new_source_transformations": 0}, indent=2))


if __name__ == "__main__":
    main()
