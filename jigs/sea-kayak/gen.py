#!/usr/bin/env python3
"""Writes build.json of the sea-kayak Jig:  python3 -I gen.py > build.json

A multichine stitch-and-glue sea kayak in okoume plywood, Greenland style. Everything is built by 3DCraft
from formulas: this script only writes commands. It computes no geometry: no offsets, intersections,
unfolding, areas or hydrostatics. Those are 3DCraft's (feature.developable, feature.plate, feature.unfold,
measure.levelFor, measure.section and the assertions).

The lines
---------
x runs along the boat (stern -L/2, bow +L/2), y to starboard, z up from the keel's lowest point. A
station is eta in [0, 1] (0 the stern tip, 1 the bow tip), a skewed copy of xi = x / L + 1/2,
eta = xi + s xi (1 - xi), so that the widest station (eta = 1/2) lies at the fraction xmax of the length.
In every formula below `t` is eta.

Every hull panel j is a generalised cylinder: in every station it is a straight line at the same angle
th_j (its flare), from chine j to chine j + 1, with a width w_j(eta) = W_j G^p_j (1 + sp_j (1 - G)),
G = 4 eta (1 - eta). Its trace in the plane square to its direction d_j = (cos th_j, sin th_j) is the curve
(x, g_j(x)), g_j = P_j . (-sin th_j, cos th_j) for P_j the panel's lower chine. Extruded along d_j, the
region inside that curve is a solid whose curved face is the panel's surface; the ten solids (four hull
panels and the deck, each side) intersected are the hull envelope, and its edges are the keel, the chines
and the sheer, found by the kernel where neighbouring panels meet. The keel rises as
z0 = rA (q u^2 + (1 - q) u^4) + rC u^5 (u = 2 eta - 1): the u^2 term keeps the keel curved in the
middle, so that the connection of two chines is never degenerate there. The deck is a cylinder at the
crown angle from the sheer to a ridge on the centre line.

The panels are then the developable sheets between the envelope's edges (feature.developable), given
their thickness and joints (feature.plate: touching at the chines, the sheer panel under the deck),
and laid flat (feature.unfold) beside the boat.
"""
import json
import os
import re

STAGE = int(os.environ.get("STAGE", "99"))   # for development: stop after a stage
NP = 4            # hull panels a side (three chines)
FLOOR = -150      # mm: the floor the flat panels lie on, below the keel
GAP = 40          # mm between flat panels on the floor

OKOUME, WALNUT, CREAM, OCHRE, COPPER, PETROL = "#D9B98A", "#7A5638", "#E8DFCC", "#D4A24C", "#B87350", "#2E7D7A"

steps = []


def C(cmd, **p):
    steps.append([cmd, p])


def V(name, expr):
    C("variable.set", name=name, expr=expr)


def done(stage):
    if STAGE <= stage:
        print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
        raise SystemExit(0)


# ---------------------------------------------------------------- inputs
for n_, e in [("L", "5300 mm"), ("B", "545 mm"), ("D", "190 mm"), ("crown", "22 deg"),
              ("rockB", "300 mm"), ("rockS", "240 mm"), ("mPad", "80"), ("payload", "5"), ("water", "1")]:
    V(n_, e)
C("table.set", name="waters", columns=["water", "rho"], rows=[["Sea water", 1025], ["Fresh water", 1000]])

# ---------------------------------------------------------------- constants (sources in the README)
V("xmax", "0.47")       # the widest station, from the stern
V("pb", "1.0")          # how the bottom panel narrows to the ends (G^p; p <= 1 keeps every panel's trace convex)
V("pt", "0.8")          # ... and the topside
V("spring", "0.4")      # sheer spring: the upper panels stay wider towards the ends (sp_j <= p_j)
V("q", "0.3")           # share of the rocker that is a parabola (curvature in the middle)
V("ea", "0.03")         # the plywood hull runs from eta = ea to eb; the rest is the hardwood tips
V("eb", "0.97")
V("et", "0.004")        # the tips end here, a few millimetres wide
V("ex", "0.002")        # the cylinders reach a little past the tips, which the keel panel's cylinder sets
V("tHull", "4 mm")      # okoume plywood
V("tDeck", "3 mm")
V("rhoPly", "500")      # okoume plywood, kg/m^3 (CLC: a 4 mm 4 x 8 ft sheet weighs 13 lb)
V("rho", "waters[water].rho")

