#!/usr/bin/env python3
"""Writes build.json for the Strandbeest leg Jig (python3 -I gen.py > build.json).

Theo Jansen's walking linkage: a crank and eleven bars (two of them rigid
triangles) that turn the crank's rotation into a foot path with a long, nearly
flat bottom stroke. Every joint position is a formula of the crank angle, worked
out as closed-form circle-circle intersections, so dragging the crank angle walks
the leg. Every part is drawn once in its own frame (a bar from its first pin
along +x) and placed by a transform: turned by the angle of the line between its
pins and moved to its first pin. Its other pin holes therefore land on the joints
only when the kinematics close, which the assertions measure.

Coordinates of the leg's plane: the crank axle O at the origin, x horizontal
(the walker walks towards -x when the crank turns counter-clockwise), y up; in
the model the leg stands in the world zx plane (its y is world z) and its layers
stack towards the front, -y (sketches on zx, parts turned about -y). The fixed pivot B is at (-a, -l). Joints (Wang 2026, eq. 1-3, same
letters as Jansen's numbers):
    A = O + m (cos th, sin th)          crank pin
    C = circ(A, j; B, b)                upper joint, above B
    D = circ(B, d; C, e)                outer corner of the hip triangle B C D
    E = circ(A, k; B, c)                knee, below B
    F = circ(D, f; E, g)                upper corner of the foot triangle E F G
    G = circ(F, h; E, i)                the foot
circ(P, r; Q, s) is P + al u + sg r sqrt(q) n with u the unit vector P->Q, n
it turned by +90 deg, al = (r^2 - s^2 + |PQ|^2) / (2 |PQ|), q = 1 - (al/r)^2 the
normalised discriminant (the sine squared of the angle at P), and sg the branch:
+1 left of P->Q, -1 right. The branches are those of Jansen's leg, kept the same
at every angle.

Layers (one leg, from the frame outwards; layer n has its back face at depth
n (t + gap) in front of the frame's back face):
    0  frame                        (pins O and B through it)
    1  crank, hip triangle, foot triangle
    2  bar j, bar c
    3  bar k, bar f
Parts on one layer never meet over the whole turn, and a pin only passes layers
whose parts stay clear of it (checked at every degree by the generator's own
simulation when the layering was chosen, and at the form's crank angle by the
assertions). With two legs the second is the same stack mirrored behind a
second frame plate, half a turn out of phase, both cranks on one axle.
"""
import json
import math

ID = "strandbeest-leg"

# Theo Jansen's "holy numbers" (his units; the crank m = 15).
HOLY = dict(a=38.0, b=41.5, c=39.3, d=40.1, e=55.8, f=39.4, g=36.7, h=65.7, i=49.0, j=50.0, k=61.9, l=7.8, m=15.0)

# Sheet materials: name, thinnest sheet mm, least web round a hole mm (printed: four 0.4 mm perimeters).
MATERIALS = [
    ("Birch plywood, laser-cut", 3, 1.5),
    ("Walnut plywood, laser-cut", 3, 1.5),
    ("Acrylic (PMMA), laser-cut", 2, 1.5),
    ("PLA, 3D printed", 2, 1.6),
    ("PETG, 3D printed", 2, 1.6),
]
# Pins: name, diameter mm.
PINS = [
    ("M3 bolt", 3),
    ("M4 bolt", 4),
    ("M5 bolt", 5),
    ("3 mm steel rod", 3),
    ("4 mm steel rod", 4),
    ("5 mm steel rod", 5),
    ("1/8 in brass rod", 3.175),
]

N = 24              # crank angles sampled for the foot path and the closure check
STANCE = 4          # the stance: samples -STANCE..STANCE (120 degrees of crank)
QMIN = "0.01"       # least normalised discriminant: no joint flatter than ~5.7 deg
FLAT = "0.03"       # the stance's height spread at most 3 % of the stride

INPUTS = [
    ("crank", "15 mm"),
    ("theta", "0 deg"),
    ("legs", "1"),
    ("material", "1"),
    ("t", "3 mm"),
    ("w", "9 mm"),
    ("pin", "1"),
    ("clr", "0.2 mm"),
    ("gap", "1 mm"),
]

BRANCH = dict(C=-1, D=1, E=1, F=-1, G=-1)


