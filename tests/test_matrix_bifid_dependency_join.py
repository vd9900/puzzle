import unittest

from tools.matrix_bifid_dependency_join import report


class MatrixBifidDependencyJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_upstream_panel_is_exact_but_typed(self):
        panel = self.document["upstream_panel"]
        self.assertEqual(panel["shape"], [13, 15])
        self.assertEqual(panel["dbbi_columns_zero_based"], list(range(7)))
        self.assertEqual(panel["raw_label_bit_columns_zero_based"], list(range(7, 15)))
        self.assertTrue(panel["rowwise_join_round_trip"])

    def test_square_uses_first_occurrences_from_six_dbbi_columns(self):
        square = self.document["square_dependency"]
        self.assertEqual(square["observed_first_occurrence_symbols"], "dbifhcega")
        self.assertEqual(square["dbbi_panel_columns_contributing_first_occurrences_zero_based"], list(range(6)))
        self.assertEqual(square["dbbi_panel_columns_without_first_occurrence_zero_based"], [6])
        self.assertEqual(square["fixed_alphabet_supplement_count"], 16)

    def test_every_downstream_group_uses_all_faed_symbols(self):
        summary = self.document["dependency_summary"]
        self.assertEqual(summary["groups"], 15)
        self.assertEqual(summary["groups_with_all_nine_faed_input_symbols"], 15)
        self.assertEqual(summary["groups_with_exact_local_faed_column_lineage"], 15)

    def test_global_key_dependency_is_not_diagonal_panel_flow(self):
        summary = self.document["dependency_summary"]
        self.assertEqual(summary["distinct_global_dbbi_key_column_patterns"], 1)
        self.assertEqual(summary["shared_global_dbbi_key_columns_zero_based"], list(range(6)))
        self.assertEqual(summary["groups_with_exclusive_same_index_upstream_panel_dependency"], 0)

    def test_label_bits_are_not_bifid_inputs(self):
        self.assertEqual(self.document["dependency_summary"]["groups_with_any_raw_label_bit_dependency"], 0)
        self.assertTrue(self.document["classification"]["raw_matrixsumlist_bits_to_bifid_transform"].startswith("REJECTED"))

    def test_non_executing_scope(self):
        for field in (
            "numeric_sum_vectors_calculated",
            "numeric_mapping_trials",
            "candidate_lists_generated",
            "mnemonic_words_generated",
            "checksum_tests",
            "seed_derivations",
            "private_key_operations",
            "aes_operations",
        ):
            self.assertEqual(self.document[field], 0)


if __name__ == "__main__":
    unittest.main()
