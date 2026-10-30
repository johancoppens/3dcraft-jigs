#!/usr/bin/env python3
"""Writes the Strandbeest assemblies (python3 -I gen.py): the command batches 01-bar.json to
06-strandbeest-walker.json, run in order by scripts/asm.py, and check.json.

The strandbeest-leg Jig works every joint out by hand, as circle-circle intersections. Here the leg is
built again from parts and the assembly solver finds the joints instead:

    bar.3dcraft     one flat bar with a pin hole at each end; its length `len` is a public parameter,
                    so each bar of the leg is an instance of it with its own length (a configuration)
    pin.3dcraft     a round pin; its length `len` is a public parameter
    leg.3dcraftasm  one leg: a frame bar O-B fixed to the world, the crank O-A, ten bars (the hip
                    triangle B C D and the foot triangle E F G are three bars each, pinned at their
                    corners), a second crank arm (the web) at the front holding the crank pin A at
                    both ends, and a pin at every joint; revolute mates at the joints. It is not driven:
                    the crank can still turn (1 degree of freedom). A flexible subassembly brings its
                    own drivers into the parent, so a driven leg could not be turned by a crankshaft.
    strandbeest-leg.3dcraftasm    one leg as a flexible subassembly, on a drive shaft behind the
                    frame that t turns once: the leg walks, its foot is traced.
    strandbeest-walker.3dcraftasm four instances of the leg as flexible subassemblies in a row on
                    one crankshaft: the drive shaft, and between two legs a journal fixed to the front
                    crank arm of one and the axle of the next, a quarter turn on (the phase offsets).
                    Every leg starts at crank angle 0; the solve turns legs 2 to 4 to their phases.

Layers. The parts of a leg lie in seven layers, from the frame (0) towards the front (-y), each
`thick` thick with `gap` between them. The layering was found by search (the generator's own
simulation, layering() below) so that over a whole turn of the crank (every 2 deg): parts on one layer
stay at least 1 mm apart (between their edges), parts joined by a pin are on different layers, and no
pin passes a part between its two outer layers within 1 mm. The crank sits right in front of the frame
so its axle only passes the frame; bars j and k pass over the axle, so the crankshaft cannot go through
the leg: the crank pin A runs to a web on layer 6, and the next leg is driven from that web (a crank
throw).

    0 frame   1 crank   2 bars j, c, f   3 bars b, g   4 bars d, i   5 bars k, e, h   6 web

The leg's plane is the world's xz plane (x along the ground, z up), as in the Jig; the crank angle is
counter-clockwise seen from the front (-y), and at crank angle th the crank pin is at
(m cos th, m sin th). The parts' start poses are the Jig's joints at the leg's crank angle, rounded to
the millimetre and to 5 deg, so the solver really assembles the leg.
"""
import itertools
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = "build/strandbeest"
LEG_OUT = "dist/strandbeest-leg.3dcraftasm"
WALKER_OUT = "dist/strandbeest-walker.3dcraftasm"

# Jansen's "holy numbers" (the crank m = 15 mm: lengths in mm), as in the Jig.
HOLY = dict(a=38.0, b=41.5, c=39.3, d=40.1, e=55.8, f=39.4, g=36.7, h=65.7, i=49.0, j=50.0, k=61.9, l=7.8, m=15.0)
BRANCH = dict(C=-1, D=1, E=1, F=-1, G=-1)
W, THICK, GAP, PIN, HOLE, STUB = 9.0, 3.0, 1.0, 3.0, 3.2, 10.0
PITCH = THICK + GAP

# Bars: instance name, Jansen's letter (its length), first joint, second joint.
BARS = [
    ("Frame", None, "O", "B"),
    ("Crank", "m", "O", "A"),
    ("Web", "m", "O", "A"),
    ("BarJ", "j", "A", "C"),
    ("BarK", "k", "A", "E"),
    ("BarB", "b", "B", "C"),
    ("BarC", "c", "B", "E"),
    ("BarD", "d", "B", "D"),
    ("BarE", "e", "C", "D"),
    ("BarF", "f", "D", "F"),
    ("BarG", "g", "E", "F"),
    ("BarH", "h", "F", "G"),
    ("BarI", "i", "E", "G"),
]
# Persistent names in the parts (document.edges of build/strandbeest/bar.3dcraft and pin.3dcraft):
# the bar's pin holes at its back face (z = 0): the first at the origin, the second at (0, len);
# and the pin's end circles, at z = 0 and z = len.
HOLE1 = "F2:startEdge(e12)"
HOLE2 = "F2:startEdge(e14)"
HOLE1_FRONT = "F2:endEdge(e12)"
PIN_BACK = "F1:edge(0)"
PIN_FRONT = "F1:edge(1)"


