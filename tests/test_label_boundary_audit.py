import json
import unittest

from tools.instruction_graphs import primary_layout
from tools.label_boundary_audit import OUTPUT, report


class LabelBoundaryAuditTests(unittest.TestCase):
    def test_typed_regions_and_delimiters_cover_exact_primary(self):
        document = report()
        self.assertEqual((len(document["regions"]), len(document["z_delimiters"]), document["primary_compact_length"]), (10, 3, 1075))
        self.assertTrue(document["typed_regions_reconstruct_primary_exactly"])
        self.assertEqual([entry["normalized_span_zero_based_half_open"] for entry in document["z_delimiters"]], [[765, 766], [829, 830], [859, 860]])
        self.assertEqual(document["encoded_container_internal_z_is_not_delimiter"][0]["normalized_span_zero_based_half_open"], [958, 959])

    def test_all13_label_octets_match_original_source(self):
        document = report()
        unused_layout, compact, unused_span = primary_layout()
        binary = document["binary_label"]
        self.assertEqual((binary["encoded_length"], binary["decoded_length"]), (104, 13))
        self.assertEqual("".join(entry["decoded_character"] for entry in binary["source_octets"]), "matrixsumlist")
        for entry in binary["source_octets"]:
            start, end = entry["normalized_span_zero_based_half_open"]
            self.assertEqual(compact[start:end].translate(str.maketrans("ab", "01")), entry["original_binary_octet"])
        self.assertTrue(binary["exact_round_trip"])

    def test_borrowed_positions_are_original_encoded_label_data(self):
        witnesses = report()["borrowed_marker_witnesses"]
        self.assertEqual([(entry["mask"], entry["logical_position_one_based"], entry["original_marker_source"]["binary_offset_zero_based"], entry["decoded_label_character"]) for entry in witnesses], [(505, 89, 4, "m"), (505, 97, 12, "a"), (1017, 89, 5, "m"), (1017, 97, 13, "a")])
        self.assertTrue(all(entry["not_an_instruction_to_remove_label_bits"] for entry in witnesses))

    def test_adjacency_and_local_sha_mapping_do_not_define_arguments(self):
        document = report()
        self.assertTrue(document["dbbi_to_binary_and_binary_to_faed_have_no_explicit_separator"])
        self.assertTrue(document["primary_sequence_has_no_operator_argument_syntax"])
        self.assertTrue(document["known_operator_mapping_is_local_not_uniform"]["not_a_global_substitution"])
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))

    def test_two_type_hypotheses_have_required_fields_and_limits(self):
        document = report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(document["hypotheses"]), 2)
        self.assertTrue(all(required <= hypothesis.keys() for hypothesis in document["hypotheses"]))
        self.assertTrue(all(hypothesis["status"] == "INCONCLUSIVE" for hypothesis in document["hypotheses"]))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "label-boundary-audit.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report())
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
