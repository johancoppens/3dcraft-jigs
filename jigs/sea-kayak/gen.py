#!/usr/bin/env python3
"""Writes build.json of the sea-kayak Jig:  python3 -I gen.py > build.json

A multichine stitch-and-glue sea kayak in okoume plywood, Greenland style (after the character of Ken
Taylor's 1959 Igdlorssuit kayak; the lines are our own). Everything is built by 3DCraft from formulas: this
script only writes commands and formulas. It computes no geometry (no offsets, intersections, areas,
developments or hydrostatics); its loops only write lists of commands.

The lines
---------
x runs along the boat (stern -L/2, bow +L/2), y to starboard, z up from the keel's lowest point. A station
is eta in [0, 1] (0 the stern tip, 1 the bow tip), a skewed copy of xi = x / L + 1/2,
eta = xi + s xi (1 - xi), so the widest station (eta = 1/2) lies at the fraction xmax of the length. In
every curve formula below `t` is eta.

Every hull panel j is a generalised cylinder: in every station a straight line at the same flare angle
th_j, from chine j to chine j + 1, of width w_j = W_j G^p_j (1 + sp_j (1 - G)), G = 4 eta (1 - eta). At the
widest station the chines lie on a quarter ellipse (B / 2, D), equally spaced in angle. The keel rises as
z0 = rA u^4 + rC u^5 (u = 2 eta - 1). The deck is one panel a side at the crown angle, from the sheer to a
ridge on the centre line. A generalised cylinder is the extrusion of a plane curve (its trace in the
plane square to its direction d_j) along d_j: `sketch.curve` draws the trace from the formulas and
`feature.extrude` sweeps it, so each panel's surface is exact. The solids so made, one per panel and side,
intersected are the hull envelope; its edges are the keel, the chines and the sheer, found by the kernel.
"""
import json
import os
import re

STAGE = int(os.environ.get("STAGE", "99"))   # for development: stop after a stage
FLOOR = -150      # mm: the floor the flat parts lie on, below the keel
ROW = 520         # mm between the rows of flat panels on the floor
PIECE_GAP = 50    # mm: the three pieces of a flat panel lie this far apart along it

OKOUME, WALNUT, CREAM, COPPER = "#D9B98A", "#7A5638", "#E8DFCC", "#B87350"

steps = []


def C(cmd, **p):
    steps.append([cmd, p])


def V(name, expr):
    C("variable.set", name=name, expr=expr)


def A(name, **kw):
    C("assert.add", name=name, **kw)


def done(stage):
    if STAGE <= stage:
        print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
        raise SystemExit(0)


def at(expr, v):
    return re.sub(r"\bt\b", f"({v})", expr)


def when(d, cond):
    if cond:
        d["when"] = cond
    return d


# ================================================================ inputs (published at the end)
for n_, e in [("L", "5300 mm"), ("B", "545 mm"), ("D", "190 mm"), ("crown", "22 deg"), ("rockB", "300 mm"),
              ("rockS", "240 mm"), ("xmax", "0.47"), ("chines", "3"), ("form", "2"), ("mPad", "80"),
              ("hPad", "1780 mm"), ("payload", "5"), ("water", "1"), ("tHull", "4 mm"), ("tDeck", "3 mm"),
              ("cockL", "800 mm"), ("cockW", "420 mm"), ("hatches", "1"), ("endCap", "2"), ("holeD", "2 mm"),
              ("holeIn", "8 mm")]:
    V(n_, e)
# The ends: how fast the panels narrow to the tips, G^p (bottom panel pb, topside pt).
# kA, kD: the panels' and the deck's area as a share of length x girth, and kCap: a block coefficient of the
# volume below the sheer less 45 mm, each read off the kernel's measures over the corners of the ranges
# (kCap on the safe side); the assertions hold the form to the real masses and waterline.
C("table.set", name="forms", columns=["form", "pb", "pt", "kA", "kD", "kCap"],
  rows=[["Fine", 1.8, 1.0, 0.622, 0.610, 0.330], ["Moderate", 1.6, 1.0, 0.637, 0.626, 0.336],
        ["Full", 1.3, 1.0, 0.661, 0.655, 0.345]])
C("table.set", name="endcaps", columns=["endCap"], rows=[["None"], ["Hardwood strip"]])
C("table.set", name="waters", columns=["water", "rho"], rows=[["Sea water", 1025], ["Fresh water", 1000]])

# ================================================================ constants (sources in the README)
V("rhoPly", "500")          # okoume plywood, kg/m^3 (CLC: a 4 mm 4 x 8 ft sheet weighs 13 lb)
V("rhoWood", "600")         # hardwood: tips, sheer clamps, coaming, hatch covers
V("glassHull", "0.80")      # kg/m^2: 6 oz glass outside with epoxy, inside coat, seam tape
V("glassDeck", "0.55")      # kg/m^2: 4 oz glass with epoxy
V("fittings", "2.5")        # kg: seat pad, back band, hatch rims, deck lines
V("cgUp", "254 mm")         # paddler's centre of gravity above the seat (Sea Kayaker: 10 in)
V("cgFwd", "254 mm")        # ... and ahead of the seat back
V("clampA", "20 mm")        # sheer clamp: depth under the deck
V("clampB", "12 mm")        # ... and thickness against the topside
V("spring", "0.8")          # sheer spring: the upper panels stay wider towards the ends
V("ea", "0.03")             # the plywood hull runs from eta = ea to eb; beyond are the hardwood tips
V("eb", "0.97")
V("ex", "0.005")            # the other panels' solids reach this much past the ends
V("riserH", "30 mm")        # the coaming's riser stands 30 mm above the deck, the lip on it
V("riserT", "6 mm")
V("lipW", "28 mm")
V("lipT", "6 mm")
V("backGap", "60 mm")       # the cockpit opening's aft edge behind the seat back
V("bkAft", "150 mm")        # the aft bulkhead behind the seat back
V("hatchR", "120 mm")       # 24 cm round hatches

# ================================================================ the lines, as formulas
V("rho", "waters[water].rho")
V("pb", "forms[form].pb")
V("pt", "forms[form].pt")
V("n", "chines + 1")        # hull panels a side
V("s", "(0.5 - xmax) / (xmax * (1 - xmax))")
V("rA", "(rockB + rockS) / 2")
V("rC", "(rockB - rockS) / 2")
V("tc", "tan(crown)")
for j in range(4):
    a, b = f"90 deg * {j} / n", f"90 deg * {j + 1} / n"
    V(f"dy{j}", f"if(n > {j}, B / 2 * (sin({b}) - sin({a})), 0 mm)")
    V(f"dz{j}", f"if(n > {j}, D * (cos({a}) - cos({b})), 0 mm)")
    V(f"W{j}", f"sqrt(dy{j}^2 + dz{j}^2)")
    V(f"c{j}", f"if(n > {j}, dy{j} / W{j}, 0.6)")
    V(f"s{j}", f"if(n > {j}, dz{j} / W{j}, 0.8)")
    V(f"th{j}", f"atan2(s{j}, c{j})")
    V(f"p{j}", f"if(n > {j}, pb + (pt - pb) * {j} / (n - 1), 1)")
    V(f"sp{j}", f"if(n > {j}, spring * {j} / (n - 1), 0)")