def circ(v, p, j, P, r, Q, s):
    """Joint j of prefix p: the intersection of circle (P, r) and (Q, s), branch BRANCH[j]."""
    n = p + j
    px, py, qx, qy = P[0], P[1], Q[0], Q[1]
    v.append((n + "dd", "sqrt((%s - %s)^2 + (%s - %s)^2)" % (qx, px, qy, py)))
    v.append((n + "al", "(%s^2 - %s^2 + %sdd^2) / (2 * %sdd)" % (r, s, n, n)))
    v.append((n + "q", "1 - (%sal / %s)^2" % (n, r)))
    sg = "+" if BRANCH[j] > 0 else "-"
    hh = "%s * sqrt(max(%sq, 0))" % (r, n)
    v.append((n + "x", "%s + (%sal * (%s - %s) %s %s * (%s - %s)) / %sdd" % (px, n, qx, px, "-" if sg == "+" else "+", hh, qy, py, n)))
    v.append((n + "y", "%s + (%sal * (%s - %s) %s %s * (%s - %s)) / %sdd" % (py, n, qy, py, sg, hh, qx, px, n)))
    return (n + "x", n + "y")


def kin(v, p, ang):
    """The joints of a leg (prefix p) at crank angle ang: returns {joint: (x, y)}."""
    J = {"O": ("0 mm", "0 mm"), "B": ("-La", "-Ll")}
    v.append((p + "Ax", "Lm * cos(%s)" % ang))
    v.append((p + "Ay", "Lm * sin(%s)" % ang))
    J["A"] = (p + "Ax", p + "Ay")
    J["C"] = circ(v, p, "C", J["A"], "Lj", J["B"], "Lb")
    J["D"] = circ(v, p, "D", J["B"], "Ld", J["C"], "Le")
    J["E"] = circ(v, p, "E", J["A"], "Lk", J["B"], "Lc")
    J["F"] = circ(v, p, "F", J["D"], "Lf", J["E"], "Lg")
    J["G"] = circ(v, p, "G", J["F"], "Lh", J["E"], "Li")
    return J


def simulate():
    """The generator's own check of what the layering and the ranges rely on, at every degree of
    crank with Jansen's numbers (crank 15): every joint closes with q >= 0.05, parts on one layer
    stay at least 13 apart (centre line to centre line; the bars are at most 11.25 wide), and a pin
    passes a part of a layer between its ends at least 13 from that part's centre line (half a bar
    and a pin hole are at most 11.25). Raises if Jansen's leg ever broke them; returns the numbers."""
    L = HOLY

    def cc(P, r, Q, s, sg):
        dx, dy = Q[0] - P[0], Q[1] - P[1]
        d = math.hypot(dx, dy)
        al = (r * r - s * s + d * d) / (2 * d)
        q = 1 - (al / r) ** 2
        h = r * math.sqrt(max(q, 0))
        return (P[0] + (al * dx - sg * h * dy) / d, P[1] + (al * dy + sg * h * dx) / d), q

    def leg(th):
        P = {"O": (0.0, 0.0), "B": (-L["a"], -L["l"]), "A": (L["m"] * math.cos(th), L["m"] * math.sin(th))}
        qs = []
        for j, p1, r1, p2, r2 in (("C", "A", "j", "B", "b"), ("D", "B", "d", "C", "e"), ("E", "A", "k", "B", "c"),
                                  ("F", "D", "f", "E", "g"), ("G", "F", "h", "E", "i")):
            P[j], q = cc(P[p1], L[r1], P[p2], L[r2], BRANCH[j])
            qs.append(q)
        return P, min(qs)

    def seg_pt(p, a, b):
        ax, ay = b[0] - a[0], b[1] - a[1]
        ll = ax * ax + ay * ay
        t = 0.0 if ll == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / ll))
        return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def inside(p, tri):
        s1, s2, s3 = cross(tri[0], tri[1], p), cross(tri[1], tri[2], p), cross(tri[2], tri[0], p)
        return (s1 >= 0 and s2 >= 0 and s3 >= 0) or (s1 <= 0 and s2 <= 0 and s3 <= 0)

    def edges(sh):
        return [(sh[0], sh[0])] if len(sh) == 1 else [(sh[i], sh[(i + 1) % len(sh)]) for i in range(len(sh) if len(sh) == 3 else 1)]

    def seg_seg(p, q, r, t):
        if cross(p, q, r) * cross(p, q, t) < 0 and cross(r, t, p) * cross(r, t, q) < 0:
            return 0.0
        return min(seg_pt(p, r, t), seg_pt(q, r, t), seg_pt(r, p, q), seg_pt(t, p, q))

    def dist(a, b):
        for x, y in ((a, b), (b, a)):
            if len(y) == 3 and any(inside(p, y) for p in x):
                return 0.0
        return min(seg_seg(p, q, r, t) for p, q in edges(a) for r, t in edges(b))

    members = {"crank": "OA", "j": "AC", "k": "AE", "hip": "BCD", "c": "BE", "f": "DF", "foot": "EFG"}
    layer = {"crank": 1, "hip": 1, "foot": 1, "j": 2, "c": 2, "k": 3, "f": 3}
    span = {"O": (0, 1), "A": (1, 3), "B": (0, 2), "C": (1, 2), "D": (1, 3), "E": (1, 3), "F": (1, 3)}
    qmin, same, pinmin = 9.0, 1e9, 1e9
    for deg in range(360):
        P, q = leg(math.radians(deg))
        qmin = min(qmin, q)
        sh = {n: [P[c] for c in v] for n, v in members.items()}
        names = list(members)
        for x in range(len(names)):
            for y in range(x + 1, len(names)):
                if layer[names[x]] == layer[names[y]]:
                    same = min(same, dist(sh[names[x]], sh[names[y]]))
        for j, (lo, hi) in span.items():
            for n in names:
                if lo <= layer[n] <= hi and j not in members[n]:
                    pinmin = min(pinmin, dist(sh[n], [P[j]]))
    if qmin < 0.05 or same < 13 or pinmin < 13:
        raise SystemExit("Jansen's leg breaks the layering: q %g, same layer %g, pins %g" % (qmin, same, pinmin))
    return qmin, same, pinmin


