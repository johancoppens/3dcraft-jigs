# Miura-ori fold panel

A Miura-ori panel: a sheet of parallelograms, 3 to 12 rows by 3 to 12 columns, that folds in and out in one
motion. The Jig shows the panel at any angle from flat to folded flat, and exports the crease pattern to print
and score, or to laser-score. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Rows | Pattern | 6 | 3 to 12, and no more than leave cells of 10 mm on the paper |
| Columns | Pattern | 8 | 3 to 12, and no more than leave cells of 10 mm on the paper |
| Cell width | Pattern | 30 mm | 10 mm to what fits the paper inside the margin, step 0.5 mm |
| Cell height | Pattern | 28 mm | 10 mm to what fits the paper inside the margin, step 0.5 mm |
| Parallelogram angle | Pattern | 70 deg | 45 to 80 deg, step 1 deg |
| Fold | Fold | 90 deg | 0 (flat) to 180 deg (folded flat), step 1 deg |
| Paper | Paper | A4 | A4, A3, Letter (table `sheets`) |
| Landscape | Paper | on | on / off |
| Margin | Paper | 10 mm | 0 to 30 mm, step 1 mm |

The maximum cell sizes follow the paper, the orientation, the margin, the rows and columns and the angle: the
flat pattern is `columns x cell width + d` wide and `rows x cell height` high, with `d = cell height / tan(angle)`
the zigzag's offset.

Why these limits: 12 x 12 keeps the solve well inside 3DCraft's 400 crease angles solved at once (264 here).
Above 80 deg, and with 12 rows of 14 columns, the folded-flat panel stacks so many facets in one place (156) that
3DCraft's search for the order of the layers runs out of its work allowance (it says so rather than guess), so
the angle stops at 80 deg and the columns at 12, where every corner of the ranges folds flat.

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

## Checked by assertions

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
- `Kawasaki holds at every interior vertex`, `Maekawa holds at every interior vertex`: `kawasakiFails` and
  `maekawaFails` are 0 (every vertex has sectors `angle, 180 - angle, 180 - angle, angle` and three creases of
  one kind). Both are necessary for folding flat, and prove nothing more on their own.
- `the pattern folds flat (an order of the layers exists)`: `flatFoldable` is true. 3DCraft decides it with
  every crease at 180 deg, whatever the Fold angle is now.
- `the pattern fits the sheet's width inside the margin`, `... height ...`: the flat sheet's box fits the paper
  less twice the margin.

The fold itself must solve at every point of the range: `scripts/check.sh` regenerates the defaults, the
corners of all ranges (fold 0 and 180 deg, angles 45 and 80 deg, 3 and 12 rows and columns, the largest cells)
and random points, and a failed fold fails the point. `fold.check` lists each vertex's sums:

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

**Known problem (3DCraft, filed as a repro): the export draws only the seed creases**, one of each of the eight
kinds in the lower left corner, and leaves out their pattern copies, while the outline is whole. The fold,
`fold.check` and the assertions do use every copy. Until 3DCraft draws the copies, the exported crease pattern
is incomplete; do not print or cut it. In the window: **File › Export…**, *Crease pattern of: Miura-ori*, SVG or DXF (the dialog has
no line width; for a printable SVG use the command above). The outline is black on
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

## Notes

- Needs a 3DCraft that reads format version 45 (creases from sketch patterns, the Kawasaki, Maekawa and
  flat-foldable measures, folding flat): built and checked with `main` at 93ce1873; older builds cannot open
  or build this Jig.
- `build.json` is written by `python3 gen.py > build.json`; gen.py only writes commands with expressions
  (`3 * a + d`), never coordinates it computed.