V("thD", "180 deg - crown")

X = "((2 * t / ((1 + s) + sqrt((1 + s)^2 - 4 * s * t))) - 0.5) * L"
G = "(4 * t * (1 - t))"
Z0 = "(rA * (2 * t - 1)^4 + rC * (2 * t - 1)^5)"


def w(m):
    return f"W{m} * pow({G}, p{m}) * (1 + sp{m} * (1 - {G}))"


def Y(k):
    return "0 mm" if k == 0 else " + ".join(f"{w(m)} * c{m}" for m in range(k))


def Z(k):
    return Z0 if k == 0 else Z0 + " + " + " + ".join(f"{w(m)} * s{m}" for m in range(k))


ZR = f"({Z(4)} + ({Y(4)}) * tc)"     # the ridge, on the centre line


def trace(j, off="0 mm"):
    """The inward offset of panel j's cylinder, P . (-sin th_j, cos th_j) for a point P of its lower chine,
    plus off (inward: the inner skin of the plywood)."""
    if j == "D":
        return f"-cos(crown) * {ZR} + {off}"
    return " + ".join([f"c{j} * {Z0}"] + [f"{w(m)} * sin(th{m} - th{j})" for m in range(j)]) + f" + {off}"


V("Xa", at(X, "ea"))
V("Xb", at(X, "eb"))
V("Xa2", at(X, "ea - ex"))
V("Xb2", at(X, "eb + ex"))
V("Lhull", "Xb - Xa")
V("Xmid", at(X, "0.5"))        # the widest station
V("Zmid", at(Z(4), "0.5"))     # the sheer there (= D)
V("Ymid", at(Y(4), "0.5"))     # the half beam there (= B / 2)

# ================================================================ the hull envelope
PANELS = [0, 1, 2, 3, "D"]
EXISTS = {0: None, 1: None, 2: "n > 2", 3: "n > 3", "D": None}
NM = ["1", "2", "3", "D"]
for j in PANELS:
    C("datum.plane", **{"from": "zx", "about": "x", "angle": "thD" if j == "D" else f"th{j}", "name": f"Plane{j}"})


def trace_solid(tag, j, off, ext=True, cond=None, rng=None):
    """The solid inside panel j's surface (moved inward by off), extruded along its direction."""
    ta, tb, xa, xb = rng or (("ea - ex", "eb + ex", "Xa2", "Xb2") if ext else ("ea", "eb", "Xa", "Xb"))
    sk = f"{tag}Trace"
    C("sketch.create", plane=f"Plane{j}", name=sk)
    C("sketch.curve", sketch=sk, x=trace(j, off), y=X, t=[ta, tb])
    C("sketch.line", sketch=sk, **{"from": "e2", "to": ["1500 mm", xb]})
    C("sketch.line", sketch=sk, **{"from": ["1500 mm", xb], "to": ["1500 mm", xa]})
    C("sketch.line", sketch=sk, **{"from": ["1500 mm", xa], "to": "e1"})
    C("feature.extrude", **when(dict(sketch=sk, distance="3000 mm", symmetric=True, name=tag), cond))


def envelope(tag, off_hull, off_deck):
    """The intersection of the panels' solids, both sides: tag "" is the outside of the planking,
    "In" its inside (each trace moved inward by the plywood's thickness)."""
    for j in PANELS:
        trace_solid(f"{tag}Cyl{j}", j, off_deck if j == "D" else off_hull, ext=j != 0, cond=EXISTS[j])
    prev = f"{tag}Cyl0"
    for k in NM:
        C("feature.boolean", op="intersect", target=prev, tool=f"{tag}Cyl{k}", name=f"{tag}Half{k}")
        prev = f"{tag}Half{k}"
    C("feature.mirror", source=prev, normal=[0, 1, 0], keep=True, name=f"{tag}Port")
    C("feature.boolean", op="intersect", target=prev, tool=f"{tag}Port", name=f"{tag}Hull")


envelope("", "0 mm", "0 mm")


def face(j, port=False):
    """The envelope's face of panel j ("D": the deck), starboard or port."""
    if j == 0:
        return f"Hull:copy({1 if port else 0})/Cyl0:side(e3)"
    k = "D" if j == "D" else NM[j - 1]
    inner = f"Half{k}:copy(1)/Cyl{k}:side(e3)"
    return f"Hull:copy(1)/Port:copy(0)/{inner}" if port else f"Hull:copy(0)/{inner}"


def edge(a, b):
    return f"Hull:between[{a},{b}]"


KEEL = edge(face(0), face(0, True))
RIDGE = edge(face("D"), face("D", True))
CAPA, CAPB = "Hull:copy(0)/Cyl0:side(e10)", "Hull:copy(0)/Cyl0:side(e5)"


def chine(k, port):
    return KEEL if k == 0 else edge(face(k - 1, port), face(k, port))


def sheer(nn, port):
    return edge(face(nn - 1, port), face("D", port))


done(1)

# ================================================================ the plywood: plates on the envelope's faces
# Plated on feature.developable's sheets between the chines instead, the panels above the bottom one fail
# today (a topside's offset folds over, the port ends' corners are not reached, a skin does not unfold, the
# flat panels lie another way: plan/repro/repro-sea-kayak-14.json in 3DCraft), the bottom panel's connection
# has a fold cone (not yet unfoldable) and the deck's is refused (repro 8); so every plate is on the envelope.
# Each panel is the envelope's face given its thickness inwards (side in). Keel and chines: the inner edges
# touch (the outside V is the epoxy fillet). Sheer: the topside rests under the deck, which covers its edge.
# Ridge: the deck panels touch. Ends: on the planes where the plywood ends. The topside and the deck depend
# on the number of chines (which panel the sheer is on), so they come in one version per number of panels.
C("datum.plane", **{"from": "yz", "distance": "Xa", "name": "EndA"})
C("datum.plane", **{"from": "yz", "distance": "Xb", "name": "EndB"})
SIDES = [(False, "S"), (True, "P")]


def ends(me):
    return [{"edge": edge(me, CAPA), "kind": "onto", "onto": "EndA"},
            {"edge": edge(me, CAPB), "kind": "onto", "onto": "EndB"}]


