# Sea kayak (stitch and glue)

A Greenland-style **multichine sea kayak in okoume plywood**, built stitch and glue: two to four hull panels
a side, a two-panel deck with a keyhole cockpit and its coaming riser, sheer clamps, fore and aft bulkheads
with round hatch covers, end pours of thickened epoxy in the stems and an optional hardwood stem strip.
Every panel is laid flat on the floor beside the boat, cut into three pieces with staggered puzzle joints
(a panel is longer than a 2440 mm sheet), with its stitch holes. It is built **entirely by 3DCraft from
formulas**: `gen.py` writes commands and formulas and computes no geometry; its loops only write lists of
commands. Licence: CC-BY-4.0.

**Lines.** The character is that of the Greenland kayak Emanuele Korneliussen built at Igdlorssuit for Ken
Taylor in 1959, surveyed by Duncan Winning in 1964 (the boat behind the Anas Acuta): about 5.2 m long,
0.53 m wide, low volume, strong rocker, raised ends. Its published plans carry no licence that allows reuse
of the offsets, so **these lines are our own**, a parametric family *inspired by* that boat. Its published
hydrostatics (displacement 88 kg, Cp 0.524, LWL 4.00 m, BWL 0.48 m, draft 0.122 m, wetted surface
1.57 m², transverse KM 0.27 m) are the yardstick.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Length overall | Hull | 5300 mm | 5000 to 5800 mm |
| Beam | Hull | 545 mm | 530 to 600 mm at the sheer; at least 570 mm with one chine |
| Depth at the sheer | Hull | 190 mm | 170 mm to min(230 mm, 0.35 × beam): deeper hulls carry their weight too high |
| Deck crown | Hull | 22° | 12 to 26° |
| Bow rise, Stern rise | Hull | 300, 240 mm | 250 to 400, 220 to 350 mm (rocker) |
| Widest station | Hull | 0.47 | 0.44 to 0.52 of the length from the stern |
| Chines per side | Hull | 3 | 1 to 3 (2 to 4 hull panels a side) |
| Ends | Hull | Moderate | Fine, Moderate, Full (table `forms`) |
| End cap | Hull | Hardwood strip | None or a hardwood strip along the stems |
| Paddler weight (kg) | Paddler and load | 80 | 45 to what the hull carries with 45 mm freeboard and GM ≥ 0 (93 kg at 530 mm beam, +0.3 kg per mm, 12 kg less with one chine, at most 110) |
| Paddler height | Paddler and load | 1780 mm | 1500 to 2000 mm |
| Load (kg) | Paddler and load | 5 | 0 to what is left, at most 40 |
| Water | Paddler and load | Sea water | Sea (1025 kg/m³) or fresh (1000 kg/m³) |
| Hull, deck plywood | Plywood | 4, 3 mm | 3 to 5, 3 to 4 mm |
| Stitch hole diameter, edge distance | Plywood | 2, 8 mm | 1.5 to 3, 6 to 10 mm |
| Cockpit length | Cockpit and hatches | 800 mm | 0.34 × height + 100 mm to min(950 mm, 0.57 × height − 40 mm) |
| Cockpit width | Cockpit and hatches | 420 mm | 380 to 460 mm |
| Bulkheads and hatches | Cockpit and hatches | on | off: an open hull for float bags |

## How 3DCraft builds it

`x` runs along the boat (stern −L/2, bow +L/2), `y` to starboard, `z` up from the keel's lowest point; a
station is η from 0 (stern tip) to 1 (bow tip), skewed (η = ξ + s ξ(1 − ξ)) so that η = ½ is the widest
station.

- **The lines.** Every hull panel j is a *generalised cylinder*: in every station a straight line at the same
  flare angle θⱼ, from chine j to chine j + 1, of width Wⱼ G^pⱼ (1 + σⱼ (1 − G)), G = 4η(1 − η), σⱼ the
  sheer spring. At the widest station the chines lie on a quarter ellipse (B/2, D), equally spaced in angle.
  The keel rises as rA u⁴ + rC u⁵ (u = 2η − 1). The deck is one panel a side at the crown angle, from the
  sheer to a ridge on the centre line. Such a surface is developable (do Carmo §3-5) and is exactly the
  extrusion of a plane curve, its *trace*, along its direction: **`sketch.curve` draws each trace from the
  formulas and `feature.extrude` sweeps it**; the ten solids (four hull panels and the deck, each side,
  `when` the hull has them) intersected are the hull envelope, whose edges are the keel, chines and sheer,
  found by the kernel. (`feature.developable` between the chines gives the same surfaces; its sheets cannot
  yet carry the plates, see *What 3DCraft cannot do yet*.)
