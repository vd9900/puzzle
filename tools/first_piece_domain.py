import json
import re
from urllib.parse import urlsplit

from PIL import Image

from tools.instruction_graphs import ROOT, source, text_location, write_artifact
from tools.selector_evidence import CHAT, CREATOR, record_by_header


OUTPUT = ROOT / "research/artifacts/cycle19"
MANIFEST = ROOT / "research/sources/manifest.json"
PRIMARY_PAGES = ("theseedisplanted.html", "phase2.html", "salphaseion.html")
IMAGE_NAMES = ("gsmg-puzzle.png", "privatekeys-puzzle.png", "community-puzzle.png")
SECONDARY_ANCHORS = (
    ("community-README.md", "![puzzle image](./puzzle.png)"),
    ("community-README.md", "## 1. https://gsmg.io/puzzle"),
    ("community-README.md", "## 2. https://gsmg.io/theseedisplanted"),
    ("community-README.md", "![theseedisplanted.png](./theseedisplanted.png)"),
    ("community-README.md", "Go to the first puzzle piece (https://gsmg.io/puzzle) and hash the text there."),
    ("maintained-README.md", "![puzzle image](./puzzle.png)"),
    ("maintained-README.md", "## Phase 0 - The Bunny Image"),
    ("maintained-README.md", "Using everything we have so far, it points us back to the original image to hash the text on the image, which then\nleads us to SalPhaseIon using:"),
    ("privatekeys-gsmg.html", '<p><img src="https://privatekeys.pw/images/puzzles/gsmg-puzzle.png" class="w-50" alt="GSMG Puzzle"></p>'),
    ("privatekeys-gsmg.html", '<li><a href="https://gsmg.io/puzzle">Original page</a></li>'),
)
NEXT_TEST = "Inspect only the preserved original PNG container structure: chunk types, validated CRCs, any textual-chunk presence and terminal-byte coverage. Determine whether a metadata-text source actually exists before treating HASHTHETEXT as a PNG metadata instruction. Do not decode pixels, QR symbols or new trial text."


def exact_anchor(path, literal):
    document = path.read_text()
    if document.count(literal) != 1:
        raise ValueError("Expected one fixed source-domain anchor")
    start = document.index(literal)
    return {"source": source(path), "literal": literal, **text_location(document, start, start + len(literal))}


def is_initial_url(value):
    parsed = urlsplit(value)
    return parsed.hostname in ("gsmg.io", "www.gsmg.io") and parsed.path.rstrip("/") == "/puzzle"


def capture_domain():
    manifest = json.loads(MANIFEST.read_text())
    matches = [name for name, entry in manifest.items() if is_initial_url(entry["url"]) or is_initial_url(entry["final_url"])]
    if matches != ["gsmg-puzzle.png"]:
        raise ValueError("Unexpected captured initial-source domain")
    name = matches[0]
    entry = manifest[name]
    path = ROOT / "research/sources" / name
    payload = path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n") or entry["content_type"] != "image/png":
        raise ValueError("Initial response is not the recorded PNG")
    if len(payload) != entry["bytes"] or source(path)["sha256"] != entry["sha256"]:
        raise ValueError("Initial response differs from preserved manifest")
    copies = []
    for image_name in IMAGE_NAMES:
        image_path = ROOT / "research/sources" / image_name
        image_entry = manifest[image_name]
        if image_path.read_bytes() != payload or source(image_path)["sha256"] != image_entry["sha256"]:
            raise ValueError("An original-image copy differs")
        with Image.open(image_path) as picture:
            dimensions = list(picture.size)
        copies.append({"source": source(image_path), "dimensions": dimensions, "byte_identical": True})
    return {
        "manifest_source": source(MANIFEST), "manifest_entries_considered": len(manifest),
        "initial_url_capture_names": matches, "capture": {"source": source(path), **entry},
        "png_signature_verified": True, "copies": copies,
        "initial_html_response_preserved": False,
        "capture_is_not_proof_of_2019_or_2020_HTTP_response_type": True,
        "a_browser_image_document_is_not_preserved_creator_HTML": True,
        "no_external_state_snapshot_opened": True,
    }


