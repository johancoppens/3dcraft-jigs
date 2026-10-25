#!/usr/bin/env python3
"""Writes build.json for the tensegrity table Jig (python3 -I gen.py > build.json).

The maker's "floating table": a base plate and a top plate, each with a hook
(a plate standing on edge) reaching into the other. The top hangs from the
base's hook by one short central cable; three or four outer cables, tensioned
between the edges of the two plates, keep it level.

Coordinates: z up, the base plate's underside at z = 0, the top plate's upper
face at z = H. Both hooks stand in the plane x = 0 (thickness T along x): the
base hook rises at -y and reaches over the centre, the top hook hangs at +y and
reaches under it. The central cable runs at x = y = 0 from the top hook's arm
(its upper face at zB) up to the base hook's arm (its lower face at zA). The
hook profiles are drawn on the yz plane (sketch x = world y, sketch y = world z)
and extruded symmetrically along x.

Statics (see README): the top, with the load Q anywhere on it, hangs from the
central cable; the outer cables pull down at the anchors, a regular polygon of
radius rA. With a pretension P (the sum of the outer tensions, set when the
cables are tightened) and the load's moment shared by the outer cables as in a
pile or bolt group, T_i = P / n - 2 W (w . p_i) / (n rA^2). The worst case for
cable i is the load at the top's edge right over it.
"""
import json

# Sheet materials: name, rho: density in kg/m^3, fm: bending strength in MPa,
# sf: safety factor (with creep under the permanent pretension), printed: 1 for a
# 3D printed part, E: modulus of elasticity in MPa, tMin: thinnest sheet. MDF is
# not offered: it creeps too much under a permanent load (EN 1995-1-1, kmod
# permanent 0.2 against 0.6 for plywood). PETG is not offered either: with its
# lower stiffness (about 2 GPa) the printed posts buckle before they carry a
# useful load at the default size.
MATERIALS = [
    ("Birch plywood", 680, 40, 3.5, 0, 9000, 9),
    ("Poplar plywood", 450, 25, 3.5, 0, 6000, 9),
    ("PLA, 3D printed solid", 1240, 50, 5, 1, 3500, 12),
]
# Cables and chain: name, d: diameter in mm, swl: safe working load in N.
# Wire rope 7x7 (strand core), grade 1770: minimum breaking force K d^2 R with
# K = 0.359 (EN 12385-4), safe load a fifth of it. Chain DIN 766 4 mm: working
# load limit 200 kg for static suspended loads (supplier data, Carl Stahl).
CABLES = [
    ("Steel wire rope 1.5 mm", 1.5, 286),
    ("Steel wire rope 2 mm", 2, 508),
    ("Steel wire rope 3 mm", 3, 1144),
    ("Steel wire rope 4 mm", 4, 2033),
    ("Steel chain 4 mm (DIN 766)", 4, 1962),
]

INPUTS = [
    ("H", "400 mm"),         # overall height
    ("shape", "1"),          # 1 square, 2 round, 3 triangle
    ("S", "300 mm"),         # side of the square or triangle, diameter of the round top
    ("Lc", "100 mm"),        # central cable length = how far the hooks overlap
    ("cables", "1"),         # 1: 3 outer cables, 2: 4 outer cables
    ("T", "18 mm"),          # sheet thickness
    ("material", "1"),
    ("outer", "2"),          # outer cable type (row of the cables table)
    ("central", "3"),        # central cable type
    ("load", "3"),           # kg on the table
    ("bed", "350 mm"),       # print bed, for printed parts
    ("clearance", "0.1 mm"),  # slots are this much wider than the tabs
]

