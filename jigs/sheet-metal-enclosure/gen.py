#!/usr/bin/env python3
"""Writes build.json for the sheet-metal enclosure Jig (python3 -I gen.py > build.json).

build.json is the source of truth; this script is how it was written and is
kept so the tables and the construction are readable. It computes no
geometry: every size is a 3DCraft formula of the inputs.

Two parts, each bent from one sheet (feature.sheetMetal):

- the base: a floor with two tall side walls bent up, a return flange bent
  inwards at the top of each wall (the lid's screws go through it) and a
  low lip bent up at the front and the back; the floor's corners relieved
  and closed (the walls cover the lips' ends).
- the lid: a top with two short side skirts and a front and a back wall bent
  down; it sits on the return flanges, its skirts and walls outside the
  base with a clearance, its corners relieved and closed (the front and
  back walls cover the skirts' ends).

Every hole is cut flat: the return flanges' screw holes are holes of the
base's sketch, drawn where the flanges lie in the flat pattern; the lid's
screw holes are holes of its sketch; the optional vent slots and feet holes
are `cutouts` sketches switched by `when`.
"""
import json

ID = "sheet-metal-enclosure"

# Material per row: minimum inner bend radius and K-factor as multiples of
# the thickness / plain factor, and the press brake's V-die opening as a
# multiple of the thickness (the minimum flange is 0.7 of it). Sources in
# README.md.
MATERIALS = [
    # name,                         minR/t, K,    V/t, red, green, blue
    ["Steel DC01",                   1.0,   0.42, 8,   125, 133, 140],
    ["Aluminium 5754",               1.0,   0.38, 6,   185, 190, 196],
    ["Stainless 304",                2.0,   0.45, 10,  200, 206, 214],
]
# Screws: nominal diameter, clearance hole (ISO 273 medium), pan head
# diameter and height (ISO 7045 / ISO 14583).
SCREWS = [
    ["M3", 3.0, 3.4, 5.6, 1.8],
    ["M4", 4.0, 4.5, 8.0, 2.4],
]
CORNERS = ["Open", "Butt", "Overlap", "Miter"]     # feature.sheetMetal corner kind 1..4
RELIEFS = ["Rect", "Round", "Tear"]                # relief shape 1..3

INPUTS = [
    ("Wi", "160 mm"), ("Di", "120 mm"), ("Hi", "50 mm"),
    ("material", "1"), ("t", "1 mm"),
    ("radiusExtra", "0"),
    ("screw", "1"), ("fit", "0.5 mm"),
    ("vents", "1"), ("feet", "1"),
    ("corner", "3"), ("gap", "0.5 mm"), ("reliefShape", "2"),
]
DERIVED = [
    ("R", "(mats[material].minR + radiusExtra) * t"),
    ("K", "mats[material].k"),
    ("V", "mats[material].v * t"),               # die opening
    ("minFlange", "0.7 * V"),                   # to the outside mould line
    ("holeEdge", "2.5 * t + R"),                # least hole edge to bend tangent line
    ("relief", "R + t + 0.5 mm"),               # corner relief along each edge: past the bend zone R + t
    ("d", "screws[screw].d"),
    ("dc", "screws[screw].clear"),
    # Base: floor half sizes (the walls' inner faces at +-Wi/2, the lips' at +-Di/2).
    ("a", "Wi / 2 - R"),
    ("b", "Di / 2 - R"),
    ("wallL", "Hi - t - 2 * R"),                # side wall flat: the return flange's top at Hi + t
    ("lipL", "max(10 mm, minFlange - R - t + 1 mm)"),
    ("retL", "max(minFlange - R - t + 1 mm, 2 * holeEdge + dc + 1 mm)"),
    # Lid: its top's underside at Hi + t, on the return flanges.
    ("zl", "Hi + t"),
    ("al", "Wi / 2 + t + fit - R"),
    ("bl", "Di / 2 + t + fit - R"),
    ("skirtL", "max(12 mm, minFlange - R - t + 1 mm)"),
    ("frontL", "zl - R - fit"),                 # the lid's front and back walls end fit above the floor
    # Screws: through the lid's top and the return flanges' middle.
    ("xs", "Wi / 2 - R - retL / 2"),
    ("ys", "b - relief - max(8 mm, holeEdge + dc)"),
    # Where the return flanges' holes lie in the base's flat pattern: past the wall's bend
    # (its allowance BA), the wall's flat, the return flange's bend and half the return flange.
    ("BA", "pi / 2 * (R + K * t)"),             # bend allowance of a 90 degree bend
    ("flatHoleX", "a + BA + wallL + BA + retL / 2"),
    ("flatHoleY", "ys"),
    ("headD", "screws[screw].head"),
    ("headK", "screws[screw].k"),
    ("shankL", "2 * t + 3 * d"),                # through both sheets and a nut below
    # Vents: slots along y in the lid's top, between the return flanges.
    ("ventW", "max(4 mm, 2 * t)"),         # slot width at least 2 t
    ("ventP", "2 * ventW + 2 mm"),
    ("ventSpan", "Wi - 2 * R - 2 * retL - 10 mm"),
    ("ventN", "max(1, floor((ventSpan - ventW) / ventP) + 1)"),
    ("ventX0", "-(ventN - 1) * ventP / 2"),
    ("ventH", "Di / 4 - ventW / 2"),            # half the straight part: slots Di / 2 long
    # Feet holes: in the floor's corners.
    ("footX", "a - relief - max(8 mm, holeEdge + dc)"),
    ("footY", "b - relief - max(8 mm, holeEdge + dc)"),
]


