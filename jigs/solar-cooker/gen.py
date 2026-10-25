#!/usr/bin/env python3
"""Writes build.json of the solar-cooker Jig:  python3 gen.py > build.json

A parabolic solar cooker: a dish z = r^2 / (4 f) made of N flat petals (gores) of sheet,
a pot holder ring at the focus on three legs from the rim, the pot in place and a simple
stand. The flat petals lie on the ground beside it, in two rows: they are the cut sheet.

The world origin is the dish's vertex (the paraboloid's lowest point), z up, so the
focus is the point (0, 0, f). The ground is at z = -standH.

The petal outline (a gore) comes from the paraboloid's arc length, measured from the
vertex along a meridian:
    s(r) = integral_0^r sqrt(1 + (u / 2f)^2) du
         = (r / 2) sqrt(1 + (r / 2f)^2) + f asinh(r / 2f)
At arc length s(r) the petal is 2 pi r / N wide (the circle of radius r shared by N
petals), so its edges are the curves (s(t), +-pi t / N) for t from the hole to the rim.
"""
import json

TABS = 5  # glue tabs along one edge of each petal
SIMPSON = 16  # panels of the independent Simpson integral the length assertion is checked against


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


def S(r):
    """The closed-form arc length s(r) as an expression (asinh u = ln(u + sqrt(1 + u^2)))."""
    u = f"(({r}) / (2 * f))"
    return f"(({r}) / 2 * sqrt(1 + {u}^2) + f * ln({u} + sqrt(1 + {u}^2)))"


def simpson_length():
    """The petal length by Simpson's rule on sqrt(1 + (r / 2f)^2), independent of the closed form."""
    terms = []
    for k in range(SIMPSON + 1):
        w = 1 if k in (0, SIMPSON) else (4 if k % 2 else 2)
        r = f"(r0 + {k} * (R - r0) / {SIMPSON})"
        terms.append(f"{w} * sqrt(1 + ({r} / (2 * f))^2)")
    return f"(R - r0) / {3 * SIMPSON} * (" + " + ".join(terms) + ")"


ALU, CREAM, STEEL, POT = "#B9BEC4", "#E8DFCC", "#7D858C", "#7A5638"

steps = [
    # --- inputs ---
    V("D", "1000 mm"),          # dish diameter (aperture)
    V("fD", "0.3"),             # focal ratio f / D
    V("N", "12"),               # number of petals
    V("th", "2 mm"),            # sheet thickness
    V("pot", "2"),              # row of the pots table
    V("standH", "600 mm"),      # height of the dish's vertex above the ground
    V("tabW", "15 mm"),         # glue / rivet tab along one edge of each petal
    ["table.set", {"name": "pots",
                   "columns": ["pot", {"name": "d", "unit": "mm"}, {"name": "h", "unit": "mm"}],
                   "rows": [["Pot 16 cm", 160, 110], ["Pot 20 cm", 200, 130], ["Pot 24 cm", 240, 150],
                            ["Kettle", 170, 200]]}],
    # --- derived ---
    V("potD", "pots[pot].d"),
    V("potH", "pots[pot].h"),
    V("f", "fD * D"),
    V("R", "D / 2"),
    V("r0", "D / 20"),          # radius of the central hole
    V("depth", "D^2 / (16 * f)"),
    V("rimAngle", "2 * atan(1 / (4 * fD))"),  # rim angle: axis to the ray from the focus to the rim
    V("S0", S("r0")),
    V("SR", S("R")),
    V("L", "SR - S0"),          # length of a flat petal
    V("halfR", "pi * R / N"),   # half-width at the rim
    V("half0", "pi * r0 / N"),  # half-width at the hole
    # Nesting on the sheet: every other petal is turned end for end. Two petals side by side, one
    # turned, are at most M wide together at any station: half-widths are pi r / N, r is concave in
    # s, so r(s) + r(L - s) <= 2 r(mid), and the tangent of s(r) at the rim bounds r(mid) from above.
    V("gap", "10 mm"),
    V("M", "2 * pi / N * (R - L / (2 * sqrt(1 + (R / (2 * f))^2)))"),
    V("nestP", "M + 2 * tabW + gap"),     # turned petal: tabs face each other
    V("pitch", "2 * M + 2 * tabW + 2 * gap"),
    V("nA", "ceil(N / 2)"),
    V("seg", f"(R - r0) / {2 * TABS + 1}"),   # tabs and the gaps between them, along the radius
    V("tc", "min(tabW / 2, seg / 4)"),        # how far a tab's flanks lean in
    V("nB", "floor(N / 2)"),
    # The holder: a flat ring under the pot, the pot's bottom a quarter of its height below the focus.
    V("ringT", "4 mm"),
    V("rIn", "potD / 2 - 20 mm"),
    V("rOut", "potD / 2 + 15 mm"),
    V("potZ", "f - potH / 4"),
    V("ringZ", "potZ - ringT"),
    V("rod", "5 mm"),
    # A leg runs from just above and outside the rim to under the ring.
    V("legX0", "R + rod + 0.5 mm"),
    V("legZ0", "depth + th + 2 * rod + 2 mm"),
    V("legX1", "rOut - 8 mm"),
    V("legZ1", "ringZ - rod + 1.5 mm"),   # 1.5 mm into the ring, so they weld into one body
    V("legLen", "sqrt((legX1 - legX0)^2 + (legZ1 - legZ0)^2)"),
    # The stand.
    V("postR", "20 mm"),
    V("hubR", "r0 + 25 mm"),
    V("hubT", "10 mm"),
    V("hubZ", "r0^2 / (4 * f)"),   # the hub's top touches the dish along the hole's edge only
    V("footL", "0.45 * D"),
    V("footR", "15 mm"),
    # Where the flat petals lie: beside the stand, two rows, centred on y.
    V("X0", "max(R, footL) + 100 mm"),
    V("Y0", "-(N - 1) * pitch / 4"),
    V("G", "-standH"),
]

