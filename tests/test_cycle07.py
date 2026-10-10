import json
import unittest

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square
from tools.gsmg import ARTIFACTS
from tools.joint_derivation import columnar
from tools.plan_numeric_routing import derive_candidates
from tools.research_common import fingerprint
from tools.secret_safe_aes import load_candidates


OUTPUT = ARTIFACTS / "cycle07"


class NumericRoutingTests(unittest.TestCase):
    def test_numeric_columnar_ties_and_ragged_round_trip(self):
        keyword = (6, 10, 8, 7, 6, 6)
        expected_order = [0, 4, 5, 3, 2, 1]
        self.assertEqual(sorted(range(len(keyword)), key=lambda index: (keyword[index], index)), expected_order)
        text = "publicnumericroutecontrol"
        encoded = columnar(text, keyword, False)
        self.assertEqual(encoded, "".join(text[index::len(keyword)] for index in expected_order))
        self.assertEqual(columnar(encoded, keyword, True), text)
        self.assertEqual(columnar(columnar(text, keyword, True), keyword, False), text)

    def test_frozen_routes_rederive_without_logging_password_material(self):
        forms, passwords = derive_candidates()
        plan = json.loads((OUTPUT / "numeric-routing-frozen-plan.json").read_text())
        self.assertEqual((len(forms), len(passwords)), (144, 414))
        self.assertEqual(plan["forms"], forms)
        self.assertEqual(plan["candidate_fingerprints"], sorted(passwords))
        self.assertNotIn("passwords", plan)
        self.assertEqual(plan["candidate_set_sha256"], fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))))
        self.assertTrue(all(form["round_trip"] for form in forms))

    def test_routed_faed_then_exact_bifid_returns_the_same_route(self):
        segments = split_segments()
        square = key_square(segments["dbbi"])
        sums = (6, 10, 8, 7, 6, 6, 5, 4, 9, 9, 7, 8, 7, 9)
        for decrypt in (False, True):
            routed = columnar(segments["faed"], sums, decrypt)
            output = bifid(routed, square, 570)
            self.assertEqual(bifid(output, square, 570, False), routed)
            self.assertEqual(columnar(bifid(output, square, 570, False), sums, not decrypt), segments["faed"])

    def test_numeric_routing_results_and_historical_overlap(self):
        plan, candidates, duplicates = load_candidates("numeric-routing")
        self.assertEqual((len(candidates), duplicates), (414, 0))
        result = json.loads((OUTPUT / "numeric-routing-results.json").read_text())
        self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"], result["bounded_raw_key_slots"]), (2484, 9, 0, 96))
        self.assertFalse(result["TARGET_MATCH"])
        self.assertEqual(result["ledger_sha256"], fingerprint((OUTPUT / "numeric-routing-aes.jsonl").read_bytes()))
        audit = json.loads((OUTPUT / "numeric-routing-audit.json").read_text())
        self.assertEqual(audit["id"], "C07-NUMERIC-ROUTING-AUDIT")

    def test_current_cumulative_union_is_exact(self):
        report = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
        self.assertEqual((len(report["audited_ledgers"]), report["unique_passwords"], report["distinct_target_kdf_trials"], report["trial_records"], report["padding_hit_records"]), (15, 41619, 249714, 254322, 1036))
        self.assertFalse(report["TARGET_MATCH"])
        for ledger in report["audited_ledgers"]:
            self.assertEqual(fingerprint((ARTIFACTS.parents[1] / ledger["ledger"]).read_bytes()), ledger["ledger_sha256"])


if __name__ == "__main__":
    unittest.main()
