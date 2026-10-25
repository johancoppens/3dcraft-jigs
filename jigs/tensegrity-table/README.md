# Tensegrity table

The maker's "floating table": a base and a top, each with a hook reaching into the other. The top hangs
from the base's hook by one short central cable. Three or four outer cables, tensioned between the edges of
the top and the base, hold it level, so nothing seems to hold the top up. It is cut from plywood (or
printed), with tab-and-slot joints and a cut sheet. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Height | Size | 400 mm | `Hmin` to `Hmax` (see below), step 1 mm |
| Top shape | Size | square | square, round, triangle (top and base alike) |
| Top size | Size | 300 mm | 160 mm (triangle 240 mm) to 600 mm (a printed top: the print bed) |
| Central cable length | Size | 100 mm | 20 mm to `LcMax` |
| Outer cables | Cables | 3 cables | 3 or 4 (a triangle always has 3) |
| Outer cable type | Cables | Steel wire rope 2 mm | table `ropes` |
| Central cable type | Cables | Steel wire rope 3 mm | table `ropes` |
| Load on the table | Load | 3 (kg) | 0 to `maxLoad` (whole kg) |
| Material | Material | Birch plywood | table `sheets` |
| Sheet thickness | Material | 18 mm | `tMin` of the material (9 or 12 mm) to 24 mm, step 0.1 mm |
| Slot clearance | Material | 0.1 mm | 0 to 0.6 mm |
| Print bed | Material | 350 mm | 250 to 500 mm (used only for a printed material) |

The load is a mass anywhere on the top, the worst place included: the very edge over a cable. At the
defaults the range ends at 6 kg; a load at the centre alone could be much larger.

**Tables.**
- `ropes` gives each cable's diameter and safe working load (SWL):
  - steel wire rope 7x7 of 1.5, 2, 3 and 4 mm: 286, 508, 1144 and 2033 N;
  - steel chain DIN 766 4 mm: 1962 N.
- `sheets` gives each material's density, bending strength fm, safety factor sf, modulus E and thinnest
  sheet:
  - birch plywood: 680 kg/m³, 40 MPa, 3.5, 9000 MPa, 9 mm;
  - poplar plywood: 450, 25, 3.5, 6000, 9 mm;
  - PLA printed solid: 1240, 50, 5, 3500, 12 mm.
- MDF and PETG are not offered (see *Sources*).

## How it is built

z is up, and both hooks stand in the plane x = 0.
- **Base hook.** A plate standing on edge. Its post rises at -y, with two tabs through the base plate, and
  its arm reaches over the centre.
- **Top hook.** It hangs from the top at +y, and its arm reaches under the centre.
- **Central cable.** It runs vertically at the centre, from the top hook's arm up to the base hook's arm.
  Its length is how far the hooks overlap.
- **Outer cables.** They run vertically through holes 25 mm in from the edge, on a regular polygon of
  radius `rA`: three cables at 0°, 120° and 240°, four on the diagonals.

The arm depth and post width are `b = clamp(0.25 yEdge + 5 mm, 25 mm, 80 mm)`, or `0.35 yEdge` for printed
hooks. `yEdge` is the top's half-width along the hooks. `b` is kept small enough to leave 6 mm between one
hook's arm and the other hook's post. The arms have round ends, a hole for the central cable's loop or
shackle, and an inside fillet of radius b/4 where they meet the post (the largest moment is there). The
outer corners are rounded.

The plates are walnut coloured, the hooks plywood and the cables steel. In 3DCraft a colour cannot follow a
choice yet, so the colours stay the same whatever the material.

## The statics

All forces are vertical. The top (plate and hook) has weight `Wt` and its centre of mass is `eTop` off
centre along y. The top and the load `Q` hang from the central cable at the centre, and the outer cables
pull down at the anchors.

