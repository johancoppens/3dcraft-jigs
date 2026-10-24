#!/usr/bin/env python3
"""Writes build.json for the flat-pack stool Jig (python3 gen.py > build.json).

A stool or side table cut from one sheet of plywood, joined without screws:
two legs that cross at the middle with a half-lap (cross-lap) joint, their tabs
through mortises in the seat. The seat is a square turned 45 degrees over the
legs (each leg runs from corner to corner), with rounded corners and a
hand-hold slot between two leg arms.

Every part is a sketch, offset by kerf / 2 (feature.offsetProfile) and
extruded: the bodies are the laser's or the router's cut paths, so the cut
sheet is right as exported. Slots and mortises are drawn a clearance wider
than the sheet so the parts slide together after the kerf is taken.

Axes: z up; the seat's top at z = height. Leg A lies along x, leg B along y.
"""
import json

INPUTS = [
    ("height", "450 mm"),
    ("seat", "340 mm"),
    ("thick", "18 mm"),
    ("kerf", "0 mm"),
    ("clearance", "0.2 mm"),
    ("style", "2"),          # 1 straight, 2 splayed, 3 waisted
    ("handhold", "1"),
]
DERIVED = [
    ("T", "thick"),
    ("hLeg", "height - T"),                          # top edge of the legs = underside of the seat
    ("cr", "clamp(0.12 * seat, 20 mm, 50 mm)"),      # seat corner radius
    ("half", "seat / sqrt(2)"),                      # centre to a sharp corner of the seat
    ("cc", "half - cr * sqrt(2)"),                   # centre to a corner's arc centre
    ("reach", "half - cr * (sqrt(2) - 1)"),          # centre to the rounded corner's tip
    ("tw", "2 * (reach - 30 mm)"),                   # width of a leg at the top
    ("splay", "choose(style, 0 mm, 0.14 * hLeg, 0 mm)"),
    ("bw", "tw + 2 * splay"),                        # width of a leg at the floor
    ("waist", "0.08 * tw"),                          # how far a waisted leg's sides bow in
    ("wr", "(hLeg * hLeg / 4 + waist * waist) / (2 * waist)"),  # ... the radius of those arcs
    ("aw", "0.5 * bw"),                              # arch between the feet: width
    ("ah", "min(0.28 * hLeg, 0.42 * aw)"),           # ... and height
    ("ra", "(aw * aw / 4 + ah * ah) / (2 * ah)"),    # arch radius
    ("cy", "ah - ra"),                               # arch centre (below the floor)
    ("s", "T + clearance"),                          # slot width (nominal, before kerf)
    ("ys", "cy + sqrt(ra * ra - s * s / 4)"),        # where the slot meets the arch
    ("tabW", "clamp(0.16 * tw, 30 mm, 60 mm)"),
    ("tabX", "tw / 2 - tabW / 2 - 25 mm"),           # centre of a tab from the leg's middle
    ("mw", "tabW + clearance"),                      # mortise, nominal
    ("hk", "kerf / 2"),
    ("hr", "15 mm"),                                 # hand-hold: half its width
    ("hl", "clamp(0.3 * seat - 50 mm, 20 mm, 55 mm)"),  # ... half its straight length
    ("hc", "(seat / 2 - 25 mm - hr) * sqrt(0.5)"),  # ... its centre at (hc, hc): 25 mm from the edge
    ("rim", "min(2 mm, T / 6)"),                     # rounded top rim of the seat
]