# ---------------------------------------------------------------- the lines, as formulas
V("s", "(0.5 - xmax) / (xmax * (1 - xmax))")
V("rA", "(rockB + rockS) / 2")
V("rC", "(rockB - rockS) / 2")
for j in range(NP):
    a, b = f"90 deg * {j} / {NP}", f"90 deg * {j + 1} / {NP}"
    # at the widest station the chines lie on a quarter ellipse (B / 2, D), equally spaced in angle
    V(f"dy{j}", f"B / 2 * (sin({b}) - sin({a}))")
    V(f"dz{j}", f"D * (cos({a}) - cos({b}))")
    V(f"W{j}", f"sqrt(dy{j}^2 + dz{j}^2)")
    V(f"c{j}", f"dy{j} / W{j}")
    V(f"s{j}", f"dz{j} / W{j}")
    V(f"th{j}", f"atan2(dz{j}, dy{j})")
    V(f"p{j}", f"pb + (pt - pb) * {j} / {NP - 1}")
    V(f"sp{j}", f"spring * p{j} * {j} / {NP - 1}")
V("thD", "180 deg - crown")

X = "((2 * t / ((1 + s) + sqrt((1 + s)^2 - 4 * s * t))) - 0.5) * L"
G = "(4 * t * (1 - t))"
Z0 = "(rA * (q * (2 * t - 1)^2 + (1 - q) * (2 * t - 1)^4) + rC * (2 * t - 1)^5)"


def w(m):
    return f"W{m} * pow({G}, p{m}) * (1 + sp{m} * (1 - {G}))"


def Y(k):
    return "0 mm" if k == 0 else " + ".join(f"{w(m)} * c{m}" for m in range(k))


def Z(k):
    return Z0 if k == 0 else Z0 + " + " + " + ".join(f"{w(m)} * s{m}" for m in range(k))


def trace(j):
    """The inward offset of panel j's cylinder, P . (-sin th_j, cos th_j) for a point P of its lower chine."""
    if j == "D":   # the deck: through the ridge z = Z4 + Y4 tan(crown) on the centre line
        return f"-cos(crown) * ({Z(NP)} + ({Y(NP)}) * tan(crown))"
    return " + ".join([f"c{j} * {Z0}"] + [f"{w(m)} * sin(th{m} - th{j})" for m in range(j)])


def at(expr, v):
    return re.sub(r"\bt\b", f"({v})", expr)


V("Xa", at(X, "ea"))
V("Xb", at(X, "eb"))
V("XA", at(X, "et"))
V("XB", at(X, "1 - et"))
V("XA2", at(X, "et - ex"))
V("XB2", at(X, "1 - et + ex"))
# the sheer at the widest station, and the ridge there (the deck's highest point amidships)
V("Ymid", at(Y(NP), "0.5"))
V("Zmid", at(Z(NP), "0.5"))

# ---------------------------------------------------------------- the hull envelope
# The keel panel's solid runs from the end plane at eta = ea to the one at eb (the plywood hull); the other
# solids run on nearly to the tips (et), and with a second keel solid of that length they make the two
# hardwood tips beyond the end planes, which so continue the hull's lines.
PANELS = list(range(NP)) + ["D"]
for j in PANELS + ["T"]:
    ta, tb, xa, xb = {0: ("ea", "eb", "Xa", "Xb"), "T": ("et", "1 - et", "XA", "XB")}.get(
        j, ("et - ex", "1 - et + ex", "XA2", "XB2"))
    if j != "T":
        C("datum.plane", **{"from": "zx", "about": "x", "angle": "thD" if j == "D" else f"th{j}", "name": f"Plane{j}"})
    C("sketch.create", plane="Plane0" if j == "T" else f"Plane{j}", name=f"Trace{j}")
    C("sketch.curve", sketch=f"Trace{j}", x=trace(0 if j == "T" else j), y=X, t=[ta, tb])
    C("sketch.line", sketch=f"Trace{j}", **{"from": "e2", "to": ["1500 mm", xb]})
    C("sketch.line", sketch=f"Trace{j}", **{"from": ["1500 mm", xb], "to": ["1500 mm", xa]})
    C("sketch.line", sketch=f"Trace{j}", **{"from": ["1500 mm", xa], "to": "e1"})
    C("feature.extrude", sketch=f"Trace{j}", distance="3000 mm", symmetric=True, name=f"Cyl{j}")
NM = [str(j) for j in range(1, NP)] + ["D"]
prev = "Cyl0"
for k in NM:
    C("feature.boolean", op="intersect", target=prev, tool=f"Cyl{k}", keepTool=True, name=f"Half{k}")
    prev = f"Half{k}"
C("feature.mirror", source=prev, normal=[0, 1, 0], keep=True, name="Port")
C("feature.boolean", op="intersect", target=prev, tool="Port", name="Hull")
prev = "CylT"
for k in NM:
    C("feature.boolean", op="intersect", target=prev, tool=f"Cyl{k}", name=f"TipHalf{k}")
    prev = f"TipHalf{k}"
