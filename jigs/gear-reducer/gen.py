#!/usr/bin/env python3
"""Writes build.json of the gear-reducer Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written. Adapted from the generators of the
3DCraft test drive of 2026-10-25 (a two-stage reducer built headless with commands only): the same
tables, shafts, keys, bearings, housing and assertions, with the gears drawn as the spur-gear Jig draws
them and the shaft diameters, the housing and the ranges made to follow the gears.

Coordinates: the shafts stand along z, the input shaft on the z axis, the intermediate and the output
shaft along +x; stage 1 (pinion 1, wheel 2) lies on z >= 0, stage 2 (pinion 3, wheel 4) above it. The
housing is split along the plane y = 0 into a rear half (y > 0) and a front half (y < 0).
"""
import json
import math
import sys

# ---------------------------------------------------------------- data

# ISO 54 modules (first and second series, the range this Jig offers).
MODULES = [("1 mm", 1), ("1.25 mm", 1.25), ("1.5 mm", 1.5), ("2 mm", 2), ("2.5 mm", 2.5), ("3 mm", 3), ("4 mm", 4)]
DEFAULT_MODULE = 3  # 1.5 mm
# DIN 6885-1 form A parallel keys by shaft diameter: width b, height h, depth in the shaft t1, in the hub t2.
KEYS = [("6-8", 2, 2, 1.2, 1.0), ("8-10", 3, 3, 1.8, 1.4), ("10-12", 4, 4, 2.5, 1.8), ("12-17", 5, 5, 3.0, 2.3),
        ("17-22", 6, 6, 3.5, 2.8), ("22-30", 8, 7, 4.0, 3.3), ("30-38", 10, 8, 5.0, 3.3), ("38-44", 12, 8, 5.0, 3.3),
        ("44-50", 14, 9, 5.5, 3.8)]
KEY_ROW = "1 + ({d} > 8 mm) + ({d} > 10 mm) + ({d} > 12 mm) + ({d} > 17 mm) + ({d} > 22 mm) + ({d} > 30 mm)" \
          " + ({d} > 38 mm) + ({d} > 44 mm)"
# ISO 15 deep-groove ball bearings, series 60 and 62: bore d, outside diameter D and width B.
BEARINGS = [("00", 10, 26, 8, 30, 9), ("01", 12, 28, 8, 32, 10), ("02", 15, 32, 9, 35, 11), ("03", 17, 35, 10, 40, 12),
            ("04", 20, 42, 12, 47, 14), ("05", 25, 47, 12, 52, 15), ("06", 30, 55, 13, 62, 16)]
# The bearing row under a gear seat: the largest bore below the seat (a seat of 17 mm or more may take
# a bearing of its own diameter, the gears then going on from the other end).
BRG_ROW = "1 + ({s} >= 14 mm) + ({s} >= 17 mm) + ({s} >= 19 mm) + ({s} >= 22 mm) + ({s} >= 27 mm) + ({s} >= 32 mm)"
# Standard shaft diameters the gear seats are chosen from, with the hub keyway depth t2 of each.
SHAFTS = [10, 12, 15, 17, 20, 25, 30, 35, 40]


def brg_row(d):
    return 1 + sum(d >= x for x in (14, 17, 19, 22, 27, 32))


def t2_of(d):
    row = 1 + sum(d > x for x in (8, 10, 12, 17, 22, 30, 38, 44))
    return KEYS[row - 1][4]


# Shared Jig palette.
STEEL = {"color": "#7D858C", "metallic": 0.85, "roughness": 0.4}
BRASS = {"color": "#B8954A", "metallic": 0.9, "roughness": 0.35}
ALU = {"color": "#B9BEC4", "metallic": 0.9, "roughness": 0.25}
SLATE = {"color": "#5B7299", "metallic": 0.3, "roughness": 0.5}
DARK = {"color": "#4A4F55", "metallic": 0.7, "roughness": 0.4}

# ---------------------------------------------------------------- helpers

steps = []
fid = [0]


def cmd(c, **p):
    """Appends a command; returns the id the feature it makes will get (sketches count)."""
    steps.append([c, p])
    if c == "sketch.create" or (c.startswith("feature.") and c not in ("feature.when", "feature.rename",
                                                                         "feature.visible")):
        fid[0] += 1
        return "F%d" % fid[0]
    return None


def var(name, expr):
    cmd("variable.set", name=name, expr=expr)


def look(body, colour, material, density):
    cmd("body.appearance", body=body, **colour)
    cmd("body.material", body=body, name=material, density=density)


# ---------------------------------------------------------------- tables and inputs

cmd("table.set", name="iso54", columns=["module", {"name": "mn", "unit": "mm"}], rows=[list(r) for r in MODULES])
cmd("table.set", name="din6885", columns=["shaft", {"name": "kb", "unit": "mm"}, {"name": "kh", "unit": "mm"},
                                          {"name": "t1", "unit": "mm"}, {"name": "t2", "unit": "mm"}],
    rows=[list(r) for r in KEYS])
cmd("table.set", name="brg", columns=["bore", {"name": "d", "unit": "mm"}, {"name": "D60", "unit": "mm"},
                                      {"name": "B60", "unit": "mm"}, {"name": "D62", "unit": "mm"},
                                      {"name": "B62", "unit": "mm"}],
    rows=[list(r) for r in BEARINGS])
cmd("table.set", name="series", columns=["series"], rows=[["60xx (light)"], ["62xx (medium)"]])
cmd("table.set", name="shafts", columns=["shaft", {"name": "d", "unit": "mm"}],
    rows=[["%d mm" % d, d] for d in SHAFTS])
cmd("table.set", name="steps", columns=["step"], rows=[["same as stage 1"], ["one size up"], ["two sizes up"]])

