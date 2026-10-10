import json
import unittest

from tools.last_words_literal import AUDIT_PATH, LEDGER_PATH, PLAN_PATH, RESULTS_PATH, derive_candidates, source_forms


class LastWordsLiteralTests(unittest.TestCase):
    def test_source_forms_are_bounded(self):
        forms = source_forms()
        self.assertEqual(len(forms), 12)
        self.assertIn(b"One for one, four for one.", forms)
        self.assertIn(b"oneforonefourforone", forms)
        self.assertIn(b"ONEFORONEFOURFORONE", forms)

    def test_candidate_derivation_is_exact(self):
        forms, candidates = derive_candidates()
        self.assertEqual((len(forms), len(candidates)), (12, 36))
        self.assertEqual({entry["password_transform"] for candidate in candidates.values() for entry in candidate["provenance"]}, {"raw", "sha256-lowerhex", "sha256-raw"})

    def test_frozen_execution_is_complete_and_secret_safe(self):
        plan = json.loads(PLAN_PATH.read_text())
        results = json.loads(RESULTS_PATH.read_text())
        audit = json.loads(AUDIT_PATH.read_text())
        self.assertEqual(plan["search_space"]["new_unique_passwords"], results["unique_passwords"])
        self.assertEqual(plan["search_space"]["planned_aes_trials"], results["aes_trials"])
        self.assertEqual(results["ledger_sha256"], audit["ledger_sha256"])
        self.assertFalse(results["TARGET_MATCH"])
        forbidden = ("password_hex", "password_base64", '"key":', '"iv":', '"plaintext":', '"addresses":')
        ledger = LEDGER_PATH.read_text()
        self.assertTrue(all(item not in ledger for item in forbidden))


if __name__ == "__main__":
    unittest.main()
