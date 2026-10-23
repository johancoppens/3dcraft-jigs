# Welding table

A fixture welding table (FabBlock style) to cut from 1/4 in steel plate: a top plate with a 2 in grid
of 16 mm holes, on a grid of half-lapped ribs whose tabs sit in slots shaped as plug-weld pockets.
The document is in inches (the holes stay 16 mm). Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Length (x) | Size | 36 in | 24 to 48 in, step 1 in |
| Width (y) | Size | 24 in | 18 to 36 in, step 1 in |
| Kerf | Cutting | 0.2 mm | 0 to 0.3 mm, step 0.01 mm |
| Clearance | Cutting | 0.15 mm | 0.05 to 0.25 mm, step 0.01 mm |
| Tabs per cell | Joints | 2 | 1 to 3 |

The size is capped at 48 × 36 in so that a change regenerates quickly, also in the browser (single
threaded). Native release: median about 26 ms, at most about 100 ms per regeneration over the whole range.
The rib spacing (about 6 in), plate thickness (1/4 in), height (6 in) and tab and slot sizes are fixed in
the design; edit them with *Open for editing* if you need other stock.

**Cutting.** The named face set **Cut sheet** holds the top plate and every rib. File › Export…, DXF or
SVG, with the face set "Cut sheet" gives every part on one sheet at true size, kerf included, one layer per
body (`file.export {"path": "table.dxf", "set": "Cut sheet"}`; add `"width": "48 in"` to wrap the parts
into rows).

**Checked.** `check-range` passes at the default, all 32 corners and random points (also with `--deep`).

Source: the showcase model of 3DCraft's `plan/weldtable.md` (nested sketch patterns, `gen3.py`), made
into a Jig; the plug welds of the showcase are left out.
