# Sliceform sculpture

A sliceform sculpture, or a lamp shade, to cut on a laser: two families of flat slices, one in planes across
x and one in planes across y, slide into each other with half-lap slots and together show a shape given by
a formula. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Shape | Shape | Saddle | Twisted vase or lamp shade, Ellipsoid or sphere, Saddle, Wave (table `shapes`) |
| Height | Shape | 220 mm | 100 to 600 mm, step 1 mm |
| Width | Shape | 340 mm | from a least that follows the sheet, the shape and the lamp room (100 mm for the saddle at the default) to 600 mm |
| X slices | Slices | 6 | 3 (with the lamp room: enough for a slice beside it) to as many as leave a finger of two sheet thicknesses between the slots, at most 12 |
| Y slices | Slices | 6 | the same |
| Sheet | Material | Plywood 4 mm | plywood 3, 4, 6 mm; MDF 3, 6 mm; acrylic 3, 4 mm; greyboard 2 mm; corrugated cardboard 3 mm (table `sheets`) |
| Slot clearance | Material | 0.15 mm | 0 to 0.5 mm, step 0.01 mm |
| Relief | Saddle and wave | 40 % | 5 % of the height (less when the most is lower) to what keeps two webs under the lowest point and slopes of at most 2.5, at most 40 % |
| Twist | Vase | 180 deg | -180 to 180 deg |
| Section ratio | Vase | 70 % | 55 to 100 % (100: round) |
| Waist | Vase | 25 % | -30 % (a belly) to 30 % |
| Lamp room | Lamp | on | on / off (vase only) |
| Lamp room width | Lamp | 64 mm | 44 mm to what leaves a slice outside the room on each side |
| Lamp room height | Lamp | 110 mm | 40 mm to the height less two webs |

The ranges are the real ones: the model uses the number you set. The form shows each limit as it follows
the other parameters (a thick sheet or a small shape allows fewer slices).

For a lamp shade: shape *Twisted vase or lamp shade*, 5 x 5 slices, width 360 mm, height 250 mm, with the vase
defaults above (twist 180 deg, section ratio 70 %, waist 25 %).

## The shapes

Each slice's outline is the exact section of the shape in the slice's plane, drawn with `sketch.curve`
from the shape's formula (a spline fitted within half the document's tolerance, never a polyline), and
extruded one sheet thick. `A` is half the width, `H` the height.

- **Twisted vase or lamp shade.** At height `z` the section is an ellipse with semi-axes `a(z)` and
  `b(z) = ratio * a(z)`, `a(z) = A (1 - waist sin(pi z / H))` (scaled so the widest is `A`), turned by
  `phi(z) = twist (z / H - 1/2)`. In the plane `x = c`, with `k = a / b` and `u = c / a`, the ellipse
  `(x cos phi + y sin phi)^2 / a^2 + (-x sin phi + y cos phi)^2 / b^2 = 1` gives the two edges
  `y = a (-R u ± sqrt(Q - k^2 u^2)) / Q`, `Q = sin^2 phi + k^2 cos^2 phi`, `R = sin phi cos phi (1 - k^2)`
  (the Y slices likewise, with x and y swapped). Foot and rim are flat. With a strong waist and twist the
  slices end in long, sharp wing tips (at the rim and the foot, outside the crossings): sand their points
  or choose less twist or waist if the shade will be handled a lot.
- **Ellipsoid or sphere.** `x^2 / A^2 + y^2 / A^2 + (z - H/2)^2 / (H/2)^2 = 1`: every section is an
  ellipse, drawn as four quarters. A sphere when width = height.
- **Saddle** (the default). A hyperbolic paraboloid over a square: `z = H - D + D (x^2 - y^2) / A^2`, `D`
  the relief. The two families of sections are parabolas, opening down in one family and up in the other.
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
  `g = A - (slot / 2 + web)`. The number of slices is limited so that the finger between two slots is at
  least two sheet thicknesses wide at the reliefs, and the least width follows from room for three slices
  (and the lamp room).
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
  (distance 0). On its own that proves one pair; together with the two counts above (every crossing has
  its X floor and its Y floor on the same plane) it proves that each slot pair adds up to the full height.
- `X slots are sheet + clearance wide`, `Y slots ...`: the slot floors together have the area
  `crossings x (slot width - 2 x relief radius) x sheet`. Each floor runs between the two reliefs and is
  bounded by straight edges only, so its area is exact, and it pins the slot width.
- `fingers between the X slots at least 2 x sheet`, `... Y slots ...`: the floors of the first two slots of
  slice 1 lie at least two sheet thicknesses plus four relief radii apart, so the finger between two slots
  is at least two sheet thicknesses wide where the reliefs narrow it (all slots are equally spaced).
- `web round the X slots at least 2 x sheet`, `... Y slots ...`: from the floor of every slot, the nearest
  edge of the slice that is not a slot (the foot, the rim, the outline, the lamp room) is at least two sheet
  thicknesses away.
- `fits the width`, `stands on z = 0`, `fits the height`: the box of all slices lies within
  `[-width / 2, width / 2]` in x and y and `[0, height]` in z.

## Cutting

The named face set **Cut sheet** holds one face of every slice. File › Export…, SVG or DXF with *Sheet of
set: Cut sheet* and your laser's bed as the sheet width. The parts are laid out in rows of that width, but
the sheet grows as tall as it needs: at the default the twelve slices (each about 340 x 220 mm) fill about four
600 x 400 mm bed, so split the file over several beds in your laser software, or cut the slices from their
layers a few at a time.

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
   Long fingers between slots are flexible (in a lamp shade with the lamp room, the Y slices beside the
   room are combs whose fingers can be about 200 mm long): guide each finger into its slot by hand, start
   every slot of a slice before pushing it home, and push evenly along the slice.
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
  measure takes a boolean per pair of slices (81 for a 9 x 9 vase, about 25 s a point) and, with 3 mm sheet,
  the kernel could not tell for one pair (`boolean produced an invalid body`). For a 9 x 9 vase
  `document.interference` found the 81 crossing pairs touching, the other 72 pairs clear and none overlapping.
- The slot width is measured through the floors' area, not as the distance between the slot walls: for
  walls bounded by the spline outline 3DCraft's distance gives a loose lower bound (4.15 mm found, at least
  3.26 mm proven), so such an assertion stays *not proven*.
- 3DCraft does not engrave text yet, hence the layer names instead of numbers on the parts.

`build.json` is written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
