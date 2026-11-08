#!/usr/bin/env python3
"""Build, render and check the 3DCraft Jigs (AGENTS.md).

  tools/jigs.py build    [ID ...]   jigs/ID/build.json -> dist/ID.3dcraftjig; document.check; stats into meta.json
  tools/jigs.py render   [ID ...]   dist/ID.3dcraftjig -> jigs/ID/preview.png and dist/thumbs/ID.png
  tools/jigs.py check    [ID ...]   rebuild in a scratch folder and check what AGENTS.md asks
                                    (--quick skips check-range and the bend sequence)
  tools/jigs.py coverage            the 3DCraft commands the Jigs use, and those none uses
  tools/jigs.py readme              rewrite the table in README.md from the meta.json files
  tools/jigs.py gallery             write dist/index.html

Without an ID: every Jig under jigs/. Every craft3d-cli run is capped in memory (systemd-run, when
there is one) and in time. CRAFT3D_CLI names the binary (default: craft3d-cli on PATH); it must be
the 3DCraft commit pinned in tools/pin.json. Exit code 0 when all passed.
"""

import argparse
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JIGS = ROOT / "jigs"
DIST = ROOT / "dist"
PIN = json.loads((ROOT / "tools" / "pin.json").read_text())

# The gallery look (AGENTS.md, The preview). meta.json "preview" may change only the framing keys below.
RENDER = {"width": 1600, "height": 1200, "view": "iso", "projection": "perspective", "zoom": 1,
          "renderer": "cpu"}
THUMB = {"width": 640, "height": 480}
LOOK = {"mode": "studio", "environment": "workshop", "tonemap": "aces", "exposure": 0.5,
        "background": "plain", "accumulate": 8}
PREVIEW_KEYS = {"view", "zoom", "camera", "projection", "box"}
PREVIEW_LOOK_KEYS = {"light", "rotation", "reflections"}

TIERS = ("simple", "difficult", "complex")
BUDGET_LOAD_S = {"simple": 1.0, "difficult": 2.0, "complex": 4.0}
WORST_POINT_FACTOR = 3  # the slowest point of the range may take this many times the load budget
BUDGET_BYTES = 1_000_000
STEP_GUIDE = {"simple": 100, "difficult": 250, "complex": 600}
PARAMETERS_MIN, PARAMETERS_MAX = 3, 12
ASSERTIONS_MIN = 3
RANGE_SAMPLES, RANGE_MAX_CORNERS = 32, 64
REQUIRED_META = ("id", "title", "summary", "description", "domain", "process", "tier",
                 "difficulty", "standards", "materials", "licence", "exports")
REQUIRED_FILES = ("build.json", "meta.json", "README.md", "formtest.md", "preview.png")
# Never in a build.json: assemblies are out of scope; the tool opens, saves and publishes.
FORBIDDEN = ("assembly.", "instance.", "mate.", "joint.", "coupling.", "motion.", "jig.", "file.",
             "view.", "edit.", "history.", "select.", "param.", "session.", "agent.", "recovery.")
NOT_IN_SCOPE = FORBIDDEN + ("measure.joint", "measure.pose", "font.")
NOT_MODELLING = ("variable.delete", "variable.rename", "variable.unpublish", "feature.edit",
                 "feature.suppress", "feature.move", "feature.delete", "feature.rename",
                 "document.inspect", "document.measure", "document.edges", "document.sample",
                 "document.setTolerance", "sketch.edit", "sketch.delete", "sketch.inspect",
                 "sketch.textEdit", "material.presets", "datum.references", "fold.edit", "fold.inspect",
                 "assert.edit", "assert.delete", "assert.list", "output.list", "set.edit", "set.remove",
                 "set.list", "table.delete", "table.rename", "table.list")
EXPORT_COMMANDS = ("file.export", "cut.export", "cut.list")
DEFAULT_NAME = re.compile(r"^[A-Za-z]+[0-9]+$")
VARIABLE_NAME = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
TABLE_START = "<!-- jigs:start -->"
TABLE_END = "<!-- jigs:end -->"

