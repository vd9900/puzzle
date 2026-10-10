import json
from datetime import datetime

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header
from tools.speech_operand_audit import mapped_speech_anchor


OUTPUT = ROOT / "research/artifacts/cycle16"
CREATOR_HEADER = "=== [19.09.2024 02:20:23 UTC-05:00] Jrk Bgrt"
PRIOR_HEADER = "=== [18.09.2024 15:29:23 UTC-05:00] Szymon Szczawiński"
SECONDARY_HEADER = "=== [07.09.2023 00:32:26 UTC-05:00] Deleted Account"


def literal_source(path, document, literal):
    if document.count(literal) != 1:
        raise ValueError("Expected one exact public source anchor")
    start = document.index(literal)
    return {"source": source(path), "literal": literal, **text_location(document, start, start + len(literal))}


def antecedents():
    phase3 = ROOT / "research/artifacts/phase3.txt"
    raw = phase3.read_bytes()
    archived = ROOT / "research/sources/maintained-phase2-assets__phase3.txt"
    if raw != archived.read_bytes():
        raise ValueError("Earlier decoded fixture differs from its preserved archive")
    document = raw.decode()
    paragraphs = document.split("\r\n\r\n")
    if len(paragraphs) < 4 or not paragraphs[3].startswith("Phase 3.2 is ciphered"):
        raise ValueError("Unexpected earlier public paragraph boundaries")
    source_maps = [literal_source(phase3, document, literal) for literal in [
        "The thinker's 1name", "(of humanity)", "Definitely look into his works might you have time.",
        "I just passed a cheshire cat", "The fundamental limit to the precision",
    ]]
    walk = ROOT / "research/sources/community-README.md"
    walkthrough = walk.read_text()
    identifications = [literal_source(walk, walkthrough, literal) for literal in [
        "Jacque Fresco quote:", "The future is ours to direct.", "3. Heisenberg uncertainty principle",
    ]]
    phase32 = ROOT / "research/artifacts/phase32.txt"
    later = phase32.read_bytes()[:443].decode("ascii")
    nearby = [literal_source(phase32, later, literal) for literal in [
        "I've been waiting for you.", "... am I here? Wake up, you...",
    ]]
    return {
        "earlier_phase3_fixture_matches_preserved_archive": True,
        "earlier_primary_source_maps": source_maps,
        "secondary_thinker_identifications": identifications,
        "nearby_phase32_public_source_maps": nearby,
        "above_is_not_a_unique_document_or_paragraph_selector": True,
        "phase3_does_not_name_the_thinker_explicitly": True,
        "phase32_intro_does_not_name_a_wiseman": True,
        "no_new_decoding_or_trial_input": True,
    }


def creator_attribution():
    creator_body, creator_location = record_by_header(CREATOR, CREATOR_HEADER)
    chat_body, chat_location = record_by_header(CHAT, CREATOR_HEADER)
    prior_body, prior_location = record_by_header(CHAT, PRIOR_HEADER)
    if creator_body != chat_body:
        raise ValueError("Creator export and original chat disagree")
    if not creator_body.startswith("I simply liked Jacque's ideas a lot."):
        raise ValueError("Unexpected creator-attributed thematic wording")
    if "REINSERTING THE PRIME BASICS" not in prior_body:
        raise ValueError("Unexpected original prior-message context")
    elapsed = (datetime.fromisoformat(chat_location["archived_utc_timestamp"]) - datetime.fromisoformat(prior_location["archived_utc_timestamp"])).total_seconds()
    return {
        "creator_record": creator_location, "original_chat_record": chat_location,
        "exact_public_body": creator_body,
        "both_preserved_bodies_match": True,
        "classification": "CREATOR_ATTRIBUTED_THEMATIC_PREFERENCE_NOT_EXPLICIT_PUZZLE_INSTRUCTION",
        "prior_community_speech_record": prior_location,
        "elapsed_since_prior_community_speech_seconds": int(elapsed),
        "reply_target_metadata_preserved": False,
        "does_not_confirm_wiseman_antecedent_or_value140": True,
        "does_not_supply_Architect_word_count_or_consumer": True,
    }


