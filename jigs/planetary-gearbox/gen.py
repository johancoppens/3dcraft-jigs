#!/usr/bin/env python3
"""Writes build.json for the planetary gearbox Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the gear construction and the assembly conditions are readable.

Every gear is drawn as the spur-gear Jig draws one (jigs/spur-gear): one
tooth from the involute's formula (sketch.curve), a radial foot, tip and root
arcs, repeated round as a chained sketch pattern, extruded once. The ring's
teeth are cut by such an outline with the addendum and dedendum swapped: the
space of an internal gear has the shape of an external gear's tooth.

Coordinates: the sun's axis is the z axis, the gears from z = 0 to z = w,
planet 1 on the +x axis, the carrier above the gears.
"""
import json

MODULES = [0.8, 1, 1.25, 1.5, 2, 2.5, 3]
DEFAULT_MODULE = 4  # 1.5 mm

SUN = {"color": "#D4A24C", "roughness": 0.45}      # ochre
PLANET = {"color": "#2E7D7A", "roughness": 0.45}   # petrol
RING = {"color": "#5B7299", "roughness": 0.5}      # slate blue
CARRIER = {"color": "#C2694B", "roughness": 0.5}   # terracotta

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


def gear_outline(p, teeth, ra, rf, thin, rs=None):
    """Variables and a sketch for the outline of an external gear with
    `teeth` teeth, tip radius ra and root radius rf, each tooth made
    thinner by `thin` on the pitch circle (negative: thicker). The tooth is
    centred on the +x axis. Below rs (default: the base circle, or 0.1 module
    above the root when that is higher) the flank runs radially to the root."""
    var(p + "rp", "module * %s / 2" % teeth)
    var(p + "rb", "%srp * cos(alpha)" % p)
    var(p + "ra", ra)
    var(p + "rf", rf)
    var(p + "g", "-pi / (2 * %s) - (tan(alpha) - alpha / 1 rad) + (%s) / (2 * %srp)" % (teeth, thin, p))
    var(p + "rs", rs or "max(%srb, %srf + 0.1 * module)" % (p, p))
    var(p + "t0", "sqrt((%srs / %srb)^2 - 1)" % (p, p))
    var(p + "ta", "sqrt((%sra / %srb)^2 - 1)" % (p, p))
    var(p + "phis", "%sg + %st0 - atan(%st0) / 1 rad" % (p, p, p))
    var(p + "half", "pi / %s" % teeth)
    var(p + "thetaA", "%sg + %sta - atan(%sta) / 1 rad" % (p, p, p))
    sk = p + "Outline"
    cmd("sketch.create", name=sk)
    R = lambda s: s.replace("$", p)  # noqa: E731
    cmd("sketch.point", sketch=sk, at=[R("$rf * cos($phis * 1 rad)"), R("$rf * sin($phis * 1 rad)")])
    cmd("sketch.curve", sketch=sk, x=R("$rb * (cos($g + t) + t * sin($g + t))"),
        y=R("$rb * (sin($g + t) - t * cos($g + t))"), t=[R("$t0"), R("$ta")])
    cmd("sketch.curve", sketch=sk, x=R("$rb * (cos($g + t) + t * sin($g + t))"),
        y=R("-$rb * (sin($g + t) - t * cos($g + t))"), t=[R("$t0"), R("$ta")])
    cmd("sketch.curve", sketch=sk, x=R("$ra * cos(t)"), y=R("$ra * sin(t)"), t=[R("$thetaA"), R("-$thetaA")],
        start="e3", end="e6")
    cmd("sketch.curve", sketch=sk, x=R("$rf * cos(t)"), y=R("$rf * sin(t)"), t=[R("-$phis"), R("2 * $half + $phis")])
    cmd("sketch.line", sketch=sk, **{"from": "e1", "to": "e2"})
    cmd("sketch.line", sketch=sk, **{"from": "e5", "to": "e9"})
    cmd("sketch.pattern", sketch=sk, entities=["e12", "e4", "e8", "e7", "e13", "e11"], chain=["e1", "e10"],
        angle="360 deg / %s" % teeth, center=["0 mm", "0 mm"], count=teeth)
    return sk


