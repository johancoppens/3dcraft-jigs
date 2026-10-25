#!/usr/bin/env python3
"""Writes build.json of the sliceform Jig:  python3 gen.py > build.json

A sliceform: two families of flat slices, the X slices in planes x = c and the
Y slices in planes y = d, that slide into each other with half-lap slots and
together show a shape given by a formula. Each slice's outline is the exact
section of the shape in its plane, drawn with sketch.curve from the shape's
formula (four curves: bottom, right, top, left), and extruded one sheet thick.

The shapes (table `shapes`):
  1 twisted vase / lamp shade: elliptical sections, semi-axes a(z) and
    b(z) = ratio * a(z), a(z) following a waist or belly, turned by the twist
    from the foot to the rim; flat foot and rim.
  2 ellipsoid (a sphere when width = height).
  3 saddle (hyperbolic paraboloid) over a square:  z = H - D + D (x^2 - y^2) / A^2.
  4 wave over a square:  z = H - D + D sin(1.5 pi x / A) cos(1.5 pi y / A).

Section of the vase in the plane x = c (the Y slices likewise with x and y
swapped): with k = a / b, phi the turn and u = c / a, the ellipse
(x cos phi + y sin phi)^2 / a^2 + (-x sin phi + y cos phi)^2 / b^2 = 1 gives
  y = a (-R u +- sqrt(Q - k^2 u^2)) / Q,  Q = sin^2 phi + k^2 cos^2 phi,
  R = sin phi cos phi (1 - k^2).

All crossings lie in a square grid of half-width g, chosen so that every crossing
is inside the shape at every height it spans, with a web of at least twice the
sheet thickness below and above the slots and beside the outermost slots. The
two slots of a crossing meet on one plane z = zm: X slices are slotted from the
top down to zm, Y slices from the bottom up to zm, so each pair adds up to the
full height at the crossing. Slots are the sheet thickness plus the clearance
wide, with small round reliefs (dogbones) in their inner corners.

The slices that exist are switched on by the counts (feature.when): NMAX of each
family are built into the history.
"""
import json

NMAX = 12
COL_X = "#D4A24C"   # ochre
COL_Y = "#2E7D7A"   # petrol

SHEETS = [
    ["Plywood 3 mm", 3], ["Plywood 4 mm", 4], ["Plywood 6 mm", 6],
    ["MDF 3 mm", 3], ["MDF 6 mm", 6],
    ["Acrylic 3 mm", 3], ["Acrylic 4 mm", 4],
    ["Greyboard 2 mm", 2], ["Corrugated cardboard 3 mm", 3],
]
SHAPES = [
    ["Twisted vase or lamp shade", "elliptical sections that turn and taper"],
    ["Ellipsoid or sphere", "a sphere when width = height"],
    ["Saddle", "hyperbolic paraboloid z = x^2 - y^2"],
    ["Wave", "z = sin(x) cos(y)"],
]


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