def cc(P, r, Q, s, sg):
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    d = math.hypot(dx, dy)
    al = (r * r - s * s + d * d) / (2 * d)
    h = r * math.sqrt(max(1 - (al / r) ** 2, 0))
    return (P[0] + (al * dx - sg * h * dy) / d, P[1] + (al * dy + sg * h * dx) / d)


def leg(th):
    """The Jig's closed form: the joints at crank angle th (radians), {joint: (x, z)}."""
    L = HOLY
    P = {"O": (0.0, 0.0), "B": (-L["a"], -L["l"]), "A": (L["m"] * math.cos(th), L["m"] * math.sin(th))}
    for j, p1, r1, p2, r2 in (("C", "A", "j", "B", "b"), ("D", "B", "d", "C", "e"), ("E", "A", "k", "B", "c"),
                              ("F", "D", "f", "E", "g"), ("G", "F", "h", "E", "i")):
        P[j] = cc(P[p1], L[r1], P[p2], L[r2], BRANCH[j])
    return P


def layering():
    """The least number of layers in which the leg turns freely (see the docstring), frame on 0,
    crank on 1, web in front of everything; the first such assignment in a fixed order."""
    def seg_pt(p, a, b):
        ax, ay = b[0] - a[0], b[1] - a[1]
        ll = ax * ax + ay * ay
        u = 0.0 if ll == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / ll))
        return math.hypot(p[0] - a[0] - u * ax, p[1] - a[1] - u * ay)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def seg_seg(p, q, r, s):
        if cross(p, q, r) * cross(p, q, s) < 0 and cross(r, s, p) * cross(r, s, q) < 0:
            return 0.0
        return min(seg_pt(p, r, s), seg_pt(q, r, s), seg_pt(r, p, q), seg_pt(s, p, q))

    joints = {n: (p, q) for n, _, p, q in BARS}
    names = [n for n, _, _, _ in BARS]
    pos = [leg(math.radians(d)) for d in range(0, 360, 2)]
    dd = {}
    for x, y in itertools.combinations(names, 2):
        dd[(x, y)] = min(seg_seg(P[joints[x][0]], P[joints[x][1]], P[joints[y][0]], P[joints[y][1]]) for P in pos)
    dj = {(n, J): min(seg_pt(P[J], P[joints[n][0]], P[joints[n][1]]) for P in pos) for n in names for J in "OABCDEFG"}
    at = {J: [n for n in names if J in joints[n]] for J in "OABCDEFG"}
    at["O"] = ["Frame", "Crank"]          # the axle reaches the crank only

    def ok(lay):
        for x, y in itertools.combinations(names, 2):
            if lay[x] == lay[y]:
                if set(joints[x]) & set(joints[y]) or dd[(x, y)] < W + 1.0:
                    return False
        for J, parts in at.items():
            lo, hi = min(lay[n] for n in parts), max(lay[n] for n in parts)
            for n in names:
                if n not in parts and lo <= lay[n] <= hi and dj[(n, J)] < W / 2 + PIN / 2 + 1.0:
                    return False
        return True

    free = [n for n in names if n not in ("Frame", "Crank", "Web")]
    for top in range(3, 8):
        for combo in itertools.product(range(2, top), repeat=len(free)):
            lay = dict(zip(free, combo), Frame=0, Crank=1, Web=top)
            if ok(lay):
                return lay
    raise SystemExit("no layering found")


