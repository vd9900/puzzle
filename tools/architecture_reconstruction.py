import base64
import hashlib
import json
import math
import re
from datetime import datetime

from tools.instruction_graphs import HEADER, ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle22"
NEXT_TEST = "Perform one static coordinate-interface test on the frozen 25-event/25-prime-marker correspondence: compare the actual original-image row/column domain and symbol multiplicities with the source-keyed 5x5 square domain, preserving all event identities and duplicate positions. Accept a direct lookup-table architecture only if a source-defined, complete, single-valued bijection exists without rescaling, modular reduction, ranking, guessed alphabets or discarded events. Reuse original coordinates and square; do not generate trial text or run a cipher. If no direct bijection exists, close that direct edge and retain only an explicitly missing coordinate-conversion interface."
CLAIM_HEADERS = (
    "=== [11.06.2025 19:30:31 UTC-05:00] Sycorax",
    "=== [25.06.2025 07:49:43 UTC-05:00] Sycorax",
)


def fingerprint(payload):
    return hashlib.sha256(payload).hexdigest()


def envelope(encoded):
    compact = b"".join(encoded.split())
    payload = base64.b64decode(compact, validate=True)
    if payload[:8] != b"Salted__" or len(payload) < 32:
        raise ValueError("Expected a complete public OpenSSL salted envelope")
    ciphertext = payload[16:]
    if len(ciphertext) % 16:
        raise ValueError("Public ciphertext is not a multiple of 16 bytes")
    return {
        "base64_characters": len(compact), "blob_bytes": len(payload),
        "header_bytes": 8, "salt_bytes": 8, "salt_hex": payload[8:16].hex(),
        "ciphertext_bytes": len(ciphertext), "ciphertext_sha256": fingerprint(ciphertext),
        "blob_sha256": fingerprint(payload), "sixteen_byte_blocks": len(ciphertext) // 16,
        "if_CBC_PKCS7_plaintext_length_range": [len(ciphertext) - 16, len(ciphertext) - 1],
        "mode_and_KDF_not_identified_by_header": True,
    }


def literal_location(document, literal, offset=0, original_document=None):
    positions = [match.start() for match in re.finditer(re.escape(literal), document)]
    if len(positions) != 1:
        raise ValueError("Expected one exact public literal in its source record")
    position = positions[0]
    location = text_location(original_document, offset + position, offset + position + len(literal)) if original_document is not None else text_location(document, position, position + len(literal))
    return location | {
        "absolute_character_span_zero_based_half_open": [offset + positions[0], offset + positions[0] + len(literal)],
    }


