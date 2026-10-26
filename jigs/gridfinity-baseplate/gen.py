#!/usr/bin/env python3
"""Writes build.json of the gridfinity-baseplate Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written. The Gridfinity numbers and the
socket and foot profiles come from scripts/gridfinitylib.py, shared with gridfinity-bin, so a bin from
that Jig seats in a plate from this one (a bin's foot is placed in the first cell and checked).

Layout. The drawer's inside, less a clearance, is filled with as many 42 mm cells as fit with at least
MIN_FILL on each side; what is left is a filler strip on both sides (the plate is centred). Along each
axis the cells are split into pieces that fit the print bed: the first pieces hold k cells each, the
last one the rest, and the end pieces also carry the filler, so the first piece of a row is the widest.
The pieces lie assembled (they touch along straight joints at cell boundaries), each its own body, in up
to SLOTS x SLOTS slots switched on by `when`.

Every cut is made once for the whole plate (the cells with their holes, the connector pockets along
every joint) and taken out of each piece's block (subtract, keeping the tool), so a piece only costs a
few features.

Connectors: bowtie (butterfly) clips pressed into pockets on the underside across every joint, one at the
middle of every cell along it (the pieces stay alike and the top flat), or dovetail tabs on the joint
edges (the piece on the left or in front carries the tab, the next one the slot), or none.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import gridfinitylib as gf  # noqa: E402

ID = "gridfinity-baseplate"
SLOTS = 5
MIN_FILL = 4.0          # mm, the thinnest filler strip; less and a cell is left out instead
# Bowtie clip (butterfly key): 18 mm across the joint, 12 mm wide at its ends, 6 mm at the neck, 2 mm thick.
BT_L, BT_END, BT_NECK, BT_T = 9.0, 6.0, 3.0, 2.0      # half length, half widths, thickness
# Dovetail tab: 8 mm deep, 8 mm wide at the joint, 12 mm at its end (a 1:4 flare, 14 deg).
DT_L, DT_NECK, DT_END = 8.0, 4.0, 6.0
CLR_MAX = 0.4
WALL_MIN = 0.8          # two perimeters of a 0.4 mm nozzle
FLOOR = 3.4             # Light and Solid: a 2.4 mm magnet pocket on 1 mm (rebuilt: h_skel 1 + 2.4)


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


def W(feature, expr):
    return ["feature.when", {"feature": feature, "expr": expr}]


def unit(v):
    return "%.6g mm" % v


def offset_polygon(pts):
    """Miter offset of a counter-clockwise polygon by 1: for each vertex the vector to add, times the
    offset distance, to move every edge out by that distance."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        normals = []
        for a, b in ((p0, p1), (p1, p2)):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            normals.append((dy / ln, -dx / ln))        # outward for a counter-clockwise polygon
        (ax, ay), (bx, by) = normals
        d = 1 + ax * bx + ay * by
        out.append(((ax + bx) / d, (ay + by) / d))
    return out


def poly_expr(pts, off, c, u0, v0, swap):
    """Points of a polygon in joint axes (u across the joint, v along it), offset by c (an expression),
    placed at (u0, v0) (expressions), as sketch coordinates [x, y] (swap: u is y)."""
    res = []
    for (u, v), (mu, mv) in zip(pts, off):
        U = "(%s) + %s + %.6g * (%s)" % (u0, unit(u), mu, c)
        Vv = "(%s) + %s + %.6g * (%s)" % (v0, unit(v), mv, c)
        res.append([Vv, U] if swap else [U, Vv])
    return res


