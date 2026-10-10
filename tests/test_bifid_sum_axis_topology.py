import unittest

from tools.bifid_sum_axis_topology import report


class BifidSumAxisTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_both_architectures_have_fifteen_complete_groups(self):
        shapes = self.document["fixed_shapes"]
        self.assertEqual(shapes["groups_per_architecture"], 15)
        self.assertEqual(shapes["symbols_per_group"], 38)
        topology = self.document["dependency_topology"]
        self.assertEqual(topology["plane_paired_output_coverage"], 570)
        self.assertEqual(topology["rendered_output_coverage"], 570)

    def test_plane_pairing_preserves_each_source_column(self):
        topology = self.document["dependency_topology"]
        self.assertEqual(topology["plane_paired_single_source_column_groups"], 15)
        self.assertEqual(
            topology["plane_paired_source_columns_zero_based"],
            [[column] for column in range(15)],
        )

    def test_serialized_columns_mix_source_columns(self):
        topology = self.document["dependency_topology"]
        self.assertEqual(topology["rendered_single_source_column_groups"], 0)
        self.assertEqual(topology["rendered_two_source_column_groups"], 15)

    def test_post_bifid_groups_are_not_formal_repeats(self):
        comparisons = self.document["formal_additive_comparison"]["comparisons"]
        self.assertEqual(len(comparisons), 5)
        for comparison in comparisons.values():
            self.assertEqual(comparison["ordered_equal_groups"], 0)
            self.assertEqual(comparison["all_pair_equal_groups"], 0)
            self.assertFalse(comparison["whole_vector_multiset_equal"])

    def test_graph_prefers_dependency_preserving_axis(self):
        architecture = self.document["architecture_discriminator"]
        self.assertTrue(architecture["serialized_38x15_column_reduction"].startswith("WEAK"))
        self.assertTrue(architecture["coordinate_plane_paired_column_reduction"].startswith("STRONGLY SUPPORTED"))
        self.assertTrue(architecture["prior_raw_faed_sum_campaign_equivalence"].startswith("REJECTED"))

    def test_non_executing_scope(self):
        self.assertEqual(self.document["formal_additive_comparison"]["numeric_sum_vectors_calculated"], 0)
        self.assertEqual(self.document["formal_additive_comparison"]["numeric_mapping_trials"], 0)
        for field in (
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
