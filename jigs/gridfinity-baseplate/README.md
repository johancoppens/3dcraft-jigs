# Gridfinity baseplate

A [Gridfinity](https://gridfinity.xyz/) baseplate made to fill a drawer, for 3D printing. Give the
drawer's inside and your print bed: the plate holds as many 42 mm cells as fit, centred, with filler
strips out to the drawer's walls, split into pieces that fit the bed, which lock together with bowtie
clips (or dovetail tabs). Every bin of the [`gridfinity-bin`](../gridfinity-bin/) Jig (and any other
Gridfinity bin) seats in it. Licence: CC-BY-4.0.

The default fills a 400 × 500 mm drawer for a 256 mm bed (Bambu Lab, Prusa class): 9 × 11 cells with
10.75 mm and 18.75 mm fillers, in 2 × 3 = 6 pieces (the largest 220.75 × 186.75 mm), joined by 29 bowtie
clips, Light style.

**Styles and heights.** Light 8.3 mm (a 3.4 mm floor with a window in every cell), Solid 8.3 mm (a full
3.4 mm floor), Weighted 11.3 mm (a 6.4 mm bottom with a weight pocket under every cell) and Thin 4.9 mm
(the standard frame with no floor at all, Zack Freedman's original and rebuilt's thin plate). The floor is
what carries the magnets, the screw holes and the clips' pockets, so the Thin style has none of them: in
the form, Magnet holes and Screw holes are off and Connector is None for it (setting them otherwise is
refused with the reason). A Thin plate's frame is 5.7 mm wide at the bottom between two cells and ends
in a ridge, too little for a dovetail slot with 0.8 mm round it, so its pieces just butt together; the
drawer holds them.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Drawer width | Drawer | 400 mm | 60 to 600 mm, step 1 mm (the inside, left to right) |
| Drawer depth | Drawer | 500 mm | 60 to 600 mm, step 1 mm |
| Drawer clearance | Drawer | 0.5 mm | 0 to 3 mm in total, step 0.1 mm |
| Print bed | Printer | 256 mm | 180 to 400 mm, step 1 mm (the bed's usable size, its smaller side) |
| Style | Plate | Light | Light, Solid, Weighted, Thin (heights above) |
| Magnet holes | Plate | off | on / off (off for Thin) |
| Screw holes | Plate | off | on / off (off for Thin) |
| Connector | Pieces | Bowtie clips | Bowtie clips, Dovetail tabs, None (None for Thin) |
| Connector fit | Pieces | 0.15 mm | 0 to 0.4 mm, step 0.05 mm (play on every side) |

**Layout.** The plate fills the drawer less the clearance, W = drawer − clearance, along each axis:
cells = floor((W − 8 mm) / 42 mm), so each filler strip is at least 4 mm; filler = (W − cells × 42 mm) / 2
on both sides. A piece that carries a filler (the first and last of a row) holds at most
k₀ = floor((bed − filler − tab) / 42 mm) cells (tab: 8 mm for dovetails); the cells are shared out evenly
over ceil(cells / k₀) pieces (at least two when the whole plate is wider than the bed), the last piece
taking what is left. So the first piece of every row and column is the largest. Joints run along cell
boundaries. The pieces lie assembled (`Piece A1` front left, `A2` to its right, `B1` behind it, …), in
alternating colours so the joints show.

**Gridfinity dimensions** (from `scripts/gridfinitylib.py`, shared with the bin Jig).
- Grid 42 mm. The socket of every cell, from its bottom up: 0.35 mm straight at its narrowest (36.3 mm
  square, corner radius 1.15 mm), a 0.7 mm 45° chamfer, 1.8 mm straight and a 2.15 mm 45° chamfer to the
  42 mm opening with 4 mm corners: 5 mm in all. Neighbouring openings meet in a knife edge; here the top is
  0.1 mm lower, leaving a 0.2 mm flat on every ridge (0.1 mm at a plate's edge), which prints cleanly and
  keeps neighbouring openings from touching along a line. A seated bin's base ends 0.15 mm below it.
- A bin stands on the socket's floor: its 0.8 mm bottom chamfer then lies in the plane of the socket's
  0.7 mm one and its 2.15 mm top chamfer in the plane of the socket's, and its straight part stands
  0.25 mm off the socket's (37.2 mm in 37.7 mm), as its 41.5 mm top does in the 42 mm opening.
- Floor under the sockets: Light and Solid 3.4 mm (a 2.4 mm magnet hole on 1 mm), Weighted 6.4 mm,
  Thin none (a bin then stands on the drawer's bottom, flush with the plate's). The plate is that plus
  4.9 mm tall.
- Light: a window through the floor of every cell, leaving a rim that holds the magnets and the connector
  pockets with 0.8 mm round them (3.5 mm at least); with screw holes a cross of 10 mm ribs carries the
  screw's boss. Solid: a full floor. Weighted: a 21.4 mm square pocket 4 mm deep from below in every cell
  for a weight (steel washers, lead or a printed-in nut stack, glued), with four 8.5 mm round-ended
  channels 2 mm deep when there is no connector (they run where the connectors sit).
- Magnet holes: 6.5 × 2.4 mm from the top of the floor, at the four corners of every cell, 8 mm in from
  its sides (as in the bins). In the Weighted style each one touches a corner of the weight pocket below
  it at zero thickness (the magnet hole's circle passes 0.003 mm from the pocket's corner, its floor is the
  pocket's ceiling plane), exactly as in rebuilt's weighted plate; the plate holds, but there is no wall
  there.
- Screw holes: a countersunk M3 clearance hole (3.35 mm, 90° countersink 6.4 mm across) in the middle of
  every cell, to screw the plate to the drawer. In the Weighted style the screw goes through the weight
  pocket: use washers (with a hole) as the weight, or leave those cells' pockets empty.

**Connectors.**
- **Bowtie clips** (default): a separately printed bowtie (butterfly key) 12 mm across the joint, 15 mm
  wide at its ends and 6 mm at the neck, 1.8 mm thick, in a pocket on the underside that spans the joint,
  one at the middle of every cell along every joint. The pocket is the clip grown by the fit on every side
  (and the fit above it), 1.2 mm of floor or more over it. Every piece is cut the same way, so the top
  stays flat and the pieces stay alike. The clips are in the model, in place (body `Clips across x` for
  the joints between columns, `Clips across y` between rows; set `Print: clips`).
- **Play.** The clip's flanks stand at 36.87° (a 3:4 slope) to the line across the joint, so with a fit c
  a joint can open by c / sin 36.87° = c / 0.6 on each half of the clip: 0.25 mm per half at the default
  0.15 mm, about a bin's 0.25 mm side play in its socket (a steeper, longer bowtie would let it open
  three times as much). In the drawer the clearance limits it anyway: all the joints across together
  cannot open further than the drawer clearance.
- **Assembly.** Lay the pieces upside down on a flat table, drop the clips into the pockets (they fall in
  at the fit; a drop of glue if you want them to stay), push the neighbouring piece on, turn the plate
  over and put it in the drawer.
- **Dovetail tabs**: the piece to the left of (or in front of) a joint carries a tab 8 mm deep, 8 mm wide
  at the joint and 12 mm at its end (a 1:4 flare), at the middle of every cell along the joint; the next
  piece has the slot, the tab grown by the fit, from below up to 1.2 mm under the socket's floor (so it
  does not show), and the tab is that less the fit. No loose parts, but the pieces are no longer alike,
  and the bed allowance includes the tab. Its play is fit / sin 14° per joint, more than the bowtie's;
  the drawer clearance limits it the same way.
- **None**: straight joints only.
- Both connector shapes are steeper than a woodworker's dovetail (1:6 to 1:8): a printed clip is short and
  its plastic does not crush, so a steeper flare locks it with less length and less play. The default fit, 0.15 mm on
  every side, is the usual starting point for a hand-assembled FDM fit; print one joint first and adjust.

**Checks (assertions, at every regeneration).**
- One body per piece; cells across × cells deep sockets; the pieces together are exactly drawer −
  clearance wide and deep and start at the origin; each filler is the computed one (measured from the
  plate's edge to the first socket) and at least 4 mm.
- The largest piece (the first) fits the bed both ways, the others hold no more cells, and there are at
  most 5 × 5 pieces.
- The plate's height.
- Fit: a bin's foot (the same profile as `gridfinity-bin`, hidden in the view) seated in the first cell
  overlaps nothing and touches the socket's chamfers (clearance 0), and its straight sides stand 0.25 mm
  off the socket's; no two parts overlap (pieces, clips and the foot).
- Bowtie clips: one per cell along every joint, two half pockets per clip, the flanks at 36.87° (a
  face of that normal on every clip), and the play per half, fit / 0.6, 0.25 mm at the default fit (a
  formula check, from the measured angle).
- Bowtie gap, by volume: a box round the first clip's pocket, less the two pieces and the clips (the real
  bodies), leaves exactly the pocket's volume (the clip's outline grown by the fit, times its height,
  a closed form in the fit) less the clip's; with no overlap this proves the pocket is the clip grown by
  the fit all round. And the least distance from the clips to the pockets is the fit: at least the fit on
  every side, exactly the fit on the closest.
- Dovetails: one tab per cell along every joint; the same gap-volume check round the first tab (slot
  volume less tab volume, closed form) and the same distance check.
- The pockets and slots keep 0.8 mm (two perimeters) from the magnet and screw holes, the windows, the
  weight pocket, the sockets and the top of the floor. Measured on a hidden check body: a box 1.2 mm
  larger than the first pocket (or slot) all round and up into the socket, less the two pieces, which
  holds the pocket's void and every other void that comes near it; a small body, so the distance is
  proven. Every joint is made the same way.

- Without joints, the distance checks measure the hidden foot against the plate's edge instead (a measure
  needs something to measure), a distance the assertion knows, and the gap boxes stay whole.

