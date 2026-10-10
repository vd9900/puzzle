import base64
import json
import re

from tools.instruction_graphs import HEADER, ROOT, primary_layout, source, text_location, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle11"
PUBLIC_HINT = "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangwewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingitverylaststepisatruegiveawaypromised"
PHRASES = ["yellowblueprimes", "matrixsumlist", "lastwordsbeforearchichoice", "yinyang", "wewontgiveawaythepassword", "itsinfrontofyoureyesbutyourenotseeingit", "verylaststepisatruegiveawaypromised"]


def reversed_stream_decode(octets):
    if not octets or any(re.fullmatch(r"[01]{8}", octet) is None for octet in octets):
        raise ValueError("Expected complete binary octets only")
    reversed_stream = "".join(octets)[::-1]
    return bytes(int(reversed_stream[offset:offset + 8], 2) for offset in range(0, len(reversed_stream), 8))


def reversed_stream_encode(payload):
    stream = "".join(format(value, "08b") for value in payload)[::-1]
    return [stream[offset:offset + 8] for offset in range(0, len(stream), 8)]


def archived_hint(path):
    document = path.read_text()
    candidates = []
    for match in re.finditer(r"(?m)^00100110 10100110(?: [01]{8})+$", document):
        headers = list(HEADER.finditer(document, 0, match.start()))
        if headers and headers[-1].group() == "=== [23.02.2023 18:20:03 UTC-05:00] Jrk Bgrt":
            candidates.append((match, headers[-1].group()))
    if len(candidates) != 1:
        raise ValueError("Expected one original dated creator-labeled hint, excluding later reposts")
    match, header = candidates[0]
    octets = list(re.finditer(r"[01]{8}", match.group()))
    return document, match, octets, header


def binary_hint_evidence():
    path = ROOT / "research/evidence/cycle02/_work__creator_jrk.txt"
    document, match, octets, header = archived_hint(path)
    strings = [octet.group() for octet in octets]
    decoded = reversed_stream_decode(strings).decode("ascii")
    if decoded != PUBLIC_HINT or reversed_stream_encode(decoded.encode()) != strings:
        raise ValueError("The exact public hint and inverse source encoding differ")
    chat_path = ROOT / "research/evidence/cycle02/_work__chat_transcript.txt"
    chat, chat_match, chat_octets, chat_header = archived_hint(chat_path)
    if [octet.group() for octet in chat_octets] != strings:
        raise ValueError("Creator-labeled export and full transcript differ")
    reposts = []
    for copied in re.finditer(r"(?m)^00100110 10100110(?: [01]{8})+$", chat):
        if copied.start() == chat_match.start():
            continue
        copied_headers = list(HEADER.finditer(chat, 0, copied.start()))
        reposts.append({"header": copied_headers[-1].group() if copied_headers else None, "line_one_based": chat.count("\n", 0, copied.start()) + 1, "same_octets": copied.group().split() == strings, "not_independent_creator_evidence": True})
    source_map = []
    for output_index, symbol in enumerate(decoded):
        source_octet_index = len(strings) - 1 - output_index
        octet = octets[source_octet_index]
        source_map.append({"output_index_zero_based": output_index, "symbol": symbol, "source_octet_index_zero_based": source_octet_index, "bit_order": "source octet bits7..0 become decoded bits0..7", **text_location(document, match.start() + octet.start(), match.start() + octet.end())})
    regions = []
    for phrase in PHRASES:
        start = decoded.index(phrase)
        end = start + len(phrase)
        first_octet = octets[len(strings) - end]
        last_octet = octets[len(strings) - 1 - start]
        regions.append({"phrase": phrase, "decoded_span_zero_based_half_open": [start, end], "original_octet_span_zero_based_half_open": [len(strings) - end, len(strings) - start], "source_order": "descending octet indices and reversed bits", **text_location(document, match.start() + first_octet.start(), match.start() + last_octet.end())})
    readme_path = ROOT / "research/sources/maintained-README.md"
    readme = readme_path.read_text()
    section_start = readme.index("## 2023-02-23 - Official Hint")
    block = re.search(r"```\s*\n(.*?)\n```", readme[section_start:], re.S)
    rendered = "".join(block.group(1).split())
    if rendered != decoded:
        raise ValueError("Maintained prose transcription differs from exact reversal")
    image = ROOT / "research/sources/maintained-hints__2023-02-23.png"
    return {
        "source": source(path), "source_header": header, "raw_binary_source": text_location(document, match.start(), match.end()),
        "classification": "CREATOR_ATTRIBUTED_ARCHIVED_HINT_CORROBORATED_BY_SCREENSHOT; NOT_SIGNED_AUTHENTICATION",
        "octet_count": len(strings), "bit_count": len(strings) * 8, "decoded_public_text": decoded,
        "transform": "Reverse the complete1288-bit stream, then decode MSB-first ASCII octets",
        "equivalent_transform": "Reverse octet order AND reverse bits within each octet",
        "round_trip": True, "source_map": source_map, "phrase_regions": regions,
        "controls": {"identity_matches": bytes(int(octet, 2) for octet in strings) == decoded.encode(), "reverse_octet_order_only_matches": bytes(int(octet, 2) for octet in strings[::-1]) == decoded.encode(), "reverse_bits_within_octets_only_matches": bytes(int(octet[::-1], 2) for octet in strings) == decoded.encode(), "full_reversal_matches": reversed_stream_decode(strings) == decoded.encode()},
        "full_transcript_correspondence": {"source": source(chat_path), "header": chat_header, **text_location(chat, chat_match.start(), chat_match.end()), "same_octets": True, "exports_are_not_independent_creator_authentication": True, "later_binary_reposts": reposts},
        "screenshot": {"source": source(image), "visible_month_day": "February23", "year_from_transcript_and_archive": "2023", "speaker_label": "Jrk Bgrt/admin", "binary_body_pixel_rectangle_xyxy": [64, 60, 507, 750], "visual_label_and_prefix_suffix_reviewed": True, "not_an_independent_OCR_verification_of_all_octets": True},
        "secondary_readme": {"source": source(readme_path), **text_location(readme, section_start + block.start(1), section_start + block.end(1)), "normalized_transcription_matches": True, "displayed_spaces_not_in_original_decoded_bytes": True},
    }


