#!/usr/bin/env python3
"""Writes build.json of the Miura-ori Jig:  python3 gen.py > build.json

A Miura-ori fold panel: a sheet of rows x cols parallelograms, folded rigidly by
3DCraft's own fold solver (feature.fold), of paper or of thick panels on a membrane
(feature.fold with panels), with the crease pattern exported for printing and scoring.

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
# The fold itself is solved by 3DCraft's sparse solve far past these (27 x 38 cells in under 2 s); the limit is
# the flat-folded state's order of layers, which 3DCraft searches within a work allowance (flat-foldability is
# NP-hard) and which the assertion `flatFoldable` and the Fold at 180 deg need. Measured at 3DCraft 0dc5efb6:
# every grid up to 12 x 12 is decided for angles up to 80 deg, and up to 14 rows of 16 columns for angles up to
# 65 deg; past 12 x 12, tall narrow cells at 70 deg run out (12 x 14 cells of 10 x 33 mm: 144 facets on one another).
MAX_ROWS = 14
MAX_COLS = 16
SMALL = 12      # the grid up to which the angle may go to 80 deg
# The angle's range follows the grid, so the columns' range must not follow the angle (they would chase each
# other): it allows for the largest zigzag offset, d = b / tan(45 deg) = b, whatever the angle.

SHEETS = [  # name, short side, long side (mm)
    ("A4", 210, 297),
    ("A3", 297, 420),
    ("Letter", 215.9, 279.4),
]

COL_PANEL = "#E8E2D0"   # paper
COL_BOARD = "#C9A672"   # card or plywood panels
# The thick-panel folds: name, side of the sketch the panels are on, when on.
THICK = [("Thick panels", "back", "thick && !panelFront"), ("Thick panels (front)", "front", "thick && panelFront")]
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
        ("thick", "0"),
        ("tPanel", "1.5 mm"),
        ("cPanel", "1.5 mm"),
        ("panelFront", "0"),
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
        # Thick panels: the zigzag creases fold fastest, by 2 atan(tan(fold / 2) / cos(gamma)), and the panels
        # beside a crease folded towards them meet at 2 atan(cPanel / tPanel); so the panels meet when the fold
        # reaches foldLimit. The Fold slider stops at the last whole degree below it.
        ("foldLimit", "2 * atan(cos(gamma) * cPanel / tPanel)"),
        ("foldMax", "if(thick, max(0, ceil(foldLimit / (1 deg)) - 1) * (1 deg), 180 deg)"),
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
    # The facet that stays: the middle of cell fi of row fj (a row of even j, whose zigzag edge runs along
    # (cos gamma, sin gamma)). The sheet (paper, no thickness) is on without thick panels; with them, the same
    # crease pattern folds as thick panels on a membrane (the fabric hinge on the sheet's plane), on the back
    # or the front. fold.check and the crease pattern's export read the sheet's fold even while it is off.
    fixed = ["(fi + 0.5) * a + 0.5 * d", "(fj + 0.5) * b"]
    add(["feature.fold", {"sketch": "Crease pattern", "name": "Miura-ori", "creases": creases,
                          "fixed": fixed, "when": "!thick"}])
    add(["body.appearance", {"body": "Miura-ori", "color": COL_PANEL}])
    for name, side, when in THICK:
        add(["feature.fold", {"sketch": "Crease pattern", "name": name, "creases": creases, "fixed": fixed,
                              "panels": {"thickness": "tPanel", "clearance": "cPanel", "side": side}, "when": when}])
        add(["body.appearance", {"body": name, "color": COL_BOARD, "roughness": 0.8}])
    # Lay the folded panel level: its facets lean by theta = atan(tan(fold / 2) / cos(gamma)) (half the
    # zigzag creases' fold angle) about their zigzag edge, so turning the panel back by theta about that
    # edge's direction puts its mean plane, the plane of a zigzag crease line, on z = 0.
    add(["variable.set", {"name": "theta", "expr": "if(fold < 180 deg, atan(tan(fold / 2) / cos(gamma)), 0 deg)"}])
    for source, name, when in [("Miura-ori", "Panel", "!thick && fold < 180 deg")] + \
            [(n, "Level " + n, w) for n, _, w in THICK]:
        add(["feature.transform", {"source": source, "name": name, "angle": "theta",
                                   "axis": ["cos(gamma)", "sin(gamma)", "0"], "pivot": fixed + ["0 mm"], "when": when}])

    add(["assert.add", {"name": "every cell is in the folded panel (area rows x cols x a x b)", "measure": "area", "of": PANEL,
                        "eq": "flatArea", "when": "!thick"}])
    add(["assert.add", {"name": "the flat sheet is rows x cols parallelograms of a x b", "measure": "area", "of": "Flat sheet", "eq": "flatArea"}])
    add(["assert.add", {"name": "one facet per cell", "measure": "count",
                        "of": {"kind": "face", "where": {"not": {"in": "Flat sheet"}}}, "eq": "rows * cols", "when": "!thick"}])
    # Thick panels. Each panel is its parallelogram set back by cPanel from every crease (not the outline):
    # base a and height b, it keeps (b - k cPanel) between its straight sides and (a sin(gamma) - m cPanel) between
    # its zigzag sides, k and m the creases among them, so its area is the product over sin(gamma). Summed over
    # the grid the rows and columns separate: every inside line takes cPanel off the two rows (columns) beside it.
    add(["assert.add", {"name": "thick panels: one six-sided prism per cell", "measure": "count",
                        "of": {"kind": "face", "where": {"not": {"in": "Flat sheet"}}}, "eq": "6 * rows * cols", "when": "thick"}])
    add(["assert.add", {"name": "thick panels: volume tPanel (rows b - 2 c (rows - 1)) (cols a sin(gamma) - 2 c (cols - 1)) / sin(gamma)",
                        "measure": "volume", "of": PANEL, "when": "thick",
                        "eq": "tPanel * (rows * b - 2 * cPanel * (rows - 1)) * (cols * a * sin(gamma) - 2 * cPanel * (cols - 1)) / sin(gamma)"}])
    # The panel's thickness when folded, by the closed form (Schenk and Guest 2013): a straight crease of
    # length a, at gamma to the zigzag edge, leans by theta, and mountains and valleys alternate above and
    # below the mean plane. Checks the solved fold against the kinematics, and that the panel lies level.
    add(["assert.add", {"name": "folded thickness a sin(gamma) sin(theta), by the closed form", "measure": "extent",
                        "of": PANEL, "axis": "z", "eq": "a * sin(gamma) * sin(theta)", "tol": "0.001 mm", "when": "!thick"}])
    add(["assert.add", {"name": "the panel lies level about z = 0", "measure": "boxMax",
                        "of": PANEL, "axis": "z", "eq": "a * sin(gamma) * sin(theta) / 2", "tol": "0.001 mm", "when": "!thick"}])
    # Thick panels, levelled: every facet leans by theta, so a panel reaches tPanel cos(theta) past the sheet on its
    # side, and the set-back from a zigzag crease lowers a panel's top (or lifts its bottom) by cPanel sin(theta).
    # The odd zigzag creases are on top, the even ones below; the left outline (line 0) is below and the right
    # one (line cols) on top when cols is odd: a panel along the outline is not set back there.
    add(["assert.add", {"name": "thick panels: folded height a sin(gamma) sin(theta) + tPanel cos(theta) - c sin(theta) for even cols",
                        "measure": "extent", "of": PANEL, "axis": "z", "tol": "0.001 mm", "when": "thick",
                        "eq": "a * sin(gamma) * sin(theta) + tPanel * cos(theta) - mod(cols + 1, 2) * cPanel * sin(theta)"}])
    add(["assert.add", {"name": "thick panels on the back: the bottom at -a sin(gamma) sin(theta) / 2 - tPanel cos(theta)",
                        "measure": "boxMin", "of": PANEL, "axis": "z", "tol": "0.001 mm", "when": "thick && !panelFront",
                        "eq": "-a * sin(gamma) * sin(theta) / 2 - tPanel * cos(theta)"}])
    add(["assert.add", {"name": "thick panels on the front: the bottom at -a sin(gamma) sin(theta) / 2",
                        "measure": "boxMin", "of": PANEL, "axis": "z", "tol": "0.001 mm", "when": "thick && panelFront",
                        "eq": "-a * sin(gamma) * sin(theta) / 2"}])
    add(["assert.add", {"name": "thick panels: the fold is below the closed-form limit 2 atan(cos(gamma) c / t) (guards the slider's rounding; that the panels clear is 3DCraft's own check)",
                        "measure": "value", "expr": "foldLimit - fold", "min": "0.001 deg", "when": "thick"}])
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
                  "group": "Pattern", "kind": "integer", "min": "3", "max": "min(%d, floor((usableW - b) / (10 mm)))" % MAX_COLS}),
        ("cellW", {"label": "Cell width", "description": "Length of the parallelograms' straight sides (along the straight creases)",
                   "group": "Pattern", "min": "10 mm", "max": "floor((usableW - d) / cols / (0.5 mm)) * (0.5 mm)", "step": "0.5 mm", "unit": "mm"}),
        ("cellH", {"label": "Cell height", "description": "Distance between two straight creases (the row pitch)",
                   "group": "Pattern", "min": "10 mm", "max": "floor(usableH / rows / (0.5 mm)) * (0.5 mm)", "step": "0.5 mm", "unit": "mm"}),
        ("gamma", {"label": "Parallelogram angle", "description": "Acute angle of the parallelograms; nearer 90 deg the cells stack deeper when folded flat",
                   "group": "Pattern", "min": "45 deg", "max": "if(rows <= %d && cols <= %d, 80 deg, 65 deg)" % (SMALL, SMALL), "step": "1 deg", "unit": "deg"}),
        ("fold", {"label": "Fold", "description": "Fold angle of the straight creases: 0 is flat, 180 deg folded flat (paper; thick panels stop where they meet); all other creases follow",
                  "group": "Fold", "min": "0 deg", "max": "foldMax", "step": "1 deg", "unit": "deg"}),
        ("thick", {"label": "Thick panels", "description": "Rigid panels of card or plywood joined by a fabric hinge, instead of paper",
                   "group": "Panels", "kind": "boolean"}),
        ("tPanel", {"label": "Panel thickness", "description": "Thickness of the card or plywood panels",
                    "group": "Panels", "min": "0.3 mm", "max": "6 mm", "step": "0.1 mm", "unit": "mm"}),
        ("cPanel", {"label": "Hinge clearance", "description": "How far each panel stands back from every crease (the bare fabric between two panels is twice this); more clearance lets thick panels fold further",
                    "group": "Panels", "min": "0.3 mm", "max": "min(10 mm, floor(min(b, a * sin(gamma)) / 4 / (0.1 mm)) * (0.1 mm))", "step": "0.1 mm", "unit": "mm"}),
        ("panelFront", {"label": "Panels on the front", "description": "Glue the panels on the printed side (the front) instead of the back",
                        "group": "Panels", "kind": "boolean"}),
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
                       "and margin; paper, or thick card or plywood panels on a fabric hinge that fold as far as they clear each other; "
                       "the crease pattern exports as SVG or DXF, mountains red dash-dot, valleys blue dashed, to print "
                       "and score or laser-score.",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "tags": ["origami", "miura-ori", "fold", "paper", "laser", "thick panels", "plywood"],
    }])
    add(["jig.export", {"path": "dist/miura-ori.3dcraftjig"}])
    print("[")
    print(",\n".join(json.dumps(c) for c in cmds))
    print("]")


if __name__ == "__main__":
    main()
