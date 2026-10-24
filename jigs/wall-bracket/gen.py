#!/usr/bin/env python3
"""Writes build.json for the wall bracket Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the sizing formulas and the material table are readable.

Coordinates: the wall is the plane x = 0, the arm runs along +x, z is up,
the bracket is symmetric about y = 0. The profile is drawn on the zx plane
(sketch x = world z, sketch y = world x) and extruded symmetrically along y.
"""
import json

# name, fy: yield (0.2 % proof) strength in MPa, sf: safety factor,
# tMin, tMax: thinnest and thickest plate in mm, kind: 1 steel, 2 stainless,
# 3 aluminium, 4 printed PLA, 5 printed PETG.
MATERIALS = [
    ("Steel S235", 235, 2, 3, 6, 1),
    ("Stainless 1.4301", 210, 2, 2, 5, 2),
    ("Aluminium 6060-T66", 150, 2, 3, 8, 3),
    ("Aluminium 6082-T6", 240, 2, 3, 8, 3),
    ("PLA, 3D printed", 50, 4, 4, 10, 4),
    ("PETG, 3D printed", 45, 4, 4, 10, 5),
]
DEFAULT_MATERIAL = 5
# Countersunk wood or chipboard screws: name, d: hole (clearance), dk: head,
# pull: the tension in N one screw is allowed to take in its wall plug (an
# assumption on the safe side for nylon plugs in solid brick or concrete;
# check your plugs' data).
SCREWS = [
    ("4 mm", 4.5, 8, 200),
    ("5 mm", 5.5, 10, 300),
    ("6 mm", 6.6, 12, 400),
]
COLOURS = {
    1: {"color": "#7D858C", "metallic": 0.85, "roughness": 0.45},   # steel
    2: {"color": "#B9BEC4", "metallic": 0.9, "roughness": 0.3},     # stainless
    3: {"color": "#B9BEC4", "metallic": 0.85, "roughness": 0.45},   # aluminium
    4: {"color": "#C2694B", "roughness": 0.6},                      # PLA, terracotta
    5: {"color": "#2E7D7A", "roughness": 0.5},                      # PETG, petrol
}

steps = []
fid = [0]


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
    def __init__(self, name, plane, offset=None):
        p = {"name": name, "plane": plane}
        if offset is not None:
            p["offset"] = offset
        self.id = cmd("sketch.create", **p)
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
        lines = [self.line(ids[i], ids[(i + 1) % len(ids)]) for i in range(len(ids))]
        return ids, lines


