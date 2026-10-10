import json
import unittest

from tools.door_reference_audit import OUTPUT, report
from tools.instruction_graphs import ROOT


class DoorReferenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_three_brace_groups_preserve_source_spacing_and_date_match(self):
        records = self.document["records"]
        document = (ROOT / "research/evidence/cycle02/_work__creator_jrk.txt").read_text()
        self.assertEqual([entry["literal"] for entry in records["brace_groups"]], ["{1 }", "{4}", "{21}"])
        for entry in records["brace_groups"]:
            start, end = entry["character_span_zero_based_half_open"]
            self.assertEqual(document[start:end], entry["literal"])
        self.assertEqual(records["archived_UTC_date"], "2021-04-01")
        self.assertTrue(records["brace_values_match_archived_day_month_shortyear"])

    def test_distinct_rab_message_is_not_the_door_hint(self):
        records = self.document["records"]
        self.assertEqual(records["seconds_door_to_rab"], 23523)
        self.assertEqual(records["creator_record"]["line_one_based"], 534)
        self.assertEqual(records["rab_creator_record"]["line_one_based"], 540)
        self.assertTrue(records["same_bodies_in_both_exports"])
        self.assertTrue(records["rab_message_is_distinct_not_same_hint"])

    def test_screenshot_and_timezone_limits_are_explicit(self):
        screenshot = self.document["screenshot"]
        self.assertEqual(screenshot["dimensions"], [516, 164])
        self.assertTrue(screenshot["does_not_display_braced_door_hint"])
        self.assertTrue(screenshot["time_display_timezone_not_encoded"])
        self.assertTrue(screenshot["secondary_filename_april_fool_is_not_creator_authentication"])

    def test_context_does_not_define_selector_or_dismiss_hint_as_joke(self):
        records = self.document["records"]
        self.assertEqual(len(records["context"]), 4)
        self.assertTrue(all(not entry["reply_target_metadata_preserved"] for entry in records["context"]))
        self.assertTrue(records["December2021_reiteration_rules_out_dismissing_door_only_as_a_joke"])
        self.assertTrue(records["reiteration_does_not_select_date_coordinates_or_indexing"])

    def test_three_hypotheses_are_bounded_and_have_required_fields(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 3)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertEqual(self.document["search_space"]["new_index_or_route_trials"], 0)
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "door-reference-audit.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    main()
