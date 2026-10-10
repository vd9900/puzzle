import unittest

from tools.residual_faed_topology import report


class ResidualFaedTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_residual_tiles_but_does_not_preserve_source_axis(self):
        preflight = self.document["residual_width15_preflight"]
        self.assertEqual(preflight["shape"], [4, 15])
        axes = preflight["source_axis_checks"]
        self.assertEqual(axes["original_raw15_constant_target_columns"], [])
        self.assertEqual(axes["logical_domain15_constant_target_columns"], [])
        self.assertEqual(axes["original_dbbi7_constant_target_columns"], [14])

    def test_no_direct_whole_or_row_identity(self):
        preflight = self.document["residual_width15_preflight"]
        self.assertTrue(all(offset == -1 for offset in preflight["whole_residual_substring_offsets_minus_one_means_absent"].values()))
        self.assertTrue(all(not matches for matches in preflight["exact_downstream_row_matches"].values()))

    def test_residual_event_branch_reaches_exact_square(self):
        dependency = self.document["convergent_dependency"]
        self.assertEqual(dependency["residual_tokens"], 60)
        self.assertEqual(dependency["event_labels_used_to_reconstruct_dbbi"], 23)
        self.assertEqual(dependency["reconstructed_dbbi_letters"], 91)
        self.assertEqual(dependency["square_first_occurrences_owned_by_residual"], 7)
        self.assertEqual(dependency["square_first_occurrences_owned_by_events"], 2)
        self.assertTrue(dependency["derived_square_matches_used_square"])

    def test_faed_is_independent_bifid_input(self):
        dependency = self.document["convergent_dependency"]
        self.assertEqual(dependency["faed_symbols_consumed"], 570)
        self.assertEqual(dependency["bifid_symbols_produced"], 570)
        self.assertTrue(dependency["bifid_round_trip"])
        self.assertEqual(dependency["raw_label_bits_consumed_by_current_bifid_graph"], 0)

    def test_architecture_discriminator(self):
        discriminator = self.document["architecture_discriminator"]
        self.assertTrue(discriminator["serial_residual_to_faed"].startswith("WEAK"))
        self.assertTrue(discriminator["parallel_convergence_at_bifid"].startswith("STRONGLY SUPPORTED"))

    def test_non_executing_scope(self):
        self.assertEqual(self.document["new_cryptographic_trials"], 0)
        self.assertEqual(self.document["new_trial_inputs"], 0)
        self.assertEqual(self.document["private_key_operations"], 0)
        self.assertEqual(self.document["aes_operations"], 0)


if __name__ == "__main__":
    unittest.main()