def rotvec(m):
    """The rotation vector (degrees) of a rotation matrix given as columns [x, y, z]."""
    (x0, x1, x2), (y0, y1, y2), (z0, z1, z2) = m
    # rows r_ij = column j's component i
    r = [[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]]
    tr = r[0][0] + r[1][1] + r[2][2]
    ang = math.acos(max(-1.0, min(1.0, (tr - 1) / 2)))
    if ang < 1e-12:
        return [0.0, 0.0, 0.0]
    if math.pi - ang < 1e-6:
        # a half turn: the axis from the symmetric part
        ax = [math.sqrt(max(0.0, (r[i][i] + 1) / 2)) for i in range(3)]
        k = max(range(3), key=lambda i: ax[i])
        for i in range(3):
            if i != k:
                ax[i] = math.copysign(ax[i], r[k][i])
        return [math.degrees(ang) * a for a in ax]
    s = 2 * math.sin(ang)
    ax = [(r[2][1] - r[1][2]) / s, (r[0][2] - r[2][0]) / s, (r[1][0] - r[0][1]) / s]
    return [math.degrees(ang) * a for a in ax]


def placement(p0, p1, layer):
    """Start pose of a bar drawn from its first hole at the origin up its own +y to the second, lying
    in the leg's plane on `layer`, its +z towards the front (-y): its first hole at p0, its second
    towards p1. Rounded to 1 mm and 5 deg."""
    phi = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    phi = math.radians(5 * round(math.degrees(phi) / 5))
    d = (math.cos(phi), 0.0, math.sin(phi))           # the bar's +y in the world
    z = (0.0, -1.0, 0.0)
    x = (d[1] * z[2] - d[2] * z[1], d[2] * z[0] - d[0] * z[2], d[0] * z[1] - d[1] * z[0])   # y x z
    pos = [round(p0[0]), -layer * PITCH, round(p0[1])]
    return pos, rotvec([x, d, z])


def mm(x):
    return "%g mm" % x


def bar_part():
    return [
        ["file.new", {"units": "mm"}],
        ["variable.set", {"name": "len", "expr": "40 mm"}],
        ["variable.set", {"name": "w", "expr": mm(W)}],
        ["variable.set", {"name": "thick", "expr": mm(THICK)}],
        ["variable.set", {"name": "hole", "expr": mm(HOLE)}],
        ["variable.set", {"name": "r", "expr": "w / 2"}],
        # Drawn up +y, as the Jig draws its bars (its repro-strandbeest-leg-1: an end arc that ends
        # in the direction of a hole circle's seam broke the overlap test with the pin).
        ["sketch.create", {"name": "Outline", "plane": "xy"}],
        ["sketch.path", {"sketch": "Outline", "start": ["r", "0 mm"], "segments": [
            {"line": ["r", "len"]}, {"arc": ["-r", "len"], "center": ["0 mm", "len"], "clockwise": False},
            {"line": ["-r", "0 mm"]}, {"arc": "start", "center": ["0 mm", "0 mm"], "clockwise": False}]}],
        ["sketch.circle", {"sketch": "Outline", "center": ["0 mm", "0 mm"], "radius": "hole / 2"}],
        ["sketch.circle", {"sketch": "Outline", "center": ["0 mm", "len"], "radius": "hole / 2"}],
        ["feature.extrude", {"sketch": "Outline", "distance": "thick", "name": "Bar"}],
        ["body.appearance", {"body": "Bar", "color": "#C89B62", "roughness": 0.7}],
        ["variable.publish", {"name": "len", "label": "Length", "description": "Centre to centre of the pin holes",
                              "group": "Size", "order": 1, "min": "5 mm", "max": "300 mm", "unit": "mm"}],
        ["document.info", {"title": "Strandbeest bar", "description": "A flat bar with a pin hole at each end (3 mm plywood, 9 mm wide, holes for a 3 mm pin with 0.2 mm clearance); its length between the holes is a parameter.",
                           "author": "3DCraft Jigs", "licence": "CC-BY-4.0"}],
        ["file.save", {"path": BUILD + "/bar.3dcraft"}],
    ]


def pin_part():
    return [
        ["file.new", {"units": "mm"}],
        ["variable.set", {"name": "len", "expr": "10 mm"}],
        ["variable.set", {"name": "d", "expr": mm(PIN)}],
        ["feature.cylinder", {"radius": "d / 2", "height": "len", "name": "Pin"}],
        ["body.appearance", {"body": "Pin", "color": "#9AA3AD", "metallic": 1.0, "roughness": 0.35}],
        ["variable.publish", {"name": "len", "label": "Length", "group": "Size", "order": 1,
                              "min": "1 mm", "max": "500 mm", "unit": "mm"}],
        ["document.info", {"title": "Pin", "description": "A 3 mm round pin; its length is a parameter.",
                           "author": "3DCraft Jigs", "licence": "CC-BY-4.0"}],
        ["file.save", {"path": BUILD + "/pin.3dcraft"}],
    ]