PLATES = {"S": [], "P": []}   # (name, when, panel, row on the floor)
for port, tag in SIDES:
    for j in range(4):
        me = face(j, port)
        low = ({"edge": KEEL, "kind": "touch", "with": face(0, not port)} if j == 0 else
               {"edge": chine(j, port), "kind": "touch", "with": face(j - 1, port)})
        if j < 3:   # a panel below the topside touches the next one up
            nm = f"Plank{j}{tag}"
            C("feature.plate", faces=[me], thickness="tHull", side="in", name=nm, when=f"n > {j + 1}",
              joints=ends(me) + [low, {"edge": chine(j + 1, port), "kind": "touch", "with": face(j + 1, port)}])
            PLATES[tag].append((nm, f"n > {j + 1}", j, j))
        if j > 0:   # the topside of a hull of j + 1 panels a side rests under the deck
            nm = f"Top{j + 1}{tag}"
            C("feature.plate", faces=[me], thickness="tHull", side="in", name=nm, when=f"n == {j + 1}",
              joints=ends(me) + [low, {"edge": sheer(j + 1, port), "kind": "under", "with": face("D", port),
                                       "thickness": "tDeck"}])
            PLATES[tag].append((nm, f"n == {j + 1}", j, j))
    me = face("D", port)
    for nn in (2, 3, 4):
        nm = f"Deck{nn}{tag}"
        C("feature.plate", faces=[me], thickness="tDeck", side="in", name=nm, when=f"n == {nn}",
          joints=ends(me) + [{"edge": sheer(nn, port), "kind": "over", "with": face(nn - 1, port),
                              "thickness": "tHull"},
                             {"edge": RIDGE, "kind": "touch", "with": face("D", not port)}])
        PLATES[tag].append((nm, f"n == {nn}", "D", 4))


def madeby(names):
    return {"any": [{"madeBy": nm} for nm in names]}


def solids(names):
    """The solid bodies made from these features (the plates, through the cuts later made in them)."""
    return {"kind": "body", "where": {"all": [madeby(names), {"volume": {"min": "1 mm^3"}}]}}


def plates_of(tag, panel_test):
    return [p[0] for p in PLATES[tag] if panel_test(p[2])]


done(2)

# ================================================================ the cockpit's place (the trim: see the README)
V("legReach", "0.57 * hPad")          # seat back to the foot brace (the fore bulkhead), legs nearly straight
V("xBack", "Xmid - 230 mm")           # the seat back, behind the widest station
V("xBkF", "xBack + legReach")         # fore bulkhead
V("xBkA", "xBack - bkAft")            # aft bulkhead
V("xHatF", "xBkF + 300 mm")           # hatch centres
V("xHatA", "xBkA - 330 mm")
# Keyhole: the convex hull of an aft circle (r1) and a forward one (r2), centres dK apart.
V("r1", "cockW / 2")
V("r2", "0.62 * cockW / 2")
V("dK", "cockL - r1 - r2")
V("alK", "asin((r1 - r2) / dK)")
V("xKey1", "xBack - backGap + r1")
V("xKey2", "xKey1 + dK")
V("Pkey", "r1 * (pi + 2 * alK / 1 rad) + r2 * (pi - 2 * alK / 1 rad) + 2 * dK * cos(alK)")

# ================================================================ sheer clamps
# A strip clampB thick against the topside's inside and clampA deep under the deck's inside, from 15 % to
# 85 % of the length: the region between the topside's inner skin and that skin moved clampB inward, and
# between the deck's inner skin and that moved clampA inward. One version per number of panels.
V("Xc1", at(X, "0.15"))
V("Xc2", at(X, "0.85"))
for nn in (2, 3, 4):
    cond = f"n == {nn}"
    trace_solid(f"ClT{nn}a", nn - 1, "tHull", cond=cond)
    trace_solid(f"ClT{nn}b", nn - 1, "tHull + clampB", cond=cond)
    trace_solid(f"ClD{nn}a", "D", "tDeck", cond=cond)
    trace_solid(f"ClD{nn}b", "D", "tDeck + clampA", cond=cond)
    C("feature.boolean", op="subtract", target=f"ClT{nn}a", tool=f"ClT{nn}b", name=f"ClT{nn}", when=cond)
    C("feature.boolean", op="subtract", target=f"ClD{nn}a", tool=f"ClD{nn}b", name=f"ClD{nn}", when=cond)
    C("feature.block", size=["Xc2 - Xc1", "1000 mm", "1000 mm"], position=["Xc1", "0 mm", "-100 mm"],
      name=f"ClBox{nn}", when=cond)
    C("feature.boolean", op="intersect", target=f"ClT{nn}", tool=f"ClD{nn}", name=f"ClTD{nn}", when=cond)
    C("feature.boolean", op="intersect", target=f"ClTD{nn}", tool=f"ClBox{nn}", name=f"Clamp{nn}S", when=cond)
    C("feature.mirror", source=f"Clamp{nn}S", normal=[0, 1, 0], keep=True, name=f"Clamp{nn}P", when=cond)
CLAMPS = [f"Clamp{nn}{t}" for nn in (2, 3, 4) for t in "SP"]
done(3)

# ================================================================ bulkheads (with hatches)
# The inside of the planking (the envelope with every trace moved inward by the plywood), cut to a slab
# tHull thick at each bulkhead's station, less the sheer clamps.
envelope("In", "tHull", "tDeck")
for bk, xv in (("Fore", "xBkF"), ("Aft", "xBkA")):
    C("feature.block", size=["tHull", "1000 mm", "1000 mm"], position=[f"{xv} - tHull / 2", "-500 mm", "-100 mm"],
      name=f"BkSlab{bk}", when="hatches")
    C("feature.boolean", op="intersect", target=f"BkSlab{bk}", tool="InHull", keepTool=True, name=f"Bk{bk}0",
      when="hatches")
    prev = f"Bk{bk}0"
    for k, cl in enumerate(CLAMPS):
        nm = f"Bulkhead{bk}" if k == len(CLAMPS) - 1 else f"Bk{bk}{k + 1}"
        C("feature.boolean", op="subtract", target=prev, tool=cl, keepTool=True, name=nm, when="hatches")
        prev = nm
done(4)

# ================================================================ the ends: the hull runs to the stems, end pours
# Beyond the end planes (eta < ea, eta > eb) the panels are only millimetres wide, too narrow to plate: the
# hull's surfaces run on to near the tips (eta = et), and what they enclose there is the end pour of
# thickened epoxy a stitch-and-glue builder puts in each end (the panels' faces outside it). Inside the
# plywood hull the end pour goes on for pourL past each end plane: the inside of the planking within it.
# An optional hardwood stem strip (endCap) runs along the keel line of each end.
V("et", "0.004")
V("ex2", "0.002")
V("XT1", at(X, "et"))
V("XT2", at(X, "1 - et"))
V("XT1b", at(X, "et - ex2"))
V("XT2b", at(X, "1 - et + ex2"))
V("pourL", "120 mm")
V("stripT", "4 mm")
V("stripW", "10 mm")
for j in PANELS:
    rng = ("et", "1 - et", "XT1", "XT2") if j == 0 else ("et - ex2", "1 - et + ex2", "XT1b", "XT2b")
    trace_solid(f"TipCyl{j}", j, "0 mm", cond=EXISTS[j], rng=rng)
