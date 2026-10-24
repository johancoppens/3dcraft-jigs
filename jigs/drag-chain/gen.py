#!/usr/bin/env python3
"""Writes build.json for the cable drag chain Jig (python3 gen.py > build.json).

A cable drag chain (energy chain) for a 3D printer or a CNC machine, to print.
Each link has two side walls that step in half way: the outer half of one link's
wall overlaps the inner half of the next one's, and a snap pin on the inner half
(chamfered, to click in) turns in a hole of the outer half. A bottom bridge joins
the walls; the top bridge is a separate part that clips on, so cables can be
laid in (an opening bridge).

The chain is laid out as it runs on a machine: a lower run, a bend of
`nb` links round the bend radius (each link a turn of the one before it about the
bend's centre: a circular pattern) and an upper run back (a linear pattern of an
upside-down link); or straight.

Link axes: x along the chain (the link's first hinge at x = 0, its second at
x = pitch), y across (the walls from y = 0 and their mirror image), z up (the
hinge axis at z = 0).
"""
import json

INPUTS = [
    ("innerW", "15 mm"),
    ("innerH", "10 mm"),
    ("pitch", "22 mm"),
    ("length", "500 mm"),
    ("radius", "45 mm"),
    ("layout", "1"),         # 1 bent (U), 2 straight
]
DERIVED = [
    ("ts", "clamp(0.12 * innerH + 1 mm, 1.6 mm, 3 mm)"),   # wall thickness
    ("tb", "ts"),                                          # bridge thickness
    ("g", "0.3 mm"),                                       # gap between the walls of two links
    ("cl", "0.15 mm"),                                     # radial clearance of the pin in its hole
    ("h", "innerH + 2 * tb"),                              # outer height of a link
    ("W", "innerW + 2 * (2 * ts + g)"),                    # outer width of a link
    ("c", "0.12 * pitch"),                                 # half the bridge's length along the chain
    ("pr", "0.22 * h"),                                    # pin radius
    ("pl", "ts + g - 0.4 mm"),                             # pin length
    ("pc", "min(0.3 * pr, 0.4 * pl)"),                     # pin tip chamfer (snap-in lead)
    ("rf", "0.45 * tb"),                                   # top bridge round-over
    ("bent", "layout == 1"),
    ("nb", "max(2, round(pi * radius / pitch))"),          # links in the bend (a half turn)
    ("th", "180 deg / nb"),                                # turn from link to link in the bend
    ("Rb", "pitch / (2 * sin(th / 2))"),                   # radius of the hinges in the bend
    ("nL", "max(1, round(length / pitch))"),               # links in all
    ("n1", "if(bent, ceil((nL - nb) / 2), nL)"),           # lower run
    ("n2", "nL - nb - n1"),                                # upper run (bent)
    ("x0", "n1 * pitch"),                                  # where the bend starts
    # Closed-form volumes, to prove that no two links touch or pass into each other.
    ("dArea", "(pitch / 2 + c) * h + pi * h * h / 8"),    # one half wall: a rectangle and a half disc
    ("vSide", "ts * (dArea - pi * (pr + cl) ^ 2) + ts * dArea + 2 * c * g * h + pi * pr * pr * pl - pi * pc * pc * (pr - pc / 3)"),
    ("vLink", "2 * vSide + 2 * c * innerW * tb"),
    ("vTop", "2 * c * innerW * tb - 2 * (1 - pi / 4) * rf * rf * innerW"),
]


def block(name, x0, x1, y0, y1, z0, z1):
    return ["feature.block", {"name": name,
                              "size": ["(%s) - (%s)" % (x1, x0), "(%s) - (%s)" % (y1, y0), "(%s) - (%s)" % (z1, z0)],
                              "position": [x0, y0, z0]}]


