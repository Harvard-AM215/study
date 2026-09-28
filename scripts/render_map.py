#!/usr/bin/env python3
"""Draw each graph in my/map.md as a picture, and link the picture under its graph.

    python3 scripts/render_map.py          (Windows: py -3 scripts/render_map.py)

The study skill keeps the student's map in my/map.md: a section per chapter, each with a mermaid
graph of the chapter's ideas. GitHub and some editors draw mermaid, but many Markdown viewers,
the Claude desktop app's among them, show only its code. This script draws each graph itself, as
my/map-<section>.svg (my/map-chapter-6.svg for a section headed "Chapter 6: ..."), which any web
browser opens, and puts a link to the drawing on the line under the graph. Run it again after
changing a graph: it redraws every graph and leaves the rest of the file as it was.

It reads the part of mermaid the skill uses: a first line `graph TD` (or LR, BT, RL), nodes
written A["label"], and the arrows --> (solid), -.-> (dashed) and ==> (thick), each with an
optional label written -. label .-> or -->|label|. Anything else stops the script with the line
it could not read, and then nothing is written. A node whose label ends in "— recalled",
"— added" or "— repaired" is colored by that status.

Standard library only, so it runs with any Python 3.9 or later and nothing to install.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

MAP = Path(__file__).resolve().parent.parent / "my" / "map.md"

# Sizes in pixels. A rank is a row of the drawing (TD, BT) or a column (LR, RL).
FONT, SMALL, TITLE = 14, 12, 15  # label text; status lines and arrow labels; the heading
LINE = 1.3  # line height, in font sizes
WRAP = 190  # longest line of a label before it wraps
PAD_X, PAD_Y = 12, 9  # inside a box
GAP = 28  # between neighbours in a rank
RANK_GAP = 56  # between ranks
PASS = 10  # room an arrow takes where it passes through a rank on its way to a later one
MARGIN = 20

# Fill, border and text colors of a box, by the status at the end of its label: stops 50, 600
# and 800 of the color ramps the Claude desktop app uses for diagrams, and for its dark mode
# stops 800, 200 and 100. The SVG, on a white background, uses the light ones.
RAMPS = {
    "recalled": (("#E6F1FB", "#185FA5", "#0C447C"), ("#0C447C", "#85B7EB", "#B5D4F4")),  # blue
    "added": (("#FAEEDA", "#854F0B", "#633806"), ("#633806", "#EF9F27", "#FAC775")),  # amber
    "repaired": (("#EAF3DE", "#3B6D11", "#27500A"), ("#27500A", "#97C459", "#C0DD97")),  # green
    "": (("#F1EFE8", "#5F5E5A", "#444441"), ("#444441", "#B4B2A9", "#D3D1C7")),  # gray
}
INK, ARROW_INK = "#2C2C2A", "#5F5E5A"


class MapError(Exception):
    """A line of a graph that this script cannot read."""


# ----------------------------------------------------------------------------------------------
# Reading a graph


@dataclass
class Node:
    id: str
    label: str
    kind: str = ""  # "recalled", "added", "repaired" or ""
    main: list = field(default_factory=list)  # the label, wrapped
    status: list = field(default_factory=list)  # "recalled ...", wrapped, on the lines below
    w: float = 0.0
    h: float = 0.0


@dataclass
class Edge:
    src: str
    dst: str
    style: str  # "solid", "dashed" or "thick"
    arrow: bool
    label: str = ""


@dataclass
class Graph:
    direction: str = "TD"
    nodes: dict = field(default_factory=dict)  # id -> Node, in order of first appearance
    edges: list = field(default_factory=list)


HEADER = re.compile(r"(?:graph|flowchart)(?:\s+(TD|TB|BT|LR|RL))?", re.I)
# Styling, clicks and subgraph boxes are left out of the drawing; the nodes inside a subgraph
# are still drawn.
SKIP = re.compile(r"(?:classDef\s|class\s|style\s|linkStyle\s|click\s|direction\s|subgraph\b|end$)")
NODE_ID = re.compile(r"\w+")
SHAPES = [("([", "])"), ("[[", "]]"), ("[(", ")]"), ("((", "))"), ("{{", "}}"),
          ("[", "]"), ("(", ")"), ("{", "}"), (">", "]")]
ARROW = re.compile(
    r"""\s*(?:
        (?P<open>--|-\.|==)\s+(?P<text>\S.*?)\s+(?P<close>-{2,}>|-{3,}|\.-+>|\.-+|={2,}>|={3,})
      | (?P<bare>-{2,}>|-{3,}|-\.+->|-\.+-|={2,}>|={3,})
    )(?:\s*\|(?P<pipe>[^|]*)\|)?\s*""",
    re.X,
)
AMPERSAND = re.compile(r"\s*&\s*")
CLASS_SUFFIX = re.compile(r":::\w+")
STATUS = re.compile(r"(.*?)\s+[—–-]+\s+((recalled|added|repaired)\b.*)", re.I | re.S)


def clean(text: str) -> str:
    """A label as plain text: <br> becomes a line break, and #quot; and #NNN; become characters."""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I).replace("#quot;", '"')
    text = re.sub(r"#(\d+);", lambda m: chr(int(m.group(1))), text)
    return "\n".join(" ".join(part.split()) for part in text.split("\n")).strip()


