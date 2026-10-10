import json
import struct
import unittest
import zlib

from tools.instruction_graphs import ROOT
from tools.png_source_structure import OUTPUT, SIGNATURE, chunk_structure, report


def synthetic_chunk(name, data):
    type_bytes = name.encode("ascii")
    return struct.pack(">I", len(data)) + type_bytes + data + struct.pack(">I", zlib.crc32(type_bytes + data) & 0xffffffff)


def synthetic_png(extra=b""):
    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return SIGNATURE + synthetic_chunk("IHDR", header) + extra + synthetic_chunk("IDAT", b"synthetic-not-inflated") + synthetic_chunk("IEND", b"")


class PNGSourceStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_actual_chunk_sequence_dimensions_and_metadata_absence(self):
        structure = self.document["structure"]
        self.assertEqual([entry["type"] for entry in structure["chunks"]], ["IHDR", "sRGB", "gAMA", "pHYs", "IDAT", "IEND"])
        self.assertEqual((structure["image_header"]["width"], structure["image_header"]["height"]), (1048, 1556))
        self.assertEqual(structure["text_chunk_types"], [])
        self.assertEqual(structure["trailing_byte_count"], 0)

    def test_actual_chunks_cover_every_original_byte(self):
        payload = (ROOT / "research/sources/gsmg-puzzle.png").read_bytes()
        structure = self.document["structure"]
        offset = 8
        for entry in structure["chunks"]:
            start, end = entry["file_span_zero_based_half_open"]
            self.assertEqual(start, offset)
            self.assertEqual(end - start, entry["length"] + 12)
            self.assertEqual(payload[start + 4:start + 8].decode(), entry["type"])
            self.assertTrue(entry["CRC_valid"])
            offset = end
        self.assertEqual(offset, len(payload))

    def test_text_chunk_positive_controls_without_payload_decoding(self):
        for name in ("tEXt", "zTXt", "iTXt"):
            structure = chunk_structure(synthetic_png(synthetic_chunk(name, b"public-control")))
            self.assertEqual(structure["text_chunk_types"], [name])
            self.assertTrue(structure["chunk_data_not_decompressed_or_interpreted"])
            self.assertNotIn("public-control", json.dumps(structure))

    def test_corrupt_crc_and_truncated_chunks_are_rejected(self):
        payload = bytearray(synthetic_png())
        payload[20] ^= 1
        with self.assertRaisesRegex(ValueError, "CRC"):
            chunk_structure(bytes(payload))
        with self.assertRaisesRegex(ValueError, "Truncated"):
            chunk_structure(synthetic_png()[:-1])

    def test_terminal_suffix_is_counted_not_ignored(self):
        structure = chunk_structure(synthetic_png() + b"suffix")
        self.assertEqual(structure["trailing_byte_count"], 6)
        with self.assertRaisesRegex(ValueError, "terminal"):
            chunk_structure(synthetic_png()[:-12])

    def test_duplicate_header_and_nonconsecutive_data_are_rejected(self):
        header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "IHDR"):
            chunk_structure(synthetic_png(synthetic_chunk("IHDR", header)))
        payload = synthetic_png()[:-12] + synthetic_chunk("tEXt", b"control") + synthetic_chunk("IDAT", b"more") + synthetic_chunk("IEND", b"")
        with self.assertRaisesRegex(ValueError, "Nonconsecutive"):
            chunk_structure(payload)

    def test_object_roles_are_narrowly_classified_with_required_fields(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        hypotheses = self.document["hypotheses"]
        self.assertEqual([entry["status"] for entry in hypotheses], ["REJECTED", "INCONCLUSIVE"])
        self.assertTrue(all(required <= entry.keys() for entry in hypotheses))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "png-source-structure.json"
        original = path.read_bytes()
        self.assertEqual(json.loads(original), self.document)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
