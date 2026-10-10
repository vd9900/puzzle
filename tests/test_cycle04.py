import json
import unittest
from fractions import Fraction

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, exact_shuffle_probability, key_square, prefix_domains, prefix_match
from tools.gsmg import ARTIFACTS, SOURCES
from tools.research_common import fingerprint
from tools.zeroed_residual import load_frozen_plan
from tools.plan_literal_sumlist import derive_candidates as derive_literal_sumlists


OUTPUT = ARTIFACTS / "cycle04"


class BifidEvidenceTests(unittest.TestCase):
    def test_bifid_round_trip_with_ragged_periods(self):
        square = key_square("matrixsumlist")
        text = "defensivepuzzleresearch"
        for period in (1, 2, 7, 15, 38, len(text)):
            self.assertEqual(bifid(bifid(text, square, period, False), square, period), text)
        for square_value, period in (("abc", 1), (square, 0)):
            with self.assertRaises(ValueError):
                bifid(text, square_value, period)

    def test_source_keyed_bifid_matches_archived_claim_and_parity(self):
        segments = split_segments()
        square = key_square(segments["dbbi"])
        self.assertEqual(square, "dbifhcegaklmnopqrstuvwxyz")
        plaintext = bifid(segments["faed"], square, 570)
        self.assertTrue(plaintext.startswith("btcseed"))
        self.assertEqual(set(plaintext[::2]), set("bcde"))
        self.assertEqual(fingerprint(plaintext.encode()), "15d62c8228c1a30f3f6280fcdce2251fe616135e9de291b0c7b8a792dd8d0507")
        report = json.loads((OUTPUT / "bifid-evidence.json").read_text())
        self.assertEqual(report["plaintext"], plaintext)
        self.assertTrue(report["claimed_full_output_matches_primary_derived"])

    def test_prefix_constraints_and_exact_shuffle_probability(self):
        segments = split_segments()
        square = key_square(segments["dbbi"])
        domains = prefix_domains("btcseed", square, 570)
        self.assertEqual(set(domains), {0, 1, 2, 3, 285, 286, 287, 288})
        self.assertTrue(prefix_match(segments["faed"], domains))
        self.assertEqual(exact_shuffle_probability("aabb", {0: ["a"], 1: ["b"]}), Fraction(1, 3))
        self.assertEqual(exact_shuffle_probability("aabb", {0: ["a"], 1: ["b"]}, "a"), Fraction(2, 3))
        self.assertEqual(exact_shuffle_probability("aabb", {0: ["b"]}, "a"), 0)

    def test_all_reported_prefix_squares_independently_reproduce(self):
        report = json.loads((OUTPUT / "bifid-square-control.json").read_text())
        source = split_segments()["faed"]
        self.assertEqual(report["square_prefixes_tested"], 362880)
        self.assertEqual(report["prefix_matches"], 8)
        self.assertEqual(sum(match["is_exact_source_key"] for match in report["matches"]), 1)
        self.assertEqual(len({match["square"] for match in report["matches"]}), 8)
        for match in report["matches"]:
            plaintext = bifid(source, match["square"], 570)
            self.assertTrue(plaintext.startswith("btcseed"))
            self.assertEqual(fingerprint(plaintext.encode()), match["output_sha256"])


class Cycle04EvidenceTests(unittest.TestCase):
    def test_original_and_added_evidence_remain_intact(self):
        for root in (SOURCES, SOURCES.parent / "evidence/cycle04"):
            manifest = json.loads((root / "manifest.json").read_text())
            for name, entry in manifest.items():
                self.assertEqual(fingerprint((root / name).read_bytes()), entry["sha256"], name)

    def test_frozen_ranked_and_bifid_candidates_rederive(self):
        for family, count, trials, hits in (("ranked", 2496, 14976, 67), ("bifid", 54, 324, 3)):
            path, plan = load_frozen_plan(family)
            self.assertEqual(len(plan["passwords"]), count)
            stem = "ranked-alphabet" if family == "ranked" else "bifid-material"
            result = json.loads((OUTPUT / (stem + "-results.json")).read_text())
            self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"]), (trials, hits, 0))
            self.assertEqual(fingerprint((OUTPUT / (stem + "-aes.jsonl")).read_bytes()), result["ledger_sha256"])

    def test_hash_composition_rederives_and_matches_first_hash(self):
        path, plan = load_frozen_plan("composition")
        self.assertEqual(plan["first_flower_hash_verified"], "5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75")
        self.assertEqual((len(plan["forms"]), len(plan["passwords"]), plan["search_space"]["planned_aes_trials"]), (120, 360, 2160))
        result = json.loads((OUTPUT / "hash-composition-results.json").read_text())
        self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"]), (2160, 6, 0))

    def test_next_literal_sumlist_plan_is_exact_and_unexecuted(self):
        lists, forms, passwords = derive_literal_sumlists()
        plan = json.loads((OUTPUT / "next-literal-sumlist-plan.json").read_text())
        self.assertEqual((len(lists), len(forms), len(passwords)), (24, 288, 864))
        self.assertEqual(plan["forms"], forms)
        self.assertEqual(plan["passwords"], passwords)
        self.assertEqual(plan["search_space"]["planned_aes_trials"], 5184)
        self.assertEqual(plan["status"], "UNTESTED")

    def test_cumulative_count_and_binary_format_audits_match(self):
        cumulative = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
        self.assertEqual((cumulative["unique_passwords"], cumulative["trial_records"], cumulative["distinct_target_kdf_trials"], cumulative["padding_hit_records"]), (39681, 242694, 238086, 997))
        self.assertEqual(len(cumulative["audited_ledgers"]), 11)
        for ledger in cumulative["audited_ledgers"]:
            self.assertEqual(fingerprint((ARTIFACTS.parents[1] / ledger["ledger"]).read_bytes()), ledger["ledger_sha256"])
        for group, slots in (("ranked", 1436), ("bifid", 96), ("composition", 160)):
            audit = json.loads((OUTPUT / ("binary-key-pair-" + group + "-audit.json")).read_text())
            self.assertEqual(audit["slot_checks"], slots)
            self.assertEqual(audit["status"], "CONFIRMED")


if __name__ == "__main__":
    unittest.main()
