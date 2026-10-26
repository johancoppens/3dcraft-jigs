# Geared orrery

A hand-cranked mechanical model of the solar system: the Sun in the centre, Mercury to Saturn on nested
tubes, the Moon round the Earth as an option, every body driven from one crank through two gear stages
whose tooth counts were searched so that its period matches the real sidereal period. One turn of the
crank is one year; set the date and every ball moves to where its gears put it. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Planets | Planets | Mercury to Saturn | Mercury to Earth, to Mars, to Jupiter or to Saturn (table `planetSets`) |
| Moon | Planets | on | on / off |
| Accuracy target | Gear trains | 0.03 % (300 ppm) | 0.5 %, 0.1 %, 0.05 % or 0.03 % (table `targets`) |
| Most teeth per gear | Gear trains | 120 | `zLeast` (60 to 120: the least that meets the target, see below) to 120, step 10 |
| Module | Gear trains | 1 mm | 1, 1.25, 1.5 or 2 mm |
| Gears made by | Gear trains | 3D printed (4 mm) | 3D printed, laser-cut acrylic 3 mm, laser-cut plywood 4 mm |
| Mercury's arm | Arms | 60 mm | Sun + Mercury + 2 mm to 90 mm, step 1 mm |
| Gap between orbits | Arms | 14 mm | 3 to 20 mm, step 0.5 mm |
| Ball size | Arms | 1.4 | 0.6 to 1.8 (the Sun 24 mm across at 1) |
| Days since 1 Jan 2000 | Crank | 0 | −36525 to 36525 (1900 to 2100), step 1 day |

## The astronomy

Each body turns once per **sidereal period**: once round the Sun measured against the stars (NASA
fact sheets):

| Body | Sidereal period | Mean longitude at J2000 |
|---|---|---|
| Mercury | 87.969 d | 252.250° |
| Venus | 224.701 d | 181.979° |
| Earth | 365.256 d | 100.465° |
| Mars | 686.980 d | 355.447° (−4.553°) |
| Jupiter | 4332.589 d | 34.396° |
| Saturn | 10759.22 d | 49.954° |
| Moon (round the Earth) | 27.3217 d | 218.316° |

One turn of the crank is one sidereal year of the Earth (365.256 days). A body whose train turns
`ratio = (zA / zB) · (zC / zD)` times per crank turn has the period 365.256 d / ratio: the error is
that period against the real one. The parameter **Days since 1 Jan 2000** turns the crank by
360° · days / 365.256, and every arm turns by that angle times its ratio. At day 0 (1 January 2000,
12:00 TT, the epoch J2000) each arm points at its body's **mean heliocentric longitude** then (planets:
E. M. Standish, JPL, *Keplerian Elements for Approximate Positions of the Major Planets*, table 1; the
Earth's value is that of the Earth-Moon barycentre); the Moon's arm at the Moon's mean geocentric
longitude (J. Meeus, *Astronomical Algorithms*, 2nd ed., ch. 47: L′ = 218.3164477°). Directions are
seen from the north (from above): every arm turns anticlockwise, and the x axis of the model points to
the vernal equinox.

The Moon is geared to its **sidereal** month (27.32 d). Its **synodic** month, from new moon to new
moon (29.53 d), is not geared: it appears by itself as the Moon's arm laps the Earth's arm,
1 / (1 / 27.3217 − 1 / 365.256) = 29.5306 d (29.539 d with the default gears). The Moon is new when its
ball lies between the Earth and the Sun.

**What is to scale and what is not.**
- To scale: the periods (within the accuracy target) and the directions of the bodies at any date
  (their *mean* longitudes).
