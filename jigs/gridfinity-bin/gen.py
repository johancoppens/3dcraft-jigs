#!/usr/bin/env python3
"""Writes build.json for the Gridfinity bin Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the profiles are readable. Run it again only to change the model.

Dimensions: the Gridfinity system by Zack Freedman (MIT), as written down in
gridfinity.xyz and in kennetek's gridfinity-rebuilt-openscad (MIT):
a 42 mm grid, bins 0.5 mm smaller (41.5 mm a unit), outer corner radius
3.75 mm, a 7 mm height unit, the base profile 0.8 / 1.8 / 2.15 mm (4.75 mm
tall, 2.95 mm in), the stacking lip 0.7 / 1.8 / 1.9 mm (4.4 mm tall, 2.6 mm
in), magnet holes 6.5 x 2.4 mm 8 mm from the sides of a unit.
"""
import json

DRAFT = "gridfinity-bin"


def rrect(name, z, hx, hy, r, cx="0 mm", cy="0 mm"):
    """A rounded rectangle about (cx, cy) on a plane parallel to xy at z:
    half sizes hx, hy and corner radius r (all expressions)."""
    def p(x, y):
        return ["(%s) + (%s)" % (cx, x), "(%s) + (%s)" % (cy, y)]
    X, Y, R = "(%s)" % hx, "(%s)" % hy, "(%s)" % r
    seg = [
        {"line": p(X, "%s - %s" % (Y, R))},
        {"arc": p("%s - %s" % (X, R), Y), "center": p("%s - %s" % (X, R), "%s - %s" % (Y, R))},
        {"line": p("-%s + %s" % (X, R), Y)},
        {"arc": p("-" + X, "%s - %s" % (Y, R)), "center": p("-%s + %s" % (X, R), "%s - %s" % (Y, R))},
        {"line": p("-" + X, "-%s + %s" % (Y, R))},
        {"arc": p("-%s + %s" % (X, R), "-" + Y), "center": p("-%s + %s" % (X, R), "-%s + %s" % (Y, R))},
        {"line": p("%s - %s" % (X, R), "-" + Y)},
        {"arc": "start", "center": p("%s - %s" % (X, R), "-%s + %s" % (Y, R))},
    ]
    return [["sketch.create", {"name": name, "plane": "xy", "offset": z}],
            ["sketch.path", {"sketch": name, "start": p(X, "-%s + %s" % (Y, R)), "segments": seg}]]


INPUTS = [
    ("gx", "2"),            # grid units along x
    ("gy", "2"),            # grid units along y
    ("hu", "3"),            # height units of 7 mm
    ("nx", "2"),            # compartments along x
    ("ny", "2"),            # compartments along y
    ("label", "1"),         # label ledge
    ("magnets", "1"),       # magnet holes in the base
    ("lip", "1"),           # stacking lip
    ("wall", "1.2 mm"),
]
DERIVED = [
    ("grid", "42 mm"),
    ("gap", "0.5 mm"),                      # a bin is 0.5 mm smaller than its grid
    ("R", "3.75 mm"),                       # outer corner radius
    ("hx", "(gx * grid - gap) / 2"),
    ("hy", "(gy * grid - gap) / 2"),
    ("H", "hu * 7 mm"),                     # top of the wall: where the next bin stands
    ("baseH", "4.75 mm"),                   # the base profile's height
    ("floorZ", "7 mm"),                     # the floor inside: one height unit
    ("lipTop", "H + 4 mm"),                 # the lip's 4.4 mm less a 0.4 mm flat on top
    ("topZ", "if(lip, lipTop, H)"),
    ("cx0", "-(gx - 1) * grid / 2"),        # centre of the first unit
    ("cy0", "-(gy - 1) * grid / 2"),
    ("ri", "R - wall"),                     # inner corner radius
    ("wi", "hx - wall"),                    # inner half sizes
    ("di", "hy - wall"),
    ("divT", "1.2 mm"),
    ("scoop", "ri"),                        # radius of the rounded floor                     # divider thickness
    ("divTop", "H - 1 mm"),
    ("ledgeTop", "H - 0.6 mm"),
    ("ledgeT", "1.2 mm"),                   # its thickness at the front
    ("rowD", "2 * di / ny"),                # depth of a row of compartments
    ("colW", "2 * wi / nx"),
    ("ledgeL", "min(12 mm, min(rowD / 2, ledgeTop - ledgeT - divT / 2 - floorZ - 1 mm))"),  # how far the ledge reaches in
    ("lipLow", "H - 1.2 mm - (2.6 mm - wall)"),  # where the lip's support meets the wall
]


