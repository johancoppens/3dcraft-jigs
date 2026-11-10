# Catalogue: the 33 Jigs

> **About this file.** The briefs the AI agents built the Jigs from, as written in November 2026: "the coordinator"
> is the agent session that briefed them, and a *Probe* a feasibility test run before a risky Jig was built; what
> the probes found 3DCraft doing wrong is in [`3DCRAFT-FEEDBACK.md`](3DCRAFT-FEEDBACK.md).

The brief for every Jig: what the real thing is, what the form asks, what it must show, its line of the palette, what
it must prove, and its risks. For a Jig from the old collection, *Must improve* lists what was already seen to be
wrong; it is a floor, not the whole job (AGENTS.md: no Jig is grandfathered). Sizes named here are starting points: the
builder verifies every number against the standard or source and cites it.

A builder may improve a brief (a better standard, a better parameter), but changes its domain, its main techniques or
its palette line only with the coordinator. Baseline load times are the old files at 3DCraft `cc90d757`.

For every Jig from the old collection: `build.json` is rewritten by hand or from the old one into a minimal script that
meets AGENTS.md (descriptive variable names, no `gen.py`, tables and patterns instead of repeated steps), `meta.json`
and `formtest.md` are new, the README follows AGENTS.md §6, the preview shows the object as it is used.

The numbers are the folders' (`jigs/NN-<id>/`): from the least to the most demanding by the reviewer's score, then in the
order the catalogue was first written. No Jig ended in the simple tier: the simplest were built up to a real Jig.

## Difficult

### 01. Nest box · `nest-box` · woodwork · new
- **Real thing:** a nest box for garden birds from one plank, sawn and screwed. Entrance hole, floor area and height per
  species from a nature organisation's published table (cite it; several species of the Low Countries).
- **Form:** species (choice from a table), plank thickness, plank width, optional predator guard, hanging style.
- **Shows:** how much a small Jig can do: one choice drives everything through a table; `choicesFrom`; a saw list.
- **Look:** untreated larch, weathered zinc roof strip.
- **Proves:** hole diameter and floor area match the species' row; all boards fit the plank length; hole height above
  floor; drainage and ventilation present.
- **Output:** cut list and a board layout (DXF or SVG).

### 02. Dovetail drawer · `joint-drawer` · woodwork · kept
- **Real thing:** a drawer with through dovetails or finger joints, a bottom in a groove.
- **Form:** the opening it must fit (width, height, depth), board thickness, joint, tails from the width.
- **Must improve:** ask for the opening and the running clearance, not the inside; 1 assertion today (dovetail slope per
  wood type, tail count from width, bottom groove set in from the edge, volume); cut list; a proper knob.
- **Look:** walnut fronts, maple sides.

### 03. Polyhedron net · `polyhedron-net` · paper, education · new
- **Real thing:** a net of a Platonic solid with glue tabs; a slider folds it shut.
- **Form:** solid (choice), edge length, paper thickness, tabs, fold amount.
- **Shows:** `feature.fold` driven by one parameter; a table of dihedral angles; the crease pattern to print.
- **Look:** coloured card, one colour per face family.
- **Proves:** V − E + F = 2 from the table; the enclosed volume (`cavity` on the sheet) against the closed form, within
  0.1 % near closure.
- **Probe (2026-11-08):** feasible for all five solids, 0.03 s per regeneration. One
  sketch per solid (polyline outline, construction creases), one `feature.fold` per solid with `when`, the angle
  `min(fold_pct, 99.99) / 100 * solids[solid].fold`, table with `choicesFrom`. Exactly 100 % is refused (free edges
  that meet: report it), so the form's 100 % is capped at 99.99 % and the README says so. Tabs that fold with the faces
  are refused near closure: show the net without them in 3D and export a separate tabbed pattern (untested: the builder
  proves it). The net coordinates must be in `build.json`, by table or formula, without a committed generator. `panels`
  thickness reaches 99.9 % on most solids, 98 % on the icosahedron: narrow the range by solid.

### 04. Keyboard plate · `keyboard-plate` · laser cutting, electronics · new
- **Real thing:** a column-staggered ergonomic keyboard plate with bottom plate and spacers, for standard mechanical
  switches (cite the switch cutout and key pitch).