for name, expr in (
        # public inputs
        ("i_total", "10"), ("z_1", "18"), ("z_3", "17"), ("mi_1", str(DEFAULT_MODULE)), ("up_2", "3"),
        ("b_1", "14 mm"), ("b_3", "20 mm"), ("ser", "2"), ("c_w", "5 mm"), ("t_w", "6 mm"), ("theta_in", "0 deg"),
        # fixed design values
        ("alpha", "20 deg"),       # ISO 53 pressure angle
        ("jt", "0.12 mm"),         # circumferential backlash per mesh, on the pitch circle
        ("hub_l", "10 mm"),        # hub length of every gear
        ("s_gap", "5 mm"),         # bearing to cavity
        ("st_gap", "4 mm"),        # between the stages along the shafts
        ("ext_len", "30 mm"),      # input and output shaft ends outside the housing
        ("fit_cl", "0.01 mm"),     # radial fit of bores, keys and seats (makes the touching pairs decidable)
        ("rim_k", "2.5"),          # rim under a hub keyway, in modules
        # the ratio split: stage 1 takes 1.1 sqrt(i)
        ("i_1", "round(1.1 * sqrt(i_total), 0.01)"),
        ("mn_1", "iso54[mi_1].mn"),
        ("mi_2", "min(mi_1 + up_2 - 1, %d)" % len(MODULES)),
        ("mn_3", "iso54[mi_2].mn")):
    var(name, expr)

# ---------------------------------------------------------------- gear sizes


def gear_vars(s, mn, width, z):
    """Variables of gear s: module, width, teeth, circles and the involute outline (as the spur-gear Jig)."""
    for name, expr in (
            ("mn", mn), ("b", width), ("z", z),
            ("r", "mn@ * z@ / 2"),
            ("rb", "r@ * cos(alpha)"),
            ("ra", "r@ + mn@"),
            ("rf", "r@ - 1.25 * mn@"),
            # The flank turned so that a tooth is symmetric about +x, thinned by jt / 4 on each flank.
            ("g", "-pi / (2 * z@) - (tan(alpha) - alpha / 1 rad) + jt / (4 * r@)"),
            ("rs", "max(rb@, rf@ + 0.1 * mn@)"),
            ("t0", "sqrt((rs@ / rb@)^2 - 1)"),
            ("ta", "sqrt((ra@ / rb@)^2 - 1)"),
            ("phis", "g@ + t0@ - atan(t0@) / 1 rad"),
            ("half", "pi / z@"),
            ("thetaA", "g@ + ta@ - atan(ta@) / 1 rad")):
        if expr != name + s:
            var(name + s, expr.replace("@", s))


def fits(g):
    """How many standard shaft diameters gear g holds with its keyway and a rim of rim_k modules."""
    return " + ".join("(%g mm <= rf%s - rim_k * mn%s)" % (d / 2 + t2_of(d), g, g) for d in SHAFTS)


gear_vars("_1", "mn_1", "b_1", "z_1")
var("z_2", "round(z_1 * i_1)")
gear_vars("_2", "mn_1", "b_1", "z_2")
var("a12", "mn_1 * (z_1 + z_2) / 2")
gear_vars("_3", "mn_3", "b_3", "z_3")
var("z_4", "round(z_3 * i_total * z_1 / z_2)")
gear_vars("_4", "mn_3", "b_3", "z_4")
var("a34", "mn_3 * (z_3 + z_4) / 2")
var("i_actual", "z_2 / z_1 * z_4 / z_3")

# Shaft diameters: the largest standard one each gear holds; the intermediate shaft the smaller of its
# two gears', the input shaft no larger than it, the output shaft at most two sizes larger.
for g in ("_1", "_2", "_3", "_4"):
    var("nfit" + g, fits(g))
# The intermediate shaft's bearing must also fit beside the input shaft's (as large as pinion 1 allows).
var("ji_cap1", BRG_ROW.format(s="shafts[max(1, nfit_1)].d"))
var("brg_Dcap1", "if(ser == 1, brg[ji_cap1].D60, brg[ji_cap1].D62)")
var("nfit_b", " + ".join("(if(ser == 1, %g mm, %g mm) / 2 + brg_Dcap1 / 2 + 2 mm <= a12)"
                         % (BEARINGS[brg_row(d) - 1][2], BEARINGS[brg_row(d) - 1][4], ) for d in SHAFTS))
var("ix_s2", "max(1, min(min(nfit_2, nfit_3), nfit_b))")
var("ix_s1", "max(1, min(nfit_1, ix_s2))")
var("ix_s3", "max(1, min(nfit_4, ix_s2 + 2))")
var("d_s1", "shafts[ix_s1].d")
var("d_s2", "shafts[ix_s2].d")
var("d_s3", "shafts[ix_s3].d")
# The bounds the tooth ranges use, independent of z_3: the input shaft is at most what pinion 1 holds,
# the output shaft at most two sizes over the intermediate one's bound.
var("d_cap1", "shafts[max(1, nfit_1)].d")
# Pinion 3 at most z3_hi teeth (it must clear the input shaft's spacer), so the shafts it sets are at most
# what such a pinion holds.
var("z3_hi", "min(40, floor(2 * ((a12 - d_cap1 / 2 - 4 mm) / mn_3 - 1)))")
var("nfit_3hi", fits("_3").replace("rf_3", "(mn_3 * (z3_hi / 2 - 1.25))"))
var("d_cap3", "shafts[min(max(1, min(min(nfit_2, nfit_3hi), nfit_b)) + 2, %d)].d" % len(SHAFTS))
var("i_2n", "i_total * z_1 / z_2")

GEAR_SHAFT = {"_1": "d_s1", "_2": "d_s2", "_3": "d_s2", "_4": "d_s3"}
for g, d in GEAR_SHAFT.items():
    var("d_bore" + g, d)
    var("hub_d" + g, "min(2 * d_bore@ + 6 mm, 2 * rf@ - 2 * mn@)".replace("@", g))
    var("ki" + g, KEY_ROW.format(d="d_bore" + g))
    for col in ("kb", "kh", "t1", "t2"):
        var("key_%s%s" % (col, g), "din6885[ki%s].%s" % (g, col))

# Bearings per shaft from its seat.
for s in ("_s1", "_s2", "_s3"):
    var("seat" + s, "d" + s)
    var("ji" + s, BRG_ROW.format(s="seat" + s))
    var("brg_d" + s, "brg[ji%s].d" % s)
    var("brg_D" + s, "if(ser == 1, brg[ji@].D60, brg[ji@].D62)".replace("@", s))
    var("brg_B" + s, "if(ser == 1, brg[ji@].B60, brg[ji@].B62)".replace("@", s))
    var("zA0" + s, "-s_gap - brg_B" + s)
    var("d_ext" + s, "brg_d%s - 2 mm" % s)
    var("collar_d" + s, "seat%s + 5 mm" % s)
    var("t_ringA" + s, "(brg_D@ - brg_d@) * 0.28".replace("@", s))
    var("t_ringB" + s, "(brg_D@ - brg_d@) * 0.28".replace("@", s))

