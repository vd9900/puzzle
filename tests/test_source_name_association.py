import json
import unittest

from tools.instruction_graphs import ROOT
from tools.source_name_association import OUTPUT, report


class SourceNameAssociationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_original_quote_body_and_two_export_locations_are_exact(self):
        quote = self.document["original_quote"]
        self.assertEqual(quote["public_text"], '"Globally supporting my generation"')
        self.assertEqual(quote["creator_record"]["line_one_based"], 763)
        self.assertEqual(quote["original_chat_record"]["line_one_based"], 21639)
        for key in ("creator_record", "original_chat_record"):
            entry = quote[key]
            start, end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual((ROOT / entry["source"]["path"]).read_bytes()[start:end], quote["public_text"].encode())

    def test_one_natural_initial_correspondence_matches_primary_name(self):
        correspondence = self.document["one_initial_correspondence"]
        self.assertEqual(correspondence["source_words"], ["Globally", "supporting", "my", "generation"])
        self.assertEqual(correspondence["initials"], "GSMG")
        self.assertTrue(correspondence["matches_primary_public_source_label"])
        self.assertTrue(correspondence["no_alternative_word_order_or_initial_encoding"])

    def test_primary_title_is_exact_and_image_owner_not_extracted(self):
        title = self.document["primary_title"]
        start, end = title["utf8_byte_span_zero_based_half_open"]
        self.assertEqual((ROOT / title["source"]["path"]).read_bytes()[start:end], b"<title>GSMG Puzzle</title>")
        self.assertTrue(self.document["image_owner_reused"]["no_image_text_or_identifier_extraction"])

    def test_five_context_records_do_not_authenticate_reply_or_operand(self):
        context = self.document["context"]
        self.assertEqual(len(context), 5)
        self.assertTrue(all(not entry["reply_target_metadata_preserved"] for entry in context))
        self.assertTrue(self.document["no_authored_literal_input_or_consumer_assignment"])

    def test_three_name_roles_have_fields_without_trial_or_acronym_variants(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 3)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"], self.document["new_acronym_variants"]), (0, 0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "source-name-association.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
