#!/usr/bin/env python3
"""Writes build.json of the welding-table Jig:  python3 gen.py > build.json

A system welding table in the style of the 16 mm and 28 mm block tables, designed to be laser cut and
MIG welded: a top plate with a grid of system holes, side plates (skirts) on all four edges carrying the
same grid, a grid of half-lapped ribs under the top, and legs and a lower frame of standard square hollow
section. Every plate joint is tab and slot (see README.md for the rules and their sources):

- the skirts' tabs go up into notches in the edge of the top, the left and right skirts' ends into
  notches in the front and back skirts' ends, the ribs' tabs up into slots in the top, and each rib end
  has a tab into a slot in a skirt;
- a tab reaches 50 to 75 % into the plate it enters and leaves at least 3 mm, a pocket that a MIG plug
  weld fills and that is ground flush, so the working surface stays flat;
- slots are the tab plus the fit clearance on every side; every inside corner of a slot or notch has a
  T-bone relief and every tab root a dogbone, clearance and relief radius scaled with the plate, so a
  square tab seats fully although a thick laser cut rounds its inside corners.

Coordinates: the working surface is z = 0, the table's corner at the origin, x along the length, y across.
"""
import json
import math

STEEL = {"color": "#7D858C", "metallic": 0.85, "roughness": 0.45}      # tubes and foot plates
PLATE = {"color": "#B9BEC4", "metallic": 0.9, "roughness": 0.35}       # the laser-cut table plates

# Square hollow sections, cold formed (EN 10219-2): b x b x t. Outside corner radius ro = 2 t for
# t <= 6 mm (the standard allows 1.6 t to 2.4 t) and 2.5 t above (2.0 t to 3.0 t); inside ri = ro - t.
SHS = [(40, 3), (40, 4), (50, 3), (50, 4), (50, 5), (60, 3), (60, 4), (60, 5), (70, 4), (70, 5), (80, 4),
       (80, 5), (80, 6), (90, 5), (100, 4), (100, 5), (100, 6), (100, 8)]
DEFAULT_PROFILE = SHS.index((80, 4)) + 1


def shs_rows():
    rows = []
    for b, t in SHS:
        ro = 2 * t if t <= 6 else 2.5 * t
        ri = ro - t
        area = 4 * t * (b - t) - (4 - math.pi) * (ro * ro - ri * ri)     # mm^2, as EN 10219-2 computes it
        rows.append(["SHS %dx%dx%d" % (b, b, t), b, t, ro, ri, round(area * 7850e-6, 2)])   # kg/m
    return rows


steps = []


def cmd(c, **p):
    steps.append([c, p])


def V(name, expr):
    cmd("variable.set", name=name, expr=expr)


def when(feature, expr):
    cmd("feature.when", feature=feature, expr=expr)


def sub(a, b):
    return "(%s) - (%s)" % (a, b)


def add(a, b):
    return "(%s) + (%s)" % (a, b)


def lin(o, cu, u, cv, v):
    """o + cu * u + cv * v with cu, cv in -1, 0, 1."""
    s = "(%s)" % o
    for c, e in ((cu, u), (cv, v)):
        if c == 1:
            s += " + (%s)" % e
        elif c == -1:
            s += " - (%s)" % e
    return s


