import json
import unittest

from tools.weighted_conservation import OUTPUT, compare_residual, consecutive_sum_witness, partition_totals, report, source_partitions


class WeightedConservationTests(unittest.TestCase):
    def test_source_partitions_cover_the_original_grid_exactly_once(self):
        matrix = [[row * 14 + column for column in range(14)] for row in range(14)]
        expected_total = sum(range(196))
        partitions = source_partitions(14)
        self.assertEqual([len(partition["groups"]) for partition in partitions], [14, 14, 25])
        for partition in partitions:
            totals = partition_totals(matrix, partition["groups"])
            self.assertEqual(sum(totals), expected_total)
        self.assertEqual([len(group) for group in partitions[-1]["groups"]], [8] * 24 + [4])

    def test_repeated_or_missing_cells_are_rejected(self):
        matrix = [[1, 2], [3, 4]]
        for groups in [[[(0, 0), (0, 1)], [(1, 0), (0, 0)]], [[(0, 0), (0, 1)], [(1, 0)]], [[], [(0, 0), (0, 1), (1, 0), (1, 1)]]]:
            with self.assertRaises(ValueError):
                partition_totals(matrix, groups)

    def test_consecutive_positive_groups_have_exact_inverse_boundaries(self):
        result = consecutive_sum_witness([2, 3, 1, 4, 5], [5, 5, 5])
        self.assertTrue(result["match"])
        self.assertEqual([group["residual_span_zero_based_half_open"] for group in result["successful_prefix_groups"]], [[0, 2], [2, 4], [4, 5]])

    def test_same_total_does_not_imply_a_supported_partition(self):
        result = consecutive_sum_witness([4, 9, 6], [5, 14])
        self.assertFalse(result["match"])
        self.assertEqual(result["complete_residual_total"], result["complete_target_total"])
        self.assertEqual(result["first_failure"]["wanted_cumulative_sum"], 5)
        self.assertEqual(result["first_failure"]["nearest_lower_cumulative_sum_and_end_index"], [4, 1])
        self.assertEqual(result["first_failure"]["nearest_upper_cumulative_sum_and_end_index"], [13, 2])

    def test_zero_group_and_unused_symbols_are_not_silently_removed(self):
        self.assertFalse(consecutive_sum_witness([2, 3], [5, 0])["match"])
        self.assertFalse(consecutive_sum_witness([2, 3], [2])["match"])
        with self.assertRaises(ValueError):
            consecutive_sum_witness([2, 0, 3], [5])

    def test_direct_comparison_has_a_positive_control(self):
        result = compare_residual([2, 3, 4], [2, 3, 4])
        self.assertTrue(all(comparison["match"] for comparison in result.values()))

    def test_fixed_public_data_rejects_exactly_the_documented_comparisons(self):
        document = report()
        self.assertEqual(document["weighted_total"], 341)
        self.assertEqual([(branch["mask"], len(branch["values"]), branch["total"]) for branch in document["residual_branches"]], [(505, 61, 341), (1017, 60, 336)])
        self.assertEqual(document["search_space"]["exact_comparisons"], 18)
        self.assertTrue(all(not comparison["match"] for entry in document["results"] for comparison in entry["comparisons"].values()))
        self.assertEqual([entry["comparisons"]["consecutive_additive_partition"]["first_failure"]["wanted_cumulative_sum"] for entry in document["results"]], [32, 32, 9, 9, 6, 6])
        events = document["color_frame_accounting"]["event_counts_by_group"]
        self.assertEqual(sum(events), 25)
        self.assertEqual(events, [1] * 20 + [2] + [1] * 3 + [0])
        self.assertEqual((document["search_space"]["new_cryptographic_trials"], document["search_space"]["new_trial_inputs"]), (0, 0))

    def test_current_artifact_matches_deterministic_regeneration(self):
        path = OUTPUT / "weighted-conservation.json"
        preserved = path.read_bytes()
        self.assertEqual(json.loads(preserved), report())
        self.assertEqual(path.read_bytes(), preserved)


if __name__ == "__main__":
    unittest.main()