var("z2_0", "b_1 + hub_l + st_gap")
var("zB0", "z2_0 + b_3 + hub_l + s_gap")
# The poses: pinion 1 turns with the input angle, the others follow; an even wheel turns half a pitch so
# a gap faces its pinion's tooth.
var("w2", "if(mod(z_2, 2) == 0, 180 deg / z_2, 0 deg) - theta_in * z_1 / z_2")
var("w4", "if(mod(z_4, 2) == 0, 180 deg / z_4, 0 deg) + theta_in * z_1 * z_3 / (z_2 * z_4)")
var("ph3", "-if(mod(z_2, 2) == 0, 180 deg / z_2, 0 deg)")

# ---------------------------------------------------------------- gears


def gear_geom(s, place_angle, x, zoff, colour, tooth_turn=None):
    v = lambda e: e.replace("@", s)
    sk = "Outline" + s
    cmd("sketch.create", name=sk, plane="xy")
    cmd("sketch.point", sketch=sk, at=[v("rf@ * cos(phis@ * 1 rad)"), v("rf@ * sin(phis@ * 1 rad)")])
    cmd("sketch.curve", sketch=sk, x=v("rb@ * (cos(g@ + t) + t * sin(g@ + t))"),
        y=v("rb@ * (sin(g@ + t) - t * cos(g@ + t))"), t=[v("t0@"), v("ta@")])
    cmd("sketch.curve", sketch=sk, x=v("rb@ * (cos(g@ + t) + t * sin(g@ + t))"),
        y=v("-rb@ * (sin(g@ + t) - t * cos(g@ + t))"), t=[v("t0@"), v("ta@")])
    cmd("sketch.curve", sketch=sk, x=v("ra@ * cos(t)"), y=v("ra@ * sin(t)"), t=[v("thetaA@"), v("-thetaA@")],
        start="e3", end="e6")
    cmd("sketch.curve", sketch=sk, x=v("rf@ * cos(t)"), y=v("rf@ * sin(t)"), t=[v("-phis@"), v("2 * half@ + phis@")])
    cmd("sketch.line", sketch=sk, **{"from": "e1", "to": "e2"})
    cmd("sketch.line", sketch=sk, **{"from": "e5", "to": "e9"})
    cmd("sketch.pattern", sketch=sk, entities=["e12", "e4", "e8", "e7", "e13", "e11"], chain=["e1", "e10"],
        angle=v("360 deg / z@"), center=["0 mm", "0 mm"], count=v("z@"))
    cmd("feature.extrude", sketch=sk, distance=v("b@"), name="Rim" + s)
    rim = "Rim" + s
    if tooth_turn:
        cmd("feature.transform", source=rim, angle=tooth_turn, axis=[0, 0, 1], name="RimT" + s)
        rim = "RimT" + s
    cmd("feature.cylinder", radius=v("hub_d@ / 2"), height="hub_l", position=[0, 0, v("b@")], name="Hub" + s)
    cmd("feature.boolean", op="union", target=rim, tool="Hub" + s, name="GearHub" + s)
    cmd("feature.cylinder", radius=v("d_bore@ / 2 + fit_cl / 2"), height=v("b@ + hub_l + 2 mm"),
        position=[0, 0, "-1 mm"], name="Bore" + s)
    cmd("feature.block", size=[v("d_bore@ / 2 + key_t2@"), v("key_kb@"), v("b@ + hub_l + 2 mm")],
        position=[0, v("-key_kb@ / 2"), "-1 mm"], name="Key" + s)
    cmd("feature.boolean", op="union", target="Bore" + s, tool="Key" + s, name="BoreKey" + s)
    cmd("feature.boolean", op="subtract", target="GearHub" + s, tool="BoreKey" + s, name="GearLocal" + s)
    cmd("feature.transform", source="GearLocal" + s, angle=place_angle, axis=[0, 0, 1], translate=[x, 0, zoff],
        name="Gear" + s)
    look("Gear" + s, colour, "Steel 42CrMo4", "7.85 g/cm3")


gear_geom("_1", "theta_in", 0, 0, STEEL)
gear_geom("_2", "w2", "a12", 0, BRASS)
gear_geom("_3", "w2", "a12", "z2_0", STEEL, tooth_turn="ph3")
gear_geom("_4", "w4", "a12 + a34", "z2_0", BRASS)

# ---------------------------------------------------------------- shafts, keys, spacers, bearings