**Printing.** Each piece flat, top up, no supports (the sockets' 45° chamfers and the windows print
without). PLA or PETG, 0.2 mm layers, a 0.4 mm nozzle, two or three perimeters, 15 % infill. The clips
flat; PETG clips are a little more forgiving. Glue or press the magnets in. Export each piece by its body name (`Piece A1`, …) and the
clips (`Clips across x`, `Clips across y`) as STL or 3MF, for instance
`file.export {"path": "A1.3mf", "bodies": ["Piece A1"]}`. The named sets `Print: pieces` and
`Print: clips` list them. The hidden `Fit check foot` and the hidden cut bodies (`Cuts`, `Tabs`) are part
of the checks, not parts to print, as are the hidden `Clip gap`, `Tab gap`, `Pocket check` and `Slot check`.

**Checked.** With 3DCraft `main` 5c9153e2: `check-range` passes at the default, 64 corners, the five
choices and 16 random points (seed 1), also `--deep`: 86 of 86, none with unproven assertions;
regeneration median about 130 ms, at most about 5 s (a 600 × 600 mm drawer on a 180 mm bed: 14 × 14
cells in 25 pieces). STL export of a piece and the clips closed. For a fine STL export, export one piece
at a time (the mesh tolerance follows the size of what is exported).

**Sources.**
- Gridfinity by Zack Freedman (Voidstar Lab), 2022, MIT licence; the unofficial specification at
  [gridfinity.xyz](https://gridfinity.xyz/specification/) and
  [github.com/gridfinity-unofficial/specification](https://github.com/gridfinity-unofficial/specification).
- The socket profile, plate height, corner radius, magnet and screw holes and the weighted pocket as
  kennetek's [gridfinity-rebuilt-openscad](https://github.com/kennetek/gridfinity-rebuilt-openscad) (MIT)
  writes them down (`src/core/gridfinity-baseplate.scad`: `_BASEPLATE_PROFILE`, `BASEPLATE_HEIGHT`,
  `BASEPLATE_OUTER_RADIUS`; `src/core/standard.scad`: `bp_h_bot`, `bp_cut_size`, `bp_cut_depth`,
  `bp_rcut_*`, `MAGNET_HOLE_*`, `d_hole_from_side`; `d_screw` 3.35 in `gridfinity-rebuilt-baseplate.scad`);
  its fit-to-drawer option (cells that fit, the rest as padding) is the same idea as the layout here. No
  code was taken from it.
- Joined baseplates with separate clips are a common Gridfinity remix, e.g.
  [CLICKbase](https://www.printables.com/model/982173-clickbase-a-no-magnet-latching-gridfinity-baseplat).
  The bowtie is the woodworker's [butterfly joint](https://en.wikipedia.org/wiki/Butterfly_joint), two
  dovetails joined at their narrow ends; see [dovetail joint](https://en.wikipedia.org/wiki/Dovetail_joint)
  for the 1:6 to 1:8 slopes used in wood.
- Fit for FDM prints: 0.1 mm per side tight, 0.15 mm a safe general fit, 0.2 mm easy
  ([CCI Digital Fabrication Lab, *Design the clearance and tolerance*](https://wiki.cci.arts.ac.uk/books/digital-fabrication-lab/page/design-the-clearance-and-tolerance)).

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` (or `scripts/gridfinitylib.py`)
and run it again to change the model.
