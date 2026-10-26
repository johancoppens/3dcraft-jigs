# Two-stage spur gear reducer

A two-stage spur gear reducer as an assembly: four involute gears, each keyed on a stepped shaft, six
deep-groove ball bearings, spacers, a split cast housing with bolts and nuts, a fill and a drain plug.
Set a target ratio and the tooth counts follow; the shafts, keys, bearings and housing follow the gears.
Every body is its own part with a material, so the model gives masses and exports as an assembly (STEP)
or as single parts. Licence: CC-BY-4.0.

The front half of the housing (and its drain plug) is hidden in the view so the gears show; it is built,
checked and exported like every other part.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Target ratio (`i_total`) | Ratio | 10 | 5 to 20, step 0.5 |
| Pinion teeth, stage 1 (`teeth1`) | Ratio | 18 | 14 to 30; raised to what a 10 mm shaft needs (see below) |
| Pinion teeth, stage 2 (`teeth3`) | Ratio | 17 | 14 to 40; kept between `z3_lo` and `z3_hi` (see below) |
| Module, stage 1 (`mi_1`) | Gears | 1.5 mm | 1, 1.25, 1.5, 2, 2.5, 3 or 4 mm (table `iso54`) |
| Module, stage 2 (`up_2`) | Gears | two sizes up (2.5 mm) | the same as stage 1, one or two sizes up the table (at most 4 mm) |
| Face width, stage 1 (`width1`) | Gears | 14 mm | 8 to 60 mm, step 0.5 mm; kept between max(8 mm, 5 modules) and 15 modules |
| Face width, stage 2 (`width3`) | Gears | 20 mm | 8 to 60 mm, step 0.5 mm; kept between max(8 mm, 5 modules) and 15 modules |
| Bearing series (`ser`) | Shafts | 62xx (medium) | 60xx (light) or 62xx (medium) |
| Gear-to-wall clearance (`c_w`) | Housing | 5 mm | 2 to 30 mm, step 0.5 mm |
| Wall thickness (`t_w`) | Housing | 6 mm | 3 to 20 mm, step 0.5 mm |
| Input shaft angle (`theta_in`) | Motion | 0° | −360° to 360°, step 1°: turn the input and every gear and shaft follows |

At the defaults: 18 / 63 and 17 / 49 teeth, ratio 63/18 × 49/17 = 10.09 (`i_actual`), shafts of 12, 17
and 25 mm, bearings 6200, 6202 and 6204, centre distances 60.75 and 82.5 mm.

**Ratio.** Stage 1 takes i1 = 1.1 √i (rounded to 0.01), stage 2 the rest: z2 = round(z1 · i1),
z4 = round(z3 · i · z1 / z2). The teeth are whole numbers, so the ratio built is close to the target
(the variable `i_actual`).

**Gears** (ISO 53 basic rack: 20° pressure angle, addendum 1 module, dedendum 1.25 modules). Each gear
is drawn as the `spur-gear` Jig draws one: one tooth from the involute's formula (`sketch.curve`), tip
and root arcs and a radial foot below the base circle, repeated round as a chained sketch pattern and
extruded once. Each flank is thinned by jt / 4 on the pitch circle, so a mesh has a circumferential
backlash jt = 0.12 mm (normal backlash jn = jt cos 20°). Centre distance module · (z1 + z2) / 2. A wheel
with an even number of teeth is turned half a pitch so a space faces its pinion's tooth; the input angle
turns pinion 1, and each gear follows by its ratio. Every gear has a hub of 10 mm (diameter
min(2 d + 6 mm, root diameter − 2 modules)).

**Shafts and keys.** The gear seats are standard diameters (10, 12, 15, 17, 20, 25, 30, 35, 40 mm; table
`shafts`): each gear holds the largest one whose DIN 6885 hub keyway leaves a rim of 2.5 modules under
the teeth. The intermediate shaft takes the smaller of its two gears' and no more than leaves room for
its bearing beside the input shaft's; the input shaft is no larger than the intermediate one; the output
shaft is at most two sizes larger than the intermediate one. Parallel keys DIN 6885 form A (round ends;
table `din6885`: width, height, shaft and hub depths) sit 0.01 mm inside their keyways all round, and the
bores are 0.01 mm over their seats (`fit_cl`, see *Limits*). Each shaft is a revolved profile: bearing
seat, collar, gear seat, bearing seat, with the input shaft's end out of the top and the output shaft's
out of the bottom (30 mm each). Spacers hold the gears against the collars.

**Bearings** (ISO 15 deep-groove ball bearings, series 60 and 62, bores 8 to 30 mm; table `brg`). Each
shaft gets the bearing with the largest bore smaller than its gear seat (608 or 628 under a 10 mm seat), so
the shaft always steps down from the gear to the bearing, in the end walls, 5 mm from the cavity. A bearing is drawn as an inner
and an outer ring and eight balls.

**Housing.** A cast box split on the shafts' plane, its four corners along the shafts rounded (the input
end round about the input shaft), the cavity `c_w` round every gear's tip and at least as wide as the
bearing seats, end walls as thick as the widest bearing + 4 mm, four bolting ears with M6 bolts (ISO 4017)
and nuts (ISO 4032), an M12 fill plug on the rear half and a drain plug on the front half. Cast aluminium
EN AC-42100; gears 42CrMo4, shafts C45, bearings 100Cr6.

