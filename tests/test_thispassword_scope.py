import json
import unittest

from tools.instruction_graphs import ROOT
from tools.thispassword_scope import OUTPUT, report


class ThisPasswordScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_three_primary_units_have_character_not_word_spacing(self):
        grammar = self.document["primary_grammar"]
        self.assertEqual(len(grammar["segments"]), 3)
        self.assertTrue(all(entry["encoded_character_spacing_is_not_decoded_word_spacing"] for entry in grammar["segments"]))
        self.assertTrue(all(not entry["literal_assignment_punctuation_present"] for entry in grammar["segments"]))
        self.assertTrue(grammar["decoded_phrase1_phrase2_are_separate_z_delimited_units"])

    def test_subphrases_preserve_complete_local_sha_prefix(self):
        subphrases = self.document["primary_grammar"]["command_subphrases"]
        self.assertEqual([entry["literal"] for entry in subphrases], ["shabef", "ourfirsthintisyourlastcommand", "shabef", "anstoo"])
        self.assertTrue(self.document["primary_grammar"]["first_command_begins_with_complete_shabef_not_four"])

    def test_five_secondary_passages_map_exact_source_and_list_positions(self):
        document = (ROOT / "research/sources/community-README.md").read_text()
        passages = self.document["secondary_grammar"]["mapped_passages"]
        self.assertEqual(len(passages), 5)
        for entry in passages:
            start, end = entry["character_span_zero_based_half_open"]
            self.assertEqual(document[start:end], entry["literal"])
        self.assertEqual([entry["line_one_based"] for entry in passages], [381, 381, 390, 391, 393])
        self.assertTrue(self.document["secondary_grammar"]["listed_labels_do_not_define_antecedent_or_recipe_scope"])

    def test_two_scopes_retain_missing_syntax_and_are_not_a_dictionary(self):
        hypotheses = self.document["hypotheses"]
        self.assertEqual([entry["scope"] for entry in hypotheses], ["BACKWARD_RESULT", "FORWARD_RECIPE_LABEL"])
        self.assertTrue(all(len(entry["missing_grammar"]) == 3 for entry in hypotheses))
        self.assertFalse(self.document["unique_scope_established"])
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))
        self.assertEqual(self.document["search_space"]["new_extractions"], 0)

    def test_all_hypothesis_fields_are_preserved(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in self.document["hypotheses"]))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "thispassword-scope.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
