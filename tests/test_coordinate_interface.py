import json
import unittest

from tools.coordinate_interface import OUTPUT, direct_coordinate_membership, label_information, report


class CoordinateInterfaceTests(unittest.TestCase):
    def test_complete_same_domain_bijection(self):
        coordinates = [(row, column) for row in range(2) for column in range(2)]
        self.assertTrue(direct_coordinate_membership(coordinates, 2)["direct_bijection"])

    def test_outside_or_duplicate_coordinates_fail_direct_bijection(self):
        self.assertFalse(direct_coordinate_membership([(0, 0), (0, 1), (1, 0), (2, 2)], 2)["direct_bijection"])
        result = direct_coordinate_membership([(0, 0), (0, 1), (1, 0), (0, 0)], 2)
        self.assertFalse(result["direct_bijection"])
        self.assertEqual(result["duplicate_coordinate_multiplicities"], [{"coordinate": [0, 0], "count": 2}])

    def test_labels_are_not_unique_event_identity(self):
        result = label_information(["blue", "blue", "yellow"])
        self.assertEqual(result["distinct_labels"], 2)
        self.assertFalse(result["can_be25_distinct_symbols_without_position_or_extra_information"])
        self.assertTrue(result["repeated_labels_do_not_destroy_original_event_identity"])

    def test_malformed_coordinate_domains_rejected(self):
        for coordinates, side in (([(0, 0)], 0), ([(0, 0)], True), ([(0, 0, 1)], 5), ([(0, "1")], 5)):
            with self.assertRaises(ValueError):
                direct_coordinate_membership(coordinates, side)

    def test_frozen_direct_lookup_fails_without_remapping(self):
        document = report()
        self.assertEqual(document["status"], "REJECTED")
        self.assertEqual(document["direct_square_domain"]["in_domain_source_indices"], [6, 11, 19])
        self.assertEqual(len(document["direct_square_domain"]["out_of_domain_source_indices"]), 22)
        self.assertEqual(document["original_domain"]["unique_source_coordinates"], 25)
        self.assertEqual(len(document["ordered_event_marker_records"]), 25)
        self.assertEqual(document["search_space"]["coordinate_conversions"], 0)
        self.assertEqual(document["search_space"]["square_variants"], 0)

    def test_frozen_report_is_exact_and_zero_trial(self):
        document = report()
        self.assertEqual(json.loads((OUTPUT / "coordinate-interface.json").read_text()), document)
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"], document["new_image_variants"]), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
