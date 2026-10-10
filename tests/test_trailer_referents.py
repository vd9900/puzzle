import json
import unittest

from tools.instruction_graphs import ROOT
from tools.trailer_referents import OUTPUT, alphabetic_source_map, choice_quote, report, speech_wording


class TrailerReferentTests(unittest.TestCase):
    def test_alphabetic_normalization_retains_exact_source_positions(self):
        text = "prefix AB-Cé 12 Def suffix"
        normalized, positions = alphabetic_source_map(text, 7, 19)
        self.assertEqual(normalized, "abcdef")
        self.assertEqual(positions, [7, 8, 10, 16, 17, 18])

    def test_archived_spaced_speech_matches_the_entire_verified_fixture(self):
        evidence = speech_wording()
        self.assertTrue(evidence["all1539_letters_match"])
        self.assertEqual([word["word"] for word in evidence["pre_select_phrase_words"]], ["REINSERTING", "THE", "PRIME", "BASICS"])
        self.assertEqual(evidence["pre_select_phrase_letter_count"], 25)
        self.assertTrue(evidence["selected_word_count_is_not_specified"])

    def test_every_mapped_spaced_anchor_matches_original_bytes(self):
        evidence = speech_wording()
        original = (ROOT / evidence["source"]["path"]).read_bytes()
        for anchor in evidence["anchors"]:
            start, end = anchor["utf8_byte_span_zero_based_half_open"]
            self.assertEqual(original[start:end].decode(), anchor["archived_spacing"])

    def test_literal_choice_passage_is_not_the_modified_speech(self):
        evidence = choice_quote()
        records = {item["normalized_phrase"]: item for item in evidence["phrase_presence_comparison"]}
        self.assertFalse(records["theproblemischoice"]["in_verified_modified_speech"])
        self.assertTrue(records["theproblemischoice"]["in_quoted_community_passage"])
        self.assertTrue(records["reinsertingtheprimebasics"]["in_verified_modified_speech"])
        self.assertFalse(records["reinsertingtheprimebasics"]["in_quoted_community_passage"])

    def test_current_finite_hypotheses_have_all_required_fields(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 3)
        self.assertTrue(all(required <= hypothesis.keys() for hypothesis in document["hypotheses"]))
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))

    def test_frozen_referent_artifact_regenerates_exactly(self):
        path = OUTPUT / "trailer-referents.json"
        preserved = path.read_bytes()
        self.assertEqual(json.loads(preserved), report())
        self.assertEqual(path.read_bytes(), preserved)


if __name__ == "__main__":
    unittest.main()