# --- the dish: one petal revolved through 360 / N degrees, patterned round in two colours ---
x_in = "t^2 / (4 * f)"
steps += [
    ["sketch.create", {"name": "Meridian", "plane": "zx"}],
    # sketch x is world z, sketch y is world x
    ["sketch.curve", {"sketch": "Meridian", "x": x_in, "y": "t", "t": ["r0", "R"]}],
    ["sketch.curve", {"sketch": "Meridian", "x": f"{x_in} + th", "y": "t", "t": ["r0", "R"]}],
    ["sketch.line", {"sketch": "Meridian", "from": "e1", "to": "e4"}],
    ["sketch.line", {"sketch": "Meridian", "from": "e2", "to": "e5"}],
    ["feature.revolve", {"sketch": "Meridian", "axis": "x", "angle": "360 deg / N", "name": "DishPetal"}],
    ["feature.transform", {"source": "DishPetal", "angle": "360 deg / N", "axis": [0, 0, 1], "keep": True,
                           "name": "DishPetal2"}],
    # With an odd N the last petal comes on its own (a pattern may not go past a full turn).
    ["feature.transform", {"source": "DishPetal", "angle": "(N - 1) * 360 deg / N", "axis": [0, 0, 1], "keep": True,
                           "name": "DishLast", "when": "mod(N, 2) == 1"}],
    ["feature.pattern", {"source": "DishPetal", "count": "nB", "angle": "720 deg / N", "axis": [0, 0, 1],
                         "name": "DishA"}],
    ["feature.pattern", {"source": "DishPetal2", "count": "nB", "angle": "720 deg / N", "axis": [0, 0, 1],
                         "name": "DishB"}],
    ["body.appearance", {"body": "DishA", "color": ALU, "metallic": 0.8, "roughness": 0.3}],
    ["body.appearance", {"body": "DishB", "color": CREAM, "roughness": 0.5}],
    ["body.appearance", {"body": "DishLast", "color": ALU, "metallic": 0.8, "roughness": 0.3}],
    ["set.define", {"name": "Dish", "kind": "body", "where": {"any": [{"in": "DishA"}, {"in": "DishB"},
                                                                       {"in": "DishLast"}]}}],
]

# --- the flat petals (the cut sheet), nested end for end in one row ---
X = f"X0 + {S('t')} - S0"
LOW, HIGH, TAB = "Y0 - pi * t / N", "Y0 + pi * t / N", "Y0 + pi * t / N + tabW"


def gore_outline():
    """The petal's outline: the lower edge in one curve, the upper edge in TABS + 1 pieces with a
    trapezoid tab between each two. The parts b(i) = r0 + i seg split the radius in 2 TABS + 1
    equal steps; tabs sit on the odd ones, their straight flanks inset by tc."""
    out, n = [], 0

    def curve(y, t0, t1):
        nonlocal n
        out.append(["sketch.curve", {"sketch": "Gore", "x": X, "y": y, "t": [t0, t1]}])
        n += 3
        return f"e{n - 2}", f"e{n - 1}"

    def line(a, b):
        nonlocal n
        out.append(["sketch.line", {"sketch": "Gore", "from": a, "to": b}])
        n += 1

    def bnd(i):
        return f"r0 + {i} * seg"

    lo0, lo1 = curve(LOW, "r0", "R")
    body = [curve(HIGH, bnd(2 * j), bnd(2 * j + 1)) for j in range(TABS + 1)]
    for k in range(1, TABS + 1):
        t0, t1 = curve(TAB, f"{bnd(2 * k - 1)} + tc", f"{bnd(2 * k)} - tc")
        line(body[k - 1][1], t0)
        line(t1, body[k][0])
    line(lo0, body[0][0])        # the hole end
    line(lo1, body[TABS][1])     # the rim end
    return out


