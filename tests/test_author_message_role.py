import json
import unittest

from tools.author_message_role import OUTPUT, report
from tools.instruction_graphs import ROOT


class AuthorMessageRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_original_talks_for_me_body_and_locations_are_exact(self):
        communication = self.document["original_communication"]
        self.assertEqual(communication["public_text"], "The puzzle talks for me.")
        self.assertEqual(communication["creator_record"]["line_one_based"], 775)
        self.assertEqual(communication["original_chat_record"]["line_one_based"], 22661)
        for key in ("creator_record", "original_chat_record"):
            entry = communication[key]
            start, end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual((ROOT / entry["source"]["path"]).read_bytes()[start:end], communication["public_text"].encode())

    def test_author_body_is_distinct_from_truncated_reply_preview(self):
        screenshot = self.document["screenshot"]
        self.assertEqual(screenshot["dimensions"], [562, 313])
        self.assertEqual(screenshot["visible_author_body_time"], "07:08 PM")
        self.assertTrue(screenshot["clipped_reply_preview"]["not_author_body_or_complete_instruction"])
        self.assertTrue(screenshot["clipped_reply_preview"]["preview_is_truncated_not_reconstructed"])
        self.assertTrue(screenshot["lower_financial_message_out_of_scope_not_transcribed"])
        self.assertFalse(screenshot["date_and_timezone_visible"])

    def test_absent_later_phrase_is_a_preserved_coverage_limit(self):
        self.assertEqual([entry["count"] for entry in self.document["transcript_exact_companion_phrase_counts"]], [0, 0])
        self.assertTrue(self.document["coverage_reused"]["absence_not_a_disproof_of_later_screenshot"])

    def test_name_role_is_reused_without_new_format_or_consumer(self):
        self.assertTrue(self.document["name_role_reused"]["no_name_or_checkpoint_audit_repeated"])
        self.assertTrue(self.document["no_narrowed_stage_or_ciphertext_consumer"])

    def test_finite_roles_have_fields_without_private_data_dependency_search(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"], self.document["personal_data_queries"]), (0, 0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "author-message-role.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
