#!/usr/bin/env python3
import json
import re

from tools.baseline_coverage import baseline_passwords, historical_identifiers
from tools.gsmg import ARTIFACTS, SOURCES, extract_salphaseion, parse_salted, textareas
from tools.plan_hash_composition import derive_candidates
from tools.research_common import fingerprint, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle08"


def locate_regions():
    path = SOURCES / "salphaseion.html"
    document = path.read_bytes().decode("utf-8")
    match = next(re.finditer(r"<textarea\b[^>]*>(.*?)</textarea>", document, re.S | re.I))
    original = match.group(1)
    if original != textareas(document)[0]:
        raise ValueError("Entity decoding requires an explicit source-offset mapping")
    positions = [index for index, symbol in enumerate(original) if not symbol.isspace()]
    compact = "".join(original[index] for index in positions)
    runs = list(re.finditer(r"[ab]{16,}", compact))
    if len(runs) != 2:
        raise ValueError("Expected the matrixsumlist and inline enter runs")
    before_blob, unused_tail = compact.split("U2FsdGVkX1", 1)
    separators = [index for index, symbol in enumerate(before_blob) if symbol == "z"]
    if len(separators) != 3:
        raise ValueError("Expected three separators before the small cipher")
    first_command = compact.index("shabefourfirsthintisyourlastcommand")
    second_command = compact.index("shabefanstoo")
    small_start = len(before_blob)
    pieces = [
        ("dbbi", 0, runs[0].start()),
        ("matrixsumlist-label", runs[0].start(), runs[0].end()),
        ("faed", runs[0].end(), separators[0]),
        ("lastwordsbeforearchichoice-label", separators[0] + 1, separators[1]),
        ("thispassword-label", separators[1] + 1, separators[2]),
        ("first-sha-command", first_command, small_start),
        ("small-base64-before-enter", small_start, runs[1].start()),
        ("inline-enter-label", runs[1].start(), runs[1].end()),
        ("small-base64-after-enter", runs[1].end(), second_command),
        ("answer-sha-command", second_command, len(compact)),
    ]
    regions = []
    for name, start, end in pieces:
        source_start = match.start(1) + positions[start]
        source_end = match.start(1) + positions[end - 1] + 1
        regions.append({
            "name": name, "normalized_span_zero_based_half_open": [start, end],
            "source_utf8_byte_span_zero_based_half_open": [len(document[:source_start].encode()), len(document[:source_end].encode())],
            "source_line_one_based": document.count("\n", 0, source_start) + 1,
            "normalized_length": end - start, "fingerprint": fingerprint(compact[start:end].encode()),
        })
    extracted = extract_salphaseion(document)
    if extracted["command_clue"] != "shabefourfirsthintisyourlastcommand" or extracted["binary_clues"] != ["matrixsumlist", "enter"]:
        raise ValueError("Primary instruction extraction differs")
    salt, ciphertext = parse_salted(extracted["small_blob"])
    if compact[small_start:second_command].replace(runs[1].group(), "", 1) != extracted["small_blob"]:
        raise ValueError("The inline enter removal does not reconstruct the exact small cipher")
    return {
        "source_evidence": [source_record(path, "first textarea; whitespace normalization mapped back to UTF-8 byte offsets")],
        "normalized_length": len(compact), "regions": regions,
        "commands": [
            {"literal": "shabefourfirsthintisyourlastcommand", "decoded_operator": "sha256", "remaining_literal": "ourfirsthintisyourlastcommand", "location": "before SMALL", "input": "UNKNOWN"},
            {"literal": "shabefanstoo", "decoded_operator": "sha256", "remaining_literal": "anstoo", "location": "after SMALL", "input": "UNKNOWN; possibly SMALL answer"},
        ],
        "small_cipher": {"ciphertext_bytes": len(ciphertext), "salt": salt.hex(), "base64_fingerprint": fingerprint(extracted["small_blob"].encode())},
        "separator_policy": "Only the three z characters before the first Base64 marker delimit plaintext clue regions; the later z belongs to the exact Base64 cipher",
        "order_invariant": first_command < small_start < runs[1].start() < runs[1].end() < second_command,
    }


def transcript_context(path, quote):
    lines = path.read_text().splitlines()
    matches = []
    header = None
    for line_number, line in enumerate(lines, 1):
        if line.startswith("=== ["):
            header = line
        if quote in line:
            matches.append({"line_one_based": line_number, "archived_header": header, "classification": "UNAUTHENTICATED_TRANSCRIPT_LABEL"})
    if not matches:
        raise ValueError("The expected archived quote is absent")
    return {"source": source_record(path, quote), "matches": matches}