class Doc:
    def __init__(self):
        self.steps = []

    def do(self, cmd, params):
        self.steps.append([cmd, params])


def slot(sk, x, h, r):
    """A stadium along y centred at (x, 0): straight half length h, radius r."""
    X, H, Rr = "(%s)" % x, "(%s)" % h, "(%s)" % r
    return {"sketch": sk, "start": ["%s + %s" % (X, Rr), "-" + H], "segments": [
        {"line": ["%s + %s" % (X, Rr), H]},
        {"arc": ["%s - %s" % (X, Rr), H], "center": [X, H]},
        {"line": ["%s - %s" % (X, Rr), "-" + H]},
        {"arc": "start", "center": [X, "-" + H]},
    ]}


def sheet(sketch, name, flanges, walls, others, cutouts):
    """A part with every corner closed by the `corner` choice, the flanges `walls` covering the others' ends."""
    return {
        "sketch": sketch, "name": name, "thickness": "t", "radius": "R", "kFactor": "K",
        "relief": {"shape": "reliefShape", "size": "relief"},
        "corner": {"kind": "corner", "gap": "gap"},
        "corners": [{"flanges": [w, o], "kind": "corner", "over": w} for w in walls for o in others],
        "cutouts": cutouts,
        "flanges": flanges}


def base(d):
    sk = "BaseSketch"
    d.do("sketch.create", {"plane": "xy", "name": sk})
    # Lines e5 (front, -y), e6 (right, +x), e7 (back), e8 (left).
    d.do("sketch.rect", {"sketch": sk, "from": ["-a", "-b"], "to": ["a", "b"]})
    # The return flanges' screw holes, where the flanges lie in the flat pattern.
    for sx in ("", "-"):
        for sy in ("", "-"):
            d.do("sketch.circle", {"sketch": sk, "center": [sx + "flatHoleX", sy + "flatHoleY"], "radius": "dc / 2"})
    # The feet holes: an option, a cut-out sketch in the floor's plane.
    d.do("sketch.create", {"plane": "xy", "name": "FeetHoles"})
    for sx in ("", "-"):
        for sy in ("", "-"):
            d.do("sketch.circle", {"sketch": "FeetHoles", "center": [sx + "footX", sy + "footY"], "radius": "dc / 2"})
    d.do("feature.when", {"feature": "FeetHoles", "expr": "feet == 1"})
    d.do("feature.sheetMetal", sheet(sk, "Base", [
        {"edge": "e6", "length": "wallL", "angle": "90 deg"},   # 0 right wall
        {"edge": "e8", "length": "wallL", "angle": "90 deg"},   # 1 left wall
        {"edge": "e5", "length": "lipL", "angle": "90 deg"},    # 2 front lip
        {"edge": "e7", "length": "lipL", "angle": "90 deg"},    # 3 back lip
        {"tip": 0, "length": "retL", "angle": "90 deg"},        # 4 right return flange
        {"tip": 1, "length": "retL", "angle": "90 deg"},        # 5 left return flange
    ], [0, 1], [2, 3], ["FeetHoles"]))


