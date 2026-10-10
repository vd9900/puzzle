import json
import unittest

from tools.instruction_graphs import ROOT
from tools.phase_name_semantics import OUTPUT, report


class PhaseNameSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_creator_body_and_three_clauses_are_exact(self):
        record = self.document["creator_name_record"]
        self.assertEqual(record["creator_record"]["line_one_based"], 510)
        self.assertEqual(record["original_chat_record"]["line_one_based"], 15661)
        self.assertEqual(record["salphation_spelling_occurrences_in_this_record"], 2)
        self.assertEqual(len(record["clauses"]), 3)
        payload = (ROOT / record["creator_record"]["source"]["path"]).read_bytes()
        for entry in record["clauses"]:
            start, end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual(payload[start:end], entry["literal"].encode())

    def test_primary_headings_are_exact_not_generated_names(self):
        headings = self.document["primary_headings"]
        self.assertEqual([entry["literal"] for entry in headings], ["<h1> SalPhaseIon </h1>", "<h1> Cosmic Duality </h1>"])
        self.assertEqual([entry["line_one_based"] for entry in headings], [16, 19])

    def test_screenshot_identity_does_not_supply_timezone_or_extraction(self):
        screenshot = self.document["screenshot"]
        self.assertEqual(screenshot["dimensions"], [552, 349])
        self.assertTrue(screenshot["displayed_0345AM_timezone_not_given"])
        self.assertTrue(screenshot["locator_not_OCR_or_text_selection_rule"])

    def test_secondary_salvation_is_mapped_without_primary_promotion(self):
        entry = self.document["secondary_salvation"]
        start, end = entry["utf8_byte_span_zero_based_half_open"]
        self.assertEqual((ROOT / entry["source"]["path"]).read_bytes()[start:end], entry["literal"].encode())
        self.assertEqual(entry["literal"].lower(), "salvation")
        self.assertEqual(entry["classification"], "COMMUNITY_MOVIE_QUOTATION_NOT_PRIMARY_PUZZLE_TEXT")
        self.assertTrue(self.document["secondary_passage_not_substituted_for_verified_speech"])

    def test_three_role_readings_do_not_create_literal_gate_or_name_variants(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertTrue(self.document["checkpoint_reused"]["no_checkpoint_or_cover_experiment_repeated"])
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"], self.document["new_name_variants"]), (0, 0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "phase-name-semantics.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