def nest(fn, items):
    return "%s(%s)" % (fn, ", ".join(items))


def r90(p):
    """A point turned by +90 degrees in the leg's plane."""
    return p if p == "start" else ["-(%s)" % p[1], p[0]]


def sw(p):
    """A point of the leg's plane (x along the ground, y up) in a sketch on the zx plane, whose
    axes are world z (up) and world x."""
    return p if p == "start" else [p[1], p[0]]


class Sketch:
    """Sketches of the leg's plane: on the world zx plane (the leg stands up, its layers along -y);
    points are given as (x, y) of the leg's plane. Swapping the axes mirrors, so arcs turn the
    other way."""

    def __init__(self, steps, name, plane="zx", offset=None, turn=False):
        self.steps, self.name, self.swap = steps, name, plane == "zx"
        self.turn = turn
        p = {"name": name, "plane": plane}
        if offset:
            p["offset"] = offset
        steps.append(["sketch.create", p])

    def path(self, start, segs):
        if self.turn:
            start = r90(start)
            segs = [{"line": r90(g["line"])} if "line" in g else dict(g, arc=r90(g["arc"]), center=r90(g["center"]))
                    for g in segs]
        if self.swap:
            start = sw(start)
            out = []
            for g in segs:
                if "line" in g:
                    out.append({"line": sw(g["line"])})
                else:
                    out.append({"arc": sw(g["arc"]), "center": sw(g["center"]), "clockwise": not g["clockwise"]})
            segs = out
        self.steps.append(["sketch.path", {"sketch": self.name, "start": start, "segments": segs}])

    def polyline(self, pts):
        self.steps.append(["sketch.polyline", {"sketch": self.name, "points": [sw(p) if self.swap else p for p in pts]}])

    def circle(self, c, r):
        if self.turn:
            c = r90(c)
        self.steps.append(["sketch.circle", {"sketch": self.name, "center": sw(c) if self.swap else c, "radius": r}])


