#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint


OUTPUT = ARTIFACTS / "cycle04"


def log_results():
    root = ARTIFACTS.parents[1]
    configurations = [
        ("C04-RANKED-ALPHABET", "ranked-alphabet-results.json", "Stable-ranked image-axis sums as checkerboard alphabet", "26 sums and26-letter clue support a finite ranking interpretation, not an established cipher key", "python3 -m tools.zeroed_residual audit --family ranked", ["research/artifacts/cycle03/next-ranked-alphabet-plan.json", "research/artifacts/cycle04/ranked-alphabet-aes.jsonl"], ARTIFACTS / "cycle03/next-ranked-alphabet-plan.json"),
        ("C04-BIFID-EVIDENCE", "bifid-evidence.json", "Exact source-keyed Bifid btcseed claim and conditional controls", "Reproduce concrete claim with round-trip, derive eight input constraints, show forced parity restriction and compare exact symbol-multiset shuffle nulls", "python3 -m tools.bifid_evidence --shuffles 10000", ["research/sources/salphaseion.html", "research/evidence/cycle02/_work__chat_transcript.txt"], None),
        ("C04-BIFID-SQUARE-CONTROL", "bifid-square-control.json", "Measure prefix selectivity over9! small-square symbol orders", "Existing eight-key assertion is independently testable; assess selectivity, not expand password/wallet-key search", "python3 -m tools.bifid_square_controls", ["research/artifacts/cycle04/bifid-square-control-plan.json", "research/artifacts/cycle04/bifid-evidence.json"], OUTPUT / "bifid-square-control-plan.json"),
        ("C04-BIFID-MATERIAL", "bifid-material-results.json", "Exact Bifid output/suffix/parity rails as AES material", "Concrete source-keyed output can feed a downstream gate; alphabetic noise is not itself evidence of a successful decode", "python3 -m tools.zeroed_residual audit --family bifid", ["research/artifacts/cycle04/bifid-material-plan.json", "research/artifacts/cycle04/bifid-material-aes.jsonl"], OUTPUT / "bifid-material-plan.json"),
        ("C04-HASH-COMPOSITION", "hash-composition-results.json", "Combine first-hint and source-answer sha256 digests", "Two explicit shabef instructions motivate bounded composition; sequential interpretation remains open and XOR is a weaker yinyang hypothesis", "python3 -m tools.zeroed_residual audit --family composition", ["research/artifacts/cycle04/hash-composition-plan.json", "research/artifacts/cycle04/hash-composition-aes.jsonl"], OUTPUT / "hash-composition-plan.json"),
        ("C04-CUMULATIVE-AES-AUDIT", "cumulative-aes-audit.json", "Cumulative distinct password/target/KDF accounting", "Overlapping families must not inflate unique tested space; exact derivation/cipher audits precede counts", "python3 -m tools.audit_cycle04", ["research/artifacts/cycle04/aes-ledger-audit.json", "research/artifacts/cycle04/cumulative-aes-audit.json"], None),
        ("C04-NEXT-LITERAL-SUMLIST", "next-literal-sumlist-plan.json", "Literal image-axis sum lists and exact words before choice", "Test actual clue nouns as outputs rather than assumed alphabet/stream roles; source image and verified speech fix inputs", "python3 -m tools.plan_literal_sumlist", ["research/sources/gsmg-puzzle.png", "research/sources/salphaseion.html", "research/artifacts/phase32-beaufort.txt"], OUTPUT / "next-literal-sumlist-plan.json"),
    ]
    for group in ("ranked", "bifid", "composition"):
        configurations.append(("C04-BINARY-KEY-PAIRS-" + group.upper(), "binary-key-pair-" + group + "-results.json", "Adjacent raw-key format on " + group + " small-blob hits", "Checkerboard explicitly references two keys; check exact targets even for unreadable plaintext", "python3 -m tools.audit_binary_key_pairs audit --group " + group, ["research/artifacts/cycle04/binary-key-pair-" + group + "-checks.jsonl", "research/artifacts/cycle04/binary-key-pair-" + group + "-audit.json"], OUTPUT / ("binary-key-pair-" + group + "-plan.json")))
    ledger_path = root / "research/candidates.jsonl"
    existing = {entry["id"]: entry for entry in (json.loads(line) for line in ledger_path.read_text().splitlines())}
    added = 0
    with ledger_path.open("a") as output:
        for identifier, artifact, description, reasoning, command, sources, plan_path in configurations:
            artifact_path = OUTPUT / artifact
            document = json.loads(artifact_path.read_text())
            space_document = json.loads(plan_path.read_text()) if plan_path else document
            search_space = space_document.get("search_space", {key: document[key] for key in ("unique_passwords", "trial_records", "distinct_target_kdf_trials", "square_prefixes_tested", "prefix_matches") if key in document})
            result = document.get("result", document.get("meaning", document.get("limits")))
            if identifier == "C04-CUMULATIVE-AES-AUDIT":
                result = f"{document['unique_passwords']} unique passwords, {document['distinct_target_kdf_trials']} distinct target/KDF trials, {document['trial_records']} records, {document['padding_hit_records']} padding-hit records; final key absent"
            if document["status"] == "UNTESTED":
                result = "Frozen plan only; actual AES KEY/IV/padding/plaintext/target results not yet executed"
            entry = {"id": identifier, "description": description, "source_evidence": sources, "reasoning": reasoning, "transformation": description, "search_space": search_space, "status": document["status"], "result": result, "confidence": "high for literal observations/reproduction; intended cipher/key role remains unproven", "reproduction_command": command, "artifact": str(artifact_path.relative_to(root)), "artifact_sha256": fingerprint(artifact_path.read_bytes()), "date": "2026-09-30", "candidate_details": "Exact plans/derivations/parameters and outcomes are in linked artifacts; UNTESTED plans lack AES results"}
            if identifier == "C04-RANKED-ALPHABET":
                entry["executes_plan"] = "C03-NEXT-RANKED-ALPHABET"
            if identifier in existing:
                if existing[identifier] == entry:
                    continue
                entry["supersedes"] = identifier
                entry["id"] = identifier + ":" + fingerprint(json.dumps(entry, sort_keys=True).encode())[:16]
                if entry["id"] in existing:
                    continue
            output.write(json.dumps(entry, sort_keys=True) + "\n")
            added += 1
    print(f"Appended {added} cycle04 records")


if __name__ == "__main__":
    log_results()