INPUTS = [
    ("shape", "1"),        # the vase at build time (every slice valid); the saddle below
    ("sheet", "2"),
    ("height", "220 mm"),
    ("width", "340 mm"),
    ("nx", str(NMAX)),     # all slices at build time; set to the default below
    ("ny", str(NMAX)),
    ("clearance", "0.15 mm"),
    ("twist", "180 deg"),
    ("ratio", "70"),
    ("waist", "25"),
    ("relief", "40"),
    ("lamp", "1"),
    ("bulbD", "64 mm"),
    ("bulbH", "110 mm"),
]
DERIVED = [
    ("T", "sheets[sheet].thick"),
    ("w", "T + clearance"),                       # slot width
    ("rr", "0.5 mm"),                             # relief radius in the slot corners
    ("Wmin", "2 * T"),                            # least web anywhere
    ("Wv", "Wmin + rr + 0.5 mm"),                 # web planned (relief and a margin)
    ("e", "w / 2 + Wv"),                          # from the axis of an outer slot to the edge
    ("H", "height"),
    ("A0", "width / 2"),
    ("lampOn", "if(shape == 1, lamp, 0)"),
    ("tw", "twist"),
    ("rb", "ratio / 100"),
    ("k2", "1 / rb^2"),
    ("sN", "max(1, 1 - waist / 100)"),
    ("minS", "min(1, 1 - waist / 100) / sN"),
    ("bmin", "rb * A0 * minS"),
    ("Cz", "H / 2"),
    # Most relief: two webs under the lowest point of the top, and slopes of at most 2.5 (saddle:
    # 2 D / A, wave: 1.5 pi D / A), so the slots stay sound and the kernel cuts them reliably.
    ("reliefMax", "min(40, 50 * (1 - 2 * Wv / H), if(shape == 3, 125 * A0 / H, "
                  "if(shape == 4, 250 / (1.5 * pi) * A0 / H, 40)))"),
    ("Dz", "relief / 100 * H"),
    ("zm", "choose(shape, if(lampOn, (bulbH + H) / 2, H / 2), H / 2, (H - 2 * Dz) / 2, (H - 2 * Dz) / 2)"),
    # Half-width of the crossing grid, per shape.
    ("gVase", "if(2 * bmin^2 > e^2, (sqrt(2 * bmin^2 - e^2) - e) / 2, 0 mm)"),
    ("gEh", "(sqrt(2 * A0^2 - e^2) - e) / 2"),
    ("Kell", "A0^2 * (1 - (Wv / Cz)^2)"),
    ("gEv", "if(8 * Kell > w^2, (sqrt(8 * Kell - w^2) - w) / 4, 0 mm)"),
    ("g", "choose(shape, gVase, min(gEh, gEv), A0 - e, A0 - e)"),
    # What the grid must reach: three slices with webs between the slots, and the lamp's room.
    # (with the lamp room: its sides on the walls of two slots, the next slots outside it a web away)
    ("sp", "w + Wv + rr"),
    ("gNeed", "max(sp, if(lampOn, 22 mm - w / 2 + 2 * sp, 0 mm))"),
    ("bNeed", "sqrt(((2 * gNeed + e)^2 + e^2) / 2)"),
    ("widthMin", "max(100 mm, choose(shape, 2 * bNeed / (rb * minS), "
                 "2 * max(bNeed, sqrt(((4 * gNeed + w)^2 + w^2) / 8 / (1 - (Wv / Cz)^2))), "
                 "2 * (gNeed + e), 2 * (gNeed + e)))"),
    ("nMax", "min(%d, floor(2 * g / sp) + 1)" % NMAX),
    ("nMin", "if(lampOn, max(3, ceil(2 * g / max(1 mm, g + w / 2 - 22 mm)) + 1), 3)"),
    ("nXe", "nx"),
    ("nYe", "ny"),
    ("px", "2 * g / (nXe - 1)"),
    ("py", "2 * g / (nYe - 1)"),
    ("bulbDMax", "if(lampOn, 2 * (g - max(px, py) + w / 2), 160 mm)"),
    ("bD", "bulbD"),
    ("bulbHMax", "H - 2 * Wv"),
    # Lamp room: a square opening whose sides are the outer walls of the slots of the slices
    # nearest to bulbD / 2 (so the slices beside it are cut square), the next slices outside.
    ("qL", "bD / 2 - w / 2"),
    ("aox", "if(mod(nXe, 2) == 1, ceil(qL / px) * px, (ceil(qL / px - 0.5) + 0.5) * px) + w / 2"),
    ("aoy", "if(mod(nYe, 2) == 1, ceil(qL / py) * py, (ceil(qL / py - 0.5) + 0.5) * py) + w / 2"),
    ("ztop", "H + 20 mm"),
    ("zlow", "-20 mm"),
]


def vase_s(f, tau, sign, family):
    """Across coordinate of the vase's section edge in the slice through f, at height fraction tau."""
    ph = "(tw * ((%s) - 0.5))" % tau
    a = "(A0 * (1 - waist / 100 * sin(pi * (%s))) / sN)" % tau
    if family == "X":
        q = "(sin(%s)^2 + k2 * cos(%s)^2)" % (ph, ph)
    else:
        q = "(cos(%s)^2 + k2 * sin(%s)^2)" % (ph, ph)
    r = "(sin(%s) * cos(%s) * (1 - k2))" % (ph, ph)
    u = "(%s / %s)" % (f, a)
    return "(%s * (-%s * %s %s sqrt(max(0, %s - k2 * %s^2))) / %s)" % (a, r, u, sign, q, u, q)


def ell(f, theta):
    rho = "sqrt(1 - %s^2 / A0^2)" % f
    return ("(A0 * %s * cos(%s))" % (rho, theta), "(Cz + Cz * %s * sin(%s))" % (rho, theta))


def h_top(xe, ye):
    sad = "(H - Dz + Dz * ((%s)^2 - (%s)^2) / A0^2)" % (xe, ye)
    wav = "(H - Dz + Dz * sin(1.5 * pi * (%s) / A0) * cos(1.5 * pi * (%s) / A0))" % (xe, ye)
    return sad, wav