- **Form:** rows, columns, stagger per column as a choice of layouts, thumb keys, split or one piece, plate material.
- **Shows:** tables of stagger values; counts change the topology; `sketch.pattern`.
- **Look:** smoke acrylic top on black, bright standoffs.
- **Proves:** cutout size and pitch; key count from rows and columns; web between cutouts; screw posts clear the switches.

### 05. Laser-cut box · `laser-box` · laser cutting · kept (rebuilt with compartments: tier difficult, coordinator 2026-11-08)
- **Real thing:** a finger-jointed box with a loose lid. Named in the chapter on Jigs of 3DCraft's guide: the id stays.
- **Form:** outside or inside size, sheet thickness, finger width, kerf, divider, lid.
- **Must improve:** 0 assertions today (finger counts odd, fit of the lid, smallest finger ≥ the sheet, inner volume in
  closed form); 13 parameters to review; variable names; a nicer look than one colour per panel (real plywood, burnt
  edges); `cut.export` if it fits better than a face set.
- **Look:** birch plywood, dark laser-burnt edges.

### 06. GT2 pulley · `gt2-pulley` · 3D printing · kept · CC-BY-SA-4.0
- **Real thing:** a GT2 timing pulley. Named in the chapter on Jigs of 3DCraft's guide: the id stays; the tooth outline's licence
  and attribution stay.
- **Form:** teeth, belt width, bore type and size; hub, flanges and set screws as options.
- **Must improve:** 14 parameters, too many for a pulley (at most 10); 1 assertion today (pitch diameter = teeth × 2 mm
  / π, wall over the bore and the set screw, flange height); print orientation and first-layer chamfer; 3MF export.
- **Look:** anodised black aluminium with bright teeth, or a printed variant by choice.

### 07. Gridfinity-compatible bin · `gridfinity-bin` · 3D printing · kept
- **Real thing:** a storage bin for the open Gridfinity system (credit Zack Freedman).
- **Must improve:** 13 parameters to cut down; overhang and first-layer checks over the range; 3MF export in print
  orientation; the proof that it seats in the baseplate at far corners.
- **Look:** teal PETG.

### 08. Gridfinity-compatible baseplate · `gridfinity-baseplate` · 3D printing · kept
- **Real thing:** fills your drawer and splits for your print bed. The best "form asks what you know" in the old set.
- **Must improve:** load 1.9 s is at the edge for its tier at the defaults: measure at the largest drawer; 3MF of every
  piece; preview of the plate in a drawer outline.
- **Look:** two-tone grey and green PLA pieces.

