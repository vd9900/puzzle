import unittest

from tools.matrix_sum_interface import COLUMN_SUMS, ROW_SUMS, report


class MatrixSumInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_exact_sum_lists_and_conservation(self):
        observed = self.document["observed"]
        self.assertEqual(observed["column_sum_list"], COLUMN_SUMS)
        self.assertEqual(observed["row_sum_list"], ROW_SUMS)
        self.assertEqual(observed["conserved_total"], 478)
        self.assertTrue(observed["transpose_invariant"])

    def test_only_fifteen_value_direction_aligns_downstream(self):
        observed = self.document["observed"]
        self.assertTrue(observed["fifteen_value_list_matches_every_downstream_column_domain"])
        self.assertFalse(observed["thirteen_value_list_matches_any_downstream_axis"])
        self.assertTrue(all(shape[1] == 15 for shape in observed["downstream_shapes"].values()))

    def test_panel_information_accounting_closes(self):
        accounting = self.document["information_accounting"]
        self.assertEqual(accounting["residual_dbbi_cells"], 60)
        self.assertEqual(accounting["first23_event_expanded_dbbi_cells"], 31)
        self.assertEqual(accounting["final2_event_cells_in_raw_label"], 2)
        self.assertEqual(accounting["other_raw_label_cells"], 102)
        self.assertEqual(accounting["panel_cells_accounted"], accounting["panel_cells_expected"])
        self.assertTrue(accounting["all25_event_labels_represented"])

    def test_downstream_operation_remains_unknown(self):
        self.assertTrue(self.document["architecture_discriminator"]["how_list15_operates_on_downstream_columns"].startswith("UNKNOWN"))

    def test_non_executing_scope(self):
        self.assertEqual(self.document["new_cryptographic_trials"], 0)
        self.assertEqual(self.document["new_trial_inputs"], 0)
        self.assertEqual(self.document["private_key_operations"], 0)
        self.assertEqual(self.document["aes_operations"], 0)


if __name__ == "__main__":
    unittest.main()
