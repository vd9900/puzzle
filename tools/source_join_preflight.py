import json
import re

from tools.gsmg import checkerboard, decode_checkerboard, encode_checkerboard
from tools.instruction_graphs import ROOT, digest, fixed_tokens, primary_layout, prime, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle12"
FROZEN = ROOT / "research/artifacts/cycle11/trailer-referents.json"
ARTIFACT_NAME = "source-join-preflight-v2.json"


def fixed_selection(text, indices):
    if len(indices) != len(set(indices)) or indices != sorted(indices):
        raise ValueError("Selection must use distinct source positions in ascending order")
    if any(index < 0 or index >= len(text) for index in indices):
        raise ValueError("Out-of-range source positions must not be dropped or wrapped")
    chosen = set(indices)
    selected = "".join(text[index] for index in indices)
    omitted = "".join(symbol for index, symbol in enumerate(text) if index not in chosen)
    inverse = []
    selected_iterator = iter(selected)
    omitted_iterator = iter(omitted)
    for index in range(len(text)):
        inverse.append(next(selected_iterator) if index in chosen else next(omitted_iterator))
    if "".join(inverse) != text:
        raise ValueError("Selected and omitted text do not reconstruct the original source")
    return selected, omitted


def checkerboard_source_map():
    fixture = ROOT / "research/artifacts/phase32.txt"
    payload = fixture.read_bytes()
    match = re.search(rb"\r\n\r\n([0-9]{100,})", payload)
    if match is None:
        raise ValueError("Published numeric source not found")
    numbers = match.group(1).decode("ascii")
    decoded = decode_checkerboard(numbers)
    saved = ROOT / "research/artifacts/phase32-checkerboard.txt"
    if saved.read_text().strip() != decoded or encode_checkerboard(decoded) != numbers:
        raise ValueError("Exact published checkerboard source does not round-trip")
    board = checkerboard()
    offset = 0
    mapped = []
    while offset < len(numbers):
        width = 2 if numbers[offset] in ("1", "4") else 1
        code = numbers[offset:offset + width]
        symbol = board[code]
        mapped.append({"output_index_zero_based": len(mapped), "numeric_byte_span_in_encoded_fixture_zero_based_half_open": [match.start(1) + offset, match.start(1) + offset + width], "code": code, "symbol": symbol})
        offset += width
    return decoded, {"source": source(fixture), "saved_decoded_source": source(saved), "numeric_byte_span_zero_based_half_open": [match.start(1), match.end(1)], "numeric_length": len(numbers), "decoded_length": len(decoded), "round_trip": True, "output_source_map": mapped}


def published_quote():
    path = ROOT / "research/evidence/cycle02/_work__chat_transcript.txt"
    lines = path.read_text().splitlines()
    header = "=== [03.03.2026 20:39:06 UTC-05:00] Denis Golovkin"
    header_index = lines.index(header)
    next_header = next(index for index in range(header_index + 1, len(lines)) if lines[index].startswith("=== ["))
    matches = [index for index in range(header_index + 1, next_header) if lines[index] == "ncsyangcahiriasogaleafayanestve"]
    if len(matches) != 1:
        raise ValueError("Expected one exact extraction quote within its dated community message")
    quote_index = matches[0]
    quoted = lines[quote_index]
    return quoted, {"source": source(path), "header": header, "quote_line_one_based": quote_index + 1, "quoted_length": len(quoted), "quoted_public_text_sha256": digest(quoted.encode()), "classification": "COMMUNITY_PUBLISHED_TEXT_SELECTION_NOT_CREATOR_CONFIRMATION"}


