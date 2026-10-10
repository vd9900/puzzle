import hashlib
import json
import re
from datetime import datetime, timezone

from tools.instruction_graphs import HEADER, ROOT, source, text_location, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle12"
CHAT = ROOT / "research/evidence/cycle02/_work__chat_transcript.txt"
CREATOR = ROOT / "research/evidence/cycle02/_work__creator_jrk.txt"


def record_by_header(path, wanted):
    document = path.read_text()
    headers = list(HEADER.finditer(document))
    matches = [index for index, header in enumerate(headers) if header.group() == wanted]
    if len(matches) != 1:
        raise ValueError("Expected one exact dated archived message")
    index = matches[0]
    start = headers[index].end()
    end = headers[index + 1].start() if index + 1 < len(headers) else len(document)
    raw = document[start:end]
    stripped = raw.strip()
    body_start = start + len(raw) - len(raw.lstrip())
    body_end = body_start + len(stripped)
    stamp = re.match(r"=== \[(.*?) UTC([+-]\d{2}:\d{2})\]", wanted)
    parsed = datetime.strptime(stamp.group(1) + stamp.group(2), "%d.%m.%Y %H:%M:%S%z")
    return stripped, {"source": source(path), "header": wanted, "archived_utc_timestamp": parsed.astimezone(timezone.utc).isoformat(), **text_location(document, body_start, body_end)}


def original_time_order():
    headers = [
        "=== [03.03.2026 20:27:00 UTC-05:00] Jrk Bgrt",
        "=== [03.03.2026 20:27:47 UTC-05:00] gnomad",
        "=== [03.03.2026 20:28:55 UTC-05:00] D1rty Byrd",
        "=== [03.03.2026 20:29:05 UTC-05:00] Jrk Bgrt",
        "=== [03.03.2026 20:39:06 UTC-05:00] Denis Golovkin",
        "=== [03.03.2026 20:57:30 UTC-05:00] Denis Golovkin",
    ]
    records = []
    for header in headers:
        body, evidence = record_by_header(CHAT, header)
        records.append(evidence | {"body_sha256": hashlib.sha256(body.encode()).hexdigest(), "body_not_republished": True})
    times = [datetime.fromisoformat(record["archived_utc_timestamp"]) for record in records]
    if times != sorted(times):
        raise ValueError("Original message chronology differs")
    return {
        "records": records, "bingo_record_index_zero_based": 3,
        "published_extraction_record_index_zero_based": 4, "full_recipe_record_index_zero_based": 5,
        "bingo_precedes_extraction_seconds": int((times[4] - times[3]).total_seconds()),
        "bingo_precedes_full_recipe_seconds": int((times[5] - times[3]).total_seconds()),
        "no_reply_reference_identifies_confirmation_target": True,
        "chronology_cannot_confirm_later_published_recipe": True,
        "prior_context": "Creator-labeled Looks at gnomad, gnomad referring to the eyes phrase, then another participant's social joke, then Bingo. Exact intended target is not preserved.",
    }


def greeting_audit():
    timestamp_headers = [f"=== [31.12.2025 {time} UTC-05:00] Jrk Bgrt" for time in ["22:15:02", "22:16:15", "22:17:05", "22:18:07", "22:19:05", "22:20:03"]]
    records = []
    binary = None
    for index, header in enumerate(timestamp_headers):
        body, evidence = record_by_header(CREATOR, header)
        if index < 5:
            if body != "." * (index + 1):
                raise ValueError("Original dot sequence differs")
            records.append(evidence | {"dot_count": len(body)})
        else:
            if re.fullmatch(r"[01]{8}(?: [01]{8})+", body) is None:
                raise ValueError("Greeting must be complete binary octets")
            octets = body.split()
            binary = bytes(int(octet, 2) for octet in octets).decode("ascii")
            records.append(evidence | {"octet_count": len(octets)})
    wanted = "Happy new year! Make the best of everything. Oh, and here's a \"tiny hint\" <3."
    if binary != wanted:
        raise ValueError("Direct binary greeting differs from preserved transcription")
    times = [datetime.fromisoformat(record["archived_utc_timestamp"]) for record in records]
    differences = [int((later - earlier).total_seconds()) for earlier, later in zip(times, times[1:])]
    return {
        "records": records, "decoded_public_greeting": binary,
        "binary_transform": "Direct MSB-first ASCII octets; no reversal",
        "dot_counts": [1, 2, 3, 4, 5], "exact_intermessage_seconds": differences,
        "all_messages_exactly_one_minute_apart": all(difference == 60 for difference in differences),
        "secondary_wording_overstates_exact_timing": True,
        "archive_filename_date": "2026-01-01", "transcript_local_date": "2025-12-31", "UTC_date": "2026-01-01",
        "screenshot_timezone_not_preserved": True,
        "no_explicit_join_source_axis_word_count_or_index_convention": True,
        "dot_count_less_than3_timing_interpretations_not_executed": True,
        "screenshot_source": source(ROOT / "research/sources/maintained-hints__2026-01-01-new-year-hint.png"),
    }


