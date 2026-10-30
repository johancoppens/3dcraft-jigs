#!/usr/bin/env python3
"""Builds and checks the assemblies made from Jigs (3DCraft .3dcraftasm files).

    scripts/asm.py build [id ...]     run jigs/<id>/assembly/NN-*.json in order (each writes its file)
    scripts/asm.py check [id ...]     check dist/ against jigs/<id>/assembly/check.json
    scripts/asm.py all [id ...]       both

Without ids: every Jig that has an assembly/ folder. An assembly is built from the Jig in dist/ (build the
Jig first, scripts/build.sh), so `build` reads dist/<id>.3dcraftjig and writes dist/<name>.3dcraftasm,
packed (it carries copies of its sources and opens anywhere). Intermediate parts and assemblies (the
strandbeest's bar and pin parts, its leg) go to build/, which is not committed.

Each NN-*.json is a command batch, run as `craft3d-cli run --script` on a fresh session; it starts with
file.new (a part) or assembly.new and ends by saving. jigs/<id>/assembly/gen.py writes them, and
check.json, which says what `check` proves on each built assembly (exit status 1 when anything fails):

- "at_rest": {"dof": n, "identity": [instances]}: assembly.solve is ok with n degrees of freedom left,
  and the instances listed sit exactly where their source puts them (pose within 1e-9 of the
  identity), so the mates reproduce the Jig's own placement;
- "motion": [{"t": [t0, t1], "samples": n}]: motion.check of every assertion of the assembly at n
  moments of the motion; no assertion may fail or be in error at any sample (a sampled check: what
  happens between two samples is not seen, and the result says sampled: true), and no dead point may be
  met. An assertion that is only notProven somewhere (3DCraft found a value within the bounds but could
  not pin it down closely enough: a clearance between spline faces) is printed as a warning with the
  value found, as check-range counts it, and does not fail the check;
- "traces": [{"name", "point", "samples", "svg": bool}]: view.trace of a point over t in [0, 1], written
  to build/evidence/<id>/ as SVG when asked (file.export with trace);
- "willis": {"sun", "carrier", "ratio", "tol_deg"}: from two traces about the z axis, the sun's turn
  over the carrier's at every sample equals the ratio (the angles unwrapped from sample to sample);
- "foot": [{"trace", "crank0_deg", "turn_deg", "tol": mm}]: a trace's points (x, z) against the
  closed-form foot of Jansen's linkage (circle intersections, as the strandbeest-leg Jig computes it) at
  the crank angle crank0 + turn * t of each sample;
- "renders": [t, ...]: view.motion at each t, then view.render into build/evidence/<name>/ (look at them),
  seen from "view" (iso, front, ...; default iso);
- "replay": {"frames": n}: the motion as an animated GIF, build/evidence/<name>/<name>.gif (craft3d-cli
  replay with view.replay's motion; needs ffmpeg).

Uses only the Python standard library; CRAFT3D_CLI or craft3d-cli on PATH. Every run is one process
at a time.
"""
import glob
import json
import math
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EVIDENCE = os.path.join("build", "evidence")


def cli():
    path = os.environ.get("CRAFT3D_CLI") or shutil.which("craft3d-cli")
    if not path or not os.access(path, os.X_OK):
        sys.exit("craft3d-cli not found: put it on PATH or set CRAFT3D_CLI")
    return path


def run(args, label):
    """Runs craft3d-cli in the repository root; returns its JSON lines (a failed command stops it).
    glibc's per-thread arenas hold on to freed memory; two keep a long motion check small."""
    env = dict(os.environ)
    env.setdefault("MALLOC_ARENA_MAX", "2")
    r = subprocess.run([cli()] + args, cwd=ROOT, capture_output=True, text=True, env=env)
    out = []
    for line in r.stdout.splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            out.append(line)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit("FAILED: %s (exit %d)" % (label, r.returncode))
    return out


