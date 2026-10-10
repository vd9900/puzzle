import json
import unittest

from tools.carry_forward_ownership import OUTPUT, report
from tools.instruction_graphs import ROOT


class CarryForwardOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_two_public_fixture_archive_pairs_remain_exact(self):
        pairs = self.document["fixture_archive_pairs_verified"]
        self.assertEqual(len(pairs), 2)
        for fixture, archive in pairs:
            self.assertEqual((ROOT / fixture).read_bytes(), (ROOT / archive).read_bytes())

    def test_nine_primary_anchors_reconstruct_exact_bytes(self):
        anchors = self.document["primary_local_anchors"] + self.document["current_prefix_anchors"]
        self.assertEqual(len(anchors), 9)
        for entry in anchors:
            payload = (ROOT / entry["source"]["path"]).read_bytes()
            start, end = entry["utf8_byte_span_zero_based_half_open"]
            self.assertEqual(payload[start:end], entry["literal"].encode())

    def test_names_from_solved_riddles_are_not_literal_source_labels(self):
        self.assertEqual(self.document["earlier_names_not_literal_in_primary_phase3"], {"Jacque Fresco": False, "Heisenberg": False})

    def test_six_interfaces_distinguish_local_consumer_from_carried_identity(self):
        interfaces = self.document["ownership_interfaces"]
        self.assertEqual(len(interfaces), 6)
        self.assertTrue(all(entry["later_carried_object_identity"] == "NOT_ASSIGNED" for entry in interfaces))
        self.assertEqual(interfaces[0]["binding"], "EXPLICIT_PRIMARY_AGGREGATE")
        self.assertEqual(self.document["explicit_later_carried_input_identities"], 0)

    def test_frozen_directives_baseline_and_branch_roles_are_reused(self):
        controls = self.document["frozen_controls"]
        self.assertEqual(len(controls["speech_directives"]["anchors"]), 8)
        self.assertEqual(len(controls["branch_roles"]["roles"]["paragraphs"]), 6)
        self.assertTrue(controls["speech_delta"]["no_baseline_realignment"])
        self.assertEqual(controls["branch_roles"]["roles"]["paragraphs"][2]["byte_span_zero_based_half_open"], [447, 1986])

    def test_hypotheses_have_fields_and_no_derived_input(self):
        required = {"hypothesis", "source_evidence", "source_locations", "assumptions", "operation_order", "input", "output", "confidence", "contradictions", "next_test"}
        self.assertEqual(len(self.document["hypotheses"]), 3)
        self.assertTrue(all(required <= entry.keys() for entry in self.document["hypotheses"]))
        self.assertEqual((self.document["new_cryptographic_trials"], self.document["new_trial_inputs"]), (0, 0))

    def test_frozen_report_regenerates_without_mutation(self):
        path = OUTPUT / "carry-forward-ownership.json"
        payload = path.read_bytes()
        self.assertEqual(json.loads(payload), self.document)
        self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