def shaft_geom(s, segs, place_angle, x, keyed, spacers):
    """segs: (z_start, z_end, radius) bottom to top; keyed: (gear, z0, z1) keyway ranges; spacers:
    (name, z0, z1, inner radius) sleeves."""
    sk = "S_shaft" + s
    cmd("sketch.create", plane="zx", name=sk)
    pts = [[segs[0][0], "0 mm"]]
    for z0, z1, r in segs:
        pts.append([z0, r])
        pts.append([z1, r])
    pts.append([segs[-1][1], "0 mm"])
    clean = [pts[0]]
    for p in pts[1:]:
        if p != clean[-1]:
            clean.append(p)
    cmd("sketch.polyline", sketch=sk, points=clean, closed=True)
    cmd("feature.revolve", sketch=sk, axis="x", name="ShaftRaw" + s)
    prev = "ShaftRaw" + s
    for gi, (g, z0, z1) in enumerate(keyed):
        kb, kh, t1, d = "key_kb" + g, "key_kh" + g, "key_t1" + g, "d_bore" + g
        L = "(%s) - (%s)" % (z1, z0)
        # The shaft keyway: a slot with round ends.
        cmd("feature.block", size=["%s + 1 mm" % t1, kb, "%s - 4 mm - %s" % (L, kb)],
            position=["%s / 2 - %s" % (d, t1), "-%s / 2" % kb, "(%s) + 2 mm + %s / 2" % (z0, kb)], name="KwB" + g)
        cmd("feature.cylinder", radius="%s / 2" % kb, height="%s + 1 mm" % t1,
            position=["%s / 2 - %s" % (d, t1), 0, "(%s) + 2 mm + %s / 2" % (z0, kb)], axis=[1, 0, 0], name="KwE1" + g)
        cmd("feature.cylinder", radius="%s / 2" % kb, height="%s + 1 mm" % t1,
            position=["%s / 2 - %s" % (d, t1), 0, "(%s) - 2 mm - %s / 2" % (z1, kb)], axis=[1, 0, 0], name="KwE2" + g)
        cmd("feature.boolean", op="union", target="KwB" + g, tool="KwE1" + g, name="Kwa" + g)
        cmd("feature.boolean", op="union", target="Kwa" + g, tool="KwE2" + g, name="Kw" + g)
        cmd("feature.boolean", op="subtract", target=prev, tool="Kw" + g, name="ShaftK%d%s" % (gi, s))
        prev = "ShaftK%d%s" % (gi, s)
        # The key (form A), fit_cl inside the keyway all round.
        cmd("feature.block", size=[kh, "%s - 2 * fit_cl" % kb, "%s - 4.4 mm - %s" % (L, kb)],
            position=["%s / 2 - %s + fit_cl" % (d, t1), "-%s / 2 + fit_cl" % kb, "(%s) + 2.2 mm + %s / 2" % (z0, kb)],
            name="KyB" + g)
        cmd("feature.cylinder", radius="%s / 2 - fit_cl" % kb, height=kh,
            position=["%s / 2 - %s + fit_cl" % (d, t1), 0, "(%s) + 2.2 mm + %s / 2" % (z0, kb)], axis=[1, 0, 0],
            name="KyE1" + g)
        cmd("feature.cylinder", radius="%s / 2 - fit_cl" % kb, height=kh,
            position=["%s / 2 - %s + fit_cl" % (d, t1), 0, "(%s) - 2.2 mm - %s / 2" % (z1, kb)], axis=[1, 0, 0],
            name="KyE2" + g)
        cmd("feature.boolean", op="union", target="KyB" + g, tool="KyE1" + g, name="Kya" + g)
        cmd("feature.boolean", op="union", target="Kya" + g, tool="KyE2" + g, name="KeyLocal" + g)
    cmd("feature.rename", feature=prev, name="ShaftLocal" + s)
    for nm, z0, z1, rin in spacers:
        cmd("sketch.create", plane="xy", offset=z0, name="S_" + nm)
        cmd("sketch.circle", sketch="S_" + nm, center=["0 mm", "0 mm"], radius="%s + 3 mm" % rin)
        cmd("sketch.circle", sketch="S_" + nm, center=["0 mm", "0 mm"], radius=rin)
        cmd("feature.extrude", sketch="S_" + nm, distance="(%s) - (%s)" % (z1, z0), name=nm + "Local")
    for tag, z0 in (("A", "zA0" + s), ("B", "zB0")):
        nm = "Brg%s%s" % (tag, s)
        t = "t_ring%s%s" % (tag, s)
        for ring, r_in, r_out in (("in", "brg_d%s / 2" % s, "brg_d%s / 2 + %s" % (s, t)),
                                  ("out", "brg_D%s / 2 - %s" % (s, t), "brg_D%s / 2" % s)):
            skr = "S_%s_%s" % (nm, ring)
            cmd("sketch.create", plane="xy", offset=z0, name=skr)
            cmd("sketch.circle", sketch=skr, center=["0 mm", "0 mm"], radius=r_out)
            cmd("sketch.circle", sketch=skr, center=["0 mm", "0 mm"], radius=r_in)
            cmd("feature.extrude", sketch=skr, distance="brg_B" + s, name="%s_%s" % (nm, ring))
        cmd("feature.sphere", radius="(brg_D@ - brg_d@) * 0.16".replace("@", s),
            position=["(brg_D@ + brg_d@) / 4".replace("@", s), 0, "%s + brg_B%s / 2" % (z0, s)], name=nm + "_ball")
        cmd("feature.pattern", source=nm + "_ball", count=8, angle="45 deg", name=nm + "_balls")
        cmd("feature.boolean", op="union", target=nm + "_in", tool=nm + "_balls", name=nm + "_ib")
        cmd("feature.boolean", op="union", target=nm + "_ib", tool=nm + "_out", name=nm + "Local")
    parts = [("ShaftLocal" + s, "Shaft" + s, ALU, ("Steel C45", "7.85 g/cm3"))]
    parts += [("KeyLocal" + g, "FeatherKey" + g, DARK, ("Steel C45K", "7.85 g/cm3")) for g, _, _ in keyed]
    parts += [(nm + "Local", nm, BRASS, ("Steel S235", "7.85 g/cm3")) for nm, _, _, _ in spacers]
    parts += [("BrgA%sLocal" % s, "BearingA" + s, STEEL, ("Bearing steel 100Cr6", "7.81 g/cm3")),
              ("BrgB%sLocal" % s, "BearingB" + s, STEEL, ("Bearing steel 100Cr6", "7.81 g/cm3"))]
    for local, final, colour, mat in parts:
        cmd("feature.transform", source=local, angle=place_angle, axis=[0, 0, 1], translate=[x, 0, 0], name=final)
        look(final, colour, mat[0], mat[1])


shaft_geom("_s1", [("zA0_s1 - 2 mm", "-s_gap", "brg_d_s1 / 2"), ("-s_gap", "0 mm", "collar_d_s1 / 2"),
                   ("0 mm", "b_1 + hub_l", "d_bore_1 / 2"),
                   ("b_1 + hub_l", "zB0 + brg_B_s1 + 2 mm", "brg_d_s1 / 2"),
                   ("zB0 + brg_B_s1 + 2 mm", "zB0 + brg_B_s1 + 2 mm + ext_len", "d_ext_s1 / 2")],
           "theta_in", "0 mm", [("_1", "0 mm", "b_1 + hub_l")], [("Spacer_s1", "b_1 + hub_l", "zB0", "brg_d_s1 / 2")])
