import unittest

from tools.btcseed_format_contract import report


class BtcseedFormatContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = report()

    def test_official_dimensions_are_frozen(self):
        contracts = self.document["official_contracts"]
        self.assertEqual(contracts["BIP39"]["allowed_mnemonic_word_counts"], [12, 15, 18, 21, 24])
        self.assertEqual(contracts["BIP39"]["derived_seed_bits"], 512)
        self.assertEqual(contracts["BIP32"]["allowed_seed_bits_inclusive"], [128, 512])

    def test_exact_public_object_lengths(self):
        observed = self.document["observed"]
        self.assertEqual(observed["prefix7"]["characters"], 7)
        self.assertEqual(observed["body563"]["characters"], 563)
        self.assertEqual(observed["full570"]["characters"], 570)

    def test_no_direct_bip39_contract(self):
        for entry in self.document["observed"].values():
            self.assertEqual(entry["whitespace_delimited_tokens"], 1)
            self.assertFalse(entry["direct_bip39_word_count_valid"])

    def test_no_direct_bip32_contract(self):
        for entry in self.document["observed"].values():
            self.assertFalse(entry["direct_bip32_seed_byte_length_valid"])

    def test_body_and_full_are_not_binary_or_hex_text(self):
        for name in ("body563", "full570"):
            self.assertFalse(self.document["observed"][name]["is_binary_text"])
            self.assertFalse(self.document["observed"][name]["is_hex_text"])

    def test_non_executing_scope(self):
        self.assertEqual(self.document["new_cryptographic_trials"], 0)
        self.assertEqual(self.document["new_trial_inputs"], 0)
        self.assertEqual(self.document["private_key_operations"], 0)
        self.assertEqual(self.document["seed_derivations"], 0)
        self.assertEqual(self.document["aes_operations"], 0)


if __name__ == "__main__":
    unittest.main()