def claim_audit(plaintext):
    transcript = CHAT.read_text()
    claims = []
    for header in CLAIM_HEADERS:
        body, location = record_by_header(CHAT, header)
        result = re.search(r'^Result:\n"([a-z]+)"$', body, re.M)
        if result is None or result.group(1) != plaintext:
            raise ValueError("Dated community result differs from frozen public Bifid object")
        start = location["character_span_zero_based_half_open"][0] + result.start(1)
        claims.append({
            "record": location, "speaker_role": "COMMUNITY_CLAIM_NOT_CREATOR_INSTRUCTION",
            "body_sha256": fingerprint(body.encode()), "result_matches_frozen_full_output": True,
            "full_result_location": text_location(transcript, start, start + len(plaintext)),
            "recognized_prefix_location": text_location(transcript, start, start + 7),
            "remaining_body_location": text_location(transcript, start + 7, start + len(plaintext)),
            "exact_role_phrases": [
                {"text": phrase, **literal_location(body, phrase, location["character_span_zero_based_half_open"][0], transcript)}
                for phrase in ("Bifid Ciphertext (All the characters of \"faed\"):",
                               "Bifid Period: 570 (Length of ciphertext)",
                               "A potential find in first seven characters. Can't make this shit up!!:",
                               "And then you have the rest to be solved:",
                               "I have not gotten much farther then this.")
            ],
            "body_consumer_algorithm_supplied": False,
        })
    exact_hits = list(re.finditer(re.escape(plaintext), transcript))
    header_matches = list(HEADER.finditer(transcript))
    hit_headers = []
    for match in exact_hits:
        preceding = next(header for header in reversed(header_matches) if header.start() < match.start())
        hit_headers.append(preceding.group())
    expected_headers = [CLAIM_HEADERS[0],
                        "=== [15.06.2025 10:47:26 UTC-05:00] X",
                        "=== [16.06.2025 13:00:56 UTC-05:00] X",
                        "=== [16.06.2025 13:23:34 UTC-05:00] X",
                        CLAIM_HEADERS[1],
                        "=== [07.01.2026 21:42:01 UTC-05:00] Dasharo",
                        "=== [18.01.2026 10:42:04 UTC-05:00] X",
                        "=== [07.06.2026 15:09:38 UTC-05:00] gnosis"]
    if hit_headers != expected_headers:
        raise ValueError("Frozen full result has unexpected preserved transcript references")
    references = [{"header": header, "source": source(CHAT),
                   **text_location(transcript, match.start(), match.end()),
                   "creator_instruction": False}
                  for header, match in zip(hit_headers, exact_hits)]
    first_time = datetime.fromisoformat(claims[0]["record"]["archived_utc_timestamp"])
    second_time = datetime.fromisoformat(claims[1]["record"]["archived_utc_timestamp"])
    caveat_body, caveat_location = record_by_header(CHAT, "=== [11.06.2025 20:15:17 UTC-05:00] Sycorax")
    caveat = "this could entirely be a coincidence of course and have absolutely nothing to do with the puzzle"
    return {
        "claims": claims, "full_output_occurrences": len(exact_hits),
        "all_eight_exact_references": references,
        "secondary_layout_replacement": {
            "header": expected_headers[1], "full_output_line": references[1]["line_one_based"],
            "replaces_primary_dbbi91_matrix104_faed570_with_Bifid570": True,
            "matrixsumlist_label_omitted_in_this_community_presentation": True,
            "not_an_authorized_source_edit_or_execution_order": True,
        },
        "identical_body_repost": claims[0]["body_sha256"] == claims[1]["body_sha256"],
        "repost_delay_seconds": int((second_time - first_time).total_seconds()),
        "reposts_are_not_independent_discoveries": True,
        "explicit_discovery_caveat": {"record": caveat_location, "text": caveat,
                                     **literal_location(caveat_body, caveat, caveat_location["character_span_zero_based_half_open"][0], transcript)},
        "C04_description_names_repost_date_C10_already_maps_earlier_discovery": True,
        "no_new_statistical_test_or_body_cipher": True,
    }


def prefix_boundary(dependencies, prefix_length=7):
    if [entry["output_index_zero_based"] for entry in dependencies] != list(range(570)):
        raise ValueError("Frozen Bifid output-coordinate map is incomplete")
    groups = {"prefix": set(), "body": set()}
    coordinate_sets = {"prefix": set(), "body": set()}
    for entry in dependencies:
        region = "prefix" if entry["output_index_zero_based"] < prefix_length else "body"
        for dependency in entry["dependencies"]:
            index = dependency["faed_index_zero_based"]
            groups[region].add(index)
            coordinate = (index, dependency["source_coordinate"])
            if coordinate in coordinate_sets[region]:
                raise ValueError("Frozen map repeats a source-coordinate dependency")
            coordinate_sets[region].add(coordinate)
    if coordinate_sets["prefix"] & coordinate_sets["body"]:
        raise ValueError("Source coordinates are consumed twice across the output boundary")
    if coordinate_sets["prefix"] | coordinate_sets["body"] != {(index, axis) for index in range(570) for axis in ("row", "column")}:
        raise ValueError("Frozen map does not preserve all source coordinates")
    return {
        "recognized_prefix_length": prefix_length, "body_length": 570 - prefix_length,
        "source_symbols_shared_across_cut": sorted(groups["prefix"] & groups["body"]),
        "prefix_coordinate_count": len(coordinate_sets["prefix"]),
        "body_coordinate_count": len(coordinate_sets["body"]),
        "all1140_source_coordinates_preserved": True,
        "seven_letter_cut_is_not_an_entire_source_symbol_boundary": bool(groups["prefix"] & groups["body"]),
        "no_primary_separator_or_Bifid_block_boundary_at_output7": True,
        "boundary_claim_is_community_recognition_not_author_instruction": True,
    }


