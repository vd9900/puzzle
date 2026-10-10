import json
import unittest

from tools.first_piece_domain import OUTPUT, report
from tools.instruction_graphs import ROOT


class FirstPieceDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_initial_response_is_png_not_preserved_html(self):
        domain = self.document["capture_domain"]
        self.assertEqual(domain["manifest_entries_considered"], 93)
        self.assertEqual(domain["initial_url_capture_names"], ["gsmg-puzzle.png"])
        self.assertEqual(domain["capture"]["content_type"], "image/png")
        self.assertTrue(domain["png_signature_verified"])
        self.assertFalse(domain["initial_html_response_preserved"])
        self.assertTrue(domain["capture_is_not_proof_of_2019_or_2020_HTTP_response_type"])

    def test_three_original_copies_are_identical_whole_images(self):
        copies = self.document["capture_domain"]["copies"]
        self.assertEqual(len(copies), 3)
        self.assertEqual(len({entry["source"]["sha256"] for entry in copies}), 1)
        self.assertTrue(all(entry["dimensions"] == [1048, 1556] for entry in copies))

    def test_secondary_anchors_reconstruct_exact_bytes_and_lines(self):
        anchors = self.document["secondary_anchors"]
        self.assertEqual(len(anchors), 10)
        for entry in anchors:
            path = ROOT / entry["source"]["path"]
            document = path.read_text()
            start, end = entry["character_span_zero_based_half_open"]
            byte_start, byte_end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual(document[start:end], entry["literal"])
            self.assertEqual(path.read_bytes()[byte_start:byte_end], entry["literal"].encode())
            self.assertEqual(entry["line_one_based"], document.count("\n", 0, start) + 1)

    def test_eight_images_and_headings_belong_to_later_pages(self):
        pages = self.document["page_inventory"]["pages"]
        self.assertEqual([len(entry["body_image_references"]) for entry in pages], [8, 0, 0])
        self.assertEqual([[heading["text"] for heading in entry["headings"]] for entry in pages], [[], ["PHASE 2", "PHASE 3"], ["SalPhaseIon", "Cosmic Duality"]])
        self.assertEqual(self.document["search_space"]["later_headings"], 4)
        self.assertEqual([entry["textarea_count"] for entry in pages], [0, 2, 2])
        for page in pages:
            document = (ROOT / page["source"]["path"]).read_text()
            for entry in page["body_image_references"] + page["comments"]:
                start, end = entry["character_span_zero_based_half_open"]
                self.assertEqual(document[start:end], entry["markup"])
            self.assertFalse(page["is_initial_puzzle_response"])

    def test_original_resource_pointer_is_not_a_region_selector(self):
        pointer = self.document["creator_pointer"]
        self.assertEqual(pointer["literal"], "Gsmg.io/puzzle")
        self.assertEqual(pointer["creator_record"]["line_one_based"], 165)
        self.assertEqual(pointer["original_chat_record"]["line_one_based"], 3572)
        self.assertTrue(pointer["a_resource_pointer_does_not_select_an_image_region"])

    def test_frozen_regions_share_owner_without_new_masks(self):
        ownership = self.document["image_ownership"]
        self.assertEqual(len(ownership["regions"]), 3)
        self.assertTrue(all(entry["owner"] == ownership["source"] for entry in ownership["regions"]))
        self.assertTrue(all(not entry["authored_region_selection"] for entry in ownership["regions"]))
        self.assertTrue(ownership["grid_is_a_subobject_not_the_whole_original_response"])
        self.assertTrue(ownership["no_identifier_or_QR_decoding_or_use"])

    def test_finite_hypotheses_have_fields_without_executed_routes(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertTrue(all(entry["status"] == "INCONCLUSIVE" for entry in hypotheses))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"], self.document["new_routes"]), (0, 0, 0))

    def test_report_regenerates_without_mutation(self):
        path = OUTPUT / "first-piece-domain-v2.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
