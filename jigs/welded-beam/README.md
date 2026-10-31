# Welded beam

A straight beam of any size, **welded from laser-cut plate** (1 to 10 mm, steel or aluminium) that locates
itself by **tab and slot**: four walls, bulkheads inside and end plates, every joint cut into the plates. The
laser cuts the parts flat, straight and to a tenth of a millimetre; tab and slot carries that into the welded
beam without a welding jig, so you can make beams of any section and length to build machines from: the
gantry and frame of a CNC router, a gantry crane's beam, a stiff base. The outputs tell you how stiff and
strong the beam is for the load you set: the section is measured on the model itself. Licence: CC-BY-4.0.

A derivative of the [`welding-table`](../welding-table/) Jig: its tab-and-slot rules, scaled down to sheet.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Length | Size | 1000 mm | 200 to 3000 mm, step 10 mm |
| Width | Size | 100 mm | left + right plate + 40 mm to 600 mm, step 1 mm (over the side plates) |
| Height | Size | 150 mm | top + bottom plate + 40 mm to 600 mm, step 1 mm (over the top and bottom plates) |
| Open side | Size | None (a closed box) | None, Top (U), Bottom (upside-down U), Left (C), Right (C) |
| Top, bottom, left, right plate | Plate thickness | 4, 4, 3, 3 mm | 1 to 10 mm, step 0.5 mm, each |
| Top left, top right, bottom left, bottom right edge | Edges: which plate lies on which | the top and bottom plates on the sides | either plate on the other, each edge |
| Lip (x plate thickness) | Edges | 2 | 2 to 5, step 0.5 |
| Bulkhead thickness | Bulkheads | 4 mm | 1 to 10 mm, step 0.5 mm |
| Bulkhead spacing | Bulkheads | 300 mm | 100 to 1000 mm, step 10 mm (at most) |
| First bulkhead from the end | Bulkheads | 100 mm | 30 mm to half the length, step 1 mm |
| Hole in the bulkheads (%) | Bulkheads | 50 | 20 to 70 % of the smaller inside size, at least 8 mm |
| End plates | End plates | yes | yes, no |
| End plate thickness | End plates | 6 mm | 1 to 10 mm, step 0.5 mm |
| Bolt holes | End plates | M8 clearance | None, M5 to M12 clearance (ISO 273 medium), M5 to M12 tap drill |
| Bolt hole pitch | End plates | 50 mm | 20 to 200 mm, step 5 mm |
| Tab spacing | Tab and slot | 150 mm | 2 x the widest edge tab + 4 x the bulkhead + 20 mm, to 400 mm, step 5 mm (at most) |
| Tab depth in thick plate (%) | Tab and slot | 60 | 50 to 75 |
| Extra fit clearance | Tab and slot | 0 mm | 0 to 0.3 mm, step 0.01 mm |
| Top, bottom, left, right plate | Cutouts between the bulkheads | rounded rectangles, none, triangles, triangles | None, Rounded rectangles, Triangles (truss), Circles, each |
| Rim beside the cutouts | Cutouts | 15 mm | 5 to 100 mm (at least 2 x the plate) |
| Web between the cutouts | Cutouts | 15 mm | 5 to 100 mm (at least 2 x the plate) |
| Cutout corner radius | Cutouts | 6 mm | 1 to 50 mm, step 0.5 mm |
| Material | Material and load | S235 steel | S235, S355 steel; aluminium 5754-H111, 5083-H111, 6082-T6 (table `materials`) |
| Supports | Material and load | Simply supported, load in the middle | Cantilever, Simply supported, Fixed at both ends |
| Point load (N) | Material and load | 1000 | 0 to 50000 |
| Spread load (N/m) | Material and load | 0 | 0 to 50000, on top of the beam's own weight |
| Torque (N m) | Material and load | 50 | 0 to 5000 |

## How it is built

x runs along the beam from one end, y across it (the left side plate at y = 0) and z up (the bottom plate's
underside at z = 0). *Width* and *height* are the box over the walls; the lips of the plates that lie on
others come on top (outputs `overallWidth`, `overallHeight`).

