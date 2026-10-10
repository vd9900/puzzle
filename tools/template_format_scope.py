import json
import re

from tools.instruction_graphs import ROOT, source, text_location, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle18"


def html_paragraphs(path):
    document = path.read_bytes().decode("utf-8")
    return document, [{
        "text": match.group(1),
        "source_location": text_location(document, match.start(1), match.end(1)),
    } for match in re.finditer(r"<p>(.*?)</p>", document, re.S | re.I)]


def earlier_templates():
    path = ROOT / "research/sources/phase2.html"
    document, paragraphs = html_paragraphs(path)
    templates = []
    for index, paragraph in enumerate(paragraphs):
        matches = list(re.finditer(r"/\(([^)]*)\)", paragraph["text"]))
        for match in matches:
            prefix = paragraph["text"][:match.start()].strip()
            if prefix:
                owner_indices = [index]
                owner_rule = "INLINE_TAG_IN_SAME_PRIMARY_PARAGRAPH"
            else:
                owner_indices = [index - 1]
                owner_rule = "STANDALONE_TAG_AFTER_PRECEDING_PRIMARY_PARAGRAPH"
            start = paragraph["source_location"]["character_span_zero_based_half_open"][0] + match.start()
            templates.append({
                "literal_tag": match.group(), "tag_body": match.group(1),
                "tag_source_location": text_location(document, start, start + len(match.group())),
                "paragraph_index_zero_based": index,
                "candidate_owner_paragraph_indices": owner_indices,
                "owner_rule_supported_by_format": owner_rule,
                "candidate_owner_locations": [paragraphs[owner]["source_location"] for owner in owner_indices],
                "position_supports_scope_not_exact_creator_authentication": True,
            })
    if [entry["literal_tag"] for entry in templates] != ["/(aaa, connected enf)", "/(aBa, connected enf)", "/(aBa, connected not enf)"]:
        raise ValueError("Unexpected exact earlier primary format tags")
    aggregate = next(paragraph for paragraph in paragraphs if "--> parts 1..7 --> sha-256" in paragraph["text"])
    phase3_path = ROOT / "research/artifacts/phase3.txt"
    phase3 = phase3_path.read_bytes().decode("utf-8")
    phase3_riddles = phase3.split("\r\n\r\n")[:3]
    local_tags = []
    cursor = 0
    for index, paragraph in enumerate(phase3_riddles):
        match = re.search(r"/\(aa,connected enf\)$", paragraph)
        if not match:
            raise ValueError("Missing fixed local Phase3 format tag")
        local_tags.append({
            "paragraph_index_zero_based": index, "literal_tag": match.group(),
            "tag_source_location": text_location(phase3, cursor + match.start(), cursor + match.end()),
            "same_paragraph_prefix_length": match.start(),
            "not_a_global_character_count_instruction": True,
        })
        cursor += len(paragraph) + 4
    return {
        "primary_page_source": source(path), "primary_paragraph_count": len(paragraphs),
        "format_templates": templates,
        "aggregate_order_and_consumer": aggregate,
        "aggregate_order_names_local_parts_and_next_phase": True,
        "phase3_source": source(phase3_path), "phase3_local_tags": local_tags,
        "same_tag_family_has_scope_variation_and_different_casing_patterns": True,
        "not_enf_and_enf_are_distinct_authored_spellings": True,
        "scope_rule_does_not_define_an_unmentioned_current_object": True,
    }


