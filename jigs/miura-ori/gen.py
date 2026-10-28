#!/usr/bin/env python3
"""Writes build.json of the Miura-ori Jig:  python3 gen.py > build.json

A Miura-ori fold panel: a sheet of rows x cols parallelograms, folded rigidly by
3DCraft's own fold solver (feature.fold), with the crease pattern exported for
printing and scoring.

No geometry is computed here. Every point of the crease pattern is a held sketch
point whose coordinates are 3DCraft expressions of the variables a (cell width),
b (cell height), d = b / tan(gamma) (the zigzag's offset), rows and cols, so the
pattern follows the parameters inside 3DCraft: P(i, j) = (i a + mod(j, 2) d, j b).

The grid follows rows and cols through sketch patterns: each kind of crease piece
(zigzag up-right and up-left, in odd and in even columns; straight, in odd and in
even rows and cells) is one seed line repeated every two cells and every two rows
(sketch.pattern, counts from rows and cols), and the fold takes the seed with all
its copies as creases ("e33[*]"). The outline's zigzag edges are patterns too.

Crease assignment (the classic Miura-ori, seen from the front, +z):
  zigzag line i (1 .. cols-1): valley for even i, mountain for odd i, its whole length;
  straight line j (1 .. rows-1), segment i: valley when i + j is odd, mountain when even.
Every interior vertex then has three creases of one kind and one of the other.
The straight valleys of the odd rows' even cells (one seed line and its copies)
are driven by the fold angle; 3DCraft solves the other straight creases and every
zigzag crease (the sheet has one degree of freedom, and every straight crease of a
Miura-ori folds by the same angle). At 180 deg the sheet is folded flat, with its
layers.
"""
import json

ROWS = 6        # the defaults
COLS = 8
MAX_ROWS = 12   # the solver takes at most 400 crease angles: (rows - 1) cols + (cols - 1) rows = 264 at 12 x 12
MAX_COLS = 12

SHEETS = [  # name, short side, long side (mm)
    ("A4", 210, 297),
    ("A3", 297, 420),
    ("Letter", 215.9, 279.4),
]

COL_PANEL = "#E8E2D0"   # paper
# The folded panel: the body of Panel (levelled) below 180 deg, of the fold itself when folded flat (a flat-folded
# body is not built on, so the levelling transform is off then).
PANEL = {"kind": "body", "where": {"not": {"name": "Flat sheet"}}}


def mul(k, v):
    if k == 0:
        return "0 mm"
    return v if k == 1 else "%d * %s" % (k, v)


def point_expr(i, j):
    x = mul(i, "a")
    if j % 2:
        x = "d" if i == 0 else x + " + d"
    return [x, mul(j, "b")]


