#!/usr/bin/env python3
"""Writes build.json for the wall-mount 19-inch rack cabinet Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written. The rack numbers (EIA-310-D,
IEC 60297-3-100) and the sheet stock table come from scripts/racklib.py, shared with rack-panel: the
rails carry the hole pattern a rack-panel bolts onto, and the sides stand the width apart that the panel
Jig checks it fits between.

Every part is a sheet-metal part (feature.sheetMetal) bent from one sheet, with its holes drawn in the flat
(in the base's sketch, also those of the flanges, or in a cut-out sketch switched by `when`, so every hole is
in its flat pattern), its corners relieved and closed by the `corner` choice:
- two sides (plate along y-z) with a front lip, a top and a bottom flange bent inward, the rails' bolt
  holes, and in the left side's lip the door's hinge holes;
- a lid and a bottom pan with three flanges (front, left, right) over the sides, cable knock-outs near
  the back;
- a back plate (the wall plate) with four flanges forward, inside the sides, and four wall-mount holes;
- two front rails, L or C profile, square cage-nut holes or M6 tap holes on the EIA-310 pattern, their
  legs bolted to the sides (three M6 holes in each leg); optionally the same two rails at the back;
- a vented door (a pan with four flanges), hinged at the left, shown opened by an angle.
Parts bolted together touch; none overlap (checked).

Frame: x across (the rack's centre line x = 0), y from the front (y = 0, the sides' front lips) to the
wall (y = D, the back plate's back face), z up from the sides' bottom (z = 0; the pan under it).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import racklib as rk  # noqa: E402

ID = "rack-cabinet"
MAX_U = 15
unit = rk.unit

PROFILES = ["L", "C"]
RAIL_HOLES = ["Square 9.5 mm (cage nuts)", "M6 tapped"]
# Knock-outs for metric cable glands (EN 50262): the clearance hole of M20, M25, M32.
KNOCKOUTS = [("M20", 20.5), ("M25", 25.5), ("M32", 32.5)]
CORNERS = ["Open", "Butt", "Overlap", "Miter"]     # feature.sheetMetal corner kind 1..4
RELIEFS = ["Rect", "Round", "Tear"]                # relief shape 1..3

INPUTS = [
    ("nU", "9"),
    ("D", "450 mm"),
    ("door", "1"),
    ("doorOpen", "105 deg"),
    ("profile", "2"),
    ("railHoles", "1"),
    ("rear", "1"),
    ("knock", "3"),
    ("gland", "2"),
    ("corner", "3"),
    ("gap", "0.5 mm"),
    ("reliefShape", "2"),
]
DERIVED = [
    ("Wi", "cabInnerW"),                       # clear width between the sides
    ("mr", "5 mm"),                             # the rails reach this far past the U range
    ("Hc", "nU * U + 2 * (mr + R + t)"),        # the sides' height
    ("zU0", "R + t + mr"),                      # the lowest U boundary
    ("s", "R + t + 0.5 mm"),                   # relief size (each edge and its flange end s from a corner)
    ("BA", "pi / 2 * (R + K * t)"),            # bend allowance of a 90 degree bend: where a flange's flat starts
    ("rM4", unit(rk.M4_CLEAR / 2)),
    ("rB", unit(rk.M6_CLEAR / 2)),             # rail bolts: M6 clearance (ISO 273 medium)
    ("Lside", "max(25 mm, minFlange, 2 * (holeMin + rM4) + 1 mm)"),   # sides: front lip (hinge holes in it)
    ("Lf", "max(20 mm, minFlange)"),           # other flanges
    ("Ld", "max(15 mm, minFlange)"),           # door flanges
    ("leg", "max(30 mm, minFlange, 2 * (holeMin + rB) + 1 mm)"),   # rail leg against the side (bolt holes in it)
    ("ret", "max(15 mm, minFlange)"),          # C rail's return
    ("yr", "50 mm"),                           # front rails' front face (room for handles behind the door)
    ("xo", "Wi / 2 - R - t"),                  # rails' outer bend line: the leg's outside on the side
    # The back's screw tabs (three each side, on the sides' inner faces): long enough to hold an M6
    # hole 2.5 t + r from the bend, the hole centred; the sides have the matching holes.
    ("Ltab", "max(Lf, 2 * (holeMin + rB) + 1 mm)"),
    ("tabW", "2 * rB + 2 * max(6 mm, 2 * t)"),
    ("tabY", "D - t - R - Ltab / 2"),          # folded: the tabs' flat starts R behind the back's inside
    ("yrr", "D - t - R - Ltab - 3 * (R + t) - leg - ret - 5 mm"),   # rear rails' front face
    ("gd", "2 mm"),                            # door gap in front of the lid's lip
    ("yd", "-t - gd - t - R - Ld"),            # door front face
    ("Wd", "Wi + 4 * t"),                      # door width (flush with the lid's flanges)
    ("kD", "glands[gland].d"),
    ("kP", "kD + 30 mm"),                      # knock-out pitch
    ("kY", "D - 45 mm"),                       # knock-outs' row
    ("wmD", unit(9.0)),                        # wall-mount holes: M8 clearance (ISO 273 medium)
    # Door vents: slots 50 x 6 mm, a band of rows at the top and at the bottom.
    ("vHalf", "22 mm"), ("vR", "3 mm"), ("vPx", "60 mm"), ("vPz", "14 mm"),
    ("vCols", "floor((Wd - 100 mm) / vPx)"),
    ("vRows", "max(1, min(4, floor((Hc / 2 - 80 mm) / vPz)))"),
    ("vX0", "-(vCols - 1) * vPx / 2"),
    ("hingeX", "-(Wi / 2 + t - R) + holeMin + 6 mm"),   # hinge holes' x on the door
    # Hinge holes in the left side's lip, at the door's hinge holes' heights: in the side's sketch, the
    # lip's flat starts BA in front of its edge (u = R + t); the holes in the middle of it.
    ("lipHoleU", "R + t - BA - Lside / 2"),
    # Rail bolt holes: in the rail's sketch the leg's flat starts BA past its edge (v = xo); folded, the
    # leg's flat starts R + t behind the rail's face, so the holes lie at y = yr + t + R + leg / 2.
    ("legHoleV", "xo + BA + leg / 2"),
    ("boltY", "yr + t + R + leg / 2"),
    ("boltYr", "yrr + t + R + leg / 2"),
    ("boltZ1", "zU0 + U / 2"), ("boltZ2", "zU0 + nU * U / 2"), ("boltZ3", "zU0 + nU * U - U / 2"),
    ("rRail", "if(railHoles == 1, %s, %s)" % (unit(rk.CAGE_HOLE / 2), unit(rk.M6_TAP / 2))),
]


def main():
    s = rk.stock_commands("3")
    s += rk.spec_variables()
    s.append(["table.set", {"name": "glands", "columns": ["gland", {"name": "d", "unit": "mm"}],
                            "rows": [[n, d] for n, d in KNOCKOUTS]}])
    for name, expr in INPUTS + DERIVED:
        s.append(["variable.set", {"name": name, "expr": expr}])

    s += sides()
    s += lid_and_pan()
    s += back()
    s += rails()
    s += door()

    slate = "#5B7299"
    for b in ("Side left", "Side right", "Lid", "Pan", "Back"):
        s.append(["body.appearance", {"body": b, "color": slate, "metallic": 0.1, "roughness": 0.6}])
    s.append(["body.appearance", {"body": "Door shown", "color": slate, "metallic": 0.1, "roughness": 0.6}])
    for b in ("Rail right", "Rail left", "Rear rail right", "Rear rail left"):
        s.append(["body.appearance", {"body": b, "color": "#7D858C", "metallic": 0.7, "roughness": 0.4}])

    # References from the spec, hidden: the clear 450 mm opening over the U range, from the front rails
    # to the rear rails' place, and a stack of rack-panels (482.6 mm, n U - 0.8 mm) on the front rails.
    s.append(["feature.block", {"name": "Opening", "size": ["opening", "yrr - yr", "nU * U"],
                                "position": ["-opening / 2", "yr", "zU0"]}])
    s.append(["feature.block", {"name": "Ref panel", "size": ["panelW", "2 mm", "nU * U - panelGap"],
                                "position": ["-panelW / 2", "yr - 2 mm", "zU0 + panelGap / 2"]}])
    s.append(["feature.visible", {"feature": ["Opening", "Ref panel"], "visible": False}])

    s += assertions()
    s += publish()
    s.append(["document.info", {
        "title": "19-inch wall rack cabinet",
        "description": "A wall-mount 19-inch rack cabinet (EIA-310-D) of 6 to 15 U, 300 to 600 mm deep, every part bent "
                       "from aluminium or steel sheet: two sides, a lid and a bottom pan with cable knock-outs, a back "
                       "plate with wall-mount holes, front rails (and optionally rear rails) of L or C profile with "
                       "square cage-nut holes or M6 holes on the EIA-310 pattern, and a vented door with hinge holes. "
                       "Panels from the rack-panel Jig bolt onto its rails and fit between its sides. The flat pattern "
                       "of each part, with its bend lines, is written by file.export with sheetMetal (see the README).",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/" + ID,
        "tags": ["19-inch rack", "EIA-310", "rack cabinet", "wall cabinet", "sheet metal", "enclosure"]}])
    s.append(["jig.export", {"path": "dist/%s.3dcraftjig" % ID}])
    return s


def rect_uv(u0, u1, v0, v1):
    """A rectangle counter-clockwise in (u, v): lines 0 (v = v0), 1 (u = u1), 2 (v = v1), 3 (u = u0)."""
    return [[u0, v0], [u1, v0], [u1, v1], [u0, v1]]


def sm(sketch, name, flanges, relief=True, when=None, cover=None, cutouts=None):
    """A part; with relief, its corners relieved, and with cover = [(i, j), ...] closed by the `corner`
    choice, flange i covering flange j's end at each corner."""
    p = {"sketch": sketch, "name": name, "thickness": "t", "radius": "R", "kFactor": "K",
         "flanges": flanges}
    if relief:
        p["relief"] = {"shape": "reliefShape", "size": "s"}
        # And a bend relief at every end of a bend inside its edge (the tabs): the corners' shape, but
        # round for tear (a tear there made the back's flat cross itself).
        p["bendRelief"] = {"shape": "if(reliefShape == 3, 2, reliefShape)", "size": "s"}
    if cover:
        p["corner"] = {"kind": "corner", "gap": "gap"}
        p["corners"] = [{"flanges": [i, j], "kind": "corner", "over": i} for i, j in cover]
    if cutouts:
        p["cutouts"] = cutouts
    if when is not None:
        p["when"] = when
    return ["feature.sheetMetal", p]


