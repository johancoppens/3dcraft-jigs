# Strandbeest leg

Theo Jansen's walking linkage, the leg of his *Strandbeesten* (beach animals). One crank and eleven bars,
two of them rigid triangles, turn the crank's rotation into a foot path with a long, nearly flat stroke
along the ground and a high return. Drag the **crank angle** and the leg walks: every joint is solved by
formulas, and the foot's path is drawn in front of the leg (terracotta: the stance, slate blue: the
swing). The flat parts are cut from sheet (or printed) and joined with bolts or rod. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Crank length | Size | 15 mm | `crankMin` (8.5 to 12 mm, from the pin and the material) to 60 mm, step 0.5 mm |
| Crank angle | Size | 0° | 0 to 360°, step 1° |
| Legs | Size | 1 leg | 1 leg, or 2 legs half a turn apart on one axle |
| Material | Parts | Birch plywood, laser-cut | table `sheets` |
| Sheet thickness (`thick`) | Parts | 3 mm | the material's `tMin` (2 or 3 mm) to 6 mm |
| Bar width | Parts | 9 mm | `wMin` = hole + 2 × web to `wMax` = 0.75 × crank |
| Pins | Parts | M3 bolt | table `pins`: M3, M4, M5 bolts; 3, 4, 5 mm steel rod; 1/8 in brass rod |
| Pin clearance | Parts | 0.2 mm | 0.05 to 0.6 mm |
| Layer gap | Parts | 1 mm | 0.3 to 3 mm (a washer) |

The crank length sets the scale: every bar is Jansen's number times `crank / 15`. At the default 15 mm
the bars are Jansen's numbers in millimetres and the leg is 135 mm tall (`legHeight`); a 25 cm leg needs a
crank of about 28 mm. **Renamed (2026-10-30):** the sheet thickness was `t` and is `thick`: `t` is the name of 3DCraft's
timeline (a plain number from 0 to 1 that motion is a formula of), and with a thickness holding the name
this Jig could not be given a motion. Scripts that set `t` must set `thick` now. **Tables.** `sheets` gives each material's thinnest sheet and the least web
of material round a pin hole (1.5 mm for sheet, 1.6 mm for printed parts, four 0.4 mm perimeters).
`pins` gives the pin diameters.

## The linkage

Jansen's "holy numbers" (his units; the crank is m):

| a | b | c | d | e | f | g | h | i | j | k | l | m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 38.0 | 41.5 | 39.3 | 40.1 | 55.8 | 39.4 | 36.7 | 65.7 | 49.0 | 50.0 | 61.9 | 7.8 | 15.0 |

The crank turns about the axle O at the origin; the fixed pivot B sits `a` to the side and `l` below it.
x runs along the ground, z up, and the leg's layers stack towards the front (-y). With the crank angle θ
(counter-clockwise seen from the front):

```text
A = O + m (cos θ, sin θ)       crank pin
C = circ(A, j; B, b)           upper joint, above B
D = circ(B, d; C, e)           outer corner of the hip triangle B C D (sides b, d, e)
E = circ(A, k; B, c)           knee, below B
F = circ(D, f; E, g)           upper corner of the foot triangle E F G (sides g, h, i)
G = circ(F, h; E, i)           the foot
```

`circ(P, r; Q, s)` is a closed-form circle-circle intersection: with `dd = |PQ|`,
`al = (r² - s² + dd²) / (2 dd)` and `q = 1 - (al / r)²`, the point is `P + al u ± r sqrt(q) n`, `u` the
unit vector from P to Q and `n` it turned by 90°. `q` is the square of the sine of the angle at P, so the
circles meet while `q >= 0`. The sign picks the branch of Jansen's leg: C, F and G lie right of the
line from the first centre to the second, D and E left of it. The branch is the same at every angle, so
the leg never flips. These are the joint equations of Wang (2026), eq. 1-3,
with the same letters.

Each part is drawn once in its own frame (first pin at the origin, second pin along an axis) and placed by
a transform: turned by `atan2` of the line between the two joints it joins and moved to the first. Its
other holes land on their joints only when the linkage really closes, which the assertions measure.

The model also works the leg out at 24 crank angles (every 15°) for the foot path and the gait:

| Variable | What | At any size |
|---|---|---|
| `stride` | the foot path's length along the ground, one step per crank turn | 4.52 × crank (67.8 mm) |
| `stepHeight` | how high the foot lifts | 1.48 × crank (22.2 mm) |
| `stanceLength` | how far the foot moves over the 120° of crank round its lowest point | 3.07 × crank (46.0 mm) |
| `flatness` | the height spread over those 120°, as a part of `stride` | 0.57 % |
| `closeMin` | the least `q` of any joint at the 24 angles | 0.064 (the knee E, near its fold) |
| `legHeight` | top of the hip triangle (or the frame) to the foot | 8.97 × crank (135 mm) |