def rounded_polygon(sk, pts, r):
    """Outline of the convex hull of circles of radius r round pts (counter-clockwise, as
    expressions [x, y]); nrm[i] is the outward unit normal of edge i, given as expressions."""
    n = len(pts)
    normals = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        ln = "sqrt(((%s) - (%s))^2 + ((%s) - (%s))^2)" % (x1, x0, y1, y0)
        normals.append(("((%s) - (%s)) / %s" % (y1, y0, ln), "-((%s) - (%s)) / %s" % (x1, x0, ln)))

    def off(p, nv):
        return ["(%s) + %s * %s" % (p[0], r, nv[0]), "(%s) + %s * %s" % (p[1], r, nv[1])]

    start = off(pts[0], normals[0])
    segs = []
    for i in range(n):
        p1 = pts[(i + 1) % n]
        segs.append({"line": off(p1, normals[i])})
        end = off(p1, normals[(i + 1) % n]) if i < n - 1 else "start"
        segs.append({"arc": end, "center": [p1[0], p1[1]], "clockwise": False})
    sk.path(start, segs)


def bar_outline(sk, L, r):
    """A link from (0, 0) to (L, 0) with round ends of radius r."""
    sk.path(["0 mm", "-" + r], [
        {"line": [L, "-" + r]},
        {"arc": [L, r], "center": [L, "0 mm"], "clockwise": False},
        {"line": ["0 mm", r]},
        {"arc": "start", "center": ["0 mm", "0 mm"], "clockwise": False}])