shaft_geom("_s2", [("zA0_s2 - 2 mm", "-s_gap", "brg_d_s2 / 2"), ("-s_gap", "0 mm", "collar_d_s2 / 2"),
                   ("0 mm", "z2_0 + b_3 + hub_l", "d_bore_2 / 2"),
                   ("z2_0 + b_3 + hub_l", "zB0 + brg_B_s2 + 2 mm", "brg_d_s2 / 2")],
           "w2", "a12", [("_2", "0 mm", "b_1 + hub_l"), ("_3", "z2_0", "z2_0 + b_3 + hub_l")],
           [("Spacer_s2a", "b_1 + hub_l", "z2_0", "d_bore_2 / 2"),
            ("Spacer_s2b", "z2_0 + b_3 + hub_l", "zB0", "brg_d_s2 / 2")])
shaft_geom("_s3", [("zA0_s3 - 2 mm - ext_len", "zA0_s3 - 2 mm", "d_ext_s3 / 2"),
                   ("zA0_s3 - 2 mm", "-s_gap", "brg_d_s3 / 2"), ("-s_gap", "z2_0", "collar_d_s3 / 2"),
                   ("z2_0", "z2_0 + b_4 + hub_l", "d_bore_4 / 2"),
                   ("z2_0 + b_4 + hub_l", "zB0 + brg_B_s3 + 2 mm", "brg_d_s3 / 2")],
           "w4", "a12 + a34", [("_4", "z2_0", "z2_0 + b_4 + hub_l")],
           [("Spacer_s3", "z2_0 + b_4 + hub_l", "zB0", "brg_d_s3 / 2")])

# ---------------------------------------------------------------- housing

for name, expr in (
        ("wall_ax", "max(brg_B_s1, max(brg_B_s2, brg_B_s3)) + 4 mm"),
        # The cavity: c_w round every gear, and at least as wide as the bearing seats in the end walls.
        ("r_end1", "max(ra_1 + c_w, brg_D_s1 / 2)"),
        ("xi_lo", "-r_end1"),
        ("xi_hi", "a12 + a34 + max(ra_4 + c_w, brg_D_s3 / 2)"),
        ("yi", "max(max(max(ra_1, ra_2), max(ra_3, ra_4)) + c_w, max(brg_D_s2, brg_D_s3) / 2)"),
        ("r_box", "min(r_end1, yi)"),
        ("z_cav_lo", "-s_gap"), ("z_cav_hi", "zB0"),
        ("z_h_lo", "z_cav_lo - wall_ax"), ("z_h_hi", "z_cav_hi + wall_ax")):
    var(name, expr)
for tag, grow, z0, h in (("out", "t_w", "z_h_lo", "z_h_hi - z_h_lo"), ("in", "0 mm", "z_cav_lo", "z_cav_hi - z_cav_lo")):
    cmd("feature.block", size=["xi_hi - xi_lo + 2 * %s" % grow, "2 * (yi + %s)" % grow, h],
                   position=["xi_lo - %s" % grow, "-(yi + %s)" % grow, z0], name="Box_" + tag)
# The four edges along z rounded (a block's faces 2 to 5 are its sides).
for tag, rad in (("out", "r_box + t_w"), ("in", "r_box")):
    F = "Box_" + tag
    cmd("feature.fillet", edges=[["%s:face(4)" % F, "%s:face(2)" % F], ["%s:face(2)" % F, "%s:face(5)" % F],
                                 ["%s:face(5)" % F, "%s:face(3)" % F], ["%s:face(3)" % F, "%s:face(4)" % F]],
        radius=rad, name="Box_%s_r" % tag)
cmd("feature.boolean", op="subtract", target="Box_out_r", tool="Box_in_r", name="H_shell")
var("xL", "xi_lo - t_w - 8 mm")
var("xR", "xi_hi + t_w + 8 mm")
var("zE1", "z_h_lo + 10 mm")
var("zE2", "z_h_hi - 10 mm")
prev = "H_shell"
ears = [("xL", "zE1"), ("xL", "zE2"), ("xR", "zE1"), ("xR", "zE2")]
for i, (x, z) in enumerate(ears):
    lo = "%s - 8 mm" % x if x == "xL" else "%s - 12 mm" % x
    cmd("feature.block", size=["20 mm", "24 mm", "16 mm"], position=[lo, "-12 mm", "%s - 8 mm" % z], name="Ear%d" % i)
    cmd("feature.boolean", op="union", target=prev, tool="Ear%d" % i, name="H_e%d" % i)
    prev = "H_e%d" % i
cut = []


def tool(name, r, h, pos, axis=None):
    p = {"radius": r, "height": h, "position": pos, "name": name}
    if axis:
        p["axis"] = axis
    cmd("feature.cylinder", **p)
    cut.append(name)


for s, x in (("_s1", "0 mm"), ("_s2", "a12"), ("_s3", "a12 + a34")):
    tool("SeatA" + s, "brg_D%s / 2 + fit_cl / 2" % s, "brg_B%s + 1.5 mm" % s, [x, 0, "zA0%s - 0.5 mm" % s])
    tool("SeatB" + s, "brg_D%s / 2 + fit_cl / 2" % s, "brg_B%s + 1.5 mm" % s, [x, 0, "zB0 - 1 mm"])
tool("Pass_s1", "d_ext_s1 / 2 + 1 mm", "wall_ax + 2 mm", ["0 mm", 0, "zB0 + brg_B_s1"])
tool("Relief_s1", "brg_d_s1 / 2 + 1 mm", "3 mm", ["0 mm", 0, "zA0_s1 - 3 mm"])
tool("ReliefA_s2", "brg_d_s2 / 2 + 1 mm", "3 mm", ["a12", 0, "zA0_s2 - 3 mm"])
tool("ReliefB_s2", "brg_d_s2 / 2 + 1 mm", "3 mm", ["a12", 0, "zB0 + brg_B_s2"])
tool("Pass_s3", "d_ext_s3 / 2 + 1 mm", "wall_ax + 2 mm", ["a12 + a34", 0, "z_h_lo - 1 mm"])
tool("Relief_s3", "brg_d_s3 / 2 + 1 mm", "3 mm", ["a12 + a34", 0, "zB0 + brg_B_s3"])
for i, (x, z) in enumerate(ears):
    tool("BoltHole%d" % i, "3.3 mm", "26 mm", [x, "-13 mm", z], [0, 1, 0])