def source_paragraph_roles():
    path = ROOT / "research/artifacts/phase32.txt"
    payload = path.read_bytes()
    paragraphs = payload.split(b"\r\n\r\n")
    expected_lengths = [332, 107, 1539, 149, 145, 130]
    if list(map(len, paragraphs)) != expected_lengths:
        raise ValueError("Fixed original paragraph layout differs")
    roles = ["public stage introductory text", "encoding and classical-transform clue", "encoded Architect-speech branch", "numeric checkerboard branch", "checkerboard-alphabet clue immediately before the container", "public encoded container"]
    records = []
    offset = 0
    for index, (paragraph, role) in enumerate(zip(paragraphs, roles)):
        records.append({"paragraph_index_zero_based": index, "role": role, "byte_span_zero_based_half_open": [offset, offset + len(paragraph)], "length": len(paragraph), "contains_literal_choice": b"choice" in paragraph.lower(), "ASCII_only": paragraph.isascii(), "numeric_only": paragraph.isdigit()})
        offset += len(paragraph) + 4
    if not paragraphs[5].startswith(b"U2FsdGVkX1") or not paragraphs[3].isdigit():
        raise ValueError("Known source branch/container ordering differs")
    clue = b"One for one, four for one."
    clue_start = payload.index(clue)
    codebook_width = b"as wide as the first one seen"
    width_start = payload.index(codebook_width)
    return {
        "source": source(path), "paragraphs": records,
        "encoding_clue": {"literal": clue.decode(), "byte_span_zero_based_half_open": [clue_start, clue_start + len(clue)], "clue_has_no_literal_1141_index_or_slice": True},
        "checkerboard_width_clue": {"literal": codebook_width.decode(), "byte_span_zero_based_half_open": [width_start, width_start + len(codebook_width)], "belongs_to_paragraph_index_zero_based": 4},
        "91_letter_selected_text_origin": "Numeric paragraph3 via the already verified checkerboard, not the encoded Architect speech in paragraph2",
        "91_letter_text_is_not_immediately_adjacent_to_container": True,
        "no_primary_choice_word_in_any_paragraph": all(not record["contains_literal_choice"] for record in records),
        "layout_does_not_prove_a_last_words_referent": True,
        "historical_speech_offset1141_selection_already_tested_not_relaunched": True,
    }