### 09. Cable drag chain · `drag-chain` · 3D printing · kept
- **Must improve:** ask for the cable bundle and the machine's travel, derive pitch and link count, not the reverse; 3
  assertions today (bend radius ≥ the cable's minimum, link count from the travel, hinge clearance, wall thickness);
  print layout as a separate export.
- **Look:** black nylon with orange bridges.

### 10. Wooden stair · `wooden-stair` · joinery · new
- **Real thing:** a straight closed stair with housed treads in two CNC-cut stringers.
- **Form:** floor-to-floor height, available run, width, tread thickness, handrail, risers on or off.
- **Shows:** the number of treads comes from a formula; rise and going follow Blondel (2R + G, cite the range and the
  building rule used); the stringers and treads export for the CNC.
- **Look:** oak treads, painted stringers.
- **Proves:** 2R + G within the rule, head height, equal rises to the top, tread count; the Jig refuses what cannot be
  a comfortable stair.

### 11. Cam disc · `cam-disc` · machine building · new
- **Real thing:** a disc cam with roller follower laid out from a motion law.
- **Form:** rise, dwell and return angles, motion law (choice: cycloidal, simple harmonic, 3-4-5), base circle, roller,
  **drive angle**.
- **Shows:** `sketch.curve` from a law chosen in a table; the follower moves with a slider.
- **Look:** ground steel disc, blue follower.
- **Proves:** maximum pressure angle ≤ the limit; minimum radius of curvature > roller radius (no undercut); closed
  profile; lift at key angles.

### 12. Tensegrity table · `tensegrity-table` · woodwork · kept
- **Must improve:** a fine concept with statics: names, 12 parameters checked, a colour that follows the material
  (3DCraft can now do this), hardware drawn better, load limit as an output visible in the form.
- **Look:** walnut plates, plywood hooks, steel cable.

### 13. Sheet-metal enclosure · `sheet-metal-enclosure` · sheet metal · kept
- **Must improve:** names; proof of what bends; the preview with the lid on and a hint of inside; ask for the board's
  size if that is what a maker has; DXF flat patterns as exports.
- **Look:** anthracite powder coat with brass screws.

### 14. 19-inch rack cabinet · `rack-cabinet` · sheet metal · kept
- **Must improve:** names; door hardware; the panel that used to be its own Jig (`rack-panel`) offered as blank or
  punched panels if it costs little; 74 assertions to keep or prune for regeneration time.
- **Look:** blue-grey powder coat.

### 15. Miura-ori · `miura-ori` · origami · kept
- **Must improve:** names; fold slider front and centre; a preview half folded; crease pattern with mountain and valley
  layers for die makers; thick-panel option honest over the range.
- **Look:** cream card with a faint sheen.

## Complex

### 16. Loudspeaker box · `loudspeaker-box` · woodwork, acoustics · new
- **Real thing:** a finger-jointed plywood or MDF cabinet for one driver, sealed or vented, sized by Thiele-Small
  parameters (cite the alignments used).
- **Form:** the driver's Fs, Qts, Vas, baffle cutout and depth; alignment; board thickness; proportions.
- **Shows:** the box is computed from physics, and the net volume is **measured on the model**, minus bracing, port and
  driver, and asserted against the target; port length from Helmholtz with end correction; outputs f3, fb.
- **Look:** walnut veneer with a black baffle.
- **Proves:** net volume within 2 % of target; port velocity limit; driver fits the depth; port clears the back.

### 17. Cycloidal drive · `cycloidal-drive` · 3D printing, robotics · new
- **Real thing:** a single-stage printable cycloidal reducer.
- **Form:** ratio (from the pin count), size, eccentricity, shaft, **input angle**.
- **Shows:** a trochoid from `sketch.curve`; the disc orbits with the input angle; the ratio you see is the ratio asked.
- **Look:** printed orange disc, grey housing, steel pins.
- **Proves:** no undercut (formula), ratio from the counts, walls and clearances; 3MF for each part.
- **Risks:** the regeneration time of a long spline profile through booleans; the range of the eccentricity.

### 18. Geodesic dome · `geodesic-dome` · building, laser cutting · new
- **Real thing:** a timber-strut dome with laser-cut steel or plywood hubs.
- **Form:** radius, frequency (1V to 3V), strut section, hub thickness, truncation.
- **Shows:** a table of chord factors drives counts and lengths; patterns of the icosahedron's symmetry.
- **Look:** pale timber, galvanised hubs.
- **Proves:** Euler's count at each frequency; strut lengths against published chord factors; hub bolts fit the strut.
- **Risks:** feature count at 3V: load budget.

### 19. Welding table · `welding-table` · welding, laser cutting · kept
- Named in the chapter on Jigs of 3DCraft's guide: the id stays.
- **Must improve:** names; load 1 s fine, measure at the largest table; steel look; mass and hole counts as outputs.
- **Look:** bare steel top, black frame.

### 20. Welded plate box · `welded-box` · welding, machine building · kept (was `welded-beam`, redesigned 2026-11-08)
- **Real thing:** a building block for machines, from CNC routers to welding tables, where standard profiles fall short: any
  rectangular box, cube or beam shape up to 3000 mm each way, welded from laser-cut plate of 3 mm and up that locates itself by
  tab and slot, so the straightness the laser's cut gives carries over into self-built machines. Tab clearance is on the form.
  Inside, half-lapped ribs that slide into each other as in the welding table. Holes for mounting are added afterwards through
  Open for editing: the Jig stays simple.
- **Must be (the developer, 2026-11-08):** a full `build.json` from nothing; short discrete recessed tabs at every thickness,
  nothing standing proud, tab length and pitch on the form with the weld share as an output, about 20 to 30 % by default;
  rectangular, circular or triangular cutouts per pair of walls; mass, plate list and weld length for every shape, strength
  never (no strength figures, section stiffness only); no bolt holes, no choice per edge; at most 12 parameters.
- **Look:** dark steel, bright cut edges.

### 21. Tuned chimes · `tuned-chimes` · metalwork, acoustics · kept
- **Must improve:** the preview must show the chime as a beautiful object; names; a scale that fits on the form; hang
  points at the nodes asserted; a tube cut list.
- **Look:** satin aluminium tubes, oak top.

### 22. Sliceform · `sliceform` · laser cutting, art · kept
- **Must improve:** 14 parameters, cut down; 245 features at load 1.8 s: fewer and larger; no lamp (wood temperature cannot be proven; coordinator, 2026-11-09); slice count and finger width by range.
- **Look:** two-tone birch and walnut.

### 23. RC wing · `rc-wing` · aeromodelling, laser cutting · new
- **Real thing:** a built-up balsa or light-ply wing: NACA 4-digit ribs, spars, leading and trailing edges.
- **Form:** span, root and tip chord, NACA code by digits, sweep, washout, rib count, sheet thickness, weight.
- **Shows:** a formula airfoil (`sketch.curve`); every rib cut from a lofted wing by a pattern of plates, each one a part
  for the cut sheet; aerodynamic outputs: wing area, aspect ratio, wing loading, stall speed.
- **Look:** balsa skeleton, blue film on half of the wing (an option).
- **Proves:** area and MAC in closed form; rib count; spar slot fits the stock; airfoil thickness against the NACA formula.
- **Probe (2026-11-08):** feasible. One closed `sketch.curve` (t from -1 to 1, x/c = t²,
  coefficient -0.1036 closes the trailing edge), a ruled `feature.loft`, `document.setTolerance` 0.01 mm (at 1e-6 the
  spline takes 29 s to load). Use the 40-step route: a `feature.pattern` of plates intersected with the loft, 1.6 s at
  12 ribs, 5.2 s at 30: default about 12 ribs, range to about 20 unless the worst point stays in budget. The cut sheet is
  a named face set through `file.export`, since `cut.list` refuses one multi-lump body. The 290-step per-rib copy that
  `cut.export` accepts is exactly what AGENTS.md §3 rules out; report the gap (per-instance formulas in a pattern; a
  pattern of separate plates in `cut.list`) with the probe's reproducer.

### 24. Jansen linkage leg · `jansen-leg` · mechanisms · kept
- **Must improve:** names; a drive angle at the top of the form; foot path drawn; a pair of legs as an option; assembly
  removed. The title stays "Jansen linkage": the name "Strandbeest" is Theo Jansen's, so the id
  became `jansen-leg` (2026-11-10).
- **Look:** plywood bars, walnut triangles, brass pins.

### 25. Dobsonian telescope · `dobsonian-telescope` · woodwork, optics · new
- **Real thing:** a Newtonian on a plywood rocker box with altitude bearings.
- **Form:** mirror diameter, focal ratio, tube type, board thickness.
- **Shows:** optics derive the tube and the secondary; the altitude axis sits at the **centre of mass measured on the
  model**, asserted; the cut sheet holds the box and bearings.
- **Look:** gloss white tube, birch box, black fittings.
- **Proves:** balance within a stated tolerance; focal plane reaches the eyepiece; the fully illuminated field; no tube
  to box collision over the altitude range.
- **Risks:** the balance is a measure of the result, so it can be asserted, not fed back: a closed-form position, asserted.

### 26. Sundial · `sundial` · laser cutting, astronomy · kept
- **Must improve:** 1940 steps to at most 600 with tables and patterns; names; a brass look; a proper gnomon.
- **Look:** brass face and gnomon on slate.

### 27. Astrolabe · `astrolabe` · laser cutting, astronomy · new
- **Real thing:** a planispheric astrolabe for a latitude: mater, plate, rete and rule. Exact stereographic projection:
  almucantars and azimuths are circles with closed-form centres and radii.
- **Form:** latitude, diameter, plate thickness, star count, altitude step, lettering.
- **Shows:** formulas drawing an instrument; a star table (public-domain catalogue, in `ATTRIBUTION.md`); text along
  arcs; the plate changes with the place, the rete does not.
- **Look:** polished brass, deep engraving.
- **Proves:** projected radius of the equator and the tropics against the closed form; horizon position against the
  latitude; the rete's stars inside the rim; smallest engraved gap ≥ the tool.
- **Probe (2026-11-08):** feasible. Real grooves in one plate take 22 s, over budget; with
  the numerals and ticks on a separate limb body they take 3.9 s (slowest point 4.5 s, 716 KB, 485 steps): use that, so
  the instrument looks engraved, with grooves wide enough to read (0.4 mm barely shows at 900 px). Clipping is closed
  form: `acos(clamp(...))` end angles, almucantars as two half-arcs from the bottom point, azimuths ending at
  min(horizon, rim), with a zenith gap of at least w / (2 sin(step / 2)): 53 arcs at every degree from 25 to 60. The
  laser's file comes from sketches (exact arcs, 12 KB), but a named set cannot export a sketch: the builder must make the
  export work from the form (a separate flat engraving face set, or report it), and measure CPU time against the web
  budget. Stars come from a public-domain catalogue, cited, not from memory; southern stars beyond the rete are filtered.

### 28. Solar cooker · `solar-cooker` · sheet metal, energy · kept
- **Must improve:** load 3.4 s for 37 features: why; the preview must show the dish, focused, not the petals laid out;
  names; focal point and pot height asserted; petals as a cut-sheet export.
- **Look:** mirror foil, black steel fork.

### 29. Music box · `music-box` · 3D printing, mechanisms · new
- **Real thing:** a printable cylinder music box: pinned drum, tuned comb, crank.
- **Form:** melody (choice of public-domain tunes in a table), drum size, comb material, tempo, **crank angle**.
- **Shows:** data in a table drives pins; the comb's teeth tuned by the cantilever formula; a slider turns the drum.
- **Look:** cherry case, brass drum, spring-steel comb.
- **Proves:** every pin on a note the comb has, timing per beat, no pin clash, teeth lengths against the formula.
- **Probe (2026-11-08):** feasible: 3 tunes, 175 notes, 18 tracks, 64 beats, comb and crank
  in 221 steps, 731 KB, 0.15 s to open, slowest range point 0.1 s. Tables `tunes` and `notes` (tune, beat, track); per
  tune one sketch of one `sketch.rect` per note, corners read from the table, x within ±πR; `feature.extrude` with
  `wrap` on the drum and `when: tune == k`, joined with the same `when`; `feature.transform` by the crank. Comb: one
  polyline of formula points. The file budget binds first: about 3.8 KB per pin, so about 250 notes over all tunes. Pins
  are rectangular, since a wrapped circle can fail `document.check` (bug, reproducer in the probe's folder). A `make.py`
  may write the tune tables and the per-note steps from committed public-domain tunes. Assert the tooth lengths against
  the formula and the pin positions, which the probe did not.

### 30. Planetary gearbox · `planetary-gearbox` · mechanisms · kept
- **Must improve:** the form asks ratio and size where it can; a drive angle that turns the gears; more than 2
  assertions (Willis ratio, assembly condition, tip clearance, tooth counts); a printable housing and 3MF export;
  assembly removed (AGENTS.md §1).
- **Look:** blue ring, teal planets, orange carrier.

### 31. Two-stage gear reducer · `gear-reducer` · mechanisms, casting · kept
- **Must improve:** load 5.7 s against a budget of 4 s; names; a drive angle; assembly removed.
- **Look:** machine-green cast housing, bright shafts.

### 32. Geared orrery · `orrery` · mechanisms, laser cutting · kept
- **Must improve:** 1859 steps to at most 600 with tables and patterns; a date slider that sets the planets; `trains.py`
  becomes `make.py`, writing tables only; names.
- **Look:** brass and walnut, painted planets.

### 33. CubeSat · `cubesat` · aerospace · kept
- **Must improve:** a full `build.json` from nothing replaces `source.3dcraft` and `edits/`; names; preview deployed.
- **Look:** anodised black frame, deep-blue cells, gold foil.

## Removed from the old collection (2026-11-08)

`key-tags`, `pot-knob`, `phone-stand`, `wavy-vase`, `wall-bracket`, `flatpack-stool`, `welded-table-frame`, `spur-gear`,
`pillow-block`, `shelf-32mm`, `rack-panel`, `electronics-enclosure`, `screw-jar`, `print-in-place-hinge`: they only
scaled a simple shape, or a stronger Jig or example already shows the same. They are in the git history.

`sea-kayak` was dropped on 2026-11-09 (by the developer): a stitch-and-glue kayak could not come near the load and size budgets
without far more work than it would show. It is in the git history.
