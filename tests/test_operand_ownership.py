import json
import unittest

from tools.instruction_graphs import ROOT
from tools.operand_ownership import OUTPUT, graph_preflight, ownership_interfaces, report


class OperandOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_typed_objects_preserve_exact_primary_source_spans(self):
        primary = (ROOT / "research/sources/salphaseion.html").read_text()
        objects = self.document["source_objects"]
        labels = {entry["object"]: entry for entry in objects}
        self.assertEqual(labels["matrixsumlist"]["source_span"]["normalized_span_zero_based_half_open"], [91, 195])
        self.assertEqual(labels["thispassword"]["source_span"]["normalized_span_zero_based_half_open"], [830, 859])
        for name in ("first-shabef", "second-shabef", "ourfirsthintisyourlastcommand", "anstoo"):
            entry = labels[name]
            start, end = entry["source_span"]["character_span_zero_based_half_open"]
            self.assertEqual("".join(primary[start:end].split()), entry["source_span"]["literal"])

    def test_seven_operand_interfaces_remain_unbound(self):
        interfaces = self.document["interfaces"]
        self.assertEqual(len(interfaces), 7)
        self.assertTrue(all(not entry["explicit_source_bindings"] for entry in interfaces))
        self.assertTrue(all(not entry["input_ready"] for entry in interfaces))
        self.assertTrue(all(entry["required_bindings"] == entry["unresolved_bindings"] for entry in interfaces))

    def test_four_symbolic_graphs_do_not_claim_execution_or_selection(self):
        graphs = self.document["graphs"]
        self.assertEqual(len(graphs), 4)
        self.assertEqual(sum(len(graph["edges"]) for graph in graphs), 24)
        self.assertTrue(all(graph["symbolic_only"] for graph in graphs))
        self.assertTrue(all(not graph["source_bound_executable_construction"] for graph in graphs))
        self.assertEqual([graph["unresolved_binding_count"] for graph in graphs], [14, 13, 12, 12])
        self.assertTrue(all(not edge["newly_executed"] for graph in graphs for edge in graph["edges"]))

    def test_missing_interface_is_not_silently_accepted(self):
        with self.assertRaises(KeyError):
            graph_preflight({"interfaces": ["invented-interface"]}, ownership_interfaces())

    def test_speech_and_attribution_limits_are_propagated(self):
        constraints = self.document["speech_constraints_propagated"]
        self.assertEqual((constraints["baseline_covered_letters"], constraints["baseline_uncovered_letters"]), (1076, 463))
        self.assertTrue(constraints["question_repetition_not_a_selector"])
        self.assertFalse(constraints["literal_choice"])
        self.assertTrue(constraints["word_count_unspecified"])
        self.assertTrue(constraints["deictic_antecedent_not_uniquely_bound"])

    def test_small_and_bifid_are_objects_not_known_answers(self):
        objects = {entry["object"]: entry for entry in self.document["source_objects"]}
        self.assertFalse(objects["SMALL"]["primary_literal_present"])
        self.assertTrue(objects["SMALL"]["container_is_input_not_known_answer"])
        self.assertEqual(objects["Bifid-object"]["prefix_input_indices"], [0, 1, 2, 3, 285, 286, 287, 288])
        self.assertTrue(objects["Bifid-object"]["prefix_does_not_bind_output_consumer"])
        self.assertFalse(objects["HASHTHETEXT"]["argument_bound"])

    def test_finite_hypotheses_have_all_required_fields(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 4)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertEqual(self.document["thispassword_scope_survivors"], ["BACKWARD_REFERENCE_TO_SELECTED_OBJECT", "FORWARD_LABEL_FOR_FOLLOWING_RECIPE"])
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "operand-ownership.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