def lid(d):
    sk = "LidSketch"
    d.do("sketch.create", {"plane": "xy", "offset": "zl", "name": sk})
    d.do("sketch.rect", {"sketch": sk, "from": ["-al", "-bl"], "to": ["al", "bl"]})
    for sx in ("", "-"):
        for sy in ("", "-"):
            d.do("sketch.circle", {"sketch": sk, "center": [sx + "xs", sy + "ys"], "radius": "dc / 2"})
    # The vent slots: an option, a cut-out sketch in the top's plane.
    # The slot's curves: line e3, arc e6, line e8, arc e10 (points e1, e2, e4, e5, e7, e9).
    d.do("sketch.create", {"plane": "xy", "offset": "zl", "name": "Vents"})
    d.do("sketch.path", slot("Vents", "ventX0", "ventH", "ventW / 2"))
    d.do("sketch.pattern", {"sketch": "Vents", "entities": ["e3", "e6", "e8", "e10"],
                            "count": "ventN", "step": ["ventP", "0 mm"]})
    d.do("feature.when", {"feature": "Vents", "expr": "vents == 1"})
    d.do("feature.sheetMetal", sheet(sk, "Lid", [
        {"edge": "e6", "length": "skirtL", "angle": "90 deg", "direction": "down"},  # 0 right skirt
        {"edge": "e8", "length": "skirtL", "angle": "90 deg", "direction": "down"},  # 1 left skirt
        {"edge": "e5", "length": "frontL", "angle": "90 deg", "direction": "down"},  # 2 front wall
        {"edge": "e7", "length": "frontL", "angle": "90 deg", "direction": "down"},  # 3 back wall
    ], [2, 3], [0, 1], ["Vents"]))


def main():
    d = Doc()
    d.do("table.set", {"name": "mats", "columns": ["material", "minR", "k", "v", "red", "green", "blue"],
                       "rows": MATERIALS})
    d.do("table.set", {"name": "screws", "columns": ["screw", {"name": "d", "unit": "mm"},
                                                     {"name": "clear", "unit": "mm"}, {"name": "head", "unit": "mm"},
                                                     {"name": "k", "unit": "mm"}], "rows": SCREWS})
    for name, expr in INPUTS + DERIVED:
        d.do("variable.set", {"name": name, "expr": expr})

    base(d)
    lid(d)

    # The screws, through the lid's holes and the return flanges' holes.
    d.do("feature.cylinder", {"name": "Shank", "radius": "d / 2", "height": "shankL",
                              "position": ["xs", "ys", "zl + t - shankL"]})
    d.do("feature.pattern", {"name": "Shanks2", "source": "Shank", "count": "2", "step": ["-2 * xs", "0 mm", "0 mm"]})
    d.do("feature.pattern", {"name": "Screws", "source": "Shanks2", "count": "2", "step": ["0 mm", "-2 * ys", "0 mm"]})
    d.do("feature.cylinder", {"name": "Head", "radius": "headD / 2", "height": "headK",
                              "position": ["xs", "ys", "zl + t"]})
    d.do("feature.pattern", {"name": "Heads2", "source": "Head", "count": "2", "step": ["-2 * xs", "0 mm", "0 mm"]})
    d.do("feature.pattern", {"name": "Heads", "source": "Heads2", "count": "2", "step": ["0 mm", "-2 * ys", "0 mm"]})

    # Appearance: the parts in the material's colour, the screws brass.
    colour = ["mats[material].red", "mats[material].green", "mats[material].blue"]
    for body in ("Base", "Lid"):
        d.do("body.appearance", {"body": body, "color": colour, "roughness": 0.5, "metallic": 0.3})
    for body in ("Screws", "Heads"):
        d.do("body.appearance", {"body": body, "color": "#B8954A", "roughness": 0.35, "metallic": 0.8})

    asserts(d)
    publish(d)
    d.do("document.info", {
        "title": "Sheet-metal enclosure",
        "description": "A two-part sheet-metal case for electronics, each part laser cut and bent on a press brake "
                       "from one sheet: a base (floor, side walls with return flanges, front and back lips) and a "
                       "lid (top, side skirts, front and back walls) screwed onto the return flanges. Set the inside "
                       "size, the material (steel DC01, aluminium 5754, stainless 304) and thickness, the bend "
                       "radius, M3 or M4 screws, vent slots and feet holes, how the corners are closed (open, butt, "
                       "overlap or miter, and the gap) and the corner reliefs' shape; the bend radius, flange "
                       "lengths, hole distances, corner reliefs and gaps, the lid's fit and the screws' alignment "
                       "are checked against the material's table. Every hole is in the flat patterns, with the "
                       "bend lines: file.export with sheetMetal (see README).",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/" + ID,
        "tags": ["sheet metal", "enclosure", "electronics", "press brake", "laser cutting", "flat pattern"]})
    d.do("jig.export", {"path": "dist/%s.3dcraftjig" % ID})
    return d