prev = "TipCyl0"
for k in NM:
    C("feature.boolean", op="intersect", target=prev, tool=f"TipCyl{k}", name=f"TipHalf{k}")
    prev = f"TipHalf{k}"
C("feature.mirror", source=prev, normal=[0, 1, 0], keep=True, name="TipPort")
C("feature.boolean", op="intersect", target=prev, tool="TipPort", name="TipStock")
C("feature.block", size=["Lhull", "2000 mm", "2000 mm"], position=["Xa", "-1000 mm", "-500 mm"], name="TipSlab")
C("feature.boolean", op="subtract", target="TipStock", tool="TipSlab", name="EndPourTips")
# The stem strip: stripT deep and stripW wide under the keel line, from near the tip to eta = 0.07 (0.93).
for e, (e0, e1) in (("Stern", ("et", "0.07")), ("Bow", ("0.93", "1 - et"))):
    sk = f"Strip{e}"
    C("sketch.create", plane="zx", name=sk)
    C("sketch.curve", sketch=sk, x=Z0, y=X, t=[e0, e1])
    C("sketch.curve", sketch=sk, x=f"{Z0} - stripT", y=X, t=[e0, e1])
    C("sketch.line", sketch=sk, **{"from": "e1", "to": "e4"})
    C("sketch.line", sketch=sk, **{"from": "e2", "to": "e5"})
    C("feature.extrude", sketch=sk, distance="stripW", symmetric=True, name=f"StemStrip{e}", when="endCap == 2")
for e, x0 in (("Stern", "Xa"), ("Bow", "Xb - pourL")):
    C("feature.block", size=["pourL", "1000 mm", "1000 mm"], position=[x0, "-500 mm", "-100 mm"], name=f"Pour{e}Slab")
    C("feature.boolean", op="intersect", target=f"Pour{e}Slab", tool="InHull", keepTool=True, name=f"EndPour{e}")
done(5)

# ================================================================ cockpit coaming and hatch covers
# The riser: the keyhole ring (riserT wide) outside the envelope and inside the envelope raised by riserH,
# so it stands riserH on the deck all round, following the crown. The lip: a ring lipW wide on top, between
# the envelope raised riserH and raised riserH + lipT. Hatch covers likewise, 22 mm proud of the deck.
V("zKeyLow", "Zmid - 60 mm")


def keyhole(sk, grow):
    R1, R2 = f"(r1 + {grow})", f"(r2 + {grow})"
    p1 = [f"xKey1 + {R1} * sin(alK)", f"{R1} * cos(alK)"]
    p2 = [f"xKey2 + {R2} * sin(alK)", f"{R2} * cos(alK)"]
    q2 = [p2[0], f"0 mm - {R2} * cos(alK)"]
    q1 = [p1[0], f"0 mm - {R1} * cos(alK)"]
    C("sketch.path", sketch=sk, start=p1, segments=[
        {"line": p2}, {"arc": q2, "center": ["xKey2", "0 mm"], "clockwise": True},
        {"line": q1}, {"arc": "start", "center": ["xKey1", "0 mm"], "clockwise": True}])


for nm, grows in (("RiserRing", ["0 mm", "riserT"]),):
    C("sketch.create", plane="xy", offset="zKeyLow", name=nm)
    for g_ in grows:
        keyhole(nm, g_)
    C("feature.extrude", sketch=nm, distance="400 mm", name=f"{nm}Stock")
for nm, up, cond in (("RaisedR", "riserH", None), ("RaisedH", "22 mm", "hatches")):
    C("feature.transform", **when(dict(source="Hull", keep=True, translate=["0 mm", "0 mm", up], name=nm), cond))
# The lip (LipRingStock within RaisedL, less RaisedR) is refused by the boolean: the two raised envelopes
# are taken as nearly coincident (plan/repro/repro-sea-kayak-10.json in 3DCraft); it is left out until then.
C("feature.boolean", op="subtract", target="RiserRingStock", tool="Hull", keepTool=True, name="RiserOut")
C("feature.boolean", op="intersect", target="RiserOut", tool="RaisedR", name="CoamingRiser")
for h, xv in (("Fore", "xHatF"), ("Aft", "xHatA")):
    C("sketch.create", plane="xy", offset="zKeyLow", name=f"Hat{h}")
    C("sketch.circle", sketch=f"Hat{h}", center=[xv, "0 mm"], radius="hatchR")
    C("feature.extrude", sketch=f"Hat{h}", distance="500 mm", name=f"Hat{h}Stock", when="hatches")
    C("feature.boolean", op="subtract", target=f"Hat{h}Stock", tool="Hull", keepTool=True, name=f"Hat{h}Out",
      when="hatches")
    C("feature.boolean", op="intersect", target=f"Hat{h}Out", tool="RaisedH", keepTool=h == "Fore",
      name=f"Hatch{h}", when="hatches")
done(6)

# ================================================================ stitch holes
# Holes of diameter holeD, holeIn in from the edge, along every seam that is stitched: the keel, the
# chines, the sheer and the ridge. The holes of a seam are at the same stations on both of its panels (the
# stations of one grid along the boat, in eta), each holeIn from the shared chine along its own panel's
# station line, so they pair up across the seam when the boat is stitched. The grid is closer towards the
# ends, where the panels bend most: eta = 1/2 + 0.44 (0.6 v + 0.4 sin(pi v / 2)), v from -1 to 1 in steps of
# 0.05 (about 130 mm apart amidships, 65 mm near the ends of a 5.3 m hull); each seam uses the stations
# where both its panels are wide enough (|v| <= its reach). A hole is a circle in the plane square to its
# panel's station normal, at the panel's own formulas, drilled through the plate; the flat panels carry the
# holes (an unfold keeps holes), so they are on the cut sheet.
NG = 41
GRID = [round(-1 + 0.05 * i, 4) for i in range(NG)]


def eta_v(v):
    return f"(0.5 + 0.44 * (0.6 * ({v}) + 0.4 * sin(pi * ({v}) / 2)))"


REACH = {"keel": 0.5, 1: 0.5, 2: 0.6, 3: 0.6, "sheer": 0.6, "ridge": 0.9}


for i, v in enumerate(GRID):
    V(f"etaG{i}", eta_v(v))
    V(f"GG{i}", f"4 * etaG{i} * (1 - etaG{i})")


def at_grid(expr, i):
    """expr (in t) at grid station i, with G read from GG_i to keep it short."""
    return at(expr.replace(G, f"GG{i}"), f"etaG{i}")


JOINTS = {0: (-0.375, 0.375), 1: (-0.475, 0.275)}   # puzzle joints of even and odd rows, in v (below)


def stations(seam, rows):
    """The seam's stations: within its reach, and not within two stations of a puzzle joint of either
    panel's row (where the joint is glued and taped), so a joint never runs into a hole whatever the
    panel's stretch along its chine."""
    near = [vj for r in rows for vj in JOINTS[r % 2]]
    return [v for v in GRID if abs(v) <= REACH[seam] + 1e-9 and all(abs(v - vj) > 0.08 for vj in near)]