- **Plywood.** `feature.plate` gives each envelope face its thickness inwards: `touch` at keel and chines
  (the inner edges of two stitched panels just touch; the outside V is the epoxy fillet), the topside
  `under` the deck and the deck `over` it (the deck rests on the topside), `touch` at the ridge, `onto` the
  end planes at η = 0.03 and 0.97. The topside and deck plates come in one version per number of chines.
- **Sheer clamps** (20 × 12 mm, from 15 to 85 % of the length): the region between the topside's inner skin
  and that skin moved 12 mm in, and between the deck's inner skin and that moved 20 mm in, both traces
  offset by formulas and extruded.
- **Bulkheads** (with hatches): the inside of the planking (a second envelope, every trace moved in by the
  plywood) cut to a slab at each bulkhead station (0.57 × height ahead of the seat back, 150 mm behind it),
  notched for the clamps. **Hatch covers**: discs on the deck, 22 mm proud (the envelope raised by 22 mm,
  less the envelope).
- **Coaming riser**: the keyhole ring (an aft circle of half the cockpit's width and a forward one of 0.62 of
  it, joined by tangents), 6 mm wide, outside the envelope and inside the envelope raised by 30 mm: it
  stands 30 mm on the deck all round, following the crown.
- **The ends.** The plywood plates end at η = 0.03 and 0.97, where the panels are only millimetres wide. The
  hull's surfaces run on to the stems (η = 0.004 and 0.996, the panels' own cylinders), and what they enclose
  there is the **end pour** of thickened epoxy a stitch-and-glue builder puts in each end (CLC); inside the
  plywood hull the end pour goes on for 120 mm past each end plane (the inside of the planking within that
  slab). The optional **stem strip** is a hardwood strip 10 × 4 mm under the keel line over the last stretch
  of each end, drawn from the keel's formula.
- **Flat panels.** `feature.unfold` lays the outside skin of each starboard plate flat on the floor (cut two
  of each, stacked face to face, for the pair). Each is cut by three regions into three pieces at two
  **puzzle joints**: a line across the panel with a dovetail key every 73 mm, half way between two stitch
  stations; even rows are joined at v = ±0.375 of the stitch grid (η ≈ 0.30 and 0.70), odd rows at −0.475
  and 0.275, so the joints are staggered; the middle piece lies 50 mm along, the last 100 mm.
