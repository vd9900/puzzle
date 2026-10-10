import json
import unittest

from tools.instruction_graphs import ROOT
from tools.speech_operand_audit import CHAT, OUTPUT, report
from tools.trailer_referents import alphabetic_source_map


class SpeechOperandAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_fixed_regions_round_trip_both_public_sources(self):
        speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
        document = CHAT.read_text()
        regions = self.document["regions"]
        self.assertEqual(len(regions), 3)
        self.assertEqual(sum(len(region["segments"]) for region in regions), 24)
        self.assertEqual(sum(region["fixed_anchor_count"] for region in regions), 12)
        for region in regions:
            start, end = region["puzzle_span_zero_based_half_open"]
            self.assertEqual("".join(segment["puzzle_normalized_text"] for segment in region["segments"]), speech[start:end])
            for segment in region["segments"]:
                raw_start, raw_end = segment["baseline_source_location"]["character_span_zero_based_half_open"]
                normalized, unused_positions = alphabetic_source_map(document, raw_start, raw_end)
                self.assertEqual(normalized, segment["baseline_normalized_text"])
                decoded_start, decoded_end = segment["puzzle_decoded_span_zero_based_half_open"]
                self.assertEqual(segment["puzzle_encoded_fixture_span_zero_based_half_open"], [447 + decoded_start, 447 + decoded_end])
                if segment["kind"] == "EXACT_INHERITED_ANCHOR":
                    self.assertEqual(segment["baseline_normalized_text"], segment["puzzle_normalized_text"])

    def test_fixed_baseline_coverage_retains_uncovered_regions(self):
        coverage = self.document["coverage"]
        self.assertEqual((coverage["selected_baseline_coverage_letters"], coverage["uncovered_letters"]), (1076, 463))
        missing = [entry["span_zero_based_half_open"] for entry in coverage["intervals"] if entry["classification"] == "BASELINE_NOT_PRESERVED_BY_SELECTED_QUOTATIONS"]
        self.assertEqual(missing, [[421, 832], [1487, 1539]])
        self.assertTrue(coverage["uncovered_text_not_automatically_creator_insertion"])
        self.assertTrue(coverage["no_claim_of_complete_original_movie_baseline"])

    def test_speaker_role_comparison_preserves_duplicate_baseline_question(self):
        roles = self.document["dialogue_roles"]
        self.assertEqual(roles["duplicate_neo_question_count_in_baseline_record"], 2)
        self.assertEqual(roles["verified_question_count_in_puzzle"], 1)
        self.assertEqual([entry["mapped_puzzle_anchor"]["puzzle_decoded_span_zero_based_half_open"] for entry in roles["roles"]], [[341, 371], [371, 383]])
        self.assertTrue(roles["double_you_not_independently_an_extraction_command"])

    def test_secondary_variant_claim_is_not_original_baseline_authentication(self):
        claims = self.document["variant_claims"]
        self.assertEqual(len(claims["claims"]), 2)
        self.assertTrue(claims["gap_intent_and_pre_puzzle_provenance_remain_unverified"])
        self.assertTrue(all(not entry["pre_puzzle_original_source_preserved"] for entry in claims["claims"]))
        self.assertEqual([entry["source_location"]["line_one_based"] for entry in claims["claims"]], [84036, 95714])

    def test_seven_public_references_map_exactly_without_a_consumer(self):
        speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
        references = self.document["object_references"]
        self.assertEqual(len(references), 7)
        for entry in references:
            start, end = entry["puzzle_decoded_span_zero_based_half_open"]
            self.assertEqual(speech[start:end], entry["phrase"])
            normalized, unused_positions = alphabetic_source_map(entry["secondary_spacing"], 0, len(entry["secondary_spacing"]))
            self.assertEqual(normalized, entry["phrase"])
            self.assertFalse(entry["defined_input_count_or_consumer"])
        self.assertFalse(references[0]["within_new_selected_baseline_region"])

    def test_finite_hypotheses_preserve_all_fields_and_zero_extraction(self):
        document = self.document
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 3)
        self.assertTrue(all(required <= entry.keys() for entry in document["hypotheses"]))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in document["hypotheses"]))
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))
        self.assertEqual(document["inherited_choice_limits_not_retested"]["new_Architect_word_extractions"], 0)

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "speech-operand-audit.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
