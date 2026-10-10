import json
import unittest

from tools.bifid_evidence import bifid
from tools.instruction_graphs import PRIMARY, ROOT, build_report, derived_source_maps, fixed_tokens, primary_layout, speech_map, text_location


class InstructionGraphTests(unittest.TestCase):
    def test_primary_regions_partition_every_nonseparator_symbol(self):
        layout, compact, unused_span = primary_layout()
        intervals = [region["normalized_span_zero_based_half_open"] for region in layout["regions"]]
        covered = [index for start, end in intervals for index in range(start, end)]
        omitted = sorted(set(range(len(compact))) - set(covered))
        self.assertEqual(omitted, [765, 829, 859])
        self.assertEqual(len(covered), len(set(covered)))
        self.assertEqual(layout["normalized_length"], 1075)
        self.assertFalse(layout["small_literal_present"])
        self.assertFalse(layout["hashtext_literal_present"])
        self.assertFalse(layout["faed570_literal_present"])

    def test_every_primary_region_round_trips_through_original_bytes(self):
        layout, compact, unused_span = primary_layout()
        original = PRIMARY.read_bytes()
        for region in layout["regions"]:
            start, end = region["utf8_byte_span_zero_based_half_open"]
            normalized_start, normalized_end = region["normalized_span_zero_based_half_open"]
            self.assertEqual("".join(original[start:end].decode().split()), compact[normalized_start:normalized_end])
        self.assertEqual([item["literal"] for item in layout["command_subphrases"]], ["shabef", "ourfirsthintisyourlastcommand", "shabef", "anstoo"])

    def test_unicode_locations_use_bytes_and_one_based_line_columns(self):
        location = text_location("é\nabc", 2, 5)
        self.assertEqual(location["utf8_byte_span_zero_based_half_open"], [3, 6])
        self.assertEqual((location["line_one_based"], location["column_one_based"]), (2, 1))

    def test_fixed_documented_tokenizations_preserve_the_source(self):
        unused_layout, compact, unused_span = primary_layout()
        for mask, length in [(505, 84), (1017, 83)]:
            tokens = fixed_tokens(compact[:91], mask)
            self.assertEqual(len(tokens), length)
            self.assertEqual("".join(token["token"] for token in tokens), compact[:91])
            self.assertTrue(all(token["token"] == compact[token["offset"]:token["offset"] + len(token["token"])] for token in tokens))

    def test_residual_and_frame_maps_retain_original_provenance(self):
        unused_layout, compact, span = primary_layout()
        maps = derived_source_maps(compact, span)
        branches = maps["branches"]
        residues = []
        for branch in branches:
            remaining = branch["residual_source_map"]
            residues.append("".join(entry["symbol"] for entry in remaining))
            self.assertTrue(all(compact[slice(*entry["normalized_span_zero_based_half_open"])] == entry["symbol"] for entry in remaining))
            covered = set()
            for item in remaining + branch["prime_marker_source_map"]:
                start, end = item["normalized_span_zero_based_half_open"]
                self.assertTrue(covered.isdisjoint(range(start, end)))
                covered.update(range(start, end))
            self.assertEqual(covered, set(range(91)))
        self.assertEqual(residues[0], residues[1] + "e")
        frame = maps["continuous_frame"]["source_map"]
        self.assertEqual(len(frame), 25)
        self.assertEqual([entry["logical_position_one_based"] for entry in frame[-2:]], [89, 97])
        self.assertEqual([entry["normalized_span_zero_based_half_open"] for entry in frame[-2:]], [[96, 97], [104, 105]])

    def test_every_bifid_output_coordinate_has_exact_input_dependencies(self):
        unused_layout, compact, span = primary_layout()
        evidence = derived_source_maps(compact, span)["source_bifid"]
        square = evidence["key_square"]
        decoded = bifid(compact[195:765], square, 570)
        for item in evidence["coordinate_source_map"]:
            coordinates = []
            for dependency in item["dependencies"]:
                symbol = compact[195 + dependency["faed_index_zero_based"]]
                row, column = divmod(square.index(symbol), 5)
                coordinates.append(row if dependency["source_coordinate"] == "row" else column)
            self.assertEqual(square[coordinates[0] * 5 + coordinates[1]], decoded[item["output_index_zero_based"]])
        self.assertEqual(evidence["prefix_input_indices"], [0, 1, 2, 3, 285, 286, 287, 288])
        self.assertEqual(evidence["public_prefix"], "btcseed")
        self.assertTrue(evidence["round_trip"])

    def test_speech_anchors_map_to_the_exact_public_encoded_fixture(self):
        evidence = speech_map()
        self.assertEqual(evidence["length"], 1539)
        self.assertEqual(evidence["literal_choice_occurrences"], 0)
        self.assertEqual([item["character_span_zero_based_half_open"][0] for item in evidence["anchors"][:4]], [1021, 1089, 1114, 1143])
        self.assertTrue(all(item["encoded_byte_span_zero_based_half_open"][1] - item["encoded_byte_span_zero_based_half_open"][0] == len(item["phrase"]) for item in evidence["anchors"]))

    def test_finite_hypotheses_and_scoped_provenance(self):
        report, occurrences = build_report()
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(report["hypotheses"]), 7)
        self.assertTrue(all(required <= item.keys() for item in report["hypotheses"]))
        self.assertTrue(report["corpus_inventory"]["small_only_secondary"])
        self.assertTrue(all(not quote["creator_authenticated"] for quote in report["corroboration"]["quotes"]))
        self.assertFalse(any("blockstream-" in entry["source"]["path"] or "mempool-" in entry["source"]["path"] for entry in occurrences))
        self.assertEqual(report["weighted_diagnostic"]["weighted_matrix_total"], 341)
        self.assertEqual(report["weighted_diagnostic"]["residual_totals"], {"505": 341, "1017": 336})
        self.assertEqual((report["new_cryptographic_trials"], report["new_trial_inputs"]), (0, 0))
        self.assertEqual(set(report["data_flow_graphs"]), {item["id"] for item in report["hypotheses"]})
        for graph in report["data_flow_graphs"].values():
            self.assertTrue(all(start in graph["nodes"] and end in graph["nodes"] and evidence for start, end, evidence in graph["edges"]))
        self.assertEqual(report["primary_layout"]["cosmic_container"]["normalized_length"], 1792)
        issue_mentions = [entry for entry in occurrences if "record_id" in entry]
        self.assertTrue(issue_mentions)
        self.assertTrue(all(entry["json_field"] == "body" and entry["record_created_at"] for entry in issue_mentions))

    def test_frozen_text_report_reproduces_without_mutation(self):
        report, occurrences = build_report()
        path = ROOT / "research/artifacts/cycle10/instruction-graphs-v3.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), report)
        inventory = ROOT / "research/artifacts/cycle10/instruction-occurrences-v3.jsonl"
        self.assertEqual([json.loads(line) for line in inventory.read_text().splitlines()], occurrences)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
