# 3DCraft feedback from the Jigs

> **About this file.** While the Jigs were built, everything 3DCraft got wrong or could not yet do was written
> down here rather than worked around in silence: bugs, each with a minimal reproducer under `findings/`, missing
> capabilities, performance with numbers, and friction for an agent that drives 3DCraft through its commands. It
> is a dated record against the 3DCraft commits named below, not a list of known issues of the current release.
> Entries fixed since say so in their status line, "R1" is the milestone that became 3DCraft 0.1.0, and "3DCraft's
> session" is the agent session that works on 3DCraft itself. To see whether an entry still holds in your version,
> run its reproducer with `craft3d-cli run --new '{"units":"mm"}' --script findings/<id>/repro.json`.

What building the Jigs found in 3DCraft: bugs, missing capabilities, performance and agent friction (AGENTS.md §7).
Collected here, never fixed from this repository. Ids are `J-nnn`; an entry that the examples already reported cites its
`F-nnn` in the examples' [`3DCRAFT-FEEDBACK.md`](https://github.com/johancoppens/3dcraft-examples/blob/main/3DCRAFT-FEEDBACK.md). Each entry was reproduced at the pin, 3DCraft `150f0015`, unless
it says otherwise. A reproducer runs with `craft3d-cli run --new '{"units":"mm"}' --script findings/J-nnn-<slug>/repro.json`.

**Status (2026-11-10):** the Jigs are built and checked on 3DCraft `dc449d5a` (the same command line as `150f0015`; only
the window changed). 3DCraft's session triaged all 71 entries with the developer: J-020 (a warning), J-021 (the summary says
distance is between surfaces), J-022, J-042, J-008, J-003 and J-026 (a feature switched off is skipped in a list of bodies),
J-040 (a face colour wins), J-045 and J-046 (hidden bodies left out of 3D exports and the cut list) are being fixed for R1,
J-028 if it stays small; the rest is ordered for after R1 (J-018 first, J-015 with J-014).

## Index

