#!/usr/bin/env python3
"""Audit source-authored wording for matrixsumlist argument bindings."""

from collections import Counter
from datetime import datetime
import json
import re

from tools.gsmg import ARTIFACTS, SOURCES
from tools.instruction_graphs import primary_layout, source, write_artifact


OUTPUT = ARTIFACTS / "cycle34"
CREATOR = SOURCES.parent / "evidence/cycle02/_work__creator_jrk.txt"
CHAT = SOURCES.parent / "evidence/cycle02/_work__chat_transcript.txt"
PRIMARY = SOURCES / "salphaseion.html"
HINT_ORDER = ARTIFACTS / "cycle11/hint-instruction-order.json"

TERMS = (
    "yellow", "blue", "number", "numbers", "prime", "primes", "matrix", "matrices",
    "sum", "sums", "list", "lists", "row", "rows", "column", "columns",
    "horizontal", "vertical", "axis", "axes", "across", "cell", "cells", "square",
    "squares", "pixel", "pixels", "grid", "grids", "table", "tables",
)


def messages(path):
    records = []
    current = None
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        header = re.fullmatch(r"=== \[(.*?)\] (.*)", line)
        if header:
            if current is not None:
                current["body"] = "\n".join(current.pop("body_lines")).strip()
                records.append(current)
            current = {
                "header_line_one_based": line_number,
                "timestamp": header.group(1),
                "speaker": header.group(2),
                "body_lines": [],
            }
        elif current is not None:
            current["body_lines"].append(line)
    if current is not None:
        current["body"] = "\n".join(current.pop("body_lines")).strip()
        records.append(current)
    return records


def term_counts(text):
    lowered = text.lower()
    return {
        term: len(re.findall(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lowered))
        for term in TERMS
    }


def one_message(records, body_start):
    found = [record for record in records if record["body"].startswith(body_start)]
    if len(found) != 1:
        raise ValueError(f"Expected one message starting {body_start!r}, found {len(found)}")
    return found[0]


def message_at(records, timestamp, body_start):
    found = [record for record in records if record["timestamp"] == timestamp and record["body"].startswith(body_start)]
    if len(found) != 1:
        raise ValueError(f"Expected one message at {timestamp!r} starting {body_start!r}, found {len(found)}")
    return found[0]


def elapsed(first, second):
    format_string = "%d.%m.%Y %H:%M:%S UTC-05:00"
    return int((datetime.strptime(second["timestamp"], format_string) - datetime.strptime(first["timestamp"], format_string)).total_seconds())


