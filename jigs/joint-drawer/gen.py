#!/usr/bin/env python3
"""Writes build.json for the dovetail / finger-joint drawer Jig (python3 gen.py > build.json).

A drawer or box of four boards joined at the corners with through dovetails or
finger (box) joints, with a bottom in a groove (or under the boards) and a knob.

The front and the back carry the tails (or the end fingers); the sides carry the
sockets. One tail is a prism drawn in the x-z plane: as wide as `TW` at the end
of the front board (x = 0), narrowing by the slope towards the baseline at the
side's inner face (x = t). A finger joint is the same with slope 0 and the pins as
wide as the fingers. The sockets of the sides are the tails cut out of them; the
front's waste between its tails ("pins" here) is the corner zone without the
tails.

Axes: x across the front (the left side at x = 0), y from the front (y = 0) to the
back, z up.
"""
import json

INPUTS = [
    ("innerW", "240 mm"),
    ("innerD", "200 mm"),
    ("innerH", "100 mm"),
    ("t", "15 mm"),
    ("tails", "3"),
    ("joint", "2"),        # 1 finger, 2 dovetail
    ("slopeChoice", "2"),  # 1 = 1:6 (softwood), 2 = 1:8 (hardwood)
    ("groove", "1"),
    ("knob", "1"),
]
DERIVED = [
    ("dovetail", "joint == 2"),
    ("bt", "clamp(t / 2, 4 mm, 8 mm)"),           # bottom thickness
    ("gOff", "max(6.3 mm, t / 2 + 0.3 mm)"),       # groove above the lower edge (off round numbers, so it never meets a tail's corner exactly)
    ("gd", "t / 2"),                              # groove depth
    ("H", "if(groove, innerH + gOff + bt, innerH)"),
    ("Wo", "innerW + 2 * t"),
    ("Do", "innerD + 2 * t"),
    ("s", "if(dovetail, choose(slopeChoice, 1 / 6, 1 / 8), 0)"),
    ("N", "tails"),
    # Finger joint: 2N + 1 equal parts, the front owning both ends. Dovetail: pins pn
    # wide at the end of the front board, half pins as wide at the top and the bottom.
    ("pn", "if(dovetail, clamp(0.25 * H / (N + 0.5), 4 mm, 20 mm), H / (2 * N + 1))"),
    ("TW", "(H - (N + 1) * pn) / N"),
    ("P", "TW + pn"),
    ("maxTails", "clamp(floor(H / (2.2 * t)), 1, 12)"),
    ("kr", "clamp(0.11 * H, 7 mm, 14 mm)"),        # knob radius
]


def block(name, x0, x1, y0, y1, z0, z1):
    return ["feature.block", {"name": name,
                              "size": ["(%s) - (%s)" % (x1, x0), "(%s) - (%s)" % (y1, y0), "(%s) - (%s)" % (z1, z0)],
                              "position": [x0, y0, z0]}]