_cli = None
_measured_at_load = 0.0  # the 1-minute load average when the last load time was measured


class CheckError(Exception):
    pass


def die(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def cli():
    """The craft3d-cli binary, checked once against the pinned commit."""
    global _cli
    if _cli is None:
        path = os.environ.get("CRAFT3D_CLI") or shutil.which("craft3d-cli")
        if not path or not os.access(path, os.X_OK):
            die("craft3d-cli not found: put it on PATH or set CRAFT3D_CLI")
        # The binary carries the commit it was built from, but may not print it.
        if PIN["commit"][:12].encode() not in Path(path).read_bytes():
            die(f"{path} is not 3DCraft {PIN['commit'][:12]} (tools/pin.json): install that build "
                "or ask the coordinator to move the pin")
        _cli = path
    return _cli


def run_cli(args, cwd, memory="3G", timeout=900):
    """Runs craft3d-cli under a memory cap and a timeout; returns (result, seconds)."""
    command = [cli()] + [str(a) for a in args]
    if shutil.which("systemd-run") and not os.environ.get("CRAFT3D_NO_CAP"):
        # CRAFT3D_SLICE names a shared slice that caps parallel agents together (AGENTS.md section 3).
        shared = [f"--slice={os.environ['CRAFT3D_SLICE']}"] if os.environ.get("CRAFT3D_SLICE") else []
        command = ["systemd-run", "--user", "--scope", "-q", *shared, "-p", f"MemoryMax={memory}",
                   "-p", "MemorySwapMax=0", "timeout", str(timeout)] + command
    elif shutil.which("timeout"):
        command = ["timeout", str(timeout)] + command
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    # CPU time of the run (all threads): what a single-threaded host such as the web build pays.
    result.cpu_seconds = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    return result, time.monotonic() - start


def explain_failure(result, what):
    code = result.returncode
    reason = {137: "killed at the memory cap", 124: "timed out"}.get(code, f"exit code {code}")
    tail = "\n".join((result.stdout.strip().splitlines() + result.stderr.strip().splitlines())[-8:])
    return f"{what}: {reason}\n{tail}"


def jig_ids(given):
    every = sorted(p.parent.name for p in JIGS.glob("*/build.json"))
    for name in given:
        if name not in every:
            die(f"no Jig {name} (jigs/{name}/build.json)")
    return list(given) or every


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise CheckError(f"{path.relative_to(ROOT)}: {e}")


def write_meta(jig, meta):
    (JIGS / jig / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


def step_id(step):
    if isinstance(step, list) and step:
        return step[0]
    if isinstance(step, dict):
        return step.get("command", "?")
    return "?"


def step_params(step):
    if isinstance(step, list) and len(step) > 1:
        return step[1]
    if isinstance(step, dict):
        return step.get("params", {})
    return {}


def manifest_bytes(path):
    with zipfile.ZipFile(path) as z:
        return z.read("manifest.json")


def build_into(jig, scratch, meta):
    """Builds jigs/jig/build.json into scratch/jig.3dcraftjig. Returns (stats, document manifest, report)."""
    global _measured_at_load
    source = JIGS / jig
    script = read_json(source / "build.json")
    if not isinstance(script, list) or not script:
        raise CheckError("build.json must be a non-empty JSON list of steps")
    if step_id(script[-1]) != "document.check":
        raise CheckError("build.json must end with document.check")
    bad = sorted({step_id(s) for s in script if str(step_id(s)).startswith(FORBIDDEN)})
    if bad:
        raise CheckError(f"build.json may not use {', '.join(bad)} (AGENTS.md section 2)")
    building = scratch / f".{jig}.building.3dcraft"
    new = json.dumps(meta.get("new", {"units": "mm"}))
    result, seconds = run_cli(["run", "--new", new, "--script", source / "build.json", "--out", building],
                              cwd=scratch)
    if result.returncode != 0:
        raise CheckError(explain_failure(result, "build.json failed"))
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    try:
        report = json.loads(lines[-1])
    except (IndexError, ValueError):
        raise CheckError("no document.check result in the output")
    if not report.get("ok"):
        raise CheckError("document.check is not ok:\n" + json.dumps(
            {k: report.get(k) for k in ("problems", "assertions")}, indent=1)[:3000])
    final = scratch / f"{jig}.3dcraftjig"
    published, _ = run_cli(["run", building, "--cmd", "jig.export", "--params",
                            json.dumps({"path": final.name})], cwd=scratch)
    if published.returncode != 0 or not final.is_file():
        raise CheckError(explain_failure(published, "jig.export failed"))
    # The least of two openings: other work on the machine only ever adds time.
    load_s = load_cpu_s = None
    for _ in range(2):
        result, spent = run_cli(["info", final], cwd=scratch)
        if result.returncode != 0:
            raise CheckError(explain_failure(result, "craft3d-cli info failed"))
        load_s = spent if load_s is None else min(load_s, spent)
        load_cpu_s = result.cpu_seconds if load_cpu_s is None else min(load_cpu_s, result.cpu_seconds)
    _measured_at_load = os.getloadavg()[0]
    doc = json.loads(manifest_bytes(final))
    ids = Counter(step_id(s) for s in script)
    assertions = report.get("assertions", {})
    return {
        "steps": len(script),
        "variables": ids["variable.set"],
        "parameters": ids["variable.publish"],
        "features": len(doc.get("document", {}).get("features", [])),
        "assertions": assertions.get("count", ids["assert.add"]),
        "warnings": len(assertions.get("unproven", [])),
        "build_s": round(seconds, 2),
        "load_s": round(load_s, 2),
        "load_cpu_s": round(load_cpu_s, 2),
        "file_bytes": final.stat().st_size,
    }, doc, report


def lint_parameters(body, errors, warnings):
    public = [v for v in body.get("variables", []) if v.get("public")]
    if not public:
        errors.append("no public parameters")
    elif not PARAMETERS_MIN <= len(public) <= PARAMETERS_MAX:
        warnings.append(f"{len(public)} public parameters (AGENTS.md asks {PARAMETERS_MIN} to {PARAMETERS_MAX})")
    for variable in public:
        name, form = variable.get("name"), variable["public"]
        for key in ("label", "description", "group"):
            if not form.get(key):
                errors.append(f"parameter {name}: no {key}")
        kind = form.get("kind", "number")
        if kind in ("number", "integer") and not (form.get("min") and form.get("max") and form.get("step")):
            errors.append(f"parameter {name}: a {kind} needs min, max and step")
        if kind == "choice" and not (form.get("choices") or form.get("choices_from")):
            errors.append(f"parameter {name}: a choice needs choices or choicesFrom")


def lint(jig, meta, doc, stats, script):
    """Returns (errors, warnings) for names, budgets, the form and the meta.json fields."""
    errors, warnings = [], []
    for key in REQUIRED_META:
        if key not in meta or meta[key] in ("", None):
            errors.append(f"meta.json: missing {key}")
    if meta.get("id") != jig:
        errors.append(f"meta.json: id is {meta.get('id')!r}, not {jig!r}")
    tier = meta.get("tier")
    if tier not in TIERS:
        errors.append(f"meta.json: tier must be one of {', '.join(TIERS)}")
        tier = "complex"
    if not meta.get("exports"):
        errors.append("meta.json: exports must name what a maker sends to the machine")
    for key in meta.get("preview", {}):
        if key == "look":
            if set(meta["preview"]["look"]) - PREVIEW_LOOK_KEYS:
                errors.append(f"meta.json: preview.look may only set {sorted(PREVIEW_LOOK_KEYS)}")
        elif key not in PREVIEW_KEYS:
            errors.append(f"meta.json: preview may only set {sorted(PREVIEW_KEYS)} and look")
    body = doc.get("document", {})
    tools = {f.get("kind", {}).get("tool") for f in body.get("features", [])
             if f.get("kind", {}).get("type") == "boolean"}
    for feature in body.get("features", []):
        name = feature.get("name", "")
        if DEFAULT_NAME.match(name):
            if feature.get("id") in tools:
                warnings.append(f"feature {name!r} keeps its automatic name (the tool of a boolean)")
            else:
                errors.append(f"feature {name!r} has an automatic name: name it for its intent")
    for assertion in body.get("assertions", []):
        if DEFAULT_NAME.match(assertion.get("name", "")):
            errors.append(f"assertion {assertion.get('name')!r} has an automatic name")
    for variable in body.get("variables", []):
        name = variable.get("name", "")
        if not VARIABLE_NAME.match(name) or len(name) < 3:
            errors.append(f"variable {name!r}: use a descriptive snake_case name of 3+ letters")
    info = body.get("info") or {}
    for key in ("title", "description", "author", "licence"):
        if not info.get(key):
            errors.append(f"document.info: no {key}")
    if info.get("licence") and info.get("licence") != meta.get("licence"):
        errors.append(f"document.info licence {info.get('licence')} is not meta.json's {meta.get('licence')}")
    if "export" not in (info.get("description") or "").lower():
        errors.append("document.info: the description must say how to export the result")
    lint_parameters(body, errors, warnings)
    if stats["assertions"] < ASSERTIONS_MIN:
        errors.append(f"{stats['assertions']} assertions, at least {ASSERTIONS_MIN} (AGENTS.md section 4.7)")
    # Timings taken while the machine is busy (load average over half its CPUs) only warn.
    busy = _measured_at_load > (os.cpu_count() or 1) / 2
    timing = warnings if busy else errors
    busy_note = (f" (measured at load average {_measured_at_load:.1f} on {os.cpu_count()} CPUs: "
                 "re-measure at a quiet moment)") if busy else ""
    excepted = bool(meta.get("budget_exception"))
    if stats["load_s"] > BUDGET_LOAD_S[tier] and not excepted:
        timing.append(f"loads in {stats['load_s']} s, budget {BUDGET_LOAD_S[tier]} s for {tier}{busy_note}")
    cpu_budget = 3 * BUDGET_LOAD_S[tier]
    if stats["load_cpu_s"] > cpu_budget and not excepted:
        timing.append(f"loads in {stats['load_cpu_s']} s of CPU (the web build's time), "
                      f"budget {cpu_budget} s for {tier}{busy_note}")
    if stats["file_bytes"] > BUDGET_BYTES and not excepted:
        errors.append(f"{stats['file_bytes']} bytes, budget {BUDGET_BYTES}")
    modelling = stats["steps"] - stats["variables"] - stats["parameters"]
    if modelling > STEP_GUIDE[tier]:
        warnings.append(f"{modelling} steps besides variables and parameters, guide {STEP_GUIDE[tier]} for {tier}")
    if stats["warnings"]:
        warnings.append(f"{stats['warnings']} assertion(s) not proven: explain in the README")
    return errors, warnings


def prove_exports(jig, scratch, meta):
    """Runs meta.json's exports on the built Jig; an export with values gets a run of its own."""
    exports = meta.get("exports", [])
    final = f"{jig}.3dcraftjig"
    plain = ["run", final]
    runs = []
    for export in exports:
        params = {k: v for k, v in export.items() if k not in ("command", "values")}
        command = export.get("command", "file.export")
        if command not in EXPORT_COMMANDS:
            raise CheckError(f"export command {command!r} must be one of {EXPORT_COMMANDS}")
        path = params.get("path", "")
        if command != "cut.list":  # a cut list is answered, not written
            if not path.startswith("exports/"):
                raise CheckError(f"export path {path!r} must start with exports/")
            (scratch / path).parent.mkdir(parents=True, exist_ok=True)
        step = ["--cmd", command, "--params", json.dumps(params)]
        if export.get("values"):
            runs.append(["run", final, "--cmd", "param.set",
                         "--params", json.dumps({"values": export["values"]})] + step)
        else:
            plain += step
    if len(plain) > 2:
        runs.insert(0, plain)
    for args in runs:
        result, _ = run_cli(args, cwd=scratch)
        if result.returncode != 0:
            raise CheckError(explain_failure(result, "exports failed"))
    for export in exports:
        if export.get("command") == "cut.list":
            continue
        path = scratch / export.get("path", "")
        if not path.is_file() or path.stat().st_size == 0:
            raise CheckError(f"export {export.get('path')} was not written")


def cmd_build(ids):
    failed = 0
    DIST.mkdir(exist_ok=True)
    for jig in ids:
        try:
            meta = read_json(JIGS / jig / "meta.json")
            with tempfile.TemporaryDirectory(prefix=f"build-{jig}-") as scratch:
                scratch = Path(scratch)
                stats, doc, _ = build_into(jig, scratch, meta)
                errors, warnings = lint(jig, meta, doc, stats, read_json(JIGS / jig / "build.json"))
                shutil.copyfile(scratch / f"{jig}.3dcraftjig", DIST / f"{jig}.3dcraftjig")
            meta["stats"] = {**meta.get("stats", {}), **stats}
            meta["craft3d"] = {"commit": PIN["commit"][:12], "format_version": doc.get("format_version")}
            write_meta(jig, meta)
            for w in warnings:
                print(f"{jig}: warning: {w}")
            for e in errors:
                print(f"{jig}: ERROR: {e}")
            print(f"{jig}: built, {stats['steps']} steps, {stats['features']} features, "
                  f"{stats['parameters']} parameters, load {stats['load_s']} s, {stats['file_bytes']} bytes")
            failed += bool(errors)
        except CheckError as e:
            print(f"{jig}: FAILED: {e}")
            failed += 1
    return failed


def render_one(jig, meta, size, path):
    params = dict(RENDER, **size)
    look = dict(LOOK)
    for key, value in meta.get("preview", {}).items():
        if key == "look":
            look.update({k: v for k, v in value.items() if k in PREVIEW_LOOK_KEYS})
        elif key in PREVIEW_KEYS:
            params[key] = value
    if "camera" in params:
        # A camera is the whole framing: view, zoom and projection would contradict it.
        for key in ("view", "zoom", "projection", "box"):
            params.pop(key, None)
    params["look"] = look
    params["path"] = str(path)
    result, seconds = run_cli(["run", DIST / f"{jig}.3dcraftjig", "--cmd", "view.render", "--params",
                               json.dumps(params)], cwd=JIGS / jig, memory="4G", timeout=1800)
    if result.returncode != 0:
        raise CheckError(explain_failure(result, "view.render failed"))
    return seconds


def cmd_render(ids):
    failed = 0
    (DIST / "thumbs").mkdir(parents=True, exist_ok=True)
    for jig in ids:
        try:
            meta = read_json(JIGS / jig / "meta.json")
            if not (DIST / f"{jig}.3dcraftjig").is_file():
                raise CheckError(f"no dist/{jig}.3dcraftjig: run build first")
            seconds = render_one(jig, meta, {}, JIGS / jig / "preview.png")
            seconds += render_one(jig, meta, THUMB, DIST / "thumbs" / f"{jig}.png")
            print(f"{jig}: preview.png and thumbnail, {seconds:.0f} s")
        except CheckError as e:
            print(f"{jig}: FAILED: {e}")
            failed += 1
    return failed


def prove_range(jig, rebuilt, scratch):
    """check-range at the fixed seed. Returns (problems, notes, range stats)."""
    report_path = scratch / "range.json"
    result, seconds = run_cli(["check-range", rebuilt, "--samples", RANGE_SAMPLES, "--seed", 1,
                               "--max-corners", RANGE_MAX_CORNERS, "--json"],
                              cwd=scratch, memory="4G", timeout=3600)
    report_path.write_text(result.stdout)
    if result.returncode not in (0, 1):
        return [explain_failure(result, "check-range did not finish")], [], {}
    report = json.loads(result.stdout)
    times = [(p.get("ms") or 0) / 1000 for p in report.get("points", [])]  # a point that cannot be set has ms null
    stats = {"range_points": len(times), "range_unproven": report.get("unproven", 0),
             "range_mean_s": round(sum(times) / max(1, len(times)), 2), "range_worst_s": round(max(times or [0]), 2)}
    if not report.get("ok"):
        worst = json.dumps(report.get("failures", [])[:3], indent=1)[:2500]
        return [f"check-range: {report.get('failed')} of {len(times)} points failed\n{worst}"], [], stats
    notes = [f"check-range passed: {len(times)} points in {seconds:.0f} s, slowest {stats['range_worst_s']} s, "
             f"{stats['range_unproven']} with unproven assertions"]
    return [], notes, stats


def cmd_check(ids, quick):
    failed = 0
    for jig in ids:
        directory = JIGS / jig
        problems, notes = [], []
        try:
            for name in REQUIRED_FILES:
                if not (directory / name).is_file():
                    problems.append(f"missing {name}")
            meta = read_json(directory / "meta.json")
            script = read_json(directory / "build.json")
            committed = DIST / f"{jig}.3dcraftjig"
            with tempfile.TemporaryDirectory(prefix=f"check-{jig}-") as scratch:
                scratch = Path(scratch)
                stats, doc, _ = build_into(jig, scratch, meta)
                errors, warnings = lint(jig, meta, doc, stats, script)
                problems += errors
                notes += warnings
                rebuilt = scratch / f"{jig}.3dcraftjig"
                if not committed.is_file():
                    problems.append(f"missing dist/{jig}.3dcraftjig: run build")
                elif manifest_bytes(committed) != manifest_bytes(rebuilt):
                    problems.append(f"dist/{jig}.3dcraftjig is stale: run build")
                if not (DIST / "thumbs" / f"{jig}.png").is_file():
                    problems.append(f"missing dist/thumbs/{jig}.png: run render")
                prove_exports(jig, scratch, meta)
                if not quick:
                    found, said, range_stats = prove_range(jig, rebuilt, scratch)
                    problems += found
                    notes += said
                    if range_stats:
                        tier = meta.get("tier") if meta.get("tier") in TIERS else "complex"
                        budget = WORST_POINT_FACTOR * BUDGET_LOAD_S[tier]
                        if range_stats["range_worst_s"] > budget and not meta.get("budget_exception"):
                            problems.append(f"slowest point of the range takes {range_stats['range_worst_s']} s, "
                                            f"budget {budget} s for {tier}")
                        if range_stats != meta.get("stats", {}) and range_stats:
                            meta.setdefault("stats", {}).update(range_stats)
                            write_meta(jig, meta)
                    if (directory / "press.json").is_file():
                        env = dict(os.environ, CRAFT3D_CLI=cli())
                        bend = subprocess.run([sys.executable, str(ROOT / "tools" / "bendcheck.py"), jig],
                                              cwd=ROOT, capture_output=True, text=True, env=env)
                        if bend.returncode != 0:
                            problems.append("bendcheck failed:\n" + "\n".join(bend.stdout.splitlines()[-8:]))
                        else:
                            notes.append("bend sequence proven")
            if (meta.get("difficulty") or {}).get("score") is None:
                notes.append("no difficulty score yet (the reviewer gives it)")
            if not (meta.get("form_test") or {}).get("result"):
                notes.append("form not tested yet")
        except CheckError as e:
            problems.append(str(e))
        for n in notes:
            print(f"{jig}: note: {n}")
        for p in problems:
            print(f"{jig}: PROBLEM: {p}")
        print(f"{jig}: {'FAILED' if problems else 'ok'}")
        failed += bool(problems)
    return failed


def measure_command(measure):
    """The measure.* command an assertion's or output's measure kind stands for."""
    for prefix, command in (("floating", "measure.floating"), ("section", "measure.section"),
                            ("volumeBelow", "measure.below"), ("centroidBelow", "measure.below"),
                            ("symmetric", "measure.symmetry")):
        if measure.startswith(prefix):
            return command
    return f"measure.{measure}"


def cmd_coverage():
    result, _ = run_cli(["commands"], cwd=ROOT)
    if result.returncode != 0:
        die(explain_failure(result, "craft3d-cli commands failed"))
    every = [line.strip() for line in result.stdout.splitlines()
             if line and not line[0].isspace() and re.match(r"^[a-z]+(\.[a-zA-Z]+)+$", line.strip())]
    relevant = [c for c in every if not c.startswith(NOT_IN_SCOPE) and c not in NOT_MODELLING]
    used, users = Counter(), {}
    for jig in jig_ids([]):
        script = read_json(JIGS / jig / "build.json")
        meta = read_json(JIGS / jig / "meta.json")
        ids = {step_id(s) for s in script}
        ids |= {e.get("command", "file.export") for e in meta.get("exports", [])}
        ids |= {measure_command(step_params(s).get("measure")) for s in script
                if step_id(s) in ("assert.add", "variable.measure")
                and isinstance(step_params(s), dict) and step_params(s).get("measure")}
        for c in ids:
            used[c] += 1
            users.setdefault(c, []).append(jig)
    print(f"{len([c for c in relevant if used[c]])} of {len(relevant)} commands in scope used")
    for c in relevant:
        mark = f"{used[c]:2d}  {', '.join(users.get(c, [])[:4])}" if used[c] else " -  UNUSED"
        print(f"  {c:32s} {mark}")
    return 0


def cmd_readme():
    rows = []
    for jig in jig_ids([]):
        try:
            meta = read_json(JIGS / jig / "meta.json")
        except CheckError:
            continue
        score = (meta.get("difficulty") or {}).get("score")
        if score is not None:  # the table shows reviewed Jigs only
            rows.append((TIERS.index(meta.get("tier", "complex")), score, jig, meta))
    rows.sort(key=lambda r: r[:3])
    lines = ["| | Jig | Workshop | Difficulty | Licence |", "|---|---|---|---|---|"]
    for _, score, jig, meta in rows:
        title = meta.get("title", jig)
        picture = f'<img src="dist/thumbs/{jig}.png" width="240" alt="{title}">'
        lines.append(f"| {picture} | **[{title}](jigs/{jig}/)**<br>{meta.get('description', '')}"
                     f" | {meta.get('domain', '')} | {score}/10 | {meta.get('licence', '')} |")
    readme = ROOT / "README.md"
    text = readme.read_text()
    if TABLE_START not in text or TABLE_END not in text:
        die("README.md lacks the table markers")
    head, rest = text.split(TABLE_START, 1)
    _, tail = rest.split(TABLE_END, 1)
    readme.write_text(head + TABLE_START + "\n" + "\n".join(lines) + "\n" + TABLE_END + tail)
    print(f"README.md: {len(rows)} Jigs")
    return 0


def cmd_gallery():
    return subprocess.run([sys.executable, str(ROOT / "tools" / "gallery.py"), str(DIST)]).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("build", "render", "check", "coverage", "readme", "gallery"))
    parser.add_argument("ids", nargs="*")
    parser.add_argument("--quick", action="store_true", help="check: skip check-range and the bend sequence")
    args = parser.parse_args()
    if args.action == "build":
        failed = cmd_build(jig_ids(args.ids))
    elif args.action == "render":
        failed = cmd_render(jig_ids(args.ids))
    elif args.action == "check":
        failed = cmd_check(jig_ids(args.ids), args.quick)
    elif args.action == "coverage":
        failed = cmd_coverage()
    elif args.action == "readme":
        failed = cmd_readme()
    else:
        failed = cmd_gallery()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
