import json
import unittest

from tools.source_binding_audit import CREATOR, OUTPUT, context_evidence, original_records, report


class SourceBindingAuditTests(unittest.TestCase):
    def test_original_phrase_maps_and_corresponding_exports(self):
        document = CREATOR.read_text()
        records = original_records()
        self.assertEqual(len(records), 6)
        self.assertEqual([record["creator_labeled_export"]["line_one_based"] for record in records], [195, 375, 486, 489, 627, 672])
        for record in records:
            for phrase in record["phrases"]:
                start, end = phrase["character_span_zero_based_half_open"]
                self.assertEqual(document[start:end], phrase["literal"])
            self.assertTrue(record["matching_exports_are_not_independent_authentication"])

    def test_first_zero_refers_to_piece_context_not_defined_indexing(self):
        context = context_evidence()["first_or_zero"]
        self.assertEqual(context["question_to_response_seconds"], 3270)
        self.assertEqual(len(context["window"]), 4)
        self.assertEqual(context["best_supported_referent"], "first/zero puzzle-piece numbering")
        self.assertTrue(context["not_a_defined_array_origin_or_bit_operator"])

    def test_community_prime_values_are_not_creator_parameters(self):
        context = context_evidence()["prime_part"]
        self.assertEqual(context["question_to_prime_response_seconds"], 20)
        self.assertEqual(len(context["window"]), 7)
        self.assertTrue(context["confirms_prime_relevance_not_the_community_prime_values"])

    def test_generic_importance_does_not_confirm_prime_valued_sums(self):
        context = context_evidence()["sumlist_response"]
        self.assertEqual(context["question_to_response_seconds"], 15223)
        self.assertEqual(len(context["window"]), 2)
        self.assertTrue(context["generic_prime_importance_not_a_yes_to_prime_valued_sumlist"])

    def test_zeroing_reinsertion_and_operand_constraints_are_not_conflated(self):
        document = report()
        constraints = document["operation_constraints"]
        self.assertTrue(constraints["prime_relevance_explicit"])
        self.assertTrue(constraints["some_character_zeroing_explicit"])
        for key in ("zeroing_means_deletion", "zeroing_equals_inverse_of_reinsertion", "same_operand_or_site", "reinsertion_site"):
            self.assertEqual(constraints[key], "NOT_SPECIFIED")
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))

    def test_finite_hypotheses_have_required_fields(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 3)
        self.assertTrue(all(required <= hypothesis.keys() for hypothesis in document["hypotheses"]))
        self.assertEqual(document["search_space"]["context_messages"], 13)

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "source-binding-audit.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
