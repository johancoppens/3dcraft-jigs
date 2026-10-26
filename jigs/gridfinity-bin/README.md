# Gridfinity bin

A storage bin for the [Gridfinity](https://gridfinity.xyz/) system by Zack Freedman, for 3D printing. It
seats in any Gridfinity baseplate (and in a plate from the [`gridfinity-baseplate`](../gridfinity-baseplate/)
Jig, which checks it) and stacks on other Gridfinity bins. Licence: CC-BY-4.0.

The default is a 2 × 3 × 6 bin (83.5 × 125.5 mm, 42 mm tall plus the lip) with two dividers front to back
(three rows), a label tab at the back of every row, a scoop at the front of every row and magnet holes.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Width | Size | 2 | 1 to 6 grid units of 42 mm |
| Depth | Size | 3 | 1 to 6 grid units of 42 mm |
| Height | Size | 6 | 2 to 15 units of 7 mm, base included, without the lip |
| Dividers across | Compartments | 0 | 0 to 2 × width − 1 (compartments side by side) |
| Dividers front to back | Compartments | 2 | 0 to depth (rows) |
| Label tab | Compartments | Back | None, Back, Front (of every row) |
| Label tab angle | Compartments | 36° | 30° to min(60°, atan((height × 7 mm − 9.8 mm − extra floor) / 5 mm)), so the tab is at least 5 mm deep |
| Scoop | Compartments | on | on / off |
| Magnet holes | Base | on | on / off |
| Screw holes | Base | off | on / off |
| Stacking lip | Base | on | on / off |
| Wall | Walls | 1.2 mm | 0.95 mm to 1.8 mm with the lip (2.5 mm without), step 0.05 mm |
| Extra floor | Walls | 0 mm | 0 to min(10 mm, height × 7 mm − 17 mm), step 0.5 mm |

**Dimensions (Gridfinity).** All numbers come from `scripts/gridfinitylib.py`, which the baseplate Jig
uses too.
- Grid 42 mm; a bin is 0.5 mm smaller than its grid (41.5 mm for one unit), outer corner radius 3.75 mm.
- Height unit 7 mm: the top of the wall, where the next bin stands, is at height × 7 mm above the bottom
  of the feet (the base is part of the first unit, as in the standard).
- Base: one foot per unit with the base profile, from the bottom up a 0.8 mm 45° chamfer, 1.8 mm straight
  and a 2.15 mm 45° chamfer (4.75 mm tall, 2.95 mm in; the foot is 35.6 mm square at the bottom, corner
  radius 0.8 mm). The feet are joined by the floor up to 7 mm, where the inside starts (plus the extra
  floor).
- Stacking lip: from the top down a 1.9 mm 45° slope, 1.8 mm straight and a 0.7 mm 45° slope (4.4 mm tall,
  2.6 mm deep), on a 1.2 mm straight support and a 45° slope back to the wall. The sharp tip is cut off
  0.4 mm, leaving a 0.4 mm flat on top that prints cleanly (the bin is 4 mm taller than height × 7 mm);
  a stacked bin's feet rest on the lip's slopes, not on the tip. With the lip the wall is at most 1.8 mm,
  so the lip's 1.9 mm step stays inside it.
- Holes, in the four corners of every unit, 8 mm in from its sides: magnet holes 6.5 mm across and 2.4 mm
  deep (6 × 2 mm magnets and two 0.2 mm layers), and/or M3 screw holes 3 mm across and 6 mm deep, in the
  same place (with both, the screw hole goes on above the magnet's).
- Dividers 1.2 mm, every compartment as wide and every row as deep; their top 1 mm under the wall's top.
- Label tab: the standard's 15.85 mm deep tab with its support at 36° (adjustable), 1.2 mm straight at the
  front; its top 0.6 mm under the wall's top, below a stacked bin's feet. In a short row or a low bin it
  is shorter (at most half the row, and its support must end 1 mm above the floor); the angle's range
  keeps it at least 5 mm deep.
- Scoop: a quarter round between the floor and the front of every row, radius min(15 mm, half the row,
  half the inside height). Under a front label it takes the room the tab leaves when the tab is 5 mm deep
  and is left out where less than 3 mm remains.

**Checks (assertions, at every regeneration).**
- One body; width and depth = units × 42 mm − 0.5 mm; it stands on z = 0 and its top is height × 7 mm
  (+ 4 mm with the lip).
- The foot profile: the area of the bottom faces is units × (35.6² − (4 − π) 0.8²) mm² less the holes, and
  the area of the profile's sides (chamfer, straight, chamfer) is units × the frustum areas of the profile,
  to 0.05 mm²: a wrong chamfer, radius or height changes them.
- The walls: the distance from the outside face to the inside face is the wall (left, and front or back),
  and the wall is at least the standard's thinnest (0.95 mm).
- Dividers: as many as asked each way, and every divider face lies within 0.01 mm of where equal
  compartments put it, between the floor and the dividers' top.
- Label tabs: one per row, and the support face runs down to where the angle puts it; at least 5 mm deep.
- Scoops: one quarter-round face of the computed radius per row.
- Stacking: a second bin's foot (the same profile, hidden in the view, in the back right unit) seated in
  the lip touches the lip's slopes without entering the bin (so no divider or tab reaches into a stacked
  bin's feet); without the lip it is held 10 mm over the rim and the clearance is checked against that.
- That the bin seats in a baseplate is checked in the baseplate Jig, with the same foot.

**How it is built.** Each foot is a ruled loft through four rounded rectangles of the base profile,
patterned over the grid and joined to the body. The inside is one ruled loft through the stacking lip's
profile (without the lip its sections stand straight above one another), with its floor edges rounded at
the inner corner radius (3.75 mm − wall). Dividers, label tabs and scoops are taken out of that hollow
before it is cut from the body, so they join the walls without a seam; the tabs for a front label are the
back ones mirrored. Feature names are used in the fillet's edge names (`LipHollow:startCap(...)`).

**Printing.** Standing on its feet, no supports (the tab's support and the lip's slopes are self-supporting;
a tab angle above 45° prints more cleanly than the standard's 36°). PLA or PETG, 0.2 mm layers, a 0.4 mm
nozzle, two or three perimeters. Glue or press the magnets in.

**Checked.** `check-range` passes at the default, 64 corners, the choices and 16 random points (seed 1), also
`--deep`: 83 of 83; regeneration median about 100 ms, at most about 450 ms. STL export closed. Export the body `Bin` (STL or 3MF); the hidden `Stacked foot` is a check, not a
part.

**Sources.**
- Gridfinity by Zack Freedman (Voidstar Lab), introduced in *Gridfinity: Your Ultimate Modular Workshop is
  FREE!* (2022) and released under the MIT licence; the community's write-up of the specification is at
  [gridfinity.xyz](https://gridfinity.xyz/specification/) and
  [github.com/gridfinity-unofficial/specification](https://github.com/gridfinity-unofficial/specification)
  (42 × 42 × 7 mm unit, 41.5 mm bins, 6 × 2 mm magnets, M3 screws).
- The profile, lip, hole, divider, wall and tab numbers as kennetek's
  [gridfinity-rebuilt-openscad](https://github.com/kennetek/gridfinity-rebuilt-openscad) (MIT) writes them
  down (`src/core/standard.scad`: `BASE_PROFILE`, `STACKING_LIP_LINE`, `MAGNET_HOLE_*`, `SCREW_HOLE_RADIUS`,
  `d_hole_from_side`, `d_div`, `d_wall`, `TAB_POLYGON`). No code was taken from it; this model is built from
  the numbers.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` (or `scripts/gridfinitylib.py`)
and run it again to change the model.
