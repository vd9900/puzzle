#!/usr/bin/env python3
import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS, SOURCES
from tools.image_sum_derivation import residual
from tools.prime_markers import is_prime, tokenizations
from tools.research_common import fingerprint, score_plaintext, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle08"


def derive_candidates():
    segments = split_segments()
    branches = {}
    for mask, tokens in tokenizations(segments["dbbi"]):
        if mask in (505, 1017):
            branches[mask] = "".join(entry["token"] for entry in tokens if not is_prime(entry["position_one_based"]))
    selected = residual()
    if branches[1017] != selected or branches[505] != selected + "e":
        raise ValueError("Expected the unchanged60/61-symbol prime residuals")
    squares = {key_square(text) for text in branches.values()}
    if len(squares) != 1:
        raise ValueError("The prime branch ambiguity unexpectedly changes the Bifid keyword")
    square = squares.pop()
    if square == key_square(segments["dbbi"]):
        raise ValueError("The residual keyword repeats the already tested source square")
    output = bifid(segments["faed"], square, 570)
    if bifid(output, square, 570, False) != segments["faed"]:
        raise ValueError("The residual-keyed Bifid does not preserve its source")
    payload = output.encode("ascii")
    parameters = {
        "transformation": "remove logical prime b/be markers, first-occurrence keyed Bifid, decrypt exact faed570",
        "branch_masks": sorted(branches), "residual_lengths": sorted(map(len, branches.values())),
        "residual_fingerprints": {str(mask): fingerprint(text.encode()) for mask, text in branches.items()},
        "keyword_square_fingerprint": fingerprint(square.encode()), "bifid_period": 570,
        "source_fingerprint": fingerprint(segments["faed"].encode()), "terminal_e_branch_invariant": True,
    }
    forms = [{"parameters": parameters, "output_fingerprint": fingerprint(payload), "output_length": len(payload), "score": score_plaintext(payload), "round_trip": True, "retains_btcseed_prefix": output.startswith("btcseed")}]
    passwords = {}
    for transform, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
        passwords[fingerprint(password)] = {"password_hex": password.hex(), "provenance": [parameters | {"password_transform": transform}]}
    return forms, passwords


def plan():
    forms, passwords = derive_candidates()
    report = {
        "id": "C08-RESIDUAL-BIFID", "status": "UNTESTED",
        "source_evidence": [source_record(SOURCES / "salphaseion.html"), source_record(ARTIFACTS / "cycle03/prime-boundary.json"), source_record(ARTIFACTS / "cycle04/bifid-evidence.json"), source_record(OUTPUT / "instruction-order.json"), source_record(OUTPUT / "baseline-identity-audit.json")],
        "hypothesis": "Prime marker removal is a Bifid keyword preparation step, rather than treating unmodified dbbi as the keyword",
        "invariant": "Both documented prime branches yield the same source-derived square; full-period decryption re-encodes to unchanged faed; exact local target or independently justified next-stage structure is required",
        "justification": "The original dbbi keyword yielded a nonverified btcseed prefix, while its independently structured prime extraction yields a60-letter residual. Testing only that residual as the same existing Bifid keyword connects these clues without free alphabets or new ciphers. This does not establish that the residual is an AES answer; loss of the prefix is recorded rather than optimized away",
        "search_space": {"prime_branches": 2, "distinct_source_keyed_squares": 1, "bifid_periods": [570], "forms": len(forms), "password_transforms": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6},
        "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))),
        "candidate_fingerprints": sorted(passwords), "forms": forms,
        "gate": "Unchanged structure/downstream checks and bounded adjacent32-byte raw-key pairs for qualifying small-blob padding hits; final local Boolean independently verified on a positive target",
        "limits": "One source-derived keyword, one existing period/direction, no alternate alphabet/period/prefix edits or phrase composition; exclude both all15 historical ledgers and preserved baseline before AES; no candidate bytes written",
    }
    write_once_json(OUTPUT / "residual-bifid-frozen-plan.json", report)
    print(json.dumps({name: value for name, value in report.items() if name not in ("forms", "candidate_fingerprints")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
