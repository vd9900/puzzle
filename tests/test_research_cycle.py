import itertools
import json
import unittest
from pathlib import Path

from tools.analyze_salphaseion import profile, split_segments
from tools.corpus_index import classify, records
from tools.joint_derivation import columnar, nine_checkerboard
from tools.prime_markers import color_bits, marker_match, tokenizations
from tools.research_common import CYCLE, fingerprint, index_of_coincidence, score_plaintext, structural_checks, target_checks
from tools.gsmg import SOURCES, CURVE_ORDER, candidate_addresses
from tools.gsmg import base58check_encode
from tools.salphaseion_experiments import decode_board, keyed_alphabet, rectangular_routes
from tools.verify_btc import FIELD_PRIME, GENERATOR, add_points, independent_addresses, multiply_generator, verify_candidate
from tools.residual_coordinates import derived_forms, selected_payload, square_transforms
from tools.plan_zeroed_residual import planned_forms


class ArtifactAnalysisTests(unittest.TestCase):
    def test_exact_structural_segments(self):
        segments = split_segments()
        self.assertEqual({name: len(text) for name, text in segments.items()}, {"dbbi": 91, "faed": 570, "joined": 661})
        self.assertEqual(segments["dbbi"] + segments["faed"], segments["joined"])
        self.assertEqual(profile(segments["dbbi"])["counts"]["b"], 25)
        self.assertAlmostEqual(index_of_coincidence(segments["dbbi"]), 0.1509157509157509)

    def test_profile_transition_totals(self):
        result = profile("ababcab")
        total = sum(count for row in result["transition_counts"].values() for count in row.values())
        self.assertEqual(total, 6)
        self.assertEqual(index_of_coincidence("aaaa"), 1)
        self.assertEqual(index_of_coincidence(""), 0)

    def test_residual_coordinate_family_bounds(self):
        self.assertEqual(len(selected_payload()), 60)
        orientations = list(square_transforms())
        self.assertEqual(len(orientations), 8)
        forms = list(derived_forms())
        self.assertEqual(len(forms), 388)
        self.assertEqual(sum(len(payload) == 40 for parameters, payload in forms), 384)

    def test_next_zeroed_residual_plan_is_exact_and_non_destructive(self):
        forms = list(planned_forms())
        self.assertEqual(len(forms), 180)
        self.assertEqual(sum(entry["error"] is not None for entry in forms), 120)
        self.assertEqual({len(entry["residual"]) for entry in forms}, {60, 61})
        for entry in forms:
            self.assertEqual(len(entry["digits"]), len(entry["residual"]))
            self.assertNotEqual(entry["parameters"]["alphabet"], "hint-phrase")
        document = json.loads((CYCLE / "next-zeroed-residual-plan.json").read_text())
        self.assertEqual(document["status"], "UNTESTED")
        self.assertEqual(document["forms"], forms)
        self.assertEqual(document["search_space"]["unique_passwords"], 180)
        self.assertEqual(document["search_space"]["planned_aes_trials"], 1080)

    def test_rectangular_routes_preserve_every_cell(self):
        for rows, columns in ((1, 1), (2, 3), (7, 13), (13, 7), (19, 30)):
            expected = set(itertools.product(range(rows), range(columns)))
            for name, coordinates in rectangular_routes(rows, columns):
                self.assertEqual(len(coordinates), rows * columns, name)
                self.assertEqual(set(coordinates), expected, name)

    def test_keyed_columnar_round_trip_with_duplicates(self):
        for keyword in ("matrixsumlist", "theseedisplanted", "letter", "a"):
            for length in (1, 12, 60, 91, 570):
                plaintext = ("abcdefghi" * 64)[:length]
                self.assertEqual(columnar(columnar(plaintext, keyword, False), keyword, True), plaintext)
        with self.assertRaises(ValueError):
            columnar("abc", "")

    def test_checkerboards_agree_with_known_stream(self):
        digits = "15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112"
        decoded = decode_board(digits, (1, 4), "fubcdora/lethingkymvpszjqwx.")
        self.assertEqual(decoded, "incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive")
        with self.assertRaises(ValueError):
            decode_board("1", (1, 4), "fubcdora/lethingkymvpszjqwx.")
        with self.assertRaises(ValueError):
            nine_checkerboard([1], "abcdefghiklmnopqrstuvwxyz", (1, 4))
        self.assertEqual(len(keyed_alphabet("matrixsumlist")), 28)

    def test_prime_dp_agrees_with_exhaustive_enumeration(self):
        text = split_segments()["dbbi"]
        expected = color_bits()
        maximum = 0
        total = 0
        from tools.prime_markers import is_prime
        for mask, tokens in tokenizations(text):
            total += 1
            markers = [entry["token"] for entry in tokens if is_prime(entry["position_one_based"])]
            bits = "".join("1" if token == "b" else "0" if token == "be" else "?" for token in markers)
            prefix = 0
            for actual, wanted in zip(bits, expected):
                if actual != wanted:
                    break
                prefix += 1
            maximum = max(maximum, prefix)
        self.assertEqual(total, 1024)
        self.assertEqual(maximum, 20)
        self.assertEqual(marker_match(text, expected), maximum)
        self.assertEqual(expected, "111101110011110110010010")
        report = json.loads((CYCLE / "prime-markers.json").read_text())
        near_white_one = report["near_white_frame"]["hypotheses"][1]
        exact_prefix = [item for item in near_white_one["comparisons"] if item["all_available_prime_markers_match"]]
        self.assertEqual(len(exact_prefix), 1)
        self.assertEqual(exact_prefix[0]["mask"], 1017)
        self.assertEqual(exact_prefix[0]["matched_prefix"], 23)
        self.assertEqual(exact_prefix[0]["unconsumed_frame_bits"], "10")

    def test_scoring_does_not_confirm_english(self):
        english = score_plaintext(b"the private key belongs to your puzzle")
        noise = score_plaintext(bytes(range(80)))
        self.assertGreater(english["printable_ratio"], noise["printable_ratio"])
        self.assertGreater(english["language_score"], noise["language_score"])
        self.assertIn("not proof", english["score_limit"])
        self.assertEqual(structural_checks(b"plain English text without a key"), ([], []))
        self.assertEqual(target_checks(b"plain English text")["target_match"], False)

    def test_wif_structure_and_target_gate(self):
        candidate = (1).to_bytes(32, "big")
        wif = base58check_encode(b"\x80" + candidate).encode()
        structures, decoded = structural_checks(wif)
        self.assertEqual(structures, ["valid_wif"])
        self.assertEqual(decoded, [candidate])
        result = target_checks(wif)
        self.assertEqual(len(result["candidate_checks"]), 1)
        self.assertFalse(result["target_match"])

    def test_corpus_handles_byte_encoded_source(self):
        extracted = list(records(SOURCES / "maintained-phase3-assets__phase3.2.txt"))
        self.assertEqual(len(extracted), 1)
        self.assertIn("I've been waiting for you.", extracted[0][1])
        self.assertEqual(classify("salphaseion.html", {}), "ORIGINAL")
        self.assertEqual(classify("github-issue-108.json", {}), "UNVERIFIED_CLAIM")


