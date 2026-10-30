#!/usr/bin/env python3
"""Writes build.json for the 19-inch rack panel Jig:  python3 gen.py > build.json

build.json is the source of truth; this script is how it was written. The rack numbers (EIA-310-D,
IEC 60297-3-100) and the sheet stock table come from scripts/racklib.py, shared with rack-cabinet, so a
panel from this Jig bolts onto the rails of a cabinet from that one (both check it with the same values).

The panel is a sheet-metal part (feature.sheetMetal): flat, or with its top and bottom edges bent back
between the rails as stiffening flanges. Its holes (the mounting slots or holes on the rail pattern,
handle holes and a row of connector cut-outs or a window) are holes of the base's sketch, so they are in
the flat pattern and holeToBend sees them. A hole of a sketch cannot be switched by a condition, so there
is one sketch and one part per combination of the options (flat or flanged, cut-out, handles, slots or
holes), each with its `when`; exactly one is on, and a chain of unions passes it on as the body Panel.

Frame: x across the panel (the rack's centre line at x = 0), z up (the panel from z = 0 to its height,
its lower U boundary at z = -0.4 mm), y back into the rack: the panel's back face at y = 0, against the
rails' front, its front face at y = -t, the flanges reaching back into y > 0. The sketches lie on the
zx plane (sketch axes u = z, v = x, normal +y), so a flange bent up turns back into the rack.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import racklib as rk  # noqa: E402

ID = "rack-panel"
MAX_U = 4
unit = rk.unit

CUTOUTS = ["None", "D-sub DE-9 (socket)", "XLR / Neutrik D", "Window"]
FIXINGS = ["Round holes", "Slots"]

INPUTS = [
    ("nU", "3"),
    ("flanged", "1"),
    ("fixing", "2"),          # 1 round holes, 2 slots
    ("handles", "1"),
    ("cutout", "3"),          # 1 none, 2 D-sub, 3 XLR, 4 window
    ("count", "8"),
    ("winW", "300 mm"),
    ("winH", "25 mm"),
]
DERIVED = [
    ("H", "nU * U - panelGap"),                 # the panel's height
    ("z0", "-panelGap / 2"),                    # its lower U boundary
    ("d", "R + t"),                             # flange notch: the bent flange's back flush with the edge
    ("a", "opening / 2 - 5 mm - d"),            # the flanges span -a..a, inside the rails
    ("flangeL", "max(15 mm, minFlange)"),       # flange beyond the bend
    ("rM", unit(rk.M6_CLEAR / 2)),              # mounting hole / slot end radius
    ("slotHalf", "(10 mm - 6.6 mm) / 2"),
    ("mHalf", "if(fixing == 2, slotHalf, 0 mm)"),
    ("rH", unit(rk.M4_CLEAR / 2)),              # handle screw holes
    ("hX", "holeX - %s" % unit(rk.HANDLE_IN)),  # handle holes' x
    ("edgeMin", "if(flanged, d + holeMin, 2 * t) + 1 mm"),   # least distance from an edge to a hole
    ("eh", "max(8 mm, edgeMin + rH)"),          # handle holes from the edges
    ("hc", "H - 2 * eh"),                       # handle hole centres
    ("xa", "if(handles, hX - rH - 6 mm, opening / 2 - 5 mm)"),   # cut-outs within -xa..xa
    # D-sub DE-9 front-mount cut-out for a female (socket) connector (Harting, CECC 75 301-802): 20.5 x 11.4 mm, sides at 10 deg,
    # 3.1 mm holes on 25 mm centres; pitch 33 mm (flange 30.8 mm).
    ("dsW", "20.5 mm"), ("dsH", "11.4 mm"), ("dsHole", "1.55 mm"), ("dsC", "12.5 mm"), ("dsP", "33 mm"),
    # Neutrik D series (XLR): 24 mm hole, two 3.2 mm holes 19 mm x 24 mm apart on a diagonal; flange
    # 26 x 31 mm, pitch 32 mm.
    ("xlR", "12 mm"), ("xlHole", "1.6 mm"), ("xlDx", "9.5 mm"), ("xlDz", "12 mm"), ("xlP", "32 mm"),
    ("pitch", "if(cutout == 2, dsP, xlP)"),
    ("cw", "if(cutout == 2, 2 * dsC + 2 * dsHole, 2 * xlR)"),     # a cut-out's width
    ("maxCount", "max(1, floor((2 * xa - cw) / pitch) + 1)"),
    ("n", "count"),
    ("cx0", "-(n - 1) * pitch / 2"),            # the first cut-out's x
    ("zc", "H / 2"),
]


def outline(flanged):
    """The base's outline in (u, v) = (z, x), counter-clockwise, and the indices of its flange lines.
    Flanged: a 45-degree notch d deep at each end of the flanges (their bend relief), so the flanges stop
    at x = -a .. a while the ears stay flat."""
    if not flanged:
        xz = [("-panelW / 2", "0 mm"), ("panelW / 2", "0 mm"), ("panelW / 2", "H"), ("-panelW / 2", "H")]
        flange_segments = []
    else:
        xz = [("-panelW / 2", "0 mm"), ("-a - d", "0 mm"), ("-a", "d"), ("a", "d"), ("a + d", "0 mm"),
              ("panelW / 2", "0 mm"), ("panelW / 2", "H"), ("a + d", "H"), ("a", "H - d"), ("-a", "H - d"),
              ("-a - d", "H"), ("-panelW / 2", "H")]
        flange_segments = [(2, 3), (8, 9)]           # point indices in xz order
    # (x, z) counter-clockwise is clockwise in (u, v) = (z, x): reverse it.
    m = len(xz)
    order = list(reversed(range(m)))
    pts = [[xz[i][1], xz[i][0]] for i in order]
    lines = []
    for (i, j) in flange_segments:
        # reversed, the segment i -> j runs from j to i: line k joins order[k] -> order[k + 1]
        for k in range(m):
            if order[k] == j and order[(k + 1) % m] == i:
                lines.append(k)
    return pts, lines


def panel_sketch(name, flanged, cut, handles, slots):
    sk = rk.Sketch(name, "zx", "-t", when=cond(flanged, cut, handles, slots))
    pts, fl = outline(flanged)
    lines = sk.polyline(pts)
    flanges = [lines[k] for k in fl]
    seeds = []
    # Mounting holes: the outer two holes of every U (6.35 and 38.1 mm above its boundary), both sides.
    for h in ("hole1", "hole3"):
        zc = "z0 + %s" % h
        if slots:
            seeds += sk.slot(zc, "-holeX", "slotHalf", "rM")
        else:
            seeds.append(sk.circle([zc, "-holeX"], "rM"))
    hseed = sk.circle(["zc - hc / 2", "-hX"], "rH") if handles else None
    cseed = []
    if cut == 2:      # D-sub: a trapezoid (wide at the top), two screw holes
        top, bot = "zc + dsH / 2", "zc - dsH / 2"
        wt, wb = "dsW / 2", "dsW / 2 - dsH * tan(10 deg)"
        cseed += sk.polyline([[bot, "cx0 - (%s)" % wb], [bot, "cx0 + (%s)" % wb],
                              [top, "cx0 + (%s)" % wt], [top, "cx0 - (%s)" % wt]][::-1])
        cseed.append(sk.circle(["zc", "cx0 - dsC"], "dsHole"))
        cseed.append(sk.circle(["zc", "cx0 + dsC"], "dsHole"))
    elif cut == 3:    # Neutrik D: the round hole and two screw holes on a diagonal
        cseed.append(sk.circle(["zc", "cx0"], "xlR"))
        cseed.append(sk.circle(["zc + xlDz", "cx0 - xlDx"], "xlHole"))
        cseed.append(sk.circle(["zc - xlDz", "cx0 + xlDx"], "xlHole"))
    elif cut == 4:    # a window
        sk.polyline([["zc - winH / 2", "-winW / 2"], ["zc + winH / 2", "-winW / 2"],
                     ["zc + winH / 2", "winW / 2"], ["zc - winH / 2", "winW / 2"]])
    sk.pattern(seeds, count="2", step=["0 mm", "2 * holeX"], count2="nU", step2=["U", "0 mm"])
    if hseed:
        sk.pattern([hseed], count="2", step=["hc", "0 mm"], count2="2", step2=["0 mm", "2 * hX"])
    if cseed:
        sk.pattern(cseed, count="n", step=["0 mm", "pitch"])
    return sk.cmds, flanges


def cond(flanged, cut, handles, slots):
    return "flanged == %d && cutout == %d && handles == %d && fixing == %d" % (flanged, cut, handles, 2 if slots else 1)


def variant_name(flanged, cut, handles, slots):
    return "Panel %s %s%s %s" % ("flanged" if flanged else "flat", ["none", "D-sub", "XLR", "window"][cut - 1],
                                 " handles" if handles else "", "slots" if slots else "holes")


def main():
    s = rk.stock_commands("1")
    s += rk.spec_variables()
    for name, expr in INPUTS + DERIVED:
        s.append(["variable.set", {"name": name, "expr": expr}])

    names = []
    for flanged in (1, 0):
        for cut in (3, 1, 2, 4):
            for handles in (1, 0):
                for slots in (True, False):
                    nm = variant_name(flanged, cut, handles, slots)
                    sk_name = "Sketch " + nm[6:]
                    cmds, flanges = panel_sketch(sk_name, flanged, cut, handles, slots)
                    s += cmds
                    s.append(["feature.sheetMetal", {
                        "sketch": sk_name, "name": nm, "thickness": "t", "radius": "R", "kFactor": "K",
                        "flanges": [{"edge": e, "length": "flangeL", "angle": "90 deg", "direction": "up"}
                                    for e in flanges],
                        "when": cond(flanged, cut, handles, slots)}])
                    names.append(nm)
    # One of them is on: a chain of unions passes it on as the body Panel.
    prev = names[0]
    for i, nm in enumerate(names[1:]):
        out = "Panel" if i == len(names) - 2 else "Panel union %d" % (i + 1)
        s.append(["feature.boolean", {"op": "union", "target": prev, "tool": nm, "name": out}])
        prev = out
    s.append(["body.appearance", {"body": "Panel", "color": ["if(stock <= 2, 185, 125)", "if(stock <= 2, 190, 133)",
                                                             "if(stock <= 2, 196, 140)"],
                                  "metallic": 0.8, "roughness": 0.45}])

    # Two rails of a rack (the spec's opening and the cabinet's sides), hidden: the panel must bolt
    # onto their front at y = 0 without reaching into them.
    for side, sx in (("left", "-1"), ("right", "1")):
        s.append(["feature.block", {"name": "Rail %s" % side,
                                    "size": ["cabInnerW / 2 - opening / 2", unit(rk.RAIL_DEPTH), "nU * U + 20 mm"],
                                    "position": ["if(%s < 0, -cabInnerW / 2, opening / 2)" % sx, "0 mm", "z0 - 10 mm"]}])
    s.append(["feature.visible", {"feature": ["Rail left", "Rail right"], "visible": False}])

    s.append(["set.define", {"name": "Cut sheet", "kind": "face", "where": {
        "in": "Panel", "surface": "plane", "normal": {"along": "-y"},
        "inside": [["-1000 mm", "if(flanged, 1000 mm, -t - 0.01 mm)", "-1000 mm"], ["1000 mm", "1000 mm", "1000 mm"]]}}])

    s += assertions()
    s += publish()
    s.append(["document.info", {
        "title": "19-inch rack panel",
        "description": "A 19-inch rack front panel (EIA-310-D / IEC 60297) of 1 to 4 U, cut and bent from aluminium or "
                       "steel sheet: flat, or with stiffening flanges bent back between the rails; M6 mounting slots "
                       "or holes on the rail pattern, handle holes, and a row of D-sub or XLR (Neutrik D) cut-outs "
                       "or a window. It bolts onto any 19-inch rack, and onto the rails of the rack-cabinet Jig, "
                       "whose sides it fits between. Flat: export the face set Cut sheet (DXF or SVG). Flanged: "
                       "the flat pattern with its bend lines is written by file.export with sheetMetal (see the "
                       "README).",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/" + ID,
        "tags": ["19-inch rack", "EIA-310", "rack panel", "sheet metal", "laser cutting", "audio", "electronics"]}])
    s.append(["jig.export", {"path": "dist/%s.3dcraftjig" % ID}])
    return s


def faces(where):
    return {"kind": "face", "where": where}


def box(lo, hi):
    return {"inside": [lo, hi]}


def assertions():
    a = []

    def add(name, measure, **kw):
        kw = {k.rstrip("_"): v for k, v in kw.items()}
        a.append(["assert.add", dict(name=name, measure=measure, **kw)])

    big = "1000 mm"
    slab = ("-t - 0.01 mm", "0.01 mm")      # the panel's base, front face to back face
    add("width: 19 in (482.6 mm, EIA-310)", "extent", of="Panel", axis="x", eq="panelW")
    add("height: n U - 0.8 mm (IEC 60297-3-100)", "extent", of="Panel", axis="z", eq="H")
    add("centred on its U boundaries (0.4 mm above the lower one)", "boxMin", of="Panel", axis="z", eq="z0 + panelGap / 2")
    add("its measured width leaves 4 mm to each side of a rack-cabinet (cabInnerW; the cabinet checks its sides with a reference panel)", "extent", of="Panel", axis="x",
        max="cabInnerW - 2 * sideClear")
    # A hole's wall is a face of the sheet's rim across the sheet: a round hole's wall is one cylinder
    # (axis along y), a slot's two half-cylinders and two planes, a D-sub's or a window's sides planes
    # whose normal is square to y. The bends are cylinders too, but along x, so a hole wall is a cylinder
    # along y. The holes are counted in boxes where they belong: every place the spec gives has its hole,
    # exactly (a round hole's one cylinder, a slot's two half-cylinders and two planes), and no hole lies
    # anywhere else.
    interior = [["-panelW / 2 + 0.01 mm", slab[0], "0.01 mm"], ["panelW / 2 - 0.01 mm", slab[1], "H - 0.01 mm"]]
    hole_wall = {"in": "Panel", "surface": "cylinder", "axis": {"along": "y"}}
    walls = {"all": [{"in": "Panel", "inside": interior},
                     {"any": [{"surface": "cylinder", "axis": {"along": "y"}},
                              {"surface": "plane", "normal": {"perpendicular": "y"}}]}]}
    opening_zone = box(["-opening / 2", slab[0], "-" + big], ["opening / 2", slab[1], big])
    ears = [box(["%s * holeX - mHalf - rM - 0.01 mm" % sx, slab[0], "-" + big],
                ["%s * holeX + mHalf + rM + 0.01 mm" % sx, slab[1], big]) for sx in ("-1", "1")]
    boxes = []
    for k in range(MAX_U):
        for h, hval in (("hole1", rk.HOLES_IN_U[0]), ("hole3", rk.HOLES_IN_U[2])):
            zc = "z0 + %d * U + %s" % (k, h)
            for sx in ("-1", "1"):
                b = box(["%s * holeX - mHalf - rM - 0.01 mm" % sx, slab[0], "%s - rM - 0.01 mm" % zc],
                        ["%s * holeX + mHalf + rM + 0.01 mm" % sx, slab[1], "%s + rM + 0.01 mm" % zc])
                boxes.append(b)
                add("mounting hole at the EIA-310 place: U %d, %g mm, x = %s465.1 / 2 mm" % (k + 1, hval, "-" if sx == "-1" else "+"),
                    "count", of=faces({"all": [walls, b]}), eq="if(nU > %d, if(fixing == 2, 4, 1), 0)" % k)
    # No face at all (a hole's wall or anything else) lies inside the ears off the mounting holes' places.
    add("no hole in the ears off the EIA-310 pattern", "count",
        of=faces({"in": "Panel", "inside": interior, "any": ears, "not": {"any": boxes}}), eq="0")
    # Every hole wall (a face across the sheet, inside the outline) lies in the 450 mm opening between
    # the rails or in a mounting hole's place: cut-outs and handle holes stay inside the opening and clear
    # of the mounting holes (the two zones are 2.5 mm apart or more).
    add("cut-outs and handle holes inside the 450 mm opening, clear of the mounting holes", "count",
        of=faces({"all": [walls, {"not": {"any": [opening_zone] + ears}}]}), eq="0")
    cz = [["-xa - 0.01 mm", slab[0], "-" + big], ["xa + 0.01 mm", slab[1], big]]
    add("cut-outs: as many as asked, inside their zone (XLR 3 round holes, D-sub 2)", "count",
        of=faces(dict(hole_wall, inside=cz)), eq="if(cutout == 3, 3 * n, if(cutout == 2, 2 * n, 0))")
    add("cut-outs centred on the panel: XLR 24 mm holes, D-sub screw holes", "count",
        of=faces(dict(hole_wall, inside=[["-xa - 0.01 mm", slab[0], "zc - xlR - 0.01 mm"], ["xa + 0.01 mm", slab[1], "zc + xlR + 0.01 mm"]])),
        eq="if(cutout == 3, n, if(cutout == 2, 2 * n, 0))")
    add("window and D-sub sides: four each", "count",
        of=faces({"all": [walls, opening_zone, {"surface": "plane"}]}),
        eq="if(cutout == 4, 4, if(cutout == 2, 4 * n, 0))")
    for sx in ("-1", "1"):
        for dz in ("-", "+"):
            add("handle hole, 19.05 mm inboard of the mounting holes (%s, %s)" % ("left" if sx == "-1" else "right",
                                                                               "low" if dz == "-" else "high"), "count",
                of=faces(dict(hole_wall, inside=[["%s * hX - rH - 0.01 mm" % sx, slab[0], "zc %s hc / 2 - rH - 0.01 mm" % dz],
                                                 ["%s * hX + rH + 0.01 mm" % sx, slab[1], "zc %s hc / 2 + rH + 0.01 mm" % dz]])),
                eq="if(handles, 1, 0)")
    # The sheet-metal rules. bendRadius, flangeLength and holeToBend refuse a part that is switched off,
    # also when every part is meant (repro-rack-2), and the panel is one of 32 parts by its `when`: the
    # rules are measured on the geometry instead. The bends are the cylinders of the part along x (the
    # hole walls are along y): an inner skin of radius R and an outer one of R + t each; the flanges reach
    # back to R + flange beyond the back face.
    bend = {"in": "Panel", "surface": "cylinder", "axis": {"along": "x"}}
    add("bends: two, each an inner and an outer skin", "count", of=faces(bend), eq="if(flanged, 4, 0)")
    add("bends: two inner skins of radius R", "count",
        of=faces(dict(bend, radius={"eq": "R", "tol": "0.0001 mm"})), eq="if(flanged, 2, 0)")
    add("bend radius at least the stock's minimum", "count",
        of=faces(dict(bend, radius={"min": "minR - 0.0001 mm", "max": big})), eq="if(flanged, 4, 0)")
    add("flanges at least 4 t (stock) beyond the bend", "boxMax", of="Panel", axis="y",
        min="if(flanged, R + minFlange, 0 mm)", max="if(flanged, R + flangeL, 0 mm)")
    # Measured to the bends' skins; the rails' backs (40 mm behind the panel) stand in for them when
    # there are no bends, so the measure always has something to measure to.
    add("holes at least 2.5 t + r from a bend", "distance", from_=faces(walls),
        to=faces({"any": [bend,
                          {"in": "Rail left", "normal": {"along": "y"}}]}),
        min="if(flanged, holeMin, 0 mm)")
    # On a rack: against the rails' front, reaching into neither.
    add("bolts onto the rails without reaching into them", "clearance", from_="Panel", to=["Rail left", "Rail right"],
        min="0 mm", max="0 mm")
    return a


def publish():
    pub = [
        ("nU", dict(label="Height", description="Height in rack units of 44.45 mm (the panel is 0.8 mm less); "
                                                "a flanged panel with handles or cut-outs is at least 2 U",
                    group="Panel", order=1, kind="integer",
                    min="if(flanged && (handles || cutout > 1), 2, 1)", max=str(MAX_U))),
        ("stock", dict(label="Sheet", description="Material and thickness (bend radius and K-factor from the "
                                                  "stock table)", group="Panel", order=2, kind="choice",
                       choicesFrom="stocks")),
        ("flanged", dict(label="Flanges", description="Bend the top and bottom edges back between the rails, "
                                                      "for stiffness", group="Panel", order=3, kind="boolean")),
        ("fixing", dict(label="Mounting", description="6.6 mm holes for M6, or M6 slots (10 x 6.6 mm, for lateral play; "
                                                     "not offered in 3 mm aluminium)",
                        group="Panel", order=4, kind="choice", choices=FIXINGS, max="if(stock == 2, 1, 2)")),
        ("handles", dict(label="Handle holes", description="Two M4 holes each side for front handles, "
                                                           "19.05 mm inboard of the mounting holes",
                         group="Panel", order=5, kind="boolean")),
        ("cutout", dict(label="Cut-outs", description="A centred row of connector cut-outs, or a window",
                        group="Cut-outs", order=1, kind="choice", choices=CUTOUTS)),
        ("count", dict(label="Connectors", description="How many D-sub or XLR cut-outs (as many as fit, at most)",
                       group="Cut-outs", order=2, kind="integer", min="1", max="maxCount")),
        ("winW", dict(label="Window width", description="Width of the rectangular window",
                      group="Cut-outs", order=3, min="20 mm", max="2 * xa", step="1 mm", unit="mm")),
        ("winH", dict(label="Window height", description="Height of the window (it keeps clear of the bends)",
                      group="Cut-outs", order=4, min="10 mm", max="max(10 mm, H - 2 * edgeMin)", step="0.5 mm", unit="mm")),
    ]
    out = []
    for name, fields in pub:
        p = {"name": name}
        p.update(fields)
        out.append(["variable.publish", p])
    return out


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