def formatting_blocks():
    blocks = []
    page = ROOT / "research/sources/phase2.html"
    document = page.read_text()
    for index, match in enumerate(re.finditer(r"<textarea\b[^>]*>(.*?)</textarea>", document, re.S | re.I)):
        lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
        compact = "".join(lines)
        if not compact.startswith("U2FsdGVkX1"):
            continue
        base64.b64decode(compact, validate=True)
        blocks.append({"source": source(page), "object": f"textarea-{index}", "line_lengths": list(map(len, lines)), "nonfinal_lines_are64": all(len(line) == 64 for line in lines[:-1]), **text_location(document, match.start(1), match.end(1))})
    sal = ROOT / "research/sources/salphaseion.html"
    sal_document = sal.read_text()
    matches = list(re.finditer(r"<textarea\b[^>]*>(.*?)</textarea>", sal_document, re.S | re.I))
    lines = [line.strip() for line in matches[1].group(1).splitlines() if line.strip()]
    base64.b64decode("".join(lines), validate=True)
    blocks.append({"source": source(sal), "object": "Cosmic textarea", "line_lengths": list(map(len, lines)), "nonfinal_lines_are64": all(len(line) == 64 for line in lines[:-1]), **text_location(sal_document, matches[1].start(1), matches[1].end(1))})
    for filename in ("phase3.txt", "phase32.txt"):
        path = ROOT / "research/artifacts" / filename
        text = path.read_bytes().decode("latin-1")
        for match in re.finditer(r"(?m)^U2FsdGVkX1[A-Za-z0-9+/=]*\r?$", text):
            tail = text[match.start():]
            lines = []
            for line in tail.splitlines():
                stripped = line.strip()
                if re.fullmatch(r"[A-Za-z0-9+/=]+", stripped) is None:
                    break
                lines.append(stripped)
            base64.b64decode("".join(lines), validate=True)
            blocks.append({"source": source(path), "object": "published embedded Base64 block", "line_lengths": list(map(len, lines)), "nonfinal_lines_are64": all(len(line) == 64 for line in lines[:-1]), "source_line_one_based": text.count("\n", 0, match.start()) + 1, "source_byte_span_zero_based_half_open": [match.start(), match.start() + len("\r\n".join(lines))]})
    if len(blocks) != 5 or not all(block["nonfinal_lines_are64"] for block in blocks):
        raise ValueError("Previously published Base64 formatting differs")
    layout, compact, unused_span = primary_layout()
    first = next(region for region in layout["regions"] if region["name"] == "small-container-first-part")
    second = next(region for region in layout["regions"] if region["name"] == "small-container-second-part")
    enter = next(region for region in layout["regions"] if region["name"] == "enter")
    first_text = compact[slice(*first["normalized_span_zero_based_half_open"])]
    second_text = compact[slice(*second["normalized_span_zero_based_half_open"])]
    decoded = base64.b64decode(first_text + second_text, validate=True)
    return {
        "precedent_blocks": blocks, "embedded_fragment_lengths": [len(first_text), len(second_text)],
        "inline_enter": enter, "formatting_interpretation": "enter denotes the conventional64-character Base64 line break",
        "matches_published_formatting": len(first_text) == len(second_text) == 64,
        "decoded_container_header_is_Salted": decoded.startswith(b"Salted__"), "decoded_public_container_bytes": len(decoded),
        "content_bytes_unchanged_by_whitespace": base64.b64decode(first_text + "\n" + second_text) == decoded,
        "not_a_container_processing_or_answer_instruction": "Formatting is directly supported. This does not prove no secondary role or identify any plaintext answer.",
    }


