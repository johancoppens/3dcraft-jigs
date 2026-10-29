# Miura-ori fold panel

A Miura-ori panel: a sheet of parallelograms, 3 to 14 rows by 3 to 16 columns, that folds in and out in one
motion, of paper or of **thick panels** (card or plywood on a fabric hinge). The Jig shows the panel at any
angle from flat to folded flat (paper) or to where the panels meet (thick), and exports the crease pattern to
print and score, or to laser-score. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Rows | Pattern | 6 | 3 to 14, and no more than leave cells of 10 mm on the paper |
| Columns | Pattern | 8 | 3 to 16, and no more than leave cells of 10 mm on the paper (allowing for a zigzag offset of one cell height) |
| Cell width | Pattern | 30 mm | 10 mm to what fits the paper inside the margin, step 0.5 mm |
| Cell height | Pattern | 28 mm | 10 mm to what fits the paper inside the margin, step 0.5 mm |
| Parallelogram angle | Pattern | 70 deg | 45 to 80 deg up to 12 x 12 cells, to 65 deg on a larger grid, step 1 deg |
| Fold | Fold | 90 deg | 0 (flat) to 180 deg (folded flat); with thick panels to the last whole degree below where they meet, step 1 deg |
| Thick panels | Panels | off | on: card or plywood panels on a fabric hinge instead of paper |
| Panel thickness | Panels | 1.5 mm | 0.3 to 6 mm, step 0.1 mm |
| Hinge clearance | Panels | 1.5 mm | 0.3 mm to a quarter of the cell's narrower width (at most 10 mm), step 0.1 mm |
| Panels on the front | Panels | off | on: the panels on the printed side |
| Paper | Paper | A4 | A4, A3, Letter (table `sheets`) |
| Landscape | Paper | on | on / off |
| Margin | Paper | 10 mm | 0 to 30 mm, step 1 mm |

The maximum cell sizes follow the paper, the orientation, the margin, the rows and columns and the angle: the
flat pattern is `columns x cell width + d` wide and `rows x cell height` high, with `d = cell height / tan(angle)`
the zigzag's offset.

Why these limits: the fold itself is no longer the limit. 3DCraft's sparse solve folds 27 x 38 cells (some
2000 crease angles) in under two seconds. What limits the grid is the **order of the layers** when the panel is
folded flat. 3DCraft searches for it within a work allowance, because flat-foldability is NP-hard, and it says
so rather than guess. The Fold at 180 deg and the `flatFoldable` assertion both need that order. Measured at
3DCraft 0dc5efb6, every grid up to 12 x 12 is decided at angles up to 80 deg, and every grid up to 14 rows of 16
columns at angles up to 65 deg. Past that, tall, narrow cells at high angles run out (12 x 14 cells of 10 x 33 mm
at 70 deg stack 144 facets in one place; 12 x 16 cells of 10 x 24.5 mm at 80 deg, 192; 27 x 38 cells even at
50 deg). So the grid stops at 14 x 16, and the angle's range drops to 65 deg once either count passes 12. The columns' range allows for the
largest zigzag offset (`d = b` at 45 deg) whatever the angle, so the two ranges do not depend on each other.

## How it folds

Every point of the pattern is a sketch point held by expressions of the cell width `a`, the cell height `b`,
`d = b / tan(angle)`, the rows and the columns: grid point `(i, j)` lies at `(i a + mod(j, 2) d, j b)`. The
straight creases run across at every row (`y = j b`), the zigzag creases up the columns. Seen from the printed
side:

- **zigzag creases**: odd columns mountains, even columns valleys, each along its whole length;
- **straight creases**: alternately mountain and valley along each line, shifted by one cell from one line to
  the next (segment `i` of line `j` is a valley when `i + j` is odd).

The grid follows Rows and Columns through sketch patterns: each kind of crease piece (a zigzag piece leaning
right or left, in an odd or an even column; a straight piece in an odd or an even row and cell) is one seed line
repeated every two cells and every two rows, with counts that are formulas of the rows and columns, and the
fold takes each seed with all its copies as creases (`e33[*]`). The outline's zigzag edges are patterns too.

