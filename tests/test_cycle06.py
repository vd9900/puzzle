import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from tools.gsmg import ARTIFACTS, candidate_addresses, evp_bytes_to_key
from tools.research_common import fingerprint
from tools.secret_safe_aes import audit, evaluate, load_candidates, plaintext_result, run, scalar_result


OUTPUT = ARTIFACTS / "cycle06"


class SecretSafeTests(unittest.TestCase):
    def test_positive_target_verification_returns_only_booleans(self):
        scalar = (1).to_bytes(32, "big")
        public_test_address = candidate_addresses(scalar)["compressed"]
        with patch("tools.secret_safe_aes.TARGET_ADDRESS", public_test_address), patch("tools.verify_btc.TARGET_ADDRESS", public_test_address):
            result = scalar_result(scalar)
        self.assertEqual(result, {"valid_scalar": True, "TARGET_MATCH": True, "independently_verified": True})
        self.assertEqual(scalar_result(bytes(32)), {"valid_scalar": False, "TARGET_MATCH": False, "independently_verified": False})

    def test_trial_serialization_does_not_store_secret_bytes(self):
        password = b"public-synthetic-secret-safe-test"
        plaintext = b"NeverStoreThisPlaintextInResults!" * 2
        salt = b"localslt"
        key, initialization_vector = evp_bytes_to_key(password, salt, "sha256")
        ciphertext = AES.new(key, AES.MODE_CBC, initialization_vector).encrypt(pad(plaintext, 16))
        candidate = {"password_hex": password.hex(), "provenance": [{"representation": "public-synthetic-control"}]}
        record = evaluate(fingerprint(password), candidate, "test-plan-fingerprint", {"phase32-inner": (salt, ciphertext)})
        encoded = json.dumps(record)
        for forbidden in (password.decode(), password.hex(), key.hex(), initialization_vector.hex(), plaintext.decode(), plaintext.hex()):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(len(record["evaluations"]), 2)
        hit = next(entry for entry in record["evaluations"] if entry["digest"] == "sha256")
        self.assertTrue(hit["padding_valid"])
        self.assertEqual(hit["plaintext_result"]["plaintext_fingerprint"], fingerprint(plaintext))
        self.assertEqual(len(hit["plaintext_result"]["bounded_raw_key_checks"]), 2 * (len(plaintext) - 63))
        self.assertFalse(hit["TARGET_MATCH"])

    def test_direct_key_results_never_return_key_or_address(self):
        result = plaintext_result((1).to_bytes(32, "big"), "phase32-inner")
        self.assertEqual(len(result["direct_key_checks"]), 1)
        self.assertEqual(set(result["direct_key_checks"][0]), {"candidate_fingerprint", "valid_scalar", "TARGET_MATCH", "independently_verified"})
        self.assertFalse(result["TARGET_MATCH"])

    def test_completed_run_is_preserved_and_tampered_record_rejected(self):
        password = b"public-synthetic-run-control"
        scalar_identifier = fingerprint(password)
        candidates = {scalar_identifier: {"password_hex": password.hex(), "provenance": []}}
        salt = b"localslt"
        key, initialization_vector = evp_bytes_to_key(password, salt, "sha256")
        ciphertext = AES.new(key, AES.MODE_CBC, initialization_vector).encrypt(pad(b"public-test-checkpoint", 16))
        blobs = {target: (salt, ciphertext) for target in ("phase32-inner", "salphaseion-small", "cosmic-duality")}
        plan = {"id": "TEST-SECRET-SAFE", "search_space": {"new_aes_trials": 6}}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch("tools.secret_safe_aes.OUTPUT", output), patch("tools.secret_safe_aes.load_execution", return_value=(plan, candidates, "public-plan-fingerprint", blobs)), contextlib.redirect_stdout(io.StringIO()):
                run()
                ledger = output / "missing-cell-aes.jsonl"
                preserved = ledger.read_bytes()
                report = audit()
                self.assertEqual(report["aes_trials"], 6)
                self.assertEqual(ledger.read_bytes(), preserved)
                with self.assertRaises(FileExistsError):
                    run()
                self.assertEqual(ledger.read_bytes(), preserved)
                altered = json.loads(preserved)
                altered["evaluations"][0]["iterations"] = 2
                ledger.write_text(json.dumps(altered) + "\n")
                with self.assertRaisesRegex(ValueError, "do not reproduce"):
                    audit()


class Cycle06EvidenceTests(unittest.TestCase):
    def test_frozen_missing_cell_family_and_overlap_gate(self):
        plan, candidates, duplicates = load_candidates()
        self.assertEqual((len(candidates), duplicates), (576, 0))
        self.assertEqual(plan["search_space"]["planned_aes_trials"], 3456)
        result = json.loads((OUTPUT / "missing-cell-results.json").read_text())
        self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"], result["bounded_raw_key_slots"]), (3456, 13, 0, 352))
        self.assertFalse(result["TARGET_MATCH"])
        self.assertEqual(result["ledger_sha256"], fingerprint((OUTPUT / "missing-cell-aes.jsonl").read_bytes()))

    def test_new_ledger_has_only_secret_safe_fields(self):
        forbidden = {"password_hex", "password_base64", "plaintext", "plaintext_base64", "key", "iv", "scalar", "addresses"}

        def check(value):
            if isinstance(value, dict):
                self.assertFalse(set(value) & forbidden)
                for nested in value.values():
                    check(nested)
            elif isinstance(value, list):
                for nested in value:
                    check(nested)

        with (OUTPUT / "missing-cell-aes.jsonl").open() as source:
            for line in source:
                check(json.loads(line))

    def test_cumulative_trial_union_is_exact(self):
        report = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
        self.assertEqual((len(report["audited_ledgers"]), report["unique_passwords"], report["distinct_target_kdf_trials"], report["trial_records"], report["padding_hit_records"]), (14, 41205, 247230, 251838, 1027))
        self.assertFalse(report["TARGET_MATCH"])
        for ledger in report["audited_ledgers"]:
            self.assertEqual(fingerprint((ARTIFACTS.parents[1] / ledger["ledger"]).read_bytes()), ledger["ledger_sha256"])


if __name__ == "__main__":
    unittest.main()
