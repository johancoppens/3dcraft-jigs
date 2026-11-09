# Form test

I run a paper-engineering workshop. On Saturday everyone folds a Miura-ori from one A3 sheet of 200 g/m² card, lying on
its long side, with 8 mm of the sheet left free at the edge. I want 9 rows of 12 columns of parallelograms with a 65
degree corner. I would like to see it half folded on the screen first. Then I need the file for our cutting plotter to
score the folds, with the mountains and the valleys kept apart so the plotter can do them on different passes, and I want to
know how big each cell is, how many metres of creases there are of each kind, and how thick the pack will be when it is
folded flat, to see whether it fits in the participants' envelopes.

A friend wants the same pattern as 3 mm plywood panels glued on a linen hinge, with 8 mm of linen between the panels.
How far will that fold, and what does he cut on his laser? And one participant asks whether she can fold 20 rows on an
A5 sheet.

## Acceptance

- A3 landscape, margin 8 mm, 9 rows, 12 columns, 65 degrees, 200 g/m². Half folded (Fold 50): the zigzag creases stand at
  90 degrees and the straight ones at 45.8. Cell width 32.45 mm, row height 31.22 mm, zigzag edge 34.45 mm. The fold is
  317.9 × 258.8 mm and 20.8 mm deep at that point.
- Mountain creases 3.418 m, valley creases 3.108 m. Folded flat (Fold 100) the pack is 36 layers at its thickest spot, 9 mm
  thick at 200 g/m², 199 × 29.4 mm. All paper assertions pass: facets 108, Kawasaki and Maekawa 0 failures, flat-foldable
  true, folded depth, length and width in closed form to 0.001 mm.
- Export: the crease pattern of *Miura-ori* as DXF or SVG holds the outline on the layer `boundary`, 102 mountain lines on
  the layer `mountain` and 93 valley lines on the layer `valley`, at true size, 404 × 281 mm.
- Thick panels: panel thickness 3 mm and gap 8 mm: at Fold 100 the straight creases reach 54.8 degrees and the zigzag ones
  101.7 degrees, and the panels stop with 0.4 mm of gap left at the tightest crease (all thick-panel assertions pass).
  The panels export as the set *Panels cut sheet*, 108 outlines, drawn half a laser kerf larger next to the creases (0.15 mm kerf by
  default, adjustable on the form).
- Refusal: 20 rows on A5 cannot be set: the rows stop at 13 (A5 on its long side with this margin keeps cells of at least 10 mm).
  The form clamps it, or `param.set` refuses it with the range.
