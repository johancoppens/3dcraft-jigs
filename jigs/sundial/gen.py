#!/usr/bin/env python3
"""Writes build.json for the sundial Jig (python3 -I gen.py > build.json).

A plane sundial for one place: a horizontal garden dial, or a vertical wall dial
that may decline (face away from due south). A dial plate with the hour lines,
half-hour ticks and Roman numerals engraved (or cut through), and a gnomon plate
whose sloping edge, the style, lies along the Earth's axis. The gnomon stands in
slots in the dial on two tabs, so it is set at exactly the right angle.

Frame: the dial plate lies in the xy plane, its face (the side with the lines) at
z = T, its back at z = 0. x is u, y is v of the dial: on a horizontal dial u
points east and v north; on a wall dial, seen from in front, u points right and
v up (the wall dial is shown lying on its back, its face up).

Two ways to the same lines (see README):
- the build uses the textbook construction (Waugh, Rohr): every plane dial is a
  horizontal dial for another latitude, the style height SH, turned by the
  substyle angle SD and with the hour angle counted from the substyle's own
  hour angle H0 (the "difference in longitude");
- the assertions check the built geometry against an independent vector
  construction: the shadow of the polar axis cast by the sun (equinox
  direction at hour angle H) on the plane of the dial.

The Python here only writes the commands; every number the model depends on is
an expression of the published parameters, worked out by 3DCraft.
"""
import json

JIG = "sundial"
HOURS = list(range(2, 23))          # clock hours that may get a line (24 h clock)

# Places: name, latitude (deg, north positive), longitude (deg, east positive),
# meridian of the standard time zone (deg; CET 15 E, GMT 0, EST 75 W, JST 135 E ...).
PLACES = [
    ("Custom (latitude and longitude below)", 0, 0, 0),
    ("Brussel", 50.85, 4.35, 15),
    ("Gent", 51.05, 3.72, 15),
    ("Antwerpen", 51.22, 4.40, 15),
    ("Leuven", 50.88, 4.70, 15),
    ("Brugge", 51.21, 3.22, 15),
    ("Liege", 50.63, 5.57, 15),
    ("Hasselt", 50.93, 5.34, 15),
    ("Amsterdam", 52.37, 4.90, 15),
    ("Rotterdam", 51.92, 4.48, 15),
    ("Utrecht", 52.09, 5.12, 15),
    ("Groningen", 53.22, 6.57, 15),
    ("Maastricht", 50.85, 5.69, 15),
    ("Luxembourg", 49.61, 6.13, 15),
    ("Paris", 48.86, 2.35, 15),
    ("London", 51.51, -0.13, 0),
    ("Berlin", 52.52, 13.40, 15),
    ("Madrid", 40.42, -3.70, 15),
    ("Rome", 41.90, 12.50, 15),
    ("Stockholm", 59.33, 18.07, 15),
    ("Reykjavik", 64.15, -21.94, 0),
    ("New York", 40.71, -74.01, -75),
    ("San Francisco", 37.77, -122.42, -120),
    ("Tokyo", 35.68, 139.69, 135),
]
DEFAULT_PLACE = 3                   # Gent (row 3, counted from 1)

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IIII", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX",
         10: "X", 11: "XI", 12: "XII"}
# Glyphs in units of the numeral height (x right, y up, centred on y = 0): outline and width.
ST = 0.16                           # stroke width
GAP = 0.11


def glyph(ch):
    h = 0.5
    if ch == "I":
        w = ST
        return w, [(-w / 2, -h), (w / 2, -h), (w / 2, h), (-w / 2, h)]
    if ch == "V":
        w = 0.62
        t = (w / 2 - ST) / (w / 2 - ST / 2)
        yi = h - 2 * h * t
        return w, [(-w / 2, h), (-w / 2 + ST, h), (0, yi), (w / 2 - ST, h), (w / 2, h),
                   (ST / 2, -h), (-ST / 2, -h)]
    if ch == "X":
        w = 0.62
        t = (w / 2 - ST) / (w - ST)
        yn = h - 2 * h * t
        xn = ST / 2
        return w, [(-w / 2, h), (-w / 2 + ST, h), (0, yn), (w / 2 - ST, h), (w / 2, h), (xn, 0),
                   (w / 2, -h), (w / 2 - ST, -h), (0, -yn), (-w / 2 + ST, -h), (-w / 2, -h), (-xn, 0)]
    raise ValueError(ch)