| Id | Kind | Title | Jig | Impact |
|---|---|---|---|---|
| J-001 | Missing capability | `jig.export`'s thumbnail cannot be given a view or a look | all | The picture inside a `.3dcraftjig` is the flat one `file.save` draws; the gallery uses its own render |
| J-002 | Bug | `measure.overlap` errors when a curve coincides with a circle | nest-box | The zinc guard is left out of the overlap assertion. |
| J-003 | Bug | `cut.list` and `cut.export` refuse an inactive feature in `bodies` | nest-box | The layout uses a named set, so the boards do not lie along the plank. |
| J-004 | Bug | `cut.list` reads an extruded bent strip and a chamfered board as plates of the extrusion's length | nest-box | Boards stay square-edged; the zinc strip gets an odd row. |
| J-005 | Bug | `material.preset` with a pattern fails on a body that is inactive at the defaults | nest-box | Those three are given by hand. |
| J-006 | Missing capability | A sketch entity cannot be switched off by a formula | nest-box | An absent board is a 0.01 mm speck in the plank plan. |
| J-007 | Missing capability | A named set cannot export a sketch | nest-box, astrolabe | The README tells the user to select the sketch. |
| J-008 | Bug | `sketch.path` `start` refuses an image point that `sketch.line` takes | laser-box | A line is drawn first. |
| J-009 | Missing capability | A material pattern's colours cannot be expressions (see F-171) | laser-box | One wood only. |
| J-010 | Missing capability | `cut.list` treats a pattern of separate plates as one non-plate body | rc-wing | A named face set through `file.export`. |
| J-011 | Missing capability | A pattern instance has no index to read a table with (see F-027) | rc-wing, music-box | Per-note sketches in the music box; the rib slices in the wing. |
| J-012 | Missing capability | `sketch.pattern` `skip` takes only literal instances | music-box | Pins are drawn one by one. |
| J-013 | Bug | A circle wrapped onto a cylinder and joined can fail `document.check` | music-box | Pins are rectangular. |
| J-014 | Missing capability | A fold whose free edges meet exactly is refused | polyhedron-net | The form's 100 % is capped at 99.99 %. |
| J-015 | Bug | `cavity` returns a number for an open sheet; distances between a sheet's faces cannot be measured (see F-105) | polyhedron-net | The cavity is asserted near closure only. |
| J-016 | Bug | A `sketch.curve` whose ends meet when created stays closed for good | astrolabe | Two half-arcs. |
| J-017 | Missing capability | Open curves cannot be given a stroke width | astrolabe | Closed slot profiles for each line. |
| J-018 | Bug | `clearance` reports two bodies clear that `overlap` finds sharing 13.5 mm^3 | drag-chain | The lid's fit is asserted with `overlap` as well. |
| J-019 | Bug (proof weakness) | Distance and clearance assertions stop refining before they can decide their bound (see F-030) | gear-reducer, planetary-gearbox | Gaps between flanks are proven through outputs or one flank family at a time. |
| J-020 | Bug | An assertion bound finer than the document's tolerance passes a value far outside it | music-box | Tight checks are counts, not bounds on lengths. |
| J-021 | Bug | `distance` from a body lying inside another body is the gap to its surface, not 0 | solar-cooker | A sunk part is caught by another probe. |
| J-022 | Bug | A named set of bodies as `of` works for `extent` but `area` says it names nothing | polyhedron-net | The set is given as a query. |
| J-023 | Bug | A face cut in two by a boolean counts as one face (see F-141) | geodesic-dome, joint-drawer | Counts are taken of something else. |
| J-024 | Bug | A sketch arc's radius drifts below its value after re-solves, and `radius: {min}` has no tolerance | cubesat | The bound is written 0.001 mm under the standard's. |
| J-025 | Bug | `overlap` cannot decide plates that touch at zero clearance after `param.set` (see F-130) | welded-box | The overlap checks are off at 0 clearance. |
| J-026 | Bug | `overlap` errors on a feature switched off by `when` instead of skipping it | rack-cabinet, wooden-stair | The bodies are given by a query, or the assertion is split. |
| J-027 | Bug (proof weakness) | The extent of a swept body is not proven to the tolerance, and a sweep's path length cannot be read (see F-117, F-122) | jansen-leg | The step length is checked within 0.005 mm plus 50 millionths of it. |
| J-028 | Bug | A feature switched off by `when` still takes its source body, so alternatives cannot share a source | tensegrity-table | One chain of features per alternative. |
| J-029 | Bug | A fillet cannot be added while the bodies it joins are switched off | gear-reducer | The build switches the option on while it adds the round. |
| J-030 | Bug | Chamfering the rim of a rectangular opening is refused (see F-033) | tuned-chimes | The opening stays square-edged. |
| J-031 | Bug | A closed path of formula-curve pieces that meet end to end is refused for a sweep | jansen-leg | Four open sweeps instead of one closed one. |
| J-032 | Bug | Joining two sweeps that start from one section sketch fails at the shared end (see F-113) | wooden-stair | The rail's returned ends are separate bodies. |
| J-033 | Bug | A sketch arc given by a through-point loses its centre when it flips or flattens, and can leave a document unrecoverable (see F-112, F-113) | loudspeaker-box | Every arc is given by a centre written as a formula. |
| J-034 | Bug | A spline through points strays between them far more than a cubic interpolant | planetary-gearbox, gear-reducer | Flanks are circular arcs. |
| J-035 | Bug | `feature.plate` refuses a valid section: "face 0 cannot be tessellated" | sliceform | The form's range is cut back. |
| J-036 | Bug | `feature.plate` refuses some sections of a twisted loft: "the edge across a corner could not be traced" (see F-169) | sliceform | A shape was left out of the Jig. |
| J-037 | Bug | A flat net reports facets that share only a vertex as touching, at one edge length | polyhedron-net | The form's values are whole millimetres. |
| J-038 | Bug (suspected) | Glue tabs folded with a net are refused near closure | polyhedron-net | Tabs on the flat pattern only. |
| J-039 | Bug | A cut by thirteen rows of text is refused for memory, after 28 s and 2.5 GB (see F-034) | tuned-chimes | Lettering as holes in the strips, not pockets. |
| J-040 | Bug | A face colour given on a feature is hidden when the body's colour is given on a later feature | dobsonian-telescope, cubesat | Face colours are given on the final feature's face names. |
| J-041 | Bug | A material pattern stays in the model's space when its body is turned (see F-083) | jansen-leg | Cosmetic: the grain runs at a slant. |
| J-042 | Bug (cosmetic) | `cut.list` prints a turned plate's thickness with rounding noise | solar-cooker | The csv shows 3.0000000000001705. |
| J-043 | Missing capability | A flat face or a plate cannot be exported as seen from a chosen side (see F-086) | sundial | Kerf in the bodies; edges left square. |
| J-044 | Missing capability | A named set exports each face in its own place on the sheet, not where it lies (see F-142) | astrolabe, sundial, tuned-chimes, wooden-stair | Engravings drawn as one face; marks placed by hand. |
| J-045 | Missing capability | A 3D export cannot be given a named set, and without `bodies` it writes hidden bodies too (see F-045, F-161) | gridfinity-baseplate, gridfinity-bin, drag-chain, joint-drawer, cycloidal-drive, cubesat, dobsonian-telescope, solar-cooker, tuned-chimes | Switches, lists of bodies or no 3D export. |
| J-046 | Missing capability | `cut.list` and `cut.export` cannot be limited to the parts to cut (see F-161, J-003) | orrery, loudspeaker-box | Rods chamfered so they are not plates; blanks as outputs. |
| J-047 | Missing capability | A chamfer cannot follow the rim of an extruded freeform outline (see F-075, F-158) | cam-disc, cycloidal-drive, planetary-gearbox, gear-reducer | Rims left sharp, or a cone cut. |
| J-048 | Missing capability | Rounds where a cylindrical boss meets a drafted wall and a flange are refused (see F-099) | gear-reducer | Octagonal bosses; some junctions left sharp. |
| J-049 | Missing capability | Hole rims of a varying count cannot be chamfered cheaply, and a countersunk plate is no plate to `cut.list` (see F-086, F-088) | welding-table | Holes left as cut. |
| J-050 | Missing capability | `feature.plate` takes one connected sheet only | sliceform | One plate per possible slice, switched by its count. |
| J-051 | Missing capability | A body folded flat cannot be built on or moved | miura-ori | At 100 % the folded pack is not levelled. |
| J-052 | Missing capability | `feature.transform` cannot place a body by a target frame | geodesic-dome | Nine helper variables per placement. |
| J-053 | Missing capability | `metallic`, `roughness` and `transmission` take numbers only, so a material look cannot follow a choice | keyboard-plate, gt2-pulley, rack-cabinet, sheet-metal-enclosure, dobsonian-telescope | Materials differ in colour only, or a body per look. |
| J-054 | Missing capability | An expression cannot define a function or a local name | sundial, jansen-leg, orrery | Formulas written out per instance. |
| J-055 | Missing capability | No maximum, minimum or root of a formula over an interval | cam-disc, jansen-leg | Peaks sampled; searches written out. |
| J-056 | Missing capability | No frequency or electrical units: Hz, V, A, W, h, mAh, Wh (see F-106) | loudspeaker-box, tuned-chimes, cubesat | Plain numbers with the unit in the label. |
| J-057 | Missing capability | `variable.measure` takes no `when` | planetary-gearbox, cubesat | Measured gaps are assertions, not outputs. |
| J-058 | Missing capability | An output used only by assertions cannot be kept off the form | solar-cooker | Checks measure inside the assertions. |
| J-059 | Missing capability | An output cannot have a description | rack-cabinet | Warnings ride on labels. |
| J-060 | Performance | Grooves that cross each other cost 20 times grooves that do not | astrolabe | Grooves only on request; lines drawn as thin bodies. |
| J-061 | Performance | Subtracting one many-lump tool from each of many targets is twice as slow as cutters per target | gridfinity-baseplate | Three more features per piece. |
| J-062 | Performance | A circular pattern of pieces that meet edge to edge is joined at twice the cost, with no way to keep them apart (see F-125) | solar-cooker | Two interleaved patterns; the count must be even. |
| J-063 | Performance | A wrapped profile with slanted edges is about 50 times heavier than a rectangular one | music-box | Rectangular pins. |
| J-064 | Performance | A revolved cone cut across spline gear teeth costs four times the gear | planetary-gearbox | The tip chamfer is on the print plate only. |
| J-065 | Performance | Measuring a flat gear costs about 1.4 ms of CPU per tooth, far more than building it | orrery, planetary-gearbox | Fewer measures and fewer teeth. |
| J-066 | Performance | Formula curves are fitted far below the document's tolerance (see F-010) | gear-reducer, planetary-gearbox, solar-cooker | Arcs or exact low-degree splines instead. |
| J-067 | Performance | The flat-fold layer-order search gives up on larger Miura grids | miura-ori | The grid is capped. |
| J-068 | Performance (file size) | A document with text carries the whole font (see F-037) | astrolabe, tuned-chimes, sundial | A third of the 1 MB budget. |
| J-069 | Agent friction | Expressions are capped at different sizes in different places | rc-wing, music-box | Long formulas go through variables; one check split in three. |
| J-070 | Agent friction | A curvature assertion's `at` takes plain numbers only (see F-094) | dobsonian-telescope | The curvature is measured on an unmoved copy. |
| J-071 | Missing capability | `extent`, `boxMin` and `boxMax` measure bodies only, not faces | cubesat | The countersunk screw heads are drawn and their overlap with the rail is measured. |

## J-001: a Jig's thumbnail cannot be given a view or a look

- **Kind:** missing capability. **Jig:** all.
- **What happens:** `jig.export {path}` writes `thumb.png` "as `file.save` draws it": one view, one flat look.
- **What should happen:** the maker of any Jig can choose the view and the look of its picture, the same way `view.render`
  does, since a file manager or a gallery shows that picture first.
- **Impact:** cosmetic. **Workaround:** `tools/jigs.py render` writes each Jig's `thumb.png` for the gallery.

## J-002: `measure.overlap` errors when a curve coincides with a circle

- **Kind:** bug. **Jig:** nest-box.
- **What happens, and what should:** An `overlap` assertion between a plate with a round hole and a ring in it reports "cannot be measured: ... boolean does not support this". It should tell whether they overlap.
- **Reproducer:** `findings/J-002-overlap-curve-hole/repro.json`
- **Workaround and impact:** The zinc guard is left out of the overlap assertion.

## J-003: `cut.list` and `cut.export` refuse an inactive feature in `bodies`

