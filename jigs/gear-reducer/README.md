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

**Undercut.** Pinions of 14 to 16 teeth without profile shift are undercut when they are hobbed with the
ISO 53 rack (the theoretical limit is 17 teeth at 20°). The radial foot drawn below the base circle is
not a manufactured root, and its sharp corner at the root circle is a stress raiser. A real 14 to 16
tooth pinion needs a profile shift x ≥ (17 − z) / 17 or accepts a slight undercut. The mating tip clears
the drawn foot with the 0.12 mm backlash: the mesh interference assertions hold at every checked point,
and a review simulated the meshes through a pitch without contact.

**No load rating.** The sizes follow from geometry only: modules, shaft seats, keys and bearings are
chosen so the parts fit, not from a torque. There is no tooth strength calculation (ISO 6336), no shaft
torsion or bending check and no bearing life; size a real reducer for its load before making it.

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
the shaft always steps down from the gear to the bearing, in the end walls,
max(5 mm, c_w) from the cavity. A bearing is drawn as an inner and an outer ring and eight balls.

**Housing.** A cast box split on the shafts' plane, its four corners along the shafts rounded (the input
end round about the input shaft), the cavity `c_w` round every gear's tip and along the shafts (at least 5 mm there), and at least as wide
as the bearing seats, end walls as thick as the widest bearing + 4 mm, four bolting ears with M6 bolts (ISO 4017)
and nuts (ISO 4032), an M12 fill plug on the rear half and a drain plug on the front half. Cast aluminium
EN AC-42100; gears 42CrMo4, shafts C45, bearings 100Cr6.

**What makes every point of the form a valid reducer.** The published ranges are fixed; where a value
would not fit the gears, the model moves it, as the `spur-gear` Jig keeps its hub. **The form shows the
value you set, not the value used:** `document.inspect` (or the variables in the window) shows what the
model uses: `z_1`, `z_3` (pinion teeth), `z_2`, `z_4` (wheel teeth), `b_1`, `b_3` (face widths) and
`i_actual` (the ratio built). At module 1 and ratio 20, for example, teeth3 14 becomes 30, teeth1 14
becomes 21 and width3 60 mm becomes 15 mm. Ranges that follow the module were
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

What each stage-1 module allows (`python3 gen.py --table`; pinion 3 for teeth1 = 18, raised where
needed, and 62xx bearings; the stage-2 module in brackets):

| Module 1 | Pinion 1 teeth from | Face width 1 | Pinion 3 teeth (z3_lo-z3_hi) at ratio 5 / 10 / 20: same module | one size up | two sizes up |
|---|---|---|---|---|---|
| 1 mm | 21 | 8 to 15 mm | 31-40 / 31-40 / 30-40 (1 mm) | 25-40 / 26-40 / 25-40 (1.25 mm) | 21-34 / 22-40 / 21-40 (1.5 mm) |
| 1.25 mm | 18 | 8 to 18.75 mm | 27-40 / 27-40 / 26-40 (1.25 mm) | 22-37 / 23-40 / 22-40 (1.5 mm) | 17-27 / 17-39 / 17-40 (2 mm) |
| 1.5 mm | 17 | 8 to 22.5 mm | 26-40 / 26-40 / 25-40 (1.5 mm) | 20-34 / 19-40 / 19-40 (2 mm) | 16-27 / 16-38 / 15-40 (2.5 mm) |
| 2 mm | 14 | 10 to 30 mm | 23-40 / 24-40 / 23-40 (2 mm) | 19-38 / 19-40 / 19-40 (2.5 mm) | 16-31 / 16-40 / 16-40 (3 mm) |
| 2.5 mm | 14 | 12.5 to 37.5 mm | 22-40 / 22-40 / 22-40 (2.5 mm) | 18-40 / 19-40 / 19-40 (3 mm) | 14-29 / 14-40 / 14-40 (4 mm) |
| 3 mm | 14 | 15 to 45 mm | 21-40 / 22-40 / 22-40 (3 mm) | 16-37 / 16-40 / 16-40 (4 mm) | 16-37 / 16-40 / 16-40 (4 mm) |
| 4 mm | 14 | 20 to 60 mm | 20-40 / 21-40 / 21-40 (4 mm) | 20-40 / 21-40 / 21-40 (4 mm) | 20-40 / 21-40 / 21-40 (4 mm) |

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
- the moving parts (gears, shafts, keys, spacers) do not interfere with the housing; the gears clear
  the housing by at least c_w − 0.1 mm, round their tips and along the shafts (the end walls are
  max(5 mm, c_w) away); every bearing seated in the housing (at most 0.02 mm);