def main():
    cmd("table.set", name="materials",
        columns=["material", "fy", "sf", {"name": "tMin", "unit": "mm"}, {"name": "tMax", "unit": "mm"}, "kind"],
        rows=[list(r) for r in MATERIALS])
    cmd("table.set", name="screws",
        columns=["screw", {"name": "d", "unit": "mm"}, {"name": "dk", "unit": "mm"}, "pull"],
        rows=[list(r) for r in SCREWS])
    # Inputs.
    var("load", "20")
    var("arm", "200 mm")
    var("material", str(DEFAULT_MATERIAL))
    var("screw", "2")
    var("shelfHoles", "1")

    # Sizing (see README). The load hangs on the arm as a shelf spreads it:
    # its resultant at the middle of the arm. The section at the wall is
    # taken as the plate thickness t by the depth D (arm plate and gusset
    # together), a rectangle: section modulus t D^2 / 6.
    var("fy", "materials[material].fy")                  # MPa = N/mm^2
    var("sf", "materials[material].sf")
    var("kind", "materials[material].kind")
    var("tMin", "materials[material].tMin")
    var("tMax", "materials[material].tMax")
    var("lever", "arm / 2")
    var("M", "load * 9.81 * lever / (1 mm)")              # bending moment at the wall, N mm
    var("Zreq", "sf * M / fy")                            # section modulus needed, mm^3 (plain)
    var("k", "15")                                         # the gusset at most 15 times as deep as thick
    var("tIdeal", "pow(6 * Zreq / k^2, 1 / 3) * 1 mm")    # D = k t and t D^2 / 6 = Zreq
    var("tArm", "6 * Zreq / (arm / 1 mm)^2 * 1 mm")      # thinnest plate whose gusset fits under the arm
    var("t", "clamp(ceil(max(tIdeal, tArm), 0.5 mm), tMin, tMax)")
    var("Dmin", "max(0.3 * arm, 3 * t + 15 mm)")
    var("Dmax", "min(k * t, arm)")
    var("Dreq", "sqrt(6 * Zreq / (t / 1 mm)) * 1 mm")     # depth this thickness needs
    var("D", "clamp(ceil(Dreq, 0.5 mm), Dmin, max(Dmin, Dmax))")
    var("sigma", "6 * M / ((t / 1 mm) * (D / 1 mm)^2)")   # bending stress at the wall, MPa
    var("utilisation", "sigma * sf / fy")                 # at most 1
    # The most this material and arm can take: tMax, its deepest gusset.

    # Geometry.
    var("ri", "t")                                        # inside bend radius
    var("hole", "screws[screw].d")
    var("head", "min(screws[screw].dk, hole + 2 * (t - 0.8 mm))")  # countersink, leaving 0.8 mm of bore
    var("pitch", "screws[screw].dk / 2 + 5 mm")
    var("tail", "2 * pitch")                              # below the gusset: one screw on the centre line
    var("top", "D + tail")                                # back plate height
    var("b", "max(clamp(0.2 * arm, 30 mm, 60 mm), t + 2 * screws[screw].dk + 6 mm)")
    var("cope", "t / 2 + 2 mm")
    var("gLen", "0.88 * arm - t")
    var("tip", "min(4 mm, t)")
    var("rc", "min(b / 3, 10 mm)")                        # plan radius of the arm tip and the tail
    var("yh", "(b / 2 + t / 2) / 2")                      # screws beside the gusset
    var("zUp", "top - t - ri - screws[screw].dk / 2 - 4 mm")  # the two upper wall screws
    # The bracket tips about the foot of its back plate: the two upper screws
    # take the moment in tension (shown, not checked: see your wall plugs).
    var("pull", "screws[screw].pull")
    var("screwPull", "M / (zUp / 1 mm) / 2")              # N per upper screw, at most pull
    var("zUpReq", "M / (2 * pull) * 1 mm")                # how high the upper screws must sit
    # The most this bracket can take, without depending on the load: in
    # bending with the thickest plate and its deepest gusset; in the screws
    # with the upper screws as low as they can come (the shallowest gusset
    # with the thickest plate).
    var("Dcap", "min(k * tMax, arm)")
    var("bendCap", "fy * (tMax / 1 mm) * (Dcap / 1 mm)^2 / (6 * sf * 9.81 * lever / (1 mm))")
    var("zLow", "max(0.3 * arm, 3 * tMax + 15 mm) + tail - 2 * tMax - screws[screw].dk / 2 - 4 mm")
    var("screwCap", "2 * pull * (zLow / 1 mm) / (9.81 * lever / (1 mm))")
    var("maxLoad", "min(150, floor(min(bendCap, screwCap)))")

    # The bent plate: back plate and arm with an inside bend radius t.
    s = Sketch("Plate", "zx")
    p = [s.pt("0 mm", "0 mm"), s.pt("0 mm", "t"), s.pt("top - t - ri", "t")]
    c = s.pt("top - t - ri", "t + ri")
    p4 = s.pt("top - t", "t + ri")
    p5 = s.pt("top - t", "arm")
    p6 = s.pt("top", "arm")
    p7 = s.pt("top", "t + ri")
    p8 = s.pt("top - t - ri", "0 mm")
    tail_line = s.line(p[0], p[1])
    s.line(p[1], p[2])
    s.arc(c, p[2], p4)
    s.line(p4, p5)
    tip_line = s.line(p5, p6)
    s.line(p6, p7)
    s.arc(c, p8, p7)
    s.line(p8, p[0])
    plate = cmd("feature.extrude", sketch="Plate", distance="b", symmetric=True, name="BentPlate")
    curves = ",".join("e%d" % i for i in range(int(tail_line[1:]), s.n + 1))
    start_cap = "%s:startCap(%s)" % (plate, curves)
    end_cap = "%s:endCap(%s)" % (plate, curves)
    cmd("feature.fillet", name="PlateCorners", radius="rc", edges=[
        ["%s:side(%s)" % (plate, tip_line), start_cap],
        ["%s:side(%s)" % (plate, tip_line), end_cap],
        ["%s:side(%s)" % (plate, tail_line), start_cap],
        ["%s:side(%s)" % (plate, tail_line), end_cap]])

    # The gusset under the arm, coped clear of the bend.
    g = Sketch("GussetOutline", "zx")
    g.poly([("top - t - ri - cope", "t"), ("top - t", "t + ri + cope"), ("top - t", "t + gLen"),
            ("top - t - tip", "t + gLen"), ("top - D", "t + tip"), ("top - D", "t")])
    cmd("feature.extrude", sketch="GussetOutline", distance="t", symmetric=True, name="Gusset")
    cmd("feature.boolean", op="union", target="PlateCorners", tool="Gusset", name="Welded")

    # Countersunk wall screws: two high up beside the gusset, where the
    # bracket pulls, and one in the tail; two holes in the arm for screws
    # into the shelf from below.
    def wall_screw(name, y, z):
        cmd("feature.cylinder", name=name + "Bore", radius="hole / 2", height="t + 2 mm",
            position=["-1 mm", y, z], axis=[1, 0, 0])
        cmd("feature.cone", name=name + "Sink", radius="head / 2 + 1 mm", height="head / 2 + 1 mm",
            position=["t + 1 mm", y, z], axis=[-1, 0, 0])
        cmd("feature.boolean", op="union", target=name + "Bore", tool=name + "Sink", name=name)

    wall_screw("WallScrewL", "-yh", "zUp")
    wall_screw("WallScrewR", "yh", "zUp")
    wall_screw("WallScrewLow", "0 mm", "pitch")
    cmd("feature.boolean", op="union", target="WallScrewL", tool="WallScrewR", name="WallScrewsUp")
    cmd("feature.boolean", op="union", target="WallScrewsUp", tool="WallScrewLow", name="WallScrews")
    cmd("feature.boolean", op="subtract", target="Welded", tool="WallScrews", name="WallDrilled")
    cmd("feature.cylinder", name="ShelfHole", radius="hole / 2", height="t + 2 mm",
        position=["0.6 * arm", "-yh", "top - t - 1 mm"])
    cmd("feature.pattern", name="ShelfHoles", source="ShelfHole", count="2", step=["0 mm", "2 * yh", "0 mm"])
    for n in ("ShelfHole", "ShelfHoles"):
        when(n, "shelfHoles")
    cmd("feature.boolean", op="subtract", target="WallDrilled", tool="ShelfHoles", name="Drilled")

    # Turned so the thumbnail looks at its front. (Its colour cannot follow
    # the material: an inactive feature still colours the body it passes on.)
    cmd("feature.transform", source="Drilled", angle="90 deg", axis=[0, 0, 1], name="Bracket")
    cmd("body.appearance", body="Bracket", **COLOURS[4])

    # The checks: the bracket's height, measured on the model, against what
    # the load needs in bending (the gusset) and in the upper screws' pull.
    cmd("assert.add", name="Gusset deep enough for the load", measure="extent", of="Bracket", axis="z",
        min="Dreq + tail")
    cmd("assert.add", name="Upper screws high enough for the load", measure="extent", of="Bracket", axis="z",
        min="zUpReq + 2 * t + screws[screw].dk / 2 + 4 mm")
    cmd("assert.add", name="one body", measure="count", of={"kind": "body"}, eq="1")

    pub = [
        ("load", dict(label="Load per bracket", description="In kg, spread over the arm as a shelf spreads it. "
                      "The most it allows (maxLoad) follows from the material, the arm and the screws",
                      group="Load", order=1, kind="integer", min="1", max="maxLoad")),
        ("arm", dict(label="Arm length", description="How far the bracket reaches from the wall (the shelf's depth)",
                     group="Load", order=2, min="100 mm", max="400 mm", step="5 mm", unit="mm")),
        ("material", dict(label="Material", description="Yield strength and safety factor from the table: 2 for metals, "
                          "4 for 3D prints (layers, creep)", group="Material", order=1, kind="choice",
                          choicesFrom="materials")),
        ("screw", dict(label="Screws", description="Countersunk wood or chipboard screws with wall plugs; "
                       "3 in the wall, 2 into the shelf", group="Screws", order=1, kind="choice", choicesFrom="screws")),
        ("shelfHoles", dict(label="Shelf screw holes", description="Two holes in the arm to screw the shelf on from below",
                            group="Screws", order=2, kind="boolean")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        cmd("variable.publish", **p)
    cmd("document.info",
        title="Wall bracket sized by its load",
        description="A shelf or console bracket whose plate thickness and gusset depth are worked out from the load: "
                    "set the load per bracket in kg, the arm length, the material (steel, stainless, aluminium or a 3D "
                    "print) and the screws. The bending moment at the wall sets the section (t x D^2 / 6 against the "
                    "material's yield strength and safety factor); the upper screws are placed high enough for their "
                    "pull. The load's range stops at what the material, the arm and the screws can carry, and two "
                    "assertions check the built bracket against the load. Read t, D, sigma and utilisation in the "
                    "variables. Export STL or 3MF to print, STEP for a metal shop.",
        author="Johan Coppens", licence="CC-BY-4.0",
        url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/wall-bracket",
        tags=["bracket", "shelf", "wall", "formula", "3D printing", "sheet metal"])
    cmd("jig.export", path="dist/wall-bracket.3dcraftjig")
    return steps


if __name__ == "__main__":
    main()
    print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