- **Kind:** bug. **Jig:** nest-box.
- **What happens, and what should:** A Jig that lists its optional boards by name fails when an option is off ("has no body now: it is inactive"). An inactive body should be skipped, so one list holds for every option.
- **Reproducer:** `findings/J-003-cut-bodies-inactive/repro.json`
- **Workaround and impact:** The layout uses a named set, so the boards do not lie along the plank.

## J-004: `cut.list` reads an extruded bent strip and a chamfered board as plates of the extrusion's length

- **Kind:** bug. **Jig:** nest-box.
- **What happens, and what should:** A bent strip extruded 160 mm is listed as a plate 160 thick; a chamfered board likewise. It should say they are not plates, or find the real thickness.
- **Reproducer:** `findings/J-004-eased-plate/repro.json`
- **Workaround and impact:** Boards stay square-edged; the zinc strip gets an odd row.

## J-005: `material.preset` with a pattern fails on a body that is inactive at the defaults

- **Kind:** bug. **Jig:** nest-box.
- **What happens, and what should:** "the body has no geometry yet to fit the pattern to". Any option that starts off cannot be given a patterned material without `pattern.scale`, `axis` and `origin`; the fit should wait for the geometry.
- **Reproducer:** `findings/J-005-preset-inactive-body/repro.json`
- **Workaround and impact:** Those three are given by hand.

## J-006: A sketch entity cannot be switched off by a formula

- **Kind:** missing capability. **Jig:** nest-box.
- **What happens, and what should:** A rectangle or a label in a sketch exists at every point of the range, and a rectangle of zero size is refused. A drawing whose rows depend on an option needs entities that come and go with a condition.
- **Reproducer:** `findings/J-006-sketch-entity-when/repro.json`
- **Workaround and impact:** An absent board is a 0.01 mm speck in the plank plan.

## J-007: A named set cannot export a sketch

- **Kind:** missing capability. **Jig:** nest-box, astrolabe.
- **What happens, and what should:** `set.define` accepts kind `sketch`, but `file.export {set}` refuses it ("holds no flat face"). What a designer drew as the plan for a machine cannot be offered in the export dialog without selecting it in Features, which a Jig's user should not have to do.
- **Reproducer:** `findings/J-007-set-of-sketch-export/repro.json`
- **Workaround and impact:** The README tells the user to select the sketch.

## J-008: `sketch.path` `start` refuses an image point that `sketch.line` takes

- **Kind:** bug. **Jig:** laser-box.
- **What happens, and what should:** "e10 is a image, not a point". Both should accept the same references.
- **Reproducer:** `findings/J-008-sketch-path-from-image/repro.json`
- **Workaround and impact:** A line is drawn first.

## J-009: A material pattern's colours cannot be expressions (see F-171)

- **Kind:** missing capability. **Jig:** laser-box.
- **What happens, and what should:** A pattern's `colors` take literals only, although `body.appearance` `color` takes expressions as `[r, g, b]`, so a veneer's grain cannot follow a choice of wood.
- **Reproducer:** `findings/J-009-pattern-colours-from-a-table/repro.json`
- **Workaround and impact:** One wood only.

## J-010: `cut.list` treats a pattern of separate plates as one non-plate body

- **Kind:** missing capability. **Jig:** rc-wing.
- **What happens, and what should:** Plates patterned and intersected form one multi-lump body, which `cut.list` refuses; `body.split` does not follow a changing count. Separate lumps should count as parts.
- **Reproducer:** `findings/J-010-cutlist-pattern-of-plates/repro.json`
- **Workaround and impact:** A named face set through `file.export`.

## J-011: A pattern instance has no index to read a table with (see F-027)

- **Kind:** missing capability. **Jig:** rc-wing, music-box.
- **What happens, and what should:** `i` and `index` are unknown in a pattern, so a pattern cannot scale, skip or place instances from a table. It forces one sketch or feature per instance.
- **Reproducer:** none needed: the command list says so.
- **Workaround and impact:** Per-note sketches in the music box; the rib slices in the wing.

## J-012: `sketch.pattern` `skip` takes only literal instances

- **Kind:** missing capability. **Jig:** music-box.
- **What happens, and what should:** `skip` must be an array of numbers; a formula cannot leave instances out.
- **Reproducer:** `findings/J-012-sketch-pattern-skip-literal/repro.json`
- **Workaround and impact:** Pins are drawn one by one.

## J-013: A circle wrapped onto a cylinder and joined can fail `document.check`

- **Kind:** bug. **Jig:** music-box.
- **What happens, and what should:** "a boundary integral that does not settle", depending on the position. The same circle elsewhere passes.
- **Reproducer:** `findings/J-013-wrapped-circle-check/repro.json`
- **Workaround and impact:** Pins are rectangular.

## J-014: A fold whose free edges meet exactly is refused

- **Kind:** missing capability. **Jig:** polyhedron-net.
- **What happens, and what should:** A net folding shut stops at 99.99999 % ("touch or lie on each other"). Closing a loop is what a net is for.
- **Reproducer:** `findings/J-014-fold-closed-loop/repro.json`
- **Workaround and impact:** The form's 100 % is capped at 99.99 %.

## J-015: `cavity` returns a number for an open sheet; distances between a sheet's faces cannot be measured (see F-105)

- **Kind:** bug. **Jig:** polyhedron-net.
- **What happens, and what should:** A net folded halfway has a `cavity` of 18 674 mm³, though it encloses nothing: it should refuse. Seam closure cannot be asserted.
- **Reproducer:** `findings/J-015-cavity-open-sheet/repro.json`
- **Workaround and impact:** The cavity is asserted near closure only.

## J-016: A `sketch.curve` whose ends meet when created stays closed for good

- **Kind:** bug. **Jig:** astrolabe.
- **What happens, and what should:** When a variable later opens it the sketch fails: "starts and ends on the one point e1, but its formulas put its start at ...". Closed or open should follow the formulas.
- **Reproducer:** `findings/J-016-curve-closed-for-good/repro.json`
- **Workaround and impact:** Two half-arcs.

## J-017: Open curves cannot be given a stroke width

- **Kind:** missing capability. **Jig:** astrolabe.
- **What happens, and what should:** `feature.offsetProfile` refuses an open line ("the profile is not closed"). Engraving a line needs a stroke of width w along it, for any curve.
- **Reproducer:** `findings/J-017-offset-open-curve/repro.json`
- **Workaround and impact:** Closed slot profiles for each line.

## J-018: `clearance` reports two bodies clear that `overlap` finds sharing 13.5 mm^3

- **Kind:** bug. **Jig:** drag-chain.
- **What happens, and what should:** Between a chain link and its lid, `clearance` returns `clear`, 0.0707 mm found and at least 0.03 mm proven, while `overlap` of the same pair finds 13.5456 mm^3 in common. A clearance that is proven must mean the bodies do not meet.
- **Reproducer:** `findings/J-018-clearance-clear-on-overlap/repro.json` (the Jig with its lid seat raised 0.5 mm, 374 steps, not minimal: 44 s on a busy machine; the last assertion is the `overlap`)
- **Workaround and impact:** The lid's fit is asserted with `overlap` as well as `clearance`.

## J-019: Distance and clearance assertions stop refining before they can decide their bound (see F-030)

