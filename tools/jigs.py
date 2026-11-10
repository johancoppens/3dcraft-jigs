#!/usr/bin/env python3
"""Build, render and check the 3DCraft Jigs (AGENTS.md).

  tools/jigs.py build    [ID ...]   jigs/NN-ID/build.json -> jigs/NN-ID/ID.3dcraftjig; document.check; stats
                                    into meta.json
  tools/jigs.py render   [ID ...]   ID.3dcraftjig -> preview.png and thumb.png in jigs/NN-ID/
  tools/jigs.py check    [ID ...]   rebuild in a scratch folder and check what AGENTS.md asks
                                    (--quick skips check-range and the bend sequence)
  tools/jigs.py coverage            the 3DCraft commands the Jigs use, and those none uses
  tools/jigs.py readme              rewrite the table in README.md from the meta.json files
  tools/jigs.py site     [DIR]      write a local web folder of the Jigs (default site/, not committed):
                                    every ID.3dcraftjig, thumbs/ID.png and index.html, the gallery; the
                                    files of an earlier run whose Jig is gone are removed

A Jig lives in jigs/NN-ID/, NN its place in CATALOGUE.md; the ID never carries the number.
Without an ID: every Jig under jigs/. Every craft3d-cli run is capped in memory (systemd-run, when
there is one) and in time. CRAFT3D_CLI names the binary (default: craft3d-cli on PATH); by what its
--version reports, it must be the 3DCraft commit pinned in tools/pin.json, or the release named there,
with the pinned file format. Linux and macOS only. Exit code 0 when all passed.
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
SITE = ROOT / "site"
FOLDER = re.compile(r"^(\d\d)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
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
BENDCHECK_TIMEOUT_S = 7200  # tools/bendcheck.py over all its points; each of its craft3d-cli runs has its own timeout
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

# What `craft3d-cli --version` prints: the program, the version, the commit when the build knows it, the file format.
VERSION_LINE = re.compile(r"^craft3d-cli (?P<version>\S+) \((?:(?P<commit>[0-9A-Za-z]+), )?format (?P<format>[0-9]+)\)$")

_cli = None
_build = None  # (version, commit or None, format) of _cli
_measured_at_load = 0.0  # the 1-minute load average when the last load time was measured


class CheckError(Exception):
    pass


def die(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def capped(command, memory, timeout):
    """command under a memory cap (systemd-run, where there is one) and a timeout: every craft3d-cli run of the tools
    goes through here. CRAFT3D_NO_CAP=1 leaves the memory cap out; CRAFT3D_SLICE names a shared slice that caps
    parallel agents together (AGENTS.md section 3)."""
    command = [str(c) for c in command]
    if shutil.which("systemd-run") and not os.environ.get("CRAFT3D_NO_CAP"):
        shared = [f"--slice={os.environ['CRAFT3D_SLICE']}"] if os.environ.get("CRAFT3D_SLICE") else []
        return ["systemd-run", "--user", "--scope", "-q", *shared, "-p", f"MemoryMax={memory}",
                "-p", "MemorySwapMax=0", "timeout", str(timeout)] + command
    if shutil.which("timeout"):
        return ["timeout", str(timeout)] + command
    return command


def version_of(path):
    """What `craft3d-cli --version` prints, and what it says: (line, (version, commit or None, format) or None).
    The line is `craft3d-cli 0.1.0 (8c8383e9c89a, format 69)`; a build that does not know its commit leaves it out."""
    try:
        result = subprocess.run(capped([path, "--version"], "1G", 60), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return str(e), None
    lines = result.stdout.strip().splitlines()
    line = lines[-1].strip() if lines else (result.stderr.strip() or f"exit code {result.returncode}")
    match = VERSION_LINE.match(line)
    if result.returncode != 0 or not match:
        return line, None
    return line, (match["version"], match["commit"], int(match["format"]))


def pinned(build):
    """How a build meets tools/pin.json: "commit" when it is the pinned commit (the check the Jigs were built with),
    "release" when it reports itself as the pinned release, or None; either way with the pinned file format.
    `--version` marks nothing else that tells a release build from a development build of the same version."""
    version, commit, file_format = build
    if file_format != PIN["format_version"]:
        return None
    pin = PIN["commit"].lower()
    if commit and len(commit) >= 12 and (pin.startswith(commit.lower()) or commit.lower().startswith(pin)):
        return "commit"
    if PIN.get("release") and version == PIN["release"]:
        return "release"
    return None


def cli():
    """The craft3d-cli binary, checked once against tools/pin.json by what its --version reports."""
    global _cli, _build
    if _cli is None:
        path = os.environ.get("CRAFT3D_CLI") or shutil.which("craft3d-cli")
        if not path or not os.access(path, os.X_OK):
            die("craft3d-cli not found: put it on PATH or set CRAFT3D_CLI (README.md, Building and checking)")
        line, build = version_of(path)
        how = pinned(build) if build else None
        if how is None:
            release = f" or the release {PIN['release']}" if PIN.get("release") else ""
            die(f"{path} reports {line!r}, not 3DCraft {PIN['commit'][:12]}{release} with file format "
                f"{PIN['format_version']}, the build this repository is pinned to (tools/pin.json): the committed "
                "Jigs and their checks are what that build produces, and another build may write other bytes. "
                "Install that build (README.md, Building and checking); the committed .3dcraftjig files open "
                "without it")
        if how == "release":
            print(f"note: {line}: accepted as 3DCraft {PIN['release']}, the release in tools/pin.json, but it is "
                  f"not the pinned commit {PIN['commit'][:12]}: if its Jigs differ in bytes, check reports them "
                  "as stale", file=sys.stderr)
        _cli, _build = path, build
    return _cli


def built_with(file_format):
    """meta.json's `craft3d`: the build that wrote the files, as its --version reports it."""
    version, commit, _ = _build
    return {"commit": commit[:12] if commit else None, "version": version, "format_version": file_format}


