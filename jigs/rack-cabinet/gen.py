#!/usr/bin/env python3
"""Writes build.json for the wall-mount 19-inch rack cabinet Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written. The rack numbers (EIA-310-D,
IEC 60297-3-100) and the sheet stock table come from scripts/racklib.py, shared with rack-panel: the
rails carry the hole pattern a rack-panel bolts onto, and the sides stand the width apart that the panel
Jig checks it fits between.

Every part is a sheet-metal part (feature.sheetMetal) bent from one sheet, with its holes in the base's
sketch (so they are in its flat pattern), its corners relieved:
- two sides (plate along y-z) with a front lip, a top and a bottom flange bent inward;
- a lid and a bottom pan with three flanges (front, left, right) over the sides, cable knock-outs near
  the back;
- a back plate (the wall plate) with four flanges forward, inside the sides, and four wall-mount holes;
- two front rails, L or C profile, square cage-nut holes or M6 tap holes on the EIA-310 pattern, their
  legs against the sides; optionally the same two rails at the back;
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
]
DERIVED = [
    ("Wi", "cabInnerW"),                       # clear width between the sides
    ("mr", "5 mm"),                             # the rails reach this far past the U range
    ("Hc", "nU * U + 2 * (mr + R + t)"),        # the sides' height
    ("zU0", "R + t + mr"),                      # the lowest U boundary
    ("s", "R + t + 1 mm"),                     # relief size (each edge and its flange end s from a corner)
    ("Lside", "max(25 mm, minFlange)"),        # sides: front lip
    ("Lf", "max(20 mm, minFlange)"),           # other flanges
    ("Ld", "max(15 mm, minFlange)"),           # door flanges
    ("leg", "max(30 mm, minFlange)"),          # rail leg against the side
    ("ret", "max(15 mm, minFlange)"),          # C rail's return
    ("yr", "50 mm"),                           # front rails' front face (room for handles behind the door)
    ("xo", "Wi / 2 - R - t"),                  # rails' outer bend line: the leg's outside on the side
    ("yrr", "D - t - R - Lf - 3 * (R + t) - leg - ret - 5 mm"),   # rear rails' front face
    ("gd", "2 mm"),                            # door gap in front of the lid's lip
    ("yd", "-t - gd - t - R - Ld"),            # door front face
    ("Wd", "Wi + 4 * t"),                      # door width (flush with the lid's flanges)
    ("kD", "glands[gland].d"),
    ("kP", "kD + 30 mm"),                      # knock-out pitch
    ("kY", "D - 45 mm"),                       # knock-outs' row
    ("wmD", unit(9.0)),                        # wall-mount holes: M8 clearance (ISO 273 medium)
    # Door vents: slots 50 x 6 mm, a band of rows at the top and at the bottom.
    ("vHalf", "22 mm"), ("vR", "max(3 mm, 1.7 * t)"), ("vPx", "60 mm"), ("vPz", "14 mm"),
    ("vCols", "floor((Wd - 100 mm) / vPx)"),
    ("vRows", "max(1, min(4, floor((Hc / 2 - 80 mm) / vPz)))"),
    ("vX0", "-(vCols - 1) * vPx / 2"),
    ("hingeX", "-(Wi / 2 + t - R) + holeMin + 6 mm"),   # hinge holes' x on the door
    ("rM4", unit(rk.M4_CLEAR / 2)),
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


def sm(sketch, name, flanges, relief=True, when=None):
    p = {"sketch": sketch, "name": name, "thickness": "t", "radius": "R", "kFactor": "K",
         "flanges": flanges}
    if relief:
        p["relief"] = {"shape": "round", "size": "s"}
    if when is not None:
        p["when"] = when
    return ["feature.sheetMetal", p]


def fl(edge, length, direction, **kw):
    f = {"edge": edge, "length": length, "angle": "90 deg", "direction": direction}
    f.update(kw)
    return f


def sides():
    """The sides: on the yz plane (u = y, v = z), the inner face at x = +-Wi / 2, flanges inward."""
    out = []
    for name, off, direction in (("Side right", "Wi / 2", "down"), ("Side left", "-Wi / 2 - t", "up")):
        sk = rk.Sketch("Sketch " + name, "yz", off)
        ln = sk.polyline(rect_uv("R + t", "D", "R + t", "Hc - R - t"))
        out += sk.cmds
        out.append(sm(sk.name, name, [fl(ln[3], "Lside", direction), fl(ln[2], "Lf", direction),
                                      fl(ln[0], "Lf", direction)]))
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
                                      fl(ln[3], "Lf", direction)]))
    return out


def back():
    """The wall plate: on the zx plane (u = z, v = x) at y = D - t, its back face on the wall, four
    flanges bent forward inside the sides, under the sides' top and over their bottom flanges."""
    sk = rk.Sketch("Sketch Back", "zx", "D - t")
    xe = "Wi / 2 - R - t"
    ln = sk.polyline(rect_uv("R + 2 * t", "Hc - R - 2 * t", "-(%s)" % xe, xe))
    w = sk.circle(["zU0 + 40 mm", "-(Wi / 2 - 70 mm)"], "wmD / 2")
    sk.pattern([w], count="2", step=["Hc - 2 * zU0 - 80 mm", "0 mm"], count2="2", step2=["0 mm", "Wi - 140 mm"])
    return sk.cmds + [sm(sk.name, "Back", [fl(e, "Lf", "down") for e in ln])]


