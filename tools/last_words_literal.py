import argparse
import json
import re
from hashlib import sha256
from time import perf_counter

from tools.baseline_coverage import baseline_passwords
from tools.candidate_identity import POLICY, previously_tested, tagged_identity
from tools.gsmg import ARTIFACTS, parse_salted
from tools.research_common import fingerprint, source_record, write_once_json
from tools.secret_safe_aes import evaluate, summarize


OUTPUT = ARTIFACTS / "cycle23"
PLAN_PATH = OUTPUT / "last-words-literal-plan.json"
LEDGER_PATH = OUTPUT / "last-words-literal-aes.jsonl"
RESULTS_PATH = OUTPUT / "last-words-literal-results.json"
AUDIT_PATH = OUTPUT / "last-words-literal-audit.json"
SOURCE_SENTENCE = "One for one, four for one."


def source_forms():
    payload = (ARTIFACTS / "phase32.txt").read_bytes()
    matches = re.findall(rb"One for one, four for one\.", payload)
    if matches != [SOURCE_SENTENCE.encode("ascii")]:
        raise ValueError("Expected one exact sentence immediately before the Architect block")
    base = {
        "exact": SOURCE_SENTENCE,
        "without-terminal-period": SOURCE_SENTENCE[:-1],
        "letters-and-spaces": re.sub(r"[^A-Za-z ]", "", SOURCE_SENTENCE),
        "letters-compact": re.sub(r"[^A-Za-z]", "", SOURCE_SENTENCE),
    }
    forms = {}
    for punctuation, text in base.items():
        for case, material in (("source-case", text), ("lowercase", text.lower()), ("uppercase", text.upper())):
            forms.setdefault(material.encode("ascii"), []).append({"punctuation": punctuation, "case": case})
    return forms


def derive_candidates():
    forms = source_forms()
    candidates = {}
    public_forms = []
    for material, provenance in sorted(forms.items()):
        public_forms.append({
            "material_length": len(material),
            "material_fingerprint": fingerprint(b"gsmg-last-words-material\x00" + material),
            "provenance": provenance,
        })
        digest = sha256(material).digest()
        for transform, password in (
            ("raw", material),
            ("sha256-lowerhex", digest.hex().encode("ascii")),
            ("sha256-raw", digest),
        ):
            identifier = tagged_identity(password)
            candidates.setdefault(identifier, {"password_hex": password.hex(), "provenance": []})["provenance"].append({
                "source": "exact last sentence before the encoded Architect block",
                "material_fingerprint": fingerprint(b"gsmg-last-words-material\x00" + material),
                "normalizations": provenance,
                "password_transform": transform,
            })
    return public_forms, candidates


def historical_identifiers():
    cumulative_path = ARTIFACTS / "cycle09/cumulative-aes-audit.json"
    cumulative = json.loads(cumulative_path.read_text())
    identifiers = {fingerprint(password) for password in baseline_passwords()}
    for ledger in cumulative["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("Historical audited ledger changed")
        with path.open() as handle:
            identifiers.update(json.loads(line)[ledger.get("candidate_identifier_field", "password_sha256")] for line in handle)
    cycle10_audit = json.loads((ARTIFACTS / "cycle10/masked-missing-cell-audit.json").read_text())
    cycle10_path = ARTIFACTS / "cycle10/masked-missing-cell-aes.jsonl"
    if fingerprint(cycle10_path.read_bytes()) != cycle10_audit["ledger_sha256"]:
        raise ValueError("Cycle10 audited ledger changed")
    with cycle10_path.open() as handle:
        identifiers.update(json.loads(line)["password_fingerprint"] for line in handle)
    return identifiers


def fresh_candidates():
    forms, candidates = derive_candidates()
    historical = historical_identifiers()
    fresh = {
        identifier: candidate
        for identifier, candidate in candidates.items()
        if not previously_tested(bytes.fromhex(candidate["password_hex"]), historical)
    }
    return forms, candidates, fresh


def plan():
    forms, candidates, fresh = fresh_candidates()
    report = {
        "id": "C23-LAST-WORDS-LITERAL",
        "date": "2026-10-02",
        "status": "UNTESTED",
        "hypothesis": "The literal last sentence before the encoded Architect block is the password material referenced by lastwordsbeforearchichoice and thispassword; the following shabef command applies SHA256",
        "source_evidence": [
            source_record(ARTIFACTS / "phase32.txt", SOURCE_SENTENCE),
            source_record(ARTIFACTS.parents[1] / "research/sources/salphaseion.html", "lastwordsbeforearchichoice / thispassword / shabef sequence"),
            source_record(ARTIFACTS / "cycle08/instruction-order.json"),
            source_record(ARTIFACTS / "cycle09/cumulative-aes-audit.json"),
            source_record(ARTIFACTS / "cycle10/masked-missing-cell-audit.json"),
        ],
        "justification": "The sentence is the exact final prose before the encoded Architect speech in the source stage. Existing candidate inventories contain 1141 and generic labels but no literal occurrence of the sentence or its compact form. The three transformations are the raw source and the two standard SHA256 representations already distinguished by the verified earlier stages.",
        "invariant": "Only punctuation removal, whitespace compaction and whole-string source/lower/upper casing are allowed. No word permutations, internal case masks, added terms, dictionaries, cipher changes or keyspace enumeration.",
        "forms": forms,
        "candidate_identifier_policy": POLICY,
        "candidate_fingerprints": sorted(candidates),
        "new_candidate_fingerprints": sorted(fresh),
        "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))),
        "search_space": {
            "source_sentences": 1,
            "distinct_normalized_materials": len(forms),
            "password_transforms": ["raw", "sha256-lowerhex", "sha256-raw"],
            "unique_passwords": len(candidates),
            "previously_tested_passwords_skipped": len(candidates) - len(fresh),
            "new_unique_passwords": len(fresh),
            "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"],
            "kdf_digests": ["md5", "sha256"],
            "planned_aes_trials": len(fresh) * 6,
        },
        "verification_policy": "Only local Boolean target results and structural scores are saved. Password, AES key/IV, plaintext bytes, scalars and candidate addresses are omitted.",
        "new_cryptographic_trials_executed": 0,
    }
    write_once_json(PLAN_PATH, report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("forms", "candidate_fingerprints", "new_candidate_fingerprints", "source_evidence")}, indent=2))
    return report