def source_boundary_evidence():
    selectors = []
    for path, header, classification, literal in [
        (CHAT, "=== [01.03.2021 05:16:37 UTC-05:00] Janusz Baran", "COMMUNITY_PROPOSAL", "if you know how the array is indexed ofc"),
        (CREATOR, "=== [01.03.2021 06:33:17 UTC-05:00] Jrk Bgrt", "CREATOR_ATTRIBUTED_TYPO_RESPONSE", "Ancient spelling"),
        (CREATOR, "=== [08.04.2020 15:33:39 UTC-05:00] Jrk Bgrt", "CREATOR_ATTRIBUTED_MOVIE_QUOTE", "Humph. Hope, it is the quintessential human delusion"),
        (CREATOR, "=== [08.04.2020 15:33:48 UTC-05:00] Jrk Bgrt", "EXPLICIT_NEXT_MESSAGE_NOT_A_HINT", "not a hint btw"),
    ]:
        body, evidence = record_by_header(path, header)
        if literal not in body:
            raise ValueError("Expected source-boundary wording differs")
        selectors.append(evidence | {"classification": classification, "short_public_phrase": literal})
    creator = CREATOR.read_text()
    keyword_counts = {term: len(re.findall(r"\b" + re.escape(term) + r"\b", creator, re.I)) for term in ["array", "index", "indices", "selector", "select", "choice", "sumlist", "column", "row"]}
    page = ROOT / "research/sources/salphaseion.html"
    html = page.read_text()
    relevant_tags = [match.group() for match in re.finditer(r"<(?:textarea|h1|form|input|script|img)\b[^>]*>", html, re.I)]
    return {
        "attributed_records": selectors,
        "creator_export_literal_keyword_counts": keyword_counts, "creator_export_message_count": len(list(HEADER.finditer(creator))),
        "keyword_absence_is_not_a_full_semantic_selector_proof": True,
        "primary_html": {"source": source(page), "relevant_tags": relevant_tags, "comment_count": len(re.findall(r"<!--", html)), "script_count": len(re.findall(r"<script\b", html, re.I)), "no_hidden_selector_found_in_relevant_tags": not any(re.search(r"\b(?:id|name|data-\w+)\s*=", tag) for tag in relevant_tags)},
        "spelling_hint_screenshot": source(ROOT / "research/sources/maintained-hints__2021-03-01-spelling-hint.png"),
        "not_all_primary_image_semantics_eliminated": True,
    }


def report():
    chronology = original_time_order()
    return {
        "id": "C12-SELECTOR-EVIDENCE", "date": "2026-09-30", "status": "INCONCLUSIVE",
        "hypothesis": "Preserved instruction context fixes a selector/source binding for the proposed sumlist-to-Architect join",
        "source_evidence": [source(CHAT), source(CREATOR), source(ROOT / "research/sources/salphaseion.html")],
        "source_locations": ["research/evidence/cycle02/_work__chat_transcript.txt:13996", "research/evidence/cycle02/_work__creator_jrk.txt:483", "research/evidence/cycle02/_work__chat_transcript.txt:168545", "research/evidence/cycle02/_work__creator_jrk.txt:1225", "research/sources/salphaseion.html:18"],
        "assumptions": ["Transcript timestamps/order are faithfully preserved", "No authenticated reply metadata fixes the creator confirmation target", "A lack of literal selector keywords is a bounded audit result, not impossibility proof"],
        "operation_order": ["bind exact dated messages", "check original chronology", "decode one existing public greeting", "compare attribution for array/spelling/choice claims", "inspect primary markup for explicit selectors"],
        "input": "Preserved public text, screenshots and primary HTML", "output": "Timestamp/attribution/source-boundary audit",
        "confidence": "HIGH for original chronology and exact wording; UNKNOWN for missing selector",
        "chronology": chronology, "newyear_greeting": greeting_audit(), "source_boundaries": source_boundary_evidence(),
        "result": "No explicit source/index/count convention is established by the inspected claims. Bingo predates the published extraction and full recipe. Array-indexing was a community suggestion; a creator movie quote was followed by an explicit not-a-hint disclaimer.",
        "contradictions": ["Bingo cannot be assigned to a recipe published601 seconds later from chronology alone", "The exact dot timing is73/50/62/58/58 seconds, not five60-second intervals", "Creator spelling response labels a typo, not an array-index instruction", "The preserved movie quotation has an explicit next-message disclaimer"],
        "next_test": "Inspect source-authored encoding/number anchors with an exact mapping preflight before any selector extraction; do not use community timing or anagrams as authorization for route expansion.",
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "selector-evidence.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "bingo_precedes_extraction_seconds": document["chronology"]["bingo_precedes_extraction_seconds"], "explicit_join_selector_established": False, "exact_one_minute_timing": document["newyear_greeting"]["all_messages_exactly_one_minute_apart"], "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
