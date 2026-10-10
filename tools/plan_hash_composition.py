#!/usr/bin/env python3
import base64
import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS, SOURCES, SALPHASEION_PREIMAGE
from tools.image_sum_derivation import residual
from tools.research_common import fingerprint, score_plaintext, source_record, write_once_json


def derive_candidates():
    segments = split_segments()
    decoded = bifid(segments["faed"], key_square(segments["dbbi"]), 570)
    flower = "theflowerblossomsthroughwhatseemstobeaconcretesurface"
    hints = {"first-form-flower-answer": flower, "first-instruction-white-rabbit": "followthewhiterabbit", "first-image-decoded-route": "gsmg.io/theseedisplanted", "first-image-printed-text": SALPHASEION_PREIMAGE, "audio-instruction": "HASHTHETEXT"}
    answers = {"source-bifid-full570": decoded, "source-bifid-suffix563": decoded[7:], "frame-selected-residual60": residual(), "unchanged-faed570": segments["faed"]}
    forms = []
    passwords = {}
    for hint_name, hint in hints.items():
        hint_digest = bytes.fromhex(fingerprint(hint.encode()))
        for answer_name, answer in answers.items():
            answer_digest = bytes.fromhex(fingerprint(answer.encode()))
            for representation in ("digest-raw32", "digest-lowerhex64"):
                first = hint_digest if representation == "digest-raw32" else hint_digest.hex().encode()
                second = answer_digest if representation == "digest-raw32" else answer_digest.hex().encode()
                composed = {"first-then-answer": first + second, "answer-then-first": second + first, "equal-length-xor": bytes(left ^ right for left, right in zip(first, second))}
                for operation, material in composed.items():
                    parameters = {"first_hint": hint_name, "first_hint_text": hint, "first_hint_sha256": hint_digest.hex(), "answer": answer_name, "answer_sha256": answer_digest.hex(), "digest_representation": representation, "composition": operation}
                    forms.append({"parameters": parameters, "decoded_base64": base64.b64encode(material).decode(), "score": score_plaintext(material)})
                    for transform, password in (("raw-composition", material), ("sha256-composition-lowerhex", fingerprint(material).encode()), ("sha256-composition-raw", bytes.fromhex(fingerprint(material)))):
                        candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                        candidate["provenance"].append(parameters | {"password_transform": transform})
    return hints, answers, forms, passwords


def plan():
    hints, answers, forms, passwords = derive_candidates()
    transcript_path = SOURCES.parent / "evidence/cycle02/_work__creator_jrk.txt"
    first_hash = fingerprint(hints["first-form-flower-answer"].encode())
    if first_hash not in transcript_path.read_text():
        raise ValueError("First-stage flower hash does not match preserved transcript")
    report = {"id": "C04-HASH-COMPOSITION", "status": "UNTESTED", "source_evidence": [source_record(SOURCES / "salphaseion.html", "shabefourfirsthintisyourlastcommand, shabefanstoo"), source_record(transcript_path, "2019-04-22 first-stage answer hash"), source_record(ARTIFACTS / "cycle04/bifid-evidence.json"), source_record(ARTIFACTS / "cycle03/prime-boundary.json")], "first_flower_hash_verified": first_hash, "hypothesis": "The two sha256 instructions require combining first-hint and answer digests before the unresolved AES", "justification": "Exact shabef...ans too wording supports two source-grounded hashes; first hint has multiple documented interpretations. Test digest concatenation ordering and complementary XOR as explicitly weaker yinyang alternative. No claim that hash composition is intended.", "search_space": {"first_hint_materials": len(hints), "answer_materials": len(answers), "digest_representations": 2, "composition_rules": 3, "decode_forms": len(forms), "password_transforms": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 3), "gate": "Recognized independently supported downstream stage or exact scoped target, including bounded adjacent raw-key pairs in small-blob plaintext", "limits": "Frozen source-grounded first-hint/answer materials only; no arbitrary phrases, free hash chain depth, KDF iteration/algorithm expansion, or key-space search. Hash instructions may instead be sequential, not compositional.", "forms": forms, "passwords": passwords}
    write_once_json(ARTIFACTS / "cycle04/hash-composition-plan.json", report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("forms", "passwords")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
