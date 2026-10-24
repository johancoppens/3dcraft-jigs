# Laser-cut box

A finger-jointed box with a loose lid, cut from plywood or acrylic sheet. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Width | Size | 160 mm | 100 to 300 mm, step 1 mm |
| Depth | Size | 110 mm | 80 to 250 mm, step 1 mm |
| Height (lid on) | Size | 80 mm | 50 to 150 mm, step 1 mm |
| Sheet thickness | Material | 3 mm | 2 to 6 mm |
| Finger width | Joints | 12 mm | 8 to 20 mm |
| Kerf | Laser | 0.15 mm | 0 to 0.3 mm |
| Clearance | Laser | 0 mm | 0 to 0.2 mm |
| Thumb notch radius | Details | 11 mm | 6 to 15 mm |
| Lid grip | Details | Round hole | Round hole, Finger slot, None |
| Grip size | Details | 9 mm | 5 to 15 mm (radius of the hole; half the width of the slot) |
| Divider | Divider | on | on / off |
| Divider position | Divider | 50 | 25 to 75 (% of the inside depth from the front) |
| Show the lid lifted | View | on | on / off (only how the model is shown) |

**How it is built.** Six bodies: front, back, left, right, bottom and a lid that lies on the walls, and
an optional divider.
Each edge is cut into an odd number of fingers, the one nearest to edge / finger width (at least 3); the
panels own alternate segments so they interlock. The bodies are the *cut paths*: the nominal outline
offset outward by kerf / 2, with every finger flank moved by (clearance − kerf) / 2. With kerf and
clearance 0 the panels fill the walls exactly.

**Options.** The lid has a round finger hole in the middle, a finger slot (a stadium 2 × grip size wide
and 3 × grip size long, at most half the inside width) near the front edge, or nothing (`feature.when` on
a choice). The divider stands across the box, parallel to the front, as high as the walls less one sheet;
one tab goes through each side wall and two (each min(2 × finger width, inside width / 5) long) through
the bottom, into mortises cut clearance / 2 wider on every side, less the kerf. With the divider off its
mortises are off too. **Show the lid lifted** moves the lid up by half the height and back by a quarter
of the depth, so the thumbnail and the viewport show the inside; the cut sheet is the same either way.

**Colours.** Every panel has its own colour from the Jigs palette, which also tells the panels apart in
the viewport: front terracotta, back petrol, left sage, right ochre, bottom cream, lid slate blue,
divider plum.

**Cutting.** The named face set **Cut sheet** holds the broad face of each panel. File › Export…, DXF or
SVG, with the face set "Cut sheet" lays every panel (six, seven with the divider) on one sheet at true size, one layer per panel
(`file.export {"path": "box.svg", "set": "Cut sheet"}`, or
`craft3d-cli convert box.3dcraft box.dxf --set "Cut sheet"`).

**Checked.** `check-range --deep` passes: 99 of 99 points (64 of the corners, every choice, 32 random), and
130 of 130 more with `--samples 64 --seed 7`; 3DCraft `main` at baf6c1f5. Regeneration median about 65 ms, at most
about 170 ms native release. The cut sheet exports as 12 closed paths with the divider and the finger slot.

Source: the showcase model of 3DCraft's `plan/laserbox.md` (2026-10-16), made into a Jig.