def main():
    s = []
    for name, expr in INPUTS + DERIVED:
        s.append(["variable.set", {"name": name, "expr": expr}])

    # One foot of the base, in the first unit: a ruled loft through the profile's corners.
    foot = [("0 mm", "17.8 mm", "0.8 mm"), ("0.8 mm", "18.6 mm", "1.6 mm"),
            ("2.6 mm", "18.6 mm", "1.6 mm"), ("baseH", "20.75 mm", "R")]
    names = []
    for i, (z, h, r) in enumerate(foot):
        n = "Foot%d" % i
        names.append(n)
        s += rrect(n, z, h, h, r, "cx0", "cy0")
    s.append(["feature.loft", {"sections": names, "ruled": True, "name": "Foot"}])
    s.append(["feature.pattern", {"source": "Foot", "count": "gx", "step": ["grid", "0 mm", "0 mm"], "name": "FeetX"}])
    s.append(["feature.pattern", {"source": "FeetX", "count": "gy", "step": ["0 mm", "grid", "0 mm"], "name": "Feet"}])

    # The body above the base, up to the wall's top (or the lip's).
    s += rrect("Outline", "baseH", "hx", "hy", "R")
    s.append(["feature.extrude", {"sketch": "Outline", "distance": "topZ - baseH", "name": "Shell"}])
    s.append(["feature.boolean", {"op": "union", "target": "Shell", "tool": "Feet", "name": "Solid"}])

    # The hollow: a ruled loft through the stacking lip's profile. Without the lip its sections
    # stand straight above one another (inset 0), past the top of the wall.
    lipsec = [("floorZ", "0 mm"),
              ("if(lip, lipLow, H + 0.5 mm)", "0 mm"),
              ("if(lip, H - 1.2 mm, H + 1 mm)", "if(lip, 2.6 mm - wall, 0 mm)"),
              ("if(lip, H, H + 1.5 mm)", "if(lip, 2.6 mm - wall, 0 mm)"),
              ("if(lip, H + 0.7 mm, H + 2 mm)", "if(lip, 1.9 mm - wall, 0 mm)"),
              ("if(lip, H + 2.5 mm, H + 2.5 mm)", "if(lip, 1.9 mm - wall, 0 mm)"),
              ("if(lip, H + 4.4 mm, H + 3 mm)", "if(lip, -wall, 0 mm)")]
    names = []
    for i, (z, ins) in enumerate(lipsec):
        n = "Lip%d" % i
        names.append(n)
        s += rrect(n, z, "wi - (%s)" % ins, "di - (%s)" % ins, "ri - (%s)" % ins)
    s.append(["feature.loft", {"sections": names, "ruled": True, "name": "LipHollow"}])
    # A rounded floor, easy to scoop out: the hollow's bottom edges rounded.
    s.append(["feature.fillet", {"name": "Hollow", "radius": "scoop", "chain": True,
                                 "edges": [["F18:startCap(e3,e6,e8,e11,e13,e16,e18,e20)", "F18:side(e3,e3)"]]}])

    # Dividers and label ledges are taken out of the hollow before it is cut.
    s.append(["feature.block", {"name": "DivX", "size": ["divT", "2 * hy + 2 mm", "divTop - floorZ + 1 mm"],
                                "position": ["-wi + colW - divT / 2", "-hy - 1 mm", "floorZ - 1 mm"]}])
    s.append(["feature.pattern", {"source": "DivX", "count": "max(1, nx - 1)", "step": ["colW", "0 mm", "0 mm"], "name": "DividersX"}])
    s.append(["feature.when", {"feature": "DivX", "expr": "nx > 1"}])
    s.append(["feature.when", {"feature": "DividersX", "expr": "nx > 1"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollow", "tool": "DividersX", "name": "Hollow1"}])
    s.append(["feature.block", {"name": "DivY", "size": ["2 * hx + 2 mm", "divT", "divTop - floorZ + 1 mm"],
                                "position": ["-hx - 1 mm", "di - rowD - divT / 2", "floorZ - 1 mm"]}])
    s.append(["feature.pattern", {"source": "DivY", "count": "max(1, ny - 1)", "step": ["0 mm", "-rowD", "0 mm"], "name": "DividersY"}])
    s.append(["feature.when", {"feature": "DivY", "expr": "ny > 1"}])
    s.append(["feature.when", {"feature": "DividersY", "expr": "ny > 1"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollow1", "tool": "DividersY", "name": "Hollow2"}])
    # A ledge along the back of every row: a prism across the bin, its back in the wall or divider.
    s.append(["sketch.create", {"name": "LedgeSketch", "plane": "yz"}])
    s.append(["sketch.polyline", {"sketch": "LedgeSketch", "closed": True, "points": [
        ["di + divT / 2", "ledgeTop"], ["di - ledgeL", "ledgeTop"], ["di - ledgeL", "ledgeTop - ledgeT"],
        ["di + divT / 2", "ledgeTop - ledgeT - ledgeL - divT / 2"]]}])
    s.append(["feature.extrude", {"sketch": "LedgeSketch", "distance": "2 * hx + 2 mm", "symmetric": True, "name": "Ledge"}])
    s.append(["feature.pattern", {"source": "Ledge", "count": "ny", "step": ["0 mm", "-rowD", "0 mm"], "name": "Ledges"}])
    s.append(["feature.when", {"feature": "Ledge", "expr": "label"}])
    s.append(["feature.when", {"feature": "Ledges", "expr": "label"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollow2", "tool": "Ledges", "name": "Hollow3"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Solid", "tool": "Hollow3", "name": "Hollowed"}])

    # Magnet holes, 6.5 mm x 2.4 mm, 8 mm from the sides of every unit.
    s.append(["feature.cylinder", {"name": "Magnet", "radius": "3.25 mm", "height": "3.4 mm",
                                   "position": ["cx0 - 13 mm", "cy0 - 13 mm", "-1 mm"]}])
    s.append(["feature.pattern", {"source": "Magnet", "count": "2", "step": ["26 mm", "0 mm", "0 mm"], "name": "Magnet2"}])
    s.append(["feature.pattern", {"source": "Magnet2", "count": "2", "step": ["0 mm", "26 mm", "0 mm"], "name": "Magnet4"}])
    s.append(["feature.pattern", {"source": "Magnet4", "count": "gx", "step": ["grid", "0 mm", "0 mm"], "name": "MagnetRow"}])
    s.append(["feature.pattern", {"source": "MagnetRow", "count": "gy", "step": ["0 mm", "grid", "0 mm"], "name": "Magnets"}])
    for f in ("Magnet", "Magnet2", "Magnet4", "MagnetRow", "Magnets"):
        s.append(["feature.when", {"feature": f, "expr": "magnets"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "Hollowed", "tool": "Magnets", "name": "Bin"}])
    s.append(["body.appearance", {"body": "Bin", "color": "#2E7D7A", "roughness": 0.6}])
    s.append(["assert.add", {"name": "one body", "measure": "count", "of": {"kind": "body"}, "eq": "1"}])
    s.append(["assert.add", {"name": "footprint", "measure": "extent", "of": "Bin", "axis": "x", "eq": "2 * hx"}])
    pub = [
        ("gx", dict(label="Width", description="Width in grid units of 42 mm", group="Size", order=1,
                    kind="integer", min="1", max="5")),
        ("gy", dict(label="Depth", description="Depth in grid units of 42 mm", group="Size", order=2,
                    kind="integer", min="1", max="5")),
        ("hu", dict(label="Height", description="Height in units of 7 mm, without the stacking lip (6 is 42 mm)",
                    group="Size", order=3, kind="integer", min="2", max="12")),
        ("nx", dict(label="Compartments across", description="Compartments side by side along the width",
                    group="Compartments", order=1, kind="integer", min="1", max="2 * gx + 1")),
        ("ny", dict(label="Compartments deep", description="Rows of compartments front to back",
                    group="Compartments", order=2, kind="integer", min="1", max="gy + 1")),
        ("label", dict(label="Label ledge", description="A sloping ledge at the back of every row, for a label and to grip the bin",
                       group="Options", order=1, kind="boolean")),
        ("lip", dict(label="Stacking lip", description="The lip on top that the next bin stands in",
                     group="Options", order=2, kind="boolean")),
        ("magnets", dict(label="Magnet holes", description="Holes for 6 x 2 mm magnets in the corners of every unit (6.5 x 2.4 mm)",
                         group="Options", order=3, kind="boolean")),
        ("wall", dict(label="Wall", description="Thickness of the outer walls",
                      group="Options", order=4, min="0.8 mm", max="2 mm", step="0.05 mm", unit="mm")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        s.append(["variable.publish", p])
    s.append(["document.info", {
        "title": "Gridfinity bin",
        "description": "A storage bin for the Gridfinity system: set the width and depth in 42 mm grid units, the height "
                       "in 7 mm units, the compartments, and switch the label ledge, the stacking lip and the magnet holes "
                       "on or off. The base and the lip follow the Gridfinity profiles, so the bin fits any Gridfinity "
                       "baseplate and stacks on other bins. Print it standing on its feet, without supports. Export it "
                       "with File > Export... (STL or 3MF). Gridfinity is by Zack Freedman (MIT).",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/gridfinity-bin",
        "tags": ["Gridfinity", "storage", "bin", "organiser", "3D printing"]}])
    s.append(["jig.export", {"path": "dist/gridfinity-bin.3dcraftjig"}])
    return s


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