DERIVED = [
    ("g", "9.81"),
    ("rho", "sheets[material].rho"),
    ("fm", "sheets[material].fm"),
    ("sf", "sheets[material].sf"),
    ("printed", "sheets[material].printed"),
    ("E", "sheets[material].E"),
    ("Tmin", "sheets[material].tMin * 1 mm"),
    ("n", "if(shape == 3, 3, cables + 2)"),           # a triangle always has 3 outer cables
    ("dO", "ropes[outer].d"),
    ("swlO", "ropes[outer].swl"),
    ("dC", "ropes[central].d"),
    ("swlC", "ropes[central].swl"),
    # Ranges that follow the other inputs.
    ("Smin", "choose(shape, 160 mm, 160 mm, 240 mm)"),
    ("Smax", "if(printed, bed, 600 mm)"),
    # The top's outline.
    ("rc", "min(20 mm, S / 10)"),                                  # corner radius
    ("R3", "S / sqrt(3)"),                                         # triangle: centre to a corner
    ("hIn", "choose(shape, S / 2, S / 2, S / (2 * sqrt(3)))"),     # centre to an edge
    ("Rout", "choose(shape, S / sqrt(2), S / 2, S / sqrt(3))"),    # reach of a load from the centre (corners sharp: on the safe side)
    ("yEdge", "choose(shape, S / 2, S / 2, S / 3)"),               # edge of the top along the hooks' plane
    ("areaTop", "choose(shape, S^2 - (4 - pi) * rc^2, pi * S^2 / 4, sqrt(3) / 4 * S^2 - 3 * rc^2 * (sqrt(3) - pi / 3))"),
    # The hooks.
    ("pOut", "yEdge - 12 mm - T / 2"),                             # outer face of a post
    ("tipC", "5 mm"),                                              # the arm's straight underside reaches tipC past the centre
    # depth of the arm and width of the post: deeper for printed parts, but leaving 6 mm between a
    # hook's arm (its inside fillet b / 4 included) and the other hook's post
    ("b", "max(25 mm, min(clamp(if(printed, 0.35, 0.25) * yEdge + 5 mm, 25 mm, 80 mm), (pOut - tipC - 6 mm) / 1.75))"),
    ("rf", "b / 4"),                                               # inside fillet, arm to post
    ("tabW", "b / 3"),
    ("p", "pOut - b / 2"),                                         # lever of the central cable on a hook
    ("gapV", "15 mm"),                                             # a hook's arm to the other plate
    ("LcMin", "20 mm"),
    ("Hmin", "ceil(LcMin + 2 * b + 2 * T + 2 * gapV + 0.001 mm, 1 mm)"),
    ("zA", "H / 2 + Lc / 2"),                                      # underside of the base hook's arm
    ("zB", "H / 2 - Lc / 2"),                                      # top of the top hook's arm
    # The anchors of the outer cables: a regular polygon of radius rA, 25 mm in from the edge.
    ("inset", "25 mm"),
    ("phi0", "if(n == 3, 0 deg, 45 deg)"),
]
for i in range(1, 5):
    DERIVED.append(("phi%d" % i, "phi0 + %d * 360 deg / n" % (i - 1)))
    DERIVED.append(("rho%d" % i, "choose(shape, (S / 2) / max(abs(cos(phi%d)), abs(sin(phi%d))), S / 2, "
                    "hIn / max(cos(phi%d - 60 deg), max(cos(phi%d - 180 deg), cos(phi%d - 300 deg))))" % ((i,) * 5)))
