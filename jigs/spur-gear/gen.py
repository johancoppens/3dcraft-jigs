#!/usr/bin/env python3
"""Writes build.json of the spur-gear Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written. The involute outline is drawn
from formula curves (sketch.curve) and repeated round as a chained sketch pattern; the bore and the set
screws come from scripts/shaftlib.py (shared with gt2-pulley); the disc can be lightened with a web
and/or holes when the gear is large enough.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import shaftlib  # noqa: E402


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


def W(feature, expr):
    return ["feature.when", {"feature": feature, "expr": expr}]


steps = [
    ["table.set", {"name": "modules", "columns": ["size", {"name": "value", "unit": "mm"}],
                   "rows": [["0.5 mm", 0.5], ["0.8 mm", 0.8], ["1 mm", 1], ["1.25 mm", 1.25], ["1.5 mm", 1.5],
                            ["2 mm", 2], ["2.5 mm", 2.5], ["3 mm", 3]]}],
    ["table.set", {"name": "angles", "columns": ["angle", {"name": "value", "unit": "deg"}],
                   "rows": [["14.5 deg", 14.5], ["20 deg", 20], ["25 deg", 25]]}],
] + shaftlib.tables()

INPUTS = [
    ("moduleSize", "4"), ("teeth", "30"), ("pressure", "2"), ("width", "6 mm"), ("bore", "5 mm"),
    ("hub", "1"), ("hubD", "14 mm"), ("hubL", "6 mm"), ("disc", "4"),
]
GEAR = [
    ("module", "modules[moduleSize].value"),
    ("alpha", "angles[pressure].value"),
    ("pd", "module * teeth"),
    ("rp", "pd / 2"),
    ("rb", "rp * cos(alpha)"),
    ("ra", "rp + module"),
    ("rf", "rp - 1.25 * module"),
    ("g", "-pi / (2 * teeth) - (tan(alpha) - alpha / 1 rad)"),
    ("rs", "max(rb, rf + 0.1 * module)"),
    ("t0", "sqrt((rs / rb)^2 - 1)"),
    ("ta", "sqrt((ra / rb)^2 - 1)"),
    ("phis", "g + t0 - atan(t0) / 1 rad"),
    ("half", "pi / teeth"),
    ("thetaA", "g + ta - atan(ta) / 1 rad"),
    # The hub is kept between the bore + 0.8 mm and 0.6 times the root diameter (and the root less 4 modules).
    ("hubE", "clamp(hubD, bore + 0.8 mm, max(bore + 0.8 mm, min(1.2 * rf, 2 * rf - 4 * module)))"),
    ("hubC", "min(0.5 mm, (hubE - bore) / 6, hubL / 4)"),
]
LIGHT = [
    # The disc between the boss (round the bore, the keyway and the hub) and the rim (under the teeth).
    ("rimR", "rf - max(1.5 mm, 2 * module)"),
    ("bossR", "max(bore / 2 + max(2 mm, module) + if(keyOn, keyT, 0 mm), if(hub, hubE / 2, 0 mm))"),
    ("room", "rimR - bossR"),
    ("webT", "max(1.5 mm, width / 3)"),
    ("webD", "(width - webT) / 2"),
    ("webOn", "(disc == 2 || disc == 4) && room >= 3 mm && webD >= 0.5 mm"),
    ("rc", "(rimR + bossR) / 2"),
    ("nh", "clamp(floor(pi * rc / (0.35 * room + 1.5 mm)), 4, 8)"),
    ("rh", "min(0.35 * room, rc * sin(180 deg / nh) - 1 mm)"),
    ("holesOn", "(disc == 3 || disc == 4) && rh >= 1 mm"),
]
for name, expr in INPUTS + shaftlib.INPUTS + GEAR + shaftlib.variables("hubE", "hub", "rf") + LIGHT:
    steps.append(V(name, expr))

steps += [
    ["sketch.create", {"name": "Outline"}],
    ["sketch.point", {"sketch": "Outline", "at": ["rf * cos(phis * 1 rad)", "rf * sin(phis * 1 rad)"]}],
    ["sketch.curve", {"sketch": "Outline", "x": "rb * (cos(g + t) + t * sin(g + t))",
                      "y": "rb * (sin(g + t) - t * cos(g + t))", "t": ["t0", "ta"]}],
    ["sketch.curve", {"sketch": "Outline", "x": "rb * (cos(g + t) + t * sin(g + t))",
                      "y": "-rb * (sin(g + t) - t * cos(g + t))", "t": ["t0", "ta"]}],
    ["sketch.curve", {"sketch": "Outline", "x": "ra * cos(t)", "y": "ra * sin(t)", "t": ["thetaA", "-thetaA"],
                      "start": "e3", "end": "e6"}],
    ["sketch.curve", {"sketch": "Outline", "x": "rf * cos(t)", "y": "rf * sin(t)", "t": ["-phis", "2 * half + phis"]}],
    ["sketch.line", {"sketch": "Outline", "from": "e1", "to": "e2"}],
    ["sketch.line", {"sketch": "Outline", "from": "e5", "to": "e9"}],
    ["sketch.pattern", {"sketch": "Outline", "entities": ["e12", "e4", "e8", "e7", "e13", "e11"], "chain": ["e1", "e10"],
                        "angle": "360 deg / teeth", "center": ["0 mm", "0 mm"], "count": "teeth"}],
    ["feature.extrude", {"sketch": "Outline", "distance": "width", "name": "Rim"}],          # F2
    # The hub, its top edge broken (F3: face 0 the wall, 2 the top).
    ["feature.cylinder", {"name": "Hub", "radius": "hubE / 2", "height": "hubL",
                          "position": ["0 mm", "0 mm", "width"]}],                            # F3
    ["feature.chamfer", {"name": "HubC", "distance": "hubC", "edges": [["F3:face(0)", "F3:face(2)"]]}],
    W("Hub", "hub"), W("HubC", "hub"),
    ["feature.boolean", {"op": "union", "target": "Rim", "tool": "HubC", "name": "WithHub"}],
    # A web: the disc recessed from both faces between the boss and the rim.
    ["feature.cylinder", {"name": "WebOuter", "radius": "rimR", "height": "webD + 1 mm",
                          "position": ["0 mm", "0 mm", "-1 mm"]}],
    ["feature.cylinder", {"name": "WebInner", "radius": "bossR", "height": "webD + 3 mm",
                          "position": ["0 mm", "0 mm", "-2 mm"]}],
    ["feature.boolean", {"op": "subtract", "target": "WebOuter", "tool": "WebInner", "name": "Web1"}],
    ["feature.mirror", {"source": "Web1", "normal": [0, 0, 1], "point": ["0 mm", "0 mm", "width / 2"], "keep": True,
                        "name": "Web2"}],
    W("WebOuter", "webOn"), W("WebInner", "webOn"), W("Web1", "webOn"), W("Web2", "webOn"),
    ["feature.boolean", {"op": "subtract", "target": "WithHub", "tool": "Web1", "name": "Webbed1"}],
    ["feature.boolean", {"op": "subtract", "target": "Webbed1", "tool": "Web2", "name": "Webbed"}],
    # Lightening holes on a circle between the boss and the rim.
    ["feature.cylinder", {"name": "Hole", "radius": "rh", "height": "width + 2 mm",
                          "position": ["rc * cos(180 deg / nh)", "rc * sin(180 deg / nh)", "-1 mm"]}],
    ["feature.pattern", {"name": "Holes", "source": "Hole", "count": "nh", "angle": "360 deg / nh", "axis": [0, 0, 1]}],
    W("Hole", "holesOn"), W("Holes", "holesOn"),
    ["feature.boolean", {"op": "subtract", "target": "Webbed", "tool": "Holes", "name": "Disc"}],
]
steps += shaftlib.steps(bore_z0="-1 mm", bore_h="width + hubL + 2 mm", scr_z="width + hubL / 2",
                        nut_z0="width + hubL / 2 - nutW / sqrt(3)", nut_h="hubL / 2 + nutW / sqrt(3) + 1 mm",
                        target="Disc", name="Gear")

# The volume in closed form: the root disc and the teeth (the involute's area integral), the hub less its
# chamfer, less the bore (with its flat or keyway), the web's recesses and the holes. The set screws and
# nut slots are estimated (a cylinder and a box each) and widen the tolerance by a share of their volume.
steps += [
    V("u", "-g"),
    V("iA", "u * ta^2 / 2 - ta^3 / 3 + ((ta^2 + 1) * atan(ta) / 1 rad - ta) / 2"),
    V("i0", "u * t0^2 / 2 - t0^3 / 3 + ((t0^2 + 1) * atan(t0) / 1 rad - t0) / 2"),
    V("toothArea", "(u - (t0 - atan(t0) / 1 rad)) * (rs^2 - rf^2) + 2 * rb^2 * (iA - i0)"),
    V("br", "bore / 2"),
    V("flatA", "br^2 * acos((br - flatDepth) / br) / 1 rad - (br - flatDepth) * sqrt(br^2 - (br - flatDepth)^2)"),
    V("keyA", "if(keyOn, keyW * (br + keyT) - (keyW / 2 * sqrt(br^2 - keyW^2 / 4) + br^2 * asin(keyW / (2 * br)) / 1 rad), 0 * (1 mm)^2)"),
    V("boreA", "pi * br^2 - if(flatOn, flatA, 0 * (1 mm)^2) + if(keyOn, keyA, 0 * (1 mm)^2)"),
    # Per screw: the hole from the bore (the flat, past the keyway) to the outside, and the nut slot.
    V("nutV", "if(nutOn, nutT * nutW * (hubL / 2 + nutW / sqrt(3)) - pi * (scrD / 2)^2 * nutT, 0 * (1 mm)^3)"),
    V("screw1V", "pi * (scrD / 2)^2 * (hubE / 2 - br + if(flatOn, flatDepth, 0 mm) - if(keyOn, keyT, 0 mm)) + nutV"),
    V("screw2V", "if(scr2On, pi * (scrD / 2)^2 * (hubE / 2 - br) + nutV, 0 * (1 mm)^3)"),
    V("screwV", "if(scrOn, screw1V + screw2V, 0 * (1 mm)^3)"),
    V("gearV", "(pi * rf^2 + teeth * toothArea) * width"
               " + if(hub, pi * (hubE / 2)^2 * hubL - pi * hubC^2 * (hubE / 2 - hubC / 3), 0 * (1 mm)^3)"
               " - boreA * (width + if(hub, hubL, 0 mm))"
               " - if(webOn, 2 * pi * (rimR^2 - bossR^2) * webD, 0 * (1 mm)^3)"
               " - if(holesOn, nh * pi * rh^2 * if(webOn, webT, width), 0 * (1 mm)^3)"
               " - screwV"),
    ["assert.add", {"name": "volume", "measure": "volume", "of": "Gear", "eq": "gearV",
                    "tol": "1e-6 * gearV + 0.2 * screwV"}],
    ["assert.add", {"name": "one body", "measure": "count", "of": {"kind": "body"}, "eq": "1"}],
    ["body.appearance", {"body": "Gear", "color": "#D4A24C", "roughness": 0.45}],
]

params = [
    dict(name="moduleSize", label="Module", group="Teeth", order=1, kind="choice", choicesFrom="modules",
         description="Tooth size: pitch diameter / teeth. Gears that mesh have the same module and pressure angle"),
    dict(name="teeth", label="Teeth", group="Teeth", order=2, kind="integer", min="8", max="80",
         description="Number of teeth; the pitch diameter is module x teeth"),
    dict(name="pressure", label="Pressure angle", group="Teeth", order=3, kind="choice", choicesFrom="angles",
         description="20 deg is the common standard; 14.5 deg older gears, 25 deg stronger teeth"),
    dict(name="width", label="Face width", group="Teeth", order=4, min="2 mm", max="30 mm", step="0.5 mm", unit="mm",
         description="Thickness of the gear"),
    dict(name="bore", label="Bore", group="Bore and hub", order=1, min="1 mm", max="min(rf, 2 * rf - 3 * module)",
         step="0.1 mm", unit="mm",
         description="Diameter of the shaft hole; at most half the root diameter (and the root diameter less three modules)"),
    dict(name="hub", label="Hub", group="Bore and hub", order=4, kind="boolean",
         description="A hub on one side, which holds the set screws (or a press fit on the shaft)"),
    dict(name="hubD", label="Hub diameter", group="Bore and hub", order=5, min="max(bore + 2 mm, %s)" % shaftlib.hub_d_min(),
         max="bore + 40 mm", step="0.5 mm", unit="mm",
         description="Outside diameter of the hub; kept at least 0.8 mm over the bore and at most 0.6 times the root "
                     "diameter (and the root diameter less four modules)"),
    dict(name="hubL", label="Hub length", group="Bore and hub", order=6, min=shaftlib.hub_l_min("2 mm"), max="20 mm",
         step="0.5 mm", unit="mm", description="How far the hub stands out; long enough for the screw or the nut slot"),
    dict(name="disc", label="Disc", group="Disc", order=1, kind="choice",
         choices=["Solid", "Web", "Holes", "Web and holes"],
         description="Lighten a large gear: a web (the disc recessed from both faces to a third of the width, at "
                     "least 1.5 mm) and/or a ring of 4 to 8 holes between the hub and the rim. Only built when the gear "
                     "has room for it"),
]
for p in params:
    steps.append(["variable.publish", p])
steps += shaftlib.publish("Bore and hub", 2, "hub")
steps += [
    ["document.info", {
        "title": "Involute spur gear",
        "description": "A spur gear with true involute teeth, drawn from the involute's formula: choose the module and "
                       "the pressure angle, set the number of teeth, the face width and the bore (round, D-shaft or "
                       "keyway), with or without a hub with one or two set screws (M2.5, M3 or M4, optionally in "
                       "captive nuts), and lighten a large gear with a web and holes. Pitch diameter = module x teeth, "
                       "outside diameter = module x (teeth + 2); two gears mesh when they share module and pressure "
                       "angle, at a centre distance of module x (teeth1 + teeth2) / 2. Export it with File > Export... "
                       "(STL or 3MF to print, STEP for CAD).",
        "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/spur-gear",
        "tags": ["gear", "involute", "3D printing", "mechanism"]}],
    ["jig.export", {"path": "dist/spur-gear.3dcraftjig"}],
]

print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
