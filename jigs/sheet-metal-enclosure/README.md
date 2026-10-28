# Sheet-metal enclosure

A two-part sheet-metal case for electronics, the kind a laser cutter and a press brake make from one sheet
each: a **base** (a floor, two side walls bent up with a return flange bent inwards at the top of each, and
a low lip at the front and the back) and a **lid** (a top with short side skirts and a front and a back wall
bent down) that sits on the return flanges and is screwed to them. The model shows the folded parts
assembled, the lid fitted on the base, with the screws; the flat patterns with their bend lines and the
bend table come out by command (below); every hole, the return flanges' screw holes included, is cut in
the flat. The corners are closed (overlap by default) with a gap you set. The sheet-metal counterpart of
[`electronics-enclosure`](../electronics-enclosure/). Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Inside width | Size | 160 mm | 100 to 400 mm, step 1 mm (between the side walls) |
| Inside depth | Size | 120 mm | 80 to 300 mm, step 1 mm (between the front and back lips); raised where the screws at the front and the back need more room (2 mm between their heads) |
| Inside height | Size | 50 mm | 30 to 200 mm, step 1 mm (floor to the lid's underside) |
| Material | Sheet | Steel DC01 | Steel DC01, Aluminium 5754, Stainless 304 (the table below) |
| Thickness | Sheet | 1 mm | 0.8 to 2 mm, step 0.1 mm |
| Extra bend radius | Sheet | 0 | 0 to 2 thicknesses, step 0.1: the inner radius is (the table's minimum + this) × thickness |
| Screws | Fit | M3 | M3, M4 |
| Lid clearance | Fit | 0.5 mm | 0.2 to 1 mm, step 0.1 mm |
| Corners | Corners | Overlap | Open, Butt, Overlap, Miter (below) |
| Corner gap | Corners | 0.5 mm | 0.1 to 2 mm, step 0.1 mm; for a butt at most the thickness less 0.1 mm |
| Corner relief | Corners | Round | Rect, Round, Tear, R + t + 0.5 mm along each edge |
| Vent slots | Options | on | on / off |
| Feet holes | Options | on | on / off |

## How it is built

Both parts are `feature.sheetMetal`: a flat base from a sketch (holes allowed) with flanges bent from its
edges or from the far edge of an earlier flange, every bend with the inner radius R and the material's
K-factor, so the flat pattern carries the bend allowance θ (R + K t) per bend. Every size is a formula of
the inputs (`gen.py` writes `build.json`; it computes no geometry).

- **Base.** The floor is the inside size less R each side, so the walls' inner faces lie at ± width / 2 and
  the lips' at ± depth / 2. Side walls `height − t − 2R` long (the return flange's top is then the inside
  height above the floor), return flanges bent up again (inwards), front and back lips. The floor's four
  corners, where a wall and a lip meet, have a **corner relief** (below) and are **closed**: the walls
  cover the lips' ends.
- **Lid.** Its top lies on the return flanges; its side skirts and its front and back walls are bent down
  outside the base with the **lid clearance** all round (the walls stop that far above the floor); its
  corners are relieved and closed as the base's, the front and back walls covering the skirts' ends.
- **Screws.** Four pan-head screws (ISO 7045 sizes) through clearance holes (ISO 273 medium: 3.4 mm for M3,
  4.5 mm for M4) in the lid's top and in the middle of the return flanges, near the front and the back.
  The holes in the lid are holes of its sketch; those in the return flanges are holes of the base's sketch
  too, drawn where the return flanges lie in the flat pattern (x = ± `flatHoleX` = width / 2 − R + BA +
  wall + BA + retL / 2, with BA = π/2 (R + K t), y = ± `flatHoleY`), so both are cut flat, and the screws'
  assertions prove that they line up once bent.
- **Vent slots** (option): a row of slots across the middle of the lid's top, half the inside depth long,
  max(4 mm, 4 t) wide, at a pitch of twice the width plus 2 mm, between the return flanges.
- **Feet holes** (option): four clearance holes in the floor's corners, for screw-on feet or standoffs.
- The vents and the feet holes are `cutouts` sketches of the lid and the base, each switched on and off by
  its option (`when`), so they are cut in the flat pattern too. (Before, each option was a second variant
  of the part and the return flanges were drilled by a boolean: two parts and three booleans fewer now.)

## Corners and reliefs

**Corners.** Where two flanges meet at a corner the Jig closes the corner by the *Corners* choice
(`feature.sheetMetal`'s `corner` and `corners`, the choice numbered 1 open, 2 butt, 3 overlap, 4 miter),
the flats running on past their bends towards the other flange and stopping *Corner gap* from it:

- **Overlap** (the default): the covering flange runs flush with the other's outside face, the other
  stops the gap short of the cover's inside face. On the base the walls cover the lips, on the lid the front
  and back walls cover the skirts, so the tall flange's end is seen from the side and the seam is closed to
  the eye. It is what a shop folds for an unwelded box: it closes the corner without welding, tolerates the
  press brake's angle error (the covered flange has the gap to move) and needs no finishing.
- **Butt**: as overlap, the covering flange also the gap short of flush (the gap must be less than the
  thickness, so the range of *Corner gap* is narrowed to t − 0.1 mm when butt is chosen).
- **Miter**: both flanges to the plane halving the corner, the gap apart; the ends are bevelled (cut square
  by a laser, the gap takes that up), the joint to weld or braze.
- **Open**: each flange ends at its bend, as before (the corner is open by the relief and the bend radii).

**Reliefs.** Every corner keeps its relief: a closed corner needs it as the hole where the two bends would
cross. Its shape is the *Corner relief* choice (relief `shape` by expression, 1 rect, 2 round, 3 tear),
its size **R + t + 0.5 mm** along each edge, the same rule as in [`rack-cabinet`](../rack-cabinet/): the
relief reaches past the bend zone (inner radius plus thickness) by half a millimetre, as SendCutSend's
bend relief guide asks (depth at least bend radius + thickness + 0.020 in; *Guide to designing bend
reliefs in sheet metal*, sendcutsend.com/blog/guide-to-designing-bend-reliefs). **Round** is the default:
a round relief has no sharp inside corner to start a crack from and is the smallest hole at a closed
corner; rect is the classic square notch, tear the largest (a disc tangent to both edges).

Colours: the parts in the Jig palette's steel (#7D858C) for DC01 and aluminium (#B9BEC4) for 5754, a
lighter, bluer tint (#C8CED6) for stainless 304; the screws brass.

## The material table

| Material | Min. inner radius | K-factor | V-die opening | Min. flange (0.7 V, to the mould line) |
|---|---|---|---|---|
| Steel DC01 (EN 10130, cold rolled) | 1.0 t | 0.42 | 8 t | 5.6 t |
| Aluminium 5754 (AlMg3, H22) | 1.0 t | 0.38 | 6 t | 4.2 t |
| Stainless 304 (1.4301) | 2.0 t | 0.45 | 10 t | 7 t |

- Minimum inner radius: Fictiv's sheet-metal design guide gives 0.5–1.0 t for cold-rolled steel and for
  5052 aluminium (an Al-Mg alloy like 5754) and 1.0–2.0 t for stainless 304; the table takes the upper
  (safe) end of each. Air-bent on the die below, steel takes a natural radius of about V/6 to 0.16 V
  (≈ 1.3 t), so a radius from the table is a minimum, not a promise; set Extra bend radius when your shop
  says what its tooling gives.
- K-factor: Fictiv, soft (aluminium) 0.33–0.40, medium (steel) 0.40–0.45, hard (stainless) 0.45–0.50;
  OSHCut, about 0.4 for soft and 0.45 for harder metals. Cross-check for steel: DIN 6935's correction
  factor k = 0.65 + ½ log₁₀(r/s) (the neutral fibre at k·s/2) gives K = 0.33 at r = s and 0.40 at r = 2s.
- V-die opening: Durmapress, *How to select the right press brake V-die opening*: 6–8 t for mild steel,
  8–10 t for stainless, 4–6 t for aluminium (the upper end taken).
- Minimum flange: S. Benson, *The Fabricator* (press-brake bending tips): the shortest flange a standard
  V die bends comfortably is about 70 % of the die width; it is measured from the outside mould line.
- Hole to bend: 2.5 × thickness + bend radius from the hole's edge to the bend's tangent line, as Xometry's
  sheet-metal design guide and Addmaker's *Tips for making sheet metal parts* give it (Fabcon's DFM guide
  asks 2 t + R, a little less). Corner relief: R + t + 0.5 mm (*Corners and reliefs* above).
- Bend allowance, setback, deduction: Machinery's Handbook (*Sheet metal work*), as 3DCraft's bend table
  gives them; DIN 6935 for the deduction (*Ausgleichswert*).

The tables are in `gen.py` (`MATERIALS`, `SCREWS`); 3DCraft has no material catalogue, so the data lives
here.

## Assertions (every point of the range)

| Rule | Assertion |
|---|---|
| bend radius ≥ the table's minimum × t | `bendRadius` of both parts; and there are ten bends |
| flange ≥ 0.7 V to the mould line | `flangeLength` measured to the mould line, every flange of both parts |
| hole to bend ≥ 2.5 t + R | `holeToBend`: every hole and vent slot of both parts, the return flanges' screw holes included, from the bends beside its flat |
| every corner where two bends meet is relieved | `relief` |
| the closed corners' gap is as given | `cornerGap` (through the output `cornerGapMeasured`): the least gap at every closed corner of both parts equals *Corner gap*, ± 0.001 mm; with *Corners* open there is nothing to measure and the assertion is *not proven* (below) |
| the lid clears the base | the lid's skirts and walls lie exactly the clearance from the base's walls and lips, measured at the nearest point (the least distance between the faces) |
| the lid rests on the base | the lid's underside touches the return flanges' tops (distance 0) |
| the screw holes line up | each screw shank's least clearance to the lid and to the base is exactly (clearance − d) / 2 (± 0.01 mm), so it stands in both holes, centred; the base has four bores of the clearance diameter in the return flanges, and the four feet holes when they are asked for |
| nothing overlaps | no two bodies share a volume (the lid rests on the return flanges, the heads on the lid) |

The sheet-metal measures replace the face queries the Jig needed before (platform gaps 3 and 4, fixed).

## Flat patterns and the bend table

The flat patterns are DXF or SVG cut sheets: the outline on the layer `outline`, the bend lines on `bendUp`
(dashed) and `bendDown` (dash-dot). Every bend of the base is up, every bend of the lid down, seen from
the sketch's side (the inside of the base, the outside of the lid).

```sh
craft3d-cli run dist/sheet-metal-enclosure.3dcraftjig \
  --cmd param.set --params '{"values": {"material": "Aluminium 5754", "t": "1.5 mm", "vents": false}}' \
  --cmd file.export --params '{"path": "base.dxf", "sheetMetal": "Base"}' \
  --cmd file.export --params '{"path": "lid.dxf", "sheetMetal": "Lid"}' \
  --cmd sheetMetal.bends --params '{"feature": "Base"}' \
  --cmd sheetMetal.bends --params '{"feature": "Lid"}'
```

In the window, File › Export to .dxf or .svg offers the flat pattern of each part, and both on one sheet.
`sheetMetal.bends` is the bend table: per bend its angle, inner radius, K-factor, bend allowance (and the
unfold's measured one), setback, deduction and flange length; per corner how it is closed (kind, gap,
which flange covers) and its relief; and the flat pattern's size and area.

Every hole is in the flat patterns: the return flanges' and the lid's screw holes, the feet holes and the
vent slots when they are on. A closed corner's flange runs past its bend in the flat (a tab beside the
relief); the overlap's and butt's ends are square, a miter's bevelled ends are cut square at the bottom
skin's outline (the gap takes that up).

Bend table with the defaults (steel DC01, 1 mm, R = 1 mm, K = 0.42): bend allowance 2.231 mm, setback
2 mm, deduction 1.769 mm per 90° bend; base flat 283.7 × 142.5 mm (walls 47 mm, lips 10 mm, return
flanges 11.4 mm), lid flat 189.5 × 224.5 mm (skirts 12 mm, walls 49.5 mm); round reliefs of 2.5 mm, the
corners closed by overlap with a 0.5 mm gap.

## Platform gaps (3DCraft at 0b2f171e)

Repros in the 3DCraft repository, `plan/repro/repro-sheet-metal-enclosure-<n>.json`. Gaps 1 to 6 of the
first version (the export dialog without flat patterns, no hole in a flange, the sheet-metal measures on a
part a boolean took or one switched off, `*:` globs, slots with a small end radius) are fixed in 3DCraft;
the Jig now uses what fixed them (holes in the flat, `cutouts`, the sheet-metal measures, vent slots
4 mm wide in any thickness).

7. **`cornerGap` is broken when no corner is closed**, and an assertion has no condition: with *Corners*
   open the measure fails ("no corner of the part is closed"), so an assertion on it breaks every point
   of the range where the Jig's choice opens the corners. The Jig measures it into an output and asserts
   `if(corner == 1, gap, cornerGapMeasured)`, but an unknown output makes the assertion *not proven* even
   in the branch not taken, so `check-range` counts the open points as *with unproven assertions*
   (passed with `--strict` off, failed with it on). Either a measure that says "no closed corner" as a
   value an assertion can accept, a condition on an assertion, or an `if` that does not look at the branch
   it does not take would make them pass.

## Sources

- Fictiv, *Sheet metal design guide* (blog.fictiv.com/specifications/sheet-metal): minimum bend radius per
  material, K-factor ranges.
- SendCutSend, *Guide to designing bend reliefs in sheet metal* (sendcutsend.com/blog/guide-to-designing-bend-reliefs)
  and *What are SendCutSend's bend relief requirements?* (sendcutsend.com/faq/what-are-your-bend-relief-requirements):
  relief depth at least bend radius + thickness + 0.020 in (the corner relief R + t + 0.5 mm here).
- Xometry, *Sheet metal design guide*; Addmaker, *Tips for making sheet metal parts*
  (mag.addmaker.tw, 2021); Fabcon, *Sheet metal DFM guide* (fabcon.com): hole-to-bend distance.
- OSHCut, material details, stainless 304 (oshcut.com/materialdetails/stainless-steel-304-1-finish): K-factor
  rule of thumb.
- Durmapress, *How to select the right press brake V-die opening: rule of 8 & material chart*
  (durmapress.com): die openings per material.
- S. Benson, *Press brake bending tips for forming tapered bends and determining minimum flange lengths*,
  The Fabricator (thefabricator.com): minimum flange ≈ 0.7 × die width.
- DIN 6935:2011-10, *Kaltbiegen von Flacherzeugnissen aus Stahl*: the correction factor for the neutral
  fibre and the bend deduction, as published descriptions give them.
- E. Oberg et al., *Machinery's Handbook*, 30th ed., *Sheet metal work* › *Bend allowance*.
- ISO 273 (clearance holes for bolts and screws, medium series); ISO 7045 (pan head screws).

## Checked

`check-range` with 3DCraft `main` at 0b2f171e (format 44): 89 of 89 points without a failure (64 corners,
every choice, 16 random; seed 1), 48 passed and 41 not proven, every one of those with *Corners* open
(gap 7 above); with `SAMPLES=64 SEED=7 DEEP=1` 137 of 137 without a failure. Regeneration median about
35 ms a point (28 ms before the rework, with fewer parameters, open corners and the return flanges
drilled by a boolean).