def object_record(name, payload, kind, locations, derivation, upstream, consumers, loss, unexplained, authored=False):
    return {
        "id": name, "exact_object": {"sha256": fingerprint(payload), "length": len(payload),
                                      "unit": "ASCII characters" if kind != "binary" else "bits", "alphabet": "".join(sorted(set(payload.decode("ascii"))))},
        "type": kind, "encoding": "ASCII" if kind != "binary" else "symbolic bits in frozen order",
        "source_locations": locations, "derivation": derivation,
        "creator_authenticated": False, "primary_authored_source": authored,
        "independently_reproducible": True, "upstream_dependencies": upstream,
        "known_downstream_consumers": consumers, "contains": unexplained,
        "preserves": "Exact object fingerprint and source-position dependencies retained",
        "destroys_or_omits": loss, "currently_unexplained_information": unexplained,
    }


def factors(size):
    return [[divisor, size // divisor] for divisor in range(2, math.isqrt(size) + 1) if size % divisor == 0]


def exact_tiling(text):
    if not text:
        raise ValueError("Exact tiling requires a nonempty public object")
    lengths = {1}
    for first, second in factors(len(text)):
        lengths.update((first, second))
    successful = [length for length in sorted(lengths) if length < len(text) and text[:length] * (len(text) // length) == text]
    return {"length": len(text), "proper_divisor_tile_lengths_checked": sorted(length for length in lengths if length < len(text)),
            "exact_repeating_tile_lengths": successful,
            "statistical_periodicity_not_estimated": True,
            "failure_only_rejects_exact_repeated_blocks_not_interleavings_or_cipher_periods": True}


def architecture_hypotheses(evidence, locations):
    readings = [
        ("C22-ARCH-SERIAL", "Full Bifid data feeds a specified matrix-derived transform, then a local hash/container/answer-hash chain", ["Bifid is intended data, not only recognition", "Missing matrix transform and input ownership have exact future definitions"],
         ["raw dbbi -> frozen square", "faed570 -> Bifid570", "Bifid570 -> UNKNOWN metadata transform", "UNKNOWN selected object -> first hash -> SMALL", "UNKNOWN SMALL answer -> answer hash -> UNKNOWN destination"],
         "MEDIUM full-object reversibility; LOW downstream ordering", ["Full/suffix/parity/password and numeric-route realizations already failed", "No source places inner AES immediately after Bifid", "Seven-letter boundary is not a primary or complete-coordinate boundary"]),
        ("C22-ARCH-COORDINATE", "Prime/color and matrixsumlist define coordinate metadata for a reversible lookup or permutation; Bifid is a parallel recognition/control channel", ["Metadata has an exact original domain and destination", "Recognition and data channels need not be serial"],
         ["original image <-> 25 event identities", "dbbi plus binary104 -> 25 aligned prime markers and residual60", "matrixsumlist -> UNKNOWN coordinate metadata", "metadata plus preserved data -> UNKNOWN consumer", "raw dbbi plus faed570 -> parallel Bifid object"],
         "MEDIUM parallel structural dependency; LOW direct coordinate conversion", ["25 binary event labels do not automatically define a 25-symbol permutation", "14x14 image and 5x5 square have different coordinate domains", "Existing mask/routing/sum realizations are closed negatives"]),
        ("C22-ARCH-SPEECH-SELECTOR", "Matrix-related metadata selects an exact object from the edited speech; lastwords/thispassword bind the local container, while Bifid is a separate branch", ["The speech is operational as well as thematic", "A source-bound selector and Architect boundary exist but are not yet identified"],
         ["outer envelope -> speech and numeric siblings", "image/primes -> UNKNOWN selection metadata", "metadata plus speech -> UNKNOWN last-word object", "lastwords -> thispassword -> first hash -> SMALL", "SMALL answer -> answer hash -> UNKNOWN destination"],
         "MEDIUM local grammar and named speech relationship; UNKNOWN selector", ["No literal choice or word-count binding", "Semantic mention order is not execution order", "Does not yet explain full faed/Bifid as required input"]),
        ("C22-ARCH-MULTIDOOR", "Inner and SMALL are distinct stage objects reached through separate doors and may converge only at a later object", ["Repeated-door wording permits multiple entrances", "A later convergence exists without a supplied input join"],
         ["main recovered path -> inner envelope", "audio/source-return path -> SalPhaseIon -> SMALL", "two unresolved outputs -> UNKNOWN join or independent continuation", "Cosmic separate heading -> UNKNOWN destination"],
         "HIGH distinct containers; MEDIUM alternative-door architecture", ["Distinct salts do not prove independent plaintexts", "No verified join, output equality or convergence operator", "A strict main-path serialization could still visit both containers"]),
        ("C22-ARCH-RECOGNITION", "Prime/color and Bifid are source-recognition or construction checks; the remaining executable path is earlier-source recall plus the local hash/container skeleton", ["Some intermediate data has a recognition rather than next-input role", "Body563 need not be immediately consumed by an AES stage"],
         ["image/primes -> structural recognition", "raw dbbi plus faed570 -> full reversible Bifid recognition object", "firsthint/lastcommand -> UNKNOWN earlier operand", "selected earlier object -> first hash -> SMALL -> answer hash -> UNKNOWN destination"],
         "MEDIUM conservative separation of verified and unknown edges; LOW intended recognition-only role", ["Creator does not authorize discarding body563", "A deliberate 570-letter object could remain operative data", "Recognition-only model under-explains residual60 and matrixsumlist unless they receive other roles"]),
    ]
    return [{"id": identifier, "status": "INCONCLUSIVE", "hypothesis": hypothesis,
             "source_evidence": evidence, "source_locations": locations, "assumptions": assumptions,
             "operation_order": order, "input": "Frozen public source objects, dependency maps and envelope metadata",
             "output": "A typed partial architecture, with unknown edges retained rather than executed",
             "confidence": confidence, "contradictions": contradictions, "next_test": NEXT_TEST}
            for identifier, hypothesis, assumptions, order, confidence, contradictions in readings]


def report():
    paths = {name: ROOT / relative for name, relative in {
        "checkpoint": "research/artifacts/cycle21/whole-object-accountability.json",
        "maps": "research/artifacts/cycle10/instruction-graphs-v3.json",
        "boundary": "research/artifacts/cycle15/label-boundary-audit.json",
        "frame": "research/artifacts/cycle15/frame-object-audit.json",
        "bifid": "research/artifacts/cycle04/bifid-evidence.json",
        "pipeline": "research/artifacts/cycle02/pipeline.json",
        "occurrences": "research/artifacts/cycle10/instruction-occurrences-v3.jsonl",
        "primary": "research/sources/salphaseion.html",
        "phase32": "research/artifacts/phase32.txt",
        "speech": "research/artifacts/phase32-beaufort.txt",
        "checkertext": "research/artifacts/phase32-checkerboard.txt",
        "inner": "research/artifacts/phase32-inner.b64",
        "small": "research/artifacts/salphaseion-small.b64",
        "cosmic": "research/artifacts/cosmic-duality.b64",
    }.items()}
    documents = {name: json.loads(paths[name].read_text()) for name in ("checkpoint", "maps", "boundary", "frame", "bifid", "pipeline")}
    if documents["checkpoint"]["id"] != "C21-WHOLE-OBJECT-ACCOUNTABILITY":
        raise ValueError("Unexpected preceding whole-object checkpoint")
    maps = documents["maps"]
    regions = {entry["name"]: entry for entry in documents["boundary"]["regions"]}
    primary = paths["primary"].read_bytes().decode("utf-8")
    raw_objects = {}
    for name in ("dbbi91", "matrixsumlist", "faed570", "small-container-first-part", "small-container-second-part"):
        start, end = regions[name]["character_span_zero_based_half_open"]
        raw_objects[name] = "".join(primary[start:end].split()).encode("ascii")
    dependencies = maps["derived_source_maps"]["source_bifid"]
    plaintext = documents["bifid"]["plaintext"]
    if len(plaintext) != 570 or fingerprint(plaintext.encode()) != dependencies["output_sha256"]:
        raise ValueError("Frozen full Bifid output and mapped fingerprint differ")
    residual_branch = next(entry for entry in maps["derived_source_maps"]["branches"] if entry["mask"] == 1017)
    residual = "".join(entry["symbol"] for entry in residual_branch["residual_source_map"]).encode()
    if fingerprint(residual) != residual_branch["residual_sha256"]:
        raise ValueError("Frozen residual source map and fingerprint differ")
    marker_raw_characters = sum(len(entry["token"]) for entry in residual_branch["prime_marker_source_map"])
    if marker_raw_characters + len(residual) != len(raw_objects["dbbi91"]):
        raise ValueError("Prime/residual complementary source accounting differs")
    raw_phase32 = paths["phase32"].read_bytes()
    paragraphs = raw_phase32.split(b"\r\n\r\n")
    if [len(paragraph) for paragraph in paragraphs] != [332, 107, 1539, 149, 145, 130]:
        raise ValueError("Unexpected exact Phase3.2 paragraph boundaries")
    envelopes = {name: envelope(paths[name].read_bytes()) for name in ("inner", "small", "cosmic")}
    if b"".join(paragraphs[5].split()) != b"".join(paths["inner"].read_bytes().split()):
        raise ValueError("Inner envelope is not the exact published paragraph5 object")
    if raw_objects["small-container-first-part"] + raw_objects["small-container-second-part"] != b"".join(paths["small"].read_bytes().split()):
        raise ValueError("SMALL fixture differs from both exact primary fragments")
    for name in ("inner", "small", "cosmic"):
        previous = next(entry for entry in documents["pipeline"]["stages"] if entry["stage"] == {"inner": "phase32-inner", "small": "salphaseion-small", "cosmic": "cosmic-duality"}[name])
        if envelopes[name]["ciphertext_bytes"] != previous["ciphertext_bytes"] or envelopes[name]["salt_hex"] != previous["salt_hex"]:
            raise ValueError("Public envelope does not match frozen pipeline metadata")
    evidence = [source(path) for path in paths.values()] + [source(CHAT)]
    locations = ["research/sources/salphaseion.html:17", "research/artifacts/phase32.txt:1", "research/evidence/cycle02/_work__chat_transcript.txt:122237", "research/evidence/cycle02/_work__chat_transcript.txt:124626", "research/artifacts/cycle10/instruction-graphs-v3.json"]
    speech = paths["speech"].read_bytes().removesuffix(b"\n")
    checkertext = paths["checkertext"].read_bytes().removesuffix(b"\n")
    marker_bits = "".join(entry["bit"] for entry in maps["derived_source_maps"]["continuous_frame"]["source_map"]).encode()
    binary_bits = raw_objects["matrixsumlist"].translate(bytes.maketrans(b"ab", b"01"))
    inventory = [
        object_record("dbbi91", raw_objects["dbbi91"], "source-letter-stream", [regions["dbbi91"]], "Exact primary source slice", [], ["frozen prime parse", "source-derived Bifid square"], "None until a tokenizer or first-occurrence projection is applied", "Order and repeated letters beyond square's first occurrences", True),
        object_record("matrix104", binary_bits, "binary", [regions["matrixsumlist"]], "a=0,b=1; existing 13-octet decoding retained", [], ["matrixsumlist label", "continued prime-marker positions89/97"], "Label-only use omits continued-marker role", "Which matrix, sum operation, list type and consumer", True),
        object_record("matrixsumlist", b"matrixsumlist", "instruction-or-object-label", [regions["matrixsumlist"]], "Frozen direct ASCII octets", ["matrix104"], [], "Does not instantiate a matrix or numeric list", "Metadata, operand label or operation remains unbound"),
        object_record("frame25", marker_bits, "binary", [source(paths["frame"])], "Frozen event/prime correspondence; near-white semantic1 is assumed", ["original image", "dbbi91", "matrix104"], ["conditional alignment control"], "Binary labels alone omit row/column, color identity and octet identity", "25 identities are not a 25-letter permutation"),
        object_record("residual60", residual, "source-letter-stream", [source(paths["maps"])], "Frozen mask1017 nonprime source-position projection", ["dbbi91", "prime parse"], [], "Drops31 raw characters unless complementary marker/token map is retained", "No verified selector, numeric list or next-input role"),
        object_record("faed570", raw_objects["faed570"], "source-letter-stream", [regions["faed570"]], "Exact primary source slice", [], ["frozen Bifid transformation"], "None", "Whether Bifid is intended and whether other roles exist", True),
        object_record("Bifid570", plaintext.encode(), "derived-letter-stream", [source(paths["bifid"]), source(paths["maps"])], "Reuse source-keyed square and full period570; no new decoding", ["dbbi91", "faed570"], [], "None with frozen square/period: exact inverse already verified", "Complete body consumer unknown"),
        object_record("btcseed", plaintext[:7].encode(), "recognized-prefix", [source(paths["bifid"])], "Community-recognized first7 letters", ["Bifid570"], [], "Projection omits563 output letters; no authored discard", "Recognition is not a downstream object assignment"),
        object_record("Bifid-body563", plaintext[7:].encode(), "derived-letter-stream", [source(paths["bifid"])], "Community recognition cut, not a primary delimiter", ["Bifid570"], [], "Projection omits7 letters; preserved full object remains authoritative", "No exact same-size known consumer"),
        object_record("speech1539", speech, "edited-narrative-text", [source(paths["speech"])], "Frozen CP273/Beaufort transformation", ["outer plaintext paragraph2"], ["mapped words/references; selector unknown"], "None with observed substitution alphabet and repeating key", "Selection, count, input ownership"),
        object_record("checker149", paragraphs[3], "decimal-prefix-code", [{"source": source(paths["phase32"]), "byte_span_zero_based_half_open": [1990, 2139]}], "Exact raw paragraph3", ["outer plaintext"], ["frozen straddling checkerboard"], "None under fixed observed codebook", "Codebook ancestry and wider instruction role", True),
        object_record("checkertext91", checkertext, "decoded-public-text", [source(paths["checkertext"])], "Frozen checkerboard inverse already verified; text not reproduced here", ["checker149"], [], "None with frozen codebook", "Same91 length as dbbi is not an identity"),
        object_record("SMALL", b"".join(paths["small"].read_bytes().split()), "salted-envelope-base64", [regions["small-container-first-part"], regions["small-container-second-part"]], "Join64+64 source characters; exclude separately decoded enter40", ["SalPhaseIon primary source"], [], "Formatting-only whitespace removed; clue enter retained separately", "Secondary label; local input, plaintext and destination unknown", True),
        object_record("inner-envelope", b"".join(paragraphs[5].split()), "salted-envelope-base64", [{"source": source(paths["phase32"]), "byte_span_zero_based_half_open": [2292, 2422]}], "Exact outer plaintext paragraph5, whitespace-only canonicalization", ["outer plaintext"], [], "Only CRLF wrapping removed", "Password bytes, KDF, mode, IV and plaintext unknown", True),
    ]
    dimensions = [{"object": entry["id"], "size": entry["exact_object"]["length"], "unit": entry["exact_object"]["unit"], "factor_pairs": factors(entry["exact_object"]["length"]), "factorization_is_not_a_transform_license": True} for entry in inventory]
    compatibility = [
        {"producer": "faed570", "consumer": "Bifid570", "status": "VERIFIED_TRANSFORM", "reason": "570 -> 570, exact frozen reversible coordinate map; square/period supplied"},
        {"producer": "dbbi91", "consumer": "checkertext91", "status": "REJECTED_IDENTITY", "reason": "Equal length but different exact fingerprints, alphabet and source provenance"},
        {"producer": "matrix104", "consumer": "original 14x14 grid", "status": "REJECTED_IDENTITY", "reason": "104 bits are13 ASCII octets, not196 source cells; no authored matrix reshape"},
        {"producer": "frame25", "consumer": "5x5 keyed square", "status": "UNKNOWN_CONVERSION", "reason": "Equal cardinality; binary labels/14x14 coordinates are not25 distinct square symbols"},
        {"producer": "residual60", "consumer": "faed570 or Bifid570", "status": "UNKNOWN_CONVERSION", "reason": "570=9*60+30, not a complete rectangular placement with60 intact symbols per side"},
        {"producer": "Bifid-body563", "consumer": "known fixed-size public object", "status": "NO_EXACT_LENGTH_PEER", "reason": "563 is prime; no listed object has that length, but variable-length consumers remain possible"},
        {"producer": "Bifid570 or Bifid-body563", "consumer": "raw32-byte AES key or80-byte ciphertext", "status": "REJECTED_DIRECT_IDENTITY", "reason": "570/563 ASCII bytes differ from32/80 bytes; conversion would be a separate unknown edge"},
        {"producer": "any public text", "consumer": "password API or hash input", "status": "TYPE_COMPATIBLE_NOT_BOUND", "reason": "Variable-length byte input accepts all sizes; compatibility provides no input-selection evidence"},
        {"producer": "SHA256 digest", "consumer": "raw AES256 key", "status": "TYPE_COMPATIBLE_NOT_BOUND", "reason": "32 bytes fits; preceding verified stages instead use64-character hex as KDF password"},
        {"producer": "inner-envelope", "consumer": "SMALL", "status": "REJECTED_IDENTICAL_CONTAINER", "reason": "Both128 base64/96 blob/80 ciphertext, but distinct salt/blob/ciphertext fingerprints"},
    ]
    if raw_objects["dbbi91"] == checkertext or envelopes["inner"]["blob_sha256"] == envelopes["small"]["blob_sha256"]:
        raise ValueError("Expected equal-size objects have become identical")
    author_hits = []
    for line in paths["occurrences"].read_text().splitlines():
        occurrence = json.loads(line)
        if occurrence["term"] in ("bifid", "bifid-prefix") and any(name in occurrence["source"]["path"] for name in ("creator_jrk", "salphaseion.html")):
            author_hits.append(occurrence)
    return {
        "id": "C22-ARCHITECTURAL-RECONSTRUCTION", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "A typed dependency architecture, not adjacency or size coincidence, connects existing public intermediate objects",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Frozen transformations are implementation evidence, not intended-construction proof", "Variable-length hash/password inputs cannot be inferred from dimensions", "Terminal material remains UNKNOWN and outside current analysis"],
        "operation_order": ["inventory exact frozen objects", "compare information-preserving versus lossy edges", "verify exact source-envelope ownership", "distinguish equal-size objects", "map full community output claims and recognized cut", "compare five finite partial architectures"],
        "input": "Existing public source bytes, frozen maps, stage metadata and two dated community output posts",
        "output": "14 fingerprinted public objects,10 typed interfaces,4 discriminating experiments and5 partial architectures",
        "confidence": "HIGH exact source/size/type distinctions; UNKNOWN missing operand-to-consumer edges",
        "object_inventory": inventory, "dimensions": dimensions, "typed_compatibility": compatibility,
        "envelope_metadata": envelopes, "Bifid_claims": claim_audit(plaintext),
        "Bifid_boundary": prefix_boundary(dependencies["coordinate_source_map"]),
        "exact_object_tiling": {"full_Bifid": exact_tiling(plaintext), "body": exact_tiling(plaintext[7:])},
        "Bifid_score_and_parity_reused": {"source": source(paths["bifid"]), "score": documents["bifid"]["score"], "parity": documents["bifid"]["parity"], "no_statistical_or_period_search": True},
        "square_projection_reused": {
            "source": source(paths["maps"]), "key_square": dependencies["key_square"],
            "first_occurrences": dependencies["keyword_first_occurrences"],
            "unique_observed_source_letters": 9, "raw_keyword_length": 91,
            "source_prefix13_suffices_for_same_square_after_conventional_alphabet_append": True,
            "preserves_first_occurrence_order_not_multiplicity_or_later_order": True,
            "j_merged_or_omitted_by_25_symbol_Bifid_convention": True,
            "not_a_26_letter_free_permutation": True,
        },
        "event_identity_domain_reused": {
            "source": source(paths["frame"]), "events": documents["frame"]["image"]["events"],
            "full_event_domain": "25 ordered color/row/column/spiral/octet tuples, not merely25 bits",
            "bit_projection_is_not_the_complete_event_object": True,
            "prime_markers": maps["derived_source_maps"]["continuous_frame"]["source_map"],
        },
        "primary_or_creator_exact_Bifid_term_hits_reused": author_hits,
        "dimension_accounting": {"dbbi_raw": 91, "dbbi_logical_tokens": 83, "prime_tokens_removed": 23,
                                 "raw_characters_removed": 31, "two_character_be_tokens": 8, "residual": 60,
                                 "binary_label_symbols": 104, "label_ascii_octets": 13,
                                 "markers_from_dbbi": 23, "markers_from_binary_label": 2,
                                 "full_output": 570, "prefix_plus_body": [7, 563], "Bifid_half": 285,
                                 "shared_speech_Bifid_factor": 19, "speech_Bifid_ratio_reduced": [27, 10]},
        "uninstantiated_nodes": [
            {"id": "first-SHA-input", "source": "first shabef/firsthint relation", "type": "UNKNOWN selected text/bytes", "length": None},
            {"id": "answer-SHA-input", "source": "shabefanstoo", "type": "UNKNOWN answer/representation", "length": None},
            {"id": "hash-digest", "source": "SHA256 operator inferred from preserved mapping", "type": "32-byte digest or64-hex password are distinct", "length": None},
            {"id": "terminal-object", "source": "No recovered object", "type": "UNKNOWN; outside current public text analysis", "length": None},
        ],
        "experiments": [
            {"id": "C22-EQUAL-SIZE-IDENTITY", "hypothesis": "The equal96-byte envelopes or equal91-letter objects are literally the same recovered object", "input": "Exact published fragments and frozen fixtures", "expected_observable": "Matching normalized fingerprints", "falsification_condition": "Any distinct normalized byte", "result": "REJECTED: inner/SMALL salt, blob and ciphertext differ; dbbi/checkertext differ", "graph_effect": "Remove identity edges; do not exclude equal plaintexts or later cross-stage relationships"},
            {"id": "C22-PREFIX-BOUNDARY", "hypothesis": "The seven-letter cut is a primary-authored or complete source-symbol boundary", "input": "570 frozen coordinate dependencies and two dated exact full-output records", "expected_observable": "Authored boundary or disjoint complete source symbols", "falsification_condition": "Cut shares source-symbol coordinates and only community recognition supplies boundary", "result": "REJECTED narrow promotion: source symbols3/288 straddle the cut; both posts are one identical community repost", "graph_effect": "Retain full570 object; prefix recognition/body interface remains unbound, not an authored split"},
            {"id": "C22-DIRECT-CONSUMER-TYPES", "hypothesis": "Exact dimensions directly identify matrix, lookup, raw key or ciphertext consumers", "input": "14 frozen objects and10 finite typed comparisons", "expected_observable": "Complete same-domain binding or a supplied reversible conversion", "falsification_condition": "Different type/size or missing coordinate-domain conversion", "result": "Direct104-to196 grid and570/563-to32/80 byte identities fail;25-to25 lookup remains missing conversion", "graph_effect": "Keep variable-length inputs possible but not evidence; isolate coordinate interface as the next discriminator"},
            {"id": "C22-EXACT-REPEATED-BLOCK", "hypothesis": "The complete Bifid output or its body is an exact repetition of a shorter whole block", "input": "Frozen570-letter object and its recognized563-letter body", "expected_observable": "A proper-divisor prefix tiles every symbol exactly", "falsification_condition": "No proper-divisor prefix tiles the whole object", "result": "REJECTED only exact repeated-block construction; statistical periodicity and forced parity remain separate", "graph_effect": "No repeated-tile edge supplies an exact smaller consumer; no statistical or cipher-period search"},
        ],
        "hypotheses": architecture_hypotheses(evidence, locations),
        "result": "Known paths branch rather than establish a single serial graph. Same-size containers and91-letter objects are distinct. Full Bifid570 preserves all1140 source coordinates, but seven-letter recognition splits symbols3/288 and supplies no authored body consumer. Eight exact transcript references include a community rewrite omitting matrixsumlist, not a primary edit. A ten-interface type analysis separates identities, variable-length compatibility and missing conversions. Neither object is an exact repeated tile. Five finite architectures remain; no new cipher, password, normalization or statistical search.",
        "contradictions": ["No finite architecture has a verified missing operand/consumer edge", "Factorization and variable-input compatibility do not establish a construction", "Full-object accountability does not require immediate next-stage consumption"],
        "next_test": NEXT_TEST,
        "search_space": {"public_object_records": 14, "typed_interfaces": 10, "public_envelopes": 3, "exact_full_output_references": 8, "detailed_discovery_reposts": 2, "frozen_coordinate_dependencies": 570, "finite_architectures": 5, "discriminating_experiments": 4},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_Bifid_decodes": 0,
        "external_requests": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "architecture-reconstruction-v3.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "objects": len(document["object_inventory"]), "typed_interfaces": len(document["typed_compatibility"]), "architectures": len(document["hypotheses"]), "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
