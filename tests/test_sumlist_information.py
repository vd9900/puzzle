import json
import unittest

from tools.sumlist_information import OUTPUT, rectangle_witnesses, report


class SumlistInformationTests(unittest.TestCase):
    def test_binary_rectangle_certificate_preserves_both_axes(self):
        result = rectangle_witnesses([[1, 0], [0, 1]], set())
        self.assertEqual(result["ambiguity_certificates"], 1)
        self.assertEqual(result["first_deterministic_certificate"]["symbolic_balance_deltas"], [-1, 1, 1, -1])

    def test_protected_cells_and_nonbinary_values_prevent_this_certificate(self):
        self.assertEqual(rectangle_witnesses([[1, 0], [0, 1]], {(0, 0)})["ambiguity_certificates"], 0)
        self.assertEqual(rectangle_witnesses([[2, 0], [0, 2]], set())["ambiguity_certificates"], 0)
        self.assertTrue(rectangle_witnesses([[1, 1], [0, 0]], set())["no_witness_does_not_prove_uniqueness"])

    def test_malformed_domains_rejected(self):
        for matrix, protected in (([[1, 0], [0]], set()), ([[1, -1], [0, 1]], set()), ([[1, 0], [0, 1]], {(2, 0)})):
            with self.assertRaises(ValueError):
                rectangle_witnesses(matrix, protected)

    def test_original_source_has_narrow_losslessness_counterexample(self):
        document = report()
        self.assertEqual(document["status"], "REJECTED")
        self.assertEqual(document["certificate"]["rectangles_checked"], 8281)
        self.assertGreater(document["certificate"]["ambiguity_certificates"], 0)
        self.assertTrue(document["certificate"]["no_changed_matrix_or_image_constructed"])
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"], document["new_image_variants"]), (0, 0, 0))

    def test_frozen_result_is_reproducible(self):
        self.assertEqual(json.loads((OUTPUT / "sumlist-information.json").read_text()), report())


if __name__ == "__main__":
    unittest.main()