The foot moves forward (+x) on the ground while the crank turns counter-clockwise, so the walker walks
towards -x. With three or more legs phased over the turn, a foot is always in its flat stance: that is why
Jansen's beasts have so many.

**Why the bar lengths are not parameters.** The knee E almost folds once a turn (`closeMin` 0.064): Wang
(2026) reports that changing `k` by 2 % already breaks the assembly at some crank angles, and in this
Jig's own sweep a change of 1 % to every bar at once (the corners of that box) already spoils the flat
stance beyond 3 % of the stride. A form whose every point must give a working leg cannot offer the bars
over a useful range, so they stay document variables (`Ja` to `Jm`): **Open for editing** to try your own
numbers, and the assertions below tell you at once whether the leg still closes and walks flat.

## Layers and assembly

Seen from the front, from the frame outwards (the layer gap is a washer between layers):

| Layer | Parts | Pins through it |
|---|---|---|
| 0 | frame plate (O, B and a mounting hole M) | axle O, pivot shaft B |
| 1 | crank (O to A), hip triangle (B, C, D), foot triangle (E, F; the foot G has no pin) | O, A, B, C, D, E, F |
| 2 | bar j (A to C), bar c (B to E) | A, B, C, D, E, F |
| 3 | bar k (A to E), bar f (D to F) | A, D, E, F |

Parts on one layer stay apart over the whole turn, and a pin passes only layers whose parts stay clear of
it. `gen.py` checks that at every degree of crank before it writes `build.json` (`simulate()`): the
closest pair is bar k and bar f, and the closest pin to a part it passes is E to bar f, both 13.25 ×
crank / 15 between centre lines, so `wMax = 0.75 × crank` leaves at least 2 × crank / 15 (2 mm at the
default). The assertions measure it on the model at the form's crank angle. The axle may not reach layers 2 and 3: bars j and
k pass right over O once a turn, which is why the drive is behind the frame.

1. Cut the parts: the named face set **Cut sheet**, `file.export {"path": "leg.svg", "set": "Cut sheet", "width": "400 mm"}`
   (DXF works too), every flat part at true size with its pin holes (pin + clearance).
2. Fix the crank to the axle so they turn together: glue, a D-flat with a set screw, or two nuts on a
   threaded axle. Every other joint turns freely.
3. Put the axle through the frame (from behind) and the crank; the pivot shaft through the frame, the hip
   triangle and bar c.
4. Build outwards layer by layer with a washer between layers. Pin lengths between the outer faces (add a
   bolt's head and nut, or room for e-clips on rod):
   - A, D, E, F: three layers, `2 (thick + gap) + thick` (11 mm at the defaults);
   - C: two layers, `thick + gap + thick` (7 mm);
   - B: frame to layer 2, `2 (thick + gap) + thick` (11 mm);
   - O: the stub behind the frame (`dg = max(10 mm, 2 w)`, for a pulley, gear or crank handle) to the
     crank's face (25 mm at the defaults).
5. Tighten nuts until the joints turn without play (nylon lock nuts hold that setting), then turn the crank
   by hand once round: nothing should rub or catch.

**Two legs.** A second frame plate sits `dg` behind the first, held by spacers at B and M (with a bolt
through M). The second leg is the same stack behind it, mirrored front to back, its crank half a turn
round from the first on the same axle; the pivot shaft runs through both. Drive the axle with a pulley or
gear between the frame plates. For a walker, mount several of these on one chassis with the cranks phased
evenly over the turn.

**3D printed.** Print every part flat; 0.3 to 0.4 mm of clearance suits most printers.

## Assertions (checked at every regeneration)

Measured on the model:
- *No part overlaps another*: pins pass their holes, and nothing on one layer runs into another part.
- *Pin X sits in its hole in part P*, for every pin and every part it joins (17): the clearance from the
  pin to the part is at most half the clearance (plus 0.005 mm), and with no overlap that puts the pin
  inside its hole. A part drawn from its bar length and turned to its joints has its far hole on the joint
  only when the joints are where the bar says.
- *Parts on one layer stay apart* (crank, hip and foot triangle; j and c; k and f): at least 0.5 mm.
- *The leg runs free of its frame*: the front leg's box ends at least half the layer gap in front of the
  frame's front face (measured exactly as a box). The second leg is the same stack behind the second
  frame, from the same formulas mirrored; the overlap check covers it.
- *Stance is flat*: the stance tube (the foot path over the 120° of crank round its lowest point) is at
  most 3 % of `stride` high, plus the tube.
- *Foot path as wide as the stride*: the path's measured width matches `stride`.
- *Only the feet reach down to the ground*: everything but the foot triangles stays at least `stepHeight`
  above the lowest point of the foot, so the leg clears the ground and steps over what the foot steps over.

A formula check (a measured size compared with a bound that the formula sets):
- *Linkage closes over the whole turn*: every joint's `q` is at least 0.01 (no joint flatter than about
  6°) at all 24 sampled angles. Between the samples, `simulate()` in `gen.py` checks Jansen's leg at
  every degree (least `q` 0.062).

