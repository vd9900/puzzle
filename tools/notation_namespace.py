import json
import re

from tools.instruction_graphs import ROOT, source, text_location, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle18"
FIXED_ANCHORS = [
    ("research/sources/phase2.html", "It'll grant the first part.", "LOCAL_ANSWER_PART"),
    ("research/sources/phase2.html", "--> parts 1..7 --> sha-256 -> dgst is the password to enter Phase 3.", "EXPLICIT_LOCAL_ORDER_AND_CONSUMER"),
    ("research/artifacts/phase2.txt", "2name", "LOCAL_NUMBERED_RIDDLE"),
    ("research/artifacts/phase2.txt", "3Moon", "LOCAL_NUMBERED_RIDDLE"),
    ("research/artifacts/phase2.txt", "4How", "LOCAL_NUMBERED_RIDDLE"),
    ("research/artifacts/phase2.txt", "# X 2 S H 4 Y 0 Q B 15 #", "DISTINCT_SYMBOL_NUMERAL_SEQUENCE"),
    ("research/artifacts/phase2.txt", "{eps3.4_[in one of the valleys of Phillip]runtime-error.r00., where daughters hit magic keypads}", "BRACED_MEDIA_REFERENCE"),
    ("research/artifacts/phase3.txt", "1name", "LOCAL_NUMBERED_RIDDLE"),
    ("research/artifacts/phase3.txt", "3.The", "LOCAL_NUMBERED_RIDDLE"),
    ("research/artifacts/phase3.txt", "I just passed a cheshire cat", "UNNUMBERED_INTERVENING_RIDDLE"),
]
FORMAT_ANCHORS = [
    ("research/sources/phase2.html", "/(aaa, connected enf)"),
    ("research/sources/phase2.html", "/(aBa, connected enf)"),
    ("research/sources/phase2.html", "/(aBa, connected not enf)"),
    ("research/artifacts/phase3.txt", "/(aa,connected enf)"),
]


def mapped_anchor(relative, literal, role):
    path = ROOT / relative
    document = path.read_bytes().decode("utf-8")
    matches = list(re.finditer(re.escape(literal), document))
    if len(matches) != 1:
        raise ValueError("Expected one exact fixed notation anchor")
    match = matches[0]
    return {"source": source(path), "literal": literal, "role": role, **text_location(document, match.start(), match.end())}


def normalization_notation():
    mapped = []
    for relative, literal in FORMAT_ANCHORS:
        path = ROOT / relative
        document = path.read_bytes().decode("utf-8")
        matches = list(re.finditer(re.escape(literal), document))
        expected = 3 if relative.endswith("phase3.txt") else 1
        if len(matches) != expected:
            raise ValueError("Fixed formatting-notation multiplicity changed")
        mapped.extend({"source": source(path), "literal": literal, **text_location(document, match.start(), match.end())} for match in matches)
    return {
        "source_maps": mapped,
        "same_tag_family_allows_different_local_formats": True,
        "aa_and_aaa_literal_lengths_do_not_define_character_selection_counts": True,
        "connected_not_enf_is_explicitly_distinct_from_connected_enf": True,
        "no_new_normalized_trial_text_generated": True,
    }


