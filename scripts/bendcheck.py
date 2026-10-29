#!/usr/bin/env python3
"""Proves that every sheet-metal part of a Jig can be bent on a press brake, at the points the range
check proves (document.sample: the defaults, the corners of the ranges, every choice, random points from
a fixed seed), with 3DCraft's sheetMetal.bendSequence and standard tooling.

    scripts/bendcheck.py <id> [--samples N] [--seed S] [--max-corners N] [--points K]

(defaults: 8 random points, 8 corners, seed 1: about 25 points; a point costs seconds to minutes).

The parts to check are in jigs/<id>/press.json:

    {"die": "V", "parts": [{"part": "Base", "body": "Base", "prove": {"corner": 1}, "owed": "why"}]}

`die` names the variable holding the V-die opening (a length); without it the opening is 8 t. `body` is
the body the part's faces are in (default the part's own: a part a union or a transform took). `prove`
says where the part must be proven bendable: absent at every point, a set of variable values at the
points where every one holds, false nowhere (what 3DCraft cannot prove yet, the reason in `owed`); the
part is still checked and reported at every point where it is on. Exit status 1 when a part is not
proven at a point where it must be.

A part's verdict at a point: proven (an order whose every step 3DCraft proves clear, with the punch
that gave it), collides (every order collides with every punch tried: with tools as long as the longest
bend, see below, which is not proof that the part cannot be bent), notProven (3DCraft could not prove a
stroke interval, or refused the search as too large) or off.

The tooling (millimetres, in the plane square to the bend; sheetMetal.bendSequence's frame: the punch's
tip centre at the origin and its body along +y, the die's top at y = 0 and its body below):

- `straight`: a straight punch with an 88-degree tip, 12 mm wide and 120 mm tall, in a clamp 80 mm wide
  and 100 mm tall (the clamp is part of the polygon: a flange that reaches it collides);
- `gooseneck`: a gooseneck punch with the same tip and clamp, its blade 8 mm wide at the tip, a throat
  29 mm deep from 15 to 95 mm above the tip on the +x side; and the same punch turned round in the clamp
  (`gooseneck turned`, the throat on the -x side), since the frame's x depends on the bend's direction;
- the die: a single V of 88 degrees, opening V (8 t unless press.json names a variable), 2 V wide
  (at least 30 mm) and 60 mm tall.

Each punch is tried in that order for each part, the next only when the last one collided with the
punch; a part passes when one of them gives a feasible order, every step at least 0.5 mm clear.

The tools are as long as the part's longest bend (measured on the part: a bend's two skins are
cylinders of radius R and R + T over its angle, so their area gives its length), centred on each bend.
So the punch covers every bend, and since a prism inside another is farther from everything, an order
that clears with these tools also clears with a punch segmented to each bend's own length (but no
shorter). Tools longer than a bend are what make a box's last bends collide with its standing ends:
3DCraft takes one tool length for every bend (see the README of each Jig).

Uses only the Python standard library; CRAFT3D_CLI or craft3d-cli on PATH.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TIP = math.tan(math.radians(44.0))        # an 88-degree tip: flanks 44 degrees off the y axis
CLAMP = [(40.0, 120.0), (40.0, 220.0), (-40.0, 220.0), (-40.0, 120.0)]


def straight():
    w = 6.0
    return [(0.0, 0.0), (w, w / TIP), (w, 120.0)] + CLAMP + [(-w, 120.0), (-w, w / TIP)]


def gooseneck(turned=False):
    w = 4.0
    pts = [(0.0, 0.0), (w, w / TIP), (w, 15.0), (-25.0, 45.0), (-25.0, 95.0), (40.0, 120.0),
           (40.0, 220.0), (-40.0, 220.0), (-40.0, 40.0), (-w, w / TIP)]
    if turned:
        pts = [(-x, y) for x, y in reversed(pts)]
    return pts


CLEARANCE = 0.5           # mm, the least gap proven between a tool and the part
PUNCHES = [("straight", straight()), ("gooseneck", gooseneck()), ("gooseneck turned", gooseneck(True))]


def die(v):
    depth = (v / 2.0) / TIP
    half = max(v, 15.0)
    return [(-half, 0.0), (-v / 2.0, 0.0), (0.0, -depth), (v / 2.0, 0.0), (half, 0.0), (half, -60.0),
            (-half, -60.0)]


def cli():
    c = os.environ.get("CRAFT3D_CLI") or shutil.which("craft3d-cli")
    if not c or not os.access(c, os.X_OK):
        sys.exit("craft3d-cli not found: put it on PATH or set CRAFT3D_CLI")
    return c


def run(jig, cmds, keep_going=False):
    """Runs the commands on the Jig (nothing saved); returns one result per command (with keep_going a
    command that fails gives {"failed": id, "error": text} and the rest still run)."""
    args = [cli(), "run", jig] + (["--keep-going"] if keep_going else [])
    cmds = [["jig.edit", {}]] + cmds          # an editable copy: the check adds measures to it
    for cmd, params in cmds:
        args += ["--cmd", cmd, "--params", json.dumps(params)]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0 and not keep_going:
        raise RuntimeError("craft3d-cli failed: %s" % (out.stderr.strip() or out.stdout.strip())[-2000:])
    lines = [json.loads(l) for l in out.stdout.splitlines() if l.strip().startswith("{")]
    if len(lines) != len(cmds):
        raise RuntimeError("expected %d results, got %d" % (len(cmds), len(lines)))
    return lines[1:]


def longest_bend(jig, values, part, body):
    """The longest bend of a part that is on, measured on its body: a bend's two skins (faces
    copy(0) and copy(1) of face 2 id - 1) are cylinders of radius R and R + T over its angle, so their
    area is angle (2 R + T) times the bend's length."""
    res = run(jig, [["param.set", {"values": values}], ["sheetMetal.bends", {"feature": part}]])
    bends = res[1]["bends"]
    measures = [["variable.measure", {
        "name": "bendcheck%d" % b["id"], "measure": "area",
        "of": {"kind": "face", "where": [{"in": body}, {"madeBy": part},
                                         {"name": "*copy(*)/*face(%d)" % (2 * b["id"] - 1)}]}}] for b in bends]
    areas = run(jig, [["param.set", {"values": values}]] + measures)[1:]
    best = 0.0
    for b, m in zip(bends, areas):
        if m.get("status") != "known" or not m.get("value"):
            raise RuntimeError("%s: the bend of flange %s could not be measured: %s" % (part, b["id"], m.get("message")))
        theta = math.radians(b["angle"])
        best = max(best, m["value"] / (theta * (2.0 * b["radius"] + b["thickness"])))
    return best