class IndependentBitcoinVerificationTests(unittest.TestCase):
    def test_curve_arithmetic(self):
        self.assertEqual(multiply_generator(1), GENERATOR)
        self.assertEqual(multiply_generator(2), add_points(GENERATOR, GENERATOR))
        self.assertIsNone(add_points(GENERATOR, (GENERATOR[0], -GENERATOR[1] % FIELD_PRIME)))
        self.assertEqual(add_points(None, GENERATOR), GENERATOR)
        for invalid in (0, CURVE_ORDER, -1):
            with self.assertRaises(ValueError):
                multiply_generator(invalid)

    def test_independent_address_vectors_and_scalars(self):
        for scalar in (1, 2, 17, 20260930, CURVE_ORDER - 1):
            candidate = scalar.to_bytes(32, "big")
            self.assertEqual(independent_addresses(candidate), candidate_addresses(candidate))
        self.assertEqual(independent_addresses((1).to_bytes(32, "big"))["compressed"], "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH")
        self.assertTrue(verify_candidate((2).to_bytes(32, "big"))["implementations_agree"])


class CycleEvidenceTests(unittest.TestCase):
    def test_original_and_new_evidence_checksums(self):
        for root in (SOURCES, SOURCES.parent / "evidence" / "cycle02"):
            manifest = json.loads((root / "manifest.json").read_text())
            for name, entry in manifest.items():
                self.assertEqual(fingerprint((root / name).read_bytes()), entry["sha256"], name)

    def test_cycle_exact_spaces_and_completed_ledgers(self):
        results = json.loads((CYCLE / "inner-search-results.json").read_text())
        self.assertEqual(results["unique_passwords"], 4914)
        self.assertEqual(results["total_trials"], 29484)
        self.assertEqual(results["padding_hits"], 113)
        self.assertEqual(results["structural_hits"], 0)
        sal = json.loads((CYCLE / "sal-experiment-results.json").read_text())
        self.assertEqual(sal["total_trials"], 10644)
        joint = json.loads((CYCLE / "joint-results.json").read_text())
        self.assertEqual(joint["aes_trials"], 86760)
        self.assertEqual(joint["structure_hits"], 0)
        self.assertEqual(joint["target_matches"], 0)
        with (CYCLE / "joint-aes.jsonl").open() as ledger:
            self.assertEqual(sum(1 for line in ledger), 14460)
        gap = json.loads((CYCLE / "prime-gap-results.json").read_text())
        self.assertEqual(gap["trials"], 3402)
        self.assertEqual(gap["structural_hits"], 0)
        paired = json.loads((CYCLE / "paired-results.json").read_text())
        self.assertEqual(paired["aes_trials"], 53136)
        self.assertEqual(paired["structure_hits"], 0)
        coordinate = json.loads((CYCLE / "coordinate-results.json").read_text())
        self.assertEqual(coordinate["aes_trials"], 6984)
        self.assertEqual(coordinate["padding_hits"], 25)
        audit = json.loads((CYCLE / "ledger-audit.json").read_text())
        self.assertEqual(audit["total_trials"], 179766)
        self.assertEqual(audit["unique_passwords"], 29961)


if __name__ == "__main__":
    unittest.main()
