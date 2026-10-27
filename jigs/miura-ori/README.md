# Miura-ori fold panel

A Miura-ori panel: a sheet of 6 x 8 parallelograms that folds in and out in one motion. The Jig shows the
folded panel at any angle from flat to almost folded flat, and exports the crease pattern to print and score,
or to laser-score. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Cell width | Pattern | 30 mm | 10 mm to what fits the paper inside the margin, step 0.5 mm |
| Cell height | Pattern | 28 mm | 10 mm to what fits the paper inside the margin, step 0.5 mm |
| Parallelogram angle | Pattern | 70 deg | 45 to 85 deg, step 1 deg |
| Fold | Fold | 90 deg | 0 (flat) to 179 deg (almost folded flat), step 1 deg |
| Paper | Paper | A4 | A4, A3, Letter (table `sheets`) |
| Landscape | Paper | on | on / off |
| Margin | Paper | 10 mm | 0 to 30 mm, step 1 mm |

The maximum cell sizes follow the paper, the orientation, the margin and the angle: the flat pattern is
`8 x cell width + d` wide and `6 x cell height` high, with `d = cell height / tan(angle)` the zigzag's offset.

**The number of rows and columns is fixed at 6 x 8.** 3DCraft's `feature.fold` takes its creases as lines
drawn one by one, and does not take the instances of a sketch pattern as creases, so a crease grid whose
size follows a rows or columns parameter cannot be expressed yet (filed as a missing capability of 3DCraft).
For another grid, change `ROWS` and `COLS` in `gen.py` and run it again.

## How it folds

Every point of the pattern is a sketch point held by expressions of the cell width `a`, the cell height `b`
and `d = b / tan(angle)`: grid point `(i, j)` lies at `(i a + (j mod 2) d, j b)`. The straight creases run
across at every row (`y = j b`), the zigzag creases up the columns. Seen from the printed side:

- **zigzag creases**: column 1, 3, 5, 7 mountains, column 2, 4, 6 valleys, each along its whole length;
- **straight creases**: alternately mountain and valley along each line, shifted by one cell from one line to
  the next (segment `i` of line `j` is a valley when `i + j` is odd).

At every inside vertex three creases are of one kind and one of the other. The panel is folded rigidly by
3DCraft's own fold solver: only one crease, the first segment of the lowest straight line, has the **Fold**
angle; 3DCraft solves the other 81 crease pieces from it (a Miura-ori sheet has one degree of freedom). The
straight creases all fold by the Fold angle, the zigzag creases by `2 atan(tan(fold / 2) / cos(angle))`, which
is faster: at the defaults (90 deg) the zigzags are at 142.2 deg. At 179 deg the panel is a thin stack; exactly
180 deg (folded flat) is not offered: a sheet without thickness folded flat lays facets on one another, which
3DCraft refuses.

The facet that stays in place is a middle cell (the fourth) of the third row. A folded Miura-ori leans: each facet tilts
by `theta = atan(tan(fold / 2) / cos(angle))` (half the zigzag creases' fold angle) about its zigzag edge, so the
Jig turns the folded sheet back by `theta` about that edge's direction (`feature.transform`, the body `Panel`).
The panel then lies level, its mean plane (the plane of each zigzag crease line) on `z = 0`, and it shrinks in
place as it folds.

## Checked by assertions

- `every cell is in the folded panel (area rows x cols x a x b)`: the folded panel's area is `6 x 8 x a x b`
  (each parallelogram has base `a` and height `b`), so no facet is missing or cut short.
- `the flat sheet is rows x cols parallelograms of a x b`: the flat sheet (a hidden fill of the same outline) has
  that area too.
- `one facet per cell`: the folded panel has 48 facets, so the fold built every cell.
- `folded thickness a sin(gamma) sin(theta), by the closed form`: the folded panel's height in z is
  `a sin(angle) sin(theta)`, with `theta = atan(tan(fold / 2) / cos(angle))` the facets' lean (Schenk and Guest
  2013): the solved fold against the Miura-ori's kinematics, to 0.001 mm.
- `the panel lies level about z = 0`: its top is at half that height, so it lies level, mountains above and
  valleys below.
- `the pattern fits the sheet's width inside the margin`, `... height ...`: the flat sheet's box fits the paper
  less twice the margin.

The fold itself must solve at every point of the range: `scripts/check.sh` regenerates the defaults, the
corners of all ranges (fold 0 and 179 deg with angles 45 and 85 deg, the largest cells) and random points, and
a failed fold fails the point. Not an assertion yet: Kawasaki's and Maekawa's conditions at every vertex.
`fold.check` reports them (all 35 inside vertices pass at every size and angle, since every vertex has sectors
`angle, 180 - angle, 180 - angle, angle` and three creases of one kind), but its result cannot be used in an
assertion in 3DCraft yet (filed as a missing capability). Run it by hand:

```sh
craft3d-cli run dist/miura-ori.3dcraftjig --cmd fold.check --params '{"fold": "Miura-ori"}'
```

## Printing and scoring

Export the crease pattern (a fold exports flat, whatever the Fold angle):

```sh
craft3d-cli run dist/miura-ori.3dcraftjig \
  --cmd param.set --params '{"values": {"cellW": "30 mm", "cellH": "28 mm"}}' \
  --cmd file.export --params '{"path": "miura-ori.svg", "fold": "Miura-ori"}'
```

(`.dxf` for DXF). The window's **File › Export…** dialog does not offer a fold's crease pattern yet; use the
command `file.export` with `fold` (from the CLI as above, or by an agent). The outline is black on
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

- Needs a 3DCraft with `feature.fold` (built and checked with `main` at 4d82484c); older builds cannot open
  or build this Jig.
- The export's lines are hairlines (0.01 mm), right for a laser; most printers print a hairline as their
  thinnest line, which is enough to score along. 3DCraft has no stroke-width option for the crease pattern yet.
- `build.json` is written by `python3 gen.py > build.json`; gen.py only writes commands with expressions
  (`3 * a + d`), never coordinates it computed.