def join_report():
    frozen = json.loads(FROZEN.read_text())
    if not frozen["speech_wording"]["all1539_letters_match"]:
        raise ValueError("Prior fixed source-binding evidence differs")
    decoded, source_map = checkerboard_source_map()
    quote, quote_source = published_quote()
    unused_layout, compact, span = primary_layout()
    dbbi = compact[:91]
    if len(decoded) != len(dbbi) or len(decoded) != 91:
        raise ValueError("Published proposed alignment is no longer91 characters")
    results = []
    for mask in (505, 1017):
        tokens = fixed_tokens(dbbi, mask)
        markers = [token for token in tokens if prime(token["logical_position_one_based"])]
        if any(token["token"] not in ("b", "be") for token in markers):
            raise ValueError("Documented prime markers changed")
        raw_positions = [offset for token in markers for offset in range(token["offset"], token["offset"] + len(token["token"]))]
        logical_positions = [token["logical_position_one_based"] - 1 for token in markers]
        selected, omitted = fixed_selection(decoded, raw_positions)
        logical_selected, unused_logical_omitted = fixed_selection(decoded, logical_positions)
        marker_map = []
        for token in markers:
            marker_map.append({"token": token["token"], "logical_position_one_based": token["logical_position_one_based"], "chosen_raw_positions_zero_based": list(range(token["offset"], token["offset"] + len(token["token"]))), **span(token["offset"], token["offset"] + len(token["token"]))})
        recognized = []
        for word in ("yang", "yin", "ying", "yinyang", "yingyang"):
            matches = list(re.finditer(re.escape(word), selected))
            recognized.append({"literal": word, "count": len(matches), "source_positions_zero_based": [raw_positions[match.start():match.end()] for match in matches], "selected_spans_zero_based_half_open": [[match.start(), match.end()] for match in matches]})
        results.append({
            "mask": mask, "logical_dbbi_length": len(tokens), "prime_token_count": len(markers),
            "prime_token_source_map": marker_map, "raw_selected_positions_zero_based": raw_positions,
            "raw_selected_length": len(selected), "raw_omitted_length": len(omitted),
            "raw_selected_public_text_sha256": digest(selected.encode()), "raw_omitted_public_text_sha256": digest(omitted.encode()),
            "raw_result_equals_published_quote": selected == quote,
            "logical_selected_positions_zero_based": logical_positions, "logical_selected_length": len(logical_selected),
            "logical_result_equals_published_quote": logical_selected == quote,
            "literal_checkpoint_tests": recognized, "source_partition_round_trip": True,
            "unchanged_complement_does_not_claim_dbbi_residual_identity": True,
        })
    if [result["raw_result_equals_published_quote"] for result in results] != [False, True]:
        raise ValueError("Fixed published recipe attribution differs")
    shared = sorted(set(results[0]["raw_selected_positions_zero_based"]) & set(results[1]["raw_selected_positions_zero_based"]))
    return {
        "id": "C12-SOURCE-JOIN-PREFLIGHT", "revision": 2, "date": "2026-09-30", "status": "INCONCLUSIVE",
        "hypothesis": "The published prime/raw-position selection supplies the missing join from the ordered hint to a fixed text source",
        "source_evidence": [source(FROZEN), source(ROOT / "research/sources/salphaseion.html"), source_map["source"], quote_source["source"]],
        "source_locations": ["research/sources/salphaseion.html:18", "research/artifacts/phase32-checkerboard.txt:1", "research/evidence/cycle02/_work__chat_transcript.txt:168601", "research/evidence/cycle02/_work__chat_transcript.txt:168664"],
        "assumptions": ["Equal91-character lengths motivate aligning dbbi with the decoded checkerboard text", "A marker be selects both raw source characters, rather than one logical token position", "The community-defined checkerboard text is the trailer's last-words referent", "matrixsumlist describes a movie-speech label or intermediate rather than an actual sum"],
        "operation_order": ["verify saved numeric checkerboard source only", "reuse two existing dbbi tokenizations", "map prime b/be tokens to raw physical source positions", "compare one published31-letter quote", "test literal checkpoint identity and record the missing graph edges"],
        "input": "Existing dbbi91/decoded checkerboard91 and a fixed community-published recipe", "output": "Two raw/logical source-map audits without trial-material generation",
        "confidence": "HIGH for recipe reproduction; LOW for intended source join",
        "source_alignment": {"dbbi_length": len(dbbi), "checkerboard_decoded_length": len(decoded), "matching_lengths_are_not_a_selector_instruction": True},
        "checkerboard": source_map, "published_quote": quote_source, "results": results,
        "source_paragraph_roles": source_paragraph_roles(),
        "shared_selected_source_positions_zero_based": shared,
        "yang_source_positions_shared_by_both_branches": [6, 10, 11, 13],
        "branch_yang_matches_are_not_independent": True,
        "missing_edges": ["No preserved primary command identifies checkerboard text as lastwordsbeforearchichoice", "Published recipe gives no numeric sum operation or matrixsumlist result", "Raw physical indexing is an additional convention, distinct from logical prime indexing", "Neither unchanged output contains literal yin, ying, yinyang or yingyang", "Anagramming is community speculation and is not executed"],
        "scope_of_rejection": "Reject only the claim that this unchanged published extraction already equals or contains the complete literal yin-yang checkpoint; reproducing a31-letter partial result is not intent verification",
        "search_space": {"existing_tokenizations": 2, "fixed_text_sources": 1, "published_raw_index_recipe": 1, "logical_index_diagnostic": 1, "complete_literal_checkpoint_strings": ["yinyang", "yingyang"], "new_cryptographic_trials": 0, "new_trial_inputs": 0},
        "contradictions": ["The source is a checkerboard instruction, not the verified modified Architect speech or its community choice quote", "Complete yin-yang requires an unexplained additional transformation", "Both branches yield the same yang letters at shared positions", "Creator Bingo attribution must be checked chronologically, not attached to a later recipe"],
        "next_test": "Audit primary number/encoding clues that could bind a selector without inventing a route; retain the observed partial extraction as a community recipe, not a solved construction.",
    }


def main():
    document = join_report()
    write_artifact(OUTPUT / ARTIFACT_NAME, (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "fixed_sources": 1, "existing_branches": 2, "published_quote_reproduced_for_mask": 1017, "complete_literal_yinyang_matches": 0, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
