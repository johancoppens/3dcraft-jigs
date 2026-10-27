# Sheet-metal enclosure

A two-part sheet-metal case for electronics, the kind a laser cutter and a press brake make from one sheet
each: a **base** (a floor, two side walls bent up with a return flange bent inwards at the top of each, and
a low lip at the front and the back) and a **lid** (a top with short side skirts and a front and a back wall
bent down) that sits on the return flanges and is screwed to them. The model shows the folded parts
assembled, the lid fitted on the base, with the screws; the flat patterns with their bend lines and the
bend table come out by command (below). The sheet-metal counterpart of
[`electronics-enclosure`](../electronics-enclosure/). Licence: CC-BY-4.0.

> **Before you cut.** The base's flat pattern has **no holes in the return flanges** (3DCraft cannot put a
> hole in a flange yet, gap 2 below). Drill them after bending, or mark them on the flat before: on each
> return flange's centre line, retL / 2 in from the flat's outer edge (parallel to the bend lines), at
> x = ± `flatHoleX`, y = ± `flatHoleY` in the flat's axes, Ø of the screw's clearance hole. `retL`,
> `flatHoleX` and `flatHoleY` are derived variables of the document, so they can be read for any
> parameter point (`variable.get`, or the Variables panel). With the defaults: x = ± 136.16 mm,
> y = ± 48.5 mm, retL = 11.4 mm, Ø 3.4 mm.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Inside width | Size | 160 mm | 100 to 400 mm, step 1 mm (between the side walls) |
| Inside depth | Size | 120 mm | 80 to 300 mm, step 1 mm (between the front and back lips) |
| Inside height | Size | 50 mm | 30 to 200 mm, step 1 mm (floor to the lid's underside) |
| Material | Sheet | Steel DC01 | Steel DC01, Aluminium 5754, Stainless 304 (the table below) |
| Thickness | Sheet | 1 mm | 0.8 to 2 mm, step 0.1 mm |
| Extra bend radius | Sheet | 0 | 0 to 2 thicknesses, step 0.1: the inner radius is (the table's minimum + this) × thickness |
| Screws | Fit | M3 | M3, M4 |
| Lid clearance | Fit | 0.5 mm | 0.2 to 1 mm, step 0.1 mm |
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
  corners, where a wall and a lip meet, have a **rect relief** of R + 1.5 t along each edge.
- **Lid.** Its top lies on the return flanges; its side skirts and its front and back walls are bent down
  outside the base with the **lid clearance** all round (the walls stop that far above the floor); its
  corners are relieved as the base's.
- **Screws.** Four pan-head screws (ISO 7045 sizes) through clearance holes (ISO 273 medium: 3.4 mm for M3,
  4.5 mm for M4) in the lid's top and in the middle of the return flanges, near the front and the back.
  The holes in the lid are holes of its sketch, so they are in its flat pattern; those in the return
  flanges are drilled into the folded base (a cylinder subtracted), because a flange cannot have a hole of
  its own yet (platform gap 2 below).
- **Vent slots** (option): a row of slots across the middle of the lid's top, half the inside depth long,
  max(4 mm, 4 t) wide, at a pitch of twice the width plus 2 mm, between the return flanges.
- **Feet holes** (option): four clearance holes in the floor's corners, for screw-on feet or standoffs.
- Each option is a second variant of the part (`BaseFeet`/`BasePlain`, `LidVented`/`LidPlain`) switched
  by `when`, so the holes and slots are in the part's own sketch and in its flat pattern.

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
  asks 2 t + R, a little less). Corner relief: Fictiv asks a relief at least t wide and 1.5 t deep; the relief here is
  R + 1.5 t, so it also reaches past the bend zone.
- Bend allowance, setback, deduction: Machinery's Handbook (*Sheet metal work*), as 3DCraft's bend table
  gives them; DIN 6935 for the deduction (*Ausgleichswert*).

The tables are in `gen.py` (`MATERIALS`, `SCREWS`); 3DCraft has no material catalogue, so the data lives
here.

## Assertions (every point of the range)

| Rule | Assertion |
|---|---|
| bend radius ≥ the table's minimum × t | no bend skin (a cylinder along x or y) of either part has a smaller radius; and there are ten bends |
| flange ≥ 0.7 V to the mould line | the base's lips and the lid's skirts and walls reach that far from the outside of the other leg (their ends lie beyond it), the return flanges from the walls' outside; the walls' flats between their two bends ≥ 0.7 V − R − t |
| hole to bend ≥ 2.5 t + R | the least distance from the feet holes and the drilled return-flange holes to the base's bends, and from the lid's screw holes and vent slots to the lid's bends |
| every corner where two bends meet is relieved | at all four corners of each part the two bends stay at least t apart (without a relief they would meet in a point) |
| the lid clears the base | the lid's skirts and walls lie exactly the clearance from the base's walls and lips, measured at the nearest point (the least distance between the faces) |
| the lid rests on the base | the lid's underside touches the return flanges' tops (distance 0) |
| the screw holes line up | each screw shank's least clearance to the lid and to the base is exactly (clearance − d) / 2 (± 0.01 mm), so it stands in both holes, centred; and the base has four bores of the clearance diameter in the return flanges (a screw in open air, or holes beside the flanges, fail both) |
| nothing overlaps | no two bodies share a volume (the lid rests on the return flanges, the heads on the lid) |

The sheet-metal measures `bendRadius`, `flangeLength`, `holeToBend` and `relief` were the first choice but
cannot be used here (platform gaps 3 and 4 below); the assertions above measure the same rules on the
parts' faces with the general measures (`count` of a face query, `distance`, `clearance`, `overlap`).

## Flat patterns and the bend table

The flat patterns are DXF or SVG cut sheets: the outline on the layer `outline`, the bend lines on `bendUp`
(dashed) and `bendDown` (dash-dot). Every bend of the base is up, every bend of the lid down, seen from
the sketch's side (the inside of the base, the outside of the lid).

```sh
craft3d-cli run dist/sheet-metal-enclosure.3dcraftjig \
  --cmd param.set --params '{"values": {"material": "Aluminium 5754", "t": "1.5 mm", "vents": false}}' \
  --cmd file.export --params '{"path": "base.dxf", "sheetMetal": "BaseFeet"}' \
  --cmd file.export --params '{"path": "lid.dxf", "sheetMetal": "LidPlain"}' \
  --cmd sheetMetal.bends --params '{"feature": "BaseFeet"}' \
  --cmd sheetMetal.bends --params '{"feature": "LidPlain"}'
```

The part to name is the variant that is on: `BaseFeet` (feet holes on) or `BasePlain`, `LidVented` (vent
slots on) or `LidPlain`. `sheetMetal.bends` is the bend table: per bend its angle, inner radius, K-factor,
bend allowance (and the unfold's measured one), setback, deduction and flange length, and the flat
pattern's size and area.

**The base's flat pattern has no holes in the return flanges** (gap 2, *Before you cut* above):
`flatHoleX` = width / 2 − R + BA + wall + BA + retL / 2, with BA = π/2 (R + K t) and wall = height − t − 2R;
`flatHoleY` = ys = depth / 2 − 2R − 1.5 t − max(8 mm, 2.5 t + R + hole).

Bend table with the defaults (steel DC01, 1 mm, R = 1 mm, K = 0.42): bend allowance 2.231 mm, setback
2 mm, deduction 1.769 mm per 90° bend; base flat 283.7 × 142.5 mm (walls 47 mm, lips 10 mm, return
flanges 11.4 mm), lid flat 189.5 × 224.5 mm (skirts 12 mm, walls 49.5 mm).

## Platform gaps (3DCraft at c75ca7b8)

Repros in the 3DCraft repository, `plan/repro/repro-sheet-metal-enclosure-<n>.json`:

1. **The export dialog cannot offer a flat pattern.** File › Export… writes the selection, a named set's
   flat faces or the view; nothing in it reaches `file.export` with `sheetMetal`, so someone using the Jig
   in the window cannot get the cut sheets out (an agent or the CLI can, as above).
2. **A flange cannot have a hole.** The base sketch is one closed profile; a hole for the return flanges
   (beyond the floor's outline) makes a second profile and is refused. The holes are drilled into the
   folded part instead, and are missing from the flat pattern.
3. **A sheet-metal measure cannot name a part a later feature used.** Named, the drilled base is refused
   ("the body went into BaseF; name that feature") and the drilling is refused too ("not a sheet-metal
   part"); measured by default (every part) it works.
4. **A sheet-metal measure fails on a part switched off by `when`**, named or by default (every part), so
   no sheet-metal assertion holds over a range whose options switch variants.
5. **A name glob that starts with `*:` is read as a face of the feature `*`** in `select.query`,
   `set.define` and assertion subjects (`*face(6)` works).
6. **A slot whose end radius is near the thickness breaks the plate** (a stadium slot r 1.5 mm in a 1.5 mm
   sheet: "face cannot be tessellated" or the self-intersection check runs out of work); full circles of
   the same radius are fine. The vent slots are therefore at least 4 t wide (end radius 2 t).

## Sources

- Fictiv, *Sheet metal design guide* (blog.fictiv.com/specifications/sheet-metal): minimum bend radius per
  material, K-factor ranges, relief width and depth.
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
