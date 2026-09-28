#!/usr/bin/env python3
"""Offline tests for get_textbook.py: python3 scripts/test_get_textbook.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import get_textbook as gt  # noqa: E402


class FakeSite:
    """Serves config.json, page JSONs and Markdown from dicts; counts downloads."""

    def __init__(self, pages: dict[str, str], extra_parts=True):
        self.pages = dict(pages)  # slug -> markdown text
        self.fail = set()
        self.downloads = 0
        self.extra_parts = extra_parts

    def json(self, url):
        name = url.rsplit("/", 1)[1]
        if name == "config.json":
            slugs = [s for s in self.pages if s != "index"]
            pages = [{"slug": s, "title": s} for s in slugs]
            if self.extra_parts:
                pages += [{"title": "Appendices", "level": 1}, {"slug": None, "title": "Part"}]
            return {"projects": [{"index": "index", "pages": pages}]}
        slug = name[:-5]
        text = self.pages[slug]
        return {"frontmatter": {"exports": [
            {"format": "md", "filename": f"{slug}.md", "url": f"/textbook/build/{slug}-{hash(text) & 0xffff}.md"}]}}

    def get(self, url):
        slug = url.rsplit("/", 1)[1].rsplit("-", 1)[0]
        if slug in self.fail:
            raise gt.FetchError(f"{url}: simulated failure")
        self.downloads += 1
        return self.pages[slug].encode()


class Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        gt.DEST = Path(self.tmp.name) / "textbook"
        gt.SOURCE = gt.DEST / "SOURCE.json"

    def tearDown(self):
        self.tmp.cleanup()

    def run_sync(self, site):
        return gt.sync(fetch=site.get, fetch_json=site.json)

    def test_first_run_then_nothing(self):
        site = FakeSite({"index": "intro", "gbm": "# GBM"})
        new, gone, allf = self.run_sync(site)
        self.assertEqual(new, ["gbm.md", "index.md"])
        self.assertEqual((gt.DEST / "gbm.md").read_text(), "# GBM")
        self.assertEqual(self.run_sync(site)[0], [])
        self.assertEqual(site.downloads, 2)

    def test_added_changed_removed(self):
        site = FakeSite({"index": "intro", "gbm": "# GBM", "mle": "# MLE"})
        self.run_sync(site)
        site.pages["gbm"] = "# GBM v2"
        del site.pages["mle"]
        site.pages["evt"] = "# EVT"
        new, gone, _ = self.run_sync(site)
        self.assertEqual(new, ["evt.md", "gbm.md"])
        self.assertEqual(gone, ["mle.md"])
        self.assertFalse((gt.DEST / "mle.md").exists())

    def test_partial_failure_changes_nothing(self):
        site = FakeSite({"index": "intro", "gbm": "# GBM", "mle": "# MLE"})
        self.run_sync(site)
        before = {p.name: p.read_bytes() for p in gt.DEST.iterdir()}
        site.pages["gbm"] = "# GBM v2"
        site.pages["mle"] = "# MLE v2"
        site.fail = {"mle"}
        with self.assertRaises(gt.FetchError):
            self.run_sync(site)
        after = {p.name: p.read_bytes() for p in gt.DEST.iterdir()}
        self.assertEqual(before, after)

    def test_deleted_or_edited_file_is_fetched_again(self):
        site = FakeSite({"index": "intro", "gbm": "# GBM"})
        self.run_sync(site)
        (gt.DEST / "gbm.md").unlink()
        (gt.DEST / "index.md").write_text("edited")
        new, _, _ = self.run_sync(site)
        self.assertEqual(new, ["gbm.md", "index.md"])
        self.assertEqual((gt.DEST / "index.md").read_text(), "intro")

    def test_unsafe_filename_rejected(self):
        site = FakeSite({"index": "intro"})
        orig = site.json
        site.json = lambda url: ({"frontmatter": {"exports": [
            {"format": "md", "filename": "../x.md", "url": "/textbook/build/x.md"}]}}
            if url.endswith("index.json") else orig(url))
        with self.assertRaises(gt.FetchError):
            self.run_sync(site)
        self.assertFalse(Path(self.tmp.name, "x.md").exists())

    def test_offline_uses_only_a_complete_copy(self):
        site = FakeSite({"index": "intro", "gbm": "# GBM"})
        self.run_sync(site)
        self.assertEqual(gt.intact_copy(), [])
        (gt.DEST / "gbm.md").unlink()
        self.assertEqual(gt.intact_copy(), ["gbm.md"])

    def test_malformed_page_json_is_a_fetch_error(self):
        site = FakeSite({"index": "intro"})
        orig = site.json
        site.json = lambda url: ({"frontmatter": ["not", "a", "dict"]}
                                 if url.endswith("index.json") else orig(url))
        with self.assertRaises(gt.FetchError):
            self.run_sync(site)


if __name__ == "__main__":
    unittest.main(verbosity=1)