def main():
    s = []
    v = []
    s.append(["table.set", {"name": "sheets", "columns": ["material", {"name": "tMin", "unit": "mm"},
                                                          {"name": "web", "unit": "mm"}],
                            "rows": [list(r) for r in MATERIALS]}])
    s.append(["table.set", {"name": "pins", "columns": ["pin", {"name": "d", "unit": "mm"}],
                            "rows": [list(r) for r in PINS]}])
    v += INPUTS
    # Jansen's numbers, and the lengths at this scale (the crank is m).
    for k, x in HOLY.items():
        v.append(("J" + k, repr(x)))
    v.append(("u", "crank / Jm"))
    for k in HOLY:
        v.append(("L" + k, "J%s * u" % k))
    v += [
        ("pd", "pins[pin].d"),                 # pin diameter
        ("hole", "pd + clr"),                  # pin hole
        ("web", "sheets[material].web"),
        ("tMin", "sheets[material].tMin"),
        ("wMin", "ceil(hole + 2 * web, 0.1 mm)"),
        ("wMax", "floor(0.75 * crank, 0.1 mm)"),
        ("crankMin", "ceil((hole + 2 * web) / 0.75, 0.5 mm)"),
        ("pitch", "t + gap"),                  # layer to layer
        ("dg", "max(10 mm, 2 * w)"),           # drive gap behind the frame (axle stub, or between the frames)
        ("rt", "0.04 * crank"),                # foot path tube (thicker breaks the mitre at the sharp turn)
        ("Mx", "-La / 2"),                     # frame's mounting hole
        ("My", "0.6 * La"),
        ("zTop", "3 * pitch + t"),             # front face of leg 1's stack
        ("zPath", "zTop + gap + 2 * rt"),
    ]
    # Layer underside z, leg 1 (in front of the frame at z 0..t) and leg 2 (behind the second frame).
    zb = {1: lambda n: "%d * pitch" % n, 2: lambda n: "-dg - t - %d * pitch" % n}

    # Kinematics of the legs at the form's angle (leg 2 half a turn later), and the samples.
    legs = {1: kin(v, "p", "theta"), 2: kin(v, "r", "theta + 180 deg")}
    samples = []
    for k in range(N):
        samples.append(kin(v, "s%02d" % k, "%d deg" % (k * 360 // N)))
    qs = ["s%02d%sq" % (k, j) for k in range(N) for j in "CDEFG"]
    v.append(("closeMin", nest("min", qs)))
    gx = [S["G"][0] for S in samples]
    gy = [S["G"][1] for S in samples]
    v += [
        ("footMinX", nest("min", gx)), ("footMaxX", nest("max", gx)),
        ("footMinY", nest("min", gy)), ("footMaxY", nest("max", gy)),
        ("stride", "footMaxX - footMinX"),               # step length per crank turn
        ("stepHeight", "footMaxY - footMinY"),           # how high the foot lifts
    ]
    st = [gy[k % N] for k in range(-STANCE, STANCE + 1)]
    v.append(("stanceSpread", "%s - %s" % (nest("max", st), nest("min", st))))
    v.append(("stanceLength", "abs(%s - %s)" % (gx[STANCE], gx[-STANCE])))
    v.append(("flatness", "stanceSpread / stride"))
    cy = [S[j][1] for S in samples for j in ("C", "D")]
    v.append(("legTop", nest("max", cy)))
    v.append(("legHeight", "max(legTop, My) + w / 2 - footMinY + w / 2"))
    # The triangles in their own frames: hip B (0,0), C (Lb, 0), D (aD, hD); foot F (0,0), E (Lg, 0), G (aG, -hG).
    v += [
        ("aD", "(Ld^2 - Le^2 + Lb^2) / (2 * Lb)"), ("hD", "sqrt(Ld^2 - aD^2)"),
        ("aG", "(Lh^2 - Li^2 + Lg^2) / (2 * Lg)"), ("hG", "sqrt(Lh^2 - aG^2)"),
    ]
    # Turn of each part: the angle of the line from its first pin to its second.
    PARTS = [
        # name, shape, first pin, second pin, bar length, layer
        ("Crank", "bar", "O", "A", "Lm", 1),
        ("HipTriangle", "hip", "B", "C", None, 1),
        ("FootTriangle", "foot", "F", "E", None, 1),
        ("BarJ", "bar", "A", "C", "Lj", 2),
        ("BarC", "bar", "B", "E", "Lc", 2),
        ("BarK", "bar", "A", "E", "Lk", 3),
        ("BarF", "bar", "D", "F", "Lf", 3),
    ]
    for q, J in legs.items():
        for nm, shape, p0, p1, L, layer in PARTS:
            v.append(("%s%d" % (nm, q) + "Ang", "atan2(%s - %s, %s - %s)" % (J[p1][1], J[p0][1], J[p1][0], J[p0][0])))
    for nm, e in v:
        s.append(["variable.set", {"name": nm, "expr": e}])

    two = "legs == 2"
    r = "w / 2"
    hr = "hole / 2"

    # Frame plate(s): a rounded triangle round the axle O, the fixed pivot B and a mounting hole M.
    frame_pts = [["0 mm", "0 mm"], ["Mx", "My"], ["-La", "-Ll"]]
    sk = Sketch(s, "FrameSketch")
    rounded_polygon(sk, frame_pts, "0.75 * w")
    for p in frame_pts:
        sk.circle(p, hr)
    s.append(["feature.extrude", {"sketch": "FrameSketch", "distance": "t", "name": "FrameLocal"}])
    s.append(["feature.transform", {"source": "FrameLocal", "translate": ["0 mm", "dg", "0 mm"], "keep": True,
                                    "name": "Frame2", "when": two}])
    s.append(["feature.transform", {"source": "FrameLocal", "translate": ["0 mm", "-t", "0 mm"], "name": "Frame"}])

    # The moving parts, each drawn once in its own frame and placed for each leg.
    placed = {1: {}, 2: {}}
    for nm, shape, p0, p1, L, layer in PARTS:
        # Drawn turned by +90 degrees (the first pin at the origin, the second up the sketch's x),
        # and turned back when placed: see repro-strandbeest-leg-1 (an end arc whose end lies
        # in the direction of its hole circle's seam breaks the overlap test with the pin).
        sk = Sketch(s, nm + "Sketch", turn=True)
        if shape == "bar":
            bar_outline(sk, L, r)
            holes = [["0 mm", "0 mm"], [L, "0 mm"]]
        elif shape == "hip":
            pts = [["0 mm", "0 mm"], ["Lb", "0 mm"], ["aD", "hD"]]
            rounded_polygon(sk, pts, r)
            holes = pts
        else:
            pts = [["0 mm", "0 mm"], ["aG", "-hG"], ["Lg", "0 mm"]]
            rounded_polygon(sk, pts, r)
            holes = [pts[0], pts[2]]          # no pin at the foot
        for h in holes:
            sk.circle(h, hr)
        s.append(["feature.extrude", {"sketch": nm + "Sketch", "distance": "t", "name": nm + "Local"}])
        for q in (2, 1):
            J = legs[q]
            # turned about -y (counter-clockwise in the leg's plane seen from the front, -y),
            # its underside (the leg's plane z) at world y = -z - t
            p = {"source": nm + "Local", "angle": "%s%dAng - 90 deg" % (nm, q), "axis": [0, -1, 0],
                 "translate": [J[p0][0], "-(%s) - t" % zb[q](layer), J[p0][1]], "name": "%s%d" % (nm, q)}
            if q == 2:
                p["keep"] = True
                p["when"] = two
            s.append(["feature.transform", p])
            placed[q][nm] = "%s%d" % (nm, q)

    # Pins: from the underside of the lowest layer they join to the top of the highest.
    def top(q, n):
        return "%d * pitch + t" % n if q == 1 else "-dg - %d * pitch" % n

    pins = {1: {}, 2: {}}
    PINSPAN = [("A", 1, 3), ("C", 1, 2), ("D", 1, 3), ("E", 1, 3), ("F", 1, 3)]
    for q in (1, 2):
        J = legs[q]
        for j, lo, hi in PINSPAN:
            nm = "Pin%s%d" % (j, q)
            z0 = zb[q](lo) if q == 1 else zb[q](hi)
            z1 = top(q, hi) if q == 1 else top(q, lo)
            p = {"radius": "pd / 2", "height": "(%s) - (%s)" % (z1, z0), "axis": [0, 1, 0],
                 "position": [J[j][0], "-(%s)" % z1, J[j][1]], "name": nm}
            if q == 2:
                p["when"] = two
            s.append(["feature.cylinder", p])
            pins[q][j] = nm
    # The crank axle: 1 leg, from a stub behind the frame to the crank's face; 2 legs, crank to crank.
    s.append(["feature.cylinder", {"radius": "pd / 2", "height": "if(legs == 2, 2 * pitch + 2 * t + dg, pitch + t + dg)",
                                   "axis": [0, 1, 0], "position": ["0 mm", "-pitch - t", "0 mm"], "name": "Axle"}])
    # The fixed pivot's shaft: through the frame(s), the hip triangle and bar c.
    s.append(["feature.cylinder", {"radius": "pd / 2", "height": "if(legs == 2, 4 * pitch + 2 * t + dg, 2 * pitch + t)",
                                   "axis": [0, 1, 0], "position": ["-La", "-2 * pitch - t", "-Ll"], "name": "PivotShaft"}])
    # Two legs: spacers between the frames at B and M, and a bolt at M.
    for nm, (x, y) in (("SpacerB", ("-La", "-Ll")), ("SpacerM", ("Mx", "My"))):
        sk = Sketch(s, nm + "Sketch")
        sk.circle([x, y], "0.75 * w")
        sk.circle([x, y], hr)
        s.append(["feature.extrude", {"sketch": nm + "Sketch", "distance": "dg", "name": nm, "when": two}])
    s.append(["feature.cylinder", {"radius": "pd / 2", "height": "dg + 2 * t", "axis": [0, 1, 0], "position": ["Mx", "-t", "My"],
                                   "name": "MountBolt", "when": two}])

    # The foot path: the foot at every 15 degrees of crank, as a tube in front of the leg. The stance
    # (the 120 degrees of crank round the lowest point) is a tube of its own, so its flatness is measured.
    def path_tube(name, idx):
        pts = [[gx[k % N], gy[k % N]] for k in idx]
        sk = Sketch(s, name + "Path", "zx", "-zPath")
        sk.polyline(pts)
        (x0, y0), (x1, y1) = pts[0], pts[1]
        ln = "sqrt((%s - %s)^2 + (%s - %s)^2)" % (x1, x0, y1, y0)
        nx, ny = "-(%s - %s) / %s" % (y1, y0, ln), "(%s - %s) / %s" % (x1, x0, ln)
        s.append(["datum.plane", {"through": [[x0, "-zPath", y0], [x0, "-zPath - 1 mm", y0],
                                              ["%s + 1 mm * %s" % (x0, nx), "-zPath", "%s + 1 mm * %s" % (y0, ny)]],
                                  "name": name + "Plane"}])
        Sketch(s, name + "Profile", name + "Plane")  # a circle at its origin: no swap needed
        s.append(["sketch.circle", {"sketch": name + "Profile", "center": ["0 mm", "0 mm"], "radius": "rt"}])
        s.append(["feature.sweep", {"sketch": name + "Profile", "path": name + "Path", "name": name}])

    path_tube("Stance", range(-STANCE, STANCE + 1))
    path_tube("Swing", range(STANCE, N - STANCE + 1))

    # Appearance.
    ply = {"color": "#D9B98A", "roughness": 0.75}
    walnut = {"color": "#7A5638", "roughness": 0.6}
    brass = {"color": "#B8954A", "metallic": 0.8, "roughness": 0.35}
    petrol = {"color": "#2E7D7A", "roughness": 0.6}
    steel = {"color": "#7D858C", "metallic": 0.85, "roughness": 0.4}
    look = {"Crank": brass, "HipTriangle": walnut, "FootTriangle": walnut, "BarJ": ply, "BarC": ply, "BarK": ply, "BarF": ply}
    for q in (1, 2):
        for nm, a in look.items():
            s.append(["body.appearance", dict(body=placed[q][nm], **a)])
        for nm in pins[q].values():
            s.append(["body.appearance", dict(body=nm, **steel)])
    for nm in ("Frame", "Frame2"):
        s.append(["body.appearance", dict(body=nm, **petrol)])
    for nm in ("SpacerB", "SpacerM"):
        s.append(["body.appearance", dict(body=nm, **brass)])
    for nm in ("Axle", "PivotShaft", "MountBolt"):
        s.append(["body.appearance", dict(body=nm, **steel)])
    s.append(["body.appearance", {"body": "Stance", "color": "#C2694B", "roughness": 0.5}])
    s.append(["body.appearance", {"body": "Swing", "color": "#5B7299", "roughness": 0.5}])

    # Named sets.
    flat = ["Frame", "Frame2"] + [placed[q][nm] for q in (1, 2) for nm, *_ in PARTS]
    s.append(["set.define", {"name": "Cut sheet", "kind": "face",
                             "where": {"any": [{"in": nm, "normal": {"along": "-y"}} for nm in flat]}}])
    allpins = [n for q in (1, 2) for n in pins[q].values()] + ["Axle", "PivotShaft", "MountBolt"]
    parts = flat + ["SpacerB", "SpacerM"] + allpins
    s.append(["set.define", {"name": "Parts", "kind": "body", "where": {"any": [{"in": nm} for nm in parts]}}])
    s.append(["set.define", {"name": "Foot path", "kind": "body", "where": {"any": [{"in": "Stance"}, {"in": "Swing"}]}}])
    above = [n for n in parts if not n.startswith("FootTriangle")]
    s.append(["set.define", {"name": "Above the feet", "kind": "body", "where": {"any": [{"in": nm} for nm in above]}}])
    moving1 = [placed[1][nm] for nm, *_ in PARTS]
    s.append(["set.define", {"name": "Leg 1", "kind": "body", "where": {"any": [{"in": nm} for nm in moving1]}}])

    # Assertions.
    A = []

    def a(name, **p):
        p["name"] = name
        A.append(["assert.add", p])

    a("Linkage closes over the whole turn (every joint at 24 crank angles, none flatter than ~6 deg)",
      measure="extent", of="Frame", axis="x", min="if(closeMin >= %s, 0 mm, 1 m)" % QMIN)
    a("No part overlaps another (pins pass their holes, layers clear)", measure="overlap", of={"set": "Parts"}, **{"is": False})
    members = {"O": ["Frame", "Crank"], "A": ["Crank", "BarJ", "BarK"], "B": ["Frame", "HipTriangle", "BarC"],
               "C": ["HipTriangle", "BarJ"], "D": ["HipTriangle", "BarF"], "E": ["BarK", "BarC", "FootTriangle"],
               "F": ["BarF", "FootTriangle"]}
    for j, mem in members.items():
        for m in mem:
            pin = "Axle" if j == "O" else "PivotShaft" if j == "B" else pins[1][j]
            body = m if m == "Frame" else placed[1][m]
            a("Pin %s sits in its hole in %s (gap at most half the clearance)" % (j, body), measure="clearance",
              **{"from": pin, "to": body}, max="clr / 2 + 0.005 mm")
    for x, y in (("Crank1", "HipTriangle1"), ("Crank1", "FootTriangle1"), ("HipTriangle1", "FootTriangle1"),
                 ("BarJ1", "BarC1"), ("BarK1", "BarF1")):
        a("%s and %s, on one layer, stay apart" % (x, y), measure="clearance", **{"from": x, "to": y}, min="0.5 mm")
    a("The leg runs free of its frame", measure="clearance", **{"from": "Frame", "to": {"set": "Leg 1"}}, min="gap / 2")
    a("Stance is flat: the foot's lowest 120 deg of crank stays within 3 % of the stride in height",
      measure="extent", of="Stance", axis="z", max="%s * stride + 2.2 * rt" % FLAT)
    a("Foot path as wide as the stride", measure="extent", of={"set": "Foot path"}, axis="x",
      min="stride + 1.9 * rt", max="stride + 4 * rt")
    a("Only the feet reach down to the ground (everything else a step height above it)", measure="boxMin",
      of={"set": "Above the feet"}, axis="z", min="footMinY - w / 2 + stepHeight")
    s.extend(A)

    pub = [
        ("crank", dict(label="Crank length", description="Length of the crank (Jansen's m = 15): it sets the scale "
                       "of the whole leg, every bar in proportion to Jansen's numbers. At 15 mm the leg is about "
                       "14 cm tall.", group="Size", order=1, min="crankMin", max="60 mm", step="0.5 mm", unit="mm")),
        ("theta", dict(label="Crank angle", description="Turn of the crank, counter-clockwise from +x: drag it and "
                       "the leg walks (the foot follows the coloured path; the terracotta part is the stance)",
                       group="Size", order=2, min="0 deg", max="360 deg", step="1 deg", unit="deg")),
        ("legs", dict(label="Legs", description="One leg, or two legs half a turn apart on one crank axle, on "
                      "either side of a double frame (the drive goes between the frame plates)", group="Size",
                      order=3, kind="choice", choices=["1 leg", "2 legs (180 deg apart)"])),
        ("material", dict(label="Material", description="What the flat parts are cut or printed from (table "
                          "sheets: thinnest sheet and least web round a hole)", group="Parts", order=1,
                          kind="choice", choicesFrom="sheets")),
        ("t", dict(label="Sheet thickness", description="Thickness of every flat part", group="Parts", order=2,
                   min="tMin", max="6 mm", step="0.1 mm", unit="mm")),
        ("w", dict(label="Bar width", description="Width of the bars and of the rim round the triangles' pins; at "
                   "least the pin hole and the material's web on both sides, at most 3/4 of the crank (so the "
                   "parts on one layer stay apart over the whole turn)", group="Parts", order=3,
                   min="wMin", max="wMax", step="0.1 mm", unit="mm")),
        ("pin", dict(label="Pins", description="Bolts or rod for the joints and the axle (table pins)", group="Parts",
                     order=4, kind="choice", choicesFrom="pins")),
        ("clr", dict(label="Pin clearance", description="How much larger the holes are than the pins: 0.1 to 0.2 mm "
                     "for laser-cut parts (the kerf adds about 0.1 mm), 0.3 to 0.4 mm for printed ones",
                     group="Parts", order=5, min="0.05 mm", max="0.6 mm", step="0.01 mm", unit="mm")),
        ("gap", dict(label="Layer gap", description="Space between the layers, for a washer: the bars of one layer "
                     "slide past the next without rubbing", group="Parts", order=6, min="0.3 mm", max="3 mm",
                     step="0.1 mm", unit="mm")),
    ]
    for name, fields in pub:
        p_ = {"name": name}
        p_.update(fields)
        s.append(["variable.publish", p_])

    s.append(["document.info", {
        "title": "Strandbeest leg",
        "description": "Theo Jansen's walking linkage: a crank and eleven bars (Jansen's \"holy numbers\") that turn "
                       "rotation into a walking foot path with a long, flat stroke along the ground. Drag the crank "
                       "angle and the leg walks; the foot's path is drawn in front of it. Set the size, one or two "
                       "legs, the sheet, the bar width and the pins; every joint is solved by formulas and the "
                       "assertions check that the linkage closes over the whole turn, that every pin sits in its "
                       "holes and that the parts on one layer stay apart. stride and stepHeight report the gait. "
                       "Cut sheet: file.export {\"path\": \"leg.svg\", \"set\": \"Cut sheet\"}.",
        "author": "3DCraft Jigs",
        "licence": "CC-BY-4.0",
        "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/" + ID,
        "tags": ["mechanism", "linkage", "kinetic", "Strandbeest", "Theo Jansen", "walking", "laser", "plywood", "3D print"]}])
    s.append(["jig.export", {"path": "dist/%s.3dcraftjig" % ID}])
    return s


if __name__ == "__main__":
    simulate()
    print("[\n" + ",\n".join(json.dumps(x) for x in main()) + "\n]")