C("feature.mirror", source=prev, normal=[0, 1, 0], keep=True, name="TipPort")
C("feature.boolean", op="intersect", target=prev, tool="TipPort", name="TipStock")
C("feature.block", size=["Xb - Xa", "2000 mm", "2000 mm"], position=["Xa", "-1000 mm", "-500 mm"], name="Slab")
C("feature.boolean", op="subtract", target="TipStock", tool="Slab", name="Tips")


def face(j, port=False):
    """The envelope's face of panel j (NP: the deck), starboard or port."""
    if j == 0:
        return f"Hull:copy({1 if port else 0})/Cyl0:side(e3)"
    k = NM[j - 1]
    inner = f"Half{k}:copy(1)/Cyl{k}:side(e3)"
    return f"Hull:copy(1)/Port:copy(0)/{inner}" if port else f"Hull:copy(0)/{inner}"


def edge(a, b):
    return f"Hull:between[{a},{b}]"


KEEL = edge(face(0), face(0, True))
RIDGE = edge(face(NP), face(NP, True))
CH = {False: [KEEL] + [edge(face(j - 1), face(j)) for j in range(1, NP + 1)],
      True: [KEEL] + [edge(face(j - 1, True), face(j, True)) for j in range(1, NP + 1)]}
done(1)

# ---------------------------------------------------------------- the panels: developable sheets between the chines
SIDES = [(False, "S"), (True, "P")]
for port, tag in SIDES:
    for j in range(NP):
        C("feature.developable", a={"edges": [CH[port][j]]}, b={"edges": [CH[port][j + 1]]}, name=f"Panel{j}{tag}")
done(2)

# ---------------------------------------------------------------- the plywood: plates on the envelope's faces
# Each panel is the envelope's face given its thickness inwards (side in: the faces are the hull's outside).
# Chines: the panels' inner edges touch (stitch and glue: the outside V is the epoxy fillet). Sheer: the
# sheer panel rests under the deck, which covers its edge. Ridge: the deck panels touch. Ends: on the planes
# where the plywood ends (the hardwood tips go on there).
C("datum.plane", **{"from": "yz", "distance": "Xa", "name": "EndA"})
C("datum.plane", **{"from": "yz", "distance": "Xb", "name": "EndB"})
CAPA, CAPB = "Hull:copy(0)/Cyl0:side(e10)", "Hull:copy(0)/Cyl0:side(e5)"
THK = ["tHull"] * NP + ["tDeck"]


def plate_name(j, tag):
    return f"Deck{tag}" if j == NP else f"Plank{j}{tag}"


for port, tag in SIDES:
    for j in range(NP + 1):
        me = face(j, port)
        joints = [{"edge": edge(me, CAPA), "kind": "onto", "onto": "EndA"},
                  {"edge": edge(me, CAPB), "kind": "onto", "onto": "EndB"}]
        if j == 0:
            joints.append({"edge": KEEL, "kind": "touch", "with": face(0, not port)})
        else:
            joints.append({"edge": CH[port][j], "kind": "under" if j == NP else "touch", "with": face(j - 1, port),
                           "thickness": THK[j - 1]})
        if j < NP:
            joints.append({"edge": CH[port][j + 1], "kind": "over" if j + 1 == NP else "touch",
                           "with": face(j + 1, port), "thickness": THK[j + 1]})
        else:
            joints.append({"edge": RIDGE, "kind": "touch", "with": face(NP, not port)})
        C("feature.plate", faces=[me], thickness=THK[j], side="in", joints=joints, name=plate_name(j, tag))
done(3)

# ---------------------------------------------------------------- the flat panels: the outside skins laid flat
for j in range(NP + 1):
    C("feature.unfold", faces=[f"{plate_name(j, 'S')}:copy(0)/{face(j)}"], at=["-2500 mm", f"-450 mm - {j} * 250 mm", f"{FLOOR} mm"], angle="-90 deg",
      name=f"Flat{j}")
done(4)


def A(name, **kw):
    C("assert.add", name=name, **kw)


for port, tag in SIDES:
    side = "starboard" if tag == "S" else "port"
    for j in range(1, NP):
        A(f"chine {j} ({side}): the panels' inner edges touch", measure="distance",
          **{"from": plate_name(j - 1, tag), "to": plate_name(j, tag)}, eq="0 mm", tol="0.01 mm")
    A(f"sheer ({side}): the deck rests on the sheer panel", measure="distance",
      **{"from": plate_name(NP - 1, tag), "to": plate_name(NP, tag)}, eq="0 mm", tol="0.01 mm")
