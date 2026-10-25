# Tensegrity table

The maker's "floating table": a base and a top, each with a hook reaching into the other. The top hangs
from the base's hook by one short central cable, and three or four outer cables, tensioned between the
edges of the top and the base, hold it level. Nothing seems to hold the top up. Cut from plywood (or MDF,
or printed), with tab-and-slot joints and a cut sheet. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Height | Size | 400 mm | `Hmin` to `Hmax` (see below), step 1 mm |
| Top shape | Size | square | square, round, triangle (top and base alike) |
| Top size | Size | 300 mm | 150 mm (triangle 230 mm) to 600 mm (a printed top: the print bed) |
| Central cable length | Size | 100 mm | 20 mm to `LcMax` |
| Outer cables | Cables | 3 cables | 3 or 4 |
| Outer cable type | Cables | Steel wire rope 2 mm | table `ropes` |
| Central cable type | Cables | Steel wire rope 3 mm | table `ropes` |
| Load on the table | Load | 4 (kg) | 0 to `maxLoad` (whole kg) |
| Material | Material | Birch plywood | table `sheets` |
| Sheet thickness | Material | 18 mm | 9 to 24 mm, step 0.1 mm |
| Slot clearance | Material | 0.1 mm | 0 to 0.6 mm |
| Print bed | Material | 350 mm | 250 to 500 mm (only used for a printed material) |

**Tables.** `ropes` (diameter, safe working load SWL): steel wire rope 7x7 of 1.5, 2, 3 and 4 mm
(264, 470, 1058 and 1880 N) and steel chain DIN 766 3 mm (500 N). `sheets` (density, bending strength fm,
safety factor): birch plywood (680 kg/m³, 40 MPa, 3), poplar plywood (450, 25, 3), MDF (750, 20, 3),
PLA and PETG printed with about 30 % infill (750 and 760 kg/m³, 30 and 25 MPa, 4).

## How it is built

z is up; both hooks stand in the plane x = 0. The base hook is a plate standing on edge whose post rises
at -y (two tabs through the base plate) and whose arm reaches over the centre; the top hook hangs from the
top at +y and its arm reaches under the centre. The central cable runs vertically at the centre, from the
top hook's arm up to the base hook's arm; its length is how far the hooks overlap. The outer cables run
vertically through holes 25 mm in from the edge, on a regular polygon of radius `rA` (3 cables at 0°, 120°
and 240°, 4 cables on the diagonals). Hook arm depth and post width: `b = clamp(0.25 yEdge + 5 mm, 25 mm,
80 mm)`, with `yEdge` the top's half-width along the hooks. The ends of the arms are round, the outer
corners rounded, and each arm has a hole for the central cable's loop or shackle.

The plates are walnut coloured, the hooks plywood, the cables steel: in 3DCraft a colour cannot follow a
choice yet, so the colours stay the same whatever the material.

## The statics

All forces are vertical. The top (plate and hook, weight `Wt`, centre of mass `eTop` off centre along y)
and the load `Q` hang from the central cable at the centre; the outer cables pull down at the anchors.

