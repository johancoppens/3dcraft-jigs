#!/usr/bin/env python3
"""Writes build.json of the orrery Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written. The gear trains are found here
(trains.py: a deterministic search over the tooth counts) and written into the document as a table, so
the model itself never searches: a row is picked by the planets, the Moon, the most teeth and the
accuracy target.

Layout (seen from above, z up): the centre post C on the z axis carries the planets' tubes, nested, the
innermost (Mercury) longest; the lay shaft L2 stands at (a2, 0) and carries loose compound gears; the
input shaft L1 with the crank stands at (x1, y1), y1 < 0. Each body X has two layers of gears above the
base plate: in the lower one A_X (fixed on L1) drives B_X (on L2), in the upper one C_X (fixed to B_X)
drives D_X (fixed on the tube of X). Above the gears the tubes end in arms, the outermost (Saturn)
lowest; each arm carries a pin and the planet's ball at the height of the Sun. With the Moon, the Moon's
tube ends just below the Earth's arm in a gear that drives, through an idler under the arm, a gear of
the same size on the Earth's sleeve: the sleeve then keeps the Moon tube's turn (parallel motion) and
carries the Moon's arm.

Every gear is drawn as the spur-gear Jig draws one (the same tooth variables, tip and root arcs, a
chained sketch pattern), but each flank is a circular arc from the root circle through the involute's
point at t^2 = 0.3 t0^2 + 0.7 ta^2 to its tip point (the centre worked out in variables) instead of a
fitted spline with a radial foot: a spline flank made a gear about 45 times slower to build, and this
orrery has up to 35 gears. Over the involute part the arc lies within 0.041 module inside the involute
and 0.004 outside (python3 gen.py --flank). See the README for why there is no radial foot.

Every part is its own body, apart from every other by at least 0.01 mm (a fixed gear on its tube or
spindle, an arm on its tube, a ball on its pin), so overlap assertions over groups of bodies cover every
pair in the model.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trains  # noqa: E402
from trains import BODIES, SETS, TARGETS, ZMAX  # noqa: E402

KEYS = [b[0] for b in BODIES]
NAME = {b[0]: b[1] for b in BODIES}
PER = {b[0]: b[2] for b in BODIES}
L0 = {b[0]: b[3] for b in BODIES}
ORBITS = ["Me", "Ve", "Ea", "Ma", "Ju", "Sa"]   # round the Sun, inside out (the Moon goes with the Earth)

MODULES = [("1 mm", 1), ("1.25 mm", 1.25), ("1.5 mm", 1.5), ("2 mm", 2)]
# Material of the gears: face width b (the sheet for a laser-cut gear).
MATERIALS = [("3D printed (PLA, PETG)", 4), ("Laser-cut acrylic 3 mm", 3), ("Laser-cut plywood 4 mm", 4)]

# Ball radii (mm at size 1): ordered as the real ones are, not to scale.
BALL = {"Sun": 12, "Me": 3, "Ve": 4.6, "Ea": 4.8, "Mo": 1.8, "Ma": 3.6, "Ju": 8.5, "Sa": 7.5}

# The flank arc passes through the involute's point at t^2 = (1 - W_MID) t0^2 + W_MID ta^2.
W_MID = 0.7
MAX_IDL = 5     # idlers under the Earth's arm, at most

# Shared Jig palette.
BRASS = {"color": "#B8954A", "metallic": 0.9, "roughness": 0.35}
STEEL = {"color": "#7D858C", "metallic": 0.85, "roughness": 0.4}
ALU = {"color": "#B9BEC4", "metallic": 0.9, "roughness": 0.25}
COPPER = {"color": "#B87350", "metallic": 0.85, "roughness": 0.35}
WALNUT = {"color": "#7A5638", "roughness": 0.6}
COLOUR = {
    "Sun": {"color": "#D4A24C", "roughness": 0.4},      # ochre
    "Me": {"color": "#7D858C", "roughness": 0.5},       # steel
    "Ve": {"color": "#D9B98A", "roughness": 0.5},       # plywood (pale yellow)
    "Ea": {"color": "#5B7299", "roughness": 0.45},      # slate blue
    "Mo": {"color": "#B9BEC4", "roughness": 0.5},       # aluminium
    "Ma": {"color": "#C2694B", "roughness": 0.5},       # terracotta
    "Ju": {"color": "#B87350", "roughness": 0.45},      # copper (Jupiter's bands)
    "Sa": {"color": "#E8DFCC", "roughness": 0.45},      # cream, with its ring
}

steps = []


def cmd(c, **p):
    steps.append([c, p])


def var(name, expr):
    cmd("variable.set", name=name, expr=expr)


def look(body, colour, material=("PLA", "1.24 g/cm3")):
    cmd("body.appearance", body=body, **colour)
    cmd("body.material", body=body, name=material[0], density=material[1])


# ---------------------------------------------------------------- the trains table

ROWS, ZLIM = trains.table()
cols = ["row", "S12", "S2"]
for k in KEYS:
    cols += ["zA_" + k, "zB_" + k, "zC_" + k, "zD_" + k]
rows = []
for s, moon, Z, ti, r in ROWS:
    worst, S12, S2, sol = r
    row = ["%d-%d-%d-%d" % (s, moon, Z, ti), S12, S2]
    for k in KEYS:
        if k in sol:
            row += list(sol[k][1:])
        else:   # not built in this row: an even split, never used
            row += [S12 // 2, S12 - S12 // 2, S2 // 2, S2 - S2 // 2]
    rows.append(row)
cmd("table.set", name="trains", columns=cols, rows=rows)
cmd("table.set", name="zlim", columns=["key", "zmin"], rows=[[k, v] for k, v in ZLIM])
cmd("table.set", name="planetSets", columns=["planets"], rows=[[s] for s in SETS])
cmd("table.set", name="targets", columns=["target", "ppm"], rows=[[t, v] for t, v in TARGETS])
cmd("table.set", name="modules", columns=["size", {"name": "value", "unit": "mm"}], rows=[list(r) for r in MODULES])
cmd("table.set", name="materials", columns=["material", {"name": "b", "unit": "mm"}], rows=[list(r) for r in MATERIALS])

NT = len(TARGETS)
NZ = len(ZMAX)
for name, expr in (
        # public inputs
        ("pset", "4"), ("moon", "1"), ("maxTeeth", "120"), ("acc", str(NT)), ("moduleSize", "1"),
        ("material", "1"), ("rIn", "60 mm"), ("gapO", "14 mm"), ("size", "1.4"), ("days", "0"),
        # fixed design values (trains.py keeps the same)
        ("alpha", "20 deg"),             # pressure angle (ISO 53)
        ("jt", "0.15 mm"),               # backlash on the pitch circle, for a print or a laser cut
        ("rS", "%g mm" % trains.R_SHAFT), ("clr", "%g mm" % trains.CLR), ("wall", "%g mm" % trains.WALL),
        ("fit", "%g mm" % trains.FIT), ("rim", "%g mm" % trains.RIM), ("gapR", "%g mm" % trains.GAP),
        ("g", "1 mm"),                   # between layers: a washer
        ("RING", "1.8"),                 # Saturn's ring, in its radii
        ("hw", "3.5 mm"), ("pinR", "1.5 mm"),
        ("tPlate", "6 mm"),              # the base plate and the bridge plate
        ("pillarR", "5 mm"),
        ("year", "%r" % trains.YEAR),
        # derived
        ("mn", "modules[moduleSize].value"),
        ("b", "materials[material].b"),
        ("zRow", "clamp(floor((maxTeeth - %d) / 10), 0, %d)" % (ZMAX[0], NZ - 1)),
        ("tr", "1 + (((pset - 1) * 2 + moon) * %d + (acc - 1)) * %d + zRow" % (NT, NZ)),
        ("target", "targets[acc].ppm * 1e-6"),
        ("S12", "trains[tr].S12"), ("S2", "trains[tr].S2"),
        ("crank", "360 deg * days / year"),
        ("on_Me", "1"), ("on_Ve", "1"), ("on_Ea", "1"), ("on_Mo", "moon"), ("on_Ma", "pset >= 2"),
        ("on_Ju", "pset >= 3"), ("on_Sa", "pset >= 4"),
        ("idx_Me", "0"), ("idx_Ve", "1"), ("idx_Ea", "2"), ("idx_Mo", "3"), ("idx_Ma", "3 + moon"),
        ("idx_Ju", "4 + moon"), ("idx_Sa", "5 + moon"),
        ("n", "3 + moon + pset - 1")):
    var(name, expr)

# ---------------------------------------------------------------- gears


def gear_vars(p, z):
    """The tooth variables of gear p (as the spur-gear Jig), each flank thinned by jt / 4."""
    for name, expr in (
            ("z", z),
            ("r", "mn * z@ / 2"),
            ("rb", "r@ * cos(alpha)"),
            ("ra", "r@ + mn"),
            ("rf", "r@ - 1.25 * mn"),
            ("g", "-pi / (2 * z@) - (tan(alpha) - alpha / 1 rad) + jt / (4 * r@)"),
            ("rs", "max(rb@, rf@ + 0.1 * mn)"),
            ("t0", "sqrt((rs@ / rb@)^2 - 1)"),
            ("ta", "sqrt((ra@ / rb@)^2 - 1)"),
            ("tm", "sqrt(%g * t0@^2 + %g * ta@^2)" % (1 - W_MID, W_MID)),
            ("rm", "rb@ * sqrt(1 + tm@^2)"),
            ("phis", "g@ + t0@ - atan(t0@) / 1 rad"),
            ("phim", "g@ + tm@ - atan(tm@) / 1 rad"),
            ("half", "pi / z@"),
            ("thetaA", "g@ + ta@ - atan(ta@) / 1 rad"),
            # The flank arc's centre: the circle through the root point, the involute's point at tm and
            # its tip point.
            ("x0", "rf@ * cos(phis@ * 1 rad)"), ("y0", "rf@ * sin(phis@ * 1 rad)"),
            ("xm", "rm@ * cos(phim@ * 1 rad)"), ("ym", "rm@ * sin(phim@ * 1 rad)"),
            ("xa", "ra@ * cos(thetaA@ * 1 rad)"), ("ya", "ra@ * sin(thetaA@ * 1 rad)"),
            ("dd", "2 * (x0@ * (ym@ - ya@) + xm@ * (ya@ - y0@) + xa@ * (y0@ - ym@))"),
            ("ux", "((x0@^2 + y0@^2) * (ym@ - ya@) + (xm@^2 + ym@^2) * (ya@ - y0@) + (xa@^2 + ya@^2) * (y0@ - ym@)) / dd@"),
            ("uy", "((x0@^2 + y0@^2) * (xa@ - xm@) + (xm@^2 + ym@^2) * (x0@ - xa@) + (xa@^2 + ya@^2) * (xm@ - x0@)) / dd@")):
        var(name + "_" + p, expr.replace("@", "_" + p))


def gear(p, z, bore, angle, at, when=None, colour=None):
    """Gear p with z teeth and a bore of radius bore, its layer bottom at at = [x, y, z], turned by angle
    (its tooth 0 on +x at angle 0). Makes the body named p."""
    gear_vars(p, z)
    v = lambda e: e.replace("@", "_" + p)  # noqa: E731

    def pt(rad, ang):
        return [v("%s * cos((%s) * 1 rad)" % (rad, ang)), v("%s * sin((%s) * 1 rad)" % (rad, ang))]

    sk = "S_" + p
    cmd("sketch.create", name=sk, plane="xy")
    # One tooth and the root gap after it: a flank arc from the root circle through the involute to the
    # tip, the tip arc, the other flank down to the root, the root arc to the next tooth.
    cmd("sketch.path", sketch=sk, start=pt("rf@", "phis@"), segments=[
        {"arc": pt("ra@", "thetaA@"), "center": [v("ux@"), v("uy@")]},
        {"arc": pt("ra@", "-thetaA@"), "center": ["0 mm", "0 mm"]},
        {"arc": pt("rf@", "-phis@"), "center": [v("ux@"), v("-uy@")]},
        {"arc": pt("rf@", "2 * half@ + phis@"), "center": ["0 mm", "0 mm"]}])
    cmd("sketch.pattern", sketch=sk, entities=["e4", "e7", "e10", "e13"], chain=["e1", "e11"],
        angle=v("360 deg / z@"), center=["0 mm", "0 mm"], count=v("z@"))
    cmd("sketch.circle", sketch=sk, center=["0 mm", "0 mm"], radius=bore)
    ex = {"sketch": sk, "distance": "b", "name": p + "0"}
    tf = {"source": p + "0", "angle": angle, "axis": [0, 0, 1], "translate": at, "name": p}
    if when:
        ex["when"] = when
        tf["when"] = when
    cmd("feature.extrude", **ex)
    cmd("feature.transform", **tf)
    look(p, colour or BRASS, ("Brass-coloured PLA", "1.24 g/cm3"))


for k in KEYS:
    for s in "ABCD":
        var("z%s_%s" % (s, k), "trains[tr].z%s_%s" % (s, k))
    # Tube of X: k = idx + 1 (the centre post is tube 0).
    var("tIn_" + k, "rS + clr + idx_%s * (wall + clr)" % k)
    var("tOut_" + k, "tIn_%s + wall" % k)
    var("zAB_" + k, "g + 2 * idx_%s * (b + g)" % k)
    var("zCD_" + k, "zAB_%s + b + g" % k)

var("a2", "mn * S2 / 2")
var("d12", "mn * S12 / 2")
for k in KEYS:
    var("raA_" + k, "mn * (zA_%s / 2 + 1)" % k)
    var("raD_" + k, "mn * (zD_%s / 2 + 1)" % k)
# max() takes two arguments: nest it.
req = "0 mm"
for k in KEYS:
    req = "max(%s, if(on_%s, max(raA_%s + tOut_%s + gapR, raD_%s + rS + gapR), 0 mm))" % (req, k, k, k, k)
var("dReq", req)
var("d1", "min(d12 + a2, max(dReq, sqrt(d12^2 + a2^2)))")
var("x1", "(d1^2 - d12^2 + a2^2) / (2 * a2)")
var("y1", "-sqrt(max(0 * (1 mm)^2, d1^2 - x1^2))")
var("beta1", "atan2(-y1, a2 - x1)")         # direction L1 -> L2
var("zTop", "g + 2 * n * (b + g)")

for k in KEYS:
    on = "on_" + k
    w = None if k in ("Me", "Ve", "Ea") else on
    var("rhoB_" + k, "beta1 + 180 deg + 180 deg / zB_{k} - zA_{k} / zB_{k} * (crank - beta1)".format(k=k))
    var("rhoC_" + k, "180 deg - zA_{k} / zB_{k} * crank".format(k=k))
    var("rhoD_" + k, "180 deg / zD_{k} - zC_{k} / zD_{k} * (rhoC_{k} - 180 deg)".format(k=k))
    gear("A_" + k, "zA_" + k, "rS + fit", "crank", ["x1", "y1", "zAB_" + k], w)
    gear("B_" + k, "zB_" + k, "rS + clr", "rhoB_" + k, ["a2", "0 mm", "zAB_" + k], w, COPPER)
    gear("C_" + k, "zC_" + k, "rS + clr", "rhoC_" + k, ["a2", "0 mm", "zCD_" + k], w, COPPER)
    gear("D_" + k, "zD_" + k, "tOut_%s + fit" % k, "rhoD_" + k, ["0 mm", "0 mm", "zCD_" + k], w)
    # B and C are glued into a compound with a spacer between them; a washer under each compound.
    for nm, r_out, z0, h in (("Spacer_", "min(mn * (zB_%s / 2 - 1.25), mn * (zC_%s / 2 - 1.25)) - 1 mm" % (k, k),
                              "zAB_%s + b + fit" % k, "g - 2 * fit"),
                             ("Washer_", "rS + 2.5 mm", "zAB_%s - g + fit" % k, "g - 2 * fit")):
        sk = "S_" + nm + k
        cmd("sketch.create", name=sk, plane="xy")
        cmd("sketch.circle", sketch=sk, center=["0 mm", "0 mm"], radius=r_out)
        cmd("sketch.circle", sketch=sk, center=["0 mm", "0 mm"], radius="rS + clr")
        p = {"sketch": sk, "distance": h, "name": nm + "0" + k}
        t = {"source": nm + "0" + k, "translate": ["a2", "0 mm", z0], "name": nm + k}
        if w:
            p["when"] = w
            t["when"] = w
        cmd("feature.extrude", **p)
        cmd("feature.transform", **t)
        look(nm + k, COPPER if nm == "Spacer_" else STEEL, ("PLA", "1.24 g/cm3"))

# ---------------------------------------------------------------- orbits and arms

for name, expr in (
        ("Rsun", "%g mm * size" % BALL["Sun"]),
        ("ell", "(%g mm + %g mm) * size + 4 mm" % (BALL["Ea"], BALL["Mo"]))):
    var(name, expr)
for k in KEYS:
    var("R_" + k, "%g mm * size" % BALL[k])
# The Moon's gears: the centre gear on the Moon tube and the Earth's sleeve gear have the same teeth (the
# least that fit the Moon tube), the idler as many as reach the Earth's orbit radius.
var("zc", "max(12, ceil(2 * (tOut_Mo + fit + rim) / mn + 2.5))")
var("raGp", "mn * (zc / 2 + 1)")
# Reach of each body's arm end, post, ball (and the Earth's Moon train) from its orbit radius.
for k in ORBITS:
    if k == "Ea":
        var("e_Ea", "max(max(R_Ea, hw), if(moon, max(ell + R_Mo, raGp), 0 mm))")
    elif k == "Sa":
        var("e_Sa", "max(RING * R_Sa, hw)")
    else:
        var("e_" + k, "max(R_%s, hw)" % k)
var("rP_Me", "rIn * mn / 1 mm")
var("rP_Ve", "rP_Me + e_Me + gapO + e_Ve")
var("rE0", "rP_Ve + e_Ve + gapO + e_Ea")
# The idlers between them: 1, 3 or 5 equal ones in a row along the arm (an odd number, so the sleeve
# turns as the Moon tube does), together as many teeth as reach the Earth's orbit radius.
var("tFill", "max(0, rE0 / mn - zc)")
var("nIdl", "clamp(1 + 2 * floor(tFill / 60), 1, %d)" % MAX_IDL)
var("zI", "max(12, ceil(tFill / nIdl))")
var("rP_Ea", "if(moon, mn * (zc + nIdl * zI), rE0)")
var("nGears", "4 * n + moon * (2 + nIdl)")
var("rP_Ma", "rP_Ea + e_Ea + gapO + e_Ma")
var("rP_Ju", "rP_Ma + e_Ma + gapO + e_Ju")
var("rP_Sa", "rP_Ju + e_Ju + gapO + e_Sa")

# Heights: the arms from the outermost tube (lowest) in; the Moon's slot holds its gears.
# Each arm is deeper the longer it is, so that its tip sags as little as a 3 mm arm of 120 mm does
# (a bar's sag under its own weight grows as length^4 / depth^2): 3 to 12 mm deep.
for k in ORBITS:
    var("armH_" + k, "clamp(3 mm * (rP_%s / 120 mm)^2, 3 mm, 12 mm)" % k)
# Above the gears the bridge plate (tPlate), the crank on it (hub, bar and a 14 mm knob), then the arms,
# at least 40 mm above the knob so a hand on the crank stays clear of them.
var("zBr", "zTop")
var("zCrank", "zBr + tPlate + 1 mm")
var("zKnob", "zCrank + 14 mm")
var("zArm0", "zKnob + 40 mm")
var("zArm_Sa", "zArm0")
var("zArm_Ju", "zArm_Sa + on_Sa * (armH_Sa + 3 mm)")
var("zArm_Ma", "zArm_Ju + on_Ju * (armH_Ju + 3 mm)")
var("zArm_Mo", "zArm_Ma + on_Ma * (armH_Ma + 3 mm) + 1 mm")   # 1 mm for the idlers' pin ends
var("zArm_Ea", "zArm_Mo + moon * (b + g)")
var("zArm_Ve", "zArm_Ea + armH_Ea + 3 mm")
var("zArm_Me", "zArm_Ve + armH_Ve + 3 mm")
var("H", "zArm_Me + armH_Me + 2 mm + Rsun")

# Arm angles: each tube turns as its gear D does; the arm sits at the body's mean longitude at J2000.
for k in KEYS:
    var("L0_" + k, "%r deg" % L0[k])
    var("th_" + k, "L0_{k} + rhoD_{k} - 180 deg / zD_{k}".format(k=k))

# The base plate: round the gears' tips with 6 mm to spare, holes for the post and both spindles.
raC = "0 mm"
raL1 = "0 mm"
raL2 = "0 mm"
for k in KEYS:
    raC = "max(%s, if(on_%s, raD_%s, 0 mm))" % (raC, k, k)
    raL1 = "max(%s, if(on_%s, raA_%s, 0 mm))" % (raL1, k, k)
    raL2 = "max(%s, if(on_%s, mn * (max(zB_%s, zC_%s) / 2 + 1), 0 mm))" % (raL2, k, k, k)
var("raC", raC)
var("raL1", raL1)
var("raL2", raL2)
# The box of every gear's tip circle (cb..), the plates 16 mm beyond it, a pillar at each corner 8 mm
# outside it (so clear of every gear whatever the trains).
for name, expr in (
        ("cbL", "min(-raC, x1 - raL1)"), ("cbR", "max(a2 + raL2, x1 + raL1)"),
        ("cbB", "min(min(-raC, -raL2), y1 - raL1)"), ("cbT", "max(raC, raL2)"),
        ("bxL", "cbL - 16 mm"), ("bxR", "cbR + 16 mm"), ("byL", "cbB - 16 mm"), ("byH", "cbT + 16 mm"),
        ("cR", "10 mm"),
        ("tOutN", "rS + clr + (n - 1) * (wall + clr) + wall")):    # the outermost tube
    var(name, expr)
for nm, z0, holes in (("Base", "-tPlate", [("0 mm", "0 mm", "rS + fit"), ("a2", "0 mm", "rS + fit"),
                                           ("x1", "y1", "rS + clr")]),
                      ("Bridge", "zBr", [("0 mm", "0 mm", "tOutN + clr"), ("a2", "0 mm", "rS + fit"),
                                         ("x1", "y1", "rS + clr")])):
    sk = "S_" + nm
    cmd("sketch.create", name=sk, plane="xy", offset=z0)
    cmd("sketch.path", sketch=sk, start=["bxL + cR", "byL"], segments=[
        {"line": ["bxR - cR", "byL"]}, {"arc": ["bxR", "byL + cR"], "center": ["bxR - cR", "byL + cR"]},
        {"line": ["bxR", "byH - cR"]}, {"arc": ["bxR - cR", "byH"], "center": ["bxR - cR", "byH - cR"]},
        {"line": ["bxL + cR", "byH"]}, {"arc": ["bxL", "byH - cR"], "center": ["bxL + cR", "byH - cR"]},
        {"line": ["bxL", "byL + cR"]}, {"arc": "start", "center": ["bxL + cR", "byL + cR"]}])
    for hx, hy, hr in holes:
        cmd("sketch.circle", sketch=sk, center=[hx, hy], radius=hr)
    cmd("feature.extrude", sketch=sk, distance="tPlate", name=nm + "Plate")
    look(nm + "Plate", WALNUT, ("Walnut", "0.65 g/cm3"))
for i, (px, py) in enumerate((("cbL - 8 mm", "cbB - 8 mm"), ("cbR + 8 mm", "cbB - 8 mm"),
                              ("cbR + 8 mm", "cbT + 8 mm"), ("cbL - 8 mm", "cbT + 8 mm")), start=1):
    cmd("feature.cylinder", radius="pillarR", height="zBr - 2 * fit", position=[px, py, "fit"], name="Pillar%d" % i)
    look("Pillar%d" % i, BRASS, ("Brass", "8.5 g/cm3"))

# The centre post (fixed, up into the Sun), the lay shaft L2 (fixed), the input shaft L1 with the crank.
cmd("feature.cylinder", radius="rS", height="H - Rsun - fit + tPlate", position=["0 mm", "0 mm", "-tPlate"],
    name="CentrePost")
look("CentrePost", STEEL, ("Steel", "7.85 g/cm3"))
cmd("feature.cylinder", radius="rS", height="zBr + 2 * tPlate", position=["a2", "0 mm", "-tPlate"], name="LayShaft")
look("LayShaft", STEEL, ("Steel", "7.85 g/cm3"))
var("lcMax", "d1 - (rS + clr + (n - 1) * (wall + clr) + wall) - 4 mm")
var("lcr", "min(22 mm, lcMax)")
cmd("feature.cylinder", radius="rS", height="zCrank + 4 mm + tPlate", position=["0 mm", "0 mm", "-tPlate"],
    name="InSpindle")
cmd("feature.cylinder", radius="4 mm", height="4 mm", position=["0 mm", "0 mm", "zCrank"], name="CrankHub")
cmd("feature.block", size=["lcr", "6 mm", "4 mm"], position=["0 mm", "-3 mm", "zCrank"], name="CrankBar")
cmd("feature.cylinder", radius="3 mm", height="zKnob - zCrank", position=["lcr", "0 mm", "zCrank"], name="CrankKnob")
cmd("feature.boolean", op="union", target="InSpindle", tool="CrankHub", name="In1")
cmd("feature.boolean", op="union", target="In1", tool="CrankBar", name="In2")
cmd("feature.boolean", op="union", target="In2", tool="CrankKnob", name="In3")
cmd("feature.transform", source="In3", angle="crank + beta1 + 180 deg", axis=[0, 0, 1],
    translate=["x1", "y1", "0 mm"], name="InputShaft")
look("InputShaft", STEEL, ("Steel", "7.85 g/cm3"))

# Tubes: from the bottom of D up to its arm (the Moon's: up to the top of its centre gear).
for k in KEYS:
    w = None if k in ("Me", "Ve", "Ea") else "on_" + k
    sk = "S_Tube_" + k
    cmd("sketch.create", name=sk, plane="xy")
    cmd("sketch.circle", sketch=sk, center=["0 mm", "0 mm"], radius="tOut_" + k)
    cmd("sketch.circle", sketch=sk, center=["0 mm", "0 mm"], radius="tIn_" + k)
    top = "zArm_Mo + b" if k == "Mo" else "zArm_%s - fit" % k
    # It stands on the gear of the tube inside it (Mercury's on the base plate).
    var("zTube_" + k, "if(idx_{k} == 0, fit, zAB_{k} - g + fit)".format(k=k))
    p = {"sketch": sk, "distance": "%s - zTube_%s" % (top, k), "name": "Tube0_" + k}
    t = {"source": "Tube0_" + k, "translate": ["0 mm", "0 mm", "zTube_" + k], "name": "Tube_" + k}
    if w:
        p["when"] = w
        t["when"] = w
    cmd("feature.extrude", **p)
    cmd("feature.transform", **t)
    look("Tube_" + k, BRASS, ("Brass", "8.5 g/cm3"))


def arm(k, hole_r, end_hole=None):
    """The arm of k in its own frame (along +x from the centre, bottom at z = 0): a hub round the tube,
    a bar of width 2 hw ending in a half circle at the orbit radius."""
    sk = "S_Arm_" + k
    r = "rP_" + k
    cmd("sketch.create", name=sk, plane="xy")
    hub = "(tOut_%s + 2.5 mm)" % k
    q = "sqrt(%s^2 - hw^2)" % hub
    cmd("sketch.path", sketch=sk, start=[q, "hw"], segments=[
        {"line": [r, "hw"]},
        {"arc": [r, "-hw"], "center": [r, "0 mm"], "clockwise": True},
        {"line": [q, "-hw"]},
        {"arc": "start", "center": ["0 mm", "0 mm"], "clockwise": True}])
    cmd("sketch.circle", sketch=sk, center=["0 mm", "0 mm"], radius=hole_r)
    if end_hole:
        cmd("sketch.circle", sketch=sk, center=[r, "0 mm"], radius=end_hole)
    return sk


for k in ORBITS:
    w = None if k in ("Me", "Ve", "Ea") else "on_" + k
    W = (lambda d: dict(d, when=w)) if w else (lambda d: d)  # noqa: E731
    sk = arm(k, "tIn_" + k, "rS + clr" if k == "Ea" else None)
    cmd("feature.extrude", **W({"sketch": sk, "distance": "armH_" + k, "name": "Arm0_" + k}))
    # The pin from the arm up to fit below the ball (the Earth's fills its sleeve hole when there is no Moon).
    pin = "rS + 0.5 mm" if k == "Ea" else "pinR"
    pw = "on_Ea && !moon" if k == "Ea" else w
    pp = {"radius": pin, "height": "H - R_{k} - fit - zArm_{k} - armH_{k} + 0.5 mm".format(k=k),
          "position": ["rP_" + k, "0 mm", "armH_%s - 0.5 mm" % k], "name": "Pin0_" + k}
    if pw:
        pp["when"] = pw
    cmd("feature.cylinder", **pp)
    cmd("feature.boolean", **W({"op": "union", "target": "Arm0_" + k, "tool": "Pin0_" + k, "name": "Arm1_" + k}))
    if k == "Ea":
        # The idlers' pins under the Earth's arm (with the Moon).
        src = "Arm1_Ea"
        for j in range(1, MAX_IDL + 1):
            cmd("feature.cylinder", radius="pinR", height="b + g + 1 mm + 0.5 mm", when="moon && nIdl >= %d" % j,
                position=["mn * (zc / 2 + (%d - 0.5) * zI)" % j, "0 mm", "-(b + g + 1 mm)"], name="IdlerPin%d" % j)
            cmd("feature.boolean", op="union", target=src, tool="IdlerPin%d" % j, name="Arm%d_Ea" % (j + 1))
            src = "Arm%d_Ea" % (j + 1)
    else:
        src = "Arm1_" + k
    cmd("feature.transform", **W({"source": src, "angle": "th_" + k, "axis": [0, 0, 1],
                                  "translate": ["0 mm", "0 mm", "zArm_" + k], "name": "Arm_" + k}))
    look("Arm_" + k, BRASS, ("Brass", "8.5 g/cm3"))

# ---------------------------------------------------------------- the Moon train

# Gc on the Moon tube's top, the idlers on their pins under the Earth's arm, Gp on the Earth's sleeve; in
# the arm's frame Gc turns by rc and each gear follows the one before (the mesh formula of the trains).
# With an odd number of idlers and Gp as Gc, Gp keeps the Moon tube's turn: the Moon's arm, fixed to it,
# points at the Moon's mean longitude.
var("rc", "rhoD_Mo - th_Ea")
gear("Gc", "zc", "tOut_Mo + fit", "rhoD_Mo", ["0 mm", "0 mm", "zArm_Mo"], "moon")
prev_r, prev_z = "rc", "zc"
for j in range(1, MAX_IDL + 1):
    var("rI%d" % j, "180 deg + 180 deg / zI - %s / zI * %s" % (prev_z, prev_r))
    xj = "mn * (zc / 2 + (%d - 0.5) * zI)" % j
    gear("Idler%d" % j, "zI", "pinR + clr", "th_Ea + rI%d" % j,
         ["%s * cos(th_Ea)" % xj, "%s * sin(th_Ea)" % xj, "zArm_Mo"], "moon && nIdl >= %d" % j)
    prev_r, prev_z = "rI%d" % j, "zI"
# The last idler that is built.
var("rIl", "choose((nIdl + 1) / 2, rI1, rI3, rI5)")
var("rp", "180 deg + 180 deg / zc - zI / zc * rIl")
var("thMo", "L0_Mo + rhoD_Mo - 180 deg / zD_Mo")
var("rSl", "rS")
gear("Gp", "zc", "rSl + fit", "th_Ea + rp", ["rP_Ea * cos(th_Ea)", "rP_Ea * sin(th_Ea)", "zArm_Mo"], "moon")
# The Earth's sleeve, from the bottom of Gp up through the arm to the Moon's arm, which carries the
# Earth's pin and the Moon's pin; built about the origin along +x, then moved.
var("zMA", "zArm_Ea + armH_Ea + 1 mm")
cmd("feature.cylinder", radius="rSl", height="zMA - zArm_Mo + 0.5 mm", position=["0 mm", "0 mm", "zArm_Mo"],
    when="moon", name="Sleeve0")
cmd("sketch.create", name="S_MoonArm", plane="xy", offset="zMA")
cmd("sketch.path", sketch="S_MoonArm", start=["0 mm", "2.5 mm"], segments=[
    {"line": ["ell", "2.5 mm"]}, {"arc": ["ell", "-2.5 mm"], "center": ["ell", "0 mm"], "clockwise": True},
    {"line": ["0 mm", "-2.5 mm"]}, {"arc": "start", "center": ["0 mm", "0 mm"], "clockwise": True}])
cmd("feature.extrude", sketch="S_MoonArm", distance="2.5 mm", when="moon", name="MoonArm0")
cmd("feature.cylinder", radius="1.6 mm", height="H - R_Ea - fit - zMA - 2 mm", position=["0 mm", "0 mm", "zMA + 2 mm"],
    when="moon", name="EarthPin0")
cmd("feature.cylinder", radius="1 mm", height="H - R_Mo - fit - zMA - 2 mm", position=["ell", "0 mm", "zMA + 2 mm"],
    when="moon", name="MoonPin0")
cmd("feature.boolean", op="union", target="Sleeve0", tool="MoonArm0", name="Moon1")
cmd("feature.boolean", op="union", target="Moon1", tool="EarthPin0", name="Moon2")
cmd("feature.boolean", op="union", target="Moon2", tool="MoonPin0", name="Moon3")
cmd("feature.transform", source="Moon3", angle="thMo", axis=[0, 0, 1],
    translate=["rP_Ea * cos(th_Ea)", "rP_Ea * sin(th_Ea)", "0 mm"], when="moon", name="MoonCarrier")
look("MoonCarrier", BRASS, ("Brass", "8.5 g/cm3"))

# ---------------------------------------------------------------- the Sun and the balls

cmd("feature.sphere", radius="Rsun", position=["0 mm", "0 mm", "H"], name="Sun")
look("Sun", COLOUR["Sun"])
for k in ORBITS:
    w = None if k in ("Me", "Ve", "Ea") else "on_" + k
    p = {"radius": "R_" + k, "position": ["rP_%s * cos(th_%s)" % (k, k), "rP_%s * sin(th_%s)" % (k, k), "H"],
         "name": "Ball_" + k if k != "Sa" else "Ball0_Sa"}
    if w:
        p["when"] = w
    cmd("feature.sphere", **p)
# Saturn's ring: a disc through the ball, 0.8 mm thick, out to RING radii, tilted 26.7 deg (the tilt of
# Saturn's axis); it turns with the arm.
cmd("sketch.create", name="S_Ring", plane="xy", offset="H - 0.4 mm")
cmd("sketch.circle", sketch="S_Ring", center=["0 mm", "0 mm"], radius="RING * R_Sa")
cmd("feature.extrude", sketch="S_Ring", distance="0.8 mm", when="on_Sa", name="Ring0")
cmd("feature.transform", source="Ring0", angle="26.7 deg", axis=[1, 0, 0], pivot=["0 mm", "0 mm", "H"],
    when="on_Sa", name="Ring1")
cmd("feature.transform", source="Ring1", angle="th_Sa", axis=[0, 0, 1],
    translate=["rP_Sa * cos(th_Sa)", "rP_Sa * sin(th_Sa)", "0 mm"], when="on_Sa", name="Ring2")
cmd("feature.boolean", op="union", target="Ball0_Sa", tool="Ring2", when="on_Sa", name="Ball_Sa")
cmd("feature.sphere", radius="R_Mo", when="moon", name="Ball_Mo",
    position=["rP_Ea * cos(th_Ea) + ell * cos(thMo)", "rP_Ea * sin(th_Ea) + ell * sin(thMo)", "H"])
for k in ORBITS + ["Mo"]:
    look("Ball_" + k, COLOUR[k])


# ---------------------------------------------------------------- what the model is checked by

GEARS = ["A_" + k for k in KEYS] + ["B_" + k for k in KEYS] + ["C_" + k for k in KEYS] + ["D_" + k for k in KEYS] \
    + ["Gc", "Gp"] + ["Idler%d" % j for j in range(1, MAX_IDL + 1)]
cmd("set.define", name="Input gears", kind="body", where={"name": "A_*"})
cmd("set.define", name="Lay gears", kind="body", where={"any": [{"name": "B_*"}, {"name": "C_*"}]})
cmd("set.define", name="Tube gears", kind="body", where={"name": "D_*"})
cmd("set.define", name="Train gears", kind="body",
    where={"any": [{"set": "Input gears"}, {"set": "Lay gears"}, {"set": "Tube gears"}]})
cmd("set.define", name="Gears", kind="body", where={"any": [{"set": "Train gears"}, {"name": "Gc"}, {"name": "Idler*"},
                                                             {"name": "Gp"}]})
# The Moon's gears with the centre post, which they clear, so that the set is never empty (an assertion on
# an empty set is in error).
cmd("set.define", name="Moon gears", kind="body",
    where={"any": [{"name": "Gc"}, {"name": "Idler*"}, {"name": "Gp"}, {"name": "CentrePost"}]})
cmd("set.define", name="Tubes", kind="body", where={"any": [{"name": "CentrePost"}, {"name": "Tube_*"}]})
cmd("set.define", name="Balls", kind="body", where={"any": [{"name": "Sun"}, {"name": "Ball_*"}]})
# Cut sheets for a laser, one per thickness: every gear's outline (its underside; in the SVG or DXF each
# is on a layer named after the gear, A_Me ...), and the two plates.
cmd("set.define", name="Cut sheet: gears", kind="face",
    where={"any": [{"in": gname, "normal": {"along": "-z"}} for gname in GEARS]})
cmd("set.define", name="Cut sheet: plates", kind="face",
    where={"any": [{"in": p, "normal": {"along": "-z"}} for p in ("BasePlate", "BridgePlate")]})

# The trains, from the teeth alone (not from S12, S2 or the ratios the geometry uses).
mesh = []
accs = []
teeth = []
for k in KEYS:
    var("prod_" + k, "zA_{k} * zC_{k} / (zB_{k} * zD_{k})".format(k=k))
    var("T_" + k, "%r" % PER[k])
    var("Tm_" + k, "year / prod_" + k)                          # the period the gears make, days
    var("err_" + k, "(Tm_%s / T_%s - 1) * 1e6" % (k, k))          # ppm
    var("dT_" + k, "Tm_%s - T_%s" % (k, k))                       # days per orbit
    mesh.append("(!on_{k} || (zA_{k} + zB_{k} == S12 && zC_{k} + zD_{k} == S2))".format(k=k))
    accs.append("(!on_{k} || abs(err_{k}) <= targets[acc].ppm)".format(k=k))
    teeth.append("(!on_{k} || (min(min(zA_{k}, zB_{k}), min(zC_{k}, zD_{k})) >= 12 && "
                 "max(max(zA_{k}, zB_{k}), max(zC_{k}, zD_{k})) <= maxTeeth))".format(k=k))
var("meshOK", " && ".join(mesh))
var("accOK", " && ".join(accs))
var("teethOK", " && ".join(teeth) + " && (!moon || (zc >= 12 && zI >= 12 && zc <= maxTeeth && zI <= maxTeeth))")
gears = {"kind": "body", "where": {"set": "Gears"}}
cmd("assert.add", name="Each stage meshes on its shafts' centre distance: zA + zB = S12, zC + zD = S2",
    measure="count", of=gears, eq="if(meshOK, nGears, 0)")
cmd("assert.add", name="Each train's period within the accuracy target",
    measure="count", of=gears, eq="if(accOK, nGears, 0)")
cmd("assert.add", name="Every gear has 12 to maxTeeth teeth",
    measure="count", of=gears, eq="if(teethOK, nGears, 0)")
# Where the gears are: on the centre post, on the lay shaft at the stage-2 centre distance, on the input
# shaft at the stage-1 centre distance from the lay shaft (from Mercury's teeth; the check above makes
# every train's sums equal to Mercury's).
var("s1x", "mn * (zA_Me + zB_Me) / 2")
var("s2x", "mn * (zC_Me + zD_Me) / 2")
var("xAx", "(d1^2 - s1x^2 + s2x^2) / (2 * s2x)")
var("yAx", "-sqrt(max(0 * (1 mm)^2, d1^2 - xAx^2))")
for setname, ex, ey in (("Tube gears", "0 mm", "0 mm"), ("Lay gears", "s2x", "0 mm"), ("Input gears", "xAx", "yAx")):
    for ax, e in (("x", ex), ("y", ey)):
        cmd("assert.add", name="%s on their axis (%s)" % (setname, ax), measure="centerOfMass",
            of={"kind": "body", "where": {"set": setname}}, axis=ax, eq=e, tol="0.001 mm")
# No two parts overlap: every pair of bodies, in groups (an overlap assertion takes at most 500 pairs).
cmd("set.define", name="Shafts and tubes", kind="body",
    where={"any": [{"set": "Tubes"}, {"name": "LayShaft"}, {"name": "InputShaft"}]})
cmd("set.define", name="Frame", kind="body",
    where={"any": [{"name": "BasePlate"}, {"name": "BridgePlate"}, {"name": "Pillar*"}]})
cmd("set.define", name="Washers and spacers", kind="body", where={"any": [{"name": "Washer_*"}, {"name": "Spacer_*"}]})
cmd("set.define", name="Arms and balls", kind="body",
    where={"any": [{"name": "Arm_*"}, {"name": "MoonCarrier"}, {"set": "Balls"}]})
Q = lambda name: {"kind": "body", "where": {"set": name}}  # noqa: E731
for label, of, to in (("train gears", "Train gears", None), ("Moon gears", "Moon gears", None),
                      ("train gears and Moon gears", "Train gears", "Moon gears"),
                      ("gears and shafts or tubes", "Gears", "Shafts and tubes"),
                      ("gears and washers or spacers", "Gears", "Washers and spacers"),
                      ("gears and the frame", "Gears", "Frame"),
                      ("shafts, tubes, washers, spacers and the frame", None, None),
                      ("arms and balls", "Arms and balls", None),
                      ("arms or balls and shafts or tubes", "Arms and balls", "Shafts and tubes"),
                      ("arms or balls and washers or spacers", "Arms and balls", "Washers and spacers"),
                      ("arms or balls and train gears", "Arms and balls", "Train gears"),
                      ("arms or balls and Moon gears", "Arms and balls", "Moon gears"),
                      ("arms or balls and the frame", "Arms and balls", "Frame")):
    p = {"name": "No overlap: " + label + " (at the current crank angle)", "measure": "overlap", "is": False}
    if of is None:
        p["of"] = {"kind": "body", "where": {"any": [{"set": "Shafts and tubes"}, {"set": "Washers and spacers"},
                                                     {"set": "Frame"}]}}
    else:
        p["of"] = Q(of)
    if to:
        p["to"] = Q(to)
    cmd("assert.add", **p)
cmd("assert.add", name="Tubes nest with running clearance", measure="clearance",
    **{"from": {"kind": "body", "where": {"set": "Tubes"}}, "to": {"kind": "body", "where": {"set": "Tubes"}}},
    min="0.2 * clr")
# Every shaft held at both ends: the input shaft runs in a hole of both plates, the lay shaft and the
# centre post are fitted in the base plate, the lay shaft in the bridge too, and the bridge's hole holds
# the outermost tube (and with it the tubes inside it and the centre post) at the top.
for shaft, plate, gap in (("InputShaft", "BasePlate", "clr"), ("InputShaft", "BridgePlate", "clr"),
                          ("LayShaft", "BasePlate", "fit"), ("LayShaft", "BridgePlate", "fit"),
                          ("CentrePost", "BasePlate", "fit")):
    cmd("assert.add", name="%s held in the %s" % (shaft, plate), measure="clearance", **{"from": shaft, "to": plate},
        max="%s + 0.005 mm" % gap)
cmd("assert.add", name="The tubes held in the BridgePlate", measure="clearance",
    **{"from": {"kind": "body", "where": {"set": "Tubes"}}, "to": "BridgePlate"}, max="clr + 0.005 mm")
cmd("assert.add", name="The shafts reach through the bridge", measure="boxMax", axis="z",
    of=["LayShaft", "InputShaft"], min="zBr + tPlate")
# Headroom over the crank: its top at least 40 mm below the lowest arm.
cmd("assert.add", name="Crank headroom: the crank's top", measure="boxMax", axis="z", of="InputShaft",
    max="zArm0 - 40 mm")
cmd("assert.add", name="Crank headroom: the lowest arm or Moon gear", measure="boxMin", axis="z",
    of={"kind": "body", "where": {"any": [{"set": "Arms and balls"}, {"name": "Gc"}, {"name": "Idler*"},
                                          {"name": "Gp"}]}}, min="zArm0 - 0.001 mm")
# The arms, posts and balls of neighbouring orbits apart at any angle: each body's reach (ball, arm end,
# Saturn's ring, the Earth's Moon and its gears) stays within its ring of radii.
apart = ["rP_Me - e_Me >= Rsun + 2 mm"]
prev = "Me"
for k in ORBITS[1:]:
    apart.append("(!on_{k} || rP_{k} - e_{k} - rP_{p} - e_{p} >= gapO - 0.001 mm)".format(k=k, p=prev))
    prev = k
var("apartOK", " && ".join(apart) + " && lcr >= 10 mm")
cmd("assert.add", name="Neighbouring orbits apart at every angle, the crank clear of the tubes",
    measure="count", of={"kind": "body", "where": {"set": "Balls"}}, eq="if(apartOK, n + 1, 0)")
# Each ball where its gear train puts it, and within the accuracy target of the real body's mean
# longitude on that day. Measured as the centre of mass of the ball and the Sun (the Sun at the origin,
# so a body that is not built leaves the Sun's 0).
var("V_Sun", "4 / 3 * pi * Rsun^3")
for k in ORBITS + ["Mo"]:
    if k == "Sa":
        var("V_Sa", "4 / 3 * pi * R_Sa^3 + pi * (RING * R_Sa)^2 * 0.8 mm - pi * (R_Sa^2 * 0.8 mm - (0.8 mm)^3 / 12)")
    else:
        var("V_" + k, "4 / 3 * pi * R_%s^3" % k)
    var("w_" + k, "V_%s / (V_%s + V_Sun)" % (k, k))
for k in ORBITS:
    var("aP_" + k, "L0_%s + crank * prod_%s" % (k, k))
    var("aR_" + k, "L0_%s + 360 deg * days / T_%s" % (k, k))
    var("dA_" + k, "2 * pi * abs(days) / T_%s * targets[acc].ppm * 1.01e-6" % k)
    for ax, f in (("x", "cos"), ("y", "sin")):
        var("p%s_%s" % (ax, k), "rP_%s * %s(aP_%s)" % (k, f, k))
        var("q%s_%s" % (ax, k), "rP_%s * %s(aR_%s)" % (k, f, k))
var("aP_Mo", "L0_Mo + crank * prod_Mo")
var("aR_Mo", "L0_Mo + 360 deg * days / T_Mo")
var("dA_Mo", "2 * pi * abs(days) / T_Mo * targets[acc].ppm * 1.01e-6")
for ax, f in (("x", "cos"), ("y", "sin")):
    var("p%s_Mo" % ax, "p%s_Ea + ell * %s(aP_Mo)" % (ax, f))
    var("q%s_Mo" % ax, "q%s_Ea + ell * %s(aR_Mo)" % (ax, f))
for k in ORBITS + ["Mo"]:
    reach = "rP_Ea * dA_Ea + ell * dA_Mo" if k == "Mo" else "rP_%s * dA_%s" % (k, k)
    pair = {"kind": "body", "where": {"any": [{"name": "Ball_" + k}, {"name": "Sun"}]}}
    for ax in ("x", "y"):
        cmd("assert.add", name="%s follows its gears (%s)" % (NAME[k], ax), measure="centerOfMass", of=pair, axis=ax,
            eq="if(on_%s, w_%s * p%s_%s, 0 mm)" % (k, k, ax, k), tol="0.001 mm")
        cmd("assert.add", name="%s within the accuracy target of its real place (%s)" % (NAME[k], ax),
            measure="centerOfMass", of=pair, axis=ax, eq="if(on_%s, w_%s * q%s_%s, 0 mm)" % (k, k, ax, k),
            tol="w_%s * (%s) + 0.001 mm" % (k, reach))

# ---------------------------------------------------------------- parameters

NTG = len(TARGETS)
# (A parameter's range cannot look a table up itself yet: through a variable.)
var("zLeast", "zlim[(pset - 1) * %d + moon * %d + acc].zmin" % (2 * NTG, NTG))
params = [
    dict(name="pset", label="Planets", group="Planets", order=1, kind="choice", choicesFrom="planetSets",
         description="Which planets the orrery shows, from the Sun out: the inner planets to the Earth, to Mars, "
                     "to Jupiter or to Saturn (the planets known before 1781)"),
    dict(name="moon", label="Moon", group="Planets", order=2, kind="boolean",
         description="The Moon round the Earth, driven by its own train (sidereal month) and an idler under the "
                     "Earth's arm, so it keeps its direction in space as the Earth goes round"),
    dict(name="acc", label="Accuracy target", group="Gear trains", order=1, kind="choice", choicesFrom="targets",
         description="The largest error of any body's period. The smallest gearbox whose trains all meet it is "
                     "chosen (a tighter target needs more teeth)"),
    dict(name="maxTeeth", label="Most teeth per gear", group="Gear trains", order=2, kind="integer",
         min="zLeast", max="120", step="10",
         description="The largest gear the trains may use (60 to 120). Its least value is the least that meets "
                     "the accuracy target for these planets: 120 for Mercury to Saturn with the Moon at 0.03 %, "
                     "the default"),
    dict(name="moduleSize", label="Module", group="Gear trains", order=3, kind="choice", choicesFrom="modules",
         description="Tooth size of every gear: pitch diameter = module x teeth. The whole gearbox scales with it"),
    dict(name="material", label="Gears made by", group="Gear trains", order=4, kind="choice", choicesFrom="materials",
         description="3D printed gears 4 mm thick, or laser-cut from 3 mm acrylic or 4 mm plywood (the named "
                     "face sets Cut sheet: gears and Cut sheet: plates lay them out for the laser)"),
    dict(name="rIn", label="Mercury's arm (at module 1)", group="Arms", order=1,
         min="(Rsun + e_Me + 2 mm) / (mn / 1 mm)", max="90 mm", step="1 mm", unit="mm",
         description="Radius of Mercury's orbit at module 1; it grows with the module, as the gearbox does. The "
                     "others follow outwards; not to scale (see the README)"),
    dict(name="gapO", label="Gap between orbits", group="Arms", order=2, min="3 mm", max="20 mm", step="0.5 mm",
         unit="mm", description="Least room between the balls, arms and pins of neighbouring orbits"),
    dict(name="size", label="Ball size", group="Arms", order=3, min="0.6", max="1.8", step="0.05",
         description="Scale of the Sun and the planets (the Sun 24 mm across at 1); ordered by size, not to scale"),
    dict(name="days", label="Days since 1 Jan 2000", group="Crank", order=1, min="-36525", max="36525", step="1",
         description="Turn the crank: one turn is one sidereal year (365.256 days). Day 0 is 1 January 2000, "
                     "12:00 TT (J2000), with every body at its mean longitude then; -36525 is 1900, 36525 is 2100"),
]
for p in params:
    cmd("variable.publish", **p)
cmd("document.info",
    title="Geared orrery",
    description="A hand-cranked orrery: the Sun, Mercury to Saturn on nested tubes, the Moon round the Earth "
                "as an option, each driven from one crank through two gear stages whose tooth counts were "
                "searched so its period matches the real sidereal period within the accuracy target (one crank "
                "turn is one year). Choose the planets, the target, the most teeth per gear, the module, printed "
                "or laser-cut gears and the arms; turn the date and every ball moves to its place by its gears. "
                "Involute teeth (20 deg), assertions on the trains, the meshing, the clearances and the planets' "
                "places. Two cut sheets (gears, plates) for a laser.",
    author="3DCraft Jigs", licence="CC-BY-4.0",
    url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/orrery",
    tags=["orrery", "planetarium", "astronomy", "gear", "gear train", "involute", "mechanism", "3D printing",
          "laser cutting"])
cmd("jig.export", path="dist/orrery.3dcraftjig")


def flank():
    """python3 gen.py --flank: how far the flank arc lies from the involute, over the involute's part of
    the flank (from rs to the tip), for 12 to 150 teeth, in modules: + where the tooth is thicker."""
    al = math.radians(20)
    lo, hi = 0.0, 0.0
    for z in range(12, 151):
        r = z / 2
        rb, ra, rf = r * math.cos(al), r + 1, r - 1.25
        g = -math.pi / (2 * z) - (math.tan(al) - al)
        rs = max(rb, rf + 0.1)
        t0, ta = math.sqrt((rs / rb) ** 2 - 1), math.sqrt((ra / rb) ** 2 - 1)
        tm = math.sqrt((1 - W_MID) * t0 * t0 + W_MID * ta * ta)

        def inv(t):
            return rb * (math.cos(g + t) + t * math.sin(g + t)), rb * (math.sin(g + t) - t * math.cos(g + t))
        phis = g + t0 - math.atan(t0)
        (ax, ay), (bx, by), (cx, cy) = (rf * math.cos(phis), rf * math.sin(phis)), inv(tm), inv(ta)
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        R = math.hypot(ax - ux, ay - uy)
        for k in range(1, 400):
            x, y = inv(t0 + (ta - t0) * k / 400)
            rho, th = math.hypot(x, y), math.atan2(y, x)
            dd = math.hypot(ux, uy)
            a = (rho * rho - R * R + dd * dd) / (2 * dd)
            h = math.sqrt(max(0.0, rho * rho - a * a))
            px, py = ux * a / dd, uy * a / dd
            cands = [(px - h * uy / dd, py + h * ux / dd), (px + h * uy / dd, py - h * ux / dd)]
            tha = min((math.atan2(q[1], q[0]) for q in cands), key=lambda q: abs(q - th))
            dev = (th - tha) * rho
            lo, hi = min(lo, dev), max(hi, dev)
    print("flank arc from the involute: %.4f to +%.4f module (+: tooth thicker)" % (lo, hi))


def table():
    """python3 gen.py --table [set moon maxTeeth target]: the trains of a row, for the README."""
    a = [int(x) for x in sys.argv[2:6]] if len(sys.argv) >= 6 else [4, 1, 120, len(TARGETS)]
    for s_, moon, Z, ti, r in ROWS:
        if [s_, moon, Z, ti] != a:
            continue
        worst, S12, S2, sol = r
        print("S12 = %d, S2 = %d (stage 1 at %g modules, stage 2 at %g modules), worst %.0f ppm"
              % (S12, S2, S12 / 2, S2 / 2, worst * 1e6))
        print("| Body | A | B | C | D | Turns per year | Period built | Real period | Error |")
        print("|---|---|---|---|---|---|---|---|---|")
        for k in KEYS:
            if k not in sol:
                continue
            _, za, zb, zc, zd = sol[k]
            ratio = za * zc / (zb * zd)
            tm = trains.YEAR / ratio
            print("| %s | %d | %d | %d | %d | %.6f | %.4f d | %s d | %+.0f ppm (%+.4f d per orbit) |"
                  % (NAME[k], za, zb, zc, zd, ratio, tm, PER[k], (tm / PER[k] - 1) * 1e6, tm - PER[k]))


def sweep():
    """python3 gen.py --sweep: every row the form can reach, at every module: the input shaft's triangle
    closes, every gear clears the tubes and spindles it passes, the crank clears the tubes."""
    bad = 0
    for s_, moon, Z, ti, r in ROWS:
        worst, S12, S2, sol = r
        keys = trains.enabled(s_, moon)
        for _, mn in MODULES:
            a2, d12 = mn * S2 / 2, mn * S12 / 2
            req = 0
            for k_i, k in enumerate(keys, start=1):
                _, za, zb, zc, zd = sol[k]
                ra = lambda z: mn * (z / 2 + 1)  # noqa: E731
                rf = lambda z: mn * (z / 2 - 1.25)  # noqa: E731
                tout = trains.tube_out(k_i)
                req = max(req, ra(za) + tout + trains.GAP, ra(zd) + trains.R_SHAFT + trains.GAP)
                ok = (a2 - ra(zb) >= tout + trains.GAP and d12 - ra(zc) >= trains.R_SHAFT + trains.GAP
                      and rf(zd) >= tout + trains.FIT + trains.RIM - 1e-9 and rf(za) >= trains.R_SHAFT + trains.RIM
                      and min(rf(zb), rf(zc)) - 1 >= trains.R_SHAFT + trains.CLR + 1)
                if not ok:
                    bad += 1
                    print("gear clearance", s_, moon, Z, ti, mn, k)
            d1 = min(d12 + a2, max(req, math.hypot(d12, a2)))
            if req > d12 + a2 + 1e-9:
                bad += 1
                print("triangle", s_, moon, Z, ti, mn)
            n = len(keys)
            if d1 - (trains.tube_out(n)) - 4 < 10:
                bad += 1
                print("crank", s_, moon, Z, ti, mn)
    print("%d rows x %d modules, %d failing" % (len(ROWS), len(MODULES), bad), file=sys.stderr)
    return bad == 0


if "--flank" in sys.argv:
    flank()
    sys.exit(0)
if "--table" in sys.argv:
    table()
    sys.exit(0)
if "--sweep" in sys.argv:
    sys.exit(0 if sweep() else 1)
print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
