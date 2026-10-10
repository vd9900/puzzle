#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS, PHASE32_PREIMAGE
from tools.research_common import fingerprint, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle08"


def baseline_passwords():
    speech = (ARTIFACTS / "phase32-beaufort.txt").read_text().strip()
    message = (ARTIFACTS / "phase32-checkerboard.txt").read_text().strip()
    clues = ("matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword")
    materials = {
        "causality", PHASE32_PREIMAGE, "thematrixhasyou", "THEMATRIXHASYOU", "why", "neo", "you",
        "halfandbetterhalf", "half", "betterhalf", "fubcdora/lethingkymvpszjqwx.", "1141", "cp1141",
        "ourfirsthintisyourlastcommand", "hashthetext", "HASHTHETEXT", "ciaobellao", "sha256",
        speech, speech[1141:], speech[-len("ciaobellao"):], message, message.upper(),
        "".join(clues), "".join(clues) + "matrixsumlist",
        "matrixsumlistlastwordsbeforearchichoicethispassword", "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    }
    materials.update(clues)
    materials.update(speech[-width:] for width in range(1, 33))
    passwords = set()
    for material in materials:
        payload = material.encode()
        passwords.update((payload, fingerprint(payload).encode()))
    expected = json.loads((ARTIFACTS / "bounded-search.json").read_text())
    if len(passwords) != expected["passwords_per_target"] or fingerprint(b"\x00".join(sorted(passwords))) != expected["candidate_set_sha256"]:
        raise ValueError("The preserved baseline candidate identities do not reproduce")
    if expected["trials"] != len(passwords) * 6 or any(hit["password_sha256"] not in {fingerprint(password) for password in passwords} for hit in expected["padding_valid_hits"]):
        raise ValueError("The preserved baseline trial metadata differs from its candidate set")
    return passwords


def historical_identifiers():
    previous = json.loads((ARTIFACTS / "cycle07/cumulative-aes-audit.json").read_text())
    identifiers = set()
    for ledger in previous["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("A historical audited ledger changed")
        with path.open() as source:
            identifiers.update(json.loads(line)[ledger.get("candidate_identifier_field", "password_sha256")] for line in source)
    if len(identifiers) != previous["unique_passwords"]:
        raise ValueError("The historical password union does not reproduce")
    return previous, identifiers


def report():
    passwords = baseline_passwords()
    identifiers = {fingerprint(password) for password in passwords}
    previous, historical = historical_identifiers()
    document = {
        "id": "C08-BASELINE-IDENTITY-AUDIT", "status": "CONFIRMED",
        "source_evidence": [source_record(ARTIFACTS / name) for name in ("bounded-search.json", "phase32-beaufort.txt", "phase32-checkerboard.txt", "cycle07/cumulative-aes-audit.json")] + [source_record(ARTIFACTS.parents[1] / "tools/gsmg.py", "bounded_search candidate generation only")],
        "passwords": len(passwords), "previously_executed_baseline_trials": len(passwords) * 6,
        "candidate_set_sha256": fingerprint(b"\x00".join(sorted(passwords))),
        "candidate_fingerprints": sorted(identifiers), "overlap_with_15_ledger_union": len(identifiers & historical),
        "baseline_only_passwords": len(identifiers - historical),
        "combined_unique_passwords": len(identifiers | historical),
        "combined_distinct_target_kdf_trials": previous["distinct_target_kdf_trials"] + len(identifiers - historical) * 6,
        "new_aes_trials": 0,
        "result": "Exact baseline candidate identities reproduce without rerunning AES; earlier cumulative ledgers intentionally excluded baseline but future no-repeat filtering must include it",
        "limits": "This audits candidate identity and preserved metadata, not the unrecorded baseline padding-negative outcomes; no baseline AES trial is rerun and no secret bytes are logged",
    }
    write_once_json(OUTPUT / "baseline-identity-audit.json", document)
    print(json.dumps({name: value for name, value in document.items() if name not in ("candidate_fingerprints", "source_evidence")}, indent=2))
    return document


if __name__ == "__main__":
    report()
