import unittest

from tools.matrix_operator_feasibility import report


class MatrixOperatorFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_all_direct_interpretations_fail(self):
        observed = self.document["observed"]
        self.assertEqual(observed["direct_interpretations_passing"], 0)
        self.assertTrue(all(not check["valid"] for check in observed["direct_checks"].values()))

    def test_permutation_is_out_of_range_and_nonunique(self):
        for name in ("column_permutation_zero_based", "column_permutation_one_based"):
            check = self.document["observed"]["direct_checks"][name]
            self.assertFalse(check["valid"])
            self.assertFalse(check["all_distinct"])
        self.assertEqual(self.document["observed"]["duplicate_values"], [6, 13])

    def test_selection_and_partition_domains_fail(self):
        checks = self.document["observed"]["direct_checks"]
        self.assertEqual(checks["partition_full_faed"]["observed_total"], 478)
        self.assertFalse(checks["partition_full_faed"]["valid"])
        self.assertFalse(checks["partition_one_faed_half"]["valid"])
        self.assertEqual(checks["one_row_per_faed_column_zero_based"]["failing_offsets_zero_based"], list(range(7)))

    def test_surviving_family_is_explicitly_unknown(self):
        self.assertEqual(self.document["classification"]["normalized_or_arithmetic_consumer"], "UNKNOWN")
        self.assertEqual(len(self.document["missing_parameters"]), 5)

    def test_creator_record_has_no_literal_operator_binding(self):
        scan = self.document["source_language_constraints"]["creator_export_literal_scan"]
        self.assertEqual(scan["messages"], 411)
        self.assertTrue(all(count == 0 for count in scan["keyword_counts"].values()))

    def test_non_executing_scope(self):
        self.assertEqual(self.document["new_cryptographic_trials"], 0)
        self.assertEqual(self.document["new_trial_inputs"], 0)
        self.assertEqual(self.document["private_key_operations"], 0)
        self.assertEqual(self.document["aes_operations"], 0)


if __name__ == "__main__":
    unittest.main()
