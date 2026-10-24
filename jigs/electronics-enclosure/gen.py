#!/usr/bin/env python3
"""Writes build.json for the electronics enclosure Jig (python3 gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the tables and the construction are readable. Run it again only to
change the model.
"""
import json

# Screws for the PCB standoffs and the lid: pilot (the hole a screw cuts its
# own thread in, or the hole for a heat-set insert), clearance hole, head and
# boss (standoff) diameter, in mm.
SCREWS = [
    ["M2", 1.6, 2.4, 4.0, 4.5],
    ["M2.5", 2.1, 2.9, 5.0, 5.5],
    ["M3", 2.5, 3.4, 6.0, 6.5],
    ["M3 heat-set insert", 4.0, 3.4, 6.0, 7.5],
]
# Port cut-outs: width and height of the opening, its corner radius, its
# centre's height above the top of the PCB, and whether it is round (then
# the width is the diameter). Openings carry about 0.3 mm play round the part.
PORTS = [
    ["none", 1, 1, 0.2, 0, 0],
    ["USB-C", 9.6, 3.8, 1.5, 1.65, 0],
    ["micro-USB", 8.2, 3.4, 1.0, 1.5, 0],
    ["DC jack 5.5 mm", 8.0, 8.0, 0.2, 6.5, 1],
    ["Toggle switch (6 mm)", 6.4, 6.4, 0.2, 7, 1],
    ["Slide switch", 9.0, 4.5, 0.8, 2.0, 0],
]
SIDES = ["Front", "Back", "Left", "Right"]


class Doc:
    """Collects the commands and counts the ids 3DCraft gives sketches and features."""

    def __init__(self):
        self.steps = []
        self.n = 0

    def var(self, name, expr):
        self.steps.append(["variable.set", {"name": name, "expr": expr}])

    def add(self, cmd, params, ids=1):
        self.steps.append([cmd, params])
        self.n += ids
        return "F%d" % self.n

    def do(self, cmd, params):
        self.steps.append([cmd, params])

    def when(self, feature, expr):
        self.do("feature.when", {"feature": feature, "expr": expr})

    def rrect(self, name, z, hx, hy, r, holes=()):
        """A sketch parallel to xy at z with a rounded rectangle about the
        origin (half sizes hx, hy, corner radius r), and more inside it as
        holes. Its curves are e3, e6, e8, e11, e13, e16, e18, e20."""
        fid = self.add("sketch.create", {"name": name, "plane": "xy", "offset": z})
        for (a, b, c) in ((hx, hy, r),) + tuple(holes):
            self.do("sketch.path", path(name, a, b, c))
        return fid


def path(sketch, hx, hy, r):
    X, Y, R = "(%s)" % hx, "(%s)" % hy, "(%s)" % r

    def p(x, y):
        return [x, y]
    seg = [
        {"line": p(X, "%s - %s" % (Y, R))},
        {"arc": p("%s - %s" % (X, R), Y), "center": p("%s - %s" % (X, R), "%s - %s" % (Y, R))},
        {"line": p("-%s + %s" % (X, R), Y)},
        {"arc": p("-" + X, "%s - %s" % (Y, R)), "center": p("-%s + %s" % (X, R), "%s - %s" % (Y, R))},
        {"line": p("-" + X, "-%s + %s" % (Y, R))},
        {"arc": p("-%s + %s" % (X, R), "-" + Y), "center": p("-%s + %s" % (X, R), "-%s + %s" % (Y, R))},
        {"line": p("%s - %s" % (X, R), "-" + Y)},
        {"arc": "start", "center": p("%s - %s" % (X, R), "-%s + %s" % (Y, R))},
    ]
    return {"sketch": sketch, "start": p(X, "-%s + %s" % (Y, R)), "segments": seg}


LOOP = "e3,e6,e8,e11,e13,e16,e18,e20"

