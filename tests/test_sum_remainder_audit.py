import json
import unittest

from tools.instruction_graphs import ROOT
from tools.sum_remainder_audit import CHAT, OUTPUT, opening_comparison, report
from tools.trailer_referents import alphabetic_source_map


class SumRemainderAuditTests(unittest.TestCase):
    def test_preserved_baseline_prefix_and_changed_referent_map_exactly(self):
        comparison = opening_comparison()
        document = CHAT.read_text()
        for entry in comparison["records"]:
            start, end = entry["changed_referent_source_location"]["character_span_zero_based_half_open"]
            normalized, unused_positions = alphabetic_source_map(document, start, end)
            self.assertEqual(normalized, "thematrix")
            self.assertEqual(entry["baseline_normalized_length"], 85)
        self.assertEqual(comparison["shared_prefix_length"], 76)
        self.assertEqual(comparison["changed_puzzle_referent_span_zero_based_half_open"], [76, 86])

    def test_all_five_puzzle_anchors_reproduce_verified_source(self):
        comparison = opening_comparison()
        speech = (ROOT / "research/artifacts/phase32-beaufort.txt").read_text().strip()
        self.assertEqual(len(comparison["anchors"]), 5)
        for anchor in comparison["anchors"]:
            start, end = anchor["verified_decoded_span_zero_based_half_open"]
            self.assertEqual(speech[start:end], anchor["phrase"])
            self.assertEqual(anchor["encoded_fixture_byte_span_zero_based_half_open"], [447 + start, 447 + end])
        self.assertEqual(sum(anchor["inherited_from_preserved_baseline"] for anchor in comparison["anchors"]), 4)

    def test_secondary_baseline_is_not_independent_or_explicit_arithmetic(self):
        comparison = opening_comparison()
        self.assertTrue(comparison["matching_secondary_quotations_not_independent_authentication"])
        self.assertFalse(comparison["explicit_sum_operator_operand_or_list_format"])
        self.assertFalse(comparison["literal_matrixsumlist_in_opening"])
        self.assertEqual([entry["quoted_opening_source_location"]["line_one_based"] for entry in comparison["records"]], [32774, 164325])

    def test_both_semantic_hypotheses_have_required_fields(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 2)
        self.assertTrue(all(required <= hypothesis.keys() for hypothesis in document["hypotheses"]))
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "sum-remainder-audit.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