def report():
    creator_text = CREATOR.read_text()
    creator_messages = messages(CREATOR)
    chat_messages = messages(CHAT)
    counts = term_counts(creator_text)
    if len(creator_messages) != 411:
        raise ValueError("Creator-attributed message count changed")

    color_hint = one_message(creator_messages, "Roses are White but often Red.")
    prime_part = one_message(creator_messages, "You are at the prime part already???")
    prime_aside = one_message(creator_messages, "Oh wait, shouldn't have said that.")
    prior_hint = one_message(creator_messages, "I gave an unforseen hint already")
    zeroing_hint = one_message(creator_messages, 'The previous "there is another door hint"')
    prime_later = one_message(creator_messages, "At least prime number is very important")
    rab_notation = one_message(creator_messages, "R=18\nA=1\nB=2")

    matrix_question = message_at(chat_messages, "14.03.2021 10:12:04 UTC-05:00", "So don't you think it's time for a hint on matrixsumlist?")
    matrix_reply = message_at(chat_messages, "14.03.2021 10:19:29 UTC-05:00", "I gave an unforseen hint already")
    prime_values_question = message_at(chat_messages, "01.03.2021 06:34:22 UTC-05:00", "just say which primes 2,3,5,7 we need use")
    prime_part_reply = message_at(chat_messages, "01.03.2021 06:34:42 UTC-05:00", "You are at the prime part already???")
    sumlist_prime_question = message_at(chat_messages, "09.01.2023 00:57:03 UTC-05:00", "sumlist matrix -contains prime numbers ?")
    sumlist_prime_reply = message_at(chat_messages, "09.01.2023 05:10:46 UTC-05:00", "At least prime number is very important")
    community_arithmetic = message_at(chat_messages, "01.04.2021 08:27:27 UTC-05:00", "look: 15+9+1= 25 bit")
    rab_reply = message_at(chat_messages, "01.04.2021 08:29:41 UTC-05:00", "R=18\nA=1\nB=2")

    hint = json.loads(HINT_ORDER.read_text())
    decoded_hint = hint["binary_hint"]["decoded_public_text"]
    layout, compact, _ = primary_layout()
    primary_document = PRIMARY.read_text()
    textarea_match = re.search(r"<textarea\b[^>]*>(.*?)</textarea>", primary_document, re.S | re.I)
    if textarea_match is None:
        raise ValueError("Primary textarea missing")
    textarea_content = textarea_match.group(1)
    textarea_nonempty_lines = [line for line in textarea_content.splitlines() if line.strip()]
    regions = {region["name"]: region for region in layout["regions"]}
    label = regions["matrixsumlist"]
    dbbi = regions["dbbi91"]
    faed = regions["faed570"]
    if (dbbi["normalized_span_zero_based_half_open"][1], label["normalized_span_zero_based_half_open"], faed["normalized_span_zero_based_half_open"][0]) != (91, [91, 195], 195):
        raise ValueError("Primary label boundaries changed")

    relevant_plaintext = "\n".join(record["body"] for record in (color_hint, prime_part, prime_aside, prior_hint, zeroing_hint, prime_later, rab_notation))
    relevant_counts = term_counts(relevant_plaintext)
    axis_terms = {term: relevant_counts[term] for term in ("row", "rows", "column", "columns", "horizontal", "vertical", "axis", "axes", "across")}
    domain_terms = {term: relevant_counts[term] for term in ("cell", "cells", "square", "squares", "pixel", "pixels", "grid", "grids", "table", "tables")}
    if any(axis_terms.values()) or any(domain_terms.values()):
        raise ValueError("A previously absent explicit axis/domain word appeared")

    creator_matches = []
    pattern = re.compile(r"(?<![a-z])(?:" + "|".join(map(re.escape, TERMS)) + r")(?![a-z])", re.I)
    for record in creator_messages:
        matched = sorted(set(match.group(0).lower() for match in pattern.finditer(record["body"])))
        if matched:
            creator_matches.append({
                "header_line_one_based": record["header_line_one_based"],
                "timestamp": record["timestamp"],
                "body": record["body"],
                "matched_terms": matched,
                "relevant_to_matrixsumlist_binding": record in (color_hint, prime_part, zeroing_hint, prime_later),
            })

    return {
        "id": "C34-MATRIXSUMLIST-WORDING-AUDIT",
        "date": "2026-10-02",
        "status": "INCONCLUSIVE",
        "hypothesis": "Preserved source-authored wording or formatting explicitly fixes at least one matrixsumlist argument: cell domain, numeric interpretation, or axis.",
        "pass_condition": "An authored phrase must identify a concrete operand subset, numeric role/value rule, or row/column/other summation direction without importing a community convention.",
        "source_evidence": [source(path) for path in (CREATOR, CHAT, PRIMARY, HINT_ORDER)],
        "creator_corpus": {
            "message_count": len(creator_messages),
            "exact_term_counts": counts,
            "messages_matching_audited_terms": creator_matches,
            "matrix_literal_count_before_decoding_binary_hints": counts["matrix"],
            "sum_literal_count_before_decoding_binary_hints": counts["sum"],
            "axis_and_domain_counts_in_relevant_messages": axis_terms | domain_terms,
        },
        "relevant_records": [
            {
                "id": "COLOR-FIRST-PIECE",
                "record": color_hint,
                "establishes": ["Yellow and Blue each have a number", "return to the first puzzle piece"],
                "does_not_establish": ["a cell subset", "either number", "whether numbers are values or indices", "a sum axis"],
            },
            {
                "id": "PRIME-PART",
                "records": [prime_part, prime_aside],
                "establishes": ["prime relevance at the current part"],
                "does_not_establish": ["specific prime values", "index origin", "operand", "values versus positions"],
            },
            {
                "id": "MATRIXSUMLIST-REPLY",
                "question": matrix_question,
                "reply": matrix_reply,
                "elapsed_seconds": elapsed(matrix_question, matrix_reply),
                "establishes": ["the creator treated an earlier remark as a hint when matrixsumlist was requested"],
                "does_not_establish": ["which earlier hint was meant with certainty", "cell domain", "numeric value", "axis"],
            },
            {
                "id": "PRIME-ZEROING",
                "record": zeroing_hint,
                "establishes": ["prime numbers are required somewhere", "some characters are zeroed somewhere"],
                "does_not_establish": ["that characters are image cells", "which characters", "whether zero is a summation weight", "axis"],
            },
            {
                "id": "SUMList-PRIME-CONTEXT",
                "question": sumlist_prime_question,
                "reply": sumlist_prime_reply,
                "elapsed_seconds": elapsed(sumlist_prime_question, sumlist_prime_reply),
                "reply_metadata_present": False,
                "establishes": ["prime importance is reiterated"],
                "does_not_establish": ["yes to prime-valued matrix entries", "primes as entries rather than positions", "a sum list"],
            },
            {
                "id": "RAB-NUMERIC-NOTATION",
                "preceding_community_message": community_arithmetic,
                "creator_record": rab_reply,
                "elapsed_seconds": elapsed(community_arithmetic, rab_reply),
                "establishes": ["creator-authored A1Z26-style examples R=18, A=1, B=2 exist"],
                "does_not_establish": ["Y=25 in this operation", "B/Y as matrix weights", "which cells", "axis", "a reply binding to the preceding message"],
            },
        ],
        "question_reply_controls": {
            "specific_prime_values_question": prime_values_question,
            "generic_prime_part_reply": prime_part_reply,
            "elapsed_seconds": elapsed(prime_values_question, prime_part_reply),
            "specific_values_confirmed": False,
        },
        "formatting": {
            "primary_compact_length": len(compact),
            "physical_order": ["dbbi91", "matrixsumlist104", "faed570"],
            "normalized_spans": {
                "dbbi91": dbbi["normalized_span_zero_based_half_open"],
                "matrixsumlist104": label["normalized_span_zero_based_half_open"],
                "faed570": faed["normalized_span_zero_based_half_open"],
            },
            "separator_before_label": False,
            "separator_after_label": False,
            "label_decoded": label["decoded"],
            "label_contains_authored_spaces_or_punctuation": False,
            "textarea_physical_nonempty_lines": len(textarea_nonempty_lines),
            "textarea_supplies_matrix_rows": len(textarea_nonempty_lines) > 1,
            "official_hint_decoded": decoded_hint,
            "official_hint_sequence": hint["strongest_supported_clue_sequence"],
            "official_hint_contains_explicit_arrows_verbs_axis_or_index_convention": False,
            "secondary_spaced_transcription_is_not_primary_formatting": True,
        },
        "classification": {
            "first_piece_as_source_domain": "STRONGLY SUPPORTED",
            "yellow_and_blue_each_have_some_number": "VERIFIED as wording",
            "actual_yellow_blue_numbers": "UNKNOWN",
            "prime_relevance": "VERIFIED as wording",
            "prime_role_values_vs_positions": "UNKNOWN",
            "matrixsumlist_as_three-word_imperative": "WEAK/PLAUSIBLE; source supplies a concatenated label without grammar",
            "cell_domain": "UNKNOWN",
            "numeric_interpretation": "UNKNOWN",
            "summation_axis": "UNKNOWN",
        },
        "result": "No preserved source-authored wording or formatting fixes the cell domain, numeric interpretation, or summation axis. The strongest statements identify the first puzzle piece, say Yellow and Blue each have a number, and require primes somewhere. The R/A/B notation proves an alphabet-number convention was available but does not bind B/Y as matrix weights. Primary and official-hint formatting provide adjacency/order only, with no separators, rows, verbs, axis, or index convention.",
        "graph_effect": "Retain yellowblueprimes -> matrixsumlist as authored mention order. Do not promote it to selected-cells -> weighted matrix -> row/column sums.",
        "next_test": "Stop source-internal matrix execution. Resume only if a new author-attributed record explicitly binds at least one of cell domain, numeric type, or axis; otherwise preserve matrixsumlist as underdetermined.",
        "new_pixel_operations": 0,
        "new_numeric_combinations": 0,
        "candidate_material_generated": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "matrixsumlist-wording-audit.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({
        "status": document["status"],
        "cell_domain": document["classification"]["cell_domain"],
        "numeric_interpretation": document["classification"]["numeric_interpretation"],
        "summation_axis": document["classification"]["summation_axis"],
        "explicit_binding_found": False,
        "cryptographic_operations": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
