import base64
import contextlib
import io
import json
import tempfile
import unittest
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import key_square
from tools.direct_source_keys import load_plan as load_direct_plan
from tools.gsmg import ARTIFACTS, SOURCES
from tools.plan_bifid_rails import coordinate_rails, serialize_digits
from tools.plan_missing_cell import derive_candidates as derive_missing_cell, missing_cell_matrices
from tools.prime_selection_controls import count_shuffled_frames, subsequence_selections
from tools.research_common import fingerprint
from tools.zeroed_residual import audit, decoded_forms, load_frozen_plan, run


OUTPUT = ARTIFACTS / "cycle05"


class RailAndSelectionTests(unittest.TestCase):
    def test_rails_retain_all_source_coordinates(self):
        segments = split_segments()
        square = key_square(segments["dbbi"])
        rails = coordinate_rails(segments["faed"], square)
        self.assertEqual(len(rails["binary-row"]["coordinates"]), 285)
        self.assertEqual(len(rails["quinary-column"]["coordinates"]), 285)
        reconstructed = []
        for index in range(285):
            for half in (0, 1):
                row = rails["binary-row"]["coordinates"][index][half]
                column = rails["quinary-column"]["coordinates"][index][half]
                reconstructed.append((index + half * 285, square[row * 5 + column]))
        self.assertEqual("".join(symbol for index, symbol in sorted(reconstructed)), segments["faed"])
        with self.assertRaises(ValueError):
            coordinate_rails("abc", square)

    def test_strict_serialization_refuses_bit_tail_repairs(self):
        self.assertEqual(serialize_digits([0, 1, 0, 0, 0, 0, 0, 1], 2, "strict-byte-chunks"), b"A")
        self.assertEqual(serialize_digits([2, 3, 0], 5, "strict-byte-chunks"), b"A")
        self.assertEqual(serialize_digits([0, 1], 2, "minimal-integer-big-endian"), b"\x01")
        self.assertEqual(serialize_digits([0, 1], 2, "ascii-digits"), b"01")
        for digits, radix in (([0, 1], 2), ([4, 3], 5), ([2] * 8, 2)):
            with self.assertRaises(ValueError):
                serialize_digits(digits, radix, "strict-byte-chunks")

    def test_exact_null_automaton_agrees_with_small_exhaustive_control(self):
        patterns = ("101", "011")
        matches = 0
        for ones in combinations(range(4), 2):
            ordinary = ["1" if index in ones else "0" for index in range(4)]
            frame = "".join(ordinary[:2] + ["1"] + ordinary[2:])
            matches += any(list(subsequence_selections(frame, pattern)) for pattern in patterns)
        self.assertEqual(count_shuffled_frames(patterns, 2, 2, 2, "1"), (matches, 6))
        self.assertEqual(list(subsequence_selections("01", "010")), [])

    def test_recorded_branch_ambiguity_and_conditional_counts(self):
        report = json.loads((OUTPUT / "prime-selection-controls.json").read_text())
        comparisons = report["frame_comparisons"]
        self.assertEqual([len(entry["matches"]) for entry in comparisons], [0, 5])
        self.assertEqual([entry["conditional_shuffle_null"]["matched_frames"] for entry in comparisons], [107, 72])
        matches = comparisons[1]["matches"]
        self.assertEqual({match["mask"] for match in matches if match["one_event_per_distinct_byte"]}, {505, 1017})
        self.assertEqual([match["mask"] for match in matches if match["exact_first_23_bytes"]], [505])
        self.assertEqual(report["continuous_counter_matches"][0]["mask"], 1017)
        self.assertEqual(report["binary_tail_control"]["uniform_lowercase_first_two_chars_matches"], 168)