for i, nm in enumerate(cut):
    cmd("feature.boolean", op="subtract", target=prev, tool=nm, name="H_c%d" % i)
    prev = "H_c%d" % i
cmd("feature.transform", source=prev, keep=True, name="H_copy")
cmd("feature.block", size=["xi_hi - xi_lo + 200 mm", "yi + 60 mm", "z_h_hi - z_h_lo + 20 mm"],
    position=["xi_lo - 100 mm", "-yi - 60 mm", "z_h_lo - 10 mm"], name="CutBelow")
cmd("feature.block", size=["xi_hi - xi_lo + 200 mm", "yi + 60 mm", "z_h_hi - z_h_lo + 20 mm"],
    position=["xi_lo - 100 mm", "0 mm", "z_h_lo - 10 mm"], name="CutAbove")
cmd("feature.boolean", op="subtract", target=prev, tool="CutBelow", name="HousingTop_raw")
cmd("feature.boolean", op="subtract", target="H_copy", tool="CutAbove", name="HousingBottom_raw")
var("z_mid", "(z_cav_lo + z_cav_hi) / 2")
var("y_wall", "yi + t_w")
# Fill plug in the rear half, drain plug in the front half (M12 x 1.5 plugs with a washer).
for tag, sgn, half, final, colour in (("Fill", "", "HousingTop_raw", "HousingTop", BRASS),
                                      ("Drain", "-", "HousingBottom_raw", "HousingBottom", DARK)):
    ax = [0, 1, 0] if sgn == "" else [0, -1, 0]
    cmd("feature.cylinder", radius="10 mm", height="5 mm", position=["a12", "%s(y_wall - 2 mm)" % sgn, "z_mid"],
        axis=ax, name=tag + "Boss")
    cmd("feature.boolean", op="union", target=half, tool=tag + "Boss", name=half + "_b")
    cmd("feature.cylinder", radius="6 mm", height="t_w + 12 mm", position=["a12", "%s(y_wall - t_w - 6 mm)" % sgn, "z_mid"],
        axis=ax, name=tag + "Hole")
    cmd("feature.boolean", op="subtract", target=half + "_b", tool=tag + "Hole", name=final)
    cmd("feature.cylinder", radius="5.9 mm", height="t_w + 4 mm", position=["a12", "%s(y_wall - t_w + 1 mm)" % sgn, "z_mid"],
        axis=ax, name=tag + "Thread")
    cmd("feature.cylinder", radius="9 mm", height="1.5 mm", position=["a12", "%s(y_wall + 3 mm)" % sgn, "z_mid"],
        axis=ax, name=tag + "Washer")
    cmd("feature.cylinder", radius="8.08 mm", height="7 mm", position=["a12", "%s(y_wall + 4.5 mm)" % sgn, "z_mid"],
        axis=ax, name=tag + "Head")
    cmd("feature.boolean", op="union", target=tag + "Thread", tool=tag + "Washer", name=tag + "_a")
    cmd("feature.boolean", op="union", target=tag + "_a", tool=tag + "Head", name=tag + "Plug")
    look(tag + "Plug", colour, "Steel plug", "7.85 g/cm3")
for h in ("HousingTop", "HousingBottom"):
    look(h, SLATE, "Cast aluminium EN AC-42100", "2.68 g/cm3")


def hexagon(sk, offset, af):
    rc = af / math.sqrt(3)
    pts = [["%g mm" % round(rc * math.cos(math.radians(60 * k)), 4), "%g mm" % round(rc * math.sin(math.radians(60 * k)), 4)]
           for k in range(6)]
    cmd("sketch.create", plane="zx", offset=offset, name=sk)
    cmd("sketch.polyline", sketch=sk, points=pts, closed=True)


# M6 hex bolts (ISO 4017: 10 mm across flats, head 4 mm) and nuts (ISO 4032: 5.2 mm) through the ears.
hexagon("S_bolthead", "12 mm", 10)
cmd("feature.extrude", sketch="S_bolthead", distance="4 mm", name="BoltHead")
cmd("feature.cylinder", radius="3 mm", height="30 mm", position=[0, "-18 mm", 0], axis=[0, 1, 0], name="BoltShank")
cmd("feature.boolean", op="union", target="BoltHead", tool="BoltShank", name="Bolt0")
hexagon("S_nut", "-17.2 mm", 10)
cmd("sketch.circle", sketch="S_nut", center=[0, 0], radius=3)
cmd("feature.extrude", sketch="S_nut", distance="5.2 mm", name="Nut0")
for part in ("Bolt0", "Nut0"):
    look(part, DARK, "Steel 8.8", "7.85 g/cm3")
for i, (x, z) in enumerate(ears):
    last = i == len(ears) - 1
    cmd("feature.transform", source="Bolt0", translate=[x, 0, z], keep=not last, name="Bolt%d" % (i + 1))
    cmd("feature.transform", source="Nut0", translate=[x, 0, z], keep=not last, name="Nut%d" % (i + 1))

# The front half is hidden in the view, so the gears show; it is built, checked and exported as always.
cmd("feature.visible", feature=["HousingBottom", "DrainPlug"], visible=False)

# ---------------------------------------------------------------- assertions

for g, s in (("_1", "_s1"), ("_2", "_s2"), ("_3", "_s2"), ("_4", "_s3")):
    cmd("assert.add", name="Key%s fits hub and shaft" % g, measure="interference", of="FeatherKey" + g,
        to=["Gear" + g, "Shaft" + s], **{"is": True})
    cmd("assert.add", name="Gear%s sits on shaft%s" % (g, s), measure="interference", of="Gear" + g, to="Shaft" + s,
        **{"is": True})
for s in ("_s1", "_s2", "_s3"):
    cmd("assert.add", name="Bearings%s seated on shaft" % s, measure="clearance", to="Shaft" + s,
        max="0.001 mm", **{"from": ["BearingA" + s, "BearingB" + s]})
