#!/usr/bin/env python3
"""The gear-train search of the orrery Jig (imported by gen.py; python3 trains.py prints the table).

Every train runs from the input shaft L1 (the crank) to a tube on the centre post C through a compound
on the lay shaft L2: stage 1 is A (on L1) driving B (on L2), stage 2 is C (on L2, fixed to B) driving D
(on the planet's tube). All stage-1 pairs share the centre distance L1-L2 and all stage-2 pairs the
centre distance L2-C, so every stage-1 pair has the same tooth sum S12 and every stage-2 pair S2. One
turn of the crank is one sidereal year of the Earth (365.256 days); the tube turns
ratio = (zA / zB) * (zC / zD) times per crank turn, so its period is 365.256 d / ratio.
"""
import math

YEAR = 365.256  # days: the Earth's sidereal orbital period (NASA Earth fact sheet)
# key, name, sidereal period (days, NASA fact sheets), mean longitude at J2000 (deg, Standish / Meeus)
BODIES = [
    ("Me", "Mercury", 87.969, 252.25032350),
    ("Ve", "Venus", 224.701, 181.97909950),
    ("Ea", "Earth", 365.256, 100.46457166),
    ("Mo", "Moon", 27.3217, 218.3164477),
    ("Ma", "Mars", 686.980, 355.44656795),
    ("Ju", "Jupiter", 4332.589, 34.39644051),
    ("Sa", "Saturn", 10759.22, 49.95424423),
]
SETS = ["Mercury to Earth", "Mercury to Mars", "Mercury to Jupiter", "Mercury to Saturn"]
TARGETS = [("0.5 % (5000 ppm)", 5000), ("0.1 % (1000 ppm)", 1000), ("0.05 % (500 ppm)", 500),
           ("0.03 % (300 ppm)", 300)]
ZMAX = [60, 70, 80, 90, 100, 110, 120]

# Fixed sizes (mm) the search keeps clear, at the smallest module (1 mm; a larger module only adds room).
ZMIN = 12          # fewest teeth of any gear
R_SHAFT = 2.0      # radius of the centre post and of both spindles (4 mm rod)
CLR = 0.25         # radial running clearance of tubes and loose bores
WALL = 1.2         # tube wall
FIT = 0.01         # radial gap of a gear fixed on its tube or spindle (glued)
RIM = 1.5          # least material between a bore and the tooth roots
GAP = 0.5          # least radial gap between a gear's tips and a tube or spindle it passes


def tube_in(k):
    """Inner radius of tube k (1 innermost); tube 0 is the centre post (radius R_SHAFT)."""
    return R_SHAFT + CLR + (k - 1) * (WALL + CLR)


def tube_out(k):
    return R_SHAFT if k == 0 else tube_in(k) + WALL


def zmin_d(k, m=1.0):
    """Fewest teeth of a gear fixed on tube k: its root circle RIM outside the bore."""
    return max(ZMIN, math.ceil(2 * (tube_out(k) + FIT + RIM) / m + 2.5 - 1e-9))


def enabled(s, moon):
    keys = ["Me", "Ve", "Ea"] + (["Mo"] if moon else []) + ["Ma", "Ju", "Sa"][:s - 1]
    return keys


PERIOD = {b[0]: b[2] for b in BODIES}
_memo = {}


def best_pair(key, k, S12, S2, Z):
    """Best (err, a, b, c, d) for body key on tube k with tooth sums S12, S2 and at most Z teeth, or None."""
    mk = (key, k, S12, S2, Z)
    if mk in _memo:
        return _memo[mk]
    q = YEAR / PERIOD[key]
    zd_min = zmin_d(k)
    best = None
    for a in range(max(ZMIN, S12 - Z), min(Z, S12 - ZMIN) + 1):
        b = S12 - a
        # B (on L2, in the layer below D) clears tube k, which reaches down into that layer to rest on the
        # gear of tube k-1.
        if S2 / 2 - (b / 2 + 1) < tube_out(k) + GAP:
            continue
        r1 = a / b
        qq = q / r1
        cf = qq * S2 / (1 + qq)
        for c in sorted({math.floor(cf), math.ceil(cf)}):
            d = S2 - c
            if c < ZMIN or c > Z or d < zd_min or d > Z:
                continue
            # C (on L2) clears the spindle L1.
            if S12 / 2 - (c / 2 + 1) < R_SHAFT + GAP:
                continue
            err = abs(q / (r1 * c / d) - 1)
            if best is None or err < best[0]:
                best = (err, a, b, c, d)
    _memo[mk] = best
    return best


def d1_req(sol, keys):
    """Least distance C-L1 (m = 1) at which every A clears the tubes and every D the spindle L1."""
    req = 0
    for k, key in enumerate(keys, start=1):
        _, a, b, c, d = sol[key]
        req = max(req, a / 2 + 1 + tube_out(k) + GAP, d / 2 + 1 + R_SHAFT + GAP)
    return req


def search(s, moon, Z, target_ppm):
    """The smallest gearbox (least S12 + S2) whose every train is within target_ppm; ties: least worst error."""
    keys = enabled(s, moon)
    # Hardest first, so a failing pair is dropped early.
    order = sorted(keys, key=lambda x: -abs(math.log(YEAR / PERIOD[x])))
    tgt = target_ppm * 1e-6
    for tot in range(4 * ZMIN, 4 * Z + 1):
        found = None
        for S12 in range(2 * ZMIN, min(2 * Z, tot - 2 * ZMIN) + 1):
            S2 = tot - S12
            if S2 > 2 * Z:
                continue
            sol = {}
            worst = 0
            for key in order:
                bp = best_pair(key, keys.index(key) + 1, S12, S2, Z)
                if bp is None or bp[0] > tgt:
                    sol = None
                    break
                sol[key] = bp
                worst = max(worst, bp[0])
            if sol is None:
                continue
            if d1_req(sol, keys) > S12 / 2 + S2 / 2:
                continue
            if found is None or worst < found[0]:
                found = (worst, S12, S2, sol)
        if found:
            return found
    return None


def table():
    """Rows keyed set-moon-zmax-target; an infeasible row repeats the nearest feasible one of more teeth
    (it is never used: the max-teeth parameter's least value is the least feasible one, zlim)."""
    rows, zlim = [], []
    for s in range(1, len(SETS) + 1):
        for moon in (0, 1):
            for ti, (_, ppm) in enumerate(TARGETS, start=1):
                res = {Z: search(s, moon, Z, ppm) for Z in ZMAX}
                feas = [Z for Z in ZMAX if res[Z]]
                if not feas:
                    raise SystemExit("no train within %d ppm for set %d moon %d" % (ppm, s, moon))
                zlim.append(("%d-%d-%d" % (s, moon, ti), min(feas)))
                for Z in ZMAX:
                    r = res[Z] or res[min(feas)]
                    rows.append((s, moon, Z, ti, r))
    return rows, zlim


if __name__ == "__main__":
    import time
    t = time.time()
    rows, zlim = table()
    for s, moon, Z, ti, r in rows:
        print(s, moon, Z, TARGETS[ti - 1][1], r[1], r[2], "%.0f ppm" % (r[0] * 1e6),
              {k: v[1:] for k, v in r[3].items()})
    print(zlim)
    print("%.1f s" % (time.time() - t))
