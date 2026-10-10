#!/usr/bin/env python3
import json

from tools.analyze_salphaseion import split_segments
from tools.baseline_coverage import baseline_passwords
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS, SOURCES
from tools.joint_derivation import columnar
from tools.plan_literal_sumlist import derive_candidates as literal_sumlists
from tools.research_common import fingerprint, score_plaintext, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle08"


def derive_candidates():
    segments = split_segments()
    square = key_square(segments["dbbi"])
    decoded = bifid(segments["faed"], square, 570)
    if not decoded.startswith("btcseed") or len(decoded) != 570:
        raise ValueError("Expected the exact previously reproduced Bifid header/body")
    body = decoded[7:]
    lists, unused_forms, unused_passwords = literal_sumlists()
    forms = []
    candidates = {}
    for sums, provenance in lists.items():
        for decrypt in (False, True):
            routed = columnar(body, sums, decrypt)
            if columnar(routed, sums, not decrypt) != body:
                raise ValueError("Ragged post-Bifid routing does not preserve the exact body")
            if bifid(decoded[:7] + columnar(routed, sums, not decrypt), square, 570, False) != segments["faed"]:
                raise ValueError("Header-preserving inverse route/Bifid does not reconstruct the source")
            payload = routed.encode("ascii")
            parameters = {
                "source": "exact source-keyed Bifid570 then unchanged7-character btcseed header/body split",
                "header_preserved_outside_route": True, "body_length": len(body),
                "axis_sums": list(sums), "matrix_provenance": provenance,
                "columnar_direction": "decrypt" if decrypt else "encrypt",
                "stable_column_order_zero_based": sorted(range(len(sums)), key=lambda index: (sums[index], index)),
                "password_transform": "sha256-lowerhex; same representation as independently verified earlier AES stages",
            }
            forms.append({"parameters": parameters, "output_fingerprint": fingerprint(b"gsmg-research-output\x00" + payload), "fingerprint_policy": "Domain-separated output fingerprint does not disclose the hash used as a candidate password", "output_length": len(payload), "score": score_plaintext(payload), "complete_inverse_round_trip": True})
            password = fingerprint(payload).encode("ascii")
            candidate = candidates.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
            candidate["provenance"].append(parameters)
    return forms, candidates


def plan():
    forms, candidates = derive_candidates()
    previous = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
    historical = {fingerprint(password) for password in baseline_passwords()}
    for ledger in previous["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("A completed historical ledger changed")
        with path.open() as source:
            historical.update(json.loads(line)[ledger.get("candidate_identifier_field", "password_sha256")] for line in source)
    fresh = set(candidates) - historical
    report = {
        "id": "C08-NEXT-POST-BIFID-ROUTING", "status": "UNTESTED",
        "source_evidence": [source_record(SOURCES / "salphaseion.html"), source_record(SOURCES / "gsmg-puzzle.png"), source_record(ARTIFACTS / "cycle04/bifid-evidence.json"), source_record(ARTIFACTS / "cycle07/numeric-routing-frozen-plan.json"), source_record(OUTPUT / "prime-conditioned-bifid-control.json"), source_record(OUTPUT / "instruction-order.json"), source_record(OUTPUT / "cumulative-aes-audit.json")],
        "hypothesis": "The matrix sum-list routes the explicitly tagged Bifid body after fractionation, not the faed source before it; the exact btcseed header remains outside the routed payload",
        "invariant": "Restore the unchanged header, inverse the exact stable numeric route and re-encode with the original Bifid square to reproduce faed570. The next AES must pass structural/downstream/local Boolean gates; a prefix is not the verifier",
        "justification": "The primary matrix label, reproduced Bifid header/body and SHA command provide a bounded alternative operation order. Cycle07 routed faed before Bifid, and cycle04 tested the untransposed suffix; neither implements this edge. The prime-conditioned control weakens independence of btcseed, so the prefix is treated as a tentative header and never as proof of a seed/key. No new alphabet/cipher or candidate phrase is introduced",
        "search_space": {"distinct_axis_lists": 24, "columnar_directions": 2, "forms": len(forms), "header_variants": 1, "password_transforms": ["sha256-lowerhex"], "unique_passwords": len(candidates), "previously_tested_passwords_skipped": len(candidates) - len(fresh), "new_unique_passwords": len(fresh), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(fresh) * 6},
        "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))),
        "candidate_fingerprints": sorted(candidates), "new_candidate_fingerprints": sorted(fresh), "forms": forms,
        "new_aes_trials_executed": 0,
        "limits": "Frozen plan only. No current AES replay or execution. Only the24 already documented lists, two exact route directions, one preserved header and one verified SHA-password representation. No prefix repair, output pruning, raw-password/hash-chain variants, arbitrary alphabet or tie permutations",
    }
    write_once_json(OUTPUT / "next-post-bifid-routing-plan.json", report)
    print(json.dumps({name: value for name, value in report.items() if name not in ("source_evidence", "forms", "candidate_fingerprints", "new_candidate_fingerprints")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