At every inside vertex three creases are of one kind and one of the other. The panel is folded rigidly by
3DCraft's own fold solver. The straight valleys of the odd rows' even cells (one seed and its copies) have the
**Fold** angle; 3DCraft solves every other crease from them: the other straight creases by the same angle, the
zigzag creases by `2 atan(tan(fold / 2) / cos(angle))`, which is faster (at the defaults, 90 deg, the zigzags are
at 142.2 deg). A Miura-ori has one degree of freedom, so one driven crease would do in principle, and every
straight crease folds by the same angle, so driving these together is consistent. But with one crease driven,
3DCraft calls some long, low panels (3 rows of 8 to 12 columns) ambiguous. That is filed with 3DCraft as a
repro.

At **180 deg** the panel is folded flat: every facet lies in the sketch's plane, in an order of layers 3DCraft
works out from the crease kinds (the picture lifts each layer a little so you can see them).

The facet that stays in place is a cell near the middle: column `2 floor(columns / 4) + 1` (odd) of row
`2 floor(rows / 4)` (even). A folded Miura-ori leans: each facet tilts by `theta = atan(tan(fold / 2) /
cos(angle))` (half the zigzag creases' fold angle) about its zigzag edge, so below 180 deg the Jig turns the
folded sheet back by `theta` about that edge's direction (`feature.transform`, the body `Panel`). The panel then
lies level, its mean plane (the plane of each zigzag crease line) on `z = 0`, and it shrinks in place as it
folds. Folded flat, the panel already lies in its plane, and 3DCraft does not build on a flat-folded body, so the
transform is off at 180 deg (`when: fold < 180 deg`).

## Thick panels

Card, grey board or plywood does not fold like paper. Turn on **Thick panels** and every facet becomes a rigid
panel of **Panel thickness**, set back by the **Hinge clearance** from every crease. The panels are glued on
the back (or the front) of a fabric or tape membrane that is the hinge. This is 3DCraft's `feature.fold` with
`panels`: the membrane model of thick origami (Zirbel et al. 2013). The panels fold exactly as the paper
does, the hinges on the membrane's plane; only the room between the panels is new.

Between two panels a crease folding away from them opens. One folding towards them closes the gap and the
panels meet when the crease reaches `2 atan(clearance / thickness)`. In a Miura-ori the zigzag creases fold
fastest, by `2 atan(tan(fold / 2) / cos(angle))`, and half of them fold towards the panels on either side. So
the panels meet when

    fold = 2 atan(cos(angle) x clearance / thickness)

and the Fold slider stops at the last whole degree below that. With 1.5 mm panels and 1.5 mm clearance at
70 deg the limit is 37.8 deg. At 45 deg it is 70.5 deg. 3 mm plywood with a 3 mm clearance (6 mm of bare fabric
between two panels) behaves the same. More clearance, thinner panels or a lower angle let it fold further.
3DCraft checks every pair of panels as solids and refuses a fold where two meet. The limit above agrees with
it: at 45, 70 and 80 deg the fold passes 0.05 deg below the closed form and is refused 0.05 deg above it, the
first meeting being two panels beside a zigzag crease.

Thick panels cannot fold flat with the hinges on the membrane: they would pass through each other. The
methods that fold thick panels flat move the hinges off the sheet (offset panels, Edmondson et al. 2014) or
taper the panels' edges (Tachi 2011). 3DCraft does not build them yet, so a thick Miura-ori folds only part of
the way. To cut the panels, export the crease pattern (below) and cut each cell inside its creases by the
clearance (a laser's kerf takes part of it).

## Checked by assertions

Paper (Thick panels off):

- `every cell is in the folded panel (area rows x cols x a x b)`: the folded panel's area is `rows x columns x a x b`
  (each parallelogram has base `a` and height `b`), so no facet is missing or cut short.
- `the flat sheet is rows x cols parallelograms of a x b`: the flat sheet (a hidden fill of the same outline) has
  that area too.
- `one facet per cell`: the folded panel has `rows x columns` facets, so the fold built every cell.
- `folded thickness a sin(gamma) sin(theta), by the closed form`: the folded panel's height in z is
  `a sin(angle) sin(theta)`, with `theta = atan(tan(fold / 2) / cos(angle))` the facets' lean (Schenk and Guest
  2013): the solved fold against the Miura-ori's kinematics, to 0.001 mm (0 when folded flat).
- `the panel lies level about z = 0`: its top is at half that height, so it lies level, mountains above and
  valleys below.
Thick panels (on), with `c` the clearance and `t` the thickness:

- `thick panels: one six-sided prism per cell`: the panels have `6 x rows x columns` faces.
- `thick panels: volume ...`: each panel is its parallelogram set back by `c` from the creases among its sides
  (not from the outline). It keeps `b - k c` between its straight sides and `a sin(angle) - m c` between its
  zigzag sides, `k` and `m` the creases among them. Summed over the grid the rows and columns separate, so the
  volume is `t (rows b - 2 c (rows - 1)) (columns a sin(angle) - 2 c (columns - 1)) / sin(angle)`. This proves
  the set-back.
- `thick panels: folded height ...`: every facet leans by `theta`, so a panel reaches `t cos(theta)` past the
  membrane on its side. A panel set back from a zigzag crease loses `c sin(theta)` there. The odd zigzag creases lie
  on top, and the right outline is on top only for an odd number of columns. So the height is
  `a sin(angle) sin(theta) + t cos(theta)`, less `c sin(theta)` for an even number of columns. The bottom is at
  `-a sin(angle) sin(theta) / 2 - t cos(theta)` with the panels on the back, and at `-a sin(angle) sin(theta) / 2`
  on the front. Both are held to 0.001 mm. They check the panels' placement against the kinematics and the side
  they are on.
- `thick panels: the fold stays below where the panels meet`: `fold` is below the closed form above. That the
  panels do not meet is 3DCraft's own check of every pair of panels as solids, a refused fold failing the
  point.

Both:

- `Kawasaki holds at every interior vertex`, `Maekawa holds at every interior vertex`: `kawasakiFails` and
  `maekawaFails` are 0 (every vertex has sectors `angle, 180 - angle, 180 - angle, angle` and three creases of
  one kind). Both are necessary for folding flat, and prove nothing more on their own.
- `the pattern folds flat (an order of the layers exists)`: `flatFoldable` is true. 3DCraft decides it with
  every crease at 180 deg, whatever the Fold angle is now (and, with thick panels, for the paper pattern: thick
  panels themselves do not fold flat).
- `the pattern fits the sheet's width inside the margin`, `... height ...`: the flat sheet's box fits the paper
  less twice the margin.

With thick panels the paper fold is off. Its pattern still gives `fold.check`, these three measures and the
crease pattern's export. The fold itself must solve at every point of the range: `scripts/check.sh`
regenerates the defaults, the corners of all ranges (fold 0 and its maximum, angles 45 and 80 deg, 3 and 14
rows, 3 and 16 columns, the largest cells, thick panels on and off) and random points, and a failed fold fails
the point. `fold.check` lists each vertex's sums:

```sh
craft3d-cli run dist/miura-ori.3dcraftjig --cmd fold.check --params '{"fold": "Miura-ori"}'
```

## Printing and scoring

Export the crease pattern (a fold exports flat, whatever the Fold angle). For printing, give the SVG's lines
a width with `stroke`, in millimetres (0.3 mm prints well); without it they are a laser's hairline (0.01 mm),
too thin to print:

```sh
craft3d-cli run dist/miura-ori.3dcraftjig \
  --cmd param.set --params '{"values": {"rows": 6, "cols": 8, "cellW": "30 mm", "cellH": "28 mm"}}' \
  --cmd file.export --params '{"path": "miura-ori.svg", "fold": "Miura-ori", "stroke": 0.3}'
```

For a laser leave `stroke` out (`.dxf` for DXF).

The export draws every crease, the pattern copies too (at the defaults 44 mountains and 38 valleys and the
14 lines of the outline; 3DCraft before 0dc5efb6 drew only the seed creases). It reads the paper fold
`Miura-ori`, which works with thick panels on too. In the window: **File › Export…**, *Crease pattern of:
Miura-ori*, SVG or DXF (the dialog has no line width; for a printable SVG use the command above). The outline is black on
the layer `boundary`, mountains red dash-dot on `mountain`, valleys blue dashed on `valley`; the file is at
true size in millimetres (the pattern's own size, not the paper's).

**By hand, on paper or card.**

1. Print the SVG at **100 % (actual size, no "fit to page")**, centred, on the paper you chose; measure one
   cell to check the scale. 120 to 160 g/m² paper folds crisply; thin card (200 g/m²) needs scoring on both
   sides.
2. Lay a steel ruler on each line and score it with an empty ballpoint pen, a bone folder or a blunt knife back,
   pressing firmly but not cutting through. Score the **valleys (blue) on the printed side**; turn the sheet
   over and score the **mountains (red)** from the back (prick their ends through with a pin first, so you can
   find them), or score everything from the front and fold the mountains back.
3. Cut the outline (black).
4. Pre-fold every crease one way, then the other, and flatten again.
5. Fold the panel: pinch the zigzag creases into their mountains and valleys row by row, and push the
   straight creases in alternately. Once a few rows are in, the whole panel collapses together; pull two opposite
   corners and it opens in one motion.

**Laser-scoring.** Use the DXF or SVG; give the layers `mountain` and `valley` a low-power score (engrave line)
setting that half-cuts the card without going through, and the layer `boundary` a cut. **A half-cut belongs on
the outside of its fold:** the kerf opens as the card bends and the uncut skin on the inside is the hinge; a
half-cut on the inside is squeezed shut, and the card buckles or cracks beside it. Seen from the printed side
(the front), the outside of a mountain is the front and the outside of a valley is the back. A laser cuts from
the top only, so:

1. Front up: half-cut the **mountains** (red) only.
2. Flip the sheet about its long edge against a corner stop or registration marks, and mirror the file
   (left-right) in your laser software; half-cut the **valleys** (blue) only, then cut the outline.

On paper and thin card (up to about 200 g/m²) a single pass from the front for all creases works too: the
valleys then have their score on the inside, which thin stock forgives. Try your power on a test strip first.

## Sources

- K. Miura, "Method of packaging and deployment of large membranes in space", *The Institute of Space and
  Astronautical Science Report* 618, 1985: the Miura-ori pattern.
- M. Schenk and S. D. Guest, "Geometry of Miura-folded metamaterials", *PNAS* 110(9), 2013, pp. 3276-3281: the
  cell's kinematics (one degree of freedom, the zigzag fold angle from the straight one).
- T. Tachi, "Generalization of rigid-foldable quadrilateral-mesh origami", *Journal of the IASS* 50(3), 2009:
  fold angles of flat-foldable degree-4 vertices.
- T. C. Hull, *Origametry*, Cambridge University Press, 2020: Kawasaki's and Maekawa's conditions.
- S. A. Zirbel et al., "Accommodating thickness in origami-based deployable arrays", *Journal of Mechanical
  Design* 135(11), 2013: thick-origami methods compared, among them the membrane (hinges on one surface).
- B. J. Edmondson et al., "An offset panel technique for thick rigidly foldable origami", *ASME IDETC* 2014;
  T. Tachi, "Rigid-foldable thick origami", *Origami 5*, 2011: the methods that fold thick panels flat (not
  in 3DCraft yet).

## Notes

- Needs a 3DCraft that reads format version 50 (creases from sketch patterns, folding flat, thick panels,
  assertions with a condition): built and checked with `main` at 0dc5efb6; older builds cannot open or build
  this Jig.
- `build.json` is written by `python3 gen.py > build.json`; gen.py only writes commands with expressions
  (`3 * a + d`), never coordinates it computed.
