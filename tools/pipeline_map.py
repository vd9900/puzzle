#!/usr/bin/env python3
import json
from pathlib import Path

from tools.gsmg import ARTIFACTS, SOURCES, PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE, embedded_blobs, evp_bytes_to_key, parse_salted, textareas
from tools.research_common import CYCLE, fingerprint, source_record, write_once_json


def aes_entry(name, encoded, password, artifact, origin):
    salt, ciphertext = parse_salted(encoded)
    key, initialization_vector = evp_bytes_to_key(password, salt, "sha256")
    return {
        "stage": name, "status": "VERIFIED", "source": origin,
        "input_sha256": fingerprint(encoded.encode()), "input_encoding": "Base64; ASCII whitespace removed",
        "ciphertext_bytes": len(ciphertext), "ciphertext_sha256": fingerprint(ciphertext),
        "primitive": "AES-256", "mode": "CBC", "padding": "PKCS#7, 16-byte blocks",
        "kdf": "EVP_BytesToKey", "kdf_digest": "SHA-256", "kdf_iteration_count": 1,
        "kdf_formula": "D_i=SHA256(D_(i-1)||password||salt), D_0=empty; key=(D_1||D_2)[:32], IV=(D_1||D_2)[32:48]",
        "salt_hex": salt.hex(), "key_hex": key.hex(), "iv_hex": initialization_vector.hex(),
        "password_ascii": password.decode(), "password_bytes": len(password),
        "salt_handling": "8 bytes following literal Salted__; header is not ciphertext",
        "byte_ordering": "KDF/hash bytes consumed in emitted order; no integer reversal",
        "output": str(artifact.relative_to(SOURCES.parents[1])), "output_bytes": artifact.stat().st_size,
        "output_sha256": fingerprint(artifact.read_bytes()), "output_encoding": "raw bytes, preserve CRLF; Phase 3.2 contains non-UTF-8 symbols",
    }


