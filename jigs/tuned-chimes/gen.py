#!/usr/bin/env python3
"""Writes build.json for the tuned chimes Jig (python3 -I gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the tables, the physics and the per-note features are readable.

A wind chime of tubes hanging from a disc, or a glockenspiel of bars on a
frame, every tube or bar cut to the length of its note by the free-free
Euler-Bernoulli beam: f = (22.373 / (2 pi L^2)) sqrt(E I / (rho A)).

Coordinates: z up. Chime: the disc's underside at z = 0, the tubes on a circle
of radius Rc round the z axis, their middles level at z = zc (the striker 18 mm below
them). Glockenspiel: the bars side by side along x, each along y and
centred on y = 0, on a frame standing on z = 0.
"""
import json
import math

NMAX = 12          # most notes a Jig can have (features are built for each)
BETA = 22.373      # (beta1 L)^2 of a free-free beam's first mode (4.7300^2)
NODE = 0.2242      # the first mode's nodes, as a fraction of the length from each end

# Scales: name, notes per octave, semitones above the lowest note (padded).
SCALES = [
    ("Major pentatonic", [0, 2, 4, 7, 9]),
    ("Minor pentatonic", [0, 3, 5, 7, 10]),
    ("Major", [0, 2, 4, 5, 7, 9, 11]),
    ("Natural minor", [0, 2, 3, 5, 7, 8, 10]),
    ("Major triad", [0, 4, 7]),
    ("Major 7 chord", [0, 4, 7, 11]),
    ("Minor 7 chord", [0, 3, 7, 10]),
    ("Dominant 7 chord", [0, 4, 7, 10]),
    ("Westminster", [0, 5, 7, 9]),
]
SPAN_MAX = 24      # at most two octaves: the shortest note at least half the longest


def span(steps, n):
    k = n - 1
    return steps[k % len(steps)] + 12 * (k // len(steps))


def max_notes(steps):
    n = 3
    while n < NMAX and span(steps, n + 1) <= SPAN_MAX:
        n += 1
    return n


NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]

# Tube materials: E (GPa), density (kg/m^3), shear modulus G (GPa).
TUBE_MATERIALS = [
    ("Aluminium EN AW-6060 T6", 69.5, 2700, 26),
    ("Steel conduit (EMT)", 200, 7850, 79),
    ("Stainless steel 1.4301", 193, 7900, 77),
    ("Copper Cu-DHP (EN 1057)", 117, 8940, 44),
    ("Brass CuZn37", 110, 8440, 39),
]
# Bar materials: E along the bar (GPa), density (kg/m^3), G (GPa; wood about
# E / 14 along the grain). Wood E is the static modulus at 12 % moisture.
BAR_MATERIALS = [
    ("Aluminium flat bar EN AW-6060", 69.5, 2700, 26),
    ("Steel flat bar S235", 210, 7850, 81),
    ("Brass flat bar CuZn39Pb3", 97, 8470, 39),
    ("Padauk (African)", 11.72, 745, round(11.72 / 14, 3)),
    ("Honduran rosewood", 22.0, 1025, round(22.0 / 14, 3)),
    ("Hard maple", 12.62, 705, round(12.62 / 14, 3)),
]
# Tube sizes: outside diameter and wall (mm).
TUBE_SIZES = [
    ("12 x 1", 12, 1),
    ("15 x 1 copper", 15, 1),
    ("16 x 1.5", 16, 1.5),
    ("EMT 1/2 in (17.9 x 1.07)", 17.9, 1.07),
    ("20 x 1.5", 20, 1.5),
    ("22 x 1 copper", 22, 1),
    ("EMT 3/4 in (23.4 x 1.24)", 23.4, 1.24),
    ("25 x 1.5", 25, 1.5),
    ("25 x 2", 25, 2),
    ("28 x 1 copper", 28, 1),
    ("EMT 1 in (29.5 x 1.45)", 29.5, 1.45),
    ("30 x 2", 30, 2),
    ("32 x 1.5", 32, 1.5),
    ("35 x 2", 35, 2),
    ("40 x 2", 40, 2),
    ("50 x 2", 50, 2),
]
DEFAULT_SIZE = 8   # 25 x 1.5

ALU = {"color": "#B9BEC4", "metallic": 0.9, "roughness": 0.3}
WALNUT = {"color": "#7A5638", "roughness": 0.6}
PLY = {"color": "#D9B98A", "roughness": 0.8}
CORD = {"color": "#E8DFCC", "roughness": 0.9}
BRASS = {"color": "#B8954A", "metallic": 0.85, "roughness": 0.35}