def rails():
    """The right front rail in four variants (profile x holes), one on by its `when`, passed on as Rail
    right by a chain of unions; the left one its mirror; the rear ones moved copies."""
    out, names = [], []
    for profile in (2, 1):
        for holes in (1, 2):
            nm = "Rail %s %s" % (PROFILES[profile - 1], ["square", "M6"][holes - 1])
            when = "profile == %d && railHoles == %d" % (profile, holes)
            sk = rk.Sketch("Sketch " + nm, "zx", "yr", when=when)
            ln = sk.polyline(rect_uv("zU0 - mr", "zU0 + nU * U + mr", "opening / 2", "xo"))
            seeds = []
            for h in rk.HOLE_NAMES:
                zc = "zU0 + %s" % h
                if holes == 1:
                    seeds += sk.square(zc, "holeX", unit(rk.CAGE_HOLE))
                else:
                    seeds.append(sk.circle([zc, "holeX"], "rRail"))
            sk.pattern(seeds, count="nU", step=["U", "0 mm"])
            out += sk.cmds
            flanges = [fl(ln[2], "leg", "up")]
            if profile == 2:
                flanges.append({"tip": 0, "length": "ret", "angle": "90 deg", "direction": "up"})
            out.append(sm(sk.name, nm, flanges, relief=False, when=when))
            names.append(nm)
    prev = names[0]
    for i, nm in enumerate(names[1:]):
        o = "Rail right" if i == len(names) - 2 else "Rail union %d" % (i + 1)
        out.append(["feature.boolean", {"op": "union", "target": prev, "tool": nm, "name": o}])
        prev = o
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
    out.append(sm(sk.name, "Door", [fl(e, "Ld", "up") for e in ln], when="door"))
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

    # The sheet-metal rules, on every part that is always there.
    for p in PARTS:
        a += rk.sheet_rules(p, holes=not p.startswith("Side"))     # the sides have no holes
    # Rails and door are switched by `when` (and bendRadius, flangeLength, holeToBend refuse a part that
    # is off, repro-rack-2): their rules on the geometry. Bends are the cylinders of a part.
    for body, nb, cond, base_y in (("Rail right", "if(profile == 2, 4, 2)", "1", "yr"),
                                   ("Door shown", "8", "door", None)):
        add("%s: bends at least the stock's minimum radius" % body, "count",
            of=faces({"in": body, "surface": "cylinder", "radius": {"min": "minR - 0.0001 mm", "max": big}}),
            eq="if(%s, %s, 0)" % (cond, nb))
        add("%s: every bend" % body, "count", of=faces({"in": body, "surface": "cylinder"}), eq="if(%s, %s, 0)" % (cond, nb))
    add("Rail right: holes at least 2.5 t + r from the bend", "distance",
        from_=faces({"in": "Rail right", "inside": [["opening / 2 + 0.01 mm", "yr - 0.01 mm", "zU0 - mr + 0.01 mm"],
                                                 ["xo - 0.01 mm", "yr + t + 0.01 mm", "zU0 + nU * U + mr - 0.01 mm"]],
                     "any": [{"surface": "freeform"}, {"normal": {"perpendicular": "y"}}]}),
        to=faces({"in": "Rail right", "surface": "cylinder"}), min="holeMin")
    add("Rail right: leg and return at least 4 t", "boxMax", of="Rail right", axis="y",
        min="yr + t + R + minFlange + if(profile == 2, R + t, 0 mm)")
    add("knock-outs in the lid", "count",
        of=faces({"in": "Lid", "surface": "freeform", "inside": [["-" + big, "kY - kD / 2 - 0.01 mm", "-" + big], [big, "kY + kD / 2 + 0.01 mm", big]]}),
        min="knock", max="2 * knock")
    add("knock-outs in the pan", "count",
        of=faces({"in": "Pan", "surface": "freeform", "inside": [["-" + big, "kY - kD / 2 - 0.01 mm", "-" + big], [big, "kY + kD / 2 + 0.01 mm", big]]}),
        min="knock", max="2 * knock")
    for zc in ("zU0 + 40 mm", "Hc - zU0 - 40 mm"):
        for sx in ("-1", "1"):
            add("wall-mount hole in the back at x = %s(Wi / 2 - 70 mm), z = %s" % ("-" if sx == "-1" else "", zc), "count",
                of=faces({"in": "Back", "surface": "freeform",
                          "inside": [["%s * (Wi / 2 - 70 mm) - wmD / 2 - 0.01 mm" % sx, "D - t - 0.01 mm", "%s - wmD / 2 - 0.01 mm" % zc],
                                     ["%s * (Wi / 2 - 70 mm) + wmD / 2 + 0.01 mm" % sx, "D + 0.01 mm", "%s + wmD / 2 + 0.01 mm" % zc]]}),
                min="1", max="2")
    add("wall-mount holes: no other hole in the back", "count", of=faces({"in": "Back", "surface": "freeform"}),
        min="4", max="8")
    add("door: four hinge holes and the vent slots' round ends", "count",
        of=faces({"in": "Door shown", "surface": "freeform"}), min="if(door, 4 + 4 * vCols * vRows, 0)",
        max="if(door, 8 + 8 * vCols * vRows, 0)")
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