def leg_asm(lay, deg):
    """One leg, undriven, its parts placed at crank angle deg."""
    path = "%s/leg.3dcraftasm" % BUILD
    P = leg(math.radians(deg))
    length = {n: ("hypot(Ja, Jl) * u" if n == "Frame" else "J%s * u" % letter) for n, letter, _, _ in BARS}
    s = [
        ["assembly.new", {"units": "mm"}],
        ["file.save", {"path": path}],
    ]
    for k, x in HOLY.items():
        s.append(["variable.set", {"name": "J" + k, "expr": repr(x)}])
    s += [
        ["variable.set", {"name": "crank", "expr": "15 mm"}],
        ["variable.set", {"name": "u", "expr": "crank / Jm"}],
        ["variable.set", {"name": "thick", "expr": mm(THICK)}],
        ["variable.set", {"name": "pitch", "expr": "thick + %s" % mm(GAP)}],
        ["variable.set", {"name": "stub", "expr": mm(STUB)}],
    ]
    for n, letter, p0, p1 in BARS:
        pos, rot = placement(P[p0], P[p1], lay[n])
        s.append(["instance.add", {"source": BUILD + "/bar.3dcraft", "name": n, "params": {"len": length[n]},
                                   "position": pos, "rotation": [round(v, 9) for v in rot]}])
    # Pins: at each joint, from the back face of its rearmost part to the front face of its foremost
    # (the axle O from `stub` behind the frame to the crank's front face), fixed to the rearmost part.
    hole_of = {}
    for n, _, p0, p1 in BARS:
        hole_of[(n, p0)] = HOLE1
        hole_of[(n, p1)] = HOLE2
    pins = []
    for J in "OABCDEFG":
        parts = [n for n, _, p0, p1 in BARS if J in (p0, p1)]
        if J == "O":
            parts = ["Frame", "Crank"]
        if J == "A":
            parts = ["Crank", "Web", "BarJ", "BarK"]
        lo = min(parts, key=lambda n: lay[n])
        hi = max(lay[n] for n in parts)
        span = "%d * pitch + thick" % (hi - lay[lo])
        if J == "O":
            lo = "Crank"
            span = "stub + pitch + thick"
        pins.append(("Pin" + J, J, lo, span, parts))
    for name, J, owner, span, _ in pins:
        z = -lay[owner] * PITCH + (STUB + PITCH if J == "O" else 0)
        s.append(["instance.add", {"source": BUILD + "/pin.3dcraft", "name": name, "params": {"len": span},
                                   "position": [round(P[J][0]), z, round(P[J][1])], "rotation": [90, 0, 0]}])
    # The frame is held where the leg stands: its axle hole on the world's y axis, the bar pointing
    # at B. Every frame of a bar or pin has its z along the part's +z, the world's -y; world/y has it
    # along +y, so the frame's edge is turned over onto it (flip false); the angle turns the bar from
    # the world's x (world/y's x axis) to B.
    s.append(["mate.add", {"kind": "fixed", "name": "Held", "a": "world/y", "b": "Frame/" + HOLE1,
                           "angle": "atan2(Jl, -Ja) - 180 deg"}])
    # The joints: revolutes between the rearmost part at a joint and each other part there; the offset
    # is the distance between their back faces along the parts' +z (towards the front).
    def joint(name, a, ja, b, jb):
        s.append(["mate.add", {"kind": "revolute", "name": name, "a": "%s/%s" % (a, hole_of[(a, ja)]),
                               "b": "%s/%s" % (b, hole_of[(b, jb)]), "offset": "%d * pitch" % (lay[b] - lay[a]), "flip": True}])
    joint("JointO", "Frame", "O", "Crank", "O")
    s.append(["mate.add", {"kind": "fixed", "name": "Throw", "a": "Crank/" + HOLE1, "b": "Web/" + HOLE1,
                           "offset": "%d * pitch" % (lay["Web"] - lay["Crank"]), "flip": True}])
    for J in "ABCDEFG":
        parts = sorted((n for n, _, p0, p1 in BARS if J in (p0, p1) and n != "Web"), key=lambda n: (lay[n], n))
        if J == "B":
            parts = ["Frame"] + [n for n in parts if n != "Frame"]
        for other in parts[1:]:
            joint("Joint%s_%s" % (J, other[-1] if other.startswith("Bar") else other), parts[0], J, other, J)
    for name, J, owner, span, _ in pins:
        if J == "O":
            # The axle's back end is `stub` behind the frame: its offset from the crank's back face.
            s.append(["mate.add", {"kind": "fixed", "name": "Fix" + name, "a": "Crank/" + HOLE1, "b": "%s/%s" % (name, PIN_BACK),
                                   "offset": "-(stub + pitch)", "flip": True}])
        else:
            s.append(["mate.add", {"kind": "fixed", "name": "Fix" + name, "a": "%s/%s" % (owner, hole_of[(owner, J)]),
                                   "b": "%s/%s" % (name, PIN_BACK), "flip": True}])
    s += [
        ["document.info", {"title": "Strandbeest leg (undriven)", "description": "Jansen's leg from one bar part and pins, its joints found by the assembly solver; the crank turns freely.",
                           "author": "3DCraft Jigs", "licence": "CC-BY-4.0"}],
        ["file.save", {"path": path}],
    ]
    return s, pins