def main():
    cmd("table.set", name="modules", columns=["size", {"name": "value", "unit": "mm"}],
        rows=[["%g mm" % m, m] for m in MODULES])
    # Inputs.
    var("moduleSize", str(DEFAULT_MODULE))
    var("Zs", "12")
    var("Zr", "48")
    var("N", "3")
    var("w", "10 mm")
    var("backlash", "0.1 mm")
    var("module", "modules[moduleSize].value")
    var("alpha", "20 deg")
    # The planets' teeth, and the assembly conditions.
    var("Zp", "(Zr - Zs) / 2")
    var("ratio", "1 + Zr / Zs")                         # sun in, carrier out, ring held
    var("a", "module * (Zs + Zp) / 2")                  # centre distance sun - planet
    var("assembles", "mod(Zs + Zr, N) == 0 && mod(Zr - Zs, 2) == 0")
    var("tipGap", "2 * a * sin(180 deg / N) - module * (Zp + 2)")  # between neighbouring planets' tips
    # The ring teeth's range, built so that every value in it assembles, the
    # planets clear each other and the teeth do not interfere: Zr = Zs + 2 Zp,
    # with Zp = -Zs (mod Nq) (Nq = N, or N / 2 for an even N), so Zr runs in
    # steps of 2 Nq. Zp at least 17: then the ring's tips (a stub addendum of
    # 0.8 module) meet the planet's flanks only on its involute, above its
    # base circle (checked for every sun of 10 to 30 teeth; ringTipOk below).
    # Zp at most 30, and at most what keeps tipGap >= module / 2.
    var("Nq", "if(mod(N, 2) == 0, N / 2, N)")
    var("ZpLo", "17")
    var("Zp1", "ZpLo + mod(-Zs - ZpLo, Nq)")
    var("ZpHi", "min(30, floor((Zs * sin(180 deg / N) - 2.5) / (1 - sin(180 deg / N))))")
    var("ZrMin", "Zs + 2 * Zp1")
    var("ZrMax", "Zs + 2 * (Zp1 + Nq * floor((ZpHi - Zp1) / Nq))")
    var("ZsMin", "choose(N - 2, 10, 11, 17, 24)")       # the least sun for which that range is not empty
    # Involute interference of the ring's tip with the planet (KHK): the
    # ring's tip circle must meet the line of action no nearer the ring's
    # base point than the planet's base point does.
    var("rAdd", "0.8 * module")
    var("ringTipOk", "sqrt((module * Zr / 2 - rAdd)^2 - (module * Zr / 2 * cos(alpha))^2) >= (module * Zr / 2 - module * Zp / 2) * sin(alpha)")

    # Sun: tooth on +x. Planet: built at the origin, tooth on +x. The ring:
    # its tooth spaces are an outline with Zr teeth, tip at the ring's root
    # circle, root at the ring's tip circle. Bores, the ring's band and its
    # holes are circles in the same sketches (a loop inside another is a
    # hole), so no gear needs a boolean.
    var("pinFit", "0.15 mm")
    gear_outline("s", "Zs", "srp + module", "srp - 1.25 * module", "backlash / 2")
    var("sunBore", "clamp(0.5 * srf, 1 mm, 4 mm)")      # radius
    cmd("sketch.circle", sketch="sOutline", center=["0 mm", "0 mm"], radius="sunBore")
    cmd("feature.extrude", sketch="sOutline", distance="w", name="Sun")
    gear_outline("p", "Zp", "prp + module", "prp - 1.25 * module", "backlash / 2")
    var("pinR", "clamp(0.35 * prf, 1 mm, 4 mm)")
    cmd("sketch.circle", sketch="pOutline", center=["0 mm", "0 mm"], radius="pinR + pinFit")
    cmd("feature.extrude", sketch="pOutline", distance="w", name="PlanetBored")
    # The ring's tips (Zr >= 44) lie outside its base circle: its flanks are
    # involute to the tip, with only a 0.01 mm radial step there (a longer
    # radial tip would foul the planets' flanks). A band of max(3 modules,
    # 8 mm) round the teeth, six M3 holes in it.
    gear_outline("r", "Zr", "rrp + 1.25 * module", "rrp - rAdd", "-backlash / 2", rs="max(rrb, rrf + 0.01 mm)")
    var("rRoot", "rrp + 1.25 * module")
    var("rim", "max(3 * module, 8 mm)")
    var("Ro", "rRoot + rim")
    cmd("sketch.circle", sketch="rOutline", center=["0 mm", "0 mm"], radius="Ro")
    for k in range(6):
        cmd("sketch.circle", sketch="rOutline", radius="1.7 mm",
            center=["(rRoot + rim / 2) * cos(%d deg)" % (30 + 60 * k), "(rRoot + rim / 2) * sin(%d deg)" % (30 + 60 * k)])
    cmd("feature.extrude", sketch="rOutline", distance="w", name="RingGear")

    # Planet 1 on +x: a space towards the sun's tooth on +x. With an odd Zp
    # that is a tooth turned 0 and the ring has a space on +x; with an even Zp
    # the planet turns half a tooth and so does the ring.
    var("pTurn", "if(mod(Zp, 2) == 0, 180 deg / Zp, 0 deg)")
    var("rTurn", "if(mod(Zp, 2) == 0, 180 deg / Zr, 0 deg)")
    cmd("feature.transform", source="PlanetBored", angle="pTurn", axis=[0, 0, 1],
        translate=["a", "0 mm", "0 mm"], name="Planet1")
    # Planet k at 360 deg (k - 1) / N about the sun: turned about its own
    # centre by phi (Zs + Zp) / Zp, which meshes it when (Zs + Zr) / N is whole.
    for k in range(2, 7):
        phi = "(360 deg * %d / N)" % (k - 1)
        name = "Planet%d" % k
        cmd("feature.transform", source="Planet1", keep=True, angle="%s * (Zs + Zp) / Zp" % phi, axis=[0, 0, 1],
            pivot=["a", "0 mm", "0 mm"], translate=["a * cos(%s) - a" % phi, "a * sin(%s)" % phi, "0 mm"], name=name)
        if k > 3:
            when(name, "N >= %d" % k)
    cmd("body.appearance", body="Planet1", **PLANET)

    # The ring, turned to mesh.
    cmd("feature.transform", source="RingGear", angle="rTurn", axis=[0, 0, 1], name="Ring")

    # The carrier: a spider above the gears, an arm and a pin per planet,
    # and an output shaft.
    var("gap", "0.5 mm")
    var("tc", "max(3 mm, 2 * module)")
    var("zc", "w + gap")
    var("armW", "2 * pinR + 4 mm")
    var("hubR", "max(0.5 * a, sunBore + 3 mm)")
    var("shaftR", "clamp(0.25 * a, 2.5 mm, 8 mm)")
    cmd("feature.cylinder", name="Hub", radius="hubR", height="tc", position=["0 mm", "0 mm", "zc"])
    cmd("feature.block", name="Arm", size=["a", "armW", "tc"], position=["0 mm", "-armW / 2", "zc"])
    cmd("feature.cylinder", name="ArmEnd", radius="armW / 2", height="tc", position=["a", "0 mm", "zc"])
    cmd("feature.cylinder", name="Pin", radius="pinR", height="w + gap + 0.5 mm", position=["a", "0 mm", "0 mm"])
    cmd("feature.boolean", op="union", target="Arm", tool="ArmEnd", name="ArmRound")
    cmd("feature.boolean", op="union", target="ArmRound", tool="Pin", name="ArmPin")
    cmd("feature.pattern", name="Arms", source="ArmPin", count="N", angle="360 deg / N")
    cmd("feature.boolean", op="union", target="Hub", tool="Arms", name="Spider")
    cmd("feature.cylinder", name="OutputShaft", radius="shaftR", height="2 * tc + 4 mm", position=["0 mm", "0 mm", "zc"])
    cmd("feature.boolean", op="union", target="Spider", tool="OutputShaft", name="Carrier")

    cmd("body.appearance", body="Sun", **SUN)
    cmd("body.appearance", body="Ring", **RING)
    cmd("body.appearance", body="Carrier", **CARRIER)

    # The checks, at every regeneration.
    cmd("set.define", name="Planets", kind="body", where={"name": "Planet?"})
    cmd("set.define", name="Gears", kind="body",
        where={"any": [{"set": "Planets"}, {"name": "Sun"}, {"name": "Ring"}]})
    planets = {"kind": "body", "where": {"set": "Planets"}}
    cmd("assert.add", name="Assembly conditions: (sun + ring) / planets whole, planets apart, no ring tip interference",
        measure="count", of=planets, eq="if(assembles && ringTipOk && tipGap >= 0.49 * module, N, 0)")
    cmd("assert.add", name="Neighbouring planets clear each other", measure="clearance",
        **{"from": "Planet1", "to": "Planet2"}, min="0.4 * module")
    # (Whether the planets mesh without overlap is checked outside the Jig,
    # with document.interference at sample points: as an assertion, an
    # interference holds several hundred MB per point in a range check and a
    # clearance between meshing gears is slow and comes out notProven. See
    # README.)

    pub = [
        ("moduleSize", dict(label="Module", description="Tooth size: pitch diameter / teeth, the same for every gear "
                            "(pressure angle 20 deg)", group="Gears", order=1, kind="choice", choicesFrom="modules")),
        ("N", dict(label="Planets", description="Number of planet gears, evenly spaced", group="Gears", order=2,
                   kind="integer", min="3", max="6")),
        ("Zs", dict(label="Sun teeth", description="Teeth of the sun gear (the input). More planets need a larger sun "
                    "so they clear each other", group="Gears", order=3, kind="integer", min="ZsMin", max="30")),
        ("Zr", dict(label="Ring teeth", description="Teeth of the ring gear. Its range and step keep (sun + ring) / "
                    "planets whole and the planets clear of each other; planet teeth = (ring - sun) / 2",
                    group="Gears", order=4, kind="integer", min="ZrMin", max="ZrMax", step="2 * Nq")),
        ("w", dict(label="Face width", description="Thickness of the gears and the ring", group="Size", order=1,
                   min="4 mm", max="30 mm", step="0.5 mm", unit="mm")),
        ("backlash", dict(label="Backlash", description="Play between meshing teeth on the pitch circle; 0.1 to 0.2 mm "
                          "for a 3D print", group="Size", order=2, min="0.05 mm", max="0.3 mm", step="0.01 mm",
                          unit="mm")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        cmd("variable.publish", **p)
    cmd("document.info",
        title="Planetary gearbox",
        description="A planetary gear set with true involute teeth: a sun, 3 to 6 planets, an internal ring gear and a "
                    "carrier with pins and an output shaft, each its own body. Choose the module and the teeth of the sun "
                    "and the ring; the planets' teeth are (ring - sun) / 2. The ring's range and step keep the set "
                    "assemblable ((sun + ring) / planets whole), the planets clear of each other and the ring's tips "
                    "clear of the planets' feet, and assertions check that on the model. Reduction with the ring held: "
                    "1 + ring / sun (variable ratio). Export STL or 3MF to print (choose the bodies), STEP for CAD.",
        author="Johan Coppens", licence="CC-BY-4.0",
        url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/planetary-gearbox",
        tags=["gear", "planetary", "epicyclic", "involute", "gearbox", "3D printing", "mechanism"])
    cmd("jig.export", path="dist/planetary-gearbox.3dcraftjig")
    return steps


if __name__ == "__main__":
    main()
    out = json.dumps(steps)
    print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