- wheel 2 clears the output shaft, wheel 4 the input shaft, pinion 3 the input shaft and its spacer.

**Checked over the range** (3DCraft `main` at 3faaaea0, seed 1, `MALLOC_ARENA_MAX=2`): the points of
`scripts/check.sh` all pass: 74 of 74 with every corner (all 64 of the corner subset, the 9 other
choices, the defaults) and 26 of 26 with the 16 random points; with `--deep`, 30 of 30 (16 corners, 9
choices, 4 random). A regeneration takes 2.3 to 2.6 s (median), at most about 7 s; a point with its 22
assertions about a minute (the two flank clearances take most of it); a run peaks at 1.9 GB. The
three *notProven* clearances are warnings at every point (see *Limits*). The corner run found a real
fault on the way: with a 3 mm wall the bolting ears reached 1 mm into the cavity (the gears' clearance
to the housing failed), fixed.

**Limits of 3DCraft today** (found in the test drive; the Jig works within them):
- A clearance between spline faces (the involute flanks) is found but not proven: the two flank
  clearance assertions and the gears' clearance to the housing report *notProven* (a warning, never passed),
  with the value found (0.0564 mm for jn / 2 = 0.0564 mm at the defaults: as designed). `check-range`
  counts a point with a *notProven* assertion as passing (only failed assertions and assertions in error
  fail a point), so the assertions are kept as they are.
- Interference between bodies that touch is decided only with a gap: the bores, keys and bearing seats
  have a 0.01 mm fit clearance (`fit_cl`) instead of a press fit, so "no interference" and "seated"
  can be told apart.
- An `extent` assertion over spline faces after cuts measures too wide, so the overall size is not
  asserted.
- `m` and `mod` are reserved names: the module is `mn`.
- A range check holds a lot of memory with interference assertions on spline bodies: memory grows from
  point to point (glibc's per-thread arenas account for about half of it; `MALLOC_ARENA_MAX=2` keeps a
  full run under 2 GB), and the two flank clearances take most of the time (about a minute a point).

