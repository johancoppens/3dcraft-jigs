#!/usr/bin/env python3
"""Writes build.json for the pillow block Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the bearing table and the profile are readable.

Coordinates: the shaft axis is the world y axis, the housing symmetric about
x = 0 and y = 0, the base underneath at z = -Hc. The bearing is pressed in
from the +y side against a shoulder.
"""
import json

# Deep-groove ball bearings, ISO 15 boundary dimensions: d bore, D outside
# diameter, B width (mm). The table's key is the designation with its size
# ("6202  15x35x11"), so the form shows the size and a key is never a number.
BEARINGS = [
    ("608", 8, 22, 7),
    ("6000", 10, 26, 8),
    ("6001", 12, 28, 8),
    ("6002", 15, 32, 9),
    ("6003", 17, 35, 10),
    ("6004", 20, 42, 12),
    ("6005", 25, 47, 12),
    ("6200", 10, 30, 9),
    ("6201", 12, 32, 10),
    ("6202", 15, 35, 11),
    ("6203", 17, 40, 12),
    ("6204", 20, 47, 14),
    ("6205", 25, 52, 15),
]
DEFAULT_BEARING = 10  # 6202
# Socket head cap screws for the base: clearance hole (ISO 273, medium) and
# head diameter dk (ISO 4762).
BOLTS = [
    ("M4", 4.5, 7),
    ("M5", 5.5, 8.5),
    ("M6", 6.6, 10),
    ("M8", 9, 13),
]

HOUSING = {"color": "#8FA98A", "roughness": 0.6}            # sage
BEARING = {"color": "#B9BEC4", "metallic": 0.9, "roughness": 0.25}
SEAL = {"color": "#5B7299", "roughness": 0.7}               # slate blue
BRASS = {"color": "#B8954A", "metallic": 0.9, "roughness": 0.35}

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
        return [self.line(ids[i], ids[(i + 1) % len(ids)]) for i in range(len(ids))]


