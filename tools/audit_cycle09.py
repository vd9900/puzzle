#!/usr/bin/env python3
import json

from tools.baseline_coverage import baseline_passwords
from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint, write_once_json
from tools.secret_safe_aes import audit, load_candidates


OUTPUT = ARTIFACTS / "cycle09"


def extend_audit(previous, family):
    audited = audit(family)
    identifiers = set()
    for ledger in previous["audited_ledgers"]:
        path = ARTIFACTS.parents[1] / ledger["ledger"]
        if fingerprint(path.read_bytes()) != ledger["ledger_sha256"]:
            raise ValueError("Historical audited ledger changed")
        with path.open() as source:
            identifiers.update(json.loads(line)[ledger.get("candidate_identifier_field", "password_sha256")] for line in source)
    if len(identifiers) != previous["unique_passwords"]:
        raise ValueError("Historical candidate union differs from its audited count")
    baseline = {fingerprint(password) for password in baseline_passwords()}
    original, candidates, duplicates = load_candidates(family)
    if identifiers & set(candidates) or baseline & set(candidates):
        raise ValueError("Current experiment repeats a baseline or ledger candidate")
    identifiers.update(candidates)
    ledger = {"ledger": str((OUTPUT / (family + "-aes.jsonl")).relative_to(ARTIFACTS.parents[1])), "ledger_sha256": audited["ledger_sha256"], "records": audited["unique_passwords"], "trials": audited["aes_trials"], "padding_hits": audited["padding_hits"], "candidate_identifier_field": "password_fingerprint", "recomputed": "Every frozen source transform, crypto fingerprint, padding/structure/score and local Boolean direct/adjacent-key gate"}
    return {
        "id": "C09-CUMULATIVE-AES-AUDIT", "status": "CONFIRMED",
        "audited_ledgers": previous["audited_ledgers"] + [ledger],
        "unique_passwords": len(identifiers),
        "distinct_target_kdf_trials": previous["distinct_target_kdf_trials"] + audited["aes_trials"],
        "trial_records": previous["trial_records"] + audited["aes_trials"],
        "padding_hit_records": previous["padding_hit_records"] + audited["padding_hits"],
        "new_passwords": len(candidates), "previously_tested_passwords_skipped": duplicates,
        "baseline_passwords": len(baseline), "baseline_overlap_with_ledger_union": len(baseline & identifiers),
        "baseline_only_passwords": len(baseline - identifiers),
        "combined_unique_passwords_including_baseline": len(identifiers | baseline),
        "combined_distinct_target_kdf_trials_including_baseline": len(identifiers | baseline) * 6,
        "recorded_trial_count_including_baseline": previous["trial_records"] + audited["aes_trials"] + len(baseline) * 6,
        "TARGET_MATCH": previous["TARGET_MATCH"] or audited["TARGET_MATCH"],
        "meaning": "Exact detailed-ledger union with separately identity-audited baseline122 passwords/732 trials/34 overlaps; no baseline AES replay, secondary counts or solved-key claim",
    }


def run():
    previous = json.loads((ARTIFACTS / "cycle08/cumulative-aes-audit.json").read_text())
    current = extend_audit(previous, "post-bifid-routing")
    current["id"] = "C09-POST-BIFID-CUMULATIVE-AES-AUDIT"
    write_once_json(OUTPUT / "post-bifid-cumulative-aes-audit.json", current)
    if (OUTPUT / "spiral-ring-sums-aes.jsonl").exists():
        current = extend_audit(current, "spiral-ring-sums")
        current["cycle09_new_passwords"] = current["unique_passwords"] - previous["unique_passwords"]
        current["cycle09_new_aes_trials"] = current["distinct_target_kdf_trials"] - previous["distinct_target_kdf_trials"]
    else:
        current = current | {"id": "C09-CUMULATIVE-AES-AUDIT"}
    write_once_json(OUTPUT / "cumulative-aes-audit.json", current)
    print(json.dumps({name: value for name, value in current.items() if name != "audited_ledgers"}, indent=2))
    return current


if __name__ == "__main__":
    run()