BOWTIE = [(-BT_L, -BT_END), (0, -BT_NECK), (BT_L, -BT_END), (BT_L, BT_END), (0, BT_NECK), (-BT_L, BT_END)]
# The tab reaches 1 mm back into its own piece (so it joins it) and DT_L into the next one.
DT_BACK = 1.0
_s = (DT_END - DT_NECK) / DT_L
TAB = [(-DT_BACK, -(DT_NECK - _s * DT_BACK)), (DT_L, -DT_END), (DT_L, DT_END), (-DT_BACK, DT_NECK - _s * DT_BACK)]
# The slot for it: the tab offset by the fit, starting at the joint (u = 0): its side lines moved out by
# the fit meet u = 0 at half width DT_NECK + fit * (length of a side / DT_L).
_side = math.hypot(DT_L, DT_END - DT_NECK)
_ofs = offset_polygon(TAB)
SLOT = [(0, -DT_NECK), (DT_L, -DT_END), (DT_L, DT_END), (0, DT_NECK)]
SLOT_OFF = [(0, -_side / DT_L), _ofs[1], _ofs[2], (0, _side / DT_L)]
# Bowtie: polygon order above is clockwise in (u, v)? Make sure it is counter-clockwise.


def ccw(pts):
    a = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
    return a > 0


assert ccw(BOWTIE) and ccw(TAB) and ccw(SLOT)
BOWTIE_OFF = offset_polygon(BOWTIE)
TAB_OFF = [(0, 0)] * len(TAB)

INPUTS = [
    ("dw", "400 mm"), ("dd", "500 mm"), ("fitD", "0.5 mm"), ("bed", "256 mm"),
    ("style", "1"), ("magnets", "0"), ("screws", "0"), ("conn", "1"), ("clr", "0.15 mm"),
]


def axis(a, size):
    """The layout along one axis (a = x or y): cells, filler, cells per piece, pieces, cells in the last."""
    return [
        ("W" + a, "%s - fitD" % size),                                   # what the plate fills
        ("c" + a, "floor((W%s - %s) / grid)" % (a, unit(2 * MIN_FILL))),  # whole cells
        ("f" + a, "(W%s - c%s * grid) / 2" % (a, a)),                    # filler on each side
        # most cells an end piece can hold: its filler on one side, a dovetail's tabs on the other
        ("k0" + a, "floor((bed - f%s - if(conn == 2, %s, 0 mm)) / grid)" % (a, unit(DT_L))),
        ("p0" + a, "if(c%s * grid + 2 * f%s <= bed, 1, max(2, ceil(c%s / k0%s)))" % (a, a, a, a)),
        ("k" + a, "ceil(c%s / p0%s)" % (a, a)),                          # cells in every piece but the last
        ("p" + a, "ceil(c%s / k%s)" % (a, a)),                           # pieces
        ("l" + a, "c%s - (p%s - 1) * k%s" % (a, a, a)),                  # cells in the last piece
    ]


def slot_vars(a, i):
    """Start and size of slot i along axis a."""
    return [
        ("s%s%d" % (a, i), "if(%d == 0, 0 mm, f%s + %d * k%s * grid)" % (i, a, i, a)),
        ("w%s%d" % (a, i), "if(p%s == 1, W%s, if(%d == 0, f%s + k%s * grid, if(%d == p%s - 1, l%s * grid + f%s, k%s * grid)))"
         % (a, a, i, a, a, i, a, a, a, a)),
    ]


DERIVED = [
    ("grid", unit(gf.GRID)),
    ("hb", "if(style == 3, %s, %s)" % (unit(gf.WEIGHT_BOTTOM), unit(FLOOR))),   # floor under the sockets
    ("Hp", "hb + %s" % unit(gf.SOCKET_H - gf.RIDGE_CUT)),                        # the plate's height
    ("bowtie", "conn == 1"),
    ("dove", "conn == 2"),
    # Light: a window through the floor of every cell, leaving a rim that holds the magnets and the
    # connector pockets with WALL_MIN round them.
    ("rim", "max(3.5 mm, if(magnets, %s, 0 mm), if(bowtie, %s + clr, 0 mm), if(dove, %s + clr, 0 mm))"
     % (unit(gf.HOLE_IN + gf.MAGNET_D / 2 + WALL_MIN), unit(BT_L + WALL_MIN), unit(DT_L + WALL_MIN))),
    ("win", "grid - 2 * rim"),
] + axis("x", "dw") + axis("y", "dd") + [
    ("x0", "fx + grid / 2"),            # centre of the first cell
    ("y0", "fy + grid / 2"),
]
for _i in range(SLOTS):
    DERIVED += slot_vars("x", _i)
