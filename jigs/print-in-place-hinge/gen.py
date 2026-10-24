#!/usr/bin/env python3
"""Writes build.json for the print-in-place hinge Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the construction is readable. Run it again only to change the model.

The hinge lies flat on the bed, its axis along x. Leaf A (y < 0) has the
knuckles 0, 2, 4, ...; leaf B (y > 0) has 1, 3, .... Between two knuckles
A's knuckle carries a 45 degree cone (the pin) that sits in a conical socket
of B's knuckle, the clearance away all round: a cone's roof needs no support.
"""
import json


class Doc:
    def __init__(self):
        self.steps = []

    def var(self, name, expr):
        self.steps.append(["variable.set", {"name": name, "expr": expr}])

    def do(self, cmd, params):
        self.steps.append([cmd, params])


INPUTS = [
    ("length", "60 mm"),       # along the axis
    ("leafW", "22 mm"),        # each leaf, from the axis
    ("thick", "2.5 mm"),       # leaf thickness
    ("knuckleD", "8 mm"),
    ("knuckles", "5"),
    ("pinD", "4 mm"),          # base diameter of the conical pins
    ("clearance", "0.3 mm"),
    ("holes", "2"),            # screw holes per leaf
    ("holeD", "3.5 mm"),
]
DERIVED = [
    ("R", "knuckleD / 2"),
    ("z0", "R - 0.3 mm"),                        # the axis: the knuckles stand 0.3 mm flat on the bed
    ("g", "clearance"),                          # gap between knuckles
    ("s", "(length - (knuckles - 1) * g) / knuckles"),   # knuckle length
    ("pitch", "2 * (s + g)"),
    ("nA", "ceil(knuckles / 2)"),
    ("nB", "floor(knuckles / 2)"),               # also A's pins pointing +x
    ("nL", "floor((knuckles - 1) / 2)"),         # A's pins pointing -x
    ("h", "pinD / 2"),                           # pin height (45 degrees)
    ("sh", "h + clearance * sqrt(2)"),           # socket: the pin's cone moved out by the clearance
    ("zr", "R + clearance"),                     # radius kept clear round the other leaf's knuckles
    ("csD", "min(holeD / 2, 0.6 * thick)"),      # countersink depth (90 degrees)
    ("csR", "holeD / 2 + csD"),
    ("yh", "(zr + leafW) / 2"),                  # screw holes midway across the leaf
    ("cr", "min(3 mm, (leafW - zr) / 3)"),       # leaf corner radius
]


