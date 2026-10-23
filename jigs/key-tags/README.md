# Key tags

A sheet of key tags or name-tag blanks to laser-cut from plywood or acrylic (or to 3D-print): one per
student in a class, engraved afterwards. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Shape | Tag | Rounded rectangle | Rounded rectangle, Circle, Hexagon |
| Width | Tag | 50 mm | 20 to 80 mm, step 1 mm (circle: the diameter; hexagon: corner to corner) |
| Height | Tag | 20 mm | 12 to 50 mm, step 1 mm (rounded rectangle only) |
| Corner radius | Tag | 5 mm | 0.5 to 25 mm, step 0.5 mm (kept below half the smaller side) |
| Ring hole | Hole | 5 mm | 2 mm to min(8 mm, 12 mm − 2 × margin), step 0.5 mm |
| Hole margin | Hole | 3 mm | 1.5 to 5 mm, step 0.5 mm |
| Columns | Sheet | 2 | 1 to 6 |
| Rows | Sheet | 3 | 1 to 6 |
| Sheet thickness | Material | 3 mm | 1.5 to 6 mm, step 0.5 mm |
| Kerf | Laser | 0.15 mm | 0 to 0.3 mm, step 0.01 mm |

**How it is built.** Three variants, each switched by the shape (`feature.when` with `shape == 1`,
`shape == 2`, `shape == 3`): a block with four filleted corners, a disc, or an extruded hexagon, each with
its ring hole and repeated in columns and rows (a pattern of a pattern). Only the chosen one is built. The
hole sits on the tag's axis, its edge the margin from the left end; for the hexagon it is moved in so the
margin holds to both slanted edges ((hole/2 + margin) / sin 60°). As in the laser box, the bodies are the
*cut paths*: outlines grow by kerf / 2 and holes shrink by it.

**Cutting.** The named face set **Cut sheet** holds the top face of every tag. File › Export…, SVG or DXF,
with the face set "Cut sheet" lays all tags on one sheet at true size, lines and true arcs and circles
(`file.export {"path": "tags.svg", "set": "Cut sheet", "width": "300 mm"}`, or
`craft3d-cli convert tags.3dcraft tags.svg --set "Cut sheet" --width "300 mm"`); `width` is your laser
bed's width, the export starts a new row there. Add the names to engrave in your laser software.

**Checked.** `check-range` passes for each shape (each made the default in turn): 256 of the 1024 corners
and 32 random points, also with `--deep`; regeneration median about 5 ms, at most about 40 ms native.
SVG and DXF of the default sheet: 6 closed outlines with 6 holes, outer size 50.15 × 20.15 mm (kerf 0.15),
holes 4.85 mm.
