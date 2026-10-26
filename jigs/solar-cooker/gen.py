#!/usr/bin/env python3
"""Writes build.json of the solar-cooker Jig:  python3 gen.py > build.json

A parabolic solar cooker: a dish z = r^2 / (4 f) made of N flat petals (gores) of sheet on a
rim hoop, hung on a horizontal tilt axis that runs through the focus, in a fork on a base that
turns (azimuth). The pot sits level on a ring that hangs from the fork's crossbar, so it stays at
the focus whatever the tilt (as in the KSOL-type cookers). The flat petals lie on the ground
beside it, nested end for end: they are the cut sheet.

World frame: z up, the ground at z = 0, the focus at (0, 0, zF), the tilt axis along y through
it. The dish is built in its own frame, vertex at the origin and focus at (0, 0, f), then turned
by tilt = 90 deg - sun elevation about the tilt axis (towards +x, where the sun is) and lifted.

The petal outline comes from the paraboloid's arc length along a meridian:
    s(r) = integral_0^r sqrt(1 + (u / 2f)^2) du
         = (r / 2) sqrt(1 + (r / 2f)^2) + f asinh(r / 2f)
At arc length s(r) the petal is 2 pi r / N wide (the circle of radius r shared by N petals),
so its edges are the curves (s(t), +-pi t / N) for t from the hole to the rim.
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


def look(body, color):
    if color == ALU:
        return ["body.appearance", {"body": body, "color": ALU, "metallic": 0.8, "roughness": 0.3}]
    if color == STEEL:
        return ["body.appearance", {"body": body, "color": STEEL, "metallic": 0.7, "roughness": 0.4}]
    return ["body.appearance", {"body": body, "color": color, "roughness": 0.6}]


steps = [
    # --- inputs ---
    V("D", "1000 mm"),          # dish diameter (aperture)
    V("fD", "0.3"),             # focal ratio f / D
    V("N", "20"),               # number of petals (20: no wider than any pot of the table at D = 1 m)
    V("th", "2 mm"),            # sheet thickness
    V("pot", "2"),              # row of the pots table
    V("elev", "50 deg"),        # sun elevation the dish is aimed at
    V("clearG", "150 mm"),      # least gap between the swinging dish and the base
    V("tabW", "15 mm"),         # glue / rivet tab along one edge of each petal
    ["table.set", {"name": "pots",
                   "columns": ["pot", {"name": "d", "unit": "mm"}, {"name": "h", "unit": "mm"}],
                   "rows": [["Pot 16 cm", 160, 110], ["Pot 20 cm", 200, 130], ["Pot 24 cm", 240, 150],
                            ["Kettle", 170, 200]]}],
    # --- the dish ---
    V("potD", "pots[pot].d"),
    V("potH", "pots[pot].h"),
    V("f", "fD * D"),
    V("R", "D / 2"),
    V("r0", "max(D / 20, N * 20 mm / (2 * pi))"),   # central hole: every petal at least 20 mm wide there
    V("depth", "D^2 / (16 * f)"),
    V("rimAngle", "2 * atan(1 / (4 * fD))"),  # rim angle: axis to the ray from the focus to the rim
    V("tilt", "90 deg - elev"),                # the dish's axis from the vertical
    V("wa", "360 deg / N"),                    # the angle of one petal
    V("Rw", "(R + 10 mm) / cos(wa / 2)"),      # a wedge's outer corners, beyond the rim
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
    V("nB", "floor(N / 2)"),
    V("seg", f"(R - r0) / {2 * TABS + 1}"),   # tabs and the gaps between them, along the radius
    V("tc", "min(tabW / 2, seg / 4)"),        # how far a tab's flanks lean in
    # The rim hoop (a rolled flat bar), its two pivot brackets and pins, in the dish's frame.
    V("hoopH", "25 mm"),
    V("hoopT", "4 mm"),
    V("Rh", "R + 1 mm + hoopT"),
    V("Yu", "Rh + 31 mm"),                    # centre of the fork's uprights (30 mm square tube)
    V("rhoMax", "sqrt(Rh^2 + (f - depth + hoopH)^2)"),   # the farthest the reflector reaches from the axis
    # --- the fixed frame ---
    V("baseH", "60 mm"),
    V("zF", "baseH + clearG + rhoMax"),       # height of the focus and the tilt axis
    V("ringT", "4 mm"),
    V("rIn", "potD / 2 - 20 mm"),
    V("rOut", "potD / 2 + 15 mm"),
    V("potZ", "zF - potH / 4"),               # the pot's bottom a quarter of its height below the focus
    V("ringZ", "potZ - ringT"),
    V("zTop", "potZ + potH + 46 mm"),         # underside of the crossbar: room over the lid
    V("footL", "0.6 * Yu"),
    # Where the flat petals lie: on the ground beside the cooker, in one nested row centred on y.
    V("X0", "max(rhoMax, footL) + 150 mm"),
    V("Y0", "-(N - 1) * pitch / 4"),
]

# --- the dish: one petal revolved through 360 / N degrees, patterned round in two colours ---
x_in = "t^2 / (4 * f)"
TILT = {"angle": "tilt", "axis": [0, 1, 0], "pivot": ["0 mm", "0 mm", "f"], "translate": ["0 mm", "0 mm", "zF - f"]}
steps += [
    ["sketch.create", {"name": "Meridian", "plane": "zx"}],
    # sketch x is world z, sketch y is world x
    ["sketch.curve", {"sketch": "Meridian", "x": x_in, "y": "t", "t": ["r0", "R"]}],
    ["sketch.curve", {"sketch": "Meridian", "x": f"{x_in} + th", "y": "t", "t": ["r0", "R"]}],
    ["sketch.line", {"sketch": "Meridian", "from": "e1", "to": "e4"}],
    ["sketch.line", {"sketch": "Meridian", "from": "e2", "to": "e5"}],
    ["feature.revolve", {"sketch": "Meridian", "axis": "x", "name": "DishFull"}],
    ["feature.transform", {"source": "DishFull", "keep": True, "name": "DishCopy"}],
    # Every other petal is cut out by a wedge of 360 / N degrees (nB of them, 2 x 360 / N apart): the
    # wedges' part is the cream petals, the rest the aluminium ones (with an odd N two of those meet).
    ["sketch.create", {"name": "Wedge", "plane": "xy", "offset": "-10 mm"}],
    ["sketch.path", {"sketch": "Wedge", "start": ["r0 / 2", "0 mm"], "closed": True,
                     "segments": [{"line": ["Rw", "0 mm"]}, {"line": ["Rw * cos(wa)", "Rw * sin(wa)"]},
                                  {"line": ["r0 / 2 * cos(wa)", "r0 / 2 * sin(wa)"]}]}],
    ["sketch.pattern", {"sketch": "Wedge", "entities": ["e3", "e5", "e7", "e8"], "angle": "2 * wa",
                        "center": ["0 mm", "0 mm"], "count": "nB"}],
    ["feature.extrude", {"sketch": "Wedge", "distance": "depth + th + 20 mm", "name": "Wedges"}],
    ["feature.boolean", {"op": "subtract", "target": "DishFull", "tool": "Wedges", "keepTool": True, "name": "DishA0"}],
    ["feature.boolean", {"op": "intersect", "target": "DishCopy", "tool": "Wedges", "name": "DishB0"}],
    # The rim hoop: a flat bar rolled to a ring just outside the petals' rim, which they are riveted to.
    ["sketch.create", {"name": "HoopSketch", "plane": "zx"}],
    ["sketch.path", {"sketch": "HoopSketch", "start": ["depth - hoopH", "R + 1 mm"], "closed": True,
                     "segments": [{"line": ["depth + th", "R + 1 mm"]}, {"line": ["depth + th", "Rh"]},
                                  {"line": ["depth - hoopH", "Rh"]}]}],
    ["feature.revolve", {"sketch": "HoopSketch", "axis": "x", "name": "Hoop"}],
    # Two pivot brackets on the hoop, up to the tilt axis (through the focus, along y), and the pins.
    ["feature.block", {"size": ["30 mm", "Rh + 6 mm - (R + 1 mm)", "f + 12 mm - (depth - hoopH)"],
                       "position": ["-15 mm", "R + 1 mm", "depth - hoopH"], "name": "Bracket"}],
    ["feature.pattern", {"source": "Bracket", "count": "2", "angle": "180 deg", "axis": [0, 0, 1], "name": "Brackets"}],
    ["feature.cylinder", {"radius": "8 mm", "height": "Yu - 15.5 mm - (Rh + 4 mm)", "axis": [0, 1, 0],
                          "position": ["0 mm", "Rh + 4 mm", "f"], "name": "Pin"}],
    ["feature.pattern", {"source": "Pin", "count": "2", "angle": "180 deg", "axis": [0, 0, 1], "name": "Pins"}],
    ["feature.boolean", {"op": "union", "target": "Hoop", "tool": "Brackets", "name": "HoopBrackets"}],
    ["feature.boolean", {"op": "union", "target": "HoopBrackets", "tool": "Pins", "name": "Mount0"}],
    # A centre flange under the petals' narrow ends (0.2 mm of glue between).
    ["sketch.create", {"name": "FlangeSketch", "plane": "zx"}],
    ["sketch.curve", {"sketch": "FlangeSketch", "x": f"{x_in} - 3.2 mm", "y": "t", "t": ["r0 - 15 mm", "r0 + 40 mm"]}],
    ["sketch.curve", {"sketch": "FlangeSketch", "x": f"{x_in} - 0.2 mm", "y": "t", "t": ["r0 - 15 mm", "r0 + 40 mm"]}],
    ["sketch.line", {"sketch": "FlangeSketch", "from": "e1", "to": "e4"}],
    ["sketch.line", {"sketch": "FlangeSketch", "from": "e2", "to": "e5"}],
    ["feature.revolve", {"sketch": "FlangeSketch", "axis": "x", "name": "Flange0"}],
    # Aim: turn the whole reflector about the tilt axis.
    ["feature.transform", dict(TILT, source="DishA0", name="DishA")],
    ["feature.transform", dict(TILT, source="DishB0", name="DishB")],
    ["feature.transform", dict(TILT, source="Mount0", name="Mount")],
    ["feature.transform", dict(TILT, source="Flange0", name="Flange")],
    look("DishA", ALU), look("DishB", CREAM), look("Mount", STEEL), look("Flange", ALU),
    ["set.define", {"name": "Dish", "kind": "body", "where": {"any": [{"in": "DishA"}, {"in": "DishB"}]}}],
    ["set.define", {"name": "Reflector", "kind": "body", "where": {"any": [
        {"set": "Dish"}, {"in": "Mount"}, {"in": "Flange"}]}}],
]

# --- the flat petals (the cut sheet), nested end for end in one row ---
X = f"X0 + {S('t')} - S0"
LOW, HIGH, TAB = "Y0 - pi * t / N", "Y0 + pi * t / N", "Y0 + pi * t / N + tabW"


def gore_outline():
    """The petal's outline: the lower edge in one curve, the upper edge in TABS + 1 pieces with a
    trapezoid tab between each two. The parts b(i) = r0 + i seg split the radius in 2 TABS + 1
    equal steps; tabs sit on the odd ones, their straight flanks inset by tc. A 4 mm hole marks the
    narrow (hole) end and takes the rivet to the flange."""
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
    out.append(["sketch.circle", {"sketch": "Gore", "center": ["X0 + 8 mm", "Y0"], "radius": "2 mm"}])
    return out


steps += [
    ["sketch.create", {"name": "Gore", "plane": "xy"}],
] + gore_outline() + [
    ["feature.extrude", {"sketch": "Gore", "distance": "th", "name": "Petal"}],
    ["feature.transform", {"source": "Petal", "angle": "180 deg", "pivot": ["X0 + L / 2", "Y0", "0 mm"],
                           "translate": ["0 mm", "nestP", "0 mm"], "keep": True,
                           "name": "Petal2"}],
    ["feature.pattern", {"source": "Petal", "count": "nA", "step": ["0 mm", "pitch", "0 mm"], "name": "PetalsA"}],
    ["feature.pattern", {"source": "Petal2", "count": "nB", "step": ["0 mm", "pitch", "0 mm"], "name": "PetalsB"}],
    look("PetalsA", ALU), look("PetalsB", CREAM),
]

# --- the fixed frame: a base that turns on a disc (azimuth), a fork, a crossbar over the pot ---
steps += [
    ["feature.cylinder", {"radius": "150 mm", "height": "22 mm", "name": "Turntable"}],
    ["feature.block", {"size": ["80 mm", "2 * Yu + 80 mm", "40 mm"], "position": ["-40 mm", "-Yu - 40 mm", "20 mm"],
                       "name": "BeamY"}],
    ["feature.block", {"size": ["2 * footL", "80 mm", "40 mm"], "position": ["-footL", "-40 mm", "20 mm"],
                       "name": "BeamX"}],
    ["feature.block", {"size": ["30 mm", "30 mm", "zTop + 30 mm - (baseH - 2 mm)"],
                       "position": ["-15 mm", "Yu - 15 mm", "baseH - 2 mm"], "name": "Upright"}],
    ["feature.pattern", {"source": "Upright", "count": "2", "angle": "180 deg", "axis": [0, 0, 1], "name": "Uprights"}],
    ["feature.block", {"size": ["30 mm", "2 * Yu + 30 mm", "30 mm"], "position": ["-15 mm", "-Yu - 15 mm", "zTop"],
                       "name": "Crossbar"}],
    ["feature.boolean", {"op": "union", "target": "Turntable", "tool": "BeamY", "name": "Base1"}],
    ["feature.boolean", {"op": "union", "target": "Base1", "tool": "BeamX", "name": "Base"}],
    ["feature.boolean", {"op": "union", "target": "Base", "tool": "Uprights", "name": "Fork"}],
    ["feature.boolean", {"op": "union", "target": "Fork", "tool": "Crossbar", "name": "Frame"}],
    look("Frame", STEEL),
    # The pot holder: a flat ring on two hangers from the crossbar; it stays level, at the focus.
    ["sketch.create", {"name": "RingSketch", "plane": "xy", "offset": "ringZ"}],
    ["sketch.circle", {"sketch": "RingSketch", "center": ["0 mm", "0 mm"], "radius": "rOut"}],
    ["sketch.circle", {"sketch": "RingSketch", "center": ["0 mm", "0 mm"], "radius": "rIn"}],
    ["feature.extrude", {"sketch": "RingSketch", "distance": "ringT", "name": "Holder"}],
    look("Holder", STEEL),
    # Two hangers (10 mm rod) stand on the ring and are bolted to it and to the crossbar.
    ["feature.cylinder", {"radius": "4.5 mm", "height": "zTop - (ringZ + ringT)",
                          "position": ["0 mm", "potD / 2 + 8 mm", "ringZ + ringT"], "name": "Hanger"}],
    ["feature.pattern", {"source": "Hanger", "count": "2", "angle": "180 deg", "axis": [0, 0, 1], "name": "Hangers"}],
    look("Hangers", STEEL),
    # The pot, level on the ring.
    ["feature.cylinder", {"radius": "potD / 2", "height": "potH", "position": ["0 mm", "0 mm", "potZ"],
                          "name": "PotBody"}],
    ["feature.cylinder", {"radius": "potD / 2 + 2 mm", "height": "6 mm",
                          "position": ["0 mm", "0 mm", "potZ + potH"], "name": "Lid"}],
    ["feature.boolean", {"op": "union", "target": "PotBody", "tool": "Lid", "name": "Pot"}],
    look("Pot", POT),
    ["set.define", {"name": "Fixed", "kind": "body", "where": {"any": [
        {"in": "Frame"}, {"in": "Holder"}, {"in": "Hangers"}, {"in": "Pot"}]}}],
]

# --- the cut sheets ---
steps += [
    ["set.define", {"name": "Cut sheet: petals", "kind": "face", "where": {"any": [
        {"in": "PetalsA", "normal": {"along": "z"}},
        {"in": "PetalsB", "normal": {"along": "z"}}]}}],
    ["set.define", {"name": "Steel parts", "kind": "face", "where": {
        "in": "Holder", "normal": {"along": "z"}}}],
]

# --- assertions: the rules that make it cook ---
steps += [
    # The focus (0, 0, zF) lies inside the pot, at every sun elevation (the pot does not move).
    ["assert.add", {"name": "focus in pot (z low)", "measure": "boxMin", "of": "Pot", "axis": "z", "max": "zF"}],
    ["assert.add", {"name": "focus in pot (z high)", "measure": "boxMax", "of": "Pot", "axis": "z", "min": "zF"}],
    ["assert.add", {"name": "focus in pot (x low)", "measure": "boxMin", "of": "Pot", "axis": "x", "max": "0 mm"}],
    ["assert.add", {"name": "focus in pot (x high)", "measure": "boxMax", "of": "Pot", "axis": "x", "min": "0 mm"}],
    ["assert.add", {"name": "focus in pot (y low)", "measure": "boxMin", "of": "Pot", "axis": "y", "max": "0 mm"}],
    ["assert.add", {"name": "focus in pot (y high)", "measure": "boxMax", "of": "Pot", "axis": "y", "min": "0 mm"}],
    # The pot stands level: its box is exactly as tall as the pot and lid.
    ["assert.add", {"name": "pot level", "measure": "extent", "of": "Pot", "axis": "z", "eq": "potH + 6 mm",
                    "tol": "0.01 mm"}],
    # The pot's ring shades at most 10 % of the aperture: (ring diameter / D)^2 <= 0.1.
    ["assert.add", {"name": "ring shades at most 10 %", "measure": "extent", "of": "Holder", "axis": "x",
                    "max": "sqrt(0.1) * D"}],
    # Each flat petal is as long as the parabola's arc from the hole to the rim (Simpson's rule).
    ["assert.add", {"name": "petal length is the arc length", "measure": "extent", "of": "PetalsA", "axis": "x",
                    "eq": simpson_length(), "tol": "0.05 mm"}],
    # The petals close the circle: N petals of 360 / N degrees give the full shell, pi th (R^2 - r0^2).
    ["assert.add", {"name": "petals cover the full circle", "measure": "volume", "of": {"set": "Dish"},
                    "eq": "pi * th * (R^2 - r0^2)", "tol": "pi * th * (R^2 - r0^2) / 10000"}],
    # The dish is D^2 / (16 f) deep: turned by tilt about the focus, its rim's highest point lies at
    # zF + R sin(tilt) + (depth + th - f) cos(tilt).
    ["assert.add", {"name": "dish depth", "measure": "boxMax", "of": {"set": "Dish"}, "axis": "z",
                    "eq": "zF + R * sin(tilt) + (D^2 / (16 * f) + th - f) * cos(tilt)", "tol": "0.05 mm"}],
    # Nothing collides at this elevation (check-range sweeps it): the reflector clears the fixed frame,
    # the holder and the pot, and the base.
    ["assert.add", {"name": "reflector clear of frame and pot", "measure": "overlap", "of": {"set": "Fixed"},
                    "to": {"set": "Reflector"}, "is": False}],
    ["assert.add", {"name": "reflector above the base", "measure": "boxMin", "of": {"set": "Reflector"}, "axis": "z",
                    "min": "baseH + clearG / 2"}],
    ["assert.add", {"name": "nested petals clear", "measure": "clearance", "from": "PetalsA", "to": "PetalsB",
                    "min": "gap / 2"}],
]

params = [
    {"name": "D", "label": "Dish diameter", "group": "Dish", "order": 1, "min": "3.2 * (potD + 30 mm)",
     "max": "min(1600 mm, 7 * potD)", "step": "10 mm", "unit": "mm",
     "description": "Diameter of the dish's aperture: at least 3.2 x (pot + 30 mm), so the pot's ring shades at "
                    "most 10 %; at most 7 x the pot (and 1.6 m), so the petals can stay narrower than the pot"},
    {"name": "fD", "label": "Focal ratio f/D", "group": "Dish", "order": 2, "min": "0.25", "max": "0.4",
     "step": "0.01",
     "description": "Focal length over diameter: 0.25 puts the focus in the rim plane (a deep dish), 0.4 is shallow"},
    {"name": "N", "label": "Petals", "group": "Dish", "order": 3, "kind": "integer",
     "min": "max(8, ceil(pi * D / potD))", "max": "28",
     "description": "Number of flat petals (gores). At least pi x D / pot: a flat petal reflects a line as wide as "
                    "itself, so no petal may be wider than the pot"},
    {"name": "th", "label": "Sheet thickness", "group": "Dish", "order": 4, "min": "0.5 mm", "max": "4 mm",
     "step": "0.1 mm", "unit": "mm",
     "description": "0.5-1 mm aluminium, 0.8-1.5 mm polypropylene, 2-4 mm corrugated cardboard, under the foil"},
    {"name": "tabW", "label": "Glue tab", "group": "Dish", "order": 5, "min": "8 mm", "max": "25 mm",
     "step": "1 mm", "unit": "mm", "description": "Width of the tabs along one edge of each petal, for glue or rivets"},
    {"name": "pot", "label": "Pot", "group": "Pot and stand", "order": 1, "kind": "choice", "choicesFrom": "pots",
     "description": "The pot or kettle the holder takes"},
    {"name": "elev", "label": "Sun elevation", "group": "Pot and stand", "order": 2, "min": "20 deg",
     "max": "90 deg", "step": "1 deg", "unit": "deg",
     "description": "How high the sun stands: the dish turns on its axis through the focus to face it; the pot "
                    "stays level"},
    {"name": "clearG", "label": "Ground clearance", "group": "Pot and stand", "order": 3, "min": "100 mm",
     "max": "500 mm", "step": "10 mm", "unit": "mm",
     "description": "Least gap between the dish and the base at any tilt; sets the height of the focus"},
]
for p in params:
    steps.append(["variable.publish", p])
steps.append(["document.info", {
    "title": "Parabolic solar cooker",
    "description": "A parabolic solar cooker whose dish is made of flat petals (gores) cut from aluminium, "
                   "polypropylene or cardboard sheet and covered with reflective foil, riveted to a rim hoop. Each "
                   "petal's outline is drawn from the paraboloid's arc length; bent, the petals approximate the "
                   "dish z = r^2 / 4f. The dish turns on an axis through the focus in a fork on a turning base, "
                   "so the pot stays level at the focus. Set the diameter, the focal ratio, the number of petals, "
                   "the sheet, the pot and the sun's elevation. Export the sets Cut sheet: petals and Steel parts "
                   "with File > Export... (DXF or SVG). Never look into the focus, never leave it without a pot: "
                   "it gets very hot.",
    "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
    "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/solar-cooker",
    "tags": ["solar cooker", "parabolic dish", "gores", "cut sheet", "laser cutting", "formula"]}])
steps.append(["jig.export", {"path": "dist/solar-cooker.3dcraftjig"}])

print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