def local_namespaces():
    for fixture, archive in [
        ("research/artifacts/phase2.txt", "research/sources/maintained-phase2-assets__phase2.1.txt"),
        ("research/artifacts/phase3.txt", "research/sources/maintained-phase2-assets__phase3.txt"),
    ]:
        if (ROOT / fixture).read_bytes() != (ROOT / archive).read_bytes():
            raise ValueError("Verified public fixture differs from archived bytes")
    primary = [mapped_anchor(relative, literal, role) for relative, literal, role in FIXED_ANCHORS]
    walk_path = ROOT / "research/sources/community-README.md"
    walk = walk_path.read_text()
    prose = [mapped_anchor(str(walk_path.relative_to(ROOT)), literal, "SECONDARY_LOCAL_PART_INTERPRETATION") for literal in [
        "Using the other hints (2name, 3Moon, 4How so mate)",
        "The password is a concatenation of 7 parts. The first part is causality.",
        "1. Jacque Fresco quote:", "2. Alice: How long is forever?", "3. Heisenberg uncertainty principle",
    ]]
    if "The password is a concatenation of 7 parts. The first part is causality." not in walk:
        raise ValueError("Unexpected secondary part-order prose")
    return {
        "primary_source_maps": primary, "secondary_interpretation_maps": prose,
        "phase2_explicit_domain": "parts1..7 local to the Phase3-entry construction",
        "phase3_reuses_ordinal1_in_a_new_riddle_context": True,
        "phase3_middle_riddle_is_not_literally_numbered2": True,
        "shared_global_object_numbering_not_authored": True,
        "braces_are_used_for_media_reference_not_only_numeric_indices": True,
        "earlier_symbol_numeral_sequence_has_distinct_syntax": True,
        "no_existing_historical_riddle_answer_recomputed": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle17/door-reference-audit.json"
    task = json.loads(preceding.read_text())
    if task["id"] != "C17-DOOR-REFERENCE" or "fixed public-text notation comparison" not in task["next_test"]:
        raise ValueError("Unexpected frozen preceding task")
    evidence = [source(path) for path in (
        ROOT / "research/sources/phase2.html", ROOT / "research/artifacts/phase2.txt",
        ROOT / "research/artifacts/phase3.txt", ROOT / "research/sources/maintained-phase2-assets__phase2.1.txt",
        ROOT / "research/sources/maintained-phase2-assets__phase3.txt", ROOT / "research/sources/community-README.md", preceding,
    )]
    locations = ["research/sources/phase2.html:18", "research/sources/phase2.html:42", "research/artifacts/phase2.txt:1", "research/artifacts/phase2.txt:2", "research/artifacts/phase3.txt:1", "research/artifacts/phase3.txt:5", "research/sources/community-README.md:123", "research/sources/community-README.md:262"]
    hypotheses = []
    for suffix, description, confidence, assumptions, contradictions in [
        ("NUMBER-LOCAL-SLOTS", "Earlier numeric prefixes denote local riddle/answer parts rather than one global object-index namespace", "HIGH local phase2 domain; MEDIUM phase3 lexical role", ["Explicit parts1..7 consumer defines the local domain", "Reused1 in Phase3 starts a separate context"], ["Implicit cross-stage references may exist without explicit namespace", "Secondary riddle numbering is not primary syntax", "Local slots do not define the door's three brace roles"]),
        ("BRACES-REFERENCE-TYPE", "Brace punctuation groups heterogeneous references and does not alone specify coordinate/index operations", "HIGH exact syntax distinction; UNKNOWN intended door role", ["Original media-reference braces are a valid notation counterexample", "Shared delimiters do not force shared semantic types"], ["The numeric door braces may still imply a distinct selector grammar", "No source-owned type conversion between media reference and numeric groups", "No grammatical rule equates braces to coordinates or dates"]),
        ("NUMBER-CROSS-STAGE", "Door1/4/21 may reuse an implicit stage/object namespace only if another source fixes the domain and components", "LOW without explicit namespace", ["Creator expects earlier numeric labels to be remembered", "A separate instruction defines how three brace components select objects"], ["Phase2 explicitly has seven local parts, not21", "Phase3 reuses1 and has a separate numbered/un-numbered riddle layout", "No arrow or shared namespace links prior ordinal slots to door braces"]),
    ]:
        hypotheses.append({
            "id": "C18-" + suffix, "status": "INCONCLUSIVE", "hypothesis": description,
            "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions,
            "operation_order": ["map fixed earlier ordinal/brace syntax", "identify explicit local domain and consumer", "compare only declared namespace interpretation", "require authored bridge before assigning door numbers"],
            "input": "Preserved public earlier riddle text and frozen door-hint source maps",
            "output": "A grammatical namespace constraint, not selected object values or new trial text",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Map the exact local arrows and normalization tags in earlier source templates, then compare what operands/consumers those templates explicitly specify versus the unresolved current instruction fragments; no normalization enumeration",
        })
    return {
        "id": "C18-NOTATION-NAMESPACE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Earlier numeric-name and brace notation supplies a shared authored namespace for the door groups1/4/21",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Compare fixed public notation only, without solving earlier riddles again", "Local source roles and secondary exegesis remain distinct", "Explicit local domains are stronger evidence than numeral coincidence"],
        "operation_order": ["validate frozen namespace task", "verify two plaintext/archive byte identities", "map ten primary and five secondary anchors", "map six formatting tag occurrences", "compare three namespace hypotheses without extraction"],
        "input": "Earlier public source/plaintext notation and preserved door text",
        "output": "Exact source maps, local namespace and heterogeneous brace counterexamples",
        "confidence": "HIGH exact local syntax/source identity; UNKNOWN complete intended construction",
        "namespaces": local_namespaces(), "normalization_notation": normalization_notation(),
        "door_reference_reused_not_retested": {"source": source(preceding), "groups": task["records"]["brace_groups"], "date_correspondence_does_not_bind_consumer": True},
        "hypotheses": hypotheses,
        "result": "Explicit Phase2 parts1..7 arrows bind a local answer-domain and named Phase3-entry consumer. Phase3 reuses ordinal1 in a different riddle context; its middle riddle is unnumbered in primary text. Earlier braces enclose a media-reference expression, not just numeric indices. These fixed examples do not define a global object numbering or bridge to door1/4/21. Formatting tag variations are local, not extraction counts. No object/route/normalization trial generated.",
        "contradictions": ["Same numbers and braces do not supply one semantic namespace", "The earlier local seven-part domain does not define21", "Secondary list numbering cannot be promoted to primary index instructions", "Current source lacks the earlier explicit arrows/domain/consumer syntax"],
        "next_test": "Perform one fixed instruction-template comparison of explicit earlier part arrows and casing/connection tags against the current matrixsumlist/lastwords/thispassword/SHA fragments. Separate preserved source spelling, local decoder normalization and final input formatting; require an authored argument/consumer bridge rather than generating variants.",
        "search_space": {"primary_fixed_anchors": 10, "secondary_exact_anchors": 5, "format_tag_occurrences": 6, "verified_archive_fixture_pairs": 2, "finite_namespace_hypotheses": 3, "new_object_index_trials": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "notation-namespace.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "primary_fixed_anchors": 10, "global_namespace_established": False, "new_object_index_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
