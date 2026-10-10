#!/usr/bin/env python3
"""Check direct consumers of the fixed matrix sum list by type constraints only."""

import json

from tools.gsmg import ARTIFACTS
from tools.matrix_sum_interface import report as sum_report


def domain_check(values, minimum, maximum):
    failures = [index for index, value in enumerate(values) if not minimum <= value <= maximum]
    return {
        "required_range_inclusive": [minimum, maximum],
        "valid": not failures,
        "failing_offsets_zero_based": failures,
    }


def report():
    source = sum_report()
    values = source["observed"]["column_sum_list"]
    speech = (ARTIFACTS / "phase32-beaufort.txt").read_text().strip()
    if "yourlifeisthesumofaremainder" not in speech:
        raise ValueError("Expected preserved sum/remainder wording")
    selection = "selectfromovertwentythreecipherssixteenencryptionsandorsevenintertwinedpasswords"
    if selection not in speech:
        raise ValueError("Expected preserved selection scope")
    inherited = json.loads((ARTIFACTS / "cycle15/sum-remainder-audit.json").read_text())
    if "shared with both preserved movie quotations" not in inherited["result"]:
        raise ValueError("Sum/remainder provenance changed")
    selector = json.loads((ARTIFACTS / "cycle12/selector-evidence.json").read_text())
    creator_scope = selector["source_boundaries"]
    creator_counts = creator_scope["creator_export_literal_keyword_counts"]
    if creator_scope["creator_export_message_count"] != 411 or any(creator_counts.values()):
        raise ValueError("Creator-record literal operator coverage changed")

    direct_checks = {
        "column_permutation_zero_based": domain_check(values, 0, 14) | {
            "also_requires_all_distinct": True,
            "all_distinct": len(set(values)) == len(values),
        },
        "column_permutation_one_based": domain_check(values, 1, 15) | {
            "also_requires_all_distinct": True,
            "all_distinct": len(set(values)) == len(values),
        },
        "one_row_per_faed_column_zero_based": domain_check(values, 0, 37),
        "one_row_per_faed_column_one_based": domain_check(values, 1, 38),
        "one_row_per_half_panel_column_zero_based": domain_check(values, 0, 18),
        "one_row_per_half_panel_column_one_based": domain_check(values, 1, 19),
        "one_bifid_square_cell_per_column_zero_based": domain_check(values, 0, 24),
        "one_bifid_square_cell_per_column_one_based": domain_check(values, 1, 25),
        "direct_printable_ascii": domain_check(values, 32, 126),
        "partition_full_faed": {"required_total": 570, "observed_total": sum(values), "valid": sum(values) == 570},
        "partition_one_faed_half": {"required_total": 285, "observed_total": sum(values), "valid": sum(values) == 285},
    }
    if any(check["valid"] for check in direct_checks.values()):
        raise ValueError("An expected direct-operation rejection no longer holds")

    return {
        "id": "C24-MATRIX-OPERATOR-FEASIBILITY",
        "date": "2026-10-02",
        "status": "REJECTED",
        "hypothesis": "The fixed15-value matrix sum list directly specifies a downstream permutation, row/cell selection, complete partition, or printable text without another convention.",
        "input": "The exact C24 sum-list15 and fixed15-column FAED/Bifid dimensions",
        "invariant": "A direct interpretation must fit its target domain without modulo, ranking, tie breaking, offsets, truncation, padding, or a guessed arithmetic sign.",
        "observed": {
            "sum_list": values,
            "count": len(values),
            "unique_values": len(set(values)),
            "duplicate_values": sorted(value for value in set(values) if values.count(value) > 1),
            "minimum": min(values),
            "maximum": max(values),
            "total": sum(values),
            "direct_checks": direct_checks,
            "direct_interpretations_passing": 0,
        },
        "source_language_constraints": {
            "sum_of_a_remainder": "Inherited from the preserved Matrix dialogue; cycle15 found it supplies no independent modulus, operand, or serialization.",
            "select": "The preserved modified speech scopes select to twenty-three ciphers, sixteen encryptions, and/or seven intertwined passwords, not matrix rows or columns.",
            "roadmap": "The creator-attributed roadmap orders yellowblueprimes before matrixsumlist but does not name the action after the list is formed.",
            "creator_export_literal_scan": {
                "messages": creator_scope["creator_export_message_count"],
                "keyword_counts": creator_counts,
                "scope_limit": "Absence of these literal words is not proof that no encoded or synonymous instruction exists.",
            },
        },
        "classification": {
            "direct_permutation": "REJECTED",
            "direct_row_or_square_selection": "REJECTED",
            "direct_complete_partition": "REJECTED",
            "direct_printable_text": "REJECTED",
            "normalized_or_arithmetic_consumer": "UNKNOWN",
        },
        "missing_parameters": [
            "downstream target plane or rendered matrix",
            "action such as add, subtract, reorder, select, or partition",
            "modulus or reduction rule if values must enter a bounded domain",
            "index origin for selection",
            "tie rule for ranking because6 and13 repeat",
        ],
        "result": "No direct interpretation of the exact sum-list15 is type-valid. Every surviving consumer requires at least one unauthored normalization or action parameter, so applying the list now would be an unconstrained transform sweep.",
        "next_test": "Search only for an authored verb or numerical convention that fixes one missing parameter. Do not execute a downstream transform until target plane, action, and required normalization are all independently bound.",
        "new_cryptographic_trials": 0,
        "new_trial_inputs": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
