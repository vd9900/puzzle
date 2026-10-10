import json

from tools.carry_forward_ownership import mapped_literal
from tools.instruction_graphs import ROOT, source, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle21"
QUOTE_HEADER = "=== [04.08.2023 19:46:47 UTC-05:00] Jrk Bgrt"
QUOTE = '"Globally supporting my generation"'
NEXT_TEST = "Use only the frozen public primary-symbol partitions and instruction source maps to perform a whole-object accountability audit: label versus data roles of dbbi91, binary-label104, faed570 and the remaining z-delimited trailer. Determine whether any proposed instruction graph accounts for every source region without discarding unconsumed material or substituting a recognized prefix for a full output. No new routing, alphabet, period, hash input or cipher trial."


def report():
    preceding = ROOT / "research/artifacts/cycle21/author-message-role.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C21-AUTHOR-MESSAGE-ROLE" or "Globally supporting my generation" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen source-name task")
    body, creator_location = record_by_header(CREATOR, QUOTE_HEADER)
    original_body, chat_location = record_by_header(CHAT, QUOTE_HEADER)
    if body != original_body or body != QUOTE:
        raise ValueError("Unexpected original source-name quote")
    words = body[1:-1].split()
    initials = "".join(word[0] for word in words).upper()
    if len(words) != 4 or initials != "GSMG":
        raise ValueError("Fixed quote no longer matches expected source initials")
    path = ROOT / "research/sources/theseedisplanted.html"
    title = mapped_literal(path, "<title>GSMG Puzzle</title>", "PRIMARY_SOURCE_TITLE")
    image_domain_path = ROOT / "research/artifacts/cycle19/first-piece-domain-v2.json"
    image_domain = json.loads(image_domain_path.read_text())
    public_image = image_domain["image_ownership"]["source"]
    context_headers = (
        "=== [04.08.2023 18:10:26 UTC-05:00] Jerry",
        "=== [04.08.2023 18:21:03 UTC-05:00] Deleted Account",
        "=== [04.08.2023 18:29:05 UTC-05:00] Pomyk",
        QUOTE_HEADER,
        "=== [04.08.2023 20:10:41 UTC-05:00] ArchOptic",
    )
    context = []
    for header in context_headers:
        context_body, location = record_by_header(CHAT, header)
        context.append({"public_body": context_body, "record": location, "reply_target_metadata_preserved": False})
    evidence = [source(item) for item in (preceding, CREATOR, CHAT, path, image_domain_path)]
    evidence.append(public_image)
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:763", "research/evidence/cycle02/_work__chat_transcript.txt:21639", "research/sources/theseedisplanted.html:4", "research/sources/gsmg-puzzle.png", "research/artifacts/cycle19/first-piece-domain-v2.json"]
    interpretations = [
        {"id": "C21-NAME-MESSAGE-ASSOCIATION", "hypothesis": "Creator's exact four-word quote associates GSMG with an intended communicative meaning", "assumptions": ["The four ordinary initials are intended to match the public name", "Meaning association can frame the puzzle without being its technical operand"], "confidence": "HIGH exact initials/name correspondence; MEDIUM thematic intent", "contradictions": ["No sentence assigns the phrase to a ciphertext, hash or result", "The name association alone does not account for unresolved source data"]},
        {"id": "C21-NAME-COMMON-LABEL", "hypothesis": "The quote explains or playfully associates the public GSMG label without constraining the remaining construction", "assumptions": ["An acronym statement can be ordinary branding or commentary", "No hidden operation follows without an explicit consumer"], "confidence": "MEDIUM conservative label role; UNKNOWN puzzle consequence", "contradictions": ["Author says the puzzle speaks for him elsewhere", "Companion message suggests intentionally shared meaning", "A purely incidental label reading may under-explain repeated communicative wording"]},
        {"id": "C21-NAME-LITERAL-OPERAND", "hypothesis": "The quoted four-word phrase is a literal technical input for an unresolved stage", "assumptions": ["The statement's context implies an input assignment", "Exact argument normalization and destination would be supplied separately"], "confidence": "LOW; no authored assignment or consumer", "contradictions": ["Original quote does not say hash, input, output or enter", "Nearby preceding community messages are not an authenticated reply binding", "A recognizable acronym is not a full construction or an expansion license"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["cross-check fixed quoted body", "compare its four initials with primary source title", "retain label/meaning roles without an input assignment"],
        "input": "One exact public creator quote and source-title/image ownership labels",
        "output": "One finite source-name association, not a derived trial input or decoded solution",
        "next_test": NEXT_TEST,
    } for entry in interpretations]
    return {
        "id": "C21-SOURCE-NAME-ASSOCIATION", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "The fixed creator phrase and public name association identifies an intended message role in the puzzle construction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Only the exact four-word quote's natural initials are tested", "A public title/name association is not an instruction or complete derived output", "Context adjacency cannot recover missing reply references"],
        "operation_order": ["validate frozen task", "cross-check original quoted body in two exports", "compute one four-initial correspondence", "map exact primary source title", "reuse original-image ownership", "map five fixed context records without inferring reply scope", "compare three finite source-name roles"],
        "input": "Original quote, source title, preserved original-image ownership and fixed context",
        "output": "Exact GSMG initial/name correspondence and unresolved label/meaning/operand roles",
        "confidence": "HIGH exact quote/initials/primary title; UNKNOWN operative use",
        "original_quote": {"public_text": body, "creator_record": creator_location, "original_chat_record": chat_location, "matching_exports_are_not_independent_identity_authentication": True},
        "one_initial_correspondence": {"source_words": words, "initials": initials, "matches_primary_public_source_label": True, "no_alternative_word_order_or_initial_encoding": True},
        "primary_title": title,
        "image_owner_reused": {"source": source(image_domain_path), "original_image": public_image, "visible_source_title_label": "GSMG.IO", "no_image_text_or_identifier_extraction": True},
        "context": context,
        "no_authored_literal_input_or_consumer_assignment": True,
        "hypotheses": hypotheses,
        "result": "Exact creator-attributed Globally supporting my generation has four natural initials GSMG, matching the primary source title and original-image public name. Five fixed context records preserve preceding community hash/dbbi questions and later branding question, but no reply target or operand assignment. Meaning/name association is a real source-bound correspondence; it does not select a technical argument, consumer, alphabet, route or complete output.",
        "contradictions": ["Four-initial equality does not account for full encoded data", "The creator quote is not an explicit instruction to use its text", "Communicative meaning does not close source/argument/consumer interfaces"],
        "next_test": NEXT_TEST,
        "search_space": {"original_quoted_creator_bodies_cross_checked": 1, "source_words": 4, "initial_correspondences": 1, "exact_primary_titles": 1, "fixed_context_records": 5, "declared_name_roles": 3},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_acronym_variants": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "source-name-association.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "fixed_initials_match_public_name": True, "literal_operand_assigned": False, "new_acronym_variants": 0}, indent=2))


if __name__ == "__main__":
    main()
