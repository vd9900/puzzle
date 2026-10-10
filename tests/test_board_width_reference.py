import json
import unittest

from tools.board_width_reference import FEN, OUTPUT, fen_rank_widths, report
from tools.instruction_graphs import ROOT


class BoardWidthReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_original_width_clause_is_exact_and_local_to_alphabet_paragraph(self):
        clue = self.document["width_clue_reused"]
        start, end = clue["byte_span_zero_based_half_open"]
        payload = (ROOT / clue["original_source"]["path"]).read_bytes()
        self.assertEqual(payload[start:end], b"as wide as the first one seen")
        self.assertEqual(clue["belongs_to_paragraph_index_zero_based"], 4)

    def test_primary_fen_has_eight_files_and_eight_ranks_without_move(self):
        self.assertEqual(fen_rank_widths(FEN), [8] * 8)
        anchor = self.document["fen_anchor"]
        start, end = anchor["utf8_byte_span_zero_based_half_open"]
        self.assertEqual((ROOT / anchor["source"]["path"]).read_bytes()[start:end], FEN.encode())

    def test_invalid_fen_width_and_symbols_are_rejected(self):
        for value in (FEN.replace("B5KR", "B4KR"), FEN.replace("B5KR", "B9KR"), FEN.replace("B5KR/", "")):
            with self.assertRaises(ValueError):
                fen_rank_widths(value)

    def test_populated_first_row_is_not_codebook_column_count(self):
        codebook = self.document["codebook_domains"]
        self.assertEqual(codebook["filled_first_row_symbols"], 8)
        self.assertEqual(codebook["column_count"], 10)
        self.assertEqual(codebook["prefixed_row_domains"], [list(range(10)), list(range(10))])
        self.assertTrue(codebook["static_AST_inspection_only_no_codebook_or_decoder_execution"])

    def test_four_typed_objects_do_not_satisfy_all_antecedent_constraints(self):
        objects = self.document["typed_objects"]
        self.assertEqual([entry["known_width"] for entry in objects], [14, None, 8, 10])
        self.assertEqual([entry["codebook_width_equal"] for entry in objects], [False, None, False, True])
        self.assertTrue(all(not entry["authored_first_one_antecedent_assignment"] for entry in objects))
        self.assertFalse(objects[-1]["earlier_than_current_clue_in_known_pipeline"])

    def test_finite_width_readings_have_fields_without_new_variants(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual(len(hypotheses), 2)
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertEqual(self.document["search_space"]["new_board_variants"], 0)
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "board-width-reference.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
