#!/usr/bin/env python3
"""Writes build.json of the sea-kayak Jig:  python3 -I gen.py > build.json

A multichine stitch-and-glue sea kayak in okoume plywood, Greenland style (after the character of
Ken Taylor's 1959 Igdlorssuit kayak and the boats it led to; the lines are our own).

The hull
--------
x runs along the boat (stern -L/2, bow +L/2), y to starboard, z up, z = 0 at the keel's lowest point.
A station is given by eta in [0, 1] (0 the stern tip, 1 the bow tip), a skewed version of
xi = x / L + 1/2:  eta = xi + s xi (1 - xi), so the widest station (eta = 1/2) lies at xi = xmax.

Every hull panel is a generalised cylinder: in every station it is a straight line at the same angle
theta_j (the panel's flare). Such a surface is exactly developable (its rulings are parallel), and its
flat development is known in closed form up to one arc-length integral:
    flat X = integral sqrt(1 + g'(x)^2) dx,  g = P(x) . n_j  (the panel's offset along its normal)
    flat Y = P(x) . d_j  (and + the panel's width for the other edge)
with d_j = (cos theta_j, sin theta_j) in the station plane and n_j its normal. A panel j of width
W_j F_j(eta) runs from chine j to chine j + 1; F_j = (4 eta (1 - eta))^p_j, p_j larger for the bottom
panels, so they taper out first and the ends become a fine V. At the widest station the chines lie on a
quarter ellipse (half beam B/2, depth D). The keel rises to the rocker at each tip:
z0 = rA u^4 + rC u^5, u = 2 eta - 1. The deck is one panel a side at the crown angle, from the sheer
to a ridge on the centre line.

Everything is a variable of the published inputs, so the form regenerates any kayak of the family:
the stations of the loft, the Clenshaw-Curtis weights of the hydrostatic integrals, the Newton steps that
find the waterline, the flat panels' outlines and the trim (where the seat goes so the boat floats level).
"""
import json
import math

N = 24          # loft stations = Clenshaw-Curtis nodes along the hull
ETAE = 0.03     # where the plywood hull ends and the hardwood tips begin
ETAM = 0.012    # the tips' middle section
ETAT = 0.004    # the tips' far end
NEWTON = 4      # Newton steps for the waterline
BISECT = 5      # bisection steps for the stability capacity
NR = 4          # rocker exponent: z0 = rA u^4 + rC u^5
GAP = 30        # mm between flat panels on the floor
FLOOR = -60     # mm: z of the floor the flat panels lie on, just below the keel

OKOUME, WALNUT, CREAM, PETROL, OCHRE, BRASS, COPPER = "#D9B98A", "#7A5638", "#E8DFCC", "#2E7D7A", "#D4A24C", "#B8954A", "#B87350"
DECKC = COPPER   # a sapele-coloured deck over the okoume hull


def V(name, expr):
    return ["variable.set", {"name": name, "expr": expr}]


def num(v):
    return repr(round(v, 12))


steps = []
S = steps.append

# ---------------------------------------------------------------- inputs
inputs = [
    ("L", "5300 mm"), ("B", "545 mm"), ("D", "190 mm"), ("crown", "22 deg"),
    ("rockB", "300 mm"), ("rockS", "240 mm"), ("xmax", "0.47"), ("chines", "3"), ("form", "2"),
    ("mPad", "80"), ("hPad", "1780 mm"), ("payload", "5"), ("water", "1"),
    ("tHull", "4 mm"), ("tDeck", "3 mm"), ("cockL", "800 mm"), ("cockW", "420 mm"), ("hatches", "1"),
]
for n_, e in inputs:
    S(V(n_, e))
S(["table.set", {"name": "forms", "columns": ["form", "pb", "pt"],
                 "rows": [["Fine", 2.6, 1.1], ["Moderate", 2.2, 1.0], ["Full", 1.8, 1.0]]}])
S(["table.set", {"name": "waters", "columns": ["water", "rho"],
                 "rows": [["Sea water", 1025], ["Fresh water", 1000]]}])

# ---------------------------------------------------------------- constants (sources in the README)
S(V("rhoPly", "500"))      # okoume plywood, kg/m^3 (CLC: a 4 mm 4 x 8 ft sheet weighs 13 lb)
S(V("rhoWood", "600"))     # hardwood tips, sheer clamps and coaming, kg/m^3
S(V("glassHull", "0.80"))  # kg/m^2: 6 oz glass outside with its epoxy and fill coats, inside coat, seam tape
S(V("glassDeck", "0.55"))  # kg/m^2: 4 oz glass outside with its epoxy, inside coat
S(V("fittings", "2.5"))    # kg: seat pad, back band, hatch rims and covers' rubber, deck lines
S(V("cgUp", "254 mm"))    # paddler's CG above the seat (Sea Kayaker's convention: 10 in)
S(V("cgFwd", "254 mm"))   # ... and 10 in ahead of the seat back
S(V("clampA", "20 mm"))    # sheer clamp: depth along the topside
S(V("clampB", "12 mm"))    # ... and thickness

# ---------------------------------------------------------------- the hull's design curves
S(V("rho", "waters[water].rho"))
S(V("pb", "forms[form].pb"))
S(V("pt", "forms[form].pt"))
S(V("n", "chines + 1"))
S(V("spring", "0.8"))   # sheer spring: the upper panels stay wider towards the ends (F = G^p (1 + sp (1 - G)))
S(V("s", "(0.5 - xmax) / (xmax * (1 - xmax))"))
S(V("rA", "(rockB + rockS) / 2"))
S(V("rC", "(rockB - rockS) / 2"))
S(V("tc", "tan(crown)"))
S(V("cotd", "1 / tan(crown)"))
S(V("sd", "sin(crown)"))
S(V("cd", "cos(crown)"))
for j in range(4):
    a, b_ = f"90 deg * {j} / n", f"90 deg * {j + 1} / n"
    S(V(f"dy{j}", f"if(n > {j}, B / 2 * (sin({b_}) - sin({a})), 0 mm)"))
    S(V(f"dz{j}", f"if(n > {j}, D * (cos({a}) - cos({b_})), 0 mm)"))
    S(V(f"W{j}", f"sqrt(dy{j}^2 + dz{j}^2)"))
    S(V(f"c{j}", f"if(n > {j}, dy{j} / W{j}, 0.6)"))
    S(V(f"s{j}", f"if(n > {j}, dz{j} / W{j}, 0.8)"))
    S(V(f"k{j}", f"c{j} / s{j}"))
    S(V(f"p{j}", f"if(n > {j}, pb + (pt - pb) * {j} / (n - 1), 1)"))
    S(V(f"sp{j}", f"if(n > {j}, spring * {j} / (n - 1), 0)"))
    S(V(f"th{j}", f"atan2(s{j}, c{j})"))
# the topside (last hull panel) whatever the number of chines
S(V("cT", "choose(n - 1, c1, c2, c3)"))
# coefficients of the normal offsets' derivatives: panel j's normal (-s_j, c_j) against panel m's
# direction (c_m, s_m); the deck's normal (sd, cd) (up to sign)
for j in range(4):
    for m in range(j):
        S(V(f"e{j}{m}", f"W{m} * (c{j} * s{m} - s{j} * c{m})"))
for m in range(4):
    S(V(f"eD{m}", f"W{m} * (sd * c{m} + cd * s{m})"))

S(V("sT", "choose(n - 1, s1, s2, s3)"))

