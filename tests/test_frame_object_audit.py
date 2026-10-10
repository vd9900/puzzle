import json
import unittest

from tools.frame_object_audit import OUTPUT, image_frame_map, report


class FrameObjectAuditTests(unittest.TestCase):
    def test_colored_events_cover24_octets_and_nearwhite_is_extra(self):
        image = image_frame_map()
        self.assertEqual((image["event_count"], image["decoded_octet_count"]), (25, 24))
        self.assertEqual(image["events_per_decoded_octet"], [1] * 20 + [2] + [1] * 3)
        self.assertTrue(image["blue_yellow_events_label_all24_octets_once"])
        self.assertEqual(image["events_in_four_bit_tail"], 0)

    def test_nearwhite_original_bit_is_not_semantic_one(self):
        document = report()
        case = document["near_white_case"]
        event = case["image_event"]
        self.assertEqual((event["event_index_zero_based"], event["verified_spiral_index_zero_based"], event["verified_octet_index_zero_based"], event["bit_position_in_octet_zero_based"]), (20, 163, 20, 3))
        self.assertEqual(event["verified_source_character"], "n")
        self.assertEqual(event["verified_source_octet_bits"], "01101110")
        self.assertEqual(event["original_binary_bit"], 0)
        self.assertEqual(case["existing_semantic_event_label_bit"], 1)
        self.assertFalse(case["original_binary_bit_matches"])

    def test_semantic_and_original_binary_mismatches_are_separate(self):
        branches = report()["branches"]
        self.assertEqual([(branch["mask"], branch["semantic_mismatch_event_indices"], branch["original_binary_mismatch_event_indices"]) for branch in branches], [(505, [22], [20, 22]), (1017, [], [20])])

    def test_only_terminal_prime83_label_discriminates_frozen_branches(self):
        document = report()
        differences = document["branch_differences"]
        labels = [entry for entry in differences if not entry["same_bit_value"]]
        self.assertEqual(len(labels), 1)
        self.assertEqual((labels[0]["event_index_zero_based"], labels[0]["505_token"], labels[0]["1017_token"]), (22, "b", "be"))
        self.assertEqual((labels[0]["505_span"], labels[0]["1017_span"]), ([89, 90], [89, 91]))

    def test_borrowed_bits_do_not_independently_select_branch(self):
        document = report()
        self.assertFalse(document["boundary_bits_discriminate_branches"])
        self.assertEqual([branch["borrowed_boundary_bits"] for branch in document["branches"]], [[1, 0], [1, 0]])
        offsets = [[entry["binary_offset_zero_based"] for entry in branch["markers"] if entry["region"] == "matrixsumlist-binary"] for branch in document["branches"]]
        self.assertEqual(offsets, [[4, 12], [5, 13]])
        self.assertTrue(document["source_maps_reproduce_saved_continuous_frame"])

    def test_all_three_hypotheses_are_bounded_and_have_required_fields(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 3)
        self.assertTrue(all(required <= hypothesis.keys() for hypothesis in document["hypotheses"]))
        self.assertEqual(document["search_space"]["comparisons"], 50)
        self.assertEqual(document["search_space"]["new_tokenizations"], 0)
        self.assertEqual((document["new_image_variants"], document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "frame-object-audit.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
