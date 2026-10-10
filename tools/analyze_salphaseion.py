#!/usr/bin/env python3
import json
import math
from collections import Counter, defaultdict

from tools.gsmg import SOURCES, entropy, textareas
from tools.research_common import CYCLE, fingerprint, index_of_coincidence, source_record, write_once_json


def split_segments():
    import re

    compact = "".join(textareas((SOURCES / "salphaseion.html").read_text())[0].split())
    run = re.search(r"[ab]{16,}", compact)
    separator = compact.index("z")
    return {"dbbi": compact[:run.start()], "faed": compact[run.end():separator], "joined": compact[:run.start()] + compact[run.end():separator]}


def repeated_substrings(text, minimum=3, maximum=12):
    matches = []
    for width in range(minimum, maximum + 1):
        positions = defaultdict(list)
        for offset in range(len(text) - width + 1):
            positions[text[offset:offset + width]].append(offset)
        for substring, offsets in positions.items():
            if len(offsets) > 1:
                matches.append({"substring": substring, "offsets_zero_based": offsets, "distances": [second - first for first, second in zip(offsets, offsets[1:])]})
    return sorted(matches, key=lambda item: (-len(item["substring"]), -len(item["offsets_zero_based"]), item["substring"]))[:60]


def profile(text):
    counts = Counter(text)
    transitions = Counter(zip(text, text[1:]))
    conditional = 0.0
    outgoing = Counter(text[:-1])
    for (first, second), count in transitions.items():
        conditional -= (count / max(1, len(text) - 1)) * math.log2(count / outgoing[first])
    periodic = []
    for period in range(1, min(61, len(text))):
        streams = [text[offset::period] for offset in range(period)]
        coincidence = sum(first == second for first, second in zip(text, text[period:])) / (len(text) - period)
        periodic.append({"period": period, "autocoincidence": round(coincidence, 6), "mean_column_ic": round(sum(index_of_coincidence(stream) for stream in streams) / period, 6), "min_column_length": min(map(len, streams))})
    alphabet = sorted(counts)
    return {
        "length": len(text), "sha256": fingerprint(text.encode()), "alphabet": "".join(alphabet),
        "first_occurrence_alphabet": "".join(dict.fromkeys(text)), "counts": dict(sorted(counts.items())),
        "index_of_coincidence": index_of_coincidence(text), "uniform_nine_symbol_ic": 1 / 9,
        "entropy_bits_per_symbol": entropy(text.encode()), "uniform_entropy": math.log2(len(alphabet)),
        "conditional_transition_entropy": conditional,
        "transition_counts": {first: {second: transitions[first, second] for second in alphabet} for first in alphabet},
        "repeated_substrings": repeated_substrings(text), "periodicity": periodic,
        "exact_rectangle_widths": [width for width in range(2, len(text)) if len(text) % width == 0],
        "pair_alphabets": [{"offset": offset, "distinct": len(set(text[index:index + 2] for index in range(offset, len(text) - 1, 2))), "pairs": dict(Counter(text[index:index + 2] for index in range(offset, len(text) - 1, 2)).most_common())} for offset in (0, 1)],
        "boundary_information": "No spaces inside this segment; the live page inserts an independently decoded matrixsumlist binary run between dbbi and faed",
    }


def analyze():
    segments = split_segments()
    report = {"source": source_record(SOURCES / "salphaseion.html", "textarea:0, whitespace-normalized"), "segments": {name: profile(text) for name, text in segments.items()}, "interpretation": {"VERIFIED": "The 661 joined letters comprise 91 letters before and 570 letters after the matrixsumlist clue. All use exactly a-i.", "LIKELY": "Different marginal frequencies justify treating the two sides separately before assuming one cipher.", "HYPOTHESIS": "A nine-symbol coordinate/digit encoding or source-derived matrix/index instruction is more plausible than direct 26-letter monoalphabetic English.", "UNKNOWN": "Cipher, key, intended word boundaries, whether the two segments are independent encrypted units."}}
    write_once_json(CYCLE / "salphaseion-profile.json", report)
    for name, text in segments.items():
        (CYCLE / f"salphaseion-{name}.txt").write_text(text + "\n")
    print(json.dumps({name: {key: report["segments"][name][key] for key in ("length", "counts", "index_of_coincidence", "entropy_bits_per_symbol", "first_occurrence_alphabet")} for name in segments}, indent=2))
    return report


if __name__ == "__main__":
    analyze()
