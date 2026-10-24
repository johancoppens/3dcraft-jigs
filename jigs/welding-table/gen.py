#!/usr/bin/env python3
"""Writes build.json of the welding-table Jig:  python3 gen.py > build.json

A system welding table in the style of the 16 mm and 28 mm block tables: a top plate with a grid of
system holes, side plates (skirts) along all four edges carrying the same grid, a grid of half-lapped
ribs under the top, and optional legs with feet and a lower frame. The system (hole, grid, plate and
side height) comes from the table `systems`. Every plate is a flat part for laser or plasma cutting; the
named face set "Cut sheet" lays them out.
"""
import json


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


def W(feature, expr):
    return ["feature.when", {"feature": feature, "expr": expr}]


STEEL = {"color": "#7D858C", "metallic": 0.85, "roughness": 0.4}
PAINT = {"color": "#5B7299", "metallic": 0.3, "roughness": 0.5}

steps = [
    # system, hole diameter, grid, plate thickness, side height (with the plate), rib and leg sizes
    ["table.set", {"name": "systems",
                   "columns": ["system", {"name": "hole", "unit": "mm"}, {"name": "grid", "unit": "mm"},
                               {"name": "plate", "unit": "mm"}, {"name": "side", "unit": "mm"},
                               {"name": "rib", "unit": "mm"}, {"name": "leg", "unit": "mm"}],
                   "rows": [["System 16", 16, 50, 12, 100, 10, 80], ["System 28", 28, 100, 25, 200, 15, 100]]}],
    V("sys", "1"),
    V("L", "1200 mm"),
    V("Wd", "800 mm"),
    V("ribEvery", "4"),
    V("clearance", "0.3 mm"),
    V("frame", "3"),
    V("tableH", "900 mm"),
    V("hd", "systems[sys].hole"),
    V("g", "systems[sys].grid"),
    V("pt", "systems[sys].plate"),
    V("sh", "systems[sys].side"),
    V("rt", "systems[sys].rib"),
    V("legS", "systems[sys].leg"),
    # The hole grid, centred on the plate: nX by nY holes, the first at (x0, y0); rows on the sides.
    V("nX", "floor(L / g)"),
    V("nY", "floor(Wd / g)"),
    V("x0", "(L - (nX - 1) * g) / 2"),
    V("y0", "(Wd - (nY - 1) * g) / 2"),
    V("rows", "floor(sh / g)"),
    # Ribs every ribEvery holes, on the lines between two holes, centred as far as the grid allows.
    V("nRx", "max(0, ceil((nX - 1) / ribEvery) - 1)"),
    V("nRy", "max(0, ceil((nY - 1) / ribEvery) - 1)"),
    V("xr0", "x0 + (round((nX - 2) / 2 - (nRx - 1) * ribEvery / 2) + 0.5) * g"),
    V("yr0", "y0 + (round((nY - 2) / 2 - (nRy - 1) * ribEvery / 2) + 0.5) * g"),
    V("ribStep", "ribEvery * g"),
    V("rh", "sh - pt"),
    V("sw", "rt + clearance"),
    # Legs inside the corners, feet on the floor, a frame 150 mm above it.
    V("legsOn", "frame >= 2"),
    V("frameOn", "frame == 3"),
    V("footT", "10 mm"),
    V("footS", "legS + 40 mm"),
    V("railS", "0.75 * legS"),
    V("railZ", "-tableH + 150 mm"),
]

