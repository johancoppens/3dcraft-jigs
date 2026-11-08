# 3DCraft feedback from the Jigs

What building the Jigs found in 3DCraft: bugs, missing capabilities, performance and agent friction (AGENTS.md §7).
Collected here, never fixed from this repository. Ids are `J-nnn`; an entry that the examples already reported cites its
`F-nnn` in `~/code/3dcraft-examples/3DCRAFT-FEEDBACK.md`. Each entry was reproduced at the pin, 3DCraft `45233bdc`, unless
it says otherwise. A reproducer runs with `craft3d-cli run --new '{"units":"mm"}' --script findings/J-nnn-<slug>/repro.json`.

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

## J-001: a Jig's thumbnail cannot be given a view or a look

- **Kind:** missing capability. **Jig:** all.
- **What happens:** `jig.export {path}` writes `thumb.png` "as `file.save` draws it": one view, one flat look.
- **What should happen:** the maker of any Jig can choose the view and the look of its picture, the same way `view.render`
  does, since a file manager or a gallery shows that picture first.
- **Impact:** cosmetic. **Workaround:** `tools/jigs.py render` writes `dist/thumbs/<id>.png` for the gallery.

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
- **What happens, and what should:** `pattern.colors` and `body.appearance` `color` take literals, so a veneer cannot follow a choice of wood.
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
