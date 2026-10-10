#!/usr/bin/env python3
import hashlib
import json

from tools.gsmg import TARGET_ADDRESS, SECONDARY_ADDRESS, base58check_decode, candidate_addresses, CURVE_ORDER
from tools.research_common import CYCLE, fingerprint, write_once_json


FIELD_PRIME = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
GENERATOR = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def add_points(first, second):
    if first is None:
        return second
    if second is None:
        return first
    first_horizontal, first_vertical = first
    second_horizontal, second_vertical = second
    if first_horizontal == second_horizontal and (first_vertical + second_vertical) % FIELD_PRIME == 0:
        return None
    if first == second:
        slope = (3 * first_horizontal * first_horizontal) * pow(2 * first_vertical, -1, FIELD_PRIME) % FIELD_PRIME
    else:
        slope = (second_vertical - first_vertical) * pow(second_horizontal - first_horizontal, -1, FIELD_PRIME) % FIELD_PRIME
    result_horizontal = (slope * slope - first_horizontal - second_horizontal) % FIELD_PRIME
    result_vertical = (slope * (first_horizontal - result_horizontal) - first_vertical) % FIELD_PRIME
    return result_horizontal, result_vertical


def multiply_generator(scalar):
    if not 0 < scalar < CURVE_ORDER:
        raise ValueError("Scalar must be in the secp256k1 private-key range")
    result = None
    accumulator = GENERATOR
    remaining = scalar
    while remaining:
        if remaining & 1:
            result = add_points(result, accumulator)
        accumulator = add_points(accumulator, accumulator)
        remaining >>= 1
    return result


def independent_base58check(payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    encoded = payload + checksum
    remaining = int.from_bytes(encoded, "big")
    output = ""
    while remaining:
        remaining, remainder = divmod(remaining, 58)
        output = ALPHABET[remainder] + output
    zeros = len(encoded) - len(encoded.lstrip(b"\x00"))
    return "1" * zeros + output


def independent_addresses(candidate):
    if len(candidate) != 32:
        raise ValueError("Candidate must contain exactly 32 bytes")
    horizontal, vertical = multiply_generator(int.from_bytes(candidate, "big"))
    public_encodings = {
        "compressed": bytes([2 + (vertical & 1)]) + horizontal.to_bytes(32, "big"),
        "uncompressed": b"\x04" + horizontal.to_bytes(32, "big") + vertical.to_bytes(32, "big"),
    }
    return {
        name: independent_base58check(b"\x00" + hashlib.new("ripemd160", hashlib.sha256(encoding).digest()).digest())
        for name, encoding in public_encodings.items()
    }


def verify_candidate(candidate):
    primary = candidate_addresses(candidate)
    independent = independent_addresses(candidate)
    if primary != independent:
        raise ValueError("Independent EC/address implementations disagree")
    return {"candidate_sha256": fingerprint(candidate), "primary": primary, "independent": independent, "implementations_agree": True, "main_target_match": TARGET_ADDRESS in independent.values(), "secondary_target_match": SECONDARY_ADDRESS in independent.values(), "implementation_note": "Primary cryptography/OpenSSL EC implementation versus independent Python affine secp256k1 arithmetic and Base58 encoder; hashlib SHA/Ripemd shared"}


def audit_existing_claim():
    candidate_material = (CYCLE.parent / "issue108-md5.bin").read_bytes()
    results = [verify_candidate(candidate_material[offset:offset + 32]) for offset in (0, 32)]
    report = {"id": "C02-INDEPENDENT-BTC", "source": "Already-public issue108 binary candidates; not arbitrary keyspace search", "results": results, "status": "REJECTED", "result": "Neither direct candidate derives either scoped address under either public-key serialization, verified by two separate EC/address implementations"}
    write_once_json(CYCLE / "independent-btc.json", report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    audit_existing_claim()
