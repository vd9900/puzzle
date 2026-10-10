import json
import unittest

from tools.checkpoint_referents import ARTIFACT_NAME, CREATOR, OUTPUT, exact_checkpoint_records, literal_occurrences, next_phase_context, report


class CheckpointReferentTests(unittest.TestCase):
    def test_exact_original_records_and_phrase_maps(self):
        document = CREATOR.read_text()
        records = exact_checkpoint_records()
        self.assertEqual(len(records), 3)
        for record in records:
            start, end = record["quote_location"]["character_span_zero_based_half_open"]
            self.assertEqual(document[start:end], record["exact_public_quote"])
            self.assertFalse(record["reply_target_metadata_preserved"])
        self.assertEqual([record["quote_location"]["line_one_based"] for record in records], [804, 1186, 1198])

    def test_repeated_spelling_in_one_message_is_not_independent_evidence(self):
        inventory = literal_occurrences()
        literal = inventory["terms"]["yingyang"]
        self.assertEqual((literal["exact_word_occurrences"], literal["distinct_original_messages"]), (2, 1))
        self.assertEqual(inventory["terms"]["ying yang"]["distinct_original_messages"], 1)
        self.assertEqual(inventory["terms"]["yinyang"]["exact_word_occurrences"], 0)
        self.assertEqual(inventory["terms"]["SMALL"]["exact_word_occurrences"], 0)
        self.assertEqual(inventory["terms"]["small"]["exact_word_occurrences"], 1)
        self.assertEqual(inventory["terms"]["SMALL"]["case_matching"], "CASE_SENSITIVE")
        self.assertTrue(inventory["no_semantic_or_creator_authentication_claim_from_counts"])

    def test_context_does_not_invent_a_reply_binding(self):
        context = next_phase_context()
        self.assertEqual(context["elapsed_question_to_response_seconds"], 84)
        self.assertEqual(context["intervening_messages"], 3)
        self.assertEqual([entry["relative_message_index"] for entry in context["window"]], [-4, -3, -2, -1, 0, 1])
        self.assertTrue(context["no_authenticated_reply_binding"])
        self.assertTrue(context["no_container_identified_by_the_question_or_response"])

    def test_all_three_hypotheses_have_required_fields_and_typed_edges(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 3)
        for hypothesis in document["hypotheses"]:
            self.assertTrue(required <= hypothesis.keys())
            self.assertEqual(hypothesis["status"], "INCONCLUSIVE")
            graph = document["data_flow_graphs"][hypothesis["id"]]
            self.assertTrue(all(start in graph["nodes"] and end in graph["nodes"] and kind.startswith("HYPOTHESIS") for start, end, kind in graph["edges"]))

    def test_no_literal_requirement_or_container_is_promoted_to_fact(self):
        document = report()
        self.assertFalse(document["primary_small_literal_present"])
        self.assertEqual([entry["text"] for entry in document["primary_headings"]], ["SalPhaseIon", "Cosmic Duality"])
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))
        self.assertIn("not an established necessary gate", document["eliminated_requirement"])

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / ARTIFACT_NAME
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