steps += [
    ["sketch.create", {"name": "Gore", "plane": "xy", "offset": "G"}],
] + gore_outline() + [
    ["feature.extrude", {"sketch": "Gore", "distance": "th", "name": "Petal"}],
    ["feature.transform", {"source": "Petal", "angle": "180 deg", "pivot": ["X0 + L / 2", "Y0", "G"],
                           "translate": ["0 mm", "nestP", "0 mm"], "keep": True,
                           "name": "Petal2"}],
    ["feature.pattern", {"source": "Petal", "count": "nA", "step": ["0 mm", "pitch", "0 mm"], "name": "PetalsA"}],
    ["feature.pattern", {"source": "Petal2", "count": "nB", "step": ["0 mm", "pitch", "0 mm"], "name": "PetalsB"}],
    ["body.appearance", {"body": "PetalsA", "color": ALU, "metallic": 0.8, "roughness": 0.3}],
    ["body.appearance", {"body": "PetalsB", "color": CREAM, "roughness": 0.5}],
]

# --- the pot holder: a flat ring at the focus on three legs from the rim ---
steps += [
    ["sketch.create", {"name": "RingSketch", "plane": "xy", "offset": "ringZ"}],
    ["sketch.circle", {"sketch": "RingSketch", "center": ["0 mm", "0 mm"], "radius": "rOut"}],
    ["sketch.circle", {"sketch": "RingSketch", "center": ["0 mm", "0 mm"], "radius": "rIn"}],
    ["feature.extrude", {"sketch": "RingSketch", "distance": "ringT", "name": "Ring"}],
    ["feature.cylinder", {"radius": "rod", "height": "legLen", "position": ["legX0", "0 mm", "legZ0"],
                          "axis": ["legX1 - legX0", "0 mm", "legZ1 - legZ0"], "name": "Leg"}],
    ["feature.pattern", {"source": "Leg", "count": "3", "angle": "120 deg", "axis": [0, 0, 1], "name": "Legs"}],
    ["feature.boolean", {"op": "union", "target": "Ring", "tool": "Legs", "name": "Holder"}],
    ["body.appearance", {"body": "Holder", "color": STEEL, "metallic": 0.7, "roughness": 0.4}],
]

# --- the pot ---
steps += [
    ["feature.cylinder", {"radius": "potD / 2", "height": "potH", "position": ["0 mm", "0 mm", "potZ"],
                          "name": "PotBody"}],
    ["feature.cylinder", {"radius": "potD / 2 + 3 mm", "height": "6 mm",
                          "position": ["0 mm", "0 mm", "potZ + potH"], "name": "Lid"}],
    ["feature.boolean", {"op": "union", "target": "PotBody", "tool": "Lid", "name": "Pot"}],
    ["body.appearance", {"body": "Pot", "color": POT, "roughness": 0.7}],
]

# --- the stand: a post on three feet, a hub under the dish ---
steps += [
    ["feature.cylinder", {"radius": "postR", "height": "standH + hubZ - hubT", "position": ["0 mm", "0 mm", "G"],
                          "name": "Post"}],
    ["feature.cylinder", {"radius": "hubR", "height": "hubT", "position": ["0 mm", "0 mm", "hubZ - hubT"],
                          "name": "Hub"}],
    ["feature.cylinder", {"radius": "footR", "height": "footL", "position": ["0 mm", "0 mm", "G + footR"],
                          "axis": [1, 0, 0], "name": "Foot"}],
    ["feature.pattern", {"source": "Foot", "count": "3", "angle": "120 deg", "axis": [0, 0, 1],
                         "point": [0, 0, 0], "name": "Feet"}],
    ["feature.boolean", {"op": "union", "target": "Post", "tool": "Hub", "name": "PostHub"}],
    ["feature.boolean", {"op": "union", "target": "PostHub", "tool": "Feet", "name": "Stand"}],
    ["body.appearance", {"body": "Stand", "color": STEEL, "metallic": 0.7, "roughness": 0.4}],
]

# --- the cut sheet ---
steps += [
    ["set.define", {"name": "Cut sheet", "kind": "face", "where": {"any": [
        {"in": "PetalsA", "normal": {"along": "z"}},
        {"in": "PetalsB", "normal": {"along": "z"}},
        {"in": "Holder", "normal": {"along": "z"}}]}}],
]