gears = ["Gear_1", "Gear_2", "Gear_3", "Gear_4"]
cmd("assert.add", name="Stage 1 mesh: no interference", measure="interference", of="Gear_1", to="Gear_2", **{"is": True})
cmd("assert.add", name="Stage 2 mesh: no interference", measure="interference", of="Gear_3", to="Gear_4", **{"is": True})
cmd("assert.add", name="Non-meshing gears stay apart", measure="interference", of=["Gear_1", "Gear_2"],
    to=["Gear_3", "Gear_4"], **{"is": True})
for st, (a, b) in (("1", ("Gear_1", "Gear_2")), ("2", ("Gear_3", "Gear_4"))):
    cmd("assert.add", name="Stage %s flank clearance ~ jn/2" % st, measure="clearance", to=b,
        min="0.3 * jt * cos(alpha)", max="0.7 * jt * cos(alpha)", **{"from": a})
moving = gears + ["Shaft_s1", "Shaft_s2", "Shaft_s3", "FeatherKey_1", "FeatherKey_2", "FeatherKey_3", "FeatherKey_4",
                  "Spacer_s1", "Spacer_s2a", "Spacer_s2b", "Spacer_s3"]
cmd("assert.add", name="Moving parts clear the housing", measure="interference", of=["HousingTop", "HousingBottom"],
    to=moving, **{"is": True})
cmd("assert.add", name="Gear-to-housing clearance >= c_w", measure="clearance", to=["HousingTop", "HousingBottom"],
    min="min(c_w, s_gap) - 0.1 mm", **{"from": gears})
cmd("assert.add", name="Bearings seated in housing", measure="clearance", to=["HousingTop", "HousingBottom"],
    max="0.02 mm", **{"from": ["BearingA_s1", "BearingB_s1", "BearingA_s2", "BearingB_s2", "BearingA_s3", "BearingB_s3"]})
cmd("assert.add", name="Wheel 2 clears the output shaft", measure="interference", of="Gear_2",
    to=["Shaft_s3", "Spacer_s3", "BearingA_s3"], **{"is": True})
cmd("assert.add", name="Wheel 4 clears the input shaft", measure="interference", of="Gear_4",
    to=["Shaft_s1", "Spacer_s1"], **{"is": True})
cmd("assert.add", name="Pinion 3 clears the input shaft", measure="interference", of="Gear_3",
    to=["Shaft_s1", "Spacer_s1", "BearingB_s1"], **{"is": True})

# ---------------------------------------------------------------- parameters

# Tooth ranges: at least 14 teeth, and enough for the smallest shaft (10 mm with its keyway) and a rim of
# rim_k modules; pinion 3 small enough to clear the input shaft's spacer, and large enough that wheel 2
# clears the output shaft's collar (the wheel's teeth rounded: a quarter module).
Z1_MIN = "max(14, ceil(2 * (6.4 mm / mn_1 + rim_k + 1.25)))"
Z3_MIN = ("max(max(14, ceil(2 * (6.4 mm / mn_3 + rim_k + 1.25))),"
          " ceil((2 * (ra_2 + d_cap3 / 2 + 3.5 mm) / mn_3 + 0.5) / (1 + i_2n)))")
Z3_MAX = "z3_hi"
params = [
    dict(name="i_total", label="Target ratio", group="Ratio", order=1, min="5", max="20", step="0.5",
         description="The reduction you want, input turns per output turn. Stage 1 takes 1.1 x its square root, "
                     "stage 2 the rest; the teeth are whole, so the ratio built (i_actual) is close to it"),
    dict(name="z_1", label="Pinion teeth, stage 1", group="Ratio", order=2, kind="integer", min=Z1_MIN, max="30",
         description="Teeth of the input pinion; the wheel gets the ratio of stage 1 times as many. At least 14, "
                     "and enough that the pinion holds a 10 mm shaft with its key"),
    dict(name="z_3", label="Pinion teeth, stage 2", group="Ratio", order=3, kind="integer", min=Z3_MIN, max=Z3_MAX,
         description="Teeth of the second pinion. The range keeps it clear of the input shaft and its wheel 2 clear "
                     "of the output shaft"),
    dict(name="mi_1", label="Module, stage 1", group="Gears", order=1, kind="choice", choicesFrom="iso54",
         description="Tooth size of the first stage (ISO 54): pitch diameter = module x teeth"),
    dict(name="up_2", label="Module, stage 2", group="Gears", order=2, kind="choice", choicesFrom="steps",
         description="The second stage carries more torque: the same module, or one or two sizes up the ISO 54 "
                     "series (at most 4 mm)"),
    dict(name="b_1", label="Face width, stage 1", group="Gears", order=3, min="max(8 mm, 5 * mn_1)", max="15 * mn_1",
         step="0.5 mm", unit="mm", description="Width of the teeth of stage 1: 5 to 15 modules (at least 8 mm)"),
    dict(name="b_3", label="Face width, stage 2", group="Gears", order=4, min="max(8 mm, 5 * mn_3)", max="15 * mn_3",
         step="0.5 mm", unit="mm", description="Width of the teeth of stage 2: 5 to 15 modules (at least 8 mm)"),
    dict(name="ser", label="Bearing series", group="Shafts", order=1, kind="choice", choicesFrom="series",
         description="ISO 15 deep-groove ball bearings, chosen by the shaft: 60xx light or 62xx medium"),
    dict(name="c_w", label="Gear-to-wall clearance", group="Housing", order=1, min="2 mm", max="30 mm",
         step="0.5 mm", unit="mm", description="Room between the gears' tips and the housing wall"),
    dict(name="t_w", label="Wall thickness", group="Housing", order=2, min="3 mm", max="20 mm", step="0.5 mm",
         unit="mm", description="Wall of the cast housing"),
    dict(name="theta_in", label="Input shaft angle", group="Motion", order=1, min="-360 deg", max="360 deg",
         step="1 deg", unit="deg", description="Turn the input shaft: every gear and shaft follows"),
]
for p in params:
    cmd("variable.publish", **p)

