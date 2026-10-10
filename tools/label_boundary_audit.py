import json

from tools.gsmg import decode_binary_letters
from tools.instruction_graphs import PRIMARY, ROOT, primary_layout, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle15"


def binary_label_source_map(compact, span):
    encoded = compact[91:195]
    decoded = decode_binary_letters(encoded)
    if decoded != "matrixsumlist":
        raise ValueError("Existing primary binary label differs")
    mapped = []
    for index, character in enumerate(decoded):
        start = 91 + index * 8
        bits = compact[start:start + 8].translate(str.maketrans("ab", "01"))
        if chr(int(bits, 2)) != character:
            raise ValueError("Exact source octet does not reproduce label character")
        mapped.append({"decoded_index_zero_based": index, "decoded_character": character, "original_binary_octet": bits, **span(start, start + 8)})
    return {"encoded_length": len(encoded), "decoded_length": len(decoded), "decoded_public_label": decoded, "source_octets": mapped, "exact_round_trip": "".join(entry["original_binary_octet"] for entry in mapped).translate(str.maketrans("01", "ab")) == encoded}


def report():
    preceding = OUTPUT / "frame-object-audit.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C15-FRAME-OBJECT-AUDIT" or "boundary/type semantics" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding scoped task")
    layout, compact, span = primary_layout()
    binary = binary_label_source_map(compact, span)
    regions = []
    for entry in layout["regions"]:
        if entry["name"] in ("small-container-first-part", "small-container-second-part"):
            grammar_type = "ENCODED_CONTAINER_DATA"
        elif entry["name"] in ("dbbi91", "faed570"):
            grammar_type = "UNRESOLVED_SOURCE_DATA"
        elif entry["name"] in ("matrixsumlist", "enter"):
            grammar_type = "BINARY_ENCODED_TEXT_LABEL"
        elif entry["name"] in ("lastwordsbeforearchichoice", "thispassword"):
            grammar_type = "DECIMAL_INTEGER_ENCODED_TEXT_LABEL"
        else:
            grammar_type = "MIXED_LITERAL_SHA_WORDING"
        regions.append(entry | {"grammar_type": grammar_type, "type_does_not_identify_input_output_or_consumer": True})
    borrowed = []
    for branch in frozen["branches"]:
        for marker in branch["markers"]:
            if marker["region"] != "matrixsumlist-binary":
                continue
            character_index = marker["encoded_label_character_index_zero_based"]
            borrowed.append({
                "mask": branch["mask"], "logical_position_one_based": marker["logical_position_one_based"],
                "original_marker_source": {key: value for key, value in marker.items() if "span" in key or key in ("token", "semantic_label_bit", "binary_offset_zero_based", "encoded_label_bit_offset_zero_based")},
                "decoded_label_character": binary["source_octets"][character_index]["decoded_character"],
                "decoded_label_character_index_zero_based": character_index,
                "role": "SAME_ENCODED_SOURCE_BYTE_USED_AS_LABEL_ENCODING_AND_HYPOTHESIZED_MARKER_DATA",
                "not_an_instruction_to_remove_label_bits": True,
            })
    delimiters = layout["three_delimiters"]
    pieces = [(entry["name"], entry["normalized_span_zero_based_half_open"]) for entry in regions]
    pieces.extend(("z-delimiter", entry["normalized_span_zero_based_half_open"]) for entry in delimiters)
    pieces.sort(key=lambda entry: entry[1][0])
    restored = "".join(compact[start:end] for unused_name, (start, end) in pieces)
    if restored != compact or any(first[1][1] != second[1][0] for first, second in zip(pieces, pieces[1:])):
        raise ValueError("Typed source regions do not cover the exact primary compact stream")
    evidence = [source(PRIMARY), source(preceding), source(ROOT / "research/artifacts/cycle11/hint-instruction-order.json"), source(ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json")]
    locations = ["research/sources/salphaseion.html:17", "research/artifacts/cycle15/frame-object-audit.json:1", "research/artifacts/cycle11/hint-instruction-order.json:1"]
    hypotheses = []
    for suffix, claim, order, confidence, contradictions in [
        ("BOUNDARY-OBJECT", "matrixsumlist is an object/type label whose encoded bytes can simultaneously support prime-marker data", ["read encoded primary label", "retain original encoded bytes", "identify an explicitly bound object", "apply an independently specified consumer"], "MEDIUM compatibility; exact object UNKNOWN", ["No primary delimiter marks the label as postfix or prefix", "Borrowed-bit convention is historical hypothesis", "No source statement equates the label to dbbi, faed or modified speech"]),
        ("BOUNDARY-COMMAND", "matrixsumlist names an operation but its operand and accepted representation are elsewhere in the construction", ["decode the command label", "locate an explicit operand/representation", "derive that object only under a source rule", "bind downstream Architect-related consumer"], "MEDIUM compatibility; operation details UNKNOWN", ["No verb, axis, weights or representation supplied", "All previously tested literal sums/routes remain negative", "Encoding a command does not imply its source bits cease to be data"]),
    ]:
        hypotheses.append({"id": "C15-" + suffix, "status": "INCONCLUSIVE", "hypothesis": claim, "source_evidence": evidence, "source_locations": locations, "assumptions": ["Physical source boundaries are not executable dependency arrows", "One encoded artifact can have separate text and data roles"], "operation_order": order, "input": "Unchanged encoded label and unresolved adjacent source objects", "output": "An unresolved object/command binding, not generated trial text", "confidence": confidence, "contradictions": contradictions, "next_test": "Inspect exact source-defined sum/remainder wording in the modified speech and its preserved baseline, looking for a named referent that explains both matrixsumlist and prime-residual structure without arithmetic fitting"})
    return {
        "id": "C15-LABEL-BOUNDARY-AUDIT", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Exact primary boundaries distinguish encoded label/data coexistence from an assumed single execution grammar",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Use existing primary normalization/decoders only", "No extra delimiter or consumer may be invented", "Semantic label and encoded representation are distinct typed objects"],
        "operation_order": ["map ten existing primary regions plus three delimiters", "map13 original matrixsumlist octets", "locate four already documented borrowed marker positions", "record type coexistence without removing or transforming data", "retain object-versus-command hypotheses"],
        "input": "Exact primary encoded string and two existing borrowed-marker maps",
        "output": "Typed region coverage, per-character label source maps and dual-use marker witnesses",
        "confidence": "HIGH for boundaries/source identity; UNKNOWN for complete object/operation binding",
        "regions": regions, "primary_compact_length": len(compact), "typed_regions_reconstruct_primary_exactly": True,
        "z_delimiters": delimiters, "encoded_container_internal_z_is_not_delimiter": layout["container_internal_z"],
        "binary_label": binary, "borrowed_marker_witnesses": borrowed,
        "dbbi_to_binary_and_binary_to_faed_have_no_explicit_separator": True,
        "primary_sequence_has_no_operator_argument_syntax": True,
        "known_operator_mapping_is_local_not_uniform": layout["sha_operator_mapping"],
        "hypotheses": hypotheses,
        "result": "The13 decoded matrixsumlist letters and historical marker89/97 consume the same untouched104 encoded characters in distinct roles. Primary adjacency without z at either binary boundary does not identify postfix/prefix operand or execution order. Local binary/decimal/SHA mappings cannot be promoted to one uniform stream grammar or a new consuming transformation.",
        "contradictions": ["No explicit delimiter assigns matrixsumlist to the preceding or following object", "No verb or argument syntax binds a consumer", "Dual encoded-label/data role is not a new cryptographic construction", "No evidence says discard borrowed bits or replace encoded data with decoded label in another stage"],
        "next_test": "Audit the exact sum/remainder opening of the modified speech against preserved baseline wording. Determine whether it supplies a referent/object definition for matrixsumlist that explains the prime residual without new numerical fits, cipher trials or selector variants.",
        "search_space": {"primary_regions": 10, "delimiters": 3, "label_source_octets": 13, "existing_borrowed_markers": 4, "finite_type_hypotheses": 2},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "label-boundary-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "primary_regions": 10, "label_source_octets": 13, "borrowed_marker_witnesses": len(document["borrowed_marker_witnesses"]), "operator_argument_binding_verified": False, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
