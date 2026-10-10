import base64
import json
import unittest

from tools.architecture_reconstruction import OUTPUT, envelope, exact_tiling, factors, literal_location, report


class ArchitectureReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_inventory_exact_dimensions_and_different_same_size_objects(self):
        objects = {entry["id"]: entry for entry in self.document["object_inventory"]}
        self.assertEqual(len(objects), 14)
        self.assertEqual([objects[name]["exact_object"]["length"] for name in ("dbbi91", "matrix104", "frame25", "residual60", "faed570", "Bifid-body563", "speech1539", "checker149")], [91, 104, 25, 60, 570, 563, 1539, 149])
        self.assertNotEqual(objects["dbbi91"]["exact_object"]["sha256"], objects["checkertext91"]["exact_object"]["sha256"])

    def test_envelope_identity_and_conditional_plaintext_lengths(self):
        containers = self.document["envelope_metadata"]
        for name in ("inner", "small"):
            self.assertEqual([containers[name][field] for field in ("base64_characters", "blob_bytes", "ciphertext_bytes")], [128, 96, 80])
            self.assertEqual(containers[name]["if_CBC_PKCS7_plaintext_length_range"], [64, 79])
            self.assertTrue(containers[name]["mode_and_KDF_not_identified_by_header"])
        for field in ("salt_hex", "blob_sha256", "ciphertext_sha256"):
            self.assertNotEqual(containers["inner"][field], containers["small"][field])

    def test_malformed_public_envelopes_fail_closed(self):
        for encoded in (b"not base64!", base64.b64encode(b"Wrong___" + b"x" * 24), base64.b64encode(b"Salted__" + b"x" * 25)):
            with self.assertRaises(ValueError):
                envelope(encoded)

    def test_full_result_posts_are_identical_reposts_not_independent_discoveries(self):
        claims = self.document["Bifid_claims"]
        self.assertEqual(claims["full_output_occurrences"], 8)
        self.assertTrue(claims["identical_body_repost"])
        self.assertTrue(claims["reposts_are_not_independent_discoveries"])
        self.assertEqual(claims["claims"][0]["full_result_location"]["line_one_based"], 122253)
        self.assertEqual(claims["claims"][1]["full_result_location"]["line_one_based"], 124642)
        self.assertTrue(all(not entry["body_consumer_algorithm_supplied"] for entry in claims["claims"]))
        self.assertTrue(claims["secondary_layout_replacement"]["matrixsumlist_label_omitted_in_this_community_presentation"])
        self.assertEqual(claims["claims"][0]["exact_role_phrases"][3]["line_one_based"], 122258)

    def test_record_literal_locations_map_to_original_document(self):
        original = "first\nsecond\nbody phrase\n"
        mapped = literal_location("body phrase", "phrase", 13, original)
        self.assertEqual(mapped["line_one_based"], 3)
        self.assertEqual(mapped["character_span_zero_based_half_open"], [18, 24])
        with self.assertRaises(ValueError):
            literal_location("same same", "same")

    def test_exact_tiling_is_narrow_not_a_statistical_periodicity_claim(self):
        self.assertEqual(exact_tiling("abcabc")["exact_repeating_tile_lengths"], [3])
        self.assertEqual(exact_tiling("abcdef")["exact_repeating_tile_lengths"], [])
        for entry in self.document["exact_object_tiling"].values():
            self.assertEqual(entry["exact_repeating_tile_lengths"], [])
            self.assertTrue(entry["statistical_periodicity_not_estimated"])
        with self.assertRaises(ValueError):
            exact_tiling("")

    def test_recognition_cut_preserves_coordinates_but_splits_source_symbols(self):
        boundary = self.document["Bifid_boundary"]
        self.assertEqual(boundary["source_symbols_shared_across_cut"], [3, 288])
        self.assertEqual([boundary["prefix_coordinate_count"], boundary["body_coordinate_count"]], [14, 1126])
        self.assertTrue(boundary["all1140_source_coordinates_preserved"])
        self.assertTrue(boundary["seven_letter_cut_is_not_an_entire_source_symbol_boundary"])

    def test_dimensions_do_not_become_input_selection_or_alphabet_licenses(self):
        self.assertEqual(factors(563), [])
        self.assertIn([19, 30], factors(570))
        interfaces = self.document["typed_compatibility"]
        self.assertEqual(len(interfaces), 10)
        self.assertTrue(any(entry["status"] == "TYPE_COMPATIBLE_NOT_BOUND" for entry in interfaces))
        self.assertTrue(any(entry["status"] == "UNKNOWN_CONVERSION" for entry in interfaces))
        self.assertEqual(self.document["dimension_accounting"]["raw_characters_removed"], 31)

    def test_five_architectures_and_four_experiments_have_discriminators(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 5)
        self.assertEqual(len(self.document["experiments"]), 4)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        for experiment in self.document["experiments"]:
            self.assertTrue({"hypothesis", "input", "expected_observable", "falsification_condition", "result", "graph_effect"} <= experiment.keys())
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"], self.document["new_Bifid_decodes"], self.document["external_requests"]), (0, 0, 0, 0))

    def test_frozen_report_regenerates_exactly(self):
        payload = (OUTPUT / "architecture-reconstruction-v3.json").read_bytes()
        self.assertEqual(json.loads(payload), self.document)


if __name__ == "__main__":
    unittest.main()
