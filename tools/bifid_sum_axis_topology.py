#!/usr/bin/env python3
"""Compare 15-item Bifid sum axes without calculating numeric sums.

The report uses source-dependency sets and formal symbol-count vectors only.
It does not instantiate a numeric mapping, mnemonic index, checksum, seed,
private key, ciphertext operation, or AES input.
"""

from collections import Counter
import json

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square


def columns(text, width):
    if width < 1 or len(text) % width:
        raise ValueError("Object does not tile at the requested width")
    return [text[column::width] for column in range(width)]


def rows(text, width):
    if width < 1 or len(text) % width:
        raise ValueError("Object does not tile at the requested width")
    return [text[offset:offset + width] for offset in range(0, len(text), width)]


def histogram(text, alphabet):
    counts = Counter(text)
    return tuple(counts[symbol] for symbol in alphabet)


def compare_formal_groups(left, right, alphabet):
    left_vectors = [histogram(group, alphabet) for group in left]
    right_vectors = [histogram(group, alphabet) for group in right]
    return {
        "left_groups": len(left_vectors),
        "right_groups": len(right_vectors),
        "symbols_per_group": sorted({len(group) for group in left + right}),
        "ordered_equal_groups": sum(a == b for a, b in zip(left_vectors, right_vectors)),
        "all_pair_equal_groups": sum(a == b for a in left_vectors for b in right_vectors),
        "whole_vector_multiset_equal": sorted(left_vectors) == sorted(right_vectors),
    }


def report():
    segments = split_segments()
    faed = segments["faed"]
    square = key_square(segments["dbbi"])
    output = bifid(faed, square, len(faed))
    if len(faed) != 570 or len(output) != 570:
        raise ValueError("Frozen FAED/Bifid lengths changed")

    raw_columns = columns(faed, 15)
    raw_width38_rows = rows(faed, 38)
    rendered_columns = columns(output, 15)

    even_plane = output[::2]
    odd_plane = output[1::2]
    even_columns = columns(even_plane, 15)
    odd_columns = columns(odd_plane, 15)
    paired_plane_columns = [even + odd for even, odd in zip(even_columns, odd_columns)]

    rendered_positions = [[column + 15 * row for row in range(38)] for column in range(15)]
    paired_positions = []
    for column in range(15):
        positions = []
        for pair_index in range(column, 285, 15):
            positions.extend([2 * pair_index, 2 * pair_index + 1])
        paired_positions.append(positions)

    def source_columns(positions):
        # Full-period Bifid output positions 2k and 2k+1 both depend on
        # FAED offsets k and k+285.  Both have source column k mod 15.
        return sorted({(position // 2) % 15 for position in positions})

    rendered_lineage = [source_columns(group) for group in rendered_positions]
    paired_lineage = [source_columns(group) for group in paired_positions]
    if paired_lineage != [[column] for column in range(15)]:
        raise ValueError("Coordinate-plane column lineage changed")
    if any(len(group) != 2 for group in rendered_lineage):
        raise ValueError("Serialized-column lineage changed")
    if sorted(position for group in rendered_positions for position in group) != list(range(570)):
        raise ValueError("Serialized groups do not cover output exactly once")
    if sorted(position for group in paired_positions for position in group) != list(range(570)):
        raise ValueError("Plane-paired groups do not cover output exactly once")

    comparisons = {
        "plane_paired_vs_raw_width15_columns": compare_formal_groups(
            paired_plane_columns, raw_columns, square
        ),
        "rendered_vs_raw_width15_columns": compare_formal_groups(
            rendered_columns, raw_columns, square
        ),
        "plane_paired_vs_raw_width38_rows": compare_formal_groups(
            paired_plane_columns, raw_width38_rows, square
        ),
        "rendered_vs_raw_width38_rows": compare_formal_groups(
            rendered_columns, raw_width38_rows, square
        ),
        "plane_paired_vs_rendered": compare_formal_groups(
            paired_plane_columns, rendered_columns, square
        ),
    }
    if any(item["all_pair_equal_groups"] for item in comparisons.values()):
        raise ValueError("Unexpected formal group equivalence")

    return {
        "id": "C30-BIFID-SUM-AXIS-TOPOLOGY",
        "date": "2026-10-02",
        "status": "PROMISING",
        "hypothesis": "If matrixsumlist consumes Bifid570 as fifteen groups, the dependency-preserving groups are corresponding columns of its two19x15 coordinate planes, rather than columns of the serialized38x15 rendering.",
        "invariant": "A Bifid-native downstream column must retain one-to-one lineage to a single width15 FAED source column and cover every output symbol exactly once.",
        "fixed_shapes": {
            "faed": [38, 15],
            "bifid_serialized": [38, 15],
            "bifid_even_plane": [19, 15],
            "bifid_odd_plane": [19, 15],
            "groups_per_architecture": 15,
            "symbols_per_group": 38,
        },
        "dependency_topology": {
            "plane_paired_source_columns_zero_based": paired_lineage,
            "plane_paired_single_source_column_groups": sum(len(group) == 1 for group in paired_lineage),
            "rendered_source_columns_zero_based": rendered_lineage,
            "rendered_single_source_column_groups": sum(len(group) == 1 for group in rendered_lineage),
            "rendered_two_source_column_groups": sum(len(group) == 2 for group in rendered_lineage),
            "plane_paired_output_coverage": 570,
            "rendered_output_coverage": 570,
        },
        "formal_additive_comparison": {
            "method": "Represent each group by its 25-component source-keyed-square letter-count vector; equal vectors would give equal sums for every additive symbol mapping.",
            "comparisons": comparisons,
            "interpretation": "No post-Bifid group equals any raw-FAED group, and the two post-Bifid axes do not equal one another, as formal additive expressions. Special numeric mappings may still collide; none is selected here.",
            "numeric_sum_vectors_calculated": 0,
            "numeric_mapping_trials": 0,
        },
        "architecture_discriminator": {
            "serialized_38x15_column_reduction": "WEAK: exact15-item tiling, but every group mixes two FAED source columns because width15 is odd relative to Bifid digraph serialization.",
            "coordinate_plane_paired_column_reduction": "STRONGLY SUPPORTED structurally: all15 groups preserve one exact FAED source column through every Bifid cell and cover all570 output symbols once.",
            "prior_raw_faed_sum_campaign_equivalence": "REJECTED as an exact formal repeat: no output group has the same letter-count linear form as any tested raw-FAED width15-column or width38-row group.",
            "intended_numeric_sum_or_receiver": "UNKNOWN: topology selects the natural axis but supplies no symbol weights, orientation, normalization, or receiver.",
        },
        "graph_effect": "Refine the missing edge to matrixsumlist semantics plus the paired Bifid even/odd19x15 planes, reduced by their shared15-column axis, leading to an unknown15-item receiver.",
        "exact_remaining_unknown": "No authored evidence selects symbol weights or establishes that the fifteen structural groups are numeric sums, BIP39 indices, or any other receiver type.",
        "next_test": "Do not instantiate values. Resume only if source evidence supplies a numeric mapping or a non-cryptographic receiver constraint that can distinguish the remaining interpretations.",
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