def run_cli(args, cwd, memory="3G", timeout=900):
    """Runs craft3d-cli under a memory cap and a timeout; returns (result, seconds)."""
    command = capped([cli()] + list(args), memory, timeout)
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    # CPU time of the run (all threads): what a single-threaded host such as the web build pays.
    result.cpu_seconds = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    return result, time.monotonic() - start


def explain_failure(result, what):
    code = result.returncode
    # The cap's kill reaches the whole scope: systemd-run itself dies by SIGKILL (-9), or timeout reports it (137).
    reason = {137: "killed at the memory cap", -9: "killed at the memory cap", 124: "timed out"}.get(
        code, f"exit code {code}")
    tail = "\n".join((result.stdout.strip().splitlines() + result.stderr.strip().splitlines())[-8:])
    return f"{what}: {reason}\n{tail}"


def jig_ids(given):
    """The Jigs' ids, in the order of their folders' numbers."""
    every = [FOLDER.match(p.parent.name).group(2) for p in sorted(JIGS.glob("*/build.json"))
             if FOLDER.match(p.parent.name)]
    for name in given:
        if name not in every:
            die(f"no Jig {name} (jigs/NN-{name}/build.json)")
    return list(given) or every


def jig_dir(jig):
    """jigs/NN-<id>/: everything of one Jig."""
    found = [p for p in JIGS.iterdir() if FOLDER.match(p.name) and FOLDER.match(p.name).group(2) == jig]
    if len(found) != 1:
        die(f"no single folder jigs/NN-{jig}/")
    return found[0]


def jig_file(jig):
    return jig_dir(jig) / f"{jig}.3dcraftjig"


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise CheckError(f"{path.relative_to(ROOT)}: {e}")


