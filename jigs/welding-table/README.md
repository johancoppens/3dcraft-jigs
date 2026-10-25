# Welding table

A system welding table in the style of the 16 mm and 28 mm block tables (Siegmund, Demmeler and the like),
designed to be **laser cut and MIG welded**: a perforated top plate, perforated side plates (skirts) on all
four edges, a grid of half-lapped ribs under the top, and legs and a lower frame of **standard square
hollow section**. Every plate joint is **tab and slot**, with the tabs stopping short of the surface for a
plug weld and a relief in every inside corner. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| System | System | System 16 | System 16, System 28 (table `systems`) |
| Length | Size | 1200 mm | 600 to 2000 mm, step 50 mm |
| Width | Size | 800 mm | 400 to 1200 mm, step 50 mm |
| Rib spacing | Size | 250 mm | 150 to 400 mm, step 10 mm (at most; rounded to the grid and to what the tabs need) |
| Tab spacing | Tab and slot | 200 mm | 100 to 400 mm, step 10 mm (along the skirts, at most) |
| Tab depth | Tab and slot | 60 % | 50 to 75 % of the plate a tab enters |
| Fit clearance | Tab and slot | 0.25 mm | 0.1 to 0.5 mm per side |
| Laser kerf | Tab and slot | 0.3 mm | 0.1 to 0.6 mm (sets the reliefs' radius) |
| Base | Base | Legs and frame | None, Legs, Legs and frame |
| Working height | Base | 900 mm | 600 to 1000 mm, step 10 mm |
| Tube | Base | SHS 80x80x4 | 18 square hollow sections (table `profiles`, below) |

| System | Holes | Grid | Top plate | Depth (with the top) | Skirts and ribs |
|---|---|---|---|---|---|
| System 16 | Ø16 mm | 50 mm | 12 mm | 100 mm | 10 mm |
| System 28 | Ø28 mm | 100 mm | 25 mm | 200 mm | 20 mm |

The skirts and ribs are thinner than the top (10 and 20 mm) so the notches for their tabs in the top's edge
leave at least half the top's thickness of steel to the nearest system hole (rule 6 below); the plate
thicknesses belong to the system and are not a parameter.

## How it is built

The working surface is z = 0, the table's corner at the origin. The top has nX × nY holes (floor(length /
grid) by floor(width / grid)), centred, so a 1200 × 800 System 16 top has 24 × 16 holes, the outer ones
25 mm from the edge. The front and back skirts run the full length under the top's edge, the left and right
skirts between them, flush outside; each carries rows of holes on the same columns, half a grid apart from
the surface. Ribs run both ways under the top, as deep as the skirts, on the lines between two hole columns
(so no hole is blocked), every so many holes as the rib spacing allows, centred, and clear of the legs.
Where they cross they are half-lapped: the ribs across slotted from the top, the ribs along from below.
**Base**: a leg of square tube in each corner inside the skirts, from a 10 mm foot plate to the underside
of the top (welded to both skirts and the top); with *Legs and frame* rails of the same tube between the
legs, 150 mm above the floor. Each foot plate has a 13 mm hole: the vent while the closed tube is welded,
then for an M12 levelling foot.

## The tab-and-slot system

| Joint | Tab | Into |
|---|---|---|
| Skirt to top | on the skirt's top edge, between two hole columns, every *tab spacing* | an open notch in the top's edge |
| Rib to top | on the rib's top edge, one either side of every crossing | a closed slot in the top |
| Rib to skirt | one on each end of a rib, at mid-depth | a closed slot in the skirt |
| Rib to rib | half-lap notches (rib thickness + 2 × clearance wide) | |

The rules, each checked by an assertion at every regeneration (`assert.list`):

