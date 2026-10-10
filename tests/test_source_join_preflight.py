import json
import unittest

from tools.instruction_graphs import ROOT
from tools.source_join_preflight import ARTIFACT_NAME, OUTPUT, checkerboard_source_map, fixed_selection, join_report, source_paragraph_roles


class SourceJoinTests(unittest.TestCase):
    def test_selection_and_complement_partition_source_exactly(self):
        self.assertEqual(fixed_selection("abcdef", [0, 2, 5]), ("acf", "bde"))
        self.assertEqual(fixed_selection("abc", []), ("", "abc"))

    def test_indices_are_not_reordered_repaired_or_wrapped(self):
        for indices in [[0, 0], [2, 0], [-1], [3]]:
            with self.assertRaises(ValueError):
                fixed_selection("abc", indices)

    def test_checkerboard_numeric_source_maps_and_round_trips(self):
        decoded, evidence = checkerboard_source_map()
        original = (ROOT / evidence["source"]["path"]).read_bytes()
        self.assertEqual((evidence["numeric_length"], evidence["decoded_length"]), (149, 91))
        self.assertEqual("".join(item["symbol"] for item in evidence["output_source_map"]), decoded)
        for item in evidence["output_source_map"]:
            start, end = item["numeric_byte_span_in_encoded_fixture_zero_based_half_open"]
            self.assertEqual(original[start:end].decode(), item["code"])

    def test_only_the_published_raw_branch_reproduces_the_community_quote(self):
        document = join_report()
        results = document["results"]
        self.assertEqual([result["raw_selected_length"] for result in results], [30, 31])
        self.assertEqual([result["raw_omitted_length"] for result in results], [61, 60])
        self.assertEqual([result["raw_result_equals_published_quote"] for result in results], [False, True])
        self.assertTrue(all(not result["logical_result_equals_published_quote"] for result in results))
        self.assertEqual([result["logical_selected_length"] for result in results], [23, 23])

    def test_partial_yang_is_shared_but_complete_checkpoint_is_absent(self):
        document = join_report()
        for result in document["results"]:
            literals = {item["literal"]: item for item in result["literal_checkpoint_tests"]}
            self.assertEqual(literals["yang"]["count"], 1)
            self.assertEqual(literals["yang"]["source_positions_zero_based"], [[6, 10, 11, 13]])
            self.assertTrue(all(literals[word]["count"] == 0 for word in ["yin", "ying", "yinyang", "yingyang"]))
        self.assertTrue(document["branch_yang_matches_are_not_independent"])

    def test_original_paragraphs_distinguish_speech_numeric_and_container_branches(self):
        evidence = source_paragraph_roles()
        self.assertEqual([record["byte_span_zero_based_half_open"] for record in evidence["paragraphs"]], [[0, 332], [336, 443], [447, 1986], [1990, 2139], [2143, 2288], [2292, 2422]])
        self.assertTrue(evidence["paragraphs"][3]["numeric_only"])
        self.assertTrue(evidence["91_letter_text_is_not_immediately_adjacent_to_container"])
        self.assertTrue(evidence["no_primary_choice_word_in_any_paragraph"])

    def test_original_instruction_anchor_spans_reconstruct_exact_bytes(self):
        evidence = source_paragraph_roles()
        original = (ROOT / evidence["source"]["path"]).read_bytes()
        for key in ["encoding_clue", "checkerboard_width_clue"]:
            anchor = evidence[key]
            start, end = anchor["byte_span_zero_based_half_open"]
            self.assertEqual(original[start:end].decode(), anchor["literal"])

    def test_frozen_audit_regenerates_without_new_search_inputs(self):
        path = OUTPUT / ARTIFACT_NAME
        original = path.read_bytes()
        document = join_report()
        self.assertEqual(json.loads(original), document)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual((document["search_space"]["new_cryptographic_trials"], document["search_space"]["new_trial_inputs"]), (0, 0))
        self.assertEqual(len(document["missing_edges"]), 5)


if __name__ == "__main__":
    unittest.main()
