"""Shared by the gen.py of rack-panel and rack-cabinet: the 19-inch rack dimensions (EIA-310-D,
IEC 60297-3-100) and the sheet stock table, as numbers and 3DCraft commands, so that a panel from one
Jig always bolts onto the rails of a cabinet from the other.

Sources (numbers only, read from the public descriptions; the standards themselves are sold by IHS/IEC):
- EIA-310-D (ECIA, 1992), "Cabinets, Racks, Panels, and Associated Equipment": a 19 in (482.6 mm) panel,
  a rack unit U of 1.75 in (44.45 mm), mounting holes on 18.312 in (465.1 mm) centres, the hole pattern
  repeating every U with spacings of 1/2, 5/8, 5/8 in (holes at 1/4, 7/8 and 1 1/2 in above the U's
  boundary), and an opening of at least 17.72 in (450 mm) between the rails. As restated by
  RackSolutions, "What is EIA-310" (help.racksolutions.com/hc/en-us/articles/10431608060692) and by
  IBM, "Rack installation specifications for racks not purchased from IBM"
  (ibm.com/docs/POWER9/p9had/p9had_oemrack.htm: 450 mm minimum opening, holes 465 +- 1.6 mm,
  square holes 9.5 mm).
- IEC 60297-3-100: a front panel is n x 44.45 mm - 0.8 mm high (43.65 mm for 1U, 88.1 mm for 2U), the
  0.8 mm being the clearance between stacked panels; the panel sits centred on its U boundaries.
- Fasteners: M6 cage nuts in 9.5 mm square holes; ISO 273 (medium series) clearance holes, 6.6 mm for
  M6, 4.5 mm for M4; ISO 261 / ISO 2306 tap drill 5.0 mm for M6 x 1.

The sheet stock (min inner bend radius, K-factor, min flange, hole to bend):
- Min inner radius: DIN 6935 table 1 for cold-formed steel (DC01, EN 10130; Rm <= 390 MPa): 1.6 mm for
  1.5 mm sheet, 2.5 mm for 2 mm sheet (the row "over 1.5 to 2.5 mm"). Aluminium 5052-H32: 1 t for
  2 mm and 1.5 t for 3 mm, the Aluminum Association's 90-degree bend radii (Aluminum Standards and Data)
  as suppliers restate them.
- K-factor: DIN 6935 (a standard for steel, used here for 5052 as an approximation): its correction factor k = 0.65 + 0.5 log10(r / s) (for r / s < 5) puts the neutral
  fibre at r + k s / 2, so K = k / 2; computed in the document from the row's radius and thickness.
- Min flange 4 t, holes at least 2.5 t + r from a bend: the rules of thumb of Protolabs' sheet metal
  design guide (protolabs.com/resources/design-tips/sheet-metal), measured here (conservatively) from
  the bend's tangent line.
"""

U = 44.45                 # mm, one rack unit (1.75 in)
PANEL_W = 482.6           # mm, the panel's width (19 in)
PANEL_GAP = 0.8           # mm, a panel is n U - 0.8 mm high (IEC 60297-3-100)
HOLE_X = 465.1 / 2        # mm, the mounting holes' centres from the rack's centre line (18.312 in apart)
HOLES_IN_U = (6.35, 22.225, 38.1)   # mm, the three holes of a U above its lower boundary
HOLE_NAMES = ("hole1", "hole2", "hole3")   # the same as document variables (spec_variables)
OPENING = 450.0           # mm, the clear opening between the rails (17.72 in)
CAGE_HOLE = 9.5           # mm, square hole for a cage nut
M6_TAP = 5.0              # mm, tap drill for M6 x 1
M6_CLEAR = 6.6            # mm, ISO 273 medium clearance hole for M6
M6_SLOT_L = 10.0          # mm, a panel slot's length (lateral play of 3.4 mm)
M4_CLEAR = 4.5            # mm, ISO 273 medium clearance for M4 (handle screws)
HANDLE_IN = 19.05         # mm, handle screws 3/4 in inboard of the mounting holes
# The cabinet: every rack-cabinet has this clear width between its sides, and a panel must leave
# PANEL_SIDE_CLEAR to each side (fingers, a panel's tolerance).
CAB_INNER_W = 520.0
PANEL_SIDE_CLEAR = 4.0
RAIL_DEPTH = 40.0         # mm, the depth a rail's flange reaches back (the reference rail of rack-panel)

# Sheet stock: name, thickness, the bend radius used (= the minimum inner radius of the row's source).
STOCK = [
    ("Aluminium 5052-H32 2 mm", 2.0, 2.0),
    ("Aluminium 5052-H32 3 mm", 3.0, 4.5),
    ("Steel DC01 1.5 mm", 1.5, 1.6),
    ("Steel DC01 2 mm", 2.0, 2.5),
]


def unit(v):
    return "%.6g mm" % v


def stock_commands(default="1"):
    """The stock table, the `stock` choice and the variables every sheet-metal part uses: t, R (the
    inner radius bent), minR (the table's minimum), K (DIN 6935), minFlange, holeMin."""
    return [
        ["table.set", {"name": "stocks",
                       "columns": ["stock", {"name": "t", "unit": "mm"}, {"name": "minR", "unit": "mm"}],
                       "rows": [[n, t, r] for n, t, r in STOCK]}],
        ["variable.set", {"name": "stock", "expr": default}],
        ["variable.set", {"name": "t", "expr": "stocks[stock].t"}],
        ["variable.set", {"name": "minR", "expr": "stocks[stock].minR"}],
        ["variable.set", {"name": "R", "expr": "minR"}],
        ["variable.set", {"name": "K", "expr": "(0.65 + 0.5 * log10(R / t)) / 2"}],
        ["variable.set", {"name": "minFlange", "expr": "4 * t"}],
        ["variable.set", {"name": "holeMin", "expr": "2.5 * t + R"}],
    ]