- Not to scale: the distances. Saturn is 24.5 times as far from the Sun as Mercury (9.54 against 0.387
  AU); with Mercury's arm at 60 mm, Saturn's would be 1.48 m. The arms are spaced evenly (by each
  ball's reach and the gap), as in nearly every orrery.
- Not to scale: the sizes. The Sun is 109 Earths across and Jupiter 11; to scale the Earth would be a
  speck or the Sun a wall. The balls keep the real order of size (Jupiter > Saturn > Earth ≳ Venus >
  Mars > Mercury > Moon).
- Not modelled: the orbits are circles in one plane, run at an even speed. The real bodies move faster
  near the Sun (Kepler's second law), so a real planet can stand up to about 2e radians from its mean
  longitude (e the eccentricity): about 24° for Mercury, 11° for Mars, 6° for Jupiter and Saturn, 2° for
  the Earth. The Moon's orbit is tilted 5° and the Earth's axis 23.4°; neither is shown. The Earth's ball
  turns with the Moon's arm (once a month, not once a day), and Saturn's ring turns with its arm.

## The history

The oldest known geared model of the sky is the **Antikythera mechanism**, a Greek bronze machine of the
2nd or 1st century BC found in a shipwreck off Antikythera in 1901; its 30 surviving gears showed the
Moon's phases and predicted eclipses, and its front probably showed the planets (Freeth et al., *Nature*
444, 2006; *Scientific Reports* 11, 2021). Clockmaker **George Graham** built a planetary machine about
1704; the instrument maker **John Rowley** built copies of it, one about 1712-13 for Charles Boyle, 4th
Earl of Orrery, which gave every such model its name (Science Museum, London, object 1952-73). Rowley's
orrery shows the Sun, Earth and Moon; "grand orreries" with all the planets out to Saturn, the planets
known before William Herschel found Uranus in 1781, followed in the 18th century. This Jig's
**Planets** stop at Saturn for that reason (and because Neptune would need a ratio of 1 : 165 to the
Earth).

## How it is built

**Three axes.** The centre post C (on the z axis, fixed in the base plate) carries the bodies' tubes,
nested with 0.25 mm running clearance, Mercury's innermost and longest. The lay shaft L2 (fixed, at
(a2, 0)) carries loose compound gears. The input shaft L1 (at (x1, y1)) turns in the base plate and
carries the crank on top. Seen from above, the three form a triangle.

