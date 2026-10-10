#!/usr/bin/env python3
"""Check direct public Bitcoin seed-format contracts without deriving secrets."""

import hashlib
import json
import math

from tools.analyze_salphaseion import split_segments
from tools.bifid_evidence import bifid, key_square


BIP39_WORD_COUNTS = [12, 15, 18, 21, 24]
BIP39_ENTROPY_BITS = [128, 160, 192, 224, 256]
BIP32_SEED_BYTES = list(range(16, 65))


def digest(text):
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def direct_contract(name, text):
    tokens = text.split()
    alphabet = "".join(sorted(set(text)))
    return {
        "name": name,
        "characters": len(text),
        "ascii_bytes": len(text.encode("ascii")),
        "alphabet": alphabet,
        "distinct_symbols": len(alphabet),
        "whitespace_delimited_tokens": len(tokens),
        "has_word_separators": any(symbol.isspace() for symbol in text),
        "is_binary_text": set(text) <= set("01"),
        "is_hex_text": set(text.lower()) <= set("0123456789abcdef"),
        "direct_bip39_word_count_valid": len(tokens) in BIP39_WORD_COUNTS,
        "direct_bip32_seed_byte_length_valid": len(text.encode("ascii")) in BIP32_SEED_BYTES,
        "radix25_information_capacity_bits": round(len(text) * math.log2(25), 6),
        "sha256_identifier": digest(text),
    }


def report():
    segments = split_segments()
    output = bifid(segments["faed"], key_square(segments["dbbi"]), len(segments["faed"]))
    if not output.startswith("btcseed"):
        raise ValueError("Recovered public prefix changed")
    objects = {
        "prefix7": output[:7],
        "body563": output[7:],
        "full570": output,
    }
    contracts = {name: direct_contract(name, text) for name, text in objects.items()}
    if any(entry["direct_bip39_word_count_valid"] or entry["direct_bip32_seed_byte_length_valid"] for entry in contracts.values()):
        raise ValueError("Expected direct seed-format rejection changed")

    return {
        "id": "C28-BTCSEED-FORMAT-CONTRACT",
        "date": "2026-10-02",
        "status": "REJECTED",
        "hypothesis": "The literal btcseed prefix, remaining body563, or complete Bifid570 is already a directly serialized BIP39 mnemonic or BIP32 seed.",
        "invariant": "A direct BIP39 mnemonic has one of the specified word counts; a direct BIP32 seed byte sequence has16 through64 bytes in the specified128 through512-bit range. No decoding, segmentation, hashing, or key derivation may be added.",
        "official_contracts": {
            "BIP39": {
                "allowed_entropy_bits": BIP39_ENTROPY_BITS,
                "allowed_mnemonic_word_counts": BIP39_WORD_COUNTS,
                "derived_seed_bits": 512,
                "source": "research/sources/bip39-structural-excerpt.txt",
                "upstream_sha256": "afcbcbed36fe9eb734bd607398a8c124683ded2a75c3830e1b16c47b043a9134",
            },
            "BIP32": {
                "allowed_seed_bits_inclusive": [128, 512],
                "allowed_whole_byte_lengths": BIP32_SEED_BYTES,
                "source": "research/sources/bip32-structural-excerpt.txt",
                "upstream_sha256": "e5e00a8289db2f681052cf24a745320afc225e66b25d1e489a7c884d2fc7f11f",
            },
        },
        "observed": contracts,
        "classification": {
            "btcseed_as_recognized_literal_prefix": "VERIFIED",
            "prefix7_as_direct_standard_seed": "REJECTED",
            "body563_as_direct_standard_seed": "REJECTED",
            "full570_as_direct_standard_seed": "REJECTED",
            "btcseed_as_type_or_operation_hint": "UNKNOWN",
            "encoded_or_extracted_seed_interface": "UNKNOWN and requires an authored codec/selection rule",
        },
        "graph_effect": "Delete direct Bifid string -> BIP39/BIP32 serialization edges. Retain only an unknown transform from the complete Bifid output, potentially signaled by btcseed, to an unspecified downstream type.",
        "result": "All three literal objects fail both direct contracts: each is one unseparated token rather than12/15/18/21/24 mnemonic words, and their ASCII lengths7/563/570 fall outside BIP32's16..64-byte seed range. The body/full alphabet is neither binary nor hexadecimal. Any surviving seed reading needs an unprovided segmentation or codec.",
        "limits": [
            "This is a direct-format check only; it does not test word segmentation, arbitrary encodings, checksums, derivation paths, or wallet outputs.",
            "Information capacity under a hypothetical radix25 encoding is reported only as dimensional context; no symbol-to-bit encoding is chosen or executed.",
            "Community claims about mnemonic, WIF, or key formats are not treated as creator instructions.",
        ],
        "next_test": "Require an authored codec, token boundary, or receiving format. Without one, no safe structural operation can turn the Bifid body into a standard seed object.",
        "new_cryptographic_trials": 0,
        "new_trial_inputs": 0,
        "private_key_operations": 0,
        "seed_derivations": 0,
        "aes_operations": 0,
    }


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
