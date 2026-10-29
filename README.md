# 3DCraft Jigs

Parametric generators for [3DCraft](https://github.com/johancoppens/3dcraft) that run without AI.

A **Jig** is a 3DCraft design whose driving variables are published as **parameters**: a width, a number
of teeth, a laser's kerf. Someone who opens a Jig sets those parameters in a form and gets a new model,
regenerated deterministically by 3DCraft's own kernel; no AI and no code run. A published Jig is a
`.3dcraftjig` file: the same format as a `.3dcraft` document, with its info (title, description, author,
licence) and a thumbnail.

Jigs are not part of 3DCraft. 3DCraft provides the mechanism (public parameters, the form, `.3dcraftjig`
files, the range check); this repository holds Jigs.

Grouped by workshop: laser cutting and woodwork, metalwork, mechanisms, 3D printing, and assemblies to a
standard.

| Jig | What it makes | Licence |
|---|---|---|
| [`laser-box`](jigs/laser-box/) | A finger-jointed box with a loose lid, cut from sheet, with an optional divider and lid grip | CC-BY-4.0 |
| [`key-tags`](jigs/key-tags/) | A sheet of key tags or name-tag blanks to laser-cut: rectangle, circle or hexagon | CC-BY-4.0 |
| [`shelf-32mm`](jigs/shelf-32mm/) | A bookcase or wardrobe carcass on the 32 mm system (IKEA compatible): sides drilled for 5 mm shelf pins, shelves, back, plinth, cut sheets | CC-BY-4.0 |
| [`flatpack-stool`](jigs/flatpack-stool/) | A screwless plywood stool or side table: cross-lap legs, tabs through the seat, hand-hold slot, cut sheet | CC-BY-4.0 |
| [`tensegrity-table`](jigs/tensegrity-table/) | A floating (tensegrity) table: top hung from the base's hook by a central cable, held level by 3 or 4 outer cables, with tensions and the load limit from statics, cut sheet | CC-BY-4.0 |
| [`sliceform`](jigs/sliceform/) | A sliceform sculpture or lamp shade: two families of laser-cut slices with half-lap slots showing a saddle, a wave, an ellipsoid or a twisted vase from its formula | CC-BY-4.0 |
| [`miura-ori`](jigs/miura-ori/) | A Miura-ori fold panel of up to 14 rows by 16 columns that folds in and out with one slider (the other creases solved by 3DCraft), of paper to folded flat or of thick card or plywood panels on a fabric hinge to where they meet; Kawasaki, Maekawa, flat-foldability and the thick panels' volume and height asserted, with its crease pattern to print and score or laser-score | CC-BY-4.0 |
| [`joint-drawer`](jigs/joint-drawer/) | A drawer or box with through dovetails or finger joints, a bottom in a groove and a brass knob | CC-BY-4.0 |
| [`solar-cooker`](jigs/solar-cooker/) | A parabolic solar cooker from flat petals (gores) drawn from the paraboloid's arc length, tilting on an axis through the focus so the pot stays level, with cut sheets | CC-BY-4.0 |
| [`sundial`](jigs/sundial/) | A horizontal garden or (declining) wall sundial for your place: hour lines with the longitude correction, numerals, a slotted gnomon at the latitude angle, cut sheet | CC-BY-4.0 |
| [`welding-table`](jigs/welding-table/) | A system welding table (System 16 / 28 block style) to laser cut and MIG weld: perforated top and skirts, half-lapped ribs, every joint tab and slot with dogbone reliefs and plug-weld pockets, legs and frame of square tube from a table, cut sheet and tube cut list | CC-BY-4.0 |
| [`welded-table-frame`](jigs/welded-table-frame/) | A welded steel table frame of tube or angle, mitred or butt, with cross rails, levelling feet and a cut list | CC-BY-4.0 |
| [`wall-bracket`](jigs/wall-bracket/) | A shelf bracket whose plate and gusset are sized from the load by formulas, with a load limit | CC-BY-4.0 |
| [`sheet-metal-enclosure`](jigs/sheet-metal-enclosure/) | A two-part sheet-metal case for electronics to laser cut and bend: a base with return flanges (each with an outline of its own holding its screw holes) and a lid screwed onto them, closed corners (overlap, butt or miter, with their gap) and corner reliefs, vent slots and feet holes, bend radius, flanges, hole distances and corner gaps checked against a material table (DC01, 5754, 304), flat patterns with every hole, the bend lines and the bend table | CC-BY-4.0 |
| [`tuned-chimes`](jigs/tuned-chimes/) | A wind chime of tubes or a glockenspiel of bars, each cut to its note by the free-free beam formula, with holes at the nodes, a cut list and a cut sheet | CC-BY-4.0 |
| [`gt2-pulley`](jigs/gt2-pulley/) | A GT2 (2 mm pitch) timing pulley: round, D-shaft or keyway bore, set screws with optional captive nuts, optional flanges and hub | CC-BY-SA-4.0 |
| [`spur-gear`](jigs/spur-gear/) | An involute spur gear (module, teeth, pressure angle): bore types, hub with set screws, web and lightening holes | CC-BY-4.0 |
| [`planetary-gearbox`](jigs/planetary-gearbox/) | A planetary gear set (sun, planets, ring, carrier) with involute teeth and its assembly conditions | CC-BY-4.0 |
| [`gear-reducer`](jigs/gear-reducer/) | A two-stage spur gear reducer from a target ratio: involute gears keyed on stepped shafts (DIN 6885), ISO 15 bearings, a split cast housing, twenty-two assertions on fits and clearances | CC-BY-4.0 |
| [`strandbeest-leg`](jigs/strandbeest-leg/) | Theo Jansen's walking linkage from his "holy numbers": drag the crank angle and the leg walks, joints solved by circle intersections, foot path drawn, layered bars and pins checked, cut sheet | CC-BY-4.0 |
| [`orrery`](jigs/orrery/) | A hand-cranked geared orrery, Mercury to Saturn and the Moon, whose two-stage trains were searched to match the real sidereal periods (one crank turn a year, the date sets every planet to its mean longitude), with a cut sheet for laser-cut gears | CC-BY-4.0 |
| [`pillow-block`](jigs/pillow-block/) | A pillow block bearing housing for a deep-groove bearing from a table (608, 60xx, 62xx), with slots and a grease nipple | CC-BY-4.0 |
| [`drag-chain`](jigs/drag-chain/) | A printable cable drag chain with snap-in hinge pins and clip-on bridges, laid out round its bend radius | CC-BY-4.0 |
| [`pot-knob`](jigs/pot-knob/) | A knob for a potentiometer or encoder shaft (D-shaft or round), with grip grooves | CC-BY-4.0 |
| [`gridfinity-bin`](jigs/gridfinity-bin/) | A Gridfinity storage bin: grid size, height, dividers both ways, label tabs at the back or front with their angle, scoops, magnet and screw holes, stacking lip, wall and floor | CC-BY-4.0 |
| [`gridfinity-baseplate`](jigs/gridfinity-baseplate/) | A Gridfinity baseplate that fills a drawer: the cells that fit, centred, filler strips to the walls, split into pieces for your print bed that lock with bowtie clips or dovetails; light, solid or weighted, magnet and screw holes; checked against a seated bin | CC-BY-4.0 |
| [`electronics-enclosure`](jigs/electronics-enclosure/) | A box for a circuit board: standoffs, port cut-outs from a table, a screwed or snap-fit lid | CC-BY-4.0 |
| [`print-in-place-hinge`](jigs/print-in-place-hinge/) | A hinge that prints in one piece on conical pins, with an adjustable clearance | CC-BY-4.0 |
| [`screw-jar`](jigs/screw-jar/) | A jar with a helical thread and a screw-on lid that follows it, with grip ribs | CC-BY-4.0 |
| [`phone-stand`](jigs/phone-stand/) | A phone or tablet stand with a curved strut and open back: angle, device thickness, optional cable slot | CC-BY-4.0 |
| [`wavy-vase`](jigs/wavy-vase/) | A twisted, wavy vase or pot cover from a formula, for vase-mode printing | CC-BY-4.0 |
| [`cubesat`](jigs/cubesat/) | A CubeSat to the CDS Rev 14.1 and PC/104: 1U to 6U, stowed or deployed wings and antennas, a PC/104 stack as large as fits, optional camera, twelve assertions on the standard | CC-BY-4.0 |
| [`rack-panel`](jigs/rack-panel/) | A 19-inch rack front panel (EIA-310) of 1 to 4 U in aluminium or steel sheet: flat or with bent-back flanges, M6 slots or holes on the rail pattern, handle holes, a row of D-sub or XLR cut-outs or a window, flat pattern | CC-BY-4.0 |
| [`rack-cabinet`](jigs/rack-cabinet/) | A wall-mount 19-inch rack cabinet of 6 to 15 U, every part bent from sheet: sides, lid and pan with knock-outs, wall plate screwed to the sides by six tabs, L or C rails with cage-nut or M6 holes front and rear bolted to the sides, a vented door with hinge holes, closed corners; every hole in the flat patterns; rack-panels fit it | CC-BY-4.0 |

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
jigs/<id>/build.json   the command batch that builds the Jig (from nothing, or from source.3dcraft): the source of truth
jigs/<id>/source.3dcraft  (optional) a document designed interactively, opened by build.json
jigs/<id>/edits/       (optional) the command batches applied to source.3dcraft since, NN-<what>.json, in order
jigs/<id>/new.json     (optional) params of file.new for the empty document; default {"units": "mm"}
jigs/<id>/README.md    what it makes, its parameters, sources and notes
jigs/<id>/gen.py       (optional) the script that wrote build.json, when the batch is long and generated
jigs/<id>/press.json   (sheet metal) the parts scripts/bendcheck.py proves bendable on a press brake, and where
scripts/build.sh       build every Jig into dist/, then the gallery
scripts/check.sh       prove every Jig over its parameter range (craft3d-cli check-range)
scripts/bendcheck.py   prove a sheet-metal Jig's parts bendable on a press brake (sheetMetal.bendSequence)
scripts/shaftlib.py    shared bore and set-screw options (gt2-pulley, spur-gear gen.py)
scripts/gridfinitylib.py  the Gridfinity dimensions and profiles (gridfinity-bin, gridfinity-baseplate gen.py)
scripts/racklib.py     the 19-inch rack (EIA-310) dimensions and the sheet stock table (rack-panel, rack-cabinet gen.py)
scripts/gallery.py     dist/index.html and dist/thumbs/ from the built Jigs (Python standard library only)
dist/                  the built Jigs, their thumbnails and the gallery page
```

Each `build.json` is a JSON array of 3DCraft commands, run on an empty document by
`craft3d-cli run --new '{"units": "mm"}' --script jigs/<id>/build.json`. It models the part, publishes its
parameters (`variable.publish`: label, description, group, range, step, unit), sets the document info
(`document.info`: title, description, author "3DCraft Jigs", licence, tags) and ends with
`jig.export {"path": "dist/<id>.3dcraftjig"}`. The same 3DCraft version builds a bit-identical file.

A Jig designed interactively (by hand or by an agent over MCP) can keep that document as
`jigs/<id>/source.3dcraft`, with its parameters already published; its `build.json` starts with
`file.open {"path": "jigs/<id>/source.3dcraft"}`, then sets the document info and exports. Change such a
design with command batches that open `source.3dcraft`, make the edits and `file.save` it, run with
`craft3d-cli run --script`, and keep each batch as `jigs/<id>/edits/NN-<what>.json` so the change can be
reviewed (`cubesat` is built this way).

`dist/` is committed (about 300 kB with thumbnails) so the Jigs can be used without building them. Rebuild
it after changing a `build.json` or upgrading 3DCraft, and commit the result together with the source.

## Building and checking

You need `craft3d-cli` from 3DCraft, any build that has `jig.export` and `check-range` (the files in `dist/`
were built with different builds of 3DCraft `main`, so a Jig needs a build that reads its format version or a newer
one). Most were built and checked at 3faaaea0 (format version 36); `gridfinity-bin` and `gridfinity-baseplate` are at
format version 37; `rack-panel` (sheet metal) was built and checked at 3DCraft 3c885c35 and is at format version 50;
`rack-cabinet` and `sheet-metal-enclosure` (flanges with an outline of their own, flange ids) were built and
checked at 3DCraft 1f92b83b and are at format version 50 (their bend sequences checked at 0dc5efb6, whose
sheet metal is the same); `miura-ori` (creases from sketch patterns, folding flat, thick panels) is at format
version 50, built and checked at 0dc5efb6 and 1f92b83b. Each needs that build or a newer one. Put it on `PATH`
or point `CRAFT3D_CLI` at it.

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

**Bend sequence.** A sheet-metal Jig also has a `press.json`, and `scripts/bendcheck.py <id>` runs
3DCraft's `sheetMetal.bendSequence` on its parts at the points `check-range` takes (fewer of them by
default: the defaults, 8 corners, every choice, 8 random points), with a straight punch, a gooseneck
punch and a V-die of 8 t unless `press.json` names the opening (the tools are in the script): an order of the bends in which neither tool comes
within 0.5 mm of the part. `bendSequence` is a command, not an assertion, so this is a script beside
`check.sh` and not part of `check-range`; what each Jig's parts are proven to do, and what 3DCraft cannot
prove yet, is in its README.

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