# The top plate: z from -pt to 0 (the working surface).
steps += [
    ["sketch.create", {"name": "TopSketch", "plane": "xy", "offset": "-pt"}],
    ["sketch.rect", {"sketch": "TopSketch", "from": ["0 mm", "0 mm"], "to": ["L", "Wd"]}],
    ["sketch.circle", {"sketch": "TopSketch", "center": ["x0", "y0"], "radius": "hd / 2"}],      # e9, e10
    ["sketch.pattern", {"sketch": "TopSketch", "entities": ["e10"], "count": "nX", "step": ["g", "0 mm"],
                        "count2": "nY", "step2": ["0 mm", "g"]}],
    ["feature.extrude", {"sketch": "TopSketch", "distance": "pt", "name": "Top"}],
    # Front side: on zx (sketch x = world z, y = world x), extruded along +y.
    ["sketch.create", {"name": "FrontSketch", "plane": "zx"}],
    ["sketch.rect", {"sketch": "FrontSketch", "from": ["-sh", "0 mm"], "to": ["-pt", "L"]}],
    ["sketch.circle", {"sketch": "FrontSketch", "center": ["-g / 2", "x0"], "radius": "hd / 2"}],
    ["sketch.pattern", {"sketch": "FrontSketch", "entities": ["e10"], "count": "nX", "step": ["0 mm", "g"],
                        "count2": "rows", "step2": ["-g", "0 mm"]}],
    ["feature.extrude", {"sketch": "FrontSketch", "distance": "pt", "name": "Front"}],
    ["feature.mirror", {"source": "Front", "normal": [0, 1, 0], "point": ["0 mm", "Wd / 2", "0 mm"], "keep": True,
                        "name": "Back"}],
    # Left side: on yz (sketch x = world y, y = world z), between the front and back, extruded along +x.
    ["sketch.create", {"name": "LeftSketch", "plane": "yz"}],
    ["sketch.rect", {"sketch": "LeftSketch", "from": ["pt", "-sh"], "to": ["Wd - pt", "-pt"]}],
    ["sketch.circle", {"sketch": "LeftSketch", "center": ["y0", "-g / 2"], "radius": "hd / 2"}],
    ["sketch.pattern", {"sketch": "LeftSketch", "entities": ["e10"], "count": "nY", "step": ["g", "0 mm"],
                        "count2": "rows", "step2": ["0 mm", "-g"]}],
    ["feature.extrude", {"sketch": "LeftSketch", "distance": "pt", "name": "Left"}],
    ["feature.mirror", {"source": "Left", "normal": [1, 0, 0], "point": ["L / 2", "0 mm", "0 mm"], "keep": True,
                        "name": "Right"}],
    # Ribs across (along y, at x positions), half-lapped from the top, and along (along x), from below.
    ["feature.block", {"name": "RibY", "size": ["rt", "Wd - 2 * pt", "rh"], "position": ["xr0 - rt / 2", "pt", "-sh"]}],
    ["feature.block", {"name": "LapY", "size": ["rt + 2 mm", "sw", "rh / 2 + 1 mm"],
                       "position": ["xr0 - rt / 2 - 1 mm", "yr0 - sw / 2", "-pt - rh / 2"]}],
    ["feature.pattern", {"name": "LapsY", "source": "LapY", "count": "nRy", "step": ["0 mm", "ribStep", "0 mm"]}],
    ["feature.boolean", {"op": "subtract", "target": "RibY", "tool": "LapsY", "name": "RibYLapped"}],
    ["feature.pattern", {"name": "RibsY", "source": "RibYLapped", "count": "nRx", "step": ["ribStep", "0 mm", "0 mm"]}],
    ["feature.block", {"name": "RibX", "size": ["L - 2 * pt", "rt", "rh"], "position": ["pt", "yr0 - rt / 2", "-sh"]}],
    ["feature.block", {"name": "LapX", "size": ["sw", "rt + 2 mm", "rh / 2 + 1 mm"],
                       "position": ["xr0 - sw / 2", "yr0 - rt / 2 - 1 mm", "-sh - 1 mm"]}],
    ["feature.pattern", {"name": "LapsX", "source": "LapX", "count": "nRx", "step": ["ribStep", "0 mm", "0 mm"]}],
    ["feature.boolean", {"op": "subtract", "target": "RibX", "tool": "LapsX", "name": "RibXLapped"}],
    ["feature.pattern", {"name": "RibsX", "source": "RibXLapped", "count": "nRy", "step": ["0 mm", "ribStep", "0 mm"]}],
]
for f in ["RibY", "LapY", "LapsY", "RibYLapped", "RibsY"]:
    steps.append(W(f, "nRx >= 1 && nRy >= 1"))
for f in ["RibX", "LapX", "LapsX", "RibXLapped", "RibsX"]:
    steps.append(W(f, "nRx >= 1 && nRy >= 1"))

