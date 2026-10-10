import json
import unittest

from tools.selector_evidence import OUTPUT, greeting_audit, original_time_order, report, source_boundary_evidence


class SelectorEvidenceTests(unittest.TestCase):
    def test_bingo_precedes_later_recipe_and_has_no_reply_binding(self):
        evidence = original_time_order()
        self.assertEqual(evidence["bingo_precedes_extraction_seconds"], 601)
        self.assertEqual(evidence["bingo_precedes_full_recipe_seconds"], 1705)
        self.assertTrue(evidence["no_reply_reference_identifies_confirmation_target"])

    def test_binary_greeting_and_exact_timestamp_intervals(self):
        evidence = greeting_audit()
        self.assertEqual(evidence["dot_counts"], [1, 2, 3, 4, 5])
        self.assertEqual(evidence["exact_intermessage_seconds"], [73, 50, 62, 58, 58])
        self.assertFalse(evidence["all_messages_exactly_one_minute_apart"])
        self.assertEqual(evidence["records"][-1]["octet_count"], 77)
        self.assertEqual(evidence["records"][-1]["archived_utc_timestamp"], "2026-01-01T03:20:03+00:00")

    def test_array_indexing_and_typo_response_are_separate_speakers(self):
        evidence = source_boundary_evidence()
        records = evidence["attributed_records"]
        self.assertIn("Janusz Baran", records[0]["header"])
        self.assertIn("Jrk Bgrt", records[1]["header"])
        self.assertEqual(records[0]["classification"], "COMMUNITY_PROPOSAL")
        self.assertEqual(records[3]["classification"], "EXPLICIT_NEXT_MESSAGE_NOT_A_HINT")

    def test_primary_markup_contains_no_extra_selector_tags(self):
        evidence = source_boundary_evidence()
        self.assertEqual(evidence["creator_export_message_count"], 411)
        self.assertTrue(all(value == 0 for value in evidence["creator_export_literal_keyword_counts"].values()))
        self.assertEqual(evidence["primary_html"]["comment_count"], 0)
        self.assertEqual(evidence["primary_html"]["script_count"], 0)
        self.assertTrue(evidence["primary_html"]["no_hidden_selector_found_in_relevant_tags"])

    def test_frozen_evidence_matches_regeneration_and_preserves_unknowns(self):
        path = OUTPUT / "selector-evidence.json"
        original = path.read_bytes()
        document = report()
        self.assertEqual(json.loads(original), document)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(document["status"], "INCONCLUSIVE")
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