def numeral_polys(m):
    """Polygons of the Roman numeral m in numeral-height units, centred on (0, 0)."""
    glyphs = [glyph(c) for c in ROMAN[m]]
    total = sum(w for w, _ in glyphs) + GAP * (len(glyphs) - 1)
    x = -total / 2
    polys = []
    for w, pts in glyphs:
        cx = x + w / 2
        polys.append([(cx + px, py) for px, py in pts])
        x += w + GAP
    return polys


def num(v):
    v = round(v, 9)
    if abs(v) < 1e-12:
        return "0"
    return repr(v) if v >= 0 else "(%r)" % v


steps = []


def cmd(c, **p):
    steps.append([c, p])


def var(name, expr):
    cmd("variable.set", name=name, expr=expr)


def ray_to_boundary(prefix, ox, oy, du, dv, bc, bs):
    """Variables: the distance from (ox, oy) along the unit direction (du, dv) to the
    plate's edge shrunk by an inset: a circle of radius bc (horizontal dial) or a
    square of half side bs (wall dial). Returns the variable's name."""
    var(prefix + "b", "%s * %s + %s * %s" % (ox, du, oy, dv))
    var(prefix + "c", "%s^2 + %s^2 - %s^2" % (ox, oy, bc))
    var(prefix + "tx", "if(%s > 1e-9, (%s - %s) / %s, if(%s < -1e-9, (-%s - %s) / %s, 1000000 mm))"
        % (du, bs, ox, du, du, bs, ox, du))
    var(prefix + "ty", "if(%s > 1e-9, (%s - %s) / %s, if(%s < -1e-9, (-%s - %s) / %s, 1000000 mm))"
        % (dv, bs, oy, dv, dv, bs, oy, dv))
    var(prefix + "t", "if(vert, min(%stx, %sty), -%sb + sqrt(max(%sb^2 - %sc, 0 mm^2)))"
        % (prefix, prefix, prefix, prefix, prefix))
    return prefix + "t"


class Sketch:
    """A sketch of closed polylines; predicts entity ids (points first, then the lines,
    per polyline) so the faces they make can be named."""

    def __init__(self, name, offset):
        self.name, self.n, self.curves = name, 0, []
        cmd("sketch.create", name=name, plane="xy", offset=offset)

    def poly(self, pts):
        k = len(pts)
        cmd("sketch.polyline", sketch=self.name, points=pts, closed=True)
        lines = ["e%d" % (self.n + k + i + 1) for i in range(k)]
        self.n += 2 * k
        self.curves.append(lines)


def cut(sk, tool, boolean, when, target, p):
    """Extrudes sketch sk (drawn along +x from the origin: x along line p, y to its left) down
    through the top layer into a tool, turns it onto line p's direction about its origin,
    and subtracts it from target. (3DCraft at 3faaaea0 refuses a few thin slanted rectangles
    as loops that cross themselves; drawn square to the axes and turned as a solid they build.)"""
    cmd("feature.extrude", sketch=sk.name, distance="-(1 mm + dTop)", name=tool, when=when)
    cmd("feature.transform", source=tool, angle="atan2(%sdv, %sdu)" % (p, p), axis=[0, 0, 1],
        translate=["%sox" % p, "%soy" % p, "0 mm"], name=tool + "Placed", when=when)
    cmd("feature.boolean", op="subtract", target=target, tool=tool + "Placed", name=boolean, when=when)
    return boolean


DIAL_COLOUR = "#B8954A"     # brass
LINE_COLOUR = "#7A5638"     # walnut
GNOMON_COLOUR = "#7A5638"   # walnut