# Legs with feet in the four corners, and a frame of rails between them.
steps += [
    ["feature.block", {"name": "Leg", "size": ["legS", "legS", "tableH - sh - footT"],
                       "position": ["pt", "pt", "-tableH + footT"]}],
    ["feature.block", {"name": "Foot", "size": ["footS", "footS", "footT"],
                       "position": ["pt + legS / 2 - footS / 2", "pt + legS / 2 - footS / 2", "-tableH"]}],
    ["feature.boolean", {"op": "union", "target": "Leg", "tool": "Foot", "name": "LegFoot"}],
    ["feature.pattern", {"name": "LegRow", "source": "LegFoot", "count": "2", "step": ["L - 2 * pt - legS", "0 mm", "0 mm"]}],
    ["feature.pattern", {"name": "Legs", "source": "LegRow", "count": "2", "step": ["0 mm", "Wd - 2 * pt - legS", "0 mm"]}],
    ["feature.block", {"name": "RailX", "size": ["L - 2 * pt - 2 * legS", "railS", "railS"],
                       "position": ["pt + legS", "pt + legS / 2 - railS / 2", "railZ"]}],
    ["feature.pattern", {"name": "RailsX", "source": "RailX", "count": "2", "step": ["0 mm", "Wd - 2 * pt - legS", "0 mm"]}],
    ["feature.block", {"name": "RailY", "size": ["railS", "Wd - 2 * pt - 2 * legS", "railS"],
                       "position": ["pt + legS / 2 - railS / 2", "pt + legS", "railZ"]}],
    ["feature.pattern", {"name": "RailsY", "source": "RailY", "count": "2", "step": ["L - 2 * pt - legS", "0 mm", "0 mm"]}],
]
for f in ["Leg", "Foot", "LegFoot", "LegRow", "Legs"]:
    steps.append(W(f, "legsOn"))
for f in ["RailX", "RailsX", "RailY", "RailsY"]:
    steps.append(W(f, "frameOn"))

for body in ["Top", "Front", "Back", "Left", "Right", "RibsX", "RibsY"]:
    steps.append(["body.appearance", dict(body=body, **STEEL)])
for body in ["Legs", "RailsX", "RailsY"]:
    steps.append(["body.appearance", dict(body=body, **PAINT)])
steps += [
    ["assert.add", {"name": "holes in the top", "measure": "count",
                    "of": {"kind": "face", "where": {"in": "Top", "hole": True}}, "eq": "nX * nY"}],
    ["assert.add", {"name": "holes in the sides", "measure": "count",
                    "of": {"kind": "face", "where": {"any": [{"in": "Front"}, {"in": "Back"}, {"in": "Left"}, {"in": "Right"}],
                                                     "hole": True}}, "eq": "2 * rows * (nX + nY)"}],
]

params = [
    dict(name="sys", label="System", group="System", order=1, kind="choice", choicesFrom="systems",
         description="System 16: 16 mm holes on a 50 mm grid, 12 mm plate, 100 mm sides. System 28: 28 mm holes on a "
                     "100 mm grid, 25 mm plate, 200 mm sides"),
    dict(name="L", label="Length", group="Size", order=1, min="600 mm", max="2000 mm", step="50 mm", unit="mm",
         description="Length of the top (x)"),
    dict(name="Wd", label="Width", group="Size", order=2, min="400 mm", max="1200 mm", step="50 mm", unit="mm",
         description="Width of the top (y)"),
    dict(name="ribEvery", label="Rib spacing", group="Ribs", order=1, kind="integer", min="2", max="8",
         description="A rib every so many holes, both ways, on the lines between the holes"),
    dict(name="clearance", label="Lap clearance", group="Ribs", order=2, min="0 mm", max="1 mm", step="0.05 mm",
         unit="mm", description="Extra width of the half-lap slots where the ribs cross"),
    dict(name="frame", label="Base", group="Base", order=1, kind="choice", choices=["None", "Legs", "Legs and frame"],
         description="Only the block (to put on trestles), four legs with feet, or legs joined by a frame near the floor"),
    dict(name="tableH", label="Working height", group="Base", order=2, min="600 mm", max="1000 mm", step="10 mm",
         unit="mm", description="Height of the top surface above the floor, with legs"),
]
for p in params:
    steps.append(["variable.publish", p])
steps += [
    ["set.define", {"name": "Cut sheet", "kind": "face", "where": {"any": [
        {"in": "Top", "normal": {"along": "z"}}, {"in": "Front", "normal": {"along": "-y"}},
        {"in": "Back", "normal": {"along": "y"}}, {"in": "Left", "normal": {"along": "-x"}},
        {"in": "Right", "normal": {"along": "x"}}, {"in": "RibsX", "normal": {"along": "-y"}},
        {"in": "RibsY", "normal": {"along": "x"}}]}}],
    ["document.info", {
        "title": "Welding table",
        "description": "A system welding table in the style of the 16 mm and 28 mm block tables: a top plate with a "
                       "grid of system holes, side plates on all four edges carrying the same grid, half-lapped ribs "
                       "under the top, and legs with a frame if you want them. Choose the system and the size. To cut "
                       "the plates: File > Export..., DXF or SVG with the face set \"Cut sheet\" (the top, the four "
                       "sides and every rib at true size); STEP for the whole table.",
        "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/welding-table",
        "tags": ["welding", "fixture table", "steel", "laser", "plasma"]}],
    ["jig.export", {"path": "dist/welding-table.3dcraftjig"}],
]
print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
