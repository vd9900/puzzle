#!/usr/bin/env python3
import json

from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint
from tools.zeroed_residual import OUTPUT


def log_results():
    root = ARTIFACTS.parents[1]
    specifications = [
        ("C03-ZEROED-RESIDUAL", "zeroed-residual-results.json", "INCONCLUSIVE", "Literal single-symbol zero replacement on exact prime residuals then known checkerboard", "Execute the frozen plan, not a new dictionary; retain every parse failure", "1080 AES trials, three padding hits, no recognized structure/scoped key", "python3 -m tools.zeroed_residual audit", ["research/artifacts/cycle02/next-zeroed-residual-plan.json", "research/artifacts/cycle03/zeroed-residual-aes.jsonl"], "high for exact family negative, low for intended cipher"),
        ("C03-PRIME-BOUNDARY", "prime-boundary.json", "PROMISING", "Continue prime-position indexing into the untouched matrixsumlist binary run", "Original 23/25 color frame left two bits; next prime positions 89 and 97 occur naturally in the adjacent independently decoded a/b region", "One of 4096 tokenization/color/counter comparisons matches all 25 events: mask1017, near-white=1, continuous counter; no reset full match", "python3 -m tools.prime_boundary", ["research/sources/salphaseion.html", "research/sources/gsmg-puzzle.png"], "high for exact cross-artifact observation; not a final decrypt or authenticated intent"),
        ("C03-IMAGE-SUMSTREAM", "image-sum-results.json", "INCONCLUSIVE", "Literal original/reduced image-axis sums as mod9 stream", "matrixsumlist, 13/26 clue lengths and unique near-white position justify three explicit matrix alternatives; VIC/mod9 assumptions remain hypotheses", "2304 decode forms, 6030 passwords, 36180 AES trials, 137 padding hits, no recognized structure/scoped key; reduced total89 is not unique across deletions", "python3 -m tools.audit_cycle03", ["research/artifacts/cycle03/image-sum-plan.json", "research/artifacts/cycle03/image-sum-decodes.json", "research/artifacts/cycle03/image-sum-aes.jsonl"], "high for finite negative only"),
        ("C03-BINARY-KEY-PAIRS", "binary-key-pair-results.json", "REJECTED", "Two adjacent raw 32-byte keys in saved small-blob padding hits", "Checkerboard refers to two keys; 80-byte ciphertext admits 64..79-byte plaintext and at most15 bytes metadata", "16282 exact scalar-slot checks over509 saved hits, neither scoped address matches", "python3 -m tools.audit_binary_key_pairs plan", ["research/artifacts/cycle03/binary-key-pair-plan.json", "research/artifacts/cycle03/binary-key-pair-checks.jsonl"], "high for this direct adjacent big-endian format only"),
        ("C03-BINARY-KEY-PAIRS-IMAGE", "binary-key-pair-image-results.json", "REJECTED", "Same adjacent raw-key gate on new image-sum hits", "Do not assume random-looking output is wrong when it may contain two binary keys; test exact targets", "2912 scalar-slot checks over91 new small-blob hits, neither scoped address matches", "python3 -m tools.audit_binary_key_pairs plan --group image", ["research/artifacts/cycle03/binary-key-pair-image-plan.json", "research/artifacts/cycle03/binary-key-pair-image-checks.jsonl"], "high for this fixed format only"),
        ("C03-CUMULATIVE-AES-AUDIT", "cumulative-aes-audit.json", "CONFIRMED", "Recompute new trials and reconcile overlap with prior candidate sets", "Different source-derived families can share passwords; count unique target/KDF trials, not just sum ledgers", "35403 unique passwords, 212418 distinct target/KDF trials, 217026 trial records including overlaps, 895 padding-hit records; no new recognized structure or scoped key", "python3 -m tools.audit_cycle03", ["research/artifacts/cycle03/cumulative-aes-audit.json", "research/artifacts/cycle03/aes-ledger-audit.json"], "high for reproducibility/accounting, not puzzle completion"),
        ("C03-DECIMAL-RESIDUAL", "decimal-residual-results.json", "INCONCLUSIVE", "Adjacent solved decimal-to-byte rule on unchanged prime residual and faed", "a1/o0 decimal-to-big-endian-byte encoding is independently verified nearby; exact radix10 on the selected residual complements prior base9 trials", "160 forms, 1368 passwords, 8208 AES trials, 26 padding hits, zero recognized structure/scoped keys", "python3 -m tools.zeroed_residual audit --family decimal", ["research/artifacts/cycle03/next-decimal-residual-plan.json", "research/artifacts/cycle03/decimal-residual-aes.jsonl"], "high for finite negative only"),
        ("C03-BINARY-KEY-PAIRS-DECIMAL", "binary-key-pair-decimal-results.json", "REJECTED", "Raw adjacent two-key gate on decimal-family small-blob hits", "Validate binary private keys directly instead of assuming unreadable bytes imply failure", "480 scalar-slot checks over15 small-blob hits, neither scoped address matches", "python3 -m tools.audit_binary_key_pairs plan --group decimal", ["research/artifacts/cycle03/binary-key-pair-decimal-plan.json", "research/artifacts/cycle03/binary-key-pair-decimal-checks.jsonl"], "high for adjacent fixed big-endian format only"),
        ("C03-NEXT-RANKED-ALPHABET", "next-ranked-alphabet-plan.json", "UNTESTED", "Image-axis sum list as checkerboard alphabet ranking", "26 reduced-image axis sums and 26-letter clue favor testing a ranked alphabet rather than another additive stream; duplicate sums use fixed stable ties", "Frozen plan only: 32 alphabets, 1408 decode forms, 576 parse failures, 2496 passwords, 14976 prospective AES trials", "python3 -m tools.plan_ranked_alphabet", ["research/artifacts/cycle03/next-ranked-alphabet-plan.json", "research/sources/gsmg-puzzle.png", "research/sources/salphaseion.html"], "moderate contextual support; untested cipher role"),
    ]
    path = root / "research/candidates.jsonl"
    existing = {}
    for line in path.read_text().splitlines():
        entry = json.loads(line)
        existing[entry["id"]] = entry
    added = 0
    with path.open("a") as output:
        for identifier, artifact, status, description, reasoning, result, command, evidence, confidence in specifications:
            artifact_path = OUTPUT / artifact
            document = json.loads(artifact_path.read_text())
            search_space = document.get("search_space", {key: document[key] for key in ("unique_passwords", "aes_trials", "decode_forms", "slot_checks", "trial_records", "distinct_target_kdf_trials") if key in document})
            if "plan.json" not in artifact and artifact.endswith("results.json"):
                plan_names = {"zeroed-residual-results.json": ARTIFACTS / "cycle02/next-zeroed-residual-plan.json", "decimal-residual-results.json": OUTPUT / "next-decimal-residual-plan.json", "image-sum-results.json": OUTPUT / "image-sum-plan.json", "binary-key-pair-results.json": OUTPUT / "binary-key-pair-plan.json", "binary-key-pair-image-results.json": OUTPUT / "binary-key-pair-image-plan.json", "binary-key-pair-decimal-results.json": OUTPUT / "binary-key-pair-decimal-plan.json"}
                if artifact in plan_names:
                    search_space = json.loads(plan_names[artifact].read_text())["search_space"]
            entry = {"id": identifier, "description": description, "source_evidence": evidence, "reasoning": reasoning, "transformation": description, "search_space": search_space, "status": status, "result": result, "confidence": confidence, "reproduction_command": command, "artifact": str(artifact_path.relative_to(root)), "artifact_sha256": fingerprint(artifact_path.read_bytes()), "date": "2026-09-30", "candidate_details": "Exact per-candidate derivations/parameters/failures/results in linked immutable ledgers; structural match and audited accounting are not final solution"}
            if identifier == "C03-CUMULATIVE-AES-AUDIT":
                entry["result"] = f"{document['unique_passwords']} unique passwords, {document['distinct_target_kdf_trials']} distinct target/KDF trials, {document['trial_records']} trial records including overlaps, {document['padding_hit_records']} padding-hit records; audit verifies accounting, not the final key"
            if identifier == "C03-ZEROED-RESIDUAL":
                entry["executes_plan"] = "C02-NEXT-ZEROED-RESIDUAL"
            if status == "UNTESTED":
                entry["candidate_details"] = "Exact planned forms/parse failures/passwords are preserved; AES keys/IVs/plaintexts/gates have not been computed for this plan"
            if identifier in existing:
                if existing[identifier] == entry:
                    continue
                entry["supersedes"] = identifier
                entry["id"] = identifier + ":" + fingerprint(json.dumps(entry, sort_keys=True).encode())[:16]
                if entry["id"] in existing:
                    continue
            output.write(json.dumps(entry, sort_keys=True) + "\n")
            added += 1
    print(f"Appended {added} cycle03 records")


if __name__ == "__main__":
    log_results()
