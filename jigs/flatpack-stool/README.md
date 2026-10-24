# Flat-pack stool

A stool or small side table cut from one sheet of plywood on a CNC router or a laser, put together
without screws or glue. Two legs cross at the middle with a half-lap (cross-lap) joint, and the two tabs
on top of each leg go through mortises in the seat. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Height | Size | 450 mm | 300 to 650 mm, step 1 mm |
| Seat size | Size | 340 mm | 260 to 450 mm, step 1 mm |
| Leg style | Size | splayed | straight, splayed, waisted |
| Hand-hold slot | Size | on | on / off |
| Sheet thickness | Material | 18 mm | 9 to 24 mm, step 0.1 mm |
| Kerf | Cutting | 0 mm | 0 to 0.5 mm, step 0.01 mm |
| Clearance | Cutting | 0.2 mm | 0 to 0.6 mm, step 0.01 mm |

**How it is built.** The seat is a square with rounded corners (radius 12 % of the seat, 20 to 50 mm),
turned 45 degrees over the legs, so each leg runs from corner to corner and the stool stands on a wide
base. Its top rim is rounded (2 mm, at most a sixth of the sheet: a router's round-over) and a hand-hold
slot (30 mm wide, with round ends) lies between two leg arms, 25 mm from an edge. Each leg is as wide at
the top as the seat reaches along its diagonal less 30 mm a side; splayed legs widen by 14 % of their
height on each side towards the floor, waisted legs bow in by 8 % of their width at mid height. An arch
between the feet (half the leg's width at the floor) makes four feet. Leg A has the cross-lap slot from
the floor up, leg B from the top down, each to half the leg's height. Slots and mortises are drawn the
sheet thickness plus the clearance wide (and the tab width plus the clearance long).

**Cutting.** Every part is a sketch offset by kerf / 2 (`feature.offsetProfile`) and extruded: the bodies
are the cut paths, so a kerf of 0.15 mm makes the outlines 0.075 mm larger and the slots 0.15 mm
narrower, and the parts come out at their nominal size. For a CNC router whose CAM compensates the tool,
leave the kerf at 0. The named face set **Cut sheet** holds the seat and both legs: File › Export…, DXF or
SVG with *Sheet of set: Cut sheet* (`file.export {"path": "stool.svg", "set": "Cut sheet"}`) lays them on
one sheet at true size, one layer per part. The seat is drawn from below, the face the cutter sees.

**Assembly.** Slide leg B (slot from the top) down over leg A (slot from the floor), then press the seat
onto the four tabs. With the default clearance of 0.2 mm the joints slide; 0 is a press fit for a sheet
that is exactly its nominal thickness. Measure your sheet: plywood sold as 18 mm is often 17.5 to 18.5 mm.

**Checked.** `check-range --deep` passes at the default, 64 corners, every leg style and random points
(83 points with seed 1, 131 with 64 samples and seed 7); regeneration median about 390 ms, at most about
680 ms (most of it the round-over of the rim). At the default and with a waisted leg and no clearance,
`document.interference` finds the three parts touching and nowhere overlapping.

**Notes.** `feature.offsetProfile` does not offset splines yet, so the waisted legs' sides are circular
arcs rather than formula curves, and the two side shapes are two sketches per leg switched by the leg
style (`feature.when`).

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