class RecoveryTests(unittest.TestCase):
    def test_decoded_form_schema_handles_base64_materials(self):
        material = {"parameters": {}, "decoded_base64": "QQ==", "error": None}
        self.assertEqual(decoded_forms({"forms": [material]}), [material])
        legacy = {"parameters": {}, "decoded": "A", "error": None}
        self.assertEqual(decoded_forms({"forms": [legacy]})[0]["decoded"], "A")

    def test_recovery_requires_complete_unmodified_trial_coverage(self):
        password = b"public-clue-recovery-test"
        identifier = fingerprint(password)
        plan = {"passwords": {identifier: {"password_hex": password.hex(), "provenance": []}}, "forms": [{"parameters": {}, "decoded_base64": base64.b64encode(password).decode(), "error": None}], "candidate_set_sha256": fingerprint(password), "search_space": {"targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": 6}}
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory) / "research/artifacts"
            destination = artifacts / "cycle05"
            destination.mkdir(parents=True)
            plan_path = destination / "bifid-rails-plan.json"
            plan_path.write_text(json.dumps(plan))
            for target in plan["search_space"]["targets"]:
                (artifacts / (target + ".b64")).write_bytes((ARTIFACTS / (target + ".b64")).read_bytes())
            with patch("tools.zeroed_residual.ARTIFACTS", artifacts), patch("tools.zeroed_residual.load_frozen_plan", return_value=(plan_path, plan)), contextlib.redirect_stdout(io.StringIO()):
                run("rails")
                ledger = destination / "bifid-rails-aes.jsonl"
                preserved = ledger.read_bytes()
                summary = destination / "bifid-rails-results.json"
                summary.unlink()
                report = audit("rails", recover_summary=True)
                self.assertEqual(report["aes_trials"], 6)
                self.assertEqual(ledger.read_bytes(), preserved)
                self.assertIsNone(json.loads(summary.read_text())["elapsed_seconds"])
                with self.assertRaisesRegex(ValueError, "existing summary"):
                    audit("rails", recover_summary=True)
                summary.unlink()
                ledger.write_bytes(b"")
                with self.assertRaisesRegex(ValueError, "incomplete"):
                    audit("rails", recover_summary=True)
                self.assertFalse(summary.exists())
                altered = json.loads(preserved)
                altered["evaluations"][0]["iterations"] = 2
                ledger.write_text(json.dumps(altered) + "\n")
                with self.assertRaisesRegex(ValueError, "metadata"):
                    audit("rails", recover_summary=True)
                self.assertFalse(summary.exists())


class Cycle05EvidenceTests(unittest.TestCase):
    def test_original_and_new_manifests_match(self):
        for root in (SOURCES, SOURCES.parent / "evidence/cycle05"):
            manifest = json.loads((root / "manifest.json").read_text())
            for name, entry in manifest.items():
                self.assertEqual(fingerprint((root / name).read_bytes()), entry["sha256"], name)

    def test_literal_and_rail_frozen_candidates_and_results(self):
        for family, stem, forms, passwords, trials, hits in (("literal", "literal-sumlist", 288, 864, 5184, 17), ("rails", "bifid-rails", 32, 84, 504, 0)):
            path, plan = load_frozen_plan(family)
            result = json.loads((OUTPUT / (stem + "-results.json")).read_text())
            self.assertEqual((len(plan["forms"]), len(plan["passwords"])), (forms, passwords))
            self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"], result["target_matches"]), (trials, hits, 0, 0))
            self.assertEqual(fingerprint((OUTPUT / (stem + "-aes.jsonl")).read_bytes()), result["ledger_sha256"])
        path, plan = load_frozen_plan("rails")
        self.assertEqual(sum(form["error"] is not None for form in plan["forms"]), 4)

    def test_current_cumulative_space_is_exact(self):
        report = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
        self.assertEqual((len(report["audited_ledgers"]), report["unique_passwords"], report["distinct_target_kdf_trials"], report["trial_records"], report["padding_hit_records"]), (13, 40629, 243774, 248382, 1014))
        for ledger in report["audited_ledgers"]:
            self.assertEqual(fingerprint((ARTIFACTS.parents[1] / ledger["ledger"]).read_bytes()), ledger["ledger_sha256"])

    def test_direct_source_scalar_gap_is_bounded_and_reproduced(self):
        plan, candidates = load_direct_plan()
        self.assertEqual(len(candidates), 12475)
        self.assertEqual(plan["search_space"]["new_aes_trials"], 0)
        result = json.loads((OUTPUT / "direct-source-keys-results.json").read_text())
        self.assertEqual((result["scalar_checks"], result["invalid_scalars"], result["target_matches"]), (12475, 0, 0))
        self.assertEqual(result["ledger_sha256"], fingerprint((OUTPUT / "direct-source-keys-checks.jsonl").read_bytes()))

    def test_next_missing_cell_plan_preserves_every_source_symbol(self):
        matrices, lists, forms, passwords = derive_missing_cell()
        plan = json.loads((OUTPUT / "next-missing-cell-plan.json").read_text())
        self.assertEqual((len(matrices), len(lists), len(forms), len(passwords)), (6, 48, 192, 576))
        self.assertEqual(plan["forms"], forms)
        self.assertEqual(plan["passwords"], passwords)
        self.assertEqual(plan["search_space"]["planned_aes_trials"], 3456)
        self.assertEqual(plan["status"], "UNTESTED")
        for parameters, matrix in missing_cell_matrices():
            self.assertEqual(matrix[7][4], 0)
            self.assertEqual(sum(map(sum, matrix)), parameters["total"])
            self.assertEqual(parameters["source_symbols"], 195)
        spiral = [parameters for parameters, matrix in missing_cell_matrices() if parameters["fill_route"] == "verified-counterclockwise-spiral"]
        self.assertEqual([parameters["hole_route_offset_zero_based"] for parameters in spiral], [163, 163])


if __name__ == "__main__":
    unittest.main()
