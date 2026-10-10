import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.baseline_coverage import baseline_passwords, historical_identifiers
from tools.gsmg import ARTIFACTS, SOURCES
from tools.instruction_order import locate_regions, transcript_context
from tools.plan_residual_bifid import derive_candidates
from tools.plan_post_bifid_routing import derive_candidates as post_bifid_candidates
from tools.prime_bifid_controls import branch_templates, control, prefix_for_source_key, rebuild
from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.research_common import fingerprint
from tools.secret_safe_aes import load_candidates


OUTPUT = ARTIFACTS / "cycle08"


class InstructionOrderTests(unittest.TestCase):
    def test_primary_region_offsets_preserve_exact_source(self):
        document = (SOURCES / "salphaseion.html").read_bytes()
        report = locate_regions()
        self.assertEqual(report["normalized_length"], 1075)
        self.assertTrue(report["order_invariant"])
        regions = {region["name"]: region for region in report["regions"]}
        self.assertEqual(regions["first-sha-command"]["normalized_span_zero_based_half_open"], [860, 895])
        self.assertEqual(regions["answer-sha-command"]["normalized_span_zero_based_half_open"], [1063, 1075])
        for region in report["regions"]:
            start, end = region["source_utf8_byte_span_zero_based_half_open"]
            normalized = "".join(document[start:end].decode().split()).encode()
            self.assertEqual(fingerprint(normalized), region["fingerprint"])
            self.assertEqual(len(normalized), region["normalized_length"])
        self.assertEqual(report["commands"][0]["remaining_literal"], "ourfirsthintisyourlastcommand")
        self.assertEqual(report["small_cipher"]["ciphertext_bytes"], 80)

    def test_archived_quote_does_not_upgrade_author_authentication(self):
        path = SOURCES.parent / "evidence/cycle02/_work__chat_transcript.txt"
        record = transcript_context(path, "my first hint might be your last command")
        self.assertEqual(len(record["matches"]), 1)
        match = record["matches"][0]
        self.assertEqual(match["line_one_based"], 12406)
        self.assertIn("08.01.2021", match["archived_header"])
        self.assertIn("Deleted Account", match["archived_header"])
        self.assertEqual(match["classification"], "UNAUTHENTICATED_TRANSCRIPT_LABEL")
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory) / "empty.txt"
            empty.write_text("=== [public synthetic timestamp] public synthetic author\nNo instruction here\n")
            with self.assertRaisesRegex(ValueError, "quote is absent"):
                transcript_context(empty, "absent quote")

    def test_baseline_candidate_identities_are_bound_to_preserved_digest(self):
        passwords = baseline_passwords()
        report = json.loads((OUTPUT / "baseline-identity-audit.json").read_text())
        identifiers = {fingerprint(password) for password in passwords}
        self.assertEqual(len(passwords), 122)
        self.assertEqual(report["candidate_fingerprints"], sorted(identifiers))
        self.assertEqual(report["new_aes_trials"], 0)
        previous, historical = historical_identifiers()
        self.assertEqual((len(identifiers & historical), len(identifiers - historical)), (34, 88))
        self.assertEqual(len(historical | identifiers), 41707)
        self.assertEqual(previous["unique_passwords"], 41619)
        with patch("tools.baseline_coverage.fingerprint", return_value="wrong-public-fingerprint"):
            with self.assertRaisesRegex(ValueError, "identities do not reproduce"):
                baseline_passwords()

    def test_exact_residual_keyword_family_reproduces_without_secret_logging(self):
        forms, candidates = derive_candidates()
        frozen = json.loads((OUTPUT / "residual-bifid-frozen-plan.json").read_text())
        self.assertEqual((len(forms), len(candidates)), (1, 3))
        self.assertEqual(frozen["forms"], forms)
        self.assertEqual(frozen["candidate_fingerprints"], sorted(candidates))
        self.assertEqual(frozen["candidate_set_sha256"], fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))))
        self.assertTrue(forms[0]["round_trip"])
        self.assertFalse(forms[0]["retains_btcseed_prefix"])
        self.assertEqual(forms[0]["parameters"]["residual_lengths"], [60, 61])
        encoded = json.dumps(frozen).encode()
        for candidate in candidates.values():
            if candidate["provenance"][0]["password_transform"] != "sha256-lowerhex":
                self.assertTrue(bytes.fromhex(candidate["password_hex"]) not in encoded, "Raw candidate material must not be serialized")
        self.assertNotIn("passwords", frozen)

    def test_baseline_and_all_ledgers_participate_in_no_repeat_gate(self):
        plan, candidates, duplicates = load_candidates("residual-bifid")
        self.assertEqual((len(candidates), duplicates), (3, 0))
        self.assertEqual(plan["search_space"]["planned_aes_trials"], 18)
        with patch("tools.baseline_coverage.baseline_passwords", return_value={bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()}):
            unused_plan, filtered, skipped = load_candidates("residual-bifid")
        self.assertEqual((len(filtered), skipped), (0, 3))

    def test_prime_conditioned_prefix_control_preserves_source_constraints(self):
        segments = split_segments()
        for template, residual in branch_templates().values():
            self.assertEqual(rebuild(template, residual), segments["dbbi"])
            alternative = rebuild(template, residual[::-1])
            self.assertEqual(sorted(alternative), sorted(segments["dbbi"]))
            self.assertEqual(prefix_for_source_key(segments["faed"], alternative), bifid(segments["faed"], key_square(alternative), 570)[:7])
        first = control(20, 2026093008)
        self.assertEqual(first, control(20, 2026093008))
        self.assertEqual(first["new_aes_trials"], 0)
        self.assertTrue(first["original_prefix_reproduced"])

    def test_completed_secret_safe_results_and_combined_union(self):
        result = json.loads((OUTPUT / "residual-bifid-results.json").read_text())
        self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"], result["bounded_raw_key_slots"]), (18, 0, 0, 0))
        self.assertFalse(result["TARGET_MATCH"])
        self.assertEqual(result["ledger_sha256"], fingerprint((OUTPUT / "residual-bifid-aes.jsonl").read_bytes()))
        union = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
        self.assertEqual((len(union["audited_ledgers"]), union["unique_passwords"], union["distinct_target_kdf_trials"], union["trial_records"], union["padding_hit_records"]), (16, 41622, 249732, 254340, 1036))
        self.assertEqual((union["combined_unique_passwords_including_baseline"], union["combined_distinct_target_kdf_trials_including_baseline"], union["recorded_trial_count_including_baseline"]), (41710, 250260, 255072))

    def test_next_plan_preserves_header_and_contains_no_password_bytes(self):
        forms, candidates = post_bifid_candidates()
        plan = json.loads((OUTPUT / "next-post-bifid-routing-plan.json").read_text())
        self.assertEqual(plan["forms"], forms)
        self.assertEqual(plan["candidate_fingerprints"], sorted(candidates))
        self.assertTrue(all(form["complete_inverse_round_trip"] for form in forms))
        self.assertTrue(all(form["parameters"]["body_length"] == 563 for form in forms))
        encoded = json.dumps(plan).encode()
        self.assertTrue(all(bytes.fromhex(candidate["password_hex"]) not in encoded for candidate in candidates.values()), "Candidate password bytes must not be serialized")
        self.assertEqual(plan["new_aes_trials_executed"], 0)


if __name__ == "__main__":
    unittest.main()