for _i in range(SLOTS):
    DERIVED += slot_vars("y", _i)
DERIVED += [
    ("pieces", "px * py"),
    ("nclips", "if(bowtie, cy * (px - 1) + cx * (py - 1), 0)"),
    ("ntabs", "if(dove, cy * (px - 1) + cx * (py - 1), 0)"),
]


def main():
    s = []
    for name, expr in INPUTS + DERIVED:
        s.append(V(name, expr))

    # One cell's cut, at the first cell: the socket, then what goes with it.
    s += gf.socket_cutter("Socket", "hb", 0.0, "x0", "y0")
    s.append(["feature.cylinder", {"name": "Magnet", "radius": unit(gf.MAGNET_D / 2), "when": "magnets",
                                   "height": "%s + 1 mm" % unit(gf.MAGNET_DEPTH),
                                   "position": ["x0 - %s" % unit(21 - gf.HOLE_IN), "y0 - %s" % unit(21 - gf.HOLE_IN),
                                                "hb - %s" % unit(gf.MAGNET_DEPTH)]}])
    s.append(["feature.pattern", {"source": "Magnet", "count": "2", "step": [unit(2 * (21 - gf.HOLE_IN)), "0 mm", "0 mm"],
                                  "name": "Magnet2", "when": "magnets"}])
    s.append(["feature.pattern", {"source": "Magnet2", "count": "2", "step": ["0 mm", unit(2 * (21 - gf.HOLE_IN)), "0 mm"],
                                  "name": "Magnets", "when": "magnets"}])
    # A countersunk M3 hole in the middle of the cell, to screw the plate down: a 90 deg cone that is
    # PLATE_SCREW_HEAD wide at the floor, and the clearance hole through.
    head = gf.PLATE_SCREW_HEAD / 2
    s.append(["feature.cone", {"name": "Countersink", "radius": unit(head + 1), "height": unit(head + 1),
                               "position": ["x0", "y0", "hb + 1 mm"], "axis": [0, 0, -1], "when": "screws"}])
    s.append(["feature.cylinder", {"name": "ScrewHole", "radius": unit(gf.PLATE_SCREW_D / 2), "height": "hb + 2 mm",
                                   "position": ["x0", "y0", "-1 mm"], "when": "screws"}])
    s.append(["feature.boolean", {"op": "union", "target": "Countersink", "tool": "ScrewHole", "name": "Screw",
                                  "when": "screws"}])
    # Light: the window through the floor; with screws a cross of 10 mm ribs carries the screw's boss.
    s += gf.rrect("WindowSketch", "-1 mm", "win / 2", "win / 2", "min(3 mm, win / 4)", "x0", "y0")
    s.append(["feature.extrude", {"sketch": "WindowSketch", "distance": "hb + 1.5 mm", "name": "Window0",
                                  "when": "style == 1"}])
    s.append(["feature.block", {"name": "RibX", "size": ["grid", "10 mm", "hb + 4 mm"],
                                "position": ["x0 - grid / 2", "y0 - 5 mm", "-2 mm"], "when": "style == 1 && screws"}])
    s.append(["feature.block", {"name": "RibY", "size": ["10 mm", "grid", "hb + 4 mm"],
                                "position": ["x0 - 5 mm", "y0 - grid / 2", "-2 mm"], "when": "style == 1 && screws"}])
    s.append(["feature.boolean", {"op": "union", "target": "RibX", "tool": "RibY", "name": "Ribs",
                                  "when": "style == 1 && screws"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Window0", "tool": "Ribs", "name": "Window",
                                  "when": "style == 1"}])
    # Weighted: the pocket from below, with its four round-ended channels when no connector sits there.
    sq = gf.WEIGHT_SQ
    s.append(["feature.block", {"name": "WeightSq", "size": [unit(sq), unit(sq), unit(gf.WEIGHT_DEPTH + 1)],
                                "position": ["x0 - %s" % unit(sq / 2), "y0 - %s" % unit(sq / 2), "-1 mm"],
                                "when": "style == 3"}])
    arms = "style == 3 && conn == 3"
    s.append(["feature.block", {"name": "Chan", "size": [unit(gf.CHAN_W), unit(gf.CHAN_L), unit(gf.CHAN_DEPTH + 1)],
                                "position": ["x0 - %s" % unit(gf.CHAN_W / 2), "y0 + %s" % unit(gf.CHAN_AT - gf.CHAN_L / 2),
                                             "-1 mm"], "when": arms}])
    s.append(["feature.cylinder", {"name": "ChanEnd", "radius": unit(gf.CHAN_W / 2), "height": unit(gf.CHAN_DEPTH + 1),
                                   "position": ["x0", "y0 + %s" % unit(gf.CHAN_AT + gf.CHAN_L / 2), "-1 mm"],
                                   "when": arms}])
    s.append(["feature.boolean", {"op": "union", "target": "Chan", "tool": "ChanEnd", "name": "Chan1", "when": arms}])
    s.append(["feature.pattern", {"source": "Chan1", "count": "4", "angle": "90 deg", "point": ["x0", "y0", "0 mm"],
                                  "name": "Chans", "when": arms}])
    s.append(["feature.boolean", {"op": "union", "target": "WeightSq", "tool": "Chans", "name": "Weight",
                                  "when": "style == 3"}])
    cut = "Socket"
    for tool in ("Magnets", "Screw", "Window", "Weight"):
        s.append(["feature.boolean", {"op": "union", "target": cut, "tool": tool, "name": "Cell" + tool}])
        cut = "Cell" + tool
    s.append(["feature.pattern", {"source": cut, "count": "cx", "step": ["grid", "0 mm", "0 mm"], "name": "CellsX"}])
    s.append(["feature.pattern", {"source": "CellsX", "count": "cy", "step": ["0 mm", "grid", "0 mm"], "name": "Cells"}])

    # Connector pockets along the joints, made once: the joints across x (between columns of pieces) lie
    # k cells apart, as do those across y. Seeds at the first joint's first cell.
    jx, jy = "fx + kx * grid", "fy + ky * grid"
    across_x = "px > 1"
    across_y = "py > 1"
    for d, (u0, v0, swap, more, cnt, step_v, step_u) in {
        "X": (jx, "y0", False, across_x, "cy", ["0 mm", "grid", "0 mm"], ["kx * grid", "0 mm", "0 mm"]),
        "Y": (jy, "x0", True, across_y, "cx", ["grid", "0 mm", "0 mm"], ["0 mm", "ky * grid", "0 mm"]),
    }.items():
        joints = "p%s - 1" % d.lower()
        # Bowtie pocket: the clip offset by the fit, from below the plate to the clip's top + the fit.
        s.append(["sketch.create", {"name": "BowtiePocketSketch" + d, "plane": "xy", "offset": "-1 mm"}])
        s.append(["sketch.polyline", {"sketch": "BowtiePocketSketch" + d, "closed": True,
                                      "points": poly_expr(BOWTIE, BOWTIE_OFF, "clr", u0, v0, swap)}])
        s.append(["feature.extrude", {"sketch": "BowtiePocketSketch" + d, "distance": "%s + clr + 1 mm" % unit(BT_T),
                                      "name": "BowtiePocket" + d, "when": "bowtie && " + more}])
        # Dovetail slot: the tab offset by the fit, from the joint into the next piece, up to the floor.
        s.append(["sketch.create", {"name": "DovetailSlotSketch" + d, "plane": "xy", "offset": "-1 mm"}])
        s.append(["sketch.polyline", {"sketch": "DovetailSlotSketch" + d, "closed": True,
                                      "points": poly_expr(SLOT, SLOT_OFF, "clr", u0, v0, swap)}])
        s.append(["feature.extrude", {"sketch": "DovetailSlotSketch" + d, "distance": "hb + 1 mm",
                                      "name": "DovetailSlot" + d, "when": "dove && " + more}])
        s.append(["feature.boolean", {"op": "union", "target": "BowtiePocket" + d, "tool": "DovetailSlot" + d,
                                      "name": "Pocket" + d, "when": "conn != 3 && " + more}])
        s.append(["feature.pattern", {"source": "Pocket" + d, "count": cnt, "step": step_v, "name": "PocketRow" + d,
                                      "when": "conn != 3 && " + more}])
        s.append(["feature.pattern", {"source": "PocketRow" + d, "count": "max(1, %s)" % joints, "step": step_u,
                                      "name": "Pockets" + d, "when": "conn != 3 && " + more}])
        # The clips themselves, in place (z 0 to the clip's thickness).
        s.append(["sketch.create", {"name": "ClipSketch" + d, "plane": "xy"}])
        s.append(["sketch.polyline", {"sketch": "ClipSketch" + d, "closed": True,
                                      "points": poly_expr(BOWTIE, [(0, 0)] * 6, "0 mm", u0, v0, swap)}])
        s.append(["feature.extrude", {"sketch": "ClipSketch" + d, "distance": unit(BT_T), "name": "Clip" + d,
                                      "when": "bowtie && " + more}])
        s.append(["feature.pattern", {"source": "Clip" + d, "count": cnt, "step": step_v, "name": "ClipRow" + d,
                                      "when": "bowtie && " + more}])
        s.append(["feature.pattern", {"source": "ClipRow" + d, "count": "max(1, %s)" % joints, "step": step_u,
                                      "name": "Clips across " + d.lower(), "when": "bowtie && " + more}])
        # Dovetail tabs, to be joined to the piece before the joint (z 0 to the floor less the fit).
        s.append(["sketch.create", {"name": "TabSketch" + d, "plane": "xy"}])
        s.append(["sketch.polyline", {"sketch": "TabSketch" + d, "closed": True,
                                      "points": poly_expr(TAB, TAB_OFF, "0 mm", u0, v0, swap)}])
        s.append(["feature.extrude", {"sketch": "TabSketch" + d, "distance": "hb - clr", "name": "Tab" + d,
                                      "when": "dove && " + more}])
        s.append(["feature.pattern", {"source": "Tab" + d, "count": cnt, "step": step_v, "name": "TabRow" + d,
                                      "when": "dove && " + more}])
        s.append(["feature.pattern", {"source": "TabRow" + d, "count": "max(1, %s)" % joints, "step": step_u,
                                      "name": "Tabs" + d, "when": "dove && " + more}])
    s.append(["feature.boolean", {"op": "union", "target": "Cells", "tool": "PocketsX", "name": "Cuts1"}])
    s.append(["feature.boolean", {"op": "union", "target": "Cuts1", "tool": "PocketsY", "name": "Cuts"}])
    s.append(["feature.boolean", {"op": "union", "target": "TabsX", "tool": "TabsY", "name": "Tabs",
                                  "when": "dove && pieces > 1"}])

    # The pieces: a block per slot less the cuts; with dovetails, plus the tabs on its far edges (a union
    # whose tool is inactive passes its target on, so every piece ends in a feature of its own name).
    colours = ["#8FA98A", "#5B7299"]
    for j in range(SLOTS):
        for i in range(SLOTS):
            on = "%d < px && %d < py" % (i, j)
            name = "Piece %s%d" % ("ABCDE"[j], i + 1)
            blk = "Block%d%d" % (i, j)
            s.append(["feature.block", {"name": blk, "size": ["wx%d" % i, "wy%d" % j, "Hp"],
                                        "position": ["sx%d" % i, "sy%d" % j, "0 mm"], "when": on}])
            # The tabs this piece carries: those on its right and back edges, inside this box.
            tab_on = "%s && dove && (%d < px - 1 || %d < py - 1)" % (on, i, j)
            box = "TabBox%d%d" % (i, j)
            s.append(["feature.block", {"name": box,
                                        "size": ["wx%d + 0.2 mm" % i, "wy%d + 0.2 mm" % j, "Hp"],
                                        "position": ["sx%d + %s" % (i, unit(DT_L + 0.1)), "sy%d + %s" % (j, unit(DT_L + 0.1)),
                                                     "-1 mm"], "when": tab_on}])
            s.append(["feature.boolean", {"op": "intersect", "target": box, "tool": "Tabs", "keepTool": True,
                                          "name": "PieceTabs%d%d" % (i, j), "when": tab_on}])
            s.append(["feature.boolean", {"op": "subtract", "target": blk, "tool": "Cuts", "keepTool": True,
                                          "name": "Cut%d%d" % (i, j), "when": on}])
            s.append(["feature.boolean", {"op": "union", "target": "Cut%d%d" % (i, j), "tool": "PieceTabs%d%d" % (i, j),
                                          "name": name, "when": on}])
            s.append(["body.appearance", {"body": name, "color": colours[(i + j) % 2], "roughness": 0.6}])
    s.append(["feature.visible", {"feature": "Cuts", "visible": False}])
    s.append(["feature.visible", {"feature": "Tabs", "visible": False}])
    for d in ("x", "y"):
        s.append(["body.appearance", {"body": "Clips across " + d, "color": "#C2694B", "roughness": 0.5}])

    # A bin's foot (the same profile as gridfinity-bin's) seated in the first cell, hidden: the fit check.
    s += gf.foot("Fit check foot", "hb", "x0", "y0")
    s.append(["feature.visible", {"feature": "Fit check foot", "visible": False}])

    s += [
        ["set.define", {"name": "Print: pieces", "kind": "body", "where": {"name": "Piece *"}}],
        ["set.define", {"name": "Print: clips", "kind": "body", "where": {"name": "Clips across *"}}],
    ]
    s += assertions()
    s += publish()
    s.append(["document.info", {
        "title": "Gridfinity baseplate",
        "description": "A Gridfinity baseplate made to fill a drawer: give the drawer's inside and your print bed, and "
                       "it fits as many 42 mm cells as it can, centred, with filler strips to the walls, split into "
                       "pieces that fit the bed. The pieces lock together with bowtie clips pressed into pockets "
                       "underneath, or with dovetail tabs. Light (windows in the floor), solid or weighted, with "
                       "magnet holes and screw holes if you want. Every bin of the Gridfinity bin Jig seats in it. "
                       "Export each piece and the clips (sets Print: pieces and Print: clips) as STL or 3MF. "
                       "Gridfinity is by Zack Freedman (MIT).",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/" + ID,
        "tags": ["Gridfinity", "storage", "baseplate", "drawer", "organiser", "3D printing"]}])
    s.append(["jig.export", {"path": "dist/%s.3dcraftjig" % ID}])
    return s


