import bisect
import hashlib
import html
import json
import math
import re
from collections import Counter
from pathlib import Path

from tools.bifid_evidence import bifid, key_square
from tools.gsmg import decode_binary_letters, decode_decimal_letters, extract_grid


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/artifacts/cycle10"
PRIMARY = ROOT / "research/sources/salphaseion.html"
TERMS = {
    "first-command": ["shabefourfirsthintisyourlastcommand", "our first hint is your last command", "ourfirsthintisyourlastcommand"],
    "answer-command": ["shabefanstoo", "shabef ans too", "sha256 answer too"],
    "small-label": ["SMALL"],
    "hash-text": ["HASHTHETEXT", "hash the text"],
    "matrix-sum-list": ["matrixsumlist", "matrix sum list"],
    "last-words": ["lastwordsbeforearchichoice", "last words before archi choice"],
    "this-label": ["thispassword", "this password"],
    "bifid": ["Bifid", "bifid"],
    "bifid-prefix": ["btcseed", "BTCSEED"],
    "faed-label": ["faed570", "faed", "FAED"],
    "residual-label": ["60-letter residual", "60-letter", "61-letter", "residual60"],
    "first-hint-echo": ["my first hint might be your last command"],
}
TEXT_SUFFIXES = {".html", ".md", ".txt", ".ipynb", ".py", ".cjs"}
HEADER = re.compile(r"=== \[(\d{2})\.(\d{2})\.(\d{4}) ([^]]+)\] (.*)")


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def source(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def text_location(document, start, end):
    previous_newline = document.rfind("\n", 0, start)
    return {
        "character_span_zero_based_half_open": [start, end],
        "utf8_byte_span_zero_based_half_open": [len(document[:start].encode()), len(document[:end].encode())],
        "line_one_based": document.count("\n", 0, start) + 1,
        "column_one_based": start - previous_newline,
    }


def primary_layout():
    document = PRIMARY.read_bytes().decode("utf-8")
    textareas = list(re.finditer(r"<textarea\b[^>]*>(.*?)</textarea>", document, re.S | re.I))
    if len(textareas) != 2:
        raise ValueError("Expected exactly two original textareas")
    match = textareas[0]
    original = match.group(1)
    if html.unescape(original) != original:
        raise ValueError("Entity decoding requires a different source map")
    offsets = [match.start(1) + index for index, symbol in enumerate(original) if not symbol.isspace()]
    compact = "".join(document[offset] for offset in offsets)
    binary_runs = list(re.finditer(r"[ab]{16,}", compact))
    cipher_start = compact.index("U2FsdGVkX1")
    separators = [index for index, symbol in enumerate(compact[:cipher_start]) if symbol == "z"]
    if len(binary_runs) != 2 or len(separators) != 3:
        raise ValueError("Unexpected original clue boundaries")
    first_command = compact.index("shabefourfirsthintisyourlastcommand")
    answer_command = compact.index("shabefanstoo")
    boundaries = [
        ("dbbi91", 0, binary_runs[0].start()),
        ("matrixsumlist", binary_runs[0].start(), binary_runs[0].end()),
        ("faed570", binary_runs[0].end(), separators[0]),
        ("lastwordsbeforearchichoice", separators[0] + 1, separators[1]),
        ("thispassword", separators[1] + 1, separators[2]),
        ("first-command", first_command, cipher_start),
        ("small-container-first-part", cipher_start, binary_runs[1].start()),
        ("enter", binary_runs[1].start(), binary_runs[1].end()),
        ("small-container-second-part", binary_runs[1].end(), answer_command),
        ("answer-command", answer_command, len(compact)),
    ]

    def span(start, end):
        return {"normalized_span_zero_based_half_open": [start, end], **text_location(document, offsets[start], offsets[end - 1] + 1)}

    regions = []
    for name, start, end in boundaries:
        region = {"name": name, "length": end - start, "source": source(PRIMARY), **span(start, end)}
        encoded = compact[start:end]
        if name in ("matrixsumlist", "enter"):
            region["decoded"] = decode_binary_letters(encoded)
            region["transform"] = "a=0,b=1; MSB-first ASCII octets"
        elif name in ("lastwordsbeforearchichoice", "thispassword"):
            region["decoded"] = decode_decimal_letters(encoded)
            region["transform"] = "a..i=1..9,o=0; decimal integer to minimal big-endian ASCII"
        elif name.endswith("command"):
            region["literal"] = encoded
        region["encoded_sha256"] = digest(encoded.encode())
        regions.append(region)
    decoded_names = [region["name"] for region in regions if "decoded" in region]
    if any(region["decoded"] != region["name"] for region in regions if region["name"] in decoded_names):
        raise ValueError("Published instruction labels changed")
    subphrases = []
    for name, start, end in [("first-shabef", first_command, first_command + 6), ("ourfirsthintisyourlastcommand", first_command + 6, cipher_start), ("second-shabef", answer_command, answer_command + 6), ("anstoo", answer_command + 6, len(compact))]:
        subphrases.append({"name": name, "literal": compact[start:end], **span(start, end)})
    layout = {
        "source": source(PRIMARY), "normalized_length": len(compact), "regions": regions,
        "command_subphrases": subphrases,
        "headings": [{"text": found.group(1).strip(), **text_location(document, found.start(1), found.end(1))} for found in re.finditer(r"<h1>(.*?)</h1>", document, re.S)],
        "three_delimiters": [span(index, index + 1) for index in separators],
        "container_internal_z": [span(index, index + 1) for index in range(cipher_start, answer_command) if compact[index] == "z"],
        "small_literal_present": "SMALL" in document or "SMALL" in compact,
        "hashtext_literal_present": "HASHTHETEXT" in document or "HASHTHETEXT" in compact,
        "faed570_literal_present": "faed570" in document,
        "layout_is_not_execution_order": True,
        "sha_operator_mapping": {"literal_prefix": "sha", "encoded_suffix": [{"symbol": symbol, "decimal_digit": str(ord(symbol) - 96)} for symbol in "bef"], "decoded_operator": "sha256", "not_a_global_substitution": True},
        "cosmic_container": {"source": source(PRIMARY), "normalized_length": len("".join(textareas[1].group(1).split())), **text_location(document, textareas[1].start(1), textareas[1].end(1))},
    }
    return layout, compact, span


def fixed_tokens(text, mask):
    starts = [offset for offset in range(len(text) - 1) if text[offset:offset + 2] == "be"]
    merged = {offset for index, offset in enumerate(starts) if mask >> index & 1}
    result = []
    offset = 0
    while offset < len(text):
        width = 2 if offset in merged else 1
        result.append({"token": text[offset:offset + width], "offset": offset, "logical_position_one_based": len(result) + 1})
        offset += width
    return result


def prime(position):
    return position >= 2 and all(position % divisor for divisor in range(2, math.isqrt(position) + 1))


def derived_source_maps(compact, span):
    dbbi = compact[:91]
    faed = compact[195:765]
    branches = []
    for mask in (505, 1017):
        tokens = fixed_tokens(dbbi, mask)
        remaining = [token for token in tokens if not prime(token["logical_position_one_based"])]
        residue = "".join(token["token"] for token in remaining)
        branches.append({
            "mask": mask, "logical_length": len(tokens), "residual_length": len(residue),
            "residual_sha256": digest(residue.encode()), "a1_numeric_total": sum(ord(symbol) - 96 for symbol in residue),
            "residual_source_map": [{"output_index_zero_based": index, "symbol": token["token"], "logical_position_one_based": token["logical_position_one_based"], **span(token["offset"], token["offset"] + len(token["token"]))} for index, token in enumerate(remaining)],
            "prime_marker_source_map": [{"token": token["token"], "logical_position_one_based": token["logical_position_one_based"], **span(token["offset"], token["offset"] + len(token["token"]))} for token in tokens if prime(token["logical_position_one_based"])],
        })
    if [branch["residual_length"] for branch in branches] != [61, 60]:
        raise ValueError("Previously documented branch identities changed")
    square = key_square(dbbi)
    decoded = bifid(faed, square, 570)
    restored = bifid(decoded, square, 570, False)
    first_occurrences = [{"symbol": symbol, "first_dbbi_index_zero_based": dbbi.index(symbol), **span(dbbi.index(symbol), dbbi.index(symbol) + 1)} for symbol in dict.fromkeys(dbbi)]
    coordinate_map = []
    for output_index in range(570):
        dependencies = []
        for role, stream_index in [("row", output_index), ("column", 570 + output_index)]:
            source_index, source_axis = divmod(stream_index, 2)
            dependencies.append({"output_coordinate": role, "faed_index_zero_based": source_index, "source_coordinate": ["row", "column"][source_axis], **span(195 + source_index, 196 + source_index)})
        coordinate_map.append({"output_index_zero_based": output_index, "dependencies": dependencies})
    boundary_path = ROOT / "research/artifacts/cycle03/prime-boundary.json"
    boundary = json.loads(boundary_path.read_text())
    selected = next(result for result in boundary["results"] if result["near_white_hypothesis_bit"] == 1)["full_matches"]
    if len(selected) != 1 or selected[0]["mask"] != 1017:
        raise ValueError("Saved prime-frame attribution changed")
    frame_map = []
    for index, marker in enumerate(selected[0]["frame_markers"]):
        offset = marker["raw_offset_zero_based"]
        frame_map.append({"event_index_zero_based": index, "region": marker["region"], "logical_position_one_based": marker["position_one_based"], "bit": marker["bit"], **span(offset, offset + len(marker["token"]))})
    return {
        "branches": branches,
        "continuous_frame": {"source": source(boundary_path), "event_count": len(frame_map), "source_map": frame_map, "assumptions": ["one-based logical prime positions", "b=1,be=0 inside dbbi", "a=0,b=1 inside binary label", "counter continues across the boundary", "near-white special event assigned 1"], "not_an_independent_selection_proof": True},
        "source_bifid": {"keyword_first_occurrences": first_occurrences, "key_square": square, "period": 570, "output_length": len(decoded), "public_prefix": decoded[:7], "output_sha256": digest(decoded.encode()), "round_trip": restored == faed, "coordinate_source_map": coordinate_map, "prefix_input_indices": sorted({entry["faed_index_zero_based"] for item in coordinate_map[:7] for entry in item["dependencies"]}), "prefix_is_not_a_verified_instruction": True},
    }


def speech_map():
    path = ROOT / "research/artifacts/phase32-beaufort.txt"
    speech = path.read_text().strip()
    fixture = ROOT / "research/artifacts/phase32.txt"
    raw = fixture.read_bytes()
    separator = b"four for one.\r\n\r\n"
    block_start = raw.index(separator) + len(separator)
    numeric_match = re.search(rb"\r\n\r\n[0-9]{100,}", raw)
    block_end = numeric_match.start()
    if block_end - block_start != len(speech):
        raise ValueError("Speech source mapping must be one-to-one")
    normalized = raw[block_start:block_end].decode("latin-1").encode("cp273").decode("ascii")
    keyword = "THEMATRIXHASYOU"
    verified = "".join(chr(97 + (ord(keyword[index % len(keyword)]) - 65 - (ord(symbol) - 97)) % 26) for index, symbol in enumerate(normalized))
    if verified != speech:
        raise ValueError("Saved speech does not match its public encoded fixture")
    anchors = []
    for phrase in ["sourcecodes", "reinsertingtheprimebasics", "afterwhich", "selectfrom", "ciaobellao"]:
        start = speech.index(phrase)
        anchors.append({"phrase": phrase, "decoded_source": source(path), **text_location(speech, start, start + len(phrase)), "encoded_source": source(fixture), "encoded_byte_span_zero_based_half_open": [block_start + start, block_start + start + len(phrase)]})
    return {"source": source(path), "encoded_source": source(fixture), "length": len(speech), "anchors": anchors, "literal_choice_occurrences": speech.count("choice"), "verified_transform": "one-to-one CP273 encoding then Beaufort THE MATRIX HAS YOU", "lastwords_referent": "No literal choice anchor. The phrase before afterwhich/select is a semantic interpretation, not a uniquely delimited last-word extraction."}


def preserved_occurrences():
    folders = [ROOT / "research/sources", *[ROOT / f"research/evidence/cycle{cycle}" for cycle in ("02", "04", "05")]]
    occurrences = []
    inspected = []
    for folder in folders:
        for path in sorted(folder.iterdir()):
            is_issue = path.name.startswith("github-issue") and path.suffix == ".json"
            if (path.suffix not in TEXT_SUFFIXES and not is_issue) or path.name.startswith(("blockstream-", "mempool-", "openssl-", "pycryptodome-")):
                continue
            document = path.read_bytes().decode("utf-8", errors="replace")
            source_id = source(path)
            inspected.append(source_id)
            lines = [0] + [match.end() for match in re.finditer("\n", document)]
            headers = [(match.start(), f"{match.group(3)}-{match.group(2)}-{match.group(1)}", match.group(4), match.group(5)) for match in HEADER.finditer(document)]
            header_offsets = [header[0] for header in headers]
            issue_regions = []
            if is_issue:
                parsed = json.loads(document)
                items = parsed if isinstance(parsed, list) else [parsed]
                items = [item for item in items if isinstance(item, dict) and "body" in item]
                body_matches = list(re.finditer(r'"body"\s*:\s*("(?:[^"\\]|\\.)*"|null)', document))
                if len(items) != len(body_matches):
                    raise ValueError("Issue body source map differs from JSON records")
                for index, (item, body_match) in enumerate(zip(items, body_matches)):
                    if json.loads(body_match.group(1)) != item["body"]:
                        raise ValueError("Issue body location does not match its record")
                    issue_regions.append((body_match.start(1), body_match.end(1), index, item))
            for term, variants in TERMS.items():
                for variant in variants:
                    for found in re.finditer(re.escape(variant), document):
                        header_index = bisect.bisect_right(header_offsets, found.start()) - 1
                        label = "PRIMARY_DOCUMENT" if path == PRIMARY else "SECONDARY_INTERPRETATION"
                        entry = {"term": term, "exact_match": variant, "source": source_id, "provenance": label, "raw_file_line_one_based": bisect.bisect_right(lines, found.start()), "raw_character_span_zero_based_half_open": [found.start(), found.end()]}
                        if path.name in ("_work__chat_transcript.txt", "_work__creator_jrk.txt"):
                            entry["provenance"] = "UNAUTHENTICATED_TRANSCRIPT_LABEL"
                        if header_index >= 0:
                            unused_offset, date, time, speaker = headers[header_index]
                            entry["archived_date"] = date
                            entry["archived_time_with_offset"] = time
                            entry["archived_speaker_label"] = speaker
                        if path.suffix == ".ipynb":
                            entry["locator_note"] = "Raw notebook JSON storage offsets, not decoded cell-output offsets"
                        if is_issue:
                            entry["provenance"] = "SECONDARY_PUBLIC_ISSUE_NOT_CREATOR_AUTHENTICATED"
                            for start, end, record_index, item in issue_regions:
                                if start <= found.start() < end:
                                    entry["json_record_index_zero_based"] = record_index
                                    entry["json_field"] = "body"
                                    entry["record_id"] = item.get("id")
                                    entry["record_created_at"] = item.get("created_at")
                                    entry["record_author_label"] = (item.get("user") or {}).get("login")
                                    break
                        occurrences.append(entry)
    counts = Counter(entry["term"] for entry in occurrences)
    small = [entry for entry in occurrences if entry["term"] == "small-label"]
    chronological = {}
    for term in TERMS:
        dated = [entry for entry in occurrences if entry["term"] == term and "archived_date" in entry and entry["source"]["path"].endswith("_work__chat_transcript.txt")]
        if dated:
            chronological[term] = min(dated, key=lambda entry: (entry["archived_date"], entry["archived_time_with_offset"]))
    return occurrences, {"inspected_files": inspected, "exact_case_sensitive_counts": dict(counts), "small_only_secondary": all(entry["provenance"].startswith("SECONDARY") for entry in small), "small_source_files": sorted({entry["source"]["path"] for entry in small}), "earliest_preserved_transcript_mentions": chronological, "limits": ["Publication time is not retrieval time or filename date", "A transcript speaker label is not creator authentication", "Literal matches exclude encoded primary equivalents mapped separately", "Source-code matches are not executed", "Binary images/audio are mapped separately, not searched as text", "Public issue body offsets refer to raw JSON storage, with record creation metadata kept separate", "No external-state JSON or cryptographic libraries/documentation searched"]}


def archived_quote(path, quote, classification):
    document = path.read_text()
    start = document.index(quote)
    headers = list(HEADER.finditer(document, 0, start))
    header = headers[-1] if headers else None
    return {"quote": quote, "source": source(path), **text_location(document, start, start + len(quote)), "classification": classification, "archived_header": header.group() if header else None, "creator_authenticated": False}


def corroboration():
    creator = ROOT / "research/evidence/cycle02/_work__creator_jrk.txt"
    chat = ROOT / "research/evidence/cycle02/_work__chat_transcript.txt"
    quotes = [
        (creator, "Roses are White but often Red.\nYellow has a number and so does Blue.\nGo back to the first puzzle piece without further ado.", "CREATOR_ATTRIBUTED_TRANSCRIPT_CORROBORATED_BY_SCREENSHOT"),
        (creator, "some characters need to be 'zeroed out'", "CREATOR_ATTRIBUTED_TRANSCRIPT"),
        (creator, 'Once you hit a "ying yang", you\'ll be able to solve it the same day.', "CREATOR_ATTRIBUTED_TRANSCRIPT"),
        (creator, "A hash which we provided as the website was giving a lot of token errors.", "CREATOR_ATTRIBUTED_TRANSCRIPT"),
        (chat, "lol ofc. my first hint might be your last command", "DELETED_ACCOUNT_NOT_CREATOR_AUTHENTICATED"),
        (chat, 'if shabef is indeed sha256, we need to hash "Follow the white rabbit"?', "COMMUNITY_QUESTION_NOT_A_DERIVATION"),
        (chat, "the part after AES is shabef ans too.. so after AES decryption if we hash it maybe it decrypts the cosmic duality", "COMMUNITY_CONJECTURE"),
        (chat, "the AES from salph might lead back to 3_2_2 aes", "COMMUNITY_COMPETING_CONJECTURE"),
        (chat, "Basically after using various ciphers I found that a small portion of", "COMMUNITY_BIFID_DISCOVERY"),
        (chat, "this could entirely be a coincidence of course and have absolutely nothing to do with the puzzle", "COMMUNITY_BIFID_CAVEAT"),
        (ROOT / "research/sources/community-README.md", "our first hint is your last command", "PINNED_2021_SECONDARY_WALKTHROUGH"),
        (ROOT / "research/sources/maintained-salphaseion.ipynb", 'four first hint is your last command', "SECONDARY_NOTEBOOK_INITIAL_PARSE_ERROR"),
        (ROOT / "research/evidence/cycle05/fork-solver__experiments__claude_endgame_2026_09_02__BRIEFING.md", "blob AES **SMALL**", "SECONDARY_CONTAINER_LABEL_NO_AUTHENTICATED_CREATION_DATE"),
    ]
    audio_path = ROOT / "research/artifacts/audio-reproduction.json"
    audio = json.loads(audio_path.read_text())
    source_manifest = json.loads((ROOT / "research/sources/manifest.json").read_text())
    audio_sources = [source(ROOT / "research/sources" / name) for name, entry in source_manifest.items() if entry["sha256"] == audio["source_sha256"]]
    if bytes.fromhex(audio["transcription"]).decode("ascii") != "HASHTHETEXT" or len(audio_sources) != 1:
        raise ValueError("Archived audio transcription or source differs")
    return {
        "quotes": [archived_quote(path, quote, classification) for path, quote, classification in quotes],
        "color_hint_image": {"source": source(ROOT / "research/sources/maintained-hints__2020-01-14-roses-are-red.png"), "pixel_rectangle_xyxy": [62, 39, 545, 102], "archived_date_from_transcript": "2020-01-14", "date_not_visible_in_image": True, "transcription": quotes[0][1], "creator_attribution": "Visible Jrk Bgrt/admin label; not cryptographic authentication"},
        "hashtext": {"source": source(audio_path), "audio_sources": audio_sources, "image_source": source(ROOT / "research/artifacts/decentraland-spectrogram.png"), "image_hex_pixel_rectangle_xyxy": [153, 416, 1718, 526], "pixel_rectangle_is_a_visual_locator_not_an_exact_audio_time_range": True, "operation": audio["transform"], "human_transcription": audio["transcription"], "decoded": "HASHTHETEXT", "transcription_not_machine_inferred": True, "argument_not_encoded_in_this_instruction": True},
        "authentication": "Direct page/image content, archived creator-attributed hints, and community deductions are distinct. No preserved author signature or authenticated publication metadata establishes a unique creator-authenticated execution graph.",
    }


def weighted_diagnostic(maps):
    grid = extract_grid(ROOT / "research/sources/gsmg-puzzle.png")
    counts = Counter(color for row in grid["colors"] for color in row)
    palette = {"black": 1, "white": 0, "near_white": 0, "blue": 2, "yellow": 25}
    total = sum(counts[color] * weight for color, weight in palette.items())
    return {"source": source(ROOT / "research/sources/gsmg-puzzle.png"), "marker_numeric_letters": {"b": {"decimal": 2, "A1Z26": "B"}, "be": {"decimal": 25, "A1Z26": "Y"}}, "palette": palette, "color_counts": dict(counts), "weighted_matrix_total": total, "residual_totals": {str(branch["mask"]): branch["a1_numeric_total"] for branch in maps["branches"]}, "logical_status": "A single conserved total under an inferred hybrid palette; not a positional reconstruction", "assumptions": ["B/Y denote color initials", "initials are numeric cell weights, not only marker labels", "achromatic cells keep the verified binary values", "near-white treated as achromatic zero"], "contradiction": "341 selects the61-letter branch, whereas the conditional continuous25-event frame selects the60-letter branch (336). Neither convention is proven creator intent.", "no_sumlists_or_trial_inputs_generated": True}


def hypothesis_records():
    page = "research/sources/salphaseion.html:18"
    speech = "research/artifacts/phase32-beaufort.txt:1"
    color = "research/evidence/cycle02/_work__creator_jrk.txt:195"
    return [
        {
            "id": "C10-G01", "hypothesis": "The two local shabef commands bracket a container-processing step: SHA256(X) -> SMALL -> SHA256(Y).",
            "source_evidence": ["First shabef precedes the embedded public container; shabefanstoo follows it", "anstoo plausibly reads 'answer too'"], "source_locations": [page, "research/evidence/cycle02/_work__chat_transcript.txt:22488"],
            "assumptions": ["Reading order expresses execution order", "ans refers to the intervening container's answer", "The first digest is used by that container rather than an earlier text step"],
            "operation_order": ["obtain X (unknown)", "SHA256(X)", "interpret the SMALL container (symbolic, not executed)", "SHA256(Y) (Y unknown)", "next object unknown"], "input": "Unresolved first-hint/text result X and published container", "output": "Unresolved answer Y then its digest",
            "confidence": {"physical_layout": "HIGH", "runtime_graph": "MEDIUM", "arguments_and_next_target": "LOW"}, "contradictions": ["No explicit X, Y, connector or named destination", "Cosmic is a separate textarea; adjacency does not prove a digest edge"], "next_test": "Bind each pronoun to a source object using exact formatting/context, not a guessed readable output", "status": "PROMISING",
        },
        {
            "id": "C10-G02", "hypothesis": "matrixsumlist is a postfix object label for dbbi, rather than an imperative performed after it.",
            "source_evidence": ["dbbi91 immediately precedes the separately encoded matrixsumlist word", "Decoded instruction words contain no verbs or punctuation separating label from operation"], "source_locations": [page], "assumptions": ["Encoded inline labels identify preceding objects", "dbbi encodes matrix-sum-list data through an unresolved representation"],
            "operation_order": ["read dbbi", "decode its postfix matrixsumlist label", "interpret dbbi as an object of that type", "use faed and trailer labels in an unresolved second step"], "input": "dbbi91", "output": "A hypothesized sum-list object, not verified",
            "confidence": "MEDIUM-LOW", "contradictions": ["Neighboring enter behaves as a formatting instruction, not an object name", "Previously tested literal codecs do not identify residual60/61 with fixed binary axis/ring lists"], "next_test": "Test an evidence-derived numeric palette for an exact representation, preserving positions and all symbols", "status": "INCONCLUSIVE",
        },
        {
            "id": "C10-G03", "hypothesis": "matrixsumlist is an imperative constructing an image-derived object used by the residual/faed branch.",
            "source_evidence": ["Word names matrix, sum and list", "Color hint explicitly returns to the first puzzle piece", "Prime extraction leaves nonprime symbols and connects to original image events"], "source_locations": [page, color, "research/artifacts/cycle03/prime-boundary.json"], "assumptions": ["matrix refers to the original image", "Residual or faed is the consumer, rather than sumlist being the final result", "Axis and numeric encoding are not specified by the word itself"],
            "operation_order": ["image and prime/color analysis", "construct a matrix sum list (operand/axis unknown)", "apply to residual or faed through an unknown operation", "resolve trailer commands"], "input": "Original matrix, residual60/61, faed570", "output": "An intermediate list and unresolved instruction object",
            "confidence": "MEDIUM for image referent; LOW for consumer edge", "contradictions": ["No encoded axis, ordering or operation on the residual", "Literal, missing-cell, numeric-routing and post-Bifid-routing realizations have already failed their documented gates"], "next_test": "Compare label and weighted-object interpretations through exact public-data invariants only", "status": "INCONCLUSIVE",
        },
        {
            "id": "C10-G04", "hypothesis": "dbbi supports parallel prime/color and Bifid branches; the Bifid result is an intermediate, not a verified instruction.",
            "source_evidence": ["Exact dbbi first-occurrence square and faed570/full-period Bifid reproduce btcseed", "Prime residual is derived from the same dbbi", "Prefix coordinate map uses only faed0..3 and285..288"], "source_locations": [page, "research/evidence/cycle02/_work__chat_transcript.txt:122232", "research/artifacts/cycle09/exact-prime-bifid-control.json"], "assumptions": ["Creator intended Bifid, which is named only in community research", "Two transforms of the same text are intentional branches"],
            "operation_order": ["dbbi -> first-occurrence keyed square", "faed -> full-period Bifid", "dbbi -> prime residual in parallel", "unknown join via matrixsumlist or trailer labels"], "input": "dbbi91, faed570, original image", "output": "570-letter transformed public text and60/61-letter residual; join unknown",
            "confidence": "HIGH for transform reproducibility; LOW-MEDIUM for intended graph", "contradictions": ["Bifid is absent from primary instructions", "Even-position output restriction is structural", "Conditional prime/Bifid evidence is dependent; prefix does not validate the remaining563 symbols"], "next_test": "Require any proposed join to preserve the mapped source dependency graph and explain the entire output", "status": "PROMISING",
        },
        {
            "id": "C10-G05", "hypothesis": "The first-hint/last-command relation recalls the HASHTHETEXT/SHA operation, not necessarily the earliest hint's literal text.",
            "source_evidence": ["HASHTHETEXT is an audio-derived command with no explicit argument", "Primary shabef decodes to SHA256 while the remaining phrase stays ordinary text", "2019 hash was explained as a website-error validation aid"], "source_locations": ["research/artifacts/audio-reproduction.json", page, "research/evidence/cycle02/_work__creator_jrk.txt:41", "research/evidence/cycle02/_work__chat_transcript.txt:12406"], "assumptions": ["first means an earlier operative instruction rather than first chronologically", "Last command reuses the hash operation on a new result", "HASHTHETEXT is intended to be recalled beyond the already documented entry route"],
            "operation_order": ["earlier HASHTHETEXT -> public page entry (documented)", "derive a new text object (unknown)", "reuse SHA256 as final text command", "ans-too may repeat the operation"], "input": "An earlier instruction and a newly constructed text object", "output": "Hash operation on an unknown referent",
            "confidence": "MEDIUM-LOW", "contradictions": ["ourfirsthint need not mean the audio hint", "January8 2021 echo is a Deleted Account label, not authenticated creator evidence", "Hash argument case/spacing and final placement are unspecified"], "next_test": "Source-context audit of first-hint usages; distinguish chronological first, first puzzle piece and first command", "status": "INCONCLUSIVE",
        },
        {
            "id": "C10-G06", "hypothesis": "lastwordsbeforearchichoice and thispassword are a local source-selection recipe, potentially separate from matrixsumlist.",
            "source_evidence": ["Two consecutive z-delimited decoded phrases before the first SHA command", "Verified speech orders sourcecodes -> reinsertingtheprimebasics -> afterwhich -> selectfrom", "No literal choice occurs in the modified speech"], "source_locations": [page, speech, "research/evidence/cycle02/_work__chat_transcript.txt:18957"], "assumptions": ["Archi denotes the Architect", "Choice denotes selectfrom in the modified speech OR the movie passage quoted in secondary chat", "thispassword refers backward to the selected words rather than forward to a recipe"],
            "operation_order": ["identify the correct Architect source and selection boundary", "select the referenced last words", "interpret thispassword binding", "apply the adjacent SHA command if it governs the selection"], "input": "An unresolved choice-bearing text object", "output": "A selected text object (not generated as trial material)",
            "confidence": "MEDIUM for Architect reference; LOW for exact words/binding", "contradictions": ["Modified speech has select but no literal choice", "Secondary movie quotation is not present in verified speech", "No primary word boundaries or count resolve 'last words'", "Previously tested reinsertingtheprimebasics compositions are not new experiments"], "next_test": "Token/span alignment of the preserved Architect quotation with the creator-modified speech; no phrase enumeration", "status": "INCONCLUSIVE",
        },
        {
            "id": "C10-G07", "hypothesis": "b/be encode color initials B/Y through2/25, and matrixsumlist may refer to a weighted-color numeric object.",
            "source_evidence": ["Primary shabef supplies b2,e5,f6", "Prime markers are b and be", "Creator-attributed hint says Yellow has a number and so does Blue", "With binary achromatic values and blue2/yellow25, original image total341 equals residual61 A1 total341"], "source_locations": [page, color, "research/sources/gsmg-puzzle.png", "research/artifacts/cycle10/instruction-graphs.json"], "assumptions": ["b/be digits are decoded again as A1Z26 B/Y", "B/Y denote numeric cell weights, not only labels", "Black/white retain1/0", "Near-white remains0"],
            "operation_order": ["b/be ->2/25 ->B/Y color identities", "original image -> fixed hybrid weighted matrix", "matrix -> sum-list object (axis unresolved)", "compare with nonprime residual numeric object before any further operation"], "input": "Original color image and both documented residual branches", "output": "A341-total matrix object and a competing61-letter branch interpretation",
            "confidence": "LOW; exact single-total equality, no spatial evidence", "contradictions": ["Weighted total is not a list reconstruction", "61-letter branch conflicts with conditional25-event60-letter selection", "Many sums can agree accidentally; no multiple-testing significance claimed", "Marker meaning may be a label rather than weight"], "next_test": "Freeze a positional conservation audit: only original palette black1,white0,near-white0,blue2,yellow25, verified spiral, and the two existing branch maps. Demand a source-backed partition/order before computing any list representation.", "status": "INCONCLUSIVE",
        },
    ]


def data_flow_graphs():
    return {
        "C10-G01": {"nodes": ["unknown-X", "first-SHA", "SMALL-container", "unknown-Y", "answer-SHA", "unknown-next"], "edges": [["unknown-X", "first-SHA", "UNKNOWN_REFERENT"], ["first-SHA", "SMALL-container", "INFERRED_FROM_LAYOUT"], ["SMALL-container", "unknown-Y", "UNRESOLVED_PROCESSING"], ["unknown-Y", "answer-SHA", "INFERRED_ANS_BINDING"], ["answer-SHA", "unknown-next", "UNKNOWN_DESTINATION"]]},
        "C10-G02": {"nodes": ["dbbi", "sumlist-typed-object", "faed-or-trailer-consumer"], "edges": [["dbbi", "sumlist-typed-object", "INFERRED_POSTFIX_LABEL"], ["sumlist-typed-object", "faed-or-trailer-consumer", "UNKNOWN_JOIN"]]},
        "C10-G03": {"nodes": ["image", "matrixsumlist-operation", "sumlist", "residual-or-faed", "trailer-consumer"], "edges": [["image", "matrixsumlist-operation", "INFERRED_MATRIX_REFERENT"], ["matrixsumlist-operation", "sumlist", "INFERRED_IMPERATIVE"], ["sumlist", "residual-or-faed", "UNKNOWN_OPERATION"], ["residual-or-faed", "trailer-consumer", "UNKNOWN_JOIN"]]},
        "C10-G04": {"nodes": ["dbbi", "square", "faed", "Bifid570", "residual", "unknown-join"], "edges": [["dbbi", "square", "VERIFIED_FIRST_OCCURRENCE_TRANSFORM"], ["square", "Bifid570", "VERIFIED_TRANSFORM_NOT_INTENT"], ["faed", "Bifid570", "VERIFIED_TRANSFORM_NOT_INTENT"], ["dbbi", "residual", "VERIFIED_CONDITIONAL_PRIME_TRANSFORM"], ["Bifid570", "unknown-join", "UNKNOWN_JOIN"], ["residual", "unknown-join", "UNKNOWN_JOIN"]]},
        "C10-G05": {"nodes": ["audio", "HASHTHETEXT", "entry-image-text", "archived-page-entry", "new-text", "final-SHA"], "edges": [["audio", "HASHTHETEXT", "REPRODUCED_SPECTROGRAM_HUMAN_TRANSCRIPTION"], ["HASHTHETEXT", "entry-image-text", "SECONDARY_ARGUMENT_INTERPRETATION"], ["entry-image-text", "archived-page-entry", "PRIOR_DOCUMENTED_PUBLIC_ROUTE_NOT_REEXECUTED"], ["HASHTHETEXT", "final-SHA", "INFERRED_OPERATOR_RECALL"], ["new-text", "final-SHA", "UNKNOWN_REFERENT"]]},
        "C10-G06": {"nodes": ["Architect-source", "choice-boundary", "last-words", "thispassword-label", "SHA-command"], "edges": [["Architect-source", "choice-boundary", "AMBIGUOUS_SOURCE_AND_ANCHOR"], ["choice-boundary", "last-words", "UNKNOWN_WORD_COUNT"], ["last-words", "thispassword-label", "INFERRED_BACKWARD_BINDING"], ["thispassword-label", "SHA-command", "INFERRED_LAYOUT_EDGE"]]},
        "C10-G07": {"nodes": ["b-be-markers", "B-Y-identities", "color-image", "fixed-weighted-matrix", "sumlist", "residual61"], "edges": [["b-be-markers", "B-Y-identities", "VERIFIED_2_25_A1Z26_ARITHMETIC"], ["B-Y-identities", "fixed-weighted-matrix", "INFERRED_COLOR_WEIGHTS"], ["color-image", "fixed-weighted-matrix", "FIXED_DIAGNOSTIC_MAPPING_NOT_INTENT"], ["fixed-weighted-matrix", "sumlist", "UNKNOWN_AXIS_AND_PARTITION"], ["sumlist", "residual61", "ONLY_TOTAL_EQUALITY_NO_POSITIONAL_EDGE"]]},
    }


def build_report():
    layout, compact, span = primary_layout()
    maps = derived_source_maps(compact, span)
    occurrences, inventory = preserved_occurrences()
    report = {
        "id": "C10-INSTRUCTION-CONSTRUCTION", "revision": 3, "date": "2026-09-30", "status": "INCONCLUSIVE",
        "scope": "Offline public text/image provenance and deterministic transformations only",
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
        "primary_layout": layout, "derived_source_maps": maps, "speech": speech_map(),
        "corpus_inventory": inventory, "corroboration": corroboration(), "weighted_diagnostic": weighted_diagnostic(maps),
        "hypotheses": hypothesis_records(),
        "data_flow_graphs": data_flow_graphs(),
        "object_roles": {
            "SMALL": {"best_supported": "Secondary name for an embedded published ciphertext container, hence an input to a possible processing step", "eliminated": ["literal creator command", "literal primary text input", "known decoded output"], "remaining": ["container input", "intermediate stage label"], "not_proven": "Container's decoded result or its next consumer"},
            "matrixsumlist": {"verified": "Decoded inline word between dbbi91 and faed570", "remaining": ["postfix object/type label", "imperative producing a matrix-sum-list object", "indirect ordering clue if a later explicit route is identified"], "not_proven": "Axis, weights, operand, serialization or routing algorithm"},
            "residual60": {"verified": "Derived non-contiguous nonprime symbols from dbbi; conditional frame convention selects it", "remaining": ["intermediate numeric/text object", "input to an unresolved join", "checkpoint only"]},
            "faed570": {"verified": "Research name for exact570-symbol source; literal faed prefix but no570 suffix in primary", "remaining": ["input to source-keyed Bifid", "unresolved numeric/text object"]},
        },
        "best_supported_order": "Physical: dbbi91 -> encoded matrixsumlist -> faed570 -> three z-delimited trailer segments -> first shabef command -> embedded container with inline enter -> shabefanstoo; Cosmic follows under its own heading/textarea. Execution: only a plausible SHA(X) -> container -> SHA(Y) skeleton; X,Y and next consumer remain unknown.",
        "eliminated_interpretations": ["four first hint as the correctly split command", "SMALL as literal creator text or a decoded answer", "every z as a clue delimiter", "matrixsumlist naming a uniquely specified row/column order", "btcseed as a verified complete instruction", "Deleted Account echo as authenticated creator confirmation", "Community SMALL-to-Cosmic or SMALL-to-inner32 edges as proven", "A literal choice-word boundary in the modified speech", "Literal binary sum-list identity and earlier tested routing constructions as unexplored paths"],
        "highest_value_next_experiment": {"name": "Fixed weighted-color positional conservation audit", "reason": "The only new numeric link connects color wording, mixed numeric encoding, prime markers, matrixsumlist and residual length while exposing a61-vs60 branch conflict", "allowed_inputs": ["unchanged original14x14 image", "fixed palette black1/white0/near-white0/blue2/yellow25", "already verified down-first counterclockwise spiral", "documented505 and1017 token maps"], "required_preflight": "Identify a partition and comparison order explicitly supported by existing source boundaries; if no such partition exists, report an unsupported edge rather than invent one", "pass_gate": "Exact position-preserving reconstruction with all symbols accounted for, not total341 alone", "exclusions": ["new palette permutations", "new geometric routes", "trial-material generation", "cipher searches"]},
    }
    return report, occurrences


def write_artifact(path, payload):
    if path.exists() and path.read_bytes() != payload:
        raise ValueError(f"Refusing to overwrite differing research artifact: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def main():
    report, occurrences = build_report()
    write_artifact(OUTPUT / "instruction-graphs-v3.json", (json.dumps(report, indent=2, sort_keys=True) + "\n").encode())
    write_artifact(OUTPUT / "instruction-occurrences-v3.jsonl", "".join(json.dumps(entry, sort_keys=True) + "\n" for entry in occurrences).encode())
    print(json.dumps({"status": report["status"], "hypotheses": len(report["hypotheses"]), "indexed_occurrences": len(occurrences), "inspected_public_text_files": len(report["corpus_inventory"]["inspected_files"]), "primary_small_literal": report["primary_layout"]["small_literal_present"], "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
