import unittest

from tools.bifid_sumlist_bip39_preflight import report


class BifidSumlistBip39PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_dimension_chain_is_exact(self):
        chain = self.document["exact_dimension_chain"]
        self.assertEqual(chain["bifid_matrix"], [38, 15])
        self.assertEqual(chain["sum_across_rows_produces_items"], 15)
        self.assertEqual(chain["bip39_allows_word_count"], 15)

    def test_bounds_do_not_select_a_mapping(self):
        bounds = self.document["symbolic_map_bounds_only"]
        self.assertTrue(bounds["all_bounds_fit_bip39_index_domain"])
        self.assertEqual(bounds["compatible_mapping_count"], 9)
        self.assertEqual(bounds["actual_sum_vectors_computed"], 0)

    def test_prior_family_is_related_but_not_exact(self):
        coverage = self.document["coverage_comparison"]
        self.assertTrue(coverage["same_family_at_high_level"])
        self.assertFalse(coverage["exact_input_stage_previously_covered_by_that_script"])
        self.assertEqual(coverage["genuinely_new_difference"], "post-Bifid rather than raw-FAED matrix input")

    def test_architecture_remains_unbound(self):
        architecture = self.document["architecture_discriminator"]
        self.assertEqual(architecture["matrixsumlist_to15_item_seed_interface"], "DIMENSIONALLY COMPATIBLE")
        self.assertTrue(architecture["unique_numeric_mapping"].startswith("REJECTED"))
        self.assertEqual(len(self.document["blocking_unknowns"]), 5)

    def test_non_executing_scope(self):
        for field in ("candidate_lists_generated", "mnemonic_words_generated", "checksum_tests", "seed_derivations", "private_key_operations", "aes_operations"):
            self.assertEqual(self.document[field], 0)


if __name__ == "__main__":
    unittest.main()