def along(j, k, e):
    """P . d_j of chine k (4: the sheer) at eta e: the coordinate along panel j's direction."""
    if j == "D":
        return f"(-cos(crown) * ({at_grid(Y(4), e)}) + sin(crown) * ({at_grid(Z(4), e)}))"
    return f"(c{j} * ({at_grid(Y(k), e)}) + s{j} * ({at_grid(Z(k), e)}))"


for j in PANELS:
    C("datum.plane", **{"from": "zx", "about": "x", "angle": ("thD" if j == "D" else f"th{j}") + " + 90 deg",
                        "name": f"HolePlane{j}"})
# A joint sets a plate's outside edge back from the chine (the inner skins meet at the chine's station
# line, each panel turned by the seam's angle d): by its thickness x tan(d / 2). The holes are holeIn in
# from that edge, so holeIn + t tan(d / 2) from the chine along each panel.
V("dKeel", "2 * th0")
for k in (1, 2, 3):
    V(f"dCh{k}", f"th{k} - th{k - 1}")
V("dSheer", "thD - choose(n - 1, th1, th2, th3)")
V("dRidge", "2 * crown")
SEAM_ANGLE = {"keel": "dKeel", 1: "dCh1", 2: "dCh2", 3: "dCh3", "sheer": "dSheer", "ridge": "dRidge"}


def inset(seam, t):
    return f"(holeIn + {t} * tan({SEAM_ANGLE[seam]} / 2))"


HOLES = {}   # plate (starboard name without the side) -> number of holes
for nm, cond, j, row in PLATES["S"]:
    base = nm[:-1]
    if base.startswith("Plank"):
        seams = [("keel" if j == 0 else j, "lo", [0] if j == 0 else [j - 1, j]), (j + 1, "hi", [j, j + 1])]
    elif base.startswith("Top"):
        seams = [(j, "lo", [j - 1, j]), ("sheer", "hi", [j, 4])]
    else:
        m = int(base[4])    # Deck m: its topside is panel m - 1, on row m - 1
        seams = [("sheer", "lo", [m - 1, 4]), ("ridge", "hi", [4])]
    sk = f"Holes{base}"
    C("sketch.create", plane=f"HolePlane{j}", name=sk)
    count = 0
    for seam, where, rows in seams:
        for v in stations(seam, rows):
            e = GRID.index(v)
            t = "tDeck" if j == "D" else "tHull"
            a_ = inset(seam, t)
            if j == "D":
                c_ = f"{along('D', 4, e)} + {a_}" if where == "lo" else f"sin(crown) * {at_grid(ZR, e)} - {a_}"
            else:
                c_ = f"{along(j, j, e)} + {a_}" if where == "lo" else f"{along(j, j + 1, e)} - {a_}"
            C("sketch.circle", sketch=sk, center=[f"0 mm - ({c_})", at(X, f"etaG{e}")], radius="holeD / 2")
            count += 1
    HOLES[base] = (count, cond)
    C("feature.extrude", sketch=sk, distance="1500 mm", symmetric=True, name=f"Drill{base}S", when=cond)
    C("feature.mirror", source=f"Drill{base}S", normal=[0, 1, 0], keep=True, name=f"Drill{base}P", when=cond)
    for t in "SP":
        C("feature.boolean", op="subtract", target=f"{base}{t}", tool=f"Drill{base}{t}", name=f"{base}{t}h", when=cond)
FLATS = []   # (flat name, when, row)
done(7)

# ================================================================ the flat panels on the floor
# The outside skin of every starboard plate laid flat (cut two of each, stacked face to face, for the pair),
# one row per panel beside the boat, its stern end at x = Xa.
def row_y(r):
    return f"0 mm - Ymid - 350 mm - {r} * {ROW} mm"


for nm, cond, j, row in PLATES["S"]:
    fl = f"Flat{nm[:-1]}"
    C("feature.unfold", faces=[f"{nm}:copy(0)/{face(j)}"], at=["Xa", row_y(row), f"{FLOOR} mm"], angle="-90 deg",
      name=fl, when=cond)
    FLATS.append((fl, cond, row))

# Each flat panel is cut into three pieces at two puzzle joints (a panel is longer than a 2440 mm sheet),
# staggered from row to row so that the joints never line up on the hull. A joint is a line across the
# panel with a dovetail key every 73 mm (wherever the panel lies across the row, keys fall on it); the
# middle piece moves PIECE_GAP along, the last twice that.
# Joints lie half way between two stations of the hole grid (v = +-0.375 on even rows, -0.475 and 0.275 on
# odd rows), at about that station's distance along the flat panel (x from the end plane, 0.4 % longer:
# the panels' lengths along their chines); the seams leave out the stations near them (above).
KEYS = range(-6, 3)   # key centres: row line + k * 73 mm


def joint_line(xj, yr, up):
    """Points of a joint at x = xj across the row (from below to above when up, else back down)."""
    pts = []
    for k in KEYS:
        yc = f"{yr} + 31 mm + {k} * 73 mm"
        pts += [[xj, f"{yc} - 12 mm"], [f"{xj} + 18 mm", f"{yc} - 20 mm"], [f"{xj} + 18 mm", f"{yc} + 20 mm"],
                [xj, f"{yc} + 12 mm"]]
    return pts if up else pts[::-1]


for r in range(5):
    yr = row_y(r)
    j1, j2 = (f"(Xa + ({at(X, eta_v(v))} - Xa) * 1.004)" for v in JOINTS[r % 2])
    # the regions reach 1500 mm either side of the row (only their flat panel is cut by them, and a panel
    # bows across its row by a few hundred millimetres), the keys in the middle
    lo, hi = f"{yr} - 1500 mm", f"{yr} + 1500 mm"
    regions = {
        "a": [["Xa - 300 mm", lo], [j1, lo]] + joint_line(j1, yr, True) + [[j1, hi], ["Xa - 300 mm", hi]],
        "b": [[j1, lo], [j2, lo]] + joint_line(j2, yr, True) + [[j2, hi], [j1, hi]] + joint_line(j1, yr, False),
        "c": [[j2, lo], ["Xb + 600 mm", lo], ["Xb + 600 mm", hi], [j2, hi]] + joint_line(j2, yr, False),
    }
    for pc, pts in regions.items():
        sk = f"Cut{r}{pc}"
        C("sketch.create", plane="xy", offset=f"{FLOOR - 20} mm", name=sk)
        C("sketch.polyline", sketch=sk, points=pts, closed=True)
        C("feature.extrude", sketch=sk, distance="40 mm", name=f"Cutter{r}{pc}")
