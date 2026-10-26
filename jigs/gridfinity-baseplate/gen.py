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
# Bowtie clip (butterfly key): 12 mm across the joint, 15 mm wide at its ends, 6 mm at the neck, 1.8 mm thick
# (its pocket, 2.2 mm at the largest fit, leaves 1.2 mm of floor over it).
# Its flanks stand 36.87 deg off the line across the joint (3:4), so a fit c lets a half of the joint open
# by c / sin(36.87 deg) = c / 0.6: 0.25 mm at the default 0.15 mm, about a bin's side play.
BT_L, BT_END, BT_NECK, BT_T = 6.0, 7.5, 3.0, 1.8      # half length, half widths, thickness
BT_SIN = (BT_END - BT_NECK) / math.hypot(BT_L, BT_END - BT_NECK)   # 0.6
BT_COS = BT_L / math.hypot(BT_L, BT_END - BT_NECK)                  # 0.8: a flank's normal is (sin, cos) in
                                                                     # (across, along) the joint
# Dovetail tab: 8 mm deep, 8 mm wide at the joint, 12 mm at its end (a 1:4 flare, 14 deg).
DT_L, DT_NECK, DT_END = 8.0, 4.0, 6.0
CLR_MAX = 0.4
WALL_MIN = 0.8          # two perimeters of a 0.4 mm nozzle
FLOOR = 3.4             # Light and Solid: a 2.4 mm magnet pocket on 1 mm (rebuilt: h_skel 1 + 2.4)
SLOT_UNDER = 1.2        # a dovetail slot stops this far under the socket's floor


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


def area_poly(pts, off):
    """The area of a polygon whose vertices move by off times c, as (a0, a1, a2): a0 + a1 c + a2 c^2."""
    a0 = a1 = a2 = 0.0
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        (p0, q0), (p1, q1) = off[i], off[(i + 1) % n]
        a0 += x0 * y1 - x1 * y0
        a1 += x0 * q1 + p0 * y1 - x1 * q0 - p1 * y0
        a2 += p0 * q1 - p1 * q0
    return a0 / 2, a1 / 2, a2 / 2


def ccw(pts):
    a = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
    return a > 0


assert ccw(BOWTIE) and ccw(TAB) and ccw(SLOT)
BOWTIE_OFF = offset_polygon(BOWTIE)
BT_REACH = max(abs(m[0]) for m in BOWTIE_OFF)      # how far the pocket's ends reach past the clip's, per fit
BT_WIDE = max(abs(m[1]) for m in BOWTIE_OFF)
DT_REACH = max(abs(m[0]) for m in SLOT_OFF)
DT_WIDE = max(abs(m[1]) for m in SLOT_OFF)
BT_AREA = area_poly(BOWTIE, BOWTIE_OFF)            # pocket area a0 + a1 c + a2 c^2; a0 is the clip's
DT_AREA = area_poly(SLOT, SLOT_OFF)                # slot area
DT_TAB_IN = DT_L * (DT_NECK + DT_END)              # the tab's area past the joint
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
    # floor under the sockets: none in the Thin style (the standard 5 mm frame)
    ("hb", "if(style == 3, %s, if(style == 4, 0 mm, %s))" % (unit(gf.WEIGHT_BOTTOM), unit(FLOOR))),
    ("Hp", "hb + %s" % unit(gf.SOCKET_H - gf.RIDGE_CUT)),                        # the plate's height
    ("bowtie", "conn == 1"),
    ("dove", "conn == 2"),
    # Light: a window through the floor of every cell, leaving a rim that holds the magnets and the
    # connector pockets with WALL_MIN (and 0.05 mm to spare) round them.
    ("rim", "max(3.5 mm, if(magnets, %s, 0 mm), if(bowtie, %s + %.6g * clr, 0 mm), if(dove, %s + %.6g * clr, 0 mm))"
     % (unit(gf.HOLE_IN + gf.MAGNET_D / 2 + WALL_MIN + 0.05), unit(BT_L + WALL_MIN + 0.05), BT_REACH,
        unit(DT_L + WALL_MIN + 0.05), DT_REACH)),
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
    ("play", "clr / %.6g" % BT_SIN),                 # how far a bowtie joint's half can open
    # Gap checks at the first joint across x: a box round the pocket (or slot), less the pieces and the
    # clips, leaves the gap round the clip (or tab).
    ("gu", "%s + %.6g * clr + 0.3 mm" % (unit(BT_L), BT_REACH)),
    ("gv", "%s + %.6g * clr + 0.3 mm" % (unit(BT_END), BT_WIDE)),
    ("du", "%s + %.6g * clr + 0.3 mm" % (unit(DT_L), DT_REACH)),
    ("dv", "%s + %.6g * clr + 0.3 mm" % (unit(DT_END), DT_WIDE)),
    ("btGap", "(%.9g * 1 mm^2 + %.9g mm * clr + %.9g * clr^2) * (%s + clr) - %.9g * 1 mm^2 * %s"
     % (BT_AREA[0], BT_AREA[1], BT_AREA[2], unit(BT_T), BT_AREA[0], unit(BT_T))),
    ("dtGap", "(%.9g * 1 mm^2 + %.9g mm * clr + %.9g * clr^2) * (hb - %s) - %.9g * 1 mm^2 * (hb - %s - clr)"
     % (DT_AREA[0], DT_AREA[1], DT_AREA[2], unit(SLOT_UNDER), DT_TAB_IN, unit(SLOT_UNDER))),
]