- **Pretension.** The outer tensions are not fixed by equilibrium: with the central support strictly
  inside the polygon of the anchors there is a state of self-stress, the outer cables pulling down and
  the central cable up, in which every outer cable carries a share of a pretension `P`. That is what
  makes a tensegrity: a structure held in shape by tension it carries itself
  ([Snelson](#sources), [Fuller](#sources)). If the central support were outside the anchor polygon, no
  set of outer tensions could all be positive.
- **Moment of the load.** The moment of a weight W at w about the centre is shared by the outer cables as
  in a pile or bolt group (rigid top, equal cables, anchors on a regular polygon, Σ p pᵀ = n rA²/2 · I):
  `Ti = P/n - 2 W (w · pi) / (n rA²)`. A load near cable i takes tension from it; the worst case for
  each cable is the load at the edge of the top right over it, at most `Rout` from the centre (the
  corner of the square or the triangle, taken sharp: on the safe side).
- **Formulas** (variables of the document; `document.inspect` shows their values):

```text
D       = 2 / (n rA) (Wt eUse + Q g Rout)     largest change of an outer cable's tension, N
T0      = 1.25 D + 10 N                       pretension to give each outer cable, unloaded
TminW   = T0 - D                              least outer tension, load at the worst edge (> 0)
ToutMax = T0 + D                              most outer tension (<= SWL of the outer cable)
Tc      = n T0 + Wt + Q g                     central cable (<= SWL of the central cable)
TcHook  = fm / sf · T b² / 6 / p              what a hook's arm and post carry in bending, p the lever
bReq    = sqrt(6 Tc p sf / (fm T))            arm depth the central cable needs
maxLoad = what keeps ToutMax <= SWL and Tc <= min(SWL, TcHook), at most 50 kg
```

`eUse = eTop + 2 mm`; `eTop` is the area-weighted centroid of the hook (post, arm, round end, less the
rounded corner) and the plate (the tabs fill the slots). At the defaults: `Wt` 12.7 N, `eTop` 13.2 mm (the
model measures 13.16 mm), `T0` about 67 N per outer cable, `Tc` about 250 N, `maxLoad` 12 kg (the hooks'
bending is the limit here).

- **Stability of the top.** The top's own centre of mass must lie inside the anchor polygon, so that its
  weight alone does not take the pretension off a cable. A tall table with a small top has a long, heavy
  hook post: `Hmax` and `LcMax` stop the post where the centre of mass would reach 95 % of `aIn`, the
  half-side of a square inside the anchor polygon's inscribed circle.
- **Room.** Each hook's arm stays 15 mm from the other plate (`Hmin`, `LcMax`), the hooks at least 5 mm
  from each other; a printed part fits the print bed (`Smax`, `Hmax`, `LcMax`).

## Assertions (checked at every regeneration)

- *Height as set*: the whole table's extent in z is `H`.
- *Hooks do not touch*: clearance from the base hook to the top hook at least 5 mm; *No part overlaps
  another*.
- *Top's centre of mass inside the anchor polygon* (x and y, `centerOfMass` of the set *Top assembly*
  within ±`aIn`), and *no further off centre than the statics take it* (`≤ eUse`).
- *Central support inside the anchor polygon*: the central cable's box (`boxMin`/`boxMax`) within ±`aIn`.
- *Worst load position within the statics' reach*: the top plate's box (`boxMin`/`boxMax`, x and y)
  within ±`Rout`, the reach the worst load case is computed with.
- *Outer cables stay taut with the load at the worst edge*: holds while `TminW > 0`.
- *Outer cable* and *Central cable thick enough for its tension*: the modelled cable's diameter is at
  least `d sqrt(T / SWL)` (a rope's strength goes with d²), so this holds exactly while `T <= SWL`.
- *Top hook's* and *Base hook's arm deep enough*: the arm reaches at least `bReq` from the cable.
- *Printed parts fit the print bed* (a printed material only).

`check-range --deep` passes 96 of 96 points (seed 1: default, 64 corners, 15 choices, 16 random) and 144
of 144 (64 samples, seed 7).

## Cutting

The named face set **Cut sheet** holds the two plates (seen from below) and the two hooks:
`file.export {"path": "table.svg", "set": "Cut sheet"}` (DXF too) lays them on one sheet at true size,
with the slots, the cable holes (cable diameter + 1 mm) and the tabs. Slots are drawn `clearance` wider
than the sheet and the tabs; a laser's kerf adds about 0.1 mm to that, so 0 to 0.1 mm gives a tight fit
with a laser. Measure your sheet: plywood sold as 18 mm is often 17.5 to 18.5 mm.

## How to assemble and adjust

1. Glue the hooks' tabs into the slots of their plates, square to the plate (the hooks are pushed into
   their plates by the cables, but the tabs carry the moment `Tc · p`: glue them).
2. Set the **central cable** first: thread it through the holes of both arms and make it the length of
   *Central cable length* between the arms (crimp sleeves, or a shackle and a short turnbuckle for the
   chain). Hang the top from it: it tilts towards its hook.
3. Thread the **outer cables** through the holes in the top and the base, with a stop (crimp sleeve or
   knot over a washer) under the base and above the top, and a turnbuckle or a cable tensioner in each.
4. Tension them in turns, a little at a time, until the top is level and stiff; aim for `T0` per cable
   (`document.inspect` gives it). Retension after a day, once the cables have settled.
5. Never load the table beyond the load it was built for (`maxLoad` for the chosen cables and sheet).

## Sources

- Kenneth Snelson, *Continuous tension, discontinuous compression structures*, US patent 3,169,611
  (1965), and his writings on "floating compression"; R. Buckminster Fuller, *Tensile-integrity
  structures*, US patent 3,063,521 (1962), who coined *tensegrity*.
- R. Motro, *Tensegrity: Structural Systems for the Future* (Kogan Page, 2003): self-stress states and
  why the compressed parts must be enclosed by the cables.
- The floating (tensegrity) table as makers build it: the many Instructables and maker videos of 2020
  and since, a top hung from a hook on the base by one chain and held level by outer chains or cables.
- Load shared by vertical members as in a pile or bolt group (rigid cap): any structural analysis text,
  e.g. the elastic method for eccentrically loaded bolt groups.
- Wire rope minimum breaking force `F = K d² R` with K = 0.332 for 7x7 and grade R = 1770 N/mm²
  (EN 12385-4 form), safe working load a fifth of it (a factor of 5, an assumption usual for static
  rigging). Chain DIN 766 3 mm: 4 kN breaking force (supplier data), safe load an eighth of it. Decorative
  chain (DIN 5685) is not tested for strength and is not offered.
- Bending strength: birch plywood about 40 MPa along the face grain (manufacturers' data, EN 636 /
  EN 310), poplar plywood about 25 MPa, MDF at least 20 MPa (EN 622-5); printed PLA and PETG with
  infill: assumed 30 and 25 MPa with a factor 4. Densities from the same data sheets.

This is a sizing aid, not a certified calculation: creep of the cables, the glue joints, the floor and
people leaning on the table are not checked.

`build.json` was written by `python3 -I gen.py > build.json`; edit `gen.py` and run it again to change
the model.
