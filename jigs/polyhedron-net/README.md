# Platonic net to fold and glue

Pick one of the five Platonic solids, drag one slider and watch its classic net rise off the sheet and fold shut. The
same model tells you how big the solid can be on your paper, and hands you the pattern with glue tabs to print, cut,
fold and glue: a maths lesson you can hold.

![An icosahedron net two thirds folded, rising from its printed pattern with glue tabs](preview.png)

## What it shows

- `feature.fold` driven by one parameter: every crease of the net folds by the same angle,
  `min(fold_percent, 99.99) / 100 * closing_angle`, so one slider closes the whole solid.
- A choice that changes the structure: `solid` (`table.set`, `variable.publish` with `choicesFrom`) picks a row of the
  table `solids` (faces, edges, vertices, Schläfli symbol, closing angle, volume and area factors, net size, tabs), and
  five folds with `when` give five different nets, 3 to 19 creases each.
- The nets are data: one table per solid (`net_cube`, ...) holds every outline point in edge lengths, and each glue
  tab's two outer points as a direction along the hinge and a normal, so one formula draws every row:
  `edge_length * net_cube[7].x + tab_shoulder * net_cube[7].ux + tab_depth * net_cube[7].nx`.
- Ranges that follow the choices: the edge length's maximum is a formula of the solid and the sheet, the tab width's
  maximum a formula of the edge and the room left on the sheet. An edge that does not fit cannot be entered.
- Colours from a theorem: each solid is coloured with the fewest colours that keep neighbouring faces different (4, 3,
  2, 4 and 3), `face.appearance` per family.
- A second fold per solid is the flat print pattern: the net with its glue tabs, all creases mountain and at 0 degrees,
  lying under the folding model as the sheet it came from, tabs in their own colour. It exists to be exported
  (`file.export` with `fold`).

A static model shows one net at one angle. This one is five solids at any size that fits your sheet, open or closed,
and always ready to print.

## The real thing

**The solids.** The five regular convex polyhedra, Schläfli symbols {3,3}, {4,3}, {3,4}, {5,3} and {3,5}. Closing
angles, volumes and areas are the standard closed forms (H.S.M. Coxeter, *Regular Polytopes*): for example the
dodecahedron's volume is (15 + 7√5)/4 a³. The closing angle (180° less the dihedral angle) is held in the table and
checked against the Schläfli formula, 180° − 2 asin(cos(180°/q) / sin(180°/p)).

**The nets.** The ones a teacher knows: the tetrahedron as one big triangle, the cube as the Latin cross, the
octahedron as a symmetric band of triangles, the dodecahedron as two flowers of six pentagons joined at a petal, the
icosahedron as the belt of ten triangles with five teeth on each side. A net has F − 1 joints and E − F + 1 seams.

**The paper.** Sheet sizes are ISO 216 (A5, A4, A3) and US Letter. Paper is sold by grammage (ISO 536, g/m²); its
thickness is not on the pack, so the Jig assumes a bulk of 1.25 cm³/g, typical of uncoated paper (80 g/m² is 0.10 mm,
160 g/m² is 0.20 mm). That is an assumption, shown in the outputs. The pattern stays 10 mm inside the sheet, a safe
margin for ordinary printers.

**The glue tabs.** One tab on each seam, on whichever of its two edges has room. A tab is a trapezoid whose shoulders
leave the hinge at 30 degrees: this is the Jig's own choice, not a standard, for two reasons. The notch between two
petals of the dodecahedron's flowers is only 36 degrees wide, and a steeper shoulder would not fit in it; the tab left in that notch is a thin sliver, fiddly for a child. And where
two tabs tuck under a triangle's 60-degree corner they share it exactly, each staying on its own side of the bisector.
Each shoulder is set back one paper thickness more, so heavy card does not ride up at the corners. A tab is at most a
quarter of the edge, at most 20 mm, and at least 5 mm, a width glue and fingers can manage.

