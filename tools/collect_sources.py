#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "research" / "sources"
MANIFEST = SNAPSHOTS / "manifest.json"
REPOSITORY = "puzzlehunt/gsmgio-5btc-puzzle"
MAX_BYTES = 8 * 1024 * 1024


def snapshot(name, url):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError("Snapshot names must not contain directories")
    if not url.startswith("https://"):
        raise ValueError("Only public HTTPS sources are supported")
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    request = urllib.request.Request(url, headers={"User-Agent": "gsmg-public-puzzle-research/0.1"})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise ValueError("Source exceeds the snapshot size limit")
        entry = {
            "url": url,
            "final_url": response.url,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    destination = SNAPSHOTS / name
    if destination.exists() and destination.read_bytes() != payload:
        previous_digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        previous_name = f"{destination.stem}.{previous_digest[:16]}{destination.suffix}"
        previous_path = SNAPSHOTS / previous_name
        if previous_path.exists() and previous_path.read_bytes() != destination.read_bytes():
            raise ValueError("Historical snapshot collision")
        previous_path.write_bytes(destination.read_bytes())
        if name in manifest:
            manifest[previous_name] = manifest[name]
    destination.write_bytes(payload)
    manifest[name] = entry
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"{name}: {len(payload)} bytes, sha256={entry['sha256']}")
    return payload


def collect_initial():
    sources = [
        ("privatekeys-gsmg.html", "https://privatekeys.pw/puzzles/gsmg-puzzle"),
        ("gsmg-puzzle.png", "https://gsmg.io/puzzle"),
        ("github-repository.json", f"https://api.github.com/repos/{REPOSITORY}"),
        ("github-issues-page1.json", f"https://api.github.com/repos/{REPOSITORY}/issues?state=all&per_page=100&page=1"),
        ("github-issues-page2.json", f"https://api.github.com/repos/{REPOSITORY}/issues?state=all&per_page=100&page=2"),
        ("blockstream-address.json", "https://blockstream.info/api/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"),
        ("mempool-address.json", "https://mempool.space/api/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"),
        ("blockstream-utxos.json", "https://blockstream.info/api/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe/utxo"),
        ("blockstream-secondary-address.json", "https://blockstream.info/api/address/17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"),
        ("mempool-secondary-address.json", "https://mempool.space/api/address/17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"),
        ("github-commit.json", f"https://api.github.com/repos/{REPOSITORY}/commits/master"),
    ]
    for name, url in sources:
        try:
            snapshot(name, url)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            print(f"FAILED {name}: {error}")
    commit_path = SNAPSHOTS / "github-commit.json"
    if commit_path.exists():
        commit = json.loads(commit_path.read_text())["sha"]
        snapshot("community-README.md", f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}/README.md")
        snapshot("github-tree.json", f"https://api.github.com/repos/{REPOSITORY}/git/trees/{commit}?recursive=1")
    for number in (68, 108):
        snapshot(f"github-issue-{number}.json", f"https://api.github.com/repos/{REPOSITORY}/issues/{number}")
        snapshot(f"github-issue-{number}-comments.json", f"https://api.github.com/repos/{REPOSITORY}/issues/{number}/comments?per_page=100")
    for name, url in (
        ("phase2.html", "https://gsmg.io/choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself"),
        ("salphaseion.html", "https://gsmg.io/89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32"),
    ):
        snapshot(name, url)


def main():
    parser = argparse.ArgumentParser(description="Snapshot public puzzle sources; never signs or submits transactions")
    parser.add_argument("--initial", action="store_true")
    parser.add_argument("--name")
    parser.add_argument("--url")
    arguments = parser.parse_args()
    if arguments.initial:
        collect_initial()
    elif arguments.name and arguments.url:
        snapshot(arguments.name, arguments.url)
    else:
        parser.error("Specify --initial or both --name and --url")


if __name__ == "__main__":
    main()