cmd("document.info",
    title="Two-stage spur gear reducer",
    description="A two-stage spur gear reducer: set a target ratio and the tooth counts follow, choose the modules "
                "(ISO 54), the face widths, the bearing series, the housing's clearance and wall. Involute teeth "
                "(ISO 53 basic rack, 20 deg), each gear keyed (DIN 6885 form A) on a stepped shaft, deep-groove "
                "ball bearings (ISO 15, 60xx or 62xx) chosen from the shaft, a split cast housing with bolts, a "
                "fill and a drain plug. Twenty-two assertions check the fits and clearances at every point. The "
                "front half of the housing is hidden in the view; it is exported with the rest.",
    author="3DCraft Jigs", licence="CC-BY-4.0",
    url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/gear-reducer",
    tags=["gear", "gearbox", "reducer", "involute", "bearing", "mechanism"])
cmd("jig.export", path="dist/gear-reducer.3dcraftjig")



def sweep():
    """python3 gen.py --sweep: the ranges' formulas mirrored in Python and every point the form allows
    tried (every module pair, the ratio in steps of 0.1, every tooth count, both bearing series) against
    the conditions they are made for. Prints what fails; nothing when every point is a valid reducer."""
    def keyrow(d):
        return 1 + sum(d > x for x in (8, 10, 12, 17, 22, 30, 38, 44))

    def nfit(rf, mn):
        return sum(d / 2 + t2_of(d) <= rf - 2.5 * mn for d in SHAFTS)

    def bearing(d, ser):
        r = BEARINGS[brg_row(d) - 1]
        return (r[1], r[2], r[3]) if ser == 1 else (r[1], r[4], r[5])

    def rnd(x):
        return math.floor(x + 0.5)

    bad, points, most = [], 0, 0
    for mi1 in range(1, len(MODULES) + 1):
        for up in (1, 2, 3):
            m1, m3 = MODULES[mi1 - 1][1], MODULES[min(mi1 + up - 1, len(MODULES)) - 1][1]
            for it in [5 + 0.1 * k for k in range(151)]:
                i1 = round(1.1 * math.sqrt(it), 2)
                for z1 in range(max(14, math.ceil(2 * (6.4 / m1 + 2.5 + 1.25))), 31):
                    z2 = rnd(z1 * i1)
                    a12 = m1 * (z1 + z2) / 2
                    ra = [m1 * (z1 / 2 + 1), m1 * (z2 / 2 + 1)]
                    n1, n2 = nfit(m1 * (z1 / 2 - 1.25), m1), nfit(m1 * (z2 / 2 - 1.25), m1)
                    dcap1 = SHAFTS[max(1, n1) - 1]
                    z3hi = min(40, math.floor(2 * ((a12 - dcap1 / 2 - 4) / m3 - 1)))
                    n3hi = nfit(m3 * (z3hi / 2 - 1.25), m3)
                    i2n = it * z1 / z2
                    for ser in (1, 2):
                        nb = sum(bearing(d, ser)[1] / 2 + bearing(dcap1, ser)[1] / 2 + 2 <= a12 for d in SHAFTS)
                        dcap3 = SHAFTS[min(max(1, min(n2, n3hi, nb)) + 2, len(SHAFTS)) - 1]
                        z3lo = max(14, math.ceil(2 * (6.4 / m3 + 3.75)),
                                   math.ceil((2 * (ra[1] + dcap3 / 2 + 3.5) / m3 + 0.5) / (1 + i2n)))
                        if z3lo > z3hi:
                            bad.append(("empty range of z_3", m1, m3, it, z1, ser))
                        for z3 in range(z3lo, z3hi + 1):
                            points += 1
                            z4 = rnd(z3 * it * z1 / z2)
                            most = max(most, z2, z4)
                            a34 = m3 * (z3 + z4) / 2
                            rf = [m1 * (z1 / 2 - 1.25), m1 * (z2 / 2 - 1.25), m3 * (z3 / 2 - 1.25), m3 * (z4 / 2 - 1.25)]
                            ra3, ra4 = m3 * (z3 / 2 + 1), m3 * (z4 / 2 + 1)
                            n3, n4 = nfit(rf[2], m3), nfit(rf[3], m3)
                            ix2 = max(1, min(n2, n3, nb))
                            ix = [max(1, min(n1, ix2)), ix2, max(1, min(n4, ix2 + 2))]
                            d = [SHAFTS[k - 1] for k in ix]
                            brg = [bearing(x, ser) for x in d]
                            where = (m1, m3, it, z1, z3, ser)
                            if min(n1, n2, n3, n4) < 1:
                                bad.append(("a gear holds no shaft", where))
                            if ra3 + brg[0][0] / 2 + 3 + 0.5 > a12:
                                bad.append(("pinion 3 into the input spacer", where))
                            if ra[1] + (d[2] + 5) / 2 + 0.5 > a34:
                                bad.append(("wheel 2 into the output collar", where))
                            if ra4 + brg[0][0] / 2 + 3 + 0.5 > a12 + a34:
                                bad.append(("wheel 4 into the input spacer", where))
                            if brg[0][1] / 2 + brg[1][1] / 2 + 2 > a12 or brg[1][1] / 2 + brg[2][1] / 2 + 2 > a34:
                                bad.append(("bearing seats overlap", where))
                            for dd, r, mn, b in ((d[0], rf[0], m1, max(8, 5 * m1)), (d[1], rf[1], m1, max(8, 5 * m1)),
                                                 (d[1], rf[2], m3, max(8, 5 * m3)), (d[2], rf[3], m3, max(8, 5 * m3))):
                                hub = min(2 * dd + 6, 2 * r - 2 * mn) / 2
                                if hub < dd / 2 + t2_of(dd) + 1 or r < dd / 2 + t2_of(dd) + 1:
                                    bad.append(("keyway through a hub or rim", where))
                                if b + 10 - 4.4 - KEYS[keyrow(dd) - 1][1] < 1:
                                    bad.append(("key longer than its seat", where))
                            for cw in (2, 30):
                                rend = max(ra[0] + cw, brg[0][1] / 2)
                                yi = max(max(ra[0], ra[1], ra3, ra4) + cw, max(brg[1][1], brg[2][1]) / 2)
                                if yi - rend < 1:
                                    bad.append(("housing end wider than the housing", where))
    for b in bad[:20]:
        print(*b)
    print("%d points, %d failing, at most %d teeth" % (points, len(bad), most), file=sys.stderr)
    return not bad


if "--sweep" in sys.argv:
    sys.exit(0 if sweep() else 1)
print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