def main():
    d = Doc()
    for name, expr in INPUTS + DERIVED:
        d.var(name, expr)
    X = [1, 0, 0]
    # Leaf A, its knuckles, cut clear round B's knuckles, then its pins.
    d.do("feature.block", {"name": "LeafA", "size": ["length + 2 mm", "leafW + 1 mm", "thick + 1 mm"],
                           "position": ["-1 mm", "-leafW - 1 mm", "-1 mm"]})
    d.do("feature.cylinder", {"name": "KnA", "radius": "R", "height": "s + 1 mm", "axis": X, "position": ["-0.5 mm", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "KnucklesA", "source": "KnA", "count": "nA", "step": ["pitch", "0 mm", "0 mm"]})
    d.do("feature.boolean", {"op": "union", "target": "LeafA", "tool": "KnucklesA", "name": "A0"})
    d.do("feature.cylinder", {"name": "ZoneB", "radius": "zr", "height": "s + 2 * g", "axis": X,
                              "position": ["s", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "ZonesB", "source": "ZoneB", "count": "nB", "step": ["pitch", "0 mm", "0 mm"]})
    d.do("feature.boolean", {"op": "subtract", "target": "A0", "tool": "ZonesB", "name": "A1"})
    d.do("feature.cone", {"name": "PinR", "radius": "h + 0.5 mm", "height": "h + 0.5 mm", "axis": X,
                          "position": ["s - 0.5 mm", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "PinsR", "source": "PinR", "count": "nB", "step": ["pitch", "0 mm", "0 mm"]})
    d.do("feature.boolean", {"op": "union", "target": "A1", "tool": "PinsR", "name": "A2"})
    d.do("feature.cone", {"name": "PinL", "radius": "h + 0.5 mm", "height": "h + 0.5 mm", "axis": [-1, 0, 0],
                          "position": ["pitch + 0.5 mm", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "PinsL", "source": "PinL", "count": "max(1, nL)", "step": ["pitch", "0 mm", "0 mm"]})
    for f in ("PinL", "PinsL"):
        d.do("feature.when", {"feature": f, "expr": "nL > 0"})
    d.do("feature.boolean", {"op": "union", "target": "A2", "tool": "PinsL", "name": "A3"})

    # Leaf B, its knuckles, cut clear round A's knuckles, then the sockets.
    d.do("feature.block", {"name": "LeafB", "size": ["length + 2 mm", "leafW + 1 mm", "thick + 1 mm"],
                           "position": ["-1 mm", "0 mm", "-1 mm"]})
    d.do("feature.cylinder", {"name": "KnB", "radius": "R", "height": "s + 1 mm", "axis": X, "position": ["s + g - 0.5 mm", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "KnucklesB", "source": "KnB", "count": "nB", "step": ["pitch", "0 mm", "0 mm"]})
    d.do("feature.boolean", {"op": "union", "target": "LeafB", "tool": "KnucklesB", "name": "B0"})
    d.do("feature.cylinder", {"name": "ZoneA", "radius": "zr", "height": "s + 2 * g", "axis": X,
                              "position": ["-g", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "ZonesA", "source": "ZoneA", "count": "nA", "step": ["pitch", "0 mm", "0 mm"]})
    d.do("feature.boolean", {"op": "subtract", "target": "B0", "tool": "ZonesA", "name": "B1"})
    d.do("feature.cone", {"name": "SocketR", "radius": "sh - g / 2", "height": "sh - g / 2", "axis": X,
                          "position": ["s + g / 2", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "SocketsR", "source": "SocketR", "count": "nB", "step": ["pitch", "0 mm", "0 mm"]})
    d.do("feature.boolean", {"op": "subtract", "target": "B1", "tool": "SocketsR", "name": "B2"})
    d.do("feature.cone", {"name": "SocketL", "radius": "sh - g / 2", "height": "sh - g / 2", "axis": [-1, 0, 0],
                          "position": ["pitch - g / 2", "0 mm", "z0"]})
    d.do("feature.pattern", {"name": "SocketsL", "source": "SocketL", "count": "max(1, nL)", "step": ["pitch", "0 mm", "0 mm"]})
    for f in ("SocketL", "SocketsL"):
        d.do("feature.when", {"feature": f, "expr": "nL > 0"})
    d.do("feature.boolean", {"op": "subtract", "target": "B2", "tool": "SocketsL", "name": "B3"})

    # Countersunk screw holes in both leaves.
    for n, sgn in (("A", "-"), ("B", "")):
        d.do("feature.cylinder", {"name": "Hole" + n, "radius": "holeD / 2", "height": "thick + 3 mm",
                                  "position": ["length / holes / 2", sgn + "yh", "-2 mm"]})
        d.do("feature.cone", {"name": "Sink" + n, "radius": "csR + 1 mm", "height": "csR + 1 mm", "axis": [0, 0, -1],
                              "position": ["length / holes / 2", sgn + "yh", "thick + 1 mm"]})
        d.do("feature.boolean", {"op": "union", "target": "Hole" + n, "tool": "Sink" + n, "name": "Screw" + n})
        d.do("feature.pattern", {"name": "Screws" + n, "source": "Screw" + n, "count": "holes",
                                 "step": ["length / holes", "0 mm", "0 mm"]})
        d.do("feature.boolean", {"op": "subtract", "target": n + "3", "tool": "Screws" + n, "name": n + "4"})
    # The outline: the leaves' rounded corners and ends, and the bed, which the leaves stand on and
    # the knuckles on a 0.3 mm flat. Everything is made a little larger and trimmed to it.
    X0, Y0, Rr = "length / 2", "leafW", "cr"
    def p(x, y):
        return ["length / 2 + (%s)" % x, y]
    d.do("sketch.create", {"name": "OutlineSketch", "plane": "xy"})
    d.do("sketch.path", {"sketch": "OutlineSketch", "start": p(X0, "-%s + %s" % (Y0, Rr)), "segments": [
        {"line": p(X0, "%s - %s" % (Y0, Rr))},
        {"arc": p("%s - %s" % (X0, Rr), Y0), "center": p("%s - %s" % (X0, Rr), "%s - %s" % (Y0, Rr))},
        {"line": p("-%s + %s" % (X0, Rr), Y0)},
        {"arc": p("-" + X0, "%s - %s" % (Y0, Rr)), "center": p("-%s + %s" % (X0, Rr), "%s - %s" % (Y0, Rr))},
        {"line": p("-" + X0, "-%s + %s" % (Y0, Rr))},
        {"arc": p("-%s + %s" % (X0, Rr), "-" + Y0), "center": p("-%s + %s" % (X0, Rr), "-%s + %s" % (Y0, Rr))},
        {"line": p("%s - %s" % (X0, Rr), "-" + Y0)},
        {"arc": "start", "center": p("%s - %s" % (X0, Rr), "-%s + %s" % (Y0, Rr))}]})
    d.do("feature.extrude", {"sketch": "OutlineSketch", "distance": "knuckleD + 2 mm", "name": "Outline"})
    d.do("feature.boolean", {"op": "intersect", "target": "A4", "tool": "Outline", "keepTool": True, "name": "Leaf A"})
    d.do("feature.boolean", {"op": "intersect", "target": "B4", "tool": "Outline", "name": "Leaf B"})
    d.do("body.appearance", {"body": "Leaf A", "color": "#C2694B", "roughness": 0.6})
    d.do("body.appearance", {"body": "Leaf B", "color": "#8FA98A", "roughness": 0.6})
    d.do("assert.add", {"name": "two leaves", "measure": "count", "of": {"kind": "body"}, "eq": "2"})
    d.do("assert.add", {"name": "leaves apart", "measure": "interference", "of": ["Leaf A", "Leaf B"]})

    pub = [
        ("length", dict(label="Length", description="Length of the hinge along its axis", group="Size", order=1,
                        min="40 mm", max="200 mm", step="1 mm", unit="mm")),
        ("leafW", dict(label="Leaf width", description="Width of each leaf, from the axis to its edge", group="Size", order=2,
                       min="knuckleD / 2 + clearance + 2 * holeD + 4 mm", max="80 mm", step="0.5 mm", unit="mm")),
        ("thick", dict(label="Leaf thickness", description="Thickness of the leaves; at most the axis height, so the hinge folds flat",
                       group="Size", order=3, min="1.5 mm", max="knuckleD / 2 - 0.5 mm", step="0.1 mm", unit="mm")),
        ("knuckleD", dict(label="Knuckle diameter", description="Outside diameter of the knuckles", group="Knuckles", order=1,
                          min="6 mm", max="16 mm", step="0.5 mm", unit="mm")),
        ("knuckles", dict(label="Knuckles", description="Number of knuckles; leaf A has the first, the third and so on",
                          group="Knuckles", order=2, kind="integer", min="2",
                          max="floor((length + clearance) / (pinD + clearance + 3 mm))")),
        ("pinD", dict(label="Pin diameter", description="Base diameter of the 45 degree conical pins between the knuckles",
                      group="Knuckles", order=3, min="2 mm", max="min(knuckleD - 3 mm, 8 mm)", step="0.1 mm", unit="mm")),
        ("clearance", dict(label="Clearance", description="Gap between the moving parts (printer tuning): 0.3 mm suits most printers",
                           group="Knuckles", order=4, min="0.15 mm", max="0.8 mm", step="0.05 mm", unit="mm")),
        ("holes", dict(label="Screw holes", description="Countersunk screw holes in each leaf", group="Screws", order=1,
                       kind="integer", min="1", max="6")),
        ("holeD", dict(label="Screw diameter", description="Hole diameter; the countersink is 90 degrees", group="Screws", order=2,
                       min="2 mm", max="5 mm", step="0.1 mm", unit="mm")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        d.do("variable.publish", p)
    d.do("document.info", {
        "title": "Print-in-place hinge",
        "description": "A hinge that prints in one piece and turns straight off the bed: set its length, leaf width and "
                       "thickness, the knuckles and their conical pins, the clearance between the moving parts, and "
                       "countersunk screw holes. The pins and their sockets are 45 degree cones, so it prints flat "
                       "without supports. Export both leaves together with File > Export... (STL or 3MF) and print them "
                       "as they lie.",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/print-in-place-hinge",
        "tags": ["hinge", "print in place", "mechanism", "3D printing"]})
    d.do("jig.export", {"path": "dist/print-in-place-hinge.3dcraftjig"})
    return d.steps


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
