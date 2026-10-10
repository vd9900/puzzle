import json
import unittest

from tools.matrixsumlist_wording_audit import OUTPUT, report


class MatrixsumlistWordingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_creator_corpus_has_no_explicit_matrix_sum_or_axis_words(self):
        corpus = self.document["creator_corpus"]
        self.assertEqual(corpus["message_count"], 411)
        self.assertEqual(corpus["matrix_literal_count_before_decoding_binary_hints"], 0)
        self.assertEqual(corpus["sum_literal_count_before_decoding_binary_hints"], 0)
        self.assertTrue(all(value == 0 for value in corpus["axis_and_domain_counts_in_relevant_messages"].values()))

    def test_color_hint_names_domain_but_not_values_or_axis(self):
        record = next(item for item in self.document["relevant_records"] if item["id"] == "COLOR-FIRST-PIECE")
        self.assertIn("Yellow has a number and so does Blue.", record["record"]["body"])
        self.assertIn("Go back to the first puzzle piece", record["record"]["body"])
        self.assertIn("either number", record["does_not_establish"])
        self.assertIn("a sum axis", record["does_not_establish"])

    def test_prime_replies_do_not_confirm_values_or_matrix_entries(self):
        control = self.document["question_reply_controls"]
        self.assertEqual(control["elapsed_seconds"], 20)
        self.assertFalse(control["specific_values_confirmed"])
        later = next(item for item in self.document["relevant_records"] if item["id"] == "SUMList-PRIME-CONTEXT")
        self.assertEqual(later["elapsed_seconds"], 15223)
        self.assertFalse(later["reply_metadata_present"])
        self.assertIn("yes to prime-valued matrix entries", later["does_not_establish"])

    def test_rab_notation_is_available_but_unbound(self):
        record = next(item for item in self.document["relevant_records"] if item["id"] == "RAB-NUMERIC-NOTATION")
        self.assertEqual(record["elapsed_seconds"], 134)
        self.assertIn("R=18\nA=1\nB=2", record["creator_record"]["body"])
        self.assertIn("B/Y as matrix weights", record["does_not_establish"])

    def test_primary_formatting_supplies_order_without_grammar(self):
        formatting = self.document["formatting"]
        self.assertEqual(formatting["physical_order"], ["dbbi91", "matrixsumlist104", "faed570"])
        self.assertEqual(formatting["normalized_spans"], {"dbbi91": [0, 91], "matrixsumlist104": [91, 195], "faed570": [195, 765]})
        self.assertFalse(formatting["separator_before_label"])
        self.assertFalse(formatting["separator_after_label"])
        self.assertEqual(formatting["textarea_physical_nonempty_lines"], 1)
        self.assertFalse(formatting["textarea_supplies_matrix_rows"])
        self.assertFalse(formatting["official_hint_contains_explicit_arrows_verbs_axis_or_index_convention"])

    def test_all_three_bindings_remain_unknown(self):
        classification = self.document["classification"]
        self.assertEqual(classification["cell_domain"], "UNKNOWN")
        self.assertEqual(classification["numeric_interpretation"], "UNKNOWN")
        self.assertEqual(classification["summation_axis"], "UNKNOWN")
        self.assertIn("Do not promote", self.document["graph_effect"])

    def test_non_executing_scope_and_frozen_artifact(self):
        for field in ("new_pixel_operations", "new_numeric_combinations", "candidate_material_generated", "private_key_operations", "aes_operations"):
            self.assertEqual(self.document[field], 0)
        path = OUTPUT / "matrixsumlist-wording-audit.json"
        if path.exists():
            before = path.read_bytes()
            self.assertEqual(json.loads(before), self.document)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
