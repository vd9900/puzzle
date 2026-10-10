import json
import unittest

from tools.final_reference_audit import OUTPUT, report


class FinalReferenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_three_final_clauses_keep_exact_preserved_positions(self):
        clauses = self.document["clauses"]
        self.assertEqual([entry["decoded_span_zero_based_half_open"] for entry in clauses["clauses"]], [[62, 87], [87, 126], [126, 161]])
        self.assertTrue(clauses["password_is_lexically_named_before_it"])
        self.assertTrue(clauses["it_has_no_explicit_page_image_or_stage_name"])
        self.assertTrue(clauses["no_hint_binary_decoding_repeated"])

    def test_image_locators_are_not_selections_or_identifier_use(self):
        regions = self.document["visible_regions"]
        self.assertEqual(regions["original_dimensions"], [1048, 1556])
        self.assertEqual(len(regions["human_visual_region_locators"]), 3)
        self.assertTrue(regions["locators_are_not_exact_OCR_boxes_or_selection_masks"])
        self.assertTrue(regions["no_qr_or_identifier_decoding_matching_or_use"])
        self.assertFalse(regions["current_primary_literal_SMALL"])

    def test_secondary_entry_route_does_not_define_final_argument(self):
        interpretation = self.document["secondary_entry_interpretation"]
        self.assertEqual(interpretation["source_location"]["line_one_based"], 158)
        self.assertTrue(interpretation["an_earlier_entry_route_does_not_identify_a_later_selected_object"])
        self.assertTrue(interpretation["earlier_audio_command_argument_not_encoded"])

    def test_separate_creator_question_does_not_confirm_bifid(self):
        question = self.document["separate_question"]
        self.assertEqual(question["creator_record"]["line_one_based"], 745)
        self.assertTrue(question["does_not_literally_name_Bifid_residual_or_btcseed"])
        self.assertTrue(question["separate_date_and_wording_not_the_final_hint_clause"])

    def test_three_hypotheses_have_fields_without_extracted_material(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 3)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertEqual(self.document["search_space"]["new_pixel_or_text_selections"], 0)
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "final-reference-audit-v2.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)
        self.assertTrue((OUTPUT / "final-reference-audit.json").exists())


if __name__ == "__main__":
    unittest.main()
