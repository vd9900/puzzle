import json
import unittest

from tools.instruction_graphs import ROOT
from tools.progress_ack_context import OUTPUT, report


class ProgressAckContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_sixteen_exact_context_bodies_reconstruct_original_bytes(self):
        records = self.document["context"]["records"]
        self.assertEqual(len(records), 16)
        payload = (ROOT / "research/evidence/cycle02/_work__chat_transcript.txt").read_bytes()
        for entry in records:
            start, end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual(payload[start:end], entry["public_body"].encode())
            self.assertFalse(entry["reply_target_metadata_preserved"])

    def test_two_creator_acknowledgements_and_timing_are_exact(self):
        context = self.document["context"]
        self.assertEqual(len(context["creator_bodies_cross_checked"]), 2)
        self.assertEqual(context["third_door_question_to_acknowledgement_seconds"], 110)
        self.assertEqual(context["acknowledgement_to_hardest_statement_seconds"], 34)
        self.assertEqual([entry["creator_record"]["line_one_based"] for entry in context["creator_bodies_cross_checked"]], [757, 760])

    def test_separate_community_method_mentions_are_not_one_confirmed_recipe(self):
        records = self.document["context"]["records"]
        self.assertEqual([entry["public_body"] for entry in records[1:4]], ["Matrix and prime numbers", "Double hash", "And… nothing"])
        self.assertTrue(self.document["context"]["no_cipher_recipe_output_or_named_operand_in_fixed_window"])
        self.assertTrue(self.document["context"]["flat_export_order_does_not_recover_reply_targets"])

    def test_prior_question_and_checkpoint_constraints_are_reused(self):
        self.assertTrue(self.document["earlier_question_reused"]["no_btc_question_retested_or_reinterpreted_as_Bifid_confirmation"])
        self.assertTrue(self.document["checkpoint_reused"]["no_specific_container_binding_derived"])

    def test_three_scopes_have_fields_without_algorithm_promotion(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in hypotheses))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "progress-acknowledgement.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
