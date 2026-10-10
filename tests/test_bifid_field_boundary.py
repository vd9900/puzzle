import unittest

from tools.bifid_field_boundary import report


class BifidFieldBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_recognized_prefix_cut_splits_one_digraph(self):
        first = self.document["first_row"]
        self.assertEqual(first["left7"], "btcseed")
        self.assertEqual(first["global_cut_offset"], 7)
        self.assertEqual(first["source_pair_overlap"], [3])
        self.assertEqual(first["shared_faed_offsets"], [3, 288])

    def test_field_behavior_alternates_across_rendered_rows(self):
        rows = self.document["all_rendered_rows"]
        self.assertEqual(rows["split_digraph_boundaries"], 19)
        self.assertEqual(rows["between_digraph_boundaries"], 19)
        self.assertEqual(rows["split_rows_zero_based"], list(range(0, 38, 2)))
        self.assertEqual(rows["between_rows_zero_based"], list(range(1, 38, 2)))

    def test_coordinate_planes_do_not_contain_prefix_as_first_field(self):
        control = self.document["coordinate_plane_control"]
        self.assertEqual(control["even_plane_shape"], [19, 15])
        self.assertEqual(control["odd_plane_shape"], [19, 15])
        self.assertFalse(control["either_plane_first7_is_btcseed"])

    def test_direct_field_preservation_is_rejected(self):
        classification = self.document["classification"]
        self.assertEqual(classification["btcseed_as_serialized_prefix"], "VERIFIED")
        self.assertEqual(classification["btcseed_as_independent_seven_column_bifid_field"], "REJECTED")
        self.assertEqual(classification["upstream_7_plus_8_to_downstream_7_plus_8_data_flow"], "REJECTED for direct field preservation")

    def test_non_executing_scope(self):
        self.assertEqual(self.document["new_cryptographic_trials"], 0)
        self.assertEqual(self.document["new_trial_inputs"], 0)
        self.assertEqual(self.document["private_key_operations"], 0)
        self.assertEqual(self.document["aes_operations"], 0)


if __name__ == "__main__":
    unittest.main()
