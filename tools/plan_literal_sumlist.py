#!/usr/bin/env python3
import base64
import json

from tools.gsmg import ARTIFACTS, SOURCES
from tools.image_sum_derivation import image_matrices
from tools.research_common import fingerprint, source_record, write_once_json


def derive_candidates():
    lists = {}
    for name, matrix in image_matrices():
        rows = list(map(sum, matrix))
        columns = list(map(sum, zip(*matrix)))
        for axis, sums in (("rows", rows), ("columns", columns), ("rows-then-columns", rows + columns), ("columns-then-rows", columns + rows)):
            for reverse in (False, True):
                values = sums[::-1] if reverse else sums
                lists.setdefault(tuple(values), []).append({"matrix": name, "axis": axis, "reverse": reverse, "shape": [len(matrix), len(matrix[0])]})
    speech = (ARTIFACTS / "phase32-beaufort.txt").read_text().strip()
    words = "reinsertingtheprimebasics"
    if words + "afterwhichyouwillberequiredtoselect" not in speech:
        raise ValueError("Exact last words before choice no longer match verified speech")
    passwords = {}
    forms = []
    for sums, provenance in lists.items():
        materials = {"raw-one-byte-totals": bytes(sums), "decimal-concatenation": "".join(map(str, sums)).encode(), "decimal-comma-list": ",".join(map(str, sums)).encode(), "a1z26-axis-letters": "".join(chr(96 + value) for value in sums).encode()}
        for representation, material in materials.items():
            for wording, composition in (("sumlist-alone", material), ("sumlist-before-lastwords", material + words.encode()), ("lastwords-before-sumlist", words.encode() + material)):
                parameters = {"axis_sums": list(sums), "matrix_provenance": provenance, "material_representation": representation, "wording_composition": wording, "last_words_before_choice": words}
                forms.append({"parameters": parameters, "material_base64": base64.b64encode(composition).decode()})
                for transform, password in (("raw", composition), ("sha256-lowerhex", fingerprint(composition).encode()), ("sha256-raw", bytes.fromhex(fingerprint(composition)))):
                    candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                    candidate["provenance"].append(parameters | {"password_transform": transform})
    return lists, forms, passwords


def plan():
    lists, forms, passwords = derive_candidates()
    report = {"id": "C04-NEXT-LITERAL-SUMLIST", "status": "UNTESTED", "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png"), source_record(SOURCES / "salphaseion.html", "matrixsumlist, lastwordsbeforearchichoice, thispassword"), source_record(ARTIFACTS / "phase32-beaufort.txt", "reinsertingtheprimebasics before the select-from-ciphers clause")], "hypothesis": "The literal matrix-axis sum list, optionally ordered with the exact words before choice, is the passphrase material", "reasoning": "Tests the explicit neighboring clue nouns as actual outputs rather than guessed alphabet/additive stream roles. Source grid and verified speech constrain all inputs; representations and concatenation order remain hypotheses.", "search_space": {"matrix_variants": 3, "axis_orders": 4, "directions": 2, "distinct_literal_sum_lists": len(lists), "material_representations": 4, "wording_compositions": 3, "forms": len(forms), "password_transforms": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 3), "gate": "Recognized independent next-stage structure or exact scoped key; bounded adjacent raw-key gate for small-blob hits", "limits": "Plan only, no AES executed. No additional word window/row deletion, altered image, cipher key, tie permutation or password dictionary. Near-white hypotheses stay explicit and originals unchanged.", "forms": forms, "passwords": passwords}
    write_once_json(ARTIFACTS / "cycle04/next-literal-sumlist-plan.json", report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("forms", "passwords")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
