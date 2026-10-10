import json
import itertools
import unittest
from fractions import Fraction
from unittest.mock import patch

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS
from tools.exact_prime_bifid_control import first_occurrence_probability
from tools.joint_derivation import columnar
from tools.plan_post_bifid_routing import derive_candidates
from tools.plan_spiral_ring_sums import derive_candidates as ring_candidates, ring_totals
from tools.plan_masked_missing_cell import derive_candidates as masked_candidates, masked_matrices
from tools.plan_missing_cell import missing_cell_matrices
from tools.research_common import fingerprint
from tools.secret_safe_aes import load_candidates
from tools.sumlist_codec_preflight import encode_neighbor_codec, numeric_representations
from tools.gsmg import decode_decimal_letters


OUTPUT = ARTIFACTS / "cycle09"
FROZEN = ARTIFACTS / "cycle08/next-post-bifid-routing-plan.json"


class PostBifidRoutingTests(unittest.TestCase):
    def test_frozen_family_is_exact_and_secret_safe(self):
        preserved = FROZEN.read_bytes()
        forms, candidates = derive_candidates()
        plan = json.loads(preserved)
        self.assertEqual((len(forms), len(candidates)), (48, 46))
        self.assertEqual(plan["forms"], forms)
        self.assertEqual(plan["candidate_fingerprints"], sorted(candidates))
        self.assertEqual(plan["candidate_set_sha256"], fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))))
        self.assertTrue(all(bytes.fromhex(candidate["password_hex"]) not in preserved for candidate in candidates.values()), "Candidate password bytes must not be serialized")
        self.assertEqual(FROZEN.read_bytes(), preserved)

    def test_post_route_and_bifid_inverse_preserve_the_complete_source(self):
        segments = split_segments()
        square = key_square(segments["dbbi"])
        decoded = bifid(segments["faed"], square, 570)
        forms, unused_candidates = derive_candidates()
        for form in forms:
            parameters = form["parameters"]
            sums = tuple(parameters["axis_sums"])
            decrypt = parameters["columnar_direction"] == "decrypt"
            routed = columnar(decoded[7:], sums, decrypt)
            restored = decoded[:7] + columnar(routed, sums, not decrypt)
            self.assertEqual(bifid(restored, square, 570, False), segments["faed"])
            self.assertEqual(form["output_fingerprint"], fingerprint(b"gsmg-research-output\x00" + routed.encode()))
            self.assertNotEqual(routed, bifid(columnar(segments["faed"], sums, decrypt), square, 570)[7:])

    def test_all_baseline_and_ledger_identities_filter_the_frozen_candidates(self):
        plan, candidates, duplicates = load_candidates("post-bifid-routing")
        self.assertEqual((len(candidates), duplicates), (46, 0))
        self.assertEqual(plan["search_space"]["planned_aes_trials"], 276)
        with patch("tools.baseline_coverage.baseline_passwords", return_value={bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()}):
            with self.assertRaisesRegex(ValueError, "untested subset differs"):
                load_candidates("post-bifid-routing")

    def test_exact_order_probability_agrees_with_exhaustive_small_multisets(self):
        template = [None, "b", None, None, "be", None, None, "b", None]
        residual = "accdee"
        permutations = set(itertools.permutations(residual))
        counts = {}
        for symbols in permutations:
            pending = iter(symbols)
            keyword = "".join(next(pending) if token is None else token for token in template)
            order = "".join(dict.fromkeys(keyword))
            counts[order] = counts.get(order, 0) + 1
        total = Fraction(0, 1)
        for order in itertools.permutations("abcde"):
            order = "".join(order)
            actual, unused_diagnostics = first_occurrence_probability(template, residual, order)
            self.assertEqual(actual, Fraction(counts.get(order, 0), len(permutations)))
            total += actual
        self.assertEqual(total, 1)

    def test_completed_post_route_results_reproduce_all_gates(self):
        result = json.loads((OUTPUT / "post-bifid-routing-results.json").read_text())
        self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"], result["bounded_raw_key_slots"]), (276, 3, 0, 64))
        self.assertFalse(result["TARGET_MATCH"])
        self.assertEqual(result["ledger_sha256"], fingerprint((OUTPUT / "post-bifid-routing-aes.jsonl").read_bytes()))

    def test_spiral_rings_partition_the_original_matrix(self):
        matrix = [[row * 4 + column for column in range(4)] for row in range(4)]
        totals, members = ring_totals(matrix)
        expected_outer = sum(matrix[row][column] for row in range(4) for column in range(4) if row in (0, 3) or column in (0, 3))
        self.assertEqual(totals, [expected_outer, sum(map(sum, matrix)) - expected_outer])
        self.assertEqual(members, [list(range(12)), list(range(12, 16))])
        single, indices = ring_totals([[5]])
        self.assertEqual((single, indices), ([5], [[0]]))
        with self.assertRaises(ValueError):
            ring_totals([[1, 2]])

    def test_ring_family_preserves_center_and_frozen_candidate_identities(self):
        forms, candidates = ring_candidates()
        plan = json.loads((OUTPUT / "spiral-ring-sums-frozen-plan.json").read_text())
        self.assertEqual((len(forms), len(candidates)), (24, 72))
        self.assertEqual(plan["forms"], forms)
        self.assertEqual(plan["candidate_fingerprints"], sorted(candidates))
        lists = {tuple(form["parameters"]["ring_totals"]) for form in forms}
        self.assertIn((30, 25, 18, 12, 11, 5, 0), lists)
        self.assertIn((30, 25, 18, 12, 12, 5, 0), lists)
        self.assertIn((28, 23, 16, 10, 9, 3, 0), lists)
        self.assertTrue(all(len(values) == 7 and (values[0] == 0 or values[-1] == 0) for values in lists))
        unused_plan, fresh, duplicates = load_candidates("spiral-ring-sums")
        self.assertEqual((len(fresh), duplicates), (72, 0))

    def test_neighbor_codec_round_trip_and_typed_sumlist_serializations(self):
        for public_label in ("lastwordsbeforearchichoice", "thispassword", "publiccodeccontrol"):
            self.assertEqual(decode_decimal_letters(encode_neighbor_codec(public_label.encode())), public_label)
        values = (0, 12, 3)
        representations = numeric_representations(values)
        self.assertEqual(representations["one-byte-totals"], bytes(values))
        self.assertEqual(representations["decimal-concatenation"], b"0123")
        self.assertEqual(representations["decimal-comma-list"], b"0,12,3")
        self.assertEqual(representations["decimal-minimal-integer-big-endian"], bytes([123]))
        with self.assertRaises(ValueError):
            encode_neighbor_codec(b"")

    def test_current_completed_union_and_exact_conditional_control(self):
        report = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
        self.assertEqual((len(report["audited_ledgers"]), report["unique_passwords"], report["distinct_target_kdf_trials"], report["trial_records"], report["padding_hit_records"]), (18, 41740, 250440, 255048, 1042))
        self.assertEqual((report["combined_unique_passwords_including_baseline"], report["combined_distinct_target_kdf_trials_including_baseline"], report["recorded_trial_count_including_baseline"]), (41828, 250968, 255780))
        exact = json.loads((OUTPUT / "exact-prime-bifid-control.json").read_text())
        self.assertEqual([Fraction(entry["exact_prefix_probability_numerator"], entry["exact_prefix_probability_denominator"]) for entry in exact["controls"]], [Fraction(185207349440, 901107283675599), Fraction(97260203200, 487484268217947)])
        ring = json.loads((OUTPUT / "spiral-ring-sums-results.json").read_text())
        self.assertEqual((ring["aes_trials"], ring["padding_hits"], ring["bounded_raw_key_slots"]), (432, 3, 96))
        self.assertFalse(ring["TARGET_MATCH"])

    def test_next_mask_plan_reconstructs_every_annotated_value(self):
        matrices = list(masked_matrices())
        self.assertEqual(len(matrices), 2)
        original = next(matrix for parameters, matrix in missing_cell_matrices() if parameters["value_mapping"] == "dbbi-a1-i9-binary-a0-b1" and parameters["fill_route"] == "verified-counterclockwise-spiral")
        self.assertTrue(all(matrices[0][1][row][column] + matrices[1][1][row][column] == original[row][column] for row in range(14) for column in range(14)))
        self.assertTrue(all(matrix[7][4] == 0 for parameters, matrix in matrices))
        forms, candidates = masked_candidates()
        frozen = json.loads((OUTPUT / "next-masked-missing-cell-plan.json").read_text())
        self.assertEqual(frozen["forms"], forms)
        self.assertEqual(frozen["candidate_fingerprints"], sorted(candidates))
        self.assertEqual(frozen["candidate_set_sha256"], fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()))))
        self.assertEqual(frozen["new_aes_trials_executed"], 0)
        encoded = json.dumps(frozen).encode()
        self.assertTrue(all(bytes.fromhex(candidate["password_hex"]) not in encoded for candidate in candidates.values()), "Candidate password bytes must not be serialized")


if __name__ == "__main__":
    unittest.main()