class Sketch:
    """Builds sketch commands and predicts the entity ids 3DCraft gives them
    (e1, e2, ... in creation order: a path's start, then per segment its end
    point, its centre point (arc with a centre) and the curve)."""

    def __init__(self, steps, name, plane="xy", offset=None):
        self.steps, self.name, self.n = steps, name, 0
        p = {"name": name, "plane": plane}
        if offset:
            p["offset"] = offset
        steps.append(["sketch.create", p])

    def _new(self):
        self.n += 1
        return "e%d" % self.n

    def path(self, start, segments, closed=False):
        """segments: ("line", end) or ("arc", end, center, clockwise). end may be an
        existing id ("e3"), "start" or [x, y]. Returns the ids of the corner points."""
        pts = []
        if isinstance(start, list):
            pts.append(self._new())
        else:
            pts.append(start)
        segs = []
        for seg in segments:
            kind, end = seg[0], seg[1]
            if isinstance(end, list):
                pts.append(self._new())
            else:
                pts.append(pts[0] if end == "start" else end)
            if kind == "line":
                self._new()
                segs.append({"line": end})
            else:
                self._new()  # centre
                self._new()  # arc
                segs.append({"arc": end, "center": seg[2], "clockwise": seg[3]})
        if closed:
            self._new()
        p = {"sketch": self.name, "start": start, "segments": segs}
        if closed:
            p["closed"] = True
        self.steps.append(["sketch.path", p])
        return pts

    def curve(self, start, end, x, y):
        self.steps.append(["sketch.curve", {"sketch": self.name, "start": start, "end": end,
                                            "x": x, "y": y, "t": ["0", "1"]}])
        self._new()

    def rect(self, x0, y0, x1, y1):
        return self.path([x0, y0], [("line", [x1, y0]), ("line", [x1, y1]), ("line", [x0, y1]), ("line", "start")])


def leg(steps, name, slot_from_top, waisted):
    """One leg in the sketch's xy (x across, y up), stood up later, as one closed path of
    lines and arcs (feature.offsetProfile does not offset splines yet). The cross-lap slot
    is cut from the floor (leg A) or from the top (leg B), to half the leg's height. The
    sides are straight lines (straight and splayed legs) or arcs bowed in by `waist`."""
    sk = Sketch(steps, name)
    # Top edge, right to left, with two tabs (and leg B's slot in the middle).
    seg = [("line", ["tabX + tabW / 2", "hLeg"]), ("line", ["tabX + tabW / 2", "hLeg + T"]),
           ("line", ["tabX - tabW / 2", "hLeg + T"]), ("line", ["tabX - tabW / 2", "hLeg"])]
    if slot_from_top:
        seg += [("line", ["s / 2", "hLeg"]), ("line", ["s / 2", "hLeg / 2"]),
                ("line", ["-s / 2", "hLeg / 2"]), ("line", ["-s / 2", "hLeg"])]
    seg += [("line", ["-tabX + tabW / 2", "hLeg"]), ("line", ["-tabX + tabW / 2", "hLeg + T"]),
            ("line", ["-tabX - tabW / 2", "hLeg + T"]), ("line", ["-tabX - tabW / 2", "hLeg"]),
            ("line", ["-tw / 2", "hLeg"])]
    # Left side down to the floor.
    if waisted:
        seg += [("arc", ["-tw / 2", "0 mm"], ["-tw / 2 - (wr - waist)", "hLeg / 2"], True)]
    else:
        seg += [("line", ["-bw / 2", "0 mm"])]
    # Bottom edge, left to right, with the arch between the feet (and leg A's slot).
    seg += [("line", ["-aw / 2", "0 mm"])]
    if slot_from_top:
        seg += [("arc", ["aw / 2", "0 mm"], ["0 mm", "cy"], True)]
    else:
        seg += [("arc", ["-s / 2", "ys"], ["0 mm", "cy"], True),
                ("line", ["-s / 2", "hLeg / 2"]), ("line", ["s / 2", "hLeg / 2"]),
                ("line", ["s / 2", "ys"]),
                ("arc", ["aw / 2", "0 mm"], ["0 mm", "cy"], True)]
    seg += [("line", ["tw / 2" if waisted else "bw / 2", "0 mm"])]
    # Right side back up to the start.
    if waisted:
        seg += [("arc", "start", ["tw / 2 + (wr - waist)", "hLeg / 2"], True)]
    else:
        seg += [("line", "start")]
    sk.path(["tw / 2", "hLeg"], seg)
    return name