INPUTS = [
    ("pcbW", "70 mm"), ("pcbD", "50 mm"), ("pcbT", "1.6 mm"),
    ("holeX", "3.5 mm"), ("holeY", "3.5 mm"), ("screw", "3"), ("standoffH", "5 mm"),
    ("wall", "2 mm"), ("clearance", "1 mm"), ("room", "20 mm"),
    ("lid", "1"),
    ("p1", "2"), ("p1Side", "1"), ("p1Off", "0 mm"),
    ("p2", "4"), ("p2Side", "2"), ("p2Off", "8 mm"),
]
DERIVED = [
    ("screwLid", "lid == 1"),
    ("snapLid", "lid == 2"),
    ("boss", "screws[screw].boss"),
    ("postR", "boss / 2 + 0.5 mm"),         # the lid's screw posts in the corners
    ("postRoom", "if(screwLid, 2 * postR - 0.5 mm, 0 mm)"),  # room beside the PCB for them
    ("Wi", "pcbW + 2 * clearance + 2 * postRoom"),   # inside
    ("Di", "pcbD + 2 * clearance"),
    ("W", "Wi + 2 * wall"),                 # outside
    ("D", "Di + 2 * wall"),
    ("Ro", "wall + 2 mm"),                  # outer corner radius; inside 2 mm
    ("pcbZ", "wall + standoffH"),           # underside of the PCB
    ("topZ", "pcbZ + pcbT"),                # top of the PCB
    ("Hb", "topZ + room"),                  # height of the box
    ("lidT", "wall"),
    ("fit", "0.2 mm"),                      # play of the snap-fit lid's skirt
    ("skirtH", "4 mm"),
    ("skirtT", "1.6 mm"),
    ("q", "wall + postR - 1 mm"),           # a post's centre from the outside, in x and y
    ("keep", "2 * postR"),                  # ports stay this far from the inside corners
    ("ch", "0.6 mm"),                       # chamfers round the bottom and the lid
    ("gap", "10 mm"),                       # between box and lid as laid out to print
]


def port(d, k, cut_from):
    """Port k cut from the body of feature cut_from; returns the last feature."""
    t = "p%d" % k
    d.var(t + "W", "ports[%s].w" % t)
    d.var(t + "H", "ports[%s].h" % t)
    d.var(t + "R", "ports[%s].r" % t)
    d.var(t + "Round", "ports[%s].round" % t)
    d.var(t + "Z", "topZ + ports[%s].z" % t)
    d.var(t + "On", "%s > 1" % t)
    # Where its centre is: on the wall's mid-plane, offset to the right as seen from outside.
    side, off = t + "Side", t + "Off"
    d.var(t + "X", "choose(%s, %s, -%s, -(W - wall) / 2, (W - wall) / 2)" % (side, off, off))
    d.var(t + "Y", "choose(%s, -(D - wall) / 2, (D - wall) / 2, -%s, %s)" % (side, off, off))
    d.var(t + "A", "if(%s > 2, 90 deg, 0 deg)" % side)
    L = "wall + 1 mm"
    blk = d.add("feature.block", {"name": "Port%dBlock" % k, "size": [t + "W", L, t + "H"],
                                  "position": ["-%sW / 2" % t, "-(%s) / 2" % L, "-%sH / 2" % t]})
    rnd = d.add("feature.fillet", {"name": "Port%dSlot" % k, "radius": t + "R",
                                   "edges": [["%s:face(0)" % blk, "%s:face(4)" % blk], ["%s:face(0)" % blk, "%s:face(5)" % blk],
                                             ["%s:face(1)" % blk, "%s:face(4)" % blk], ["%s:face(1)" % blk, "%s:face(5)" % blk]]})
    cyl = d.add("feature.cylinder", {"name": "Port%dHole" % k, "radius": t + "W / 2", "height": L,
                                     "axis": [0, 1, 0], "position": ["0 mm", "-(%s) / 2" % L, "0 mm"]})
    for f in ("Port%dBlock" % k, "Port%dSlot" % k):
        d.when(f, "%sOn && !%sRound" % (t, t))
    d.when("Port%dHole" % k, "%sOn && %sRound" % (t, t))
    last = cut_from
    for src, nm in (("Port%dSlot" % k, "Port%dSlotTool" % k), ("Port%dHole" % k, "Port%dHoleTool" % k)):
        d.add("feature.transform", {"source": src, "name": nm, "angle": t + "A", "axis": [0, 0, 1],
                                    "translate": [t + "X", t + "Y", t + "Z"]})
        d.when(nm, "%sOn && %s%sRound" % (t, "!" if "Slot" in nm else "", t))
        last = d.add("feature.boolean", {"op": "subtract", "target": last, "tool": nm,
                                         "name": "%sCut%d%s" % ("Box" if k == 2 and "Hole" in nm else "Port", k, "S" if "Slot" in nm else "H")})
    return last


