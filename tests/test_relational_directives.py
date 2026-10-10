import json
import unittest

from tools.instruction_graphs import ROOT
from tools.relational_directives import OUTPUT, mapped_directives, report


class RelationalDirectiveTests(unittest.TestCase):
    def test_all_fixed_anchors_map_to_verified_text_and_spacing(self):
        document = mapped_directives()
        speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
        spacing = (ROOT / "research/sources/community-README.md").read_text()
        self.assertEqual(len(document["mapped_anchors"]), 8)
        for anchor in document["mapped_anchors"]:
            start, end = anchor["verified_decoded_span_zero_based_half_open"]
            self.assertEqual(speech[start:end], anchor["normalized_phrase"])
            raw_start, raw_end = anchor["secondary_spacing_location"]["character_span_zero_based_half_open"]
            self.assertEqual(spacing[raw_start:raw_end], anchor["archived_spacing"])
            self.assertEqual(anchor["encoded_fixture_byte_span_zero_based_half_open"], [447 + start, 447 + end])
        self.assertTrue(document["all1539_letters_match"])

    def test_local_after_which_order_does_not_bind_operands(self):
        document = report()
        graph = document["conditional_operation_graph"]
        self.assertIn(["reinsert-prime-basics", "select-from-described-objects", "EXPLICIT_AFTER_WHICH_LOCAL_ANTECEDENT"], graph["edges"])
        self.assertTrue(all(hypothesis["status"] == "INCONCLUSIVE" for hypothesis in document["hypotheses"]))
        self.assertTrue(any("not explicitly named" in contradiction for contradiction in document["contradictions"]))

    def test_numeric_phrases_keep_types_and_qualifiers(self):
        document = mapped_directives()
        self.assertEqual(document["typed_numeric_phrases"], [{"value": 23, "qualifier": "over", "noun": "ciphers"}, {"value": 16, "qualifier": None, "noun": "encryptions"}, {"value": 7, "qualifier": "and or", "noun": "intertwined passwords"}])
        self.assertTrue(document["numbers_are_not_an_algorithm_list_or_position_selector"])
        self.assertFalse(document["literal_choice_in_speech"])

    def test_finite_source_referents_have_required_evidence_fields(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 3)
        self.assertTrue(all(required <= hypothesis.keys() for hypothesis in document["hypotheses"]))
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "relational-directives.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