1. **Slot = tab + clearance on every side.** Slot width = plate thickness + 2 × clearance, slot length =
   tab width + 2 × clearance. Default 0.25 mm per side: SendCutSend gives 0.003 in (0.08 mm) per side for
   thin sheet, 0.005 in (0.13 mm) for 1/8 in and 0.010–0.020 in (0.25–0.5 mm) for 1/4 in plate and
   thicker [1]; PCBWay 0.1–0.15 mm per side for sheet [3]. Our plates are 10–25 mm, so 0.25 mm sits at
   the tight end of the thick-plate range: snug enough to locate the parts square without a jig [1][2],
   loose enough to assemble with a mallet. The outlines are nominal: the cutter's kerf compensation makes
   them true size.
2. **Tabs stop short of the surface; the pocket is the weld.** A tab reaches *tab depth* (50–75 %) into
   the plate it enters, leaving at least 3 mm. "The tab should be .5 to .75 the depth of the mating part";
   one that sticks out past it is too long, one too short "can't be plug welded easily" [2]. Fabricators
   make the tab shorter than the plate so the slot can be plug welded shut and ground flush [5];
   SendCutSend's weldment example uses a 0.35 in tab in a 0.375 in plate so nothing protrudes [4]. For MIG
   this is the point: a protruding tab has to be ground off (and with it the weld), a flush tab leaves no
   room for weld metal, a recessed tab leaves a pocket the wire fills, fused to the tab's end and both slot
   walls, and ground flush. So the working surface and the skirts' outside faces stay flat; grind the top
   flat and true after welding, as real system tables are.
3. **Tab width at least 40 mm and 3 × the plate.** A plug weld in the pocket is as long as the tab. The
   shortest tack bead for semi-automatic GMAW on plate over 6 mm is 40 mm (JASS 6, quoted by Kobelco [6]);
   PCBWay gives 3–5 × the thickness for a tab [3]. So tab width = max(40 mm, 3 × plate): 40 mm in System
   16, 60 mm in System 28.
4. **Tabs at most 400 mm apart.** Tack welds are spaced "approximately 400 mm or less" [6]; with too few the
   joint closes up as welding proceeds [7]. The assertion takes the longest run without a tab along every
   skirt, inside every rib cell and at every rib end.
