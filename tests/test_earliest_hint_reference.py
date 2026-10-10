import json
import unittest

from tools.earliest_hint_reference import OUTPUT, report
from tools.instruction_graphs import ROOT


class EarliestHintReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_earliest_exact_phrase_has_community_not_creator_provenance(self):
        earliest = self.document["earliest_rabbit"]
        self.assertEqual(earliest["case_insensitive_exact_phrase_occurrences_in_preserved_chat"], 111)
        self.assertEqual(earliest["earliest_record"]["header"], "=== [20.04.2019 02:18:49 UTC-05:00] Ewout")
        self.assertEqual(earliest["earliest_record"]["line_one_based"], 32)
        self.assertTrue(earliest["earliest_reference_is_a_community_question_not_creator_instruction"])
        self.assertTrue(earliest["earliest_preserved_occurrence_is_not_original_publication_date"])

    def test_rabbit_question_precedes_first_code_acknowledgement(self):
        earliest = self.document["earliest_rabbit"]
        self.assertEqual(earliest["rabbit_reference_precedes_code_acknowledgement_seconds"], 32400)
        acknowledgement = earliest["first_code_acknowledgement"]
        self.assertEqual(acknowledgement["creator_record"]["line_one_based"], 2)
        self.assertEqual(acknowledgement["original_chat_record"]["line_one_based"], 107)

    def test_fixed_secondary_anchors_reconstruct_exact_source_bytes(self):
        anchors = self.document["secondary_attributions"]
        self.assertEqual(len(anchors), 3)
        for entry in anchors:
            path = ROOT / entry["source"]["path"]
            start, end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual(path.read_bytes()[start:end], entry["literal"].encode())
        self.assertIn("something along the lines", anchors[1]["literal"])

    def test_existing_command_and_piece_context_are_reused_without_operand(self):
        commands = self.document["commands_reused"]
        self.assertEqual([entry["literal"] for entry in commands["subphrases"]], ["shabef", "ourfirsthintisyourlastcommand", "shabef", "anstoo"])
        self.assertTrue(commands["no_decoding_or_segment_variants"])
        context = self.document["First_zero_context_reused"]
        self.assertTrue(context["original_piece_return_supported"])
        self.assertTrue(context["no_index_origin_or_literal_hint_operand_derived"])

    def test_three_referent_roles_have_fields_without_new_trial_material(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in hypotheses))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "earliest-hint-reference.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