def main():
    s = []
    for name, expr in INPUTS + DERIVED:
        s.append(V(name, expr))

    # One cell's cut, at the first cell: the socket, then what goes with it.
    s += gf.socket_cutter("Socket", "hb", "if(style == 4, 1 mm, 0 mm)", "x0", "y0")
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
        # Dovetail slot: the tab offset by the fit, from the joint into the next piece, from below up to
        # SLOT_UNDER under the socket's floor.
        s.append(["sketch.create", {"name": "DovetailSlotSketch" + d, "plane": "xy", "offset": "-1 mm"}])
        s.append(["sketch.polyline", {"sketch": "DovetailSlotSketch" + d, "closed": True,
                                      "points": poly_expr(SLOT, SLOT_OFF, "clr", u0, v0, swap)}])
        s.append(["feature.extrude", {"sketch": "DovetailSlotSketch" + d, "distance": "hb - %s + 1 mm" % unit(SLOT_UNDER),
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
        # Dovetail tabs, to be joined to the piece before the joint (z 0 to the slot's top less the fit).
        s.append(["sketch.create", {"name": "TabSketch" + d, "plane": "xy"}])
        s.append(["sketch.polyline", {"sketch": "TabSketch" + d, "closed": True,
                                      "points": poly_expr(TAB, TAB_OFF, "0 mm", u0, v0, swap)}])
        s.append(["feature.extrude", {"sketch": "TabSketch" + d, "distance": "hb - %s - clr" % unit(SLOT_UNDER), "name": "Tab" + d,
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

    # Gap checks (hidden): a box round the first clip's pocket, less the two pieces and the clips, is the
    # gap round that clip; a box round the first dovetail slot, less the two pieces, the gap round its tab.
    # Without that joint nothing is taken away and the box stays whole.
    jx = "fx + kx * grid"
    bt = "bowtie && px > 1"
    # (both boxes start 0.5 mm under the plate, so the gap is never empty, even at a fit of 0)
    s.append(["feature.block", {"name": "Clip gap check", "size": ["2 * gu", "2 * gv", "%s + clr + 0.5 mm" % unit(BT_T)],
                                "position": ["%s - gu" % jx, "y0 - gv", "-0.5 mm"]}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Clip gap check", "tool": "Piece A1", "keepTool": True,
                                  "name": "Clip gap check 1", "when": bt}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Clip gap check 1", "tool": "Piece A2", "keepTool": True,
                                  "name": "Clip gap check 2", "when": bt}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Clip gap check 2", "tool": "Clips across x",
                                  "keepTool": True, "name": "Clip gap", "when": bt}])
    dt = "dove && px > 1"
    s.append(["feature.block", {"name": "Tab gap check", "size": ["du", "2 * dv", "max(1 mm, hb - %s) + 0.5 mm" % unit(SLOT_UNDER)],
                                "position": [jx, "y0 - dv", "-0.5 mm"]}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Tab gap check", "tool": "Piece A1", "keepTool": True,
                                  "name": "Tab gap check 1", "when": dt}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Tab gap check 1", "tool": "Piece A2", "keepTool": True,
                                  "name": "Tab gap", "when": dt}])
    for nm, cond, uo, us, vs in (("Pocket check", bt, "%s - gu - 1.2 mm" % jx, "2 * gu + 2.4 mm", "gv + 1.2 mm"),
                                 ("Slot check", dt, "%s - 1.5 mm" % jx, "du + 2.7 mm", "dv + 1.2 mm")):
        s.append(["feature.block", {"name": nm + " box", "size": [us, "2 * (%s)" % vs, "hb + 0.5 mm"],
                                    "position": [uo, "y0 - (%s)" % vs, "0 mm"]}])
        s.append(["feature.boolean", {"op": "subtract", "target": nm + " box", "tool": "Piece A1", "keepTool": True,
                                      "name": nm + " 1", "when": cond}])
        s.append(["feature.boolean", {"op": "subtract", "target": nm + " 1", "tool": "Piece A2", "keepTool": True,
                                      "name": nm, "when": cond}])
    s.append(["feature.visible", {"feature": ["Clip gap", "Tab gap", "Pocket check", "Slot check"], "visible": False}])

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
    bt, dt = "bowtie && px > 1", "dove && px > 1"      # the first joint across x carries a clip, a tab
    foot = "Fit check foot"
    # Faces of the pieces only (the cuts are kept, hidden, as the tool every piece is cut by; the checks
    # below are hidden bodies made from the pieces).
    real = {"not": {"any": [{"in": b} for b in ("Cuts", "Tabs", "Clip gap", "Tab gap", "Pocket check", "Slot check")]}}

    def made(*features, **more):
        return {"all": [real, {"any": [{"madeBy": f} for f in features]}] + ([more] if more else [])}

    add("one body for each piece", "count", of=pieces, eq="pieces")
    # Every socket has two straight faces facing +x (its 0.35 mm foot and its 1.8 mm middle).
    add("cells: whole cells across times whole cells deep", "count",
        of=faces(made("Socket", surface="plane", normal={"along": "x"})), eq="2 * cx * cy")
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
    add("bowtie clips: the flanks at 36.87 deg (3:4), one per clip", "count",
        of=faces({"any": [{"in": "Clips across x", "normal": {"along": [BT_SIN, BT_COS, 0]}},
                          {"in": "Clips across y", "normal": {"along": [BT_COS, BT_SIN, 0]}}]}), eq="nclips")
    # From the flank angle: a joint's half opens by fit / sin(flank), 0.25 mm at the default fit (a formula).
    add("bowtie clips: a half joint opens at most fit / 0.6 (0.25 mm at the default 0.15 mm fit)", "count",
        of={"kind": "body", "where": {"name": first}},
        eq="if(abs(play - clr / %.6g) < 0.0001 mm && 0.15 mm / %.6g <= 0.2501 mm, 1, 0)" % (BT_SIN, BT_SIN))
    add("bowtie clips: the gap round a clip has the volume of the pocket (the clip grown by the fit) less the clip",
        "volume", of="Clip gap", eq="if(%s, btGap + 4 * gu * gv * 0.5 mm, 4 * gu * gv * (%s + clr + 0.5 mm))" % (bt, unit(BT_T)), tol="0.001 * 1 mm^3")
    add("bowtie clips: at least the fit from the pockets on every side, exactly the fit on the closest", "distance",
        from_=faces({"any": [{"in": "Clips across x"}, {"in": "Clips across y"}, {"in": foot, "surface": "plane", "normal": {"along": "-x"}}]}),
        to=faces({"any": [made("BowtiePocketX", "BowtiePocketY"), outer_x]}),
        eq="if(nclips > 0, clr, fx + %s)" % unit(gf.GRID / 2 - (gf.BIN_TOP / 2 - gf.FOOT[1][1])))
    add("dovetail tabs: one in the middle of every cell along every joint", "count",
        of=faces(made("TabX", "TabY", normal={"along": "z"})), eq="ntabs")
    add("dovetail tabs: the gap round a tab has the volume of the slot (the tab grown by the fit) less the tab",
        "volume", of="Tab gap", eq="if(%s, dtGap + 2 * du * dv * 0.5 mm, 2 * du * dv * (max(1 mm, hb - %s) + 0.5 mm))" % (dt, unit(SLOT_UNDER)),
        tol="0.001 * 1 mm^3")
    add("dovetail tabs: at least the fit from the slots on every side, exactly the fit on the closest", "distance",
        from_=faces({"any": [made("TabX", "TabY", **{"not": {"normal": {"along": "-z"}}}), {"in": foot, "surface": "plane", "normal": {"along": "-x"}}]}),
        to=faces({"any": [made("DovetailSlotX", "DovetailSlotY"), outer_x]}),
        eq="if(ntabs > 0, clr, fx + %s)" % unit(gf.GRID / 2 - (gf.BIN_TOP / 2 - gf.FOOT[1][1])))
    # Material round the connectors, on the hidden material checks: a box 1.5 mm larger than the first
    # pocket (or slot) all round and up into the socket, less the two pieces, holds the pocket's void and
    # whatever other void comes within 1.5 mm of it (holes, windows, the weight pocket, the socket over
    # the floor). Small bodies, so the distances are proven; every joint is made the same way. Without
    # that joint the box stays whole and the plate's edge and the hidden foot are measured instead.
    def void(body, *features):
        return {"all": [{"in": body}, {"any": [{"madeBy": f} for f in features]}]}

    # (madeBy names the features that made the faces: the primitives, not the booleans that joined them)
    others = ("Magnet", "Countersink", "ScrewHole", "Window0", "WeightSq", "Chan", "ChanEnd", "Socket")
    add("bowtie pockets leave %g mm round them (holes, windows, weight pocket, sockets and floor)" % WALL_MIN,
        "distance", from_=faces({"any": [void("Pocket check", "BowtiePocketX"), outer_x]}),
        to=faces({"any": [void("Pocket check", *others), {"in": foot, "surface": "plane", "normal": {"along": "-x"}}]}),
        min=unit(WALL_MIN))
    add("dovetail slots leave %g mm round them (holes, windows, weight pocket, sockets and floor)" % WALL_MIN,
        "distance", from_=faces({"any": [void("Slot check", "DovetailSlotX"), outer_x]}),
        to=faces({"any": [void("Slot check", *others), {"in": foot, "surface": "plane", "normal": {"along": "-x"}}]}),
        min=unit(WALL_MIN))
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
        ("style", dict(label="Style", description="Light (8.3 mm): a 3.4 mm floor with a window in every cell; "
                                                  "Solid (8.3 mm): a full 3.4 mm floor; Weighted (11.3 mm): a 6.4 mm "
                                                  "bottom with a pocket for a weight under every cell; Thin (4.9 mm): "
                                                  "the standard frame without a floor, lightest, but without magnets, "
                                                  "screws or connectors (the floor carries those)",
                       group="Plate", order=1, kind="choice", choices=["Light", "Solid", "Weighted", "Thin"])),
        ("magnets", dict(label="Magnet holes", description="6.5 x 2.4 mm holes for 6 x 2 mm magnets in the four "
                                                           "corners of every cell (not in the Thin style)",
                         group="Plate", order=2, kind="boolean", max="if(style == 4, 0, 1)")),
        ("screws", dict(label="Screw holes", description="A countersunk M3 hole in the middle of every cell, to "
                                                         "screw the plate down (not in the Thin style)",
                        group="Plate", order=3, kind="boolean", max="if(style == 4, 0, 1)")),
        ("conn", dict(label="Connector", description="How the pieces lock together: bowtie clips pressed into "
                                                     "pockets underneath, dovetail tabs on the joint edges, or none "
                                                     "(the only choice for the Thin style)",
                      group="Pieces", order=1, kind="choice", choices=["Bowtie clips", "Dovetail tabs", "None"],
                      min="if(style == 4, 3, 1)")),
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