`check-range --deep` passes 92 of 92 points with seed 1 and 140 of 140 with 64 samples and seed 7. A sweep
of the crank angle in 10° steps with two legs and the widest bars passes every assertion.

## Sources

- Theo Jansen, *The Great Pretender* (010 Publishers, Rotterdam, 2007; 2nd ed. 2014), and
  [strandbeest.com](https://www.strandbeest.com): the Strandbeest, its leg and the "holy numbers" found by
  his evolutionary search for a flat, long stride.
- [Jansen's linkage](https://en.wikipedia.org/wiki/Jansen%27s_linkage), Wikipedia: the eleven numbers and
  the crank, with the drawing of which bar joins which.
- Jichao Wang, *Durability-Aware Multi-Objective Optimization of the Jansen Linkage: Trading Gait Quality
  Against Joint Wear*, [arXiv:2606.22129](https://arxiv.org/abs/2606.22129) (2026): the forward kinematics
  as two-circle intersections (eq. 1-3, Table 1, the same letters as here), and the sensitivity of `k`.
  Its optimised link lengths (Table 5) were tried as a second variant, but with these joint equations
  they do not close over the whole turn, so they are not offered.
- The circle-circle intersection: any analytic geometry text (two circles meet where the radical line
  cuts them).

## Notes

- The colours stay the same whatever the material (in 3DCraft a colour cannot follow a choice yet):
  plywood bars, walnut triangles, a brass crank, a petrol frame, steel pins.
- The foot path is drawn as the polyline through the 24 sampled foot positions. The foot passes exactly
  through them; between them the true path lies up to 0.1 × crank (1.5 mm at the default) off the line,
  most at the sharp turn at the front of the swing. The tube is thin (0.04 × crank) because a thicker one
  cannot be mitred round that turn.
- The cut sheet lays the parts out as they stand at the form's crank angle. Set the crank angle to taste
  before exporting, or nest the parts in your laser software.

## As an assembly

This Jig works every joint out by hand, as circle intersections. `dist/strandbeest-leg.3dcraftasm` and
`dist/strandbeest-walker.3dcraftasm` build the same leg again from parts, and 3DCraft's assembly solver
finds the joints instead. `assembly/gen.py` writes the command batches that build them
(`assembly/01-bar.json` to `05-strandbeest-walker.json`) and `assembly/check.json`;
`scripts/asm.py all strandbeest-leg` builds and checks them. Both files are packed: they carry their parts
and open anywhere.

**Parts.** One bar (`bar.3dcraft`: 3 mm plywood, 9 mm wide, a hole for a 3 mm pin with 0.2 mm clearance at
each end; its length between the holes, `len`, is a public parameter) and one pin (`pin.3dcraft`, 3 mm;
`len` public too). Every link of the leg is an instance of the bar with its own length: the frame O-B
(√(a² + l²)), the crank m, and the bars b to k. The two rigid triangles of the Jig (the hip B C D and the
foot E F G) are three bars each, pinned at their corners: the solver closes them like every other loop. A
pin goes through every joint, fixed to the rearmost part there (the axle O to the crank), from that part's
back face to the front face of the foremost (the axle from 10 mm behind the frame).

**The leg** (`leg.3dcraftasm`, built into `build/strandbeest/` and packed into the two files): the frame
is fixed to the world (its axle hole on the world's y axis, the bar pointing at B), and a revolute joins
the parts at every joint, sixteen in all. The parts start where the Jig's joints put them at crank angle
0, rounded to the millimetre and to 5°, so the solver really assembles the leg. Nothing drives it: the
crank can still turn (one degree of freedom).

**Layers.** The parts lie in seven layers, from the frame towards the front (-y), 3 mm thick with 1 mm
between them: 0 frame, 1 crank, 2 bars j, c and f, 3 bars b and g, 4 bars d and i, 5 bars k, e and h, 6 a
second crank arm (the web). `gen.py` found this layering by search, with its own simulation of the leg at
every 2° of crank: parts on one layer stay at least 1 mm apart, parts joined by a pin are on different
layers, and no pin passes a part on a layer between its ends within 1 mm. Bars j and k pass right over the
axle O once a turn, so no shaft can run through the leg: the crank pin A runs from the crank to the web,
and crank, pin A and web make one crank throw (glue or key them, as the crank to the axle). The next leg is
driven from the web.

**One leg** (`strandbeest-leg.3dcraftasm`): the leg as a flexible subassembly (its own joints move in the
parent), on a 20 mm drive shaft behind the frame, fixed to the leg's axle and turning about the world's y
axis. The timeline t turns it once: the crank angle is `theta = theta0 + 360 deg * t` (`theta0` = 0,
counter-clockwise seen from the front, as the Jig's), and the drive joint is set to `-theta` (it turns about
+y). The foot is traced (`view.trace` of the foot pin's centre), and the trace written as SVG.

**Four legs** (`strandbeest-walker.3dcraftasm`): four instances of the same leg as flexible
subassemblies in a row along the axle, 43 mm apart, on one crankshaft: the drive shaft behind the first
leg, and between two legs a 6 mm journal fixed to the web of one and to the axle of the next, a quarter
turn on (the phase offsets). Every leg starts at crank angle 0; the solve at rest turns legs 2 to 4 a
quarter, a half and three quarters of a turn on, and they stay on Jansen's branch (the feet show it).

**Assertions** (at every regeneration, and over the motion):
- *the foot is where the Jig's circle intersections put it*: the assembly carries the Jig's closed form
  as its own variables (A, then C, D, E, F and G as circle intersections of the crank angle, the same
  formulas and branches as the Jig's `kin`), and the foot pin's centre (the centroid of its section
  across the pin) must lie within 0.001 mm of G; for each leg of the walker at its own phase;
- *no part overlaps another* (one leg: every pair of its 22 bodies); in the walker, *the crankshaft runs
  clear of every part* (the drive shaft and the journals against every body: 3DCraft measures at most 500
  pairs at once, and each leg is the one checked alone).

**Checked** (3DCraft 57ba7632, `scripts/asm.py check strandbeest-leg`, under a minute):
- one leg: solved at rest with no degree of freedom left; over a whole turn, sampled at 73 moments (5°
  apart; what happens between two samples is not seen), the foot is where the Jig's circle intersections
  put it at every sample (largest miss 1.5e-6 mm) and no part overlaps another; the trace of the foot
  (73 points) misses the Jig's path (the same closed form, computed by `scripts/asm.py` itself) by at most
  1.5e-6 mm; it is closed, 148.9 mm long, 67.86 mm wide and 22.31 mm high (the Jig: stride 67.8 mm, step
  height 22.2 mm);
- four legs: solved at rest with no degree of freedom left; at 25 moments over a turn every foot is where
  the circle intersections put it at its own phase (largest miss 9.2e-7 mm), and the crankshaft runs
  clear of every part; each foot's trace (73 points) matches the closed form at its phase (0°, 90°, 180°,
  270°) within 9.2e-7 mm.

**Not modelled.** The crank, pin A and web are held together by a fixed mate, as a glued or keyed throw;
the pins are fixed to one part each, where a real pin turns in every hole. The walker's legs stand side by
side on one frame line, not on a chassis, and nothing touches the ground. The parts are the Jig's default
material and sizes (3 mm sheet, 9 mm bars, 3 mm pins); the leg's crank is 15 mm, so its bars are Jansen's
numbers in millimetres.

**Found in 3DCraft** (building these): a flexible subassembly brings its own drivers into the parent,
with the values they have in its own file. A leg whose crank its own file drives (tried: `joint.set` of
its crank to 30°) cannot be turned by a parent: the parent's drive and the leg's driver contradict each
other ("over-constrained: ... the driver of Drive.angle, the driver of JointO.angle"). So the leg file is
undriven, and both the one-leg assembly and the walker drive it from outside; a leg file cannot both play
its own motion and serve as a part of a machine.

**Also missing in 3DCraft:**
- No measure of a point's position for an assertion: the foot is measured as the centroid of the foot
  pin's section across its middle.
- An overlap assertion measures at most 500 pairs of bodies: the walker's legs are not checked against each
  other (they stand 43 mm apart along the axle, and each is the leg checked alone).
- `motion.check` on an assembly holds memory for every moment it measures, so `scripts/asm.py` runs it 17
  moments at a time.
- The world's axes have frames whose x axis is not stated: the drive joint's zero (180° about `world/y`)
  was found by tracing the foot; the check against the closed form at every sample proves it right.
