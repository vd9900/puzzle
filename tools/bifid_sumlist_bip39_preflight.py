#!/usr/bin/env python3
"""Type-check a Bifid matrix-sum/BIP39 interface without producing indices."""

import json

from tools.gsmg import ARTIFACTS


def sum_bounds(rows, minimum, maximum):
    return [rows * minimum, rows * maximum]


def report():
    width = json.loads((ARTIFACTS / "cycle24/matrix-width-interface.json").read_text())
    seed = json.loads((ARTIFACTS / "cycle28/btcseed-format-contract.json").read_text())
    coverage_path = ARTIFACTS.parent / "evidence/cycle29/faed-matrix-sum-coverage.json"
    coverage = json.loads(coverage_path.read_text())
    shape = width["observed"]["faed_shape"]
    if shape != [38, 15] or seed["official_contracts"]["BIP39"]["mnemonic_word_counts"] != [12, 15, 18, 21, 24]:
        raise ValueError("Frozen matrix or BIP39 dimensions changed")
    if coverage["structural_coverage"]["recovered_bifid570_used_as_sum_matrix_input"]:
        raise ValueError("Prior coverage classification changed")

    rows, columns = shape
    maps = {
        "bifid_row_coordinate_zero_based": [0, 4],
        "bifid_row_coordinate_one_based": [1, 5],
        "bifid_column_coordinate_zero_based": [0, 4],
        "bifid_column_coordinate_one_based": [1, 5],
        "bifid_coordinate_pair_total_zero_based": [0, 8],
        "bifid_coordinate_pair_total_one_based": [2, 10],
        "source_keyed_square_rank_zero_based": [0, 24],
        "source_keyed_square_rank_one_based": [1, 25],
        "alphabetic_ordinal": [1, 26],
    }
    bounds = {name: sum_bounds(rows, *domain) for name, domain in maps.items()}
    bip39_index_domain = [0, 2047]
    compatible = {
        name: lower >= bip39_index_domain[0] and upper <= bip39_index_domain[1]
        for name, (lower, upper) in bounds.items()
    }
    if not all(compatible.values()):
        raise ValueError("Expected broad range compatibility changed")

    return {
        "id": "C29-BIFID-SUMLIST-BIP39-PREFLIGHT",
        "date": "2026-10-02",
        "status": "INCONCLUSIVE",
        "hypothesis": "matrixsumlist instructs reducing the recovered Bifid38x15 matrix to fifteen column sums, with btcseed identifying a fifteen-word BIP39 interface.",
        "invariant": "Structural preflight may compare dimensions and theoretical ranges only. It must not calculate the fifteen values, map them to words, repair/test a checksum, derive a seed, or check a wallet.",
        "exact_dimension_chain": {
            "bifid_matrix": shape,
            "sum_across_rows_produces_items": columns,
            "bip39_allows_word_count": 15,
            "bip39_entropy_bits_for15_words": 160,
            "bip39_checksum_bits_for15_words": 5,
            "bip39_index_domain": bip39_index_domain,
        },
        "symbolic_map_bounds_only": {
            "row_count": rows,
            "per_symbol_domains": maps,
            "possible_column_sum_bounds": bounds,
            "all_bounds_fit_bip39_index_domain": all(compatible.values()),
            "compatible_mapping_count": sum(compatible.values()),
            "actual_sum_vectors_computed": 0,
        },
        "coverage_comparison": {
            "prior_secondary_script": coverage,
            "prior_family": "raw FAED570 -> fifteen contiguous38-symbol row sums -> BIP39 candidate/checksum/wallet checks",
            "proposed_family": "recovered Bifid570 ->38x15 column sums -> possible fifteen-item BIP39 interface",
            "same_family_at_high_level": True,
            "exact_input_stage_previously_covered_by_that_script": False,
            "genuinely_new_difference": "post-Bifid rather than raw-FAED matrix input",
        },
        "architecture_discriminator": {
            "direct_literal_seed_serialization": "REJECTED by cycle28",
            "matrixsumlist_to15_item_seed_interface": "DIMENSIONALLY COMPATIBLE",
            "unique_numeric_mapping": "REJECTED: nine canonical mappings all fit the index range by bounds alone",
            "intended_bip39_architecture": "WEAK/UNKNOWN: exact15 count and btcseed wording support it, but no authored word-index or checksum instruction exists",
        },
        "blocking_unknowns": [
            "whether the matrix operand is raw FAED or recovered Bifid output",
            "which symbol-to-number mapping is intended",
            "coordinate origin and orientation",
            "whether sums are direct indices or require normalization",
            "whether BIP39 is intended rather than another fifteen-item receiver",
        ],
        "result": "A post-Bifid matrix-sum route has exact15-item/BIP39 dimensional compatibility and is distinct from the preserved raw-FAED BIP39 campaign. Range compatibility cannot select it because all nine canonical maps fit0..2047. The next discriminant would create/check concrete mnemonic indices, which is prohibited in this phase and unsupported by an authored mapping.",
        "next_test": "Do not execute this family. Require an authored numeric mapping or explicit BIP39/word-index instruction before any value generation or checksum test.",
        "candidate_lists_generated": 0,
        "mnemonic_words_generated": 0,
        "checksum_tests": 0,
        "seed_derivations": 0,
        "private_key_operations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
