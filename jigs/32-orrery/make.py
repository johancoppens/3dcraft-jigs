#!/usr/bin/env python3
"""Writes the data tables of the orrery into build.json: the bodies' mean motions and the gear trains.

Input (committed): data/elements.json, the mean longitudes at J2000 and their rates, copied from E. M. Standish's
Table 1 (JPL, the planets) and from the IERS Conventions 2003 fundamental arguments (ERFA, the Moon).
Output, replaced in place in build.json (the steps `table.set` named `bodies`, `trains` and `train_limits`):

- `bodies`: per body its mean longitude at J2000.0 (deg) and its sidereal mean motion (deg per Julian century).
- `trains`: per choice of planets, Moon and largest period error, the tooth counts of every body's train. Each train
  runs from the input arbor (the crank) through a compound on the lay arbor to the body's tube on the centre post:
  stage one is gear A (on the input arbor) driving B (on the lay arbor), stage two C (fixed to B) driving D (on the
  tube). All stage-one pairs share the centre distance input to lay arbor, all stage-two pairs lay arbor to centre, so
  every stage-one pair has the same tooth sum (`stage_one_sum`) and every stage-two pair another (`stage_two_sum`). One
  turn of the crank is one sidereal year of the Earth; the tube turns (A / B) (C / D) times per turn.
- `train_limits`: per choice of planets and Moon, the smallest largest-period-error that has a train: the least value
  of that parameter.

The search: for each choice it tries the tooth sums from the smallest gearbox up (least stage_one_sum +
stage_two_sum) and keeps the first whose every body has a train within the error, ties broken by the least worst
error. Each gear has 12 to 104 teeth (the largest gear at the least module within 160 sheet thicknesses); each mesh has a contact ratio of at least 1.2 and no involute interference (the
tip of each gear within the other's limit point, sqrt(rb^2 + (a sin alpha)^2), KHK eq. for interference); each gear's
root is RIM clear of its bore; the lay arbor's gears clear the tubes and the input arbor by GAP, and the input arbor
can be placed so its gears clear the tubes and the tube gears clear it (all at the smallest module: a larger module
only adds room). The model checks these again at its own module (assertions).

Runs offline, deterministic, standard library only. Usage: python3 make.py [--print]
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INCH = 25.4

# Mechanical limits of the search; the model's variables of the same names hold the same values.
TEETH_MIN = 12
GEAR_SIZE_RATIO = 160                 # the model's rule: a gear's tip diameter at most 160 sheet thicknesses
SHEET = 1.0                           # mm, the brass sheet
MODULE_MIN = 1.5                      # mm: the least module of the form
TEETH_MAX = int(GEAR_SIZE_RATIO * SHEET / MODULE_MIN - 2)   # 104: the largest gear allowed at the least module
PRESSURE_ANGLE = math.radians(20)     # ISO 53 basic rack
CONTACT_MIN = 1.2
ROD = INCH / 8                        # K&S 8164 brass rod, 1/8 in: the arbors and the centre post
TUBE_STEP = INCH / 32                 # K&S telescopic brass tube: outside diameters 1/8 in + k/32 in
BUSH = ROD + TUBE_STEP                # the lay arbor's compounds turn on a 5/32 in tube
BORE_FIT = 0.1                        # mm: a bore is its shaft's diameter plus this
RIM = 1.5                             # mm: least brass between a bore and the tooth roots
GAP = 1.0                             # mm: least gap from a gear's tips to a tube or arbor it passes

KEYS = ["me", "ve", "ea", "mo", "ma", "ju", "sa"]   # the tubes from the inside out (the Moon's only with the Moon)
SETS = ["Mercury to Earth", "Mercury to Mars", "Mercury to Jupiter", "Mercury to Saturn"]
ERROR_STEPS = list(range(2, 16))      # largest period error, in hundredths of a percent: 0.02 % to 0.15 %


# Check values, typed again from the cited sources, so that a slip in data/elements.json stops the script:
# Standish's Table 1 (L, L_rate) and the IERS / ERFA constants; and a second source, the NASA fact sheets' sidereal
# periods (days), which the derived periods must match to 100 ppm, and the NASA Saturn sheet's J2000 mean longitude.
TABLE_1 = {"me": (252.25032350, 149472.67411175), "ve": (181.97909950, 58517.81538729),
           "ea": (100.46457166, 35999.37244981), "ma": (-4.55343205, 19140.30268499),
           "ju": (34.39644051, 3034.74612775), "sa": (49.95424423, 1222.49362201)}
ERFA = (335779.526232, 1739527262.8478, 450160.398036, -6962890.5431, 0.024381750)
NASA_PERIOD = {"me": 87.969, "ve": 224.701, "ea": 365.256, "mo": 27.3217, "ma": 686.980, "ju": 4332.589,
               "sa": 10755.699}
NASA_SATURN_LONGITUDE = 49.94432


def check_data(data, bodies):
    for row in data["planets"]["rows"]:
        if (row["L"], row["L_rate"]) != TABLE_1[row["key"]]:
            raise SystemExit("data/elements.json: %s differs from Standish's Table 1" % row["name"])
    moon = data["moon"]
    if (moon["F_arcsec"], moon["F_rate_arcsec"], moon["Omega_arcsec"], moon["Omega_rate_arcsec"],
            moon["pA_rate_rad"]) != ERFA:
        raise SystemExit("data/elements.json: the Moon's constants differ from ERFA's")
    for key, period in NASA_PERIOD.items():
        derived = 36525 * 360 / bodies[key][2]
        if abs(derived / period - 1) > 1e-4:
            raise SystemExit("%s: derived period %.4f d is not within 100 ppm of NASA's %.4f d" % (key, derived, period))
    if abs(bodies["sa"][1] - NASA_SATURN_LONGITUDE) > 0.05:
        raise SystemExit("Saturn's J2000 mean longitude is not within 0.05 degrees of NASA's")


def elements():
    data = json.loads((HERE / "data" / "elements.json").read_text())
    bodies = {}
    for row in data["planets"]["rows"]:
        bodies[row["key"]] = (row["name"], row["L"] % 360.0, row["L_rate"])
    moon = data["moon"]
    longitude = ((moon["F_arcsec"] + moon["Omega_arcsec"]) / 3600.0) % 360.0
    rate = (moon["F_rate_arcsec"] + moon["Omega_rate_arcsec"]) / 3600.0 - math.degrees(moon["pA_rate_rad"])
    bodies["mo"] = ("Moon", longitude, rate)
    check_data(data, bodies)
    return bodies


BODIES = elements()


def turns_per_year(key):
    """Turns of the body's tube per sidereal year of the Earth (per crank turn)."""
    return BODIES[key][2] / BODIES["ea"][2]