**Two stages per body.** For each body X, from the base plate up, two layers of gears: in the lower one
A_X (fixed on L1) drives B_X (on L2); in the upper one C_X (glued to B_X with a spacer: a compound)
drives D_X (glued to the tube of X). Every stage-1 pair (A, B) sits at the same centre distance (L1 to
L2), every stage-2 pair (C, D) at the same centre distance (L2 to C): so all pairs of a stage share one
tooth sum, S12 or S2, and the centre distances are `module · S12 / 2` and `module · S2 / 2`. Two meshes
keep the sense of rotation: every tube turns with the crank. The distance L1 to C is free; it is the
least at which every A clears the tubes and every D clears L1 (and at most a right angle at L2), so the
triangle closes. Each tube stands on the gear of the tube inside it (Mercury's on the base plate), a
steel washer under each compound on L2.

**The search** (`trains.py`, run by `gen.py`; Python, deterministic). For each choice of planets, Moon,
most teeth (60 to 120 in steps of 10) and accuracy target it tries the tooth sums S12 and S2 from the
smallest gearbox up, and for each the best (zA, zB, zC, zD) per body: 12 teeth at least, the most teeth
at most, each D large enough for its tube's bore with 1.5 mm of rim, each B clear of the tubes it passes
and each C clear of L1 (at module 1; a larger module only adds room). The first gearbox whose every
train is within the target wins (ties: the least worst error). The tooth counts go into the document as
the table `trains` (224 rows, one per combination), so the model looks them up and never searches. The
least *most teeth* that meets each target is the table `zlim`, and the parameter's lower bound
(`zLeast`). `python3 gen.py --table [planets moon most target]` prints a row, `--sweep` checks every row at
every module.

The default trains (Mercury to Saturn with the Moon, at most 120 teeth, 300 ppm):

S12 = 117, S2 = 129: stage 1 at 58.5 modules, stage 2 at 64.5 modules; worst error 262 ppm.

| Body | A | B | C | D | Turns per year | Period built | Real period | Error |
|---|---|---|---|---|---|---|---|---|
| Mercury | 91 | 26 | 70 | 59 | 4.152542 | 87.9596 d | 87.969 d | −107 ppm (−0.0094 d per orbit) |
| Venus | 88 | 29 | 45 | 84 | 1.625616 | 224.6878 d | 224.701 d | −59 ppm (−0.0132 d per orbit) |
| Earth | 39 | 78 | 86 | 43 | 1 (exact) | 365.2560 d | 365.256 d | 0 |
| Moon | 87 | 30 | 106 | 23 | 13.365217 | 27.3288 d | 27.3217 d | +262 ppm (+0.0071 d per orbit) |
| Mars | 47 | 70 | 57 | 72 | 0.531548 | 687.1557 d | 686.98 d | +256 ppm (+0.176 d per orbit) |
| Jupiter | 15 | 102 | 47 | 82 | 0.084290 | 4333.3350 d | 4332.589 d | +172 ppm (+0.746 d per orbit) |
| Saturn | 24 | 93 | 15 | 114 | 0.033956 | 10756.7892 d | 10759.22 d | −226 ppm (−2.43 d per orbit) |

Without the Moon the default gearbox is S12 = 92, S2 = 130 with a worst error of 182 ppm. Looser targets
give smaller gearboxes: 0.5 % takes S12 = 79, S2 = 95 for all planets and the Moon. The error of each
body in the open model is in the variables `err_X` (ppm), `Tm_X` (the period built, days) and `dT_X`
(days per orbit), X = Me, Ve, Ea, Mo, Ma, Ju, Sa.

**The Moon** has its own train to its tube (between the Earth's and Mars's). That tube ends just under
the Earth's arm in a gear Gc; 1, 3 or 5 equal idlers on pins under the Earth's arm carry its turn out
to a gear Gp as large as Gc, fixed to the Earth's sleeve. With an odd number of idlers and Gp equal to
Gc, the sleeve keeps the Moon tube's own turn as the arm goes round (parallel motion), so the Moon's arm
on top of it points at the Moon's mean longitude. The Earth's orbit radius is rounded to what the idlers
reach: module × (Gc + idlers × idler teeth).

**The arms.** Above the gears the tubes end in arms, the outermost tube (Saturn) lowest, each 3 mm thick
and 7 mm wide, with a pin up to its ball; all balls (and the Sun, on the centre post) at one height. Each
orbit radius is the one inside it plus both bodies' reach (ball, arm end, Saturn's ring at 2.2 radii,
the Earth's Moon and Moon gears) plus the **gap between orbits**. An arm is always lower than the arms
inside it and shorter than the orbits outside it, so nothing of one orbit can meet anything of another
at any angle.

**The gears.** Each gear is drawn as the `spur-gear` Jig draws one (the same tooth variables: pressure
angle 20°, addendum 1 and dedendum 1.25 modules, each flank thinned by backlash / 4, here 0.15 mm in
all, a chained sketch pattern of one tooth and its root gap, extruded once), with one change: each flank
is a circular arc from the root circle through the involute's point at t² = 0.3 t0² + 0.7 ta² to the
involute's tip point (its centre worked out in variables), instead of the fitted involute spline with a
radial foot. Over the involute part
of the flank the arc lies within 0.041 module inside the involute and at most 0.004 module outside it
(`python3 gen.py --flank`), well within the 0.0375 mm a flank is thinned and below what a printer or a
laser holds. Why: see *Limits of 3DCraft* below.

**Sizes.** The centre post and both spindles are 4 mm rods; tubes have 1.2 mm walls with 0.25 mm
clearance (the 7th is 24.3 mm across); gears fixed on a rod or tube have a 0.01 mm gap there (glue);
loose bores 0.25 mm. Layers of gears 1 mm apart (washers). The base plate (6 mm, walnut) is the gears'
outline plus 6 mm, with corners of 10 mm radius.

## Making it

Print or cut: every gear (A, B, C, D of each body; with the Moon Gc, the idlers and Gp), the spacers and
washers, the tubes, the arms with their pins, the Moon's carrier, the balls, the Sun, the base plate;
4 mm steel or brass rod for the centre post and both spindles. For laser-cut gears, the named face set
**Cut sheet** holds every gear's outline and the base plate:
`file.export {"path": "orrery.svg", "set": "Cut sheet", "width": "600 mm"}` (its kerf is not
compensated: the backlash takes about 0.15 mm; check a pair before cutting them all). Print the tubes
upright; a thin tube prints better slowly or in PETG. Brass telescoping tubing works too, if you change
the tube sizes to its steps.

Assembly, from the bottom:
1. Glue the centre post and the lay shaft into the base plate; the input shaft turns freely in its hole.
2. Glue every A gear onto the input shaft at its height (layer by layer, a spacer block of the layer
   pitch helps), and the crank on top.
3. Per body, from Mercury out: slide its washer and compound (B, spacer, C glued, all the same way up)
   onto the lay shaft; slide its tube with D glued at the bottom over the tube inside it, so that D sits
   in the layer of its C. Turn the crank a little after each one: it must still run freely.
4. With the Moon: glue Gc onto the Moon's tube top.
5. Set the crank so its day counter is 0 (or turn on to today), then glue each arm onto its tube pointing
   at the body's mean longitude for that day (the open model shows the angles: `th_Me`, …; the Moon's
   `thMo`). Mount the idlers and the Earth's sleeve with Gp and the Moon's carrier.
