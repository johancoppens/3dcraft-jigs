# AGENTS.md: guide for AI agents working on the 3DCraft Jigs

This repository holds **33 Jigs** for [3DCraft](https://github.com/johancoppens/3dcraft), the parametric CAD
modeller built for AI. A Jig is a design whose driving variables are published as parameters: someone opens it,
sets a form, and 3DCraft regenerates a new model and its manufacturing files. No AI and no code run. Together the
Jigs show what that can do, across laser cutting, woodwork, sheet metal, welding, 3D printing, mechanisms,
acoustics, astronomy, aeronautics and building. Each one must be **a real Jig: real, makeable, beautiful, light and
proven over its whole range**.

Read this file, then [`CATALOGUE.md`](CATALOGUE.md) (what each Jig must be), then the Jig you work on.

**No Jig is grandfathered.** A Jig that came from the old collection meets exactly the same bar as a new one. Its
old `build.json`, its old README and the fact that it once passed `check-range` count for nothing. Rethink it as a
new Jig that happens to have a head start: better form, better geometry, better look, more proof. A kept Jig that
cannot reach the bar is thrown away.

## 1. Ground rules

- **Language.** The developer writes in Dutch: answer in Dutch. Everything that lands in this
  repository is English: files, names inside the models, commit messages.
- **3DCraft is pinned.** Every Jig is built and checked with one 3DCraft commit, recorded in
  [`tools/pin.json`](tools/pin.json): the installed `craft3d-cli` (`~/.local/bin/craft3d-cli`). `tools/jigs.py`
  refuses any other build. Only the coordinator moves the pin, after rebuilding and checking every Jig.
- **Do not change 3DCraft from here.** What 3DCraft gets wrong or lacks is *collected* in
  [`3DCRAFT-FEEDBACK.md`](3DCRAFT-FEEDBACK.md) (§7); the developer takes it to 3DCraft in one go. Do not build
  around a limit in silence.
- **Jigs only: no assemblies.** No `assembly.*`, `instance.*`, `mate.*`, `joint.*`, `coupling.*` or motion
  commands: assemblies get a repository of their own later (the last ones are at the git tag
  `assemblies-format-58`). A mechanism moves in a Jig through a **drive parameter**: a published angle or position
  that places its parts by formulas, so the form's slider runs it (§4.1).
- **Original designs.** Generic types (a Dobsonian mount, a Gridfinity-compatible bin, a Jansen linkage) are fine and
  are credited; a brand's specific design, logo or name is not. Text uses 3DCraft's bundled fonts; never commit font
  files.
- **Licence.** The Jigs are CC-BY-4.0 unless a source requires otherwise (`gt2-pulley` is CC-BY-SA-4.0); the
  licence is in `document.info` and `meta.json`. The tools are MIT. Data from elsewhere (a star catalogue, a tune)
  needs a licence that allows it and a row in [`ATTRIBUTION.md`](ATTRIBUTION.md).

## 2. Layout

```text
AGENTS.md README.md CATALOGUE.md 3DCRAFT-FEEDBACK.md ATTRIBUTION.md LICENSE
tools/jigs.py           build, render, check, coverage, readme, site (python3, standard library only)
tools/pin.json          the pinned 3DCraft commit and file format
tools/bendcheck.py      proves sheet-metal parts bendable on a press brake (run by check when a Jig has press.json)
tools/gallery.py        the gallery page of the web folder (run by tools/jigs.py site)
findings/<J-nnn>-<slug>/  minimal reproducers for 3DCRAFT-FEEDBACK.md
jigs/NN-<id>/           everything of one Jig: NN its place in CATALOGUE.md, <id> kebab-case; the id never changes
                        (it is the file's name and URL) and never carries the number
site/ log/ plan/        local only (gitignored): the web folder tools/jigs.py site writes, dev log, plans
```

| File in `jigs/NN-<id>/` | What it is | Made by |
|---|---|---|
| `build.json` | **The source**: a JSON list of `[command, params]` steps run in a new document, ending with `document.check`. No file paths, no `file.*` or `jig.*` steps: the tool saves and publishes. | hand |
| `meta.json` | title, card summary, domain, tier, difficulty, standards, materials, licence, preview framing, exports | hand; `stats` and `craft3d` written by the tool |
| `README.md`, `formtest.md` | the Jig's page and its form test (§6) | hand |
| `<id>.3dcraftjig` | the published Jig, committed so it works without building | `tools/jigs.py build` |
| `preview.png`, `thumb.png` | the picture (§5) and the gallery's | `tools/jigs.py render` |
| `press.json` | sheet metal only: the parts `tools/bendcheck.py` must prove bendable | hand |
| `make.py`, `data/` | only for input from outside or a search (§3) | hand |

## 3. Working with 3DCraft

- **Build headless.** Edit `build.json`, then `tools/jigs.py build <id>`: it runs the script, refuses to publish
  when `document.check` is not ok, writes `jigs/NN-<id>/<id>.3dcraftjig`, measures, and lints names, form and budgets.
  To look around: `craft3d-cli run jigs/NN-<id>/<id>.3dcraftjig --cmd document.inspect`. To try the form:
  `craft3d-cli run jigs/NN-<id>/<id>.3dcraftjig --cmd param.list`, `--cmd param.set --params '{"values": {...}}'`. To learn
  a command: `craft3d-cli commands --filter <id>`. The user guide (`~/code/3dcraft/docs/guide/`, chapter 5 for Jigs)
  and its examples (`~/code/3dcraft/docs/examples/*.json`) show the idioms; read them, never edit them.
- **Never use the session's 3DCraft MCP tools** (`mcp__craft3d__*`): they drive the developer's own window. Work
  through `craft3d-cli`; its commands are the same ones MCP runs.
- **Memory and time.** The developer's laptop has crashed on runaway processes. `tools/jigs.py` caps every run; by
  hand, always `systemd-run --user --scope -q -p MemoryMax=3G -p MemorySwapMax=0 timeout 900 craft3d-cli …`. Exit
  137 means the cap was hit: that is a finding, never a reason to raise the cap. When several agents work at once, the
  coordinator sets a shared slice (`systemctl --user set-property --runtime jigs.slice MemoryMax=8G
  MemorySwapMax=0`): then `export CRAFT3D_SLICE=jigs.slice` (the tool adds it) and add `--slice=jigs.slice` to every
  `systemd-run` you type. One render or `check-range` at a time per agent. Never use `pkill` or `killall`: other agents and sessions share this machine. No cargo builds are needed here; never
  build 3DCraft from this repo. A 3DCraft window you start gets `--recovery-dir none`.
- **Python.** Everything a Jig decides lives in the document: variables, tables, formulas, `when` conditions,
  patterns, outputs, assertions. `build.json` is the source; no `gen.py` is committed. A long, repetitive
  `build.json` means a table, a pattern or a formula is missing. Python is allowed for what does not belong in a CAD
  platform (fetching and converting outside data, a search such as the orrery's gear trains): a `make.py` runs
  offline from committed inputs, is deterministic, and writes steps into `build.json`. Python that computes geometry
  3DCraft should compute is a workaround: log the missing capability first (§7), use it only when the Jig cannot
  exist otherwise, and say so in its README.
- **Lessons paid for by the examples:**
  - Face names come from the sketch's entity ids (`F2:side(e13)`): a point added to a profile renumbers its lines.
    Read them from `document.inspect` (`faceNames`) after every change to a profile.
  - A measure's face subject is a query: `{"kind": "face", "where": {"name": "*F6:side(e7)"}}` (a glob: later
    features prefix the names).
  - A feature's body cannot be measured once a later feature has taken it: measure the final body, and split it
    with planes (`volumeBelow`) or outputs (`variable.measure`) for closed-form checks.
  - Units in `tol` are expressions: `0.01 mm^3` means (0.01 mm)³; write the plain number `0.01` (the document's unit).
  - `body.appearance` replaces the whole appearance: give every field, or set them all in `material.preset`.
  - Coatings (black oxide, paint, powder coat, anodising) render best as a dielectric layer (`metallic` 0).
  - Every measure on a complex body runs at every regeneration, and in a Jig at every change of the form. Measure
    what proves something.
  - Every `variable.measure` and `variable.output` shows among the form's outputs, also one that only feeds an
    assertion: keep such helpers few (one measure per thing proven, not one per face) and label them `Check: …`, so
    the maker's outputs stay readable.
  - Standard values written from memory are often wrong: verify every value against a source and cite it.
  - Every number in the README is the model's (`output.list`, `assert.list`), and every claim is one the checks
    prove ("every length" when check-range tried 32 points is untrue).
  - Look at the full-size preview for renderer artefacts: smears (`look.reflections`), stepped shadow bands
    (`look.light`), blotches in cavities. Fix them with the framing keys of §5 and say so in the README.
  - Under the Workshop environment at rotation 0 the warm key light makes polished steel read as brass: render at
    `look.rotation` 0, 90, 180 and 270 and keep the one where neutral metals read neutral (often 180).
  - The body is named after its last feature: name that feature for the part ("Stand", "Bowl").
  - In a sketch a circle is entity `e2` (its centre is `e1`): `sketch.pattern` wants the `e2`.
  - `face.appearance` must follow its extrude: later on, source names are refused.
  - A sketch on the zx plane takes points as `[z, x]`.
  - A distance to a notched body can come back unproven: measure between plane faces.
  - Real use, not only the drawing: will it be gripped, driven, hung, will it tip, does it fit the tool that makes it
    (jaws, a slicer's walls, a press brake)?
- **Prefer 3DCraft's own means**: variables and formulas, tables with `choicesFrom`, ranges that are formulas of other
  parameters, `sketch.curve` (curves from formulas), `feature.pattern`, `sketch.pattern`, conditional features
  (`feature.when`), named sets for export, datums, `cut.list` and `cut.export` for plates, `feature.thread`,
  `feature.fold` and `feature.unfold`, `feature.sheetMetal`.

## 4. The quality bar

### 4.1 A real Jig
This is what separates a Jig from an example. A reviewer rejects a Jig that fails any of these:
- **The form asks what the maker knows.** Latitude, a mirror's diameter, a drawer's inside, a floor height, a bird
  species: the real need, in the maker's words and units. Not a list of the model's internal dimensions.
- **The form changes the structure, not only the sizes.** Counts, choices and options change what gets built: the
  number of treads, which holes, which joint. A Jig that only scales a shape is not a Jig; it is thrown away.
- **The result goes to a machine.** A cut sheet, a flat pattern, a 3MF in print orientation, a STEP, a cut list: named
  sets or plate bodies that export without picking anything, and a description that says how.
- **It knows its limits.** Ranges that depend on other parameters and on tables, so a bad combination cannot be
  entered; assertions that say why a design is out of bounds; outputs that tell the maker what matters (mass, tuning,
  load limit, cut length).
- **It is enjoyable.** Dragging a parameter shows something happening. Where the thing moves, a drive parameter
  runs it.

### 4.2 Real
Sizes follow the named standard (number, part, table) or a stated real reference, cited in the README. Proportions a
professional of the trade would accept **at every point of the range**, not only at the defaults. Real units and
tolerances where they matter.

### 4.3 Makeable
Name the process; prove with assertions what can be proven, over the range:
- **FDM printing:** walls ≥ 1.2 mm (`measure.thickness`); no overhang below 45° from the bed unless the README says
  where supports go (`measure.draft`, pull = the build direction); a first-layer chamfer; clearances for fits; 3MF
  export in the print orientation.
- **Sheet metal:** inner bend radius ≥ the material's minimum; `bendable`; holes ≥ 2.5 t + r from a bend; reliefs;
  flat pattern as DXF; `press.json` with the bend sequence proven where 3DCraft can.
- **Laser, plasma, waterjet:** smallest slot and hole ≥ the thickness; kerf stated and a parameter; cut and engrave apart.
- **CNC milling:** inside corners ≥ the tool radius; pockets ≤ 4 × the tool diameter deep.
- **Turning, casting, welding, woodworking:** casting draft ≥ 1° and fillets on every cast edge; weld access and joint
  preparation; boards of stock thickness, grain stated, joints in proportion.

### 4.4 Beautiful
- Fillets and chamfers wherever the real object has them (the developer asks this explicitly): no blocky, untouched
  edges.
- Materials from `material.preset`, tuned with `body.appearance` (colour, roughness); a colour and a density may
  follow a choice. Keep to your Jig's line of the palette in `CATALOGUE.md`, so the 33 look different side by side.
- The defaults show the Jig at its best: the object as it will be used, assembled and upright, not its parts laid out.
  Flat parts for cutting are a named set that exports, not what the preview shows, unless an option asks for them.
- Look at the preview at full size, and from two more angles and at two far points of the range, before you hand in.

### 4.5 Light
Loading means opening the `.3dcraftjig` and regenerating it; the tool measures it (`stats.load_s`, `craft3d-cli
info`, the least of two openings). Budgets on the developer's laptop: **simple ≤ 1 s, difficult ≤ 2 s, complex ≤ 4 s**,
file ≤ 1 MB, CPU time (all threads, `stats.load_cpu_s`) at most 3 × the load budget, since the web build is
single-threaded. A Jig is regenerated at every change of the form, so **the slowest point of the range is at most
3 × the load budget** (`stats.range_worst_s`). A timing taken while the machine is busy (load average over half its
CPUs) only warns; the coordinator re-measures at a quiet moment. Over budget, simplify (fewer, larger features; a
pattern instead of copies; no needless booleans; detail switched off by an option); only the coordinator grants
an exception (`meta.json` `budget_exception` with the reason).

### 4.6 Parametric, named, minimal
- Every size a maker might change is a variable; everything derived is a formula. No magic numbers in feature params
  (0, 1 and angles of symmetry aside).
- **Names.** Variables in descriptive `snake_case` with the unit in the expression (`wall_thickness` = `2 mm`, not
  `t`); features, sketches, datums, sets and assertions named for their intent in plain English (`Bolt holes`,
  `Seat round-over`). No automatic names (`Extrude2`): the tool rejects them.
- **The form: 3 to 12 public parameters**, in groups, each with a label a maker understands, a description, a unit
  and a range and step (`variable.publish`). The first group holds what most people change. Defaults make a good,
  typical object. More than 12 means the Jig is doing two jobs.
- **A minimal history.** Every step contributes to the final model: no dead, suppressed, trial or undone steps; one
  feature where one suffices. Guide: simple ≤ 100 steps, difficult ≤ 250, complex ≤ 600 (tables and assertions
  included; `variable.set` and `variable.publish` not counted). Order: variables and tables, then per part its sketches and features, materials, named sets,
  outputs and assertions, `variable.publish`, `document.info` (title, description with how to export, author
  `3DCraft Jigs`, licence, tags), `document.check`.

### 4.7 Proven over the range
End with assertions that make the Jig prove itself, at every point: at least one closed-form or independently computed
measure (volume, area, capacity, mass, a section property), the counts that matter, and the process checks of §4.3;
never fewer than three. Outputs carry the numbers a maker wants. `tools/jigs.py check` runs `check-range` (the
defaults, at most 64 corners of the box of the ranges, every choice, 32 random points from seed 1): every point passes, and any unproven assertion is
explained in the README. A claim about the range must be one those points support. **A passing range check is not the proof:** with many
parameters it sees a sliver of the box. For every assertion that can fail, work out which combination breaks it, make
the published ranges exclude it by formula (or let the assertion be the refusal the form shows), and try that combination
by hand with `param.set`. An assertion that compares a formula with itself proves nothing: remove it. An assertion measured on the
model is worth keeping even when the ranges should exclude a failure: it guards the modelling. Keep assertions cheap: they run at
every change of the form.

## 5. The preview

`tools/jigs.py render <id>`: 1600 × 1200 `preview.png` and 640 × 480 `thumb.png` in `jigs/NN-<id>/`, studio look,
**Workshop** environment, **ACES** tone curve, **+0.5 stop**, plain background, CPU renderer, 8 frames accumulated: the
same look as the examples. `meta.json` `preview` may set only the framing (`view`, `zoom`, `camera`, `projection`,
`box`, and `look.light`, `look.rotation`; `look.reflections: false` only where the renderer's reflections smear a
surface, said in the README). It takes about a minute.

## 6. README, meta.json and form test

**`README.md`** of a Jig, in this order: title and a one-paragraph pitch; the preview; *What it shows* (the 3DCraft
techniques, command ids in backticks, and what the form does that a static model cannot); *The real thing* (standards,
process, material, how to make it: print settings, cut and bend order, finish); *Parameters* (groups, ranges, what
each changes); *Checks* (the assertions in words, what the range check covers, what it does not); *Export* (what to
send to which machine); *Files*; *Rebuild*; *Difficulty* (the reviewer's score out of 10 and one line why); *Platform
notes* (links to `3DCRAFT-FEEDBACK.md` entries, if any). Every claim must be true of the model.

**`meta.json`**:

```json
{
  "id": "sundial",
  "title": "Garden sundial",
  "summary": "your place, hour lines, cut sheet",
  "description": "A horizontal or wall sundial for your latitude and longitude, to laser cut and engrave.",
  "domain": "Laser cutting, astronomy",
  "process": "Laser cutting and engraving",
  "tier": "complex",
  "difficulty": {"score": null, "rationale": ""},
  "standards": [],
  "materials": ["Brass sheet, 3 mm"],
  "licence": "CC-BY-4.0",
  "new": {"units": "mm"},
  "preview": {"zoom": 1.1, "look": {"light": [200, 70]}},
  "exports": [{"command": "file.export", "path": "exports/cut-sheet.svg", "set": "Cut sheet"},
              {"command": "file.export", "path": "exports/other.dxf", "set": "Cut sheet", "values": {"latitude": "37 deg"}}],
  "form_test": {"date": null, "model": null, "result": null}
}
```

`summary` is the card's line (a few words). `exports` are proven by `check` in a scratch folder and are not committed:
paths start with `exports/`, `command` is `file.export`, `cut.export` or `cut.list` (a saw list: no path), `values` runs the export at other parameter
values. `new` is optional (`file.new`'s params). `stats` and `craft3d` are written by the tool.

**`formtest.md`**: a real job in a maker's words ("I have a 150 mm f/6 mirror and want a telescope I can carry"; "our
stairwell is 2 760 mm high and 3 300 mm long"). Only the job: no parameter names or values. Below it, *Acceptance*: what
the result must be (counts, measures, what the exported file holds, an out-of-bounds request the Jig must refuse or
flag). The form tester gets only the published Jig and this text, and may use only `param.list`, `param.set` and an
export. A form that needs its README to be understood fails. Done once tested (§8): `meta.json` `form_test` records the
date, model and result.

## 7. 3DCraft feedback

Collect, never fix. [`3DCRAFT-FEEDBACK.md`](3DCRAFT-FEEDBACK.md) has four kinds:
- **Bug**: a wrong result, a crash, a valid request refused. With a minimal reproducer in
  `findings/<J-nnn>-<slug>/repro.json` (a script for `craft3d-cli run --new '{"units":"mm"}' --script`).
- **Missing capability**: phrased generally, for any shape and anyone who designs with 3DCraft (3DCraft is a platform:
  never "an astrolabe command", but "text along a circle given by a formula").
- **Performance**: too slow or too heavy, with numbers.
- **Agent friction**: what made building through commands slow or error-prone.

Each entry: id (`J-001` …, so as not to clash with the examples' `F-nnn`), kind, title, the Jig it was found in, the
3DCraft commit, what happens and what should happen, the reproducer, the impact on the Jig (blocked, workaround used,
cosmetic) and the workaround. Check `~/code/3dcraft-examples/3DCRAFT-FEEDBACK.md` first and cite an `F-nnn` that already
covers it. A Jig that works around something links its entry from its README, so it can be improved once 3DCraft is
fixed. Builders propose entries in their report and write the reproducer; the coordinator numbers them and edits
`3DCRAFT-FEEDBACK.md`.

## 8. Roles and the review loop

| Role | Model, effort | Does |
|---|---|---|
| **Coordinator** (main session) | Opus 5.5, xhigh | Owns this file, `CATALOGUE.md`, `README.md`, `3DCRAFT-FEEDBACK.md`, `tools/`; briefs agents; runs the review loop; commits (the only one who does); reports to the developer in Dutch. |
| **Feasibility probe** | Opus 5.5, medium | Answers "can 3DCraft do X at the pin" with a minimal script, before a risky Jig is built. |
| **Builder** | Opus 5.5; high (simple), xhigh (difficult, complex) | Owns `jigs/NN-<id>/` only. Writes `build.json`, `meta.json`, `README.md`, `formtest.md`; builds, renders, checks itself against §4 and looks at the pictures before handing in; writes reproducers in `findings/`. Never commits. |
| **Reviewer** | Opus 5.5; high, xhigh for complex | Fresh, and reads the files, not the builder's report. Plays the trade's professional (telescope maker, cabinetmaker, sheet-metal shop, print farm, aeromodeller, loudspeaker builder) **and** a first-time user of the form. Rebuilds, renders two more views and two far points of the range, checks §4 point by point, gives the difficulty score. |
| **Form tester** | Sonnet 5.5, medium (once Opus 5.5 if Sonnet fails, to tell a weak form from a weak model) | Fresh, gets only the Jig and `formtest.md`, fills the form, exports; the coordinator compares the result with the *Acceptance*. |

**Review verdict**: `PASS` or `REVISE`, with findings marked **MUST** (wrong, unmakeable, ugly, over budget, untrue
README, not a real Jig by §4.1), **SHOULD** or **NIT**, each with its evidence (a measure, a picture, a clause of a
standard, a point of the range), and the difficulty score with one line why. Builder and reviewer loop until no MUST is
open; the same reviewer is continued for the re-review.

**What reviews keep finding** (eleven Jigs so far; look for these yourself before handing in, it saves a round):
- An assertion that restates a formula instead of measuring the model: do a mutation test (break the geometry in a scratch
  copy) and see that an assertion notices. A loosened fit, a moved hole, a wrong ratio must fail something.
- A failure inside the published range that sampling missed: an unmakeable slit or a thin web, a model that does not build
  at one depth. Scan a grid of the combinations that matter; export and look at the file.
- Parts that cannot be assembled or made: a bearing that cannot reach its seat, a groove that ends in a flange, a shaft
  longer than its bore. Walk the assembly and the machine's path step by step.
- Exports: a part drawn twice, a section that is not true size, a helper body in the 3MF, a layout that does not fit the
  bed, or something a form user cannot get without picking.
- README claims the model does not bear out, and sources cited but not read (a value from memory that is cited is a MUST):
  say what was read, what is from a secondary source, what is your own judgement.
- Safety: a stair, a hanging table, a load limit. The form states only what the model proves and says who must verify the
  rest.

**Difficulty** (1 to 10, scored by the reviewer): what it takes to build this Jig from scratch in 3DCraft, by hand or
with an agent, the form and its range included.

| Score | Typical content |
|---|---|
| 1–2 | a few solid features from simple sketches, a small form |
| 3–4 | several features, a constrained sketch, patterns, fillets and chamfers, a table or formulas, options by `when` |
| 5–6 | datums and angled work, booleans between several bodies, sheet metal with several bends, folds, topology that changes with counts |
| 7–8 | freeform: lofts, sweeps along 3D paths, developables, surfaces; many coupled formulas; process checks across bodies; kernel limits to navigate over a range |
| 9–10 | class-A surfacing, data-driven geometry, large coupled multi-body designs, expert domain knowledge |

Tiers roughly: simple 1–3, difficult 4–6, complex 7–10.
The folders are numbered from the least to the most demanding (by score, then CATALOGUE.md's order), and
CATALOGUE.md follows the same numbers; a new Jig takes the number its score gives it, and the coordinator renumbers.

**Done, for one Jig:** `tools/jigs.py check <id>` passes · the preview is rendered at the pin and looked at · README,
meta.json and formtest.md are complete and true · reviewer PASS, score in `meta.json` · form tested · feedback entries
filed · committed by the coordinator and `tools/jigs.py readme` run.

## 9. Before a session ends

Append to `log/devlog.md` (local): what landed, the numbers (load time, steps, score), what is open. Keep
`tools/jigs.py check` green for every committed Jig: a session can end abruptly, and the dev log plus a clean tree is
how the next one picks up.