**Making it.** Print the pattern at 100 % (no "fit to page") and in landscape: the pattern lies along the sheet's long
side and the file is only as big as the pattern, so portrait cuts off part of it (the default icosahedron is 247.5 mm
long, wider than a portrait A4). Cut on the solid outline. Score heavy card with a blunt
point along the fold lines, then fold away from you on every dash-dot line, tabs included. Every crease is a mountain, so the printed side, with its
fold lines, ends up on the outside of the finished solid. Glue each tab under the edge
it meets, working round the solid and leaving one face for last: press its tabs through the remaining open edge.

**The picture.** The shadows under the rising net show faint streaks, a renderer artefact (`look.light` is set to the
direction that gave the fewest of them).

**Limits of the model.** The folding net is a sheet with no thickness, and it has no tabs: tabs folded with the faces
are refused by 3DCraft near closure ([finding](../../findings/J-038-tabs-refused-near-closure/repro.json)), so the tabs
live on the flat pattern. The form's 100 % folds to 99.99 % of the closing angle (a 40 mm cube then stands
0.013 mm taller than it should), because at exactly 100 % the free edges meet and 3DCraft refuses the fold
([finding](../../findings/J-014-fold-closed-loop/repro.json)).

## Parameters

| Group | Parameter | Range | What it changes |
|---|---|---|---|
| The solid | Solid | five solids | The whole net, its creases, seams, tabs, colours and outputs |
| The solid | Edge length | 20 mm up to what fits the sheet, whole mm | The size of everything; see the table below |
| The solid | Fold it shut | 0 to 100 % | The folded model only: 0 is the flat net, 100 the closed solid |
| Paper and glue | Sheet of paper | A5, A4, A3, US Letter | The limit on the edge and the tabs; the pattern lies along the sheet's long side |
| Paper and glue | Paper weight | 80 to 300 g/m² | Paper thickness (so the tab's corner set-back) and the mass |
| Paper and glue | Glue tab width | 5 mm up to a quarter of the edge, 20 mm at most, and what the sheet still has room for | Every tab |

Largest edge in mm (whole mm, with 6 mm of tab room kept each side):

| | A5 | A4 | A3 | US Letter |
|---|---|---|---|---|
| Tetrahedron | 66 | 102 | 152 | 106 |
| Cube | 38 | 59 | 88 | 61 |
| Octahedron | 46 | 71 | 106 | 73 |
| Dodecahedron | 21 | 32 | 47 | 30 |
| Icosahedron | 32 | 48 | 70 | 44 |

Outputs: the finished solid's surface, volume and the angle between its faces; the pattern's length, width and area;
the number of glue tabs; the paper's thickness and mass; the longest edge on this sheet and the paper left over at each
side.

## Checks

The nine assertions:

- **Euler**: vertices − edges + faces = 2, from the table's row.
- **Closing angle**: the table's value against the Schläfli formula (an independent closed form).
- **Net area** (`area`, measured on the folded sheet) against the closed form, at every fold.
- **Pattern area** (measured) against the faces plus the tabs in closed form, tabs being trapezoids of the depth and the
  shoulder of the form.
- **Facets** (`count`): the net and the pattern together have 2 × faces + tabs facets.
- **Tab end** at least 1 mm wide. The ranges exclude a failure (smallest 1.9 mm, at 20 mm edge, 5 mm tab and 300 g/m²).
- **Pattern fits** the sheet's length and width inside the margins (two measured extents). The ranges exclude a failure;
  the measure guards the model.
- **Closure** (`cavity`, measured): the closed net encloses the closed-form volume within 0.1 % (largest error found
  +0.034 %, the tetrahedron). Active at 100 % only: `cavity` at other folds is not a volume, and an assertion cannot be
  measured at another value of a parameter (`F-059`).

`tools/jigs.py check` runs `check-range`: 104 points (the defaults, 64 corners, every choice, 32 random points), all
passing, none unproven. Beyond the range check:

- every combination of whole-millimetre edge and tab for all five solids (on A3, whose list of whole-mm edges contains
  every other sheet's) at 80, 190 and 300 g/m², and folds 0, 1, 50, 99 and 100 at every edge, were set and passed:
  11 881 points. The tab limits of the smaller sheets and the other paper weights are covered only by `check-range`
  and by a hand-picked grid of 920 points at each sheet's largest edges and tabs, all passing;
- every whole percent of fold from 0 to 100, for all five solids at their smallest and largest A4 edge, closes without
  a collision (1 010 points);
- too big an edge or tab is refused with its range by `param.set`, tried by hand.

Why whole millimetres: the form's values are whole millimetres because at one non-integer edge (44.9818… mm, the
icosahedron on US Letter before the ranges were rounded) 3DCraft reports facets that merely share a vertex as touching
([finding](../../findings/J-037-flat-fold-touch-false-positive/repro.json)). The form rounds a value typed between two steps to the
nearest step; only `param.set` refuses it.

Not checked: that real paper folds this cleanly; the glue; the bulk assumption against a particular paper.

## Export

**File › Export…**, then **Crease pattern of [solid] print pattern**, as SVG to print or DXF for a plotter or cutter:
the cutting outline on the layer `boundary` and every fold line, faces and tabs alike, on the layer `mountain` (red,
dash-dot, seen from the printed side). The file holds the exact size: print at 100 %. In the export dialog SVG lines
come out as 0.01 mm hairlines, too thin for most printers (see Platform notes): thicken them in a viewer, or from the
command line give
`file.export` `"stroke": 0.3` as the checks of this Jig do. **Crease pattern of [solid] net** is the plain net with no
tabs, for taping edge to edge; its folds are marked valley, as the model folds them towards you.

Only the pattern of the solid chosen in the form is offered.

## Files

`build.json` (the source), `meta.json`, `formtest.md`, `preview.png`, and `dist/polyhedron-net.3dcraftjig`,
`dist/thumbs/polyhedron-net.png` from the tool.

## Rebuild

```sh
tools/jigs.py build polyhedron-net
tools/jigs.py render polyhedron-net
tools/jigs.py check polyhedron-net
```

## Difficulty

5/10: folds driven by a parameter, a per-solid net table with hand-derived coordinates and tab hinges, topology by
`when`, and cavity closure.

## Platform notes

Entries in `3DCRAFT-FEEDBACK.md` (J-014, J-015, J-022, J-037, J-038), each with a reproducer in `findings/` unless noted:

- A fold whose free edges meet exactly at the closed state is refused ("touch or lie on each other"): a closed net is a
  legitimate state ([repro](../../findings/J-014-fold-closed-loop/repro.json)). Workaround: the crease angle is capped
  at 99.99 % of the closing angle.
- Facets that share a vertex are reported as touching in a flat fold at one particular edge length, a false positive
  ([repro](../../findings/J-037-flat-fold-touch-false-positive/repro.json)). Workaround: range ends rounded to whole
  millimetres.
- Glue tabs folded with the faces are refused near closure, even a few degrees past the neighbouring face
  ([repro](../../findings/J-038-tabs-refused-near-closure/repro.json)). Workaround: tabs on the flat pattern only.
- `cavity` of an open sheet returns a number that is not a volume (136 300 mm³ for a half-folded 64 000 mm³ cube) rather
  than saying it is not closed ([repro](../../findings/J-015-cavity-open-sheet/repro.json)). Workaround: the closure
  assertion is on only at 100 %.
- A set of bodies used as `of: {"set": ...}` works for `extent` but `area` says it names nothing
  ([repro](../../findings/J-022-area-of-set-names-nothing/repro.json)). Workaround: `{"kind": "body", "where": {"set": ...}}`.
- The export dialog has no line width for an SVG crease pattern, so it is written as hairlines (no reproducer: the
  dialog).
- Already filed: `F-105` (`distance` refuses sheets, so a seam gap cannot be measured; the closure is proven by
  `cavity`), `F-171` (`face.appearance` refuses a feature switched off by `when`; the script sets `solid` to each value
  while colouring that solid's faces), `F-059` (an assertion is measured only at the current values).