def main():
    d = Doc()
    d.do("table.set", {"name": "screws", "columns": ["screw", {"name": "pilot", "unit": "mm"},
                                                     {"name": "clear", "unit": "mm"}, {"name": "head", "unit": "mm"},
                                                     {"name": "boss", "unit": "mm"}], "rows": SCREWS})
    d.do("table.set", {"name": "ports", "columns": ["port", {"name": "w", "unit": "mm"}, {"name": "h", "unit": "mm"},
                                                   {"name": "r", "unit": "mm"}, {"name": "z", "unit": "mm"}, "round"],
                       "rows": PORTS})
    for name, expr in INPUTS + DERIVED:
        d.var(name, expr)

    # The box: a rounded block made hollow, open at the top, its bottom edge chamfered.
    sk = d.rrect("BoxSketch", "0 mm", "W / 2", "D / 2", "Ro")
    ext = d.add("feature.extrude", {"sketch": "BoxSketch", "distance": "Hb", "name": "BoxBlock"})
    sh = d.add("feature.shell", {"source": "BoxBlock", "thickness": "wall", "open": ["%s:endCap(%s)" % (ext, LOOP)], "name": "BoxShell"})
    d.add("feature.chamfer", {"name": "BoxChamfer", "distance": "ch", "chain": True,
                              "edges": [["%s:copy(0)/%s:startCap(%s)" % (sh, ext, LOOP), "%s:copy(0)/%s:side(e3)" % (sh, ext)]]})

    # Standoffs under the PCB's four holes, with a pilot hole each.
    d.add("feature.cylinder", {"name": "Standoff", "radius": "boss / 2", "height": "standoffH + 0.5 mm",
                               "position": ["-pcbW / 2 + holeX", "-pcbD / 2 + holeY", "wall - 0.5 mm"]})
    d.add("feature.pattern", {"source": "Standoff", "count": "2", "step": ["pcbW - 2 * holeX", "0 mm", "0 mm"], "name": "Standoffs2"})
    d.add("feature.pattern", {"source": "Standoffs2", "count": "2", "step": ["0 mm", "pcbD - 2 * holeY", "0 mm"], "name": "Standoffs"})
    d.add("feature.boolean", {"op": "union", "target": "BoxChamfer", "tool": "Standoffs", "name": "WithStandoffs"})
    d.add("feature.cylinder", {"name": "Pilot", "radius": "screws[screw].pilot / 2", "height": "standoffH + 1 mm",
                               "position": ["-pcbW / 2 + holeX", "-pcbD / 2 + holeY", "wall + 0.5 mm"]})
    d.add("feature.pattern", {"source": "Pilot", "count": "2", "step": ["pcbW - 2 * holeX", "0 mm", "0 mm"], "name": "Pilots2"})
    d.add("feature.pattern", {"source": "Pilots2", "count": "2", "step": ["0 mm", "pcbD - 2 * holeY", "0 mm"], "name": "Pilots"})
    d.add("feature.boolean", {"op": "subtract", "target": "WithStandoffs", "tool": "Pilots", "name": "Drilled"})

    # Screw lid: a post in every corner, 0.2 mm under the rim, with a pilot hole.
    d.add("feature.cylinder", {"name": "Post", "radius": "postR", "height": "Hb - 0.2 mm - wall + 0.5 mm",
                               "position": ["-W / 2 + q", "-D / 2 + q", "wall - 0.5 mm"]})
    d.add("feature.pattern", {"source": "Post", "count": "2", "step": ["W - 2 * q", "0 mm", "0 mm"], "name": "Posts2"})
    d.add("feature.pattern", {"source": "Posts2", "count": "2", "step": ["0 mm", "D - 2 * q", "0 mm"], "name": "Posts"})
    d.add("feature.boolean", {"op": "union", "target": "Drilled", "tool": "Posts", "name": "WithPosts"})
    d.add("feature.cylinder", {"name": "PostHole", "radius": "screws[screw].pilot / 2", "height": "min(12 mm, room)",
                               "position": ["-W / 2 + q", "-D / 2 + q", "Hb - min(12 mm, room) + 1 mm"]})
    d.add("feature.pattern", {"source": "PostHole", "count": "2", "step": ["W - 2 * q", "0 mm", "0 mm"], "name": "PostHoles2"})
    d.add("feature.pattern", {"source": "PostHoles2", "count": "2", "step": ["0 mm", "D - 2 * q", "0 mm"], "name": "PostHoles"})
    d.add("feature.boolean", {"op": "subtract", "target": "WithPosts", "tool": "PostHoles", "name": "Posted"})
    for f in ("Post", "Posts2", "Posts", "PostHole", "PostHoles2", "PostHoles"):
        d.when(f, "screwLid")

    # Snap-fit lid: a groove along the inside of the front and back walls for the skirt's beads.
    d.add("feature.cylinder", {"name": "Groove", "radius": "0.75 mm", "height": "Wi * 0.6",
                               "axis": [1, 0, 0], "position": ["-Wi * 0.3", "-Di / 2", "Hb - skirtH / 2"]})
    d.add("feature.pattern", {"source": "Groove", "count": "2", "step": ["0 mm", "Di", "0 mm"], "name": "Grooves"})
    d.add("feature.boolean", {"op": "subtract", "target": "Posted", "tool": "Grooves", "name": "Grooved"})
    for f in ("Groove", "Grooves"):
        d.when(f, "snapLid")

    last = port(d, 1, "Grooved")
    last = port(d, 2, last)
    d.add("feature.transform", {"source": last, "name": "Box"})
    d.do("body.appearance", {"body": "Box", "color": "#5B7299", "roughness": 0.6})

    # The lid, built where it sits on the box, then laid upside down beside it to print.
    d.rrect("LidSketch", "Hb", "W / 2", "D / 2", "Ro")
    lid = d.add("feature.extrude", {"sketch": "LidSketch", "distance": "lidT", "name": "LidPlate"})
    d.add("feature.chamfer", {"name": "LidEdge", "distance": "ch", "chain": True,
                              "edges": [["%s:endCap(%s)" % (lid, LOOP), "%s:side(e3)" % lid]]})
    # Screw lid: counterbored holes over the posts.
    d.add("feature.cylinder", {"name": "LidHole", "radius": "screws[screw].clear / 2", "height": "lidT + 2 mm",
                               "position": ["-W / 2 + q", "-D / 2 + q", "Hb - 1 mm"]})
    d.add("feature.cylinder", {"name": "LidBore", "radius": "screws[screw].head / 2 + 0.3 mm", "height": "lidT / 2 + 1 mm",
                               "position": ["-W / 2 + q", "-D / 2 + q", "Hb + lidT / 2"]})
    d.add("feature.boolean", {"op": "union", "target": "LidHole", "tool": "LidBore", "name": "LidHoleTool"})
    d.add("feature.pattern", {"source": "LidHoleTool", "count": "2", "step": ["W - 2 * q", "0 mm", "0 mm"], "name": "LidHoles2"})
    d.add("feature.pattern", {"source": "LidHoles2", "count": "2", "step": ["0 mm", "D - 2 * q", "0 mm"], "name": "LidHoles"})
    d.add("feature.boolean", {"op": "subtract", "target": "LidEdge", "tool": "LidHoles", "name": "LidDrilled"})
    for f in ("LidHole", "LidBore", "LidHoleTool", "LidHoles2", "LidHoles"):
        d.when(f, "screwLid")
    # Snap lid: a skirt that fits inside the box with play, with a bead on its front and back.
    d.rrect("SkirtSketch", "Hb - skirtH", "Wi / 2 - fit", "Di / 2 - fit", "2 mm - fit",
            holes=(("Wi / 2 - fit - skirtT", "Di / 2 - fit - skirtT", "max(0.5 mm, 2 mm - fit - skirtT)"),))
    d.add("feature.extrude", {"sketch": "SkirtSketch", "distance": "skirtH + lidT / 2", "name": "Skirt"})
    d.add("feature.cylinder", {"name": "Bead", "radius": "0.6 mm", "height": "Wi * 0.5",
                               "axis": [1, 0, 0], "position": ["-Wi * 0.25", "-Di / 2 + fit", "Hb - skirtH / 2"]})
    d.add("feature.pattern", {"source": "Bead", "count": "2", "step": ["0 mm", "Di - 2 * fit", "0 mm"], "name": "Beads"})
    d.add("feature.boolean", {"op": "union", "target": "Skirt", "tool": "Beads", "name": "BeadedSkirt"})
    d.add("feature.boolean", {"op": "union", "target": "LidDrilled", "tool": "BeadedSkirt", "name": "LidSnap"})
    for f in ("Skirt", "Bead", "Beads", "BeadedSkirt"):
        d.when(f, "snapLid")
    d.add("feature.transform", {"source": "LidSnap", "name": "Lid", "angle": "180 deg", "axis": [1, 0, 0],
                                "pivot": ["0 mm", "0 mm", "(Hb + lidT) / 2"], "translate": ["W + gap", "0 mm", "0 mm"]})
    d.do("body.appearance", {"body": "Lid", "color": "#D4A24C", "roughness": 0.6})
    d.do("assert.add", {"name": "box and lid", "measure": "count", "of": {"kind": "body"}, "eq": "2"})

    pub = [
        ("pcbW", dict(label="PCB width", description="Size of the board along x", group="PCB", order=1,
                      min="30 mm", max="160 mm", step="0.5 mm", unit="mm")),
        ("pcbD", dict(label="PCB depth", description="Size of the board along y", group="PCB", order=2,
                      min="30 mm", max="120 mm", step="0.5 mm", unit="mm")),
        ("pcbT", dict(label="PCB thickness", description="Thickness of the board", group="PCB", order=3,
                      min="0.8 mm", max="2.4 mm", step="0.1 mm", unit="mm")),
        ("holeX", dict(label="Holes from side", description="Mounting holes' centres from the board's left and right edges",
                       group="PCB", order=4, min="3 mm", max="pcbW / 2 - 5 mm", step="0.1 mm", unit="mm")),
        ("holeY", dict(label="Holes from front", description="Mounting holes' centres from the board's front and back edges",
                       group="PCB", order=5, min="3 mm", max="pcbD / 2 - 5 mm", step="0.1 mm", unit="mm")),
        ("screw", dict(label="Screws", description="Screws for the board and the lid; the standoffs and posts get a pilot hole for them",
                       group="PCB", order=6, kind="choice", choicesFrom="screws")),
        ("standoffH", dict(label="Standoff height", description="Room under the board, from the floor",
                           group="PCB", order=7, min="3 mm", max="15 mm", step="0.5 mm", unit="mm")),
        ("room", dict(label="Room above PCB", description="Inside height above the board, for its parts",
                      group="Box", order=1, min="15 mm", max="60 mm", step="0.5 mm", unit="mm")),
        ("wall", dict(label="Wall", description="Thickness of the walls, floor and lid",
                      group="Box", order=2, min="1.6 mm", max="3 mm", step="0.1 mm", unit="mm")),
        ("clearance", dict(label="Clearance", description="Gap between the board and the walls",
                           group="Box", order=3, min="1 mm", max="5 mm", step="0.1 mm", unit="mm")),
        ("lid", dict(label="Lid", description="Screwed on four corner posts, or snapped in by a skirt with beads",
                     group="Box", order=4, kind="choice", choices=["Screws", "Snap fit"])),
    ]
    for k, order in ((1, 1), (2, 4)):
        t = "p%d" % k
        pub += [
            (t, dict(label="Port %d" % k, description="The cut-out for a connector or switch", group="Ports",
                     order=order, kind="choice", choicesFrom="ports")),
            (t + "Side", dict(label="Port %d side" % k, description="The wall it is in", group="Ports", order=order + 1,
                              kind="choice", choices=SIDES)),
            (t + "Off", dict(label="Port %d offset" % k,
                             description="From the middle of the wall, to the right as seen from outside",
                             group="Ports", order=order + 2,
                             min="-((if(%sSide <= 2, Wi, Di) - %sW) / 2 - keep)" % (t, t),
                             max="(if(%sSide <= 2, Wi, Di) - %sW) / 2 - keep" % (t, t),
                             step="0.5 mm", unit="mm")),
        ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        d.do("variable.publish", p)
    d.do("document.info", {
        "title": "Electronics enclosure",
        "description": "A box for a circuit board with a lid: set the board's size and its mounting holes (standoffs "
                       "for M2 to M3 screws or heat-set inserts), the room above it, the walls and two port cut-outs "
                       "(USB-C, micro-USB, DC jack, toggle or slide switch) on any side. The lid screws onto corner "
                       "posts or snaps in. Box and lid are laid out side by side to print, the lid upside down. "
                       "Export it with File > Export... (STL or 3MF).",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/electronics-enclosure",
        "tags": ["enclosure", "electronics", "PCB", "box", "3D printing"]})
    d.do("jig.export", {"path": "dist/electronics-enclosure.3dcraftjig"})
    return d.steps


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
