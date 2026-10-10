import json
import unittest

from tools.hint_order_audit import OUTPUT, PHRASES, PUBLIC_HINT, binary_hint_evidence, formatting_blocks, report, reversed_stream_decode, reversed_stream_encode
from tools.instruction_graphs import ROOT


class HintOrderTests(unittest.TestCase):
    def test_full_reversal_round_trips_all_byte_values(self):
        payload = bytes(range(256))
        self.assertEqual(reversed_stream_decode(reversed_stream_encode(payload)), payload)
        self.assertEqual(reversed_stream_encode(b"abc"), ["11000110", "01000110", "10000110"])

    def test_invalid_binary_groups_are_not_repaired(self):
        for groups in [[], ["001"], ["0000000x"]]:
            with self.assertRaises(ValueError):
                reversed_stream_decode(groups)

    def test_exact_hint_requires_octet_and_bit_order_reversal(self):
        evidence = binary_hint_evidence()
        self.assertEqual(evidence["decoded_public_text"], PUBLIC_HINT)
        self.assertEqual((evidence["octet_count"], evidence["bit_count"]), (161, 1288))
        self.assertEqual(evidence["controls"], {"identity_matches": False, "reverse_octet_order_only_matches": False, "reverse_bits_within_octets_only_matches": False, "full_reversal_matches": True})
        self.assertTrue(evidence["secondary_readme"]["normalized_transcription_matches"])
        self.assertEqual(len(evidence["full_transcript_correspondence"]["later_binary_reposts"]), 4)
        self.assertTrue(all(item["same_octets"] for item in evidence["full_transcript_correspondence"]["later_binary_reposts"]))

    def test_decoded_characters_are_mapped_to_original_binary_octets(self):
        evidence = binary_hint_evidence()
        original = (ROOT / evidence["source"]["path"]).read_bytes()
        for item in evidence["source_map"]:
            start, end = item["utf8_byte_span_zero_based_half_open"]
            encoded = original[start:end].decode()
            self.assertEqual(chr(int(encoded[::-1], 2)), item["symbol"])
            self.assertEqual(item["source_octet_index_zero_based"], 160 - item["output_index_zero_based"])

    def test_phrase_spans_account_for_complete_hint(self):
        evidence = binary_hint_evidence()
        regions = evidence["phrase_regions"]
        self.assertEqual([region["phrase"] for region in regions], PHRASES)
        self.assertEqual([region["decoded_span_zero_based_half_open"] for region in regions], [[0, 16], [16, 29], [29, 55], [55, 62], [62, 87], [87, 126], [126, 161]])
        self.assertEqual("".join(region["phrase"] for region in regions), PUBLIC_HINT)

    def test_inline_enter_matches_five_published_formatting_precedents(self):
        evidence = formatting_blocks()
        self.assertEqual(len(evidence["precedent_blocks"]), 5)
        self.assertTrue(all(block["nonfinal_lines_are64"] for block in evidence["precedent_blocks"]))
        self.assertEqual(evidence["embedded_fragment_lengths"], [64, 64])
        self.assertEqual(evidence["decoded_public_container_bytes"], 96)
        self.assertTrue(evidence["decoded_container_header_is_Salted"])
        self.assertTrue(evidence["content_bytes_unchanged_by_whitespace"])

    def test_frozen_artifact_regenerates_and_does_not_claim_runtime_edges(self):
        path = OUTPUT / "hint-instruction-order.json"
        original = path.read_bytes()
        document = report()
        self.assertEqual(json.loads(original), document)
        self.assertEqual(path.read_bytes(), original)
        self.assertTrue(all(edge[2] == "ORDERED_MENTIONS_NOT_VERIFIED_DATAFLOW" for edge in document["best_supported_data_flow"]["edges"]))
        self.assertEqual((document["new_cryptographic_trials"], document["new_trial_inputs"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