PIECES = {pc: [] for pc in "abc"}
for fl, cond, row in FLATS:
    C("feature.transform", source=fl, keep=True, name=f"{fl}_b0", when=cond)
    C("feature.transform", source=fl, keep=True, name=f"{fl}_c0", when=cond)
    for k, pc in enumerate("abc"):
        src = fl if pc == "a" else f"{fl}_{pc}0"
        nm = f"{fl}{pc}" if pc == "a" else f"{fl}_{pc}1"
        C("feature.boolean", op="intersect", target=src, tool=f"Cutter{row}{pc}", keepTool=True, name=nm, when=cond)
        if pc != "a":
            C("feature.transform", source=nm, translate=[f"{k * PIECE_GAP} mm", "0 mm", "0 mm"], name=f"{fl}{pc}",
              when=cond)
        PIECES[pc].append((f"{fl}{pc}", row))

# The coaming's riser developed and the bulkheads laid flat: feature.unfold refuses these faces (a face of
# a cut whose boundary "does not close in the surface's parameters", plan/repro/repro-sea-kayak-11.json in
# 3DCraft). The bulkheads are flat already, and go on the cut sheet as they are; the riser's strip waits.
done(8)

# ================================================================ materials, weight, hydrostatics
WOODP = [p[0] for t in "SP" for p in PLATES[t]]
for nm in WOODP:
    C("body.material", body=nm, name="okoume plywood", density="rhoPly")
# The boat's weight, from formulas: plywood (its area as a coefficient of the panels' widths, kA from the
# table of ends, checked against the kernel's mass of the plates below), glass and epoxy, sheer clamps,
# coaming, bulkheads and fittings.
V("kA", "forms[form].kA")
V("aHull", "kA * L * 2 * (W0 + W1 + W2 + W3) / (1 m)^2")
V("aDeck", "forms[form].kD * L * 2 * Ymid / cos(crown) / (1 m)^2")
V("mPly", "rhoPly * (aHull * tHull + aDeck * tDeck) / (1 m)")
V("mGlass", "glassHull * aHull + glassDeck * aDeck")
V("mClamps", "rhoWood * 2 * clampA * clampB * (Xc2 - Xc1) / (1 m)^3")
V("mCoam", "rhoWood * Pkey * riserT * 70 mm / (1 m)^3")
V("mBulk", "hatches * rhoPly * tHull * 2 * 0.6 * 2 * Ymid * (Zmid + Ymid * tc) / (1 m)^3")
V("mBoat", "mPly + mGlass + mClamps + mCoam + mBulk + fittings + 0.6")   # 0.6 kg: end pours and stem strips
V("mTotal", "mPad + payload + mBoat")
V("Vdisp", "mTotal / rho * (1 m)^3")
# What the hull carries with the sheer 45 mm above the water (a block coefficient of the volume below that
# plane, on the safe side of the kernel's measure.below over the corners of the hull's ranges), less the
# boat: it bounds the paddler's and the load's ranges.
V("kCap", "forms[form].kCap - 0.00017 * (rockB + rockS - 470 mm) / (1 mm)")
V("mCap", "kCap * L * B * (Zmid - 45 mm) * rho / (1 m)^3 - mBoat")
# The heaviest paddler with GM >= 0 (sitting still), a bound on the safe side of the output GM over the
# corners of the ranges (narrow, deep hulls are the tender ones); the GM assertion checks it at every point.
V("mStab", "93 + 0.3 * (B - 530 mm) / (1 mm)")
done(9)

# ================================================================ assertions
def plates_where(tag, names):
    return solids([p for p in names])


def panel_set(tag, k):
    """The plate of panel k (a panel under the topside, or the topside), whichever this hull has."""
    return [p[0] for p in PLATES[tag] if p[2] == k]


def tops(tag, below):
    return [p[0] for p in PLATES[tag] if p[0].startswith("Top") and int(p[0][3]) <= below]


def decks(tag, upto):
    return [p[0] for p in PLATES[tag] if p[0].startswith("Deck") and int(p[0][4]) <= upto]


for port, tag in SIDES:
    side = "starboard" if tag == "S" else "port"
    for k in (1, 2, 3):
        # chine k; on a hull with fewer chines the same pair is the topside and the deck (the sheer)
        frm = panel_set(tag, k - 1) + tops(tag, k)
        to = panel_set(tag, k) + decks(tag, k)
        A(f"chine {k} ({side}): the panels' inner edges touch (on a hull with fewer chines: the sheer)",
          measure="distance", **{"from": solids(frm), "to": solids(to)}, eq="0 mm", tol="0.01 mm")
    A(f"sheer ({side}): the deck rests on the topside", measure="distance",
      **{"from": solids(tops(tag, 4)), "to": solids(decks(tag, 4))}, eq="0 mm", tol="0.01 mm")
A("keel: the bottom panels' inner edges touch", measure="distance",
  **{"from": solids(panel_set("S", 0)), "to": solids(panel_set("P", 0))}, eq="0 mm", tol="0.01 mm")
A("ridge: the deck panels' inner edges touch", measure="distance",
  **{"from": solids(decks("S", 4)), "to": solids(decks("P", 4))}, eq="0 mm", tol="0.01 mm")
PANELFACES = {"kind": "face", "where": {"all": [{"in": "Hull"}, {"name": "*side(e3)"}]}}
A("the panels are developable (the envelope's faces the plates are made of)", measure="developable",
  of=PANELFACES, **{"is": True})
A("the panels' Gaussian curvature", measure="curvature", of=PANELFACES, max="1e-9 / (1 mm)^2")
A("plywood: the kernel's mass of the plates is the weight formula's", measure="mass", of=solids(WOODP),
  eq="mPly", tol="mPly / 25")
A("freeboard: the waterline for boat, paddler and load lies 45 mm below the sheer amidships",
  measure="levelFor", of="Hull", volume="Vdisp", max="Zmid - 45 mm")
A("the end pours at the stems are dry: above the highest waterline the freeboard allows", measure="boxMin",
  of="EndPourTips", axis="z", min="Zmid - 45 mm")
A("the coaming stands on the deck", measure="distance", **{"from": "CoamingRiser", "to": solids(decks("S", 4))},
  eq="0 mm", tol="0.01 mm")
A("the cockpit lets the knees in (buttock-knee 0.34 x stature, room behind the seat back)", measure="extent",
  of="CoamingRiser", axis="x", min="0.34 * hPad + backGap + 2 * riserT")
for pc in "abc":
    for par in (0, 1):
        names = [nm for nm, row in PIECES[pc] if row % 2 == par]
        A(f"the flat panels' piece {pc} (rows {'0, 2, 4' if par == 0 else '1, 3'}) fits a 2440 mm sheet",
          measure="extent", of={"kind": "body", "where": madeby(names)}, axis="x", max="2440 mm - 20 mm")