def page_inventory():
    pages = []
    for name in PRIMARY_PAGES:
        path = ROOT / "research/sources" / name
        document = path.read_text()
        assets = [{"markup": match.group(), **text_location(document, match.start(), match.end())}
                  for match in re.finditer(r'<img\b[^>]*>', document, re.I)]
        headings = [{"text": match.group(1).strip(), **text_location(document, match.start(1), match.end(1))}
                    for match in re.finditer(r'<h1\b[^>]*>(.*?)</h1>', document, re.I | re.S)]
        comments = [{"markup": match.group(), **text_location(document, match.start(), match.end())}
                    for match in re.finditer(r'<!--.*?-->', document, re.S)]
        pages.append({
            "source": source(path), "body_image_references": assets, "headings": headings,
            "comments": comments, "textarea_count": len(re.findall(r'<textarea\b', document, re.I)),
            "is_initial_puzzle_response": False,
        })
    return {
        "pages": pages,
        "shared_bunny_comment_is_theme_not_a_unique_source_binding": True,
        "eight_asset_references_belong_to_later_theseedisplanted_page": True,
        "asset_reference_order_not_rearranged_or_executed": True,
        "distinct_headings_do_not_define_hidden_navigation_edges": True,
    }


def creator_pointer():
    header = "=== [13.10.2019 13:38:53 UTC-05:00] Jrk Bgrt"
    body, location = record_by_header(CREATOR, header)
    original_body, original_location = record_by_header(CHAT, header)
    if body != "Gsmg.io/puzzle" or body != original_body:
        raise ValueError("Unexpected original creator-attributed resource pointer")
    return {
        "literal": body, "creator_record": location, "original_chat_record": original_location,
        "matching_exports_are_not_independent_identity_authentication": True,
        "a_resource_pointer_does_not_select_an_image_region": True,
        "January_warning_does_not_explicitly_repeat_this_URL": True,
    }


