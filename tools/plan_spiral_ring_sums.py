#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS, SOURCES, spiral_coordinates
from tools.image_sum_derivation import image_matrices
from tools.research_common import fingerprint, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle09"


def ring_totals(matrix):
    size = len(matrix)
    if not size or any(len(row) != size for row in matrix):
        raise ValueError("Spiral rings require a nonempty square matrix")
    totals = [0] * ((size + 1) // 2)
    members = [[] for ring in totals]
    for offset, (row, column) in enumerate(spiral_coordinates(size)):
        ring = min(row, column, size - 1 - row, size - 1 - column)
        totals[ring] += matrix[row][column]
        members[ring].append(offset)
    if sum(map(len, members)) != size * size or sum(totals) != sum(map(sum, matrix)):
        raise ValueError("Spiral rings do not partition the exact matrix")
    if [offset for ring in members for offset in ring] != list(range(size * size)):
        raise ValueError("Verified spiral does not visit complete rings contiguously")
    return totals, members


def derive_candidates():
    lists = {}
    for name, matrix in image_matrices():
        totals, members = ring_totals(matrix)
        if len(totals) != 7 or totals[-1] != 0:
            raise ValueError("Expected seven image rings with the observed all-zero central ring")
        for reverse in (False, True):
            values = totals[::-1] if reverse else totals
            lists.setdefault(tuple(values), []).append({"matrix": name, "shape": [len(matrix), len(matrix)], "reverse_ring_order": reverse, "ring_cells_outer_to_inner": list(map(len, members)), "ring_spiral_spans_outer_to_inner_zero_based_half_open": [[ring[0], ring[-1] + 1] for ring in members], "central_zero_retained": True})
    forms = []
    candidates = {}
    for totals, provenance in lists.items():
        decimal = "".join(map(str, totals))
        number = int(decimal)
        materials = {
            "one-byte-totals": bytes(totals),
            "decimal-concatenation": decimal.encode(),
            "decimal-comma-list": ",".join(map(str, totals)).encode(),
            "decimal-minimal-integer-big-endian": number.to_bytes((number.bit_length() + 7) // 8, "big"),
        }
        for representation, payload in materials.items():
            parameters = {"ring_totals": list(totals), "image_provenance": provenance, "representation": representation, "integer_leading_zero_policy": "The existing minimal whole-number representation alone discards leading zeros by definition; other forms preserve the central zero", "aggregation": "sum each concentric ring visited contiguously by the independently verified counterclockwise image spiral"}
            forms.append({"parameters": parameters, "material_fingerprint": fingerprint(b"gsmg-ring-material\x00" + payload), "material_length": len(payload)})
            for transform, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
                candidate = candidates.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                candidate["provenance"].append(parameters | {"password_transform": transform})
    return forms, candidates


def plan():
    forms, candidates = derive_candidates()
    report = {
        "id": "C09-SPIRAL-RING-SUMS", "status": "UNTESTED",
        "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png", "Verified spiral partitions the image into seven contiguous concentric rings"), source_record(SOURCES / "salphaseion.html", "Exact matrixsumlist label"), source_record(ARTIFACTS / "cycle04/next-literal-sumlist-plan.json", "Historical24 axis lists; this plan changes only aggregation geometry"), source_record(OUTPUT / "post-bifid-routing-results.json", "Failed post-Bifid operator path")],
        "hypothesis": "matrixsumlist names per-spiral-ring image totals instead of row/column-axis totals",
        "invariant": "All image cells occur exactly once in the verified contiguous spiral rings; sum(ring totals) equals image total; central zero retained; same three documented image variants and four existing numeric serializations only",
        "justification": "The first verified image solution uses a counterclockwise spiral, so its concentric rings are a natural source-defined matrix partition overlooked by row/column-only sums. Seven rings exist in both14x14 and the already-defined13x13 variant, but this count does not independently confirm the copied seven-password movie wording. No new image variant, phrase, cipher, value mapping or alphabet is added; this is a weaker geometry hypothesis requiring the same hard downstream gate",
        "search_space": {"image_variants": 3, "ring_orders": 2, "distinct_ring_sum_lists": len({tuple(form["parameters"]["ring_totals"]) for form in forms}), "representations": 4, "forms": len(forms), "password_transforms": 3, "unique_passwords": len(candidates), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(candidates) * 6},
        "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))),
        "candidate_fingerprints": sorted(candidates), "forms": forms,
        "limits": "Frozen geometry comparison only; no AES at plan creation. No dropping the zero center, arbitrary diagonal/shell cuts, weighted colors, reversal inside rings, word composition, a1z26 repair for sums above26, free permutations or password dictionaries. No key/password byte sequences written",
    }
    write_once_json(OUTPUT / "spiral-ring-sums-frozen-plan.json", report)
    print(json.dumps({name: value for name, value in report.items() if name not in ("source_evidence", "forms", "candidate_fingerprints")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
