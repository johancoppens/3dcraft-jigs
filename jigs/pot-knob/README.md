# Potentiometer knob

A grippy knob for a potentiometer, rotary encoder or switch shaft, for 3D printing. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Shaft | Shaft | 6 mm D-shaft | 6 mm D-shaft, 6 mm round, 1/4 in D-shaft, 1/4 in round, 4 mm round, 3 mm round |
| Fit | Shaft | 0.15 mm | 0 to 0.4 mm, step 0.05 mm |
| Hole depth | Shaft | 11 mm | 5 mm to height − 3 mm, step 0.5 mm |
| Diameter | Knob | 24 mm | 14 to 50 mm, step 0.5 mm |
| Height | Knob | 16 mm | 10 to 30 mm, step 0.5 mm |
| Grip spacing | Knob | 3.5 mm | 2.5 to 8 mm, step 0.1 mm |
| Skirt | Details | on | on / off |
| Pointer | Details | on | on / off |

**How it is built.** A cylinder with a chamfered top (chamfer 8 % of the diameter, 0.6 to 2 mm), an
optional skirt (3 mm wider, 15 % of the height, 1.5 to 3 mm), grip grooves round the side and a pointer
groove on top along +x, in line with the D-flat. The number of grooves is computed from the circumference,
`max(6, round(pi × diameter / grip spacing))`, their radius is `clamp(0.3 × spacing, 0.5 mm, 0.07 × diameter)`
so the wall round a 1/4 in hole stays at least 2.5 mm. The shaft hole is the shaft's diameter plus the fit,
and for a D-shaft its flat sits at *across-flat − d/2* from the axis, moved out by half the fit.

**3DCraft features used.** A table of shafts (`table.set`: diameter and across-flat) with a choice parameter
taken from it (`choicesFrom`) and looked up as `shafts[shaft].d`; conditions (`clamp`, `if`, a comparison
for `hasFlat`); `feature.when` for the skirt, the pointer and the D-flat (a round shaft switches the flat
off); a circular pattern whose count is a formula; a chamfer on a circular edge.

**Checked.** `check-range` (16 random points, 64 of the 256 corners) passes for every shaft, also with
`--deep`; regeneration median about 20 ms, at most about 160 ms native. Because `check-range` keeps a
choice taken from a table at its default (a 3DCraft limitation at 0.1.0), each shaft was checked as the
default in turn. STL export closed, bounding box as set.