6. The balls and the Sun on their pins, Saturn's ring on Saturn.

**Reading it.** Each arm shows its body's heliocentric longitude, seen from above the Sun's north pole.
Seen from the Earth, the Sun stands in the opposite direction to the Earth's arm (that direction, against
the zodiac, gives the date). A planet in line with the Earth on the same side of the Sun is at
opposition (best seen); on the far side, at conjunction. The Moon's arm against the Earth's gives the
phase: towards the Sun new, away from it full. One crank turn is one year; Mercury goes round four
times, Saturn a thirtieth.

## Checked

**Assertions** (50, at every regeneration):
- the trains, from the tooth counts alone: every pair of a stage meshes on its shared centre distance
  (zA + zB = S12, zC + zD = S2 for every body); every body's period built (365.256 d · zB zD / (zA zC))
  within the accuracy target of its real one; every train gear has 12 to *most teeth* teeth (counts:
  the number of gears when all hold, 0 when not);
- the gears where they mesh: the centre of mass of the tube gears on the centre post (x and y 0), of the
  lay-shaft gears at x = module (zC + zD) / 2, y = 0, and of the input gears at the point at module
  (zA + zB) / 2 from the lay shaft and the chosen distance from the centre (from Mercury's teeth, which
  the first assertion ties to every other train's);
- no two parts overlap, at the current crank angle: every pair of the 70 or so bodies, in eleven groups
  (the meshing pairs, so the teeth are turned into each other's gaps, every gear against every shaft,
  tube, washer and spacer, the arms and balls against each other and everything below);
- the tubes nest with running clearance (at least 0.4 of the 0.25 mm, see *Limits*);
- neighbouring orbits apart at every angle (each orbit's ring of reach from the next by the gap), the
  Sun clear of Mercury, the crank clear of the tubes;
- for each body, x and y: its ball is where its gear train puts it (L0 + crank angle × zA zC / (zB zD),
  tolerance 0.001 mm), and within the accuracy target of the real body's mean longitude on that day (L0 +
  360° · days / real period; tolerance: the arc the target allows after that many days). Measured as the
  centre of mass of the ball and the Sun (so a body that is not built leaves the Sun's).

The overlap of the arms is checked only at the current crank angle; that they cannot meet at any other
follows from the orbits' rings (the formula assertion above), not from a measure.

**Over the range** (3DCraft `main` at 3faaaea0, seed 1): `scripts/check.sh orrery` passes 92 of 92
points (the defaults, 64 corners, 11 choices, 16 random), and so does `DEEP=1` (92 of 92). A
regeneration takes 78 ms (median), at most 230 ms; a range check about 3.5 minutes and 160 MB. The
first run found three faults, all fixed: the table's row order, the Moon's assertions in error with the
Moon off, and arcs given by through points (see *Limits*). `python3 gen.py --sweep` checks every
reachable row at every module (224 rows x 4 modules, none failing). Looked at: the default thumbnail,
a laser-cut acrylic orrery to Mars on 26 October 2026 (Venus in inferior conjunction: its arm in line
with the Earth's) and its cut sheet (16 gears and the base plate, 36 closed paths).

## Limits of 3DCraft today

- **Spline flanks are slow.** A gear whose flanks are fitted involute splines (`sketch.curve`, as the
  `spur-gear` Jig draws them) took about 1.8 s per 80 teeth to extrude; this orrery has up to 35 gears
  and 2000 teeth, so it would take about a minute to rebuild. With circular-arc flanks the whole orrery
  regenerates in under a tenth of a second.
- **An arc meeting a radial line in a chained ring pattern** is reported as crossing at random teeth
  (`e19[k], e3[k+1] cross or touch each other`) for about a third of the tooth counts from 12 to 120,
  so the radial foot of the `spur-gear` tooth could not be kept with arc flanks; the flank arc starts on
  the root circle instead (repro: `repro-orrery-1.json`, one gear of 16 teeth).
- **An arc given by a through point** (`sketch.path` `through`) made the sketch's constraints conflict at
  some points of a range check (the flank's through point stays between the arc's ends); the arcs are
  given by their centres instead, worked out from the three points in variables.
- **A parameter's range cannot look a table up** (`unknown table`); the least *most teeth* goes through
  the variable `zLeast` (repro: `repro-orrery-2.json`).
- An overlap assertion takes at most 500 pairs of bodies: eleven assertions over named sets.
- An assertion whose subject is a body that is switched off is in *error*; the per-body checks measure
  the ball together with the Sun so that they always have a subject.
- The clearance between the nested tubes is found (0.25 mm) but proven only to about 0.10 mm, so its
  assertion asks 0.4 × clearance; that the tubes do not overlap is proven by the overlap assertion.

## Sources

- NASA Goddard, *Planetary Fact Sheet* and the fact sheets of Mercury, Venus, Earth, the Moon, Mars,
  Jupiter and Saturn (sidereal orbit periods): https://nssdc.gsfc.nasa.gov/planetary/factsheet/
- E. M. Standish, JPL Solar System Dynamics, *Approximate Positions of the Planets*, table 1 (mean
  longitudes at J2000): https://ssd.jpl.nasa.gov/planets/approx_pos.html
- J. Meeus, *Astronomical Algorithms*, 2nd ed. (1998), ch. 47 (the Moon's mean longitude).
- T. Freeth et al., "Decoding the ancient Greek astronomical calculator known as the Antikythera
  Mechanism", *Nature* 444 (2006) 587-591; "A Model of the Cosmos in the ancient Greek Antikythera
  Mechanism", *Scientific Reports* 11 (2021) 5821.
- Science Museum Group, *Orrery made by John Rowley for the Earl of Orrery*, 1712-13:
  https://collection.sciencemuseumgroup.org.uk/objects/co56970
- ISO 53 (basic rack, 20°) and the involute construction of this collection's `spur-gear` Jig.

`build.json` was written by `python3 gen.py > build.json` (it imports `trains.py`); edit those and run
it again to change the model.
