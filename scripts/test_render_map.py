#!/usr/bin/env python3
"""Offline tests for render_map.py: python3 scripts/test_render_map.py"""

import contextlib
import io
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import render_map as rm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# The map from a real session: branches, a pair of ranks that must cross, labelled dashed arrows.
SESSION = """graph TD
  SDE["SDE: the random walk in continuous time — added"] --> GBM["GBM: drift and noise both proportional to the price — recalled"]
  GBM --> LOG["Itô's lemma applied to log S — added"]
  ITO["Itô's lemma — added"] --> LOG
  LOG --> LN["Lognormal solution — added"]
  LOG --> FIT["Fitting μ and σ from data — added"]
  GBM -. missing .-> HEDGE["Hedging: option plus shares cancel the risk, so the portfolio earns r — recalled"]
  ITO -. missing .-> HEDGE
  HEDGE -. missing .-> MU["μ drops out: the price needs only σ and r — recalled"]
  HEDGE --> BSE["Black–Scholes equation — added"]
  BSE --> DIFF["Price = diffusion run backward from the payout — added"]
  DIFF --> PAY["Price = the known payout, discounted — recalled, incomplete"]
  PAY --> BSM["Black–Scholes–Merton formula — added"]"""


def graph(text: str) -> rm.Graph:
    return rm.parse_graph(text.strip("\n").split("\n"), 1)


def quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args)


class Parse(unittest.TestCase):
    def test_nodes_arrows_and_labels(self):
        g = graph("""
graph TD
  A["Returns — recalled"] --> B["dS = μS dt + σS dW — added"]
  B -.-> C(plain)
  C ==> D
  D -. missing .-> A
  A -->|why| C
  A -- because --> D
  A --- D
""")
        self.assertEqual(list(g.nodes), ["A", "B", "C", "D"])
        self.assertEqual(g.nodes["B"].label, "dS = μS dt + σS dW — added")
        self.assertEqual(g.nodes["C"].label, "plain")
        self.assertEqual(g.nodes["D"].label, "D")
        self.assertEqual([(e.src, e.dst, e.style, e.arrow, e.label) for e in g.edges], [
            ("A", "B", "solid", True, ""), ("B", "C", "dashed", True, ""),
            ("C", "D", "thick", True, ""), ("D", "A", "dashed", True, "missing"),
            ("A", "C", "solid", True, "why"), ("A", "D", "solid", True, "because"),
            ("A", "D", "solid", False, "")])

    def test_chains_ampersands_semicolons_and_line_breaks(self):
        g = graph('flowchart LR\n  A & B --> C --> D; E["two<br>lines"]\n  %% a comment\n  style A fill:#fff')
        self.assertEqual(g.direction, "LR")
        self.assertEqual([(e.src, e.dst) for e in g.edges], [("A", "C"), ("B", "C"), ("C", "D")])
        self.assertEqual(g.nodes["E"].label, "two\nlines")

    def test_what_it_cannot_read_names_the_line(self):
        with self.assertRaisesRegex(rm.MapError, r"^line 3, 'B --o C'"):
            graph("graph TD\n  A --> B\n  B --o C")
        with self.assertRaisesRegex(rm.MapError, r"^line 1: a graph starts"):
            graph("sequenceDiagram\n  A->>B: hi")
        with self.assertRaisesRegex(rm.MapError, r"closing quote"):
            graph('graph TD\n  A["open --> B')
        with self.assertRaisesRegex(rm.MapError, r"needs a node after it"):
            graph("graph TD\n  A -->")

    def test_status_sets_the_color(self):
        g = graph('graph TD\n  A["x — recalled"] --> B["y — repaired (partial)"] --> C["log S drifts at μ − σ²/2"]')
        for n in g.nodes.values():
            rm.measure(n)
        self.assertEqual([n.kind for n in g.nodes.values()], ["recalled", "repaired", ""])
        self.assertEqual(g.nodes["B"].status, ["repaired (partial)"])

    def test_wrapping_is_balanced(self):
        lines = rm.wrap("Itô's lemma applied to log S", rm.FONT, rm.WRAP)
        self.assertEqual(len(lines), 2)
        self.assertGreater(min(len(t) for t in lines), 5)