def closed_form(s, prefix, th):
    """The Jig's circle intersections as assembly variables of the crank angle th (an expression):
    the foot G = (prefix + Gx, prefix + Gy) in the leg's plane."""
    v = []
    v.append((prefix + "Ax", "Lm * cos(%s)" % th))
    v.append((prefix + "Ay", "Lm * sin(%s)" % th))
    J = {"B": ("-La", "-Ll"), "A": (prefix + "Ax", prefix + "Ay")}

    def circ(j, P, r, Q, sq):
        n = prefix + j
        px, py, qx, qy = P[0], P[1], Q[0], Q[1]
        v.append((n + "dd", "sqrt((%s - %s)^2 + (%s - %s)^2)" % (qx, px, qy, py)))
        v.append((n + "al", "(%s^2 - %s^2 + %sdd^2) / (2 * %sdd)" % (r, sq, n, n)))
        v.append((n + "q", "1 - (%sal / %s)^2" % (n, r)))
        hh = "%s * sqrt(max(%sq, 0))" % (r, n)
        sg = "+" if BRANCH[j] > 0 else "-"
        v.append((n + "x", "%s + (%sal * (%s - %s) %s %s * (%s - %s)) / %sdd" % (px, n, qx, px, "-" if sg == "+" else "+", hh, qy, py, n)))
        v.append((n + "y", "%s + (%sal * (%s - %s) %s %s * (%s - %s)) / %sdd" % (py, n, qy, py, sg, hh, qx, px, n)))
        return (n + "x", n + "y")

    J["C"] = circ("C", J["A"], "Lj", J["B"], "Lb")
    J["D"] = circ("D", J["B"], "Ld", J["C"], "Le")
    J["E"] = circ("E", J["A"], "Lk", J["B"], "Lc")
    J["F"] = circ("F", J["D"], "Lf", J["E"], "Lg")
    J["G"] = circ("G", J["F"], "Lh", J["E"], "Li")
    for name, expr in v:
        s.append(["variable.set", {"name": name, "expr": expr}])
    return J["G"]