def fl(edge, length, direction, **kw):
    f = {"edge": edge, "length": length, "angle": "90 deg", "direction": direction}
    f.update(kw)
    return f


BOLT_Z = ("boltZ1", "boltZ2", "boltZ3")


def sides():
    """The sides: on the yz plane (u = y, v = z), the inner face at x = +-Wi / 2, flanges inward; their
    corners stay open (closed, the corner would run into the bend of the lid's or the pan's front flange,
    which wraps round it). Bolt holes for the front rails' legs; those for the
    rear rails in a cut-out sketch switched by `rear`; the left side's lip has the door's hinge holes
    (a cut-out sketch switched by `door`)."""
    out = []
    for name, off, direction in (("Side right", "Wi / 2", "down"), ("Side left", "-Wi / 2 - t", "up")):
        sk = rk.Sketch("Sketch " + name, "yz", off)
        ln = sk.polyline(rect_uv("R + t", "D", "R + t", "Hc - R - t"))
        for z in BOLT_Z:
            sk.circle(["boltY", z], "rB")
        for z in BOLT_Z:                       # the back's screw tabs
            sk.circle(["tabY", z], "rB")
        out += sk.cmds
        rear = rk.Sketch("Sketch %s rear bolts" % name, "yz", off, when="rear")
        for z in BOLT_Z:
            rear.circle(["boltYr", z], "rB")
        out += rear.cmds
        cut = [rear.name]
        if name == "Side left":
            # A placeholder pattern for the hinges' cabinet leaves (four M4 holes at the door's hinge-hole
            # heights, centred on the lip); drill to the hinge you buy.
            hinge = rk.Sketch("Sketch Side left hinge", "yz", off, when="door")
            h = hinge.circle(["lipHoleU", "60 mm"], "rM4")
            hinge.pattern([h], count="2", step=["0 mm", "20 mm"], count2="2", step2=["0 mm", "Hc - 140 mm"])
            out += hinge.cmds
            cut.append(hinge.name)
        out.append(sm(sk.name, name, [fl(ln[3], "Lside", direction), fl(ln[2], "Lf", direction),
                                      fl(ln[0], "Lf", direction)], cutouts=cut))
    return out