# Clenshaw-Curtis weights on [-1, 1] for the N + 1 cosine-spaced stations
CC = []
for k in range(N + 1):
    c = 1 if k in (0, N) else 2
    acc = 0.0
    for j in range(1, N // 2 + 1):
        bj = 1 if j == N // 2 else 2
        acc += bj / (4 * j * j - 1) * math.cos(2 * j * k * math.pi / N)
    CC.append(c / N * (1 - acc))
ETA = [ETAE + (1 - 2 * ETAE) * (1 - math.cos(math.pi * i / N)) / 2 for i in range(N + 1)]
# The hydrostatic integrals have kinks (where the waterline crosses a chine, and at its ends): they get a
# finer grid of their own, NH + 1 cosine-spaced stations, with their own Clenshaw-Curtis weights.
NH = 48
CCH = []
for k in range(NH + 1):
    c = 1 if k in (0, NH) else 2
    acc = 0.0
    for j in range(1, NH // 2 + 1):
        bj = 1 if j == NH // 2 else 2
        acc += bj / (4 * j * j - 1) * math.cos(2 * j * k * math.pi / NH)
    CCH.append(c / NH * (1 - acc))
ETAH = [ETAE + (1 - 2 * ETAE) * (1 - math.cos(math.pi * i / NH)) / 2 for i in range(NH + 1)]
LG = [str(i) for i in range(N + 1)]          # the loft's stations
HG = [f"h{i}" for i in range(NH + 1)]        # the hydrostatics' stations
GL3 = [(-math.sqrt(0.6), 5 / 9), (0.0, 8 / 9), (math.sqrt(0.6), 5 / 9)]
GL5 = [(-0.9061798459386640, 0.2369268850561891), (-0.5384693101056831, 0.4786286704993665),
       (0.0, 0.5688888888888889), (0.5384693101056831, 0.4786286704993665),
       (0.9061798459386640, 0.2369268850561891)]


class Eta:
    """eta as a number (a fixed station) or as an expression (a station that moves)."""

    def __init__(self, e):
        self.e = e
        self.isnum = not isinstance(e, str)

    def s(self):
        return num(self.e) if self.isnum else f"({self.e})"

    def u(self, k):
        return num((2 * self.e - 1) ** k) if self.isnum else f"(2 * {self.s()} - 1)^{k}"

    def G(self):
        return num(4 * self.e * (1 - self.e)) if self.isnum else f"(4 * {self.s()} * (1 - {self.s()}))"

    def dG(self):
        return num(4 - 8 * self.e) if self.isnum else f"(4 - 8 * {self.s()})"


def xi_of(et):
    return f"2 * {et.s()} / ((1 + s) + sqrt((1 + s)^2 - 4 * s * {et.s()}))"


def jac_of(et):
    return f"L / (1 + s * (1 - 2 * ({xi_of(et)})))"


def gprime(j, et):
    """d/deta of panel j's offset along its normal, g = P . n_j (4: the deck), at eta (Eta)."""
    dz0 = f"(rA * {2 * NR} * {et.u(NR - 1)} + rC * {2 * (NR + 1)} * {et.u(NR)})"
    G, dG = et.G(), et.dG()
    dF = [f"(p{m} * pow({G}, p{m} - 1) * (1 + sp{m} * (1 - {G})) - sp{m} * pow({G}, p{m}))" for m in range(4)]
    if j < 4:
        terms = [f"c{j} * {dz0}"] + [f"e{j}{m} * {dF[m]} * {dG}" for m in range(j)]
    else:
        terms = [f"cd * {dz0}"] + [f"eD{m} * {dF[m]} * {dG}" for m in range(4)]
    return "(" + " + ".join(terms) + ")"


def arc(j, et, jac):
    """sqrt(1 + g'(x)^2) of panel j (4: the deck) at eta, with jac = dx/deta there."""
    return f"sqrt(1 + ({gprime(j, et)} / ({jac}))^2)"


def station_vars(tag, eta, weight=None, arcs=False, hydro=False):
    """One station: X, the chine points Yk, Zk (k = 0..4; 4 is the sheer), the ridge ZR, the panel
    widths w0..w3 and wD, and with arcs the arc factors S0..S3, SD; with weight its quadrature weight."""
    et = Eta(eta)
    out = [V(f"X{tag}", f"(({xi_of(et)}) - 0.5) * L"),
           V(f"Z0{tag}", f"rA * {et.u(NR)} + rC * {et.u(NR + 1)}")]
    if arcs or (weight is not None and not hydro):
        out.append(V(f"jac{tag}", f"L / (1 - 2 * s * X{tag} / L)"))   # dx/deta
    for j in range(4):
        out.append(V(f"w{j}{tag}", f"W{j} * pow({et.G()}, p{j}) * (1 + sp{j} * (1 - {et.G()}))"))
        out.append(V(f"Y{j + 1}{tag}", (f"Y{j}{tag} + " if j else "") + f"c{j} * w{j}{tag}"))
        out.append(V(f"Z{j + 1}{tag}", f"Z{j}{tag} + s{j} * w{j}{tag}"))
    out.append(V(f"ZR{tag}", f"Z4{tag} + Y4{tag} * tc"))
    if not hydro:
        out.append(V(f"wD{tag}", f"Y4{tag} / cd"))
    if arcs or (weight is not None and not hydro):
        for j in range(4):
            out.append(V(f"S{j}{tag}", arc(j, et, f"jac{tag}")))
        out.append(V(f"SD{tag}", arc(4, et, f"jac{tag}")))
    if weight is not None:
        out.append(V(f"wq{tag}", f"{num(weight)} * " + (f"L / (1 - 2 * s * X{tag} / L)" if hydro else f"jac{tag}")))
    return out


for i in range(N + 1):
    steps += station_vars(f"_{i}", ETA[i], CC[i] * (1 - 2 * ETAE) / 2)
for i in range(NH + 1):
    steps += station_vars(f"_h{i}", ETAH[i], CCH[i] * (1 - 2 * ETAE) / 2, hydro=True)
steps += station_vars("_sm", ETAM)
steps += station_vars("_s", ETAT)
steps += station_vars("_bm", 1 - ETAM)
steps += station_vars("_b", 1 - ETAT)
S(V("Lhull", f"X_{N} - X_0"))   # length of the plywood hull (the tips are hardwood)


def nest(fn, items):
    e = items[0]
    for it in items[1:]:
        e = f"{fn}({e}, {it})"
    return e


def eta_at(x):
    """eta of a station at x (an expression)."""
    xi = f"(({x}) / L + 0.5)"
    return f"{xi} + s * {xi} * (1 - {xi})"


# ---------------------------------------------------------------- hydrostatics by formulas
def Yv(j, i):
    """Y of chine j at station i (the keel, j = 0, is on the centre line)."""
    return f"Y{j}_{i}" if j else "0 mm"


def clampc(T, i, j):
    lo, hi = f"Z{j}_{i}", f"Z{j + 1}_{i}"
    return f"clamp({T} - {lo}, 0 mm, {hi} - {lo})"


def cdk(T, i):
    return f"clamp({T} - Z4_{i}, 0 mm, ZR_{i} - Z4_{i})"


def half_area(T, i):
    t = [f"({Yv(j, i)} + k{j} / 2 * {clampc(T, i, j)}) * {clampc(T, i, j)}" for j in range(4)]
    t.append(f"(Y4_{i} - cotd / 2 * {cdk(T, i)}) * {cdk(T, i)}")
    return " + ".join(t)


def half_breadth(T, i):
    t = [f"k{j} * {clampc(T, i, j)}" for j in range(4)]
    return " + ".join(t) + f" - cotd * {cdk(T, i)}"


def half_zmoment(T, i):
    t = []
    for j in range(4):
        c = clampc(T, i, j)
        t.append(f"({Yv(j, i)} * Z{j}_{i} + ({Yv(j, i)} + Z{j}_{i} * k{j}) / 2 * {c} + k{j} / 3 * {c}^2) * {c}")
    c = cdk(T, i)
    t.append(f"(Y4_{i} * Z4_{i} + (Y4_{i} - Z4_{i} * cotd) / 2 * {c} - cotd / 3 * {c}^2) * {c}")
    return " + ".join(t)


def girth_wetted(T, i):
    t = [f"{clampc(T, i, j)} / s{j} * S{j}_{i}" for j in range(4)]
    t.append(f"{cdk(T, i)} / sd * SD_{i}")
    return " + ".join(t)


def per_station(prefix, fn, T, grid=HG):
    for t in grid:
        S(V(f"{prefix}_{t}", fn(T, t)))


def wsum(term, grid=HG):
    """Clenshaw-Curtis sum over the stations of grid of term(tag) (an expression) times dx."""
    return " + ".join(f"wq_{t} * {term(t)}" for t in grid)


# The panels' areas and moments (one side), for the boat's weight and centre of gravity.
for j in range(4):
    S(V(f"Ap{j}", wsum(grid=LG, term=lambda i: f"w{j}_{i} * S{j}_{i}")))
    S(V(f"Mxp{j}", wsum(grid=LG, term=lambda i: f"X_{i} * w{j}_{i} * S{j}_{i}")))
    S(V(f"Mzp{j}", wsum(grid=LG, term=lambda i: f"(Z{j}_{i} + Z{j + 1}_{i}) / 2 * w{j}_{i} * S{j}_{i}")))
    S(V(f"Lp{j}", wsum(grid=LG, term=lambda i: f"S{j}_{i}")))     # the flat panel's length
S(V("ApD", wsum(grid=LG, term=lambda i: f"wD_{i} * SD_{i}")))
S(V("MxpD", wsum(grid=LG, term=lambda i: f"X_{i} * wD_{i} * SD_{i}")))
S(V("MzpD", wsum(grid=LG, term=lambda i: f"(Z4_{i} + ZR_{i}) / 2 * wD_{i} * SD_{i}")))
S(V("LpD", wsum(grid=LG, term=lambda i: "SD_" + str(i))))
S(V("Mzc", wsum(grid=LG, term=lambda i: f"Z4_{i}")))   # for the sheer clamps' height
S(V("AHull", "2 * (Ap0 + Ap1 + Ap2 + Ap3)"))
S(V("ADeck", "2 * ApD"))

# ---------------------------------------------------------------- the cockpit (keyhole), seat, bulkheads
# Keyhole: the convex hull of an aft circle (r1) and a forward one (r2), centres dK apart.
S(V("r1", "cockW / 2"))
S(V("r2", "0.62 * cockW / 2"))
S(V("dK", "cockL - r1 - r2"))
S(V("alK", "asin((r1 - r2) / dK)"))
S(V("Akey", "r1^2 * (pi + 2 * alK / 1 rad) / 2 + r2^2 * (pi - 2 * alK / 1 rad) / 2 + (r1 + r2) * dK * cos(alK)"))
S(V("Pkey", "r1 * (pi + 2 * alK / 1 rad) + r2 * (pi - 2 * alK / 1 rad) + 2 * dK * cos(alK)"))
S(V("backGap", "60 mm"))       # the opening's aft edge behind the seat back
S(V("lipW", "28 mm"))          # coaming lip, outward of the riser
S(V("riserT", "6 mm"))
S(V("Akey1", "(r1 + riserT)^2 * (pi + 2 * alK / 1 rad) / 2 + (r2 + riserT)^2 * (pi - 2 * alK / 1 rad) / 2 + (r1 + r2 + 2 * riserT) * dK * cos(alK)"))
S(V("Akey2", "(r1 + riserT + lipW)^2 * (pi + 2 * alK / 1 rad) / 2 + (r2 + riserT + lipW)^2 * (pi - 2 * alK / 1 rad) / 2 + (r1 + r2 + 2 * (riserT + lipW)) * dK * cos(alK)"))
S(V("lipT", "6 mm"))
S(V("legReach", "0.57 * hPad"))   # seat back to the foot brace (fore bulkhead), legs nearly straight
S(V("bkAft", "150 mm"))           # aft bulkhead behind the seat back
S(V("hatchR", "120 mm"))          # 24 cm round hatches
# Items placed relative to the seat back xBack (solved below for level trim):
#   paddler CG at xBack + cgFwd, payload half in each compartment 0.6 m beyond its bulkhead,
#   coaming centred on the opening, fittings at the seat.
S(V("offPay", "((legReach + 600 mm) + (-bkAft - 600 mm)) / 2"))
S(V("offCoam", "-backGap + cockL / 2"))
# Masses that do not move with the cockpit (wood: plywood panels, clamps), kg and kg mm
S(V("tVol", "1 / (1 m)^3"))
S(V("mPanels", "rhoPly * tVol * (2 * (Ap0 + Ap1 + Ap2 + Ap3) * tHull + 2 * ApD * tDeck)"))
S(V("mxPanels", "rhoPly * tVol * 2 * ((Mxp0 + Mxp1 + Mxp2 + Mxp3) * tHull + MxpD * tDeck)"))
S(V("mzPanels", "rhoPly * tVol * 2 * ((Mzp0 + Mzp1 + Mzp2 + Mzp3) * tHull + MzpD * tDeck)"))
S(V("mClamps", "rhoWood * tVol * 2 * clampA * clampB * Lhull"))
S(V("zClamps", "Mzc / Lhull - clampA / 2"))
S(V("mGlass", "(glassHull * AHull + glassDeck * ADeck) / (1 m)^2"))
S(V("mxGlass", "2 * (glassHull * (Mxp0 + Mxp1 + Mxp2 + Mxp3) + glassDeck * MxpD) / (1 m)^2"))
S(V("mzGlass", "2 * (glassHull * (Mzp0 + Mzp1 + Mzp2 + Mzp3) + glassDeck * MzpD) / (1 m)^2"))
# Masses that move with the cockpit: the coaming (riser + lip), less the deck's opening, the fittings.
S(V("mCoam", "rhoWood * tVol * (Pkey * riserT * 70 mm + (Pkey + pi * (riserT + lipW)) * (lipW + riserT) * lipT)"))
S(V("mHole", "rhoPly * tVol * Akey / cd * tDeck + glassDeck * Akey / cd / (1 m)^2"))
# Bulkheads: their weight at a nominal section (the widest), placed at the bulkheads
S(V("mBulk", f"2 * rhoPly * tVol * tHull * 0.6 * 2 * Y4_{N // 2} * (ZR_{N // 2} - Z0_{N // 2})"))
S(V("mMove", "mCoam - mHole + fittings + mBulk"))
S(V("xMoveOff", "(mCoam * offCoam - mHole * offCoam + mBulk / 2 * (legReach - bkAft)) / mMove"))
S(V("mBoat", "mPanels + mClamps + mGlass + mMove"))
S(V("Delta", "mPad + mBoat + payload"))
S(V("Vt", "Delta / rho * (1 m)^3"))
S(V("T0", "0.8 * D"))
for m in range(NEWTON):
    per_station(f"ah{m}", half_area, f"T{m}")
    per_station(f"hb{m}", half_breadth, f"T{m}")
    S(V(f"Vn{m}", f"2 * ({wsum(lambda i: f'ah{m}_{i}')})"))
    S(V(f"An{m}", f"2 * ({wsum(lambda i: f'hb{m}_{i}')})"))
    S(V(f"T{m + 1}", f"T{m} - (Vn{m} - Vt) / An{m}"))
S(V("T", f"T{NEWTON}"))
per_station("ah", half_area, "T")
per_station("hb", half_breadth, "T")
per_station("zm", half_zmoment, "T")
per_station("gw", girth_wetted, "T", LG)
S(V("Vdisp", f"2 * ({wsum(lambda i: f'ah_{i}')})"))
S(V("Awp", f"2 * ({wsum(lambda i: f'hb_{i}')})"))
S(V("LCB", f"2 * ({wsum(lambda i: f'X_{i} * ah_{i}')}) / Vdisp"))
S(V("KB", f"2 * ({wsum(lambda i: f'zm_{i}')}) / Vdisp"))
S(V("Iwp", f"2 / 3 * ({wsum(lambda i: f'hb_{i}^3')})"))
S(V("WS", f"2 * ({wsum(lambda i: f'gw_{i}', LG)})"))
S(V("BM", "Iwp / Vdisp"))
S(V("BWL", f"2 * hb_h{NH // 2}"))
S(V("Amid", f"2 * ah_h{NH // 2}"))
# Waterline length: where the keel z0 = rA u^4 + rC u^5 crosses T, by Newton from each tip.
for side, u0 in (("b", 1.0), ("s", -1.0)):
    S(V(f"u{side}0", num(u0)))
    for m in range(8):
        S(V(f"u{side}{m + 1}", f"u{side}{m} - (rA * u{side}{m}^4 + rC * u{side}{m}^5 - T) / "
                                f"(4 * rA * u{side}{m}^3 + 5 * rC * u{side}{m}^4)"))
    S(V(f"xw{side}", f"(({xi_of(Eta(f'(u{side}8 + 1) / 2'))}) - 0.5) * L"))
S(V("LWL", "xwb - xws"))
S(V("Cp", "Vdisp / (Amid * LWL)"))
S(V("Cwp", "Awp / (LWL * BWL)"))
S(V("Cb", "Vdisp / (LWL * BWL * T)"))
S(V("DLR", "(Delta / 1016.05) / (0.01 * LWL / 1 ft)^3"))   # displacement-length ratio, long tons / (0.01 LWL ft)^3
# Trim: the seat back xBack puts the centre of gravity over the centre of buoyancy.
S(V("xBack", "(Delta * LCB - mxPanels - mClamps * (X_0 + X_" + str(N) + ") / 2 - mxGlass "
             "- mPad * cgFwd - payload * offPay - mMove * xMoveOff) / (mPad + payload + mMove)"))
S(V("xSeatC", "xBack + 200 mm"))
S(V("xBkF", "xBack + legReach"))
S(V("xBkA", "xBack - bkAft"))
S(V("xKey1", "xBack - backGap + r1"))       # centre of the aft circle of the keyhole
S(V("xKey2", "xKey1 + dK"))                 # ... and of the forward one
S(V("xHatF", "xBkF + 300 mm"))
S(V("xHatA", "xBkA - 330 mm"))
for tag, x in (("_sc", "xSeatC"), ("_bf", "xBkF"), ("_ba", "xBkA"), ("_ka", "xBack - backGap"),
               ("_kf", "xBack - backGap + cockL"), ("_hf", "xHatF"), ("_ha", "xHatA")):
    S(V(f"eta{tag}", eta_at(x)))
    steps += station_vars(tag, f"eta{tag}", arcs=(tag in ("_bf", "_ba")))
S(V("zSeat", "Z0_sc + tHull + 25 mm"))     # top of the seat pad on the floor
S(V("xPad", "xBack + cgFwd"))
S(V("zPad", "zSeat + cgUp"))
S(V("xPay", "xBack + offPay"))
S(V("zPay", "Z0_sc + 80 mm"))
S(V("zMove", "(mCoam * (ZR_kf + 40 mm) - mHole * ZR_kf + fittings * zSeat + mBulk * (Z0_sc + 100 mm)) / mMove"))
S(V("KG", "(mzPanels + mClamps * zClamps + mzGlass + mMove * zMove + mPad * zPad + payload * zPay) / Delta"))
S(V("LCG", "(mxPanels + mClamps * (X_0 + X_" + str(N) + ") / 2 + mxGlass + mMove * (xBack + xMoveOff) "
           "+ mPad * xPad + payload * xPay) / Delta"))
S(V("GM", "KB + BM - KG"))
S(V("freeboard", f"Z4_{N // 2} - T"))
S(V("zSheer", nest("min", [f"Z4_{i}" for i in range(N + 1)])))   # the lowest point of the sheer
S(V("fbMin", "zSheer - T"))
# ---------------------------------------------------------------- capacity: the heaviest paddler this hull takes
# (a) freeboard: the sheer's lowest point stays fbReq above the water: the displacement at T = zSheer - fbReq;
# (b) stability: GM >= gmReq; GM falls as the paddler gets heavier, so bisect on the draft for GM = gmReq,
# with the paddler's weight at each draft what the displacement leaves after the boat and the load.
S(V("mPadMin", "45"))     # the lightest adult paddler the form offers
S(V("fbReq", "45 mm"))   # 5 mm more than asserted: the sheer between stations, the mesh
S(V("gmReq", "0 mm"))
S(V("Tlim", f"min(zSheer - fbReq, min(Z0_0, Z0_{N}) - 5 mm)"))   # ... and the tips stay dry
per_station("ahL", half_area, "Tlim")
S(V("Vlim", f"2 * ({wsum(lambda i: f'ahL_{i}')})"))
S(V("capF", "rho * Vlim / (1 m)^3 - mBoat - payload"))
S(V("zPadC", f"Z0_{N // 2} + tHull + 25 mm + cgUp + 3 mm"))   # the seat near the keel's low point (+3 mm)
# the items that move with the cockpit taken at the widest station, 5 mm higher (no dependence on the trim)
S(V("zMoveC", f"(mCoam * (ZR_{N // 2} + 40 mm) - mHole * ZR_{N // 2} + fittings * (Z0_{N // 2} + tHull + 25 mm) "
              f"+ mBulk * (Z0_{N // 2} + 100 mm)) / mMove + 5 mm"))
S(V("Mz0", "mzPanels + mClamps * zClamps + mzGlass + mMove * zMoveC"))
S(V("Tb0", "25 mm"))
S(V("Tt0", "Tlim"))
for m in range(BISECT):
    Tm = f"Tm{m}"
    S(V(Tm, f"(Tb{m} + Tt{m}) / 2"))
    per_station(f"ahB{m}", half_area, Tm)
    per_station(f"hbB{m}", half_breadth, Tm)
    per_station(f"zmB{m}", half_zmoment, Tm)
    S(V(f"VB{m}", f"2 * ({wsum(lambda i: f'ahB{m}_{i}')})"))
    S(V(f"IB{m}", f"2 / 3 * ({wsum(lambda i: f'hbB{m}_{i}^3')})"))
    S(V(f"KBB{m}", f"2 * ({wsum(lambda i: f'zmB{m}_{i}')}) / VB{m}"))
    S(V(f"DB{m}", f"rho * VB{m} / (1 m)^3"))
    # the load is taken as high as the paddler (it is lower): the capacity then holds for any load
    S(V(f"GMB{m}", f"KBB{m} + IB{m} / VB{m} - (Mz0 + (DB{m} - mBoat) * zPadC) / DB{m}"))
    S(V(f"Tb{m + 1}", f"if(GMB{m} >= gmReq, {Tm}, Tb{m})"))
    S(V(f"Tt{m + 1}", f"if(GMB{m} >= gmReq, Tt{m}, {Tm})"))
per_station("ahS", half_area, f"Tb{BISECT}")
S(V("capS0", f"rho * 2 * ({wsum(lambda i: f'ahS_{i}')}) / (1 m)^3 - mBoat"))   # paddler + load
S(V("capS", "capS0 - payload"))
S(V("loadMax", "max(0, min(40, floor(min(rho * Vlim / (1 m)^3 - mBoat, capS0) - mPadMin)))"))   # room for the lightest paddler
S(V("mPadMax", "min(110, floor(min(capF, capS)))"))
# Ruling of the panels at the waterline, for the README: flare of each panel
for j in range(4):
    S(V(f"flare{j}", f"90 deg - th{j}"))


# ================================================================ geometry
ON = {2: "n == 2", 3: "n == 3", 4: "n == 4"}
PON = {0: None, 1: None, 2: "n > 2", 3: "n > 3", 4: None}   # when a panel exists
PANELS = [0, 1, 2, 3, 4]                                    # 4: the deck
I_CLAMP = [i for i in range(N + 1) if 0.15 <= ETA[i] <= 0.85]


def look(body, color, rough=0.55):
    return ["body.appearance", {"body": body, "color": color, "roughness": rough}]


def mat(body, name, rho):
    return ["body.material", {"body": body, "name": name, "density": rho}]


def when(d, cond):
    if cond:
        d["when"] = cond
    return d


def both(a, b):
    if a and b:
        return f"({a}) && ({b})"
    return a or b


def sketch(name, plane, offset, cond=None):
    S(["sketch.create", {"name": name, "plane": plane, "offset": offset}])
    if cond:
        S(["feature.when", {"feature": name, "expr": cond}])


# --- the hull envelope: the outside of the planking, closed by the deck (for the hydrostatics) ---
def env_points(nn, i):
    return ([["0 mm", f"Z0_{i}"]] + [[f"Y{k}_{i}", f"Z{k}_{i}"] for k in range(1, nn)] +
            [[f"Y4_{i}", f"Z4_{i}"], ["0 mm", f"ZR_{i}"], [f"-Y4_{i}", f"Z4_{i}"]] +
            [[f"-Y{k}_{i}", f"Z{k}_{i}"] for k in range(nn - 1, 0, -1)])


for nn in (2, 3, 4):
    names = []
    for i in range(N + 1):
        sk = f"St{nn}_{i}"
        names.append(sk)
        sketch(sk, "yz", f"X_{i}", ON[nn])
        S(["sketch.polyline", {"sketch": sk, "points": env_points(nn, i), "closed": True}])
    S(["feature.loft", {"sections": names, "name": f"Env{nn}", "when": ON[nn]}])


# --- the plywood panels: thin lofts through the stations, the starboard ones mirrored to port ---
def quad(j, i):
    if j < 4:
        t = f"tHull * S{j}_{i}"
        return [[Yv(j, i), f"Z{j}_{i}"], [f"Y{j + 1}_{i}", f"Z{j + 1}_{i}"],
                [f"Y{j + 1}_{i} - {t} * s{j}", f"Z{j + 1}_{i} + {t} * c{j}"],
                [f"{Yv(j, i)} - {t} * s{j}", f"Z{j}_{i} + {t} * c{j}"]]
    t = f"tDeck * SD_{i}"
    return [[f"Y4_{i}", f"Z4_{i}"], ["0 mm", f"ZR_{i}"], [f"0 mm - {t} * sd", f"ZR_{i} - {t} * cd"],
            [f"Y4_{i} - {t} * sd", f"Z4_{i} - {t} * cd"]]


PNAME = {0: "Bottom", 1: "Panel2", 2: "Panel3", 3: "Panel4", 4: "Deck"}
for j in PANELS:
    names = []
    for i in range(N + 1):
        sk = f"Pn{j}_{i}"
        names.append(sk)
        sketch(sk, "yz", f"X_{i}", PON[j])
        S(["sketch.polyline", {"sketch": sk, "points": quad(j, i), "closed": True}])
    S(["feature.loft", when({"sections": names, "name": f"{PNAME[j]}S"}, PON[j])])
    S(["feature.mirror", when({"source": f"{PNAME[j]}S", "normal": [0, 1, 0], "keep": True,
                               "name": f"{PNAME[j]}P"}, PON[j])])

# --- hardwood tips: from the hull's end station to a point, through a middle section ---
for end, tags in (("Stern", ["_0", "_sm", "_s"]), ("Bow", [f"_{N}", "_bm", "_b"])):
    names = []
    for tag in tags:
        sk = f"Tip{end}{tag}"
        names.append(sk)
        sketch(sk, "yz", f"X{tag}")
        S(["sketch.polyline", {"sketch": sk, "closed": True, "points": [
            ["0 mm", f"Z0{tag}"], [f"Y4{tag}", f"Z4{tag}"], ["0 mm", f"ZR{tag}"], [f"-Y4{tag}", f"Z4{tag}"]]}])
    S(["feature.loft", {"sections": names, "name": f"Tip{end}"}])

# --- sheer clamps: a 20 x 12 mm strip inside the hull-deck joint, glued to the topside ---
S(V("aClamp", "(tDeck / cd + clampB * tc) / sT + 2 mm"))


def clamp_pts(tag):
    """A, B, C, Dd of the clamp's section at a station (expressions)."""
    dT = f"tHull * choose(n - 1, S1{tag}, S2{tag}, S3{tag})"
    ay = f"(Y4{tag} - {dT} * sT - aClamp * cT)"
    az = f"(Z4{tag} + {dT} * cT - aClamp * sT)"
    A = [ay, az]
    Bp = [f"{ay} - clampA * cT", f"{az} - clampA * sT"]
    C = [f"{ay} - clampA * cT - clampB * sT", f"{az} - clampA * sT + clampB * cT"]
    Dd = [f"{ay} - clampB * sT", f"{az} + clampB * cT"]
    return A, Bp, C, Dd


names = []
for i in I_CLAMP:
    sk = f"Cl_{i}"
    names.append(sk)
    sketch(sk, "yz", f"X_{i}")
    S(["sketch.polyline", {"sketch": sk, "points": list(clamp_pts(f"_{i}")), "closed": True}])
S(["feature.loft", {"sections": names, "name": "ClampS"}])
S(["feature.mirror", {"source": "ClampS", "normal": [0, 1, 0], "keep": True, "name": "ClampP"}])
lo, hi = I_CLAMP[0], I_CLAMP[-1]
S(V("LClamp", f"X_{hi} - X_{lo}"))
S(V("xClamps", f"(X_{hi} + X_{lo}) / 2"))
zc = " + ".join(f"(X_{i + 1} - X_{i}) * (Z4_{i} + Z4_{i + 1}) / 2" for i in I_CLAMP[:-1])
S(V("zClamps", f"({zc}) / LClamp - aClamp * sT - clampA / 2 * sT + clampB / 2 * cT"))


# --- bulkheads: the inner section at the station, notched for the clamps ---
def inner_vertex(a, b, tag):
    da, db = f"(tHull * S{a}{tag})", f"(tHull * S{b}{tag})"
    det = f"if(n > {b}, s{b} * c{a} - s{a} * c{b}, 1)"   # (1 for a panel this hull does not have)
    return [f"Y{b}{tag} + ({da} * c{b} - {db} * c{a}) / {det}",
            f"Z{b}{tag} + ({da} * s{b} - {db} * s{a}) / {det}"]


def bulkhead_pts(nn, tag):
    half = [["0 mm", f"Z0{tag} + tHull * S0{tag} / c0"]]
    for k in range(1, nn):
        half.append(inner_vertex(k - 1, k, tag))
    A, Bp, C, Dd = clamp_pts(tag)
    half += [Bp, C, Dd]
    ridge = ["0 mm", f"ZR{tag} - tDeck * SD{tag} / cd"]
    mirror = [[f"0 mm - ({p[0]})", p[1]] for p in reversed(half[1:])]
    return half + [ridge] + mirror


def shoelace(pts):
    terms = []
    for a, b in zip(pts, pts[1:] + pts[:1]):
        terms.append(f"({a[0]}) * ({b[1]}) - ({b[0]}) * ({a[1]})")
    return "(" + " + ".join(terms) + ") / 2"


BKPTS = {}
for bk, tag, xv in (("Fore", "_bf", "xBkF"), ("Aft", "_ba", "xBkA")):
    for nn in (2, 3, 4):
        pts = []
        for k, (py, pz) in enumerate(bulkhead_pts(nn, tag)):
            S(V(f"bv{bk}{nn}y{k}", py))
            S(V(f"bv{bk}{nn}z{k}", pz))
            pts.append([f"bv{bk}{nn}y{k}", f"bv{bk}{nn}z{k}"])
        BKPTS[(bk, nn)] = pts
        sk = f"Bk{bk}{nn}"
        cond = both(ON[nn], "hatches")
        sketch(sk, "yz", f"{xv} - tHull / 2", cond)
        S(["sketch.polyline", {"sketch": sk, "points": pts, "closed": True}])
        S(["feature.extrude", {"sketch": sk, "distance": "tHull", "name": f"Bulk{bk}{nn}", "when": cond}])
        S(V(f"aBk{bk}{nn}", shoelace(pts)))
    S(V(f"aBk{bk}", f"choose(n - 1, aBk{bk}2, aBk{bk}3, aBk{bk}4)"))
S(V("mBulkReal", "hatches * rhoPly * tVol * tHull * (aBkFore + aBkAft)"))


# ================================================================ the flat panels (the cut sheet)
# where every panel is at least 26 mm wide over the whole form (beam >= 530 mm, depth >= 170 mm, every
# form and number of chines): stitch holes 8 mm in from both edges stay inside, with room
REGION = {0: (0.23, 0.77), 1: (0.2, 0.8), 2: (0.2, 0.8), 3: (0.17, 0.83), 4: (0.06, 0.94)}
THK = {0: "tHull", 1: "tHull", 2: "tHull", 3: "tHull", 4: "tDeck"}
PIECE_GAP = 50   # mm: the three pieces of a flat panel are drawn this far apart along it


def f_flat(j, et):
    """dX/deta of the flat panel j: sqrt((dx/deta)^2 + (dg/deta)^2) at eta (Eta)."""
    return f"sqrt(({jac_of(et)})^2 + {gprime(j, et)}^2)"


def gauss(j, a, b, rule=GL3):
    half, mid = (b - a) / 2, (a + b) / 2
    return " + ".join(f"{num(w * half)} * {f_flat(j, Eta(mid + half * z))}" for z, w in rule)


def vlow(j, tag):
    if j == 0:
        return f"s0 * Z0{tag}"
    return f"c{j} * Y{j}{tag} + s{j} * Z{j}{tag}" if j < 4 else f"sd * Z4{tag} - cd * Y4{tag}"


def width(j, tag):
    return f"w{j}{tag}" if j < 4 else f"wD{tag}"


# Joints: two per panel, staggered from panel to panel as kits stagger them so they never line up; the
# panel is cut into three pieces there with a dovetail key (a puzzle joint).
def joint_station(target):
    return min(range(1, N), key=lambda i: abs(ETA[i] - target))


# Alternate panels are joined at (0.32, 0.68) and (0.38, 0.73) of eta (with 24 stations), so no piece is
# longer than about 0.36 of the length even with the widest station at 0.44 or 0.52.
JOINTS = {j: ((joint_station(0.32), joint_station(0.68)) if j % 2 == 0 else
              (joint_station(0.378), joint_station(0.735))) for j in PANELS}
# Stitch holes: at the stations and at the thirds of the long intervals between them, kept at least
# ~0.016 in eta apart, inside the region where the panel is wide enough, not next to a joint.
CAND = []
for i in range(N + 1):
    CAND.append((ETA[i], i, 0))
    if i < N and ETA[i + 1] - ETA[i] > 0.03:
        CAND += [(ETA[i] + (ETA[i + 1] - ETA[i]) * q / 3, i, q) for q in (1, 2)]
CAND.sort()
HOLES = {}
for j in PANELS:
    lo, hi = REGION[j]
    pick, last = [], -1.0
    for c in CAND:
        near_joint = any(abs(c[0] - ETA[J]) < 0.012 for J in JOINTS[j])
        if lo <= c[0] <= hi and c[0] - last >= 0.016 and not near_joint:
            pick.append(c)
            last = c[0]
    HOLES[j] = pick

S(V("rowTop0", "0 mm - B / 2 - 150 mm"))
S(V("holeIn", "8 mm"))
S(V("holeR", "1 mm"))
prev = "rowTop0"
for j in [4, 3, 2, 1, 0]:
    cond = PON[j]
    S(V(f"sg{j}_0", "0 mm"))
    for i in range(N):
        S(V(f"sg{j}_{i + 1}", f"sg{j}_{i} + " + gauss(j, ETA[i], ETA[i + 1])))
    for i in range(N + 1):
        S(V(f"vl{j}_{i}", vlow(j, f"_{i}")))
    S(V(f"vmin{j}", nest("min", [f"vl{j}_{i}" for i in range(N + 1)]) + " - 2 mm"))
    S(V(f"vmax{j}", nest("max", [f"vl{j}_{i} + {width(j, f'_{i}')}" for i in range(N + 1)]) + " + 2 mm"))
    S(V(f"hF{j}", f"vmax{j} - vmin{j}"))
    S(V(f"yo{j}", f"{prev} - vmax{j}"))
    S(V(f"rowTop{j}x", f"{prev} - " + (f"if({cond}, hF{j} + {GAP} mm, 0 mm)" if cond else f"(hF{j} + {GAP} mm)")))
    prev = f"rowTop{j}x"
    J1, J2 = JOINTS[j]
    pieces = [("a", 0, J1, 0), ("b", J1, J2, 1), ("c", J2, N, 2)]
    nholes = 0
    for pc, ia, ib, k in pieces:
        dx = f" + {k * PIECE_GAP} mm" if k else ""
        P = lambda i, up: [f"X_0 + sg{j}_{i}{dx}", f"yo{j} + vl{j}_{i}" + (f" + {width(j, f'_{i}')}" if up else "")]
        sk = f"Fl{j}{pc}"
        sketch(sk, "xy", f"{FLOOR} mm", cond)
        S(["sketch.point", {"sketch": sk, "at": P(ia, False)}])      # e1
        S(["sketch.point", {"sketch": sk, "at": P(ib, False)}])      # e2
        S(["sketch.point", {"sketch": sk, "at": P(ia, True)}])       # e3
        S(["sketch.point", {"sketch": sk, "at": P(ib, True)}])       # e4
        S(["sketch.spline", {"sketch": sk, "live": True, "through": ["e1"] + [P(i, False) for i in range(ia + 1, ib)] + ["e2"]}])
        S(["sketch.spline", {"sketch": sk, "live": True, "through": ["e3"] + [P(i, True) for i in range(ia + 1, ib)] + ["e4"]}])

        def key(i, a, b):
            """the puzzle joint at station i, between points a (low edge) and b (high edge)"""
            x0, w0 = P(i, False)[0], f"w{j}_{i}" if j < 4 else f"wD_{i}"
            vm = f"yo{j} + vl{j}_{i} + {w0} / 2"
            w = f"min({w0}, 120 mm)"     # the key: at most 30 mm deep and 53 mm across its head
            return [a, [x0, f"{vm} - 0.12 * {w}"], [f"{x0} + 0.25 * {w}", f"{vm} - 0.22 * {w}"],
                    [f"{x0} + 0.25 * {w}", f"{vm} + 0.22 * {w}"], [x0, f"{vm} + 0.12 * {w}"], b]
        if ia == 0:
            S(["sketch.line", {"sketch": sk, "from": "e1", "to": "e3"}])
        else:
            S(["sketch.polyline", {"sketch": sk, "points": key(ia, "e1", "e3")}])
        if ib == N:
            S(["sketch.line", {"sketch": sk, "from": "e2", "to": "e4"}])
        else:
            S(["sketch.polyline", {"sketch": sk, "points": key(ib, "e2", "e4")}])
        for eta_, i, q in HOLES[j]:
            if not ia <= i + q / 3 < ib:
                continue
            if q:      # a third of the way along a long interval: sigma by Gauss from the station, v and
                # the width interpolated (the edges are nearly straight there: well under 0.1 mm off)
                S(V(f"sgh{j}_{i}_{q}", f"sg{j}_{i} + " + gauss(j, ETA[i], eta_)))
                sgv = f"sgh{j}_{i}_{q}"
                v = f"(vl{j}_{i} * {3 - q} + vl{j}_{i + 1} * {q}) / 3"
                wd = f"({width(j, f'_{i}')} * {3 - q} + {width(j, f'_{i + 1}')} * {q}) / 3"
            else:
                sgv, v, wd = f"sg{j}_{i}", f"vl{j}_{i}", width(j, f"_{i}")
            S(["sketch.circle", {"sketch": sk, "center": [f"X_0 + {sgv}{dx}", f"yo{j} + {v} + holeIn"], "radius": "holeR"}])
            S(["sketch.circle", {"sketch": sk, "center": [f"X_0 + {sgv}{dx}", f"yo{j} + {v} + {wd} - holeIn"],
                                 "radius": "holeR"}])
            nholes += 2
        S(["feature.extrude", when({"sketch": sk, "distance": THK[j], "name": f"Flat{j}{pc}"}, cond)])
    S(V(f"nHoles{j}", str(nholes)))
S(V("rowEnd", prev))
S(V("pieceGap", f"{PIECE_GAP} mm"))


# ================================================================ cockpit, coaming, hatches


def keyhole(sk, grow, dx="0 mm", dy="0 mm"):
    """The keyhole outline grown by grow (the hull of the two circles, radii + grow), moved by dx, dy."""
    R1, R2 = f"(r1 + {grow})", f"(r2 + {grow})"
    c1, c2 = f"xKey1 + {dx}", f"xKey2 + {dx}"
    p1 = [f"{c1} + {R1} * sin(alK)", f"{dy} + {R1} * cos(alK)"]
    p2 = [f"{c2} + {R2} * sin(alK)", f"{dy} + {R2} * cos(alK)"]
    q2 = [p2[0], f"{dy} - {R2} * cos(alK)"]
    q1 = [p1[0], f"{dy} - {R1} * cos(alK)"]
    S(["sketch.path", {"sketch": sk, "start": p1, "segments": [
        {"line": p2}, {"arc": q2, "center": [c2, dy], "clockwise": True},
        {"line": q1}, {"arc": "start", "center": [c1, dy], "clockwise": True}]}])


S(V("zKeyLow", "min(Z4_ka, Z4_kf) - 15 mm"))
S(V("riserH", "30 mm"))       # the coaming's riser stands 30 mm above the deck all round, the lip on it
S(V("zKeyTop", f"max(max(ZR_ka, ZR_kf), ZR_{N // 2}) + riserH + lipT + 20 mm"))   # (the cutters' top)
sketch("KeyCut", "xy", "zKeyLow")
keyhole("KeyCut", "0 mm")
for side in "SP":
    S(["feature.extrude", {"sketch": "KeyCut", "distance": "zKeyTop - zKeyLow + 20 mm", "cut": f"Deck{side}",
                           "name": f"Cockpit{side}"}])
sketch("Riser", "xy", "zKeyLow")
keyhole("Riser", "0 mm")
keyhole("Riser", "riserT")
S(["feature.extrude", {"sketch": "Riser", "distance": "zKeyTop - zKeyLow", "name": "Riser0"}])
sketch("Lip", "xy", "zKeyLow")
keyhole("Lip", "0 mm")
keyhole("Lip", "riserT + lipW")
S(["feature.extrude", {"sketch": "Lip", "distance": "zKeyTop - zKeyLow", "name": "Lip0"}])
# hatch covers: a round plug standing on the deck
for h, x in (("Fore", "xHatF"), ("Aft", "xHatA")):
    tag = "_hf" if h == "Fore" else "_ha"
    sketch(f"Hat{h}", "xy", f"Z4{tag} - 25 mm", "hatches")
    S(["sketch.circle", {"sketch": f"Hat{h}", "center": [x, "0 mm"], "radius": "hatchR"}])
    S(["feature.extrude", {"sketch": f"Hat{h}", "distance": f"ZR{tag} - Z4{tag} + 25 mm + 22 mm",
                           "name": f"Hatch{h}0", "when": "hatches"}])
# The riser keeps what lies between the deck and 30 mm above it (the envelope moved up), so it follows the
# deck's crown at a constant height; the lip the next 6 mm, outward of the riser. The hatch covers keep what
# lies within 22 mm of the deck, like a moulded hatch lid.
for nn in (2, 3, 4):
    S(["feature.transform", {"source": f"Env{nn}", "keep": True, "translate": ["0 mm", "0 mm", "riserH"],
                             "name": f"EnvR{nn}", "when": ON[nn]}])
    S(["feature.transform", {"source": f"Env{nn}", "keep": True, "translate": ["0 mm", "0 mm", "riserH + lipT"],
                             "name": f"EnvL{nn}", "when": ON[nn]}])
    S(["feature.boolean", {"op": "intersect", "target": "Riser0" if nn == 2 else f"Riser{nn - 1}x",
                           "tool": f"EnvR{nn}", "keepTool": True, "name": f"Riser{nn}i", "when": ON[nn]}])
    S(["feature.boolean", {"op": "subtract", "target": f"Riser{nn}i",
                           "tool": f"Env{nn}", "keepTool": True, "name": f"Riser{nn}x", "when": ON[nn]}])
    S(["feature.boolean", {"op": "intersect", "target": "Lip0" if nn == 2 else f"Lip{nn - 1}x",
                           "tool": f"EnvL{nn}", "name": f"Lip{nn}i", "when": ON[nn]}])
    S(["feature.boolean", {"op": "subtract", "target": f"Lip{nn}i",
                           "tool": f"EnvR{nn}", "name": f"Lip{nn}x", "when": ON[nn]}])
    S(["feature.transform", {"source": f"Env{nn}", "keep": True, "translate": ["0 mm", "0 mm", "22 mm"],
                             "name": f"EnvUp{nn}", "when": both(ON[nn], "hatches")}])
    for h in ("Fore", "Aft"):
        S(["feature.boolean", {"op": "intersect", "target": f"Hatch{h}0" if nn == 2 else f"Hatch{h}{nn - 1}x",
                               "tool": f"EnvUp{nn}", "keepTool": h == "Fore", "name": f"Hatch{h}{nn}i",
                               "when": both(ON[nn], "hatches")}])
        S(["feature.boolean", {"op": "subtract", "target": f"Hatch{h}{nn}i",
                               "tool": f"Env{nn}", "keepTool": True, "name": f"Hatch{h}{nn}x",
                               "when": both(ON[nn], "hatches")}])
S(["feature.boolean", {"op": "union", "target": "Riser4x", "tool": "Lip4x", "name": "Coaming"}])
S(["feature.transform", {"source": "HatchFore4x", "name": "HatchFore", "when": "hatches"}])
S(["feature.transform", {"source": "HatchAft4x", "name": "HatchAft", "when": "hatches"}])

# ---------------------------------------------------------------- flat bulkheads and the coaming's lip on the floor
S(V("xFlatB", "X_0 + 600 mm"))     # a row below the flat panels
S(V("yFlatB", "rowEnd"))
for bi, bk in enumerate(("Fore", "Aft")):
    for nn in (2, 3, 4):
        sk = f"BkFlat{bk}{nn}"
        cond = both(ON[nn], "hatches")
        sketch(sk, "xy", f"{FLOOR} mm", cond)
        pts = [[f"xFlatB + B / 2 + {bi} * (B + 100 mm) + {p[0]}", f"yFlatB - 30 mm - ZR_{N // 2} + {p[1]}"]
               for p in BKPTS[(bk, nn)]]
        S(["sketch.polyline", {"sketch": sk, "points": pts, "closed": True}])
        S(["feature.extrude", {"sketch": sk, "distance": "tHull", "name": f"BulkFlat{bk}{nn}", "when": cond}])
# The coaming's riser, developed. It is a vertical wall standing on the deck along the keyhole, so it is a
# cylinder with vertical rulings (exactly developable): flat, a band riserH high whose edges are the deck's
# height along the keyhole's perimeter (at the riser's mid-thickness) against the distance along it. The deck's
# height there is the hull's own formula, z = Z4 + (Y4 - |y|) tan(crown), sampled along the upper half of the
# keyhole (it is symmetric): the aft arc, the straight side, the front arc.
S(V("Rm1", "r1 + riserT / 2"))
S(V("Rm2", "r2 + riserT / 2"))
S(V("sAft", "Rm1 * (pi / 2 + alK / 1 rad)"))
S(V("sSide", "dK * cos(alK)"))
S(V("Phalf", "sAft + sSide + Rm2 * (pi / 2 - alK / 1 rad)"))
S(V("Priser", "2 * Phalf"))
RS = []                                   # (s, x, y) of the samples, from the aft centre to the front centre
for k in range(7):
    t = k / 6
    th = f"(180 deg - {num(t)} * (90 deg + alK))"
    RS.append((f"{num(t)} * sAft", f"xKey1 + Rm1 * cos{th}", f"Rm1 * sin{th}"))
for k in range(1, 4):
    t = k / 4
    RS.append((f"sAft + {num(t)} * sSide", f"xKey1 + Rm1 * sin(alK) + {num(t)} * (xKey2 - xKey1 + (Rm2 - Rm1) * sin(alK))",
               f"Rm1 * cos(alK) + {num(t)} * (Rm2 - Rm1) * cos(alK)"))
for k in range(0, 6):
    t = k / 5
    th = f"((90 deg - alK) * {num(1 - t)})"
    RS.append((f"sAft + sSide + {num(t)} * Rm2 * (pi / 2 - alK / 1 rad)", f"xKey2 + Rm2 * cos{th}", f"Rm2 * sin{th}"))
for k, (sk_, xk, yk) in enumerate(RS):
    S(V(f"rsS{k}", sk_))
    S(V(f"rsE{k}", eta_at(xk)))
    et = Eta(f"rsE{k}")
    F = [f"W{j} * pow({et.G()}, p{j}) * (1 + sp{j} * (1 - {et.G()}))" for j in range(4)]
    y4 = " + ".join(f"c{j} * {F[j]}" for j in range(4))
    z4 = f"rA * {et.u(NR)} + rC * {et.u(NR + 1)} + " + " + ".join(f"s{j} * {F[j]}" for j in range(4))
    S(V(f"rsZ{k}", f"{z4} + (({y4}) - ({yk})) * tc"))
NRS = len(RS)
S(V("zdMin", nest("min", [f"rsZ{k}" for k in range(NRS)])))
S(V("zdMax", nest("max", [f"rsZ{k}" for k in range(NRS)])))
S(V("xRiserF", "xFlatB + 2 * B + 250 mm"))
S(V("yRiserF", "yFlatB - 50 mm - (zdMax - zdMin) - riserH"))
sketch("RiserFlat", "xy", f"{FLOOR} mm")
FP = lambda k, sv, up: [f"xRiserF + {sv}", f"yRiserF + rsZ{k} - zdMin" + (" + riserH" if up else "")]
S(["sketch.point", {"sketch": "RiserFlat", "at": FP(0, "0 mm", False)}])      # e1
S(["sketch.point", {"sketch": "RiserFlat", "at": FP(0, "Priser", False)}])    # e2
S(["sketch.point", {"sketch": "RiserFlat", "at": FP(0, "0 mm", True)}])       # e3
S(["sketch.point", {"sketch": "RiserFlat", "at": FP(0, "Priser", True)}])     # e4
for up, a_, b_ in ((False, "e1", "e2"), (True, "e3", "e4")):
    mid = ([FP(k, f"rsS{k}", up) for k in range(1, NRS)] +
           [FP(k, f"Priser - rsS{k}", up) for k in range(NRS - 2, 0, -1)])
    S(["sketch.spline", {"sketch": "RiserFlat", "live": True, "through": [a_] + mid + [b_]}])
S(["sketch.line", {"sketch": "RiserFlat", "from": "e1", "to": "e3"}])
S(["sketch.line", {"sketch": "RiserFlat", "from": "e2", "to": "e4"}])
S(["feature.extrude", {"sketch": "RiserFlat", "distance": "riserT", "name": "CoamingRiser"}])

# ================================================================ the displaced water
S(["feature.block", {"size": ["L + 400 mm", "B + 400 mm", "T + 100 mm"],
                     "position": ["0 mm - L / 2 - 200 mm", "0 mm - B / 2 - 200 mm", "-100 mm"], "name": "Sea"}])
for nn in (2, 3, 4):
    S(["feature.boolean", {"op": "intersect", "target": f"Env{nn}", "tool": "Sea", "name": f"Wet{nn}",
                           "when": ON[nn]}])


# ================================================================ materials, colours, sets
HULLP = [f"{PNAME[j]}{side}" for j in range(4) for side in "SP"]
DECKP = ["DeckS", "DeckP"]
for b in HULLP + DECKP:
    S(mat(b, "okoume plywood", 500))
for nn in (2, 3, 4):
    for bk in ("Fore", "Aft"):
        S(mat(f"Bulk{bk}{nn}", "okoume plywood", 500))
        S(look(f"Bulk{bk}{nn}", OKOUME))
    S(mat(f"Wet{nn}", "sea water", 1025))
    S(look(f"Wet{nn}", OKOUME))
for b in ("ClampS", "ClampP", "TipStern", "TipBow", "Coaming", "HatchFore", "HatchAft"):
    S(mat(b, "hardwood", 600))
for b in HULLP:
    S(look(b, OKOUME, 0.35))
for b in DECKP:
    S(look(b, DECKC, 0.35))
for b in ("TipStern", "TipBow", "Coaming", "HatchFore", "HatchAft"):
    S(look(b, WALNUT, 0.4))
for b in ("ClampS", "ClampP"):
    S(look(b, CREAM))
for j in PANELS:
    for pc in "abc":
        S(look(f"Flat{j}{pc}", DECKC if j == 4 else OKOUME))


def inb(names):
    return {"any": [{"in": nm} for nm in names]}


def madeby(names):
    return {"any": [{"madeBy": nm} for nm in names]}


S(["set.define", {"name": "Displaced water", "kind": "body", "where": madeby(["Wet2", "Wet3", "Wet4"])}])
S(["set.define", {"name": "Wooden hull", "kind": "body", "where": madeby(
    HULLP + DECKP + ["ClampS", "ClampP"] + [f"Bulk{bk}{nn}" for bk in ("Fore", "Aft") for nn in (2, 3, 4)])}])
S(["set.define", {"name": "Deck", "kind": "body", "where": madeby(DECKP)}])
FLATS = [f"Flat{j}{pc}" for j in PANELS for pc in "abc"]
BKFLATS = [f"BulkFlat{bk}{nn}" for bk in ("Fore", "Aft") for nn in (2, 3, 4)]
S(["set.define", {"name": "Flat panels", "kind": "body", "where": madeby(FLATS + BKFLATS + ["CoamingRiser"])}])
S(["set.define", {"name": "Cut sheet: bulkheads and coaming", "kind": "face", "where": {"all": [
    madeby(BKFLATS + ["CoamingRiser"]), {"normal": {"along": "z"}}, {"above": {"z": f"{FLOOR} mm + 1 mm"}}]}}])
for b in BKFLATS:
    S(look(b, OKOUME))
S(look("CoamingRiser", WALNUT, 0.4))
S(["set.define", {"name": "Cut sheet: hull panels", "kind": "face", "where": {"all": [
    madeby([f"Flat{j}{pc}" for j in range(4) for pc in "abc"]),
    {"normal": {"along": "z"}}, {"above": {"z": f"{FLOOR} mm + 1 mm"}}]}}])
S(["set.define", {"name": "Cut sheet: deck", "kind": "face", "where": {"all": [
    madeby([f"Flat4{pc}" for pc in "abc"]),
    {"normal": {"along": "z"}}, {"above": {"z": f"{FLOOR} mm + 1 mm"}}]}}])


# ================================================================ assertions: the physics and the panels
WATER = {"set": "Displaced water"}
WOOD = {"set": "Wooden hull"}
S(V("mWood", "mPanels + mClamps * LClamp / Lhull + mBulkReal - rhoPly * tVol * Akey / cd * tDeck"))
S(V("xWood", "(mxPanels + mClamps * LClamp / Lhull * xClamps + rhoPly * tVol * tHull * (aBkFore * xBkF "
             "+ aBkAft * xBkA) * hatches - rhoPly * tVol * Akey / cd * tDeck * (xBack + offCoam)) / mWood"))
S(V("zWood", "(mzPanels + mClamps * LClamp / Lhull * zClamps + rhoPly * tVol * tHull * (aBkFore + aBkAft) "
             f"* hatches * (ZR_{N // 2} + Z0_{N // 2}) / 2 - rhoPly * tVol * Akey / cd * tDeck * ZR_kf) / mWood"))


def A(name, **kw):
    S(["assert.add", dict(name=name, **kw)])


A("displacement: the hull below the waterline holds the boat's weight in water", measure="volume", of=WATER,
  eq="Vt", tol="Vt / 500")
A("trim: the centre of buoyancy lies under the centre of gravity", measure="centerOfMass", of=WATER, axis="x",
  eq="LCG", tol="20 mm")
A("centre of buoyancy height KB", measure="centerOfMass", of=WATER, axis="z", eq="KB", tol="1 mm")
A("initial stability: GM = KB + BM - KG >= 0 (KB measured)", measure="centerOfMass", of=WATER, axis="z",
  min="KG - BM")
A("waterplane area", measure="area", of={"kind": "face", "where": {"all": [
    madeby(["Wet2", "Wet3", "Wet4"]), {"normal": {"along": "z"}}, {"above": {"z": "T - 1 mm"}}]}},
  eq="Awp", tol="Awp / 400")
A("wetted surface", measure="area", of={"kind": "face", "where": madeby(["Wet2", "Wet3", "Wet4"])}, eq="WS + Awp", tol="(WS + Awp) / 150")
A("weight of the wooden hull (formula of the panels' areas)", measure="mass", of=WOOD, eq="mWood",
  tol="mWood / 50")
A("centre of gravity of the wooden hull, x", measure="centerOfMass", of=WOOD, axis="x", eq="xWood", tol="15 mm")
A("centre of gravity of the wooden hull, z", measure="centerOfMass", of=WOOD, axis="z", eq="zWood", tol="8 mm")
A("freeboard: the sheer stays 40 mm above the waterline", measure="boxMin", of={"set": "Deck"}, axis="z",
  min="T + 40 mm")
A("the waterline ends on the plywood hull: the stern tip is dry", measure="boxMin", of="TipStern", axis="z", min="T")
A("the waterline ends on the plywood hull: the bow tip is dry", measure="boxMin", of="TipBow", axis="z", min="T")
A("the coaming stands on the deck", measure="boxMin", of="Coaming", axis="z",
  min=f"min(min(Z4_ka, Z4_kf), Z4_{N // 2}) - 2 mm")
A("coaming riser: the flat strip is as long as the riser's mid-thickness perimeter", measure="extent",
  of="CoamingRiser", axis="x", eq="Priser", tol="0.5 mm")
A("coaming riser: the flat strip spans the deck's rise along the keyhole plus the riser", measure="extent",
  of="CoamingRiser", axis="y", eq="zdMax - zdMin + riserH", tol="2 mm")
A("coaming riser: the flat strip's area is the riser's, perimeter x 30 mm", measure="area",
  of={"kind": "face", "where": {"all": [{"in": "CoamingRiser"}, {"normal": {"along": "z"}},
                                         {"above": {"z": f"{FLOOR} mm + 1 mm"}}]}},
  eq="Priser * riserH", tol="Priser * riserH / 200")
A("coaming: the riser stands 30 mm on the deck all round and the lip 6 mm on it (volume: projected ring x height)",
  measure="volume", of="Coaming", eq="(Akey1 - Akey) * riserH + (Akey2 - Akey1) * lipT",
  tol="((Akey1 - Akey) * riserH + (Akey2 - Akey1) * lipT) / 200")
A("coaming: from the deck to the top of the lip, deck's rise plus 36 mm", measure="extent", of="Coaming", axis="z",
  eq="zdMax - zdMin + riserH + lipT", tol="3 mm")
A("the cockpit lets the knees in (buttock-knee 0.34 x stature)", measure="extent", of="Coaming", axis="x",
  min="0.34 * hPad + backGap + 2 * (riserT + lipW)")
A("the coaming and the hatch covers stand on the deck", measure="boxMin",
  of={"kind": "body", "where": madeby(["Coaming", "HatchFore", "HatchAft"])}, axis="z",
  min=f"min(min(min(Z4_ka, Z4_kf), Z4_{N // 2}), if(hatches, min(Z4_hf, Z4_ha), 10 m)) - 2 mm")
A("the flat panels do not overlap", measure="overlap", of={"set": "Flat panels"}, **{"is": False})
for j in PANELS:
    # Panels 3 and 4 (j = 2, 3) exist with 2 and 3 chines only: each is checked together with the panel
    # two below it (same joints), whose terms count alone when it is absent (its width is then 0).
    nm = PNAME[j]
    grp = [j] if j in (0, 1, 4) else [j - 2, j]
    names = " and ".join(PNAME[g] for g in grp)
    on = lambda g, e: e if PON[g] is None else f"if({PON[g]}, {e}, 0)"
    ap = " + ".join((f"Ap{g}" if g < 4 else "ApD") for g in grp)
    holes = " + ".join(on(g, f"nHoles{g}") for g in grp)
    lp = f"max(Lp{grp[0]}, if({PON[j]}, Lp{j}, 0 mm))" if len(grp) > 1 else (f"Lp{j}" if j < 4 else "LpD")
    if j < 4:
        A(f"{names}: the curved panel's outside has the area of its development", measure="area",
          of={"kind": "face", "where": {"all": [inb([f"{PNAME[g]}S" for g in grp]), {"name": "*side(e5,*"}]}},
          eq=ap, tol=f"({ap}) / 1000 + 1 mm^2")
    pieces = [f"Flat{g}{pc}" for g in grp for pc in "abc"]
    A(f"{names}: the flat panel has the area of the curved one (less its stitch holes)", measure="area",
      of={"kind": "face", "where": {"all": [inb(pieces), {"normal": {"along": "z"}},
                                             {"above": {"z": f"{FLOOR} mm + 1 mm"}}]}},
      eq=f"{ap} - ({holes}) * pi * holeR^2", tol=f"({ap}) / 1000 + 1 mm^2")
    A(f"{names}: the flat panel is as long as the panel along its surface", measure="extent",
      of={"kind": "body", "where": inb(pieces)}, axis="x", eq=f"{lp} + 2 * pieceGap", tol="1 mm")
    for pc in "abc":
        A(f"{names}: piece {pc} fits a 2440 mm sheet", measure="extent",
          of={"kind": "body", "where": inb([f"Flat{g}{pc}" for g in grp])}, axis="x", max="2440 mm - 20 mm")


# ================================================================ the form
G1, G2, G3, G4 = "Hull", "Paddler and load", "Plywood", "Cockpit and hatches"
params = [
    {"name": "L", "label": "Length overall", "group": G1, "order": 1, "min": "5000 mm", "max": "5800 mm",
     "step": "10 mm", "unit": "mm", "description": "Tip to tip"},
    {"name": "B", "label": "Beam", "group": G1, "order": 2, "min": "if(chines == 1, 570 mm, 530 mm)", "max": "600 mm", "step": "5 mm",
     "unit": "mm", "description": "Widest beam at the sheer (the hull-deck joint); at least 570 mm with one chine, whose V bottom needs more beam for the same stability"},
    {"name": "D", "label": "Depth at the sheer", "group": G1, "order": 3, "min": "170 mm", "max": "min(230 mm, 0.36 * B)",
     "step": "5 mm", "unit": "mm", "description": "Height of the sheer above the keel at the widest station; the deck's crown comes on top. At most 0.36 x beam: deeper hulls carry their weight too high"},
    {"name": "crown", "label": "Deck crown", "group": G1, "order": 4, "min": "12 deg", "max": "26 deg",
     "step": "1 deg", "unit": "deg", "description": "Angle of the deck panels from the horizontal"},
    {"name": "rockB", "label": "Bow rise", "group": G1, "order": 5, "min": "250 mm", "max": "400 mm",
     "step": "5 mm", "unit": "mm", "description": "Rocker: how high the keel rises to the bow tip (Greenland ends: 250-350 mm)"},
    {"name": "rockS", "label": "Stern rise", "group": G1, "order": 6, "min": "220 mm", "max": "350 mm",
     "step": "5 mm", "unit": "mm", "description": "How high the keel rises to the stern tip"},
    {"name": "xmax", "label": "Widest station", "group": G1, "order": 7, "min": "0.44", "max": "0.52",
     "step": "0.005", "description": "Where the beam is widest, as a fraction of the length from the stern (below 0.5: swede form)"},
    {"name": "chines", "label": "Chines per side", "group": G1, "order": 8, "kind": "integer", "min": "1",
     "max": "3", "description": "Hard chines between keel and sheer on each side: 1 to 3, so 2 to 4 hull panels a side"},
    {"name": "form", "label": "Ends", "group": G1, "order": 9, "kind": "choice", "choicesFrom": "forms",
     "description": "How fast the bottom panels taper out towards the ends: fine ends are faster, full ends carry more"},
    {"name": "mPad", "label": "Paddler weight (kg)", "group": G2, "order": 1, "min": "mPadMin", "max": "mPadMax", "step": "1",
     "description": "The paddler, in kg: with the boat and the load it sets the waterline"},
    {"name": "hPad", "label": "Paddler height", "group": G2, "order": 2, "min": "1500 mm", "max": "2000 mm",
     "step": "10 mm", "unit": "mm", "description": "Stature: sets the paddler's centre of gravity, the cockpit's length and the foot brace"},
    {"name": "payload", "label": "Load (kg)", "group": G2, "order": 3, "min": "0", "max": "loadMax", "step": "1",
     "description": "Gear in the fore and aft compartments, in kg, half in each"},
    {"name": "water", "label": "Water", "group": G2, "order": 4, "kind": "choice", "choicesFrom": "waters",
     "description": "Sea water (1025 kg/m3) or fresh water (1000 kg/m3)"},
    {"name": "tHull", "label": "Hull plywood", "group": G3, "order": 1, "min": "3 mm", "max": "5 mm",
     "step": "0.5 mm", "unit": "mm", "description": "Okoume plywood for the hull panels and bulkheads (4 mm usual)"},
    {"name": "tDeck", "label": "Deck plywood", "group": G3, "order": 2, "min": "3 mm", "max": "4 mm",
     "step": "0.5 mm", "unit": "mm", "description": "Okoume plywood for the deck panels (3 mm usual)"},
    {"name": "cockL", "label": "Cockpit length", "group": G4, "order": 1, "min": "0.34 * hPad + 100 mm",
     "max": "min(950 mm, legReach + backGap - 100 mm)", "step": "5 mm", "unit": "mm",
     "description": "Keyhole opening, inside: at least the buttock-knee length (0.34 x stature) plus room behind the seat back"},
    {"name": "cockW", "label": "Cockpit width", "group": G4, "order": 2, "min": "380 mm", "max": "460 mm",
     "step": "5 mm", "unit": "mm", "description": "Keyhole opening, inside, at its widest (aft) end"},
    {"name": "hatches", "label": "Bulkheads and hatches", "group": G4, "order": 3, "kind": "boolean",
     "description": "Fore and aft bulkheads with round hatches (off: an open hull for float bags)"},
]
for p in params:
    S(["variable.publish", p])
S(["document.info", {
    "title": "Sea kayak (stitch and glue)",
    "description": "A Greenland-style multichine sea kayak in okoume plywood, built stitch and glue. Every hull "
                   "panel is a developable surface whose flat outline is computed from the hull's formulas, with "
                   "stitch holes and puzzle joints, ready to cut. The waterline, trim, stability (GM), "
                   "prismatic coefficient and wetted surface follow the paddler, the load and the lines, and "
                   "are checked against the exact geometry. Export the sets Cut sheet: hull panels and Cut "
                   "sheet: deck (DXF or SVG).",
    "author": "3DCraft Jigs", "licence": "CC-BY-4.0",
    "url": "https://github.com/johancoppens/3dcraft-jigs/tree/main/jigs/sea-kayak",
    "tags": ["kayak", "boat", "stitch and glue", "plywood", "developable", "hydrostatics", "cut sheet", "formula"]}])
S(["jig.export", {"path": "dist/sea-kayak.3dcraftjig"}])

print("[\n" + ",\n".join(json.dumps(s) for s in steps) + "\n]")