def ids_with_assemblies(ids):
    for jig in ids:
        if not os.path.exists(os.path.join(ROOT, "jigs", jig, "assembly", "check.json")):
            raise SystemExit("jigs/%s has no assembly/check.json" % jig)
    if ids:
        return ids
    return sorted(os.path.basename(os.path.dirname(os.path.dirname(p)))
                  for p in glob.glob(os.path.join(ROOT, "jigs", "*", "assembly", "check.json")))


def build(jig):
    for script in sorted(glob.glob(os.path.join(ROOT, "jigs", jig, "assembly", "[0-9][0-9]-*.json"))):
        rel = os.path.relpath(script, ROOT)
        with open(script) as f:
            saves = sorted({p["path"] for c, p in json.load(f) if c == "file.save"})
        # file.save makes no folders; a batch saves early (sources are read relative to its file), so a
        # failed one would leave a half-built file: it is removed.
        for path in saves:
            os.makedirs(os.path.dirname(os.path.join(ROOT, path)), exist_ok=True)
        try:
            run(["run", "--script", rel], rel)
        except SystemExit:
            for path in saves:
                if os.path.exists(os.path.join(ROOT, path)):
                    os.remove(os.path.join(ROOT, path))
            raise
        print("built %s" % rel)


def unwrap(angles):
    out = []
    for a in angles:
        if out:
            a += 2 * math.pi * round((out[-1] - a) / (2 * math.pi))
        out.append(a)
    return out


def leg(th, crank=15.0):
    """Jansen's leg at crank angle th (radians), as the strandbeest-leg Jig works it out: the joints
    as circle-circle intersections on the branches of Jansen's leg. Returns {joint: (x, y)}."""
    u = crank / 15.0
    L = {k: v * u for k, v in dict(a=38.0, b=41.5, c=39.3, d=40.1, e=55.8, f=39.4, g=36.7, h=65.7,
                                   i=49.0, j=50.0, k=61.9, l=7.8, m=15.0).items()}
    branch = dict(C=-1, D=1, E=1, F=-1, G=-1)

    def cc(P, r, Q, s, sg):
        dx, dy = Q[0] - P[0], Q[1] - P[1]
        d = math.hypot(dx, dy)
        al = (r * r - s * s + d * d) / (2 * d)
        h = r * math.sqrt(max(1 - (al / r) ** 2, 0))
        return (P[0] + (al * dx - sg * h * dy) / d, P[1] + (al * dy + sg * h * dx) / d)

    P = {"O": (0.0, 0.0), "B": (-L["a"], -L["l"]), "A": (L["m"] * math.cos(th), L["m"] * math.sin(th))}
    for j, p1, r1, p2, r2 in (("C", "A", "j", "B", "b"), ("D", "B", "d", "C", "e"), ("E", "A", "k", "B", "c"),
                              ("F", "D", "f", "E", "g"), ("G", "F", "h", "E", "i")):
        P[j] = cc(P[p1], L[r1], P[p2], L[r2], branch[j])
    return P


def check(jig):
    spec_path = os.path.join(ROOT, "jigs", jig, "assembly", "check.json")
    with open(spec_path) as f:
        specs = json.load(f)
    if isinstance(specs, dict):
        specs = [specs]
    failures = []
    for spec in specs:
        failures += check_one(jig, spec)
    return failures


CHUNK = 17   # samples of one motion.check process: its memory grows with the samples it measures


def run_cmds(asm, cmds):
    args = ["run", asm]
    for c, p in cmds:
        args += ["--cmd", c, "--params", json.dumps(p)]
    return run(args, "%s: %s" % (asm, ", ".join(c for c, _ in cmds)))