def lid_and_pan():
    """Lid and pan: on the xy plane (u = x, v = y), over the sides' top and under their bottom, three
    flanges (front, left, right) whose insides lie on the sides and on the sides' front lips."""
    out = []
    for name, off, direction in (("Lid", "Hc", "down"), ("Pan", "-t", "up")):
        sk = rk.Sketch("Sketch " + name, "xy", off)
        xe = "Wi / 2 + t - R"
        ln = sk.polyline(rect_uv("-(%s)" % xe, xe, "R", "D"))
        # Cable knock-outs in a row near the back.
        k = sk.circle(["-(knock - 1) * kP / 2", "kY"], "kD / 2")
        sk.pattern([k], count="knock", step=["kP", "0 mm"])
        out += sk.cmds
        out.append(sm(sk.name, name, [fl(ln[0], "Lf", direction), fl(ln[1], "Lf", direction),
                                      fl(ln[3], "Lf", direction)], cover=[(0, 1), (0, 2)]))
    return out


def back():
    """The wall plate: on the zx plane (u = z, v = x) at y = D - t, its back face on the wall, a flange
    bent forward along the top and the bottom, under the sides' top and over their bottom flanges, and
    three screw tabs each side (flanges with an outline of their own, each with an M6 hole) on the sides'
    inner faces, at the rails' bolt heights, screwed to the sides."""
    sk = rk.Sketch("Sketch Back", "zx", "D - t")
    xe = "Wi / 2 - R - t"
    ln = sk.polyline(rect_uv("R + 2 * t", "Hc - R - 2 * t", "-(%s)" % xe, xe))
    w = sk.circle(["zU0 + 40 mm", "-(Wi / 2 - 70 mm)"], "wmD / 2")
    sk.pattern([w], count="2", step=["Hc - 2 * zU0 - 80 mm", "0 mm"], count2="2", step2=["0 mm", "Wi - 140 mm"])
    out = sk.cmds
    # The tabs' outlines, drawn in the plate's plane as if the bends had no width: a rectangle beyond
    # the plate's left (v = -xe) or right (v = xe) edge, its hole in the middle.
    tabs = []
    for side, sv in (("left", "-"), ("right", "")):
        for k, z in enumerate(BOLT_Z):
            tab = rk.Sketch("Sketch Back tab %s %d" % (side, k + 1), "zx", "D - t")
            tab.polyline(rect_uv("%s - tabW / 2" % z, "%s + tabW / 2" % z,
                                 *(["-(%s + Ltab)" % xe, "-(%s)" % xe] if sv else [xe, "%s + Ltab" % xe])))
            tab.circle([z, "%s(%s + Ltab / 2)" % (sv, xe)], "rB")
            out += tab.cmds
            tabs.append({"edge": ln[0] if sv else ln[2], "outline": tab.name, "angle": "90 deg", "direction": "down"})
    # Its corners stay open: they sit in the inside of the sides' top and bottom bends, which a closed
    # corner would run into; with the tabs inset from them, only one flange reaches each corner.
    return out + [sm(sk.name, "Back", [fl(ln[1], "Lf", "down"), fl(ln[3], "Lf", "down")] + tabs)]