def alternative_attribution():
    body, location = record_by_header(CHAT, SECONDARY_HEADER)
    document = CHAT.read_text()
    start = location["character_span_zero_based_half_open"][0]
    literal = "wiseman above hinted at - Mr Satoshi himself is that wiseman"
    if not body.startswith(literal):
        raise ValueError("Unexpected fixed community alternative")
    return {
        "record": location,
        "short_public_assertion": literal,
        "assertion_source_location": text_location(document, start, start + len(literal)),
        "classification": "COMMUNITY_SPECULATION_NOT_CREATOR_AUTHENTICATION",
        "claimed_value140_link_is_not_tested_or_adopted": True,
        "no_external_source_or_numeric_extraction": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle16/speech-operand-audit.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C16-SPEECH-OPERAND-AUDIT" or "wiseman-above clause" not in frozen["next_test"]:
        raise ValueError("Unexpected preceding frozen task")
    evidence = [source(path) for path in (
        ROOT / "research/artifacts/phase3.txt", ROOT / "research/sources/maintained-phase2-assets__phase3.txt",
        ROOT / "research/artifacts/phase32.txt", ROOT / "research/artifacts/phase32-beaufort.txt",
        ROOT / "research/sources/community-README.md", CHAT, CREATOR, preceding,
    )]
    locations = [
        "research/artifacts/phase3.txt:1", "research/artifacts/phase3.txt:5",
        "research/artifacts/phase32.txt:1", "research/artifacts/phase32.txt:3",
        "research/sources/community-README.md:262",
        "research/evidence/cycle02/_work__creator_jrk.txt:1027",
        "research/evidence/cycle02/_work__chat_transcript.txt:73142",
        "research/evidence/cycle02/_work__chat_transcript.txt:34520",
    ]
    hypotheses = []
    for suffix, hypothesis, confidence, assumptions, contradictions in [
        ("DEICTIC-JACQUE", "Wiseman-above most plausibly recalls the earlier thinker/work/humanity riddle and Jacque-themed project aspiration", "MEDIUM as a thematic referent; LOW as executable construction", ["Above means an earlier puzzle stage", "Community thinker identification is correct", "Creator thematic preference is related, not a direct reply confirmation"], ["The primary riddle does not name Jacque", "Creator comment does not identify the wiseman or140", "No exact operation, word count or matrixsumlist consumer"]),
        ("DEICTIC-NEARBY", "Above instead refers locally to the Architect or another nearby speaker rather than the earlier thinker", "LOW without an explicit named nearby person", ["Above is spatial/local rather than stage-relative", "Nearby dialogue role supplies an unnamed speaker referent"], ["Neither nearby introductory paragraph names a wiseman", "Primary decoding yields no source identity binding", "No literal instruction joins this referent to last-word selection"]),
        ("DEICTIC-COMMUNITY-ALTERNATIVE", "The preserved Satoshi interpretation is a competing community antecedent, not an authorized construction rule", "HIGH for attribution distinction; UNKNOWN for intended referent", ["A community assertion remains secondary unless independently source-bound", "Numerical resemblance is not sufficient author evidence"], ["No creator-attributed confirmation of this exact antecedent", "The claim supplies its own numerical/source interpretation", "No independently authored link to matrixsumlist,60-letter residual or faed570"]),
    ]:
        hypotheses.append({
            "id": "C16-" + suffix, "status": "INCONCLUSIVE", "hypothesis": hypothesis,
            "source_evidence": evidence, "source_locations": locations,
            "assumptions": assumptions,
            "operation_order": ["map above-reference in verified speech", "map earlier source positions and secondary names", "compare creator attribution and chronology", "retain only thematic referents without constructing a trial"],
            "input": "Existing public speech reference and preserved earlier puzzle paragraphs/messages",
            "output": "An attributed semantic referent hypothesis, not a new numerical operation",
            "confidence": confidence, "contradictions": contradictions,
            "next_test": "Reuse the existing first-hint attribution and primary boundary maps in a finite symbolic operand-ownership preflight; compare label/data roles and require a source-authored graph edge before binding any hash consumer",
        })
    creator = creator_attribution()
    return {
        "id": "C16-DEICTIC-SOURCE-AUDIT", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "The wiseman-above speech reference fixes an earlier source object for the unresolved instruction graph",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Stage order is known, but above-reference scope is not", "Community names and alternative interpretations are secondary", "Creator-labeled transcript records are not signed author authentication"],
        "operation_order": ["validate frozen source-reference task", "map eight exact earlier/secondary anchors and two nearby anchors", "cross-check one creator body in two exports", "record one competing community claim", "compare three finite referents without extraction"],
        "input": "Existing public phase3/phase3.2 source text, decoded speech and preserved chat",
        "output": "Source-position, attribution and scope audit of a deictic reference",
        "confidence": "HIGH for exact source/chronology; MEDIUM for thematic Jacque referent; UNKNOWN for construction",
        "speech_reference": mapped_speech_anchor("wisemanabovehintedat"),
        "antecedents": antecedents(), "creator_attribution": creator,
        "alternative_attribution": alternative_attribution(), "hypotheses": hypotheses,
        "result": "Earlier phase3 explicitly names a thinker/work/humanity role, with Jacque identified only in secondary exposition. Creator-attributed September19 2024 preference for Jacque's ideas supports a thematic reading but does not identify wiseman/140 or an operation; it is39060 seconds after a prior community speech quote without reply metadata. Local Architect and community Satoshi alternatives remain unbound. No source/count/consumer, matrixsumlist/residual/faed join or new numerical operation is established.",
        "contradictions": ["Above is not a unique paragraph/stage selector", "Thematic endorsement is not an extraction instruction", "Value140 clause supplies no defined operand or format", "Community alternative is not creator authentication"],
        "next_test": "Use the existing public source/dependency maps for a finite symbolic operand-ownership preflight across matrixsumlist, lastwordsbeforearchichoice, thispassword and hash instructions. Compare object labels versus operations without executing any new transform; retain unknown source/count/consumer edges. Reuse, do not repeat, the completed first-hint/last-command attribution audit; its January2021 echo is Deleted Account, not creator-authenticated.",
        "review_correction": "First snapshot's prospective next-task wording incorrectly called the January2021 echo creator-attributed and overlapped existing first-hint scope work. The snapshot is preserved; current v2 next task reuses those results rather than repeating the audit.",
        "search_space": {"earlier_primary_anchors": 5, "secondary_name_anchors": 3, "nearby_primary_anchors": 2, "creator_records_cross_checked": 1, "prior_context_records": 1, "community_alternative_records": 1, "finite_semantic_hypotheses": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "deictic-source-audit-v2.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({
        "status": document["status"], "creator_thematic_record_cross_checked": True,
        "creator_confirms_exact_antecedent": False,
        "unique_source_count_consumer": False, "new_cryptographic_trials": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