steps = []


def cmd(c, **p):
    steps.append([c, p])


def var(name, expr):
    cmd("variable.set", name=name, expr=expr)


def when(feature, expr):
    cmd("feature.when", feature=feature, expr=expr)


def timo(leb):
    """The length whose Timoshenko pitch is the Euler-Bernoulli pitch of leb."""
    return "sqrt((sqrt(Ct^2 * rg^4 + 4 * (%s)^4) - Ct * rg^2) / 2)" % leb


def eb_of(l):
    """The Euler-Bernoulli length with the same pitch as a real length l."""
    return "sqrt(sqrt((%s)^4 + Ct * rg^2 * (%s)^2))" % (l, l)


def box(lo, hi):
    return [list(lo), list(hi)]


BIG = "100 m"


def main():
    cmd("table.set", name="scales",
        columns=["scale", "n"] + ["s%d" % i for i in range(1, 8)] + ["maxNotes"],
        rows=[[name, len(s)] + (s + [0] * 7)[:7] + [max_notes(s)] for name, s in SCALES])
    cmd("table.set", name="notes", columns=["note", "semi"], rows=[[n, i] for i, n in enumerate(NOTES)])
    cmd("table.set", name="tubeMaterials", columns=["material", "E", "rho", "G"], rows=[list(r) for r in TUBE_MATERIALS])
    cmd("table.set", name="barMaterials", columns=["material", "E", "rho", "G"], rows=[list(r) for r in BAR_MATERIALS])
    cmd("table.set", name="tubeSizes",
        columns=["size", {"name": "od", "unit": "mm"}, {"name": "wall", "unit": "mm"}],
        rows=[list(r) for r in TUBE_SIZES])

    # Inputs.
    var("instrument", "1")
    var("scale", "1")
    var("root", "1")
    var("octave", "5")
    var("N", "6")
    var("tubeMat", "1")
    var("tubeSize", str(DEFAULT_SIZE))
    var("strikeGap", "12 mm")
    var("barMat", "1")
    var("barW", "30 mm")
    var("barT", "6 mm")

    var("chime", "instrument == 1")
    var("bars", "instrument == 2")
    # The material and the section.
    var("E", "if(chime, tubeMaterials[tubeMat].E, barMaterials[barMat].E)")        # GPa
    var("rho", "if(chime, tubeMaterials[tubeMat].rho, barMaterials[barMat].rho)")  # kg/m^3
    var("c", "sqrt(E * 1e9 / rho)")                                                # m/s, sqrt(E / rho)
    var("OD", "tubeSizes[tubeSize].od")
    var("wall", "tubeSizes[tubeSize].wall")
    var("ID", "OD - 2 * wall")
    # Radius of gyration sqrt(I / A): a tube sqrt(OD^2 + ID^2) / 4, a bar
    # bending through its thickness t / sqrt(12).
    var("rg", "if(chime, sqrt(OD^2 + ID^2) / 4, barT / sqrt(12))")
    var("Kc", "c * rg / 1 m")                                                      # sqrt(E I / (rho A)), m^2/s
    # Timoshenko: shear and rotary inertia lower a short, fat piece's pitch.
    # (f_EB / f_T)^2 = 1 + Ct (rg / L)^2, Ct = 47.7 + 11.7 E / (kappa G),
    # kappa the shear coefficient (thin tube 0.53, rectangle 5/6).
    var("G", "if(chime, tubeMaterials[tubeMat].G, barMaterials[barMat].G)")
    var("kappa", "if(chime, 0.53, 5 / 6)")
    var("Ct", "47.7 + 11.7 * E / (kappa * G)")
    var("beta", str(BETA))
    var("nodeFrac", str(NODE))
    # The notes: equal temperament, A4 = 440 Hz.
    var("n", "scales[scale].n")
    # A range cannot look a table up (3DCraft 3faaaea0), so through a variable.
    var("maxNotes", "scales[scale].maxNotes")
    var("semi", "notes[root].semi")
    var("fRoot", "440 * pow(2, octave - 4 + (semi - 9) / 12)")
    ss = ", ".join("scales[scale].s%d" % i for i in range(1, 8))
    for k in range(1, NMAX + 1):
        var("s%d" % k, "choose(mod(%d, n) + 1, %s) + 12 * floor(%d / n)" % (k - 1, ss, k - 1))
        var("f%d" % k, "fRoot * pow(2, s%d / 12)" % k)
        # Free-free beam, first mode (Euler-Bernoulli):
        # LEB = sqrt(beta / (2 pi f) * sqrt(E I / (rho A))); with the Timoshenko
        # factor the length solves L^4 + Ct rg^2 L^2 = LEB^4, a quadratic in L^2.
        var("LEB%d" % k, "sqrt(beta / (2 * pi * f%d) * Kc) * 1 m" % k)
        var("L%d" % k, timo("LEB%d" % k))
    var("span", "choose(N, %s)" % ", ".join("s%d" % k for k in range(1, NMAX + 1)))
    var("Llong", "L1")
    var("Lshort", "choose(N, %s)" % ", ".join("L%d" % k for k in range(1, NMAX + 1)))
    # Lengths a note may have: long enough to drill and hang (and to behave
    # as a beam), short enough to handle.
    # L / rg >= 30 keeps the Timoshenko factor in its accurate range and the
    # first overtone near the slender beam's 2.76 times.
    var("Lfloor", "if(chime, max(100 mm, 5 * OD, 30 * rg), max(80 mm, 3 * barW, 30 * rg))")
    var("Lceil", "if(chime, 1500 mm, 700 mm)")
    var("LfloorEB", eb_of("Lfloor"))
    var("LceilEB", eb_of("Lceil"))
    # The octaves that keep every note between them (L ~ 1 / sqrt(f)).
    var("fTopMax", "beta / (2 * pi) * Kc / (LfloorEB / 1 m)^2")
    var("fBotMin", "beta / (2 * pi) * Kc / (LceilEB / 1 m)^2")
    var("octMax", "min(8, floor(4 + ln(fTopMax / 440) / ln(2) - (semi - 9) / 12 - span / 12))")
    var("octMin", "max(2, ceil(4 + ln(fBotMin / 440) / ln(2) - (semi - 9) / 12))")

    # ---- Wind chime ----
    var("holeD", "clamp(OD / 6, 3 mm, 6 mm)")           # the cord hole across the tube
    var("cordD", "clamp(holeD - 1.5 mm, 1.5 mm, 3 mm)")
    var("tubeGap", "max(OD / 2, 12 mm)")                 # least gap between neighbouring tubes
    var("strikerT", "12 mm")
    var("Rc", "max((OD + tubeGap) / (2 * sin(180 deg / N)), OD / 2 + strikeGap + 25 mm)")
    var("Rs", "Rc - OD / 2 - strikeGap")
    var("Rd", "Rc + OD / 2 + 15 mm")
    var("discT", "12 mm")
    var("hang", "40 mm")                                 # cord from the disc to the longest tube's top
    var("zc", "-hang - Llong / 2")                       # every tube's middle
    # The striker hits 12 to 24 mm below the middles: off the first
    # overtone's node at the middle (Hite's "dead zone").
    var("strikeDrop", "18 mm")
    var("zs", "zc - strikeDrop")
    var("sw", "clamp(1.2 * Rd, 80 mm, 250 mm)")
    var("sh", "1.3 * sw")
    var("sailT", "4 mm")
    var("sailTop", "zc - Llong / 2 - 40 mm")
    var("ringR", "15 mm")
    var("ringZ", "discT + 50 mm")

    # ---- Glockenspiel ----
    var("barHoleD", "clamp(barW / 5, 4 mm, 6 mm)")
    var("pinD", "barHoleD - 1.5 mm")                     # a pin in a rubber sleeve
    var("barGap", "max(6 mm, barW / 5)")
    var("pitch", "barW + barGap")
    var("frameT", "12 mm")
    var("feltT", "3 mm")
    var("barZ", "frameT + feltT")
    var("pinH", "barZ + barT + 4 mm")
    var("cw", "20 mm")                                   # the frame's end pieces
    var("xN", "(N - 1) * pitch")
    var("xa", "-barW / 2 - 6 mm - cw")
    var("xb", "xN + barW / 2 + 6 mm + cw")
    for k in range(1, NMAX + 1):
        var("x%d" % k, "%d * pitch" % (k - 1))
        var("nd%d" % k, "(0.5 - nodeFrac) * L%d" % k)   # a node's distance from the bar's middle
    var("ndN", "choose(N, %s)" % ", ".join("nd%d" % k for k in range(1, NMAX + 1)))
    # The rails run straight through the first and the last bar's nodes; the
    # nodes between lie off that line by a few mm, which the rail's width takes.
    var("railSlope", "(ndN - nd1) / max(xN, 1 mm)")
    for k in range(1, NMAX + 1):
        var("dev%d" % k, "if(N >= %d, abs(nd%d - nd1 - railSlope * x%d), 0 mm)" % (k, k, k))
    var("maxDev", "max(%s)" % ", ".join("dev%d" % k for k in range(1, NMAX + 1)))
    var("rw", "max(16 mm, 2 * (maxDev + pinD / 2 + 3 mm))")
    var("yA", "nd1 + railSlope * xa")
    var("yB", "nd1 + railSlope * xb")
    var("yIA", "nd1 + railSlope * (xa + cw)")
    var("yIB", "nd1 + railSlope * (xb - cw)")
    var("frameVol", "frameT * ((xb - xa) * (yA + yB + rw) - (xb - xa - 2 * cw) * (yIA + yIB - rw))"
                    " + N * 2 * pi * (pinD / 2)^2 * (pinH - frameT)")
    var("discVol", "discT * pi * (Rd^2 - N * (cordD / 2 + 0.5 mm)^2 - (cordD / 2 + 0.5 mm)^2)")

    # ================= Wind chime =================
    for k in range(1, NMAX + 1):
        on = "chime && N >= %d" % k
        a = "(%d * 360 deg / N)" % (k - 1)
        cx, cy = "Rc * cos%s" % a, "Rc * sin%s" % a
        var("tx%d" % k, cx)
        var("ty%d" % k, cy)
        tx, ty = "tx%d" % k, "ty%d" % k
        sa, ca = "sin%s" % a, "cos%s" % a
        cmd("sketch.create", name="TubeSection%d" % k, plane="xy", offset="zc - L%d / 2" % k)
        when("TubeSection%d" % k, on)
        cmd("sketch.circle", sketch="TubeSection%d" % k, center=[tx, ty], radius="OD / 2")
        cmd("sketch.circle", sketch="TubeSection%d" % k, center=[tx, ty], radius="ID / 2")
        cmd("feature.extrude", sketch="TubeSection%d" % k, distance="L%d" % k, name="TubeBlank%d" % k, when=on)
        zn = "zc + L%d / 2 - nodeFrac * L%d" % (k, k)
        var("zn%d" % k, zn)
        # The cord hole: across the tube at the top node, square to the radius.
        cmd("feature.cylinder", name="CordHole%d" % k, radius="holeD / 2", height="OD + 2 mm",
            position=["%s + %s * (OD / 2 + 1 mm)" % (tx, sa), "%s - %s * (OD / 2 + 1 mm)" % (ty, ca), "zn%d" % k],
            axis=["-" + sa, ca, "0"], when=on)
        cmd("feature.boolean", op="subtract", target="TubeBlank%d" % k, tool="CordHole%d" % k,
            name="Tube%d" % k, when=on)
        # Its cord: through the hole, up the bore to the disc, a knot on top.
        cmd("feature.cylinder", name="CordAcross%d" % k, radius="cordD / 2", height="OD + 4 mm",
            position=["%s + %s * (OD / 2 + 2 mm)" % (tx, sa), "%s - %s * (OD / 2 + 2 mm)" % (ty, ca), "zn%d" % k],
            axis=["-" + sa, ca, "0"], when=on)
        cmd("feature.cylinder", name="CordUp%d" % k, radius="cordD / 2", height="discT + 2 mm - zn%d" % k,
            position=[tx, ty, "zn%d" % k], when=on)
        cmd("feature.cylinder", name="Knot%d" % k, radius="cordD * 1.5", height="cordD * 1.5",
            position=[tx, ty, "discT"], when=on)
        cmd("feature.boolean", op="union", target="CordUp%d" % k, tool="CordAcross%d" % k,
            name="CordLoop%d" % k, when=on)
        cmd("feature.boolean", op="union", target="CordLoop%d" % k, tool="Knot%d" % k, name="Cord%d" % k, when=on)
        cmd("body.appearance", body="Tube%d" % k, **ALU)
        cmd("body.appearance", body="Cord%d" % k, **CORD)

    # The top disc: holes for the tubes' cords on the circle and the centre cord.
    cmd("sketch.create", name="DiscOutline", plane="xy")
    when("DiscOutline", "chime")
    cmd("sketch.circle", sketch="DiscOutline", center=["0 mm", "0 mm"], radius="Rd")             # e1, e2
    cmd("sketch.circle", sketch="DiscOutline", center=["0 mm", "0 mm"], radius="cordD / 2 + 0.5 mm")  # e3, e4
    cmd("sketch.circle", sketch="DiscOutline", center=["Rc", "0 mm"], radius="cordD / 2 + 0.5 mm")   # e5, e6
    cmd("sketch.pattern", sketch="DiscOutline", entities=["e6"], count="N", angle="360 deg / N",
        center=["0 mm", "0 mm"])
    cmd("feature.extrude", sketch="DiscOutline", distance="discT", name="Disc", when="chime")
    cmd("body.appearance", body="Disc", **WALNUT)

    # The striker, a puck on the centre cord at the tubes' middles.
    cmd("feature.cylinder", name="StrikerPuck", radius="Rs", height="strikerT",
        position=["0 mm", "0 mm", "zs - strikerT / 2"], when="chime")
    cmd("feature.fillet", name="StrikerRound", radius="2 mm",
        edges=[["StrikerPuck:face(0)", "StrikerPuck:face(1)"], ["StrikerPuck:face(0)", "StrikerPuck:face(2)"]],
        when="chime")
    cmd("feature.cylinder", name="StrikerHole", radius="cordD / 2 + 0.5 mm", height="strikerT + 2 mm",
        position=["0 mm", "0 mm", "zs - strikerT / 2 - 1 mm"], when="chime")
    cmd("feature.boolean", op="subtract", target="StrikerRound", tool="StrikerHole", name="Striker", when="chime")
    cmd("body.appearance", body="Striker", **WALNUT)

    # The wind sail, hanging below the longest tube.
    cmd("feature.block", name="SailBlank", size=["sw", "sailT", "sh"],
        position=["-sw / 2", "-sailT / 2", "sailTop - sh"], when="chime")
    cmd("feature.fillet", name="Sail", radius="0.3 * sw",
        edges=[["SailBlank:face(%d)" % a, "SailBlank:face(%d)" % b] for a, b in ((0, 4), (0, 5), (1, 4), (1, 5))],
        when="chime")
    cmd("body.appearance", body="Sail", **PLY)

    # The centre cord, from the sail through the striker and the disc to a
    # ring to hang it by.
    cmd("feature.cylinder", name="CentreCord", radius="cordD / 2", height="ringZ - ringR - sailTop + 1 mm",
        position=["0 mm", "0 mm", "sailTop"], when="chime")
    cmd("feature.torus", name="Ring", major="ringR", minor="2 mm", position=["0 mm", "0 mm", "ringZ"],
        axis=["0", "1", "0"], when="chime")
    cmd("feature.boolean", op="union", target="CentreCord", tool="Ring", name="Hanger", when="chime")
    cmd("body.appearance", body="Hanger", **CORD)

    # ================= Glockenspiel =================
    for k in range(1, NMAX + 1):
        on = "bars && N >= %d" % k
        cmd("feature.block", name="BarBlank%d" % k, size=["barW", "L%d" % k, "barT"],
            position=["x%d - barW / 2" % k, "-L%d / 2" % k, "barZ"], when=on)
        cmd("sketch.create", name="BarHoles%d" % k, plane="xy", offset="barZ - 1 mm")
        when("BarHoles%d" % k, on)
        cmd("sketch.circle", sketch="BarHoles%d" % k, center=["x%d" % k, "nd%d" % k], radius="barHoleD / 2")
        cmd("sketch.circle", sketch="BarHoles%d" % k, center=["x%d" % k, "-nd%d" % k], radius="barHoleD / 2")
        cmd("feature.extrude", sketch="BarHoles%d" % k, distance="barT + 2 mm", cut="BarBlank%d" % k,
            name="Bar%d" % k, when=on)
        cmd("body.appearance", body="Bar%d" % k, **ALU)

    # The frame: two rails under the node lines and two end pieces, one flat
    # part to cut from plywood, with the pins at the nodes.
    cmd("sketch.create", name="FrameOutline", plane="xy")
    when("FrameOutline", "bars")
    cmd("sketch.polyline", sketch="FrameOutline", closed=True, points=[
        ["xa", "-(yA + rw / 2)"], ["xb", "-(yB + rw / 2)"], ["xb", "yB + rw / 2"], ["xa", "yA + rw / 2"]])
    cmd("sketch.polyline", sketch="FrameOutline", closed=True, points=[
        ["xa + cw", "-(yIA - rw / 2)"], ["xb - cw", "-(yIB - rw / 2)"],
        ["xb - cw", "yIB - rw / 2"], ["xa + cw", "yIA - rw / 2"]])
    cmd("feature.extrude", sketch="FrameOutline", distance="frameT", name="FramePlate", when="bars")
    cmd("body.appearance", body="FramePlate", **PLY)
    prev = "FramePlate"
    for k in range(1, NMAX + 1):
        on = "bars && N >= %d" % k
        cmd("sketch.create", name="Pins%d" % k, plane="xy")
        when("Pins%d" % k, on)
        cmd("sketch.circle", sketch="Pins%d" % k, center=["x%d" % k, "nd%d" % k], radius="pinD / 2")
        cmd("sketch.circle", sketch="Pins%d" % k, center=["x%d" % k, "-nd%d" % k], radius="pinD / 2")
        name = "Frame" if k == NMAX else "FramePins%d" % k
        cmd("feature.extrude", sketch="Pins%d" % k, distance="pinH", name="PinPair%d" % k, when=on)
        cmd("body.appearance", body="PinPair%d" % k, **BRASS)
        cmd("feature.boolean", op="union", target=prev, tool="PinPair%d" % k, name=name, when=on)
        prev = name

    # ================= Sets =================
    tubes = [{"name": "Tube%d" % k} for k in range(1, NMAX + 1)]
    barsq = [{"name": "Bar%d" % k} for k in range(1, NMAX + 1)]
    cmd("set.define", name="Tubes", kind="body", where={"any": tubes})
    cmd("set.define", name="Bars", kind="body", where={"any": barsq})
    cmd("set.define", name="Notes", kind="body", where={"any": [{"set": "Tubes"}, {"set": "Bars"}]})
    for k in range(1, NMAX + 1):
        cmd("set.define", name="Note %d" % k, kind="body", where={"any": [{"name": "Tube%d" % k}, {"name": "Bar%d" % k}]})
    cmd("set.define", name="Cut sheet", kind="face", where={"any": [
        {"in": "Disc", "normal": {"along": "z"}},
        {"in": "Sail", "normal": {"along": "y"}},
        {"in": "Frame", "normal": {"along": "z"}, "below": {"z": "frameT + 0.001 mm"}}]})

    # ================= Assertions =================
    e = "0.01 mm"
    for k in range(1, NMAX + 1):
        lphys = "(%s)" % timo("sqrt(beta / (2 * pi * fRoot * pow(2, s%d / 12)) * c * rg / 1 m) * 1 m" % k)
        # A tube: its box is the tube on the circle, its middle at zc, and
        # exactly as long as its note wants (both ends within 0.01 mm).
        lo = ["tx%d - OD / 2 - %s" % (k, e), "ty%d - OD / 2 - %s" % (k, e), "zc - %s / 2 - %s" % (lphys, e)]
        hi = ["tx%d + OD / 2 + %s" % (k, e), "ty%d + OD / 2 + %s" % (k, e), "zc + %s / 2 + %s" % (lphys, e)]
        short_top = [lo[0], lo[1], "zc - %s / 2 + %s" % (lphys, e)]
        short_bot = [hi[0], hi[1], "zc + %s / 2 - %s" % (lphys, e)]
        cmd("assert.add", name="Tube %d is in tune (length)" % k, measure="count",
            of={"kind": "body", "where": {"name": "Tube%d" % k, "inside": box(lo, hi),
                                          "not": {"any": [{"inside": box(short_top, hi)},
                                                          {"inside": box(lo, short_bot)}]}}},
            eq="if(chime && N >= %d, 1, 0)" % k)
        zn = "(zc + %s / 2 - 0.2242 * %s)" % (lphys, lphys)
        cmd("assert.add", name="Tube %d: cord hole at the node" % k, measure="count",
            of={"kind": "face", "where": {"in": "Tube%d" % k, "hole": True, "radius": "holeD / 2",
                                          "inside": box(["-" + BIG, "-" + BIG, "%s - holeD / 2 - %s" % (zn, e)],
                                                        [BIG, BIG, "%s + holeD / 2 + %s" % (zn, e)])}},
            eq="if(chime && N >= %d, 1, 0)" % k)
        # A bar: along y, centred on y = 0, as long as its note wants.
        blo = ["x%d - barW / 2 - %s" % (k, e), "-%s / 2 - %s" % (lphys, e), "barZ - %s" % e]
        bhi = ["x%d + barW / 2 + %s" % (k, e), "%s / 2 + %s" % (lphys, e), "barZ + barT + %s" % e]
        cmd("assert.add", name="Bar %d is in tune (length)" % k, measure="count",
            of={"kind": "body", "where": {"name": "Bar%d" % k, "inside": box(blo, bhi),
                                          "not": {"any": [{"inside": box([blo[0], "-%s / 2 + %s" % (lphys, e), blo[2]], bhi)},
                                                          {"inside": box(blo, [bhi[0], "%s / 2 - %s" % (lphys, e), bhi[2]])}]}}},
            eq="if(bars && N >= %d, 1, 0)" % k)
        nd = "((0.5 - 0.2242) * %s)" % lphys
        hb = lambda s: box(["x%d - barHoleD / 2 - %s" % (k, e), "%s%s - barHoleD / 2 - %s" % (s, nd, e), "-" + BIG],
                           ["x%d + barHoleD / 2 + %s" % (k, e), "%s%s + barHoleD / 2 + %s" % (s, nd, e), BIG])
        cmd("assert.add", name="Bar %d: holes at the nodes" % k, measure="count",
            of={"kind": "face", "where": {"in": "Bar%d" % k, "hole": True, "radius": "barHoleD / 2",
                                          "any": [{"inside": hb("")}, {"inside": hb("-")}]}},
            eq="if(bars && N >= %d, 2, 0)" % k)
    # The longest note, measured as the body's extent.
    cmd("assert.add", name="Note 1: extent along its length", measure="extent", of={"set": "Note 1"},
        axis="z", eq="if(chime, %s, barT)" % timo("sqrt(beta / (2 * pi * fRoot) * Kc) * 1 m"), tol="0.001 mm")
    cmd("assert.add", name="Note 1: extent across", measure="extent", of={"set": "Note 1"},
        axis="y", eq="if(chime, OD, %s)" % timo("sqrt(beta / (2 * pi * fRoot) * Kc) * 1 m"), tol="0.001 mm")
    cmd("assert.add", name="Every note is there", measure="count", of={"set": "Notes"}, eq="N")
    cmd("assert.add", name="Node holes go through", measure="through",
        of={"kind": "face", "where": {"hole": True, "radius": "if(chime, holeD, barHoleD) / 2"}})
    cmd("assert.add", name="Node holes: one per tube, two per bar", measure="count",
        of={"kind": "face", "where": {"hole": True, "radius": "if(chime, holeD, barHoleD) / 2"}},
        eq="if(chime, N, 2 * N)")
    cmd("assert.add", name="Notes do not hit each other", measure="clearance",
        from_={"set": "Notes"}, to={"set": "Notes"}, min="0.85 * if(chime, tubeGap, barGap)")
    cmd("assert.add", name="Nothing touches a note (cords and pins pass through the holes)", measure="overlap",
        of={"set": "Notes"}, to={"kind": "body", "where": {"not": {"set": "Notes"}}}, **{"is": False})
    # The striker: its box is a disc of radius Rc - OD/2 - strikeGap (so the
    # gap to the tubes, whose places the tube assertions prove, is the striker
    # gap), standing 12 to 25 mm below the tubes' middles.
    rs = "(Rc - OD / 2 - strikeGap)"
    cmd("assert.add", name="Striker: the striker gap from every tube, 12 to 25 mm below their middles",
        measure="count",
        of={"kind": "body", "where": {"name": "Striker",
                                      "inside": box(["-%s - %s" % (rs, e), "-%s - %s" % (rs, e), "zc - 25 mm"],
                                                    ["%s + %s" % (rs, e), "%s + %s" % (rs, e), "zc - 12 mm"]),
                                      "not": {"any": [
                                          {"inside": box(["-%s + %s" % (rs, e), "-" + BIG, "-" + BIG], [BIG, BIG, BIG])},
                                          {"inside": box(["-" + BIG, "-" + BIG, "-" + BIG], ["%s - %s" % (rs, e), BIG, BIG])}]}}},
        eq="if(chime, 1, 0)")
    cmd("assert.add", name="The striker reaches every tube", measure="count",
        of={"kind": "body", "where": {"set": "Tubes", "any": [
            {"above": {"z": "zs - strikerT / 2 + 0.001 mm"}}, {"below": {"z": "zs + strikerT / 2 - 0.001 mm"}}]}},
        eq="0")
    cmd("assert.add", name="Shortest note long enough to drill and hang", measure="count",
        of={"kind": "body", "where": {"any": [
            {"set": "Tubes", "above": {"z": "zc - Lfloor / 2 + 0.001 mm"}},
            {"set": "Bars", "inside": box(["-" + BIG, "-Lfloor / 2 + 0.001 mm", "-" + BIG],
                                          [BIG, "Lfloor / 2 - 0.001 mm", BIG])}]}},
        eq="0")
    cmd("assert.add", name="Longest note short enough to handle", measure="count",
        of={"kind": "body", "where": {"set": "Notes", "not": {"inside": box(
            ["-" + BIG, "if(chime, -" + BIG + ", -Lceil / 2)", "if(chime, zc - Lceil / 2, -" + BIG + ")"],
            [BIG, "if(chime, " + BIG + ", Lceil / 2)", "if(chime, zc + Lceil / 2, " + BIG + ")"])}}},
        eq="0")
    cmd("assert.add", name="Disc or frame volume (holes cut, pins seated in the rails)", measure="volume",
        of={"kind": "body", "where": {"any": [{"name": "Disc"}, {"name": "Frame"}]}},
        eq="if(chime, discVol, frameVol)")
    cmd("assert.add", name="Cut sheet: disc and sail, or frame", measure="count", of={"set": "Cut sheet"},
        eq="if(chime, 2, 1)")

    pub = [
        ("instrument", dict(label="Instrument", description="A wind chime of tubes hanging from a disc, or a "
                            "glockenspiel of bars on a frame", group="Instrument", order=1, kind="choice",
                            choices=["Wind chime (tubes)", "Glockenspiel (bars)"])),
        ("scale", dict(label="Scale", description="The notes, from the lowest up: a scale or a chord. Westminster "
                       "is the Big Ben quarters (lowest note B for the original key)", group="Notes", order=1,
                       kind="choice", choicesFrom="scales")),
        ("root", dict(label="Lowest note", description="The note of the longest tube or bar",
                      group="Notes", order=2, kind="choice", choicesFrom="notes")),
        ("octave", dict(label="Octave", description="Octave of the lowest note (C4 is middle C, A4 = 440 Hz); the "
                        "range keeps every tube or bar between the shortest that can be drilled and the longest "
                        "that can be handled", group="Notes", order=3, kind="integer",
                        min="octMin", max="octMax")),
        ("N", dict(label="Notes", description="How many tubes or bars, following the scale up; at most two octaves",
                   group="Notes", order=4, kind="integer", min="3", max="maxNotes")),
        ("tubeMat", dict(label="Tube material", description="Young's modulus, density and shear modulus of the tube",
                         group="Wind chime", order=1, kind="choice", choicesFrom="tubeMaterials")),
        ("tubeSize", dict(label="Tube size", description="Outside diameter x wall in mm", group="Wind chime",
                          order=2, kind="choice", choicesFrom="tubeSizes")),
        ("strikeGap", dict(label="Striker gap", description="Gap between the striker and the tubes at rest",
                           group="Wind chime", order=3, min="5 mm", max="30 mm", step="1 mm", unit="mm")),
        ("barMat", dict(label="Bar material", description="Young's modulus along the bar, density and shear modulus. Wood bars are straight (not undercut): a starting point, tune by ear",
                        group="Glockenspiel", order=1, kind="choice", choicesFrom="barMaterials")),
        ("barW", dict(label="Bar width", description="Width of the flat bars", group="Glockenspiel", order=2,
                      min="15 mm", max="60 mm", step="1 mm", unit="mm")),
        ("barT", dict(label="Bar thickness", description="Thickness of the bars (they bend through it)",
                      group="Glockenspiel", order=3, min="max(3 mm, barW / 8)", max="25 mm", step="0.5 mm", unit="mm")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        cmd("variable.publish", **p)
    cmd("document.info",
        title="Tuned chimes",
        description="A wind chime of tubes, or a glockenspiel of bars, that is in tune before you cut it: pick "
                    "the scale, the lowest note, the number of notes, the material and the tube or bar size; "
                    "every tube or bar gets the length of its note from the free-free beam (Euler-Bernoulli with "
                    "the Timoshenko correction) and its cord or pin holes at the nodes, 0.2242 L from each end. Variables f1..f12 are the "
                    "frequencies (Hz) and L1..L12 the cut lengths; assert.list proves each length and hole. "
                    "Metal is within about a quarter semitone, wood is a starting point: cut long, then tune with a tuner. Export the face set \"Cut sheet\" as SVG "
                    "for the disc and sail (or the frame).",
        author="3DCraft Jigs", licence="CC-BY-4.0",
        url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/tuned-chimes",
        tags=["music", "wind chime", "glockenspiel", "xylophone", "tuning", "physics", "cut list", "laser"])
    cmd("jig.export", path="dist/tuned-chimes.3dcraftjig")


if __name__ == "__main__":
    main()
    out = []
    for c, p in steps:
        if "from_" in p:
            p["from"] = p.pop("from_")
        out.append(json.dumps([c, p]))
    print("[\n" + ",\n".join(out) + "\n]")
