import json
import unittest
from datetime import datetime

from tools.instruction_graphs import ROOT
from tools.zeroing_chronology import OUTPUT, report


class ZeroingChronologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_fixed_local_decode_predates_creator_zeroing_without_inferred_operand(self):
        chronology = self.document["chronology"]
        earlier = datetime.fromisoformat(chronology["earliest_exact_local_decode_record"]["archived_utc_timestamp"])
        later = datetime.fromisoformat(chronology["creator_zero_record"]["archived_utc_timestamp"])
        self.assertEqual(chronology["seconds_local_decode_predates_zeroing_hint"], int((later - earlier).total_seconds()))
        self.assertGreater(chronology["seconds_local_decode_predates_zeroing_hint"], 0)
        self.assertEqual(chronology["earliest_exact_local_decode_record"]["line_one_based"], 18496)
        self.assertTrue(chronology["date_order_does_not_prove_the_creator_excluded_an_already_known_step"])

    def test_generic_earliest_this_password_is_not_the_encoded_label(self):
        chronology = self.document["chronology"]
        self.assertEqual(chronology["generic_earlier_this_password_record"]["line_one_based"], 5471)
        self.assertTrue(chronology["generic_earlier_occurrence_is_not_encoded_label_evidence"])
        self.assertTrue(chronology["same_zeroing_body_in_two_exports"])

    def test_exact_phrase_source_maps_round_trip(self):
        chronology = self.document["chronology"]
        entries = [("research/evidence/cycle02/_work__chat_transcript.txt", entry) for entry in chronology["local_decode_phrase_maps"]]
        entries.extend(("research/evidence/cycle02/_work__creator_jrk.txt", chronology[name]) for name in ("zeroing_phrase_map", "another_door_reference_map"))
        for relative, entry in entries:
            document = (ROOT / relative).read_text()
            start, end = entry["character_span_zero_based_half_open"]
            self.assertEqual(document[start:end], entry["literal"])

    def test_local_zero_representation_does_not_supply_a_mask_or_inverse(self):
        roles = self.document["local_zero_roles"]
        self.assertEqual(len(roles["existing_local_label_decoder_regions"]), 2)
        self.assertTrue(roles["old_numeric_zero_decode_is_not_a_new_mask_operation"])
        self.assertEqual(roles["prime_zeroing_constraints_reused"]["same_operand_or_site"], "NOT_SPECIFIED")
        self.assertEqual(roles["prime_zeroing_constraints_reused"]["zeroing_equals_inverse_of_reinsertion"], "NOT_SPECIFIED")
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_two_hypotheses_have_required_fields(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 2)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in self.document["hypotheses"]))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "zeroing-chronology.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