def image_ownership():
    path = ROOT / "research/artifacts/cycle18/final-reference-audit-v2.json"
    frozen = json.loads(path.read_text())["visible_regions"]
    original = source(ROOT / "research/sources/gsmg-puzzle.png")
    if frozen["original_image_source"] != original:
        raise ValueError("Unexpected frozen original-image source")
    return {
        "frozen_source": source(path), "source": original,
        "regions": [region | {"owner": original, "authored_region_selection": False}
                    for region in frozen["human_visual_region_locators"]],
        "all_three_regions_belong_to_one_response": True,
        "rectangles_are_approximate_human_locators_not_extraction_masks": True,
        "grid_is_a_subobject_not_the_whole_original_response": True,
        "no_identifier_or_QR_decoding_or_use": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle18/door-topology.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C18-DOOR-TOPOLOGY" or "primary-source domain audit" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen first-piece task")
    anchors = [exact_anchor(ROOT / "research/sources" / name, literal) for name, literal in SECONDARY_ANCHORS]
    paths = [preceding, MANIFEST, CHAT, CREATOR, ROOT / "research/artifacts/cycle18/final-reference-audit-v2.json"]
    paths += [ROOT / "research/sources" / name for name in (*IMAGE_NAMES, *PRIMARY_PAGES, "community-README.md", "maintained-README.md", "privatekeys-gsmg.html")]
    evidence = [source(path) for path in paths]
    locations = ["research/evidence/cycle02/_work__creator_jrk.txt:165", "research/evidence/cycle02/_work__chat_transcript.txt:3572", "research/evidence/cycle02/_work__creator_jrk.txt:197", "research/evidence/cycle02/_work__creator_jrk.txt:199", "research/sources/manifest.json", "research/sources/theseedisplanted.html:15", "research/sources/phase2.html:17", "research/sources/salphaseion.html:16", "research/sources/salphaseion.html:19", "research/sources/gsmg-puzzle.png"]
    locations += [f'{entry["source"]["path"]}:{entry["line_one_based"]}' for entry in anchors]
    interpretations = [
        {"id": "C19-FIRST-WHOLE-IMAGE", "hypothesis": "First puzzle piece refers to the complete original PNG, whose grid, rabbit and footer share one source domain", "assumptions": ["First-piece warning recalls the initial published resource", "A source object may have several regions without each being a separate stage"], "confidence": "HIGH captured source identity; MEDIUM intended referent; UNKNOWN region or operation", "contradictions": ["January warning does not name a URL or region", "A creator resource pointer is not an explicit antecedent assignment", "The later hint's intended 2020 HTTP representation is not preserved"]},
        {"id": "C19-FIRST-GRID-SUBOBJECT", "hypothesis": "First puzzle piece refers specifically to the grid/rabbit subobject inside the original image", "assumptions": ["White/red/yellow/blue wording supplies a visual localization cue", "Matrixsumlist may recall the known grid without uniquely defining an operator"], "confidence": "MEDIUM color localization; LOW exclusive grid-only source ownership", "contradictions": ["Full PNG also contains red separator and footer", "No exact sentence restricts first piece to the matrix", "Completed grid routes and sums remain closed negatives"]},
        {"id": "C19-FIRST-HTML-CONTAINER", "hypothesis": "First puzzle piece refers to an authored HTML container with additional markup or image references outside the PNG", "assumptions": ["An earlier representation existed but was not captured", "Browser-generated image wrappers are excluded as creator evidence"], "confidence": "LOW; unsupported by the preserved initial response", "contradictions": ["Only captured original /puzzle response is image/png with PNG signature", "Eight image tags belong to a separately named later page", "Secondary Original page label does not establish content type"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["identify captured response type", "bind complete image ownership", "compare original wording with secondary labels", "retain unresolved region selection"],
        "input": "Preserved initial PNG, source manifest, fixed page markup and first-piece warning",
        "output": "One finite source-domain interpretation, not an alternate route or selected text",
        "next_test": NEXT_TEST,
    } for entry in interpretations]
    return {
        "id": "C19-FIRST-PIECE-DOMAIN", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "Preserved source ownership identifies the domain named by first-puzzle-piece and rabbits-nest without assuming an initial HTML page",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Recorded response metadata is supported by exact preserved bytes", "The2026 capture cannot establish all earlier response variants", "Only three declared source-domain readings are compared"],
        "operation_order": ["validate frozen task", "filter manifest locators without opening excluded snapshots", "verify initial PNG and two identical copies", "map one original creator resource pointer", "map ten fixed secondary anchors", "inventory three separate primary pages", "reuse frozen image regions with explicit ownership", "compare three domain readings"],
        "input": "Original source manifest/PNG, fixed later primary pages, original warning/pointer and secondary source labels",
        "output": "Exact response/page/region ownership and three bounded referent hypotheses",
        "confidence": "HIGH captured object/page distinction; UNKNOWN unique intended region and graph edge",
        "capture_domain": capture_domain(), "creator_pointer": creator_pointer(),
        "warning_reused": {"source": source(preceding), "record": frozen["chronology"]["records"][0], "no_warning_chronology_or_topology_test_repeated": True},
        "page_inventory": page_inventory(), "image_ownership": image_ownership(),
        "secondary_anchors": anchors, "secondary_page_image_alias_is_not_creator_instruction": True,
        "hypotheses": hypotheses,
        "result": "Captured /puzzle is the complete PNG, not preserved HTML. Grid/rabbit and footer belong to the same byte-identical source in three copies. Eight image tags belong only to later theseedisplanted; PHASE2 and SalPhaseIon/Cosmic headings belong to separate sources. A creator-attributed2019 URL pointer supports initial-resource identity but does not bind January warning to a region. Whole-image is the strongest domain reading; grid-only remains possible, initial-HTML reading requires missing historical evidence. No operand, entrance or consumer is derived.",
        "contradictions": ["PNG response type in2026 does not exclude earlier HTML", "Primary warning supplies no URL or region selector", "Community page/image aliases cannot authenticate an HTML container or final argument"],
        "next_test": NEXT_TEST,
        "search_space": {"manifest_locator_entries": 93, "initial_response_captures": 1, "identical_image_copies": 3, "primary_later_pages": 3, "later_body_image_tags": 8, "later_headings": 4, "fixed_secondary_anchors": 10, "creator_resource_pointers_cross_checked": 1, "frozen_image_regions": 3, "declared_domain_readings": 3},
        "review_correction": "Initial report's declared heading count and test expectation omitted the PHASE3 heading on phase2.html. Exhaustive heading mapping already contained it. First snapshot retained; current count is four headings across three distinct later pages.",
        "new_cryptographic_trials": 0, "new_trial_inputs": 0, "new_routes": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "first-piece-domain-v2.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "initial_response": "PNG", "primary_later_pages": 3, "later_image_tags": 8, "unique_region_or_consumer": False, "new_routes": 0}, indent=2))


if __name__ == "__main__":
    main()