**Changed from the test drive's model.**
- The gears are drawn as one outline per gear (the `spur-gear` Jig's chained pattern) instead of cutting
  each tooth space with a boolean, which makes a regeneration several times lighter; the root has the
  radial foot of `spur-gear` instead of a root fillet of 0.38 modules.
- The shaft diameters (12, 17 and 25 mm there) follow the gears; each bearing's bore is strictly below
  its gear seat (there a 17 mm seat took a 17 mm bearing, a step of no length in the shaft's profile,
  which fails once the values move); 608/628 bearings were added for a 10 mm seat.
- The housing's ends grow with the bearings; the bolting ears reach through the wall to 0.5 mm short of
  the cavity (with a thin wall they reached into it, found by the gears' clearance assertion).
- An assertion was added: pinion 3 clears the input shaft and its spacer.
- The room between the gears and the end walls is max(5 mm, c_w) (5 mm there), so the gears' clearance
  assertion checks c_w itself (it checked min(c_w, 5 mm) − 0.1 mm there).
- Narrowed: modules 1 to 4 mm (0.5 to 8 mm there), ratio 5 to 20 (4 to 30 there), input angle ±360°
  (±720° there); stage 2's module is chosen relative to stage 1's; the teeth and face widths are kept in
  place by formulas (above). The public inputs are `teeth1`, `teeth3`, `width1`, `width3` (`z_1`, `z_3`,
  `b_1`, `b_3` there, now the values the model uses).

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

## As an assembly

`dist/gear-reducer.3dcraftasm` puts this Jig's moving parts together as a 3DCraft assembly that turns: the
rear half of the housing (`HousingTop`), the three shafts and the four gears are instances of the Jig at
its defaults, each picking one body by the feature that made it. The front half, the bearings, keys,
spacers and bolts are left out (the front half would hide the gears; the keys and bearings turn with
their shafts). It is packed: it carries a copy of the Jig and opens anywhere. `assembly/gen.py` writes the
command batch that builds it (`assembly/01-gear-reducer.json`) and `assembly/check.json`;
`scripts/asm.py all gear-reducer` builds and checks it.

**Mates.** Every frame but the world's z axis is a circular edge: a circle's frame starts where the circle starts, and the Jig
draws every circle from +x and turns a body with its shaft, which at the defaults leaves every gear at 0°
(63 and 49 teeth are odd: only an even wheel is turned half a pitch). So a mate's zero is the Jig's own
tooth phase. The edges and their heights were read from the Jig's bodies (`document.edges`); an offset is
the difference of two heights along the shaft. At rest every instance is exactly where the Jig puts it,
which the check proves.

| Mate | Kind | Between |
|---|---|---|
| `HousingHeld` | fixed | the world's z axis and the input shaft's bearing seat in the housing |
| `Shaft1` to `Shaft3` | revolute | shaft k and its bearing seat in the housing |
| `Keyed1` to `Keyed4` | fixed | gear k and its shaft (the key's job) |

**Couplings.** `Stage1` couples shaft 1 and shaft 2 (ratio z2 / z1 = 63 / 18), `Stage2` shaft 2 and shaft 3
(z4 / z3 = 49 / 17): external gears, so each pair turns opposite ways. **Motion:** the timeline t drives
the input, `Shaft1_angle = 360 deg * t`, one turn.

**Assertions** (at every regeneration, and over the motion):
- *Output turns at z1 z3 / (z2 z4) of the input*: the output's turn is measured on the model, not read
  from the solver: the output shaft's keyway (cut along +x at rest) puts the centroid of the shaft's
  section at mid-key 0.68 mm off its axis, on the far side; its direction must be the input's turn × 18 ×
  17 / (63 × 49) = 1 / 10.088 within 0.001° (and the centroid at least 0.3 mm off the axis, so the
  direction means something);
- *Stage 1 / Stage 2 mesh with the backlash*: the flank clearance between 0.3 and 0.7 of the normal
  backlash jn = 0.12 mm × cos 20°, as the Jig asserts it;
- *No part overlaps another* (the housing, shafts and gears).

**Checked** (3DCraft 57ba7632, `scripts/asm.py check gear-reducer`, about 8 minutes):
- at rest: solved with no degree of freedom left, and all eight instances exactly where the Jig puts them;
- over the motion, sampled (what happens between two samples is not seen): 65 moments over the input's
  turn (5.6° apart, about a quarter of a pinion tooth), 33 over one tooth of pinion 1 (t from 0 to 1/18,
  stage 1's whole mesh cycle) and 33 over one tooth of pinion 3 (t from 0 to 63 / (18 × 17), stage 2's).
  The output's turn passes at every sample (largest miss 5.4e-7 rad, against the 1.7e-5 rad allowed) and
  no part overlaps another. The flank clearances are found within their bounds at every sample (stage 1
  0.0550 to 0.0564 mm, stage 2 0.0554 to 0.0564 mm, against jn / 2 = 0.0564 mm as designed) but are
  mostly *notProven*: 3DCraft proves only a lower bound of 0.014 to 0.029 mm between these spline flanks,
  as in the Jig itself (see *Limits of 3DCraft today*); a warning, not a pass.
- What the couplings decide and what is checked independently: the ratios z2 / z1 and z4 / z3 are put in
  by the couplings, so the output's turn checks that they are composed the right way round and with the
  right signs; that they are the gears' own ratios is checked by the teeth: a sign reversed in stage 1
  (tried) makes the gears overlap at the next sample; a wrong ratio (not tried) would let the teeth drift
  out of phase until they meet.

Bodies other than the moving ones, and the Jig's other parameters, are not in the assembly: the edges'
heights and the tooth counts are those of the Jig at its defaults, written into `gen.py`, so the assembly
places that one reducer. The edge names belong to the Jig's current `build.json`: after the Jig is
rebuilt, run `scripts/asm.py all gear-reducer` again (the packed copy is the Jig as it was); the check at
rest (every instance exactly where the Jig puts it) is what catches an edge that moved.

**Missing in 3DCraft** (found building this assembly):
- No measure of a joint's angle or an instance's pose for an assertion: the output's turn is measured from
  the centroid of a section through the output shaft's keyway, at a height (43 mm) copied from the Jig.
- `motion.check` on an assembly holds memory for every moment it measures (about 25 MB a moment with
  `MALLOC_ARENA_MAX=2`, far more without), so `scripts/asm.py` runs it 17 moments at a time.
- A clearance between spline flanks is found but not proven (as in the Jig).