# Stitch holes: inside the panels (their walls at least holeIn - holeD / 2 from their plate's rims, less
# 0.5 mm), every one drilled (no puzzle joint can run into one: the seams leave out the stations within
# two of a joint; a hole laid flat is two or three spline pieces, so the flat pieces are not counted), paired
# across the seams (the walls of the two nearest holes across a seam are no farther apart than two holes
# at one station, a and b either side of the chine: |a d1 + b d2| - holeD, with 0.5 mm to spare).
def drilled(names):
    """The plates' bodies after their holes are drilled (the boolean named after each plate, + h)."""
    return {"any": [{"in": f"{nm}h"} for nm in names]}


def panel_group(tag, panels):
    return [p[0] for p in PLATES[tag] if p[2] in panels]


# The holes' distance from the plates' rims is not asserted: measuring it between the holes and the rims of
# thin plates takes minutes per plate (plan/repro/repro-sea-kayak-13.json in 3DCraft). The holes are set
# holeIn + t tan(d / 2) in from the chine, which is holeIn from the plate's edge after its joint.
expected = " + ".join(f"if({cond}, {cnt}, 0)" for cnt, cond in HOLES.values())
A("every stitch hole is drilled (starboard; the port side the same)", measure="count",
  of={"kind": "face", "where": {"all": [drilled([p[0] for p in PLATES["S"]]), {"hole": True}]}},
  eq=expected, tol="0")


def pair(a, b, d):
    return f"sqrt({a}^2 + {b}^2 + 2 * {a} * {b} * cos({d})) - holeD + 0.5 mm"


def holes_of(names):
    return {"kind": "face", "where": {"all": [drilled(names), {"hole": True}]}}


A("keel: the stitch holes pair up across the seam", measure="distance",
  **{"from": holes_of(panel_set("S", 0)), "to": holes_of(panel_set("P", 0))},
  max=pair(inset("keel", "tHull"), inset("keel", "tHull"), "dKeel"))
for port, tag in SIDES:
    side = "starboard" if tag == "S" else "port"
    A(f"chine 1 ({side}): the stitch holes pair up across the seam", measure="distance",
      **{"from": holes_of(panel_set(tag, 0)), "to": holes_of(panel_set(tag, 1))},
      max=pair(inset(1, "tHull"), inset(1, "tHull"), "dCh1"))
    A(f"sheer ({side}): the stitch holes pair up across the seam", measure="distance",
      **{"from": holes_of(tops(tag, 4)), "to": holes_of(decks(tag, 4))},
      max=pair(inset("sheer", "tHull"), inset("sheer", "tDeck"), "dSheer"))
A("ridge: the stitch holes pair up across the seam", measure="distance",
  **{"from": holes_of(decks("S", 4)), "to": holes_of(decks("P", 4))},
  max=pair(inset("ridge", "tDeck"), inset("ridge", "tDeck"), "dRidge"))

# No volume shared between neighbouring plates: the overlap measure (a boolean intersection of the two
# drilled plates, which must leave nothing) for every pair of hull panels (so the keel and every chine,
# whatever the number of chines) and for the deck panels at the ridge. The topside and the deck
# at the sheer share the deck's skin (the deck rests on the topside), which the boolean does not take yet
# (coincident freeform skins: the Ov3D case of plan/repro/repro-sea-kayak-12.json in 3DCraft), so the sheer
# is proven by its distance alone until then.
def drilled_solids(names):
    return {"kind": "body", "where": drilled(names)}


HULLPLATES = [p[0] for t in "SP" for p in PLATES[t] if p[2] != "D"]
A("keel and chines: no two hull panels share any volume", measure="overlap", of=drilled_solids(HULLPLATES),
  **{"is": False})
A("ridge: the deck panels share no volume", measure="overlap", of=drilled_solids(decks("S", 4)),
  to=drilled_solids(decks("P", 4)), **{"is": False})
done(10)

# ================================================================ hydrostatics, as outputs of 3DCraft's measures
# Read-only outputs (variable.measure, variable.output): the waterline for the weight, the centre of
# buoyancy, the waterplane and its transverse moment, then KB, BM = I / V, KM, KG, GM (Biran & Lopez-Pulido,
# ch. 2-3). KG: the plywood's centre of gravity from the kernel (glass and fittings taken with it), the
# paddler's 254 mm above a 25 mm seat pad on the floor amidships, the load at 100 mm.
C("feature.block", size=["10 mm", "2000 mm", "2000 mm"], position=["Xmid - 5 mm", "-1000 mm", "-500 mm"],
  name="MidSlab")
C("feature.boolean", op="intersect", target="MidSlab", tool="Hull", keepTool=True, name="MidSlice")
C("feature.visible", feature=["MidSlice"], visible=False)
WATER = dict(of="Hull", plane="xy", offset="T")
OUT = [("T", dict(measure="levelFor", of="Hull", volume="Vdisp")),
       ("Vb", dict(measure="volumeBelow", **WATER)),
       ("KB", dict(measure="centroidBelow", axis="z", **WATER)),
       ("LCB", dict(measure="centroidBelow", axis="x", **WATER)),
       ("Awp", dict(measure="sectionArea", **WATER)),
       ("IT", dict(measure="sectionInertia", about="x", **WATER)),
       ("Amid", dict(measure="volumeBelow", of="MidSlice", plane="xy", offset="T")),
       ("zPly", dict(measure="centerOfMass", of=solids(WOODP), axis="z")),
       ("xPly", dict(measure="centerOfMass", of=solids(WOODP), axis="x"))]
for nm, kw in OUT:
    C("variable.measure", name=nm, wait=False, **kw)
for nm, ex in [("BM", "IT / Vb"), ("KM", "KB + BM"),
               ("KG", "(mBoat * zPly + mPad * (tHull + 25 mm + cgUp) + payload * 100 mm) / mTotal"),
               ("GM", "KM - KG"),
               ("LCG", "(mBoat * xPly + mPad * (xBack + cgFwd) + payload * (xBack + 250 mm)) / mTotal"),
               ("trim", "LCB - LCG"),
               ("Amidship", "Amid / 10 mm"),
               ("freeboard", "Zmid - T")]:
    C("variable.output", name=nm, expr=ex, wait=False)
A("initial stability: GM = KB + BM - KG >= 0", measure="value", expr="GM", min="0 mm")

# ================================================================ what is shown, the cut sheet
HIDE = (["Hull", "InHull", "EndA", "EndB"] + [s[1]["name"] for s in steps if s[0] in ("datum.plane", "sketch.create")]
        + [f"Cutter{r}{pc}" for r in range(5) for pc in "abc"])
C("feature.visible", feature=HIDE, visible=False)
for t in "SP":
    for nm, cond, j, row in PLATES[t]:
        C("body.appearance", body=nm, color=COPPER if j == "D" else OKOUME)
for pc in "abc":
    for nm, row in PIECES[pc]:
        C("body.appearance", body=nm, color=COPPER if row == 4 else OKOUME)
for nm in CLAMPS:
    C("body.appearance", body=nm, color=CREAM)
for nm in ("CoamingRiser", "HatchFore", "HatchAft", "StemStripStern", "StemStripBow"):
    C("body.appearance", body=nm, color=WALNUT)