def motion_check(asm, t, samples):
    """motion.check over t at samples moments, in processes of at most CHUNK samples each (each moment
    the same as one run would measure: a moment is a function of t alone). Returns the merged result:
    per assertion its worst status, the samples that failed, the first failure, min and max."""
    t0, t1 = t
    if samples < 2:
        raise SystemExit("%s: a motion check needs 2 samples or more" % asm)
    dt = (t1 - t0) / (samples - 1)
    merged, dead, at = {}, [], 0
    # inactive at some samples and passed at the others is passed; any failure outranks the rest
    rank = ["inactive", "passed", "notProven", "error", "failed"]
    while at < samples - 1:
        last = min(at + CHUNK - 1, samples - 1)
        n = last - at + 1
        r = run_cmds(asm, [("motion.check", {"t": [t0 + at * dt, t0 + last * dt], "samples": n})])[0]
        dead += r.get("deadPoints") or []
        for a in r.get("assertions", []):
            m = merged.setdefault(a["name"], {"name": a["name"], "status": "inactive", "failed": 0, "first": {},
                                               "min": None, "max": None, "unit": a.get("unit")})
            if rank.index(a["status"]) > rank.index(m["status"]):
                m["status"] = a["status"]
            m["failed"] += a.get("failed", 0)     # a sample on a chunk boundary is measured twice
            for key in ("firstFailure", "firstError", "firstNotProven"):
                if a.get(key) and key not in m["first"]:
                    m["first"][key] = a[key]
            for key, pick in (("min", min), ("max", max)):
                if a.get(key):
                    m[key] = a[key] if m[key] is None else (a[key] if pick(a[key]["value"], m[key]["value"]) == a[key]["value"] else m[key])
        at = last if last > at else samples
    for m in merged.values():
        f = m["first"]
        m["first"] = f.get("firstFailure") or f.get("firstError") or f.get("firstNotProven")
    return list(merged.values()), dead


