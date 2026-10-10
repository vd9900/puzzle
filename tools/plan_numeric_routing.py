#!/usr/bin/env python3
import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS, SOURCES
from tools.image_sum_derivation import residual
from tools.joint_derivation import columnar
from tools.plan_literal_sumlist import derive_candidates as literal_sumlists
from tools.research_common import fingerprint, score_plaintext, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle07"


def derive_candidates():
    lists, unused_forms, unused_passwords = literal_sumlists()
    segments = split_segments()
    square = key_square(segments["dbbi"])
    roots = {"frame-selected-residual60": residual(), "untouched-faed570": segments["faed"]}
    forms = []
    passwords = {}
    for sums, provenance in lists.items():
        for name, text in roots.items():
            for decrypt in (False, True):
                routed = columnar(text, sums, decrypt)
                if columnar(routed, sums, not decrypt) != text:
                    raise ValueError("Stable numeric columnar route does not preserve its exact source")
                outputs = {"routed-only": routed}
                if name == "untouched-faed570":
                    decoded = bifid(routed, square, 570)
                    if bifid(decoded, square, 570, False) != routed:
                        raise ValueError("Post-route source-keyed Bifid does not round-trip")
                    outputs["source-bifid-after-route"] = decoded
                for operation, output in outputs.items():
                    payload = output.encode("ascii")
                    parameters = {"segment": name, "source_fingerprint": fingerprint(text.encode()), "axis_sums": list(sums), "matrix_provenance": provenance, "columnar_direction": "decrypt" if decrypt else "encrypt", "stable_column_order_zero_based": sorted(range(len(sums)), key=lambda index: (sums[index], index)), "tie_policy": "Equal numeric sums retain original column index", "post_route_operation": operation, "bifid_square": square if operation == "source-bifid-after-route" else None, "bifid_period": 570 if operation == "source-bifid-after-route" else None}
                    forms.append({"parameters": parameters, "output_fingerprint": fingerprint(payload), "output_length": len(payload), "score": score_plaintext(payload), "round_trip": True})
                    for transform, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
                        candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                        candidate["provenance"].append(parameters | {"password_transform": transform})
    return forms, passwords


def plan():
    forms, passwords = derive_candidates()
    report = {"id": "C07-NUMERIC-ROUTING", "status": "UNTESTED", "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png", "Original image-axis sums, unchanged24-list definitions"), source_record(SOURCES / "salphaseion.html", "matrixsumlist/dbbi/faed boundaries"), source_record(ARTIFACTS / "cycle03/prime-boundary.json", "Explicit frame-selected60-letter residual"), source_record(ARTIFACTS / "cycle04/bifid-evidence.json", "Single exact source-keyed Bifid square and period570")], "hypothesis": "matrixsumlist specifies stable numeric column ordering, not password bytes; route the prime residual or faed, optionally before the source-keyed Bifid layer", "invariant": "Each transposition and exact Bifid output must re-encode to its input; no source symbols, tail bytes or tie permutations are invented", "justification": "The literal sum lists failed as passphrases but can specify a column ordering. Matrixsumlist neighbors dbbi and source-derived Bifid uses dbbi as a keyword, so testing ordered faed before fractionation links multiple observed artifacts. This is a weaker unproven operator hypothesis, not evidence that the creator intended transposition.", "overlap_limits": "Earlier local columnar roots used literal word keys, not these exact numeric lists. Captured secondary summaries broadly mention sum-based ordering but their precise campaigns are not locally reproduced; no claim of global novelty. All locally tested password fingerprints must be excluded before AES.", "search_space": {"distinct_axis_lists": 24, "source_segments": 2, "columnar_directions": 2, "post_route_operations": "routed-only for both segments; source-keyed Bifid for faed only", "forms": len(forms), "password_transforms": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "candidate_fingerprints": sorted(passwords), "forms": forms, "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 4), "gate": "Exact locally verified Boolean target or independently justified next-stage structure. Printable output/btcseed prefix cannot select a route.", "limits": "No AES executed in plan. No free tie rules, route inversion/reversal sweep, new alphabets, extra periods, phrase dictionaries or additional hash functions. Password bytes are generated in memory only and not written."}
    write_once_json(OUTPUT / "numeric-routing-frozen-plan.json", report)
    print(json.dumps({name: value for name, value in report.items() if name not in ("forms", "candidate_fingerprints")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