**The walls** are four plates the full length of the beam. At each long edge one plate **lies on the other**:
it reaches past the other's outside face by its lip and carries closed slots, set in from its edge; the
other plate's edge carries the tabs, which go through those slots. That choice is made per edge
(*Edges: which plate lies on which*), so you mark an edge and swap its tabs and slots: the top plate on the
sides gives a top with two lips (a flat, wide top face to mount on), the sides on the top give flush top
corners with the sides standing proud. The plate that lies on another is wider or taller by its lip, which
is *Lip* x its own thickness plus the fit clearance.

**An open side** leaves one wall out: a U channel (open top or bottom) or a C channel (open left or right).
The plates beside it end flush at that side, and the bulkheads and end plates reach to it, with no tabs
there. One wall at most: with two opposite walls out, the bulkheads would be all that joins the rest, and the
beam formulas below would not hold.

**Bulkheads** are cross plates inside the walls, from *First bulkhead from the end* to the same distance
from the other end, evenly, at most *Bulkhead spacing* apart (one in the middle when less than 50 mm is left
between). Each corner is clipped at 45 deg (2 mm + half the thickest wall) to clear the corner joint and its
weld. Each edge has tabs into closed slots in its wall, as many as *Tab spacing* asks, kept a clip away from
the corners. The hole in the middle vents the closed bays while they are welded, and passes cables.

**End plates** sit inside the walls, flush with their ends, and are the faces you bolt to. Their tabs go into
open notches in the walls' ends. The bolt holes are clearance holes (ISO 273 medium) or tap drill holes, on a
grid at *Bolt hole pitch*, centred, at least 2 x the hole from the walls (EN 1993-1-8 asks at least 1.2 x the
hole from an edge; 2 x leaves room for a washer and a socket). Without bolt holes a vent hole of 8 mm is
cut in the middle. The output `tappedThreadOK` says whether an end plate is thick enough for tapped holes: at
least 0.8 x the thread in steel (a standard nut is 0.8 d high) and 1.5 x in aluminium, a rule of thumb.

**The edge tabs** sit on one lattice along the beam, the same for all four edges, whose pitch divides the
bulkhead spacing evenly and is at most *Tab spacing*: half a pitch from each bulkhead, so no tab ever lands
on a bulkhead and every bay between two bulkheads has the same tabs. The lattice goes on into the end bays as
far as a tab fits, 2 mm clear of the end.

**Cutouts** lighten the walls and give access inside, in every bay between two bulkheads. The end bays stay
solid: there the end plate or the beam's end brings its loads in. Each wall has its own pattern:

- **Rounded rectangles**: an odd number per bay, about twice as long as high.
- **Triangles (truss)**: a Warren truss of 2m + 1 panels per bay, its diagonals near 45 deg. Every web (the
  diagonals and the rims) is *Web between the cutouts* wide, and the two half triangles at the bay's ends
  leave a post beside each bulkhead.
- **Circles**: an odd number per bay, as large as the wall allows.

Each keeps *Rim beside the cutouts* from the inside faces of the walls across it, and *Web between the
cutouts* from the bulkheads and from each other, both at least 2 x the plate. Every wall's pattern is centred
in the bay, so the middle of a bay cuts them all (the net section below). The corners are rounded by
*Cutout corner radius*. 3DCraft draws each shape sharp, inset by the radius, and grows it back by the radius
with round corners (`feature.offsetProfile`, the path a round beam cuts).

## The tab-and-slot system

| Joint | Tab | Into |
|---|---|---|
| Edge (each of the four) | on the edge of the plate that does not lie on the other | a closed slot in the plate that lies on it, set in by its lip |
| Bulkhead to wall | on each edge of every bulkhead, one or more | a closed slot in the wall |
| End plate to wall | on each edge of the end plates, one or more | an open notch in the wall's end |

These rules are checked at every regeneration as assertions (formula checks on the sizes the model is built
from), with the geometric check that no two parts overlap (so every tab lies inside its slot):