def faces(where):
    return {"kind": "face", "where": where}


def box(x, y, rx, ry, z0, z1):
    return {"inside": [["(%s) - (%s)" % (x, rx), "(%s) - (%s)" % (y, ry), z0],
                       ["(%s) + (%s)" % (x, rx), "(%s) + (%s)" % (y, ry), z1]]}


def four(x, y, rx, ry, z0, z1):
    return [box(sx + x, sy + y, rx, ry, z0, z1) for sx in ("", "-") for sy in ("", "-")]


def asserts(d):
    A = lambda **kw: d.do("assert.add", kw)
    BASE, LID = {"madeBy": "Base"}, {"madeBy": "Lid"}
    A(name="Two parts and the screws", measure="count", of={"kind": "body"}, eq="4")
    # The material table's rules, by the sheet-metal measures on both parts.
    A(name="Bend radius at least the material's minimum", measure="bendRadius", min="mats[material].minR * t * 0.999")
    A(name="Ten bends", measure="count",
      of=faces([{"any": [BASE, LID]}, {"surface": "cylinder"}, {"hole": False},
                {"not": {"axis": {"along": "z"}}}, {"radius": {"max": "R * 1.001"}}]), eq="10")
    A(name="Flanges at least the minimum flange (0.7 V, to the mould line)", measure="flangeLength",
      measured="mould", min="minFlange")
    A(name="Holes and vents at least 2.5 t + R from a bend", measure="holeToBend", min="holeEdge")
    A(name="Every corner of two bends relieved", measure="relief", **{"is": True})
    # The closed corners' gap, measured on the solid. Through an output, so that with every corner
    # open (nothing to measure) the assertion is not proven rather than broken (repro-sheet-metal-enclosure-7).
    d.do("variable.measure", {"name": "cornerGapMeasured", "measure": "cornerGap"})
    A(name="Closed corners: the gap as given", measure="value",
      expr="if(corner == 1, gap, cornerGapMeasured)", eq="gap", tol="0.001 mm")
    # The lid fits over the base with the clearance, and nothing overlaps.
    d.do("assert.add", {"name": "Lid skirts clear the base walls", "measure": "distance",
                        "from": faces([LID, {"any": [{"name": "*copy(1)/*face(2)"}, {"name": "*copy(1)/*face(4)"}]}]),
                        "to": faces([BASE, {"any": [{"name": "*copy(1)/*face(2)"}, {"name": "*copy(1)/*face(4)"}]}]),
                        "eq": "fit", "tol": "0.01 mm"})
    d.do("assert.add", {"name": "Lid walls clear the base lips", "measure": "distance",
                        "from": faces([LID, {"any": [{"name": "*copy(1)/*face(6)"}, {"name": "*copy(1)/*face(8)"}]}]),
                        "to": faces([BASE, {"any": [{"name": "*copy(1)/*face(6)"}, {"name": "*copy(1)/*face(8)"}]}]),
                        "eq": "fit", "tol": "0.01 mm"})
    d.do("assert.add", {"name": "Nothing overlaps", "measure": "overlap", "is": False})
    # The screws pass both holes with the clearance all round: the holes' axes line up, so the
    # return flanges' holes drawn in the flat land under the lid's once bent.
    for nm, part in (("lid", "Lid"), ("base", "Base")):
        d.do("assert.add", {"name": "Screws centred in the %s's holes" % nm, "measure": "clearance",
                            "from": "Screws", "to": part, "eq": "(dc - d) / 2", "tol": "0.01 mm"})
    drills = four("xs", "ys", "dc", "dc", "zl - t - 1 mm", "zl + 1 mm")
    d.do("assert.add", {"name": "Four holes in the return flanges", "measure": "count",
                        "of": faces([BASE, {"surface": "cylinder"}, {"axis": {"along": "z"}},
                                     {"radius": {"eq": "dc / 2", "tol": "0.001 mm"}}, {"any": drills}]), "eq": "4"})
    feet = four("footX", "footY", "dc", "dc", "-1 mm", "t + 1 mm")
    d.do("assert.add", {"name": "Feet holes in the floor when asked", "measure": "count",
                        "of": faces([BASE, {"surface": "cylinder"}, {"axis": {"along": "z"}},
                                     {"radius": {"eq": "dc / 2", "tol": "0.001 mm"}}, {"any": feet}]),
                        "eq": "if(feet == 1, 4, 0)"})
    # The lid rests on the return flanges.
    d.do("assert.add", {"name": "Lid rests on the return flanges", "measure": "distance",
                        "from": faces([LID, {"name": "*copy(1)/*face(0)"}]),
                        "to": faces([BASE, {"any": [{"name": "*copy(1)/*face(10)"}, {"name": "*copy(1)/*face(12)"}]}]),
                        "eq": "0 mm", "tol": "0.01 mm"})