- **Kind:** bug (proof weakness). **Jig:** gear-reducer, planetary-gearbox.
- **What happens, and what should:** A `distance` assertion between facing gear flanks with `min` 0.001 mm and `max` 0.15 mm finds 0.232 mm but proves only "at least 0.093 mm", so it reads `notProven`, while `measure.distance` proves 0.232 mm (with `max` alone the assertion fails, the builder reports). A `clearance` assertion `min` 0.06 mm on a planet that is 0.066 mm clear of the sun proves only 0.0417 mm and reads `notProven`; the same planet in another place proves 0.066 mm. The margins (0.08 mm and 0.006 mm) are far above the document's tolerance (1e-6 mm), so this is not the by-design case of a value within the tolerance: the refinement should go on until the bound is decided.
- **Reproducer:** `findings/J-019-assertion-stops-short/repro.json` (gear-reducer, 510 steps) and `clearance.json` (planetary-gearbox, 263 steps; the last `measure.clearance` lines show the bound depend on the planet, the assertion reads `notProven`)
- **Workaround and impact:** The gear-reducer's gaps are outputs (`variable.measure`, known only when proven to the tolerance) bounded both ways by assertions; the planetary gearbox measures `distance` from one flank family at a time and leaves the gears out of its overlap set.

## J-020: An assertion bound finer than the document's tolerance passes a value far outside it

- **Kind:** bug. **Jig:** music-box.
- **What happens, and what should:** At a document tolerance of 0.01 mm, a value of 0.005 mm passes `max` 0.000015 mm, and the result still shows the bound as given ("expected <= 0.000015 mm"); at the default tolerance it fails. A bound or `tol` finer than the tolerance should be refused or warned about, or the comparison made at the bound. It hid a real error in an early check of the Jig.
- **Reproducer:** `findings/J-020-assert-bound-below-tolerance/repro.json`, run with `--new '{"units":"mm","tolerance":0.01}'`
- **Workaround and impact:** The Jig's tight checks are counts, not bounds on lengths.

## J-021: `distance` from a body lying inside another body is the gap to its surface, not 0

- **Kind:** bug. **Jig:** solar-cooker.
- **What happens, and what should:** A 20 x 20 x 4 mm block wholly inside a 100 x 100 x 10 mm plate is at `distance` 3 mm from it, and so is its top face, although they share their whole volume. A body or face inside another should be at 0 (as `clearance` and `overlap` would say), or the summary should say that `distance` is between surfaces.
- **Reproducer:** `findings/J-021-distance-inside-body/repro.json`
- **Workaround and impact:** A petal set sunk into the hub ring is caught by the seam probe, measured from the petal bodies, which cross the ring's surface.

## J-022: A named set of bodies as `of` works for `extent` but `area` says it names nothing

- **Kind:** bug. **Jig:** polyhedron-net.
- **What happens, and what should:** `area` of `{"set": "Blocks"}` errors "`of` names nothing in the document as it is now"; `extent` of the same set measures it. Every measure should take the same `of`.
- **Reproducer:** `findings/J-022-area-of-set-names-nothing/repro.json`
- **Workaround and impact:** `{"kind": "body", "where": {"set": ...}}`.

## J-023: A face cut in two by a boolean counts as one face (see F-141)

- **Kind:** bug. **Jig:** geodesic-dome, joint-drawer.
- **What happens, and what should:** A slot cut across a block's top face leaves two faces, but a `count` of the plane faces at the top gives 1. A count should count the pieces; the shared persistent name is F-141's.
- **Reproducer:** `findings/J-023-split-face-counts-as-one/repro.json`
- **Workaround and impact:** The dome counts one face per bolt hole that the kerf splits; the drawer counts its tails by their baselines.

## J-024: A sketch arc's radius drifts below its value after re-solves, and `radius: {min}` has no tolerance

- **Kind:** bug. **Jig:** cubesat.
- **What happens, and what should:** Three arc corners of radius 1 mm, drawn with `sketch.path` from expressions, are counted with `"radius": {"min": "1 mm"}`. As the sketch is re-solved at other widths and back, the count reads 3, 3, 2, 2, 1, 3, while each radius prints as 1.0: it drifts a few ulps under 1 mm, and `{min, max}` are compared exactly where `eq` gets a tolerance. A given radius should stay put, and range bounds should be matched within the document's tolerance.
- **Reproducer:** `findings/J-024-radius-filter-no-tolerance/repro.json`
- **Workaround and impact:** The bound is `0.999 mm`, as the Jig's README says.

## J-025: `overlap` cannot decide plates that touch at zero clearance after `param.set` (see F-130)

- **Kind:** bug. **Jig:** welded-box.
- **What happens, and what should:** After a `param.set`, an `overlap` assertion between a web and a flange that touch errors "two points closer together than the tolerance can tell apart (at the edge of tolerance)". Touching plates should be told apart from overlapping ones.
- **Reproducer:** `findings/J-025-overlap-touching-plates/repro.json` (173 steps of the Jig)
- **Workaround and impact:** The overlap assertions are switched off at zero clearance.

## J-026: `overlap` errors on a feature switched off by `when` instead of skipping it

- **Kind:** bug. **Jig:** rack-cabinet, wooden-stair.
- **What happens, and what should:** An `overlap` assertion that names an inactive feature errors "`Option` has no body". As for `cut.list` (J-003), an inactive body should be skipped, so one assertion holds for every option.
- **Reproducer:** `findings/J-026-overlap-inactive-body/repro.json`
- **Workaround and impact:** The rack cabinet lists its bodies by a query by name; the stair has two assertions, one with `when`.

## J-027: The extent of a swept body is not proven to the tolerance, and a sweep's path length cannot be read (see F-117, F-122)

- **Kind:** bug (proof weakness). **Jig:** jansen-leg.
- **What happens, and what should:** The `extent` along x of a ribbon swept along a formula path is found as 82.0108 mm with at most 82.0109 mm, 1.4e-4 mm apart at a tolerance of 1e-6 mm, so the output is unknown. The sweep reports its path's length (82.94 mm), but no variable or output can read it.
- **Reproducer:** `findings/J-027-sweep-extent-unproven/repro.json`
- **Workaround and impact:** The step length is the search's, and an assertion holds the drawn path to it within 0.005 mm plus 50 millionths of the step (0.010 mm at the defaults).

## J-028: A feature switched off by `when` still takes its source body, so alternatives cannot share a source

- **Kind:** bug. **Jig:** tensegrity-table.
- **What happens, and what should:** Two `feature.transform` of one blank, each on for one choice, are refused: "the body of `Blank` already went into `Option one`", though `Option one` is inactive. An inactive feature should pass its source on, so alternatives by `when` can start from one body.
- **Reproducer:** `findings/J-028-when-alternatives-share-source/repro.json`
- **Workaround and impact:** One chain per veneer.

## J-029: A fillet cannot be added while the bodies it joins are switched off

- **Kind:** bug. **Jig:** gear-reducer.
- **What happens, and what should:** A `feature.fillet` between a plate and a lug that a `when` has switched off is refused: "not one body". A feature added while inactive should be accepted and checked when it comes on (compare J-005 and F-171).
- **Reproducer:** `findings/J-029-fillet-refused-while-inactive/repro.json`
- **Workaround and impact:** `build.json` builds with *Show* at *Closed* and sets *Open* just before publishing.

## J-030: Chamfering the rim of a rectangular opening is refused (see F-033)

