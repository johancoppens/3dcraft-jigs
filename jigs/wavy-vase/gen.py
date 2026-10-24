#!/usr/bin/env python3
"""Writes build.json of the wavy-vase Jig:  python3 gen.py > build.json

The vase is one smooth loft through five closed curves drawn from formulas:
r(t) = R * (1 + depth/100 * cos(waves * t)), with R following the height (a straight
taper plus a belly), each section turned by its share of the twist. It is a
solid, meant for a slicer's vase mode (spiral outer contour).
"""
import json

SPANS = 4  # spans between the sections: five sections


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


steps = [
    V("bottomD", "70 mm"),
    V("topD", "90 mm"),
    V("height", "120 mm"),
    V("belly", "10 mm"),
    V("waves", "8"),
    V("wavePct", "5"),
    V("twist", "60 deg"),
    V("R0", "bottomD / 2"),
    V("R1", "topD / 2"),
    V("tw", "twist / 1 rad"),
]
sections = []
for k in range(SPANS + 1):
    s = f"{k} / {SPANS}"
    name = f"Section{k}"
    x = f"r{k} * (1 + wavePct / 100 * cos(waves * t)) * cos(t + tw * {s})"
    y = f"r{k} * (1 + wavePct / 100 * cos(waves * t)) * sin(t + tw * {s})"
    steps += [
        V(f"r{k}", f"R0 + (R1 - R0) * {s} + belly * sin(180 deg * {s})"),
        ["sketch.create", {"name": name, "plane": "xy", "offset": f"height * {s}"}],
        # Two halves, so the loft can be told where each loop starts (no re-matching of a twist).
        ["sketch.curve", {"sketch": name, "x": x, "y": y, "t": [0, "pi"]}],
        ["sketch.curve", {"sketch": name, "x": x, "y": y, "t": ["pi", "2 * pi"], "start": "e2", "end": "e1"}],
    ]
    sections.append({"sketch": name, "start": "e3"})
steps += [
    ["feature.loft", {"sections": sections, "name": "Vase"}],
    ["body.appearance", {"body": "Vase", "color": "#C2694B", "roughness": 0.6}],
    ["assert.add", {"name": "one body", "measure": "count", "of": {"kind": "body"}, "eq": "1"}],
]
params = [
    {"name": "bottomD", "label": "Bottom diameter", "group": "Shape", "order": 1, "min": "40 mm", "max": "150 mm",
     "step": "1 mm", "unit": "mm", "description": "Mean diameter at the foot"},
    {"name": "topD", "label": "Top diameter", "group": "Shape", "order": 2, "min": "40 mm", "max": "180 mm",
     "step": "1 mm", "unit": "mm", "description": "Mean diameter at the rim"},
    {"name": "height", "label": "Height", "group": "Shape", "order": 3, "min": "40 mm", "max": "220 mm",
     "step": "1 mm", "unit": "mm", "description": "Height of the vase"},
    {"name": "belly", "label": "Belly", "group": "Shape", "order": 4, "min": "-10 mm", "max": "20 mm",
     "step": "0.5 mm", "unit": "mm", "description": "How far the middle bulges out (negative: a waist)"},
    {"name": "waves", "label": "Waves", "group": "Waves", "order": 1, "kind": "integer", "min": "3", "max": "12",
     "description": "Number of waves round the vase"},
    {"name": "wavePct", "label": "Wave depth", "group": "Waves", "order": 2, "min": "2", "max": "100 / waves",
     "step": "0.5", "description": "How far a wave stands out, in % of the radius at that height; at most 100 / waves %"},
    {"name": "twist", "label": "Twist", "group": "Waves", "order": 3, "min": "-90 deg", "max": "90 deg",
     "step": "1 deg", "unit": "deg", "description": "How far the waves turn from the foot to the rim"},
]
for p in params:
    steps.append(["variable.publish", p])
steps.append(["document.info", {
    "title": "Wavy vase",
    "description": "A vase or plant-pot cover whose wall waves and twists, drawn from a formula: r = R (1 + depth x "
                   "cos(waves x t)), each height turned a little further. Set the diameters, the height and the "
                   "belly, the number and depth of the waves and the twist. The model is solid: print it in your "
                   "slicer's vase mode (spiralize outer contour) for a thin, watertight wall with a closed bottom. "
                   "Export it with File > Export... (STL or 3MF).",
    "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
    "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/wavy-vase",
    "tags": ["vase", "planter", "formula", "vase mode", "3D printing"]}])
steps.append(["jig.export", {"path": "dist/wavy-vase.3dcraftjig"}])

print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
