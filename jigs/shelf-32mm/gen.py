#!/usr/bin/env python3
"""Writes build.json for the 32 mm shelf system Jig (python3 gen.py > build.json).

A carcass on the European 32 mm system: two sides drilled with 5 mm shelf-pin
holes on a 32 mm pitch, two columns 37 mm from the front and the back edge;
a top and a bottom between the sides, an optional fixed middle shelf on a hole
row, adjustable shelves resting on pins, a back panel in a groove or a rebate
and an optional plinth board. Sizes from a preset (real IKEA carcass sizes)
or set by hand.

Axes: x across the width (left side at x = 0), y from the front (y = 0) to
the back, z up from the floor.
"""
import json

PRESETS = [
    # key, width, depth, height (mm). Row 1 is "Custom": the size parameters.
    ("Custom", 0, 0, 0),
    ("BILLY 40 x 28 x 202", 400, 280, 2020),
    ("BILLY 80 x 28 x 202", 800, 280, 2020),
    ("PAX 50 x 35 x 201", 500, 350, 2010),
    ("PAX 50 x 58 x 201", 500, 580, 2010),
    ("PAX 50 x 58 x 236", 500, 580, 2360),
    ("PAX 75 x 58 x 201", 750, 580, 2010),
    ("PAX 75 x 58 x 236", 750, 580, 2360),
    ("PAX 100 x 35 x 201", 1000, 350, 2010),
    ("PAX 100 x 58 x 201", 1000, 580, 2010),
    ("PAX 100 x 58 x 236", 1000, 580, 2360),
]
THICK = [("15 mm", 15), ("16 mm", 16), ("18 mm", 18), ("19 mm", 19), ("22 mm", 22)]
BACKS = [("3 mm hardboard", 3), ("4 mm plywood", 4), ("6 mm plywood", 6), ("8 mm plywood", 8)]

INPUTS = [
    ("preset", "1"),
    ("width", "800 mm"),
    ("depth", "320 mm"),
    ("height", "1600 mm"),
    ("thickChoice", "3"),
    ("shelves", "2"),
    ("fixed", "1"),
    ("back", "1"),          # 1 groove, 2 rebate
    ("backChoice", "1"),
    ("plinthH", "70 mm"),   # 0 = no plinth
]
DERIVED = [
    ("W", 'if(preset == 1, width, presets[preset].w)'),
    ("D", 'if(preset == 1, depth, presets[preset].d)'),
    ("H", 'if(preset == 1, height, presets[preset].h)'),
    ("t", "thicknesses[thickChoice].t"),
    ("bt", "backs[backChoice].t"),
    ("pitch", "32 mm"),
    ("edge", "37 mm"),                       # hole columns from the front and the back edge
    ("pinR", "2.5 mm"),                      # 5 mm shelf pins
    ("hd", "min(12 mm, t - 5 mm)"),          # hole depth
    ("gd", "min(8 mm, t / 2 - 1 mm)"),       # groove or rebate depth
    ("inset", "12 mm"),                      # groove from the back edge
    ("gw", "bt + 0.5 mm"),                   # groove or rebate width
    ("grooved", "back == 1"),
    ("backFront", "if(grooved, D - inset - gw, D - gw)"),   # front of the slot the back sits in
    ("zb", "plinthH"),                       # underside of the bottom panel
    ("zIn", "zb + t"),                       # top of the bottom panel: the hole grid's origin
    ("zTopIn", "H - t"),                     # underside of the top panel
    ("hIn", "zTopIn - zIn"),
    ("z0", "zIn + 2 * pitch"),               # first hole row
    ("rows", "floor((hIn - 4 * pitch) / pitch) + 1"),
    ("zm", "zIn + pitch * round(hIn / (2 * pitch))"),       # row of the fixed shelf
    ("hA", "if(fixed, zm - zIn, hIn)"),      # lower (or only) compartment
    ("hB", "zTopIn - zm"),                   # upper compartment
    ("hEff", "if(fixed, min(hA, hB), hIn)"),
    ("maxShelves", "clamp(floor(hEff / (3 * pitch)) - 1, 0, 8)"),
    ("k", "min(shelves, maxShelves)"),
    ("gA", "pitch * floor(hA / (k + 1) / pitch)"),
    ("gB", "pitch * floor(hB / (k + 1) / pitch)"),
    ("lift", "3 mm"),                        # shelf underside above a row's centre (on the pins)
    ("sc", "1 mm"),                          # side clearance of an adjustable shelf
    ("rnd", "1 mm"),                         # edge rounding
]


