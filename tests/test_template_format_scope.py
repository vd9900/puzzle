import json
import unittest

from tools.instruction_graphs import ROOT
from tools.template_format_scope import OUTPUT, report


class TemplateFormatScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_three_original_tags_have_local_source_attachment(self):
        templates = self.document["earlier_templates"]["format_templates"]
        self.assertEqual(len(templates), 3)
        self.assertEqual(templates[0]["owner_rule_supported_by_format"], "INLINE_TAG_IN_SAME_PRIMARY_PARAGRAPH")
        self.assertTrue(all(entry["owner_rule_supported_by_format"] == "STANDALONE_TAG_AFTER_PRECEDING_PRIMARY_PARAGRAPH" for entry in templates[1:]))
        source = (ROOT / "research/sources/phase2.html").read_bytes().decode()
        for entry in templates:
            start, end = entry["tag_source_location"]["character_span_zero_based_half_open"]
            self.assertEqual(source[start:end], entry["literal_tag"])

    def test_phase3_same_tag_is_attached_to_three_distinct_riddles(self):
        templates = self.document["earlier_templates"]
        self.assertEqual(len(templates["phase3_local_tags"]), 3)
        self.assertEqual([entry["paragraph_index_zero_based"] for entry in templates["phase3_local_tags"]], [0, 1, 2])
        self.assertTrue(all(entry["same_paragraph_prefix_length"] > 20 for entry in templates["phase3_local_tags"]))
        self.assertTrue(templates["not_enf_and_enf_are_distinct_authored_spellings"])

    def test_aggregate_template_explicitly_names_parts_and_consumer(self):
        aggregate = self.document["earlier_templates"]["aggregate_order_and_consumer"]
        self.assertIn("parts 1..7", aggregate["text"])
        self.assertIn("enter Phase 3", aggregate["text"])
        self.assertIn("sha-256", aggregate["text"])

    def test_current_five_fragments_have_no_transferred_format_tag(self):
        fragments = self.document["current_fragments"]
        self.assertEqual(len(fragments["source_owned_fragment_maps"]), 5)
        self.assertTrue(fragments["five_relevant_fragments_share_one_primary_textarea"])
        self.assertEqual(fragments["literal_format_tag_occurrences_in_encoded_source"], 0)
        self.assertFalse(fragments["literal_part_range_arrows_in_encoded_source"])
        self.assertTrue(fragments["whitespace_removal_is_encoded_container_normalization_not_a_hash_input_rule"])

    def test_two_hypotheses_have_required_fields_and_no_variant_generation(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 2)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertEqual(self.document["search_space"]["new_normalization_trials"], 0)
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "template-format-scope.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
