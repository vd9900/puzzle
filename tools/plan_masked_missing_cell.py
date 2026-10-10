#!/usr/bin/env python3
import json

from tools.baseline_coverage import baseline_passwords
from tools.candidate_identity import POLICY, previously_tested, tagged_identity
from tools.gsmg import ARTIFACTS, SOURCES, extract_grid
from tools.plan_missing_cell import missing_cell_matrices
from tools.research_common import fingerprint, source_record, write_once_json
from tools.sumlist_codec_preflight import numeric_representations


OUTPUT = ARTIFACTS / "cycle09"


def masked_matrices():
    image = extract_grid(SOURCES / "gsmg-puzzle.png")
    matches = [(parameters, matrix) for parameters, matrix in missing_cell_matrices() if parameters["value_mapping"] == "dbbi-a1-i9-binary-a0-b1" and parameters["fill_route"] == "verified-counterclockwise-spiral"]
    if len(matches) != 1:
        raise ValueError("Expected one previously defined typed-digit/verified-spiral annotated matrix")
    parameters, annotated = matches[0]
    matrices = []
    for keep_bit in (0, 1):
        masked = [[value if image["matrix"][row][column] == keep_bit else 0 for column, value in enumerate(values)] for row, values in enumerate(annotated)]
        matrices.append(masked)
        yield parameters | {"keep_original_image_bit": keep_bit, "mask_policy": "Use only original black/blue1 and white/yellow/nearwhite0 mapping; the actual hole is zero under either mask", "masked_matrix_fingerprint": fingerprint(bytes(value for row in masked for value in row)), "original_annotated_matrix_fingerprint": fingerprint(bytes(value for row in annotated for value in row)), "complement_reconstruction_verified": True}, masked
    if any(matrices[0][row][column] + matrices[1][row][column] != annotated[row][column] for row in range(14) for column in range(14)):
        raise ValueError("Complementary masks do not reconstruct every annotated source value")


def derive_candidates():
    lists = {}
    for parameters, matrix in masked_matrices():
        rows = list(map(sum, matrix))
        columns = list(map(sum, zip(*matrix)))
        for axis, totals in (("rows", rows), ("columns", columns), ("rows-then-columns", rows + columns), ("columns-then-rows", columns + rows)):
            for reverse in (False, True):
                values = totals[::-1] if reverse else totals
                lists.setdefault(tuple(values), []).append(parameters | {"axis_order": axis, "reverse_totals": reverse})
    forms = []
    candidates = {}
    for values, provenance in lists.items():
        for representation, payload in numeric_representations(values).items():
            parameters = {"source_provenance": provenance, "representation": representation, "totals_fingerprint": fingerprint(b"gsmg-masked-totals\x00" + bytes(values)), "total_count": len(values)}
            forms.append({"parameters": parameters, "material_fingerprint": fingerprint(b"gsmg-masked-material\x00" + payload), "material_length": len(payload)})
            for transform, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
                candidate = candidates.setdefault(tagged_identity(password), {"password_hex": password.hex(), "provenance": []})
                candidate["provenance"].append(parameters | {"password_transform": transform})
    return forms, candidates


def plan():
    forms, candidates = derive_candidates()
    previous_path = OUTPUT / "cumulative-aes-audit.json"
    previous = json.loads(previous_path.read_text())
    historical = {fingerprint(password) for password in baseline_passwords()}
    for ledger in previous["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("A completed historical ledger changed")
        with path.open() as source:
            historical.update(json.loads(line)[ledger.get("candidate_identifier_field", "password_sha256")] for line in source)
    fresh = {identifier for identifier, candidate in candidates.items() if not previously_tested(bytes.fromhex(candidate["password_hex"]), historical)}
    report = {
        "id": "C09-NEXT-MASKED-MISSING-CELL", "status": "UNTESTED",
        "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png"), source_record(SOURCES / "salphaseion.html"), source_record(SOURCES.parent / "evidence/cycle02/_work__creator_jrk.txt", "line627, December26 2021 characters need to be zeroed out, unauthenticated speaker label"), source_record(ARTIFACTS / "cycle05/next-missing-cell-plan.json", "Existing195 typed source values/actual-hole/verified-spiral placement"), source_record(SOURCES.parent / "evidence/cycle05/fork-solver__prime_host_delta.cjs", "Secondary endpoint-zero placement uses image selectors, not the exact actual-hole placement; inspected, never executed"), source_record(OUTPUT / "sumlist-codec-preflight.json"), source_record(previous_path)],
        "hypothesis": "Image0/1 cells zero complementary portions of the existing actual-hole annotated matrix before the matrixsumlist operation",
        "invariant": "195 source values occupy every non-hole cell once under the existing typed mapping and verified spiral; the actual anomaly remains zero; complementary image masks reconstruct all annotated values exactly before axis aggregation",
        "justification": "Uses the exact195=196-1 length, observed anomaly, independently verified bit-mask/spiral, characters-zeroed wording and matrixsumlist together. The completed unmasked-hole sum experiment did not apply the image as a positional mask. Only one typed mapping and verified route are retained; no alternate fill/image/color weights introduced. This remains an unverified creator-intent hypothesis, not a plaintext prediction",
        "search_space": {"annotated_matrices": 1, "typed_value_mappings": 1, "placement_routes": 1, "complementary_image_masks": 2, "axis_orders": 4, "directions": 2, "distinct_sum_lists": len({form["parameters"]["totals_fingerprint"] for form in forms}), "representations": 4, "forms": len(forms), "password_transforms": 3, "unique_passwords": len(candidates), "previously_tested_passwords_skipped": len(candidates) - len(fresh), "new_unique_passwords": len(fresh), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(fresh) * 6},
        "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))),
        "candidate_identifier_policy": POLICY,
        "candidate_fingerprints": sorted(candidates), "new_candidate_fingerprints": sorted(fresh), "forms": forms,
        "new_aes_trials_executed": 0,
        "limits": "Plan only. No endpoint-zero placement, arbitrary holes, extra rows/column fills, symbol subsets, color RGB weights, ring/diagonal sums, keyword composition, alphabet permutations or huge dictionaries. Candidate/grid/total/key byte sequences not written; exact forms regenerate locally. Before execution revalidate all18 ledgers plus baseline identities",
    }
    write_once_json(OUTPUT / "next-masked-missing-cell-plan.json", report)
    print(json.dumps({name: value for name, value in report.items() if name not in ("source_evidence", "forms", "candidate_fingerprints", "new_candidate_fingerprints")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
