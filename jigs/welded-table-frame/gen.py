#!/usr/bin/env python3
"""Writes build.json for the welded table frame Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the profile table and the layout of the pieces are readable.

Coordinates: x along the length, y across the width, z up; the frame's outside
corner at the origin, the floor at z = 0. Every piece is a body of its own
(the cut list counts and measures them).
"""
import json

# Common cold-formed hollow sections (EN 10219-2) and hot-rolled equal angles
# (EN 10056-1). h: height of a rail standing on edge, w: its width, t: wall;
# kind 1 a tube, 2 an angle; rOut: a tube's outside corner radius (2 t, inside
# EN 10219-2's 1.6 t to 2.4 t; an angle's edges get 0.5 mm); rIn: a tube's
# inside corner radius (t), or an angle's root radius r1 (EN 10056-1).
PROFILES = [
    ("SHS 20x20x2", 20, 20, 2, 1, 4, 2),
    ("SHS 25x25x2", 25, 25, 2, 1, 4, 2),
    ("SHS 30x30x2", 30, 30, 2, 1, 4, 2),
    ("SHS 40x40x2", 40, 40, 2, 1, 4, 2),
    ("SHS 40x40x3", 40, 40, 3, 1, 6, 3),
    ("SHS 50x50x3", 50, 50, 3, 1, 6, 3),
    ("SHS 60x60x3", 60, 60, 3, 1, 6, 3),
    ("RHS 40x20x2", 40, 20, 2, 1, 4, 2),
    ("RHS 50x30x2", 50, 30, 2, 1, 4, 2),
    ("RHS 60x40x3", 60, 40, 3, 1, 6, 3),
    ("RHS 80x40x3", 80, 40, 3, 1, 6, 3),
    ("L 30x30x3", 30, 30, 3, 2, 0.5, 5),
    ("L 40x40x4", 40, 40, 4, 2, 0.5, 6),
    ("L 50x50x5", 50, 50, 5, 2, 0.5, 7),
]
DEFAULT_PROFILE = 4  # SHS 40x40x2

STEEL = {"color": "#7D858C", "metallic": 0.85, "roughness": 0.45}
ZINC = {"color": "#B9BEC4", "metallic": 0.9, "roughness": 0.35}
PAD = {"color": "#2E7D7A", "roughness": 0.7}

steps = []
fid = [0]  # features and sketches are numbered F1, F2, ... in history order


def cmd(c, **p):
    steps.append([c, p])
    if c == "sketch.create" or (c.startswith("feature.") and c not in ("feature.when", "feature.rename")):
        fid[0] += 1
        return "F%d" % fid[0]
    return None


def var(name, expr):
    cmd("variable.set", name=name, expr=expr)


def when(feature, expr):
    cmd("feature.when", feature=feature, expr=expr)


class Sketch:
    """A sketch whose entity ids are counted here (e1, e2, ... in order)."""

    def __init__(self, name, plane, offset=None):
        p = {"name": name, "plane": plane}
        if offset is not None:
            p["offset"] = offset
        cmd("sketch.create", **p)
        self.name = name
        self.n = 0

    def _new(self):
        self.n += 1
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

    def poly(self, pts):
        ids = [self.pt(x, y) for x, y in pts]
        for i in range(len(ids)):
            self.line(ids[i], ids[(i + 1) % len(ids)])

    def rounded_rect(self, x0, y0, x1, y1, r):
        """Counter-clockwise; r > 0 on every corner."""
        def p(a, op, b):
            return "%s %s %s" % (a, op, b)
        pts = [(p(x0, "+", r), y0), (p(x1, "-", r), y0),
               (x1, p(y0, "+", r)), (x1, p(y1, "-", r)),
               (p(x1, "-", r), y1), (p(x0, "+", r), y1),
               (x0, p(y1, "-", r)), (x0, p(y0, "+", r))]
        centres = [(p(x1, "-", r), p(y0, "+", r)), (p(x1, "-", r), p(y1, "-", r)),
                   (p(x0, "+", r), p(y1, "-", r)), (p(x0, "+", r), p(y0, "+", r))]
        ids = [self.pt(x, y) for x, y in pts]
        for k in range(4):
            self.line(ids[2 * k], ids[2 * k + 1])
            c = self.pt(*centres[k])
            self.arc(c, ids[2 * k + 1], ids[(2 * k + 2) % 8])


