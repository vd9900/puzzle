import json
import unittest

from tools.residual_frame_join import OUTPUT, join_tokens, report, square_with_ownership


class ResidualFrameJoinTests(unittest.TestCase):
    def test_small_complete_join(self):
        tokens = join_tokens({1: "a", 4: "c"}, [1, 0], 4)
        self.assertEqual("".join(entry["token"] for entry in tokens), "abbec")

    def test_incomplete_or_overlapping_domains_rejected(self):
        with self.assertRaises(ValueError):
            join_tokens({1: "a"}, [1, 0], 4)
        with self.assertRaises(ValueError):
            join_tokens({1: "a", 2: "x", 4: "c"}, [1, 0], 4)
        with self.assertRaises(ValueError):
            join_tokens({1: "a", 4: "c"}, [1, 2], 4)

    def test_square_records_token_ownership(self):
        square, first = square_with_ownership([
            {"logical_position_one_based": 1, "token": "d", "owner": "residual"},
            {"logical_position_one_based": 2, "token": "be", "owner": "event-label"},
        ])
        self.assertTrue(square.startswith("dbe"))
        self.assertEqual([(entry["symbol"], entry["owner"]) for entry in first], [("d", "residual"), ("b", "event-label"), ("e", "event-label")])

    def test_frozen_join_reconstructs_source_and_square(self):
        document = report()
        self.assertEqual(document["status"], "CONFIRMED")
        self.assertTrue(document["reconstruction"]["exact_raw_match"])
        self.assertTrue(document["reconstruction"]["exact_prime_token_match"])
        self.assertTrue(document["square_dependency"]["exact_match"])
        self.assertEqual(document["square_dependency"]["observed_symbols_owned_by_event_labels"], ["b", "e"])
        self.assertEqual(document["information_accounting"]["final_binary_region_labels_kept_separate"], 2)

    def test_frozen_report_is_exact_and_zero_trial(self):
        document = report()
        self.assertEqual(json.loads((OUTPUT / "residual-frame-join.json").read_text()), document)
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"], document["new_image_variants"]), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