class Sketch:
    """A sketch whose entity ids are counted here (e1, e2, ... in order of creation); patterns come last."""

    def __init__(self, name, plane, offset=None):
        p = {"name": name, "plane": plane}
        if offset is not None:
            p["offset"] = offset
        cmd("sketch.create", **p)
        self.name = name
        self.n = 0
        self.patterned = False

    def _new(self, k=1):
        assert not self.patterned, "entities after a pattern: their ids would not be known"
        self.n += k
        return "e%d" % self.n

    def pt(self, x, y):
        cmd("sketch.point", sketch=self.name, at=[x, y])
        return self._new()

    def line(self, a, b):
        cmd("sketch.line", sketch=self.name, **{"from": a, "to": b})
        return self._new()

    def arc(self, c, s, e):
        cmd("sketch.arc", sketch=self.name, center=c, start=s, end=e)
        return self._new()

    def circle(self, x, y, r):
        cmd("sketch.circle", sketch=self.name, center=[x, y], radius=r)
        self._new()            # its centre
        return self._new()     # the circle

    def rect(self, x0, y0, x1, y1):
        cmd("sketch.rect", sketch=self.name, **{"from": [x0, y0], "to": [x1, y1]})
        self._new(8)

    def pattern(self, entities, **p):
        cmd("sketch.pattern", sketch=self.name, entities=entities, **p)
        self.patterned = True

    def loop(self, pts, segs, origin, m):
        """A closed loop given in local (u, v): pts {key: (u, v)}, segs [("L", a, b) | ("A", centre, a, b)]
        with arcs counter-clockwise in (u, v). m = (xu, xv, yu, yv) maps (u, v) to the sketch's axes,
        each -1, 0 or 1; a map that mirrors turns the arcs round. Returns the loop's curves."""
        xu, xv, yu, yv = m
        flip = xu * yv - xv * yu < 0
        ids = {}
        for k, (u, v) in pts.items():
            ids[k] = self.pt(lin(origin[0], xu, u, xv, v), lin(origin[1], yu, u, yv, v))
        out = []
        for s in segs:
            if s[0] == "L":
                out.append(self.line(ids[s[1]], ids[s[2]]))
            else:
                a, b = (s[3], s[2]) if flip else (s[2], s[3])
                out.append(self.arc(ids[s[1]], ids[a], ids[b]))
        return out

    def slot(self, origin, m, a, b, r):
        """A closed slot 2a long (u) and 2b wide (v) about origin, with a T-bone relief of radius r at each
        corner, reaching past the slot's end along its length."""
        na, nb, r2 = "-(%s)" % a, "-(%s)" % b, "2 * (%s)" % r
        pts = {
            "p1": (na, nb), "p2": (a, nb), "c2": (a, add(nb, r)), "p3": (a, add(nb, r2)),
            "p4": (a, sub(b, r2)), "c3": (a, sub(b, r)), "p5": (a, b),
            "p6": (na, b), "c4": (na, sub(b, r)), "p7": (na, sub(b, r2)),
            "p8": (na, add(nb, r2)), "c1": (na, add(nb, r)),
        }
        segs = [("L", "p1", "p2"), ("A", "c2", "p2", "p3"), ("L", "p3", "p4"), ("A", "c3", "p4", "p5"),
                ("L", "p5", "p6"), ("A", "c4", "p6", "p7"), ("L", "p7", "p8"), ("A", "c1", "p8", "p1")]
        return self.loop(pts, segs, origin, m)

    def notch(self, origin, m, a, d, o, r):
        """An open notch 2a wide (u) from an edge at v = 0 to depth d (v), starting o outside the edge,
        with a T-bone relief of radius r at its two inner corners, reaching deeper (v)."""
        na, no, r2 = "-(%s)" % a, "-(%s)" % o, "2 * (%s)" % r
        pts = {
            "p1": (na, no), "p2": (a, no), "p3": (a, d), "c3": (sub(a, r), d), "p4": (sub(a, r2), d),
            "p5": (add(na, r2), d), "c5": (add(na, r), d), "p6": (na, d),
        }
        segs = [("L", "p1", "p2"), ("L", "p2", "p3"), ("A", "c3", "p3", "p4"), ("L", "p4", "p5"),
                ("A", "c5", "p5", "p6"), ("L", "p6", "p1")]
        return self.loop(pts, segs, origin, m)

    def rounded_rect(self, x0, y0, x1, y1, r):
        """Counter-clockwise; r > 0 on every corner."""
        pts = {"a": (add(x0, r), y0), "b": (sub(x1, r), y0), "c": (x1, add(y0, r)), "d": (x1, sub(y1, r)),
               "e": (sub(x1, r), y1), "f": (add(x0, r), y1), "g": (x0, sub(y1, r)), "h": (x0, add(y0, r)),
               "k1": (sub(x1, r), add(y0, r)), "k2": (sub(x1, r), sub(y1, r)), "k3": (add(x0, r), sub(y1, r)),
               "k4": (add(x0, r), add(y0, r))}
        segs = [("L", "a", "b"), ("A", "k1", "b", "c"), ("L", "c", "d"), ("A", "k2", "d", "e"), ("L", "e", "f"),
                ("A", "k3", "f", "g"), ("L", "g", "h"), ("A", "k4", "h", "a")]
        return self.loop(pts, segs, ("0 mm", "0 mm"), (1, 0, 0, 1))


ID = (1, 0, 0, 1)       # u along the sketch's x, v along its y
SWAP = (0, 1, 1, 0)     # u along its y, v along its x (a mirror)