def build_pipeline():
    baseline = json.loads((ARTIFACTS / "reproduction.json").read_text())
    small, large = textareas((SOURCES / "phase2.html").read_text())
    nested = embedded_blobs((ARTIFACTS / "phase3.txt").read_text())[0]
    stages = [{
        "stage": "phase0", "status": "VERIFIED", "source": source_record(SOURCES / "gsmg-puzzle.png"),
        "input": "14x14 dominant-cell color grid", "alphabet": "black/blue=1, white/yellow=0 (including near-white cell)",
        "transformation": "counterclockwise inward spiral, down first from upper left; 8-bit ASCII, MSB-first",
        "output": baseline["phase0"]["decoded"], "trailing_bits": baseline["phase0"]["trailing_bits"],
        "primitive": None, "password": None, "iv": None, "mode": None, "padding": None, "kdf": None, "salt": None, "iteration_count": None,
    }, {
        "stage": "phase1", "status": "LIKELY", "source": source_record(SOURCES / "theseedisplanted.html"),
        "verified": "Hidden password form exists; destination route fetched publicly",
        "not_replayed": "POST acceptance of documented lyric password", "password": "theflowerblossomsthroughwhatseemstobeaconcretesurface",
        "input_encoding": "browser form text", "output": "choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself",
        "primitive": "server verification, implementation UNKNOWN", "iv": None, "mode": None, "padding": None, "kdf": "UNKNOWN", "salt": "UNKNOWN", "iteration_count": "UNKNOWN",
    }]
    for name, encoded, preimage, filename, origin in (
        ("phase2", small, "causality", "phase2.txt", source_record(SOURCES / "phase2.html", "textarea:0")),
        ("phase3", large, PHASE3_PREIMAGE, "phase3.txt", source_record(SOURCES / "phase2.html", "textarea:1")),
        ("phase32", nested, PHASE32_PREIMAGE, "phase32.txt", source_record(ARTIFACTS / "phase3.txt", "embedded OpenSSL Base64 block")),
    ):
        entry = aes_entry(name, encoded, fingerprint(preimage.encode()).encode(), ARTIFACTS / filename, origin)
        entry["password_preimage"] = preimage
        entry["password_transform"] = "SHA-256 of exact UTF-8 preimage -> lowercase hex ASCII, no terminal newline"
        stages.append(entry)
    stages.extend([{
        "stage": "phase32_beaufort", "status": "VERIFIED", "input": "1539-byte encoded block after 'four for one.'", "source": source_record(ARTIFACTS / "phase32.txt"),
        "encoding": "Latin-1 characters re-encoded with cp273, giving a-z; cp1141 equivalence only for observed symbols",
        "primitive": "Beaufort over alphabet a-z", "password": "THEMATRIXHASYOU", "formula": "P_i=(K_i-C_i) mod 26; repeating key",
        "output": "research/artifacts/phase32-beaufort.txt", "output_payload_bytes": 1539, "iv": None, "mode": None, "padding": None, "kdf": None, "salt": None, "iteration_count": None,
    }, {
        "stage": "phase32_checkerboard", "status": "VERIFIED", "source": source_record(ARTIFACTS / "phase32.txt"), "input": "149 decimal digits",
        "encoding": "straddling checkerboard, blank columns/prefixes 1 and 4; alphabet fubcdora/lethingkymvpszjqwx.",
        "primitive": "variable-length prefix decoding", "output": baseline["phase32_classical_ciphers"]["checkerboard"]["message"],
        "round_trip": True, "password": None, "iv": None, "mode": None, "padding": None, "kdf": None, "salt": None, "iteration_count": None,
    }, {
        "stage": "decentraland_audio", "status": "VERIFIED", "source": source_record(SOURCES / "maintained-decentraland-assets__puzzlepiece.mp3"),
        "provenance_status": "ARCHIVED_PRIMARY, community copy not authenticated live parcel retrieval",
        "encoding": "MP3 stereo 44.1kHz", "transformation": "L-R -> spectrogram -> visually transcribed hex -> ASCII",
        "output": "HASHTHETEXT", "primitive": None, "password": None, "iv": None, "mode": None, "padding": None, "kdf": None, "salt": None, "iteration_count": None,
    }, {
        "stage": "salphaseion_route", "status": "VERIFIED", "input": SALPHASEION_PREIMAGE,
        "normalization": "title uppercase/alphanumeric, printed address preserving case, no spaces/punctuation/newline",
        "primitive": "SHA-256", "encoding": "UTF-8 input; lowercase hex path", "output": fingerprint(SALPHASEION_PREIMAGE.encode()),
        "source": source_record(SOURCES / "salphaseion.html"), "password": None, "iv": None, "mode": None, "padding": None, "kdf": None, "salt": None, "iteration_count": 1,
    }])
    for name in ("phase32-inner", "salphaseion-small", "cosmic-duality"):
        blob = (ARTIFACTS / f"{name}.b64").read_text()
        salt, ciphertext = parse_salted(blob)
        stages.append({"stage": name, "status": "UNKNOWN", "source": source_record(ARTIFACTS / f"{name}.b64"), "encoding": "VERIFIED OpenSSL Salted__ Base64 wrapper", "salt_hex": salt.hex(), "ciphertext_bytes": len(ciphertext), "ciphertext_sha256": fingerprint(ciphertext), "primitive": "HYPOTHESIS AES-256 by precedent", "mode": "HYPOTHESIS CBC", "padding": "HYPOTHESIS PKCS#7", "kdf": "HYPOTHESIS legacy EVP_BytesToKey", "kdf_digest": "UNKNOWN; prioritized SHA-256 and MD5", "kdf_iteration_count": "UNKNOWN; tests use 1 by precedent", "password": "UNKNOWN", "key": "UNKNOWN", "iv": "UNKNOWN (password/KDF-derived if hypothesis holds)", "byte_ordering": "HYPOTHESIS emitted digest order", "normalization": "UNKNOWN password normalization; Base64 whitespace removal VERIFIED"})
    stages.append({"stage": "salphaseion_text", "status": "UNKNOWN", "source": source_record(SOURCES / "salphaseion.html", "textarea:0"), "verified_clues": baseline["salphaseion"], "unresolved_segment_lengths": [91, 570], "note": "661 joined letters cross an inserted 104-bit matrixsumlist clue; split is structural, not yet a proven independent encryption boundary", "encoding": "ASCII a-i", "primitive": "UNKNOWN", "password": "UNKNOWN", "iv": None, "mode": "UNKNOWN", "padding": "UNKNOWN", "kdf": "UNKNOWN", "salt": None, "iteration_count": "UNKNOWN"})
    report = {"source_baseline": source_record(ARTIFACTS / "reproduction.json"), "complete_target_derivation": False, "stages": stages}
    write_once_json(CYCLE / "pipeline.json", report)
    print(json.dumps({"stages": len(stages), "statuses": {status: sum(stage["status"] == status for stage in stages) for status in ("VERIFIED", "LIKELY", "HYPOTHESIS", "UNKNOWN")}}, indent=2))
    return report


if __name__ == "__main__":
    build_pipeline()
