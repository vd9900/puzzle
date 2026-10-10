# Cycle 28 findings — 2026-10-02

`btcseed` is a verified literal prefix, but neither it, body563, nor full Bifid570 is directly serialized as a standard BIP39 mnemonic or BIP32 seed.

- BIP39 permits12,15,18,21, or24 words. Each puzzle object is one unseparated token.
- BIP32 specifies a128–512-bit seed byte sequence. Literal ASCII lengths are7,563, and570 bytes.
- Body/full use a25-letter alphabet and are neither binary nor hexadecimal text.

This rejects only direct standard serialization. Any surviving seed interpretation requires an authored segmentation, alphabet-to-bits codec, extraction rule, or other transform. None is present in the preserved source.

```bash
python3 -m tools.btcseed_format_contract
python3 -m unittest tests.test_btcseed_format_contract -v
```

No mnemonic generation, seed derivation, key operation, wallet operation, or ciphertext trial was performed.