def main():
    table_rows = [[n, la, lo, z] for n, la, lo, z in PLACES]
    cmd("table.set", name="places",
        columns=["place", {"name": "lat", "unit": "deg"}, {"name": "lon", "unit": "deg"},
                 {"name": "zone", "unit": "deg"}], rows=table_rows)

    inputs = [
        ("type", "1"),                # 1 horizontal (garden), 2 vertical (wall)
        ("place", str(DEFAULT_PLACE)),
        ("latIn", "51.05 deg"),
        ("lonIn", "3.72 deg"),
        ("zoneIn", "15 deg"),
        ("decl", "0 deg"),            # wall: how far it faces away from due south, west positive
        ("timeMode", "1"),            # 1 clock time of the zone, 2 local solar time
        ("size", "200 mm"),
        ("thick", "4 mm"),
        ("through", "0"),
        ("depth", "1 mm"),
        ("numerals", "1"),
        ("clearance", "0.15 mm"),
    ]
    for n, e in inputs:
        var(n, e)

    derived = [
        ("lat", "if(place == 1, latIn, places[place].lat)"),
        ("lon", "if(place == 1, lonIn, places[place].lon)"),
        ("zone", "if(place == 1, zoneIn, places[place].zone)"),
        ("vert", "type == 2"),
        ("D", "if(vert, decl, 0 deg)"),
        # Longitude correction: the sun is due south at clock noon on the zone's meridian;
        # every degree east of it, 4 minutes earlier.
        ("dlon", "if(timeMode == 1, lon - zone, 0 deg)"),
        ("lonCorrMin", "dlon / 1 deg * 4"),
        # Textbook construction (Waugh; Rohr): style height SH, substyle
        # angle SD from the noon line (vertical: from the downward vertical), the substyle's
        # hour angle H0.
        ("SH", "if(vert, asin(cos(lat) * cos(D)), lat)"),
        ("sinSH", "sin(SH)"),
        ("tanSH", "tan(SH)"),
        ("SD", "if(vert, atan(sin(D) / tan(lat)), 0 deg)"),
        ("H0", "if(vert, atan(tan(D) / sin(lat)), 0 deg)"),
        ("su", "if(vert, sin(SD), 0)"),              # substyle direction on the dial
        ("sv", "if(vert, -cos(SD), 1)"),
        ("sg", "if(vert, -1, 1)"),                   # the style points to the north (1) or south (-1) celestial pole
        ("nu", "sg * sv"),                           # across the substyle, towards the afternoon
        ("nv", "-sg * su"),
        # Hour lines exist for the hours the sun can shine on the dial: up at midsummer
        # (sunrise hour angle acos(-tan(lat) tan(23.44 deg))) and, on a wall, in front of it.
        ("Hlim", "min(acos(-tan(lat) * tan(23.44 deg)), 125 deg)"),
        # Sizes.
        ("T", "thick"),
        ("Rh", "size / 2"),
        ("rim", "0.035 * size"),
        ("w", "clamp(0.006 * size, 0.8 mm, 2 mm)"),
        # Engraved, the plate is two bodies: a dark base and a brass face as deep as the
        # engraving, so the floor of every cut shows dark (and it prints in two colours).
        # Cut through: the face is the whole plate.
        ("dTop", "if(through, T, min(depth, T / 2))"),
        ("kR", "if(vert, 0.7, 0.25)"),
        ("xR", "-kR * Rh * su"),                     # the root: where the style meets the dial
        ("yR", "-kR * Rh * sv"),
        # Numerals: as large as the narrowest gap between hour lines allows (near the substyle,
        # 15 deg x sin(SH) apart), at most 6 % of the dial.
        ("hN", "min(0.06 * size, 0.6 * Rh * 0.2618 * sinSH / 1.25)"),
        ("numOn", "numerals && hN >= 3.5 mm"),
        ("nf", "if(vert, -1, 1)"),                   # numerals' tops point out (garden) or to the root (wall)
        ("Bc", "Rh - rim - 0.9 * hN"),                # numeral centres stay inside this circle ...
        ("Bs", "Rh - rim - 0.9 * hN"),                # ... or square
        # Lines start r1 from the root, where neighbours are 2 line widths apart.
        ("r1", "max(0.08 * size, 2 * w / (0.2618 * sinSH))"),
        # Gnomon: run Ls along the substyle from the root, style height SH, two tabs.
        ("Bg", "Rh - rim"),
        ("gap", "1 mm"),                             # least distance from a cut to a slot
    ]
    for n, e in derived:
        var(n, e)
    tS = ray_to_boundary("gS", "xR", "yR", "su", "sv", "Bg", "Bg")
    for n, e in [
        ("Ls", "0.72 * %s" % tS),
        ("hG", "Ls * tanSH"),
        ("tl", "clamp(0.2 * Ls, 6 mm, 30 mm)"),
        ("ta1", "0.3 * Ls"),
        ("ta2", "0.75 * Ls"),
        ("gAng", "atan2(-su, sv)"),
        ("slotL", "tl + clearance"),
        ("slotW", "T + clearance"),
    ]:
        var(n, e)

    # Independent check: the polar axis G, the dial's normal N and its axes Eu, Ev in the
    # world frame (x east, y north, z up), the shadow of G on the dial for the sun at hour
    # angle H, S = (-sin H, -cos H sin(lat), cos H cos(lat)): L = (S.N) G - (G.N) S.
    for n, e in [
        ("cNx", "if(vert, -sin(D), 0)"), ("cNy", "if(vert, -cos(D), 0)"), ("cNz", "if(vert, 0, 1)"),
        ("cGy", "if(vert, -cos(lat), cos(lat))"), ("cGz", "if(vert, -sin(lat), sin(lat))"),
        ("cEux", "if(vert, cos(D), 1)"), ("cEuy", "if(vert, -sin(D), 0)"),
        ("cEvy", "if(vert, 0, 1)"), ("cEvz", "if(vert, 1, 0)"),
        ("cGN", "cGy * cNy + cGz * cNz"),
        ("cGu", "cGy * cEuy"),
        ("cGv", "cGy * cEvy + cGz * cEvz"),
        ("cGp", "sqrt(cGu^2 + cGv^2)"),
        ("cSu", "cGu / cGp"), ("cSv", "cGv / cGp"),
        ("cTan", "cGN / cGp"),                       # tan of the angle between the style and the dial
        ("cSg", "if(cGz > 0, 1, -1)"),
        ("cNu", "cSg * cSv"), ("cNv", "-cSg * cSu"),
        ("slack", "0.02 mm"),
    ]:
        var(n, e)

    # Dial plate: a disc (horizontal) or a square (wall), with the two slots for the gnomon's tabs.
    def layer(name, z0, height, cond, colour, **look):
        for shape, c in (("Disc", "!vert"), ("Square", "vert")):
            sk = name + shape + "Sketch"
            cmd("sketch.create", name=sk, plane="xy", offset=z0)
            if shape == "Disc":
                cmd("sketch.circle", sketch=sk, center=[0, 0], radius="Rh")
            else:
                cmd("sketch.polyline", sketch=sk, points=[["-Rh", "-Rh"], ["Rh", "-Rh"], ["Rh", "Rh"], ["-Rh", "Rh"]],
                    closed=True)
            full = "(%s) && (%s)" % (c, cond)
            cmd("feature.when", feature=sk, expr=full)
            cmd("feature.extrude", sketch=sk, distance=height, name=name + shape, when=full)
        cmd("feature.boolean", op="union", target=name + "Disc", tool=name + "Square", name=name)
        cmd("body.appearance", body=name, color=colour, **look)

    layer("Base", "0 mm", "T - dTop", "!through", LINE_COLOUR, roughness=0.7)
    layer("Top", "T - dTop", "dTop", "1", DIAL_COLOUR, metallic=0.6, roughness=0.45)
    target = "Top"

    def hour(k):
        return "h%02d" % k if float(k).is_integer() else "h%02dh" % int(k)

    # One variable set per line: hour angle, direction (textbook), the side of the gnomon it
    # starts from, its length, and the independent check of where it lies.
    def line_vars(k, check, p=None, H=None, side=None, cside=None):
        p = p or hour(k)
        var(p + "H", H or "15 deg * (%s - 12) + dlon" % num(k))
        var(p + "c", "cos(%sH - H0)" % p)
        var(p + "s", "sinSH * sin(%sH - H0)" % p)
        var(p + "n", "sqrt(%sc^2 + %ss^2)" % (p, p))
        var(p + "du", "(%sc * su + %ss * nu) / %sn" % (p, p, p))
        var(p + "dv", "(%sc * sv + %ss * nv) / %sn" % (p, p, p))
        var(p + "side", side or "if(sin(%sH - H0) >= 0, 1, -1)" % p)
        var(p + "ox", "xR + %sside * T / 2 * nu" % p)
        var(p + "oy", "yR + %sside * T / 2 * nv" % p)
        tB = ray_to_boundary(p + "B", p + "ox", p + "oy", p + "du", p + "dv", "Bc", "Bs")
        # Keep clear of the gnomon's slots: a line that is not yet `gap` beside them (rC) when
        # it reaches them (rA) starts beyond their far end (rB).
        var(p + "ds", "%sdu * su + %sdv * sv" % (p, p))
        var(p + "dn", "%sside * (%sdu * nu + %sdv * nv)" % (p, p, p))
        var(p + "rA", "if(%sds > 1e-9, (ta1 - slotL / 2 - gap) / %sds, 1000000 mm)" % (p, p))
        var(p + "rB", "if(%sds > 1e-9, (ta2 + slotL / 2 + gap) / %sds, 0 mm)" % (p, p))
        var(p + "rC", "if(%sdn > 1e-9, (w / 2 + clearance / 2 + gap) / %sdn, 1000000 mm)" % (p, p))
        var(p + "rS", "if(%srC > max(%srA, r1), max(r1, %srB), r1)" % (p, p, p))
        var(p + "tE", "max(%s - 0.85 * hN, %srS + 2 mm)" % (tB, p))
        var(p + "on", "abs(%sH) <= Hlim && (!vert || abs(%sH - H0) <= 90.000001 deg) && "
            "%s - 0.85 * hN >= max(r1 + 0.1 * size, %srS + 0.05 * size)" % (p, p, tB, p))
        if not check:
            return p
        # Independent: the shadow of the polar axis, in dial coordinates.
        var(p + "Sx", "-sin(%sH)" % p)
        var(p + "Sy", "-cos(%sH) * sin(lat)" % p)
        var(p + "Sz", "cos(%sH) * cos(lat)" % p)
        var(p + "SN", "%sSx * cNx + %sSy * cNy + %sSz * cNz" % (p, p, p))
        var(p + "Su", "%sSx * cEux + %sSy * cEuy" % (p, p))
        var(p + "Sv", "%sSy * cEvy + %sSz * cEvz" % (p, p))
        var(p + "Lu", "%sSN * cGu - cGN * %sSu" % (p, p))
        var(p + "Lv", "%sSN * cGv - cGN * %sSv" % (p, p))
        var(p + "Ll", "sqrt(%sLu^2 + %sLv^2)" % (p, p))
        var(p + "cdu", "%sLu / %sLl" % (p, p))
        var(p + "cdv", "%sLv / %sLl" % (p, p))
        var(p + "cside", (cside or "if(%scdu * cNu + %scdv * cNv >= 0, 1, -1)") % (p, p))
        var(p + "cox", "xR + %scside * T / 2 * cNu" % p)
        var(p + "coy", "yR + %scside * T / 2 * cNv" % p)
        var(p + "x1", "%scox + %srS * %scdu" % (p, p, p))
        var(p + "x2", "%scox + %stE * %scdu" % (p, p, p))
        var(p + "y1", "%scoy + %srS * %scdv" % (p, p, p))
        var(p + "y2", "%scoy + %stE * %scdv" % (p, p, p))
        var(p + "mx", "w / 2 * abs(%scdv) + slack" % p)
        var(p + "my", "w / 2 * abs(%scdu) + slack" % p)
        return p

    def at(p, t, across):
        """In line p's own frame: t along it, `across` to its right."""
        return [t, "-(%s)" % across]

    lines = []
    for k in HOURS:
        p = line_vars(k, True)
        sk = Sketch("Line%02dSketch" % k, "T + 0.5 mm")
        sk.poly([at(p, "%srS" % p, "-w / 2"), at(p, "%stE" % p, "-w / 2"), at(p, "%stE" % p, "w / 2"),
                 at(p, "%srS" % p, "w / 2")])
        cond = "%son" % p
        cmd("feature.when", feature=sk.name, expr=cond)
        target = cut(sk, "Line%02dTool" % k, "Line%02d" % k, cond, target, p)
        lines.append(("Line%02d" % k, "hour line %d" % k, p))

    # When an hour falls exactly on the substyle (the 12 h line of a garden or south-wall dial
    # in solar time, or with the longitude on the zone's meridian), the shadow of a thick
    # gnomon's other edge falls along its other side: that line is drawn on both sides.
    var("noonQ", "(H0 - dlon) / (15 deg)")
    hTw = "15 deg * round(noonQ) + dlon"
    p = line_vars(None, True, p="hTw", H=hTw, side="-if(sin(%s - H0) >= 0, 1, -1)" % hTw,
                  cside="-if(%scdu * cNu + %scdv * cNv >= 0, 1, -1)")
    var("twinOn", "abs(noonQ - round(noonQ)) < 1e-9 && round(noonQ) >= -10 && round(noonQ) <= 10 && hTwon")
    sk = Sketch("LineTwinSketch", "T + 0.5 mm")
    sk.poly([at(p, "hTwrS", "-w / 2"), at(p, "hTwtE", "-w / 2"), at(p, "hTwtE", "w / 2"), at(p, "hTwrS", "w / 2")])
    cmd("feature.when", feature=sk.name, expr="twinOn")
    target = cut(sk, "LineTwinTool", "LineTwin", "twinOn", target, p)

    # Half-hour ticks: the outer part of a line, between two hours that both have lines.
    for k in HOURS[:-1]:
        p = line_vars(k + 0.5, False)
        sk = Sketch("Tick%02dSketch" % k, "T + 0.5 mm")
        t0 = "max(%stE - 0.6 * hN, %srS)" % (p, p)
        sk.poly([at(p, t0, "-w / 2"), at(p, "%stE" % p, "-w / 2"),
                 at(p, "%stE" % p, "w / 2"), at(p, t0, "w / 2")])
        cond = "%son && %son && %stE - %srS >= 0.3 * hN" % (hour(k), hour(k + 1), p, p)
        cmd("feature.when", feature=sk.name, expr=cond)
        target = cut(sk, "Tick%02dTool" % k, "Tick%02d" % k, cond, target, p)

    # Roman numerals beyond the end of each line, their tops pointing outwards.
    for k in HOURS:
        p = hour(k)
        m = (k - 1) % 12 + 1
        sk = Sketch("Num%02dSketch" % k, "T + 0.5 mm")
        c = "%stE + 0.85 * hN" % p
        for poly in numeral_polys(m):
            sk.poly([at(p, "%s + nf * %s * hN" % (c, num(y)), "nf * %s * hN" % num(x)) for x, y in poly])
        cond = "%son && numOn" % p
        cmd("feature.when", feature=sk.name, expr=cond)
        target = cut(sk, "Num%02dTool" % k, "Num%02d" % k, cond, target, p)

    # The gnomon's two slots, drawn along +y about the origin, turned onto the substyle and
    # moved to the root as the gnomon is, cut through both bodies of the plate.
    cmd("sketch.create", name="SlotSketch", plane="xy", offset="-1 mm")
    for ta in ("ta1", "ta2"):
        cmd("sketch.polyline", sketch="SlotSketch", closed=True, points=[
            ["-slotW / 2", "%s - slotL / 2" % ta], ["slotW / 2", "%s - slotL / 2" % ta],
            ["slotW / 2", "%s + slotL / 2" % ta], ["-slotW / 2", "%s + slotL / 2" % ta]])
    cmd("feature.extrude", sketch="SlotSketch", distance="T + 2 mm", name="SlotTool")
    cmd("feature.transform", source="SlotTool", angle="gAng", axis=[0, 0, 1], translate=["xR", "yR", "0 mm"],
        name="SlotPlaced")
    cmd("feature.boolean", op="subtract", target="Base", tool="SlotPlaced", keepTool=True, name="DialBase",
        when="!through")
    cmd("feature.boolean", op="subtract", target=target, tool="SlotPlaced", name="Dial")

    # Gnomon: drawn on the yz plane (sketch x = world y along the substyle, sketch y = z),
    # extruded T thick about x = 0, turned onto the substyle and moved to the root.
    gp = [["0 mm", "T"], ["Ls", "T + hG"], ["Ls", "T"],
          ["ta2 + tl / 2", "T"], ["ta2 + tl / 2", "0 mm"], ["ta2 - tl / 2", "0 mm"], ["ta2 - tl / 2", "T"],
          ["ta1 + tl / 2", "T"], ["ta1 + tl / 2", "0 mm"], ["ta1 - tl / 2", "0 mm"], ["ta1 - tl / 2", "T"]]
    cmd("sketch.create", name="GnomonSketch", plane="yz")
    cmd("sketch.polyline", sketch="GnomonSketch", points=gp, closed=True)
    cmd("feature.extrude", sketch="GnomonSketch", distance="T", symmetric=True, name="GnomonFlat")
    cmd("feature.transform", source="GnomonFlat", angle="gAng", axis=[0, 0, 1], translate=["xR", "yR", "0 mm"],
        name="Gnomon")
    cmd("body.appearance", body="GnomonFlat", color=GNOMON_COLOUR, roughness=0.6)

    # Assertions.
    A = []
    A.append(dict(name="style at the latitude angle: rise of the style",
                  measure="boxMax", of="Gnomon", axis="z", eq="T + Ls * cTan", tol="0.005 mm"))
    for ax, sgn, fn, perp in (("x", "Max", "max", "cSv"), ("x", "Min", "min", "cSv"),
                              ("y", "Max", "max", "cSu"), ("y", "Min", "min", "cSu")):
        o = "xR" if ax == "x" else "yR"
        s = "cSu" if ax == "x" else "cSv"
        pm = "+" if sgn == "Max" else "-"
        A.append(dict(name="gnomon on the substyle (the noon line of a horizontal dial): %s %s" % (sgn.lower(), ax),
                      measure="box" + sgn, of="Gnomon", axis=ax,
                      eq="%s + %s(0 mm, Ls * %s) %s T / 2 * abs(%s)" % (o, fn, s, pm, perp), tol="0.005 mm"))
    A.append(dict(name="the high end of the style lies on the polar axis, away from the root", measure="count",
                  of={"kind": "vertex", "where": {"all": [{"in": "Gnomon"}, {"inside": [
                      ["xR + Ls * cSu - T / 2 * abs(cSv) - 0.05 mm", "yR + Ls * cSv - T / 2 * abs(cSu) - 0.05 mm",
                       "T + Ls * cTan - 0.05 mm"],
                      ["xR + Ls * cSu + T / 2 * abs(cSv) + 0.05 mm", "yR + Ls * cSv + T / 2 * abs(cSu) + 0.05 mm",
                       "T + Ls * cTan + 0.05 mm"]]}]}}, eq="2"))
    A.append(dict(name="tabs reach through the dial", measure="boxMin", of="Gnomon", axis="z", eq="0 mm",
                  tol="0.005 mm"))
    A.append(dict(name="no parts overlap (the gnomon stands in its slots)", measure="overlap", **{"is": False}))
    A.append(dict(name="gnomon on the plate: north / top", measure="boxMax", of="Gnomon", axis="y",
                  max="if(vert, Rh, sqrt(Rh^2 - T^2 / 4))"))
    A.append(dict(name="gnomon on the plate: south / bottom", measure="boxMin", of="Gnomon", axis="y", min="-Rh"))
    A.append(dict(name="gnomon on the plate: east / right", measure="boxMax", of="Gnomon", axis="x", max="Rh"))
    A.append(dict(name="gnomon on the plate: west / left", measure="boxMin", of="Gnomon", axis="x", min="-Rh"))
    A.append(dict(name="the rim of the dial is whole", measure="extent", of="Dial", axis="x", eq="size",
                  tol="0.005 mm"))
    A.append(dict(name="the parts: dial (face and base when engraved) and gnomon", measure="count",
                  of={"kind": "body"}, eq="if(through, 2, 3)"))
    tools = ["%sTool" % n for n, _, _ in lines] + ["LineTwinTool"] + \
        ["Tick%02dTool" % k for k in HOURS[:-1]] + ["Num%02dTool" % k for k in HOURS]
    A.append(dict(name="no line, tick or numeral comes near the gnomon's slots", measure="distance",
                  **{"from": {"kind": "face", "where": {"all": [{"in": "Dial"}, {"madeBy": "SlotTool"}]}}},
                  to={"kind": "face", "where": {"all": [{"in": "Dial"},
                                                        {"any": [{"madeBy": t} for t in tools]}]}},
                  min="gap - 0.01 mm"))
    lines.append(("LineTwin", "noon line on the other side of the gnomon", "hTw"))
    for n, label, p in lines:
        box = [["min(%sx1, %sx2) - %smx" % (p, p, p), "min(%sy1, %sy2) - %smy" % (p, p, p), "-1 mm"],
               ["max(%sx1, %sx2) + %smx" % (p, p, p), "max(%sy1, %sy2) + %smy" % (p, p, p), "T + 1 mm"]]
        on = "twinOn" if p == "hTw" else "%son" % p
        A.append(dict(name="%s where the shadow of the polar axis falls" % label, measure="count",
                      of={"kind": "face", "where": {"all": [{"in": "Dial"}, {"madeBy": "%sTool" % n},
                                                            {"inside": box}]}},
                      eq="if(%s, 4, 0)" % on))
    for a in A:
        cmd("assert.add", **a)

    # Both sets show the dial from the front, with the same outline, so the two files line up.
    # Cut sheet: engraved, the front of the base (outline and slots); cut through, the dial's
    # face with every cut. Engraving: the dial's face, the openings of the cuts inside its
    # outline and slots.
    cmd("set.define", name="Cut sheet", kind="face", where={"any": [
        {"in": "DialBase", "normal": {"along": "z"}},
        {"in": "Dial", "normal": {"along": "z"}, "above": {"z": "if(through, T - 0.01 mm, 2 * T + 1 mm)"}},
        {"in": "Gnomon", "name": "*endCap*"},
    ]})
    cmd("set.define", name="Engraving", kind="face", where={"all": [
        {"in": "Dial"}, {"normal": {"along": "z"}}, {"above": {"z": "if(through, 2 * T + 1 mm, T - 0.01 mm)"}}]})


    pub = [
        ("type", dict(label="Dial", description="A horizontal garden dial, or a vertical dial for a wall (shown lying "
                      "on its back, face up)", group="Dial", order=1, kind="choice",
                      choices=["horizontal (garden)", "vertical (wall)"])),
        ("decl", dict(label="Wall declination", description="Wall dial only: how far the wall faces away from due "
                      "south, west positive (a wall facing south-west: 45 deg). Measure it with a compass and correct "
                      "for magnetic declination, or from the sun at solar noon", group="Dial", order=2,
                      min="-50 deg", max="50 deg", step="0.5 deg", unit="deg")),
        ("timeMode", dict(label="Time shown", description="Clock time of your time zone (the hour lines shifted by "
                          "the longitude correction; add an hour in summer time), or local solar time (noon along "
                          "the gnomon)", group="Dial", order=3, kind="choice",
                          choices=["clock time (standard time)", "local solar time"])),
        ("place", dict(label="Place", description="A place from the table sets latitude, longitude and the time "
                       "zone's meridian; Custom uses the three values below", group="Place", order=1, kind="choice",
                       choicesFrom="places")),
        ("latIn", dict(label="Latitude", description="Custom place: degrees north of the equator", group="Place",
                       order=2, min="25 deg", max="65 deg", step="0.01 deg", unit="deg")),
        ("zoneIn", dict(label="Time zone meridian", description="Custom place: the meridian of your standard time: "
                        "15 deg times the zone's hours from UTC (CET +1 h: 15 deg; GMT: 0; EST -5 h: -75 deg)",
                        group="Place", order=4, min="-180 deg", max="180 deg", step="7.5 deg", unit="deg")),
        ("lonIn", dict(label="Longitude", description="Custom place: degrees east of Greenwich (west negative), "
                       "within 30 deg of the zone's meridian", group="Place", order=3,
                       min="max(zoneIn - 30 deg, -180 deg)", max="min(zoneIn + 30 deg, 180 deg)", step="0.01 deg",
                       unit="deg")),
        ("size", dict(label="Dial size", description="Diameter of the disc, or side of the square wall plate",
                      group="Size", order=1, min="120 mm", max="400 mm", step="1 mm", unit="mm")),
        ("thick", dict(label="Plate thickness", description="Dial and gnomon are cut from the same sheet; the slots "
                       "follow it", group="Size", order=2, min="3 mm", max="10 mm", step="0.1 mm", unit="mm")),
        ("through", dict(label="Lines cut through", description="Off: lines, ticks and numerals are engraved "
                         "(shallow cuts); on: they are cut through the plate (a stencil dial)", group="Lines",
                         order=1, kind="boolean")),
        ("depth", dict(label="Engraving depth", description="Depth of engraved lines (at most half the plate)",
                       group="Lines", order=2, min="0.2 mm", max="3 mm", step="0.1 mm", unit="mm")),
        ("numerals", dict(label="Hour numerals", description="Roman numerals beyond the hour lines (left out where "
                          "the lines are too close for them)", group="Lines", order=3, kind="boolean")),
        ("clearance", dict(label="Slot clearance", description="Extra width and length of the gnomon's slots: 0 is "
                           "a press fit, 0.1 to 0.2 mm slides in", group="Size", order=3, min="0 mm", max="0.5 mm",
                           step="0.01 mm", unit="mm")),
    ]
    for name, fields in pub:
        p_ = {"name": name}
        p_.update(fields)
        cmd("variable.publish", **p_)

    cmd("document.info",
        title="Sundial for your place",
        description="A sundial that tells the time where you put it: a horizontal garden dial or a vertical wall dial "
                    "(also on a wall that does not face due south), for a place picked from the table or your own "
                    "latitude and longitude. The gnomon's style lies along the Earth's axis, at the latitude angle; "
                    "the hour lines follow the standard formulas and are shifted by the longitude correction so the "
                    "dial reads the clock time of your zone (add an hour in summer). Lines, half-hour ticks and Roman "
                    "numerals are engraved or cut through; the gnomon stands in slots on two tabs. Assertions check the "
                    "built dial against an independent construction: the style's angle, the gnomon on the substyle and "
                    "every hour line where the shadow of the polar axis falls. To cut it: File > Export..., DXF or SVG "
                    "with the face set \"Cut sheet\" (the set \"Engraving\" holds the engraved areas); STL or 3MF to "
                    "print.",
        author="3DCraft Jigs", licence="CC-BY-4.0",
        url="https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/%s" % JIG,
        tags=["sundial", "garden", "astronomy", "laser", "3D printing", "sheet", "formula", "table"])
    cmd("jig.export", path="dist/%s.3dcraftjig" % JIG)
    return steps


if __name__ == "__main__":
    main()
    print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
