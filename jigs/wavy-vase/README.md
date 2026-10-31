# Wavy vase

A vase or plant-pot cover whose wall waves and twists, drawn from a formula, for 3D printing in vase mode.
Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Bottom diameter | Shape | 70 mm | 40 to 150 mm, step 1 mm |
| Top diameter | Shape | 90 mm | 40 to 180 mm, step 1 mm |
| Height | Shape | 120 mm | 40 to 220 mm, step 1 mm |
| Belly | Shape | 10 mm | −10 to 20 mm, step 0.5 mm |
| Waves | Waves | 8 | 3 to 12 (whole) |
| Wave depth | Waves | 5 % | 2 % to 100 / waves %, step 0.5 |
| Twist | Waves | 60 deg | −90 to 90 deg, step 1 deg |

**How it is built.** Five cross-sections, at 0, ¼, ½, ¾ and the full height, each a closed curve from
formulas (`sketch.curve`): r(t) = R (1 + depth/100 · cos(waves · t)), turned by the twist times the height
fraction. R follows the height: a straight taper from the bottom to the top radius plus belly × sin(180° ×
fraction). One smooth loft runs through the five sections. Each section is drawn as two halves so the loft
can be told where every loop starts (`start`), which keeps the twist exactly as drawn.

**Printing.** The model is solid on purpose: slice it in **vase mode** (Cura: *Spiralize outer contour*,
PrusaSlicer: *Spiral vase*) with a few bottom layers. You get a thin, watertight wall and a closed bottom,
printed in one continuous spiral; as a cover it takes a nursery pot of a slightly smaller diameter.

**Document tolerance.** 0.001 mm (`new.json`) instead of the default 1e-6 mm: the formula curves are fitted
within half the tolerance, and at 1e-6 mm each section needs some 780 control points (regeneration about
8 s); at 0.001 mm some 160 (well under a second). A micrometre is far below what a printer resolves.

**Checked.** `check-range` passes at the default, 64 corners and 32 random points, and with `--deep`
(16 random points); regeneration median about 110 ms, at most about 0.8 s native. The ranges were
narrowed while checking: more than 12 waves or more than 90° of twist on a short, wide vase gives a loft
3DCraft 0.1.0 cannot mesh for its self-intersection check. At 3DCraft 4e7fa69a two random points fail that way inside
the range (twist 51° on a vase 78 mm high, 7 waves; twist -48° on one 186 mm high, 10 waves): the loft's
self-intersection check needs about 1700 to 2500 segments per side at the document's 0.001 mm tolerance, above
its limit of 1024. A known 3DCraft limit (the loft's self-intersection check meshes at most 1024 segments per side),
taken up on the 3DCraft side; the Jig neither works round it nor narrows its range for it.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.

**Colour.** Terracotta (#C2694B), from the Jigs palette.