def main():
    cmds = []
    add = cmds.append
    add(["table.set", {"name": "sheets", "columns": ["sheet", {"name": "short", "unit": "mm"}, {"name": "long", "unit": "mm"}],
                       "rows": [[n, s, l] for n, s, l in SHEETS]}])
    for name, expr in [
        ("cellW", "30 mm"),
        ("cellH", "28 mm"),
        ("gamma", "70 deg"),
        ("rows", str(ROWS)),
        ("cols", str(COLS)),
        ("fold", "90 deg"),
        ("sheet", "1"),
        ("landscape", "1"),
        ("margin", "10 mm"),
    ]:
        add(["variable.set", {"name": name, "expr": expr}])
    for name, expr in [
        ("a", "cellW"),
        ("b", "cellH"),
        ("d", "b / tan(gamma)"),                                     # zigzag offset
        ("paperW", "if(landscape, sheets[sheet].long, sheets[sheet].short)"),
        ("paperH", "if(landscape, sheets[sheet].short, sheets[sheet].long)"),
        ("usableW", "paperW - 2 * margin"),
        ("usableH", "paperH - 2 * margin"),
        ("panelW", "cols * a + d"),                                  # flat pattern's box
        ("panelH", "rows * b"),
        ("flatArea", "rows * cols * a * b"),                         # each parallelogram is a * b
        ("fi", "2 * floor(cols / 4) + 1"),                           # the facet that stays: cell fi (odd)
        ("fj", "2 * floor(rows / 4)"),                               # of row fj (even), near the middle
    ]:
        add(["variable.set", {"name": name, "expr": expr}])

    # The crease pattern, built from seeds and sketch patterns so that it follows rows and cols.
    # Every point is held by expressions; P(i, j) = (i a + mod(j, 2) d, j b).
    sk = "Crease pattern"
    add(["sketch.create", {"plane": "xy", "name": sk}])
    ids = {"n": 0}

    def line(frm, to, construction):
        add(["sketch.line", {"sketch": sk, "from": frm, "to": to, "construction": construction}])
        ids["n"] += 3          # two held points and the line
        return "e%d" % ids["n"]

    def pattern(entity, count, step, count2=None, step2=None):
        p = {"sketch": sk, "entities": [entity], "count": count, "step": step}
        if count2 is not None:
            p.update({"count2": count2, "step2": step2})
        add(["sketch.pattern", p])

    # The outline: the bottom and top edges, and the zigzag left (x = 0) and right (x = cols a) edges, each a
    # pair of seeds (up-right from an even row, up-left from an odd row) repeated every two rows.
    line(["0 mm", "0 mm"], ["cols * a", "0 mm"], False)
    line(["mod(rows, 2) * d", "rows * b"], ["cols * a + mod(rows, 2) * d", "rows * b"], False)
    for x0 in ["0 mm", "cols * a"]:
        up = line([x0, "0 mm"], [x0 + " + d", "b"], False)
        pattern(up, "ceil(rows / 2)", ["0 mm", "2 * b"])
        dn = line([x0 + " + d", "b"], [x0, "2 * b"], False)
        pattern(dn, "floor(rows / 2)", ["0 mm", "2 * b"])

    creases = []
    # Zigzag creases, columns i = 1 .. cols - 1: mountains for odd i, valleys for even i, their whole length.
    for i0, kind, count in [(1, "mountain", "floor(cols / 2)"), (2, "valley", "floor((cols - 1) / 2)")]:
        x0 = mul(i0, "a")
        up = line([x0, "0 mm"], [x0 + " + d", "b"], True)
        pattern(up, count, ["2 * a", "0 mm"], "ceil(rows / 2)", ["0 mm", "2 * b"])
        dn = line([x0 + " + d", "b"], [x0, "2 * b"], True)
        pattern(dn, count, ["2 * a", "0 mm"], "floor(rows / 2)", ["0 mm", "2 * b"])
        creases += [{"line": up + "[*]", "kind": kind}, {"line": dn + "[*]", "kind": kind}]
    # Straight creases, rows j = 1 .. rows - 1, cells i = 0 .. cols - 1: a valley when i + j is odd.
    for j0, count2 in [(1, "floor(rows / 2)"), (2, "floor((rows - 1) / 2)")]:
        for i0, count in [(0, "ceil(cols / 2)"), (1, "floor(cols / 2)")]:
            a0, b0 = point_expr(i0, j0), point_expr(i0 + 1, j0)
            seed = line(a0, b0, True)
            pattern(seed, count, ["2 * a", "0 mm"], count2, ["0 mm", "2 * b"])
            crease = {"line": seed + "[*]", "kind": "valley" if (i0 + j0) % 2 else "mountain"}
            if (i0, j0) == (0, 1):
                # The drive: the valleys of the odd rows' even cells fold by the slider. In a Miura-ori every
                # straight crease folds by the same angle, so these agree with each other; driving only one of
                # them leaves the solver undecided on long, low panels (3 rows of 8 to 12 columns: "the fold is
                # ambiguous"; 3DCraft plan/repro/repro-miura-ori-3.json).
                crease["angle"] = "fold"
            creases.append(crease)

    add(["feature.fill", {"sketch": "Crease pattern", "name": "Flat sheet"}])
    add(["feature.visible", {"feature": "Flat sheet", "visible": False}])
    # The facet that stays: the middle of cell 3 of row 2 (a row of even j, whose zigzag edge runs along
    # (cos gamma, sin gamma)).
    add(["feature.fold", {"sketch": "Crease pattern", "name": "Miura-ori", "creases": creases,
                          "fixed": ["(fi + 0.5) * a + 0.5 * d", "(fj + 0.5) * b"]}])
    add(["body.appearance", {"body": "Miura-ori", "color": COL_PANEL}])
    # Lay the folded panel level: its facets lean by theta = atan(tan(fold / 2) / cos(gamma)) (half the
    # zigzag creases' fold angle) about their zigzag edge, so turning the panel back by theta about that
    # edge's direction puts its mean plane, the plane of a zigzag crease line, on z = 0.
    add(["variable.set", {"name": "theta", "expr": "if(fold < 180 deg, atan(tan(fold / 2) / cos(gamma)), 0 deg)"}])
    add(["feature.transform", {"source": "Miura-ori", "name": "Panel", "angle": "theta",
                               "axis": ["cos(gamma)", "sin(gamma)", "0"], "pivot": ["(fi + 0.5) * a + 0.5 * d", "(fj + 0.5) * b", "0 mm"],
                               "when": "fold < 180 deg"}])

    add(["assert.add", {"name": "every cell is in the folded panel (area rows x cols x a x b)", "measure": "area", "of": PANEL, "eq": "flatArea"}])
    add(["assert.add", {"name": "the flat sheet is rows x cols parallelograms of a x b", "measure": "area", "of": "Flat sheet", "eq": "flatArea"}])
    add(["assert.add", {"name": "one facet per cell", "measure": "count",
                        "of": {"kind": "face", "where": {"not": {"in": "Flat sheet"}}}, "eq": "rows * cols"}])
    # The panel's thickness when folded, by the closed form (Schenk and Guest 2013): a straight crease of
    # length a, at gamma to the zigzag edge, leans by theta, and mountains and valleys alternate above and
    # below the mean plane. Checks the solved fold against the kinematics, and that the panel lies level.
    add(["assert.add", {"name": "folded thickness a sin(gamma) sin(theta), by the closed form", "measure": "extent",
                        "of": PANEL, "axis": "z", "eq": "a * sin(gamma) * sin(theta)", "tol": "0.001 mm"}])
    add(["assert.add", {"name": "the panel lies level about z = 0", "measure": "boxMax",
                        "of": PANEL, "axis": "z", "eq": "a * sin(gamma) * sin(theta) / 2", "tol": "0.001 mm"}])
    # The crease pattern itself (fold.check and the flat-folded state): necessary local conditions at every
    # interior vertex, and the whole pattern folding flat with an order of the layers.
    add(["assert.add", {"name": "Kawasaki holds at every interior vertex", "measure": "kawasakiFails", "of": "Miura-ori", "eq": "0"}])
    add(["assert.add", {"name": "Maekawa holds at every interior vertex", "measure": "maekawaFails", "of": "Miura-ori", "eq": "0"}])
    add(["assert.add", {"name": "the pattern folds flat (an order of the layers exists)", "measure": "flatFoldable", "of": "Miura-ori", "is": True}])
    add(["assert.add", {"name": "the pattern fits the sheet's width inside the margin", "measure": "extent",
                        "of": "Flat sheet", "axis": "x", "max": "usableW"}])
    add(["assert.add", {"name": "the pattern fits the sheet's height inside the margin", "measure": "extent",
                        "of": "Flat sheet", "axis": "y", "max": "usableH"}])

    pub = [
        ("rows", {"label": "Rows", "description": "Number of rows of parallelograms (straight creases between them)",
                  "group": "Pattern", "kind": "integer", "min": "3", "max": "min(%d, floor(usableH / (10 mm)))" % MAX_ROWS}),
        ("cols", {"label": "Columns", "description": "Number of columns of parallelograms (zigzag creases between them)",
                  "group": "Pattern", "kind": "integer", "min": "3", "max": "min(%d, floor((usableW - d) / (10 mm)))" % MAX_COLS}),
        ("cellW", {"label": "Cell width", "description": "Length of the parallelograms' straight sides (along the straight creases)",
                   "group": "Pattern", "min": "10 mm", "max": "floor((usableW - d) / cols / (0.5 mm)) * (0.5 mm)", "step": "0.5 mm", "unit": "mm"}),
        ("cellH", {"label": "Cell height", "description": "Distance between two straight creases (the row pitch)",
                   "group": "Pattern", "min": "10 mm", "max": "floor(usableH / rows / (0.5 mm)) * (0.5 mm)", "step": "0.5 mm", "unit": "mm"}),
        ("gamma", {"label": "Parallelogram angle", "description": "Acute angle of the parallelograms; nearer 90 deg the cells stack deeper when folded flat",
                   "group": "Pattern", "min": "45 deg", "max": "80 deg", "step": "1 deg", "unit": "deg"}),
        ("fold", {"label": "Fold", "description": "Fold angle of the straight creases: 0 is flat, 180 deg folded flat; all other creases follow",
                  "group": "Fold", "min": "0 deg", "max": "180 deg", "step": "1 deg", "unit": "deg"}),
        ("sheet", {"label": "Paper", "description": "Paper size for the printed crease pattern (table sheets)",
                   "group": "Paper", "kind": "choice", "choicesFrom": "sheets"}),
        ("landscape", {"label": "Landscape", "description": "Print across the long side of the paper",
                       "group": "Paper", "kind": "boolean"}),
        ("margin", {"label": "Margin", "description": "Free paper round the pattern (most printers need 5 mm or more)",
                    "group": "Paper", "min": "0 mm", "max": "30 mm", "step": "1 mm", "unit": "mm"}),
    ]
    for order, (name, p) in enumerate(pub, 1):
        add(["variable.publish", dict({"name": name, "order": order}, **p)])

    add(["document.info", {
        "title": "Miura-ori fold panel",
        "description": "A Miura-ori panel that folds in and out with one slider, from flat to folded flat: one crease is "
                       "driven, 3DCraft solves the rest. Rows, columns, cell size, parallelogram angle, paper (A4, A3, Letter) "
                       "and margin; "
                       "the crease pattern exports as SVG or DXF, mountains red dash-dot, valleys blue dashed, to print "
                       "and score or laser-score.",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "tags": ["origami", "miura-ori", "fold", "paper", "laser"],
    }])
    add(["jig.export", {"path": "dist/miura-ori.3dcraftjig"}])
    print("[")
    print(",\n".join(json.dumps(c) for c in cmds))
    print("]")


if __name__ == "__main__":
    main()