- **Kind:** bug. **Jig:** tuned-chimes.
- **What happens, and what should:** A chamfer of the four top edges round a frame's rectangular opening is refused: "the chamfer does not end cleanly". The four edges close a loop, so every end meets another chamfered edge.
- **Reproducer:** `findings/J-030-chamfer-hole-rim/repro.json`
- **Workaround and impact:** The opening is left square-edged.

## J-031: A closed path of formula-curve pieces that meet end to end is refused for a sweep

- **Kind:** bug. **Jig:** jansen-leg.
- **What happens, and what should:** Three `sketch.curve` pieces of one smooth planar formula, sharing their end points and each fitted within 5e-7 mm, are refused as a sweep path: "the profile comes back 0.0000276 from where it started". A planar closed path of tangent pieces should sweep closed, the fits' small tangent errors absorbed.
- **Reproducer:** `findings/J-031-sweep-joined-curves-open/repro.json`
- **Workaround and impact:** The ribbon is four open sweeps, each starting where its tangent is level.

## J-032: Joining two sweeps that start from one section sketch fails at the shared end (see F-113)

- **Kind:** bug. **Jig:** wooden-stair.
- **What happens, and what should:** A sweep and a second sweep from the same section sketch, meeting at that section, cannot be joined: "an imprinted curve that does not fit the edges it should coincide with (at the edge of tolerance)". Two sweeps from the same section meet exactly and should join.
- **Reproducer:** `findings/J-032-sweep-join-shared-section/repro.json`
- **Workaround and impact:** The rail's returned ends are bodies of their own.

## J-033: A sketch arc given by a through-point loses its centre when it flips or flattens, and can leave a document unrecoverable (see F-112, F-113)

- **Kind:** bug. **Jig:** loudspeaker-box.
- **What happens, and what should:** An arc from (0, 0) to (40, 0) through (20, bulge) builds at a bulge of 6 mm, but a change to -3 mm (the same arc reversed) is refused as a conflicting constraint, as is 0.0001 mm (`flip.json`, `repro.json`). `dead.3dcraft`, saved after a long session of `param.set` and at its default values, has the centre of such an arc at (-1784331, 803236) and its constraint conflicting; `document.check` finds no driver body, and the same values build in a new document. The solve should follow the values, not the last solved state.
- **Reproducer:** `findings/J-033-sketch-arc-centre-escapes/` (`repro.json`, `flip.json`, `dead.3dcraft` with `--cmd sketch.inspect --params '{"sketch":"Driver cone profile"}'`)
- **Workaround and impact:** Arcs by centres written as formulas.

## J-034: A spline through points strays between them far more than a cubic interpolant

