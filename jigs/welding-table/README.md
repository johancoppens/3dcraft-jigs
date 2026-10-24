# Welding table

A system welding table in the style of the 16 mm and 28 mm block tables (Siegmund, Demmeler and the
like): a perforated top plate, side plates on all four edges with the same hole grid, a grid of
half-lapped ribs under the top, and optional legs with a frame. Every plate is a flat part to cut by laser
or plasma. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| System | System | System 16 | System 16, System 28 (table `systems`) |
| Length | Size | 1200 mm | 600 to 2000 mm, step 50 mm |
| Width | Size | 800 mm | 400 to 1200 mm, step 50 mm |
| Rib spacing | Ribs | 4 | 2 to 8 holes |
| Lap clearance | Ribs | 0.3 mm | 0 to 1 mm, step 0.05 mm |
| Base | Base | Legs and frame | None, Legs, Legs and frame |
| Working height | Base | 900 mm | 600 to 1000 mm, step 10 mm |

| System | Holes | Grid | Top plate | Sides (with the top) | Ribs | Legs |
|---|---|---|---|---|---|---|
| System 16 | Ø16 mm | 50 mm | 12 mm | 100 mm | 10 mm | 80 mm square |
| System 28 | Ø28 mm | 100 mm | 25 mm | 200 mm | 15 mm | 100 mm square |

**How it is built.** The working surface is z = 0. The top plate is a rectangle with a grid of holes
(one sketch circle, patterned in two directions), nX = floor(length / grid) by nY = floor(width / grid),
centred, so a 1200 × 800 System 16 top has 24 × 16 holes, the outer ones 25 mm from the edge. The front and
back sides run the full length under the top's edge, the left and right sides between them; each carries
floor(side height / grid) rows of holes on the same columns as the top, half a grid apart from the top
surface (25 and 75 mm for System 16, 50 and 150 mm for System 28). Ribs run both ways under the top, as
deep as the sides, one every *rib spacing* holes on the lines between two holes (so no hole is blocked),
centred as far as the grid allows; where they cross they are half-lapped, the cross ribs slotted from the
top and the long ribs from below, the slots the rib thickness plus the lap clearance. **Base**: four legs
with 10 mm foot plates in the corners under the sides, reaching from the floor to the sides at the working
height, and with *Legs and frame* rails (0.75 × the leg size) between them 150 mm above the floor.

**Colours.** Top, sides and ribs steel (#7D858C, metallic); legs and frame painted slate blue (#5B7299).

**Cutting.** The named face set **Cut sheet** holds the top, the four sides and every rib. File › Export…,
DXF or SVG, with the face set "Cut sheet" gives every plate on one sheet at true size, one layer per body
(`file.export {"path": "table.dxf", "set": "Cut sheet"}`; add `"width": "3000 mm"` to wrap the parts into
rows). The legs and rails are tube stock, not in the sheet; STEP exports the whole table. The plates are
nominal sizes: give your cutter's kerf compensation to the shop, and machine or grind the top flat after
welding as real system tables are.

**Checked.** Two assertions count the holes: nX × nY in the top and 2 × rows × (nX + nY) in the sides.
`check-range --deep` passes: 100 of 100 points (64 of the corners, every choice, 32 random), and
132 of 132 with `--samples 64 --seed 7`; 3DCraft `main` at baf6c1f5. Regeneration median about 25 ms, at most
about 120 ms native. The default cut sheet is 557 closed paths: 13 plates and 544 holes.

Earlier versions of this Jig were a FabBlock-style inch table (`plan/weldtable.md` of 3DCraft); this one
replaces it with a metric block table.