def report():
    hint = binary_hint_evidence()
    return {
        "id": "C11-HINT-INSTRUCTION-ORDER", "date": "2026-09-30", "status": "PROMISING",
        "hypothesis": "The preserved February23 2023 hint directly supplies a clue sequence that constrains the original trailer construction",
        "source_evidence": [hint["source"], hint["screenshot"]["source"], hint["secondary_readme"]["source"]],
        "source_locations": ["research/evidence/cycle02/_work__creator_jrk.txt:711", "research/evidence/cycle02/_work__chat_transcript.txt:20386", "research/sources/maintained-README.md:343", "research/sources/salphaseion.html:18"],
        "assumptions": ["Order of clue mentions may correspond to construction order", "yinyang names a later recognition checkpoint, not necessarily a cipher", "Archived creator labels are attributed evidence, not signed authentication"],
        "operation_order": ["reverse complete preserved bitstream", "map decoded phrase order to original positions", "separate clue enumeration from executable data-flow", "test enter formatting against original published blocks"],
        "input": "Preserved161-octet public hint and existing page text", "output": "Exact decoded clue sequence plus stronger inline-enter referent",
        "confidence": "HIGH for exact hint order/formatting; MEDIUM for execution dependency; UNKNOWN for operands",
        "binary_hint": hint, "enter_formatting": formatting_blocks(),
        "strongest_supported_clue_sequence": ["yellowblueprimes", "matrixsumlist", "lastwordsbeforearchichoice", "yinyang"],
        "best_supported_data_flow": {"nodes": ["yellow-blue-prime object", "sumlist object or operation", "Architect-words object", "yin-yang checkpoint"], "edges": [["yellow-blue-prime object", "sumlist object or operation", "ORDERED_MENTIONS_NOT_VERIFIED_DATAFLOW"], ["sumlist object or operation", "Architect-words object", "ORDERED_MENTIONS_NOT_VERIFIED_DATAFLOW"], ["Architect-words object", "yin-yang checkpoint", "ORDERED_MENTIONS_NOT_VERIFIED_DATAFLOW"]], "separate_local_SHA_container_SHA_graph_unchanged": True, "Bifid_branch_not_named_by_hint": True},
        "correction_to_cycle10": "Cycle10 omitted a preserved creator-attributed binary hint that mentions several independent objects in order. The later ying-yang clue is not the only archived evidence connecting them. This does not fix an operand, list axis or container destination.",
        "contradictions": ["Hint contains concatenated tokens, no explicit verbs/arrows/axis/index convention", "Bifid, faed, SMALL, thispassword and HASHTHETEXT are not named in this hint", "No authenticated command binds the sumlist to Architect words or yin-yang to a particular container"],
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
        "next_test": "A fixed source-coordinate join audit: can existing prime/color event positions and numeric objects refer to exact Architect words before a source-supported choice boundary? Identify the boundary and mapping before extraction; no source-window or route enumeration.",
    }


def main():
    document = report()
    write_artifact(OUTPUT / "hint-instruction-order.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "source_octets": document["binary_hint"]["octet_count"], "full_reversal_round_trip": document["binary_hint"]["round_trip"], "clue_sequence": document["strongest_supported_clue_sequence"], "formatting_precedents": len(document["enter_formatting"]["precedent_blocks"]), "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