def driven(out, legs, lay, pins):
    """A parent assembly: legs [(instance, leg file, crank angle at rest, y)] as flexible subassemblies
    in a row, a drive shaft behind the first that t turns once, journals between them."""
    s = [
        ["assembly.new", {"units": "mm"}],
        ["file.save", {"path": out}],
    ]
    for k, x in HOLY.items():
        s.append(["variable.set", {"name": "J" + k, "expr": repr(x)}])
    s += [
        ["variable.set", {"name": "crank", "expr": "15 mm"}],
        ["variable.set", {"name": "u", "expr": "crank / Jm"}],
    ]
    for k in HOLY:
        s.append(["variable.set", {"name": "L" + k, "expr": "J%s * u" % k}])
    s += [
        ["variable.set", {"name": "thick", "expr": mm(THICK)}],
        ["variable.set", {"name": "pitch", "expr": "thick + %s" % mm(GAP)}],
        ["variable.set", {"name": "stub", "expr": mm(STUB)}],
        ["variable.set", {"name": "theta0", "expr": "%d deg" % legs[0][2]}],
        ["variable.set", {"name": "t", "expr": "0"}],
        # The crank angle of the first leg over the motion: one turn, counter-clockwise from the front.
        ["variable.set", {"name": "theta", "expr": "theta0 + 360 deg * t"}],
    ]
    for name, src, deg, y in legs:
        s.append(["instance.add", {"source": src, "name": name, "mode": "flexible", "position": [0, y, 0]}])
    # The drive shaft: 20 mm behind the first leg's axle, turning about the world's y axis.
    y0 = legs[0][3]
    s.append(["instance.add", {"source": BUILD + "/pin.3dcraft", "name": "DriveShaft", "params": {"len": "20 mm"},
                               "position": [0, y0 + STUB + 20, 0], "rotation": [90, 0, 0]}])
    for k in range(1, len(legs)):
        prev, nxt = legs[k - 1], legs[k]
        front = prev[3] - lay["Web"] * PITCH - THICK
        back = nxt[3] + STUB
        s.append(["instance.add", {"source": BUILD + "/pin.3dcraft", "name": "Journal%d" % k,
                                   "params": {"len": mm(front - back)}, "position": [0, front, 0], "rotation": [90, 0, 0]}])
    # Drive: turned over onto world/y (its +z is the world's -y), offset to its back end along +y.
    # The joint turns about +y, the crank angle about -y: minus. world/y's x axis is not the world's x;
    # the angle puts the joint's zero where the crank points along +x (found by tracing the foot: the
    # check compares every sample with the Jig's closed form, so a wrong zero cannot pass).
    s.append(["mate.add", {"kind": "revolute", "name": "Drive", "a": "world/y", "b": "DriveShaft/" + PIN_BACK,
                           "offset": "%s + stub + 20 mm" % mm(y0), "angle": "180 deg"}])
    s.append(["variable.set", {"name": "Drive_angle", "expr": "-theta"}])
    s.append(["mate.add", {"kind": "fixed", "name": "Coupled", "a": "%s/PinO/%s" % (legs[0][0], PIN_BACK),
                           "b": "DriveShaft/" + PIN_FRONT, "flip": True}])
    for k in range(1, len(legs)):
        prev, nxt = legs[k - 1], legs[k]
        step = nxt[2] - prev[2]
        s.append(["mate.add", {"kind": "fixed", "name": "Journal%dBack" % k, "a": "%s/Web/%s" % (prev[0], HOLE1_FRONT),
                               "b": "Journal%d/%s" % (k, PIN_BACK), "flip": True}])
        # The next leg's crank is `step` further round (counter-clockwise from the front: about -y,
        # the parts' +z).
        s.append(["mate.add", {"kind": "fixed", "name": "Journal%dFront" % k, "a": "Journal%d/%s" % (k, PIN_FRONT),
                               "b": "%s/PinO/%s" % (nxt[0], PIN_BACK), "angle": "%d deg" % step, "flip": True}])
    # The foot of each leg against the Jig's circle intersections at its crank angle: the foot pin's
    # centre, where its section by a plane across it (y at its middle) has its centroid.
    for idx, (name, src, deg, y) in enumerate(legs):
        th = "(theta + %d deg)" % (deg - legs[0][2])
        gx, gy = closed_form(s, "f%d" % (idx + 1), th)
        foot = [p for p in pins if p[0] == "PinG"][0]
        owner = foot[2]
        mid = y - lay[owner] * PITCH - (1 * PITCH + THICK) / 2
        s.append(["variable.measure", {"name": "g%dx" % (idx + 1), "measure": "sectionCentroid", "of": "%s/PinG" % name,
                                       "plane": "zx", "offset": mm(mid), "axis": "x"}])
        s.append(["variable.measure", {"name": "g%dz" % (idx + 1), "measure": "sectionCentroid", "of": "%s/PinG" % name,
                                       "plane": "zx", "offset": mm(mid), "axis": "z"}])
        s.append(["assert.add", {"name": "%s's foot is where the Jig's circle intersections put it" % name, "measure": "value",
                                 "expr": "hypot(g%dx - %s, g%dz - %s)" % (idx + 1, gx, idx + 1, gy), "max": "0.001 mm"}])
    return s


