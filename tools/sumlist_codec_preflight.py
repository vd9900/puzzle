#!/usr/bin/env python3
import json
from collections import Counter

from tools.analyze_salphaseion import split_segments
from tools.gsmg import ARTIFACTS, SOURCES, decode_decimal_letters, extract_salphaseion, textareas
from tools.plan_literal_sumlist import derive_candidates as axis_candidates
from tools.plan_spiral_ring_sums import derive_candidates as ring_candidates
from tools.prime_markers import is_prime, tokenizations
from tools.research_common import fingerprint, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle09"
TO_DIGITS = str.maketrans("abcdefghio", "1234567890")
TO_LETTERS = str.maketrans("1234567890", "abcdefghio")


def encode_neighbor_codec(payload):
    if not payload:
        raise ValueError("The neighboring integer codec requires a nonempty payload")
    return str(int.from_bytes(payload, "big")).translate(TO_LETTERS)


def numeric_representations(values):
    digits = "".join(map(str, values))
    number = int(digits)
    return {
        "one-byte-totals": bytes(values), "decimal-concatenation": digits.encode(),
        "decimal-comma-list": ",".join(map(str, values)).encode(),
        "decimal-minimal-integer-big-endian": number.to_bytes((number.bit_length() + 7) // 8, "big"),
    }


def report():
    document = (SOURCES / "salphaseion.html").read_text()
    compact = "".join(textareas(document)[0].split())
    before_blob = compact.split("U2FsdGVkX1", 1)[0]
    parts = before_blob.split("z")
    extracted = extract_salphaseion(document)
    controls = []
    for encoded, expected in zip(parts[1:3], extracted["decimal_clues"]):
        if decode_decimal_letters(encoded) != expected or encode_neighbor_codec(expected.encode()) != encoded:
            raise ValueError("The exact neighboring decimal codec does not round-trip")
        controls.append({"decoded_public_label": expected, "source_length": len(encoded), "round_trip_exact": True})
    roots = {}
    for mask, tokens in tokenizations(split_segments()["dbbi"]):
        if mask in (505, 1017):
            residual = "".join(entry["token"] for entry in tokens if not is_prime(entry["position_one_based"]))
            for reverse in (False, True):
                text = residual[::-1] if reverse else residual
                roots[f"mask{mask}-reverse{reverse}"] = {"mask": mask, "reverse": reverse, "text": text}
    axis_lists, unused_forms, unused_passwords = axis_candidates()
    ring_forms, unused_passwords = ring_candidates()
    lists = {("axis", values): provenance for values, provenance in axis_lists.items()}
    for form in ring_forms:
        lists[("ring", tuple(form["parameters"]["ring_totals"]))] = form["parameters"]["image_provenance"]
    results = []
    root_summaries = []
    for name, root in roots.items():
        digits = root["text"].translate(TO_DIGITS)
        number = int(digits)
        decoded = number.to_bytes((number.bit_length() + 7) // 8, "big")
        root_summaries.append({"name": name, "mask": root["mask"], "reverse": root["reverse"], "letters": len(root["text"]), "decoded_bytes": len(decoded), "source_fingerprint": fingerprint(root["text"].encode()), "decoded_fingerprint": fingerprint(b"gsmg-preflight-decimal\x00" + decoded), "has_zero_digit": "0" in digits})
        for (geometry, values), provenance in lists.items():
            canonical_decimal = "".join(map(str, values))
            results.append({"root": name, "geometry": geometry, "totals": list(values), "provenance": provenance, "interpretation": "direct-decimal-total-concatenation", "match": digits == canonical_decimal, "length_compatible": len(digits) == len(canonical_decimal)})
            for representation, payload in numeric_representations(values).items():
                results.append({"root": name, "geometry": geometry, "totals": list(values), "provenance": provenance, "interpretation": "neighboring-whole-decimal-big-endian-codec:" + representation, "match": decoded == payload, "length_compatible": len(decoded) == len(payload), "canonical_encoding_contains_zero_digit": "o" in encode_neighbor_codec(payload)})
    matches = sum(result["match"] for result in results)
    report = {
        "id": "C09-SUMLIST-CODEC-PREFLIGHT", "status": "REJECTED" if matches == 0 else "PROMISING",
        "source_evidence": [source_record(SOURCES / "salphaseion.html"), source_record(ARTIFACTS / "cycle03/prime-boundary.json"), source_record(ARTIFACTS / "cycle04/next-literal-sumlist-plan.json"), source_record(OUTPUT / "spiral-ring-sums-frozen-plan.json")],
        "hypothesis": "The prime residual is literally an already-defined image-axis/ring sum list, using direct decimal totals or the same whole-decimal-to-big-endian codec as neighboring labels",
        "invariant": "Exact source labels independently round-trip under a1..i9/o0; every comparison uses complete residual bytes and canonical existing sum-list serializations; no zero repair, alphabet remapping, weight fitting or downstream hash search",
        "positive_controls": controls, "roots": root_summaries,
        "search_space": {"residual_branches": 2, "directions": 2, "axis_lists": len(axis_lists), "ring_lists": len(lists) - len(axis_lists), "interpretations_per_list": 5, "exact_comparisons": len(results)},
        "results": results, "matches": matches,
        "length_compatible_comparisons": sum(result["length_compatible"] for result in results),
        "comparisons_by_geometry": dict(Counter(result["geometry"] for result in results)),
        "new_passwords": 0, "new_aes_trials": 0,
        "result": "Rejects only literal identity with the fixed image-axis/ring totals under the neighboring codec/direct decimal convention; it does not reject a masked/weighted matrix or an intermediate operator role",
        "next_unexplored_edge": "Actual-anomaly-hole annotated matrix intersected with the original image bit-mask before axis sums: a typed digit placement -> image zeroing -> sumlist construction, not yet a password experiment",
        "limits": "No AES or private-key checks. Existing raw decoded residual was previously tested; this comparison adds a semantic inverse constraint, not another replay. Arbitrary symbol subsets/weights, other codecs or matrix masks remain outside this precise negative",
    }
    write_once_json(OUTPUT / "sumlist-codec-preflight.json", report)
    print(json.dumps({name: value for name, value in report.items() if name not in ("source_evidence", "results", "roots")}, indent=2))
    return report


if __name__ == "__main__":
    report()
