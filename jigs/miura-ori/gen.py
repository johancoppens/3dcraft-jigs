#!/usr/bin/env python3
"""Writes build.json of the Miura-ori Jig:  python3 gen.py > build.json

A Miura-ori fold panel: a sheet of ROWS x COLS parallelograms, folded rigidly by
3DCraft's own fold solver (feature.fold), with the crease pattern exported for
printing and scoring.

No geometry is computed here. Every point of the crease pattern is a held sketch
point whose coordinates are 3DCraft expressions of the variables a (cell width),
b (cell height) and d = b / tan(gamma) (the zigzag's offset), so the pattern
follows the parameters inside 3DCraft. This script only writes, for each grid
point (i, j), the expression  i * a + (j mod 2) * d,  j * b.

The grid is fixed at ROWS x COLS: feature.fold takes its creases as lines drawn
one by one and does not take the instances of a sketch pattern, so a crease grid
whose size follows a rows or columns parameter cannot be expressed yet
(3dcraft plan/repro/repro-miura-ori-1.json). Change ROWS and COLS here and run
the script again for another grid.

Crease assignment (the classic Miura-ori, seen from the front, +z):
  zigzag line i (1 .. COLS-1): valley for even i, mountain for odd i, its whole length;
  straight line j (1 .. ROWS-1), segment i: valley when i + j is odd, mountain when even.
Every interior vertex then has three creases of one kind and one of the other.
One straight segment (row 1, cell 0) is driven by the fold angle; 3DCraft solves
all the others (the sheet has one degree of freedom).
"""
import json

ROWS = 6
COLS = 8

SHEETS = [  # name, short side, long side (mm)
    ("A4", 210, 297),
    ("A3", 297, 420),
    ("Letter", 215.9, 279.4),
]

COL_PANEL = "#E8E2D0"   # paper


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
        ("fold", "90 deg"),
        ("sheet", "1"),
        ("landscape", "1"),
        ("margin", "10 mm"),
    ]:
        add(["variable.set", {"name": name, "expr": expr}])
    for name, expr in [
        ("rows", str(ROWS)),
        ("cols", str(COLS)),
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
    ]:
        add(["variable.set", {"name": name, "expr": expr}])

    add(["sketch.create", {"plane": "xy", "name": "Crease pattern"}])
    eid = 0
    pt = {}
    for j in range(ROWS + 1):
        for i in range(COLS + 1):
            add(["sketch.point", {"sketch": "Crease pattern", "at": point_expr(i, j)}])
            eid += 1
            pt[i, j] = "e%d" % eid
    loop = ([pt[i, 0] for i in range(COLS + 1)] + [pt[COLS, j] for j in range(1, ROWS + 1)]
            + [pt[i, ROWS] for i in range(COLS - 1, -1, -1)] + [pt[0, j] for j in range(ROWS - 1, 0, -1)])
    add(["sketch.polyline", {"sketch": "Crease pattern", "points": loop, "closed": True}])
    eid += len(loop)
    creases = []
    for j in range(1, ROWS):
        for i in range(COLS):
            add(["sketch.line", {"sketch": "Crease pattern", "from": pt[i, j], "to": pt[i + 1, j], "construction": True}])
            eid += 1
            creases.append({"line": "e%d" % eid, "kind": "valley" if (i + j) % 2 else "mountain"})
    for i in range(1, COLS):
        for j in range(ROWS):
            add(["sketch.line", {"sketch": "Crease pattern", "from": pt[i, j], "to": pt[i, j + 1], "construction": True}])
            eid += 1
            creases.append({"line": "e%d" % eid, "kind": "valley" if i % 2 == 0 else "mountain"})
    creases[0]["angle"] = "fold"   # row 1, cell 0: a valley

    add(["feature.fill", {"sketch": "Crease pattern", "name": "Flat sheet"}])
    add(["feature.visible", {"feature": "Flat sheet", "visible": False}])
    add(["feature.fold", {"sketch": "Crease pattern", "name": "Miura-ori", "creases": creases}])
    add(["body.appearance", {"body": "Miura-ori", "color": COL_PANEL}])

    add(["assert.add", {"name": "the folded sheet keeps the flat area", "measure": "area", "of": "Miura-ori", "eq": "flatArea"}])
    add(["assert.add", {"name": "the flat sheet is rows x cols parallelograms of a x b", "measure": "area", "of": "Flat sheet", "eq": "flatArea"}])
    add(["assert.add", {"name": "one facet per cell", "measure": "count",
                        "of": {"kind": "face", "where": {"in": "Miura-ori"}}, "eq": "rows * cols"}])
    add(["assert.add", {"name": "the pattern fits the sheet's width inside the margin", "measure": "extent",
                        "of": "Flat sheet", "axis": "x", "max": "usableW"}])
    add(["assert.add", {"name": "the pattern fits the sheet's height inside the margin", "measure": "extent",
                        "of": "Flat sheet", "axis": "y", "max": "usableH"}])

    pub = [
        ("cellW", {"label": "Cell width", "description": "Length of the parallelograms' straight sides (along the straight creases)",
                   "group": "Pattern", "min": "10 mm", "max": "floor((usableW - d) / cols / (0.5 mm)) * (0.5 mm)", "step": "0.5 mm", "unit": "mm"}),
        ("cellH", {"label": "Cell height", "description": "Distance between two straight creases (the row pitch)",
                   "group": "Pattern", "min": "10 mm", "max": "floor(usableH / rows / (0.5 mm)) * (0.5 mm)", "step": "0.5 mm", "unit": "mm"}),
        ("gamma", {"label": "Parallelogram angle", "description": "Acute angle of the parallelograms; 90 deg would be a plain grid, which does not fold rigidly",
                   "group": "Pattern", "min": "45 deg", "max": "85 deg", "step": "1 deg", "unit": "deg"}),
        ("fold", {"label": "Fold", "description": "Fold angle of the straight creases: 0 is flat, 179 deg almost folded flat; every other crease follows",
                  "group": "Fold", "min": "0 deg", "max": "179 deg", "step": "1 deg", "unit": "deg"}),
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
        "description": "A Miura-ori panel of %d x %d parallelograms that folds in and out with one slider: one crease is "
                       "driven, 3DCraft solves the rest. Cell size, parallelogram angle, paper (A4, A3, Letter) and margin; "
                       "the crease pattern exports as SVG or DXF, mountains red dash-dot, valleys blue dashed, to print "
                       "and score or laser-score." % (ROWS, COLS),
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