**What makes every point of the form a valid reducer.** The published ranges are fixed; where a value
would not fit the gears it is kept in place by a formula (the model uses `z_1`, `z_3`, `b_1`, `b_3`,
which `document.inspect` shows), as the `spur-gear` Jig keeps its hub. Ranges that follow the module were
tried first, but a range check sets one choice at a time with the others at their defaults, and 18
teeth or 14 mm are outside such ranges at other modules. The formulas:
- Pinion 1: at least 14 teeth and enough for a 10 mm shaft with its key and a rim of 2.5 modules:
  z1 ≥ 2 (6.4 mm / m1 + 2.5 + 1.25) (21 teeth at 1 mm, 18 at 1.25 mm, 17 at 1.5 mm, 14 from 2 mm).
- Pinion 3: at most `z3_hi` (its tip stays 1 mm off the input shaft's spacer, with the largest shaft
  pinion 1 holds) and 40; at least `z3_lo`: what holds a 10 mm shaft, and enough that wheel 2 clears the
  output shaft's collar (that shaft as large as it may be at that point).
- Stage 2's module is never smaller than stage 1's (it carries more torque, and a smaller one would put
  wheel 2 into the output shaft).
- Face widths between 5 and 15 modules and at least 8 mm, so the longest key (12 mm wide, 40 mm shaft)
  fits its seat.

`python3 gen.py --sweep` mirrors these formulas and tries every module pair, the ratio in steps of 0.1,
every tooth count the formulas let through and both bearing series against the conditions they are made
for (no gear without a shaft, no keyway through a hub or rim, pinion 3, wheel 2 and wheel 4 clear of the
other shafts, bearing seats apart, every key fits its seat, the housing's end no wider than the
housing): 1 634 388 points, none failing; a wheel has at most 163 teeth.

**Checked by assertions** (22, at every regeneration):
- per gear: its key does not interfere with the gear or the shaft; the gear does not interfere with its
  shaft (8);
- per shaft: both bearings seated on it (clearance at most 0.001 mm) (3);
- stage 1 and stage 2 mesh without interference; the gears of different stages stay apart;
- stage 1 and stage 2 flank clearance between 0.3 and 0.7 of jn (half the normal backlash at the line of
  action is the expected value);
- the moving parts (gears, shafts, keys, spacers) do not interfere with the housing; gear-to-housing
  clearance at least min(c_w, 5 mm) − 0.1 mm; every bearing seated in the housing (at most 0.02 mm);
- wheel 2 clears the output shaft, wheel 4 the input shaft, pinion 3 the input shaft and its spacer.

CHECKED_RESULTS

**Limits of 3DCraft today** (found in the test drive; the Jig works within them):
- A clearance between spline faces (the involute flanks) is found but not proven: the two flank
  clearance assertions and the gear-to-housing clearance report *notProven* (a warning, never passed),
  with the value found (0.0564 mm for jn / 2 = 0.0564 mm at the defaults: as designed). `check-range`
  counts a point with a *notProven* assertion as passing (only failed assertions and assertions in error
  fail a point), so the assertions are kept as they are.
- Interference between bodies that touch is decided only with a gap: the bores, keys and bearing seats
  have a 0.01 mm fit clearance (`fit_cl`) instead of a press fit, so "no interference" and "seated"
  can be told apart.
- An `extent` assertion over spline faces after cuts measures too wide, so the overall size is not
  asserted.
- `m` and `mod` are reserved names: the module is `mn`.

**Changed from the test drive's model.** The gears are drawn as one outline per gear (the `spur-gear`
Jig's chained pattern) instead of cutting each tooth space with a boolean, which makes a regeneration
several times lighter; the root has the radial foot of `spur-gear` instead of a root fillet of 0.38
modules. The shaft diameters (12, 17 and 25 mm there) follow the gears; the housing's ends grow with the
bearings; the bolting ears reach through the wall to 0.5 mm short of the cavity; a pinion-3 assertion was added; the modules run
from 1 to 4 mm (0.5 to 8 mm there), the ratio from 5 to 20 (4 to 30 there), the second module is chosen
relative to the first, and the tooth and width ranges are formulas (see above).

**Sources.**
- ISO 53:1998, *Cylindrical gears for general and heavy engineering: standard basic rack tooth profile*;
  ISO 54:1996, *Cylindrical gears for general engineering and for heavy engineering: modules*.
- DIN 6885-1:1968, *Drive type fastenings without taper action; parallel keys, keyways, deep pattern*.
- ISO 15:2017, *Rolling bearings: radial bearings: boundary dimensions, general plan* (series 60 and 62).
- ISO 4017 hex bolts and ISO 4032 hex nuts (M6).
- The involute construction from this collection's `spur-gear` Jig.

Designed in the 3DCraft test drive of 2026-10-25, where an agent built the reducer headless with commands
only (`reducer.3dcraft`, 277 features, 21 assertions); this Jig adapts its generator. `build.json` was
written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the model.