5. **A relief in every inside corner.** A laser cannot cut a sharp inside corner: the beam leaves a radius
   of at least half the kerf, so a square tab would ride on it and not seat. Do not shrink the tab or grow
   the slot to compensate (that loosens the joint); add corner reliefs instead [8][9]. Every slot and notch
   has a **T-bone** in each inside corner (a circle tangent to the slot's side, reaching past its end along
   its length, so the relief lies under the tab's end and away from the system holes), and every tab root
   has a **dogbone** (a circle on the corner's bisector, covering the corner) for the slot's sharp edge to
   pass. Their radius is the kerf, at least 0.5 mm: larger than the beam's own corner radius, so it cuts as
   a round. A radius in slot corners also stops cracks starting there [1][2].
6. **Webs of at least half the plate.** Between a notch in the top's edge (with its reliefs) and the nearest
   system hole, and between a skirt's top edge (with a tab's dogbone) and its first row of holes, at least
   half the plate's thickness is left: SendCutSend's rule of thumb for holes and bridges [10]. This is why
   the skirts are thinner than the top.
7. **Two tabs fit in every rib cell, clear of the crossings**; the ribs clear the legs; no part overlaps
   another (an interference check on every body, so every tab lies inside its slot).

**How tabs fight distortion and locate square.** Each tab locates its part in two directions and the slots
hold it square to the top, so the table goes together without a welding jig [1][2][4]; a skirt is held
along the edge by its tabs and pulled square by the ribs' end tabs in its slots. The welds are short plug
welds in the pockets and short stitches, not long continuous runs, which keeps the heat input low.

**How to cut and weld it.**

1. Cut every plate of the cut sheet from S235 or S355 plate (System 16: a 12 mm top, everything else 10 mm;
   System 28: 25 and 20 mm), with the cutter's kerf compensation on. Deburr.
2. Lay the top face down on a flat surface. Knock the ribs in, the ribs across (slotted from the top) first,
   then the ribs along over them, then the skirts, every tab fully seated in the top.
3. Tack every pocket lightly, working from the centre outwards and alternating sides, before any weld is
   finished; then fill the pockets with plug welds in the same order, and stitch the inside corners between
   skirts, ribs and the top.
4. Weld the legs into the corners against both skirts and the top, then the foot plates and the rails.
5. Grind the plug welds flush; machine or grind the top flat.

## Tubes

The legs and rails are square hollow sections, cold formed to EN 10219-2 [11]: the outside corner radius is
2 × wall up to 6 mm wall (the standard allows 1.6 to 2.4 × wall) and 2.5 × wall above (2.0 to 3.0 × wall);
the inside radius is the outside less the wall; the mass per metre is computed from that section and
7850 kg/m³ and matches the standard's tables (40x40x3 3.30 kg/m, 80x80x4 9.22 kg/m).

| Profile | Width | Wall | Outside radius | Inside radius | kg/m |
|---|---|---|---|---|---|
| SHS 40x40x3 | 40 | 3 | 6 | 3 | 3.30 |
| SHS 40x40x4 | 40 | 4 | 8 | 4 | 4.20 |
| SHS 50x50x3 | 50 | 3 | 6 | 3 | 4.25 |
| SHS 50x50x4 | 50 | 4 | 8 | 4 | 5.45 |
| SHS 50x50x5 | 50 | 5 | 10 | 5 | 6.56 |
| SHS 60x60x3 | 60 | 3 | 6 | 3 | 5.19 |
| SHS 60x60x4 | 60 | 4 | 8 | 4 | 6.71 |
| SHS 60x60x5 | 60 | 5 | 10 | 5 | 8.13 |
| SHS 70x70x4 | 70 | 4 | 8 | 4 | 7.97 |
| SHS 70x70x5 | 70 | 5 | 10 | 5 | 9.70 |
| SHS 80x80x4 | 80 | 4 | 8 | 4 | 9.22 |
| SHS 80x80x5 | 80 | 5 | 10 | 5 | 11.27 |
| SHS 80x80x6 | 80 | 6 | 12 | 6 | 13.21 |
| SHS 90x90x5 | 90 | 5 | 10 | 5 | 12.84 |
| SHS 100x100x4 | 100 | 4 | 8 | 4 | 11.73 |
| SHS 100x100x5 | 100 | 5 | 10 | 5 | 14.41 |
| SHS 100x100x6 | 100 | 6 | 12 | 6 | 16.98 |
| SHS 100x100x8 | 100 | 8 | 20 | 12 | 21.39 |

**Cut list.** All cuts square.

| Piece | Qty | Length (variable) | Default |
|---|---|---|---|
| Legs | 4 | working height − 10 mm foot plate − top plate (`legLen`) | 878 mm |
| Rails, long | 2 | length − 2 × skirt − 2 × tube (`railLenX`) | 1020 mm |
| Rails, short | 2 | width − 2 × skirt − 2 × tube (`railLenY`) | 620 mm |

The named sets *Legs (tube)*, *Rails, long (tube)* and *Rails, short (tube)* select them, and an assertion
checks each length against the model (measured together with a part that is always there, because a set
that is switched off cannot be measured). *Steel weight (kg)* reports the mass of the whole table (S235,
7850 kg/m³).

```sh
craft3d-cli run dist/welding-table.3dcraftjig \
  --cmd param.set --params '{"values": {"L": "1500 mm", "profile": "SHS 60x60x4"}}' \
  --cmd assert.list
```

## Cutting

The named face set **Cut sheet** holds the top, the four skirts, every rib and the four foot plates.
File › Export…, DXF or SVG, with the face set "Cut sheet" gives every plate on one sheet at true size, one
layer per body, with every tab, slot, notch, T-bone and dogbone
(`file.export {"path": "table.dxf", "set": "Cut sheet", "width": "3000 mm"}`). STEP exports the whole
table. The default sheet is 607 closed paths.

**Colours.** The table plates bright steel (#B9BEC4), the tubes and foot plates steel (#7D858C), from the
Jigs palette.

## Checked

Assertions: the hole counts (nX × nY in the top, 2 × rows × (nX + nY) in the skirts), no part overlapping
another, the six tab-and-slot rules, the three tube cut lengths and the steel weight.
`check-range` passes 101 of 101 points (the default, 64 corners, every choice, 16 random), also with
`--deep`; 3DCraft `main` (installed CLI, 2026-10-25). Regeneration median about 0.3 s, at most about 3.6 s
native (the largest System 16 table). With `--deep --samples 64 --seed 7` 148 of 149 pass: the one failure
(System 28, width 500 mm, SHS 50x50x3) is not the design but a 3DCraft limitation: the interference check
between a skirt and a leg is refused when the edge of a skirt hole runs exactly along the line where the
tube's flat side meets its corner radius (64 mm from the edge on both), "an imprinted curve that does not
fit the edges it should coincide with". Reported to 3DCraft with a minimal command batch.

## Sources

1. SendCutSend, *Mastering tab and slot design for efficient metal fabrication*,
   https://sendcutsend.com/blog/mastering-tab-and-slot-design-for-efficient-metal-fabrication/ (clearance
   per side by thickness; dog-bone reliefs; corner radius against cracking).
2. SendCutSend, *Designing sheet metal parts with tab and slots*,
   https://sendcutsend.com/blog/designing-sheet-metal-parts-with-tab-and-slots/ (tab 0.5–0.75 of the
   mating part's depth; plug welding; tabs replace welding jigs).
3. PCBWay, *Welded sheet metal parts design guidelines*,
   https://www.pcbway.com/blog/Sheet_Metal/Welded_Sheet_Metal_Parts_Design_Guidelines_a79851e3.html (tab
   width 3–5 × thickness, 0.1–0.15 mm clearance per side).
