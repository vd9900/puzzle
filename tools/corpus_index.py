#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageDraw

from tools.gsmg import ARTIFACTS, SOURCES


PATTERNS = {
    "password": r"\b(?:passphrase|password|private.?key|key.?derivation)\b",
    "aes": r"\b(?:AES|CBC|KDF|EVP|PBKDF2|salt|padding)\b",
    "hash": r"(?:sha[- ]?(?:1|224|256|384|512)|\bmd5\b|hash.?the.?text|HASHTHETEXT)",
    "target_stage": r"(?:salphaseion|salphaselon|cosmic.?duality|phase.?3[.]2|dbbi|faed)",
    "ordering": r"(?:matrix.?sum.?list|last.?words.?before.?archi.?choice|checkerboard|Bifid|Polybius|\bindex(?:ing)?\b|zeroed|prime|y[i]?n[g]?.?yang)",
    "uncertainty": r"(?:retract|speculat|unverified|not.{0,15}(?:solved|verified)|nonsense|wrong)",
    "normalization": r"(?:[.]\.\.|\/[\(]a{2,3}|\b(?:uppercase|lowercase|capitalization|whitespace|newline|reverse|punctuation)\b)",
    "numeric_constraint": r"(?:\b(?:91|570|661|1141|13|38|23|16|7)\b|\b20(?:19|20|21|22|23|24|25|26)[-/][0-9]{2}[-/][0-9]{2}\b)",
}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def classify(name, entry):
    if name.startswith("github-issue"):
        return "UNVERIFIED_CLAIM"
    if name in ("gsmg-puzzle.png", "phase2.html", "salphaseion.html", "theseedisplanted.html"):
        return "ORIGINAL"
    if name.startswith("maintained-hints__") or name.startswith("maintained-decentraland-assets__"):
        return "ARCHIVED_PRIMARY"
    if name.startswith("maintained-unverified__"):
        return "SPECULATION"
    if name.startswith(("maintained-", "community-")):
        return "SECONDARY_RESEARCH"
    if name.startswith(("blockstream-", "mempool-")):
        return "ORIGINAL"
    return "SECONDARY_RESEARCH"


def records(path):
    if path.suffix == ".ipynb":
        notebook = json.loads(path.read_text())
        for index, cell in enumerate(notebook.get("cells", [])):
            yield f"cell:{index}:{cell.get('cell_type')}", "".join(cell.get("source", [])), {"attachments": sorted(cell.get("attachments", {}))}
            for output_index, output in enumerate(cell.get("outputs", [])):
                text = output.get("text", output.get("data", {}).get("text/plain", []))
                yield f"cell:{index}:output:{output_index}", "".join(text), {}
    elif path.suffix == ".json":
        document = json.loads(path.read_text())
        items = document if isinstance(document, list) else [document]
        for index, item in enumerate(items):
            if isinstance(item, dict) and "body" in item:
                metadata = {key: item[key] for key in ("id", "number", "created_at", "html_url") if key in item}
                metadata["author"] = item.get("user", {}).get("login")
                yield f"record:{index}", (item.get("title") or "") + "\n" + (item.get("body") or ""), metadata
            else:
                yield f"record:{index}", json.dumps(item, sort_keys=True), {}
    elif path.suffix in (".html", ".md", ".txt"):
        payload = path.read_bytes()
        try:
            document = payload.decode("utf-8")
        except UnicodeDecodeError:
            document = payload.decode("latin-1")
        if path.suffix == ".html":
            parser = TextExtractor()
            parser.feed(document)
            document = "\n".join(parser.parts)
        yield "document", document, {}


def build_index():
    manifest = json.loads((SOURCES / "manifest.json").read_text())
    destination = ARTIFACTS / "cycle02"
    destination.mkdir(parents=True, exist_ok=True)
    evidence = []
    inventory = []
    for name, entry in sorted(manifest.items()):
        path = SOURCES / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Source integrity failed: {name}")
        information = {"file": name, "classification": classify(name, entry), "sha256": entry["sha256"], "url": entry["url"], "bytes": entry["bytes"], "coverage": ""}
        if path.suffix in (".png", ".jpg"):
            with Image.open(path) as image:
                information["image"] = {"width": image.width, "height": image.height, "mode": image.mode, "metadata_keys": sorted(image.info)}
            information["coverage"] = "Decoded image metadata; hint montage available for visual inspection"
        elif path.suffix == ".mp3":
            information["coverage"] = "Preserved audio; baseline FFmpeg spectral transform reproduced"
        else:
            information["coverage"] = "Structured text records scanned; notebook attachments indexed but not OCRed or executed"
        count = 0
        diagnostics = {"dates": Counter(), "uppercase_words": Counter(), "normalization_markers": Counter()}
        for location, text, metadata in records(path):
            count += 1
            diagnostics["dates"].update(re.findall(r"\b(?:20[0-9]{2}[-/.][0-9]{2}[-/.][0-9]{2}|[0-9]{2}[.][0-9]{2}[.]20[0-9]{2})\b", text))
            diagnostics["uppercase_words"].update(re.findall(r"\b[A-Z][A-Z_-]{2,24}\b", text))
            diagnostics["normalization_markers"].update(marker for marker in ("...", "# X", "(aa", "(aaa", "\r\n", "\\x") if marker in text)
            for category, pattern in PATTERNS.items():
                for match in re.finditer(pattern, text, re.I):
                    excerpt = text[max(0, match.start() - 160):min(len(text), match.end() + 260)]
                    evidence.append({"source": name, "source_sha256": entry["sha256"], "classification": information["classification"], "locator": location, "offset": match.start(), "category": category, "excerpt": excerpt, "metadata": metadata})
        information["text_records"] = count
        information["text_diagnostics"] = {category: dict(counts.most_common(30)) for category, counts in diagnostics.items()}
        inventory.append(information)
    summary = {"source_files": len(inventory), "source_bytes": sum(item["bytes"] for item in inventory), "classification_counts": dict(Counter(item["classification"] for item in inventory)), "evidence_hits": len(evidence), "category_hits": dict(Counter(item["category"] for item in evidence)), "coverage_limits": "Images are inventoried/visually reviewed, not fully OCRed. Author labels and filenames are not authenticated creator provenance. Forum claims remain unverified."}
    (destination / "corpus-index.json").write_text(json.dumps({"summary": summary, "inventory": inventory}, indent=2) + "\n")
    with (destination / "corpus-evidence.jsonl").open("w") as output:
        for record in evidence:
            output.write(json.dumps(record, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    return summary


def hint_montage():
    paths = sorted(SOURCES.glob("maintained-hints__*"))
    destination = ARTIFACTS / "cycle02"
    destination.mkdir(parents=True, exist_ok=True)
    for page_start in range(0, len(paths), 8):
        page = Image.new("RGB", (1600, 1800), "#dddddd")
        draw = ImageDraw.Draw(page)
        for index, path in enumerate(paths[page_start:page_start + 8]):
            left = (index % 2) * 800
            top = (index // 2) * 450
            draw.text((left + 10, top + 8), path.name, fill="black")
            with Image.open(path) as original:
                image = original.convert("RGB")
                image.thumbnail((780, 420))
                page.paste(image, (left + 10, top + 28))
        output = destination / f"hint-montage-{page_start // 8 + 1}.png"
        page.save(output)
        print(output)


def main():
    parser = argparse.ArgumentParser(description="Index all preserved puzzle sources without executing third-party code")
    parser.add_argument("command", choices=("index", "montage"))
    arguments = parser.parse_args()
    if arguments.command == "index":
        build_index()
    else:
        hint_montage()


if __name__ == "__main__":
    main()