def rails():
    """The right front rail in two variants (L and C profile), one on by its `when`, passed on as Rail
    right by a union; its face holes, square or round, are two cut-out sketches switched by railHoles,
    shared by both variants; the left one its mirror; the rear ones moved copies."""
    out, names, cut = [], [], []
    for holes in (1, 2):
        hs = rk.Sketch("Sketch rail %s holes" % ["square", "M6"][holes - 1], "zx", "yr",
                       when="railHoles == %d" % holes)
        seeds = []
        for h in rk.HOLE_NAMES:
            zc = "zU0 + %s" % h
            if holes == 1:
                seeds += hs.square(zc, "holeX", unit(rk.CAGE_HOLE))
            else:
                seeds.append(hs.circle([zc, "holeX"], "rRail"))
        hs.pattern(seeds, count="nU", step=["U", "0 mm"])
        out += hs.cmds
        cut.append(hs.name)
    for profile in (2, 1):
        nm = "Rail %s" % PROFILES[profile - 1]
        when = "profile == %d" % profile
        sk = rk.Sketch("Sketch " + nm, "zx", "yr", when=when)
        ln = sk.polyline(rect_uv("zU0 - mr", "zU0 + nU * U + mr", "opening / 2", "xo"))
        for z in BOLT_Z:                       # the leg's bolt holes, where the leg lies in the flat
            sk.circle([z, "legHoleV"], "rB")
        out += sk.cmds
        flanges = [fl(ln[2], "leg", "up")]
        if profile == 2:
            flanges.append({"tip": 0, "length": "ret", "angle": "90 deg", "direction": "up"})
        out.append(sm(sk.name, nm, flanges, relief=False, when=when, cutouts=cut))
        names.append(nm)
    out.append(["feature.boolean", {"op": "union", "target": names[0], "tool": names[1], "name": "Rail right"}])
    out.append(["feature.mirror", {"source": "Rail right", "normal": [1, 0, 0], "keep": True, "name": "Rail left"}])
    for side in ("right", "left"):
        out.append(["feature.transform", {"source": "Rail " + side, "translate": ["0 mm", "yrr - yr", "0 mm"],
                                          "keep": True, "name": "Rear rail " + side, "when": "rear"}])
    return out