4. SendCutSend, *How to save time with locating features for weldments*,
   https://sendcutsend.com/blog/how-to-save-time-with-locating-features-for-weldments/ (a tab shorter than
   the plate so nothing protrudes; a snug fit locates the parts).
5. PlasmaSpider forum, *Tabs and slots*, https://www.plasmaspider.com/viewtopic.php?p=190611 (tab shorter
   than the plate, plug welded and ground flush; 1/8–3/16 in tabs in 1/4 in plate).
6. Kobelco, *ABC of arc welding* 2003-01 (JASS 6 on tack welds),
   https://kobelco-welding.jp/education-center/abc/ABC_2003-01.html (tack bead at least 40 mm on plate
   over 6 mm, pitch about 400 mm or less, for SMAW and semi-automatic GMAW).
7. TWI, *Distortion control: prevention by fabrication techniques*,
   https://www.twi-global.com/technical-knowledge/job-knowledge/distortion-control-prevention-by-fabrication-techniques-036
   (number, length and spacing of tacks; sequence).
8. 247TailorSteel, *Mouse ears*, https://247tailorsteel.com/en/about-us/knowledge-centre/blog/mouse-ears
   (corner reliefs instead of a smaller tab or a larger slot).
9. SendCutSend, *Designing laser cut tab and slot parts*,
   https://sendcutsend.com/blog/designing-laser-cut-tab-and-slot-parts (square tabs and the laser's corner
   radius; dogbone reliefs).
10. SendCutSend, *Designing parts to pass DFM*, https://sendcutsend.com/education/video/designing-parts-to-pass-dfm/
    (holes and bridges at least 50 % of the material thickness).
11. EN 10219-2:2006, *Cold formed welded structural hollow sections: tolerances, dimensions and sectional
    properties* (sizes, corner radii, sectional properties).

`build.json` is written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model. Earlier versions of this Jig were a FabBlock-style inch table with tabs in plug-weld slots (the
first version), then a metric block table without tab and slot; this one joins the two.