def main():
    s = []
    for n, e in INPUTS + DERIVED:
        s.append(["variable.set", {"name": n, "expr": e}])

    # Seat: a rounded square turned 45 degrees (corners on the axes), with four mortises.
    seat = Sketch(s, "SeatSketch", "xy", "hLeg")
    q = "sqrt(0.5)"
    seat.path(["cc + cr * %s" % q, "-cr * %s" % q], [
        ("arc", ["cc + cr * %s" % q, "cr * %s" % q], ["cc", "0 mm"], False),
        ("line", ["cr * %s" % q, "cc + cr * %s" % q]),
        ("arc", ["-cr * %s" % q, "cc + cr * %s" % q], ["0 mm", "cc"], False),
        ("line", ["-cc - cr * %s" % q, "cr * %s" % q]),
        ("arc", ["-cc - cr * %s" % q, "-cr * %s" % q], ["-cc", "0 mm"], False),
        ("line", ["-cr * %s" % q, "-cc - cr * %s" % q]),
        ("arc", ["cr * %s" % q, "-cc - cr * %s" % q], ["0 mm", "-cc"], False),
        ("line", "start")])
    for sx in ("", "-"):
        seat.rect("%stabX - mw / 2" % sx, "-s / 2", "%stabX + mw / 2" % sx, "s / 2")
        seat.rect("-s / 2", "%stabX - mw / 2" % sx, "s / 2", "%stabX + mw / 2" % sx)
    # Hand-hold slot between the +x and +y leg arms: centred at (hc, hc), along (-1, 1),
    # straight part 2 hl long, round ends of radius hr. A point at a along the slot and b
    # across it (towards the edge) is (hc + (b - a) q, hc + (a + b) q).
    hand = Sketch(s, "HandSketch", "xy", "hLeg")
    pt = lambda a, b: ["hc + (%s) * %s" % (b + " - (" + a + ")", q), "hc + (%s) * %s" % (a + " + " + b, q)]
    hand.path(pt("-hl", "-hr"), [
        ("line", pt("hl", "-hr")),
        ("arc", pt("hl", "hr"), pt("hl", "0 mm"), True),
        ("line", pt("-hl", "hr")),
        ("arc", "start", pt("-hl", "0 mm"), True)])

    s.append(["feature.offsetProfile", {"sketch": "SeatSketch", "distance": "hk", "name": "SeatPath"}])
    s.append(["feature.extrude", {"sketch": "SeatPath", "distance": "T", "name": "SeatSolid"}])
    s.append(["feature.offsetProfile", {"sketch": "HandSketch", "distance": "-hk", "name": "HandPath"}])
    s.append(["feature.extrude", {"sketch": "HandPath", "distance": "T + 2 mm", "name": "HandTool"}])
    s.append(["feature.transform", {"source": "HandTool", "translate": ["0 mm", "0 mm", "-1 mm"], "name": "HandToolM"}])
    s.append(["feature.when", {"feature": "HandTool", "expr": "handhold"}])
    s.append(["feature.when", {"feature": "HandToolM", "expr": "handhold"}])
    # Round the seat's top rim (a router's round-over; the bottom face, the one cut, stays sharp).
    cap = "F4:endCap(F3:offset(e4,e6,e9,e11,e14,e16,e19,e20))"
    s.append(["feature.fillet", {"name": "SeatRound", "edges": [["F4:side(F3:offset(e4))", cap]], "chain": True,
                                 "radius": "rim"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "SeatRound", "tool": "HandToolM", "name": "Seat"}])

    # Each leg twice: with straight sides (straight and splayed) and with bowed sides
    # (waisted); the leg style switches one of them on.
    legs = []
    for leg_name, from_top in (("LegA", False), ("LegB", True)):
        for suffix, waisted, cond in (("", False, "style != 3"), ("Waisted", True, "style == 3")):
            nm = leg_name + suffix
            leg(s, nm + "Sketch", from_top, waisted)
            chain = [["feature.offsetProfile", {"sketch": nm + "Sketch", "distance": "hk", "name": nm + "Path"}],
                     ["feature.extrude", {"sketch": nm + "Path", "distance": "T", "symmetric": True, "name": nm + "Flat"}],
                     ["feature.transform", {"source": nm + "Flat", "angle": "90 deg", "axis": [1, 0, 0],
                                            "name": nm if not from_top else nm + "Up"}]]
            if from_top:
                chain.append(["feature.transform", {"source": nm + "Up", "angle": "90 deg", "axis": [0, 0, 1], "name": nm}])
            s.extend(chain)
            for c in [["sketch", {"name": nm + "Sketch"}]] + chain:
                s.append(["feature.when", {"feature": c[1]["name"], "expr": cond}])
            legs.append((nm, from_top))

    s.append(["body.appearance", {"body": "Seat", "color": "#D9B98A", "roughness": 0.8}])
    for nm, _ in legs:
        s.append(["body.appearance", {"body": nm, "color": "#C9A672", "roughness": 0.8}])

    pub = [
        ("height", dict(label="Height", description="Height of the seat's top above the floor", group="Size", order=1,
                        min="300 mm", max="650 mm", step="1 mm", unit="mm")),
        ("seat", dict(label="Seat size", description="Side of the square seat (it sits turned 45 degrees over the legs)",
                      group="Size", order=2, min="260 mm", max="450 mm", step="1 mm", unit="mm")),
        ("style", dict(label="Leg style", description="Straight, splayed (wider at the floor, steadier) or waisted (curved in at the middle)",
                       group="Size", order=3, kind="choice", choices=["straight", "splayed", "waisted"])),
        ("handhold", dict(label="Hand-hold slot", description="A rounded slot in the seat to carry it by", group="Size", order=4,
                          kind="boolean")),
        ("thick", dict(label="Sheet thickness", description="Thickness of the plywood: the slots and mortises follow it",
                       group="Material", order=1, min="9 mm", max="24 mm", step="0.1 mm", unit="mm")),
        ("kerf", dict(label="Kerf", description="Width of the cut. Laser: about 0.1 to 0.2 mm; CNC router: 0 when your CAM compensates the tool",
                      group="Cutting", order=1, min="0 mm", max="0.5 mm", step="0.01 mm", unit="mm")),
        ("clearance", dict(label="Clearance", description="Extra width of each slot and mortise after cutting: 0 is a press fit, 0.2 to 0.4 mm slides",
                           group="Cutting", order=2, min="0 mm", max="0.6 mm", step="0.01 mm", unit="mm")),
    ]
    for name, fields in pub:
        p_ = {"name": name}
        p_.update(fields)
        s.append(["variable.publish", p_])

    s.append(["set.define", {"name": "Cut sheet", "kind": "face", "where": {"any": [
        {"in": "Seat", "normal": {"along": "-z"}},
        {"in": "LegA", "normal": {"along": "-y"}},
        {"in": "LegAWaisted", "normal": {"along": "-y"}},
        {"in": "LegB", "normal": {"along": "x"}},
        {"in": "LegBWaisted", "normal": {"along": "x"}},
    ]}}])
    s.append(["document.info", {
        "title": "Flat-pack stool",
        "description": "A stool or side table cut from one sheet of plywood and put together without screws or glue: two legs "
                       "cross with a half-lap joint and their tabs go through the seat. Set the height, the seat size, the leg "
                       "style, the sheet thickness, your cutter's kerf and the clearance of the slots. To cut it: File > Export..., "
                       "DXF or SVG with the face set \"Cut sheet\" (file.export {\"path\": \"stool.svg\", \"set\": \"Cut sheet\"}): "
                       "the seat and both legs at true size, kerf included.",
        "author": "Johan Coppens",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/flatpack-stool",
        "tags": ["furniture", "stool", "flat-pack", "plywood", "CNC", "laser", "sheet"]}])
    s.append(["jig.export", {"path": "dist/flatpack-stool.3dcraftjig"}])
    return s


def fmt(v):
    v = round(v, 12)
    if abs(v) < 1e-12:
        return "0"
    return repr(v) if v >= 0 else "(%r)" % v


if __name__ == "__main__":
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
