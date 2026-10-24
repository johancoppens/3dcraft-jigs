#!/usr/bin/env python3
"""Writes build.json for the screw jar Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the profiles are readable. Run it again only to change the model.

Both threads are a trapezoid with 45 degree flanks swept along a helix
(datum.helix + feature.sweep, joined to the part). The lid's thread is the
jar's groove less the clearance, so the gap is the clearance square to every
flank and at both crests.
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
    ("innerD", "60 mm"),      # diameter of the opening
    ("height", "70 mm"),      # the jar, without its lid
    ("wall", "2 mm"),
    ("pitch", "4 mm"),
    ("turns", "2"),
    ("clearance", "0.3 mm"),
    ("ribs", "1"),
]
DERIVED = [
    ("Ri", "innerD / 2"),
    ("Rn", "Ri + wall"),                         # outside of the neck (the thread's root)
    ("td", "0.28 * pitch"),                      # thread depth
    ("b", "0.7 * pitch"),                        # thread width at its root
    ("bl", "pitch - b + 2 * td - 2 * clearance * (sqrt(2) - 1)"),   # the lid's thread at its root
    ("lw", "wall"),                              # the lid's skirt
    ("Rl", "Rn + td + clearance"),               # inside of the lid's skirt
    ("Rb", "Rl + lw"),                           # outside of jar and lid
    ("Rbi", "Rb - wall"),                        # inside of the jar's body
    ("Hn", "turns * pitch + b + 2 mm"),          # the neck, above the ledge the lid stops at
    ("Hs", "height - Hn"),                       # the ledge
    ("zi", "Hs - wall"),                         # inside, where the neck widens into the body (45 degrees)
    ("zb", "zi - (Rbi - Ri)"),
    ("floorZ", "wall + 0.5 mm"),
    ("zj", "Hs + 1 mm"),                         # bottom of the jar's thread
    ("zl", "zj + b / 2 + pitch / 2"),            # middle of the lid's thread's first turn
    ("lt", "wall + 0.5 mm"),                     # the lid's top
    ("lidZ", "height + clearance"),              # underside of the lid's top, screwed on
    ("ch", "0.6 mm"),
    ("e", "0.15 mm"),                            # how far a thread reaches into its part
    ("nRibs", "round(2 * pi * Rb / 3 mm)"),
]


def zx_polygon(d, name, pts):
    """A closed polygon in the zx plane given as (z, r) pairs (sketch x is world Z, y is world X)."""
    d.do("sketch.create", {"name": name, "plane": "zx"})
    d.do("sketch.polyline", {"sketch": name, "closed": True, "points": [[z, r] for z, r in pts]})


def main():
    d = Doc()
    for name, expr in INPUTS + DERIVED:
        d.var(name, expr)

    # The jar: a revolved profile, the neck narrower than the body so the lid sits flush with it.
    zx_polygon(d, "JarProfile", [
        ("0 mm", "0 mm"), ("0 mm", "Rb - ch"), ("ch", "Rb"), ("Hs", "Rb"), ("Hs", "Rn"),
        ("height - ch", "Rn"), ("height", "Rn - ch"), ("height", "Ri"),
        ("zi", "Ri"), ("zb", "Rbi"), ("floorZ", "Rbi"), ("floorZ", "0 mm")])
    d.do("feature.revolve", {"sketch": "JarProfile", "axis": "x", "name": "JarBody"})
    d.do("datum.helix", {"name": "JarHelix", "axis": "z", "start": ["Rn", "0 mm", "zj"], "pitch": "pitch", "turns": "turns"})
    zx_polygon(d, "JarThreadProfile", [
        ("zj - e", "Rn - e"), ("zj + td", "Rn + td"), ("zj + b - td", "Rn + td"), ("zj + b + e", "Rn - e")])
    d.do("feature.sweep", {"sketch": "JarThreadProfile", "path": "JarHelix", "join": "JarBody", "name": "Jar"})
    d.do("body.appearance", {"body": "Jar", "color": "#E8DFCC", "roughness": 0.5})

    # The lid, built screwed on, then laid upside down beside the jar to print.
    zx_polygon(d, "LidProfile", [
        ("Hs + 0.5 mm", "Rl"), ("Hs + 0.5 mm", "Rb - ch"), ("Hs + 0.5 mm + ch", "Rb"),
        ("lidZ + lt - 1 mm", "Rb"), ("lidZ + lt", "Rb - 1 mm"), ("lidZ + lt", "0 mm"),
        ("lidZ", "0 mm"), ("lidZ", "Rl")])
    d.do("feature.revolve", {"sketch": "LidProfile", "axis": "x", "name": "LidBody"})
    d.do("datum.helix", {"name": "LidHelix", "axis": "z", "start": ["Rl", "0 mm", "zl - bl / 2"], "pitch": "pitch",
                         "turns": "turns - 1"})
    zx_polygon(d, "LidThreadProfile", [
        ("zl - bl / 2 - e", "Rl + e"), ("zl + bl / 2 + e", "Rl + e"),
        ("zl + bl / 2 - td", "Rl - td"), ("zl - bl / 2 + td", "Rl - td")])
    d.do("feature.sweep", {"sketch": "LidThreadProfile", "path": "LidHelix", "join": "LidBody", "name": "LidThreaded"})
    # Grip ribs: grooves round the lid's skirt.
    d.do("feature.cylinder", {"name": "Rib", "radius": "0.7 mm", "height": "lidZ + lt - 1.5 mm - Hs",
                              "position": ["Rb", "0 mm", "Hs"]})
    d.do("feature.pattern", {"name": "Ribs", "source": "Rib", "count": "nRibs", "angle": "360 deg / nRibs", "axis": [0, 0, 1]})
    d.do("feature.boolean", {"op": "subtract", "target": "LidThreaded", "tool": "Ribs", "name": "LidGrip"})
    for f in ("Rib", "Ribs"):
        d.do("feature.when", {"feature": f, "expr": "ribs"})
    d.do("feature.transform", {"source": "LidGrip", "name": "Lid", "angle": "180 deg", "axis": [1, 0, 0],
                               "pivot": ["0 mm", "0 mm", "(lidZ + lt) / 2"], "translate": ["2 * Rb + 10 mm", "0 mm", "0 mm"]})
    d.do("body.appearance", {"body": "Lid", "color": "#8A5A7A", "roughness": 0.5})
    d.do("assert.add", {"name": "jar and lid", "measure": "count", "of": {"kind": "body"}, "eq": "2"})

    pub = [
        ("innerD", dict(label="Opening", description="Inside diameter of the neck: what goes in", group="Jar", order=1,
                        min="20 mm", max="120 mm", step="1 mm", unit="mm")),
        ("height", dict(label="Height", description="Height of the jar without its lid", group="Jar", order=2,
                        min="(turns + 1) * pitch + 3 * wall + clearance + 8 mm", max="200 mm", step="1 mm", unit="mm")),
        ("wall", dict(label="Wall", description="Wall thickness of the jar and the lid", group="Jar", order=3,
                      min="1.2 mm", max="4 mm", step="0.1 mm", unit="mm")),
        ("pitch", dict(label="Thread pitch", description="How far the lid moves per turn", group="Thread", order=1,
                       min="2.5 mm", max="8 mm", step="0.5 mm", unit="mm")),
        ("turns", dict(label="Turns", description="Turns of the jar's thread; the lid's has one turn less", group="Thread", order=2,
                       min="1.5", max="3", step="0.25")),
        ("clearance", dict(label="Clearance", description="Gap between the threads (printer tuning): 0.3 mm suits most printers",
                           group="Thread", order=3, min="0.15 mm", max="0.6 mm", step="0.05 mm", unit="mm")),
        ("ribs", dict(label="Grip ribs", description="Grooves round the lid for grip", group="Lid", order=1, kind="boolean")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        d.do("variable.publish", p)
    d.do("document.info", {
        "title": "Screw jar",
        "description": "A jar with a screw-on lid and a real thread: set the opening, the height and the wall, the thread's "
                       "pitch, turns and clearance; the lid follows the jar. Optional grip ribs round the lid. The lid "
                       "lies upside down beside the jar, both print without supports. Export it with File > Export... "
                       "(STL or 3MF).",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/screw-jar",
        "tags": ["jar", "thread", "container", "lid", "3D printing"]})
    d.do("jig.export", {"path": "dist/screw-jar.3dcraftjig"})
    return d.steps


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
