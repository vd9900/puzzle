import unittest

from tools.matrix_width_interface import report


class MatrixWidthInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_label_and_dbbi_form_exact_panel(self):
        interface = self.document["label_interface"]
        self.assertEqual((interface["joined_rows"], interface["joined_columns"]), (13, 15))
        self.assertTrue(interface["all_label_bytes_reconstructed"])
        self.assertTrue(interface["dbbi_round_trip"])
        self.assertTrue(interface["raw_label_round_trip"])

    def test_faed_halves_form_cellwise_bifid_panels(self):
        interface = self.document["faed_bifid_interface"]
        self.assertEqual((interface["faed_rows"], interface["faed_columns"]), (38, 15))
        self.assertEqual(interface["even_coordinate_plane_shape"], [19, 15])
        self.assertEqual(interface["odd_coordinate_plane_shape"], [19, 15])
        self.assertEqual(interface["cellwise_pairs_checked"], 285)
        self.assertEqual(interface["cellwise_pairs_matching"], 285)
        self.assertTrue(interface["faed_round_trip"])
        self.assertTrue(interface["bifid_interleave_round_trip"])

    def test_prefix_is_a_complete_seven_cell_field(self):
        boundary = self.document["prefix_boundary"]
        self.assertEqual(boundary["left_field"], "btcseed")
        self.assertEqual((boundary["left_field_width"], boundary["right_field_width"]), (7, 8))
        self.assertEqual(boundary["remaining_body_length"], 563)
        self.assertEqual(boundary["remaining_full_rows"], 37)
        self.assertTrue(boundary["body_decomposition_exact"])
        self.assertTrue(boundary["linear_cut_splits_a_bifid_digraph"])

    def test_non_executing_scope(self):
        self.assertEqual(self.document["new_cryptographic_trials"], 0)
        self.assertEqual(self.document["new_trial_inputs"], 0)
        self.assertEqual(self.document["private_key_operations"], 0)
        self.assertEqual(self.document["aes_operations"], 0)

    def test_requested_edges_are_classified(self):
        edges = self.document["requested_edge_classification"]
        self.assertEqual(len(edges), 8)
        self.assertEqual(
            [entry["classification"] for entry in edges],
            ["UNKNOWN", "WEAK", "STRONGLY SUPPORTED", "UNKNOWN", "STRONGLY SUPPORTED", "VERIFIED", "UNKNOWN", "UNKNOWN"],
        )


if __name__ == "__main__":
    unittest.main()