DERIVED += [
    ("rhoMin", "min(min(rho1, rho2), min(rho3, if(n == 4, rho4, rho3)))"),
    ("rA", "(hIn - inset) / hIn * rhoMin"),
    ("aIn", "rA * cos(180 deg / n) / sqrt(2)"),                     # a square inside the anchor polygon
    # The top hook's area outside the top plate and its centroid along y (tabs fill the slots).
    ("A1", "b * (H - T - zB + b)"), ("y1", "pOut - b / 2"),          # post
    ("A2", "b * (pOut - b + tipC)"), ("y2", "(pOut - b - tipC) / 2"),  # arm
    ("A3", "pi * b^2 / 8"), ("y3", "-tipC - 2 * b / (3 * pi)"),      # round end of the arm
    ("A4", "(1 - pi / 4) * (b / 2)^2"), ("y4", "pOut - 0.2234 * b / 2"),  # rounded outer corner (taken off)
    ("A5", "(1 - pi / 4) * rf^2"), ("y5", "pOut - b - 0.2234 * rf"),     # inside fillet (added)
    ("aHook", "A1 + A2 + A3 - A4 + A5"),
    ("yHook", "(A1 * y1 + A2 * y2 + A3 * y3 - A4 * y4 + A5 * y5) / aHook"),
    # Stability: the top hook's post may grow (with H and Lc) only while the top's centre of mass
    # stays inside the anchor polygon, with 5 % to spare.
    ("restA", "A2 + A3 - A4 + A5"),
    ("restM", "A2 * y2 + A3 * y3 - A4 * y4 + A5 * y5"),
    ("A1max", "(0.95 * aIn * (areaTop + restA) - restM) / max(y1 - 0.95 * aIn, 1 mm)"),
    ("eTop", "aHook * yHook / (areaTop + aHook)"),                  # the top's centre of mass, off centre along y
    ("eUse", "eTop + 2 mm"),                                        # ... as the statics take it
    ("mPlate", "areaTop * T / (1 mm)^3 * rho * 1e-9"),               # kg
    ("mTop", "(areaTop + aHook) * T / (1 mm)^3 * rho * 1e-9"),       # kg
    ("Wt", "mTop * g"),                                             # N
    ("WQ", "load * g"),
    # A hook in bending (arm and post, lever p) and its post in compression (Euler, a cantilever
    # fixed in its plate: buckling length 2 Lp, out of the hook's plane, I = b T^3 / 12).
    ("TcHook", "fm / sf * (T / 1 mm) * (b / 1 mm)^2 / 6 / (p / 1 mm)"),
    ("Ib", "(b / 1 mm) * (T / 1 mm)^3 / 12"),
    ("F0", "80 + 2 * mPlate * g"),                                  # what a post must carry at least (self-stress and the top)
    ("LbMax", "pi / 2 * sqrt(E * Ib * max(1 / F0 - 1 / TcHook, 1e-9) / sf) * 1 mm"),
    ("Hmax", "floor(min(800 mm, 2 * (A1max / b + T - b) - LcMin, 2 * (LbMax + T - b) - LcMin, if(printed, 2 * bed - 2 * b - LcMin, 800 mm)) - 0.001 mm, 1 mm)"),
    ("LcMax", "min(H - 2 * b - 2 * T - 2 * gapV, 2 * (A1max / b + T - b) - H, 2 * (LbMax + T - b) - H, if(printed, 2 * bed - H - 2 * b, 1 m))"),
    ("Lp", "H / 2 + Lc / 2 + b - T"),                               # free length of a post
    ("Ncr", "pi^2 * E * Ib / (2 * Lp / 1 mm)^2"),
    ("TcPost", "1 / (sf / Ncr + 1 / TcHook)"),                      # bending and buckling together
    # Statics, in N. D is the largest change of an outer cable's tension from the moment of the top
    # and of the load at the edge of the top over (or opposite) that cable. The vertical share of the
    # load is taken as lost by the outer cables (the hooks bend more than the cables stretch).
    ("D", "2 / (n * rA) * (Wt * eUse + WQ * Rout)"),
    ("T0", "1.25 * (D + WQ / n) + 10"),                             # pretension of each outer cable, unloaded
    ("TminW", "T0 - D - WQ / n"),                                   # least outer tension, worst load
    ("ToutMax", "T0 + D"),                                          # most outer tension, worst load
    ("Tc", "n * T0 + Wt + WQ"),                                     # central cable
    ("bReq", "sqrt(6 * Tc * (p / 1 mm) * sf / (fm * (T / 1 mm))) * 1 mm"),
    ("Lbuck", "pi / 2 * sqrt(E * Ib * max(1 - Tc / TcHook, 0) / (sf * Tc)) * 1 mm"),  # longest post that carries Tc
    ("dReqO", "dO * sqrt(ToutMax / swlO)"),
    ("dReqC", "dC * sqrt(Tc / swlC)"),
    # The largest load the cables and hooks allow (it does not depend on the load).
    ("kD", "2 / (n * rA)"),
    ("capC", "min(swlC, TcPost)"),
    ("qOut", "(swlO - 10 - 2.25 * kD * Wt * eUse) / (2.25 * kD * Rout + 1.25 / n)"),
    ("qCen", "(capC - 10 * n - Wt - 2.5 * Wt * eUse / rA) / (2.25 + 2.5 * Rout / rA)"),
    ("maxLoad", "clamp(floor(min(qOut, qCen) / g), 0, 50)"),
    ("Lout", "H - 2 * T"),                                          # outer cable length, eye to eye
]


