import json
import unittest

from tools.matrixsumlist_receiver_audit import OUTPUT, report


class MatrixsumlistReceiverAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_recovered_inventory_has_no_exact14_object_or_known_consumer(self):
        recovered = self.document["recovered_objects"]
        self.assertEqual(recovered["count"], 14)
        self.assertEqual(recovered["exact_size14_objects"], [])
        self.assertEqual(recovered["matrixsumlist_known_downstream_consumers"], [])

    def test_fixed_shapes_do_not_supply_an_independent14_receiver(self):
        self.assertEqual(self.document["fixed_shape_independent_direct14_receivers"], [])
        candidates = {entry["candidate"]: entry for entry in self.document["fixed_shape_candidates"]}
        self.assertEqual(candidates["faed570 matrix"]["shape"], [38, 15])
        self.assertEqual(candidates["Bifid coordinate planes"]["shape"], [19, 15])
        self.assertFalse(candidates["original grid row or column slots"]["independently_downstream_of_matrixsumlist"])

    def test_faed_bifid_do_not_expose_a14_or_variable_input_port(self):
        assessment = self.document["faed_bifid_assessment"]
        self.assertTrue(assessment["fifteen_column_structure_verified"])
        self.assertFalse(assessment["fourteen_value_input_contract"])
        self.assertFalse(assessment["variable_length_input_contract"])
        self.assertFalse(assessment["matrixsumlist_binding"])

    def test_variable_length_compatibility_is_not_binding(self):
        self.assertEqual(self.document["variable_length_explicitly_bound_receivers"], [])
        candidates = {entry["candidate"]: entry for entry in self.document["variable_length_candidates"]}
        self.assertEqual(candidates["password/hash byte API"]["classification"], "TYPE_COMPATIBLE_NOT_BOUND")
        self.assertFalse(candidates["first SHA input"]["explicit_matrixsumlist_binding"])
        self.assertFalse(candidates["answer SHA input"]["explicit_matrixsumlist_binding"])

    def test_architect_words_are_only_a_weak_semantic_successor(self):
        successor = self.document["ordered_hint_successor"]
        self.assertEqual((successor["from"], successor["to"]), ("matrixsumlist", "lastwordsbeforearchichoice"))
        self.assertEqual(successor["relationship"], "VERIFIED MENTION ORDER")
        self.assertEqual(successor["receiver_edge"], "UNKNOWN")
        architect = next(entry for entry in self.document["variable_length_candidates"] if entry["candidate"].startswith("lastwords"))
        self.assertEqual(set(architect["unresolved_contract"]), {"source_identity", "choice_anchor", "word_count", "word_boundaries"})

    def test_receiver_hypothesis_is_rejected_but_consumer_stays_unknown(self):
        classification = self.document["classification"]
        self.assertEqual(classification["independently_specified_receiver"], "REJECTED within the preserved corpus")
        self.assertEqual(classification["matrixsumlist_output_consumer"], "UNKNOWN")
        self.assertIn("remove any asserted", self.document["graph_effect"])

    def test_non_executing_scope_and_frozen_artifact(self):
        for field in ("numeric_sum_vectors_calculated", "numeric_mapping_trials", "candidate_material_generated", "private_key_operations", "aes_operations"):
            self.assertEqual(self.document[field], 0)
        path = OUTPUT / "matrixsumlist-receiver-audit.json"
        if path.exists():
            before = path.read_bytes()
            self.assertEqual(json.loads(before), self.document)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
