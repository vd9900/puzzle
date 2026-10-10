#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from fractions import Fraction
from math import prod

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import key_square
from tools.gsmg import ARTIFACTS
from tools.prime_bifid_controls import branch_templates, prefix_for_source_key
from tools.research_common import fingerprint, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle09"


def advance_order(order, consumed, symbols):
    for symbol in symbols:
        if symbol in order[:consumed]:
            continue
        if consumed == len(order) or symbol != order[consumed]:
            return None
        consumed += 1
    return consumed


def first_occurrence_probability(template, residual, order):
    counts = Counter(residual)
    alphabet = tuple(sorted(counts))
    if len(order) != len(set(order)) or set(order) != set(alphabet) | set("".join(symbol or "" for symbol in template)):
        raise ValueError("The target first-occurrence order must cover the exact template/residual alphabet")
    fixed = set("".join(symbol or "" for symbol in template))
    observed_fixed = set()
    states = {(tuple(counts[symbol] for symbol in alphabet), 0): 1}
    draws = 0
    peak_states = 1
    cutoff = None
    for position, token in enumerate(template):
        following = defaultdict(int)
        if token is None:
            draws += 1
            for (remaining, consumed), ways in states.items():
                for index, symbol in enumerate(alphabet):
                    if remaining[index] == 0:
                        continue
                    next_consumed = advance_order(order, consumed, symbol)
                    if next_consumed is None:
                        continue
                    updated = list(remaining)
                    updated[index] -= 1
                    following[(tuple(updated), next_consumed)] += ways * remaining[index]
        else:
            observed_fixed.update(token)
            for (remaining, consumed), ways in states.items():
                next_consumed = advance_order(order, consumed, token)
                if next_consumed is not None:
                    following[(remaining, next_consumed)] += ways
        states = following
        peak_states = max(peak_states, len(states))
        if observed_fixed == fixed:
            cutoff = position
            break
    if cutoff is None:
        raise ValueError("Expected all fixed symbols to appear before the residual finishes")
    if any(symbol is not None and not set(symbol) <= fixed for symbol in template[cutoff + 1:]):
        raise ValueError("Tail contains an unmodeled fixed symbol")
    population = len(residual)
    denominator = prod(range(population - draws + 1, population + 1))
    probability = Fraction(0, 1)
    indices = {symbol: index for index, symbol in enumerate(alphabet)}
    for (remaining, consumed), ways in states.items():
        if not fixed <= set(order[:consumed]):
            raise ValueError("The early stop did not include every fixed symbol")
        unseen = order[consumed:]
        tail = Fraction(1, 1)
        for index, symbol in enumerate(unseen):
            pending = sum(remaining[indices[next_symbol]] for next_symbol in unseen[index:])
            tail *= Fraction(remaining[indices[symbol]], pending)
        probability += Fraction(ways, denominator) * tail
    return probability, {"prefix_residual_draws": draws, "last_required_fixed_token_logical_one_based": cutoff + 1, "surviving_states": len(states), "peak_states": peak_states, "tail_method": "Conditional unseen-letter first occurrences form a size-biased order with probability count(letter)/sum(counts of still-unseen letters); all later fixed b/e symbols have already occurred"}


def report():
    segments = split_segments()
    source_square = key_square(segments["dbbi"])
    square_path = ARTIFACTS / "cycle04/bifid-square-control.json"
    square_control = json.loads(square_path.read_text())
    if square_control["prefix_matches"] != 8 or square_control["square_prefixes_tested"] != 362880:
        raise ValueError("The previously completed bounded square control differs")
    controls = []
    for mask, (template, residual) in branch_templates().items():
        total = Fraction(0, 1)
        source_probability = Fraction(0, 1)
        terms = []
        for match in square_control["matches"]:
            square = match["square"]
            order = square[:9]
            if prefix_for_source_key(segments["faed"], order) != "btcseed":
                raise ValueError("A preserved square does not produce the exact prefix")
            probability, diagnostics = first_occurrence_probability(template, residual, order)
            total += probability
            if square == source_square:
                source_probability += probability
            terms.append({"square_fingerprint": fingerprint(square.encode()), "is_original_source_square": square == source_square, "exact_probability_numerator": probability.numerator, "exact_probability_denominator": probability.denominator, "exact_probability_decimal": float(probability), "diagnostics": diagnostics})
        controls.append({
            "mask": mask, "logical_tokens": len(template), "residual_symbols": len(residual), "terms": terms,
            "exact_prefix_probability_numerator": total.numerator, "exact_prefix_probability_denominator": total.denominator,
            "exact_prefix_probability_decimal": float(total),
            "exact_original_square_probability_numerator": source_probability.numerator,
            "exact_original_square_probability_denominator": source_probability.denominator,
            "expected_prefix_matches_per_10000": float(total) * 10000,
            "null": "Exact uniform permutation of the residual multiset, fixed prime b/be template and exact faed source, same null as cycle08 Monte Carlo;8 previously enumerated prefix-producing first-nine squares reused, no new alphabet search",
        })
    document = {
        "id": "C09-EXACT-PRIME-BIFID-CONTROL", "status": "CONFIRMED",
        "source_evidence": [source_record(square_path), source_record(ARTIFACTS / "cycle08/prime-conditioned-bifid-control.json"), source_record(ARTIFACTS / "cycle03/prime-boundary.json")],
        "controls": controls, "new_passwords": 0, "new_aes_trials": 0,
        "result": "Exact first-occurrence probability under the fixed prime grammar replaces sampling uncertainty for that conditional question; neither statistical rarity nor square uniqueness verifies a downstream AES stage or creator intent",
        "limits": "Not a global discovery p-value, no correction for historical hypothesis selection and no independence claim; fixed first-nine keyed-square family only. Alternative squares are probability terms, never AES/password candidates",
    }
    write_once_json(OUTPUT / "exact-prime-bifid-control.json", document)
    print(json.dumps({"id": document["id"], "status": document["status"], "controls": [{name: value for name, value in control.items() if name not in ("terms", "null")} for control in controls], "new_aes_trials": 0, "result": document["result"]}, indent=2))
    return document


if __name__ == "__main__":
    report()