class Sketch:
    """Sketch commands, predicting the entity ids 3DCraft gives (e1, e2, ...)."""

    def __init__(self, steps, name, plane="xy", offset=None):
        self.steps, self.name, self.n = steps, name, 0
        p = {"name": name, "plane": plane}
        if offset:
            p["offset"] = offset
        steps.append(["sketch.create", p])

    def _new(self):
        self.n += 1
        return "e%d" % self.n

    def path(self, start, segments):
        """segments: ("line", end) or ("arc", end, center, clockwise); end [x, y] or "start"."""
        self._new()
        segs = []
        for seg in segments:
            end = seg[1]
            if end != "start":
                self._new()
            if seg[0] == "line":
                self._new()
                segs.append({"line": end})
            else:
                self._new()
                self._new()
                segs.append({"arc": end, "center": seg[2], "clockwise": seg[3]})
        self.steps.append(["sketch.path", {"sketch": self.name, "start": start, "segments": segs}])

    def rect(self, x0, y0, x1, y1):
        self.steps.append(["sketch.rect", {"sketch": self.name, "from": [x0, y0], "to": [x1, y1]}])
        self.n += 8

    def circle(self, x, y, r):
        self.steps.append(["sketch.circle", {"sketch": self.name, "center": [x, y], "radius": r}])
        self.n += 2


def rot(pt, k):
    """A point [x, y] (expressions) turned by k * 120 degrees."""
    if k == 0:
        return pt
    a = "%d deg" % (120 * k)
    x, y = pt
    return ["cos(%s) * (%s) - sin(%s) * (%s)" % (a, x, a, y), "sin(%s) * (%s) + cos(%s) * (%s)" % (a, x, a, y)]


def outline(sk, shape):
    """The top's (and base's) outline, counter-clockwise, corners rounded by rc."""
    if shape == "round":
        sk.circle("0 mm", "0 mm", "S / 2")
        return
    if shape == "square":
        h = "S / 2"
        c = "S / 2 - rc"
        corners = [("1", "1"), ("-1", "1"), ("-1", "-1"), ("1", "-1")]
        segs = []
        start = [h, "-(%s)" % c]
        for sx, sy in corners:
            # along the edge to the corner's first tangent point, then round it
            if sx == "1" and sy == "1":
                a, e, ctr = [h, c], [c, h], [c, c]
            elif sx == "-1" and sy == "1":
                a, e, ctr = ["-(%s)" % c, h], ["-(%s)" % h, c], ["-(%s)" % c, c]
            elif sx == "-1":
                a, e, ctr = ["-(%s)" % h, "-(%s)" % c], ["-(%s)" % c, "-(%s)" % h], ["-(%s)" % c, "-(%s)" % c]
            else:
                a, e, ctr = [c, "-(%s)" % h], "start", [c, "-(%s)" % c]
            segs.append(("line", a))
            segs.append(("arc", e, ctr, False))
        sk.path(start, segs)
        return
    # Triangle, a corner at +x: corner k at angle 120 k deg, radius R3. Near corner 0 the
    # rounding's tangent points are (R3 - 1.5 rc, -/+ sqrt(3)/2 rc), its centre (R3 - 2 rc, 0).
    t_in = ["R3 - 1.5 * rc", "-sqrt(3) / 2 * rc"]
    t_out = ["R3 - 1.5 * rc", "sqrt(3) / 2 * rc"]
    ctr = ["R3 - 2 * rc", "0 mm"]
    segs = [("arc", t_out, ctr, False)]
    for k in (1, 2):
        segs.append(("line", rot(t_in, k)))
        segs.append(("arc", rot(t_out, k), rot(ctr, k), False))
    segs.append(("line", "start"))
    sk.path(t_in, segs)


def slots(sk, sign):
    """The two slots for a hook's tabs; sign -1 for the base hook (at -y), +1 for the top hook."""
    w = "(T + clearance) / 2"
    for a, b in (("pOut - tabW", "pOut"), ("pOut - b", "pOut - b + tabW")):
        lo, hi = "%s - clearance / 2" % a, "%s + clearance / 2" % b
        if sign < 0:
            lo, hi = "-(%s)" % hi, "-(%s)" % lo
        sk.rect("-" + w, lo, w, hi)


