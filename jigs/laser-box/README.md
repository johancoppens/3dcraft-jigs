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
| Lid hole radius | Details | 9 mm | 5 to 15 mm |

**How it is built.** Six bodies: front, back, left, right, bottom and a plain lid that lies on the walls.
Each edge is cut into an odd number of fingers, the one nearest to edge / finger width (at least 3); the
panels own alternate segments so they interlock. The bodies are the *cut paths*: the nominal outline
offset outward by kerf / 2, with every finger flank moved by (clearance − kerf) / 2. With kerf and
clearance 0 the panels fill the walls exactly.

**Cutting.** The named face set **Cut sheet** holds the broad face of each panel. File › Export…, DXF or
SVG, with the face set "Cut sheet" lays all six panels on one sheet at true size, one layer per panel
(`file.export {"path": "box.svg", "set": "Cut sheet"}`, or
`craft3d-cli convert box.3dcraft box.dxf --set "Cut sheet"`).

**Checked.** `check-range` passes at the default, all 512 corners and random points (also with
`--deep`). Regeneration median about 90 ms, at most about 700 ms native release.

Source: the showcase model of 3DCraft's `plan/laserbox.md` (2026-10-16), made into a Jig.
