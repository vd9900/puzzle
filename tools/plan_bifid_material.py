#!/usr/bin/env python3
import base64
import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import SOURCES
from tools.research_common import fingerprint, score_plaintext, source_record, write_once_json


def derive_candidates():
    segments = split_segments()
    square = key_square(segments["dbbi"])
    decoded = bifid(segments["faed"], square, 570)
    if not decoded.startswith("btcseed"):
        raise ValueError("Preserved Bifid claim no longer reproduces")
    materials = {"bifid-full570": decoded, "after-btcseed563": decoded[7:], "full-even-positions285": decoded[::2], "full-odd-positions285": decoded[1::2], "bifid-prefix": "btcseed", "source-key-square": square}
    forms = []
    passwords = {}
    for material_name, text in materials.items():
        for transform, material in (("exact-lowercase", text.encode()), ("uppercase", text.upper().encode()), ("reverse-bytes", text[::-1].encode())):
            parameters = {"material": material_name, "transform": transform, "bifid_square": square, "bifid_period": 570, "source_wording": "exact faed with full-period Bifid; remove exactly the reproduced prefix only for suffix variant"}
            forms.append({"parameters": parameters, "decoded_base64": base64.b64encode(material).decode(), "score": score_plaintext(material)})
            for representation, password in (("raw", material), ("sha256-lowerhex", fingerprint(material).encode()), ("sha256-raw", bytes.fromhex(fingerprint(material)))):
                candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                candidate["provenance"].append(parameters | {"representation": representation})
    return forms, passwords


def plan():
    from tools.gsmg import ARTIFACTS

    forms, passwords = derive_candidates()
    report = {"id": "C04-BIFID-MATERIAL", "status": "UNTESTED", "source_evidence": [source_record(SOURCES / "salphaseion.html"), source_record(ARTIFACTS / "cycle04/bifid-evidence.json")], "hypothesis": "Exact source-derived Bifid output, reproduced btcseed prefix/suffix, or complementary parity rails feed unresolved AES", "justification": "A source-keyed public recipe reproduces a concrete btcseed prefix and exact archived570-letter result. Testing its actual material as downstream passphrase is stronger than assuming letters imply a solution. Parity rails are explicit weaker yinyang alternatives; their alphabet restriction is algebraically forced.", "search_space": {"materials": 6, "text_transforms": 3, "decode_forms": len(forms), "hash_representations": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 3), "gate": "Independent downstream structure or exact scoped-address match, including bounded direct raw-key pair interpretation of small-blob hits", "limits": "Plan only; no free Bifid key/period, second cipher, decoder alphabet, payload edit, arbitrary slice or brute-force dictionary. Prefix alone is not enough.", "forms": forms, "passwords": passwords}
    write_once_json(ARTIFACTS / "cycle04/bifid-material-plan.json", report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("forms", "passwords")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
