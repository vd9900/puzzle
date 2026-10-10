import json

from PIL import Image

from tools.instruction_graphs import ROOT, source, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle12"


def report():
    records = []
    for header, expected in [
        ("=== [11.12.2022 10:30:38 UTC-05:00] Jrk Bgrt", ".... That is very specific"),
        ("=== [11.12.2022 10:33:20 UTC-05:00] Jrk Bgrt", "If the puzzle is solved you'll see how scary specific that is"),
        ("=== [08.01.2023 23:52:11 UTC-05:00] Jrk Bgrt", "provided a very specific hint already."),
    ]:
        body, evidence = record_by_header(CREATOR, header)
        chat_body, chat_evidence = record_by_header(CHAT, header)
        if expected not in body or body != chat_body:
            raise ValueError("Cover-context attribution differs between archived exports")
        records.append({"creator_labeled_export": evidence, "full_transcript": chat_evidence, "short_public_quote": expected, "same_text": True, "exports_are_not_independent_authentication": True})
    cover = ROOT / "research/sources/maintained-hints__cosmic-duality-book.png"
    screenshot = ROOT / "research/sources/maintained-hints__2022-12-10-cosmic.png"
    with Image.open(cover) as image:
        cover_size = list(image.size)
    with Image.open(screenshot) as image:
        screenshot_size = list(image.size)
    return {
        "id": "C12-COVER-REFERENCE", "date": "2026-09-30", "status": "PROMISING",
        "hypothesis": "The archived cover image is a puzzle-relevant object for a visual yin-yang checkpoint rather than evidence for a guessed book-text cipher",
        "source_evidence": [source(cover), source(screenshot), source(CREATOR), source(CHAT)],
        "source_locations": ["research/sources/maintained-hints__cosmic-duality-book.png", "research/sources/maintained-hints__2022-12-10-cosmic.png", "research/evidence/cycle02/_work__creator_jrk.txt:663", "research/evidence/cycle02/_work__creator_jrk.txt:669", "research/sources/salphaseion.html:19"],
        "assumptions": ["Screenshot attachment thumbnail corresponds to preserved Cosmic Duality cover", "Creator's later barrystyle attribution refers to the prior cover/image contribution", "Visible yin-yang geometry is relevant to the checkpoint name rather than only thematic decoration"],
        "operation_order": ["locate screenshot attachment and attributed replies", "verify exact archived reaction and later attribution wording", "record visual features separately from any transformation", "retain missing correspondence rules"],
        "input": "Preserved cover and chat screenshot only", "output": "Source-attributed image-reference graph with no pixel decoding or text-cipher assumption",
        "confidence": "MEDIUM-HIGH for context attribution; LOW for mathematical construction",
        "records": records,
        "cover": {"source": source(cover), "image_size": cover_size, "visually_reviewed_title": "Cosmic Duality", "visual_observations": ["Two interlocking contrasting curved star fields", "A bright pale point in the upper warm-colored field", "A bright yellow/orange point in the lower blue/pale field"], "no_exact_star_count_claim": True, "no_source_authored_color_palette_inferred": True},
        "screenshot": {"source": source(screenshot), "image_size": screenshot_size, "visible_attachment_contributor": "barrystyle", "visible_attachment_filename": "image_2022-12-11_07-09-14.png", "visible_dates": ["December10 2022", "December11 2022"], "original_attachment_not_preserved_under_that_filename": True, "thumbnail_cover_identification_is_visual_not_byte_identity": True},
        "source_connections": ["The primary page heading independently names Cosmic Duality", "February23 2023 decoded hint names yinyang after lastwordsbeforearchichoice", "January8 2023 creator-labeled text attributes a very specific prior hint to barrystyle"],
        "unknowns": ["No explicit attachment hash binds thumbnail to full preserved cover", "No exact spatial mapping to original14x14 image or25 events", "No rule mapping cover geometry to residual60/61 or faed570", "No verified placement after a particular container", "No page number or instruction to use book text"],
        "result": "Image relevance has stronger preserved attribution than an incidental title guess, but visual yin-yang and two bright points do not specify a decoding. Creator-attributed acknowledgement is not an authenticated solution or a book-text instruction.",
        "contradictions": ["Full transcript does not preserve attachment thumbnail metadata", "Later attribution names a contributor, not a specific file digest", "The color/geometry correspondence is currently qualitative only"],
        "next_test": "Source-constrained visual correspondence audit between the preserved cover, original image and color-wording hint. First establish what is actually shared and what mapping is absent; no arbitrary palettes, star counting, rotations or cipher expansion.",
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_image_variants": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "cover-reference.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "attributed_message_pairs": len(document["records"]), "visual_reference_provenance": "PRESERVED_CONTEXT_NOT_FILE_IDENTITY", "new_cryptographic_trials": 0}, indent=2))


if __name__ == "__main__":
    main()
