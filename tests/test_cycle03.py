import json
import unittest

from tools.audit_binary_key_pairs import key_pairs
from tools.gsmg import ARTIFACTS
from tools.image_sum_derivation import image_matrices, image_sum_streams, residual
from tools.prime_boundary import binary_boundary, extended_markers, special_frames
from tools.prime_markers import tokenizations
from tools.analyze_salphaseion import split_segments
from tools.research_common import fingerprint
from tools.zeroed_residual import OUTPUT, load_frozen_plan
from tools.plan_ranked_alphabet import ranked_alphabets


class PrimeBoundaryTests(unittest.TestCase):
    def test_boundary_is_the_unchanged_known_binary_clue(self):
        boundary = binary_boundary()
        self.assertEqual(boundary["raw_start_zero_based"], 91)
        self.assertEqual(len(boundary["letters"]), 104)
        self.assertEqual(boundary["decoded"], "matrixsumlist")

    def test_full_frame_uniquely_selects_mask1017(self):
        report = json.loads((OUTPUT / "prime-boundary.json").read_text())
        self.assertEqual(report["results"][0]["full_matches"], [])
        self.assertEqual(report["results"][1]["reset_counter_full_matches"], [])
        match = report["results"][1]["full_matches"]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["mask"], 1017)
        self.assertEqual(len(match[0]["frame_markers"]), 25)
        self.assertEqual(match[0]["frame_bits"], "1111011100111101100110010")
        self.assertEqual([(entry["position_one_based"], entry["binary_offset_zero_based"], entry["bit"]) for entry in match[0]["frame_markers"][-2:]], [(89, 5, "1"), (97, 13, "0")])
        full = []
        boundary = binary_boundary()
        for near_white, frame, events in special_frames():
            for mask, tokens in tokenizations(split_segments()["dbbi"]):
                bits = "".join(entry["bit"] for entry in extended_markers(mask, tokens, boundary))
                if bits.startswith(frame):
                    full.append((near_white, mask))
        self.assertEqual(full, [(1, 1017)])

    def test_selected_residual_is_not_edited(self):
        self.assertEqual(residual(), "difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea")
        self.assertEqual(len(residual()), 60)


class ImageAndBinaryEvidenceTests(unittest.TestCase):
    def test_image_matrix_variants_preserve_source_constraints(self):
        variants = dict(image_matrices())
        self.assertEqual(sum(map(sum, variants["original-near-white-0"])), 101)
        self.assertEqual(sum(map(sum, variants["explicit-near-white-1"])), 102)
        reduced = variants["omit-near-white-row-column"]
        self.assertEqual((len(reduced), len(reduced[0]), sum(map(sum, reduced))), (13, 13, 89))
        self.assertEqual(len(image_sum_streams()), 24)
        source = variants["original-near-white-0"]
        self.assertEqual(source[7][4], 0)
        self.assertEqual(variants["explicit-near-white-1"][7][4], 1)

    def test_direct_key_pair_boundaries_have_no_truncation(self):
        payload = bytes(range(79))
        pairs = list(key_pairs(payload))
        self.assertEqual(len(pairs), 16)
        self.assertEqual(pairs[0], (0, (payload[:32], payload[32:64])))
        self.assertEqual(pairs[-1], (15, (payload[15:47], payload[47:79])))
        self.assertEqual(list(key_pairs(bytes(63))), [])
        self.assertEqual(list(key_pairs(bytes(80))), [])

    def test_frozen_zero_plan_candidates_rederive_from_source(self):
        path, plan = load_frozen_plan()
        self.assertEqual(len(plan["passwords"]), 180)
        result = json.loads((OUTPUT / "zeroed-residual-results.json").read_text())
        self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"]), (1080, 3, 0))
        self.assertEqual(result["candidate_set_sha256"], plan["candidate_set_sha256"])

    def test_current_ledgers_and_distinct_space_are_exact(self):
        cumulative = json.loads((OUTPUT / "cumulative-aes-audit.json").read_text())
        self.assertEqual((cumulative["unique_passwords"], cumulative["trial_records"], cumulative["distinct_target_kdf_trials"], cumulative["padding_hit_records"]), (36771, 225234, 220626, 921))
        for ledger in cumulative["audited_ledgers"]:
            self.assertEqual(fingerprint((ARTIFACTS.parents[1] / ledger["ledger"]).read_bytes()), ledger["ledger_sha256"])
        image = json.loads((OUTPUT / "image-sum-results.json").read_text())
        self.assertEqual((image["decode_forms"], image["unique_passwords"], image["aes_trials"], image["padding_hits"]), (2304, 6030, 36180, 137))
        for stem, slots in (("binary-key-pair", 16282), ("binary-key-pair-image", 2912), ("binary-key-pair-decimal", 480)):
            result = json.loads((OUTPUT / (stem + "-results.json")).read_text())
            self.assertEqual(result["slot_checks"], slots)
            self.assertEqual(result["target_matches"], 0)
            self.assertEqual(fingerprint((OUTPUT / (stem + "-checks.jsonl")).read_bytes()), result["ledger_sha256"])

    def test_decimal_plan_and_source_materials_rederive(self):
        path, plan = load_frozen_plan("decimal")
        self.assertEqual(len(plan["forms"]), 160)
        self.assertEqual(len(plan["passwords"]), 1368)
        self.assertEqual(plan["search_space"]["planned_aes_trials"], 8208)
        result = json.loads((OUTPUT / "decimal-residual-results.json").read_text())
        self.assertEqual((result["aes_trials"], result["padding_hits"], result["structure_hits"]), (8208, 26, 0))

    def test_next_ranked_alphabet_plan_has_finite_permutations(self):
        alphabets = ranked_alphabets()
        self.assertEqual(len(alphabets), 32)
        for alphabet in alphabets:
            self.assertEqual(len(alphabet), 28)
            self.assertEqual(set(alphabet), set("abcdefghijklmnopqrstuvwxyz/."))
        plan = json.loads((OUTPUT / "next-ranked-alphabet-plan.json").read_text())
        self.assertEqual(plan["status"], "UNTESTED")
        self.assertEqual(plan["alphabets"], alphabets)
        self.assertEqual((plan["search_space"]["decode_forms"], plan["search_space"]["parse_failures"], plan["search_space"]["unique_passwords"], plan["search_space"]["planned_aes_trials"]), (1408, 576, 2496, 14976))


if __name__ == "__main__":
    unittest.main()