def faces(where):
    return {"kind": "face", "where": where}


def assertions():
    a = []

    def add(name, measure, **kw):
        kw = {k.rstrip("_"): v for k, v in kw.items()}
        a.append(["assert.add", dict(name=name, measure=measure, **kw)])

    pieces = {"kind": "body", "where": {"name": "Piece *"}}
    first = "Piece A1"
    foot = "Fit check foot"
    # Faces of the pieces only (the cuts are kept, hidden, as the tool every piece is cut by).
    real = {"not": {"any": [{"in": "Cuts"}, {"in": "Tabs"}]}}

    def made(*features, **more):
        return {"all": [real, {"any": [{"madeBy": f} for f in features]}] + ([more] if more else [])}

    add("one body for each piece", "count", of=pieces, eq="pieces")
    add("cells: whole cells across times whole cells deep", "count",
        of=faces(made("Socket", normal={"along": "z"})), eq="cx * cy")
    add("fills the drawer across: cells x 42 mm + fillers = drawer width - clearance", "extent",
        of=pieces, axis="x", eq="dw - fitD")
    add("fills the drawer deep: cells x 42 mm + fillers = drawer depth - clearance", "extent",
        of=pieces, axis="y", eq="dd - fitD")
    add("plate starts at the origin across", "boxMin", of=pieces, axis="x", eq="0 mm")
    add("plate starts at the origin deep", "boxMin", of=pieces, axis="y", eq="0 mm")
    outer_x = {"in": first, "normal": {"along": "-x"}, "inside": [[-1, -1e6, -1e3], [0.001, 1e6, 1e3]]}
    outer_y = {"in": first, "normal": {"along": "-y"}, "inside": [[-1e6, -1, -1e3], [1e6, 0.001, 1e3]]}
    # The sockets' top edge is RIDGE_CUT in from the cell's side: the filler is that distance less.
    add("left filler is the computed one (at least %g mm)" % MIN_FILL, "distance", from_=faces(outer_x),
        to=faces(made("Socket", **{"in": first, "surface": "plane"})), eq="fx + %s" % unit(gf.RIDGE_CUT))
    add("front filler is the computed one (at least %g mm)" % MIN_FILL, "distance", from_=faces(outer_y),
        to=faces(made("Socket", **{"in": first, "surface": "plane"})), eq="fy + %s" % unit(gf.RIDGE_CUT))
    add("filler strips at least %g mm" % MIN_FILL, "count", of={"kind": "body", "where": {"name": first}},
        eq="if(fx >= %s && fy >= %s, 1, 0)" % (unit(MIN_FILL), unit(MIN_FILL)))
    # The first piece holds the most cells of its row and of its column, and a filler: the largest piece.
    add("largest piece fits the bed across", "extent", of=first, axis="x", max="bed")
    add("largest piece fits the bed deep", "extent", of=first, axis="y", max="bed")
    add("the other pieces are no larger, and there are slots for all", "count",
        of={"kind": "body", "where": {"name": first}},
        eq="if(lx <= kx && ly <= ky && px <= %d && py <= %d, 1, 0)" % (SLOTS, SLOTS))
    add("plate height", "extent", of=pieces, axis="z", eq="Hp")
    # Fit: a bin's foot seated in a cell touches the socket's 45 deg faces without entering it, and its
    # straight part stands the specified 0.25 mm from the socket's.
    add("no two parts overlap (pieces, clips and a seated bin foot)", "overlap",
        of={"kind": "body", "where": {"any": [{"name": "Piece *"}, {"name": "Clips across *"}, {"name": foot}]}},
        is_=False)
    add("a bin's foot seats on the socket's chamfers", "clearance", from_=foot, to=first, eq="0 mm")
    add("a seated bin's straight sides stand 0.25 mm off the socket's", "distance",
        from_=faces({"in": foot, "surface": "plane", "normal": {"perpendicular": "z"}}),
        to=faces(made("Socket", **{"in": first, "surface": "plane", "normal": {"perpendicular": "z"}})),
        eq=unit(gf.SEAT_SIDE_GAP))
    # Connectors. A measure needs something to measure when there is no joint: the seated foot's straight
    # side facing -x and the plate's outer face at x = 0 are measured with them, fx + 2.4 mm apart (the
    # foot's straight part is 37.2 mm wide in the 42 mm cell), far from every connector.
    add("bowtie clips: one in the middle of every cell along every joint", "count",
        of=faces({"any": [{"in": "Clips across x"}, {"in": "Clips across y"}], "normal": {"along": "-z"}}),
        eq="nclips")
    add("bowtie clips: two half pockets for every clip", "count",
        of=faces(made("BowtiePocketX", "BowtiePocketY", normal={"along": "-z"})), eq="2 * nclips")
    add("bowtie clips sit in their pockets with the fit on every side", "distance",
        from_=faces({"any": [{"in": "Clips across x"}, {"in": "Clips across y"}, {"in": foot, "surface": "plane", "normal": {"along": "-x"}}]}),
        to=faces({"any": [made("BowtiePocketX", "BowtiePocketY"), outer_x]}),
        eq="if(nclips > 0, clr, fx + %s)" % unit(gf.GRID / 2 - (gf.BIN_TOP / 2 - gf.FOOT[1][1])))
    add("dovetail tabs: one in the middle of every cell along every joint", "count",
        of=faces(made("TabX", "TabY", normal={"along": "z"})), eq="ntabs")
    add("dovetail tabs fit their slots with the fit on every side", "distance",
        from_=faces({"any": [made("TabX", "TabY", **{"not": {"normal": {"along": "-z"}}}), {"in": foot, "surface": "plane", "normal": {"along": "-x"}}]}),
        to=faces({"any": [made("DovetailSlotX", "DovetailSlotY"), outer_x]}),
        eq="if(ntabs > 0, clr, fx + %s)" % unit(gf.GRID / 2 - (gf.BIN_TOP / 2 - gf.FOOT[1][1])))
    # Material round the connectors, in the first piece and its neighbours across the first joints (A2
    # and B1, when they exist): every joint is made alike. All pieces at once would be too many faces,
    # and the hidden cuts too coarse a mesh to prove 0.8 mm on a large plate.
    near = {"any": [{"in": first}, {"in": "Piece A2"}, {"in": "Piece B1"}]}

    def at(*features):
        return {"all": [near, {"any": [{"madeBy": f} for f in features]}]}

    holes = at("Magnet", "Screw", "Window", "Weight")
    add("bowtie pockets leave %g mm round them (holes, windows, weight pocket, sockets and floor)" % WALL_MIN,
        "distance", from_=faces({"any": [at("BowtiePocketX", "BowtiePocketY"), outer_x]}),
        to=faces({"any": [holes, at("Socket")]}), min=unit(WALL_MIN))
    add("dovetails leave %g mm round them (holes, windows, weight pocket)" % WALL_MIN, "distance",
        from_=faces({"any": [at("DovetailSlotX", "DovetailSlotY", "TabX", "TabY"), outer_x]}),
        to=faces({"any": [holes, {"in": foot}]}), min=unit(WALL_MIN))
    return a