def main():
    s = []
    s.append(["table.set", {"name": "sheets", "columns": ["material", "rho", "fm", "sf", "printed", "E", "tMin"],
                            "rows": [list(r) for r in MATERIALS]}])
    s.append(["table.set", {"name": "ropes", "columns": ["cable", {"name": "d", "unit": "mm"}, "swl"],
                            "rows": [list(r) for r in CABLES]}])
    for nm, e in INPUTS + DERIVED:
        s.append(["variable.set", {"name": nm, "expr": e}])

    # Plates: one sketch per shape, each with the slots for its hook's tabs.
    plates = {"Base": [], "Top": []}
    for which, sign, z in (("Base", -1, None), ("Top", 1, "H - T")):
        for k, shape in enumerate(("square", "round", "triangle"), start=1):
          for nc in (3, 4):
            nm = "%s%s%d" % (which, shape.capitalize(), nc)
            cond = "shape == %d && n == %d" % (k, nc)
            sk = Sketch(s, nm + "Sketch", "xy", z)
            outline(sk, shape)
            slots(sk, sign)
            for i in range(1, nc + 1):   # holes for the outer cables
                sk.circle("rA * cos(phi%d)" % i, "rA * sin(phi%d)" % i, "(dO + 1 mm) / 2")
            s.append(["feature.when", {"feature": nm + "Sketch", "expr": cond}])
            s.append(["feature.extrude", {"sketch": nm + "Sketch", "distance": "T", "name": nm, "when": cond}])
            plates[which].append(nm)

    # Base hook: post at -y from the floor (tabs through the base plate) up to zA + b, arm over the centre.
    sk = Sketch(s, "BaseHookSketch", "yz")
    sk.path(["-pOut", "0 mm"], [
        ("line", ["-pOut + tabW", "0 mm"]), ("line", ["-pOut + tabW", "T"]),
        ("line", ["-pOut + b - tabW", "T"]), ("line", ["-pOut + b - tabW", "0 mm"]),
        ("line", ["-pOut + b", "0 mm"]), ("line", ["-pOut + b", "zA - rf"]),
        ("arc", ["-pOut + b + rf", "zA"], ["-pOut + b + rf", "zA - rf"], True),
        ("line", ["tipC", "zA"]),
        ("arc", ["tipC", "zA + b"], ["tipC", "zA + b / 2"], False),
        ("line", ["-pOut + b / 2", "zA + b"]),
        ("arc", ["-pOut", "zA + b / 2"], ["-pOut + b / 2", "zA + b / 2"], False),
        ("line", "start")])
    sk.circle("0 mm", "zA + b / 2", "(dC + 1 mm) / 2")   # hole for the central cable
    s.append(["feature.extrude", {"sketch": "BaseHookSketch", "distance": "T", "symmetric": True, "name": "BaseHook"}])
    # Top hook: post at +y from the top (tabs through the top plate) down to zB - b, arm under the centre.
    sk = Sketch(s, "TopHookSketch", "yz")
    sk.path(["pOut", "H"], [
        ("line", ["pOut - tabW", "H"]), ("line", ["pOut - tabW", "H - T"]),
        ("line", ["pOut - b + tabW", "H - T"]), ("line", ["pOut - b + tabW", "H"]),
        ("line", ["pOut - b", "H"]), ("line", ["pOut - b", "zB + rf"]),
        ("arc", ["pOut - b - rf", "zB"], ["pOut - b - rf", "zB + rf"], True),
        ("line", ["-tipC", "zB"]),
        ("arc", ["-tipC", "zB - b"], ["-tipC", "zB - b / 2"], False),
        ("line", ["pOut - b / 2", "zB - b"]),
        ("arc", ["pOut", "zB - b / 2"], ["pOut - b / 2", "zB - b / 2"], False),
        ("line", "start")])
    sk.circle("0 mm", "zB - b / 2", "(dC + 1 mm) / 2")   # hole for the central cable
    s.append(["feature.extrude", {"sketch": "TopHookSketch", "distance": "T", "symmetric": True, "name": "TopHook"}])

    # Cables: the central one between the arms, the outer ones through holes in both plates.
    s.append(["feature.cylinder", {"radius": "dC / 2", "height": "Lc", "position": ["0 mm", "0 mm", "zB"],
                                   "name": "CentralCable"}])
    outers = []
    for i in range(1, 5):
        nm = "OuterCable%d" % i
        p = {"radius": "dO / 2", "height": "H",
             "position": ["rA * cos(phi%d)" % i, "rA * sin(phi%d)" % i, "0 mm"], "name": nm}
        if i == 4:
            p["when"] = "n == 4"
        s.append(["feature.cylinder", p])
        outers.append(nm)

    walnut = {"color": "#7A5638", "roughness": 0.55}
    ply = {"color": "#D9B98A", "roughness": 0.75}
    steel = {"color": "#7D858C", "metallic": 0.85, "roughness": 0.4}
    for nm in plates["Base"] + plates["Top"]:
        s.append(["body.appearance", dict(body=nm, **walnut)])
    for nm in ("BaseHook", "TopHook"):
        s.append(["body.appearance", dict(body=nm, **ply)])
    for nm in ["CentralCable"] + outers:
        s.append(["body.appearance", dict(body=nm, **steel)])
    # One density for every sheet part: the centre of mass of plate and hook together does not
    # depend on it (the statics take the masses from the material table).
    for nm in plates["Top"] + ["TopHook"]:
        s.append(["body.material", {"body": nm, "name": "Sheet (birch plywood density)", "density": 680}])

    def body_set(names):
        return {"kind": "body", "where": {"any": [{"in": nm} for nm in names]}}

    s.append(["set.define", {"name": "Top assembly", "kind": "body", "where": {"any": [{"in": nm} for nm in plates["Top"] + ["TopHook"]]}}])
    s.append(["set.define", {"name": "Top plate", "kind": "body", "where": {"any": [{"in": nm} for nm in plates["Top"]]}}])
    s.append(["set.define", {"name": "Cut sheet", "kind": "face", "where": {"any":
        [{"in": nm, "normal": {"along": "-z"}} for nm in plates["Base"] + plates["Top"]] +
        [{"in": nm, "normal": {"along": "x"}} for nm in ("BaseHook", "TopHook")]}}])

    A = []

    def a(name, **p):
        p["name"] = name
        A.append(["assert.add", p])

    top = {"set": "Top assembly"}
    tplate = {"set": "Top plate"}
    a("Height as set", measure="extent", axis="z", eq="H", tol="0.01 mm")
    a("Hooks do not touch (clearance at least 5 mm)", measure="clearance", **{"from": "BaseHook", "to": "TopHook"}, min="5 mm")
    a("No part overlaps another", measure="overlap", **{"is": False})
    a("Top's centre of mass inside the anchor polygon (x)", measure="centerOfMass", of=top, axis="x", min="-aIn", max="aIn")
    a("Top's centre of mass inside the anchor polygon (y)", measure="centerOfMass", of=top, axis="y", min="-aIn", max="aIn")
    a("Top's centre of mass no further off centre than the statics take it", measure="centerOfMass", of=top, axis="y",
      min="-0.5 mm", max="eUse")
    a("Central support inside the anchor polygon (x)", measure="boxMax", of="CentralCable", axis="x", max="aIn")
    a("Central support inside the anchor polygon (-x)", measure="boxMin", of="CentralCable", axis="x", min="-aIn")
    a("Central support inside the anchor polygon (y)", measure="boxMax", of="CentralCable", axis="y", max="aIn")
    a("Central support inside the anchor polygon (-y)", measure="boxMin", of="CentralCable", axis="y", min="-aIn")
    for ax in ("x", "y"):
        a("Top plate within the box of the statics' load reach Rout (+%s)" % ax, measure="boxMax", of=tplate, axis=ax, max="Rout")
        a("Top plate within the box of the statics' load reach Rout (-%s)" % ax, measure="boxMin", of=tplate, axis=ax, min="-Rout")
    a("Outer cables stay taut with the load at the worst edge (TminW > 0)", measure="extent", of="OuterCable1", axis="z",
      min="if(TminW > 0, H - 0.01 mm, 2 * H)")
    a("Outer cable thick enough for its tension (ToutMax within the safe load)", measure="extent", of="OuterCable1",
      axis="x", min="dReqO - 0.001 mm")
    a("Central cable thick enough for its tension (Tc within the safe load)", measure="extent", of="CentralCable",
      axis="x", min="dReqC - 0.001 mm")
    a("Top hook's arm deep enough for the central cable", measure="boxMin", of="TopHook", axis="z", max="zB - bReq + 0.001 mm")
    a("Base hook's arm deep enough for the central cable", measure="boxMax", of="BaseHook", axis="z", min="zA + bReq - 0.001 mm")
    a("Base hook's post does not buckle (Euler with bending)", measure="extent", of="BaseHook", axis="z", max="T + Lbuck + 0.001 mm")
    a("Top hook's post does not buckle (Euler with bending)", measure="extent", of="TopHook", axis="z", max="T + Lbuck + 0.001 mm")
    a("Printed parts fit the print bed (top plate, x)", measure="extent", of=tplate, axis="x", max="if(printed, bed, 10 m)")
    a("Printed parts fit the print bed (top plate, y)", measure="extent", of=tplate, axis="y", max="if(printed, bed, 10 m)")
    a("Printed parts fit the print bed (hook)", measure="extent", of="BaseHook", axis="z", max="if(printed, bed, 10 m)")
    s.extend(A)

    pub = [
        ("H", dict(label="Height", description="Overall height, floor to the top's upper face", group="Size", order=1,
                   min="Hmin", max="Hmax", step="1 mm", unit="mm")),
        ("shape", dict(label="Top shape", description="Shape of the top and the base", group="Size", order=2,
                       kind="choice", choices=["square", "round", "triangle"])),
        ("S", dict(label="Top size", description="Side of the square or the triangle, diameter of the round top",
                   group="Size", order=3, min="Smin", max="Smax", step="1 mm", unit="mm")),
        ("Lc", dict(label="Central cable length", description="How far the two hooks overlap: the length of the central "
                    "cable between the arms", group="Size", order=4, min="LcMin", max="LcMax", step="1 mm", unit="mm")),
        ("cables", dict(label="Outer cables", description="Three or four outer cables between the edges of top and base (a triangle always has three)",
                        group="Cables", order=1, kind="choice", choices=["3 cables", "4 cables"])),
        ("outer", dict(label="Outer cable type", description="Wire rope or chain for the outer cables (table ropes: "
                       "diameter and safe load)", group="Cables", order=2, kind="choice", choicesFrom="ropes")),
        ("central", dict(label="Central cable type", description="Wire rope or chain for the central cable",
                         group="Cables", order=3, kind="choice", choicesFrom="ropes")),
        ("load", dict(label="Load on the table", description="Mass the table must carry anywhere on its top, kg; the "
                      "range ends where a cable or a hook would be overloaded (maxLoad)", group="Load", order=1,
                      kind="integer", min="0", max="maxLoad", step="1")),
        ("material", dict(label="Material", description="Sheet the plates and hooks are cut or printed from (table "
                          "sheets: density, bending strength, safety factor)", group="Material", order=1,
                          kind="choice", choicesFrom="sheets")),
        ("T", dict(label="Sheet thickness", description="Thickness of the plates and the hooks", group="Material",
                   order=2, min="Tmin", max="24 mm", step="0.1 mm", unit="mm")),
        ("clearance", dict(label="Slot clearance", description="How much wider each slot is drawn than its tab: 0 is a "
                           "press fit (a laser's kerf adds about 0.1 mm), 0.2 to 0.3 mm slides", group="Material",
                           order=3, min="0 mm", max="0.6 mm", step="0.01 mm", unit="mm")),
        ("bed", dict(label="Print bed", description="Largest part your printer takes (for a printed material): the "
                     "top's size and the hooks' height stay within it", group="Material", order=4,
                     min="250 mm", max="500 mm", step="1 mm", unit="mm")),
    ]
    for name, fields in pub:
        p_ = {"name": name}
        p_.update(fields)
        s.append(["variable.publish", p_])

    s.append(["document.info", {
        "title": "Tensegrity table",
        "description": "The floating table: the top hangs from a hook on the base by one central cable, and three or "
                       "four outer cables in tension hold it level. Set the height, the top's shape and size, how far "
                       "the hooks overlap, the sheet, the cables and the load; the document works out the tensions "
                       "(T0: the pretension to give each outer cable, Tc: the central cable) and limits the load to what "
                       "the cables and hooks carry. Cut sheet: file.export {\"path\": \"table.svg\", \"set\": \"Cut sheet\"}.",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/tensegrity-table",
        "tags": ["furniture", "table", "tensegrity", "plywood", "laser", "CNC", "3D print", "statics"]}])
    s.append(["jig.export", {"path": "dist/tensegrity-table.3dcraftjig"}])
    return s


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