def block(name, x0, x1, y0, y1, z0, z1):
    return ["feature.block", {"name": name,
                              "size": ["(%s) - (%s)" % (x1, x0), "(%s) - (%s)" % (y1, y0), "(%s) - (%s)" % (z1, z0)],
                              "position": [x0, y0, z0]}]


def main():
    s = []
    s.append(["table.set", {"name": "presets", "columns": ["preset", {"name": "w", "unit": "mm"},
                                                           {"name": "d", "unit": "mm"}, {"name": "h", "unit": "mm"}],
                            "rows": [list(r) for r in PRESETS]}])
    s.append(["table.set", {"name": "thicknesses", "columns": ["thickness", {"name": "t", "unit": "mm"}],
                            "rows": [list(r) for r in THICK]}])
    s.append(["table.set", {"name": "backs", "columns": ["back", {"name": "t", "unit": "mm"}],
                            "rows": [list(r) for r in BACKS]}])
    for name, expr in INPUTS + DERIVED:
        s.append(["variable.set", {"name": name, "expr": expr}])

    # Left side, its outer front and top edges rounded (they do not touch the inner face,
    # which is the drilling face of the cut sheet).
    s.append(block("LeftBlank", "0 mm", "t", "0 mm", "D", "0 mm", "H"))
    s.append(["feature.fillet", {"name": "LeftRound", "edges": [["F_LEFT:face(2)", "F_LEFT:face(4)"]], "radius": "rnd"}])
    # Shelf-pin holes: one column of rows, repeated to the back column.
    s.append(["feature.cylinder", {"name": "Hole", "radius": "pinR", "height": "hd + 1 mm",
                                   "position": ["t - hd", "edge", "z0"], "axis": [1, 0, 0]}])
    s.append(["feature.pattern", {"name": "HoleColumn", "source": "Hole", "count": "rows",
                                  "step": ["0 mm", "0 mm", "pitch"]}])
    s.append(["feature.pattern", {"name": "Holes", "source": "HoleColumn", "count": "2",
                                  "step": ["0 mm", "D - 2 * edge", "0 mm"]}])
    s.append(["feature.boolean", {"op": "subtract", "target": "LeftRound", "tool": "Holes", "name": "LeftDrilled"}])
    # Stopped groove or rebate for the back panel (kept inside the side, so the drilling face
    # stays one face with the slot in it).
    s.append(block("SideGroove", "t - gd", "t + 1 mm", "D - inset - gw", "D - inset", "zIn - gd", "zTopIn + gd"))
    s.append(["feature.when", {"feature": "SideGroove", "expr": "grooved"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "LeftDrilled", "tool": "SideGroove", "name": "LeftG"}])
    s.append(block("SideRebate", "t - gd", "t + 1 mm", "D - gw", "D + 1 mm", "zIn - gd", "zTopIn + gd"))
    s.append(["feature.when", {"feature": "SideRebate", "expr": "!grooved"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "LeftG", "tool": "SideRebate", "name": "LeftSide"}])
    s.append(["feature.mirror", {"source": "LeftSide", "normal": [1, 0, 0], "point": ["W / 2", "0 mm", "0 mm"],
                                 "keep": True, "name": "RightSide"}])

    # Top and bottom between the sides, with a groove or rebate running through.
    s.append(block("TopBlank", "t", "W - t", "0 mm", "D", "zTopIn", "H"))
    s.append(["feature.fillet", {"name": "TopRound", "edges": [["F_TOP:face(2)", "F_TOP:face(0)"]], "radius": "rnd"}])
    s.append(block("TopGroove", "t - 1 mm", "W - t + 1 mm", "D - inset - gw", "D - inset", "zTopIn - 1 mm", "zTopIn + gd"))
    s.append(["feature.when", {"feature": "TopGroove", "expr": "grooved"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "TopRound", "tool": "TopGroove", "name": "TopG"}])
    s.append(block("TopRebate", "t - 1 mm", "W - t + 1 mm", "D - gw", "D + 1 mm", "zTopIn - 1 mm", "zTopIn + gd"))
    s.append(["feature.when", {"feature": "TopRebate", "expr": "!grooved"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "TopG", "tool": "TopRebate", "name": "Top"}])

    s.append(block("BottomBlank", "t", "W - t", "0 mm", "D", "zb", "zIn"))
    s.append(["feature.fillet", {"name": "BottomRound", "edges": [["F_BOT:face(2)", "F_BOT:face(1)"]], "radius": "rnd"}])
    s.append(block("BottomGroove", "t - 1 mm", "W - t + 1 mm", "D - inset - gw", "D - inset", "zIn - gd", "zIn + 1 mm"))
    s.append(["feature.when", {"feature": "BottomGroove", "expr": "grooved"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "BottomRound", "tool": "BottomGroove", "name": "BottomG"}])
    s.append(block("BottomRebate", "t - 1 mm", "W - t + 1 mm", "D - gw", "D + 1 mm", "zIn - gd", "zIn + 1 mm"))
    s.append(["feature.when", {"feature": "BottomRebate", "expr": "!grooved"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "BottomG", "tool": "BottomRebate", "name": "Bottom"}])

    # Back panel in the slots.
    s.append(block("Back", "t - gd + 0.5 mm", "W - t + gd - 0.5 mm",
                   "if(grooved, D - inset - gw + 0.25 mm, D - bt)", "if(grooved, D - inset - 0.25 mm, D)",
                   "zIn - gd + 0.5 mm", "zTopIn + gd - 0.5 mm"))

    # Fixed middle shelf, centred on a hole row (the holes behind its ends take its connectors).
    s.append(block("FixedBlank", "t", "W - t", "0 mm", "backFront", "zm - t / 2", "zm + t / 2"))
    s.append(["feature.fillet", {"name": "FixedShelf", "edges": [["F_FIX:face(2)", "F_FIX:face(1)"]], "radius": "rnd"}])
    for f in ["FixedBlank", "FixedShelf"]:
        s.append(["feature.when", {"feature": f, "expr": "fixed"}])

    # Adjustable shelves on pins, evenly spread over the lower (or only) compartment ...
    s.append(block("ShelfA", "t + sc", "W - t - sc", "0 mm", "backFront - 1 mm", "zIn + gA + lift", "zIn + gA + lift + t"))
    s.append(["feature.fillet", {"name": "ShelfARound", "edges": [["F_SA:face(2)", "F_SA:face(1)"]], "radius": "rnd"}])
    s.append(["feature.pattern", {"name": "ShelvesLow", "source": "ShelfARound", "count": "max(k, 1)",
                                  "step": ["0 mm", "0 mm", "gA"]}])
    for f in ["ShelfA", "ShelfARound", "ShelvesLow"]:
        s.append(["feature.when", {"feature": f, "expr": "k > 0"}])
    # ... and over the upper compartment when there is a fixed shelf.
    s.append(block("ShelfB", "t + sc", "W - t - sc", "0 mm", "backFront - 1 mm", "zm + gB + lift", "zm + gB + lift + t"))
    s.append(["feature.fillet", {"name": "ShelfBRound", "edges": [["F_SB:face(2)", "F_SB:face(1)"]], "radius": "rnd"}])
    s.append(["feature.pattern", {"name": "ShelvesHigh", "source": "ShelfBRound", "count": "max(k, 1)",
                                  "step": ["0 mm", "0 mm", "gB"]}])
    for f in ["ShelfB", "ShelfBRound", "ShelvesHigh"]:
        s.append(["feature.when", {"feature": f, "expr": "k > 0 && fixed"}])

    # Plinth board at the front, between the sides.
    s.append(block("Plinth", "t", "W - t", "0 mm", "t", "0 mm", "zb"))
    s.append(["feature.when", {"feature": "Plinth", "expr": "plinthH >= 1 mm"}])

    wood = {"color": "#D9B98A", "roughness": 0.8}
    for b in ["LeftSide", "RightSide", "Top", "Bottom"]:
        s.append(["body.appearance", dict(body=b, **wood)])
    for b in ["FixedShelf", "ShelvesLow", "ShelvesHigh"]:
        s.append(["body.appearance", {"body": b, "color": "#CDAA78", "roughness": 0.8}])
    s.append(["body.appearance", {"body": "Back", "color": "#E8DFCC", "roughness": 0.9}])
    s.append(["body.appearance", {"body": "Plinth", "color": "#7A5638", "roughness": 0.8}])

    # No two parts overlap (the shelves clear the fixed shelf, the back sits in its slots).
    s.append(["assert.add", {"name": "parts do not overlap", "measure": "interference", "of": {"kind": "body"}}])

    pub = [
        ("preset", dict(label="Size", description="A real IKEA carcass size (BILLY bookcase, PAX wardrobe frame), or Custom for the width, depth and height below",
                        group="Size", order=1, kind="choice", choicesFrom="presets")),
        ("width", dict(label="Width (Custom)", description="Outside width, used when Size is Custom", group="Size", order=2,
                       min="300 mm", max="1200 mm", step="1 mm", unit="mm")),
        ("depth", dict(label="Depth (Custom)", description="Outside depth, used when Size is Custom", group="Size", order=3,
                       min="250 mm", max="650 mm", step="1 mm", unit="mm")),
        ("height", dict(label="Height (Custom)", description="Outside height, used when Size is Custom", group="Size", order=4,
                        min="600 mm", max="2400 mm", step="1 mm", unit="mm")),
        ("thickChoice", dict(label="Panel thickness", description="Thickness of the sides, top, bottom and shelves",
                             group="Material", order=1, kind="choice", choicesFrom="thicknesses")),
        ("backChoice", dict(label="Back panel", description="Thickness of the back panel",
                            group="Material", order=2, kind="choice", choicesFrom="backs")),
        ("back", dict(label="Back fixing", description="The back slides into a groove 12 mm from the back edge, or lies in a rebate flush with it",
                      group="Material", order=3, kind="choice", choices=["groove", "rebate"])),
        ("shelves", dict(label="Adjustable shelves", description="Shelves on 5 mm pins, spread evenly over each compartment (per compartment when there is a fixed shelf); at most what keeps 96 mm between them",
                         group="Shelves", order=1, kind="integer", min="0", max="maxShelves")),
        ("fixed", dict(label="Fixed middle shelf", description="A fixed shelf on the hole row nearest the middle, which stiffens a tall carcass",
                       group="Shelves", order=2, kind="boolean")),
        ("plinthH", dict(label="Plinth height", description="Height of the plinth board under the bottom panel; 0 for none (the bottom on the floor)",
                         group="Base", order=1, min="0 mm", max="150 mm", step="1 mm", unit="mm")),
    ]
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        s.append(["variable.publish", p])

    s.append(["set.define", {"name": "Cut sheet", "kind": "face", "where": {"any": [
        {"in": "LeftSide", "madeBy": "LeftBlank", "normal": {"along": "x"}},
        {"in": "RightSide", "madeBy": "LeftBlank", "normal": {"along": "-x"}},
        {"in": "Top", "normal": {"along": "z"}},
        {"in": "Bottom", "normal": {"along": "-z"}},
        {"in": "FixedShelf", "normal": {"along": "-z"}},
        {"in": "ShelvesLow", "normal": {"along": "-z"}},
        {"in": "ShelvesHigh", "normal": {"along": "-z"}},
        {"in": "Back", "normal": {"along": "y"}},
        {"in": "Plinth", "normal": {"along": "-y"}},
    ]}}])
    s.append(["set.define", {"name": "Side drilling", "kind": "face", "where":
              {"in": "LeftSide", "madeBy": "LeftBlank", "normal": {"along": "x"}}}])

    s.append(["document.info", {
        "title": "32 mm shelf system (IKEA compatible)",
        "description": "A bookcase or wardrobe carcass on the European 32 mm system: the sides drilled for 5 mm shelf pins "
                       "on a 32 mm pitch, 37 mm from the front and the back edge, so IKEA-compatible shelf pins and fittings fit. "
                       "Choose a real IKEA carcass size (BILLY, PAX) or your own, the panel thickness, adjustable shelves, a fixed "
                       "middle shelf, a back in a groove or a rebate and a plinth. To cut it: File > Export..., DXF or SVG with the "
                       "face set \"Cut sheet\" (every panel, the sides with their holes and back slot) or \"Side drilling\" (one side, "
                       "a drilling template). IKEA is a trademark of Inter IKEA Systems B.V.; this Jig is not affiliated with or "
                       "endorsed by IKEA.",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/shelf-32mm",
        "tags": ["furniture", "cabinet", "bookcase", "32 mm system", "CNC", "woodworking"]}])
    s.append(["jig.export", {"path": "dist/shelf-32mm.3dcraftjig"}])
    return resolve(s)


FEATURE_CMDS = {"feature.block", "feature.cylinder", "feature.fillet", "feature.chamfer", "feature.pattern",
                "feature.boolean", "feature.mirror", "feature.transform", "feature.extrude"}


def resolve(steps):
    """Feature ids are F1, F2, ... in history order; face names need them, so the
    placeholders F_<NAME> (the block's name in ALIAS) are replaced by the id."""
    ids, n = {}, 0
    for cmd, p in steps:
        if cmd in FEATURE_CMDS:
            n += 1
            ids[p["name"]] = "F%d" % n
    text = json.dumps(steps)
    for alias, name in ALIAS.items():
        text = text.replace(alias + ":", ids[name] + ":")
    return json.loads(text)


ALIAS = {"F_LEFT": "LeftBlank", "F_TOP": "TopBlank", "F_BOT": "BottomBlank", "F_FIX": "FixedBlank",
         "F_SA": "ShelfA", "F_SB": "ShelfB"}


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
