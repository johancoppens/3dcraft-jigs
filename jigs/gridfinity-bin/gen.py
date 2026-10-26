#!/usr/bin/env python3
"""Writes build.json for the Gridfinity bin Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written and is kept so the profiles are
readable. The Gridfinity numbers and the foot profile come from scripts/gridfinitylib.py, shared with
gridfinity-baseplate, so a bin always seats in a plate of that Jig (which checks it with this foot).

The bin: one foot per grid unit (the base profile, a ruled loft), joined by the body up to the top of
the wall (or of the stacking lip). The inside is one ruled loft through the stacking lip's profile with
its floor edges rounded; dividers, label tabs and scoops are taken out of that hollow before it is cut
from the body, so they join the walls without a seam. Magnet and screw holes are cut in every foot.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import gridfinitylib as gf  # noqa: E402

ID = "gridfinity-bin"
MAX_DIVX = 11           # 2 x the widest bin - 1
MAX_DIVY = 6


def unit(v):
    return "%.6g mm" % v


INPUTS = [
    ("gx", "2"),            # grid units along x
    ("gy", "3"),            # grid units along y
    ("hu", "6"),            # height units of 7 mm
    ("divx", "0"),          # dividers across the width (walls parallel to y)
    ("divy", "2"),          # dividers front to back (walls parallel to x)
    ("label", "2"),         # 1 none, 2 back, 3 front
    ("tabA", "36 deg"),     # the label tab's support angle
    ("scoop", "1"),         # a scoop at the front of every row
    ("magnets", "1"),       # magnet holes in the feet
    ("screws", "0"),        # M3 screw holes in the feet
    ("lip", "1"),           # stacking lip
    ("wall", "1.2 mm"),
    ("floorX", "0 mm"),     # extra floor above the base
]
DERIVED = [
    ("grid", unit(gf.GRID)),
    ("gap", unit(gf.GRID - gf.BIN_TOP)),    # a bin is 0.5 mm smaller than its grid
    ("R", unit(gf.BIN_R)),                  # outer corner radius
    ("hx", "(gx * grid - gap) / 2"),
    ("hy", "(gy * grid - gap) / 2"),
    ("H", "hu * %s" % unit(gf.UNIT_H)),     # top of the wall: where the next bin stands
    ("baseH", unit(gf.FOOT_H)),             # the base profile's height
    ("floorZ", "%s + floorX" % unit(gf.BASE_H)),   # the floor inside
    ("lipTop", "H + %s" % unit(gf.LIP_H - 0.4)),   # the lip's 4.4 mm less a 0.4 mm flat on top
    ("topZ", "if(lip, lipTop, H)"),
    ("cx0", "-(gx - 1) * grid / 2"),        # centre of the first unit
    ("cy0", "-(gy - 1) * grid / 2"),
    ("ri", "R - wall"),                     # inner corner radius
    ("wi", "hx - wall"),                    # inner half sizes
    ("di", "hy - wall"),
    ("divT", unit(gf.DIVIDER)),             # divider thickness
    ("cw", "(2 * wi - divx * divT) / (divx + 1)"),   # clear width of a compartment
    ("rd", "(2 * di - divy * divT) / (divy + 1)"),   # clear depth of a row
    ("divTop", "H - 1 mm"),
    # Label tab: its top 0.6 mm under the wall's top (below a stacked bin's feet), 1.2 mm thick at the
    # front, its support at tabA; as deep as the standard's 15.85 mm where the row and the height allow.
    ("tabTop", "H - 0.6 mm"),
    ("tabT", unit(gf.TAB_FRONT)),
    # Scoop: a quarter round at the front of every row, up to 15 mm; under a front label it takes what
    # the tab leaves when the tab is 5 mm deep.
    ("rs0", "min(15 mm, rd / 2, (H - floorZ) / 2)"),
    ("rsF", "if(scoop && label == 3, max(0 mm, min(rs0, tabTop - tabT - floorZ - 1 mm - 5 mm * tan(tabA))), 0 mm)"),
    ("tabL", "min(%s, rd / 2, (tabTop - tabT - floorZ - 1 mm - rsF) / tan(tabA))" % unit(gf.TAB_DEPTH)),
    ("tabLow", "tabTop - tabT - tabL * tan(tabA)"),  # where the support meets the wall or divider
    ("labelOn", "label > 1"),
    ("rs", "if(label == 3, min(rs0, tabLow - floorZ - 1 mm), rs0)"),
    ("scoopOn", "scoop && rs >= 3 mm"),
    ("lipLow", "H - %s - (%s - wall)" % (unit(gf.LIP_SUPPORT), unit(gf.LIP_D))),  # the lip's support meets the wall
    ("holesOn", "magnets || screws"),
    ("stackZ", "if(lip, H - 0.35 mm, H + 10 mm)"),   # where a stacked bin's foot stands
]


def main():
    s = []
    for name, expr in INPUTS + DERIVED:
        s.append(["variable.set", {"name": name, "expr": expr}])

    # One foot of the base, in the first unit, patterned over the grid.
    s += gf.foot("Foot", "0 mm", "cx0", "cy0")
    s.append(["feature.pattern", {"source": "Foot", "count": "gx", "step": ["grid", "0 mm", "0 mm"], "name": "FeetX"}])
    s.append(["feature.pattern", {"source": "FeetX", "count": "gy", "step": ["0 mm", "grid", "0 mm"], "name": "Feet"}])

    # The body above the base, up to the wall's top (or the lip's).
    s += gf.rrect("Outline", "baseH", "hx", "hy", "R")
    s.append(["feature.extrude", {"sketch": "Outline", "distance": "topZ - baseH", "name": "Shell"}])
    s.append(["feature.boolean", {"op": "union", "target": "Shell", "tool": "Feet", "name": "Solid"}])

    # The hollow: a ruled loft through the stacking lip's profile. Without the lip its sections stand
    # straight above one another (inset 0), past the top of the wall.
    d, h1, h2 = unit(gf.LIP_D), unit(gf.LIP_D - 0.7), unit(gf.LIP_SUPPORT)
    lipsec = [("floorZ", "0 mm"),
              ("if(lip, lipLow, H + 0.5 mm)", "0 mm"),
              ("if(lip, H - %s, H + 1 mm)" % h2, "if(lip, %s - wall, 0 mm)" % d),
              ("if(lip, H, H + 1.5 mm)", "if(lip, %s - wall, 0 mm)" % d),
              ("if(lip, H + 0.7 mm, H + 2 mm)", "if(lip, %s - wall, 0 mm)" % h1),
              ("if(lip, H + 2.5 mm, H + 2.5 mm)", "if(lip, %s - wall, 0 mm)" % h1),
              ("if(lip, H + 4.4 mm, H + 3 mm)", "if(lip, -wall, 0 mm)")]
    names = []
    for i, (z, ins) in enumerate(lipsec):
        n = "Lip%d" % i
        names.append(n)
        s += gf.rrect(n, z, "wi - (%s)" % ins, "di - (%s)" % ins, "ri - (%s)" % ins)
    s.append(["feature.loft", {"sections": names, "ruled": True, "name": "LipHollow"}])
    # The floor's edges rounded at the inner corner radius.
    s.append(["feature.fillet", {"name": "Hollow", "radius": "ri", "chain": True,
                                 "edges": [["LipHollow:startCap(e3,e6,e8,e11,e13,e16,e18,e20)", "LipHollow:side(e3,e3)"]]}])

    # Dividers, equally spaced (every compartment as wide, every row as deep), taken out of the hollow.
    s.append(["feature.block", {"name": "DivX", "size": ["divT", "2 * hy + 2 mm", "divTop - floorZ + 1 mm"],
                                "position": ["-wi + cw", "-hy - 1 mm", "floorZ - 1 mm"], "when": "divx > 0"}])
    s.append(["feature.pattern", {"source": "DivX", "count": "max(1, divx)", "step": ["cw + divT", "0 mm", "0 mm"],
                                  "name": "DividersX", "when": "divx > 0"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollow", "tool": "DividersX", "name": "Hollow1"}])
    s.append(["feature.block", {"name": "DivY", "size": ["2 * hx + 2 mm", "divT", "divTop - floorZ + 1 mm"],
                                "position": ["-hx - 1 mm", "di - rd - divT", "floorZ - 1 mm"], "when": "divy > 0"}])
    s.append(["feature.pattern", {"source": "DivY", "count": "max(1, divy)", "step": ["0 mm", "-(rd + divT)", "0 mm"],
                                  "name": "DividersY", "when": "divy > 0"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollow1", "tool": "DividersY", "name": "Hollow2"}])

    # Label tabs: along the back of every row, a prism across the bin whose back reaches half a divider
    # into the wall (or to a divider's middle), mirrored to the front of every row for a front label.
    b = "di + divT / 2"
    s.append(["sketch.create", {"name": "TabSketch", "plane": "yz"}])
    s.append(["sketch.polyline", {"sketch": "TabSketch", "closed": True, "points": [
        [b, "tabTop"], ["di - tabL", "tabTop"], ["di - tabL", "tabTop - tabT"],
        [b, "tabLow - divT / 2 * tan(tabA)"]]}])
    s.append(["feature.extrude", {"sketch": "TabSketch", "distance": "2 * hx + 2 mm", "symmetric": True, "name": "Tab",
                                  "when": "labelOn"}])
    s.append(["feature.pattern", {"source": "Tab", "count": "divy + 1", "step": ["0 mm", "-(rd + divT)", "0 mm"],
                                  "name": "TabRows", "when": "labelOn"}])
    s.append(["feature.mirror", {"source": "TabRows", "normal": [0, 1, 0], "name": "Tabs", "when": "label == 3"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollow2", "tool": "Tabs", "name": "Hollow3"}])

    # Scoops: a quarter round of radius rs between the floor and the front of every row, from the front
    # row (front face -di) back; a row's front is the back face of the divider before it.
    f = "-di"
    s.append(["sketch.create", {"name": "ScoopSketch", "plane": "yz"}])
    # (an arc runs counter-clockwise in the sketch's axes, y and z here: from the wall down to the floor)
    s.append(["sketch.path", {"sketch": "ScoopSketch", "start": ["%s - 0.5 mm" % f, "floorZ - 0.5 mm"], "segments": [
        {"line": ["%s - 0.5 mm" % f, "floorZ + rs"]},
        {"line": [f, "floorZ + rs"]},
        {"arc": ["%s + rs" % f, "floorZ"], "center": ["%s + rs" % f, "floorZ + rs"]},
        {"line": ["%s + rs" % f, "floorZ - 0.5 mm"]},
        {"line": "start"}]}])
    s.append(["feature.extrude", {"sketch": "ScoopSketch", "distance": "2 * hx + 2 mm", "symmetric": True,
                                  "name": "Scoop", "when": "scoopOn"}])
    s.append(["feature.pattern", {"source": "Scoop", "count": "divy + 1", "step": ["0 mm", "rd + divT", "0 mm"],
                                  "name": "Scoops", "when": "scoopOn"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollow3", "tool": "Scoops", "name": "Hollow4"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Solid", "tool": "Hollow4", "name": "Hollowed"}])

    # Holes in the feet, 8 mm in from the sides of every unit: a magnet hole 6.5 x 2.4 mm and/or an M3
    # screw hole 6 mm deep in the same place.
    p = unit(gf.GRID / 2 - gf.HOLE_IN)
    s.append(["feature.cylinder", {"name": "Magnet", "radius": unit(gf.MAGNET_D / 2), "height": unit(gf.MAGNET_DEPTH + 1),
                                   "position": ["cx0 - " + p, "cy0 - " + p, "-1 mm"], "when": "magnets"}])
    s.append(["feature.cylinder", {"name": "Screw", "radius": unit(gf.SCREW_D / 2), "height": unit(gf.SCREW_DEPTH + 1),
                                   "position": ["cx0 - " + p, "cy0 - " + p, "-1 mm"], "when": "screws"}])
    s.append(["feature.boolean", {"op": "union", "target": "Magnet", "tool": "Screw", "name": "Hole", "when": "holesOn"}])
    step = unit(2 * (gf.GRID / 2 - gf.HOLE_IN))
    for src, name, st in (("Hole", "Hole2", [step, "0 mm", "0 mm"]), ("Hole2", "Hole4", ["0 mm", step, "0 mm"]),
                          ("Hole4", "HoleRow", ["grid", "0 mm", "0 mm"]), ("HoleRow", "Holes", ["0 mm", "grid", "0 mm"])):
        cnt = "2" if name in ("Hole2", "Hole4") else ("gx" if name == "HoleRow" else "gy")
        s.append(["feature.pattern", {"source": src, "count": cnt, "step": st, "name": name, "when": "holesOn"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollowed", "tool": "Holes", "name": "Bin"}])
    s.append(["body.appearance", {"body": "Bin", "color": "#2E7D7A", "roughness": 0.6}])

    # A second bin's foot where a stacked bin stands (in the back right unit), hidden: the stacking
    # check. Without the lip it floats 10 mm above the rim.
    s += gf.foot("Stacked foot", "stackZ", "cx0 + (gx - 1) * grid", "cy0 + (gy - 1) * grid")
    s.append(["feature.visible", {"feature": "Stacked foot", "visible": False}])

    s += assertions()
    s += publish()
    s.append(["document.info", {
        "title": "Gridfinity bin",
        "description": "A storage bin for the Gridfinity system: set the width and depth in 42 mm grid units, the height "
                       "in 7 mm units, the dividers each way, a label tab at the back or front of every row (and its "
                       "angle), a scoop for small parts, magnet and screw holes, the stacking lip, the wall and the "
                       "floor. The base and the lip follow the Gridfinity profiles, so the bin fits every Gridfinity "
                       "baseplate (and the Gridfinity baseplate Jig) and stacks on other bins. Print it standing on its "
                       "feet, without supports. Export the body Bin with File > Export... (STL or 3MF). Gridfinity is "
                       "by Zack Freedman (MIT).",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/" + ID,
        "tags": ["Gridfinity", "storage", "bin", "organiser", "3D printing"]}])
    s.append(["jig.export", {"path": "dist/%s.3dcraftjig" % ID}])
    return s


def faces(where):
    return {"kind": "face", "where": where}


def assertions():
    a = []

    def add(name, measure, **kw):
        kw = {k.rstrip("_"): v for k, v in kw.items()}
        a.append(["assert.add", dict(name=name, measure=measure, **kw)])

    big = "1000 mm"
    add("one body to print", "count", of={"kind": "body", "where": {"name": "Bin"}}, eq="1")
    add("width: units x 42 mm - 0.5 mm", "extent", of="Bin", axis="x", eq="gx * grid - gap")
    add("depth: units x 42 mm - 0.5 mm", "extent", of="Bin", axis="y", eq="gy * grid - gap")
    add("stands on z = 0", "boxMin", of="Bin", axis="z", eq="0 mm")
    add("height: units x 7 mm (base included), plus the lip", "boxMax", of="Bin", axis="z",
        eq="if(lip, H + %s, H)" % unit(gf.LIP_H - 0.4))
    # The feet: the bottom faces and the sides of the base profile, area for area, unit for unit.
    hole = math.pi * (gf.MAGNET_D / 2) ** 2
    screw = math.pi * (gf.SCREW_D / 2) ** 2
    add("feet: the bottom of the base profile in every unit (35.6 mm square, 0.8 mm corners, less the holes)",
        "area", of=faces({"in": "Bin", "normal": {"along": "-z"}, "below": {"z": "0.001 mm"}}),
        eq="gx * gy * (%.6f - 4 * if(magnets, %.6f, if(screws, %.6f, 0))) * 1 mm^2" % (gf.foot_bottom_area(), hole, screw),
        tol="0.01 * 1 mm^2")
    add("feet: the sides of the base profile (0.8 / 1.8 / 2.15 mm at 45, 90, 45 deg) in every unit", "area",
        of=faces({"in": "Bin", "below": {"z": unit(gf.FOOT_H + 0.001)},
                  "not": {"any": [{"hole": True}, {"normal": {"along": "-z"}}]}}),
        eq="gx * gy * %.6f * 1 mm^2" % gf.foot_side_area(), tol="0.05 * 1 mm^2")
    # Walls: from the outside to the inside, the wall's thickness, front and back (the side walls are the
    # same offset; their inner faces, cut by every scoop and tab, are too intricate to prove a distance on).
    # The inner face is any flat face facing the inside in the wall's plane (a tab may take its name).
    # On the side of the label tabs the tab may take the inner face over (in a low bin there is no flat
    # inner face left): there, every face facing front or back is at least the wall from the outside.
    lab_out = ["-" + big, "if(label == 3, -%s, hy - 0.001 mm)" % big, "-" + big], \
        [big, "if(label == 3, -hy + 0.001 mm, %s)" % big, big]
    add("wall on the label side is at least the wall thickness", "distance",
        from_=faces({"in": "Bin", "any": [{"normal": {"along": "y"}}, {"normal": {"along": "-y"}}],
                     "inside": list(lab_out)}),
        to=faces({"in": "Bin", "surface": "plane", "any": [{"normal": {"along": "y"}}, {"normal": {"along": "-y"}}],
                  "not": {"inside": list(lab_out)}}),
        min="wall - 0.0001 mm")
    add("wall front (back under a front label) is the wall thickness", "distance",
        from_=faces({"in": "Bin", "any": [{"normal": {"along": "y"}}, {"normal": {"along": "-y"}}],
                     "inside": [["-" + big, "if(label == 3, hy - 0.001 mm, -%s)" % big, "-" + big],
                                [big, "if(label == 3, %s, -hy + 0.001 mm)" % big, big]]}),
        to=faces({"in": "Bin", "surface": "plane",
                  "any": [{"normal": {"along": "y"}}, {"normal": {"along": "-y"}}],
                  "inside": [["-" + big, "if(label == 3, di, -di) - 0.001 mm", "-" + big],
                             [big, "if(label == 3, di, -di) + 0.001 mm", big]]}),
        eq="wall")
    add("wall at least the thinnest printable (%g mm)" % gf.MIN_WALL, "count", of={"kind": "body", "where": {"name": "Bin"}},
        eq="if(wall >= %s, 1, 0)" % unit(gf.MIN_WALL))

    # Dividers: every divider's faces lie where equal compartments put them (in boxes 0.01 mm wide round
    # the expected planes, between the floor and the dividers' top), and there are as many as asked
    # (a face that the dividers the other way cut into pieces keeps one name: it counts once).
    def boxes(axis, count, expected):
        out = []
        for k in range(1, count + 1):
            e = expected(k)
            lo, hi = ["-" + big] * 3, [big] * 3
            i = 0 if axis == "x" else 1
            lo[i], hi[i] = "(%s) - 0.01 mm" % e, "(%s) + 0.01 mm" % e
            lo[2], hi[2] = "floorZ - 1 mm", "divTop + 0.001 mm"
            out.append({"inside": [lo, hi]})
        return out
    xs = boxes("x", MAX_DIVX, lambda k: "-wi + %d * (cw + divT)" % k)
    ys = boxes("y", MAX_DIVY, lambda k: "di - %d * (rd + divT)" % k)
    add("dividers across: as many as asked", "count",
        of=faces({"in": "Bin", "madeBy": "DivX", "normal": {"along": "x"}}), eq="divx")
    add("dividers across: equally spaced, inside the bin, below its top", "count",
        of=faces({"in": "Bin", "madeBy": "DivX", "normal": {"along": "x"}, "any": xs}), eq="divx")
    add("dividers front to back: as many as asked", "count",
        of=faces({"in": "Bin", "madeBy": "DivY", "normal": {"along": "-y"}}), eq="divy")
    add("dividers front to back: equally spaced, inside the bin, below its top", "count",
        of=faces({"in": "Bin", "madeBy": "DivY", "normal": {"along": "-y"}, "any": ys}), eq="divy")
    # Label tabs: one per row, their supports at the angle asked (a face whose normal is the angle's).
    add("label tabs: one per row", "count",
        of=faces({"in": "Bin", "madeBy": "Tab", "normal": {"along": "z"}}), eq="if(labelOn, divy + 1, 0)")
    # The support is the tab's one sloping face in each compartment: it runs from the tab's front edge
    # down to where the angle puts it at the wall or divider (tabLow, the prism's back half a divider on).
    add("label tabs: supported down to where the angle asked puts them", "count",
        of=faces({"in": "Bin", "madeBy": "Tab", "surface": "plane", "normal": {"perpendicular": "x"},
                  "not": {"any": [{"normal": {"along": "y"}}, {"normal": {"along": "-y"}},
                                  {"normal": {"along": "z"}}, {"normal": {"along": "-z"}}]},
                  "inside": [["-" + big, "-" + big, "tabLow - 0.001 mm"], [big, big, "tabTop - tabT + 0.001 mm"]]}),
        eq="if(labelOn, divy + 1, 0)")
    add("label tabs: at least 5 mm deep", "count", of={"kind": "body", "where": {"name": "Bin"}},
        eq="if(tabL >= 5 mm, 1, 0)")
    add("scoops: a quarter round in every compartment", "count",
        of=faces({"in": "Bin", "madeBy": "Scoop", "surface": "cylinder", "radius": "rs"}),
        eq="if(scoopOn, divy + 1, 0)")
    # Stacking: a second bin's foot stands in the lip on its chamfers without entering it: clearance 0.
    # Without the lip there is nothing to stand in: the foot floats 10 mm over the rim, clear of it.
    add("stacking: a bin's foot enters nothing (dividers and tabs stay under it)", "overlap",
        of="Stacked foot", to="Bin", is_=False)
    add("stacking: a bin's foot seats on the lip's chamfers", "clearance", from_="Stacked foot", to="Bin",
        min="0 mm", max="if(lip, 0 mm, 1000 mm)")
    return a


def publish():
    pub = [
        ("gx", dict(label="Width", description="Width in grid units of 42 mm", group="Size", order=1,
                    kind="integer", min="1", max="6")),
        ("gy", dict(label="Depth", description="Depth in grid units of 42 mm", group="Size", order=2,
                    kind="integer", min="1", max=str(MAX_DIVY))),
        ("hu", dict(label="Height", description="Height in units of 7 mm, base included, without the stacking lip "
                                                "(6 is 42 mm)", group="Size", order=3, kind="integer", min="2", max="15")),
        ("divx", dict(label="Dividers across", description="Dividers parallel to the sides: compartments side by side",
                      group="Compartments", order=1, kind="integer", min="0", max="2 * gx - 1")),
        ("divy", dict(label="Dividers front to back", description="Dividers parallel to the front: rows of compartments",
                      group="Compartments", order=2, kind="integer", min="0", max="gy")),
        ("label", dict(label="Label tab", description="A sloping tab along the back or the front of every row, for a "
                                                      "label and to grip the bin", group="Compartments", order=3,
                       kind="choice", choices=["None", "Back", "Front"])),
        ("tabA", dict(label="Label tab angle", description="Slope of the tab's support (36 deg is the standard's; "
                                                           "steeper prints more easily but leaves a shorter tab in a low bin)",
                      group="Compartments", order=4, min="30 deg",
                      max="max(30 deg, min(60 deg, atan((hu * 7 mm - 9.8 mm - floorX) / 5 mm)))",
                      step="1 deg", unit="deg")),
        ("scoop", dict(label="Scoop", description="A rounded front inside every row, so small parts slide out (left "
                                                  "out where a front label leaves less than 3 mm under it)",
                       group="Compartments", order=5, kind="boolean")),
        ("magnets", dict(label="Magnet holes", description="Holes for 6 x 2 mm magnets in the corners of every unit "
                                                           "(6.5 x 2.4 mm)", group="Base", order=1, kind="boolean")),
        ("screws", dict(label="Screw holes", description="M3 holes 6 mm deep in the corners of every unit (with the "
                                                         "magnet holes: above them)", group="Base", order=2, kind="boolean")),
        ("lip", dict(label="Stacking lip", description="The lip on top that the next bin stands in",
                     group="Base", order=3, kind="boolean")),
        ("wall", dict(label="Wall", description="Thickness of the outer walls (with the lip at most 1.8 mm, so the lip's 1.9 mm step stays inside the wall)", group="Walls", order=1,
                      min=unit(gf.MIN_WALL), max="if(lip, 1.8 mm, 2.5 mm)", step="0.05 mm", unit="mm")),
        ("floorX", dict(label="Extra floor", description="Raises the floor inside above the 7 mm base, for a stiffer "
                                                         "bottom or a shallower bin", group="Walls", order=2,
                        min="0 mm", max="max(0 mm, min(10 mm, hu * 7 mm - 17 mm))", step="0.5 mm", unit="mm")),
    ]
    out = []
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        out.append(["variable.publish", p])
    return out


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
