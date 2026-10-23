# Phone and tablet stand

A desk stand that holds a phone or tablet at the angle you choose, for 3D printing. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Angle | Device | 65 deg | 50 to 80 deg, step 1 deg |
| Device thickness | Device | 11 mm | 6 to 16 mm, step 0.5 mm |
| Back rest length | Device | 90 mm | 40 to 140 mm, step 1 mm |
| Lip height | Device | 8 mm | 4 to 16 mm, step 0.5 mm |
| Width | Stand | 70 mm | 40 to 120 mm, step 1 mm |
| Wall thickness | Stand | 5 mm | 3 to 8 mm, step 0.5 mm |
| Cable slot | Cable | on | on / off |
| Cable slot width | Cable | 12 mm | 6 to 16 mm, step 0.5 mm |

**How it is built.** One side profile (a closed polyline whose corners are formulas of the parameters),
extruded to the width: a base plate, a 4 mm front lip, a slot for the device's bottom edge and a slanted back
rest. The device leans on the back rest at the angle, so the slot is as wide as the device's footprint at
that angle, thickness / sin(angle) + 0.5 mm; the foot runs on 15 mm behind the top of the back rest so the
stand does not tip. The outer corners are rounded (min(1.5 mm, thickness / 3)), the inside corner under
the back rest gets a fillet twice that size as a gusset. The cable slot (`feature.when`) cuts through the
lip and the slot floor in the middle, so a charging plug reaches the device from below. Finally the body is
turned upright, facing the iso view.

**Printing.** Lay it on its side (the profile on the bed) in the slicer: the layers then run along the
back rest and the stand is strong, without supports.

**Checked.** `check-range` passes at the default, all 256 corners and 32 random points, also with `--deep`;
regeneration median about 50 ms, at most about 180 ms native. STL export closed.