def tube_outside(index):
    """Outside diameter of tube `index` (1 innermost): 5/32 in, 3/16 in, ..."""
    return ROD + index * TUBE_STEP


def tip(z):
    return MODULE_MIN * (z / 2 + 1)


def root(z):
    return MODULE_MIN * (z / 2 - 1.25)


def mesh_ok(z1, z2):
    """Contact ratio at least CONTACT_MIN and no involute interference, ISO 53 teeth at standard centre distance."""
    a = MODULE_MIN * (z1 + z2) / 2
    rb1, rb2 = MODULE_MIN * z1 / 2 * math.cos(PRESSURE_ANGLE), MODULE_MIN * z2 / 2 * math.cos(PRESSURE_ANGLE)
    line = a * math.sin(PRESSURE_ANGLE)
    if tip(z1) > math.hypot(rb1, line) + 1e-9 or tip(z2) > math.hypot(rb2, line) + 1e-9:
        return False
    contact = (math.sqrt(tip(z1) ** 2 - rb1 ** 2) + math.sqrt(tip(z2) ** 2 - rb2 ** 2) - line) / (
        math.pi * MODULE_MIN * math.cos(PRESSURE_ANGLE))
    return contact >= CONTACT_MIN


def bodies_built(planets, moon):
    return ["me", "ve", "ea"] + (["mo"] if moon else []) + ["ma", "ju", "sa"][:planets - 3]


_memo = {}


def best_train(key, tube, sum_one, sum_two):
    """The best (error, a, b, c, d) for body `key` on tube number `tube`, or None."""
    memo_key = (key, tube, sum_one, sum_two)
    if memo_key in _memo:
        return _memo[memo_key]
    want = turns_per_year(key)
    lay_to_centre, input_to_lay = MODULE_MIN * sum_two / 2, MODULE_MIN * sum_one / 2
    tube_radius = tube_outside(tube) / 2
    best = None
    for a in range(max(TEETH_MIN, sum_one - TEETH_MAX), min(TEETH_MAX, sum_one - TEETH_MIN) + 1):
        b = sum_one - a
        # B (lay arbor) clears tube `tube`, which reaches down through B's layer to stand on the gear below.
        if lay_to_centre - tip(b) < tube_radius + GAP:
            continue
        if root(a) - (ROD + BORE_FIT) / 2 < RIM or root(b) - (BUSH + BORE_FIT) / 2 < RIM:
            continue
        ideal = want * b / a
        c_ideal = ideal * sum_two / (1 + ideal)
        for c in sorted({math.floor(c_ideal), math.ceil(c_ideal)}):
            d = sum_two - c
            if not (TEETH_MIN <= c <= TEETH_MAX and TEETH_MIN <= d <= TEETH_MAX):
                continue
            if root(d) - (tube_outside(tube) + BORE_FIT) / 2 < RIM or root(c) - (BUSH + BORE_FIT) / 2 < RIM:
                continue
            if input_to_lay - tip(c) < ROD / 2 + GAP:            # C clears the input arbor
                continue
            error = abs(a * c / (b * d) / want - 1)
            if best is not None and error >= best[0]:
                continue
            if not (mesh_ok(a, b) and mesh_ok(c, d)):
                continue
            best = (error, a, b, c, d)
    _memo[memo_key] = best
    return best