def current_fragments():
    layout = json.loads((ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json").read_text())["primary_layout"]
    boundary = json.loads((ROOT / "research/artifacts/cycle15/label-boundary-audit.json").read_text())
    path = ROOT / "research/sources/salphaseion.html"
    document = path.read_bytes().decode("utf-8")
    textareas = list(re.finditer(r"<textarea\b[^>]*>(.*?)</textarea>", document, re.S | re.I))
    if len(textareas) != 2:
        raise ValueError("Unexpected current primary textareas")
    first = textareas[0]
    raw = first.group(1)
    compact = "".join(raw.split())
    if len(compact) != layout["normalized_length"] or len(compact) != 1075:
        raise ValueError("Current primary normalization differs from saved layout")
    regions = [entry for entry in boundary["regions"] if entry["name"] in ("matrixsumlist", "lastwordsbeforearchichoice", "thispassword", "first-command", "answer-command")]
    for entry in regions:
        start, end = entry["character_span_zero_based_half_open"]
        if not first.start(1) <= start < end <= first.end(1):
            raise ValueError("Current fragment not inside the same original textarea")
    return {
        "source": source(path), "first_textarea_source_location": text_location(document, first.start(1), first.end(1)),
        "five_relevant_fragments_share_one_primary_textarea": True,
        "source_owned_fragment_maps": regions,
        "literal_format_tag_occurrences_in_encoded_source": len(re.findall(r"/\([^)]*connected[^)]*\)", raw)),
        "literal_part_range_arrows_in_encoded_source": "parts 1..7" in raw,
        "whitespace_removal_is_encoded_container_normalization_not_a_hash_input_rule": True,
        "decoded_labels_not_replaced_into_any_trial_input": True,
        "earlier_para_scope_rules_not_transferred_to_current_textarea": True,
        "current_local_operator_subphrases": layout["command_subphrases"],
        "known_operator_does_not_supply_input_case_spacing_or_encoding": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle18/notation-namespace.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C18-NOTATION-NAMESPACE" or "instruction-template comparison" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding frozen task")
    evidence = [source(path) for path in (
        ROOT / "research/sources/phase2.html", ROOT / "research/artifacts/phase3.txt",
        ROOT / "research/sources/salphaseion.html", ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json",
        ROOT / "research/artifacts/cycle15/label-boundary-audit.json", preceding,
    )]
    locations = ["research/sources/phase2.html:18", "research/sources/phase2.html:38", "research/sources/phase2.html:41", "research/sources/phase2.html:42", "research/artifacts/phase3.txt:1", "research/artifacts/phase3.txt:3", "research/artifacts/phase3.txt:5", "research/sources/salphaseion.html:17"]
    hypotheses = []
    for suffix, hypothesis, confidence, assumptions, contradictions in [
        ("FORMAT-LOCAL-SCOPE", "Earlier casing/connection tags are local riddle-format controls rather than a universal normalization recipe", "HIGH exact local placement/variation; MEDIUM intended scope", ["Tag placement next to a paragraph supports local ownership", "An explicit not-enf tag is a deliberate local distinction"], ["Exact semantics are partly explained only by secondary sources", "Standalone tag may cover more than one prior fragment", "Local ownership does not bind the current hash argument"]),
        ("FORMAT-CURRENT-UNKNOWN", "Current character-spacing removal decodes source labels but does not establish final input casing, whitespace or representation", "HIGH source-versus-input distinction; UNKNOWN final format", ["Encoded-string normalization and semantic-object formatting are different stages", "A final argument needs its own source-owned representation rule"], ["Creator may expect implicit reuse of known conventions", "Absence of an explicit tag does not forbid a convention", "No independent selected-word object is available to format"]),
    ]:
        hypotheses.append({
            "id": "C18-" + suffix, "status": "INCONCLUSIVE", "hypothesis": hypothesis,
            "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions,
            "operation_order": ["map original format tag attachment", "separate local part-domain consumer from later fragments", "retain encoding-normalization versus final-argument distinction"],
            "input": "Public primary paragraph/text-area structures and preserved source maps",
            "output": "A local formatting-scope constraint, not normalized trial strings",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Audit exact spatial referents in the preserved in-front-of-your-eyes and very-last-step hint clauses against original-page image/text layout; do not select letter positions or derive trial text",
        })
    return {
        "id": "C18-TEMPLATE-FORMAT-SCOPE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Earlier authored instruction templates bind final argument formatting for the current label/hash sequence",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Compare only fixed original templates, not normalization variants", "Source spelling, local decoder normalization and semantic-object representation are separate roles", "Paragraph proximity supports local scope but is not author authentication"],
        "operation_order": ["validate frozen template task", "map three Phase2 format tags and aggregate consumer", "map three Phase3 local tag attachments", "map five current fragments inside one textarea", "compare two finite format-scope hypotheses"],
        "input": "Original public HTML/plaintext structure and current frozen label mappings",
        "output": "Exact primary tag-attachment and missing final-format bridge audit",
        "confidence": "HIGH original markup/tag locations; UNKNOWN current final-argument format",
        "earlier_templates": earlier_templates(), "current_fragments": current_fragments(), "hypotheses": hypotheses,
        "result": "Earlier templates attach casing/connection tags locally and explicitly distinguish connected enf from connected not enf. Phase2 states a local parts1..7 aggregate and named next-phase consumer; Phase3 attaches the same lower-case-pattern tag to three separate riddles. Current five labels/operator fragments share one encoded textarea, with no matching authored format tag or part-domain arrow. Removing encoded character spaces does not identify semantic input casing, word boundaries, serialization or consumer. No normalized trial text produced.",
        "contradictions": ["Transferring an earlier local tag silently creates an unbound current input rule", "Source decoding normalization is not final argument serialization", "Operator identity alone does not establish an argument object or format"],
        "next_test": "Perform one fixed spatial-reference audit of the preserved in-front-of-your-eyes and very-last-step clauses: exact primary image/page visible text, inline label positions and creator-attributed hint source. Separate instruction telling the solver where to look from a selection/count rule; no pixel edits, traversals or extracted trial strings.",
        "search_space": {"earlier_format_tags": 3, "earlier_local_riddle_tags": 3, "explicit_aggregate_template": 1, "current_fragments": 5, "finite_format_scope_hypotheses": 2, "new_normalization_trials": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "template-format-scope.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "explicit_current_input_format_bound": False, "new_normalization_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
