#!/usr/bin/env python3
import json
from itertools import islice, permutations
from math import factorial
from time import perf_counter

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS, SOURCES
from tools.research_common import fingerprint, source_record, write_once_json


def test_prefixes():
    source = split_segments()["faed"]
    target = "btcseed"
    half = len(source) // 2
    required = source[:4] + source[half:half + 4]
    if len(source) % 4 != 2:
        raise ValueError("Exact prefix shortcut requires observed length570")
    total = factorial(9)
    sample = list(islice(permutations("abcdefghi"), 512))
    started = perf_counter()
    for ordering in sample:
        square = "".join(ordering) + "klmnopqrstuvwxyz"
        bifid(required, square, len(required))
    throughput = len(sample) / max(1e-9, perf_counter() - started)
    plan = {"id": "C04-BIFID-SQUARE-CONTROL", "source": source_record(SOURCES / "salphaseion.html"), "search_space": {"first_nine_symbol_permutations": total, "fixed_appended_alphabet": "klmnopqrstuvwxyz", "prefix": target, "source_positions": [0, 1, 2, 3, half, half + 1, half + 2, half + 3]}, "estimated_seconds": round(total / throughput, 3), "benchmark_prefixes": len(sample), "benchmark_prefixes_per_second": round(throughput, 1), "purpose": "Measure prefix selectivity and validate the public eight-key claim; no AES trials or wallet-key enumeration"}
    output = ARTIFACTS / "cycle04"
    write_once_json(output / "bifid-square-control-plan.json", plan)
    matches = []
    started = perf_counter()
    tested = 0
    for ordering in permutations("abcdefghi"):
        square = "".join(ordering) + "klmnopqrstuvwxyz"
        prefix = bifid(required, square, len(required))
        tested += 1
        if prefix.startswith(target):
            full = bifid(source, square, len(source))
            if not full.startswith(target):
                raise ValueError("Prefix shortcut and full decode disagree")
            matches.append({"square": square, "output_prefix": full[:16], "output_sha256": fingerprint(full.encode()), "is_exact_source_key": square == key_square(split_segments()["dbbi"])})
    if tested != total:
        raise ValueError("Not all specified permutations checked")
    result = {"id": plan["id"], "square_prefixes_tested": tested, "prefix_matches": len(matches), "matches": matches, "source_key_matches": sum(match["is_exact_source_key"] for match in matches), "elapsed_seconds": round(perf_counter() - started, 3), "status": "CONFIRMED", "meaning": "Confirms count/derivation under this constrained square family only; not proof of intended cipher or final key. Square-selection frequency and shuffled-data null probabilities measure different conditional questions."}
    write_once_json(output / "bifid-square-control.json", result)
    print(json.dumps(plan, indent=2))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    test_prefixes()
