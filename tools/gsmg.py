#!/usr/bin/env python3
import argparse
import base64
import hashlib
import html
import json
import math
import re
from time import perf_counter
from collections import Counter
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from PIL import Image
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "research" / "sources"
ARTIFACTS = ROOT / "research" / "artifacts"
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
SECONDARY_ADDRESS = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
CURVE_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
PHASE3_PREIMAGE = (
    "causalitySafenetLunaHSM11110"
    "0x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F"
    "20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854"
    "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1"
)
PHASE32_PREIMAGE = "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"
SALPHASEION_PREIMAGE = "GSMGIO5BTCPUZZLECHALLENGE" + TARGET_ADDRESS


def sha256_hex(payload):
    return hashlib.sha256(payload).hexdigest()


def parse_salted(encoded):
    compact = "".join(encoded.split())
    payload = base64.b64decode(compact, validate=True)
    if payload[:8] != b"Salted__":
        raise ValueError("Missing OpenSSL Salted__ header")
    if len(payload) < 32 or (len(payload) - 16) % AES.block_size:
        raise ValueError("Invalid AES-CBC ciphertext length")
    return payload[8:16], payload[16:]


def evp_bytes_to_key(password, salt, digest="sha256"):
    if len(salt) != 8:
        raise ValueError("Legacy OpenSSL salt must be 8 bytes")
    if digest not in ("md5", "sha256"):
        raise ValueError("Only explicitly supported legacy KDF digests are allowed")
    material = b""
    previous = b""
    while len(material) < 48:
        previous = hashlib.new(digest, previous + password + salt).digest()
        material += previous
    return material[:32], material[32:48]


def decrypt_salted(encoded, password, digest="sha256"):
    salt, ciphertext = parse_salted(encoded)
    key, initialization_vector = evp_bytes_to_key(password, salt, digest)
    padded = AES.new(key, AES.MODE_CBC, initialization_vector).decrypt(ciphertext)
    return unpad(padded, AES.block_size)


def textareas(document):
    return [html.unescape(content) for content in re.findall(r"<textarea\b[^>]*>(.*?)</textarea>", document, re.S | re.I)]


def embedded_blobs(document):
    blobs = []
    current = []
    for line in document.splitlines():
        stripped = line.strip()
        if stripped.startswith("U2FsdGVkX1"):
            if current:
                blobs.append("".join(current))
            current = [stripped]
        elif current and re.fullmatch(r"[A-Za-z0-9+/=]+", stripped):
            current.append(stripped)
        elif current:
            blobs.append("".join(current))
            current = []
    if current:
        blobs.append("".join(current))
    return blobs


def spiral_coordinates(size):
    if size < 1:
        raise ValueError("Grid size must be positive")
    top = left = 0
    bottom = right = size - 1
    coordinates = []
    while top <= bottom and left <= right:
        coordinates.extend((row, left) for row in range(top, bottom + 1))
        left += 1
        coordinates.extend((bottom, column) for column in range(left, right + 1))
        bottom -= 1
        if left <= right:
            coordinates.extend((row, right) for row in range(bottom, top - 1, -1))
            right -= 1
        if top <= bottom:
            coordinates.extend((top, column) for column in range(right, left - 1, -1))
            top += 1
    return coordinates


def extract_grid(image_path):
    palette = {
        (0, 0, 0): ("black", 1),
        (63, 72, 204): ("blue", 1),
        (255, 242, 0): ("yellow", 0),
        (255, 255, 255): ("white", 0),
        (254, 254, 254): ("near_white", 0),
    }
    with Image.open(image_path) as source_image:
        image = source_image.convert("RGB")
    grid_width = image.width - 1
    rows = []
    colors = []
    for row_index in range(14):
        row = []
        color_row = []
        for column_index in range(14):
            box = (
                round(column_index * grid_width / 14),
                round(row_index * grid_width / 14),
                round((column_index + 1) * grid_width / 14),
                round((row_index + 1) * grid_width / 14),
            )
            dominant_color = Counter(image.crop(box).getdata()).most_common(1)[0][0]
            if dominant_color not in palette:
                raise ValueError(f"Unexpected dominant color at {(row_index, column_index)}")
            color_name, bit = palette[dominant_color]
            row.append(bit)
            color_row.append(color_name)
        rows.append(row)
        colors.append(color_row)
    coordinates = spiral_coordinates(14)
    bits = "".join(str(rows[row][column]) for row, column in coordinates)
    whole_bytes = len(bits) // 8
    decoded = bytes(int(bits[offset:offset + 8], 2) for offset in range(0, whole_bytes * 8, 8)).decode("ascii")
    color_indices = [index for index, (row, column) in enumerate(coordinates) if colors[row][column] in ("blue", "yellow")]
    return {
        "matrix": rows,
        "colors": colors,
        "decoded": decoded,
        "trailing_bits": bits[whole_bytes * 8:],
        "colored_spiral_indices": color_indices,
        "near_white_cells_zero_based": [[row, column] for row in range(14) for column in range(14) if colors[row][column] == "near_white"],
    }


