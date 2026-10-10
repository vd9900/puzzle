import json
import unittest

from tools.deictic_source_audit import OUTPUT, report
from tools.instruction_graphs import ROOT


class DeicticSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_earlier_and_nearby_public_anchors_have_exact_source_positions(self):
        antecedents = self.document["antecedents"]
        self.assertTrue(antecedents["earlier_phase3_fixture_matches_preserved_archive"])
        entries = antecedents["earlier_primary_source_maps"] + antecedents["secondary_thinker_identifications"] + antecedents["nearby_phase32_public_source_maps"]
        self.assertEqual(len(entries), 10)
        for entry in entries:
            payload = (ROOT / entry["source"]["path"]).read_bytes()
            if entry["source"]["path"] == "research/artifacts/phase32.txt":
                payload = payload[:443]
            source = payload.decode()
            start, end = entry["character_span_zero_based_half_open"]
            self.assertEqual(source[start:end], entry["literal"])
        self.assertEqual(antecedents["earlier_primary_source_maps"][0]["character_span_zero_based_half_open"], [127, 146])

    def test_creator_preference_is_cross_checked_not_an_extraction_instruction(self):
        creator = self.document["creator_attribution"]
        self.assertTrue(creator["both_preserved_bodies_match"])
        self.assertEqual(creator["creator_record"]["line_one_based"], 1027)
        self.assertEqual(creator["original_chat_record"]["line_one_based"], 73142)
        self.assertEqual(creator["elapsed_since_prior_community_speech_seconds"], 39060)
        self.assertFalse(creator["reply_target_metadata_preserved"])
        self.assertTrue(creator["does_not_confirm_wiseman_antecedent_or_value140"])

    def test_competing_community_claim_remains_secondary(self):
        alternative = self.document["alternative_attribution"]
        self.assertEqual(alternative["assertion_source_location"]["line_one_based"], 34520)
        self.assertEqual(alternative["classification"], "COMMUNITY_SPECULATION_NOT_CREATOR_AUTHENTICATION")
        self.assertTrue(alternative["claimed_value140_link_is_not_tested_or_adopted"])

    def test_deictic_scope_and_input_consumer_remain_unbound(self):
        antecedents = self.document["antecedents"]
        self.assertTrue(antecedents["above_is_not_a_unique_document_or_paragraph_selector"])
        self.assertTrue(antecedents["phase3_does_not_name_the_thinker_explicitly"])
        self.assertTrue(antecedents["phase32_intro_does_not_name_a_wiseman"])
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))
        self.assertIn("Deleted Account, not creator-authenticated", self.document["next_test"])

    def test_three_hypotheses_have_all_required_fields(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 3)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in self.document["hypotheses"]))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "deictic-source-audit-v2.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)
        self.assertTrue((OUTPUT / "deictic-source-audit.json").exists())


if __name__ == "__main__":
    unittest.main()