- **Stitch holes** along every stitched seam: keel, chines, sheer and ridge. Holes of `holeD` (2 mm), `holeIn`
  (8 mm) from the edge, the usual stitch-and-glue practice of copper wire through 1/16 to 3/32 in holes
  3/8 in from the edge, every 4 to 6 in (CLC; Kulczycki), closer where the panels bend most. The stations are
  one grid along the boat, η = ½ + 0.44 (0.6 v + 0.4 sin(πv/2)) for v from −1 to 1 by 0.05 (about 130 mm
  apart amidships and 65 mm near the ends of a 5.3 m hull); each seam uses the stations where both its
  panels are wide enough. Both panels of a seam get their holes at the *same stations*, each `holeIn` from
  its plate's edge along its own station line, so they pair up across the seam. Where two inner skins touch,
  that edge is `t tan(d/2)` back from the chine (d the seam's angle); the topside ends under the deck, its
  rim on the deck's inner skin, so its edge is `max(tDeck, tDeck − tHull cos d) / sin d` back from the
  sheer (the edge-distance assertion found the touching formula 1 mm short at a 12° crown, where d is 94°). A hole is a circle in the plane
  square to its panel's station normal, at the panel's own formulas, drilled through the plate (both sides
  of the boat); `feature.unfold` carries the holes onto the flat pieces, so they are on the cut sheet.

`gen.py` writes 216 variables and 24 outputs (the version that computed the geometry itself needed 3839 variables), 243 feature
commands and 56 assertions (18 of them edge distances, one per plate, each on only for hulls that have that plate); at 3DCraft 3c885c35 a point of the range check
(regeneration and every assertion) takes 19 to 43 s (median 30 s), a build about 120 s (drilling some 500
holes and the 27 flat pieces are most of it).

**Checked** at 3DCraft `main` 3c885c35 (2026-10-30) with `craft3d-cli check-range`: the defaults, every other
choice (one chine, two chines, Fine and Full ends) and 3 random points (`--samples 3 --seed 1 --no-corners`, 8
points), and 40 of the 2²¹ corners in five runs (`--samples 0 --max-corners 8`, seeds 1 to 5): every point
passes, no assertion unproven. That run found two faults the earlier checks had missed, both fixed here: the
topside's sheer holes 1 mm too close to its edge at a 12° crown (see *Stitch holes*), and GM −0.59 mm at a
single-chine corner 600 mm wide with the heaviest paddler then allowed (the bound is now 12 kg lower with one
chine, not 5). `scripts/check.sh` takes all 64 corners and the random points at once, about 35 minutes; it
was run with `SAMPLES=3 SEED=1` before these fixes and passed the 15 points it reached in 15 minutes.

## What 3DCraft checks (assertions)

| Assertion | What it proves |
|---|---|
| keel, chines 1–3 (each side; on a hull with fewer chines the sheer), sheer, ridge | the least distance between neighbouring plates is 0: the panels meet edge to edge |
| the panels are developable; their Gaussian curvature ≤ 10⁻⁹ mm⁻² | measured on the envelope faces the plates are made of: 0 |
| keel and chines: no two hull panels share volume; the sheer (topside and deck) and the ridge likewise | the overlap measure (boolean intersection) of the drilled plates |
| initial stability | the output GM ≥ 0 (the hull upright at the `levelFor` waterline) |
| free floating: stability and trim | `floatingGM` ≥ 0, `floatingTrim` within ±0.5° and `floatingStable` (`measure.floating`'s equilibrium, G from the outputs) |
| plywood mass | the kernel's mass of the plates (okoume 500 kg/m³) is the weight formula's ± 4 % |
| freeboard | the waterline for boat, paddler and load (`levelFor`) lies 45 mm below the sheer amidships |
| the end pours are dry | above the highest waterline the freeboard allows |
| the coaming stands on the deck; the cockpit lets the knees in | distance 0; its length ≥ 0.34 × height + room behind the seat |
| every flat piece fits a 2440 mm sheet | per piece and joint parity |
| stitch holes keep their distance from the edge | per plate: its hole walls lie at least `holeIn − holeD/2 − 0.5 mm` from its own rim (6.94 to 7.00 mm at the defaults; a hole is `holeIn` from the edge along its station, and the edge crosses the stations at a few degrees where the chines sweep in, so the 0.5 mm allows up to 21°) |
| every stitch hole is drilled | the starboard plates carry exactly the holes the seams call for (the port side the same); no puzzle joint can run into one, as the seams leave out the stations within two of a joint |
| stitch holes pair up across the keel, chine 1, the sheer and the ridge | the nearest hole walls across the seam are no farther apart than two holes at one station, `holeIn` either side of the chine |

## Hydrostatics

Read-only **outputs** of 3DCraft's measures (`variable.measure`, `variable.output`; File › outputs, or
`output.list`), computed after every regeneration: the waterline `T` (`levelFor` the displacement), the
volume, centre of buoyancy (`KB`, `LCB`) and waterplane (`Awp`, its transverse moment `IT`, its length `LWL`,
the `sectionExtent` along x) below it, the midship section below it (`Amidship`), the plywood's centre of
gravity (`zPly`, `xPly`), and from them `BM = IT / Vb`, `KM`, `KG`, `GM`, `LCG`, `trim = LCB − LCG`, the
prismatic coefficient `Cp = Vb / (Amidship · LWL)` and `freeboard` (Biran & López-Pulido, ch. 2–3).
GM ≥ 0 is an assertion on the output. At the defaults (80 kg paddler, 5 kg load, sea water):

| Quantity | 3DCraft (outputs) | Igdlorssuit (published) | Earlier Jig (formulas outside 3DCraft) |
|---|---|---|---|
| Boat, displacement | 15.9 kg, 100.9 kg (∇ 0.0985 m³) | 88 kg | 14.9, 99.9 kg |
| Draft T | 105.6 mm | 122 mm | 107.6 mm |
| Waterline length LWL, prismatic coefficient Cp | 4178 mm, 0.666 | 4.00 m, 0.524 | |
| Waterplane area, midship section | 1.516 m², 0.0354 m² | | 1.445 m² |
| Wetted surface | 1.74 m² (`measure.below`'s surface) | 1.57 m² | 1.69 m² |
| KB, BM, KM | 66, 218, **285** mm | KM 269 mm | 67, 204, **271** mm |
| KG | 250 mm | | 248 mm |
| **GM** | **35 mm** | | **23 mm** |
| LCB, LCG (trim lever) | −124.3, −125.0 mm (0.7 mm) | | −124.0, −123.8 mm |

The ends are fuller than the earlier lines' (bottom panels narrowing as G^1.6 where they had G^2.2: plates
refuse panels narrower than about their thickness), so the waterplane carries more area towards the ends
and BM is 7 % higher; KB and KG are as before.

The fuller ends show in Cp too: 0.666 against the Igdlorssuit's 0.524, on a waterline 4.18 m long against
4.00 m.

**The free-floating equilibrium.** The outputs above take the waterline level (`levelFor`, the hull upright)
and give the trim only as a lever, `LCB − LCG`. 3DCraft's `measure.floating` finds the equilibrium itself, with
the waterplane free to heel and trim until the centre of buoyancy lies on the vertical through G. Its measures
are outputs (`floatOffset`, `floatHeel`, `floatTrim`, `floatGM`, `floatGML`) and assertions, with G at
(`LCG`, 0, `KG`) from the outputs: the transverse GM at least 0, stable against a heel and a trim, and the trim
within ±0.5° either way. That bound is chosen, not from a standard: the ends within about 18 mm of the level
waterline over its 4.2 m length (the default trims 190 times less); the seat is placed by a formula, so the
check is what proves where it trims. At the defaults (3DCraft 3c885c35):

| Quantity | Outputs (`levelFor`, upright) | Outputs of `measure.floating` |
|---|---|---|
| Waterline | T = 105.616 mm | `floatOffset` 105.611 mm along the tilted normal |
| Trim | lever LCB − LCG = 0.728 mm | `floatTrim` 0.00267° (4.66e-5 rad): the bow 0.19 mm down over the LWL |
| Heel | 0 (assumed) | `floatHeel` −3e-9 rad: upright |
| Transverse GM | `GM` 34.65 mm | `floatGM` 34.65 mm |
| Longitudinal GM | | `floatGML` 15.6 m |

They agree. The trim the lever predicts, `atan((LCB − LCG) / GM_L) = atan(0.728 / 15618)`, is 0.00267°, which is
what `measure.floating` finds; the offsets differ by 0.005 mm because the tilted plane's offset is measured from the
origin, not from the centre of the waterplane. So the seat's place trims this hull level within a fifth of a
millimetre at the defaults.

The capacity in the ranges is a block coefficient on the safe side (outputs may not drive the
form's ranges), checked by the freeboard assertion, and the seat is placed 230 mm behind the widest station
(an output may not move geometry); the `trim` output shows how far that is from level.

## What 3DCraft cannot do yet (repros in the 3DCraft repository, plan/repro)

Re-checked against 3DCraft `main` at 3c885c35 (2026-10-30).

- **The plates are on the envelope's faces, not on the developable sheets.** `feature.developable` now builds
  every panel between the chines, the sheer panel `DevTop4S` too (repro 14). At 1f92b83b its faces are
  named by their place (the end fans, the runs, the fans at its folds: `face(0)`, `face(1)`,
  `face(10000000000)`, ...). But a plate on it has to cover all eight faces, with a joint per boundary edge,
  and whether such a plate builds is untested. The whole sheer panel still does not unfold either: the
  strip beside the bow's fold fan is refused (a standing corner, owed), and the flat panels need it. The bottom
  panel's fold cone and the deck (repro 8) are as before. So the Jig keeps its plates on the envelope's faces,
  which are the same surfaces, and **the plates' face and edge names wait** until plates and unfolding on the
  developable sheets work. They are not changed here. Both are still owed by 3DCraft at 3c885c35: a plate
  over a whole developable sheet, and the unfolding of a standing corner (what is said above of the sheets'
  faces was seen at 1f92b83b and not tried again).
- The ends' panels: plates refuse panels narrower than about their thickness, so the plywood ends at η 0.03
  and 0.97 and the end pour is the hull there; the ends table is less fine than the earlier lines
  (p = 1.8, 1.6, 1.3 for the bottom panel, where 2.6, 2.2, 1.8 left panels under a millimetre wide).
- The coaming's lip (repro 10), the riser's developed strip and the bulkheads laid flat by `feature.unfold`
  (repro 11; the bulkheads are flat and on their own cut sheet). Not re-checked.
- Done in 3DCraft since: `levelFor` on this hull (repro 9), measures in outputs and assertions (repro 4; the
  hydrostatics above), the extent of a section (repro 15; `LWL` and `Cp` above), the inside of the planking
  (`InHull`, repro 20), the overlaps the boolean could not decide here (the topside and the deck at the sheer,
  chine 3 against the topside with Fine and Full ends, the keel of a single-chine hull: repros 21 to 24, main
  233bb724; the sheer's overlap is asserted now), the holes' distance from their own plate's rim in seconds
  instead of minutes (repro 25, main 233bb724; asserted per plate now), and `measure.floating` as a measure of
  outputs and assertions (`floatingGM`, `floatingTrim`, `floatingHeel`, `floatingStable`, main 166671c1; GM and
  trim asserted now).

## Cut sheet

Export the named set **Cut sheet: panels** (DXF or SVG, `width` 2440 mm): the flat pieces with their puzzle
keys and stitch holes (`cut-sheet.svg` at the defaults), and **Cut sheet: bulkheads**
(`cut-sheet-bulkheads.svg`). Glue the puzzle joints flat on plastic sheet with thickened epoxy (and glass
tape on the hull panels) before stitching.

## Safety

- A sea kayak is a serious craft: learn to paddle it, brace, rescue yourself and others in sheltered water
  first, with others, and wear a buoyancy aid. Low-volume boats feel tippy until you paddle with your hips.
- With bulkheads and hatches off the hull has no buoyancy compartments: fit float bags fore and aft.
- Epoxy sensitises skin: gloves, ventilation, a respirator when sanding cured epoxy and glass.

## Sources

- PaddlingLight, *Igdlorssuit: Free Kayak Plans for the Boat Before Anas Acuta*: history and hydrostatics,
  quoted for comparison; its plans were not used.
- C. Kulczycki, *The New Kayak Shop*, Ragged Mountain Press 1999, and Chesapeake Light Craft (clcboats.com,
  "Stitch and glue construction"): stitch holes, copper wire, fillets and tape, end pours, okoume weights.
- A. B. Biran and R. López-Pulido, *Ship Hydrostatics and Stability*, 2nd ed., 2014: KB, BM = I/∇, GM.
- *Sea Kayaker* magazine's stability reviews: a paddler's centre of gravity 10 in above the seat.
- S. Pheasant, *Bodyspace*, 1996: buttock–knee length about 0.34 of stature; D. A. Winter, *Biomechanics*:
  the foot brace at about 0.57 of stature from the seat back.
- M. P. do Carmo, *Differential Geometry of Curves and Surfaces*, 1976, §3-5: developable surfaces.

`build.json` was written by `python3 -I gen.py > build.json`.
Built and checked with 3DCraft `main` at 3c885c35 (format version 50); needs that build or a newer one.

**Colours.** Okoume (#D9B98A) hull panels and flat pieces, a copper (#B87350) deck, walnut (#7A5638)
coaming, hatch covers and stem strips, cream (#E8DFCC) clamps, brass (#B8954A) end pours.
