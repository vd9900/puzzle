import json
import unittest

from tools.speech_delta import CHAT, OUTPUT, ROOT, mapped_alignment, normalize_with_positions, report


class SpeechDeltaTests(unittest.TestCase):
    def test_normalization_retains_numeric_values_and_positions(self):
        normalized, positions = normalize_with_positions("23 individuals, 16 female", 0, 25)
        self.assertEqual(normalized, "23individuals16female")
        self.assertEqual(positions[:2], [0, 1])

    def test_exact_baseline_reposts_do_not_claim_authentication(self):
        alignment = mapped_alignment()
        self.assertEqual([record["line_one_based"] for record in alignment["baseline_records"]], [33097, 45259])
        self.assertTrue(alignment["same_preserved_quote_in_two_messages"])
        self.assertEqual(alignment["baseline_classification"], "COMMUNITY_MOVIE_QUOTATION_NOT_AUTHENTICATED_ORIGINAL_SCRIPT")

    def test_all13_segments_reconstruct_the_exact_selected_speech(self):
        alignment = mapped_alignment()
        speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
        start, end = alignment["puzzle_decoded_span_zero_based_half_open"]
        self.assertEqual((start, end), (984, 1223))
        self.assertEqual("".join(segment["puzzle_phrase_normalized"] for segment in alignment["segments"]), speech[start:end])
        self.assertEqual(alignment["kind_counts"], {"INHERITED": 5, "REPLACEMENT": 6, "INSERTION": 2})
        for segment in alignment["segments"]:
            source_start, source_end = segment["puzzle_decoded_span_zero_based_half_open"]
            self.assertEqual(speech[source_start:source_end], segment["puzzle_phrase_normalized"])
            self.assertEqual(segment["puzzle_encoded_fixture_span_zero_based_half_open"], [447 + source_start, 447 + source_end])

    def test_baseline_locations_and_insertion_points_are_exact(self):
        document = CHAT.read_text()
        for segment in mapped_alignment()["segments"]:
            start, end = segment["baseline_quote_source_location"]["character_span_zero_based_half_open"]
            normalized, unused_positions = normalize_with_positions(document, start, end)
            expected, unused_expected_positions = normalize_with_positions(segment["baseline_phrase"], 0, len(segment["baseline_phrase"]))
            self.assertEqual(normalized, expected)
            if segment["kind"] == "INSERTION":
                self.assertEqual(start, end)

    def test_inherited_constraints_do_not_become_cipher_or_index_choices(self):
        document = report()
        self.assertTrue(all(entry["baseline_has_feature"] for entry in document["constraint_independence"]))
        self.assertIn("numeric values are inherited", document["hypotheses"][0]["contradictions"][1])
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))

    def test_both_semantic_hypotheses_have_required_fields(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 2)
        self.assertTrue(all(required <= hypothesis.keys() for hypothesis in document["hypotheses"]))
        self.assertTrue(all(hypothesis["status"] == "INCONCLUSIVE" for hypothesis in document["hypotheses"]))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "speech-delta.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