1. **Slot = tab + clearance on every side.** The clearance per side is 0.05 mm + 2.5 % of the thicker of the
   two plates, plus *Extra fit clearance*: 0.08 mm at 1 mm, 0.15 mm at 4 mm, 0.3 mm at 10 mm. That is within
   what fabricators give: SendCutSend 0.08 mm for thin sheet and 0.13 mm for 1/8 in [1], Fictiv 0.05 to
   0.1 mm per side for laser cutting and 0.2 to 0.3 mm over 6 mm [4]. The outlines are nominal: your cutter's
   kerf compensation makes them true size. Raise *Extra fit clearance* if your slots come out tight.
2. **The weld chooses itself, joint by joint, from the plate the tab enters.**
   - **Plug weld.** Where that plate is thick enough to leave a pocket of at least 3 mm deep and 3 mm wide, the
     tab stops short: it reaches *Tab depth* (50 to 75 %) into the plate [2] and the pocket is filled with a
     plug weld and ground flush, as on the welding table.
   - **Fused tab.** Otherwise the tab goes through and stands 0.2 x the plate proud (Fictiv gives tabs 1.0 to
     1.2 x the material's thickness [4]), and is fused with the slot's edge into a small weld, ground flush where the face must be flat.

   The 3 mm are a bound we chose: a pocket the arc and the wire can reach and fuse at its bottom. At 60 % a
   plug weld needs a plate of 7.5 mm (at 50 % of 6 mm; at 75 % none of the range). So at the defaults every
   joint is a fused tab.
3. **Tab width.** A plug-welded tab is 40 mm wide, the shortest tack bead for semi-automatic MIG on plate
   over 6 mm (JASS 6, quoted by Kobelco [5]). A fused tab is 4 x the plate it is cut from, at least 8 mm
   (PCBWay gives 3 to 5 x the thickness [3]). Bulkhead and end plate tabs are no wider than their share of
   the edge allows. Every tab is at least 1.5 x its plate wide (asserted; Fictiv gives 1.0 to 1.5 x [4]).
4. **Tabs at most *Tab spacing* apart**, along the edges and along the bulkheads and end plates (asserted).
   Tack welds are spaced "approximately 400 mm or less" [5]; with too few the joint closes up as it is
   welded [6]. Thin sheet wants them closer (100 to 150 mm).
5. **A relief in every inside corner.** Every slot has a T-bone at each corner (a circle reaching past the
   slot's end, under the tab's end) and every tab root a dogbone, as on the welding table. A laser leaves its
   beam's radius in an inside corner, more in thick plate, and a square tab would sit on it [1][7]. The radius
   is 8 % of the plate, at least 0.2 mm (Fictiv: at least the kerf's radius, 0.1 to 0.2 mm [4]), and at most
   the slot's width / 4.5 so the two T-bones of a narrow slot fit (asserted).
6. **Edge distances.** A slot is at least 2 x its plate's thickness from that plate's edge: Fictiv's edge
   distance [4], which is why the lip is at least 2 x the plate. Between a bulkhead's or end plate's slot and
   the edge joints at least half the plate is left, SendCutSend's rule for webs [8]. Cutouts keep 2 x the
   plate from every joint. All three are asserted.
7. **No part overlaps another**, checked on the geometry: every tab lies inside its slot.

The tabs locate every part in two directions and hold it square, so the beam goes together on a flat table
without a jig [1][2]. The welds are short (a plug or a fused tab every *Tab spacing*), which keeps the heat
input low.

## Straight and true: cutting, assembling, welding

Tab and slot gives the parts their places to within the clearance (a tenth of a millimetre or two). Welding
shrinks every bead as it cools and pulls the beam towards it [6][15], so the order of the welds decides how
straight the beam stays.

1. **Cut** all plates of one thickness from one sheet if you can (the same rolling, the same stresses),
   with kerf compensation on. Deburr. Check the long plates for flatness; a plate that is bowed will be a
   bowed wall.
2. **Assemble dry on a flat reference**: a welding table or a machined plate. Lay the bottom plate on it,
   knock in the bulkheads and end plates, then the side plates and last the top, every tab fully seated.
   Clamp the beam to the table along its length: **the table's flatness becomes the beam's straightness.**
   Check the end faces' diagonals and the twist (a straightedge across both ends, or winding sticks)
   before the first weld.
3. **Tack every joint lightly**, from the middle of the beam outwards, alternating sides: left then right,
   top then bottom, so each tack is balanced by one opposite it. Let it cool and check straightness and twist
   again: now you can still correct.
4. **Weld in the same order**: fill the plug welds, fuse the tabs, short welds, never a long run on one side.
   Welds far from the neutral axis (the top and bottom edges) bend the beam; matched welds above and below it
   cancel [15]. A beam that is not symmetric (different plates, different edges, an open side) has more weld
   on one side: weld the other side first, or give it a slight pre-camber.
5. **Leave it clamped until cold.** Release, check, and straighten if needed (a heat line on the long side,
   or a press).
6. **For linear rails and machine faces** a welded beam is close, not precise to the hundredth: mill or fly-cut
   the mounting faces after welding, or level them with epoxy, as machine builders do with welded frames.

Aluminium expands twice as much as steel and loses strength beside the weld (the heat-affected zone, below):
weld it with pulsed MIG or TIG, in shorter runs, and expect more distortion. The 5xxx alloys weld well; 6082
loses half its strength next to a weld.

## Strength (outputs)

The beam carries a vertical load (downwards) at the free end (cantilever) or in the middle (supported or fixed
at both ends), a load spread over its length on top of its own weight, and a torque about its axis. Every
output is computed again when you change a parameter, and shown on the Parameters tab below the parameters.

| Output | What it is |
|---|---|
| `sectionArea`, `Iy`, `Iz`, `zNeutral` | **The section, measured on the model** (`measure.section` of the four walls), just beside the first bulkhead, where no tab, slot or cutout is. `Iy` is for bending under a vertical load, `Iz` sideways. The assertions check them against the formula from the plates' rectangles: the model is the beam the numbers describe. |
| `sectionAreaNet`, `IyNet`, `zNeutralNet` | The section through the middle of a bay, through the cutouts |
| `massKg` | The whole beam, from the bodies and the material's density (a mass, in kg; the formulas divide it by 1 kg where they work in plain numbers) |
| `Mmax_Nmm`, `Vmax_N` | The largest bending moment and shear force, own weight included [9] |
| `deflection` | Bending deflection with `Iy` + shear deflection of the side plates [9]. Without cutouts this is the beam. |
| `deflectionNet` | The same with `IyNet` and the side plates' net height. With cutouts the real deflection lies between the two: near `deflection` for small holes, near this one for large. |
| `spanPerDeflection` | Length / `deflectionNet` (for a CNC gantry, aim for thousands to tens of thousands) |
| `sigmaTop_MPa`, `sigmaBot_MPa`, `sigmaMax_MPa`, `bendingUse_pct` | Bending stress at the top and bottom fibres of the net section, and the largest as a share of the design strength |
| `tauShear_MPa`, `tauTorsion_MPa`, `shearUse_pct` | Shear stress in the side plates' net section, shear from torsion, and their sum as a share of the design shear strength fd / sqrt(3) |
| `torsionJ`, `twist_deg`, `twistOpen_deg` | The torsion constant and the twist under the torque: closed (Bredt: 4 A² / ∮ ds / t, as if the walls were solid) and open (Σ b t³ / 3, as if cut through) [9] |
| `shearCentreOffset` | For a C channel: how far the shear centre lies outside the web, e = 3 b² tf / (6 b tf + h tw) [9] |
| `bucklingReserve` | The plates' elastic buckling stress over the stress in them: at least 1, and no plate buckles at this load [10][11] |
| `edgeTabUse_pct` | The shear flow between the top or bottom plate and the sides over one tab pitch, V S / I x pitch, as a share of what a tab carries in shear (its section x fd / sqrt(3)): what the edge joints carry if only the tabs are welded |
| `f1_Hz` | The first natural frequency of bending, from `Iy` and the beam's mass alone: λ² = 3.516, 9.870 or 22.373 for the three supports [12] |
| `strengthOK` | 1 when bending, shear, buckling and the edge tabs are all within their limits |
| `overallWidth`, `overallHeight`, `cut...` | The size over the lips, the plates' widths and heights, the number of bulkheads and the inside size of the bulkheads and end plates: the cut list |

**Design strength `fd`.** For steel it is the yield strength (S235, S355; γM0 = 1.0 [13]). For aluminium it is
the strength of the heat-affected zone over γM1 = 1.1, because tab-welded beams have welds everywhere: 5754-H111
80 MPa, 5083-H111 125 MPa and 6082-T6 125 MPa (260 MPa unwelded) [14], so 72.7, 113.6 and 113.6 MPa. E =
210 GPa for steel and 70 GPa for aluminium, G = 81 and 27 GPa, densities 7850 and 2700 kg/m³.

**Buckling.** A plate buckles at σcr = k π² E / (12 (1 − ν²)) (t / b)² [10]. Here:

- **Top and bottom plates** between the side plates: k = 4, or (a / b + b / a)² where the bulkheads are
  closer than the width.
- **Side plates in bending:** k = 23.9 [11].
- **Plates with a free edge**, beside an open side or along the rim beside a cutout: k = 0.425 + (b / a)²,
  a plate held on three sides and free on the fourth.

Where σcr is above the yield strength the plate yields first, and `bendingUse_pct` governs.

**Not covered.**
- **Lateral-torsional buckling** of an open channel over a long span: a closed box does not suffer it.
  Brace a long channel or close it.
- **Loads brought in locally** (a point load on a thin top plate between bulkheads: put a bulkhead under it).
- **Fatigue.**
- **The exact stiffness of walls with cutouts**, which needs a finite element model. The two deflections and
  the two twists bound it.

A C channel twists under a vertical load through its centroid: load it through its shear centre or close it.

## Cutting

One face set per part, because the plates can each have their own thickness:

| Face set | Parts |
|---|---|
| **Cut: top plate**, **Cut: bottom plate** | one each (none for an open side) |
| **Cut: left side**, **Cut: right side** | one each (none for an open side) |
| **Cut: bulkheads** | `cutBulkheads` of them |
| **Cut: end plates** | two |

**File › Export…**, DXF or SVG, with a set gives its plates at true size with every tab, slot, notch, T-bone,
dogbone, hole and cutout (`file.export {"path": "top.dxf", "set": "Cut: top plate"}`). Put the parts of the
same thickness on one sheet in your nesting software. STEP exports the whole beam. At the defaults the sets
are 24, 21, 17, 17, 8 and 14 closed paths (top, bottom, left, right, bulkheads, end plates).

**Colours.** Steel (#7D858C) or aluminium (#B9BEC4) from the Jigs palette, following the material, as on the
sheet-metal enclosure.

## Checked

At 3DCraft 4e7fa69a (format version 58), with `source.3dcraft` rebuilt from `edits/` (a measured mass is a
mass there, so `07-strength.json` divides `massKg` by 1 kg): `check-range` passes 117 of 117 points. Before:

With 3DCraft `main` at 57ba7632 (format version 53). `check-range` passes 117 of 117 points (the defaults, 64
corners of the 36 parameters' box, every choice, 16 random). With `--deep --samples 500 --seed 7
--max-corners 1024` it passes 1561 of 1561 (1024 corners, every choice, 500 random), none unproven.
Regeneration median about 0.2 to 0.25 s, at most about 1.7 s in the standard run; in the deep
run three corners of the range took 4.8, 6.6 and 8.0 s (the deep check measures every body as well). The
assertions: no overlap, the measured section (area, Iy, Iz) equal to the formula from the plates, a clean
section where it is measured, the number and spacing of the bulkheads, the end plates' bolt holes, and the seven
rule checks above.

By hand, beside the range check: every open side and every cutout pattern on each wall, swapped edges with
1 mm and 10 mm plates together, and the numbers against hand calculation at the defaults without cutouts
(1000 N in the middle of a 1 m beam, 100 x 150 mm, 4 and 3 mm walls): bending deflection F L³ / (48 E I) =
0.0155 mm plus 0.0016 mm from the own weight, and 0.0039 mm of shear deflection, F L / (4 G Aweb), so
`deflection` = 0.0210 mm; mass 16.7 kg, first frequency 446 Hz. The C channel's shear centre
(41.55 mm) was checked by hand too.

## What 3DCraft cannot do yet

Each with a minimal command batch in [`repro/`](repro/), for the 3DCraft repository's `plan/repro`. None stops
the Jig. They are noted so the Jig can use them when they come, not worked around.

- **Outputs with a unit or label of their own** (`repro/01-output-units.json`). Was missing at 57ba7632: no
  force, stress or torque unit, and no label or display unit on `variable.output`, so a stress is a plain number
  with its unit in its name (`sigmaMax_MPa`) and loads are plain numbers in N, N/m and N m. 3DCraft 4e7fa69a has
  N, Pa, MPa, kg and s in expressions, `label` and `unit` on outputs, and measures `mass` as a mass: the Jig
  divides `massKg` by 1 kg in its two formulas and has not moved its loads and stresses to units yet (open).
- **The torsion constant and the shear centre of a section** (`repro/02-section-torsion.json`).
  `measure.section` gives the area, centroid and second moments, but not the torsion constant J or the shear
  centre, so `torsionJ` and `shearCentreOffset` are formulas of the plates rather than measures of the model.
  With cutouts that is the gap: the real torsional stiffness of the perforated box can only be bounded.
  3DCraft 4e7fa69a measures both (`sectionTorsion`, `sectionShearCentre`); the Jig does not use them yet (open).
- **A cut sheet per plate thickness** (`repro/03-set-by-thickness.json`). A named set is a query on the
  geometry and cannot follow a variable. When the thicknesses are parameters, "every plate of 4 mm" cannot be
  one set: there is one set per part, and plates of one thickness are put together when nesting.

## How it is made

The model is `source.3dcraft`, built by 3DCraft's own commands and nothing else: variables, tables, formulas,
conditions (`when`), patterns, booleans, outputs and assertions. Every size, count and choice is a formula in
the document. The commands are kept as eight batches in `edits/`, in order, each one reviewable:

- `01-walls.json`: the inputs, the material table, the rules per edge joint (clearance, plug or fused, tab
  length and width, reliefs, lip), the walls' extents for every choice of edges and open side, the bulkhead
  layout and the tab lattice, the four wall plates.
- `02-edge-tools.json`: per edge, the tabs, dogbones and slots (with T-bones) on the lattice. Each body goes
  into whichever plate the edge's choice gives it to.
- `03-edge-joints.json`: the edge joints: tabs joined to their plate, dogbones and slots cut.
- `04-bulkheads.json`: the bulkheads with their tabs, dogbones, corner clips and hole, and their slots in the
  walls.
- `05-end-plates.json`: the end plates with their tabs, dogbones, bolt holes or vent, and the notches in the
  walls' ends.
- `06-cutouts.json`: the cutouts of each wall (rectangles, truss triangles, circles), as sketches grown round
  by `feature.offsetProfile` and cut.
- `07-strength.json`: material and colour, the measured sections, and the strength outputs.
- `08-checks-and-parameters.json`: the cut sets, the assertions and the published parameters.

`build.json` opens `source.3dcraft`, sets the document info and exports the Jig. To rebuild `source.3dcraft`
from nothing after changing a batch:

```sh
rm -f jigs/welded-beam/source.3dcraft
for e in jigs/welded-beam/edits/*.json; do
  if [ "${e##*/}" = 01-walls.json ]; then craft3d-cli run --new '{"units": "mm"}' --script "$e"
  else craft3d-cli run --script "$e"; fi
done
scripts/build.sh welded-beam && scripts/check.sh welded-beam
```

```sh
craft3d-cli run dist/welded-beam.3dcraftjig \
  --cmd param.set --params '{"values": {"length": "1500 mm", "width": "120 mm", "height": "200 mm", "cutLeft": 3, "cutRight": 3}}' \
  --cmd output.list
```

## Sources

1. SendCutSend, *Mastering tab and slot design for efficient metal fabrication*,
   https://sendcutsend.com/blog/mastering-tab-and-slot-design-for-efficient-metal-fabrication/ (clearance per
   side by thickness; dogbone reliefs; corner radius against cracking).
2. SendCutSend, *Designing sheet metal parts with tab and slots*,
   https://sendcutsend.com/blog/designing-sheet-metal-parts-with-tab-and-slots/ (tab 0.5 to 0.75 of the
   mating part's depth; plug welding; tabs replace welding jigs).
3. PCBWay, *Welded sheet metal parts design guidelines*,
   https://www.pcbway.com/blog/Sheet_Metal/Welded_Sheet_Metal_Parts_Design_Guidelines_a79851e3.html (tab
   width 3 to 5 x the thickness).
4. Fictiv, *Sheet metal tabs and slots assembly*, https://www.fictiv.com/articles/sheet-metal-tabs-and-slots-assembly
   (tab length 1.0 to 1.2 x and width 1.0 to 1.5 x the thickness; clearance 0.05 to 0.1 mm per side for
   laser, 0.2 to 0.3 mm over 6 mm; slot at least 2 x the thickness from the edge; corner radius at least the
   kerf's).
5. Kobelco, *ABC of arc welding* 2003-01 (JASS 6 on tack welds),
   https://kobelco-welding.jp/education-center/abc/ABC_2003-01.html (tack bead at least 40 mm on plate over
   6 mm, pitch about 400 mm or less).
6. TWI, *Distortion control: prevention by fabrication techniques*,
   https://www.twi-global.com/technical-knowledge/job-knowledge/distortion-control-prevention-by-fabrication-techniques-036
   (tacks, sequence, balanced welding).
7. SendCutSend, *Designing laser cut tab and slot parts*,
   https://sendcutsend.com/blog/designing-laser-cut-tab-and-slot-parts (square tabs and the laser's corner
   radius; dogbone reliefs).
8. SendCutSend, *Designing parts to pass DFM*, https://sendcutsend.com/education/video/designing-parts-to-pass-dfm/
   (holes and bridges at least 50 % of the thickness).
9. W. C. Young, R. G. Budynas, A. M. Sadegh, *Roark's Formulas for Stress and Strain*, 8th ed., McGraw-Hill,
   2012 (beam deflections and moments, shear deflection, torsion of closed and open thin-walled sections,
   the shear centre of a channel).
10. S. P. Timoshenko, J. M. Gere, *Theory of Elastic Stability*, 2nd ed., McGraw-Hill, 1961 (buckling of plates:
    k = 4 for a long plate held on four edges, 0.425 + (b/a)² with one edge free).
11. EN 1993-1-5:2006, *Plated structural elements*, Tables 4.1 and 4.2 (kσ = 23.9 in pure bending, 0.43 for an
    outstand).
12. R. D. Blevins, *Formulas for Natural Frequency and Mode Shape*, Van Nostrand Reinhold, 1979 (beams: λ² =
    3.516, 9.870, 22.373).
13. EN 1993-1-1:2005, *Design of steel structures: general rules* (yield strength, γM0 = 1.0); EN 1993-1-8:2005
    Table 3.3 (edge distance of bolt holes).
14. EN 1999-1-1:2007, *Design of aluminium structures: general rules*, Table 3.2b (fo and fo,haz of 5754, 5083
    and 6082; γM1 = 1.1).
15. O. W. Blodgett, *Design of Welded Structures*, James F. Lincoln Arc Welding Foundation, 1966 (shrinkage and
    distortion: welds balanced about the neutral axis).
16. ISO 273:1979, *Fasteners: clearance holes for bolts and screws* (medium series); ISO 2306:1972 (tap drill
    sizes).
