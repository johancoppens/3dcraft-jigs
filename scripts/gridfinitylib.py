"""Shared by the gen.py of gridfinity-bin and gridfinity-baseplate: the Gridfinity dimensions and the
profiles built from them, as 3DCraft commands, so that a bin from one Jig always seats in a baseplate
from the other.

Gridfinity is Zack Freedman's open modular storage system (Voidstar Lab, 2022, MIT licence). The numbers
below are the ones the community writes down: the unofficial specification
(github.com/gridfinity-unofficial/specification, gridfinity.xyz/specification) gives the 42 x 42 x 7 mm
unit, the 41.5 mm bin and the 6 x 2 mm magnets; the profiles, hole sizes and the weighted baseplate's
pockets are the values in kennetek's gridfinity-rebuilt-openscad (MIT, src/core/standard.scad and
src/core/gridfinity-baseplate.scad), read as numbers; no code was taken from it.

Every profile is a list of (height, inset) pairs: the inset is measured in from the outline at the top
of the profile (the bin's 41.5 mm square with a 3.75 mm corner radius, the baseplate's 42 mm opening with
a 4 mm radius), so a section's half size is half the top size minus the inset and its corner radius the
top radius minus the inset: the corners stay concentric, as an offset curve does.
"""

GRID = 42.0            # mm, the grid pitch (GRID_DIMENSIONS_MM)
UNIT_H = 7.0           # mm, the height unit
BIN_TOP = 41.5         # mm, a bin's base at its top: 0.5 mm less than the grid (BASE_TOP_DIMENSIONS)
BIN_R = 3.75           # mm, its outer corner radius (BASE_TOP_RADIUS)
# The bin's base (foot) profile from its bottom up: a 0.8 mm 45 deg chamfer, 1.8 mm straight up and a
# 2.15 mm 45 deg chamfer, 4.75 mm tall and 2.95 mm in at the bottom (BASE_PROFILE).
FOOT = [(0.0, 2.95), (0.8, 2.15), (2.6, 2.15), (4.75, 0.0)]
FOOT_H = 4.75
BASE_H = 7.0           # the base with the bridge that ties the feet together: the inside starts here
# The baseplate's socket from the bottom of its 5 mm up: 0.35 mm straight at the socket's narrowest
# (the room left under a seated bin's profile), then a 0.7 mm 45 deg chamfer, 1.8 mm straight up and a
# 2.15 mm 45 deg chamfer to the 42 mm opening at the top (_BASEPLATE_PROFILE on BASEPLATE_HEIGHT 5).
PLATE_R = 4.0          # the opening's corner radius (BASEPLATE_OUTER_RADIUS)
SOCKET = [(0.0, 2.85), (0.35, 2.85), (1.05, 2.15), (2.85, 2.15), (5.0, 0.0)]
SOCKET_H = 5.0
# The openings of neighbouring cells meet in a knife edge at the top. Here the top is cut 0.1 mm lower,
# leaving a 0.2 mm flat on every ridge (0.1 mm at a plate's edge), so neighbouring openings do not touch
# along a line; a seated bin's base ends 0.15 mm below that flat, nothing it rests on changes.
RIDGE_CUT = 0.1
# A bin seated in a socket stands on the socket's floor: its 0.8 mm bottom chamfer then lies in the
# plane of the socket's 0.7 mm one and its top chamfer in the plane of the socket's top one (both 45 deg);
# its straight part is 0.25 mm from the socket's (37.2 mm in a 37.7 mm), as its top is from the opening.
SEAT_SIDE_GAP = 0.25
# The stacking lip at the top of a bin's wall, from its inner tip down and out: 0.7 mm at 45 deg, 1.8 mm
# straight, 1.9 mm at 45 deg (4.4 mm tall, 2.6 mm deep; STACKING_LIP_LINE), on a 1.2 mm straight support
# (STACKING_LIP_SUPPORT_HEIGHT) and a 45 deg slope back to the wall.
LIP_H = 4.4
LIP_D = 2.6
LIP_SUPPORT = 1.2
# Holes in the base, at the four corners of every unit, 8 mm in from its sides (d_hole_from_side):
MAGNET_D = 6.5         # for 6 x 2 mm disc magnets (MAGNET_HOLE_RADIUS 6.5 / 2)
MAGNET_DEPTH = 2.4     # magnet 2 mm and two 0.2 mm layers (MAGNET_HOLE_DEPTH)
SCREW_D = 3.0          # M3, in the bin's base (SCREW_HOLE_RADIUS 3 / 2), 6 mm deep
SCREW_DEPTH = 6.0
HOLE_IN = 8.0
# Baseplate: M3 clearance hole with a countersink for a flat head (d_screw 3.35; ISO 10642 head 6 mm).
PLATE_SCREW_D = 3.35
PLATE_SCREW_HEAD = 6.4
# The weighted baseplate's pocket from below (bp_*): a 21.4 mm square 4 mm deep in a 6.4 mm bottom,
# with four 8.5 mm round-ended channels 2 mm deep reaching 10 mm out (centred) and 4.25 mm long.
WEIGHT_BOTTOM = 6.4
WEIGHT_SQ = 21.4
WEIGHT_DEPTH = 4.0
CHAN_W = 8.5
CHAN_L = 4.25
CHAN_AT = 10.0
CHAN_DEPTH = 2.0
# The label tab (TAB_POLYGON): 15.85 mm deep, its support at 36 deg, with 1.2 mm straight at its front.
TAB_DEPTH = 15.85
TAB_ANGLE = 36.0
TAB_FRONT = 1.2
DIVIDER = 1.2          # d_div, a divider's thickness
MIN_WALL = 0.95        # d_wall, the thinnest wall