def main():
    s = []
    for n, e in INPUTS + DERIVED:
        s.append(["variable.set", {"name": n, "expr": e}])

    # One tail, on the zx plane (sketch u = z, v = x), from y = -1 mm through the front board.
    s.append(["sketch.create", {"name": "TailSketch", "plane": "zx", "offset": "-1 mm"}])
    s.append(["sketch.polyline", {"sketch": "TailSketch", "closed": True, "points": [
        ["pn - s * 1 mm", "-1 mm"], ["pn + TW + s * 1 mm", "-1 mm"],
        ["pn + TW - s * t", "t"], ["pn + s * t", "t"]]}])
    # (TW wide at the end of the board, x = 0; it starts 1 mm outside, where it is 2 s mm wider.)
    s.append(["feature.extrude", {"sketch": "TailSketch", "distance": "t + 1 mm", "name": "Tail"}])
    s.append(["feature.pattern", {"name": "Tails", "source": "Tail", "count": "N", "step": ["0 mm", "0 mm", "P"]}])
    s.append(block("Zone", "-1 mm", "t", "-1 mm", "t", "-1 mm", "H + 1 mm"))
    s.append(["feature.boolean", {"op": "subtract", "target": "Zone", "tool": "Tails", "keepTool": True, "name": "Pins"}])
    s.append(["feature.mirror", {"source": "Pins", "normal": [1, 0, 0], "point": ["Wo / 2", "0 mm", "0 mm"],
                                 "keep": True, "name": "PinsR"}])
    s.append(["feature.mirror", {"source": "Tails", "normal": [0, 1, 0], "point": ["0 mm", "Do / 2", "0 mm"],
                                 "keep": True, "name": "TailsBack"}])

    # Front: the waste between its tails cut away at both ends.
    s.append(block("FrontBlank", "0 mm", "Wo", "0 mm", "t", "0 mm", "H"))
    s.append(["feature.boolean", {"op": "subtract", "target": "FrontBlank", "tool": "Pins", "name": "FrontL"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "FrontL", "tool": "PinsR", "name": "FrontJ"}])
    # Left side: the sockets for the front's and the back's tails.
    s.append(block("SideBlank", "0 mm", "t", "0 mm", "Do", "0 mm", "H"))
    s.append(["feature.boolean", {"op": "subtract", "target": "SideBlank", "tool": "Tails", "name": "SideF"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "SideF", "tool": "TailsBack", "name": "SideJ"}])

    # Groove for the bottom, in the inner faces (stopped half a groove depth into the corners).
    s.append(block("FrontGroove", "t - gd", "Wo - t + gd", "t - gd", "t + 1 mm", "gOff", "gOff + bt"))
    s.append(["feature.when", {"feature": "FrontGroove", "expr": "groove"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "FrontJ", "tool": "FrontGroove", "name": "Front"}])
    s.append(block("SideGroove", "t - gd", "t + 1 mm", "t - gd", "Do - t + gd", "gOff", "gOff + bt"))
    s.append(["feature.when", {"feature": "SideGroove", "expr": "groove"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "SideJ", "tool": "SideGroove", "name": "LeftSide"}])
    s.append(["feature.mirror", {"source": "Front", "normal": [0, 1, 0], "point": ["0 mm", "Do / 2", "0 mm"],
                                 "keep": True, "name": "Back"}])
    s.append(["feature.mirror", {"source": "LeftSide", "normal": [1, 0, 0], "point": ["Wo / 2", "0 mm", "0 mm"],
                                 "keep": True, "name": "RightSide"}])

    # Bottom: in the groove (0.5 mm short of its floor all round), or under the boards.
    s.append(block("Bottom", "if(groove, t - gd + 0.5 mm, 0 mm)", "if(groove, Wo - t + gd - 0.5 mm, Wo)",
                   "if(groove, t - gd + 0.5 mm, 0 mm)", "if(groove, Do - t + gd - 0.5 mm, Do)",
                   "if(groove, gOff, -bt)", "if(groove, gOff + bt, 0 mm)"))

    # Knob: a short brass cylinder on the front with a rounded rim.
    s.append(["feature.cylinder", {"name": "KnobBody", "radius": "kr", "height": "1.4 * kr",
                                   "position": ["Wo / 2", "0 mm", "H / 2"], "axis": [0, -1, 0]}])
    s.append(["feature.fillet", {"name": "Knob", "edges": [["F_KNOB:face(0)", "F_KNOB:face(2)"]], "radius": "0.35 * kr"}])
    for f in ("KnobBody", "Knob"):
        s.append(["feature.when", {"feature": f, "expr": "knob"}])

    for b in ("Front", "Back"):
        s.append(["body.appearance", {"body": b, "color": "#7A5638", "roughness": 0.7}])
    for b in ("LeftSide", "RightSide"):
        s.append(["body.appearance", {"body": b, "color": "#D9B98A", "roughness": 0.75}])
    s.append(["body.appearance", {"body": "Bottom", "color": "#E8DFCC", "roughness": 0.85}])
    s.append(["body.appearance", {"body": "Knob", "color": "#B8954A", "metallic": 0.9, "roughness": 0.35}])

    s.append(["assert.add", {"name": "boards do not overlap", "measure": "interference",
                             "of": ["Front", "Back", "LeftSide", "RightSide", "Bottom"]}])

    pub = [
        ("innerW", dict(label="Inner width", description="Inside width, between the sides", group="Size", order=1,
                        min="60 mm", max="600 mm", step="1 mm", unit="mm")),
        ("innerD", dict(label="Inner depth", description="Inside depth, front to back", group="Size", order=2,
                        min="60 mm", max="600 mm", step="1 mm", unit="mm")),
        ("innerH", dict(label="Inner height", description="Inside height, from the bottom to the top edge", group="Size", order=3,
                        min="40 mm", max="250 mm", step="1 mm", unit="mm")),
        ("t", dict(label="Board thickness", description="Thickness of the four boards", group="Size", order=4,
                   min="8 mm", max="22 mm", step="0.5 mm", unit="mm")),
        ("joint", dict(label="Joint", description="Finger (box) joints or through dovetails", group="Joints", order=1,
                       kind="choice", choices=["finger", "dovetail"])),
        ("tails", dict(label="Tails (fingers)", description="Number of tails on each end of the front and the back; for a finger joint the number of fingers of the side",
                       group="Joints", order=2, kind="integer", min="1", max="maxTails")),
        ("slopeChoice", dict(label="Dovetail slope", description="1:6 for softwood, 1:8 for hardwood (not used by a finger joint)",
                             group="Joints", order=3, kind="choice", choices=["1:6 softwood", "1:8 hardwood"])),
        ("groove", dict(label="Bottom in a groove", description="The bottom slides into a groove in all four boards; off: it is fixed under them",
                        group="Details", order=1, kind="boolean")),
        ("knob", dict(label="Knob", description="A brass knob in the middle of the front", group="Details", order=2,
                      kind="boolean")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        s.append(["variable.publish", p])

    s.append(["set.define", {"name": "Marking templates", "kind": "face", "where": {"any": [
        {"in": "Front", "madeBy": "FrontBlank", "normal": {"along": "-y"}},
        {"in": "LeftSide", "madeBy": "SideBlank", "normal": {"along": "-x"}},
    ]}}])
    s.append(["document.info", {
        "title": "Dovetail and finger-joint drawer",
        "description": "A drawer or box for woodworkers, joined with through dovetails or finger joints: set the inside "
                     "width, depth and height, the board thickness, the number of tails and the slope (1:6 softwood, "
                     "1:8 hardwood), with the bottom in a groove and a brass knob. Export STEP or STL for CAD or a CNC; "
                     "the face set \"Marking templates\" (File > Export..., SVG or DXF) gives the front's tails and a side's "
                     "sockets at true size, to print and mark out by hand.",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/joint-drawer",
        "tags": ["woodworking", "dovetail", "finger joint", "drawer", "box"]}])
    s.append(["jig.export", {"path": "dist/joint-drawer.3dcraftjig"}])
    return resolve(s)


FEATURE_CMDS = {"feature.block", "feature.cylinder", "feature.fillet", "feature.chamfer", "feature.pattern",
                "feature.boolean", "feature.mirror", "feature.transform", "feature.extrude", "sketch.create"}


def resolve(steps):
    """Feature ids are F1, F2, ... in history order (sketches included); face names
    need them: F_KNOB becomes the id of KnobBody."""
    ids, n = {}, 0
    for cmd, p in steps:
        if cmd in FEATURE_CMDS:
            n += 1
            ids[p["name"]] = "F%d" % n
    text = json.dumps(steps).replace("F_KNOB:", ids["KnobBody"] + ":")
    return json.loads(text)


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