def main():
    cmd("table.set", name="bearings",
        columns=["bearing", {"name": "d", "unit": "mm"}, {"name": "D", "unit": "mm"}, {"name": "B", "unit": "mm"}],
        rows=[["%s  %gx%gx%g" % (n, d, D, B), d, D, B] for n, d, D, B in BEARINGS])
    cmd("table.set", name="bolts",
        columns=["bolt", {"name": "hole", "unit": "mm"}, {"name": "dk", "unit": "mm"}],
        rows=[list(r) for r in BOLTS])
    # Inputs.
    var("bearing", str(DEFAULT_BEARING))
    var("Hc", "40 mm")
    var("fit", "0 mm")
    var("slots", "1")
    var("slotLen", "8 mm")
    var("grease", "1")
    # The bearing.
    var("d", "bearings[bearing].d")
    var("D", "bearings[bearing].D")
    var("B", "bearings[bearing].B")
    # The housing, in proportion to the bearing.
    var("wall", "clamp(0.2 * D, 3 mm, 8 mm)")          # ring wall round the bearing
    var("R", "D / 2 + wall")                           # outside radius of the ring
    var("tb", "clamp(0.3 * D, 5 mm, 12 mm)")           # base thickness
    var("rf", "clamp(0.12 * D, 2 mm, 5 mm)")           # fillet between pedestal and base
    var("bolt", "if(D <= 26 mm, 1, if(D <= 35 mm, 2, if(D <= 47 mm, 3, 4)))")
    var("boltHole", "bolts[bolt].hole")
    var("head", "bolts[bolt].dk")
    var("Wh", "max(B + max(2 mm, 0.25 * B), head + 6 mm)")   # housing and base width, along the shaft
    var("y0", "Wh / 2 - B")                            # the seat runs from y0 to the +y face
    var("ys", "Wh / 2 - B / 2")                        # middle of the seat
    var("Ds", "D - max(2 mm, 0.08 * D)")               # shoulder bore: bears on the outer ring only
    var("slotRun", "if(slots, slotLen, 0 mm)")
    var("xb", "R + rf + head / 2 + 1 mm + slotRun / 2")    # bolt centres
    var("Lb", "2 * (xb + slotRun / 2 + head / 2 + 2.5 mm)")  # base length
    var("rc", "min(4 mm, Wh / 4)")                     # plan radius of the base's corners
    var("zb", "-Hc")                                   # underside of the base

    # The housing's profile on the zx plane (sketch x = world z, sketch y =
    # world x): base, pedestal with flared fillets, and the ring's top half.
    s = Sketch("HousingProfile", "zx")
    P = lambda x, z: s.pt(z, x)  # noqa: E731  (world x, z) to (sketch x, sketch y)
    a = P("-Lb / 2", "zb")
    b = P("Lb / 2", "zb")
    c = P("Lb / 2", "zb + tb")
    d1 = P("R + rf", "zb + tb")
    cr = P("R + rf", "zb + tb + rf")
    d2 = P("R", "zb + tb + rf")
    e = P("R", "0 mm")
    o = P("0 mm", "0 mm")
    f = P("-R", "0 mm")
    g2 = P("-R", "zb + tb + rf")
    cl = P("-R - rf", "zb + tb + rf")
    g1 = P("-R - rf", "zb + tb")
    h = P("-Lb / 2", "zb + tb")
    bottom = s.line(a, b)
    right_end = s.line(b, c)
    s.line(c, d1)
    # In sketch axes (z, x) the arcs run the other way round: each is given
    # counter-clockwise in the sketch.
    s.arc(cr, d1, d2)
    s.line(d2, e)
    s.arc(o, f, e)
    s.line(f, g2)
    s.arc(cl, g2, g1)
    s.line(g1, h)
    left_end = s.line(h, a)
    housing = cmd("feature.extrude", sketch="HousingProfile", distance="Wh", symmetric=True, name="HousingBlank")
    curves = ",".join("e%d" % i for i in range(int(bottom[1:]), s.n + 1))
    caps = ["%s:startCap(%s)" % (housing, curves), "%s:endCap(%s)" % (housing, curves)]
    cmd("feature.fillet", name="BaseCorners", radius="rc", edges=[
        ["%s:side(%s)" % (housing, end), cap] for end in (right_end, left_end) for cap in caps])

    # Grease nipple boss on top of the ring, over the middle of the seat.
    var("rBoss", "min(5.5 mm, B / 2 - 0.5 mm)")
    var("bossTop", "R + 2.5 mm")
    cmd("feature.cylinder", name="Boss", radius="rBoss", height="bossTop - D / 2 - 1 mm",
        position=["0 mm", "ys", "D / 2 + 1 mm"])
    when("Boss", "grease")
    cmd("feature.boolean", op="union", target="BaseCorners", tool="Boss", name="WithBoss")

    # Bearing seat (D + fit, B deep from the +y face), shoulder bore through,
    # the lubrication hole down from the boss.
    seat = cmd("feature.cylinder", name="Seat", radius="(D + fit) / 2", height="B + 1 mm",
        position=["0 mm", "y0", "0 mm"], axis=[0, 1, 0])
    shoulder = cmd("feature.cylinder", name="ShoulderBore", radius="Ds / 2", height="Wh + 2 mm",
        position=["0 mm", "-Wh / 2 - 1 mm", "0 mm"], axis=[0, 1, 0])
    cmd("feature.boolean", op="union", target="Seat", tool="ShoulderBore", name="Bore")
    bored = cmd("feature.boolean", op="subtract", target="WithBoss", tool="Bore", name="Bored")
    cmd("feature.cylinder", name="LubeHole", radius="1.25 mm", height="bossTop - D / 4 + 1 mm",
        position=["0 mm", "ys", "D / 4"])
    when("LubeHole", "grease")
    cmd("feature.boolean", op="subtract", target="Bored", tool="LubeHole", name="Lubed")

    # Mounting: two slots (or round holes) through the base.
    sl = Sketch("Slots", "xy", offset="zb - 1 mm")
    for sign in ("", "-"):
        cx = "%sxb" % sign
        p1 = sl.pt("%s - slotLen / 2" % cx, "-boltHole / 2")
        p2 = sl.pt("%s + slotLen / 2" % cx, "-boltHole / 2")
        c2 = sl.pt("%s + slotLen / 2" % cx, "0 mm")
        p3 = sl.pt("%s + slotLen / 2" % cx, "boltHole / 2")
        p4 = sl.pt("%s - slotLen / 2" % cx, "boltHole / 2")
        c1 = sl.pt("%s - slotLen / 2" % cx, "0 mm")
        sl.line(p1, p2)
        sl.arc(c2, p2, p3)
        sl.line(p3, p4)
        sl.arc(c1, p4, p1)
    when("Slots", "slots")
    cmd("feature.extrude", sketch="Slots", distance="tb + 2 mm", name="SlotTool")
    when("SlotTool", "slots")
    cmd("feature.cylinder", name="BoltHole", radius="boltHole / 2", height="tb + 2 mm",
        position=["-xb", "0 mm", "zb - 1 mm"])
    cmd("feature.pattern", name="BoltHoles", source="BoltHole", count="2", step=["2 * xb", "0 mm", "0 mm"])
    for n in ("BoltHole", "BoltHoles"):
        when(n, "!slots")
    cmd("feature.boolean", op="subtract", target="Lubed", tool="SlotTool", name="Slotted")
    cmd("feature.boolean", op="subtract", target="Slotted", tool="BoltHoles", name="Mounted")
    # A 0.5 mm lead-in at the seat's mouth and at the back of the bore.
    cmd("feature.chamfer", name="Housing", distance="0.5 mm",
        edges=[[caps[1], "%s:copy(1)/%s:face(0)" % (bored, seat)],
               [caps[0], "%s:copy(1,1)/%s:face(0)" % (bored, shoulder)]])
    cmd("body.appearance", body="Housing", **HOUSING)

    # The bearing: a revolved section with its seals, in the seat.
    var("ci", "0.3 mm")                                 # edge chamfer
    var("r1", "d / 2 + 0.3 * (D - d) / 2")              # inner ring's land
    var("r2", "D / 2 - 0.25 * (D - d) / 2")             # outer ring's land
    var("rec", "0.3 mm")                                # seals sit back this far
    br = Sketch("BearingSection", "xy")
    seal_lines = br.poly([("d / 2 + ci", "y0"), ("r1", "y0"), ("r1", "y0 + rec"), ("r2", "y0 + rec"), ("r2", "y0"),
             ("D / 2 - ci", "y0"), ("D / 2", "y0 + ci"), ("D / 2", "y0 + B - ci"), ("D / 2 - ci", "y0 + B"),
             ("r2", "y0 + B"), ("r2", "y0 + B - rec"), ("r1", "y0 + B - rec"), ("r1", "y0 + B"),
             ("d / 2 + ci", "y0 + B"), ("d / 2", "y0 + B - ci"), ("d / 2", "y0 + ci")])
    bearing = cmd("feature.revolve", sketch="BearingSection", axis="y", name="Bearing")
    cmd("body.appearance", body="Bearing", **BEARING)
    # The seals: the recessed faces between the rings (2RS).
    cmd("face.appearance", body="Bearing", faces=["%s:side(%s)" % (bearing, seal_lines[2]),
                                                  "%s:side(%s)" % (bearing, seal_lines[10])], **SEAL)

    # The grease nipple (DIN 71412 form A, straight; sizes approximate):
    # hexagon 7 mm across flats, a neck and a ball head.
    nip = Sketch("NippleHex", "xy", offset="bossTop")
    nip.poly([("3.5 mm / cos(30 deg) * cos(%d deg)" % a_, "ys + 3.5 mm / cos(30 deg) * sin(%d deg)" % a_)
              for a_ in range(30, 390, 60)])
    when("NippleHex", "grease")
    cmd("feature.extrude", sketch="NippleHex", distance="4 mm", name="NippleNut")
    cmd("feature.cylinder", name="NippleNeck", radius="2 mm", height="5 mm", position=["0 mm", "ys", "bossTop + 3.5 mm"])
    cmd("feature.sphere", name="NippleBall", radius="3.25 mm", position=["0 mm", "ys", "bossTop + 9 mm"])
    cmd("feature.boolean", op="union", target="NippleNut", tool="NippleNeck", name="NippleA")
    cmd("feature.boolean", op="union", target="NippleA", tool="NippleBall", name="GreaseNipple")
    for n in ("NippleNut", "NippleNeck", "NippleBall", "NippleA", "GreaseNipple"):
        when(n, "grease")
    cmd("body.appearance", body="GreaseNipple", **BRASS)

    # interference holds when the bodies do not overlap (touching is fine).
    cmd("assert.add", name="Bearing does not overlap the housing", measure="interference", of="Bearing",
        to="Housing")
    cmd("assert.add", name="Bodies: housing, bearing, nipple", measure="count", of={"kind": "body"},
        eq="if(grease, 3, 2)")

    pub = [
        ("bearing", dict(label="Bearing", description="Deep-groove ball bearing (ISO 15): bore x outside diameter x "
                         "width, 608 = 8 x 22 x 7 mm, 6202 = 15 x 35 x 11 mm", group="Bearing", order=1,
                         kind="choice", choicesFrom="bearings")),
        ("fit", dict(label="Seat allowance", description="Added to the seat's diameter: 0 for a machined seat "
                     "(ream it to fit), 0.1 to 0.2 mm for a 3D print", group="Bearing", order=2,
                     min="0 mm", max="0.3 mm", step="0.01 mm", unit="mm")),
        ("Hc", dict(label="Centre height", description="From the underside of the base to the shaft's axis",
                    group="Housing", order=1, min="max(R, D / 2 + tb) + 1 mm", max="max(R, D / 2 + tb) + 40 mm",
                    step="0.5 mm", unit="mm")),
        ("slots", dict(label="Slots", description="Slotted mounting holes, to line the shaft up; off: round holes",
                       group="Mounting", order=1, kind="boolean")),
        ("slotLen", dict(label="Slot length", description="How far each slot lets the block move",
                         group="Mounting", order=2, min="4 mm", max="20 mm", step="1 mm", unit="mm")),
        ("grease", dict(label="Grease nipple", description="A boss on top with a lubrication hole into the seat "
                        "and a straight grease nipple (for an open or shielded bearing)",
                        group="Mounting", order=3, kind="boolean")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        cmd("variable.publish", **p)
    cmd("document.info",
        title="Pillow block bearing housing",
        description="A pillow block (plummer block) for a deep-groove ball bearing chosen from a table of real "
                    "sizes (608, 6000 to 6005, 6200 to 6205): the housing, its wall, base and mounting bolts (M4 to "
                    "M8) follow the bearing. Set the centre height, the seat allowance for printing, slotted or round "
                    "mounting holes and an optional grease nipple boss. The bearing is pressed in from the front "
                    "against a shoulder that bears on its outer ring only. Export STL or 3MF to print, STEP for CAD "
                    "(the bearing and nipple are separate bodies: leave them out with the bodies option).",
        author="Johan Coppens", licence="CC-BY-4.0",
        url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/pillow-block",
        tags=["bearing", "pillow block", "housing", "shaft", "3D printing", "machining"])
    cmd("jig.export", path="dist/pillow-block.3dcraftjig")
    return steps


if __name__ == "__main__":
    main()
    print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