PUB = [
    ("Wi", dict(label="Inside width", description="Between the base's side walls", group="Size", order=1,
                min="100 mm", max="400 mm", step="1 mm", unit="mm")),
    ("Di", dict(label="Inside depth", description="Between the base's front and back lips (at least room for the "
                "screws at the front and the back, with 2 mm between their heads)", group="Size", order=2,
                min="max(80 mm, 2 * (R + relief + max(8 mm, holeEdge + dc)) + headD + 2 mm)", max="300 mm", step="1 mm", unit="mm")),
    ("Hi", dict(label="Inside height", description="From the floor to the underside of the lid", group="Size", order=3,
                min="30 mm", max="200 mm", step="1 mm", unit="mm")),
    ("material", dict(label="Material", description="Sets the minimum bend radius, the K-factor and the die (minimum flange)",
                      group="Sheet", order=1, kind="choice", choicesFrom="mats")),
    ("t", dict(label="Thickness", description="Sheet thickness", group="Sheet", order=2,
               min="0.8 mm", max="2 mm", step="0.1 mm", unit="mm")),
    ("radiusExtra", dict(label="Extra bend radius", description="Inner bend radius above the material's minimum, "
                         "in thicknesses: 0 is the table's minimum radius, 1 adds one thickness",
                         group="Sheet", order=3, min="0", max="2", step="0.1")),
    ("corner", dict(label="Corners", description="How the walls meet at the corners: open (each flange ends at its "
                    "bend), butt, overlap (the base's walls cover the lips' ends, the lid's front and back walls "
                    "the skirts') or miter", group="Corners", order=1, kind="choice", choices=CORNERS)),
    ("gap", dict(label="Corner gap", description="The gap left at a closed corner (a butt's is less than the "
                 "thickness)", group="Corners", order=2, min="0.1 mm", max="if(corner == 2, t - 0.1 mm, 2 mm)",
                 step="0.1 mm", unit="mm")),
    ("reliefShape", dict(label="Corner relief", description="The relief cut at each corner of the flat pattern, "
                         "R + t + 0.5 mm along each edge", group="Corners", order=3, kind="choice",
                         choices=RELIEFS)),
    ("screw", dict(label="Screws", description="Lid screws, with clearance holes in the lid and the return flanges",
                   group="Fit", order=1, kind="choice", choicesFrom="screws")),
    ("fit", dict(label="Lid clearance", description="Gap between the lid's skirts and walls and the base",
                 group="Fit", order=2, min="0.2 mm", max="1 mm", step="0.1 mm", unit="mm")),
    ("vents", dict(label="Vent slots", description="A row of slots in the lid", group="Options", order=1, kind="boolean")),
    ("feet", dict(label="Feet holes", description="Four holes in the floor's corners, for feet or standoffs",
                  group="Options", order=2, kind="boolean")),
]


def publish(d):
    for name, fields in PUB:
        p = {"name": name}
        p.update(fields)
        d.do("variable.publish", p)


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main().steps) + "\n]")