def spec_variables():
    """The spec as document variables (so assertions name them)."""
    return [["variable.set", {"name": n, "expr": e}] for n, e in [
        ("U", unit(U)), ("panelW", unit(PANEL_W)), ("panelGap", unit(PANEL_GAP)), ("holeX", "465.1 mm / 2"),
        ("hole1", unit(HOLES_IN_U[0])), ("hole2", unit(HOLES_IN_U[1])), ("hole3", unit(HOLES_IN_U[2])),
        ("opening", unit(OPENING)), ("cabInnerW", unit(CAB_INNER_W)), ("sideClear", unit(PANEL_SIDE_CLEAR)),
    ]]


def sheet_rules(part=None, flanged="1", relieved=True, label=None, holes=True):
    """The material table's rules on sheet-metal parts, as assertions: `part` names one feature, None
    every sheet-metal part of the document; `flanged` is the condition under which there are bends."""
    label = label or part or "sheet metal"

    def one(name, measure, **kw):
        p = {"name": "%s: %s" % (label, name), "measure": measure}
        if part is not None:
            p["of"] = part
        p.update(kw)
        return ["assert.add", p]
    out = [
        one("bend radius at least the stock's minimum", "bendRadius", min="if(%s, minR, 0 mm)" % flanged),
        one("flanges at least 4 t (stock)", "flangeLength", min="if(%s, minFlange, 0 mm)" % flanged),
    ]
    if holes:
        out.append(one("holes at least 2.5 t + r from a bend", "holeToBend", min="if(%s, holeMin, 0 mm)" % flanged))
    if relieved:
        out.append(one("every corner of two bends relieved", "relief", **{"is": True}))
    return out


def rail_hole_centres(n_max, z0="0 mm"):
    """The z of every rail hole of n_max units above z0 (a U boundary), as expressions: the spec's
    pattern, unit by unit."""
    out = []
    for k in range(n_max):
        for h in HOLE_NAMES:
            out.append((k, "(%s) + %d * U + %s" % (z0, k, h)))
    return out


class Sketch:
    """A sketch being written, counting its entity ids the way 3DCraft gives them (one counter for
    points and curves, in the order the commands add them; constraints count apart), so that flanges
    and patterns can name curves. Every coordinate is an expression; `cmds` is the command list."""

    def __init__(self, name, plane, offset="0 mm", when=None):
        self.name, self.n, self.cmds, self.pats = name, 0, [], 0
        self.cmds.append(["sketch.create", {"name": name, "plane": plane, "offset": offset}])
        if when is not None:
            self.cmds.append(["feature.when", {"feature": name, "expr": when}])

    def _ids(self, k):
        out = ["e%d" % (self.n + i + 1) for i in range(k)]
        self.n += k
        return out

    def polyline(self, points):
        """A closed polyline: returns its lines, line i running from point i to point i + 1."""
        self.cmds.append(["sketch.polyline", {"sketch": self.name, "closed": True, "points": points}])
        self._ids(len(points))
        return self._ids(len(points))

    def circle(self, centre, r):
        self.cmds.append(["sketch.circle", {"sketch": self.name, "center": centre, "radius": r}])
        return self._ids(2)[1]

    def slot(self, cu, cv, half, r):
        """A slot along the sketch's v axis about (cu, cv): straight part 2 half, ends of radius r.
        Returns its four curves."""
        start, seg = slot(cu, cv, half, r)
        self.cmds.append(["sketch.path", {"sketch": self.name, "start": start, "segments": seg}])
        ids = self._ids(12)       # start; line: end, line; arc: end, centre, arc, through; line; arc: centre, arc, through
        return [ids[2], ids[5], ids[8], ids[10]]

    def square(self, cu, cv, s):
        return self.polyline(square(cu, cv, s))

    def pattern(self, entities, **kw):
        """A sketch.pattern of seed curves (kw: count, step, count2, step2 as expressions). Patterns come
        after every primitive (their ids are counted apart)."""
        p = {"sketch": self.name, "entities": entities}
        p.update(kw)
        self.cmds.append(["sketch.pattern", p])


def slot(cu, cv, half, r):
    """A slot along the sketch's v axis about (cu, cv) (expressions): straight part 2 * half, ends of
    radius r. Returns the sketch.path segments and start (lines and arcs: 4 curves)."""
    def p(du, dv):
        return ["(%s) + (%s)" % (cu, du), "(%s) + (%s)" % (cv, dv)]
    start = p("-(%s)" % r, "-(%s)" % half)
    seg = [{"line": p("-(%s)" % r, half)},
           {"arc": p(r, half), "through": p("0 mm", "(%s) + (%s)" % (half, r))},
           {"line": p(r, "-(%s)" % half)},
           {"arc": "start", "through": p("0 mm", "-(%s) - (%s)" % (half, r))}]
    return start, seg


def square(cu, cv, s):
    """A square of side s about (cu, cv): polyline points."""
    h = "(%s) / 2" % s
    return [["(%s) - %s" % (cu, h), "(%s) - %s" % (cv, h)], ["(%s) + %s" % (cu, h), "(%s) - %s" % (cv, h)],
            ["(%s) + %s" % (cu, h), "(%s) + %s" % (cv, h)], ["(%s) - %s" % (cu, h), "(%s) + %s" % (cv, h)]]
