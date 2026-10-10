import json
import unittest

from tools.instruction_graphs import ROOT
from tools.whole_object_accountability import OUTPUT, report


class WholeObjectAccountabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_frozen_ten_regions_and_three_delimiters_cover_all_characters(self):
        partition = self.document["frozen_primary_partition"]
        self.assertEqual(len(partition["regions"]), 10)
        self.assertEqual(len(partition["delimiters"]), 3)
        self.assertEqual((partition["region_characters"], partition["delimiter_characters"], partition["total_characters"]), (1072, 3, 1075))
        self.assertTrue(partition["no_partition_or_codec_recomputed"])

    def test_forty_role_comparisons_are_partial_not_complete_graph_claims(self):
        graphs = self.document["graph_accountability"]
        self.assertEqual(len(graphs), 4)
        self.assertEqual(sum(len(entry["region_role_rows"]) for entry in graphs), 40)
        self.assertTrue(all(entry["graph_is_a_partial_symbolic_fragment_not_a_complete_claim"] for entry in graphs))
        self.assertTrue(all(entry["absent_regions_do_not_by_themselves_reject_partial_graph"] for entry in graphs))
        self.assertTrue(all(not entry["complete_source_bound_execution"] for entry in graphs))

    def test_symbolic_roles_do_not_create_end_to_end_consumers(self):
        rows = [row for graph in self.document["graph_accountability"] for row in graph["region_role_rows"]]
        self.assertTrue(any(row["mapped_symbolic_nodes"] for row in rows))
        self.assertTrue(any(not row["mapped_symbolic_nodes"] for row in rows))
        self.assertTrue(all(not row["source_bound_end_to_end_consumer"] for row in rows))
        self.assertTrue(all(row["mapping_is_analyst_role_alias_not_authored_assignment"] for row in rows))

    def test_Bifid_prefix_and_full_output_accounting_remain_distinct(self):
        output = self.document["Bifid_object_reused"]
        self.assertEqual((output["full_output_length"], output["recognized_prefix_length"], output["remaining_body_length"]), (570, 7, 563))
        self.assertEqual(output["prefix_input_indices"], [0, 1, 2, 3, 285, 286, 287, 288])
        self.assertTrue(output["all570_dependencies_already_mapped"])
        self.assertFalse(output["complete_output_consumer_authored"])
        self.assertTrue(output["no_Bifid_transform_or_statistical_control_repeated"])

    def test_finite_accountability_readings_have_fields_without_new_transform(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"], self.document["new_source_transformations"]), (0, 0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "whole-object-accountability.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
