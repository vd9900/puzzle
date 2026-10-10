import base64
import hashlib
import json
import subprocess
import unittest

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from tools.gsmg import (
    ARTIFACTS, PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE, SOURCES,
    TARGET_ADDRESS, base58check_decode, base58check_encode, candidate_addresses,
    decode_beaufort, decode_binary_letters, decode_checkerboard, decode_decimal_letters,
    decrypt_salted, embedded_blobs, encode_checkerboard, evp_bytes_to_key, extract_grid,
    extract_salphaseion, parse_salted, reproduce, sha256_hex, spiral_coordinates,
)
from tools.collect_sources import snapshot
from unittest.mock import patch


class SourceReproductionTests(unittest.TestCase):
    def test_grid_matches_documented_matrix_and_url(self):
        grid = extract_grid(SOURCES / "gsmg-puzzle.png")
        self.assertEqual(grid["decoded"], "gsmg.io/theseedisplanted")
        self.assertEqual(grid["trailing_bits"], "0000")
        self.assertEqual(grid["colored_spiral_indices"], list(range(7, 192, 8)))
        self.assertEqual(grid["near_white_cells_zero_based"], [[7, 4]])

    def test_spirals_visit_each_cell_once(self):
        for size in range(1, 15):
            coordinates = spiral_coordinates(size)
            self.assertEqual(len(coordinates), size * size)
            self.assertEqual(set(coordinates), {(row, column) for row in range(size) for column in range(size)})
            self.assertEqual(coordinates[0], (0, 0))
        with self.assertRaises(ValueError):
            spiral_coordinates(0)

    def test_documented_preimage_hashes(self):
        expected = {
            PHASE3_PREIMAGE: "1a57c572caf3cf722e41f5f9cf99ffacff06728a43032dd44c481c77d2ec30d5",
            PHASE32_PREIMAGE: "250f37726d6862939f723edc4f993fde9d33c6004aab4f2203d9ee489d61ce4c",
            SALPHASEION_PREIMAGE: "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32",
        }
        for preimage, expected_digest in expected.items():
            self.assertEqual(sha256_hex(preimage.encode()), expected_digest)

    def test_salphaseion_clues_and_claim_match_primary(self):
        extracted = extract_salphaseion((SOURCES / "salphaseion.html").read_text())
        self.assertEqual(extracted["binary_clues"], ["matrixsumlist", "enter"])
        self.assertEqual(extracted["decimal_clues"], ["lastwordsbeforearchichoice", "thispassword"])
        self.assertEqual(extracted["small_blob"][18], "J")
        self.assertEqual(extracted["small_blob"][51], "s")
        self.assertEqual(parse_salted(extracted["small_blob"])[0].hex(), "3ab585348552415d")
        self.assertEqual(len(extracted["unresolved_prefix"]), 661)

    def test_decoders_validate_inputs(self):
        self.assertEqual(decode_binary_letters("abbaabab"), "e")
        self.assertEqual(decode_decimal_letters("ih"), "b")
        for invalid in ("a", "abcabcab"):
            with self.assertRaises(ValueError):
                decode_binary_letters(invalid)
        with self.assertRaises(ValueError):
            decode_decimal_letters("z")

    def test_base58check_and_public_key_vectors(self):
        self.assertEqual(base58check_encode(base58check_decode(TARGET_ADDRESS)), TARGET_ADDRESS)
        derived = candidate_addresses((1).to_bytes(32, "big"))
        self.assertEqual(derived["compressed"], "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH")
        self.assertEqual(derived["uncompressed"], "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm")
        with self.assertRaises(ValueError):
            base58check_decode(TARGET_ADDRESS[:-1] + "1")
        with self.assertRaises(ValueError):
            candidate_addresses(bytes(32))

    def test_checkerboard_round_trip(self):
        message = "incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive"
        expected = "15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112"
        self.assertEqual(encode_checkerboard(message), expected)
        self.assertEqual(decode_checkerboard(expected), message)
        with self.assertRaises(ValueError):
            decode_checkerboard("1")

    def test_beaufort_is_reversible(self):
        message = "yourlifeisthesumofaremainder"
        self.assertEqual(decode_beaufort(decode_beaufort(message)), message)
        with self.assertRaises(ValueError):
            decode_beaufort("UPPERCASE")

    def test_embedded_blob_boundaries(self):
        self.assertEqual(embedded_blobs("prefix\nU2FsdGVkX1abcd\nEFGHIJ==\n\nprose\nU2FsdGVkX1last\n"), ["U2FsdGVkX1abcdEFGHIJ==", "U2FsdGVkX1last"])

    def test_primary_image_mirrors_agree(self):
        official = (SOURCES / "gsmg-puzzle.png").read_bytes()
        self.assertEqual(official, (SOURCES / "community-puzzle.png").read_bytes())
        self.assertEqual(official, (SOURCES / "privatekeys-puzzle.png").read_bytes())

    def test_independent_archived_plaintexts_agree(self):
        with patch("builtins.print"):
            reproduce()
        fixtures = {
            "phase2.txt": "maintained-phase2-assets__phase2.1.txt",
            "phase3.txt": "maintained-phase2-assets__phase3.txt",
            "phase32.txt": "maintained-phase3-assets__phase3.2.txt",
        }
        for artifact, fixture in fixtures.items():
            self.assertEqual((ARTIFACTS / artifact).read_bytes(), (SOURCES / fixture).read_bytes())

    def test_offline_full_reproduction(self):
        with patch("builtins.print"):
            report = reproduce()
        self.assertFalse(report["confirmed_solution"])
        self.assertEqual([step["bytes"] for step in report["readable_decryptions"]], [648, 4090, 2422])
        self.assertEqual(report["chain_snapshot"]["confirmed_balance_satoshis"], 125636967)
        self.assertEqual(report["phase32_inner"]["blob_bytes"], 96)
        self.assertFalse(report["issue108"]["claimed_typos_present_in_primary"])
        md5_evaluation = report["issue108"]["evaluations"][0]
        self.assertTrue(md5_evaluation["padding_valid"])
        for candidate in md5_evaluation["candidate_checks"].values():
            self.assertFalse(candidate["matches_main_target"])
            self.assertFalse(candidate["matches_secondary_target"])
        self.assertEqual(report["secondary_chain_snapshot"]["confirmed_balance_satoshis"], 375055856)


