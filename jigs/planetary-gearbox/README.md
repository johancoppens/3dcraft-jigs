# Planetary gearbox

A planetary (epicyclic) gear set with true involute teeth: a sun, 3 to 6 planets, an internal ring gear
and a carrier with pins and an output shaft, each its own body and colour. Formulas, conditions, a table
and patterns together: the planets' teeth follow from the sun and the ring, the ring's range is built so
that every value assembles, and assertions check the result on the model. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Module | Gears | 1.5 mm | 0.8, 1, 1.25, 1.5, 2, 2.5 or 3 mm (table `modules`) |
| Planets | Gears | 3 | 3 to 6 |
| Sun teeth | Gears | 12 | `ZsMin` (10, 11, 17 or 24 for 3, 4, 5 or 6 planets) to 30 |
| Ring teeth | Gears | 48 | `ZrMin` to `ZrMax` in steps of `2 Nq` (see below) |
| Face width | Size | 10 mm | 4 to 30 mm, step 0.5 mm |
| Backlash | Size | 0.1 mm | 0.05 to 0.3 mm, step 0.01 mm |

At the defaults the planets have 18 teeth and the reduction (sun in, carrier out, ring held) is
`ratio = 1 + Zr / Zs` = 5.

**The formulas and conditions.** With sun teeth Zs, ring teeth Zr and N planets (KHK, *Gear Technical
Reference*, planetary gears):

```text
Zp        = (Zr - Zs) / 2                   planet teeth (coaxial condition, standard gears)
a         = module (Zs + Zp) / 2            centre distance sun - planet
assembles = mod(Zs + Zr, N) == 0 && mod(Zr - Zs, 2) == 0      the planets fit evenly spaced
tipGap    = 2 a sin(180 deg / N) - module (Zp + 2)              between neighbouring planets' tips (> 0: adjacency)
```

A Jig's range check must pass everywhere in the range, so the ring's range is built from these: Zr = Zs
+ 2 Zp with Zp ≡ −Zs (mod Nq), Nq = N (odd) or N / 2 (even), which makes (Zs + Zr) / N whole; so the
ring's teeth run in steps of 2 Nq from `ZrMin` (Zp at least 17) to `ZrMax` (Zp at most 30, and at most
what keeps `tipGap` ≥ module / 2). For 4, 5 and 6 planets that range is empty for a small sun, hence
`ZsMin`. Change the sun or the planets and the form moves the ring to the nearest valid value (it says
so).

Why at least 17 planet teeth: the ring's tips must meet the planet's flanks on its involute, above its
base circle, or they foul the planet's foot (involute interference of an internal pair, KHK). The ring has
a stub addendum of 0.8 module, and the variable `ringTipOk` is that condition:
√((rp_ring − 0.8 m)² − rb_ring²) ≥ (rp_ring − rp_planet) sin 20°. With 17 planet teeth it holds for every
sun of 10 to 30 teeth. (Found by the Jig's own checks: a sun of 40, planets of 8 and a ring of 56
overlapped by 0.07 mm³.)

Two assertions check the built gearbox at every regeneration:
- *Assembly conditions*: the number of planet bodies is N when `assembles`, `ringTipOk` and
  `tipGap ≥ module / 2` hold (0 otherwise: it fails);
- *Neighbouring planets clear each other*: the measured clearance between planets 1 and 2 is at least
  0.4 module.

That the gears mesh without overlap was checked outside the Jig, with `document.interference` on every
pair of sun, planets, ring and carrier at ten points (each planet count at its smallest and largest sun,
modules 1 to 3, backlash 0.05 mm): all clear. As an assertion it is too heavy for now: an interference
held about 1.2 GB over 13 points of a range check, and a clearance between meshing gears took minutes and
came out *not proven*.

**How it is built.** Every gear is drawn as the `spur-gear` Jig draws one: one tooth from the involute's
formula (`sketch.curve`), tip and root arcs, a radial foot below the base circle, repeated round as a
chained sketch pattern and extruded once. Addendum 1 module, dedendum 1.25 modules, pressure angle 20°.
Each tooth is thinned by backlash / 4 on each flank on the pitch circle. The ring's tooth spaces are
drawn as such an outline with Zr teeth whose tip is the ring's root circle (pitch + 1.25 module) and
whose root is the ring's tip circle (pitch − 0.8 module), thickened by the backlash: the space of an internal
gear has the shape of an external gear's tooth. The ring's tips lie outside its base circle (Zr ≥ 44),
so its flanks are involute to the tip (a radial tip, as the spur gear has at its root, fouled the
planets at module 3).

