import unittest

from tools.matrix_marginal_identity import report


class MatrixMarginalIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_upstream_list_is_two_typed_fields(self):
        typed = self.document["upstream_type_analysis"]
        self.assertEqual(typed["left_field"]["column_sums"] + typed["right_field"]["column_sums"], typed["sum_list"])
        self.assertEqual((typed["left_field"]["width"], typed["right_field"]["width"]), (7, 8))
        self.assertFalse(typed["common_numeric_scale_authored"])

    def test_ascii_high_bit_explains_zero_column(self):
        field = self.document["upstream_type_analysis"]["right_field"]
        self.assertEqual(field["column_sums"][0], 0)
        self.assertEqual(field["zero_column_offset_within_field"], 0)

    def test_all_canonical_marginal_identities_fail(self):
        tested = self.document["downstream_marginal_test"]
        self.assertEqual(tested["signatures_checked"], 36)
        self.assertEqual(tested["ordered_exact_matches"], [])
        self.assertEqual(tested["reorder_only_multiset_matches"], [])

    def test_bifid_coordinate_conservation_positive_controls_pass(self):
        self.assertTrue(all(self.document["verified_bifid_conservation"].values()))

    def test_graph_edge_is_narrowly_rejected(self):
        classification = self.document["classification"]
        self.assertEqual(classification["direct_downstream_coordinate_marginal"], "REJECTED")
        self.assertEqual(classification["parameterized_downstream_operation"], "UNKNOWN")

    def test_non_executing_scope(self):
        self.assertEqual(self.document["new_cryptographic_trials"], 0)
        self.assertEqual(self.document["new_trial_inputs"], 0)
        self.assertEqual(self.document["private_key_operations"], 0)
        self.assertEqual(self.document["aes_operations"], 0)


if __name__ == "__main__":
    unittest.main()
