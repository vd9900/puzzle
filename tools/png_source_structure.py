import json
import struct
import zlib

from tools.instruction_graphs import ROOT, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle19"
SIGNATURE = b"\x89PNG\r\n\x1a\n"
TEXT_TYPES = {"tEXt", "zTXt", "iTXt"}
NEXT_TEST = "Audit the preserved original-image text regions against the exact earlier source clue First/zero and firsthint/lastcommand wording, using only already mapped primary text and fixed original creator records. Require a source-authored distinction between command identity and literal argument identity; do not normalize, hash or extract new trial strings."


def chunk_structure(payload):
    if not payload.startswith(SIGNATURE):
        raise ValueError("Missing PNG signature")
    offset = len(SIGNATURE)
    chunks = []
    image_header = None
    image_data_closed = False
    image_data_seen = False
    while offset < len(payload):
        if len(payload) - offset < 12:
            raise ValueError("Truncated PNG chunk header")
        length = struct.unpack_from(">I", payload, offset)[0]
        end = offset + length + 12
        if end > len(payload):
            raise ValueError("Truncated PNG chunk payload")
        type_bytes = payload[offset + 4:offset + 8]
        if not all(65 <= value <= 90 or 97 <= value <= 122 for value in type_bytes):
            raise ValueError("Invalid PNG chunk type")
        name = type_bytes.decode("ascii")
        if type_bytes[2] & 32:
            raise ValueError("Invalid PNG reserved type bit")
        stored_crc = struct.unpack_from(">I", payload, end - 4)[0]
        actual_crc = zlib.crc32(payload[offset + 4:end - 4]) & 0xffffffff
        if actual_crc != stored_crc:
            raise ValueError("PNG chunk CRC mismatch")
        if not chunks and name != "IHDR":
            raise ValueError("PNG does not begin with IHDR")
        if name == "IHDR":
            if chunks or length != 13:
                raise ValueError("Duplicate or malformed IHDR")
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack_from(">IIBBBBB", payload, offset + 8)
            valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
            if not width or not height or color_type not in valid_depths or bit_depth not in valid_depths[color_type] or compression != 0 or filtering != 0 or interlace not in (0, 1):
                raise ValueError("Invalid PNG header fields")
            image_header = {"width": width, "height": height, "bit_depth": bit_depth, "color_type": color_type, "compression": compression, "filtering": filtering, "interlace": interlace}
        if name == "IDAT":
            if image_data_closed:
                raise ValueError("Nonconsecutive PNG image-data chunks")
            image_data_seen = True
        elif image_data_seen:
            image_data_closed = True
        chunks.append({
            "type": name, "length": length, "file_span_zero_based_half_open": [offset, end],
            "data_span_zero_based_half_open": [offset + 8, end - 4], "CRC_valid": True,
            "ancillary": bool(type_bytes[0] & 32), "text_chunk": name in TEXT_TYPES,
        })
        offset = end
        if name == "IEND":
            if length != 0 or not image_data_seen:
                raise ValueError("Malformed PNG terminal chunk or missing image data")
            break
    if not chunks or chunks[-1]["type"] != "IEND":
        raise ValueError("Missing PNG terminal chunk")
    return {
        "signature_span_zero_based_half_open": [0, 8], "chunks": chunks,
        "image_header": image_header, "terminal_offset": offset, "total_bytes": len(payload),
        "trailing_byte_count": len(payload) - offset,
        "text_chunk_types": [entry["type"] for entry in chunks if entry["text_chunk"]],
        "ancillary_chunk_types": [entry["type"] for entry in chunks if entry["ancillary"]],
        "chunk_data_not_decompressed_or_interpreted": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle19/first-piece-domain-v2.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C19-FIRST-PIECE-DOMAIN" or "PNG container structure" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen PNG source task")
    image = ROOT / "research/sources/gsmg-puzzle.png"
    evidence = [source(image), source(preceding)]
    locations = ["research/sources/gsmg-puzzle.png", "research/artifacts/cycle19/first-piece-domain-v2.json"]
    structure = chunk_structure(image.read_bytes())
    hypotheses = [
        {"id": "C19-PNG-METADATA-TEXT", "status": "REJECTED" if not structure["text_chunk_types"] else "INCONCLUSIVE", "hypothesis": "HASHTHETEXT refers to a standard PNG textual metadata object in the preserved initial image", "assumptions": ["The proposed object must be a tEXt, zTXt or iTXt chunk in the unchanged PNG"], "confidence": "HIGH bounded container result; UNKNOWN overall instruction role", "contradictions": ["No standard textual chunk is present in the actual preserved PNG"] if not structure["text_chunk_types"] else ["Chunk presence alone cannot bind the instruction"], "output": "Presence or absence of standard textual metadata, not a hash input"},
        {"id": "C19-PNG-VISIBLE-TEXT", "status": "INCONCLUSIVE", "hypothesis": "HASHTHETEXT refers to visible original-image text rather than PNG textual metadata", "assumptions": ["The instruction may refer to raster-visible text", "Earlier secondary image-text entry interpretation remains distinct from a final argument"], "confidence": "MEDIUM object availability; UNKNOWN final source/argument binding", "contradictions": ["Metadata absence does not prove a visible-text selection", "Source includes several visible regions without an authored selector"], "output": "Surviving visible-object interpretation without normalization, extraction or hashing"},
    ]
    hypotheses = [entry | {
        "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["read unchanged PNG", "validate chunk structure and CRCs", "classify text-object availability"],
        "input": "The original public PNG container only", "next_test": NEXT_TEST,
    } for entry in hypotheses]
    return {
        "id": "C19-PNG-SOURCE-STRUCTURE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "PNG container structure provides an additional textual source object for the instruction construction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Standard PNG metadata and trailing bytes are bounded public container objects", "No image-data decoding or alternate traversal is needed"],
        "operation_order": ["validate frozen source-domain task", "parse signature and length-delimited chunks", "verify every CRC and exact terminal coverage", "classify textual/ancillary chunk presence", "retain visible-text and other instruction arguments as unbound"],
        "input": "One unchanged original public PNG and preceding source-domain report",
        "output": "Exact PNG chunk spans, CRC results and text-object availability",
        "confidence": "HIGH byte/container properties; UNKNOWN intended command or argument",
        "structure": structure, "hypotheses": hypotheses,
        "result": "All preserved PNG chunks have valid CRCs. Standard textual metadata presence and terminal coverage are recorded exactly; no raster data, textual payload, QR symbol or trial input is decoded. Absence of standard text chunks rejects only the bounded metadata-text interpretation, not all steganography or visible-text instruction roles.",
        "contradictions": ["Standard metadata absence cannot identify a visible-text region or final argument", "Container validity is not proof of the puzzle creator's intended data flow"],
        "next_test": NEXT_TEST,
        "search_space": {"unchanged_images": 1, "chunks": len(structure["chunks"]), "text_chunks": len(structure["text_chunk_types"]), "declared_object_roles": 2, "pixel_decodes": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "png-source-structure.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "chunk_types": [entry["type"] for entry in document["structure"]["chunks"]], "text_chunks": document["search_space"]["text_chunks"], "trailing_bytes": document["structure"]["trailing_byte_count"], "new_trial_inputs": 0}, indent=2))


if __name__ == "__main__":
    main()