# --- assertions: the rules that make it cook ---
steps += [
    # The focus (0, 0, f) lies inside the pot.
    ["assert.add", {"name": "focus in pot (z low)", "measure": "boxMin", "of": "Pot", "axis": "z", "max": "f"}],
    ["assert.add", {"name": "focus in pot (z high)", "measure": "boxMax", "of": "Pot", "axis": "z", "min": "f"}],
    ["assert.add", {"name": "focus in pot (x)", "measure": "boxMin", "of": "Pot", "axis": "x", "max": "0 mm"}],
    ["assert.add", {"name": "focus in pot (y)", "measure": "boxMax", "of": "Pot", "axis": "y", "min": "0 mm"}],
    # The pot shades at most 10 % of the aperture: (pot diameter / D)^2 <= 0.1.
    ["assert.add", {"name": "pot shades at most 10 %", "measure": "extent", "of": "Pot", "axis": "x",
                    "max": "sqrt(0.1) * D"}],
    # Each flat petal is as long as the parabola's arc from the hole to the rim (Simpson's rule).
    ["assert.add", {"name": "petal length is the arc length", "measure": "extent", "of": "PetalsA", "axis": "x",
                    "eq": simpson_length(), "tol": "0.05 mm"}],
    # The petals close the circle: N petals of 360 / N degrees give the full shell, pi th (R^2 - r0^2).
    ["assert.add", {"name": "petals cover the full circle", "measure": "volume", "of": {"set": "Dish"},
                    "eq": "pi * th * (R^2 - r0^2)", "tol": "pi * th * (R^2 - r0^2) / 10000"}],
    # The dish is D^2 / (16 f) deep at the rim (its top surface is th higher).
    ["assert.add", {"name": "dish depth", "measure": "boxMax", "of": "DishA", "axis": "z",
                    "eq": "D^2 / (16 * f) + th", "tol": "0.05 mm"}],
    # Nothing collides: the holder and the pot stay off the dish.
    ["assert.add", {"name": "holder clear of dish", "measure": "overlap", "of": ["Holder"], "to": {"set": "Dish"},
                    "is": False}],
    ["assert.add", {"name": "nested petals clear", "measure": "clearance", "from": "PetalsA", "to": "PetalsB",
                    "min": "gap / 2"}],
    ["assert.add", {"name": "pot clear of dish", "measure": "overlap", "of": ["Pot"], "to": {"set": "Dish"},
                    "is": False}],
]

params = [
    {"name": "D", "label": "Dish diameter", "group": "Dish", "order": 1, "min": "3.2 * (potD + 30 mm)",
     "max": "1600 mm", "step": "10 mm", "unit": "mm",
     "description": "Diameter of the dish's aperture; at least 3.2 x (pot + 30 mm) so the pot and its ring shade at most 10 %"},
    {"name": "fD", "label": "Focal ratio f/D", "group": "Dish", "order": 2, "min": "0.25", "max": "0.4",
     "step": "0.01",
     "description": "Focal length over diameter: 0.25 puts the focus in the rim plane (a deep dish), 0.4 is shallow"},
    {"name": "N", "label": "Petals", "group": "Dish", "order": 3, "kind": "integer", "min": "8", "max": "24",
     "description": "Number of flat petals (gores) the dish is made of"},
    {"name": "th", "label": "Sheet thickness", "group": "Dish", "order": 4, "min": "0.5 mm", "max": "4 mm",
     "step": "0.1 mm", "unit": "mm", "description": "Cardboard, aluminium or polypropylene sheet under the foil"},
    {"name": "tabW", "label": "Glue tab", "group": "Dish", "order": 5, "min": "8 mm", "max": "25 mm",
     "step": "1 mm", "unit": "mm", "description": "Width of the tab along one edge of each petal, for glue or rivets"},
    {"name": "pot", "label": "Pot", "group": "Pot and stand", "order": 1, "kind": "choice", "choicesFrom": "pots",
     "description": "The pot or kettle the holder takes"},
    {"name": "standH", "label": "Stand height", "group": "Pot and stand", "order": 2, "min": "300 mm",
     "max": "1000 mm", "step": "10 mm", "unit": "mm", "description": "Height of the dish's centre above the ground"},
]
for p in params:
    steps.append(["variable.publish", p])
steps.append(["document.info", {
    "title": "Parabolic solar cooker",
    "description": "A parabolic solar cooker whose dish is made of flat petals (gores) cut from cardboard, "
                   "aluminium or polypropylene sheet and covered with reflective foil. Each petal's outline is "
                   "drawn from the paraboloid's arc length, so N petals bend into the exact dish z = r^2 / 4f. "
                   "A ring on three legs holds the pot at the focus. Set the diameter, the focal ratio, the "
                   "number of petals, the sheet, the tab and the pot. Export the cut sheet with File > Export... "
                   "(DXF or SVG, set Cut sheet). Never look into the focus: wear sunglasses, it gets very hot.",
    "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
    "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/solar-cooker",
    "tags": ["solar cooker", "parabolic dish", "gores", "cut sheet", "laser cutting", "formula"]}])
steps.append(["jig.export", {"path": "dist/solar-cooker.3dcraftjig"}])

print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