class Geometry(unittest.TestCase):
    def check(self, text: str) -> rm.Layout:
        g = graph(text)
        lay = rm.layout(g)
        boxes = list(lay.boxes.items())
        for i, (a, (xa, ya, wa, ha)) in enumerate(boxes):
            for b, (xb, yb, wb, hb) in boxes[i + 1:]:
                apart = abs(xa - xb) >= (wa + wb) / 2 or abs(ya - yb) >= (ha + hb) / 2
                self.assertTrue(apart, f"{a} and {b} overlap")
        for edge, pieces, _ in lay.links:
            for name, point in ((edge.src, pieces[0][0]), (edge.dst, pieces[-1][-1])):
                x, y, w, h = lay.boxes[name]
                on_side = (abs(abs(point[1] - y) - h / 2) < 0.01 and abs(point[0] - x) <= w / 2) or \
                          (abs(abs(point[0] - x) - w / 2) < 0.01 and abs(point[1] - y) <= h / 2)
                self.assertTrue(on_side, f"arrow {edge.src}->{edge.dst} does not meet {name}")
        return lay

    def test_session_map(self):
        lay = self.check(SESSION)
        self.assertEqual(len(lay.links), 12)
        y = {n: box[1] for n, box in lay.boxes.items()}
        for a, b in [("SDE", "GBM"), ("GBM", "LOG"), ("HEDGE", "BSE"), ("PAY", "BSM")]:
            self.assertLess(y[a], y[b])

    def test_labels_avoid_other_arrows(self):
        lay = self.check(SESSION)
        for i, (edge, _, at) in enumerate(lay.links):
            if not at:
                continue
            w, h = rm.label_size(edge.label)
            box = (at[0] - w / 2, at[1] - h / 2, at[0] + w / 2, at[1] + h / 2)
            for j, (other, pieces, _) in enumerate(lay.links):
                if j != i:
                    hits = [rm.bezier(p, t / 32) for p in pieces for t in range(33)]
                    self.assertFalse(any(rm.inside(p, box) for p in hits),
                                     f"label of {edge.src}->{edge.dst} covers {other.src}->{other.dst}")

    def test_directions(self):
        for direction, axis, sign in (("LR", 0, 1), ("RL", 0, -1), ("BT", 1, -1), ("TD", 1, 1)):
            lay = self.check(f"graph {direction}\n  A --> B --> C\n  A --> C\n  A -. long label .-> D")
            pos = {n: box[axis] for n, box in lay.boxes.items()}
            self.assertGreater(sign * (pos["B"] - pos["A"]), 0, direction)
            self.assertGreater(sign * (pos["C"] - pos["B"]), 0, direction)

    def test_cycles_and_self_loops(self):
        lay = self.check("graph TD\n  A --> B --> C --> A\n  C --> C")
        self.assertEqual(len(lay.links), 3)  # the loop from C to itself is not drawn
        ends = {(e.src, e.dst): (p[0][0], p[-1][-1]) for e, p, _ in lay.links}
        start, end = ends[("C", "A")]
        self.assertLess(abs(start[1] - lay.boxes["C"][1]), abs(end[1] - lay.boxes["C"][1]))


class File(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.map = self.dir / "map.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_draws_links_once_and_keeps_the_rest(self):
        text = ("# My map\n\n## Chapter 6: Geometric Brownian motion (2026-09-28)\n\n"
                "```mermaid\ngraph TD\n  A[\"a — recalled\"] --> B[\"b — added\"]\n```\n"
                "| Idea | How |\n|---|---|\n\n"
                "## Chapters 6 and 7: GBM and options (2026-10-05)\n\n"
                "```mermaid\ngraph TD\n  C --> D\n```\n\n## Plan\n1. Exercise 2 (15 min)\n")
        self.map.write_text(text, encoding="utf-8")
        self.assertEqual(quiet(rm.main, ["render_map.py", str(self.map)]), 0)
        linked = self.map.read_text(encoding="utf-8")
        self.assertEqual(linked.count("![Chapter 6 map](map-chapter-6.svg)"), 1)
        self.assertEqual(linked.count("![Chapters 6 and 7 map](map-chapters-6-and-7.svg)"), 1)
        expected = (text.replace("```\n| Idea", "```\n\n![Chapter 6 map](map-chapter-6.svg)\n\n| Idea", 1)
                    .replace("```\n\n## Plan", "```\n\n![Chapters 6 and 7 map](map-chapters-6-and-7.svg)\n\n## Plan", 1))
        self.assertEqual(linked, expected)
        for name in ("map-chapter-6.svg", "map-chapters-6-and-7.svg"):
            root = ET.parse(self.dir / name).getroot()
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn(">a</text>", (self.dir / "map-chapter-6.svg").read_text(encoding="utf-8"))
        # A second run changes nothing.
        self.assertEqual(quiet(rm.main, ["render_map.py", str(self.map)]), 0)
        self.assertEqual(self.map.read_text(encoding="utf-8"), linked)

    def test_a_renamed_section_moves_its_link(self):
        self.map.write_text("## Chapter 5: Walks\n\n```mermaid\ngraph TD\n  A --> B\n```\n\n"
                            "![Chapter 6 map](map-chapter-6.svg)\n", encoding="utf-8")
        quiet(rm.main, ["render_map.py", str(self.map)])
        text = self.map.read_text(encoding="utf-8")
        self.assertIn("![Chapter 5 map](map-chapter-5.svg)", text)
        self.assertNotIn("map-chapter-6.svg", text)

    def test_an_error_writes_nothing(self):
        text = "## Chapter 6\n\n```mermaid\ngraph TD\n  A --> B\n```\n\n## Chapter 7\n\n```mermaid\ngraph TD\n  A --o B\n```\n"
        self.map.write_text(text, encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(rm.main(["render_map.py", str(self.map)]), 1)
        self.assertIn("line 12, 'A --o B'", err.getvalue())
        self.assertEqual(self.map.read_text(encoding="utf-8"), text)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["map.md"])

    def test_windows_line_endings_are_kept(self):
        self.map.write_bytes(b"## Chapter 6\r\n\r\n```mermaid\r\ngraph TD\r\n  A --> B\r\n```\r\nNotes\r\n")
        quiet(rm.main, ["render_map.py", str(self.map)])
        data = self.map.read_bytes()
        self.assertIn(b"```\r\n\r\n![Chapter 6 map](map-chapter-6.svg)\r\n\r\nNotes\r\n", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))

    def test_no_map_yet(self):
        self.assertEqual(quiet(rm.main, ["render_map.py", str(self.dir / "missing.md")]), 1)

    def test_the_example_in_the_skill_draws(self):
        for skill in (".agents/skills/study/SKILL.md", ".claude/skills/study/SKILL.md"):
            text = (ROOT / skill).read_text(encoding="utf-8")
            example = re.search(r"````markdown\n(.*?)\n````", text, re.S).group(1)
            linked, svgs = rm.render(example, self.dir)
            self.assertEqual([p.name for p, _ in svgs], ["map-chapter-6.svg"], skill)
            self.assertEqual(linked, example, f"{skill}: the example should already link its drawing")


if __name__ == "__main__":
    unittest.main()