def main():
    cmd("table.set", name="profiles",
        columns=["profile", {"name": "h", "unit": "mm"}, {"name": "w", "unit": "mm"},
                 {"name": "t", "unit": "mm"}, "kind", {"name": "rOut", "unit": "mm"},
                 {"name": "rIn", "unit": "mm"}],
        rows=[list(r) for r in PROFILES])
    # Inputs.
    var("L", "1200 mm")
    var("W", "600 mm")
    var("H", "750 mm")
    var("profile", str(DEFAULT_PROFILE))
    var("mitre", "1")
    var("cross", "1")
    var("crossH", "150 mm")
    var("feet", "1")
    # The profile.
    var("h", "profiles[profile].h")
    var("w", "profiles[profile].w")
    var("t", "profiles[profile].t")
    var("rOut", "profiles[profile].rOut")
    var("rIn", "profiles[profile].rIn")
    var("isAngle", "profiles[profile].kind == 2")
    # An angle frame is always mitred at the top: an angle cannot butt
    # against an angle leg and keep its faces flush.
    var("mitred", "mitre || isAngle")
    # The legs' footprint: a tube leg h along x and w along y (a rectangular
    # tube shows its narrow side at the ends of the table); an angle leg w by w.
    var("legX", "if(isAngle, w, h)")
    var("legY", "w")
    # What a bar's section has cut out of its outside rounded rectangle: a
    # tube's bore, or for an angle the quarter beyond its two flanges (the
    # corner at (t, t) rounded with the root radius).
    var("cutEnd", "if(isAngle, 5 mm, -t)")       # how far the cut reaches past the far sides
    # Levelling feet: a 5 mm end plate under each leg, a zinc-plated M10 or
    # M12 stud with a lock nut, and a round pad.
    var("plateT", "5 mm")
    var("big", "min(legX, legY) >= 40 mm")
    var("studD", "if(big, 12 mm, 10 mm)")
    var("nutS", "if(big, 19 mm, 17 mm)")          # across flats, ISO 4032
    var("nutM", "if(big, 10.8 mm, 8.4 mm)")       # height, ISO 4032
    var("studL", "16 mm")
    var("padD", "clamp(min(legX, legY) + 10 mm, 32 mm, 60 mm)")
    var("padH", "10 mm")
    var("footH", "if(feet, plateT + studL + padH, 0 mm)")
    # The cut list (see README): every piece's length and mitre angle.
    var("legQty", "4")
    var("legLen", "H - footH - if(mitred, h, 0 mm)")
    var("topLongX0", "if(mitred, 0 mm, legX)")
    var("topShortY0", "if(mitred, 0 mm, legY)")
    var("topLongLen", "L - 2 * topLongX0")
    var("topShortLen", "W - 2 * topShortY0")
    var("topMitre", "if(mitred, 45 deg, 0 deg)")
    var("crossQty", "if(cross, 4, 0)")
    var("crossLongLen", "L - 2 * legX")
    var("crossShortLen", "W - 2 * legY")
    var("crossMitre", "0 deg")
    var("plateQty", "if(feet, 4, 0)")
    var("topZ", "H - h")
    var("totalLen", "legQty * legLen + 2 * (topLongLen + topShortLen) + if(cross, 2 * (crossLongLen + crossShortLen), 0 mm)")

    # A leg at the origin corner: the outside rounded rectangle, less the bore
    # (tube) or the quarter beyond the flanges (angle; heel at the origin).
    Sketch("LegOutline", "xy", offset="footH").rounded_rect("0 mm", "0 mm", "legX", "legY", "rOut")
    cmd("feature.extrude", sketch="LegOutline", distance="legLen", name="LegBar")
    Sketch("LegCutOutline", "xy", offset="footH - 1 mm").rounded_rect("t", "t", "legX + cutEnd", "legY + cutEnd", "rIn")
    cmd("feature.extrude", sketch="LegCutOutline", distance="legLen + 2 mm", name="LegCut")
    cmd("feature.boolean", op="subtract", target="LegBar", tool="LegCut", name="Leg1")

    # A rail: its section on the yz plane at x = x0 (sketch x = world y, inward;
    # sketch y = world z), extruded along +x; with mitre_when, mitred at both
    # ends (the triangles x - x0 < y and x - x0 > length - y are cut away).
    def rail(name, x0, z0, length, mitre_when=None, cond=None):
        made = []
        Sketch(name + "Outline", "yz", offset=x0).rounded_rect("0 mm", z0, "w", "%s + h" % z0, "rOut")
        made.append(cmd("feature.extrude", sketch=name + "Outline", distance=length, name=name + "Bar"))
        Sketch(name + "CutOutline", "yz", offset="%s - 1 mm" % x0).rounded_rect(
            "t", "%s + if(isAngle, -5 mm, t)" % z0, "w + cutEnd", "%s + h - t" % z0, "rIn")
        made.append(cmd("feature.extrude", sketch=name + "CutOutline", distance="%s + 2 mm" % length, name=name + "Cut"))
        last = name + ("Bored" if mitre_when else "")
        made.append(cmd("feature.boolean", op="subtract", target=name + "Bar", tool=name + "Cut", name=last))
        names = [name + "Bar", name + "Cut", last]
        if mitre_when:
            m = Sketch(name + "Mitres", "xy", offset="%s - 1 mm" % z0)
            m.poly([("%s - 2 mm" % x0, "-2 mm"), ("%s + w + 2 mm" % x0, "w + 2 mm"), ("%s - 2 mm" % x0, "w + 2 mm")])
            m.poly([("%s + %s + 2 mm" % (x0, length), "-2 mm"), ("%s + %s + 2 mm" % (x0, length), "w + 2 mm"),
                    ("%s + %s - w - 2 mm" % (x0, length), "w + 2 mm")])
            cmd("feature.extrude", sketch=name + "Mitres", distance="h + 2 mm", name=name + "MitreTool")
            when(name + "MitreTool", mitre_when)
            cmd("feature.boolean", op="subtract", target=last, tool=name + "MitreTool", name=name)
            names.append(name)
        if cond:
            for n in names:
                when(n, cond)

    rail("TopFront", "topLongX0", "topZ", "topLongLen", mitre_when="mitred")
    rail("TopLeftBar", "topShortY0", "topZ", "topShortLen", mitre_when="mitred")
    cmd("feature.transform", source="TopLeftBar", angle="-90 deg", axis=[0, 0, 1],
        translate=["0 mm", "W", "0 mm"], name="TopLeft")
    rail("CrossFront", "legX", "crossH", "crossLongLen", cond="cross")
    rail("CrossLeftBar", "legY", "crossH", "crossShortLen", cond="cross")
    cmd("feature.transform", source="CrossLeftBar", angle="-90 deg", axis=[0, 0, 1],
        translate=["0 mm", "W", "0 mm"], name="CrossLeft")
    when("CrossLeft", "cross")

    # Feet: an end plate welded under the leg, and a levelling foot screwed
    # into it (stud, lock nut and pad), centred under the leg.
    plate = cmd("feature.block", name="PlateBlock", size=["legX", "legY", "plateT"],
                position=["0 mm", "0 mm", "padH + studL"])
    cmd("feature.chamfer", name="Plate1", distance="1 mm",
        edges=[["%s:face(%d)" % (plate, a), "%s:face(%d)" % (plate, b)] for a, b in ((2, 4), (2, 5), (3, 4), (3, 5))])
    pad = cmd("feature.cylinder", name="PadDisc", radius="padD / 2", height="padH",
              position=["legX / 2", "legY / 2", "0 mm"])
    cmd("feature.chamfer", name="PadChamfer", distance="1 mm", edges=[["%s:face(1)" % pad, "%s:face(0)" % pad]])
    cmd("feature.fillet", name="Pad", radius="3 mm", edges=[["%s:face(2)" % pad, "%s:face(0)" % pad]])
    cmd("feature.cylinder", name="Stud", radius="studD / 2", height="studL + 2 mm",
        position=["legX / 2", "legY / 2", "padH - 2 mm"])
    nut = Sketch("NutOutline", "xy", offset="padH + studL - nutM")
    nut.poly([("legX / 2 + nutS / sqrt(3) * cos(%d deg)" % a, "legY / 2 + nutS / sqrt(3) * sin(%d deg)" % a)
              for a in range(0, 360, 60)])
    cmd("feature.extrude", sketch="NutOutline", distance="nutM", name="Nut")
    cmd("feature.boolean", op="union", target="Pad", tool="Stud", name="PadStud")
    cmd("feature.boolean", op="union", target="PadStud", tool="Nut", name="Foot1")
    for n in ("PlateBlock", "Plate1", "PadDisc", "PadChamfer", "Pad", "Stud", "Nut", "PadStud", "Foot1"):
        when(n, "feet")

    # The other three corners and sides, mirrored.
    def mirror(src, name, axis, cond=None):
        if axis == "x":
            cmd("feature.mirror", source=src, normal=[1, 0, 0], point=["L / 2", "0 mm", "0 mm"], keep=True, name=name)
        else:
            cmd("feature.mirror", source=src, normal=[0, 1, 0], point=["0 mm", "W / 2", "0 mm"], keep=True, name=name)
        if cond:
            when(name, cond)

    mirror("Leg1", "Leg2", "x")
    mirror("Leg1", "Leg4", "y")
    mirror("Leg2", "Leg3", "y")
    mirror("TopFront", "TopBack", "y")
    mirror("TopLeft", "TopRight", "x")
    mirror("CrossFront", "CrossBack", "y", "cross")
    mirror("CrossLeft", "CrossRight", "x", "cross")
    mirror("Plate1", "Plate2", "x", "feet")
    mirror("Plate1", "Plate4", "y", "feet")
    mirror("Plate2", "Plate3", "y", "feet")
    mirror("Foot1", "Foot2", "x", "feet")
    mirror("Foot1", "Foot4", "y", "feet")
    mirror("Foot2", "Foot3", "y", "feet")

    for b in ("Leg1", "TopFront", "TopLeft", "CrossFront", "CrossLeft", "Plate1"):
        cmd("body.appearance", body=b, **STEEL)
        cmd("body.material", body=b, name="S235 steel", density=7850)
    cmd("body.appearance", body="Foot1", **PAD)

    # The cut list as named sets, each checked by an assertion.
    def cut(set_name, bodies, qty, axis=None, length=None):
        cmd("set.define", name=set_name, kind="body", where={"any": [{"name": b} for b in bodies]})
        of = {"kind": "body", "where": {"set": set_name}}
        cmd("assert.add", name=set_name + ": quantity", measure="count", of=of, eq=qty)
        if axis:
            cmd("assert.add", name=set_name + ": cut length", measure="extent", of=of, axis=axis, eq=length)

    cut("Legs", ["Leg1", "Leg2", "Leg3", "Leg4"], "legQty", "z", "legLen")
    cut("Top rails, long", ["TopFront", "TopBack"], "2", "x", "topLongLen")
    cut("Top rails, short", ["TopLeft", "TopRight"], "2", "y", "topShortLen")
    cut("Cross rails, long", ["CrossFront", "CrossBack"], "if(cross, 2, 0)")
    cut("Cross rails, short", ["CrossLeft", "CrossRight"], "if(cross, 2, 0)")
    cut("End plates", ["Plate1", "Plate2", "Plate3", "Plate4"], "plateQty")
    cut("Levelling feet", ["Foot1", "Foot2", "Foot3", "Foot4"], "plateQty")
    cmd("set.define", name="Steel", kind="body",
        where={"any": [{"set": n} for n in ("Legs", "Top rails, long", "Top rails, short", "Cross rails, long",
                                             "Cross rails, short", "End plates")]})
    cmd("assert.add", name="Steel weight (kg)", measure="mass", of={"kind": "body", "where": {"set": "Steel"}}, min="0")

    pub = [
        ("L", dict(label="Length", description="Outside length of the frame", group="Size", order=1,
                   min="400 mm", max="2400 mm", step="10 mm", unit="mm")),
        ("W", dict(label="Width", description="Outside width of the frame", group="Size", order=2,
                   min="300 mm", max="1200 mm", step="10 mm", unit="mm")),
        ("H", dict(label="Height", description="From the floor to the top of the frame, feet included",
                   group="Size", order=3, min="400 mm", max="1100 mm", step="5 mm", unit="mm")),
        ("profile", dict(label="Profile", description="Square (SHS) or rectangular (RHS) tube, or equal angle (L): "
                         "height x width x wall in mm. A rectangular tube stands on edge",
                         group="Profile", order=1, kind="choice", choicesFrom="profiles")),
        ("mitre", dict(label="Mitred top corners", description="Mitre the top frame at 45 deg and set it on the legs; "
                       "off: the top rails butt between the legs (an angle frame is always mitred)",
                       group="Profile", order=2, kind="boolean")),
        ("cross", dict(label="Cross rails", description="A ring of rails between the legs near the floor, for a shelf",
                       group="Cross rails", order=1, kind="boolean")),
        ("crossH", dict(label="Cross rail height", description="From the floor to the underside of the cross rails",
                        group="Cross rails", order=2, min="100 mm", max="H - 2 * h - 100 mm", step="5 mm", unit="mm")),
        ("feet", dict(label="Levelling feet", description="An end plate welded under each leg with an M10 or M12 "
                      "levelling foot; the legs are shorter by the feet",
                      group="Feet", order=1, kind="boolean")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        cmd("variable.publish", **p)
    cmd("document.info",
        title="Welded table frame",
        description="A welded steel table frame of square or rectangular tube or angle iron: set the length, width and "
                    "height, pick the profile from a table of common sizes, mitred or butt top corners, a ring of cross "
                    "rails and levelling feet. Every piece is a body of its own; the named sets Legs, Top rails, Cross "
                    "rails, End plates and Levelling feet are the cut list, and the assertions (assert.list) give each "
                    "piece's quantity and cut length. Variables topMitre and crossMitre are the mitre angles. Export "
                    "STEP for CAD or STL to look at it.",
        author="Johan Coppens", licence="CC-BY-4.0",
        url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/welded-table-frame",
        tags=["table", "frame", "welding", "steel", "tube", "cut list"])
    cmd("jig.export", path="dist/welded-table-frame.3dcraftjig")
    return steps


if __name__ == "__main__":
    main()
    print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
