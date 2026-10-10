import json
import unittest

from tools.contextual_hint_audit import OUTPUT, report
from tools.instruction_graphs import ROOT


class ContextualHintAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_five_README_anchors_reconstruct_exact_bytes_and_lines(self):
        maps = self.document["readme_maps"]
        self.assertEqual(len(maps), 5)
        self.assertEqual([entry["line_one_based"] for entry in maps], [411, 413, 415, 417, 419])
        for entry in maps:
            start, end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual((ROOT / entry["source"]["path"]).read_bytes()[start:end], entry["literal"].encode())

    def test_snapshot_coverage_precedes_labeled_hint_and_has_no_exact_message(self):
        ranges = self.document["original_transcript_coverage"]
        self.assertEqual([entry["original_header_records"] for entry in ranges], [411, 51177])
        self.assertEqual([entry["latest_archived_UTC"][:10] for entry in ranges], ["2026-05-28", "2026-06-12"])
        self.assertTrue(all(entry["latest_record_precedes_secondary_July12_label"] for entry in ranges))
        self.assertTrue(all(entry["exact_friends_phrase_occurrences"] == entry["exact_note_phrase_occurrences"] == 0 for entry in ranges))
        self.assertTrue(all(entry["absence_not_contradiction_when_snapshot_ends_before_labeled_hint"] for entry in ranges))

    def test_screenshot_sender_date_and_capture_are_separate_provenance(self):
        screenshot = self.document["screenshot"]
        self.assertEqual(screenshot["dimensions"], [525, 128])
        self.assertEqual(screenshot["visible_times"], ["06:51 PM", "06:51 PM"])
        self.assertFalse(screenshot["date_and_timezone_visible"])
        self.assertTrue(self.document["date_provenance"]["original_message_timestamp_unverified"])
        self.assertTrue(self.document["date_provenance"]["capture_time_not_original_publication"])

    def test_README_spelling_discrepancy_is_not_ignored_or_a_forgery_claim(self):
        discrepancy = self.document["sender_spelling_discrepancy"]
        self.assertEqual((discrepancy["screenshot"], discrepancy["README"]), ("Jrk Bgrt", "Jrk Bgrk"))
        self.assertTrue(discrepancy["typo_does_not_alone_disprove_screenshot_attribution"])

    def test_three_context_readings_do_not_name_operands_or_query_people(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertTrue(self.document["instruction_scope"]["best_chance_is_not_only_possible_solver_group"])
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"], self.document["personal_data_queries"]), (0, 0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "contextual-hint-provenance.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