def main():
    lay = layering()
    files = {}
    files["01-bar.json"] = bar_part()
    files["02-pin.json"] = pin_part()
    files["03-leg.json"], pins = leg_asm(lay, 0)
    depth = lay["Web"] * PITCH + THICK
    one = driven(LEG_OUT, [("Leg", BUILD + "/leg.3dcraftasm", 0, 0.0)], lay, pins)
    one += [
        ["assert.add", {"name": "No part overlaps another", "measure": "overlap", "of": {"kind": "body"}, "is": False}],
        ["document.info", {"title": "Strandbeest leg (assembly)",
                           "description": "Theo Jansen's leg built from one bar part and pins, its joints found by 3DCraft's assembly solver instead of the Jig's circle intersections; a drive shaft turns the crank over the timeline t, and the foot's path is checked against the Jig's.",
                           "author": "3DCraft Jigs", "licence": "CC-BY-4.0", "tags": ["assembly", "linkage", "strandbeest", "motion"]}],
        ["assembly.pack", {}],
        ["file.save", {"path": LEG_OUT}],
    ]
    files["04-strandbeest-leg.json"] = one
    spacing = depth + STUB + 6.0
    legs = [("Leg%d" % (k + 1), BUILD + "/leg.3dcraftasm", 90 * k, -k * spacing) for k in range(4)]
    walker = driven(WALKER_OUT, legs, lay, pins)
    walker += [
        # Each leg is the one strandbeest-leg.3dcraftasm checks over a whole turn; here the crankshaft
        # against every part (3DCraft measures at most 500 pairs at once).
        ["assert.add", {"name": "The crankshaft runs clear of every part", "measure": "overlap",
                        "of": ["DriveShaft"] + ["Journal%d" % k for k in range(1, len(legs))], "to": {"kind": "body"}, "is": False}],
        ["document.info", {"title": "Strandbeest walker, four legs (assembly)",
                           "description": "Four Strandbeest legs as flexible subassemblies on one crankshaft, a quarter turn apart: the drive shaft and the journals between the legs' crank throws; t turns the crankshaft once and every foot follows the Jig's path at its phase.",
                           "author": "3DCraft Jigs", "licence": "CC-BY-4.0", "tags": ["assembly", "linkage", "strandbeest", "motion"]}],
        ["assembly.pack", {}],
        ["file.save", {"path": WALKER_OUT}],
    ]
    files["05-strandbeest-walker.json"] = walker
    for old in os.listdir(HERE):
        if old[:2].isdigit() and old.endswith(".json") and old not in files:
            os.remove(os.path.join(HERE, old))
    for name, steps in files.items():
        with open(os.path.join(HERE, name), "w") as f:
            f.write("[\n" + ",\n".join(json.dumps(c) for c in steps) + "\n]\n")
    check = [
        {"file": LEG_OUT,
         "at_rest": {"dof": 0},
         "motion": [{"t": [0, 1], "samples": 73}],
         "traces": [{"name": "Foot", "point": "Leg/PinG/" + PIN_BACK, "samples": 73, "svg": True}],
         "foot": [{"trace": "Foot", "crank0_deg": 0, "turn_deg": 360, "tol": 0.001}],
         "renders": [0, 0.25, 0.5], "view": "front", "replay": {"frames": 49}},
        {"file": WALKER_OUT,
         "at_rest": {"dof": 0},
         "motion": [{"t": [0, 1], "samples": 25}],
         "traces": [{"name": "Foot %d" % (k + 1), "point": "Leg%d/PinG/%s" % (k + 1, PIN_BACK), "samples": 73, "svg": k == 0}
                    for k in range(4)],
         "foot": [{"trace": "Foot %d" % (k + 1), "crank0_deg": 90 * k, "turn_deg": 360, "tol": 0.001} for k in range(4)],
         "renders": [0, 0.25, 0.5], "replay": {"frames": 49}},
    ]
    with open(os.path.join(HERE, "check.json"), "w") as f:
        json.dump(check, f, indent=1)
        f.write("\n")
    print("layers:", lay)


if __name__ == "__main__":
    main()
