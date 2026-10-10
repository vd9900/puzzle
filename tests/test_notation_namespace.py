import json
import unittest

from tools.instruction_graphs import ROOT
from tools.notation_namespace import OUTPUT, report


class NotationNamespaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_fifteen_fixed_primary_secondary_source_anchors_are_exact(self):
        namespaces = self.document["namespaces"]
        entries = namespaces["primary_source_maps"] + namespaces["secondary_interpretation_maps"]
        self.assertEqual(len(entries), 15)
        for entry in entries:
            document = (ROOT / entry["source"]["path"]).read_bytes().decode()
            start, end = entry["character_span_zero_based_half_open"]
            self.assertEqual(document[start:end], entry["literal"])
        self.assertEqual(namespaces["primary_source_maps"][2]["character_span_zero_based_half_open"], [11, 16])

    def test_explicit_local_domain_does_not_define_global_namespace(self):
        namespaces = self.document["namespaces"]
        self.assertEqual(namespaces["phase2_explicit_domain"], "parts1..7 local to the Phase3-entry construction")
        self.assertTrue(namespaces["phase3_reuses_ordinal1_in_a_new_riddle_context"])
        self.assertTrue(namespaces["phase3_middle_riddle_is_not_literally_numbered2"])
        self.assertTrue(namespaces["shared_global_object_numbering_not_authored"])

    def test_braced_media_reference_is_not_a_numeric_coordinate_schema(self):
        namespaces = self.document["namespaces"]
        self.assertTrue(namespaces["braces_are_used_for_media_reference_not_only_numeric_indices"])
        self.assertTrue(namespaces["earlier_symbol_numeral_sequence_has_distinct_syntax"])
        self.assertEqual(len(self.document["door_reference_reused_not_retested"]["groups"]), 3)

    def test_six_formatting_occurrences_preserve_local_variants(self):
        notation = self.document["normalization_notation"]
        self.assertEqual(len(notation["source_maps"]), 6)
        self.assertEqual(sum(entry["literal"] == "/(aa,connected enf)" for entry in notation["source_maps"]), 3)
        self.assertTrue(notation["connected_not_enf_is_explicitly_distinct_from_connected_enf"])
        self.assertTrue(notation["aa_and_aaa_literal_lengths_do_not_define_character_selection_counts"])

    def test_three_hypotheses_preserve_all_fields_and_zero_trials(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 3)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in self.document["hypotheses"]))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "notation-namespace.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