def poly(points):
    return [[round(x, 6), round(y, 6)] for x, y in points]


def holds(cond, var):
    """A part's `prove` condition: {variable: value, ...}, every one equal; absent: always; false:
    never (what 3DCraft cannot prove yet, its reason in the part's `owed`)."""
    if cond is False:
        return False
    return all(abs((var.get(k) if var.get(k) is not None else math.nan) - v) < 1e-9 for k, v in (cond or {}).items())


def sequence(jig, values, part, punch, v, length):
    """One sheetMetal.bendSequence: its result, or {"error": text} when 3DCraft refuses the search."""
    try:
        return run(jig, [["param.set", {"values": values}],
                         ["sheetMetal.bendSequence", {"feature": part, "punch": poly(punch), "die": poly(die(v)),
                                                      "length": length, "clearance": CLEARANCE}]])[1]
    except RuntimeError as e:
        return {"error": str(e).split("sheetMetal.bendSequence: ")[-1]}


def check_point(jig, values, press):
    """Returns [(part, verdict)] at one point. A verdict is skipped (the part is off), proven (a feasible
    order with one of the punches), collides (every order collides with every punch: with tools as long
    as the longest bend, which is not proof that the part cannot be bent) or notProven (3DCraft could not
    prove a stroke interval, or refused the search as too large)."""
    parts = press["parts"]
    doc = run(jig, [["param.set", {"values": values}], ["document.inspect", {"measures": False}]])[1]
    var = {x["name"]: x.get("value") for x in doc["variables"]}
    status = {f.get("name"): f.get("status") for f in doc["features"]}
    v = var[press["die"]] if press.get("die") else 8.0 * var["t"]
    out = []
    for i, p in enumerate(parts):
        part = p["part"]
        must = holds(p.get("prove", {}), var)
        if status.get(part) != "ok":
            out.append((part, must, {"verdict": "skipped"}))
            continue
        length = longest_bend(jig, values, part, p.get("body", part))
        if not length:
            out.append((part, must, {"verdict": "error", "why": "no bend found"}))
            continue
        tried = []
        verdict = None
        for name, punch in PUNCHES:
            r = sequence(jig, values, part, punch, v, length)
            if r.get("feasible"):
                verdict = {"verdict": "proven", "punch": name, "order": r["order"], "length": length, "V": v,
                           "least": min((s["proven"] for s in r["steps"] if s.get("proven") is not None),
                                        default=None)}
                break
            coll = r.get("collisions") or []
            unproven = [c for c in coll if "notProven" in c]
            tried.append({"punch": name, "error": r.get("error"), "collisions": len(coll),
                          "notProven": len(unproven), "first": (unproven or coll or [None])[0]})
            if r.get("error") or not any(c.get("tool") == "punch" for c in coll):
                break                       # another punch changes nothing
        if verdict is None:
            kind = "notProven" if any(x["error"] or x["notProven"] for x in tried) else "collides"
            verdict = {"verdict": kind, "tried": tried, "length": length, "V": v}
        out.append((part, must, verdict))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-corners", type=int, default=8)
    ap.add_argument("--points", type=int, default=0, help="check only the first K points (0: all)")
    a = ap.parse_args()
    jig = os.path.join(ROOT, "dist", a.id + ".3dcraftjig")
    with open(os.path.join(ROOT, "jigs", a.id, "press.json")) as f:
        press = json.load(f)
    sample = run(jig, [["document.sample", {"samples": a.samples, "seed": a.seed, "maxCorners": a.max_corners,
                                           "values": True, "timeLimitMs": None}]])[0]
    points = sample["points"]
    if a.points:
        points = points[:a.points]
    failed = 0
    tally = {}
    for p in points:
        verdicts = check_point(jig, p["values"], press)
        words = []
        bad = []
        for part, must, v in verdicts:
            k = v["verdict"]
            words.append("%s %s" % (part, "%s %s (%s)" % (k, v["order"], v["punch"]) if k == "proven" else
                                    k if must or k == "skipped" else "%s (owed)" % k))
            if k != "skipped":
                key = (part, k if k == "proven" else k + (" where it must be proven" if must else " (owed)"))
                tally[key] = tally.get(key, 0) + 1
            if must and k not in ("proven", "skipped"):
                bad.append((part, v))
        print("point %d (%s): %s" % (p["index"], p["kind"], "; ".join(words)), flush=True)
        if bad:
            failed += 1
            print("  values: %s" % json.dumps(p["values"]))
            for part, v in bad:
                print("  %s: %s" % (part, json.dumps(v)))
    print("bendcheck %s: %d of %d points pass (samples %d, seed %d, max corners %d)" % (
        a.id, len(points) - failed, len(points), a.samples, a.seed, a.max_corners))
    for (part, k), n in sorted(tally.items()):
        print("  %s: %s at %d points" % (part, k, n))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
