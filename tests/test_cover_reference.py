import json
import unittest

from tools.cover_reference import OUTPUT, report


class CoverReferenceTests(unittest.TestCase):
    def test_archived_image_context_does_not_claim_attachment_identity(self):
        evidence = report()
        self.assertEqual(evidence["cover"]["image_size"], [553, 651])
        self.assertEqual(evidence["screenshot"]["image_size"], [543, 576])
        self.assertTrue(evidence["screenshot"]["original_attachment_not_preserved_under_that_filename"])
        self.assertTrue(evidence["screenshot"]["thumbnail_cover_identification_is_visual_not_byte_identity"])

    def test_exact_context_reactions_agree_across_both_exports(self):
        evidence = report()
        self.assertEqual(len(evidence["records"]), 3)
        self.assertTrue(all(record["same_text"] and record["exports_are_not_independent_authentication"] for record in evidence["records"]))
        self.assertIn("08.01.2023", evidence["records"][-1]["creator_labeled_export"]["header"])

    def test_visual_observation_leaves_mathematical_mapping_unknown(self):
        evidence = report()
        self.assertTrue(evidence["cover"]["no_exact_star_count_claim"])
        self.assertEqual(len(evidence["unknowns"]), 5)
        self.assertEqual((evidence["new_cryptographic_trials"], evidence["new_trial_inputs"], evidence["new_image_variants"]), (0, 0, 0))

    def test_frozen_cover_reference_regenerates(self):
        path = OUTPUT / "cover-reference.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