def main():
    s = []
    for n, e in INPUTS + DERIVED:
        s.append(["variable.set", {"name": n, "expr": e}])

    # Outer half wall (y from 0 to ts): from the bridge to a round end about the second hinge.
    # Sketch on zx: u = z, v = x, normal +y.
    s.append(["sketch.create", {"name": "OuterSketch", "plane": "zx"}])
    s.append(["sketch.path", {"sketch": "OuterSketch", "start": ["-h / 2", "pitch / 2 - c"], "segments": [
        {"line": ["-h / 2", "pitch"]},
        {"arc": ["h / 2", "pitch"], "center": ["0 mm", "pitch"], "clockwise": True},
        {"line": ["h / 2", "pitch / 2 - c"]},
        {"line": "start"}]}])
    s.append(["feature.extrude", {"sketch": "OuterSketch", "distance": "ts", "name": "Outer"}])
    # Inner half wall (y from ts + g), round about the first hinge.
    s.append(["sketch.create", {"name": "InnerSketch", "plane": "zx", "offset": "ts + g"}])
    s.append(["sketch.path", {"sketch": "InnerSketch", "start": ["-h / 2", "pitch / 2 + c"], "segments": [
        {"line": ["-h / 2", "0 mm"]},
        {"arc": ["h / 2", "0 mm"], "center": ["0 mm", "0 mm"], "clockwise": False},
        {"line": ["h / 2", "pitch / 2 + c"]},
        {"line": "start"}]}])
    s.append(["feature.extrude", {"sketch": "InnerSketch", "distance": "ts", "name": "Inner"}])
    s.append(block("Web", "pitch / 2 - c", "pitch / 2 + c", "ts", "ts + g", "-h / 2", "h / 2"))
    # Snap pin on the inner half wall, towards the outside, into the previous link's hole.
    s.append(["feature.cylinder", {"name": "PinBody", "radius": "pr", "height": "pl",
                                   "position": ["0 mm", "ts + g", "0 mm"], "axis": [0, -1, 0]}])
    s.append(["feature.chamfer", {"name": "Pin", "edges": [["F_PIN:face(0)", "F_PIN:face(2)"]], "distance": "pc"}])
    s.append(["feature.boolean", {"op": "union", "target": "Outer", "tool": "Web", "name": "W1"}])
    s.append(["feature.boolean", {"op": "union", "target": "W1", "tool": "Inner", "name": "W2"}])
    s.append(["feature.boolean", {"op": "union", "target": "W2", "tool": "Pin", "name": "W3"}])
    s.append(["feature.cylinder", {"name": "Hole", "radius": "pr + cl", "height": "ts + 2 mm",
                                   "position": ["pitch", "-1 mm", "0 mm"], "axis": [0, 1, 0]}])
    s.append(["feature.boolean", {"op": "subtract", "target": "W3", "tool": "Hole", "name": "WallL"}])
    s.append(["feature.mirror", {"source": "WallL", "normal": [0, 1, 0], "point": ["0 mm", "W / 2", "0 mm"],
                                 "keep": True, "name": "WallR"}])
    s.append(block("BottomBridge", "pitch / 2 - c", "pitch / 2 + c", "2 * ts + g", "W - 2 * ts - g", "-h / 2", "-h / 2 + tb"))
    s.append(["feature.boolean", {"op": "union", "target": "WallL", "tool": "BottomBridge", "name": "L1"}])
    s.append(["feature.boolean", {"op": "union", "target": "L1", "tool": "WallR", "name": "Link"}])
    # The opening bridge on top, with its upper edges rounded.
    s.append(block("TopBlank", "pitch / 2 - c", "pitch / 2 + c", "2 * ts + g", "W - 2 * ts - g", "h / 2 - tb", "h / 2"))
    s.append(["feature.fillet", {"name": "Top", "edges": [["F_TOP:face(1)", "F_TOP:face(4)"], ["F_TOP:face(1)", "F_TOP:face(5)"]],
                                 "radius": "rf"}])

    # The bend's and the upper run's first links: copies of the link, placed before the
    # lower run's pattern takes the link itself.
    for part, nm in (("Link", "Links"), ("Top", "Bridges")):
        s.append(["feature.transform", {"source": part, "angle": "th / 2", "axis": [0, -1, 0], "pivot": ["0 mm", "0 mm", "0 mm"],
                                        "translate": ["x0", "0 mm", "0 mm"], "keep": True, "name": part + "Bend0"}])
        s.append(["feature.transform", {"source": part, "angle": "180 deg", "axis": [0, -1, 0], "pivot": ["0 mm", "0 mm", "0 mm"],
                                        "translate": ["x0", "0 mm", "2 * Rb"], "keep": True, "name": part + "Up0"}])
        s.append(["feature.pattern", {"name": nm + "Low", "source": part, "count": "n1", "step": ["pitch", "0 mm", "0 mm"]}])
        s.append(["feature.pattern", {"name": nm + "Bend", "source": part + "Bend0", "count": "nb", "angle": "th",
                                      "axis": [0, -1, 0], "point": ["x0", "0 mm", "Rb"]}])
        s.append(["feature.pattern", {"name": nm + "Up", "source": part + "Up0", "count": "n2", "step": ["-pitch", "0 mm", "0 mm"]}])
        for f in (part + "Bend0", part + "Up0", nm + "Bend", nm + "Up"):
            s.append(["feature.when", {"feature": f, "expr": "bent"}])

    for b in ("LinksLow", "LinksBend", "LinksUp"):
        s.append(["body.appearance", {"body": b, "color": "#2E7D7A", "roughness": 0.55}])
    for b in ("BridgesLow", "BridgesBend", "BridgesUp"):
        s.append(["body.appearance", {"body": b, "color": "#D4A24C", "roughness": 0.5}])

    s.append(["assert.add", {"name": "links apart", "measure": "volume",
                             "of": {"kind": "body", "where": {"name": "Links*"}}, "eq": "nL * vLink", "tol": "1e-6 * nL * vLink"}])
    s.append(["assert.add", {"name": "bridges apart", "measure": "volume",
                             "of": {"kind": "body", "where": {"name": "Bridges*"}}, "eq": "nL * vTop", "tol": "1e-6 * nL * vTop"}])
    s.append(["assert.add", {"name": "chain clear of itself", "measure": "interference", "of": {"kind": "body"}}])

    pub = [
        ("innerW", dict(label="Inner width", description="Width of the cable space inside a link", group="Link", order=1,
                        min="6 mm", max="60 mm", step="0.5 mm", unit="mm")),
        ("innerH", dict(label="Inner height", description="Height of the cable space inside a link", group="Link", order=2,
                        min="5 mm", max="40 mm", step="0.5 mm", unit="mm")),
        ("pitch", dict(label="Link pitch", description="Distance from hinge to hinge; at least 1.4 times the link's outer height, so the links can turn",
                       group="Link", order=3, min="1.4 * h", max="3 * h", step="0.5 mm", unit="mm")),
        ("length", dict(label="Chain length", description="Length along the chain; the number of links is rounded from it",
                        group="Chain", order=1, min="(nb + 2) * pitch", max="1200 mm", step="1 mm", unit="mm")),
        ("radius", dict(label="Bend radius", description="Radius of the bend, at the hinges; the links in the bend are rounded to fill a half turn",
                        group="Chain", order=2, min="pitch", max="min(8 * pitch, (1200 mm - 2.5 * pitch) / pi)", step="1 mm", unit="mm")),
        ("layout", dict(label="Layout", description="As it runs on a machine (lower run, bend, upper run) or laid out straight",
                        group="Chain", order=3, kind="choice", choices=["bent (U)", "straight"])),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        s.append(["variable.publish", p])

    s.append(["document.info", {
        "title": "Cable drag chain",
        "description": "A cable drag chain (energy chain) for a 3D printer or CNC machine, to print: links with snap-in "
                       "hinge pins and clip-on top bridges, so cables can be laid in. Set the cable space (inner width and "
                       "height), the link pitch, the chain length and the bend radius; the chain is shown as it runs, bent "
                       "round its radius, or straight. Export it with File > Export... (STL or 3MF; the links and the bridges "
                       "are separate bodies).",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/drag-chain",
        "tags": ["drag chain", "cable chain", "3D printer", "CNC", "3D printing"]}])
    s.append(["jig.export", {"path": "dist/drag-chain.3dcraftjig"}])
    return resolve(s)


FEATURE_CMDS = {"feature.block", "feature.cylinder", "feature.fillet", "feature.chamfer", "feature.pattern",
                "feature.boolean", "feature.mirror", "feature.transform", "feature.extrude", "sketch.create"}


def resolve(steps):
    ids, n = {}, 0
    for cmd, p in steps:
        if cmd in FEATURE_CMDS:
            n += 1
            ids[p["name"]] = "F%d" % n
    text = json.dumps(steps).replace("F_PIN:", ids["PinBody"] + ":").replace("F_TOP:", ids["TopBlank"] + ":")
    return json.loads(text)


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
