import json
import unittest

from tools.visual_correspondence import IMAGES, OUTPUT, color_wording, event_structure, image_metadata, report


class VisualCorrespondenceTests(unittest.TestCase):
    def test_capture_metadata_does_not_claim_publication_date(self):
        cover = image_metadata(IMAGES["cover"])
        context = image_metadata(IMAGES["cover_context"])
        self.assertEqual(cover["capture_time_without_timezone"], "2023-08-21T21:46:42")
        self.assertEqual(context["capture_time_without_timezone"], "2023-08-21T21:40:39")
        self.assertEqual(cover["software"], "gnome-screenshot")
        self.assertTrue(context["capture_metadata_is_not_hint_publication_time"])

    def test_fixed_original_event_locations_have_no_new_routes(self):
        grid = event_structure()
        self.assertEqual(grid["color_counts"], {"white": 85, "black": 86, "blue": 15, "yellow": 9, "near_white": 1})
        self.assertEqual(grid["blue_yellow_frame_offsets"], [7])
        self.assertEqual(grid["blue_yellow_event_count"], 24)
        self.assertEqual(len(grid["special_event_source_map"]), 25)
        near_white = next(event for event in grid["special_event_source_map"] if event["color"] == "near_white")
        self.assertEqual((near_white["row_zero_based"], near_white["column_zero_based"], near_white["verified_spiral_index_zero_based"]), (7, 4, 163))
        self.assertTrue(grid["no_new_image_variant_or_route"])

    def test_color_wording_is_exact_and_does_not_choose_a_palette(self):
        hint = color_wording()
        self.assertEqual(hint["phrase"], "Yellow has a number and so does Blue.")
        self.assertTrue(hint["return_to_first_piece_literal"])
        self.assertTrue(hint["number_assignment_not_specified"])
        self.assertEqual(hint["phrase_location"]["line_one_based"], 196)

    def test_bijection_rejection_is_narrow_and_not_an_image_rejection(self):
        document = report()
        rejected = [item for item in document["correspondences"] if item["status"].startswith("REJECTED")]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["status"], "REJECTED_UNCONDITIONAL_BIJECTION")
        self.assertEqual(document["status"], "INCONCLUSIVE")

    def test_report_records_missing_edges_without_generating_inputs(self):
        document = report()
        self.assertEqual(len(document["correspondences"]), 6)
        self.assertEqual((document["new_image_variants"], document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0, 0))
        self.assertTrue(document["cover_visual_observations_are_not_pixel_segmentation"])

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "visual-correspondence.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