def check_one(jig, spec):
    asm = spec["file"]
    name = os.path.splitext(os.path.basename(asm))[0]
    ev = os.path.join(EVIDENCE, name)
    os.makedirs(os.path.join(ROOT, ev), exist_ok=True)
    failures = []
    solve, inspect = run_cmds(asm, [("assembly.solve", {}), ("assembly.inspect", {})])
    rest = spec.get("at_rest", {})
    if not solve.get("ok"):
        failures.append("%s: assembly.solve is not ok: %s" % (name, solve.get("error") or solve.get("failed")))
    if "dof" in rest and solve.get("dof") != rest["dof"]:
        failures.append("%s: %s degrees of freedom left, expected %d" % (name, solve.get("dof"), rest["dof"]))
    print("%s: solved, %s degrees of freedom left" % (name, solve.get("dof")))
    poses = {i["name"]: i["pose"] for i in inspect.get("instances", [])}
    worst = 0.0
    ident = {"origin": [0, 0, 0], "x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}
    for inst in rest.get("identity", []):
        p = poses.get(inst)
        if p is None:
            failures.append("%s: no instance %s" % (name, inst))
            continue
        for key, want in ident.items():
            worst = max(worst, max(abs(a - b) for a, b in zip(p[key], want)))
    if rest.get("identity"):
        print("%s: %d instances where their source puts them (worst %.2g)" % (name, len(rest["identity"]), worst))
        if worst > 1e-9:
            failures.append("%s: an instance is not where its source puts it (%.3g off)" % (name, worst))
    for m in spec.get("motion", []):
        assertions, dead = motion_check(asm, m["t"], m["samples"])
        print("%s: motion.check t in [%g, %g] at %d samples (sampled)%s" % (
            name, m["t"][0], m["t"][1], m["samples"], ", dead points %s" % dead if dead else ""))
        for a in assertions:
            rng = ""
            if a.get("min") and a.get("max"):
                rng = " (%.6g to %.6g %s)" % (a["min"]["value"], a["max"]["value"], a.get("unit") or "")
            print("    %-9s %s%s" % (a["status"], a["name"], rng))
            if a["status"] == "notProven":
                # As check-range counts it: a warning, never a pass; the value found is printed.
                print("              not proven: %s" % (a["first"] or {}).get("message"))
            elif a["status"] != "passed":
                failures.append("%s: %s is %s over t in %s: %s" % (name, a["name"], a["status"], m["t"], a["first"]))
        if dead:
            failures.append("%s: dead points %s" % (name, dead))
    traces = {}
    if spec.get("traces"):
        cmds = []
        for tr in spec["traces"]:
            cmds.append(("view.trace", {"point": tr["point"], "name": tr["name"], "samples": tr.get("samples", 65)}))
            if tr.get("svg"):
                cmds.append(("file.export", {"path": "%s/%s.svg" % (ev, tr["name"].replace(" ", "-").lower()), "trace": tr["name"]}))
        out = run_cmds(asm, cmds)
        k = 0
        for tr in spec["traces"]:
            r = out[k]
            k += 2 if tr.get("svg") else 1
            traces[tr["name"]] = r.get("points", [])
            print("%s: trace %s: %d points, length %.3f, closed %s" % (name, tr["name"], len(r.get("points", [])),
                                                                      r.get("length", 0), r.get("closed")))
    if "willis" in spec:
        w = spec["willis"]
        sun = unwrap([math.atan2(p[1], p[0]) for p in traces[w["sun"]]])
        car = unwrap([math.atan2(p[1], p[0]) for p in traces[w["carrier"]]])
        worst = 0.0
        for i in range(1, len(sun)):
            worst = max(worst, abs(math.degrees((sun[i] - sun[0]) - w["ratio"] * (car[i] - car[0]))))
        print("%s: Willis from the traces: sun / carrier = %.9f at t = 1 (closed form %.9g), worst miss %.3g deg" % (
            name, (sun[-1] - sun[0]) / (car[-1] - car[0]), w["ratio"], worst))
        if worst > w["tol_deg"]:
            failures.append("%s: the sun's turn over the carrier's misses %g by %.3g deg" % (name, w["ratio"], worst))
    feet = spec.get("foot", [])
    for f in feet if isinstance(feet, list) else [feet]:
        pts = traces[f["trace"]]
        o = f.get("origin", [0, 0, 0])
        worst = 0.0
        for i, p in enumerate(pts):
            t = i / (len(pts) - 1)
            G = leg(math.radians(f["crank0_deg"] + f["turn_deg"] * t))["G"]
            worst = max(worst, math.hypot(p[0] - o[0] - G[0], p[2] - o[2] - G[1]))
        print("%s: %s against the closed form at crank %g deg + %g deg t, %d samples: worst miss %.3g mm" % (
            name, f["trace"], f["crank0_deg"], f["turn_deg"], len(pts), worst))
        if worst > f["tol"]:
            failures.append("%s: %s misses the closed form by %.3g mm" % (name, f["trace"], worst))
    view = spec.get("view", "iso")
    if spec.get("renders"):
        cmds = []
        for t in spec["renders"]:
            cmds.append(("view.motion", {"t": t}))
            cmds.append(("view.render", {"path": "%s/t-%.3f.png" % (ev, t), "width": 960, "height": 720, "view": view}))
        run_cmds(asm, cmds)
        print("%s: renders at t = %s in %s" % (name, spec["renders"], ev))
    if spec.get("replay"):
        gif = "%s/%s.gif" % (ev, name)
        run(["replay", asm, "--out", gif, "--size", "640x480", "--view", view, "--fps", "24",
             "--params", json.dumps({"motion": {"frames": spec["replay"]["frames"]}})], gif)
        print("%s: the motion as %s" % (name, gif))
    return failures


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("build", "check", "all"):
        sys.exit(__doc__)
    what, ids = sys.argv[1], ids_with_assemblies(sys.argv[2:])
    failures = []
    for jig in ids:
        if what in ("build", "all"):
            build(jig)
        if what in ("check", "all"):
            failures += check(jig)
    for f in failures:
        print("FAIL " + f)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