Planet 1 sits on the +x axis, turned half a tooth when Zp is even (and the ring with it) so a space faces
the sun's tooth. Planet k sits at φ = 360° (k − 1) / N and is turned about its own centre by
φ (Zs + Zp) / Zp, the turn it makes when the carrier moves by φ round a fixed sun; it then meshes with
the ring exactly when (Zs + Zr) / N is whole. Planets 4 to 6 are switched on by `N >= k`.

The sun has a bore of half its root radius (1 to 4 mm); each planet a bore of the pin + 0.15 mm. The ring
is a band of max(3 modules, 8 mm) round its teeth with six M3 holes. Bores, band and holes are circles in
the gears' own sketches, so no gear needs a boolean (light enough for the web version). The carrier is a
spider 0.5 mm above the gears: a hub, an arm and a pin per planet (a circular pattern of N), and an output
shaft.

**Fails at 3DCraft 4e7fa69a (open).** `check-range` passes 61 of 87 points: since 3DCraft 06fb1f81
(2026-10-26) a step counts from the minimum only when the minimum is a value, from 0 when it is a formula, so
the ring's step of 2 Nq no longer runs from `ZrMin`: the range check (and the form) take ring teeth such as 48
with a sun of 10 and 3 planets, which the planets cannot share evenly, and *Assembly conditions* fails (or
the planet's outline, at an odd Zr - Zs). The ring's valid values cannot be put on a grid from 0; the fix
changes the parameters (for instance a ring size index from 0 whose teeth are ZrMin + 2 Nq k) and waits for
the developer.

**Checked** before that, at 3faaaea0: `check-range --deep` passes 87 of 87 points (all 64 corners, every module, 16 random;
seed 1), and without `--deep` 103 of 103 (32 random). One regeneration takes about 0.6 s and 215 to 370
MB native.

**Sources.**
- ISO 53:1998, *Cylindrical gears: standard basic rack tooth profile* (20°, addendum 1 m, dedendum
  1.25 m); ISO 54:1996, *modules* (the table's series).
- KHK Gears, *Gear Technical Reference*, "Planetary gear mechanism": the coaxial, assembly and adjacency
  conditions (khkgears.net).
- The involute construction and the formula curves from this collection's `spur-gear` Jig.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.

## As an assembly

`dist/planetary-gearbox.3dcraftasm` puts this Jig's bodies together as a 3DCraft assembly that moves:
the ring, the carrier, the sun and three planets are instances of the Jig, each picking one body by the
feature that made it. The assembly holds the Jig's public parameters as its own variables (module 1.5 mm,
sun 12, ring 48, face width 10 mm, backlash 0.1 mm, 3 planets) and passes them to every instance, so all
six share one configuration. Some values are copies of the Jig at its defaults: the module (1.5 mm, the
Jig's `moduleSize` 4), the carrier's 0.5 mm gap and 4 mm output shaft (the joint's height), and the edge
names (`gen.py`, read with `document.edges` from the Jig's current `build.json`). Zs, Zr, w and backlash may
be changed in the assembly; another module would misplace the carrier's joint. After the Jig is rebuilt,
run `scripts/asm.py all planetary-gearbox` again (the packed copy is the Jig as it was); the check at rest
(every instance exactly where the Jig puts it) is what catches an edge that moved. It is packed: it carries a copy of the Jig and opens anywhere.
`assembly/gen.py` writes the command batch that builds it (`assembly/01-planetary-gearbox.json`) and
`assembly/check.json`; `scripts/asm.py all planetary-gearbox` builds and checks it.

**Mates.** Every mate's frame is a circular edge, which the Jig turns with its body, so a mate's zero is
the Jig's own tooth phase and every instance stays exactly where the Jig puts it.

| Mate | Kind | Between |
|---|---|---|
| `RingHeld` | fixed | the world's z axis and the ring's outer circle (turned by the Jig's `rTurn`) |
| `Output` | revolute | the world's z axis and the top edge of the carrier's output shaft |
| `SunOnCarrier` | revolute | the carrier's output shaft and the sun's bore |
| `Pin1` to `Pin3` | revolute | carrier pin k and planet k's bore (the angle: planet k's tooth phase) |

**Couplings.** Each mesh is a gear coupling between two joints: `SunPlanetk` (sun on the carrier s and
planet k on its pin p_k, ratio Zp / Zs: s + (Zp / Zs) p_k = 0, an external pair) and `PlanetRingk`
(planet k and the carrier's turn c, ratio Zr / Zp: p_k + (Zr / Zp) c = 0, a planet rolling in the fixed
ring). Willis' formula is not written into the model; it follows from the meshes.

**Motion.** The timeline t drives the sun's joint on the carrier, `SunOnCarrier_angle = 360 deg * t`: one
turn of the sun relative to the carrier, during which the carrier turns a quarter and the sun 450 deg on
the housing. The sun is the input of the gearbox, so it would be driven on the housing. 3DCraft couples
two joints at a time, though, and the sun meshes with planets whose pins turn with the carrier: the mesh
ties three angles, the sun's, the planet's and the carrier's. So the sun's joint sits on the carrier, and
t drives that joint (see *Missing in 3DCraft* below).

**Assertions** (measured at every regeneration, and over the motion by `motion.check`):
- *Carrier turns as Willis' formula says*: the carrier's turn, measured on the model (the centroid of
  planet 1's mid-plane section goes round the sun with the carrier), equals s Zs / Zr, which is Willis'
  (s + c) / c = 1 + Zr / Zs solved for c, within 0.01° (3.9 µm at the planet's centre; the assembly is
  solved to its tolerance of 1 µm, so a tighter bound would test the solver's rounding);
- *Sun and planet 1 mesh with the backlash* and *Planet 1 and the ring mesh with the backlash*: the
  clearance between their flanks between 0.3 and 0.7 of the normal backlash jn = 0.1 mm × cos 20°;
- *No part overlaps another*.

**At 3DCraft 4e7fa69a** (`scripts/asm.py all`): as below, except that over the whole turn Willis' formula is
*notProven* at a moment where 3DCraft's boolean cannot cut planet 1 at the plane its centroid is measured with
("imprint lost: a curve in which two faces cross does not divide them"; a 3DCraft limit, reported); over one
sun tooth it passes, and Willis from the traces is 5.000000000 (worst miss 8.1e-13 deg).

**Checked** (3DCraft 57ba7632, `scripts/asm.py check planetary-gearbox`, about 7 minutes):
- at rest: solved with no degree of freedom left, and all six instances exactly where the Jig puts them;
- over the motion, sampled (what happens between two samples is not seen): 65 moments over a whole turn
  of the sun on the carrier, and 33 moments over one sun tooth (t from 0 to 1/12), the meshes' whole
  cycle. Willis' formula passes at every sample (largest miss 7.6e-6 rad, 0.00043°, against 0.01°) and
  no part overlaps another.
  The two flank clearances are found within their bounds at every sample (0.0455 to 0.0470 mm sun to
  planet, 0.0446 to 0.0468 mm planet to ring, against jn / 2 = 0.047 mm as designed), but they are
  *notProven*: 3DCraft proves only a lower bound of 0.013 to 0.027 mm for a clearance between these
  spline flanks (as in the `gear-reducer` Jig); a warning, not a pass;
- Willis again, without the model's centroid measure: `view.trace` of a corner of a sun tooth and of
  planet 1's centre over the turn gives the sun's turn on the housing over the carrier's as 5.000000000
  = 1 + 48 / 12 (largest miss 7e-13 deg over 65 samples).
- What the couplings decide and what is checked independently: Willis' ratio is Zp / Zs times Zr / Zp,
  the couplings' values, so the Willis assertion and the traces check that the two meshes are composed
  the right way round and with the right signs (external, internal), not that they are the gears' own
  ratios. That is checked by the teeth: negative controls, run once on a copy, (a) one ring coupling
  reversed: its planet and the other two contradict each other, and the motion stops at t = 0 (a dead
  point); (b) all three reversed: the planets overlap the ring by 76 mm³ at the second of 9 samples over
  one sun tooth. With 3 samples, (b) passed: those samples fell on whole tooth pitches of the error, so
  a sampled check is only as good as its samples (hence 33 within one tooth here).

**Missing in 3DCraft** (found building this assembly):
- `coupling.add` couples two joints (gear, rack, screw). A planetary mesh ties three angles; 3DCraft's
  solver has a linear coupling of any number of joints (its "planetary stage"), but the command does not
  offer it. With it, the sun would turn on the housing and be driven there.
- No measure of a joint's angle or an instance's pose for an assertion: the carrier's turn is measured
  from the centroid of a planet's section.
- `motion.check` on an assembly holds memory for every moment it measures (about 25 MB a moment here with
  `MALLOC_ARENA_MAX=2`, about 300 MB without), so `scripts/asm.py` runs it 17 moments at a time.