def pieces(f, family):
    """The edges of a slice through f, per kind of outline, as (across, z) expressions in t."""
    def h(s):
        sad, wav = h_top(f, s) if family == "X" else h_top(s, f)
        return "choose(clamp(shape - 2, 1, 2), %s, %s)" % (sad, wav)

    th = ["(-0.75 * pi + 0.5 * pi * t)", "(-0.25 * pi + 0.5 * pi * t)",
          "(0.25 * pi + 0.5 * pi * t)", "(0.75 * pi + 0.5 * pi * t)"]
    return {
        # Vase: right side up, left side down; the foot and the rim are straight lines.
        "V": [(vase_s(f, "t", "+", family), "(H * t)"), (vase_s(f, "1 - t", "-", family), "(H * (1 - t))")],
        # Ellipsoid: four quarters (bottom, right, top, left), counter-clockwise.
        "E": [ell(f, x) for x in th],
        # Saddle and wave: the top, right to left; the sides and the foot are lines.
        "S": [("(A0 * (1 - t) - A0 * t)", h("(A0 * (1 - t) - A0 * t)"))],
    }


def slice_sketches(steps, nm, family, f, plane, cond):
    """Three sketches per slice, one per kind of outline, each switched by the shape:
    flat foot and rim are true lines (planes), so the slices of the two families
    meet on planes where they touch. X slices lie on yz (sketch axes y, z), Y slices
    on zx (sketch axes z, x)."""
    m = (lambda p: p) if family == "X" else (lambda p: [p[1], p[0]])
    pc = pieces(f, family)
    out = []
    for kind, when in (("V", "shape == 1"), ("E", "shape == 2"), ("S", "shape >= 3")):
        name = "%s%sSketch" % (nm, kind)
        steps.append(["sketch.create", {"name": name, "plane": plane, "offset": f}])

        def curve(k, **kw):
            s, z = pc[kind][k]
            x, y = m([s, z])
            p = {"sketch": name, "x": x, "y": y, "t": [0, 1]}
            p.update(kw)
            steps.append(["sketch.curve", p])
        if kind == "V":
            curve(0)                       # e1 foot right, e2 rim right, e3
            curve(1)                       # e4 rim left, e5 foot left, e6
            steps.append(["sketch.line", {"sketch": name, "from": "e2", "to": "e4"}])
            steps.append(["sketch.line", {"sketch": name, "from": "e5", "to": "e1"}])
        elif kind == "E":
            curve(0)
            curve(1, start="e2")
            curve(2, start="e4")
            curve(3, start="e6", end="e1")
        else:
            curve(0)                       # e1 top right, e2 top left, e3
            steps.append(["sketch.path", {"sketch": name, "start": "e2", "segments": [
                {"line": m(["-A0", "0 mm"])}, {"line": m(["A0", "0 mm"])}, {"line": "e1"}]}])
        full = "%s && %s" % (cond, when)
        steps.append(["feature.when", {"feature": name, "expr": full}])
        steps.append(["feature.extrude", {"sketch": name, "distance": "T", "symmetric": True,
                                          "name": "%s%s" % (nm, kind), "when": full}])
        out.append("%s%s" % (nm, kind))
    return out


def slot_path(steps, name, plane, family, across0):
    """One slot with round reliefs in its inner corners, at across0. X slices (comb X)
    are slotted from the top down to zm, Y slices (comb Y) from the bottom up to zm.
    Points are written as (across, z) and mapped to the sketch's axes."""
    lo, hi = "%s - w / 2" % across0, "%s + w / 2" % across0
    if family == "X":
        mouth, floor, out = "ztop", "zm", "zm + rr"
    else:
        mouth, floor, out = "zlow", "zm", "zm - rr"
    pts = [
        ("line", [lo, out]),
        ("arc", ["%s + rr" % lo, floor], [lo, floor]),
        ("line", ["%s - rr" % hi, floor]),
        ("arc", [hi, out], [hi, floor]),
        ("line", [hi, mouth]),
        ("line", "start"),
    ]
    # Seen in (across, z) with z up, an X slot's reliefs turn counter-clockwise, a Y slot's clockwise;
    # the zx sketch has its axes swapped (z, x), which mirrors the turn once more.
    ccw_in_across_z = family == "X"
    m = (lambda p: p) if family == "X" else (lambda p: p if isinstance(p, str) else [p[1], p[0]])
    clockwise = not ccw_in_across_z
    if family == "Y":
        clockwise = not clockwise
    segs = []
    for seg in pts:
        if seg[0] == "line":
            segs.append({"line": m(seg[1])})
        else:
            segs.append({"arc": m(seg[1]), "center": m(seg[2]), "clockwise": clockwise})
    steps.append(["sketch.create", {"name": name, "plane": plane}])
    steps.append(["sketch.path", {"sketch": name, "start": m([lo, mouth]), "segments": segs}])


