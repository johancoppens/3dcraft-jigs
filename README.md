# 3DCraft Jigs

Parametric generators for [3DCraft](https://github.com/johancoppens/3dcraft) that run without AI.

A **Jig** is a 3DCraft design whose driving variables are published as **parameters**: a width, a number
of teeth, a laser's kerf. Someone who opens a Jig sets those parameters in a form and gets a new model,
regenerated deterministically by 3DCraft's own kernel; no AI and no code run. A published Jig is a
`.3dcraftjig` file: the same format as a `.3dcraft` document, with its info (title, description, author,
licence) and a thumbnail.

Jigs are not part of 3DCraft. 3DCraft provides the mechanism (public parameters, the form, `.3dcraftjig`
files, the range check); this repository holds Jigs.

| Jig | What it makes | Licence |
|---|---|---|
| [`laser-box`](jigs/laser-box/) | A finger-jointed box with a loose lid, cut from sheet | CC-BY-4.0 |
| [`welding-table`](jigs/welding-table/) | A fixture welding table: perforated top plate on half-lapped ribs with weld tabs | CC-BY-4.0 |
| [`gt2-pulley`](jigs/gt2-pulley/) | A GT2 (2 mm pitch) timing pulley with optional flanges and hub | CC-BY-SA-4.0 |
| [`spur-gear`](jigs/spur-gear/) | An involute spur gear (module, teeth, pressure angle), with an optional hub | CC-BY-4.0 |
| [`pot-knob`](jigs/pot-knob/) | A knob for a potentiometer or encoder shaft (D-shaft or round), with grip grooves | CC-BY-4.0 |

## Using a Jig

**Desktop.** Open a `.3dcraftjig` file (File › Open, or double-click it once 3DCraft is installed). It opens
on its **Parameters** tab: drag or type the values; the model follows. A value outside a parameter's range is
clamped and the form says so. Then **File › Export…** (STL, 3MF or STEP for a part; DXF or SVG for a cut
sheet). **Save** saves the result as an ordinary `.3dcraft` model; the Jig file itself is never changed.
**Open for editing** makes an editable copy if you want to change the design itself.

**Web.** The 3DCraft web build opens a Jig served from the same site:
`https://example.org/3dcraft/?open=/jigs/<id>.3dcraftjig`. The gallery page (`dist/index.html`)
links every Jig that way, and offers the file for download. In the browser the model follows a parameter
when you let go of it.

**Agents and scripts.** `param.list` lists the parameters, `param.set {"values": {...}}` sets several at once
(out-of-range values are refused with the range), for instance:

```sh
craft3d-cli run dist/laser-box.3dcraftjig \
  --cmd param.set --params '{"values": {"width": "220 mm", "height": "60 mm"}}' \
  --cmd file.export --params '{"path": "box.svg", "set": "Cut sheet"}'
```

## Layout

```text
jigs/<id>/build.json   the command batch that builds the Jig from nothing: the source of truth
jigs/<id>/new.json     (optional) params of file.new for the empty document; default {"units": "mm"}
jigs/<id>/README.md    what it makes, its parameters, sources and notes
jigs/<id>/gen.py       (optional) the script that wrote build.json, when the batch is long and generated
scripts/build.sh       build every Jig into dist/, then the gallery
scripts/check.sh       prove every Jig over its parameter range (craft3d-cli check-range)
scripts/gallery.py     dist/index.html and dist/thumbs/ from the built Jigs (Python standard library only)
dist/                  the built Jigs, their thumbnails and the gallery page
```

Each `build.json` is a JSON array of 3DCraft commands, run on an empty document by
`craft3d-cli run --new '{"units": "mm"}' --script jigs/<id>/build.json`. It models the part, publishes its
parameters (`variable.publish`: label, description, group, range, step, unit), sets the document info
(`document.info`: title, description, author "3DCraft Jigs", licence, tags) and ends with
`jig.export {"path": "dist/<id>.3dcraftjig"}`. The same 3DCraft version builds a bit-identical file.

`dist/` is committed (about 300 kB with thumbnails) so the Jigs can be used without building them. Rebuild
it after changing a `build.json` or upgrading 3DCraft, and commit the result together with the source.

## Building and checking

You need `craft3d-cli` from 3DCraft, any build that has `jig.export` and `check-range` (the files in `dist/`
were built and checked with 3DCraft `main` at 5a87fd70, format version 32). Put it on `PATH` or point `CRAFT3D_CLI` at it.

```sh
export CRAFT3D_CLI=/path/to/craft3d-cli
scripts/build.sh                 # every Jig, then dist/index.html; or scripts/build.sh laser-box
scripts/check.sh                 # every Jig over its range; exit 1 when a point fails
SAMPLES=64 SEED=7 DEEP=1 scripts/check.sh gt2-pulley   # a longer, deeper run
python3 scripts/gallery.py dist  # only the gallery
```

`check.sh` runs `craft3d-cli check-range` on each Jig with a fixed seed: the defaults, the corners of the
parameter ranges and random points, each regenerated from nothing and checked as `document.check` checks it
(no failed feature, valid closed bodies, no broken assertion, no invalid parameter). A Jig is only published
when every point passes; if one fails, fix the model or narrow its range.

**CI.** There is no GitHub-hosted workflow on purpose (it would cost Actions minutes). Build and check will
run on the developer's own runners later; until then run `scripts/build.sh && scripts/check.sh` before a
commit that changes a Jig.

## Hosting

The Jigs are served next to the 3DCraft web build on the same host, so the web build can open them
(it only opens same-origin files):

```text
https://example.org/3dcraft/                 the 3DCraft web build
https://example.org/jigs/                    the contents of dist/
https://example.org/jigs/index.html          the gallery
https://example.org/jigs/<id>.3dcraftjig     a Jig; the gallery opens it with ../3dcraft/?open=/jigs/<id>.3dcraftjig
https://example.org/jigs/thumbs/<id>.png     its thumbnail
```

Serve `.3dcraftjig` as `application/x-craft3d-jig` (or `application/zip`). Nothing on the server is set up
by this repository; the planned route is a release zip of `dist/` installed by the site's updater, with a
location for `/jigs/` beside the `/3dcraft/` one.

## Adding a Jig

1. Design it in 3DCraft (by hand, or an agent over MCP) as an ordinary `.3dcraft` document, every
   derived size a formula of a few input variables.
2. Write the commands as `jigs/<id>/build.json`, ending with `variable.publish` for each input,
   `document.info` and `jig.export {"path": "dist/<id>.3dcraftjig"}`.
3. `scripts/build.sh <id> && scripts/check.sh <id>`; look at the thumbnail and export a sample.
4. Add `jigs/<id>/README.md` and a row to the table above.

Keep Jigs light: a Jig makes one kind of product; anything that would work on any shape belongs in
3DCraft itself.

## Licences

- The scripts and the build sources' structure: MIT ([LICENSE](LICENSE)).
- Each Jig carries its own licence in its document info (`document.info.licence`, an SPDX id), shown in
  the gallery and in its README. The default is **CC-BY-4.0**, unless a source requires otherwise.
- `gt2-pulley` uses the GT2 tooth outline of droftarts' *Parametric Pulley - lots of tooth profiles*
  ([thingiverse.com/thing:16627](https://www.thingiverse.com/thing:16627)), licensed
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); that Jig (its `build.json`, `gen.py`
  and `.3dcraftjig`) is therefore shared under **CC-BY-SA-4.0**, with attribution to droftarts.