def num(v):
    return "%g mm" % v


def rrect(name, z, hx, hy, r, cx="0 mm", cy="0 mm", plane="xy"):
    """A rounded rectangle about (cx, cy) on a plane parallel to xy at height z: half sizes hx, hy and
    corner radius r (all expressions)."""
    def p(x, y):
        return ["(%s) + (%s)" % (cx, x), "(%s) + (%s)" % (cy, y)]
    X, Y, R = "(%s)" % hx, "(%s)" % hy, "(%s)" % r
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
    return [["sketch.create", {"name": name, "plane": plane, "offset": z}],
            ["sketch.path", {"sketch": name, "start": p(X, "-%s + %s" % (Y, R)), "segments": seg}]]


def profile_loft(name, profile, top, radius, z0, cx="0 mm", cy="0 mm", when=None):
    """A ruled loft through a profile's sections (rounded squares), its bottom at z0 (an expression)."""
    s, names = [], []
    for i, (z, inset) in enumerate(profile):
        n = "%s%d" % (name, i)
        names.append(n)
        h = num(top / 2 - inset)
        s += rrect(n, "(%s) + %s" % (z0, num(z)), h, h, num(radius - inset), cx, cy)
    loft = {"sections": names, "ruled": True, "name": name}
    if when is not None:
        loft["when"] = when
    s.append(["feature.loft", loft])
    return s


def foot(name, z0="0 mm", cx="0 mm", cy="0 mm", when=None):
    """One unit's foot of a bin: the base profile, its bottom at z0, centred on (cx, cy)."""
    return profile_loft(name, FOOT, BIN_TOP, BIN_R, z0, cx, cy, when)


def socket_cutter(name, z0, below, cx="0 mm", cy="0 mm", when=None):
    """The opening of one baseplate cell, to subtract: the socket profile with its bottom at z0, carried
    straight down by `below` (mm, a number) and cut RIDGE_CUT under its top."""
    prof = [(-below, SOCKET[0][1])] + SOCKET[1:-1]
    zt, it = SOCKET[-2]
    z1, _ = SOCKET[-1]
    # The 45 deg chamfer stopped RIDGE_CUT under its top, then carried up 1 mm past the plate's top.
    prof.append((z1 - RIDGE_CUT, RIDGE_CUT))
    prof.append((z1 - RIDGE_CUT + 1.0, RIDGE_CUT))
    return profile_loft(name, prof, GRID, PLATE_R, z0, cx, cy, when)


def area_rrect_perimeter(size, r):
    import math
    return 4 * (size - 2 * r) + 2 * math.pi * r


def foot_side_area():
    """The area of one foot's sides (its chamfers and straight part, not its bottom), in mm^2: each piece
    is a frustum of the rounded square, its area the mean of the two perimeters times the slant height."""
    import math
    a = 0.0
    for (z0, i0), (z1, i1) in zip(FOOT, FOOT[1:]):
        p0 = area_rrect_perimeter(BIN_TOP - 2 * i0, BIN_R - i0)
        p1 = area_rrect_perimeter(BIN_TOP - 2 * i1, BIN_R - i1)
        slant = math.hypot(z1 - z0, i0 - i1)
        a += (p0 + p1) / 2 * slant
    return a


def foot_bottom_area():
    """The area of one foot's bottom face, in mm^2: a 35.6 mm square with 0.8 mm corners."""
    import math
    s, r = BIN_TOP - 2 * FOOT[0][1], BIN_R - FOOT[0][1]
    return s * s - (4 - math.pi) * r * r
