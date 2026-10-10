#!/usr/bin/env python3
import json
from collections import Counter
from hashlib import sha256

from tools.analyze_salphaseion import split_segments
from tools.gsmg import SOURCES
from tools.prime_markers import is_prime, tokenizations
from tools.research_common import CYCLE, fingerprint, source_record, write_once_json
from tools.salphaseion_experiments import ALPHABETS, decode_board


def planned_forms():
    source = split_segments()["dbbi"]
    for mask, tokens in tokenizations(source):
        if mask not in (505, 1017):
            continue
        residual = "".join(entry["token"] for entry in tokens if not is_prime(entry["position_one_based"]))
        for zeroed_symbol in "abcdefghi":
            mapping = {symbol: "0" if symbol == zeroed_symbol else str(index + 1) for index, symbol in enumerate("abcdefghi")}
            digits = "".join(mapping[symbol] for symbol in residual)
            for reverse in (False, True):
                ordered = digits[::-1] if reverse else digits
                for alphabet_name, alphabet in ALPHABETS.items():
                    if len(alphabet) != 28 or len(set(alphabet)) != 28:
                        continue
                    parameters = {"mask": mask, "zeroed_symbol": zeroed_symbol, "reverse": reverse, "alphabet": alphabet_name, "prefixes": [1, 4]}
                    entry = {"parameters": parameters, "residual": residual, "digits": ordered, "decoded": None, "error": None}
                    try:
                        entry["decoded"] = decode_board(ordered, (1, 4), alphabet)
                    except ValueError as error:
                        entry["error"] = str(error)
                    yield entry


def build_plan():
    forms = list(planned_forms())
    passwords = {}
    for entry in forms:
        if entry["decoded"] is None:
            continue
        payload = entry["decoded"].encode("ascii")
        for representation, password in (("raw", payload), ("sha256-lowerhex", sha256(payload).hexdigest().encode()), ("sha256-raw", sha256(payload).digest())):
            identifier = fingerprint(password)
            candidate = passwords.setdefault(identifier, {"password_hex": password.hex(), "provenance": []})
            candidate["provenance"].append({**entry["parameters"], "representation": representation})
    report = {
        "id": "C02-NEXT-ZEROED-RESIDUAL",
        "status": "UNTESTED",
        "source": source_record(SOURCES / "salphaseion.html", "unchanged prime-token residuals, masks 505 and 1017"),
        "supporting_evidence": ["research/artifacts/cycle02/prime-markers.json", "research/evidence/cycle02/_work__creator_jrk.txt:627", "research/artifacts/reproduction.json"],
        "hypothesis": "Zeroing means replacing one residual symbol with digit zero, not deleting it; decode using the already reproduced checkerboard prefix pair",
        "justification": "Prime b/be markers explain part of the first block; creator-attributed zeroed-out hint and the independently reproduced downstream checkerboard motivate a finite comparison of nine zero assignments",
        "search_space": {"residual_branches": 2, "zero_assignments": 9, "directions": 2, "fixed_clue_alphabets": sum(len(alphabet) == 28 and len(set(alphabet)) == 28 for alphabet in ALPHABETS.values()), "decode_forms": len(forms), "decode_errors": sum(entry["error"] is not None for entry in forms), "successful_forms_by_branch": dict(Counter(str(entry["parameters"]["mask"]) for entry in forms if entry["error"] is None)), "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6},
        "cipher_parameters": {"cipher": "AES-256-CBC", "kdf": "EVP_BytesToKey", "iterations": 1, "padding": "PKCS7", "salt_and_ciphertext": "exact saved blobs; these unresolved cipher/KDF choices remain hypotheses"},
        "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))),
        "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 4),
        "throughput_basis": "conservative 50000 trials/second from measured cycle02 inner-search benchmark; excludes I/O and candidate scoring",
        "verification_gate": "Exact scoped-address match by both implementations or independently supported next-stage structure; padding/English fragments are not sufficient",
        "limits": "Plan generation and strict checkerboard parsing only; no AES trials executed in this plan. The duplicate-symbol hint-phrase alphabet is invalid and excluded, not silently repaired. No symbol insertion/deletion, tail repair, prefix sweep or arbitrary alphabet permutation. Zeroing rule and parsed creator identity remain unverified.",
        "forms": forms,
        "passwords": passwords,
    }
    write_once_json(CYCLE / "next-zeroed-residual-plan.json", report)
    return report


def main():
    report = build_plan()
    print(json.dumps({key: value for key, value in report.items() if key not in ("forms", "passwords")}, indent=2))


if __name__ == "__main__":
    main()
