# Sliceform

A sliceform lamp shade or sculpture to cut on a laser: two families of flat slices, one in planes across
x and one in planes across y, slide into each other with half-lap slots and together show a shape given by
a formula. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Shape | Shape | Twisted vase or lamp shade | Twisted vase or lamp shade, Ellipsoid or sphere, Saddle, Wave (table `shapes`) |
| Height | Shape | 300 mm | 100 to 600 mm, step 1 mm |
| Width | Shape | 340 mm | from a least that follows the sheet, the shape and the lamp room (254 mm at the default) to 600 mm |
| X slices | Slices | 9 | 3 to 12; the model uses at most as many as leave a web of two sheet thicknesses between the slots (10 at the default, 7 with 6 mm sheet), and with the lamp room at least enough for a slice beside it |
| Y slices | Slices | 9 | the same |
| Sheet | Material | Plywood 4 mm | plywood 3, 4, 6 mm; MDF 3, 6 mm; acrylic 3, 4 mm; greyboard 2 mm; corrugated cardboard 3 mm (table `sheets`) |
| Slot clearance | Material | 0.15 mm | 0 to 0.5 mm, step 0.01 mm |
| Twist | Vase | 120 deg | -180 to 180 deg |
| Section ratio | Vase | 65 % | 55 to 100 % (100: round) |
| Waist | Vase | -10 % (a belly) | -30 % (a belly) to 30 % |
| Lamp room | Lamp | on | on / off (vase only) |
| Lamp room width | Lamp | 64 mm | 44 to 120 mm; the model uses at most what leaves a slice outside the room on each side |
| Lamp room height | Lamp | 110 mm | 40 mm to the height less two webs |
| Relief | Saddle and wave | 25 % | 5 to 40 % of the height; the model uses at most what keeps two webs under the lowest point and slopes of at most 1.5 |

## The shapes

Each slice's outline is the exact section of the shape in the slice's plane, drawn with `sketch.curve`
from the shape's formula (a spline fitted within half the document's tolerance, never a polyline), and
extruded one sheet thick. `A` is half the width, `H` the height.

- **Twisted vase or lamp shade.** At height `z` the section is an ellipse with semi-axes `a(z)` and
  `b(z) = ratio * a(z)`, `a(z) = A (1 - waist sin(pi z / H))` (scaled so the widest is `A`), turned by
  `phi(z) = twist (z / H - 1/2)`. In the plane `x = c`, with `k = a / b` and `u = c / a`, the ellipse
  `(x cos phi + y sin phi)^2 / a^2 + (-x sin phi + y cos phi)^2 / b^2 = 1` gives the two edges
  `y = a (-R u ± sqrt(Q - k^2 u^2)) / Q`, `Q = sin^2 phi + k^2 cos^2 phi`, `R = sin phi cos phi (1 - k^2)`
  (the Y slices likewise, with x and y swapped). Foot and rim are flat.
- **Ellipsoid or sphere.** `x^2 / A^2 + y^2 / A^2 + (z - H/2)^2 / (H/2)^2 = 1`: every section is an
  ellipse, drawn as four quarters. A sphere when width = height.
- **Saddle.** A hyperbolic paraboloid over a square: `z = H - D + D (x^2 - y^2) / A^2`, `D` the relief.
  The two families of sections are parabolas, opening down in one family and up in the other.
- **Wave.** `z = H - D + D sin(1.5 pi x / A) cos(1.5 pi y / A)` over a square.

A torus is not offered: its central slices would cross in the hole, so some crossings would have
almost no material round their slots, or a slice would fall apart in two.

## How it holds together

- **Where the slices go.** The crossings form a square grid of half-width `g`, the X slices at
  `x = (i - (nx + 1) / 2) * 2g / (nx - 1)` and the Y slices likewise. `g` is chosen per shape so that every
  crossing lies inside the shape at every height it spans, with a web of at least **two sheet
  thicknesses** (plus the relief radius and 0.5 mm) below and above the slots and beside the outermost
  slots: for the vase from the narrowest section's short semi-axis, for the ellipsoid from both the
  section beside the outer slot and the height left at the outermost crossing, for the saddle and the wave
  `g = A - (slot / 2 + web)`. The number of slices is limited so that two slots are at least the slot
  width plus a web apart, and the least width follows from room for three slices (and the lamp room).