def report():
    layout = locate_regions()
    previous, historical = historical_identifiers()
    baseline = {fingerprint(password) for password in baseline_passwords()}
    hints, answers, unused_forms, unused_passwords = derive_candidates()
    coverage = []
    for group, materials in (("first-hint", hints), ("unverified-answer", answers)):
        for name, text in materials.items():
            payload = text.encode()
            for transform, password in (("raw", payload), ("sha256-lowerhex", fingerprint(payload).encode()), ("sha256-raw", bytes.fromhex(fingerprint(payload)))):
                identifier = fingerprint(password)
                coverage.append({"group": group, "material": name, "transform": transform, "password_fingerprint": identifier, "in_15_ledger_union": identifier in historical, "in_baseline": identifier in baseline, "previously_tested": identifier in historical | baseline})
    creator = SOURCES.parent / "evidence/cycle02/_work__creator_jrk.txt"
    chat = SOURCES.parent / "evidence/cycle02/_work__chat_transcript.txt"
    flower_hash = fingerprint(hints["first-form-flower-answer"].encode())
    references = [
        transcript_context(creator, flower_hash),
        transcript_context(chat, "my first hint might be your last command"),
        transcript_context(chat, 'if shabef is indeed sha256, we need to hash "Follow the white rabbit"'),
        transcript_context(chat, "the part after AES is shabef ans too"),
        transcript_context(creator, 'Once you hit a "ying yang"'),
        transcript_context(creator, "when yingyang is reached, 2 hours max"),
    ]
    document = {
        "id": "C08-INSTRUCTION-ORDER", "status": "INCONCLUSIVE", **layout,
        "source_evidence": layout["source_evidence"] + [source_record(ARTIFACTS / "cycle08/baseline-identity-audit.json"), source_record(ARTIFACTS / "cycle04/hash-composition-plan.json"), source_record(SOURCES.parent / "evidence/cycle02/FINDINGS.md", "line40 secondary proposed pipeline"), source_record(SOURCES / "maintained-hints__2020-01-14-roses-are-red.png", "visually inspected: numbered colors, first puzzle piece, rabbit nest"), source_record(SOURCES / "maintained-hints__2023-08-06-4.png", "visually inspected: salvation partly passed; not an AES success report")],
        "transcript_references": references, "direct_material_coverage": coverage,
        "previous_unique_passwords_excluding_baseline": previous["unique_passwords"], "new_aes_trials": 0,
        "result": "Primary layout supports, but does not prove, SHA(input) -> SMALL -> SHA(answer) -> unresolved next cipher. No independently derived SMALL answer exists; sequential answer hashing is gated, not a license to hash arbitrary intermediate outputs",
        "evidence_corrections": [
            "The April22 2019 hash is a first-stage answer-validation digest, not an unambiguous instruction identifying the endgame first hint",
            "January8 2021 last-command remark is labeled Deleted Account, not independently authenticated creator speech",
            "August4/5 2023 sequential-AES interpretations are community proposals, not successful decryptions",
            "August6 2023 and April28 2025 yin-yang remarks do not themselves place that stage after SMALL",
            "The secondary FINDINGS.md edge directly into Cosmic Duality omits the intervening SMALL cipher; the creator's execution order remains unverified",
            "Completed source Bifid full/suffix hash passwords already failed their AES gates; running them again as sequential answers would repeat trials",
            "The historical15-ledger union excluded the separate122-password baseline; no-repeat filtering must use both sets",
        ],
        "next_bounded_construction": "Use the independently derived prime residual as the existing full-period Bifid keyword, not an arbitrary alphabet. Both83/84 logical branches produce the same keyword square because their only residual difference is an already occurring terminal e. The resulting source-preserving candidate is unverified and must pass the unchanged downstream gates",
    }
    write_once_json(OUTPUT / "instruction-order.json", document)
    print(json.dumps({"id": document["id"], "status": document["status"], "order_invariant": document["order_invariant"], "coverage_records": len(coverage), "previously_tested_direct_forms": sum(entry["previously_tested"] for entry in coverage), "new_aes_trials": 0, "result": document["result"]}, indent=2))
    return document


if __name__ == "__main__":
    report()