def publish():
    pub = [
        ("dw", dict(label="Drawer width", description="The drawer's inside, left to right", group="Drawer", order=1,
                    min="60 mm", max="600 mm", step="1 mm", unit="mm")),
        ("dd", dict(label="Drawer depth", description="The drawer's inside, front to back", group="Drawer", order=2,
                    min="60 mm", max="600 mm", step="1 mm", unit="mm")),
        ("fitD", dict(label="Drawer clearance", description="How much smaller than the drawer the plate is, in total",
                      group="Drawer", order=3, min="0 mm", max="3 mm", step="0.1 mm", unit="mm")),
        ("bed", dict(label="Print bed", description="The usable size of your printer's bed (the smaller side); "
                                                    "the plate is split into pieces that fit it",
                     group="Printer", order=1, min="180 mm", max="400 mm", step="1 mm", unit="mm")),
        ("style", dict(label="Style", description="Light: a window in every cell's floor; Solid: a full floor; "
                                                  "Weighted: a 6.4 mm bottom with a pocket for a weight under every cell",
                       group="Plate", order=1, kind="choice", choices=["Light", "Solid", "Weighted"])),
        ("magnets", dict(label="Magnet holes", description="6.5 x 2.4 mm holes for 6 x 2 mm magnets in the four "
                                                           "corners of every cell", group="Plate", order=2, kind="boolean")),
        ("screws", dict(label="Screw holes", description="A countersunk M3 hole in the middle of every cell, to "
                                                         "screw the plate down", group="Plate", order=3, kind="boolean")),
        ("conn", dict(label="Connector", description="How the pieces lock together: bowtie clips pressed into "
                                                     "pockets underneath, dovetail tabs on the joint edges, or none",
                      group="Pieces", order=1, kind="choice", choices=["Bowtie clips", "Dovetail tabs", "None"])),
        ("clr", dict(label="Connector fit", description="Play round a clip or a tab in its pocket, on every side",
                     group="Pieces", order=2, min="0 mm", max=unit(CLR_MAX), step="0.05 mm", unit="mm")),
    ]
    out = []
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        out.append(["variable.publish", p])
    return out


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