def main():
    s = []
    s.append(["table.set", {"name": "sheets", "columns": ["sheet", {"name": "thick", "unit": "mm"}],
                            "rows": SHEETS}])
    s.append(["table.set", {"name": "shapes", "columns": ["shape", "formula"], "rows": SHAPES}])
    for n, e in INPUTS + DERIVED:
        s.append(V(n, e))
    for i in range(1, NMAX + 1):
        s.append(V("cx%d" % i, "(%d - (nXe + 1) / 2) * px" % i))
        s.append(V("cy%d" % i, "(%d - (nYe + 1) / 2) * py" % i))

    # The combs: every slot of a family as one body, kept until the first slice takes it.
    slot_path(s, "SlotXSketch", "yz", "X", "cy1")
    s.append(["feature.extrude", {"sketch": "SlotXSketch", "distance": "2 * width + 40 mm", "symmetric": True,
                                  "name": "SlotX"}])
    s.append(["feature.pattern", {"source": "SlotX", "count": "nYe", "step": ["0 mm", "py", "0 mm"], "name": "CombX"}])
    slot_path(s, "SlotYSketch", "zx", "Y", "cx1")
    s.append(["feature.extrude", {"sketch": "SlotYSketch", "distance": "2 * width + 40 mm", "symmetric": True,
                                  "name": "SlotY"}])
    s.append(["feature.pattern", {"source": "SlotY", "count": "nXe", "step": ["px", "0 mm", "0 mm"], "name": "CombY"}])
    # The lamp room: a square opening from the foot, its sides midway between slices.
    s.append(["feature.block", {"size": ["2 * aox", "2 * aoy", "bulbH + 20 mm"],
                                "position": ["-aox", "-aoy", "-20 mm"], "name": "LampRoom", "when": "lampOn"}])

    fams = [("X", "yz", "cx", "nXe", "CombX", COL_X), ("Y", "zx", "cy", "nYe", "CombY", COL_Y)]
    for fam, plane, var, cnt, comb, col in fams:
        # Slice 1 always exists (at least three slices): it takes the tools last, so build it last.
        for i in list(range(2, NMAX + 1)) + [1]:
            nm = "%s%d" % (fam, i)
            cond = "%s >= %d" % (cnt, i)
            v, e, sl = slice_sketches(s, nm, fam, "%s%d" % (var, i), plane, cond)
            for b in (v, e, sl):
                s.append(["body.appearance", {"body": b, "color": col, "roughness": 0.8}])
            # Exactly one of the three is on: the unions pass it on.
            s.append(["feature.boolean", {"op": "union", "target": v, "tool": e, "name": nm + "VE",
                                          "when": "%s && shape <= 2" % cond}])
            s.append(["feature.boolean", {"op": "union", "target": nm + "VE", "tool": sl, "name": nm + "Blank",
                                          "when": cond}])
            s.append(["feature.boolean", {"op": "subtract", "target": nm + "Blank", "tool": comb,
                                          "keepTool": i != 1, "name": nm + "Slotted", "when": cond}])
            last_lamp = fam == "Y" and i == 1
            s.append(["feature.boolean", {"op": "subtract", "target": nm + "Slotted", "tool": "LampRoom",
                                          "keepTool": not last_lamp, "name": nm, "when": cond}])

    s.append(V("nx", "6"))
    s.append(V("ny", "6"))
    s.append(V("shape", "3"))

    def rest(col, slot, ax):
        """The edges of a slice that are not its slots and not its two sheet faces."""
        return {"kind": "face", "where": [{"color": col}, {"not": {"madeBy": slot}},
                                          {"not": {"normal": {"along": ax}}}, {"not": {"normal": {"along": "-" + ax}}}]}

    def on_plane(q):
        """The faces of q that lie on the meeting plane z = zm."""
        return {"kind": "face", "where": q["where"] + [{"above": {"z": "zm - 0.001 mm"}},
                                                       {"below": {"z": "zm + 0.001 mm"}}]}

    def slot_floor(q, body, ax, lo, hi):
        """The floors of q in body that lie between lo and hi along ax."""
        w = q["where"] + [{"in": body}, {"below": {ax: hi}}]
        if lo:
            w.append({"above": {ax: lo}})
        return {"kind": "face", "where": w}

    qx = {"kind": "body", "where": {"color": COL_X}}
    qy = {"kind": "body", "where": {"color": COL_Y}}
    floors_x = {"kind": "face", "where": [{"color": COL_X}, {"madeBy": "SlotX"}, {"normal": {"along": "z"}}]}
    floors_y = {"kind": "face", "where": [{"color": COL_Y}, {"madeBy": "SlotY"}, {"normal": {"along": "-z"}}]}
    s += [
        ["assert.add", {"name": "X slices", "measure": "count", "of": qx, "eq": "nXe"}],
        ["assert.add", {"name": "Y slices", "measure": "count", "of": qy, "eq": "nYe"}],
        ["assert.add", {"name": "every crossing: X slot from the top down to the meeting plane", "measure": "count",
                        "of": on_plane(floors_x), "eq": "nXe * nYe"}],
        ["assert.add", {"name": "every crossing: Y slot from the foot up to the meeting plane", "measure": "count",
                        "of": on_plane(floors_y), "eq": "nXe * nYe"}],
        ["assert.add", {"name": "the two half-slots of a crossing meet", "measure": "distance",
                        "from": floors_x, "to": floors_y, "eq": "0 mm", "tol": "0.001 mm"}],
        # Slot width through the floors: each floor runs between the two reliefs, w - 2 rr wide and a
        # sheet long, and is bounded by straight edges only, so its area is exact.
        ["assert.add", {"name": "X slots are sheet + clearance wide", "measure": "area", "of": floors_x,
                        "eq": "nXe * nYe * (w - 2 * rr) * T"}],
        ["assert.add", {"name": "Y slots are sheet + clearance wide", "measure": "area", "of": floors_y,
                        "eq": "nXe * nYe * (w - 2 * rr) * T"}],
        # Fingers: the floors of the first two slots of slice 1 lie p - w + 2 rr apart; the finger between
        # them is narrowest at the reliefs, p - w - 2 rr.
        ["assert.add", {"name": "fingers between the X slots at least 2 x sheet", "measure": "distance",
                        "from": slot_floor(floors_x, "X1", "y", None, "cy1 + py / 2"),
                        "to": slot_floor(floors_x, "X1", "y", "cy1 + py / 2", "cy2 + py / 2"),
                        "min": "Wmin + 4 * rr"}],
        ["assert.add", {"name": "fingers between the Y slots at least 2 x sheet", "measure": "distance",
                        "from": slot_floor(floors_y, "Y1", "x", None, "cx1 + px / 2"),
                        "to": slot_floor(floors_y, "Y1", "x", "cx1 + px / 2", "cx2 + px / 2"),
                        "min": "Wmin + 4 * rr"}],
        ["assert.add", {"name": "web round the X slots at least 2 x sheet", "measure": "distance",
                        "from": floors_x, "to": rest(COL_X, "SlotX", "x"), "min": "Wmin"}],
        ["assert.add", {"name": "web round the Y slots at least 2 x sheet", "measure": "distance",
                        "from": floors_y, "to": rest(COL_Y, "SlotY", "y"), "min": "Wmin"}],
        ["assert.add", {"name": "fits the width (x min)", "measure": "boxMin", "axis": "x", "min": "-width / 2 - 0.05 mm"}],
        ["assert.add", {"name": "fits the width (x max)", "measure": "boxMax", "axis": "x", "max": "width / 2 + 0.05 mm"}],
        ["assert.add", {"name": "fits the width (y min)", "measure": "boxMin", "axis": "y", "min": "-width / 2 - 0.05 mm"}],
        ["assert.add", {"name": "fits the width (y max)", "measure": "boxMax", "axis": "y", "max": "width / 2 + 0.05 mm"}],
        ["assert.add", {"name": "stands on z = 0", "measure": "boxMin", "axis": "z", "min": "-0.05 mm"}],
        ["assert.add", {"name": "fits the height", "measure": "boxMax", "axis": "z", "max": "height + 0.05 mm"}],
        ["set.define", {"name": "Cut sheet", "kind": "face", "where": {"any": [
            {"color": COL_X, "normal": {"along": "x"}},
            {"color": COL_Y, "normal": {"along": "y"}}]}}],
    ]

    pub = [
        ("shape", dict(label="Shape", description="The shape the slices show (table shapes)", group="Shape", order=1,
                       kind="choice", choicesFrom="shapes")),
        ("height", dict(label="Height", description="Overall height", group="Shape", order=2,
                        min="100 mm", max="600 mm", step="1 mm", unit="mm")),
        ("width", dict(label="Width", description="Overall width in x and y (the vase's widest diameter). "
                       "Its least follows the sheet, the shape and the lamp room: room for three slices with "
                       "webs of two sheet thicknesses", group="Shape", order=3,
                       min="widthMin", max="600 mm", step="1 mm", unit="mm")),
        ("nx", dict(label="X slices", description="Number of slices across x: at most as many as leave a "
                    "finger of two sheet thicknesses between the slots, with the lamp room at least enough for a "
                    "slice beside the room", group="Slices", order=1, kind="integer", min="nMin", max="nMax")),
        ("ny", dict(label="Y slices", description="Number of slices across y, limited as the X slices are",
                    group="Slices", order=2, kind="integer", min="nMin", max="nMax")),
        ("sheet", dict(label="Sheet", description="Material and thickness of the sheet (table sheets)",
                       group="Material", order=1, kind="choice", choicesFrom="sheets")),
        ("clearance", dict(label="Slot clearance", description="Slot width = sheet thickness + clearance. "
                           "Laser: the kerf widens the slots too; 0.1 to 0.2 mm slides on plywood",
                           group="Material", order=2, min="0 mm", max="0.5 mm", step="0.01 mm", unit="mm")),
        ("twist", dict(label="Twist", description="Vase: how far the sections turn from the foot to the rim",
                       group="Vase", order=1, min="-180 deg", max="180 deg", step="1 deg", unit="deg")),
        ("ratio", dict(label="Section ratio", description="Vase: the short axis of the elliptical section, "
                       "in % of the long one (100: round)", group="Vase", order=2, min="55", max="100",
                       step="1")),
        ("waist", dict(label="Waist", description="Vase: how far the middle narrows, in % (negative: a belly)",
                       group="Vase", order=3, min="-30", max="30", step="1")),
        ("lamp", dict(label="Lamp room", description="Vase: a square opening in the foot for an E27 lamp "
                      "holder (40 mm ring) and the bulb", group="Lamp", order=1, kind="boolean")),
        ("bulbD", dict(label="Lamp room width", description="Least width of the opening: 44 mm passes the "
                       "40 mm holder ring; 64 mm an A60 bulb. It snaps outward to the slots of the slices "
                       "beside it; at most what leaves a slice outside it", group="Lamp", order=2,
                       min="44 mm", max="bulbDMax", step="1 mm", unit="mm")),
        ("bulbH", dict(label="Lamp room height", description="Height of the opening from the foot",
                       group="Lamp", order=3, min="40 mm", max="bulbHMax", step="1 mm", unit="mm")),
        ("relief", dict(label="Relief", description="Saddle and wave: how far the top rises and falls, "
                        "in % of the height; at most what keeps two webs under the lowest point and slopes "
                        "of at most 2.5 (a tall, narrow shape gets less)", group="Saddle and wave", order=1,
                        min="min(5, reliefMax)", max="reliefMax",
                        step="1")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        s.append(["variable.publish", p])

    s.append(["document.info", {
        "title": "Sliceform sculpture",
        "description": "A sliceform sculpture, or a lamp shade: two families of flat slices that slide into each "
                       "other with half-lap slots and together show a shape from a formula. Choose the shape "
                       "(a saddle, a wave, an ellipsoid or sphere, or a twisted vase or lamp shade), its size, the "
                       "number of slices each way, the sheet and the slot clearance; the vase can have a room "
                       "in its foot for an E27 lamp holder. Every outline is the exact section of the shape. "
                       "To cut it: File > Export..., SVG or DXF with the face set \"Cut sheet\" "
                       "(file.export {\"path\": \"sliceform.svg\", \"set\": \"Cut sheet\", \"width\": \"600 mm\"}); "
                       "each slice is on a layer named after it (X1, X2, ... and Y1, Y2, ...).",
        "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/sliceform",
        "tags": ["sliceform", "sculpture", "lamp", "laser", "plywood", "formula", "sculpture", "mathematics"]}])
    s.append(["jig.export", {"path": "dist/sliceform.3dcraftjig"}])
    return s


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
