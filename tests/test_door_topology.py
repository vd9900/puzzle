import json
import unittest

from tools.door_topology import OUTPUT, report
from tools.instruction_graphs import ROOT


class DoorTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_three_dated_records_and_four_phrase_anchors_are_exact(self):
        records = self.document["chronology"]["records"]
        self.assertEqual(len(records), 3)
        self.assertEqual([entry["creator_record"]["line_one_based"] for entry in records], [195, 363, 411])
        document = (ROOT / "research/evidence/cycle02/_work__creator_jrk.txt").read_text()
        self.assertEqual(sum(len(entry["phrase_maps"]) for entry in records), 4)
        for record in records:
            for entry in record["phrase_maps"]:
                start, end = entry["character_span_zero_based_half_open"]
                self.assertEqual(document[start:end], entry["literal"])

    def test_topology_count_and_source_domain_remain_unknown(self):
        chronology = self.document["chronology"]
        self.assertTrue(chronology["whole_lot_more_is_not_an_exact_door_count"])
        self.assertTrue(chronology["second_and_extra_are_not_explicitly_equal_references"])
        self.assertTrue(chronology["first_piece_is_named_but_the_word_matrix_is_not_in_the_warning"])
        self.assertTrue(chronology["no_index_origin_or_traversal_defined"])

    def test_complete_warning_screenshot_identity_and_locator(self):
        screenshot = self.document["warning_screenshot"]
        self.assertEqual(screenshot["dimensions"], [574, 262])
        self.assertTrue(screenshot["complete_warning_visible_not_only_three_color_lines"])
        self.assertTrue(screenshot["visible_warning_below_first_piece_return_instruction"])
        self.assertTrue(screenshot["locator_not_OCR_or_source_selection_rule"])

    def test_three_topology_readings_have_fields_and_no_derived_entrance(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertEqual([len(entry["edges"]) for entry in hypotheses], [2, 2, 1])
        self.assertEqual(self.document["search_space"]["new_alternate_entry_trials"], 0)

    def test_later_door_relevance_is_reused_without_numeric_trials(self):
        reused = self.document["later_door_source_reused"]
        self.assertTrue(reused["December_reiteration_preserves_relevance"])
        self.assertTrue(reused["no_numeric_door_interpretation_retested"])
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "door-topology.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
