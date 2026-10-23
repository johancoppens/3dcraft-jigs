#!/usr/bin/env python3
"""Writes build.json for the GT2 2 mm pulley Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the tooth table is readable. Run it again only to change the model.

Tooth outline: the GT2 2 mm belt tooth from droftarts' "Parametric Pulley -
lots of tooth profiles" (https://www.thingiverse.com/thing:16627),
licensed CC BY-SA 4.0 (the model built from it is shared under the same
licence). The outline is the *belt* tooth on the outside diameter's chord
(y = 0 on the chord, y growing into the pulley), widened in x by the belt fit,
cut into the pulley once per tooth: the same construction as the original.
"""
import json

# GT2 2 mm belt tooth, (x, y) in mm, from thing:16627 (its points at
# y = -0.5 below the chord are left out: here the chord ends meet the land
# arcs). Runs from +x to -x.
GT2_TOOTH = [
    (0.747183, 0), (0.647876, 0.037218), (0.598311, 0.130528),
    (0.578556, 0.238423), (0.547158, 0.343077), (0.504649, 0.443762),
    (0.451556, 0.53975), (0.358229, 0.636924), (0.2484, 0.707276),
    (0.127259, 0.750044), (0, 0.76447), (-0.127259, 0.750044),
    (-0.2484, 0.707276), (-0.358229, 0.636924), (-0.451556, 0.53975),
    (-0.504797, 0.443762), (-0.547291, 0.343077), (-0.578605, 0.238423),
    (-0.598311, 0.130528), (-0.648009, 0.037218), (-0.747183, 0),
]
TOOTH_W = 1.494  # nominal tooth width of the profile (thing:16627)
HALF = GT2_TOOTH[0][0]
DEPTH = max(y for _, y in GT2_TOOTH)

INPUTS = [
    ("teeth", "20"),
    ("beltWidth", "6 mm"),
    ("bore", "5 mm"),
    ("beltFit", "0.2 mm"),
    ("flanges", "1"),
    ("hub", "1"),
    ("hubD", "16 mm"),
    ("hubL", "7 mm"),
]
DERIVED = [
    ("pitch", "2 mm"),
    ("pld", "0.254 mm"),                       # pitch line offset of GT2 2 mm
    ("PD", "teeth * pitch / pi"),              # pitch diameter
    ("OD", "PD - 2 * pld"),                    # outside diameter
    ("R", "OD / 2"),
    ("s", "(%g mm + beltFit) / (%g mm)" % (TOOTH_W, TOOTH_W)),  # x scale of the tooth
    ("hw", "%g mm * s" % HALF),                # half the chord the tooth is cut on
    ("d", "sqrt(R * R - hw * hw)"),            # centre to that chord
    ("th", "360 deg / teeth"),
    ("L", "beltWidth + 1 mm"),                 # length of the toothed part
    ("rootR", "d - %g mm" % DEPTH),            # deepest point of a groove
    ("flangeT", "1 mm"),
    ("lip", "2 mm"),
    # Without conditional features a flange or hub that is switched off is
    # tucked inside the toothed part, where joining it changes nothing.
    ("fR", "if(flanges, R + lip, rootR - 0.5 mm)"),
    ("f1z", "if(flanges, -flangeT, L / 4 - flangeT / 2)"),
    ("f2z", "if(flanges, L, 3 * L / 4 - flangeT / 2)"),
    ("hubR", "if(hub, hubD / 2, rootR - 0.7 mm)"),
    ("hubH", "if(hub, hubL, L / 4)"),
    ("hubZ", "if(hub, if(flanges, -flangeT, 0 mm) - hubL, 3 * L / 8)"),
    ("boreZ", "-flangeT - hubL - 1 mm"),
    ("boreH", "L + 2 * flangeT + hubL + 2 mm"),
]

SK = "ToothSketch"