def statements(line: str) -> list:
    """Split a line at semicolons outside quotes."""
    parts, current, quoted = [], [], False
    for ch in line:
        if ch == '"':
            quoted = not quoted
        if ch == ";" and not quoted:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    return parts + ["".join(current)]


def parse_graph(lines: list, first: int) -> Graph:
    """Read the lines of a mermaid block; `first` is the file's line number of lines[0]."""
    graph = Graph()
    header = False
    for number, line in enumerate(lines, first):
        for statement in statements(line):
            s = statement.strip()
            if not s or s.startswith("%%"):
                continue
            if not header:
                m = HEADER.fullmatch(s)
                if not m:
                    raise MapError(f"line {number}: a graph starts with a line such as "
                                   f"'graph TD', not {s!r}")
                graph.direction = (m.group(1) or "TD").upper().replace("TB", "TD")
                header = True
            elif not SKIP.match(s):
                parse_statement(s, graph, number)
    if not header:
        raise MapError(f"line {first - 1}: the mermaid block is empty")
    return graph


def parse_statement(s: str, graph: Graph, number: int) -> None:
    """Read one statement: nodes joined by arrows, as in A --> B & C -.-> D."""

    def fail(reason: str):
        raise MapError(f"line {number}, {s!r}: {reason}")

    groups, links, pos = [], [], 0
    while True:
        group = []
        while True:
            node_id, pos = parse_node(s, pos, graph, fail)
            group.append(node_id)
            m = AMPERSAND.match(s, pos)
            if not m:
                break
            pos = m.end()
        groups.append(group)
        if not s[pos:].strip():
            break
        m = ARROW.match(s, pos)
        if not m:
            fail("this script reads the arrows -->, -.-> and ==>, with an optional label "
                 "written -. label .-> or -->|label|")
        link = m.group("close") or m.group("bare")
        style = "dashed" if "." in link else "thick" if link.startswith("=") else "solid"
        links.append((style, link.endswith(">"), clean(m.group("text") or m.group("pipe") or "")))
        pos = m.end()
        if not s[pos:].strip():
            fail("an arrow needs a node after it")
    for (style, arrow, label), sources, targets in zip(links, groups, groups[1:]):
        for a in sources:
            for b in targets:
                graph.edges.append(Edge(a, b, style, arrow, label))