A("keel: the bottom panels' inner edges touch", measure="distance", **{"from": "Plank0S", "to": "Plank0P"},
  eq="0 mm", tol="0.01 mm")
A("ridge: the deck panels' inner edges touch", measure="distance", **{"from": "DeckS", "to": "DeckP"},
  eq="0 mm", tol="0.01 mm")
PANELFACES = {"kind": "face", "where": {"all": [{"in": "Hull"}, {"name": "*side(e3)"}]}}
A("the panels: developable (the envelope's faces the plates are made of)", measure="developable", of=PANELFACES,
  **{"is": True})
A("the panels: Gaussian curvature", measure="curvature", of=PANELFACES, max="1e-9 / (1 mm)^2")
# The developable connections of the chines (Panel0S..Panel3P) are not asserted on: measuring a 5 m sheet's
# curvature does not always settle (plan/repro/repro-sea-kayak-5.json in 3DCraft); the feature itself refuses
# a sheet that is not developable and reports its largest curvature (about 1e-12 / mm^2).
done(5)

# ---------------------------------------------------------------- weight and hydrostatics
# The boat's weight, from formulas: the plywood (its area by a coefficient of the panels' widths, checked
# below against the kernel's mass of the plates), glass and epoxy, and the fittings.
V("mPly", "rhoPly / (1 m)^3 * L * (0.70 * tHull * 2 * (W0 + W1 + W2 + W3) + 0.67 * tDeck * 2 * Ymid / cos(crown))")
V("aHull", "0.70 * L * 2 * (W0 + W1 + W2 + W3) / (1 m)^2")
V("aDeck", "0.67 * L * 2 * Ymid / cos(crown) / (1 m)^2")
V("mGlass", "0.80 * aHull + 0.55 * aDeck")   # kg: 6 oz glass and epoxy on the hull, 4 oz on the deck
V("mFit", "4.5")                             # kg: sheer clamps, bulkheads, coaming, seat, hatches, deck lines
V("mBoat", "mPly + mGlass + mFit")
V("mTotal", "mPad + payload + mBoat")
V("Vdisp", "mTotal / rho * (1 m)^3")
# What the hull can carry with the sheer 45 mm above the water: the volume below that plane by a block
# coefficient (0.355, less for more rocker; at most the kernel's own measure over the corners of the ranges,
# which the freeboard assertion holds the form to), less the boat. It bounds the paddler's and the load's
# ranges, so that the form only offers the paddlers this hull carries.
V("kCap", "0.355 - 0.00017 * (rockB + rockS - 470 mm) / (1 mm)")
V("mCap", "kCap * L * B * (Zmid - 45 mm) * rho / (1 m)^3 - mBoat")
for port, tag in SIDES:
    for j in range(NP + 1):
        C("body.material", body=plate_name(j, tag), name="okoume plywood", density="rhoPly")
WOOD = [plate_name(j, t) for t in "SP" for j in range(NP + 1)]
A("plywood: the kernel's mass of the plates is the formula's (the weight the waterline is found for)",
  measure="mass", of=WOOD, eq="mPly", tol="mPly / 25")
A("freeboard: the waterline for the boat, the paddler and the load lies 45 mm below the sheer amidships",
  measure="levelFor", of="Hull", volume="Vdisp", max="Zmid - 45 mm")
A("the hardwood tips are dry: above the highest waterline the freeboard allows", measure="boxMin", of="Tips",
  axis="z", min="Zmid - 45 mm")
done(6)

# ---------------------------------------------------------------- the cockpit coaming
# A ring standing 30 mm on the deck all round the cockpit: the ring's prism less the envelope, within the
# envelope raised by 30 mm. (The opening is cut in the deck after assembly, from the coaming.)
V("cockL", "800 mm")
V("cockW", "420 mm")
V("rim", "30 mm")
V("Xc", at(X, "0.5") + " + 60 mm")
C("sketch.create", plane="xy", name="CockpitRing")
C("sketch.curve", sketch="CockpitRing", x="Xc + (cockL / 2 + rim) * cos(t)", y="(cockW / 2 + rim) * sin(t)",
  t=["0", "2 * pi"])
C("sketch.curve", sketch="CockpitRing", x="Xc + cockL / 2 * cos(t)", y="cockW / 2 * sin(t)", t=["0", "2 * pi"])
C("feature.extrude", sketch="CockpitRing", distance="600 mm", name="RingStock")
C("feature.transform", source="Hull", translate=["0 mm", "0 mm", "rim"], keep=True, name="Raised")
C("feature.boolean", op="subtract", target="RingStock", tool="Hull", keepTool=True, name="RingOut")
C("feature.boolean", op="intersect", target="RingOut", tool="Raised", name="Coaming")
for t in "SP":
    A(f"the coaming stands on the deck ({'starboard' if t == 'S' else 'port'} panel)", measure="distance",
      **{"from": "Coaming", "to": f"Deck{t}"}, eq="0 mm", tol="0.01 mm")