- **Kind:** bug. **Jig:** planetary-gearbox, gear-reducer.
- **What happens, and what should:** A live `sketch.spline` through eight points of an involute meets a ray at 15.16171 mm where the involute is at 15.14277 mm, about 0.009 mm off normal to the flank; a clamped cubic interpolant of the same points stays within 0.0006 mm (the builder's own calculation). It should be as close as a standard cubic interpolant, or its parametrisation and end conditions documented.
- **Reproducer:** `findings/J-034-spline-through-strays/repro.json`, run with `--new '{"units":"mm","tolerance":0.01}'`
- **Workaround and impact:** Three circular arcs through seven involute points per flank (planetary gearbox); arcs with formula centres (gear-reducer, whose five-point splines varied the mesh gap by -20 to +9 %).

## J-035: `feature.plate` refuses a valid section: "face 0 cannot be tessellated"

- **Kind:** bug. **Jig:** sliceform.
- **What happens, and what should:** One slice of a sliceform ball fails: "the plate cannot be meshed to see whether it passes through itself (face 0 cannot be tessellated: its loops do not bound a region)", though its outline exported is 13 arcs and 36 lines without a crossing, and other slice positions plate. It should mesh any valid plate, or say what in the face it cannot mesh.
- **Reproducer:** `findings/J-035-plate-cannot-be-meshed/repro.json` (the Jig at the failing point, 235 steps; run with `--new '{"units":"mm","tolerance":0.01}'`; slice 11 fails, so four count and area assertions fail)
- **Workaround and impact:** The ball's height is limited so that every slice reaches the flat foot, and the kerf range ends at 0.3 mm.

## J-036: `feature.plate` refuses some sections of a twisted loft: "the edge across a corner could not be traced" (see F-169)

- **Kind:** bug. **Jig:** sliceform.
- **What happens, and what should:** A loft through turning rounded squares, cut into sections and plated, fails on some slices: "the spline through them is still 0.084789 off"; turning every section 1 deg further plates it (`compare-turned.json`). A valid section should plate, if need be with a trace within the document's tolerance.
- **Reproducer:** `findings/J-036-plate-corner-not-traced/repro.json`, run with `--new '{"units":"mm","tolerance":0.01}'`
- **Workaround and impact:** The twisted tower, which failed at several points of its range, was left out of the Jig.

## J-037: A flat net reports facets that share only a vertex as touching, at one edge length

- **Kind:** bug. **Jig:** polyhedron-net.
- **What happens, and what should:** An icosahedron net with every crease at 0 deg is refused at an edge of 44.98181818 mm: two facets "touch or lie on each other". At 45 mm and at 44.98 mm it builds (`edge-45.json`). Facets that share a vertex in a flat net do not touch.
- **Reproducer:** `findings/J-037-flat-fold-touch-false-positive/repro.json`
- **Workaround and impact:** The range ends are rounded to whole millimetres, and the form rounds a typed value to its step.

## J-038: Glue tabs folded with a net are refused near closure

- **Kind:** bug (suspected). **Jig:** polyhedron-net.
- **What happens, and what should:** A cube net whose tabs fold 3 deg past their faces builds at 50 % and 90 % of the fold, but from 99 % on it is refused: a tab and a face "pass through each other", whether the tab is 3, 10 or 20 deg past its face. A tab folded inside the neighbouring face should not meet it; not proven independently here, hence suspected.
- **Reproducer:** `findings/J-038-tabs-refused-near-closure/repro.json` (change `fold_pct` and the tab's extra angle to compare)
- **Workaround and impact:** Tabs live on the flat pattern only.

## J-039: A cut by thirteen rows of text is refused for memory, after 28 s and 2.5 GB (see F-034)

- **Kind:** bug. **Jig:** tuned-chimes.
- **What happens, and what should:** Thirteen rows of about 55 characters cut 0.3 mm into a sheet are refused: "the freeform faces it meets need more memory for their indexes than one operation may take", after 28 s wall, 48 s of CPU and 2.5 GB. Cutting the rows one by one takes about a minute (the builder's measure). Text this size should cut in seconds.
- **Reproducer:** `findings/J-039-many-glyph-boolean/repro.json`
- **Workaround and impact:** The strips are one face each with the letters as holes.

## J-040: A face colour given on a feature is hidden when the body's colour is given on a later feature

- **Kind:** bug. **Jig:** dobsonian-telescope, cubesat.
- **What happens, and what should:** A tube's inner wall is coloured with `face.appearance` after its extrude; the tube is then cut by `feature.boolean` and turned by `feature.transform`, and `body.appearance` is given on the last feature: the wall renders in the body's colour. Without that `body.appearance` the wall keeps its colour through both features (`no-body-colour.json`), and with `body.appearance` on the extrude itself it keeps it too (`same-feature.json`). So the loss is not the boolean's but the later body colour's (the builders first read it as the boolean's). A face colour should win over a body colour wherever the body colour is given, or the command should warn.
- **Reproducer:** `findings/J-040-face-colour-hidden-by-body-colour/repro.json`, with `no-body-colour.json` and `same-feature.json` to compare (each renders a png)
- **Workaround and impact:** The face colour is given on the final feature's face names (`Tube:copy(0)/F2:side(e4)`), which a step inserted before them renumbers.

## J-041: A material pattern stays in the model's space when its body is turned (see F-083)

- **Kind:** bug. **Jig:** jansen-leg.
- **What happens, and what should:** A walnut bar turned 60 deg by `feature.transform` keeps the grain of the unturned bar, so it runs across the part (`grain.png`). A transform should carry the pattern's frame with the body.
- **Reproducer:** `findings/J-041-pattern-stays-when-turned/repro.json`
- **Workaround and impact:** None: the grain of the turning bars runs at a slant and drifts as the crank turns.

## J-042: `cut.list` prints a turned plate's thickness with rounding noise

- **Kind:** bug (cosmetic). **Jig:** solar-cooker.
- **What happens, and what should:** A 3 mm plate turned 40 deg is listed as 3.000000000000014 mm thick. Sizes should be rounded to the document's tolerance, so a shop's spreadsheet groups them.
- **Reproducer:** `findings/J-042-cut-list-thickness-noise/repro.json`
- **Workaround and impact:** None needed; cosmetic.

## J-043: A flat face or a plate cannot be exported as seen from a chosen side (see F-086)

- **Kind:** missing capability. **Jig:** sundial.
- **What happens, and what should:** For a plate that faces -y, `cut.export` takes the far face as the top and draws a hole at x = 20 of a 100 mm sheet where `file.export` of the front face's set draws it at x = 80: the mirror image, so the cut no longer lines up with an engraving on the front. `file.export` of a set of back faces draws each from its own outside, mirrored as well (`back-face.json`), so a plate whose front edges are chamfered has no true outline to export. Both should take a view direction or a face that is the part's front.
- **Reproducer:** `findings/J-043-flat-export-side/repro.json` and `back-face.json`; compare `face.svg` with `cut.svg` and `back.svg`
- **Workaround and impact:** The kerf is in the bodies (`feature.offsetProfile`), the cut sheet is a named set of front faces, and the plate's and gnomon's edges are left square for the maker to break by hand.

## J-044: A named set exports each face in its own place on the sheet, not where it lies (see F-142)

- **Kind:** missing capability. **Jig:** astrolabe, sundial, tuned-chimes, wooden-stair.
- **What happens, and what should:** `file.export` of a set of three marks on one plate lays them side by side, each from its own bounding box; a board's outline and its pocket's come out next to each other (`registered.json`). Faces that lie on one plane should keep their places, so an engraving or a pocket registers with its outline.
- **Reproducer:** `findings/J-044-set-export-keeps-places/repro.json` and `registered.json`
- **Workaround and impact:** The astrolabe and the sundial engrave one connected region (star letters stamped by hand, Arabic numerals and the equation of time left off), the chimes' strips carry their letters as holes, and the stair's layout is a sketch to select (J-007).

## J-045: A 3D export cannot be given a named set, and without `bodies` it writes hidden bodies too (see F-045, F-161)

- **Kind:** missing capability. **Jig:** gridfinity-baseplate, gridfinity-bin, drag-chain, joint-drawer, cycloidal-drive, cubesat, dobsonian-telescope, solar-cooker, tuned-chimes.
- **What happens, and what should:** `file.export` to 3MF, STL or STEP refuses `set` ("`set` is for a drawing ... the other formats hold every body"), and a list of `bodies` cannot follow a layout whose bodies change and refuses one that is off; without `bodies`, a body hidden by `feature.visible` is written too. A model should be able to name what a 3D export holds by a set, and to mark helper bodies as not parts.
- **Reproducer:** `findings/J-045-3d-export-set/repro.json` and `hidden-body.json`
- **Workaround and impact:** A *Show drawer* switch (baseplate), the parts moved into a print view with the helpers off (drag chain, cycloidal drive), gauges built only when shown (bin), body lists in the README (joint drawer, cubesat, solar cooker), and no 3D export at all (dobsonian, chimes).

## J-046: `cut.list` and `cut.export` cannot be limited to the parts to cut (see F-161, J-003)

- **Kind:** missing capability. **Jig:** orrery, loudspeaker-box.
- **What happens, and what should:** A 1/8 in rod is listed as a plate 60 mm thick and goes on the cut sheet; a hidden helper body is listed too (`hidden-body.json`). `bodies` takes only names, refuses one switched off (J-003), and refuses a named set ("`bodies` must be a list of bodies"). Both commands should take a set or a filter (a material, a thickness).
- **Reproducer:** `findings/J-046-cut-list-set/repro.json` and `hidden-body.json`
- **Workaround and impact:** The orrery chamfers the ends of every rod, tube, pillar and bush so that only its 1 mm brass parts are plates; the loudspeaker box gives its blanks as outputs.

## J-047: A chamfer cannot follow the rim of an extruded freeform outline (see F-075, F-158)

- **Kind:** missing capability. **Jig:** cam-disc, cycloidal-drive, planetary-gearbox, gear-reducer.
- **What happens, and what should:** A chamfer round the rim of a prism from a closed formula curve is refused "not yet where one of the faces changes" (the cycloidal disc's lobes give the same message); along a chain of spline tooth flanks it is refused because "each end of the edge has to be a corner of exactly three faces" (`tooth-chain.json`). A first-layer chamfer round a cam, a cycloidal disc or a gear is ordinary practice.
- **Reproducer:** `findings/J-047-chamfer-freeform-rim/repro.json` and `tooth-chain.json`
- **Workaround and impact:** The cam's and the disc's rims are left sharp (the disc's README asks for elephant-foot compensation); the planets' tip chamfer is a revolved cone cut on their print plate only (J-064); the reducer's teeth are deburred by the shop.

## J-048: Rounds where a cylindrical boss meets a drafted wall and a flange are refused (see F-099)

- **Kind:** missing capability. **Jig:** gear-reducer.
- **What happens, and what should:** Rounding the boss-to-wall, boss-to-flange and wall-to-flange edges together is refused: "fillets of freeform edges that meet in a vertex are not built yet"; one after another is refused too (the builder's report). A cast housing needs these rounds.
- **Reproducer:** `findings/J-048-rounds-on-drafted-wall/repro.json`
- **Workaround and impact:** The bosses are octagons; their junctions with the wall and the plug pad's are left sharp for the pattern maker.

## J-049: Hole rims of a varying count cannot be chamfered cheaply, and a countersunk plate is no plate to `cut.list` (see F-086, F-088)

- **Kind:** missing capability. **Jig:** welding-table.
- **What happens, and what should:** A chamfer takes named face pairs, not a query, so a changing number of hole rims cannot be chamfered. 384 countersinks subtracted as a pattern of cones cost 0.6 s of CPU to build against 0.04 s for the plain plate, 1.7 s against 0.6 s to open, and `cut.list` then refuses the plate ("a cone: a countersink or a chamfered hole, not square to the plate"). The reproducer as filed gave its sketch the plate's name; that is corrected.
- **Reproducer:** `findings/J-049-countersink-pattern/repro.json` and `without-countersinks.json`
- **Workaround and impact:** The holes stay as cut and are deburred by hand; the top's outer edge is a frustum.

## J-050: `feature.plate` takes one connected sheet only

- **Kind:** missing capability. **Jig:** sliceform.
- **What happens, and what should:** The sections of a solid by a patterned sheet are one body of separate faces; one `feature.plate` of them is refused: "the faces do not hang together across shared edges: plate each piece apart". It should plate each piece into a lump of its own, so a family of slices or layers is one feature whatever its count.
- **Reproducer:** `findings/J-050-plate-separate-faces/repro.json`
- **Workaround and impact:** 24 plates, each switched by `when` and named by a literal face.

## J-051: A body folded flat cannot be built on or moved

- **Kind:** missing capability. **Jig:** miura-ori.
- **What happens, and what should:** A `feature.transform` of a fold at 180 deg is refused: "no feature is built from its body (owed); fold it to just under 180 degrees".
- **Reproducer:** `findings/J-051-flat-folded-body-cannot-be-moved/repro.json`
- **Workaround and impact:** At *Fold* 100 the pack lies in the sketch's plane instead of being levelled and squared as at every other position.

## J-052: `feature.transform` cannot place a body by a target frame

- **Kind:** missing capability. **Jig:** geodesic-dome.
- **What happens, and what should:** A transform takes an axis and an angle. Placing a part along two given directions means writing the matrix-to-axis-angle conversion in variables (the reproducer does it for one block). A transform to a frame (origin, x and z directions) would do it in one step.
- **Reproducer:** `findings/J-052-transform-to-frame/repro.json` (builds; it shows the workaround)
- **Workaround and impact:** Each strut placement carries nine helper variables.

## J-053: `metallic`, `roughness` and `transmission` take numbers only, so a material look cannot follow a choice

- **Kind:** missing capability. **Jig:** keyboard-plate, gt2-pulley, rack-cabinet, sheet-metal-enclosure, dobsonian-telescope.
- **What happens, and what should:** `body.appearance` takes `color` from expressions but refuses `metallic` from one: "`metallic` must be a finite number, got a string"; the same holds for `roughness`, `transmission` and `material.preset`'s `color`. Compare J-009 and F-171.
- **Reproducer:** `findings/J-053-appearance-numbers-not-expressions/repro.json`
- **Workaround and impact:** The GT2 pulley's rim is two extrusions that differ in appearance, one on per process; the keyboard plate, rack cabinet and enclosure change colour and density only; the telescope gives the tube's colour by a `body.appearance` after the preset.

## J-054: An expression cannot define a function or a local name

- **Kind:** missing capability. **Jig:** sundial, jansen-leg, orrery.
- **What happens, and what should:** `hour_line(k) = ...` is refused ("invalid character '('"), and an expression has no `let`, so one formula applied to many inputs is written once per input, and a sub-expression used twice is written twice. With a pattern index (J-011) one formula would draw every instance.
- **Reproducer:** `findings/J-054-expression-functions/repro.json` (the last step is refused)
- **Workaround and impact:** The sundial writes its formulas per hour (204 of its 363 variables); the Jansen leg writes the foot's position 35 times, 2.6 to 3.8 kB each; the orrery gives each gear about 25 variables of the same formulas.

## J-055: No maximum, minimum or root of a formula over an interval

- **Kind:** missing capability. **Jig:** cam-disc, jansen-leg.
- **What happens, and what should:** A design limit is often the extreme of a formula (a cam's pressure angle, a linkage's stride). There is no `max` or root of a formula over an interval, and a body's `boxMax` on the plotted curve is an unknown output (found 30.47367 mm, at most 30.47506 mm; compare F-057).
- **Reproducer:** `findings/J-055-extremum-of-a-formula/repro.json`
- **Workaround and impact:** The cam samples its peaks in about 150 variables; the Jansen leg writes out parabolic and secant searches.

## J-056: No frequency or electrical units: Hz, V, A, W, h, mAh, Wh (see F-106)

- **Kind:** missing capability. **Jig:** loudspeaker-box, tuned-chimes, cubesat.
- **What happens, and what should:** `38 Hz` is refused (`frequency.json`), and so are `2.411 V`, `0.499 A`, `1.2 W`, `3200 mA * 1 h` and `11.52 W * 1 h`, while `J` and `s` are known. They should be units with their dimensions (W = J/s, Hz = 1/s), in expressions and as an output's `unit`.
- **Reproducer:** `findings/J-056-frequency-electrical-units/repro.json` (with `--keep-going`) and `frequency.json`
- **Workaround and impact:** Frequencies, cents, power and energy are plain numbers named in their labels; formulas use `1/(1 s)`.

## J-057: `variable.measure` takes no `when`

- **Kind:** missing capability. **Jig:** planetary-gearbox, cubesat.
- **What happens, and what should:** "unknown parameter `when`". An output measured only in one view or option is measured, or unknown, in every other.
- **Reproducer:** `findings/J-057-variable-measure-no-when/repro.json`
- **Workaround and impact:** The planetary gearbox asserts its measured gaps; the CubeSat measures on queries that always hold a body.

## J-058: An output used only by assertions cannot be kept off the form

- **Kind:** missing capability. **Jig:** solar-cooker.
- **What happens, and what should:** An assertion that combines measures needs each as an output, and every output is listed with the maker's results. In the solar cooker 45 of 70 outputs were such helpers before review. An output should be markable as internal.
- **Reproducer:** `findings/J-058-check-outputs-on-form/repro.json`
- **Workaround and impact:** The checks measure inside the assertions wherever one measure proves the point, so its 32 outputs are all for the maker.

## J-059: An output cannot have a description

- **Kind:** missing capability. **Jig:** rack-cabinet.
- **What happens, and what should:** `variable.output` takes a label but refuses `description`, so a caveat about a result (who must check a wall anchor) cannot sit with it on the form.
- **Reproducer:** `findings/J-059-output-no-description/repro.json`
- **Workaround and impact:** The outputs' labels and the descriptions of *Mounting* and *Gear mass* carry it.

## J-060: Grooves that cross each other cost 20 times grooves that do not

- **Kind:** performance. **Jig:** astrolabe.
- **What happens, and what should:** Two families of 32 circles cut 0.3 mm into a disc: each family alone takes 0.11 to 0.15 s of CPU (`one-family.json`), both 2.8 s; with a line of text cut first, 7.3 s (`repro-text.json`).
- **Reproducer:** `findings/J-060-crossing-grooves-cost/repro.json`, `one-family.json`, `repro-text.json`
- **Workaround and impact:** The default shows the lines as thin bodies 0.02 mm proud of the plate; *Engraving in the model* cuts the grooves the engraving export needs.

## J-061: Subtracting one many-lump tool from each of many targets is twice as slow as cutters per target

- **Kind:** performance. **Jig:** gridfinity-baseplate.
- **What happens, and what should:** 196 cells in 16 pieces: one 196-lump cutter for every piece takes 4.9 s wall and 8.1 s of CPU to build, a cutter per piece of only its own cells 2.2 s and 3.9 s (busy machine; the builder measured 1.9 s against 0.66 s). Lumps that do not reach a target should cost next to nothing.
- **Reproducer:** `findings/J-061-subtract-many-lump-tool/repro.json` and `repro-small-tools.json`
- **Workaround and impact:** Every piece is cut by its own pattern.

## J-062: A circular pattern of pieces that meet edge to edge is joined at twice the cost, with no way to keep them apart (see F-125)

- **Kind:** performance. **Jig:** solar-cooker.
- **What happens, and what should:** 24 parabolic petals whose cut faces lie on their neighbours' are joined into one shell: 2.0 to 2.6 s wall and 6.3 to 7.3 s of CPU to open, against 1.0 to 1.2 s and 2.6 to 3.2 s for the same petals as two interleaved patterns of 12 (`interleaved.json`; busy machine). A pattern should be able to keep its instances as separate pieces (petals, slats, fins made apart), or test shared faces cheaply.
- **Reproducer:** `findings/J-062-circular-pattern-touching-cost/repro.json` and `interleaved.json`, run with `--new '{"units":"mm","tolerance":0.01}' --out`, then time `craft3d-cli info`
- **Workaround and impact:** Every other petal is one pattern and the petals between a second, so the petal count is even.

## J-063: A wrapped profile with slanted edges is about 50 times heavier than a rectangular one

- **Kind:** performance. **Jig:** music-box.
- **What happens, and what should:** 60 diamond pins wrapped onto a drum and joined take 21.6 s wall, 26.8 s of CPU and 2.5 GB; the same pins as rectangles 0.47 s and 30 MB (`compare-rect.json`).
- **Reproducer:** `findings/J-063-wrap-oblique-edges-heavy/repro.json` and `compare-rect.json`
- **Workaround and impact:** The pins are rectangles; their undersides print as short bridges rather than 45 deg points.

## J-064: A revolved cone cut across spline gear teeth costs four times the gear

- **Kind:** performance. **Jig:** planetary-gearbox.
- **What happens, and what should:** A 0.4 mm tip chamfer cut as a revolved cone across a spline-toothed sun takes 2.2 s wall and 2.7 s of CPU against 0.5 s without it (`without-cut.json`).
- **Reproducer:** `findings/J-064-cone-cut-across-teeth-cost/repro.json` and `without-cut.json`
- **Workaround and impact:** The flanks are arcs, and the cone cut is built on the planets' print plate only.

## J-065: Measuring a flat gear costs about 1.4 ms of CPU per tooth, far more than building it

- **Kind:** performance. **Jig:** orrery, planetary-gearbox.
- **What happens, and what should:** One 120-tooth gear extruded 1 mm builds in 0.01 s of CPU (`without-assertion.json`); `craft3d-cli info` of it, which measures volume, area and centroid, takes 0.17 s, and a `volume` assertion on it costs about 0.16 s at every regeneration. The body is a prism of lines and arcs, whose properties have a closed form. In the orrery about 5 of its 8 to 10 s of CPU to open is measuring 35 gears, and a `distance` between two gear faces about 0.6 s each.
- **Reproducer:** `findings/J-065-gear-measure-cost/repro.json` and `without-assertion.json` (save with `--out`, then time `info`)
- **Workaround and impact:** The orrery keeps its closed-form area check to two gears, shows engagement by an extent along z, has no mass output and fewer teeth by default; the planetary gearbox draws its flanks as arcs.

## J-066: Formula curves are fitted far below the document's tolerance (see F-010)

- **Kind:** performance. **Jig:** gear-reducer, planetary-gearbox, solar-cooker.
- **What happens, and what should:** An involute `sketch.curve` gets 35 control points (deviation 5e-8 mm) at tolerances of 1e-6, 0.001 and 0.01 mm alike (`involute.json`); a parabola, a quadratic that 3 control points draw exactly, gets 35 at 0.01 mm (deviation 1.2e-6 mm). Twelve strips from such parabolas cost 0.91 s of CPU to open against 0.16 s from exact quadratic splines (the builder's measure). A polynomial formula should give the exact B-spline of its degree, and the fit stop at the tolerance.
- **Reproducer:** `findings/J-066-formula-curve-fit-size/repro.json` (run with `--new '{"units":"mm","tolerance":0.01}'`) and `involute.json`
- **Workaround and impact:** The gears' flanks are arcs; the solar cooker's petals are exact quadratic splines with control points as formulas.

## J-067: The flat-fold layer-order search gives up on larger Miura grids

- **Kind:** performance. **Jig:** miura-ori.
- **What happens, and what should:** `flatFoldable` of a Miura pattern errors "the order of the layers was not decided within the work allowed (140 facets on one another in one place)", in 1.5 s. A regular pattern's layer order should be found without a search, or the allowance be a parameter.
- **Reproducer:** `findings/J-067-flat-fold-search-miura/repro.json`
- **Workaround and impact:** The Jig keeps to 14 x 16 cells, and to 70 deg above 144 cells.

## J-068: A document with text carries the whole font (see F-037)

- **Kind:** performance (file size). **Jig:** astrolabe, tuned-chimes, sundial.
- **What happens, and what should:** A plate engraved with two letters saves as 347 KB, of which 331 784 bytes are the bundled font. The astrolabe's font is 332 KB of 977 KB and the chimes' file is 978 kB against a budget of 1 MB. A bundled font should be referred to, or only the glyphs used stored.
- **Reproducer:** `findings/J-068-text-embeds-font/repro.json` (save with `--out` and list the zip)
- **Workaround and impact:** The astrolabe carries one set of numerals; the sundial draws its numerals as polygons.

## J-069: Expressions are capped at different sizes in different places

- **Kind:** agent friction. **Jig:** rc-wing, music-box.
- **What happens, and what should:** A `sketch.line` or `sketch.point` coordinate is refused above 1000 characters, while `sketch.curve` and variables take longer ones; an assertion is refused when what it measures exceeds 16 384 bytes (`measure-cap.json`, a count over 200 boxes). Each cap should be stated with the command, and one size should hold everywhere.
- **Reproducer:** `findings/J-069-expression-size-caps/repro.json` and `measure-cap.json`
- **Workaround and impact:** The wing writes its long coordinates through variables; the music box splits its pin check into three assertions.

## J-070: A curvature assertion's `at` takes plain numbers only (see F-094)

- **Kind:** agent friction. **Jig:** dobsonian-telescope.
- **What happens, and what should:** `at` given as expressions is refused: "`at` must be [x, y, z]"; plain numbers work. Every other point in an assertion takes expressions, and a point on a moving part moves with the parameters.
- **Reproducer:** `findings/J-070-curvature-at-no-expressions/repro.json`
- **Workaround and impact:** The mirror's curvature is asserted on an unmoved construction copy at the origin.

## J-071: `extent`, `boxMin` and `boxMax` measure bodies only, not faces

- **Kind:** missing capability. **Jig:** cubesat.
- **What happens, and what should:** `measure: "extent"` with a face query as `of` (the cone of a countersink) is refused: "extent is of bodies; the subject names faces of `Countersunk`". The size of a face's box along an axis is the natural way to read a feature's size off the model: a countersink's diameter and depth, a pocket's length, a slot's width, a flange's height. Distances between faces cover some of these, but not the size of a single face.
- **Reproducer:** `findings/J-071-extent-of-faces/repro.json` (a plate with a Ø2.2 hole countersunk to Ø4.4; both assertions should pass with 4.4 mm and 1.1 mm, both are refused)
- **Workaround and impact:** The rail screws' heads (a 90° cone at the theoretical Ø4.4 of ISO 7046-1) are drawn flush with the rail face, and `overlap` proves they do not cut into the rail, which proves more than two extents would; the gap matters where no part can be drawn in the hole.
