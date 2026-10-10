import json
import unittest
from unittest.mock import patch

from tools.candidate_identity import POLICY, previously_tested, tagged_identity
from tools.gsmg import ARTIFACTS
from tools.plan_masked_missing_cell import derive_candidates, masked_matrices
from tools.research_common import fingerprint
from tools.secret_safe_aes import load_candidates


OUTPUT = ARTIFACTS / "cycle10"
FROZEN = ARTIFACTS / "cycle09/next-masked-missing-cell-plan.json"


class MaskedMissingCellTests(unittest.TestCase):
    def test_tagged_identity_filters_both_historical_namespaces(self):
        password = b"public-synthetic-tagged-candidate-control"
        untagged = fingerprint(password)
        tagged = tagged_identity(password)
        self.assertNotEqual(untagged, tagged)
        self.assertTrue(previously_tested(password, {untagged}))
        self.assertTrue(previously_tested(password, {tagged}))
        self.assertFalse(previously_tested(password, {"public-nonmatching-identity"}))

    def test_frozen_masked_family_is_exact_and_no_password_bytes_are_logged(self):
        preserved = FROZEN.read_bytes()
        forms, candidates = derive_candidates()
        frozen = json.loads(preserved)
        self.assertEqual((len(forms), len(candidates)), (64, 192))
        self.assertEqual(frozen["forms"], forms)
        self.assertEqual(frozen["candidate_identifier_policy"], POLICY)
        self.assertTrue(all(identifier == tagged_identity(bytes.fromhex(candidate["password_hex"])) for identifier, candidate in candidates.items()))
        self.assertTrue(all(bytes.fromhex(candidate["password_hex"]) not in preserved for candidate in candidates.values()), "Frozen plan must not expose candidate bytes")
        self.assertEqual(FROZEN.read_bytes(), preserved)

    def test_masked_family_filters_baseline_and_existing_ledgers(self):
        plan, candidates, duplicates = load_candidates("masked-missing-cell")
        self.assertEqual((len(candidates), duplicates), (192, 0))
        self.assertEqual(plan["search_space"]["planned_aes_trials"], 1152)
        with patch("tools.baseline_coverage.baseline_passwords", return_value={bytes.fromhex(candidate["password_hex"]) for candidate in candidates.values()}):
            with self.assertRaisesRegex(ValueError, "untested subset differs"):
                load_candidates("masked-missing-cell")

    def test_source_placement_uses_only_frozen_mapping_route_and_hole(self):
        matrices = list(masked_matrices())
        self.assertEqual(len(matrices), 2)
        for parameters, matrix in matrices:
            self.assertEqual(parameters["fill_route"], "verified-counterclockwise-spiral")
            self.assertEqual(parameters["value_mapping"], "dbbi-a1-i9-binary-a0-b1")
            self.assertEqual(parameters["near_white_hole_zero_based"], [7, 4])
            self.assertEqual(matrix[7][4], 0)
            self.assertTrue(parameters["complement_reconstruction_verified"])


if __name__ == "__main__":
    unittest.main()
