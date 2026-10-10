#!/usr/bin/env python3
import json
from pathlib import Path

from tools.research_common import CYCLE, fingerprint


def update_ledger():
    research = CYCLE.parents[1]
    ledger = research / "candidates.jsonl"
    existing = {}
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            entry = json.loads(line)
            existing[entry["id"]] = entry
    specifications = [
        ("C02-BASELINE", "Revalidate unchanged known image/AES/classical/audio pipeline", None, "CONFIRMED", "All four requested commands completed; 16 baseline tests passed; no final target key", "high for intermediate stages, none for final solution", "python3 tools/gsmg.py reproduce && python3 tools/gsmg.py search && python3 tools/gsmg.py audio && python3 -m unittest discover -s tests -v", "Known source-derived stages should reproduce byte-for-byte before new hypotheses", ["research/architecture.md", "research/artifacts/reproduction.json", "research/artifacts/audio-reproduction.json"]),
        ("C02-CORPUS", "Index every original corpus file and locate missing linked PR research", "corpus-index.json", "CONFIRMED", "93 original files indexed; 2765 traceable evidence hits; 12 separate PR evidence files added without modifying original sources", "high for inventory; parsed chat authors/dates unauthenticated", "python3 -m tools.corpus_index index && python3 -m tools.corpus_index montage", "Ordering/normalization clues may already exist; inspect source assertions before guessing", ["research/sources/manifest.json", "research/evidence/cycle02/manifest.json", "research/artifacts/cycle02/corpus-evidence.jsonl"]),
        ("C02-SAL-PROFILE", "Treat the 91/570 structural split separately", "salphaseion-profile.json", "CONFIRMED", "91 and 570 letters with different marginal frequencies/IC; joined length 661; cipher and key roles remain unknown", "high for measurements, moderate for separate-cipher interpretation", "python3 -m tools.analyze_salphaseion", "The matrixsumlist binary run occurs between these two literal segments; do not destroy that boundary", ["research/sources/salphaseion.html"]),
        ("C02-INNER-TEXT", "Source-text transformations and SHA/MD5 representations as passphrases", "inner-search-results.json", "INCONCLUSIVE", "29484 trials, 113 padding-valid outputs, no recognized structure or target match", "high negative for precisely enumerated readable/direct-key family only", "python3 -m tools.derive_inner_aes plan && python3 -m tools.derive_inner_aes run", "Earlier stages explicitly hash exact text; case/whitespace/digest representations are plausible normalization dimensions", ["research/artifacts/cycle02/inner-search-plan.json", "research/artifacts/cycle02/C02-INNER-TEXT-bef2940d741e7f7c.jsonl"]),
        ("C02-SAL-COORDINATES", "Constrained digit/checkerboard/routes/prime-mask/grid-pair transforms", "sal-experiment-results.json", "INCONCLUSIVE", "10644 transformations; no independent semantic/downstream confirmation; arbitrary text-like checkerboard output rejected as proof", "high for reproducible results, low for actual cipher-family assignment", "python3 -m tools.salphaseion_experiments plan && python3 -m tools.salphaseion_experiments run", "Adjacent numeric segments, known checkerboard, prime/zero hints and matrixsumlist justify these finite alternatives", ["research/artifacts/cycle02/sal-experiment-plan.json", "research/artifacts/cycle02/sal-experiments.jsonl"]),
        ("C02-PRIME-MARKERS", "Optional be digraphs at prime positions repeat original grid colors", "prime-markers.json", "PROMISING", "1024 tokenizations; max 20/24 ordinary-color prefix; off-white=1 expands mask 1017 to 23/25 special-color prefix with 2 unconsumed bits. No 24/24 or 25/25 full match. 10000 seeded shuffles per frame reach at most 5 prefix bits", "high for literal partial cross-artifact match, unproven intent/downstream decoding", "python3 -m tools.prime_markers --shuffles 10000", "Prime and yellow/blue hints point directly at this reproducible constrained alignment; no arbitrary ciphertext modifications", ["research/sources/gsmg-puzzle.png", "research/sources/salphaseion.html", "research/evidence/cycle02/_work__chat_transcript.txt"]),
        ("C02-JOINT-MOD9", "Joint clue-keyed columnar/mod9/coordinate decoding then AES", "joint-results.json", "INCONCLUSIVE", "3240 decode forms, 14460 unique passwords, 86760 AES trials; 370 padding hits, zero recognized structure/target matches", "high for fixed-space negative; cipher structure remains hypothesis", "python3 -m tools.joint_derivation plan && python3 -m tools.joint_derivation run", "13-character/38-character clue lengths fit the two blocks; combine hypotheses and validate by downstream AES instead of English fragments", ["research/artifacts/cycle02/joint-plan.json", "research/artifacts/cycle02/joint-decodings.jsonl", "research/artifacts/cycle02/joint-aes.jsonl"]),
        ("C02-PRIME-GAP-SUMS", "Literal nonprime gap sum lists -> password representations", "prime-gap-results.json", "INCONCLUSIVE", "12 parse/mapping/tail sum lists, 567 unique passwords, 3402 AES trials; 12 padding hits, no structure/target matches", "high for tested finite family, low for interpreting sumlist", "python3 -m tools.prime_gap_sums plan && python3 -m tools.prime_gap_sums run", "Prime scaffold gives deterministic gaps and matrixsumlist suggests addition; tail handling is explicit", ["research/artifacts/cycle02/prime-gap-plan.json", "research/artifacts/cycle02/prime-gap-aes.jsonl"]),
        ("C02-PAIRED-SUMSTREAM", "dbbi row/column matrix sums remove faed mod9 stream", "paired-results.json", "INCONCLUSIVE", "24 sum streams, 3456 decode forms, 8856 unique passwords, 53136 AES trials; 235 padding hits, zero structure/target matches", "high for fixed family only; key/payload role unproven", "python3 -m tools.paired_digit_derivation plan && python3 -m tools.paired_digit_derivation run", "Paired page layout and 7x13 dimensions suggest a key/payload relationship; sum-stream hypothesis tests that relation directly", ["research/artifacts/cycle02/paired-plan.json", "research/artifacts/cycle02/paired-aes.jsonl"]),
        ("C02-RESIDUAL-COORDINATES", "Exact 60-letter residue interpreted as 3x3 ternary coordinates", "coordinate-results.json", "INCONCLUSIVE", "388 decode forms, 1164 unique passwords, 6984 AES trials; 25 padding hits, zero recognized structures or target matches", "high for precisely bounded negative, actual residual encoding remains unknown", "python3 -m tools.residual_coordinates plan && python3 -m tools.residual_coordinates run", "Nine symbols support 3x3 coordinates; exact 60 length yields 120 coordinate digits / 40 three-coordinate output symbols", ["research/artifacts/cycle02/coordinate-plan.json", "research/artifacts/cycle02/coordinate-aes.jsonl"]),
        ("C02-INDEPENDENT-BTC", "Verify public claimed keys with two EC/address implementations", "independent-btc.json", "REJECTED", "Both candidate keys fail both scoped addresses in compressed/uncompressed form; implementations agree", "high for rejecting these direct candidates", "python3 -m tools.verify_btc", "An address match, not key plausibility, is the required final verifier", ["research/artifacts/issue108-md5.bin", "tools/verify_btc.py"]),
        ("C02-LEDGER-AUDIT", "Recompute every logged AES trial and score", "ledger-audit.json", "CONFIRMED", "29961 unique passwords, 179766 AES trials, 755 padding hits; all keys/IVs/salts/plaintexts/scores/gates and summary counts reproduce", "high for accounting/reproducibility, not evidence of exhaustive puzzle search", "python3 -m tools.audit_cycle", "Summary counts are meaningful only after validating the detailed ledgers against actual source ciphertext", ["research/artifacts/cycle02/ledger-audit.json"]),
        ("C02-NEXT-ZEROED-RESIDUAL", "Literal zero replacement on unchanged prime residuals, then known checkerboard", "next-zeroed-residual-plan.json", "UNTESTED", "Plan only: 180 decode forms, 120 strict parse failures, 180 unique derived passwords, 1080 planned AES trials; no AES results yet", "moderate source support, low confidence in intended transform", "python3 -m tools.plan_zeroed_residual", "Prime markers, zeroed-out hint and verified checkerboard motivate replacing one of nine symbols with zero rather than deleting it; invalid duplicate-symbol alphabet excluded", ["research/artifacts/cycle02/next-zeroed-residual-plan.json", "research/evidence/cycle02/_work__creator_jrk.txt:627", "research/artifacts/cycle02/prime-markers.json"]),
    ]
    appended = 0
    with ledger.open("a") as output:
        for identifier, description, artifact, status, result, confidence, command, reasoning, sources in specifications:
            evidence_path = CYCLE / artifact if artifact else None
            if evidence_path:
                document = json.loads(evidence_path.read_text())
            else:
                document = {}
            details = "Passwords/derived KEY/IV/salt/padding/plaintext/score/downstream tests are in linked detailed per-candidate ledgers, not inferred from summary statements"
            if status == "UNTESTED":
                details = "Exact planned forms, parse failures, passwords and parameter bounds are linked; KEY/IV/padding/plaintext/score/downstream results have not been computed"
            entry = {"id": identifier, "description": description, "source_evidence": sources, "reasoning": reasoning, "transformation": description, "search_space": {key: document[key] for key in ("search_space", "unique_passwords", "trials", "total_trials", "aes_trials", "decode_trials", "decode_forms", "trials_by_family", "segments", "summary") if key in document}, "status": status, "result": result, "confidence": confidence, "reproduction_command": command, "artifact": None if evidence_path is None else str(evidence_path.relative_to(research.parent)), "artifact_sha256": None if evidence_path is None else fingerprint(evidence_path.read_bytes()), "date": "2026-09-30", "candidate_details": details}
            if identifier in existing:
                if existing[identifier] != entry:
                    revised = dict(entry)
                    revised["id"] = identifier + ":" + fingerprint(json.dumps(entry, sort_keys=True).encode())[:16]
                    revised["supersedes"] = identifier
                    if revised["id"] not in existing:
                        output.write(json.dumps(revised, sort_keys=True) + "\n")
                        appended += 1
                continue
            output.write(json.dumps(entry, sort_keys=True) + "\n")
            appended += 1
    print(f"Appended {appended} hypothesis records to {ledger}")


if __name__ == "__main__":
    update_ledger()
