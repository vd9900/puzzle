import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from tools.gsmg import ARTIFACTS, SOURCES, base58check_decode, candidate_addresses


CYCLE = ARTIFACTS / "cycle02"
VOCABULARY = tuple("the this that you your life sum remainder equation inherent programming puzzle eventuality anomaly private key password enter inner matrix before choice half better funds live return source prime basics yellow blue yin yang causality safenet luna hsm give it just one second heisenberg uncertainty principle last words hashthetext theseedisplanted".split())
COMMON_TRIGRAMS = ("the", "and", "ing", "her", "ere", "ent", "tha", "nth", "was", "eth", "for", "hat", "you", "his", "thi")


def fingerprint(payload):
    return hashlib.sha256(payload).hexdigest()


def write_once_json(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text() != encoded:
        previous = path.read_bytes()
        historical = path.with_name(f"{path.stem}.{fingerprint(previous)[:16]}{path.suffix}")
        if not historical.exists():
            historical.write_bytes(previous)
    path.write_text(encoded)


def source_record(path, locator=None):
    resolved = Path(path)
    return {"path": str(resolved.relative_to(SOURCES.parents[1])), "sha256": fingerprint(resolved.read_bytes()), "locator": locator}


def score_plaintext(payload):
    text = payload.decode("latin-1")
    letters = "".join(character.lower() for character in text if character.isascii() and character.isalpha())
    words = re.findall(r"[a-z]+", text.lower())
    word_hits = [word for word in words if word in VOCABULARY]
    hits = {word: letters.count(word) for word in VOCABULARY if len(word) >= 4 and word in letters}
    occupied = set()
    for word in sorted(hits, key=len, reverse=True):
        for match in re.finditer(re.escape(word), letters):
            occupied.update(range(match.start(), match.end()))
    trigram_hits = sum(letters.count(trigram) for trigram in COMMON_TRIGRAMS)
    printable = sum(byte in (9, 10, 13) or 32 <= byte < 127 for byte in payload)
    alphabetic = sum(65 <= byte <= 90 or 97 <= byte <= 122 for byte in payload)
    score = {
        "bytes": len(payload), "printable_ratio": round(printable / max(1, len(payload)), 6),
        "alphabetic_ratio": round(alphabetic / max(1, len(payload)), 6),
        "longest_printable_run": max((len(match) for match in re.findall(rb"[\x20-\x7e]+", payload)), default=0),
        "language_score": round(trigram_hits / max(1, len(letters) - 2), 6),
        "dictionary_coverage": round(len(occupied) / max(1, len(letters)), 6),
        "whole_word_hits": word_hits,
        "puzzle_vocabulary_hits": hits,
        "score_limit": "Heuristic based on fixed common trigrams/puzzle vocabulary; not proof of English or a correct transformation",
    }
    return score


def structural_checks(payload):
    structures = []
    for label, signature in (("openssl_salted", b"Salted__"), ("png", b"\x89PNG\r\n\x1a\n"), ("zip", b"PK\x03\x04"), ("gzip", b"\x1f\x8b"), ("pdf", b"%PDF-")):
        if payload.startswith(signature):
            structures.append(label)
    stripped = payload.strip()
    if stripped.startswith((b"{", b"[")):
        try:
            json.loads(stripped)
            structures.append("valid_json")
        except (ValueError, UnicodeError):
            pass
    wifs = []
    for match in re.finditer(rb"(?<![1-9A-HJ-NP-Za-km-z])[5KL][1-9A-HJ-NP-Za-km-z]{50,51}(?![1-9A-HJ-NP-Za-km-z])", payload):
        try:
            decoded = base58check_decode(match.group().decode("ascii"))
        except ValueError:
            continue
        if decoded[0] == 128 and (len(decoded) == 33 or len(decoded) == 34 and decoded[-1] == 1):
            structures.append("valid_wif")
            wifs.append(decoded[1:33])
    return structures, wifs


def target_checks(payload):
    structures, candidates = structural_checks(payload)
    if len(payload) == 32:
        candidates.append(payload)
    if re.fullmatch(rb"[0-9a-fA-F]{64}", payload.strip()):
        candidates.append(bytes.fromhex(payload.strip().decode("ascii")))
    result = []
    from tools.gsmg import SECONDARY_ADDRESS, TARGET_ADDRESS
    for candidate in sorted(set(candidates)):
        try:
            addresses = candidate_addresses(candidate)
        except ValueError:
            continue
        result.append({"candidate_sha256": fingerprint(candidate), "addresses": addresses, "main_target_match": TARGET_ADDRESS in addresses.values(), "secondary_target_match": SECONDARY_ADDRESS in addresses.values()})
    return {"structures": structures, "candidate_checks": result, "target_match": any(check["main_target_match"] or check["secondary_target_match"] for check in result)}


def index_of_coincidence(sequence):
    counts = Counter(sequence)
    return sum(count * (count - 1) for count in counts.values()) / max(1, len(sequence) * (len(sequence) - 1))
