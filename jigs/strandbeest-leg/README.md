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
| Sheet thickness | Parts | 3 mm | the material's `tMin` (2 or 3 mm) to 6 mm |
| Bar width | Parts | 9 mm | `wMin` = hole + 2 × web to `wMax` = 0.75 × crank |
| Pins | Parts | M3 bolt | table `pins`: M3, M4, M5 bolts; 3, 4, 5 mm steel rod; 1/8 in brass rod |
| Pin clearance | Parts | 0.2 mm | 0.05 to 0.6 mm |
| Layer gap | Parts | 1 mm | 0.3 to 3 mm (a washer) |

The crank length sets the scale: every bar is Jansen's number times `crank / 15`. At the default 15 mm
the bars are Jansen's numbers in millimetres and the leg is 135 mm tall (`legHeight`); a 25 cm leg needs a
crank of about 28 mm. **Tables.** `sheets` gives each material's thinnest sheet and the least web
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
   - A, D, E, F: three layers, `2 (t + gap) + t` (11 mm at the defaults);
   - C: two layers, `t + gap + t` (7 mm);
   - B: frame to layer 2, `2 (t + gap) + t` (11 mm);
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