def decode_binary_letters(encoded):
    compact = "".join(encoded.split())
    if not re.fullmatch(r"[ab]+", compact) or len(compact) % 8:
        raise ValueError("Binary letter run must contain whole bytes of a/b")
    bits = compact.translate(str.maketrans("ab", "01"))
    return bytes(int(bits[offset:offset + 8], 2) for offset in range(0, len(bits), 8)).decode("ascii")


def decode_decimal_letters(encoded):
    compact = "".join(encoded.split())
    if not re.fullmatch(r"[a-io]+", compact):
        raise ValueError("Decimal letter run must contain only a-i/o")
    number = int(compact.translate(str.maketrans("abcdefghio", "1234567890")))
    return number.to_bytes((number.bit_length() + 7) // 8, "big").decode("ascii")


def extract_salphaseion(document):
    sections = textareas(document)
    if len(sections) != 2:
        raise ValueError("Expected SalPhaseIon and Cosmic Duality textareas")
    compact = "".join(sections[0].split())
    binary_runs = re.findall(r"[ab]{16,}", compact)
    if len(binary_runs) != 2:
        raise ValueError("Expected two binary clue runs")
    before_blob, blob_tail = compact.split("U2FsdGVkX1", 1)
    delimited = before_blob.split("z")
    if len(delimited) != 4:
        raise ValueError("Expected three z separators before the small blob")
    binary_clues = [decode_binary_letters(run) for run in binary_runs]
    decimal_clues = [decode_decimal_letters(segment) for segment in delimited[1:3]]
    small_blob = ("U2FsdGVkX1" + blob_tail).split("shabef", 1)[0]
    small_blob = small_blob.replace(binary_runs[1], "", 1)
    parse_salted(small_blob)
    cosmic_blob = "".join(sections[1].split())
    parse_salted(cosmic_blob)
    return {
        "binary_clues": binary_clues,
        "decimal_clues": decimal_clues,
        "command_clue": delimited[3],
        "small_blob": small_blob,
        "cosmic_blob": cosmic_blob,
        "unresolved_prefix": delimited[0].replace(binary_runs[0], "", 1),
    }


def entropy(payload):
    if not payload:
        return 0.0
    return -sum((count / len(payload)) * math.log2(count / len(payload)) for count in Counter(payload).values())


def payload_summary(payload):
    return {
        "bytes": len(payload),
        "sha256": sha256_hex(payload),
        "shannon_entropy_bits_per_byte": round(entropy(payload), 4),
        "longest_printable_ascii_run": max((len(run) for run in re.findall(rb"[\x20-\x7e]+", payload)), default=0),
    }


def base58check_decode(encoded):
    if not encoded:
        raise ValueError("Empty Base58Check string")
    number = 0
    for character in encoded:
        if character not in BASE58_ALPHABET:
            raise ValueError("Invalid Base58 character")
        number = number * 58 + BASE58_ALPHABET.index(character)
    decoded = number.to_bytes((number.bit_length() + 7) // 8, "big")
    decoded = b"\x00" * (len(encoded) - len(encoded.lstrip("1"))) + decoded
    if len(decoded) < 5:
        raise ValueError("Base58Check string is too short")
    payload, checksum = decoded[:-4], decoded[-4:]
    expected = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    if checksum != expected:
        raise ValueError("Base58Check checksum mismatch")
    return payload


def base58check_encode(payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    full_payload = payload + checksum
    number = int.from_bytes(full_payload, "big")
    characters = []
    while number:
        number, remainder = divmod(number, 58)
        characters.append(BASE58_ALPHABET[remainder])
    zeros = len(full_payload) - len(full_payload.lstrip(b"\x00"))
    return "1" * zeros + "".join(reversed(characters))


def candidate_addresses(candidate):
    if len(candidate) != 32 or not 0 < int.from_bytes(candidate, "big") < CURVE_ORDER:
        raise ValueError("Candidate must be a valid 32-byte secp256k1 scalar")
    public_key = ec.derive_private_key(int.from_bytes(candidate, "big"), ec.SECP256K1()).public_key()
    addresses = {}
    for name, point_format in (
        ("compressed", serialization.PublicFormat.CompressedPoint),
        ("uncompressed", serialization.PublicFormat.UncompressedPoint),
    ):
        encoded = public_key.public_bytes(serialization.Encoding.X962, point_format)
        public_key_hash = hashlib.new("ripemd160", hashlib.sha256(encoded).digest()).digest()
        addresses[name] = base58check_encode(b"\x00" + public_key_hash)
    return addresses


def decode_beaufort(encoded, keyword="THEMATRIXHASYOU"):
    if not re.fullmatch(r"[a-z]+", encoded) or not re.fullmatch(r"[A-Z]+", keyword):
        raise ValueError("Expected lowercase Beaufort text and an uppercase keyword")
    return "".join(chr(97 + (ord(keyword[index % len(keyword)]) - 65 - (ord(letter) - 97)) % 26) for index, letter in enumerate(encoded))


def checkerboard():
    board = dict(zip("02356789", "fubcdora"))
    board.update({"1" + str(column): letter for column, letter in enumerate("/lethingky")})
    board.update({"4" + str(column): letter for column, letter in enumerate("mvpszjqwx.")})
    return board


def decode_checkerboard(numbers):
    if not re.fullmatch(r"[0-9]+", numbers):
        raise ValueError("Checkerboard input must be decimal digits")
    board = checkerboard()
    position = 0
    letters = []
    while position < len(numbers):
        code = numbers[position]
        position += 1
        if code in ("1", "4"):
            if position == len(numbers):
                raise ValueError("Truncated checkerboard prefix")
            code += numbers[position]
            position += 1
        letters.append(board[code])
    return "".join(letters)


def encode_checkerboard(message):
    inverse = {letter: code for code, letter in checkerboard().items()}
    try:
        return "".join(inverse[letter] for letter in message)
    except KeyError as error:
        raise ValueError("Unsupported checkerboard character") from error


def decode_phase32(plaintext):
    separator = b"four for one.\r\n\r\n"
    if separator not in plaintext:
        raise ValueError("Missing Phase 3.2 encoding clue")
    block_start = plaintext.index(separator) + len(separator)
    numeric_match = re.search(rb"\r\n\r\n([0-9]{100,})", plaintext)
    if numeric_match is None:
        raise ValueError("Missing Phase 3.2 numeric stream")
    encoded_block = plaintext[block_start:numeric_match.start()]
    normalized = encoded_block.decode("latin-1").encode("cp273").decode("ascii")
    speech = decode_beaufort(normalized)
    if not speech.startswith("yourlifeisthesumofaremainder") or not speech.endswith("ciaobellao"):
        raise ValueError("Beaufort did not reproduce the expected speech")
    numbers = numeric_match.group(1).decode()
    message = decode_checkerboard(numbers)
    if encode_checkerboard(message) != numbers:
        raise ValueError("Checkerboard round trip did not reproduce the numeric stream")
    ARTIFACTS.joinpath("phase32-beaufort.txt").write_text(speech + "\n")
    ARTIFACTS.joinpath("phase32-checkerboard.txt").write_text(message + "\n")
    return {
        "beaufort": {"status": "CONFIRMED", "symbol_count": len(set(encoded_block)), "normalization": "latin-1 characters encoded as cp273; this observed alphabet is also mapped by cp1141", "keyword": "THEMATRIXHASYOU", **payload_summary(speech.encode())},
        "checkerboard": {"status": "CONFIRMED", "digits": len(numbers), "prefixes": [1, 4], "alphabet": "fubcdora/lethingkymvpszjqwx.", "round_trip_matches": True, "message": message},
    }


def inspect_claim(salphaseion):
    claim = json.loads((SOURCES / "github-issue-108.json").read_text())
    claimed_blob = re.search(r"Fixed blob:\s*(U2F[A-Za-z0-9+/=]+)", claim["body"]).group(1)
    live_blob = salphaseion["small_blob"]
    if len(live_blob) != len(claimed_blob):
        raise ValueError("Claim and primary blob lengths differ")
    differences = [{"position_zero_based": index, "primary": actual, "claim": claimed} for index, (actual, claimed) in enumerate(zip(live_blob, claimed_blob)) if actual != claimed]
    password = b"matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"
    results = {
        "issue": 108,
        "claim_created_at": claim["created_at"],
        "primary_vs_claim_differences": differences,
        "claimed_typos_present_in_primary": bool(differences),
        "evaluations": [],
        "status": "INCONCLUSIVE",
        "reason": "Padding and random-looking plaintext do not demonstrate the target key or an intended puzzle step",
    }
    for digest in ("md5", "sha256"):
        try:
            plaintext = decrypt_salted(live_blob, password, digest)
            evaluation = {"digest": digest, "padding_valid": True, **payload_summary(plaintext)}
            ARTIFACTS.joinpath(f"issue108-{digest}.bin").write_bytes(plaintext)
            alleged_key_match = re.search(r"K_C1\s*=\s*([0-9a-f]+)", claim["body"])
            evaluation["claimed_first_key_matches"] = plaintext[:32].hex() == alleged_key_match.group(1)
            candidate_results = {}
            for name, start in (("K_C1", 0), ("K_C2", 32)):
                derived = candidate_addresses(plaintext[start:start + 32])
                candidate_results[name] = {
                    "addresses": derived,
                    "matches_main_target": TARGET_ADDRESS in derived.values(),
                    "matches_secondary_target": SECONDARY_ADDRESS in derived.values(),
                }
            evaluation["candidate_checks"] = candidate_results
        except ValueError as error:
            evaluation = {"digest": digest, "padding_valid": False, "error": str(error)}
        results["evaluations"].append(evaluation)
    return results


def reproduce():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    report = {"target_address": TARGET_ADDRESS, "confirmed_solution": False, "network_transactions": 0}
    grid = extract_grid(SOURCES / "gsmg-puzzle.png")
    if grid["decoded"] != "gsmg.io/theseedisplanted":
        raise ValueError("Primary image did not reproduce the documented URL")
    report["phase0"] = grid
    preimages = {"causality": "causality", "phase3": PHASE3_PREIMAGE, "phase32": PHASE32_PREIMAGE, "salphaseion": SALPHASEION_PREIMAGE}
    report["preimage_hashes"] = {name: sha256_hex(value.encode()) for name, value in preimages.items()}
    primary_blobs = textareas((SOURCES / "phase2.html").read_text())
    if len(primary_blobs) != 2:
        raise ValueError("Expected two primary Phase 2 AES blobs")
    steps = []
    for name, blob, password_name, expected_prefix in (
        ("phase2", primary_blobs[0], "causality", b"The ironic"),
        ("phase3", primary_blobs[1], "phase3", b"What if the merovingian"),
    ):
        password = report["preimage_hashes"][password_name].encode()
        plaintext = decrypt_salted(blob, password, "sha256")
        if not plaintext.startswith(expected_prefix):
            raise ValueError(f"{name} did not reproduce expected readable text")
        ARTIFACTS.joinpath(f"{name}.txt").write_bytes(plaintext)
        steps.append({"name": name, "digest": "sha256", "salt": parse_salted(blob)[0].hex(), "status": "CONFIRMED", **payload_summary(plaintext)})
    nested = embedded_blobs(plaintext.decode())
    if len(nested) != 1:
        raise ValueError("Expected one embedded Phase 3.2 blob")
    phase32_blob = nested[0]
    phase32 = decrypt_salted(phase32_blob, report["preimage_hashes"]["phase32"].encode(), "sha256")
    if not phase32.startswith(b"I've been waiting for you."):
        raise ValueError("Phase 3.2 did not reproduce the Architect text")
    ARTIFACTS.joinpath("phase32.txt").write_bytes(phase32)
    report["phase32_classical_ciphers"] = decode_phase32(phase32)
    steps.append({"name": "phase32", "digest": "sha256", "salt": parse_salted(phase32_blob)[0].hex(), "status": "CONFIRMED", **payload_summary(phase32)})
    inner_blobs = embedded_blobs(phase32.decode("latin-1"))
    if len(inner_blobs) != 1:
        raise ValueError("Expected one unsolved inner Phase 3.2 blob")
    ARTIFACTS.joinpath("phase32-inner.b64").write_text(inner_blobs[0] + "\n")
    inner_salt, inner_ciphertext = parse_salted(inner_blobs[0])
    report["phase32_inner"] = {"status": "UNTESTED", "salt": inner_salt.hex(), "ciphertext_bytes": len(inner_ciphertext), "blob_bytes": len(inner_ciphertext) + 16}
    report["readable_decryptions"] = steps
    salphaseion = extract_salphaseion((SOURCES / "salphaseion.html").read_text())
    ARTIFACTS.joinpath("salphaseion-small.b64").write_text(salphaseion["small_blob"] + "\n")
    ARTIFACTS.joinpath("cosmic-duality.b64").write_text(salphaseion["cosmic_blob"] + "\n")
    ARTIFACTS.joinpath("salphaseion-unresolved-prefix.txt").write_text(salphaseion["unresolved_prefix"] + "\n")
    report["salphaseion"] = {name: value for name, value in salphaseion.items() if name not in ("small_blob", "cosmic_blob", "unresolved_prefix")}
    report["salphaseion"]["unresolved_prefix_letters"] = len(salphaseion["unresolved_prefix"])
    report["issue108"] = inspect_claim(salphaseion)
    address = base58check_decode(TARGET_ADDRESS)
    if len(address) != 21 or address[0] != 0:
        raise ValueError("Unexpected target address encoding")
    report["target_hash160"] = address[1:].hex()
    first = json.loads((SOURCES / "blockstream-address.json").read_text())
    second = json.loads((SOURCES / "mempool-address.json").read_text())
    if first != second or first["address"] != TARGET_ADDRESS:
        raise ValueError("Explorer snapshots disagree or contain the wrong address")
    balance = first["chain_stats"]["funded_txo_sum"] - first["chain_stats"]["spent_txo_sum"]
    utxos = json.loads((SOURCES / "blockstream-utxos.json").read_text())
    if sum(output["value"] for output in utxos) != balance:
        raise ValueError("UTXO total differs from the confirmed balance")
    report["chain_snapshot"] = {"confirmed_balance_satoshis": balance, "utxo_count": len(utxos), "explorers_agree": True, "utxo_sum_agrees": True}
    secondary_first = json.loads((SOURCES / "blockstream-secondary-address.json").read_text())
    secondary_second = json.loads((SOURCES / "mempool-secondary-address.json").read_text())
    if secondary_first != secondary_second or secondary_first["address"] != SECONDARY_ADDRESS:
        raise ValueError("Secondary explorer snapshots disagree or contain the wrong address")
    secondary_balance = secondary_first["chain_stats"]["funded_txo_sum"] - secondary_first["chain_stats"]["spent_txo_sum"]
    report["secondary_chain_snapshot"] = {"address": SECONDARY_ADDRESS, "confirmed_balance_satoshis": secondary_balance, "explorers_agree": True, "scope_status": "Community-linked secondary target, not an independently authenticated reward promise"}
    report["latest_maintained_hint"] = {
        "screenshot_filename_date": "2026-07-12",
        "artifact": "maintained-hints__2026-07-12-official-hint.png",
        "provenance": "Community-maintained screenshot, not an independently authenticated chat export",
        "transcription": "My close friends have the best chance of solving it (a few tried). But they don't have the skills some of you do. NOTE: that is a hint.",
    }
    ARTIFACTS.joinpath("reproduction.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({name: value for name, value in report.items() if name != "phase0"}, indent=2))
    print("phase0:", grid["decoded"], "trailing bits:", grid["trailing_bits"])
    return report


def bounded_search():
    if not ARTIFACTS.joinpath("phase32-beaufort.txt").exists():
        raise ValueError("Run reproduce before the bounded search")
    speech = ARTIFACTS.joinpath("phase32-beaufort.txt").read_text().strip()
    message = ARTIFACTS.joinpath("phase32-checkerboard.txt").read_text().strip()
    clues = ("matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword")
    candidates = {
        "causality", PHASE32_PREIMAGE, "thematrixhasyou", "THEMATRIXHASYOU", "why", "neo", "you",
        "halfandbetterhalf", "half", "betterhalf", "fubcdora/lethingkymvpszjqwx.", "1141", "cp1141",
        "ourfirsthintisyourlastcommand", "hashthetext", "HASHTHETEXT", "ciaobellao", "sha256",
        speech, speech[1141:], speech[-len("ciaobellao"):], message, message.upper(),
        "".join(clues), "".join(clues) + "matrixsumlist",
        "matrixsumlistlastwordsbeforearchichoicethispassword", "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    }
    candidates.update(clues)
    for character_count in range(1, 33):
        candidates.add(speech[-character_count:])
    passwords = set()
    for candidate in candidates:
        passwords.add(candidate.encode())
        passwords.add(sha256_hex(candidate.encode()).encode())
    targets = {
        "phase32-inner": ARTIFACTS.joinpath("phase32-inner.b64").read_text(),
        "salphaseion-small": ARTIFACTS.joinpath("salphaseion-small.b64").read_text(),
        "cosmic-duality": ARTIFACTS.joinpath("cosmic-duality.b64").read_text(),
    }
    started = perf_counter()
    trials = 0
    padding_hits = []
    for target_name, blob in targets.items():
        for password in sorted(passwords):
            for digest in ("md5", "sha256"):
                trials += 1
                try:
                    plaintext = decrypt_salted(blob, password, digest)
                except ValueError:
                    continue
                password_fingerprint = sha256_hex(password)
                name = f"search-{target_name}-{digest}-{password_fingerprint[:16]}.bin"
                ARTIFACTS.joinpath(name).write_bytes(plaintext)
                padding_hits.append({"target": target_name, "digest": digest, "password_sha256": password_fingerprint, "status": "INCONCLUSIVE", "artifact": name, **payload_summary(plaintext)})
    report = {
        "scope": "Finite source-clue candidates only; no keyspace enumeration and no network requests",
        "candidate_rule": "Explicit page tokens, reproduced speech/message, speech suffix lengths 1..32; raw UTF-8 and lowercase SHA-256 hex passwords; MD5/SHA-256 legacy EVP KDFs",
        "passwords_per_target": len(passwords),
        "candidate_set_sha256": sha256_hex(b"\x00".join(sorted(passwords))),
        "trials": trials,
        "elapsed_seconds": round(perf_counter() - started, 4),
        "padding_valid_hits": padding_hits,
        "confirmed_solution": False,
        "status": "INCONCLUSIVE",
        "reason": "Padding-valid candidates require semantic structure or a target-address match; exhausting this finite set does not exclude other passwords",
    }
    ARTIFACTS.joinpath("bounded-search.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2))
    return report


def reproduce_audio():
    import subprocess

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    source = SOURCES / "maintained-decentraland-assets__puzzlepiece.mp3"
    output = ARTIFACTS / "decentraland-spectrogram.png"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", str(source),
        "-filter_complex", "pan=mono|c0=c0-c1,showspectrumpic=s=1600x500:legend=1:scale=log:color=intensity",
        "-frames:v", "1", str(output),
    ], check=True)
    report = {
        "source_sha256": sha256_hex(source.read_bytes()),
        "artifact": output.name,
        "transform": "Left channel minus right channel; logarithmic intensity spectrogram",
        "transcription": "48 41 53 48 54 48 45 54 45 58 54",
        "transcription_provenance": "Human/assistant visual reading of reproduced spectrogram; corroborated by maintained notebook",
        "decoded": bytes.fromhex("48 41 53 48 54 48 45 54 45 58 54").decode("ascii"),
        "status": "CONFIRMED",
    }
    ARTIFACTS.joinpath("audio-reproduction.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description="Offline, source-based GSMG puzzle reproduction")
    parser.add_argument("command", choices=("reproduce", "search", "audio"))
    arguments = parser.parse_args()
    if arguments.command == "reproduce":
        reproduce()
    elif arguments.command == "search":
        bounded_search()
    else:
        reproduce_audio()


if __name__ == "__main__":
    main()