- **Pretension.** Equilibrium does not fix the outer tensions. The central support lies strictly inside the
  polygon of the anchors, so there is a state of self-stress: the outer cables pull down and the central
  cable pulls up, each outer cable carrying a share of a pretension `P`. A structure held in shape by
  tension it carries itself is what makes a tensegrity ([Snelson, Fuller](#sources)). With the central
  support outside the anchor polygon, no set of outer tensions could all be positive.
- **Moment.** The moments of the top and of the load about the centre are shared by the outer cables as in
  a pile or bolt group: `ΔTi = -2 W (w · pi) / (n rA²)`. That sharing assumes a rigid top, equal cables,
  anchors on a regular polygon and equal pretension in every cable. With four cables the pretension is
  statically indeterminate, so tension them evenly. For each cable the worst case is the load at the edge
  of the top right over it, at most `Rout` from the centre. `Rout` is the corner of the square or the
  triangle taken sharp, which is on the safe side.
- **Vertical share.** The load also pulls the top straight down. The central path runs through two
  plywood hooks in bending, which are much softer than steel cables, so most of that vertical share would
  relax the outer cables rather than load the central one. To stay on the safe side, the formulas take the
  whole vertical share `Q g / n` as lost by every outer cable. For the central cable and the hooks they
  still take the full `n T0 + Wt + Q g`.
- **Formulas.** All are variables of the document; `document.inspect` shows their values.

```text
D       = 2 / (n rA) (Wt eUse + Q g Rout)       largest change of an outer tension from the moments, N
T0      = 1.25 (D + Q g / n) + 10 N             pretension to give each outer cable, unloaded
TminW   = T0 - D - Q g / n                      least outer tension, load at the worst edge (> 0)
ToutMax = T0 + D                                most outer tension (<= SWL of the outer cable)
Tc      = n T0 + Wt + Q g                       central cable (<= SWL of the central cable)
TcHook  = fm / sf · T b² / 6 / p                what a hook carries in bending, p the lever to the cable
Ncr     = π² E I / (2 Lp)²,  I = b T³ / 12      Euler load of a post: a cantilever fixed in its plate,
                                                buckling out of the hook's plane, free length Lp
TcPost  = 1 / (sf / Ncr + 1 / TcHook)           bending and buckling together (linear interaction)
maxLoad = what keeps ToutMax <= SWL and Tc <= min(SWL, TcPost), at most 50 kg
```

`eUse = eTop + 2 mm`. `eTop` is the area-weighted centroid of the hook and the plate. The hook counts its
post, arm and round end, plus its inside fillet, less its rounded corner. The tabs fill the slots, so the
plate counts whole.

Values at the defaults:

| Quantity | Value |
|---|---|
| `Wt` | 12.7 N |
| `eTop` | 13.2 mm (the model measures it within 0.01 mm) |
| `T0` | 65 N per outer cable |
| `TminW` | 21 N |
| `ToutMax` | 99 N |
| `Tc` | 238 N |
| `TcPost` | 432 N |
| `maxLoad` | 6 kg |

- **Top's centre of mass.** With enough pretension the top's own off-centre weight only asks for
  `P > 2 Wt eTop / rA`, and that is already in `D`. The model still keeps the top's centre of mass inside
  the anchor polygon, as a conservative design rule. Then even an outer cable that has crept slack does
  not let the top tip over its edge, and the pretension never has to fight the top's own weight. A tall
  table with a small top has a long, heavy hook post, so `Hmax` and `LcMax` stop the post where the centre
  of mass would reach 95 % of `aIn`. `aIn` is the half-side of a square inside the anchor polygon's
  inscribed circle.
- **Buckling.** `Hmax` and `LcMax` also stop the posts where they could no longer carry
  `F0 = 80 N + 2 x the plate's weight` in bending and buckling together. The load range then follows the
  actual post length.
- **Room.** Each hook's arm stays 15 mm from the other plate (`Hmin`, `LcMax`), and the hooks stay at
  least 5 mm from each other. A printed part fits the print bed (`Smax`, `Hmax`, `LcMax`).

## Assertions (checked at every regeneration)

These are measured on the model:
- *Height as set*: the whole table's extent in z is `H`.
- *Hooks do not touch*: the clearance from the base hook to the top hook is at least 5 mm.
- *No part overlaps another*.
- *Top's centre of mass inside the anchor polygon*: in x and y, the `centerOfMass` of the set *Top
  assembly* lies within ±`aIn`.
- *No further off centre than the statics take it*: that centre of mass is at most `eUse`.
- *Central support inside the anchor polygon*: the central cable's box (`boxMin`/`boxMax`) lies within
  ±`aIn`.
- *Top plate within the box of the statics' load reach Rout*: the top plate's box lies within ±`Rout`. This
  is only a consistency check, because a box within ±`Rout` does not keep every point within `Rout` of the
  centre. That the load's reach is at most `Rout` follows from the outline formulas.
- *Printed parts fit the print bed*: applies to a printed material only.

These are formula checks. A measured size is compared with a bound computed from the statics, so each
holds exactly while its formula condition holds:
- *Outer cables stay taut with the load at the worst edge*: `TminW > 0`.
- *Outer cable* and *Central cable thick enough for its tension*: the modelled diameter is at least
  `d sqrt(T / SWL)`, so `T <= SWL`.
- *Top hook's* and *Base hook's arm deep enough*: the arm reaches at least `bReq` from the cable, so the
  hook carries `Tc` in bending.
- *Base hook's* and *Top hook's post does not buckle*: the hook is no taller than `T + Lbuck`. `Lbuck` is
  the longest post that carries `Tc` in bending and buckling together.

`check-range --deep` passes every point of three runs:
- 94 of 94 with seed 1 (default, 64 corners, 13 choices, 16 random points);
- 142 of 142 with 64 samples and seed 7;
- 142 of 142 with 64 samples and seed 3.

## Cutting

The named face set **Cut sheet** holds the two plates (seen from below) and the two hooks.
`file.export {"path": "table.svg", "set": "Cut sheet"}` (DXF works too) lays them on one sheet at true
size, with the slots, the cable holes (cable diameter + 1 mm) and the tabs. The slots are drawn
`clearance` wider than the sheet and the tabs. A laser's kerf adds about 0.1 mm to that, so 0 to 0.1 mm
gives a tight fit with a laser. Measure your sheet: plywood sold as 18 mm is often 17.5 to 18.5 mm.

## How to assemble and adjust

1. Glue the hooks' tabs into the slots of their plates, square to the plate. The cables push the hooks into
   their plates, but the tabs carry the moment `Tc · p`, so glue them.
2. Set the **central cable** first. Thread it through the holes of both arms and make it the length of
   *Central cable length* between the arms (crimp sleeves, or a shackle and a short turnbuckle for the
   chain). Hang the top from it: it tilts towards its hook.
3. Thread the **outer cables** through the holes in the top and the base. Put a stop (a crimp sleeve, or a
   knot over a washer) under the base and above the top, and a turnbuckle or a cable tensioner in each
   cable.
4. Tension the outer cables in turns, a little at a time, until the top is level and stiff. Aim for `T0`
   in each (`document.inspect` gives it).
   - To measure it, hang a luggage scale in series with one cable, between the cable's end and its
     turnbuckle. Tighten until the scale reads `T0 / 9.81` kg (65 N is about 6.6 kg), then tension the
     others to the same feel or pitch.
   - Give four cables the same tension.
   - Retension after a day, once the cables have settled.
5. Do not load the table beyond `maxLoad` for the chosen cables and sheet.

## Sources

- **Tensegrity.**
  - Kenneth Snelson, *Continuous tension, discontinuous compression structures*, US patent 3,169,611
    (1965), and his writings on "floating compression".
  - R. Buckminster Fuller, *Tensile-integrity structures*, US patent 3,063,521 (1962). Fuller coined the
    word *tensegrity*.
  - R. Motro, *Tensegrity: Structural Systems for the Future* (Kogan Page, 2003): self-stress states, and
    why the compressed parts must be enclosed by the cables.
- **The floating table.** The tensegrity table as makers build it, in the many Instructables and maker
  videos since 2020: a top hung from a hook on the base by one chain and held level by outer chains or
  cables.
- **Statics.**
  - A load shared by vertical members as in a pile or bolt group with a rigid cap: the elastic method in
    any structural analysis text.
  - The Euler load of a cantilever column, buckling length 2L, and the linear interaction of compression
    and bending: any strength of materials text.
- **Wire rope.** Minimum breaking force `F = K d² R` with K = 0.359 for 7x7 (strand core, EN 12385-4) and
  rope grade R = 1770 N/mm². The safe working load is a fifth of it, a factor usual for static rigging and
  an assumption here.
- **Chain.** DIN 766 4 mm (4 x 16): working load limit 200 kg for static suspended loads, minimum breaking
  force 8 kN, from supplier data
  ([Carl Stahl](https://www.carlstahl.com/gb/en/shop/article/variants/lifting-and-rigging-components/special-chains-piece-goods/round-steel-chain-din-766-3-grade-3),
  [Kramp](https://kramp.com/shop-us/en/vp/short-link-chain-din-766-zinc-plated--ticItemGroup-47653107)).
  Decorative chain (DIN 5685) is not tested for strength and is not offered.
- **Sheet.**
  - Bending strength and stiffness: about 40 MPa and 9 GPa for birch plywood along the face grain
    (manufacturers' data, EN 636 and EN 310), and about 25 MPa and 6 GPa for poplar plywood.
  - Creep under the permanent pretension follows EN 1995-1-1 (Eurocode 5). Its kmod for permanent load is
    0.6 for plywood, so sf = 3.5 is about γM / kmod = 1.2 / 0.6 = 2, with a margin for DIY sheet. For MDF,
    kmod permanent is 0.2, which would need a factor of about 8, so MDF is not offered.
  - Printed PLA, solid, printed flat (the hook's moment along the layers): about 50 MPa and 3.5 GPa from
    filament data sheets. Its factor 5 is an assumption, for creep at room temperature. PETG is not offered:
    at about 2 GPa its posts buckle before they carry a useful load at the default size.

This is a sizing aid, not a certified calculation. It does not check creep of the cables, the glue joints,
the floor, or people leaning on the table. A tall, narrow table can also tip over when it is pushed
sideways or leaned on: that is not checked either, so keep tall tables away from where they can be bumped.

`build.json` was written by `python3 -I gen.py > build.json`; edit `gen.py` and run it again to change
the model.