def parse_node(s: str, pos: int, graph: Graph, fail) -> tuple:
    """Read a node name with an optional label in brackets; return its id and where it ends."""
    while pos < len(s) and s[pos].isspace():
        pos += 1
    m = NODE_ID.match(s, pos)
    if not m:
        fail(f"expected the name of a node at {s[pos:]!r}")
    node_id, pos = m.group(), m.end()
    label = None
    for opening, closing in SHAPES:
        if s.startswith(opening, pos):
            start = pos + len(opening)
            if s.startswith('"', start):
                end = s.find('"', start + 1)
                if end < 0:
                    fail("a label's closing quote is missing")
                label, pos = s[start + 1:end], end + 1
                if not s.startswith(closing, pos):
                    fail(f"expected {closing} after the label's closing quote")
            else:
                end = s.find(closing, start)
                if end < 0:
                    fail(f"expected {closing} to close the label")
                label, pos = s[start:end], end
            pos += len(closing)
            break
    m = CLASS_SUFFIX.match(s, pos)
    if m:
        pos = m.end()
    node = graph.nodes.setdefault(node_id, Node(node_id, node_id))
    if label is not None:
        node.label = clean(label)
    return node_id, pos


# ----------------------------------------------------------------------------------------------
# Laying it out: ranks by longest path, order within ranks by barycenters, positions by least
# squares (the usual layered drawing, in miniature)


def char_width(ch: str) -> float:
    """Approximate width of a character, in font sizes, in a common sans-serif font."""
    if ch in " .,:;'|!`il":
        return 0.30
    if ch in "fjrtI()[]{}/\\\"*-":
        return 0.40
    if ch in "mwMW@%—→←↔⇒…":
        return 0.95
    if ch.isdigit():
        return 0.58
    if "A" <= ch <= "Z":
        return 0.70
    if ch.isascii():
        return 0.56
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 1.0
    return 0.62


def text_width(text: str, size: float) -> float:
    # 5% over the estimate: text is centered, so too wide costs a little padding and too narrow
    # would let it run past its box.
    return 1.05 * size * sum(char_width(c) for c in text)


def greedy_wrap(text: str, size: float, width: float) -> list:
    lines = []
    for part in text.split("\n"):
        line = ""
        for word in part.split():
            trial = f"{line} {word}" if line else word
            if line and text_width(trial, size) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    return lines


def wrap(text: str, size: float, width: float) -> list:
    """Lines no wider than `width`, as even as the same number of lines allows, so that a label
    does not end on one short word."""
    lines = greedy_wrap(text, size, width)
    lo, hi = 0.0, width
    for _ in range(12):  # the narrowest width that still needs no more lines
        mid = (lo + hi) / 2
        if len(greedy_wrap(text, size, mid)) <= len(lines):
            hi = mid
        else:
            lo = mid
    return greedy_wrap(text, size, hi)


def measure(node: Node) -> None:
    m = STATUS.fullmatch(node.label)
    main, status = (m.group(1), m.group(2)) if m else (node.label, "")
    node.kind = m.group(3).lower() if m else ""
    node.main = wrap(main, FONT, WRAP)
    node.status = wrap(status, SMALL, WRAP) if status else []
    widest = max([text_width(t, FONT) for t in node.main] + [text_width(t, SMALL) for t in node.status])
    node.w = max(widest + 2 * PAD_X, 60)
    node.h = 2 * PAD_Y + len(node.main) * FONT * LINE + len(node.status) * SMALL * LINE


def back_edges(ids: list, edges: list) -> set:
    """Indices of the edges to turn around so that no path returns to where it started."""
    out = {n: [] for n in ids}
    for i, e in enumerate(edges):
        out[e.src].append(i)
    state, flipped = {}, set()  # state: 1 while on the search path, 2 when finished
    for root in ids:
        if root in state:
            continue
        state[root] = 1
        stack = [(root, iter(out[root]))]
        while stack:
            node, rest = stack[-1]
            for i in rest:
                nxt = edges[i].dst
                if state.get(nxt) == 1:
                    flipped.add(i)
                elif nxt not in state:
                    state[nxt] = 1
                    stack.append((nxt, iter(out[nxt])))
                    break
            else:
                state[node] = 2
                stack.pop()
    return flipped