def search(planets, moon, limit):
    keys = bodies_built(planets, moon)
    hardest_first = sorted(keys, key=lambda k: -abs(math.log(turns_per_year(k))))
    for total in range(4 * TEETH_MIN, 4 * TEETH_MAX + 1):
        found = None
        for sum_one in range(2 * TEETH_MIN, min(2 * TEETH_MAX, total - 2 * TEETH_MIN) + 1):
            sum_two = total - sum_one
            if sum_two > 2 * TEETH_MAX:
                continue
            trains, worst = {}, 0.0
            for key in hardest_first:
                train = best_train(key, keys.index(key) + 1, sum_one, sum_two)
                if train is None or train[0] > limit:
                    trains = None
                    break
                trains[key] = train
                worst = max(worst, train[0])
            if trains is None:
                continue
            # The input arbor must close the triangle: its gears clear the tubes, the tube gears clear it.
            need = max(max(tip(trains[k][1]) + tube_outside(keys.index(k) + 1) / 2 + GAP,
                           tip(trains[k][4]) + ROD / 2 + GAP) for k in keys)
            if need > MODULE_MIN * (sum_one + sum_two) / 2:
                continue
            if found is None or worst < found[0]:
                found = (worst, sum_one, sum_two, trains)
        if found:
            return found
    return None


def tables():
    rows, limits = [], []
    for planets in range(3, 3 + len(SETS)):
        for moon in (0, 1):
            results = {step: search(planets, moon, step * 1e-4 + 1e-12) for step in ERROR_STEPS}
            feasible = [s for s in ERROR_STEPS if results[s]]
            if not feasible:
                raise SystemExit("no train for planets %d moon %d" % (planets, moon))
            least = min(feasible)
            limits.append(["%d-%d" % (planets - 2, moon), least / 100])
            for step in ERROR_STEPS:
                # A step below the least is never selected (the parameter's minimum); it repeats the least's train.
                worst, sum_one, sum_two, trains = results[step] or results[least]
                largest = max(max(t[1:]) for t in trains.values())
                row = ["%d-%d-%d" % (planets - 2, moon, step), sum_one, sum_two, round(worst * 1e6, 1), largest]
                for key in KEYS:
                    if key in trains:
                        row += list(trains[key][1:])
                    else:                                  # not built in this row: an even split, never used
                        row += [sum_one // 2, sum_one - sum_one // 2, sum_two // 2, sum_two - sum_two // 2]
                rows.append(row)
    columns = ["choice", "stage_one_sum", "stage_two_sum", "worst_ppm", "largest"]
    for key in KEYS:
        columns += ["a_" + key, "b_" + key, "c_" + key, "d_" + key]
    trains_step = ["table.set", {"name": "trains", "columns": columns, "rows": rows}]
    limits_step = ["table.set", {"name": "train_limits", "columns": ["choice", "least_error"], "rows": limits}]
    bodies_step = ["table.set", {"name": "bodies", "columns": [
        "body", {"name": "longitude", "unit": "deg"}, "rate", "period"],
        "rows": [[BODIES[k][0], round(BODIES[k][1], 8), round(BODIES[k][2], 8),
                  36525 * 360 / round(BODIES[k][2], 8)] for k in KEYS]}]   # the period exactly the rate's, unrounded
    return [bodies_step, trains_step, limits_step]


def main():
    steps = tables()
    if "--print" in sys.argv:
        for row in steps[1][1]["rows"]:
            print(row[:5])
        print(steps[2][1]["rows"])
        print(steps[0][1]["rows"])
        return
    target = HERE / "build.json"
    script = json.loads(target.read_text())
    names = {s[1]["name"]: s for s in steps}
    replaced = 0
    for i, step in enumerate(script):
        if step[0] == "table.set" and step[1].get("name") in names:
            script[i] = names[step[1]["name"]]
            replaced += 1
    if replaced != len(names):
        raise SystemExit("build.json must hold the table.set steps %s once each" % sorted(names))
    target.write_text("[\n" + ",\n".join(json.dumps(s, ensure_ascii=False) for s in script) + "\n]\n")
    print("wrote %d tables into build.json" % replaced)


if __name__ == "__main__":
    main()
