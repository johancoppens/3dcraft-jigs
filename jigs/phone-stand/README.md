# Phone and tablet stand

A desk stand that holds a phone or tablet at the angle you choose, for 3D printing. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Angle | Device | 65 deg | 50 to 80 deg, step 1 deg |
| Device thickness | Device | 11 mm | 6 to 16 mm, step 0.5 mm |
| Back rest length | Device | 90 mm | 50 to 140 mm, step 1 mm |
| Lip height | Device | 8 mm | 4 to 16 mm, step 0.5 mm |
| Width | Stand | 70 mm | 40 to 120 mm, step 1 mm |
| Wall thickness | Stand | 5 mm | 3 to 8 mm, step 0.5 mm |
| Back window | Stand | on | on / off |
| Cable slot | Cable | on | on / off |
| Cable slot width | Cable | 12 mm | 6 to 16 mm, step 0.5 mm |

**How it is built.** One side profile, extruded to the width: a base with a 4 mm front lip, a slot for the
device's bottom edge (thickness / sin(angle) + 0.5 mm wide), a slanted back rest and, behind it, a curved
strut: a quarter-circle band of the wall thickness whose centre lies where the back rest's back face meets
the table, so both its arcs end square on that face. Its outer radius puts the foot 12 mm behind the
device's centre of mass (back rest length × cos(angle) + 12 mm, kept between 0.6 and 0.85 of the back
rest). Between the base, the back rest and the strut the back is open: a window with rounded corners.
Every corner of the profile is rounded (outside min(1.5 mm, thickness / 3), the top of the back rest
0.45 × thickness, the joints of the strut one thickness, the slot's back corner twice the outside radius),
and both side outlines are rounded over by 0.4 × the outside radius (`chain`). **Back window** cuts a
rounded window through the back rest below the strut, two thirds of the width (built when it is at least
10 mm tall): lighter, and a way through for a cable. The cable slot (`feature.when`) cuts through the lip
and the slot floor in the middle. Finally the body is turned upright, facing the iso view. Colour: sage
(#8FA98A), a printed part.

**Printing.** Lay it on its side (the profile on the bed) in the slicer: the layers then run along the
back rest and the strut, and it prints without supports.

**Checked.** `check-range --deep` passes: 97 of 97 points (64 of the corners, 32 random), and 129 of 129 with
`--samples 64 --seed 7`; 3DCraft `main` at baf6c1f5. Regeneration median about 310 ms, at most about 1.8 s native.
The strut's arcs are formula curves (`sketch.curve`), not `sketch.arc`: with arcs, setting several parameters at
once (a 50 deg, 50 mm, 16 mm device, 3 mm wall corner) left the profile's loops touching, while the same values
built fresh were fine.