def ranks(ids: list, pairs: list) -> dict:
    """Each node one rank below its lowest predecessor; a node with no predecessor then moves
    down to just above its nearest successor, so its arrows stay short."""
    succ = {n: [] for n in ids}
    pred = {n: [] for n in ids}
    for a, b in pairs:
        succ[a].append(b)
        pred[b].append(a)
    waiting = {n: len(pred[n]) for n in ids}
    order = [n for n in ids if not waiting[n]]
    for n in order:  # topological order (Kahn); the loop sees what it appends
        for m in succ[n]:
            waiting[m] -= 1
            if not waiting[m]:
                order.append(m)
    rank = {n: 0 for n in ids}
    for n in order:
        for m in succ[n]:
            rank[m] = max(rank[m], rank[n] + 1)
    for n in ids:
        if not pred[n] and succ[n]:
            rank[n] = min(rank[m] for m in succ[n]) - 1
    return rank


def order_ranks(ids: list, rank: dict, down: dict, up: dict) -> list:
    """The items of each rank, left to right (or top to bottom), with few arrows crossing."""
    layers = [[] for _ in range(max(rank.values(), default=-1) + 1)]
    seen = set()
    for root in [n for n in ids if not up[n]] + ids:  # depth-first from the sources
        stack = [root]
        while stack:
            k = stack.pop()
            if k not in seen:
                seen.add(k)
                layers[rank[k]].append(k)
                stack.extend(reversed(down[k]))

    def crossings() -> int:
        pos = {k: i for layer in layers for i, k in enumerate(layer)}
        count = 0
        for layer in layers:
            segs = [(pos[a], pos[b]) for a in layer for b in down[a]]
            count += sum(1 for i, (a1, b1) in enumerate(segs) for a2, b2 in segs[i + 1:]
                         if (a1 - a2) * (b1 - b2) < 0)
        return count

    # Sort each rank by the mean position of its neighbours in the rank before it, sweeping
    # down and then up, and keep the order with the fewest crossings.
    best, fewest = [layer[:] for layer in layers], crossings()
    for sweep in range(12):
        pos = {k: i for layer in layers for i, k in enumerate(layer)}
        downward = sweep % 2 == 0
        nbrs = up if downward else down
        for r in range(1, len(layers)) if downward else range(len(layers) - 2, -1, -1):
            layers[r].sort(key=lambda k: sum(pos[n] for n in nbrs[k]) / len(nbrs[k]) if nbrs[k] else pos[k])
            pos.update((k, i) for i, k in enumerate(layers[r]))
        count = crossings()
        if count < fewest:
            best, fewest = [layer[:] for layer in layers], count
    layers = best
    # Then swap neighbours wherever that removes a crossing.
    improved = True
    while improved and fewest:
        improved = False
        for layer in layers:
            for i in range(len(layer) - 1):
                layer[i], layer[i + 1] = layer[i + 1], layer[i]
                count = crossings()
                if count < fewest:
                    fewest, improved = count, True
                else:
                    layer[i], layer[i + 1] = layer[i + 1], layer[i]
    return layers


def place(desired: list, sizes: list, gap: float) -> list:
    """Centers as close as possible (least squares) to `desired`, in the same order, with
    neighbours at least `gap` apart: isotonic regression by pooling adjacent violators."""
    offsets = [0.0]
    for a, b in zip(sizes, sizes[1:]):
        offsets.append(offsets[-1] + (a + b) / 2 + gap)
    blocks = []  # [mean, count]
    for target in (d - o for d, o in zip(desired, offsets)):
        blocks.append([target, 1])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            mean, count = blocks.pop()
            blocks[-1] = [(blocks[-1][0] * blocks[-1][1] + mean * count) / (blocks[-1][1] + count),
                          blocks[-1][1] + count]
    fitted = [mean for mean, count in blocks for _ in range(count)]
    return [f + o for f, o in zip(fitted, offsets)]


