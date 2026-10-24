# Wall bracket sized by its load

A shelf or console bracket, bent from plate with a welded gusset (or 3D printed as one piece), whose
**plate thickness and gusset depth are worked out from the load** by formulas you can read in the
document. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Load per bracket | Load | 20 (kg) | 1 to `maxLoad` (whole kg; see below) |
| Arm length | Load | 200 mm | 100 to 400 mm, step 5 mm |
| Material | Material | PLA, 3D printed | 6 materials from the table `materials` |
| Screws | Screws | 5 mm | 4, 5 or 6 mm countersunk screws (table `screws`) |
| Shelf screw holes | Screws | on | on / off |

**Materials** (table `materials`): yield strength fy (0.2 % proof), safety factor sf, thinnest and
thickest plate:

| Material | fy (MPa) | sf | t (mm) |
|---|---|---|---|
| Steel S235 | 235 | 2 | 3 to 6 |
| Stainless 1.4301 | 210 | 2 | 2 to 5 |
| Aluminium 6060-T66 | 150 | 2 | 3 to 8 |
| Aluminium 6082-T6 | 240 | 2 | 3 to 8 |
| PLA, 3D printed | 50 | 4 | 4 to 10 |
| PETG, 3D printed | 45 | 4 | 4 to 10 |

**The formulas** (all are variables of the document; `document.inspect` shows their values):

```text
lever   = arm / 2                          the load spread over the arm, as a shelf spreads it
M       = load x 9.81 x lever              bending moment at the wall, N mm
Zreq    = sf x M / fy                      section modulus needed, mm^3
tIdeal  = (6 Zreq / k^2)^(1/3)             the plate for a gusset k = 15 times as deep as thick
tArm    = 6 Zreq / arm^2                   the plate whose deepest gusset fits under the arm
t       = clamp(ceil(max(tIdeal, tArm), 0.5 mm), tMin, tMax)
Dreq    = sqrt(6 Zreq / t)                 depth of the section at the wall (arm plate and gusset)
D       = clamp(ceil(Dreq, 0.5 mm), Dmin, max(Dmin, min(k t, arm)))    Dmin = max(0.3 arm, 3 t + 15 mm)
sigma   = 6 M / (t D^2)                    bending stress, MPa;  utilisation = sigma x sf / fy <= 1
zUp     = height of the two upper wall screws above the foot of the back plate
screwPull = M / zUp / 2                    tension in each upper screw, N, at most pull (table screws)
```

The section at the wall is taken as a rectangle t × D (section modulus t D² / 6), which leaves out the
arm plate's width beside the gusset: on the safe side. The bracket tips about the foot of its back plate,
so the two upper screws, beside the gusset just under the bend, take the moment in tension; one more
screw sits in the tail below the gusset.

**The warning.** The load's range ends at `maxLoad = min(150, floor(min(bendCap, screwCap)))`: what the
thickest plate with its deepest gusset carries in bending (`bendCap`), and what the upper screws carry at
their allowed pull with the screws as low as they can come (`screwCap`). Both are worked out without the
load, so the range does not move as you drag. A form clamps a larger load and says so; `param.set`
refuses it with the range (`load: its value 45 is outside its range, from 1 to 36 (maxLoad)`). With
metals the screws are almost always the limit; with prints at short arms, bending is.

**Checked on the model.** Two assertions hold the built bracket to the load at every regeneration: its
height (measured) is at least `Dreq + tail` (*Gusset deep enough for the load*), and at least what puts
the upper screws high enough for their pull (*Upper screws high enough for the load*). A third says it is
one body. `check-range --deep` passes 168 of 168 points (32 corners, every choice, 128 random), also
with the load at its maximum.

**Geometry.** Plate width b = clamp(0.2 arm, 30 mm, 60 mm), widened to leave room for the screw heads
beside the gusset. The inside bend radius is t; the gusset (thickness t) is coped clear of the bend and
runs to 0.88 of the arm; the arm tip and the tail have plan radii min(b / 3, 10 mm). The wall screw
holes are countersunk at 90° (head dk 8, 10 or 12 mm, kept 0.8 mm short of the plate's back); the shelf
holes are plain clearance holes. The bracket is one colour (terracotta) whatever the material: in 3DCraft
a body's colour cannot yet follow a choice.

**Sources and assumptions.**
- Steel S235: fy = 235 MPa for t ≤ 16 mm, EN 10025-2.
- Stainless 1.4301 (304): Rp0.2 ≥ 210 MPa, hot-rolled plate, EN 10088-2.
- Aluminium 6060-T66: Rp0.2 150 MPa, EN 755-2; 6082-T6 sheet and plate about 240 to 260 MPa,
  EN 485-2 (240 taken).
- PLA and PETG: about 50 and 45 MPa tensile strength for printed specimens, from typical filament data
  sheets (Prusament PLA and PETG); a print's strength across its layers is lower, hence the safety factor
  4 (an assumption, as is 2 for metals).
- Countersunk wood screws, heads 2 × d (ISO 7050 / DIN 7997 proportions); clearance holes 4.5, 5.5 and
  6.6 mm (ISO 273, medium).
- The allowed pull per screw, 200, 300 and 400 N for 4, 5 and 6 mm, is an assumption on the safe side for
  nylon plugs in solid brick or concrete. Hollow brick, plasterboard or wood are different: check your
  plugs' data, and give a weaker wall a smaller load.
- Beam bending: σ = M / Z with Z = t D² / 6 for a rectangular section (any strength of materials text).

This is a sizing aid, not a certified calculation: buckling of a thin gusset, the weld and the wall are
not checked.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