def main():
    steps = []
    for name, expr in INPUTS + DERIVED:
        steps.append(["variable.set", {"name": name, "expr": expr}])

    steps.append(["sketch.create", {"name": SK, "plane": "xy"}])
    # The tooth, centred on +y, from its +x end (A) to its -x end (B):
    # x = px * s, y = d - py, held by expressions so it follows the variables.
    pts = []
    for px, py in GT2_TOOTH:
        x = "%s * s" % ("%g mm" % px if px >= 0 else "(%g mm)" % px)
        y = "d - %g mm" % py
        pts.append([x, y])
    steps.append(["sketch.polyline", {"sketch": SK, "points": pts}])
    # Points e1..e21, lines e22..e41: A is e1, B is e21.
    a_id, b_id = "e1", "e%d" % len(GT2_TOOTH)
    # The land arc from B to A turned by th (the next tooth's A).
    a1 = ["hw * cos(th) - d * sin(th)", "hw * sin(th) + d * cos(th)"]
    steps.append(["sketch.arc", {"sketch": SK, "center": ["0 mm", "0 mm"],
                                 "start": b_id, "end": a1}])
    # Arc: centre e42, end e43, arc e44. A ring of `teeth` chained runs.
    lines = ["e%d" % i for i in range(len(GT2_TOOTH) + 1, 2 * len(GT2_TOOTH))]
    steps.append(["sketch.pattern", {"sketch": SK, "entities": lines + ["e44"],
                                     "chain": [a_id, "e43"], "angle": "th",
                                     "center": "e42", "count": "teeth"}])
    steps.append(["feature.extrude", {"sketch": SK, "distance": "L", "name": "Toothed"}])
    steps.append(["feature.cylinder", {"name": "Flange1", "radius": "fR", "height": "flangeT",
                                       "position": ["0 mm", "0 mm", "f1z"]}])
    steps.append(["feature.cylinder", {"name": "Flange2", "radius": "fR", "height": "flangeT",
                                       "position": ["0 mm", "0 mm", "f2z"]}])
    steps.append(["feature.cylinder", {"name": "Hub", "radius": "hubR", "height": "hubH",
                                       "position": ["0 mm", "0 mm", "hubZ"]}])
    steps.append(["feature.boolean", {"op": "union", "target": "Toothed", "tool": "Flange1", "name": "U1"}])
    steps.append(["feature.boolean", {"op": "union", "target": "U1", "tool": "Flange2", "name": "U2"}])
    steps.append(["feature.boolean", {"op": "union", "target": "U2", "tool": "Hub", "name": "U3"}])
    steps.append(["feature.cylinder", {"name": "BoreTool", "radius": "bore / 2", "height": "boreH",
                                       "position": ["0 mm", "0 mm", "boreZ"]}])
    steps.append(["feature.boolean", {"op": "subtract", "target": "U3", "tool": "BoreTool", "name": "Pulley"}])
    steps.append(["body.appearance", {"body": "Pulley", "color": "#c9ccd1", "metallic": 0.6, "roughness": 0.4}])

    pub = [
        ("teeth", dict(label="Teeth", description="Number of teeth (GT2, 2 mm pitch)", group="Pulley", order=1,
                       kind="integer", min="12", max="60")),
        ("beltWidth", dict(label="Belt width", description="Width of the belt; the toothed part is 1 mm longer",
                           group="Pulley", order=2, min="4 mm", max="20 mm", step="0.5 mm", unit="mm")),
        ("beltFit", dict(label="Belt fit", description="Extra width of each groove (printer tuning); 0.2 mm fits most printers",
                         group="Pulley", order=3, min="0 mm", max="0.3 mm", step="0.01 mm", unit="mm")),
        ("bore", dict(label="Bore", description="Diameter of the shaft hole",
                      group="Bore and hub", order=1, min="2 mm", max="OD - 4 mm", step="0.1 mm", unit="mm")),
        ("hub", dict(label="Hub", description="A hub below the pulley (for a set screw you drill)",
                     group="Bore and hub", order=2, kind="boolean")),
        ("hubD", dict(label="Hub diameter", description="Outside diameter of the hub",
                      group="Bore and hub", order=3, min="max(8 mm, bore + 4 mm)", max="60 mm", step="0.5 mm", unit="mm")),
        ("hubL", dict(label="Hub length", description="Length of the hub",
                      group="Bore and hub", order=4, min="3 mm", max="20 mm", step="0.5 mm", unit="mm")),
        ("flanges", dict(label="Flanges", description="A 1 mm flange on each side, 2 mm above the teeth, that keeps the belt on",
                         group="Flanges", order=1, kind="boolean")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        steps.append(["variable.publish", p])
    steps.append(["document.info", {
        "title": "GT2 pulley (2 mm pitch)",
        "description": "A timing pulley for GT2 belts with 2 mm pitch: set the teeth, the belt width and the bore, "
                       "with or without flanges and a hub. Pitch diameter = teeth x 2 mm / pi; the outside diameter is "
                       "0.508 mm less. Belt fit widens the grooves for 3D printing. Export it with File > Export... (STL or 3MF "
                       "to print, STEP for CAD). Tooth outline from droftarts' Parametric Pulley "
                       "(thingiverse.com/thing:16627), CC BY-SA 4.0; this Jig is shared under the same licence.",
        "author": "3DCraft Jigs (tooth outline: droftarts, thing:16627)",
        "licence": "CC-BY-SA-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/gt2-pulley",
        "tags": ["pulley", "GT2", "timing belt", "3D printing"]}])
    steps.append(["jig.export", {"path": "dist/gt2-pulley.3dcraftjig"}])
    return steps


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(s) for s in main()) + "\n]")