def door():
    """The door: a pan on the zx plane at y = yd, its four flanges bent back towards the cabinet, vent
    slots in a band at the top and the bottom, hinge holes along the left; turned about the hinge line
    (the left front edge) by doorOpen for the view."""
    sk = rk.Sketch("Sketch Door", "zx", "yd", when="door")
    xe = "Wi / 2 + t - R"
    ln = sk.polyline(rect_uv("R", "Hc - R", "-(%s)" % xe, xe))
    top = sk.slot("Hc - R - holeMin - 30 mm", "vX0", "vHalf", "vR")
    bot = sk.slot("R + holeMin + 30 mm", "vX0", "vHalf", "vR")
    hinge = sk.circle(["60 mm", "hingeX"], "rM4")
    sk.pattern(top, count="vCols", step=["0 mm", "vPx"], count2="vRows", step2=["-vPz", "0 mm"])
    sk.pattern(bot, count="vCols", step=["0 mm", "vPx"], count2="vRows", step2=["vPz", "0 mm"])
    sk.pattern([hinge], count="2", step=["20 mm", "0 mm"], count2="2", step2=["Hc - 140 mm", "0 mm"])
    out = sk.cmds
    # The left and the right flange (lines 0 and 2) cover the top and bottom flanges' ends.
    out.append(sm(sk.name, "Door", [fl(e, "Ld", "up") for e in ln], when="door",
                  cover=[(0, 1), (0, 3), (2, 1), (2, 3)]))
    out.append(["feature.transform", {"source": "Door", "angle": "-doorOpen", "axis": [0, 0, 1],
                                      "pivot": ["-Wd / 2", "-t - gd", "0 mm"], "name": "Door shown", "when": "door"}])
    return out


def faces(where):
    return {"kind": "face", "where": where}


def box(lo, hi):
    return {"inside": [lo, hi]}


PARTS = ["Side left", "Side right", "Lid", "Pan", "Back"]