# ---------------------------------------------------------------- what is shown, the cut sheet
C("feature.visible", feature=["Hull"] + [f"Panel{j}{t}" for t in "SP" for j in range(NP)] +
  [f"Plane{j}" for j in PANELS] + [f"Trace{j}" for j in PANELS + ["T"]] + ["EndA", "EndB", "CockpitRing"], visible=False)
for t in "SP":
    for j in range(NP):
        C("body.appearance", body=plate_name(j, t), color=OKOUME)
    C("body.appearance", body=plate_name(NP, t), color=COPPER)
for j in range(NP):
    C("body.appearance", body=f"Flat{j}", color=OKOUME)
C("body.appearance", body=f"Flat{NP}", color=COPPER)
C("body.appearance", body="Tips", color=WALNUT)
C("body.appearance", body="Coaming", color=WALNUT)
C("set.define", name="Cut sheet: panels", kind="face", where={"any": [{"in": f"Flat{j}"} for j in range(NP + 1)]})
done(7)

# ---------------------------------------------------------------- the form
G1, G2 = "Hull", "Paddler and load"
params = [
    {"name": "L", "label": "Length overall", "group": G1, "order": 1, "min": "5000 mm", "max": "5800 mm",
     "step": "10 mm", "unit": "mm", "description": "Tip to tip"},
    {"name": "B", "label": "Beam", "group": G1, "order": 2, "min": "530 mm", "max": "600 mm", "step": "5 mm",
     "unit": "mm", "description": "Widest beam at the sheer (the hull-deck joint)"},
    {"name": "D", "label": "Depth at the sheer", "group": G1, "order": 3, "min": "170 mm",
     "max": "min(230 mm, 0.36 * B)", "step": "5 mm", "unit": "mm",
     "description": "Height of the sheer above the keel at the widest station; the deck's crown comes on top"},
    {"name": "crown", "label": "Deck crown", "group": G1, "order": 4, "min": "12 deg", "max": "26 deg",
     "step": "1 deg", "unit": "deg", "description": "Angle of the deck panels from the horizontal"},
    {"name": "rockB", "label": "Bow rise", "group": G1, "order": 5, "min": "250 mm", "max": "400 mm",
     "step": "5 mm", "unit": "mm", "description": "Rocker: how high the keel rises to the bow tip"},
    {"name": "rockS", "label": "Stern rise", "group": G1, "order": 6, "min": "220 mm", "max": "350 mm",
     "step": "5 mm", "unit": "mm", "description": "How high the keel rises to the stern tip"},
    {"name": "mPad", "label": "Paddler weight (kg)", "group": G2, "order": 1, "min": "45", "max": "min(100, floor(mCap))", "step": "1",
     "description": "The paddler, in kg: with the boat and the load it sets the waterline; at most what the hull carries with the sheer 45 mm above the water"},
    {"name": "payload", "label": "Load (kg)", "group": G2, "order": 2, "min": "0", "max": "clamp(floor(mCap - mPad), 0, 30)", "step": "1",
     "description": "Gear in the fore and aft compartments, in kg; at most what the hull carries besides the paddler"},
    {"name": "water", "label": "Water", "group": G2, "order": 3, "kind": "choice", "choicesFrom": "waters",
     "description": "Sea water (1025 kg/m3) or fresh water (1000 kg/m3)"},
]
for p_ in params:
    C("variable.publish", **p_)
C("document.info",
  title="Sea kayak (stitch and glue)",
  description="A Greenland-style multichine sea kayak in okoume plywood, built stitch and glue, made entirely "
              "by 3DCraft from formulas: the hull is the meeting of developable panels, every panel is a plate "
              "whose inner edges touch its neighbours, the deck rests on the sheer panels, every panel is laid "
              "flat for cutting, and the waterline for the paddler and the load is found by the kernel. Export "
              "the set Cut sheet: panels (DXF or SVG).",
  author="3DCraft Jigs", licence="CC-BY-4.0",
  url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/sea-kayak",
  tags=["kayak", "boat", "stitch and glue", "plywood", "developable", "plate", "unfold", "hydrostatics",
        "cut sheet", "formula"])
C("assert.list")
C("jig.export", path="dist/sea-kayak.3dcraftjig")
done(99)