def main():
    # ------------------------------------------------------------------ tables and inputs
    # A system: hole, grid, plate (the top, the skirts and the foot plates), depth (skirt height with the
    # top), rib thickness.
    cmd("table.set", name="systems",
        columns=["system", {"name": "hole", "unit": "mm"}, {"name": "grid", "unit": "mm"},
                 {"name": "plate", "unit": "mm"}, {"name": "side", "unit": "mm"}, {"name": "rib", "unit": "mm"}],
        rows=[["System 16", 16, 50, 12, 100, 10], ["System 28", 28, 100, 25, 200, 20]])
    cmd("table.set", name="profiles",
        columns=["profile", {"name": "b", "unit": "mm"}, {"name": "t", "unit": "mm"}, {"name": "ro", "unit": "mm"},
                 {"name": "ri", "unit": "mm"}, "kgPerM"],
        rows=shs_rows())
    V("sys", "1")
    V("L", "1200 mm")
    V("Wd", "800 mm")
    V("ribTarget", "250 mm")
    V("tabTarget", "200 mm")
    V("tabPct", "60")
    V("clrPct", "2")
    V("relPct", "8")
    V("frame", "3")
    V("tableH", "900 mm")
    V("profile", str(DEFAULT_PROFILE))

    # ------------------------------------------------------------------ derived sizes
    V("hd", "systems[sys].hole")
    V("g", "systems[sys].grid")
    V("pt", "systems[sys].plate")
    V("sh", "systems[sys].side")
    V("tr", "systems[sys].rib")
    V("rh", "sh - pt")
    V("zm", "-(pt + sh) / 2")
    # The hole grid, centred: nX by nY holes, the first at (x0, y0); rows of holes in the skirts.
    V("nX", "floor(L / g)")
    V("nY", "floor(Wd / g)")
    V("x0", "(L - (nX - 1) * g) / 2")
    V("y0", "(Wd - (nY - 1) * g) / 2")
    V("rows", "floor(sh / g)")
    # Tab and slot. Clearance and relief radius grow with the plate (a thick cut tapers and its inside
    # corners round more). Every tab enters a plate of the system's thickness pt (the top or a skirt) and
    # reaches tabPct % into it, leaving at least a 3 mm pocket for the plug weld.
    V("f", "tabPct / 100")
    V("clr", "clrPct / 100 * pt")
    V("rd", "relPct / 100 * pt")
    V("e1", "rd / (2 * sqrt(2))")               # a tab root's dogbone centre from the corner, on each axis
    V("tabL", "min(f * pt, pt - 3 mm)")
    # Rib tabs: 3 x the rib, at least 40 mm (the shortest tack weld on plate over 6 mm).
    V("tabW", "max(40 mm, 3 * tr)")
    V("sw", "tr + 2 * clr")                     # a rib slot's width
    V("sl", "tabW + 2 * clr")                   # a rib slot's length
    # Skirt tabs (into notches in the top's edge, and the left and right skirts' ends into notches in the
    # front and back skirts' ends): 3 x the plate, but no wider than leaves half a plate of steel between
    # the notch with its reliefs and the nearest system hole (half a grid along the edge, eN from it).
    V("eN", "min(x0, y0)")
    V("dN", "pt + clr")
    V("aMax", "g / 2 - sqrt(max(0 mm * 1 mm, (hd / 2 + pt / 2) * (hd / 2 + pt / 2) - "
              "max(0 mm, eN - dN - rd) * max(0 mm, eN - dN - rd)))")
    # The skirt tabs' root dogbones must also keep half a plate to the holes beside a corner tab (aE), and
    # not thin the system's own web between a skirt's top edge and its first row of holes (aD).
    V("sysWeb", "g / 2 - hd / 2 - pt")
    V("aE", "g / 2 + e1 - sqrt(max(0 mm * 1 mm, (hd / 2 + pt / 2 + rd) * (hd / 2 + pt / 2 + rd) - "
            "max(0 mm, eN - pt - e1) * max(0 mm, eN - pt - e1)))")
    V("aD", "g / 2 + e1 - sqrt(max(0 mm * 1 mm, (hd / 2 + min(sysWeb, pt / 2) + rd) * "
            "(hd / 2 + min(sysWeb, pt / 2) + rd) - max(0 mm, g / 2 - pt - e1) * max(0 mm, g / 2 - pt - e1)))")
    V("tabS", "min(3 * pt, floor(2 * (aMax - clr) / (1 mm)) * 1 mm, floor(2 * aE / (1 mm)) * 1 mm, "
              "floor(2 * aD / (1 mm)) * 1 mm)")
    V("aN", "tabS / 2 + clr")
    V("sN", "tabS + 2 * clr")
    # The tube.
    V("b", "profiles[profile].b")
    V("t", "profiles[profile].t")
    V("ro", "profiles[profile].ro")
    V("ri", "profiles[profile].ri")
    V("legsOn", "frame >= 2")
    V("frameOn", "frame == 3")
    V("legLen", "tableH - 2 * pt")              # the foot plate and the top are each a plate
    V("railZ", "-tableH + 150 mm")
    V("railLenX", "L - 2 * pt - 2 * b")
    V("railLenY", "Wd - 2 * pt - 2 * b")
    # Ribs on the lines between two holes, every rE holes, centred as far as the grid allows. A rib has a
    # tab either side of every crossing, dT from it (a plate's thickness clear of the crossing rib), so a
    # cell must hold two tabs; ribs stay clear of the legs, and far enough from the skirts that a rib's
    # first tab clears the skirt's notch by a plate.
    V("dT", "tr / 2 + tabW / 2 + pt")
    V("rE", "max(ceil((2 * dT + sl + 2 * rd + pt / 2) / g), floor(ribTarget / g))")
    V("ribStep", "rE * g")
    V("legClear", "if(legsOn, b + 10 mm, 0 mm)")
    V("kMin", "max(pt + legClear + tr / 2, 2 * pt + dT + tabW / 2 + clr + rd)")
    # As many ribs as keep every cell, the end cells between the skirts and the first rib included, within
    # about a rib step; no more than fit between the keep-outs.
    for a, n, o, span in (("X", "nX", "x0", "L"), ("Y", "nY", "y0", "Wd")):
        V("jmin" + a, "max(0, ceil((kMin - %s) / g - 0.5))" % o)
        V("m" + a, "%s - 1 - 2 * jmin%s" % (n, a))
        V("nR" + a.lower(), "max(1, min(ceil((%s - 2 * pt) / ribStep) - 1, floor((m%s - 1) / rE) + 1))" % (span, a))
        V("js" + a, "jmin%s + round(((m%s - 1) - (nR%s - 1) * rE) / 2)" % (a, a, a.lower()))
    V("xr0", "x0 + (jsX + 0.5) * g")
    V("yr0", "y0 + (jsY + 0.5) * g")
    V("xrL", "xr0 + (nRx - 1) * ribStep")
    V("yrL", "yr0 + (nRy - 1) * ribStep")
    # Skirt tabs in the middle between two holes, every tE holes, centred; the corner tabs between the
    # skirts' two rows of holes.
    V("tE", "max(1, floor(tabTarget / g))")
    V("tabStep", "tE * g")
    V("nTx", "floor((nX - 2) / tE) + 1")
    V("nTy", "floor((nY - 2) / tE) + 1")
    V("xt0", "x0 + (round(((nX - 2) - (nTx - 1) * tE) / 2) + 0.5) * g")
    V("yt0", "y0 + (round(((nY - 2) - (nTy - 1) * tE) / 2) + 0.5) * g")
    V("zc", "-g")

    # ------------------------------------------------------------------ the rules, as numbers
    # webN: between a notch (with its reliefs) and the nearest system hole, exactly. webD: between a skirt
    # tab's root dogbone and the skirt's first row of holes; the system itself leaves only sysWeb there
    # (5 mm in System 16: holes half a grid below the surface, a 12 mm top), so the dogbones must not make
    # it thinner. webE: the same at a left or right skirt's corner tab.
    V("webN", "min(sqrt(max(0 mm, g / 2 - aN) * max(0 mm, g / 2 - aN) + (eN - dN) * (eN - dN)), "
              "sqrt((g / 2 - aN + rd) * (g / 2 - aN + rd) + (eN - dN) * (eN - dN)) - rd) - hd / 2")
    V("webD", "sqrt((g / 2 - tabS / 2 + e1) * (g / 2 - tabS / 2 + e1) + (g / 2 - pt - e1) * (g / 2 - pt - e1)) "
              "- rd - hd / 2")
    V("webE", "sqrt((g / 2 - tabS / 2 + e1) * (g / 2 - tabS / 2 + e1) + (eN - pt - e1) * (eN - pt - e1)) "
              "- rd - hd / 2")
    # The longest run without a tab: along a skirt, inside a cell, at a rib's ends (the end tab counts).
    V("pitch", "max(tabStep, xt0, yt0, ribStep - 2 * dT, yr0 - dT - pt, Wd - pt - yrL - dT, "
               "xr0 - dT - pt, L - pt - xrL - dT)")
    V("pocketOk", "pt - tabL >= 3 mm && tabL >= pt / 2")
    V("widthOk", "tabW >= 40 mm && tabS >= 2.5 * pt")
    V("webOk", "webN >= pt / 2 && webE >= pt / 2 && webD >= min(sysWeb, pt / 2)")
    V("reliefOk", "rd >= 0.5 mm && sw > 4 * rd && sN > 4 * rd && rh / 2 > 2 * rd")
    V("ribsOk", "mX >= 1 && mY >= 1 && ribStep - 2 * dT - sl - 2 * rd >= pt / 2")

    # ------------------------------------------------------------------ the top plate
    top = Sketch("TopSketch", "xy", offset="-pt")
    top.rect("0 mm", "0 mm", "L", "Wd")
    hole = top.circle("x0", "y0", "hd / 2")
    top.pattern([hole], count="nX", step=["g", "0 mm"], count2="nY", step2=["0 mm", "g"])
    cmd("feature.extrude", sketch="TopSketch", distance="pt", name="TopPlate")
    # Slots for the ribs' tabs: a pair either side of every crossing.
    s = Sketch("TopSlotsY", "xy", offset="-pt - 1 mm")
    e = (s.slot(("xr0", "yr0 - dT"), SWAP, "sl / 2", "sw / 2", "rd")
         + s.slot(("xr0", "yr0 + dT"), SWAP, "sl / 2", "sw / 2", "rd"))
    s.pattern(e, count="nRx", step=["ribStep", "0 mm"], count2="nRy", step2=["0 mm", "ribStep"])
    cmd("feature.extrude", sketch="TopSlotsY", distance="pt + 2 mm", cut="TopPlate", name="TopSlottedY")
    s = Sketch("TopSlotsX", "xy", offset="-pt - 1 mm")
    e = (s.slot(("xr0 - dT", "yr0"), ID, "sl / 2", "sw / 2", "rd")
         + s.slot(("xr0 + dT", "yr0"), ID, "sl / 2", "sw / 2", "rd"))
    s.pattern(e, count="nRx", step=["ribStep", "0 mm"], count2="nRy", step2=["0 mm", "ribStep"])
    cmd("feature.extrude", sketch="TopSlotsX", distance="pt + 2 mm", cut="TopSlottedY", name="TopSlotted")
    # Notches in the edges for the skirts' tabs.
    s = Sketch("TopNotches", "xy", offset="-pt - 1 mm")
    front = s.notch(("xt0", "0 mm"), (1, 0, 0, 1), "aN", "dN", "2 mm", "rd")
    back = s.notch(("xt0", "Wd"), (1, 0, 0, -1), "aN", "dN", "2 mm", "rd")
    left = s.notch(("0 mm", "yt0"), (0, 1, 1, 0), "aN", "dN", "2 mm", "rd")
    right = s.notch(("L", "yt0"), (0, -1, 1, 0), "aN", "dN", "2 mm", "rd")
    s.pattern(front + back, count="nTx", step=["tabStep", "0 mm"])
    s.pattern(left + right, count="nTy", step=["0 mm", "tabStep"])
    cmd("feature.extrude", sketch="TopNotches", distance="pt + 2 mm", cut="TopSlotted", name="Top")

    # ------------------------------------------------------------------ the skirts
    # Front: on zx (sketch x = world z, y = world x), extruded along +y: holes, the ribs' slots, and at each
    # end a notch for the left or right skirt's corner tab.
    s = Sketch("FrontSketch", "zx")
    s.rect("-sh", "0 mm", "-pt", "L")
    h = s.circle("-g / 2", "x0", "hd / 2")
    e = s.slot(("zm", "xr0"), ID, "sl / 2", "sw / 2", "rd")
    s.pattern([h], count="nX", step=["0 mm", "g"], count2="rows", step2=["-g", "0 mm"])
    s.pattern(e, count="nRx", step=["0 mm", "ribStep"])
    cmd("feature.extrude", sketch="FrontSketch", distance="pt", name="FrontPlate")
    cmd("feature.block", name="FrontTab", size=["tabS", "pt", "tabL + 1 mm"],
        position=["xt0 - tabS / 2", "0 mm", "-pt - 1 mm"])
    cmd("feature.pattern", name="FrontTabs", source="FrontTab", count="nTx", step=["tabStep", "0 mm", "0 mm"])
    cmd("feature.boolean", op="union", target="FrontPlate", tool="FrontTabs", name="FrontTabbed")
    s = Sketch("FrontCuts", "zx", offset="-1 mm")
    c1 = s.circle("-pt - e1", "xt0 - tabS / 2 + e1", "rd")
    c2 = s.circle("-pt - e1", "xt0 + tabS / 2 - e1", "rd")
    s.notch(("zc", "0 mm"), ID, "aN", "dN", "2 mm", "rd")
    s.notch(("zc", "L"), (1, 0, 0, -1), "aN", "dN", "2 mm", "rd")
    s.pattern([c1, c2], count="nTx", step=["0 mm", "tabStep"])
    cmd("feature.extrude", sketch="FrontCuts", distance="pt + 2 mm", cut="FrontTabbed", name="Front")
    cmd("feature.mirror", source="Front", normal=[0, 1, 0], point=["0 mm", "Wd / 2", "0 mm"], keep=True, name="Back")
    # Left: on yz (sketch x = world y, y = world z), between the front and the back, extruded along +x; a
    # corner tab at each end into the front and back skirts.
    s = Sketch("LeftSketch", "yz")
    s.rect("pt", "-sh", "Wd - pt", "-pt")
    h = s.circle("y0", "-g / 2", "hd / 2")
    e = s.slot(("yr0", "zm"), SWAP, "sl / 2", "sw / 2", "rd")
    s.pattern([h], count="nY", step=["g", "0 mm"], count2="rows", step2=["0 mm", "-g"])
    s.pattern(e, count="nRy", step=["ribStep", "0 mm"])
    cmd("feature.extrude", sketch="LeftSketch", distance="pt", name="LeftPlate")
    cmd("feature.block", name="LeftTab", size=["pt", "tabS", "tabL + 1 mm"],
        position=["0 mm", "yt0 - tabS / 2", "-pt - 1 mm"])
    cmd("feature.pattern", name="LeftTabs", source="LeftTab", count="nTy", step=["0 mm", "tabStep", "0 mm"])
    cmd("feature.boolean", op="union", target="LeftPlate", tool="LeftTabs", name="LeftTabbed")
    cmd("feature.block", name="LeftEnd", size=["pt", "tabL + 1 mm", "tabS"],
        position=["0 mm", "pt - tabL", "zc - tabS / 2"])
    cmd("feature.pattern", name="LeftEnds", source="LeftEnd", count="2",
        step=["0 mm", "Wd - 2 * pt + tabL - 1 mm", "0 mm"])
    cmd("feature.boolean", op="union", target="LeftTabbed", tool="LeftEnds", name="LeftEnded")
    s = Sketch("LeftReliefs", "yz", offset="-1 mm")
    c1 = s.circle("yt0 - tabS / 2 + e1", "-pt - e1", "rd")
    c2 = s.circle("yt0 + tabS / 2 - e1", "-pt - e1", "rd")
    for y in ("pt + e1", "Wd - pt - e1"):
        s.circle(y, "zc - tabS / 2 + e1", "rd")
        s.circle(y, "zc + tabS / 2 - e1", "rd")
    s.pattern([c1, c2], count="nTy", step=["tabStep", "0 mm"])
    cmd("feature.extrude", sketch="LeftReliefs", distance="pt + 2 mm", cut="LeftEnded", name="Left")
    cmd("feature.mirror", source="Left", normal=[1, 0, 0], point=["L / 2", "0 mm", "0 mm"], keep=True, name="Right")

    # ------------------------------------------------------------------ the ribs
    # Across (along y, at x = xr0 + k ribStep): half-lapped from the top (the lap a clearance deeper, so
    # the joint seats with the errors of both notches), tabs into the top either side of every crossing and
    # one at each end into the front and back skirts.
    s = Sketch("RibYSketch", "yz", offset="xr0 - tr / 2")
    s.rect("pt", "-sh", "Wd - pt", "-pt")
    cmd("feature.extrude", sketch="RibYSketch", distance="tr", name="RibYPlate")
    cmd("feature.block", name="RibYTab", size=["tr", "tabW", "tabL + 1 mm"],
        position=["xr0 - tr / 2", "yr0 - dT - tabW / 2", "-pt - 1 mm"])
    cmd("feature.pattern", name="RibYTabPair", source="RibYTab", count="2", step=["0 mm", "2 * dT", "0 mm"])
    cmd("feature.pattern", name="RibYTabs", source="RibYTabPair", count="nRy", step=["0 mm", "ribStep", "0 mm"])
    cmd("feature.block", name="RibYEnd", size=["tr", "tabL + 1 mm", "tabW"],
        position=["xr0 - tr / 2", "pt - tabL", "zm - tabW / 2"])
    cmd("feature.pattern", name="RibYEnds", source="RibYEnd", count="2",
        step=["0 mm", "Wd - 2 * pt + tabL - 1 mm", "0 mm"])
    cmd("feature.boolean", op="union", target="RibYPlate", tool="RibYTabs", name="RibYTabbed")
    cmd("feature.boolean", op="union", target="RibYTabbed", tool="RibYEnds", name="RibYEnded")
    s = Sketch("RibYLaps", "yz", offset="xr0 - tr / 2 - 1 mm")
    e = s.notch(("yr0", "-pt"), (1, 0, 0, -1), "sw / 2", "rh / 2 + clr", "2 mm", "rd")
    s.pattern(e, count="nRy", step=["ribStep", "0 mm"])
    cmd("feature.extrude", sketch="RibYLaps", distance="tr + 2 mm", cut="RibYEnded", name="RibYLapped")
    s = Sketch("RibYReliefs", "yz", offset="xr0 - tr / 2 - 1 mm")
    cs = []
    for y in ("yr0 - dT", "yr0 + dT"):
        cs.append(s.circle("%s - tabW / 2 + e1" % y, "-pt - e1", "rd"))
        cs.append(s.circle("%s + tabW / 2 - e1" % y, "-pt - e1", "rd"))
    for y in ("pt + e1", "Wd - pt - e1"):
        s.circle(y, "zm - tabW / 2 + e1", "rd")
        s.circle(y, "zm + tabW / 2 - e1", "rd")
    s.pattern(cs, count="nRy", step=["ribStep", "0 mm"])
    cmd("feature.extrude", sketch="RibYReliefs", distance="tr + 2 mm", cut="RibYLapped", name="RibY")
    cmd("feature.pattern", name="RibsY", source="RibY", count="nRx", step=["ribStep", "0 mm", "0 mm"])
    # Along (along x, at y = yr0 + k ribStep): half-lapped from below, tabs into the top either side of every
    # crossing and one at each end into the left and right skirts.
    s = Sketch("RibXSketch", "zx", offset="yr0 - tr / 2")
    s.rect("-sh", "pt", "-pt", "L - pt")
    cmd("feature.extrude", sketch="RibXSketch", distance="tr", name="RibXPlate")
    cmd("feature.block", name="RibXTab", size=["tabW", "tr", "tabL + 1 mm"],
        position=["xr0 - dT - tabW / 2", "yr0 - tr / 2", "-pt - 1 mm"])
    cmd("feature.pattern", name="RibXTabPair", source="RibXTab", count="2", step=["2 * dT", "0 mm", "0 mm"])
    cmd("feature.pattern", name="RibXTabs", source="RibXTabPair", count="nRx", step=["ribStep", "0 mm", "0 mm"])
    cmd("feature.block", name="RibXEnd", size=["tabL + 1 mm", "tr", "tabW"],
        position=["pt - tabL", "yr0 - tr / 2", "zm - tabW / 2"])
    cmd("feature.pattern", name="RibXEnds", source="RibXEnd", count="2",
        step=["L - 2 * pt + tabL - 1 mm", "0 mm", "0 mm"])
    cmd("feature.boolean", op="union", target="RibXPlate", tool="RibXTabs", name="RibXTabbed")
    cmd("feature.boolean", op="union", target="RibXTabbed", tool="RibXEnds", name="RibXEnded")
    s = Sketch("RibXLaps", "zx", offset="yr0 - tr / 2 - 1 mm")
    e = s.notch(("-sh", "xr0"), (0, 1, 1, 0), "sw / 2", "rh / 2", "2 mm", "rd")
    s.pattern(e, count="nRx", step=["0 mm", "ribStep"])
    cmd("feature.extrude", sketch="RibXLaps", distance="tr + 2 mm", cut="RibXEnded", name="RibXLapped")
    s = Sketch("RibXReliefs", "zx", offset="yr0 - tr / 2 - 1 mm")
    cs = []
    for x in ("xr0 - dT", "xr0 + dT"):
        cs.append(s.circle("-pt - e1", "%s - tabW / 2 + e1" % x, "rd"))
        cs.append(s.circle("-pt - e1", "%s + tabW / 2 - e1" % x, "rd"))
    for x in ("pt + e1", "L - pt - e1"):
        s.circle("zm - tabW / 2 + e1", x, "rd")
        s.circle("zm + tabW / 2 - e1", x, "rd")
    s.pattern(cs, count="nRx", step=["0 mm", "ribStep"])
    cmd("feature.extrude", sketch="RibXReliefs", distance="tr + 2 mm", cut="RibXLapped", name="RibX")
    cmd("feature.pattern", name="RibsX", source="RibX", count="nRy", step=["0 mm", "ribStep", "0 mm"])

    # ------------------------------------------------------------------ legs, feet and frame
    # A leg of square tube in each corner inside the skirts, from its foot plate to under the top.
    s = Sketch("LegSection", "xy", offset="-tableH + pt")
    s.rounded_rect("pt", "pt", "pt + b", "pt + b", "ro")
    s.rounded_rect("pt + t", "pt + t", "pt + b - t", "pt + b - t", "ri")
    cmd("feature.extrude", sketch="LegSection", distance="legLen", name="Leg", when="legsOn")
    cmd("feature.pattern", name="LegRow", source="Leg", count="2", step=["L - 2 * pt - b", "0 mm", "0 mm"],
        when="legsOn")
    cmd("feature.pattern", name="Legs", source="LegRow", count="2", step=["0 mm", "Wd - 2 * pt - b", "0 mm"],
        when="legsOn")
    # A foot plate under each leg, of the system's plate, flush with the skirts outside, with a hole for a
    # levelling foot's stud (and the vent of the closed tube while it is welded).
    s = Sketch("FootSketch", "xy", offset="-tableH")
    s.rect("0 mm", "0 mm", "2 * pt + b", "2 * pt + b")
    s.circle("pt + b / 2", "pt + b / 2", "6.5 mm")
    cmd("feature.extrude", sketch="FootSketch", distance="pt", name="Foot", when="legsOn")
    cmd("feature.pattern", name="FootRow", source="Foot", count="2", step=["L - 2 * pt - b", "0 mm", "0 mm"],
        when="legsOn")
    cmd("feature.pattern", name="Feet", source="FootRow", count="2", step=["0 mm", "Wd - 2 * pt - b", "0 mm"],
        when="legsOn")
    # Rails of the same tube between the legs, 150 mm above the floor, on the legs' centre lines, each with
    # an 8 mm vent hole in the middle of its underside (it is closed when welded between the legs).
    s = Sketch("RailXSection", "yz", offset="pt + b")
    s.rounded_rect("pt", "railZ", "pt + b", "railZ + b", "ro")
    s.rounded_rect("pt + t", "railZ + t", "pt + b - t", "railZ + b - t", "ri")
    cmd("feature.extrude", sketch="RailXSection", distance="railLenX", name="RailXBar", when="frameOn")
    cmd("feature.cylinder", name="RailXVent", radius="4 mm", height="t + 2 mm",
        position=["L / 2", "pt + b / 2", "railZ - 1 mm"], when="frameOn")
    cmd("feature.boolean", op="subtract", target="RailXBar", tool="RailXVent", name="RailX", when="frameOn")
    cmd("feature.pattern", name="RailsX", source="RailX", count="2", step=["0 mm", "Wd - 2 * pt - b", "0 mm"],
        when="frameOn")
    s = Sketch("RailYSection", "zx", offset="pt + b")
    s.rounded_rect("railZ", "pt", "railZ + b", "pt + b", "ro")
    s.rounded_rect("railZ + t", "pt + t", "railZ + b - t", "pt + b - t", "ri")
    cmd("feature.extrude", sketch="RailYSection", distance="railLenY", name="RailYBar", when="frameOn")
    cmd("feature.cylinder", name="RailYVent", radius="4 mm", height="t + 2 mm",
        position=["pt + b / 2", "Wd / 2", "railZ - 1 mm"], when="frameOn")
    cmd("feature.boolean", op="subtract", target="RailYBar", tool="RailYVent", name="RailY", when="frameOn")
    cmd("feature.pattern", name="RailsY", source="RailY", count="2", step=["L - 2 * pt - b", "0 mm", "0 mm"],
        when="frameOn")

    # ------------------------------------------------------------------ looks, material, sets, checks
    plates = ["Top", "Front", "Back", "Left", "Right", "Feet"]
    ribs = ["RibsY", "RibsX"]
    tubes = ["Legs", "RailsX", "RailsY"]
    for bdy in plates[:-1] + ribs:
        cmd("body.appearance", body=bdy, **PLATE)
    for bdy in tubes + ["Feet"]:
        cmd("body.appearance", body=bdy, **STEEL)
    for bdy in plates + ribs + tubes:
        cmd("body.material", body=bdy, name="S235 steel", density=7850)

    # One cut sheet per plate thickness: the system's plate (pt) and the ribs (tr).
    cmd("set.define", name="Cut sheet: top, skirts, feet", kind="face", where={"any": [
        {"in": "Top", "normal": {"along": "z"}}, {"in": "Front", "normal": {"along": "-y"}},
        {"in": "Back", "normal": {"along": "y"}}, {"in": "Left", "normal": {"along": "-x"}},
        {"in": "Right", "normal": {"along": "x"}}, {"in": "Feet", "normal": {"along": "z"}}]})
    cmd("set.define", name="Cut sheet: ribs", kind="face", where={"any": [
        {"in": "RibsY", "normal": {"along": "x"}}, {"in": "RibsX", "normal": {"along": "-y"}}]})
    cmd("set.define", name="Legs (tube)", kind="body", where={"name": "Legs"})
    cmd("set.define", name="Rails, long (tube)", kind="body", where={"name": "RailsX"})
    cmd("set.define", name="Rails, short (tube)", kind="body", where={"name": "RailsY"})
    cmd("set.define", name="Steel", kind="body", where={"any": [{"name": n} for n in plates + ribs + tubes]})

    def rule(name, cond):
        cmd("assert.add", name=name, measure="count", of={"kind": "body", "where": {"name": "Top"}},
            eq="if(%s, 1, 0)" % cond)

    # Geometric checks.
    cmd("assert.add", name="holes in the top", measure="count",
        of={"kind": "face", "where": {"in": "Top", "hole": True}}, eq="nX * nY")
    cmd("assert.add", name="holes in the skirts", measure="count",
        of={"kind": "face", "where": {"any": [{"in": "Front"}, {"in": "Back"}, {"in": "Left"}, {"in": "Right"}],
                                      "hole": True}}, eq="2 * rows * (nX + nY)")
    cmd("assert.add", name="no part overlaps another (every tab inside its slot)", measure="overlap",
        of={"kind": "body"}, **{"is": False})
    # Formula checks of the tab-and-slot rules.
    rule("rule: tabs 50 to 75 % into the plate, at least a 3 mm weld pocket", "pocketOk")
    rule("rule: rib tabs at least 40 mm, skirt tabs at least 2.5 x the plate", "widthOk")
    rule("rule: webs at the notches at least half the plate; dogbones keep the system's web", "webOk")
    rule("rule: tabs at most 400 mm apart", "pitch <= 400 mm")
    rule("rule: reliefs at least 0.5 mm and fit their slots", "reliefOk")
    rule("rule: ribs clear the legs, two tabs fit between crossings", "ribsOk")
    rule("rule: rails below the skirts", "!frameOn || railZ + b < -sh")
    # The tube cut list. A set that is switched off is empty and an empty subject cannot be measured, so
    # each is measured together with a part that is always there and lies within the tube's span.
    cmd("assert.add", name="Legs: cut length legLen (measured with the top)", measure="extent",
        of={"kind": "body", "where": {"any": [{"set": "Legs (tube)"}, {"name": "Top"}]}}, axis="z",
        eq="if(legsOn, legLen + pt, pt)")
    cmd("assert.add", name="Rails, long: cut length railLenX (measured with the ribs across)", measure="extent",
        of={"kind": "body", "where": {"any": [{"set": "Rails, long (tube)"}, {"name": "RibsY"}]}}, axis="x",
        eq="if(frameOn, railLenX, xrL - xr0 + tr)")
    cmd("assert.add", name="Rails, short: cut length railLenY (measured with the ribs along)", measure="extent",
        of={"kind": "body", "where": {"any": [{"set": "Rails, short (tube)"}, {"name": "RibsX"}]}}, axis="y",
        eq="if(frameOn, railLenY, yrL - yr0 + tr)")
    cmd("assert.add", name="Steel weight (kg)", measure="mass", of={"kind": "body", "where": {"set": "Steel"}},
        min="0")

    # ------------------------------------------------------------------ parameters and info
    params = [
        dict(name="sys", label="System", group="System", order=1, kind="choice", choicesFrom="systems",
             description="System 16: 16 mm holes on a 50 mm grid, 12 mm top and skirts, 100 mm deep, 10 mm ribs. "
                         "System 28: 28 mm holes on a 100 mm grid, 25 mm top and skirts, 200 mm deep, 20 mm ribs"),
        dict(name="L", label="Length", group="Size", order=1, min="600 mm", max="2000 mm", step="50 mm", unit="mm",
             description="Length of the top (x)"),
        dict(name="Wd", label="Width", group="Size", order=2, min="400 mm", max="1200 mm", step="50 mm", unit="mm",
             description="Width of the top (y)"),
        dict(name="ribTarget", label="Rib spacing", group="Size", order=3, min="150 mm", max="400 mm", step="50 mm",
             unit="mm", description="Ribs at most this far apart where the grid and the tabs allow, on the lines "
                                    "between the holes"),
        dict(name="tabTarget", label="Tab spacing", group="Tab and slot", order=1, min="100 mm", max="400 mm",
             step="50 mm", unit="mm", description="Tabs along the skirts at most this far apart, between two holes"),
        dict(name="tabPct", label="Tab depth (%)", group="Tab and slot", order=2, kind="integer", min="50", max="75",
             description="How far a tab reaches into the plate it enters, in % of that plate; at least 3 mm is "
                         "left as the pocket for the plug weld"),
        dict(name="clrPct", label="Fit clearance (% of plate)", group="Tab and slot", order=3, min="1", max="4",
             step="0.5", description="Clearance per side between a tab and its slot, in % of the system's plate: "
                                     "2 % is 0.24 mm in System 16 and 0.5 mm in System 28"),
        dict(name="relPct", label="Relief radius (% of plate)", group="Tab and slot", order=4, min="5", max="12",
             step="1", description="Radius of the T-bones and dogbones in the inside corners, in % of the system's "
                                   "plate: 8 % is about 1 mm in System 16 and 2 mm in System 28"),
        dict(name="frame", label="Base", group="Base", order=1, kind="choice",
             choices=["None", "Legs", "Legs and frame"],
             description="Only the block (for trestles), four legs on foot plates, or legs joined by rails near "
                         "the floor"),
        dict(name="tableH", label="Working height", group="Base", order=2, min="600 mm", max="1000 mm", step="10 mm",
             unit="mm", description="Height of the top surface above the floor, with legs"),
        dict(name="profile", label="Tube", group="Base", order=3, kind="choice", choicesFrom="profiles",
             description="Square hollow section of the legs and rails (EN 10219-2): width x width x wall in mm"),
    ]
    for p in params:
        cmd("variable.publish", **p)
    cmd("document.info",
        title="Welding table",
        description="A system welding table (16 mm or 28 mm holes) to laser cut and MIG weld: a perforated top, "
                    "perforated skirts of the same plate on all four edges and half-lapped ribs, every plate joint "
                    "tab and slot with T-bone and dogbone reliefs and tabs that stop short of the surface, so the "
                    "plug welds grind flush; legs and rails of square tube from a table of EN 10219 sizes. Export "
                    "the plates with File > Export..., DXF or SVG with the face sets \"Cut sheet: top, skirts, "
                    "feet\" and \"Cut sheet: ribs\" (one per plate thickness); the sets Legs and Rails and the "
                    "assertions (assert.list) give the tube cut list.",
        author="3DCraft Jigs", licence="CC-BY-4.0",
        url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/welding-table",
        tags=["welding", "fixture table", "steel", "laser", "tab and slot", "square tube"])
    cmd("jig.export", path="dist/welding-table.3dcraftjig")


if __name__ == "__main__":
    main()
    print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
