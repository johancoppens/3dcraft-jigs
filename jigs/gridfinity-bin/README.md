# Gridfinity bin

A storage bin for the [Gridfinity](https://gridfinity.xyz/) system by Zack Freedman, for 3D printing. It
fits any Gridfinity baseplate and stacks on other Gridfinity bins. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Width | Size | 2 | 1 to 5 grid units of 42 mm |
| Depth | Size | 2 | 1 to 5 grid units of 42 mm |
| Height | Size | 3 | 2 to 12 units of 7 mm (without the lip) |
| Compartments across | Compartments | 2 | 1 to 2 × width + 1 |
| Compartments deep | Compartments | 2 | 1 to depth + 1 |
| Label ledge | Options | on | on / off |
| Stacking lip | Options | on | on / off |
| Magnet holes | Options | on | on / off |
| Wall | Options | 1.2 mm | 0.8 to 2 mm, step 0.05 mm |

**Dimensions (Gridfinity).**
- Grid 42 mm; a bin is 0.5 mm smaller than its grid (41.5 mm for one unit), outer corner radius 3.75 mm.
- Height unit 7 mm: the top of the wall, where the next bin stands, is at height × 7 mm.
- Base: one foot per unit with the base profile, from the bottom up a 0.8 mm 45° chamfer, 1.8 mm straight
  and a 2.15 mm 45° chamfer (4.75 mm tall, 2.95 mm in; the foot is 35.6 mm square at the bottom, corner
  radius 0.8 mm). The feet are joined by the floor up to 7 mm, where the inside starts.
- Stacking lip: from the top down a 1.9 mm 45° slope, 1.8 mm straight and a 0.7 mm 45° slope (4.4 mm tall,
  2.6 mm in), on a 1.2 mm straight and a 45° support back to the wall. The sharp tip of the profile is cut
  off 0.4 mm, leaving a 0.4 mm flat on top that prints cleanly (the bin is 4 mm taller than height × 7 mm);
  a stacked bin's feet rest on the lip's slopes, not on the tip.
- Magnet holes: 6.5 mm across and 2.4 mm deep, for 6 × 2 mm magnets, 8 mm from the sides of each unit
  (26 mm apart), four per unit.

**How it is built.** Each foot is a ruled loft through four rounded rectangles of the base profile,
patterned over the grid and joined to the body. The inside is one ruled loft through the stacking lip's
profile (without the lip its sections stand straight above one another), with its floor edges rounded at
the inner corner radius (3.75 mm − wall), so the floor is easy to scoop out. Dividers (1.2 mm) and the label
ledges are taken out of that hollow before it is cut from the body, so they join the walls without a seam.
The ledge sits at the back of every row, 1.2 mm thick at the front with a 45° support under it (printable
without supports); it reaches at most 12 mm in, less in a shallow bin or a short row. Its top and the
dividers' stay below where a stacked bin's feet come.

**3DCraft features used.** Ruled lofts of formula-driven sketches, linear patterns whose counts are
parameters (and a pattern of a pattern for the magnet holes), `feature.when` for the dividers, ledges and
magnet holes, `if()` in the hollow's sections for the lip, a chained fillet along a loft's rim, assertions
(one body; the footprint is width × 42 mm − 0.5 mm).

**Checked.** `check-range --deep` passes at the default, 64 corners and random points (16 with seed 1, 64
with seed 7); regeneration median about 110 ms, at most about 450 ms. STL export closed.

**Not included.** Screw holes in the base, the "refined" press-fit magnet holes and a scoop larger than
the inner corner radius (3DCraft does not yet build a fillet torus that reaches its own axis).

**Sources.**
- Gridfinity by Zack Freedman (Voidstar Lab), introduced in *Gridfinity: Your Ultimate Modular Workshop is
  FREE!* (2022) and released under the MIT licence; the community's write-up of the specification is at
  [gridfinity.xyz](https://gridfinity.xyz/specification/) and
  [github.com/gridfinity-unofficial/specification](https://github.com/gridfinity-unofficial/specification).
- The profile numbers as kennetek's [gridfinity-rebuilt-openscad](https://github.com/kennetek/gridfinity-rebuilt-openscad)
  (MIT) writes them down (`standard.scad`). No code was taken from it; this model is built from the numbers.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