- **Half-lap slots.** The X slices are slotted from the top down to the plane `z = zm`, the Y slices from
  the foot up to the same plane, so at every crossing the two slots add up to the full height there. `zm`
  is half the height (the vase; with a lamp room, half way between the room's top and the rim), the
  centre (ellipsoid), or half the lowest point of the top (saddle and wave). Slots are the sheet thickness
  plus the clearance wide, with round reliefs of 0.5 mm radius in their inner corners (dogbones), so a
  burnt or rounded corner of the cut does not hold the other slice up.
- **Lamp room.** For the vase, a square room in the foot for an E27 lamp holder (its ring is about 40 mm
  across) and the bulb, from the foot up to the lamp room height. Its sides are the outer walls of the slots
  of the slices nearest to half the lamp room width, so it is at least that wide (a little more: it snaps to
  the slices), the slices beside it are cut square and no thin ledge is left; the next slices outside stand
  on the floor, a web away. With the room, the slots meet half way between the room's top and the rim.
  Use an **LED bulb** only (an E27 LED A60 bulb is about 60 mm across and 110 mm long and stays cool); a
  filament or halogen bulb gets far too hot for plywood, MDF, card or acrylic.

## Checked by assertions

- `X slices`, `Y slices`: as many bodies of each family as the model uses.
- `every crossing: X slot from the top down to the meeting plane`, `... Y slot from the foot up ...`: there
  are as many X slot floors lying on the plane `z = zm` as there are crossings, and as many Y slot floors.
  With the slots as wide as the sheet or wider, the X slice holds only the part of a crossing below `zm`
  and the Y slice only the part above it: the slices touch at their slots and nowhere overlap.
- `the two half-slots of a crossing meet`: the floors of the X slots touch the floors of the Y slots
  (distance 0): each slot pair adds up to the full height at its crossing.
- `X slots are sheet + clearance wide`, `Y slots ...`: the distance between the walls of a slot is the
  sheet thickness plus the clearance.
- `web round the X slots at least 2 x sheet`, `... Y slots ...`: from the floor of every slot, the nearest
  edge of the slice that is not a slot (the foot, the rim, the outline, the lamp room) is at least two sheet
  thicknesses away.
- `fits the width`, `stands on z = 0`, `fits the height`: the box of all slices lies within
  `[-width / 2, width / 2]` in x and y and `[0, height]` in z.

## Cutting

The named face set **Cut sheet** holds one face of every slice. File › Export…, SVG or DXF with *Sheet of
set: Cut sheet* and your laser's bed as the sheet width:

```sh
craft3d-cli run dist/sliceform.3dcraftjig \
  --cmd file.export --params '{"path": "sliceform.svg", "set": "Cut sheet", "width": "600 mm"}'
```

Every slice is on a layer named after it: `X1` to `Xn` (the slices across x, from -x to +x, slotted from
the top) and `Y1` to `Yn` (across y, from -y to +y, slotted from the foot). The parts are laid out in that
order: X2 ... Xn, X1, then Y2 ... Yn, Y1. 3DCraft does not engrave text yet, so number the parts with a
pencil as they come off the bed (or give each layer its own engrave pass in your laser software).
The curves stay curves in the file (splines, arcs and lines), so the laser follows them smoothly. The kerf
of the laser widens the slots by itself: on plywood a clearance of 0.1 to 0.2 mm slides, 0 is snug.
Measure your sheet: 4 mm plywood is often 3.6 to 4.2 mm thick; choose the sheet nearest to it and adjust
the clearance by the difference.

## Assembly

1. Sort the slices: X slices have their slots open at the top, Y slices at the foot.
2. Lay the X slices on their sides in order, X1 to Xn.
3. Stand two neighbouring X slices up, then lower Y1 onto them from above, slots down over slots up;
   then Yn at the far end. The frame now stands.
4. Add the remaining X slices one by one, then lower the remaining Y slices in order. Do not force a slot:
   if one binds, sand the slot wall lightly.
5. A sliceform needs no glue; a drop of wood glue at the crossings of the foot makes a lamp shade rigid.

## Sources

- John Sharp, *Sliceforms: Mathematical Models from Paper Sections*, Tarquin Publications, 1995
  (ISBN 978-1-899618-06-4): the sliceform principle, two sets of parallel sections slotted half way at
  each crossing, slots from the top in one set and from the bottom in the other, and how to generate the
  slices of a model of your own.
- John Sharp, *Surfaces: Explorations with Sliceforms*, Tarquin, 2021 (ISBN 978-1-913565-94-7): sliceform
  models of surfaces given by formulas, the hyperbolic paraboloid among them.
- E27 lamp holders and bulbs: the Edison screw E27 (IEC 60061-1); the holder's ring and the A60 bulb sizes
  above are common catalogue sizes, not a standard's values: measure yours.

## Notes

- The overlap of the slices is proven through the slot floors rather than with the `overlap` measure: that
  measure takes a boolean per pair of slices (81 at the default, about 25 s a point) and, with 3 mm sheet,
  the kernel could not tell for one pair (`boolean produced an invalid body`). At the default
  `document.interference` finds the 81 crossing pairs touching, the other 72 pairs clear and none overlapping.
- 3DCraft does not engrave text yet, hence the layer names instead of numbers on the parts.

`build.json` is written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