def write_meta(jig, meta):
    (jig_dir(jig) / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


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
    source = jig_dir(jig)
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
    for jig in ids:
        try:
            meta = read_json(jig_dir(jig) / "meta.json")
            with tempfile.TemporaryDirectory(prefix=f"build-{jig}-") as scratch:
                scratch = Path(scratch)
                stats, doc, _ = build_into(jig, scratch, meta)
                errors, warnings = lint(jig, meta, doc, stats, read_json(jig_dir(jig) / "build.json"))
                shutil.copyfile(scratch / f"{jig}.3dcraftjig", jig_file(jig))
            meta["stats"] = {**meta.get("stats", {}), **stats}
            meta["craft3d"] = built_with(doc.get("format_version"))
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
    result, seconds = run_cli(["run", jig_file(jig), "--cmd", "view.render", "--params",
                               json.dumps(params)], cwd=jig_dir(jig), memory="4G", timeout=1800)
    if result.returncode != 0:
        raise CheckError(explain_failure(result, "view.render failed"))
    return seconds


def cmd_render(ids):
    failed = 0
    for jig in ids:
        try:
            meta = read_json(jig_dir(jig) / "meta.json")
            if not jig_file(jig).is_file():
                raise CheckError(f"no {jig}.3dcraftjig: run build first")
            seconds = render_one(jig, meta, {}, jig_dir(jig) / "preview.png")
            seconds += render_one(jig, meta, THUMB, jig_dir(jig) / "thumb.png")
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
        directory = jig_dir(jig)
        problems, notes = [], []
        try:
            for name in REQUIRED_FILES:
                if not (directory / name).is_file():
                    problems.append(f"missing {name}")
            meta = read_json(directory / "meta.json")
            script = read_json(directory / "build.json")
            committed = jig_file(jig)
            with tempfile.TemporaryDirectory(prefix=f"check-{jig}-") as scratch:
                scratch = Path(scratch)
                stats, doc, _ = build_into(jig, scratch, meta)
                errors, warnings = lint(jig, meta, doc, stats, script)
                problems += errors
                notes += warnings
                rebuilt = scratch / f"{jig}.3dcraftjig"
                if not committed.is_file():
                    problems.append(f"missing {jig}.3dcraftjig: run build")
                elif manifest_bytes(committed) != manifest_bytes(rebuilt):
                    problems.append(f"{jig}.3dcraftjig is stale: run build")
                if not (directory / "thumb.png").is_file():
                    problems.append("missing thumb.png: run render")
                prove_exports(jig, scratch, meta)
                if not quick:
                    found, said, range_stats = prove_range(jig, rebuilt, scratch)
                    problems += found
                    notes += said
                    if range_stats:
                        tier = meta.get("tier") if meta.get("tier") in TIERS else "complex"
                        budget = WORST_POINT_FACTOR * BUDGET_LOAD_S[tier]
                        if range_stats["range_worst_s"] > budget and not meta.get("budget_exception"):
                            # As for the load time: a busy machine only warns (AGENTS.md section 4.5).
                            busy = os.getloadavg()[0] > (os.cpu_count() or 1) / 2
                            (notes if busy else problems).append(
                                f"slowest point of the range takes {range_stats['range_worst_s']} s, budget {budget} s "
                                f"for {tier}" + (" (busy machine: re-measure at a quiet moment)" if busy else ""))
                        if range_stats != meta.get("stats", {}) and range_stats:
                            meta.setdefault("stats", {}).update(range_stats)
                            write_meta(jig, meta)
                    if (directory / "press.json").is_file():
                        # bendcheck runs craft3d-cli through run_cli (the same caps); the whole proof is bounded too.
                        env = dict(os.environ, CRAFT3D_CLI=cli())
                        try:
                            bend = subprocess.run([sys.executable, str(ROOT / "tools" / "bendcheck.py"), jig],
                                                  cwd=ROOT, capture_output=True, text=True, env=env,
                                                  timeout=BENDCHECK_TIMEOUT_S)
                        except subprocess.TimeoutExpired:
                            problems.append(f"bendcheck did not finish in {BENDCHECK_TIMEOUT_S} s")
                        else:
                            if bend.returncode != 0:
                                problems.append("bendcheck failed:\n" + "\n".join(
                                    (bend.stdout.splitlines() + bend.stderr.splitlines())[-8:]))
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
        script = read_json(jig_dir(jig) / "build.json")
        meta = read_json(jig_dir(jig) / "meta.json")
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
            meta = read_json(jig_dir(jig) / "meta.json")
        except CheckError:
            continue
        score = (meta.get("difficulty") or {}).get("score")
        if score is not None:  # the table shows reviewed Jigs only
            rows.append((jig_dir(jig).name, score, jig, meta))
    lines = ["| | Jig | Workshop | Difficulty | Licence |", "|---|---|---|---|---|"]
    for folder, score, jig, meta in rows:  # in the order of the folders' numbers
        title = meta.get("title", jig)
        picture = f'<img src="jigs/{folder}/thumb.png" width="240" alt="{title}">'
        lines.append(f"| {picture} | **[{folder[:2]}. {title}](jigs/{folder}/)**<br>{meta.get('description', '')}"
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


SITE_TITLE = "<title>3DCraft Jigs</title>"  # what tools/gallery.py writes into index.html


def stale_site_files(out, jigs):
    """The files of an earlier `site` run in out that are no longer Jigs: ID.3dcraftjig and thumbs/ID.png whose ID is
    not in jigs. Only in a folder this tool filled (its index.html is the gallery page): anything else is left alone."""
    try:
        if SITE_TITLE not in (out / "index.html").read_text(encoding="utf-8", errors="replace"):
            return []
    except OSError:
        return []
    keep = set(jigs)
    stale = [p for p in out.glob("*.3dcraftjig") if p.is_file() and p.stem not in keep]
    stale += [p for p in (out / "thumbs").glob("*.png") if p.is_file() and p.stem not in keep]
    return sorted(stale)


def cmd_site(out):
    """A flat web folder of the Jigs: ID.3dcraftjig, thumbs/ID.png, index.html (tools/gallery.py: its addresses).
    A Jig file or picture left by an earlier run whose Jig is gone (renamed or removed) is deleted, so the gallery
    shows only the Jigs there are; nothing else in the folder is touched."""
    out = Path(out) if out else SITE
    jigs = jig_ids([])
    for jig in jigs:
        if not jig_file(jig).is_file() or not (jig_dir(jig) / "thumb.png").is_file():
            die(f"{jig}: run build and render first")
    for path in stale_site_files(out, jigs):
        path.unlink()
        print(f"removed {path}: no longer a Jig", flush=True)
    (out / "thumbs").mkdir(parents=True, exist_ok=True)
    for jig in jigs:
        shutil.copyfile(jig_file(jig), out / f"{jig}.3dcraftjig")
        shutil.copyfile(jig_dir(jig) / "thumb.png", out / "thumbs" / f"{jig}.png")
    return subprocess.run([sys.executable, str(ROOT / "tools" / "gallery.py"), str(out)]).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("build", "render", "check", "coverage", "readme", "site"))
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
        if len(args.ids) > 1:
            die("site takes one folder")
        failed = cmd_site(args.ids[0] if args.ids else None)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
