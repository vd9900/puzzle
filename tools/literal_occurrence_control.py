import json
from collections import Counter
from fractions import Fraction
from math import comb, prod

from tools.instruction_graphs import ROOT, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle12"


def falling(value, width):
    if width < 0:
        raise ValueError("Negative falling-factorial width")
    return prod(range(value - width + 1, value + 1)) if width <= value else 0


def unbordered_occurrence_probability(population, word, selected_length):
    if not word or any(word[:width] == word[-width:] for width in range(1, len(word))):
        raise ValueError("This exact control requires a nonempty unbordered word")
    if selected_length < 0 or selected_length > len(population):
        raise ValueError("Selected source length is outside the fixed population")
    counts = Counter(population)
    wanted = Counter(word)
    width = len(word)
    maximum = min([selected_length // width] + [counts[symbol] // amount for symbol, amount in wanted.items()])
    terms = []
    probability = Fraction(0)
    for number in range(1, maximum + 1):
        placements = comb(selected_length - (width - 1) * number, number)
        assignments = prod(falling(counts[symbol], number * amount) for symbol, amount in wanted.items())
        probability_term = Fraction(placements * assignments, falling(len(population), number * width))
        probability += probability_term if number % 2 else -probability_term
        terms.append({"occurrences": number, "nonoverlapping_start_sets": placements, "intersection_probability_sum": str(probability_term), "sign": 1 if number % 2 else -1})
    expected = Fraction(max(0, selected_length - width + 1) * prod(falling(counts[symbol], amount) for symbol, amount in wanted.items()), falling(len(population), width)) if len(population) >= width else Fraction(0)
    return {"at_least_one_exact_probability": str(probability), "at_least_one_decimal": float(probability), "expected_occurrences": str(expected), "terms": terms}


def report():
    path = ROOT / "research/artifacts/phase32-checkerboard.txt"
    population = path.read_text().strip()
    frozen = ROOT / "research/artifacts/cycle12/source-join-preflight-v2.json"
    joined = json.loads(frozen.read_text())
    cases = []
    for result in joined["results"]:
        word_result = next(item for item in result["literal_checkpoint_tests"] if item["literal"] == "yang")
        if word_result["count"] != 1:
            raise ValueError("Observed fixed partial occurrence differs")
        cases.append({"mask": result["mask"], "selected_positions": result["raw_selected_positions_zero_based"], "selected_length": result["raw_selected_length"], "observed_literal_count": 1, "control": unbordered_occurrence_probability(population, "yang", result["raw_selected_length"])})
    return {
        "id": "C12-PARTIAL-LITERAL-CONTROL", "date": "2026-09-30", "status": "CONFIRMED",
        "hypothesis": "Quantify the fixed yang occurrence under an exact uniform multiset-permutation control, without generating alternative puzzle text",
        "source_evidence": [source(path), source(frozen)],
        "source_locations": ["research/artifacts/phase32-checkerboard.txt:1", "research/artifacts/cycle12/source-join-preflight-v2.json:1"],
        "assumptions": ["Uniform shuffle of the complete91-letter multiset", "Published selector positions and literal yang fixed in advance for this conditional calculation", "Unbordered word makes overlapping occurrences incompatible"],
        "operation_order": ["read fixed source multiset", "hold published selected indices fixed", "count nonoverlapping literal-start events exactly", "apply finite inclusion-exclusion"],
        "input": "Public91-letter multiset, documented30/31 selected positions and one literal", "output": "Exact rational probabilities and auditable inclusion-exclusion terms",
        "confidence": "HIGH for stated arithmetic control; no global creator-intent confidence inferred",
        "word": "yang", "population_length": len(population), "word_symbol_counts": {symbol: population.count(symbol) for symbol in "yang"},
        "cases": cases,
        "formula": "P(any occurrence)=sum_k (-1)^(k+1) C(m-(w-1)k,k) * product_s (count_s)_(k*word_count_s) / (N)_(kw)",
        "result": "Partial yang has probability about0.000176786/0.000183333 for fixed30/31-symbol projections under this artificial null. Neither result is a discovery-wide p-value, a complete yin-yang output, or proof of the intended source join.",
        "contradictions": ["Literal and source selector were discovered through prior community investigation, not preregistered", "Original English text is not a uniform shuffled multiset", "Unknown upstream trials/anagram searches prevent a discovery-wide significance claim", "Both branches share the exact same four source indices, so their evidence is dependent", "No probability is multiplied with prime/Bifid clue controls"],
        "next_test": "Only source-evidenced operations explaining the missing literal and ordered matrixsumlist/Architect join may be pursued; the conditional control does not justify a search expansion.",
        "new_random_samples": 0, "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "partial-literal-control.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "conditional_probabilities": [case["control"]["at_least_one_exact_probability"] for case in document["cases"]], "new_samples": 0, "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