for nm in ("EndPourTips", "EndPourStern", "EndPourBow"):
    C("body.appearance", body=nm, color="#B8954A")
for nm in ("BulkheadFore", "BulkheadAft"):
    C("body.appearance", body=nm, color=OKOUME)
C("set.define", name="Cut sheet: panels", kind="face", where={"any": [{"in": nm} for pc in "abc" for nm, r in PIECES[pc]]})
C("set.define", name="Cut sheet: bulkheads", kind="face",
  where={"all": [madeby(["BulkheadFore", "BulkheadAft"]), {"normal": {"along": "x"}}]})

# ================================================================ the form
G1, G2, G3, G4 = "Hull", "Paddler and load", "Plywood", "Cockpit and hatches"
params = [
    {"name": "L", "label": "Length overall", "group": G1, "order": 1, "min": "5000 mm", "max": "5800 mm",
     "step": "10 mm", "unit": "mm", "description": "Tip to tip"},
    {"name": "B", "label": "Beam", "group": G1, "order": 2, "min": "if(chines == 1, 570 mm, 530 mm)",
     "max": "600 mm", "step": "5 mm", "unit": "mm",
     "description": "Widest beam at the sheer; at least 570 mm with one chine"},
    {"name": "D", "label": "Depth at the sheer", "group": G1, "order": 3, "min": "170 mm",
     "max": "min(230 mm, 0.35 * B)", "step": "5 mm", "unit": "mm",
     "description": "Keel to sheer at the widest station; the deck's crown comes on top. At most 0.35 x beam: deeper hulls carry their weight too high (GM)"},
    {"name": "crown", "label": "Deck crown", "group": G1, "order": 4, "min": "12 deg", "max": "26 deg",
     "step": "1 deg", "unit": "deg", "description": "Angle of the deck panels from the horizontal"},
    {"name": "rockB", "label": "Bow rise", "group": G1, "order": 5, "min": "250 mm", "max": "400 mm",
     "step": "5 mm", "unit": "mm", "description": "Rocker: how high the keel rises to the bow tip"},
    {"name": "rockS", "label": "Stern rise", "group": G1, "order": 6, "min": "220 mm", "max": "350 mm",
     "step": "5 mm", "unit": "mm", "description": "How high the keel rises to the stern tip"},
    {"name": "xmax", "label": "Widest station", "group": G1, "order": 7, "min": "0.44", "max": "0.52",
     "step": "0.005", "description": "Where the beam is widest, as a fraction of the length from the stern"},
    {"name": "chines", "label": "Chines per side", "group": G1, "order": 8, "kind": "integer", "min": "1",
     "max": "3", "description": "Hard chines between keel and sheer on each side: 2 to 4 hull panels a side"},
    {"name": "form", "label": "Ends", "group": G1, "order": 9, "kind": "choice", "choicesFrom": "forms",
     "description": "How fast the bottom panels narrow towards the ends"},
    {"name": "endCap", "label": "End cap", "group": G1, "order": 10, "kind": "choice", "choicesFrom": "endcaps",
     "description": "A hardwood strip along the stem and stern, or none"},
    {"name": "mPad", "label": "Paddler weight (kg)", "group": G2, "order": 1, "min": "45",
     "max": "min(min(110, floor(mCap)), floor(mStab))", "step": "1",
     "description": "The paddler, in kg: at most what the hull carries with the sheer 45 mm above the water"},
    {"name": "hPad", "label": "Paddler height", "group": G2, "order": 2, "min": "1500 mm", "max": "2000 mm",
     "step": "10 mm", "unit": "mm", "description": "Stature: sets the cockpit's length and the foot brace"},
    {"name": "payload", "label": "Load (kg)", "group": G2, "order": 3, "min": "0",
     "max": "clamp(floor(mCap - mPad), 0, 40)", "step": "1",
     "description": "Gear in the compartments, in kg; at most what the hull carries besides the paddler"},
    {"name": "water", "label": "Water", "group": G2, "order": 4, "kind": "choice", "choicesFrom": "waters",
     "description": "Sea water (1025 kg/m3) or fresh water (1000 kg/m3)"},
    {"name": "tHull", "label": "Hull plywood", "group": G3, "order": 1, "min": "3 mm", "max": "5 mm",
     "step": "0.5 mm", "unit": "mm", "description": "Okoume plywood for the hull panels and bulkheads"},
    {"name": "tDeck", "label": "Deck plywood", "group": G3, "order": 2, "min": "3 mm", "max": "4 mm",
     "step": "0.5 mm", "unit": "mm", "description": "Okoume plywood for the deck panels"},
    {"name": "cockL", "label": "Cockpit length", "group": G4, "order": 1, "min": "0.34 * hPad + 100 mm",
     "max": "min(950 mm, legReach + backGap - 100 mm)", "step": "5 mm", "unit": "mm",
     "description": "Keyhole opening: at least the buttock-knee length (0.34 x stature) plus room behind the seat"},
    {"name": "cockW", "label": "Cockpit width", "group": G4, "order": 2, "min": "380 mm", "max": "460 mm",
     "step": "5 mm", "unit": "mm", "description": "Keyhole opening at its widest (aft) end"},
    {"name": "holeD", "label": "Stitch hole diameter", "group": G3, "order": 3, "min": "1.5 mm", "max": "3 mm",
     "step": "0.5 mm", "unit": "mm", "description": "Holes for the copper wire stitches"},
    {"name": "holeIn", "label": "Stitch hole edge distance", "group": G3, "order": 4, "min": "6 mm",
     "max": "10 mm", "step": "0.5 mm", "unit": "mm", "description": "From the panel's edge to the hole's centre"},
    {"name": "hatches", "label": "Bulkheads and hatches", "group": G4, "order": 3, "kind": "boolean",
     "description": "Fore and aft bulkheads with round hatches (off: an open hull for float bags)"},
]
for p_ in params:
    C("variable.publish", **p_)
C("document.info",
  title="Sea kayak (stitch and glue)",
  description="A Greenland-style multichine sea kayak in okoume plywood, built stitch and glue entirely by "
              "3DCraft from formulas: the hull is the meeting of its developable panels, every panel a plate "
              "whose inner edges touch its neighbours, the deck on the topsides, sheer clamps, bulkheads and "
              "hatches, a keyhole coaming, end pours at the stems, and every panel laid flat in three puzzle-"
              "jointed pieces with its stitch holes. Export the sets Cut sheet: panels and Cut sheet: bulkheads.",
  author="3DCraft Jigs", licence="CC-BY-4.0",
  url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/sea-kayak",
  tags=["kayak", "boat", "stitch and glue", "plywood", "developable", "plate", "unfold", "hydrostatics",
        "cut sheet", "formula"])
C("assert.list")
C("output.list")
C("jig.export", path="dist/sea-kayak.3dcraftjig")
done(99)
