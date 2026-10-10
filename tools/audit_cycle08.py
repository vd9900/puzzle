#!/usr/bin/env python3
import json

from tools.baseline_coverage import baseline_passwords, historical_identifiers
from tools.gsmg import ARTIFACTS
from tools.research_common import fingerprint, write_once_json
from tools.secret_safe_aes import audit, load_candidates


OUTPUT = ARTIFACTS / "cycle08"


def run():
    audited = audit("residual-bifid")
    previous, identifiers = historical_identifiers()
    baseline = {fingerprint(password) for password in baseline_passwords()}
    original, candidates, duplicates = load_candidates("residual-bifid")
    if set(candidates) & (identifiers | baseline):
        raise ValueError("The new experiment repeats a ledger or baseline candidate")
    identifiers.update(candidates)
    ledger = {"ledger": str((OUTPUT / "residual-bifid-aes.jsonl").relative_to(ARTIFACTS.parents[1])), "ledger_sha256": audited["ledger_sha256"], "records": audited["unique_passwords"], "trials": audited["aes_trials"], "padding_hits": audited["padding_hits"], "candidate_identifier_field": "password_fingerprint", "recomputed": "Exact source-derived residual keyword, reversible full-period Bifid and all secret-safe AES/Boolean gates"}
    report = {
        "id": "C08-CUMULATIVE-AES-AUDIT", "status": "CONFIRMED",
        "audited_ledgers": previous["audited_ledgers"] + [ledger],
        "unique_passwords": len(identifiers),
        "distinct_target_kdf_trials": previous["distinct_target_kdf_trials"] + audited["aes_trials"],
        "trial_records": previous["trial_records"] + audited["aes_trials"],
        "padding_hit_records": previous["padding_hit_records"] + audited["padding_hits"],
        "new_passwords": len(candidates), "previously_tested_passwords_skipped": duplicates,
        "baseline_passwords": len(baseline), "baseline_overlap_with_ledger_union": len(baseline & identifiers),
        "baseline_only_passwords": len(baseline - identifiers),
        "combined_unique_passwords_including_baseline": len(identifiers | baseline),
        "combined_distinct_target_kdf_trials_including_baseline": (len(identifiers | baseline)) * 6,
        "recorded_trial_count_including_baseline": previous["trial_records"] + audited["aes_trials"] + len(baseline) * 6,
        "TARGET_MATCH": audited["TARGET_MATCH"],
        "meaning": "Exact16-ledger union retains earlier count convention and separately accounts for baseline122 passwords/732 trials/34 overlaps; baseline metadata identities audited without replaying AES. No secondary campaign counts or solved-key claim",
    }
    write_once_json(OUTPUT / "cumulative-aes-audit.json", report)
    print(json.dumps({name: value for name, value in report.items() if name != "audited_ledgers"}, indent=2))
    return report


if __name__ == "__main__":
    run()
