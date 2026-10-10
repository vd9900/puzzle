import unittest

from tools.fifteen_receiver_audit import report


class FifteenReceiverAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_no_recovered_object_has_size_fifteen(self):
        inventory = self.document["recovered_object_inventory"]
        self.assertEqual(inventory["objects_checked"], 14)
        self.assertEqual(inventory["exact_size15_objects"], [])

    def test_blue_count_is_fifteen(self):
        blue = self.document["blue_event_candidate"]
        self.assertEqual(blue["color_counts"], {"blue": 15, "near_white": 1, "yellow": 9})
        self.assertEqual(blue["blue_event_count"], 15)

    def test_blue_subset_is_dependent_on_url_parity(self):
        blue = self.document["blue_event_candidate"]
        self.assertTrue(blue["blue_events_are_exactly_terminal_one_bits"])
        self.assertEqual(blue["blue_octet_indices_zero_based"], blue["odd_ascii_octet_indices_zero_based"])
        self.assertFalse(blue["independent_of_existing_url_decode"])

    def test_blue_coordinates_do_not_supply_fifteen_columns(self):
        blue = self.document["blue_event_candidate"]
        self.assertEqual(blue["direct_distinct_column_slots"], 10)
        self.assertFalse(blue["direct_bijection_to15_bifid_columns"])
        self.assertTrue(blue["ordinal_pairing_requires_new_assignment"])

    def test_bip39_is_only_external_dimensional_match(self):
        candidate = self.document["external_standard_candidate"]
        self.assertTrue(candidate["fifteen_is_allowed"])
        self.assertFalse(candidate["recovered_public_puzzle_object"])
        self.assertFalse(candidate["source_authored_binding"])

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
