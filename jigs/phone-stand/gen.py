#!/usr/bin/env python3
"""Writes build.json of the phone-stand Jig:  python3 gen.py > build.json

The stand is one side profile extruded to the width: a base with a front lip, a slanted back rest, and
behind it a curved strut, a quarter-circle band whose centre lies where the back rest's back face meets
the table, so both of its arcs end square on that face. The strut leaves the back open (a rounded window
between the base, the back rest and the strut). Every corner of the profile is rounded, then the stand
is turned upright.
"""
import json


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


def side(e):
    return "F2:side(%s)" % e


steps = [
    V("angle", "65 deg"),
    V("deviceT", "11 mm"),
    V("lipH", "8 mm"),
    V("backL", "90 mm"),
    V("width", "70 mm"),
    V("thick", "5 mm"),
    V("cable", "1"),
    V("cableW", "12 mm"),
    V("lipT", "4 mm"),
    # The slot's back corner S, the back rest's top T (front) and Tb (back).
    V("xs", "lipT + deviceT / sin(angle) + 0.5 mm"),
    V("Tx", "xs + backL * cos(angle)"),
    V("Ty", "thick + backL * sin(angle)"),
    V("Tbx", "Tx + thick * sin(angle)"),
    V("Tby", "Ty - thick * cos(angle)"),
    # Centre C of the strut: the back face of the back rest at the table.
    V("cx", "xs + thick / sin(angle) - thick / tan(angle)"),
    # Outer radius: the foot reaches behind the device's centre of mass (about backL cos(angle) behind
    # the slot) by 12 mm, between 0.6 and 0.85 of the back rest.
    V("Ro", "clamp(backL * cos(angle) + 12 mm, 0.6 * backL, 0.85 * backL)"),
    V("Ri", "Ro - thick"),
    V("rnd", "min(1.5 mm, thick / 3)"),
    V("rTop", "0.45 * thick"),
    V("rHole", "min(2.5 mm, 0.1 * Ri)"),
    V("backWin", "1"),
    # A window through the back rest, into the open back, measured along the rest from S: from above the
    # window's lower corner to below the strut, two thirds of the width.
    V("u0", "thick / tan(angle) + rHole + 2 mm"),
    V("u1", "Ri - thick * (1 - cos(angle)) / sin(angle) - rHole - 2 mm"),
    V("winW", "width - 2 * max(8 mm, 0.18 * width)"),
    V("winR", "min(6 mm, (u1 - u0) / 2 - 0.5 mm, winW / 2 - 0.5 mm)"),
    V("winOn", "backWin && u1 - u0 >= 10 mm"),
]
P = [
    ["cx + Ro * cos(angle)", "Ro * sin(angle)"],          # e1  Po: the strut meets the back face
    ["Tbx", "Tby"],                                       # e2  Tb
    ["Tx", "Ty"],                                         # e3  T
    ["xs", "thick"],                                      # e4  S
    ["lipT", "thick"],                                    # e5
    ["lipT", "thick + lipH"],                             # e6
    ["0 mm", "thick + lipH"],                             # e7
    ["0 mm", "0 mm"],                                     # e8
    ["cx + Ro", "0 mm"],                                  # e9  Fo: the foot
]
steps += [
    ["sketch.create", {"name": "Profile", "plane": "xy"}],
    # Lines e10 (Po-Tb) ... e17 (origin-Fo).
    ["sketch.polyline", {"sketch": "Profile", "points": P}],
    # The strut's outer arc about C (e18), from the foot to Po.
    # (A formula curve, not sketch.arc: it has no unknowns, so a large jump of the parameters cannot
    # solve it the other way round.)
    ["sketch.curve", {"sketch": "Profile", "x": "cx + Ro * cos(t)", "y": "Ro * sin(t)", "t": ["0 deg", "angle"],
                      "start": "e9", "end": "e1"}],
    # The window: Q (back face at the base's top) e19, H1 (inner arc at the base's top) e20, line e21.
    ["sketch.polyline", {"sketch": "Profile", "points": [["xs + thick / sin(angle)", "thick"],
                                                         ["cx + sqrt(Ri^2 - thick^2)", "thick"]]}],
    # Pi e22 on the back face, the inner arc e23 and the back face e24 back to Q.
    ["sketch.point", {"sketch": "Profile", "at": ["cx + Ri * cos(angle)", "Ri * sin(angle)"]}],
    ["sketch.curve", {"sketch": "Profile", "x": "cx + Ri * cos(t)", "y": "Ri * sin(t)",
                      "t": ["asin(thick / Ri)", "angle"], "start": "e20", "end": "e22"}],
    ["sketch.line", {"sketch": "Profile", "from": "e22", "to": "e19"}],
    ["feature.extrude", {"sketch": "Profile", "distance": "width", "name": "Body"}],
    ["feature.fillet", {"name": "Rounds", "radius": "rnd", "edges": [
        [side("e14"), side("e15")], [side("e15"), side("e16")], [side("e16"), side("e17")], [side("e13"), side("e14")]]}],
    ["feature.fillet", {"name": "Top", "radius": "rTop", "edges": [[side("e10"), side("e11")], [side("e11"), side("e12")]]}],
    ["feature.fillet", {"name": "Joints", "radius": "2 * rnd", "edges": [[side("e12"), side("e13")]]}],
    ["feature.fillet", {"name": "Strut", "radius": "thick", "edges": [[side("e10"), side("e18")], [side("e17"), side("e18")]]}],
    ["feature.fillet", {"name": "Window", "radius": "rHole", "edges": [
        [side("e21"), side("e23")], [side("e23"), side("e24")], [side("e24"), side("e21")]]}],
    # The window tool, made along x (the rest) and turned onto the rest about S.
    ["feature.block", {"name": "WinBlock", "size": ["u1 - u0", "3 * thick", "winW"],
                       "position": ["u0", "-2 * thick", "width / 2 - winW / 2"]}],
    ["feature.fillet", {"name": "WinRound", "radius": "winR", "edges": [
        ["F8:face(0)", "F8:face(4)"], ["F8:face(0)", "F8:face(5)"], ["F8:face(1)", "F8:face(4)"], ["F8:face(1)", "F8:face(5)"]]}],
    ["feature.transform", {"name": "WinTool", "source": "WinRound", "angle": "angle", "axis": [0, 0, 1],
                           "translate": ["xs", "thick", "0 mm"]}],
    ["feature.when", {"feature": "WinBlock", "expr": "winOn"}],
    ["feature.when", {"feature": "WinRound", "expr": "winOn"}],
    ["feature.when", {"feature": "WinTool", "expr": "winOn"}],
    ["feature.boolean", {"op": "subtract", "target": "Window", "tool": "WinTool", "name": "Windowed"}],
    ["feature.block", {"name": "CableSlot", "size": ["xs", "thick + lipH + 2 mm", "cableW"],
                       "position": ["-1 mm", "-1 mm", "width / 2 - cableW / 2"]}],
    ["feature.when", {"feature": "CableSlot", "expr": "cable"}],
    ["feature.boolean", {"op": "subtract", "target": "Windowed", "tool": "CableSlot", "name": "Cut"}],
    ["feature.transform", {"source": "Cut", "angle": "180 deg", "axis": [0, 1, 1], "name": "Stand"}],
    ["body.appearance", {"body": "Stand", "color": "#8FA98A", "roughness": 0.55}],
    ["assert.add", {"name": "one body", "measure": "count", "of": {"kind": "body"}, "eq": "1"}],
]
params = [
    dict(name="angle", label="Angle", group="Device", order=1, min="50 deg", max="80 deg", step="1 deg", unit="deg",
         description="How far the device leans back, measured from the table"),
    dict(name="deviceT", label="Device thickness", group="Device", order=2, min="6 mm", max="16 mm", step="0.5 mm",
         unit="mm", description="Thickness of the phone or tablet with its case"),
    dict(name="backL", label="Back rest length", group="Device", order=3, min="50 mm", max="140 mm", step="1 mm",
         unit="mm", description="Length of the slanted back rest; about half the device's height is plenty"),
    dict(name="lipH", label="Lip height", group="Device", order=4, min="4 mm", max="16 mm", step="0.5 mm", unit="mm",
         description="Height of the front lip above the slot floor"),
    dict(name="width", label="Width", group="Stand", order=1, min="40 mm", max="120 mm", step="1 mm", unit="mm",
         description="Width of the stand"),
    dict(name="thick", label="Wall thickness", group="Stand", order=2, min="3 mm", max="8 mm", step="0.5 mm",
         unit="mm", description="Thickness of the base, the back rest and the curved strut"),
    dict(name="backWin", label="Back window", group="Stand", order=3, kind="boolean",
         description="A rounded window through the back rest, below the strut: lighter, and a way through for a cable"),
    dict(name="cable", label="Cable slot", group="Cable", order=1, kind="boolean",
         description="A slot through the lip and the slot floor for a charging cable"),
    dict(name="cableW", label="Cable slot width", group="Cable", order=2, min="6 mm", max="16 mm", step="0.5 mm",
         unit="mm", description="Width of the cable slot (the plug must pass)"),
]
for p in params:
    steps.append(["variable.publish", p])
steps += [
    ["document.info", {
        "title": "Phone and tablet stand",
        "description": "A stand that holds a phone or tablet at the angle you choose: a slanted back rest carried by "
                       "a curved strut, with an open back and rounded edges. Set the device's thickness (with its "
                       "case), the angle, the length of the back rest and the lip, the width, and whether a "
                       "charging cable passes through the front. Print it lying on its side (the profile on the bed) "
                       "for strength, without supports. Export it with File > Export... (STL or 3MF).",
        "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/phone-stand",
        "tags": ["phone", "tablet", "stand", "desk", "3D printing"]}],
    ["jig.export", {"path": "dist/phone-stand.3dcraftjig"}],
]
print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
