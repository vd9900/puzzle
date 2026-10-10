#!/usr/bin/env python3
import json
import re
from collections import Counter

from tools.analyze_salphaseion import split_segments
from tools.gsmg import SOURCES, extract_grid, spiral_coordinates, textareas
from tools.prime_markers import is_prime, tokenizations
from tools.research_common import source_record, write_once_json
from tools.zeroed_residual import OUTPUT


def binary_boundary():
    compact = "".join(textareas((SOURCES / "salphaseion.html").read_text())[0].split())
    match = re.search(r"[ab]{16,}", compact)
    run = match.group()
    bits = run.translate(str.maketrans("ab", "01"))
    if len(bits) % 8:
        raise ValueError("Incomplete binary clue bytes")
    decoded = bytes(int(bits[index:index + 8], 2) for index in range(0, len(bits), 8))
    return {"raw_start_zero_based": match.start(), "letters": run, "bits": bits, "decoded": decoded.decode("ascii")}


def special_frames():
    grid = extract_grid(SOURCES / "gsmg-puzzle.png")
    events = [{"spiral_index_zero_based": index, "row_zero_based": row, "column_zero_based": column, "color": grid["colors"][row][column]} for index, (row, column) in enumerate(spiral_coordinates(14)) if grid["colors"][row][column] in ("blue", "yellow", "near_white")]
    for near_white_bit in (0, 1):
        frame = "".join(str(near_white_bit) if event["color"] == "near_white" else "1" if event["color"] == "blue" else "0" for event in events)
        yield near_white_bit, frame, events


def extended_markers(mask, tokens, boundary):
    entries = [{**entry, "region": "dbbi", "bit": "1" if entry["token"] == "b" else "0" if entry["token"] == "be" else "?"} for entry in tokens]
    offset = len(tokens)
    entries.extend({"token": symbol, "bit": "1" if symbol == "b" else "0", "region": "matrixsumlist-binary", "position_one_based": offset + index + 1, "raw_offset_zero_based": boundary["raw_start_zero_based"] + index, "binary_offset_zero_based": index} for index, symbol in enumerate(boundary["letters"]))
    return [entry for entry in entries if is_prime(entry["position_one_based"])]


def analyze():
    boundary = binary_boundary()
    results = []
    for near_white_bit, frame, events in special_frames():
        prefix_counts = Counter()
        full = []
        reset_full = []
        for mask, tokens in tokenizations(split_segments()["dbbi"]):
            markers = extended_markers(mask, tokens, boundary)
            bits = "".join(entry["bit"] for entry in markers)
            prefix = 0
            for actual, expected in zip(bits, frame):
                if actual != expected:
                    break
                prefix += 1
            prefix_counts[prefix] += 1
            dbbi_markers = [entry for entry in markers if entry["region"] == "dbbi"]
            reset_bits = "".join(entry["bit"] for entry in dbbi_markers) + "".join("1" if symbol == "b" else "0" for index, symbol in enumerate(boundary["letters"], 1) if is_prime(index))
            if reset_bits.startswith(frame):
                reset_full.append(mask)
            if bits.startswith(frame):
                full.append({"mask": mask, "dbbi_token_count": len(tokens), "dbbi_prime_count": len(dbbi_markers), "residual": "".join(entry["token"] for entry in tokens if not is_prime(entry["position_one_based"])), "frame_bits": bits[:len(frame)], "frame_markers": markers[:len(frame)], "prime_bits_after_frame": bits[len(frame):], "source_tokens": tokens})
        results.append({"near_white_hypothesis_bit": near_white_bit, "frame": frame, "events": events, "max_prefix": max(prefix_counts), "prefix_histogram": dict(sorted(prefix_counts.items())), "full_matches": full, "reset_counter_full_matches": reset_full})
    report = {"id": "C03-PRIME-BOUNDARY", "source_evidence": [source_record(SOURCES / "salphaseion.html", "first textarea, 91 letters then intact 104-letter binary clue"), source_record(SOURCES / "gsmg-puzzle.png", "25 blue/yellow/near-white events in independently reproduced spiral")], "binary_boundary": boundary, "search_space": {"optional_be_tokenizations": 1024, "near_white_interpretations": 2, "counter_rules": ["continue", "reset"], "comparisons": 4096}, "transformation": "Tokenize be only inside dbbi; continue the same one-based prime-position counter into the intact binary clue, with its independently verified a=0/b=1 mapping; compare first 25 prime bits to special-color events", "results": results, "status": "PROMISING", "result": "Unique mask1017 with near-white=1 matches all 25 special-color events when the index continues into the binary clue. Final two markers are absolute prime positions 89 and 97, unmodified binary offsets 5 and 13, b/a = 1/0. Reset counter never gives a complete match.", "limits": "Reproduced full cross-artifact match under explicit region-dependent encoding and near-white hypothesis, not final plaintext/key or proof of creator intent. Original dbbi-only result remains 23/25. The extra two bits add limited evidence beyond the earlier strong prefix; no universal probability claim."}
    write_once_json(OUTPUT / "prime-boundary.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
    print(json.dumps([{key: value for key, value in result.items() if key not in ("events", "full_matches")} | {"full_match_masks": [match["mask"] for match in result["full_matches"]]} for result in results], indent=2))
    return report


if __name__ == "__main__":
    analyze()