def load_execution():
    saved = json.loads(PLAN_PATH.read_text())
    forms, candidates, fresh = fresh_candidates()
    if saved["forms"] != forms or saved["candidate_fingerprints"] != sorted(candidates) or saved["new_candidate_fingerprints"] != sorted(fresh):
        raise ValueError("Frozen literal-password plan no longer matches its derivation or historical filter")
    if saved["candidate_identifier_policy"] != POLICY or saved["search_space"]["planned_aes_trials"] != len(fresh) * 6:
        raise ValueError("Frozen literal-password execution parameters differ")
    blobs = {target: parse_salted((ARTIFACTS / f"{target}.b64").read_text()) for target in saved["search_space"]["targets"]}
    return saved, fresh, fingerprint(PLAN_PATH.read_bytes()), blobs


def run():
    plan_document, candidates, plan_digest, blobs = load_execution()
    started = perf_counter()
    records = []
    with LEDGER_PATH.open("x") as output:
        for identifier, candidate in sorted(candidates.items()):
            record = evaluate(identifier, candidate, plan_digest, blobs)
            output.write(json.dumps(record, sort_keys=True) + "\n")
            records.append(record)
    counts = summarize(records)
    if counts["aes_trials"] != plan_document["search_space"]["planned_aes_trials"]:
        raise ValueError("Recorded trial count differs from the frozen plan")
    report = {
        "id": plan_document["id"],
        **counts,
        "elapsed_seconds": round(perf_counter() - started, 3),
        "ledger_sha256": fingerprint(LEDGER_PATH.read_bytes()),
        "status": "PROMISING" if counts["TARGET_MATCH"] else "INCONCLUSIVE",
        "result": "Exact target match independently verified" if counts["TARGET_MATCH"] else "No exact target or recognized downstream structure; this finite literal-sentence hypothesis does not survive",
        "secret_logging": plan_document["verification_policy"],
    }
    write_once_json(RESULTS_PATH, report)
    print(json.dumps(report, indent=2))
    return report


def audit():
    plan_document, candidates, plan_digest, blobs = load_execution()
    records = []
    with LEDGER_PATH.open() as source_handle:
        for identifier, candidate in sorted(candidates.items()):
            expected = evaluate(identifier, candidate, plan_digest, blobs)
            if json.loads(source_handle.readline()) != expected:
                raise ValueError("Literal-password trial record does not reproduce")
            records.append(expected)
        if source_handle.readline():
            raise ValueError("Unexpected trailing literal-password records")
    counts = summarize(records)
    summary = json.loads(RESULTS_PATH.read_text())
    if any(summary[name] != value for name, value in counts.items()) or summary["ledger_sha256"] != fingerprint(LEDGER_PATH.read_bytes()):
        raise ValueError("Literal-password result summary differs")
    report = {
        "id": plan_document["id"] + "-AUDIT",
        **counts,
        "ledger_sha256": summary["ledger_sha256"],
        "status": "CONFIRMED",
        "meaning": "Every frozen literal form, crypto fingerprint, padding result, structure score, raw-key gate and Boolean target result reproduces without storing secret bytes",
    }
    write_once_json(AUDIT_PATH, report)
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description="Freeze, run, or audit the exact Architect-preceding sentence hypothesis")
    parser.add_argument("command", choices=("plan", "run", "audit"))
    arguments = parser.parse_args()
    {"plan": plan, "run": run, "audit": audit}[arguments.command]()


if __name__ == "__main__":
    main()