@dataclass
class Layout:
    boxes: dict  # node id -> (center x, center y, width, height)
    links: list  # (Edge, [cubic Bézier pieces, each four (x, y) points], label center or None)
    minx: float
    miny: float
    width: float
    height: float


def layout(graph: Graph) -> Layout:
    """Positions for every box, and a path for every arrow."""
    for node in graph.nodes.values():
        measure(node)
    ids = list(graph.nodes)
    edges = [e for e in graph.edges if e.src != e.dst]  # a node's arrow to itself is not drawn
    flipped = back_edges(ids, edges)
    pairs = [(e.dst, e.src) if i in flipped else (e.src, e.dst) for i, e in enumerate(edges)]
    rank = ranks(ids, pairs)

    # Work in (o, r): o along a rank, r across ranks. For TD that is (x, y); for LR, (y, x).
    across = graph.direction in ("LR", "RL")
    osize = {n: graph.nodes[n].h if across else graph.nodes[n].w for n in ids}
    rsize = {n: graph.nodes[n].w if across else graph.nodes[n].h for n in ids}
    chains = []  # each arrow as the items it passes, from its lower rank to its higher
    for i, (a, b) in enumerate(pairs):
        chain = [a]
        for r in range(rank[a] + 1, rank[b]):
            dummy = f"\0{i}.{r}"  # where the arrow passes through rank r
            rank[dummy], osize[dummy], rsize[dummy] = r, PASS, 0
            chain.append(dummy)
        chains.append(chain + [b])
    down = {k: [] for k in rank}
    up = {k: [] for k in rank}
    for chain in chains:
        for a, b in zip(chain, chain[1:]):
            down[a].append(b)
            up[b].append(a)
    layers = order_ranks(ids, rank, down, up)

    # Along each rank: start packed and centered, then pull each item toward the mean of its
    # neighbours in the ranks around it.
    o = {}
    for layer in layers:
        pos = 0.0
        for k in layer:
            o[k] = pos + osize[k] / 2
            pos += osize[k] + GAP
        for k in layer:
            o[k] -= (pos - GAP) / 2

    def settle(r: int, neighbours) -> None:
        layer = layers[r]
        desired = []
        for k in layer:
            ns = neighbours(k)
            desired.append(sum(o[n] for n in ns) / len(ns) if ns else o[k])
        for k, x in zip(layer, place(desired, [osize[k] for k in layer], GAP)):
            o[k] = x

    for _ in range(4):
        for r in range(1, len(layers)):
            settle(r, lambda k: up[k])
        for r in range(len(layers) - 2, -1, -1):
            settle(r, lambda k: down[k])
    for _ in range(2):
        for r in range(len(layers)):
            settle(r, lambda k: up[k] + down[k])

    # Across ranks: each rank as deep as its deepest box, with room for arrow labels between.
    labels = [e.label for e in edges if e.label]
    if labels and across:
        gap = max(RANK_GAP, max(text_width(t, SMALL) for s in labels for t in s.split("\n")) + 32)
    else:
        gap = RANK_GAP + (16 if labels else 0)
    depth = [max((rsize[k] for k in layer), default=0) for layer in layers]
    r_at, pos = [], 0.0
    for i, d in enumerate(depth):
        pos += (depth[i - 1] / 2 + gap + d / 2) if i else 0
        r_at.append(pos)
    rpos = {k: r_at[rank[k]] for k in rank}

    # Spread the arrows leaving (or entering) a box along its side, in the order of the items
    # they go to (or come from), so that arrowheads do not land on one another.
    leave = {n: [] for n in ids}
    enter = {n: [] for n in ids}
    for ci, chain in enumerate(chains):
        leave[chain[0]].append(ci)
        enter[chain[-1]].append(ci)
    port_out, port_in = {}, {}
    for n in ids:
        for ports, cis, other in ((port_out, leave[n], 1), (port_in, enter[n], -2)):
            cis.sort(key=lambda ci: o[chains[ci][other]])
            span = min(0.6 * osize[n], 16 * (len(cis) - 1))
            for j, ci in enumerate(cis):
                ports[ci] = o[n] - span / 2 + (span * j / (len(cis) - 1) if len(cis) > 1 else 0)

    flip = -1 if graph.direction in ("BT", "RL") else 1

    def xy(p: tuple) -> tuple:
        return (flip * p[1], p[0]) if across else (p[0], flip * p[1])

    links = []
    for i, (edge, chain) in enumerate(zip(edges, chains)):
        a, b = chain[0], chain[-1]
        points = [(port_out[i], rpos[a] + rsize[a] / 2)]
        for d in chain[1:-1]:
            half = depth[rank[d]] / 2
            points += [(o[d], rpos[d] - half), (o[d], rpos[d] + half)]
        points.append((port_in[i], rpos[b] - rsize[b] / 2))
        pieces = []
        for j, (p, q) in enumerate(zip(points, points[1:])):
            if j % 2:  # straight through a rank
                pieces.append((p, p, q, q))
            else:  # between ranks, leaving and arriving square to the rank
                mid = (p[1] + q[1]) / 2
                pieces.append((p, (p[0], mid), (q[0], mid), q))
        if i in flipped:  # drawn from its real source, so the arrowhead is at its real target
            pieces = [piece[::-1] for piece in reversed(pieces)]
        links.append([edge, [tuple(xy(p) for p in piece) for piece in pieces], None])

    boxes = {}
    for n in ids:
        x, y = xy((o[n], rpos[n]))
        boxes[n] = (x, y, graph.nodes[n].w, graph.nodes[n].h)

    # An arrow's label goes on the arrow, as near its middle as it can be without covering a box,
    # another label or another arrow: a label drawn over a crossing reads as the other arrow's.
    samples = [[bezier(piece, t / 32) for piece in pieces for t in range(33)] for _, pieces, _ in links]
    taken = [(x - w / 2 - 2, y - h / 2 - 2, x + w / 2 + 2, y + h / 2 + 2) for x, y, w, h in boxes.values()]
    for i, link in enumerate(links):
        edge, pieces, _ = link
        if not edge.label:
            continue
        w, h = label_size(edge.label)
        between = pieces[0::2]  # the pieces between ranks; the others pass through a rank
        order = sorted(range(len(between)), key=lambda j: abs(j - (len(between) - 1) / 2))
        spots = [bezier(between[j], t) for j in order
                 for t in (0.5, 0.4, 0.6, 0.3, 0.7, 0.25, 0.75, 0.2, 0.8)]
        for x, y in spots:
            box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if not any(overlap(box, t) for t in taken) and not any(
                    inside(p, box) for k, pts in enumerate(samples) if k != i for p in pts):
                break
        else:
            x, y = spots[0]
        link[2] = (x, y)
        taken.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))

    xs, ys = [], []
    for x, y, w, h in boxes.values():
        xs += [x - w / 2, x + w / 2]
        ys += [y - h / 2, y + h / 2]
    for edge, pieces, at in links:
        for piece in pieces:
            xs += [p[0] for p in piece]
            ys += [p[1] for p in piece]
        if at:
            w, h = label_size(edge.label)
            xs += [at[0] - w / 2, at[0] + w / 2]
            ys += [at[1] - h / 2, at[1] + h / 2]
    if not xs:
        return Layout(boxes, links, 0, 0, 0, 0)
    return Layout(boxes, links, min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def label_size(label: str) -> tuple:
    lines = label.split("\n")
    return max(text_width(t, SMALL) for t in lines) + 8, len(lines) * SMALL * LINE + 4


def bezier(piece: tuple, t: float) -> tuple:
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = piece
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
    return a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3


def overlap(a: tuple, b: tuple) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def inside(p: tuple, box: tuple) -> bool:
    return box[0] - 2 <= p[0] <= box[2] + 2 and box[1] - 2 <= p[1] <= box[3] + 2


# ----------------------------------------------------------------------------------------------
# Drawing it


def attr(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def draw(graph: Graph, title: str) -> str:
    """The graph as an SVG document, with its section heading above and a key to the colors."""
    lay = layout(graph)
    kinds = [k for k in ("recalled", "added", "repaired") if any(n.kind == k for n in graph.nodes.values())]
    key, x = [], 0.0
    for k in kinds:
        key.append((k, x))
        x += 14 + 6 + text_width(k, SMALL) + 18
    inner = max(lay.width, text_width(title, TITLE) * 1.05, x - 18 if kinds else 0)
    top = MARGIN + TITLE * LINE + 12
    width = inner + 2 * MARGIN
    height = top + lay.height + (16 + 14 if kinds else 0) + MARGIN
    dx = MARGIN + (inner - lay.width) / 2 - lay.minx
    dy = top - lay.miny

    def pt(p: tuple) -> str:
        return f"{p[0] + dx:.1f} {p[1] + dy:.1f}"

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="{attr(title)}">',
        f"<title>{escape(title)}</title>",
        '<style>text{font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,'
        f"sans-serif;fill:{INK}}}</style>",
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" '
        'markerHeight="9" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{ARROW_INK}"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{MARGIN}" y="{MARGIN + TITLE:.1f}" font-size="{TITLE}" '
        f'font-weight="600">{escape(title)}</text>',
    ]
    for edge, pieces, _ in lay.links:
        d = f"M {pt(pieces[0][0])} " + " ".join(f"C {pt(c1)} {pt(c2)} {pt(q)}" for _, c1, c2, q in pieces)
        extra = ' stroke-dasharray="6 4"' if edge.style == "dashed" else ""
        extra += ' marker-end="url(#arrow)"' if edge.arrow else ""
        stroke = 3 if edge.style == "thick" else 1.5
        out.append(f'<path d="{d}" fill="none" stroke="{ARROW_INK}" stroke-width="{stroke}"{extra}/>')
    for edge, _, at in lay.links:
        if at:
            w, h = label_size(edge.label)
            x, y = at[0] + dx, at[1] + dy
            out.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
                       'rx="3" fill="#ffffff"/>')
            lines = edge.label.split("\n")
            for j, text in enumerate(lines):
                base = y - h / 2 + 2 + (j + 0.5) * SMALL * LINE + 0.35 * SMALL
                out.append(f'<text x="{x:.1f}" y="{base:.1f}" font-size="{SMALL}" text-anchor="middle" '
                           f'fill="{ARROW_INK}">{escape(text)}</text>')
    for n, (x, y, w, h) in lay.boxes.items():
        node = graph.nodes[n]
        fill, border, ink = RAMPS[node.kind][0]
        x, y = x + dx, y + dy
        out.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
                   f'rx="8" fill="{fill}" stroke="{border}" stroke-width="1.5"/>')
        cursor = y - h / 2 + PAD_Y
        for text in node.main:
            base = cursor + FONT * LINE / 2 + 0.35 * FONT
            out.append(f'<text x="{x:.1f}" y="{base:.1f}" font-size="{FONT}" '
                       f'text-anchor="middle" fill="{ink}">{escape(text)}</text>')
            cursor += FONT * LINE
        for text in node.status:
            base = cursor + SMALL * LINE / 2 + 0.35 * SMALL
            out.append(f'<text x="{x:.1f}" y="{base:.1f}" font-size="{SMALL}" font-style="italic" '
                       f'text-anchor="middle" fill="{border}">{escape(text)}</text>')
            cursor += SMALL * LINE
    ky = top + lay.height + 16
    for k, kx in key:
        fill, border, _ = RAMPS[k][0]
        out.append(f'<rect x="{MARGIN + kx:.1f}" y="{ky:.1f}" width="14" height="14" rx="3" '
                   f'fill="{fill}" stroke="{border}" stroke-width="1.5"/>')
        out.append(f'<text x="{MARGIN + kx + 20:.1f}" y="{ky + 11:.1f}" font-size="{SMALL}">{k}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------------------------
# The map file

FENCE = re.compile(r" {0,3}(`{3,}|~{3,})\s*([\w-]*)")
HEADING = re.compile(r"#{1,6}\s+(.+?)\s*#*\s*")
IMAGE = re.compile(r"!\[[^\]]*\]\((?:\./)?map-[a-z0-9-]+\.svg\)\s*")
DATE = re.compile(r"\s*\(\d{4}-\d{2}-\d{2}\)\s*$")


def short(heading: str) -> str:
    """'Chapter 6: Geometric Brownian motion (2026-09-28)' -> 'Chapter 6'."""
    return DATE.sub("", heading.split(":", 1)[0]).strip() or "Map"


def slug(heading: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", short(heading).lower()).strip("-") or "map"


def render(text: str, folder: Path) -> tuple:
    """Draw every mermaid block in a map. Returns the map with each drawing linked on the line
    under its graph, and a list of (path, svg) to write."""
    lines = text.split("\n")
    blocks = []  # (heading, index of the opening fence, index of the closing fence)
    heading, i = "", 0
    while i < len(lines):
        m = FENCE.fullmatch(lines[i].rstrip())
        if m:
            fence, info = m.group(1), m.group(2).lower()
            closing = re.compile(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*")
            j = i + 1
            while j < len(lines) and not closing.fullmatch(lines[j]):
                j += 1
            if info == "mermaid":
                if j == len(lines):
                    raise MapError(f"line {i + 1}: the mermaid block that starts here is not closed")
                blocks.append((heading, i, j))
            i = j + 1
            continue
        m = HEADING.fullmatch(lines[i])
        if m:
            heading = m.group(1)
        i += 1

    drawings, names = [], set()
    for heading, start, end in blocks:  # read every graph before writing anything
        graph = parse_graph(lines[start + 1:end], start + 2)
        name, n = f"map-{slug(heading)}", 2
        while name in names:
            name, n = f"map-{slug(heading)}-{n}", n + 1
        names.add(name)
        drawings.append((f"{name}.svg", draw(graph, heading or "My map"), heading))

    for (heading, start, end), (name, _, _) in reversed(list(zip(blocks, drawings))):
        image = f"![{short(heading)} map]({name})"
        k = end + 1
        while k < len(lines) and not lines[k].strip():
            k += 1
        if k < len(lines) and IMAGE.fullmatch(lines[k]):
            lines[k] = image
        elif end + 1 < len(lines) and lines[end + 1].strip():
            lines[end + 1:end + 1] = ["", image, ""]
        else:
            lines[end + 1:end + 1] = ["", image]
    return "\n".join(lines), [(folder / name, svg) for name, svg, _ in drawings]


def shown(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def main(argv: list) -> int:
    path = Path(argv[1]) if len(argv) > 1 else MAP
    if not path.is_file():
        print(f"There is no map to draw yet: {shown(path)} does not exist.", file=sys.stderr)
        return 1
    raw = path.read_bytes().decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    try:
        linked, svgs = render(text, path.parent)
    except MapError as err:
        print(f"{shown(path)}, {err}\nNothing was written. Rewrite that line in the form the "
              "skill's example uses, then run this again.", file=sys.stderr)
        return 1
    if not svgs:
        print(f"{shown(path)} has no mermaid graph to draw.")
        return 0
    for out, svg in svgs:
        out.write_bytes(svg.encode("utf-8"))
        print(f"Drew {shown(out)}")
    if linked != text:
        path.write_bytes(linked.replace("\n", eol).encode("utf-8"))
        print(f"Linked the drawings under their graphs in {shown(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