class LegacyCryptoTests(unittest.TestCase):
    def test_kdf_agrees_with_openssl(self):
        salt = bytes.fromhex("06286612d43ed7ed")
        password = b"public-test-password"
        for digest in ("md5", "sha256"):
            key, initialization_vector = evp_bytes_to_key(password, salt, digest)
            result = subprocess.run(
                ["openssl", "enc", "-aes-256-cbc", "-P", "-md", digest, "-S", salt.hex(), "-pass", "pass:" + password.decode()],
                check=True, capture_output=True, text=True,
            )
            values = dict(line.split("=", 1) for line in result.stdout.splitlines())
            self.assertEqual(key.hex().upper(), values["key"])
            self.assertEqual(initialization_vector.hex().upper(), values["iv "])

    def test_legacy_round_trip_and_invalid_payloads(self):
        salt = b"12345678"
        password = b"public-test-password"
        message = b"Source-based puzzle decryption test"
        for digest in ("md5", "sha256"):
            key, initialization_vector = evp_bytes_to_key(password, salt, digest)
            ciphertext = AES.new(key, AES.MODE_CBC, initialization_vector).encrypt(pad(message, 16))
            encoded = base64.b64encode(b"Salted__" + salt + ciphertext).decode()
            self.assertEqual(decrypt_salted(encoded, password, digest), message)
        for invalid in ("%%%", base64.b64encode(b"NotAES__" + bytes(24)).decode(), base64.b64encode(b"Salted__" + bytes(9)).decode()):
            with self.assertRaises(ValueError):
                parse_salted(invalid)
        with self.assertRaises(ValueError):
            evp_bytes_to_key(password, b"short", "md5")
        with self.assertRaises(ValueError):
            evp_bytes_to_key(password, salt, "sha1")


class SourceIntegrityTests(unittest.TestCase):
    def test_all_snapshots_match_manifest(self):
        manifest = json.loads((SOURCES / "manifest.json").read_text())
        self.assertEqual(set(manifest), {path.name for path in SOURCES.iterdir() if path.name != "manifest.json"})
        for name, entry in manifest.items():
            payload = (SOURCES / name).read_bytes()
            self.assertEqual(len(payload), entry["bytes"], name)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), entry["sha256"], name)

    def test_collector_rejects_non_https_and_path_traversal(self):
        for name, url in (("../bad", "https://example.invalid"), ("bad.txt", "http://example.invalid")):
            with self.assertRaises(ValueError):
                snapshot(name, url)


if __name__ == "__main__":
    unittest.main()
