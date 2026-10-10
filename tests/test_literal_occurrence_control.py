import itertools
import json
import unittest
from fractions import Fraction

from tools.literal_occurrence_control import OUTPUT, report, unbordered_occurrence_probability


class LiteralOccurrenceTests(unittest.TestCase):
    def test_exact_inclusion_exclusion_agrees_with_small_exhaustive_multisets(self):
        for population, word in [("aabbcc", "ab"), ("aaabbc", "abc"), ("aabc", "bc")]:
            permutations = set(itertools.permutations(population))
            for selected_length in range(len(population) + 1):
                actual = Fraction(sum(word in "".join(sequence[:selected_length]) for sequence in permutations), len(permutations))
                calculated = unbordered_occurrence_probability(population, word, selected_length)
                self.assertEqual(Fraction(calculated["at_least_one_exact_probability"]), actual)

    def test_fixed_noncontiguous_projection_has_same_exchangeable_null(self):
        population = "aabbcc"
        permutations = set(itertools.permutations(population))
        indices = [0, 2, 3, 5]
        actual = Fraction(sum("ab" in "".join(sequence[index] for index in indices) for sequence in permutations), len(permutations))
        expected = unbordered_occurrence_probability(population, "ab", len(indices))
        self.assertEqual(Fraction(expected["at_least_one_exact_probability"]), actual)

    def test_bordering_word_or_bad_length_is_not_silently_supported(self):
        for population, word, length in [("aaaa", "aa", 4), ("abc", "aba", 3), ("abc", "", 3), ("abc", "ab", 4)]:
            with self.assertRaises(ValueError):
                unbordered_occurrence_probability(population, word, length)

    def test_exact_public_projection_probabilities_match_saved_fractions(self):
        document = report()
        self.assertEqual([case["control"]["at_least_one_exact_probability"] for case in document["cases"]], ["6677547/37771954220", "2077457/11331586266"])
        self.assertTrue(all(len(case["control"]["terms"]) == 2 for case in document["cases"]))

    def test_control_artifact_regenerates_without_sampling_or_search(self):
        path = OUTPUT / "partial-literal-control.json"
        original = path.read_bytes()
        document = report()
        self.assertEqual(json.loads(original), document)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual((document["new_random_samples"], document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
