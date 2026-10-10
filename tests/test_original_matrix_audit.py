import json
import unittest

from tools.original_matrix_audit import OUTPUT, report


class OriginalMatrixAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_original_palette_and_binary_mapping_are_exact(self):
        matrix = self.document["verified_matrix"]
        self.assertEqual(matrix["shape"], [14, 14])
        self.assertEqual(matrix["palette_counts"], {"black": 86, "blue": 15, "near_white": 1, "white": 85, "yellow": 9})
        self.assertEqual(matrix["verified_spiral_decode"], "gsmg.io/theseedisplanted")
        self.assertEqual(matrix["per_color_binary_assignments_checked"], 32)
        self.assertEqual(matrix["exact_url_mapping_match_count"], 1)
        self.assertEqual(matrix["unique_binary_mapping"], {"black": 1, "blue": 1, "yellow": 0, "white": 0, "near_white": 0})

    def test_visible_colored_cells_are_fixed_but_nearwhite_is_not_named(self):
        selected = self.document["selected_cells"]
        self.assertEqual(selected["yellow_blue_count"], 24)
        self.assertEqual([entry["octet_index_zero_based"] for entry in selected["yellow_blue_cells"]], list(range(24)))
        self.assertTrue(all(entry["bit_position_in_octet_zero_based"] == 7 for entry in selected["yellow_blue_cells"]))
        self.assertFalse(selected["near_white_is_named_by_yellowblueprimes"])
        self.assertFalse(selected["instruction_explicitly_says_to_sum_only_colored_cells"])

    def test_prime_full_match_is_conditional(self):
        prime = self.document["prime_relation"]
        self.assertEqual((prime["ordinary24_color_frame_max_prefix"], prime["ordinary24_full_match_count"]), (20, 0))
        self.assertEqual((prime["conditional25_event_full_match_count"], prime["conditional_full_match_mask"]), (1, 1017))
        self.assertEqual(len(prime["conditional_full_match_event_map"]), 25)
        self.assertIn("near-white", " ".join(prime["conditions_required"]))

    def test_encoding_value_is_not_a_bound_sum_weight(self):
        values = self.document["numeric_values"]
        self.assertEqual(values["verified_encoding_role"]["mapping"]["blue"], 1)
        self.assertEqual(values["verified_encoding_role"]["mapping"]["yellow"], 0)
        self.assertFalse(values["summation_weight_assignment_present_in_source"])
        self.assertEqual(values["near_white_conflict"], {"verified_image_bit": 0, "conditional_prime_frame_label": 1, "same_numeric_role": False})

    def test_square_matrix_and_hint_do_not_choose_axis(self):
        axis = self.document["summation_axis"]
        self.assertEqual((axis["row_count"], axis["column_count"]), (14, 14))
        self.assertEqual((axis["row_total"], axis["column_total"]), (101, 101))
        self.assertFalse(axis["ordered_lists_equal"])
        self.assertEqual(axis["explicit_axis_terms_in_relevant_creator_hints"], [])
        self.assertTrue(axis["square_dimensions_cannot_select_an_axis"])

    def test_all_requested_interfaces_remain_explicit(self):
        classification = self.document["classification"]
        self.assertEqual(classification["twenty_four_visible_yellow_blue_cells"], "VERIFIED")
        self.assertEqual(classification["exclusive_cell_mask_for_matrixsumlist"], "UNKNOWN")
        self.assertEqual(classification["yellow_blue_summation_weights"], "UNKNOWN")
        self.assertEqual(classification["summation_axis"], "UNKNOWN")
        self.assertEqual(len(self.document["exact_missing_bindings"]), 3)

    def test_non_executing_scope_and_frozen_artifact(self):
        for field in ("new_image_variants", "new_numeric_weight_sweeps", "candidate_material_generated", "private_key_operations", "aes_operations"):
            self.assertEqual(self.document[field], 0)
        path = OUTPUT / "original-matrix-audit.json"
        if path.exists():
            before = path.read_bytes()
            self.assertEqual(json.loads(before), self.document)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
