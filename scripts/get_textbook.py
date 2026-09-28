#!/usr/bin/env python3
"""Download the published chapters of the course textbook into textbook/.

    python3 scripts/get_textbook.py        (Windows: py -3 scripts/get_textbook.py)

The study skill reads the textbook from textbook/ in this folder. This script fills that folder
from the public site, https://harvard-am215.github.io/textbook/, which publishes a Markdown copy
of every page. Run it before a session; the skill runs it too when the agent is allowed to use
the network. It downloads only what changed since the last run, and a second run in a row
downloads nothing.

No file in textbook/ is changed until every page has downloaded. If the site cannot be reached
and an earlier complete copy exists, that copy is kept and the script says how old it is.

Standard library only, so it runs with any Python 3.9 or later and nothing to install.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import socket
import sys
import tempfile
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SITE = "https://harvard-am215.github.io"
BASE = SITE + "/textbook/"
DEST = Path(__file__).resolve().parent.parent / "textbook"
SOURCE = DEST / "SOURCE.json"
TIMEOUT = 20
WORKERS = 8  # a first download is about 25 requests; one at a time can take minutes


class FetchError(Exception):
    pass


# Try IPv4 addresses first. On a network whose IPv6 is broken, Python otherwise waits several
# seconds on every request before falling back (measured 2026-09-28: 3.2 s against 0.09 s).
_getaddrinfo = socket.getaddrinfo


def _ipv4_first(*args, **kwargs):
    return sorted(_getaddrinfo(*args, **kwargs), key=lambda a: a[0] != socket.AF_INET)


socket.getaddrinfo = _ipv4_first


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "am115-study-skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read()
    except Exception as e:  # network down, DNS, HTTP error: all mean "cannot fetch now"
        raise FetchError(f"{url}: {e}") from e


def get_json(url: str) -> dict:
    try:
        return json.loads(get(url))
    except json.JSONDecodeError as e:
        raise FetchError(f"{url}: not JSON ({e})") from e


def manifest(fetch_json=get_json) -> dict[str, str]:
    """{filename: absolute URL of its Markdown} for every published page."""
    config = fetch_json(BASE + "config.json")
    try:
        project = config["projects"][0]
        slugs = [project["index"]] + [p["slug"] for p in project.get("pages", []) if p.get("slug")]
        if not all(isinstance(x, str) for x in slugs):
            raise TypeError("a page slug is not a string")
    except (KeyError, IndexError, TypeError, AttributeError) as e:
        raise FetchError(f"config.json has an unexpected layout ({e!r})") from e

    with ThreadPoolExecutor(WORKERS) as pool:
        pages = list(pool.map(lambda s: fetch_json(BASE + urllib.parse.quote(s) + ".json"), slugs))

    files: dict[str, str] = {}
    for slug, page in zip(slugs, pages):
        try:
            exports = [x for x in page.get("frontmatter", {}).get("exports", [])
                       if x.get("format") == "md"]
        except (AttributeError, TypeError) as e:
            raise FetchError(f"page {slug!r} has an unexpected layout ({e!r})") from e
        if len(exports) != 1:
            raise FetchError(f"page {slug!r} has {len(exports)} Markdown exports, expected 1")
        name, url = exports[0].get("filename", ""), exports[0].get("url", "")
        if not name.endswith(".md") or name != os.path.basename(name) or name.startswith("."):
            raise FetchError(f"page {slug!r} has an unsafe filename {name!r}")
        if not url.startswith("/textbook/build/"):
            raise FetchError(f"page {slug!r} points outside the textbook: {url!r}")
        if name in files:
            raise FetchError(f"two pages both export {name!r}")
        files[name] = SITE + url
    return files


def load_source() -> dict:
    try:
        old = json.loads(SOURCE.read_text())
        return old if isinstance(old, dict) and isinstance(old.get("files"), dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def intact_copy() -> list[str]:
    """Files SOURCE.json records that are missing or changed; [] means the copy is complete."""
    old = load_source()
    if not old.get("files"):
        return ["(no downloaded copy)"]
    bad = []
    for name, rec in old["files"].items():
        path = DEST / name
        if not path.is_file() or sha256(path.read_bytes()) != rec.get("sha256"):
            bad.append(name)
    return bad


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def up_to_date(name: str, url: str, old: dict) -> bool:
    rec = old.get("files", {}).get(name)
    if not isinstance(rec, dict):
        return False
    path = DEST / name
    return bool(rec and rec.get("url") == url and path.is_file()
                and sha256(path.read_bytes()) == rec.get("sha256"))


def sync(fetch=get, fetch_json=get_json) -> tuple[list[str], list[str], list[str]]:
    """Download into a temporary folder, then move into place only if every page succeeded."""
    files = manifest(fetch_json)
    old = load_source()
    todo = {n: u for n, u in files.items() if not up_to_date(n, u, old)}

    DEST.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=DEST.parent) as tmp:
        with ThreadPoolExecutor(WORKERS) as pool:
            blobs = dict(zip(todo, pool.map(fetch, todo.values())))
        fetched = {}
        for name, data in blobs.items():
            if not data.strip():
                raise FetchError(f"{todo[name]} came back empty")
            (Path(tmp) / name).write_bytes(data)
            fetched[name] = sha256(data)

        # Every page is in hand: now change textbook/.
        for name in fetched:
            os.replace(Path(tmp) / name, DEST / name)
    gone = sorted(p.name for p in DEST.glob("*.md") if p.name not in files and p.name != "README.md")
    for name in gone:
        (DEST / name).unlink()

    record = {"files": {}}
    for name, url in files.items():
        digest = fetched.get(name) or old["files"][name]["sha256"]
        record["files"][name] = {"url": url, "sha256": digest}
    record["site"] = BASE
    record["fetched"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    SOURCE.write_text(json.dumps(record, indent=1) + "\n")
    return sorted(fetched), gone, sorted(files)


def main() -> int:
    try:
        new, gone, all_files = sync()
    except FetchError as e:
        bad = intact_copy()
        if not bad:
            print(f"Could not reach the textbook site ({e}).\n"
                  f"Using the copy downloaded {load_source().get('fetched', '(date unknown)')}. "
                  f"Run this again when you are online.")
            return 0
        print(f"Could not download the textbook ({e}).\n"
              f"Missing or changed in textbook/: {', '.join(bad)}.\n"
              f"Check your internet connection and run this again: python3 scripts/get_textbook.py")
        return 1
    except OSError as e:
        print(f"Could not write to textbook/ ({e}).\n"
              f"Check that this folder is writable, then run this again: python3 scripts/get_textbook.py")
        return 1
    print(f"Textbook up to date in textbook/: {len(all_files)} pages "
          f"({len(new)} downloaded, {len(gone)} removed).")
    for name in new:
        print(f"  downloaded {name}")
    for name in gone:
        print(f"  removed {name} (no longer published)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