def assertions():
    a = []

    def add(name, measure, **kw):
        kw = {k.rstrip("_"): v for k, v in kw.items()}
        a.append(["assert.add", dict(name=name, measure=measure, **kw)])

    big = "10000 mm"
    every_part = {"kind": "body", "where": {"not": {"any": [{"name": "Opening"}, {"name": "Ref panel"}]}}}
    add("outside: n U + 2 (mr + r + t) high plus lid and pan", "extent", of=PARTS, axis="z", eq="Hc + 2 * t")
    add("outside: as deep as asked to the wall", "boxMax", of=PARTS, axis="y", eq="D")
    add("outside: width", "extent", of=PARTS, axis="x", eq="Wi + 4 * t")

    # Rails on the EIA-310 pattern: in a box round every hole the spec gives (465.1 mm centres, the three
    # holes of every U from the lowest U boundary), the hole's walls (four per square, one per round
    # hole), and no hole of the rail elsewhere.
    per = "if(railHoles == 1, 4, 1)"
    for rail, yf, cond in (("Rail right", "yr", "1"), ("Rail left", "yr", "1"),
                           ("Rear rail right", "yrr", "rear"), ("Rear rail left", "yrr", "rear")):
        sx = "-1" if rail.endswith("left") else "1"
        bx = []
        for k, zc in rk.rail_hole_centres(MAX_U, "zU0"):
            bx.append(box(["%s * holeX - rRail - 0.01 mm" % sx, "%s - 0.01 mm" % yf, "%s - rRail - 0.01 mm" % zc],
                          ["%s * holeX + rRail + 0.01 mm" % sx, "%s + t + 0.01 mm" % yf, "%s + rRail + 0.01 mm" % zc]))
        walls = {"in": rail, "inside": [["-" + big, "%s - 0.01 mm" % yf, "zU0 - mr + 0.01 mm"],
                                        [big, "%s + t + 0.01 mm" % yf, "zU0 + nU * U + mr - 0.01 mm"]],
                 "any": [{"surface": "freeform"}, {"normal": {"perpendicular": "y"}}],
                 "not": {"inside": [["-opening / 2 - 0.01 mm" if sx == "-1" else "opening / 2 - 0.01 mm", "-" + big, "-" + big],
                                    ["-opening / 2 + 0.01 mm" if sx == "-1" else "opening / 2 + 0.01 mm", big, big]]}}
        # The rail's base between its ends: hole walls only (its inner edge at x = 225 mm lies outside the boxes).
        add("%s: holes at the EIA-310 positions, three in every U" % rail, "count",
            of=faces(dict(walls, **{"any": bx})), min="if(%s, 3 * nU * %s, 0)" % (cond, per),
            max="if(%s, 3 * nU * %s * if(railHoles == 1, 1, 2), 0)" % (cond, per))
        add("%s: no hole of its base off the pattern" % rail, "count",
            of=faces(dict(walls, **{"not": {"any": bx + [walls["not"]]}})), eq="0")
    add("rails: the leg against the side (the rail's outside at x = Wi / 2)", "boxMax", of="Rail right", axis="x", eq="Wi / 2")
    add("rails: the front face 450 / 2 mm off the centre line", "boxMin", of="Rail right", axis="x", eq="opening / 2")

    # The 450 mm opening between the rails is clear over the U range, from the front rails to the rear.
    add("the 450 mm opening between the rails is clear", "clearance", from_="Opening", to=every_part, min="0 mm")
    # A stack of rack-panels (the spec's 482.6 mm, n U - 0.8 mm) sits on the front rails and clears the sides.
    add("rack-panels: on the rails' front, inside the cabinet", "clearance", from_="Ref panel", to=every_part,
        min="0 mm", max="0 mm")
    add("rack-panels: their width fits between the sides with clearance", "distance", from_="Ref panel",
        to=["Side left", "Side right"], min="sideClear")
    add("sides: the clear width between them", "distance",
        from_=faces({"in": "Side left", "surface": "plane", "normal": {"along": "x"},
                     "inside": [["-Wi / 2 - 0.01 mm", "-" + big, "-" + big], ["-Wi / 2 + 0.01 mm", big, big]]}),
        to=faces({"in": "Side right", "surface": "plane", "normal": {"along": "-x"},
                  "inside": [["Wi / 2 - 0.01 mm", "-" + big, "-" + big], ["Wi / 2 + 0.01 mm", big, big]]}),
        eq="cabInnerW")
    add("parts: none overlaps another", "overlap", of=every_part, is_=False)

    # The sheet-metal rules on every part that is switched on (rails and door included), by the
    # sheet-metal measures; and the closed corners' gap, measured on the solid, while the corners are
    # closed (open, there is nothing to measure).
    a += rk.sheet_rules(None, label="parts")
    add("closed corners: the gap as given", "cornerGap", eq="gap", tol="0.001 mm", when="corner != 1")
    add("Rail right: every bend", "count", of=faces({"in": "Rail right", "surface": "cylinder", "hole": False}),
        eq="if(profile == 2, 4, 2)")
    add("Rail right: leg and return at least 4 t", "boxMax", of="Rail right", axis="y",
        min="yr + t + R + minFlange + if(profile == 2, R + t, 0 mm)")

    def hole_at(body, x0, x1, y, z, r, ylo=None, yhi=None):
        """Hole walls of `body` of radius r inside the box x0..x1 round (y, z)."""
        return faces({"in": body, "hole": True, "radius": {"eq": r, "tol": "0.001 mm"},
                      "inside": [[x0, "(%s) - (%s) - 0.01 mm" % (y, r), "(%s) - (%s) - 0.01 mm" % (z, r)],
                                 [x1, "(%s) + (%s) + 0.01 mm" % (y, r), "(%s) + (%s) + 0.01 mm" % (z, r)]]})
    # The rails are bolted to the sides: at every bolt place a hole in the rail's leg and one in the side.
    for side, sx in (("right", ""), ("left", "-")):
        lo, hi = ("Wi / 2 - t - 0.01 mm", "Wi / 2 + t + 0.01 mm") if not sx else \
                 ("-Wi / 2 - t - 0.01 mm", "-Wi / 2 + t + 0.01 mm")
        for rail, y, cond in (("Rail " + side, "boltY", "1"), ("Rear rail " + side, "boltYr", "rear")):
            for k, z in enumerate(BOLT_Z):
                for body in (rail, "Side " + side):
                    add("%s: bolt hole %d of %s" % (body, k + 1, rail), "count",
                        of=hole_at(body, lo, hi, y, z, "rB"), eq="if(%s, 1, 0)" % cond)
    # The door's hinge holes in the left side's lip, at the door hinge holes' heights.
    for z in ("60 mm", "80 mm", "Hc - 80 mm", "Hc - 60 mm"):
        add("Side left: hinge hole in the lip at z = %s" % z, "count",
            of=faces({"in": "Side left", "hole": True, "radius": {"eq": "rM4", "tol": "0.001 mm"},
                      "inside": [["-" + big, "-0.01 mm", "(%s) - rM4 - 0.01 mm" % z],
                                 [big, "t + 0.01 mm", "(%s) + rM4 + 0.01 mm" % z]]}),
            eq="if(door, 1, 0)")
    for part in ("Lid", "Pan"):
        add("knock-outs in the %s" % part.lower(), "count",
            of=faces({"in": part, "hole": True, "radius": {"eq": "kD / 2", "tol": "0.001 mm"},
                      "inside": [["-" + big, "kY - kD / 2 - 0.01 mm", "-" + big], [big, "kY + kD / 2 + 0.01 mm", big]]}),
            eq="knock")
    for zc in ("zU0 + 40 mm", "Hc - zU0 - 40 mm"):
        for sx in ("-1", "1"):
            add("wall-mount hole in the back at x = %s(Wi / 2 - 70 mm), z = %s" % ("-" if sx == "-1" else "", zc), "count",
                of=faces({"in": "Back", "hole": True,
                          "inside": [["%s * (Wi / 2 - 70 mm) - wmD / 2 - 0.01 mm" % sx, "D - t - 0.01 mm", "%s - wmD / 2 - 0.01 mm" % zc],
                                     ["%s * (Wi / 2 - 70 mm) + wmD / 2 + 0.01 mm" % sx, "D + 0.01 mm", "%s + wmD / 2 + 0.01 mm" % zc]]}),
                eq="1")
    add("back: four wall-mount holes and one in each of its six screw tabs, no other", "count",
        of=faces({"in": "Back", "hole": True}), eq="10")
    # The back is screwed to the sides: at every tab a hole in the tab and one in the side, in the same
    # box round the place (so they line up).
    for side, sx in (("right", ""), ("left", "-")):
        lo, hi = ("Wi / 2 - t - 0.01 mm", "Wi / 2 + t + 0.01 mm") if not sx else \
                 ("-Wi / 2 - t - 0.01 mm", "-Wi / 2 + t + 0.01 mm")
        for k, z in enumerate(BOLT_Z):
            for body in ("Back", "Side " + side):
                add("%s: screw hole of the back's %s tab %d" % (body, side, k + 1), "count",
                    of=hole_at(body, lo, hi, "tabY", z, "rB"), eq="1")
    add("door: four hinge holes", "count",
        of=faces({"in": "Door shown", "hole": True, "radius": {"eq": "rM4", "tol": "0.001 mm"}}), eq="if(door, 4, 0)")
    add("door: the vent slots' round ends", "count",
        of=faces({"in": "Door shown", "surface": "cylinder", "hole": False, "radius": {"eq": "vR", "tol": "0.001 mm"}}),
        min="if(door, 4 * vCols * vRows, 0)", max="if(door, 8 * vCols * vRows, 0)")
    return a


def publish():
    pub = [
        ("nU", dict(label="Height", description="Rack units of 44.45 mm on the rails", group="Cabinet", order=1,
                    kind="integer", min="6", max=str(MAX_U))),
        ("D", dict(label="Depth", description="From the front to the wall", group="Cabinet", order=2,
                   min="300 mm", max="600 mm", step="10 mm", unit="mm")),
        ("stock", dict(label="Sheet", description="Material and thickness (bend radius and K-factor from the "
                                                  "stock table)", group="Cabinet", order=3, kind="choice",
                       choicesFrom="stocks")),
        ("profile", dict(label="Rail profile", description="L (front face and a leg on the side) or C (with a "
                                                           "return at the back of the leg)", group="Rails",
                         order=1, kind="choice", choices=PROFILES)),
        ("railHoles", dict(label="Rail holes", description="Square holes for M6 cage nuts, or 5 mm holes to tap M6 (only in 2 mm steel: thinner sheet holds too few threads; use rivnuts or clinch nuts there)",
                           group="Rails", order=2, kind="choice", choices=RAIL_HOLES,
                           max="if(stock == 4, 2, 1)")),
        ("rear", dict(label="Rear rails", description="A second pair of rails at the back, for deep equipment",
                      group="Rails", order=3, kind="boolean")),
        ("door", dict(label="Door", description="A vented door hinged at the left, or an open front",
                      group="Door", order=1, kind="boolean")),
        ("doorOpen", dict(label="Door shown open", description="How far the door is shown open (only the view)",
                          group="Door", order=2, min="0 deg", max="110 deg", step="5 deg", unit="deg")),
        ("knock", dict(label="Knock-outs", description="Cable entries in the lid and in the bottom, near the back",
                       group="Cable entry", order=1, kind="integer", min="1", max="4")),
        ("corner", dict(label="Corners", description="How the flanges of the lid, the pan and the door meet at their "
                        "corners: open (each flange ends at its bend), butt, overlap (the lid's and the pan's front "
                        "flange and the door's side flanges cover the other flanges' ends) or miter; the sides' and "
                        "the back's corners, inside the lid's, the pan's and the sides' bends, stay open", group="Corners", order=1, kind="choice", choices=CORNERS)),
        ("gap", dict(label="Corner gap", description="The gap left at a closed corner: at least 0.4 mm (0.015 in, "
                     "SendCutSend's least gap between flanges), a butt's less than the thickness", group="Corners", order=2, min="0.4 mm", max="if(corner == 2, min(2 mm, t - 0.1 mm), 2 mm)",
                     step="0.1 mm", unit="mm")),
        ("reliefShape", dict(label="Corner relief", description="The relief cut at each corner of the flat pattern, "
                             "R + t + 0.5 mm along each edge", group="Corners", order=3, kind="choice",
                             choices=RELIEFS)),
        ("gland", dict(label="Gland size", description="Metric cable gland (EN 50262) the knock-outs take",
                       group="Cable entry", order=2, kind="choice", choicesFrom="glands")),
    ]
    out = []
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        out.append(["variable.publish", p])
    return out


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
