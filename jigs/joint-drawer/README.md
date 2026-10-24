# Dovetail and finger-joint drawer

A drawer or box for woodworkers: four boards joined at the corners with through dovetails or finger (box)
joints, a bottom in a groove and a brass knob. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Inner width | Size | 240 mm | 60 to 600 mm, step 1 mm |
| Inner depth | Size | 200 mm | 60 to 600 mm, step 1 mm |
| Inner height | Size | 100 mm | 40 to 250 mm, step 1 mm |
| Board thickness | Size | 15 mm | 8 to 22 mm, step 0.5 mm |
| Joint | Joints | dovetail | finger, dovetail |
| Tails (fingers) | Joints | 3 | 1 to height / (2.2 × thickness), at most 12 |
| Dovetail slope | Joints | 1:8 hardwood | 1:6 softwood, 1:8 hardwood |
| Bottom in a groove | Details | on | on / off |
| Knob | Details | on | on / off |

**How it is built.** The front and the back carry the tails; the sides carry the sockets, so the dovetail
shapes show on the front and the back, and the tails' end grain on the sides (a classic drawer has its
tails on the sides; here the joint is what you see from the front). A tail is a prism:
`TW` wide at the end of the board, narrowing by the slope towards its baseline at the side's inner face.
The pins between the tails are `pn` wide at the end of the board (a quarter of the pitch, 4 to 20 mm),
with half pins as wide at the top and the bottom edge. The sockets of each side are the tails themselves
subtracted from it, and the front's waste is the corner without the tails, so the boards fit exactly with
no gap and no overlap (an assertion checks it at every point). A finger joint is the same construction
with slope 0: the height is split into 2 × fingers + 1 equal parts, the front and the back owning both
ends. The bottom (thickness / 2, 4 to 8 mm) slides into a groove half the board deep, max(6.3 mm,
thickness / 2 + 0.3 mm) above the lower edge, in all four boards, stopped half a groove depth into the
corners; with the groove off it sits under the boards. The inside height is measured from the top of the
bottom. The knob (radius 11 % of the height, 7 to 14 mm) has a rounded rim.

**Exporting.** STEP, STL or 3MF for CAD and a CNC (one body per board). The named face set **Marking
templates** holds the outside face of the front (its tails) and of the left side (its sockets): File ›
Export…, SVG or DXF with *Sheet of set: Marking templates*, printed at 100 %, gives templates to glue on
the boards and saw to. The back is the front's mirror image, the right side the left's.

**Checked.** `check-range --deep` passes at the default, all 512 corners (`--max-corners 512`), every
choice and random points (seeds 1, 7 and 11 with 64 samples each); regeneration median about 30 to 70 ms,
at most about 260 ms.

**Notes.** The groove sits 0.3 mm off a round number on purpose: at 6 mm it met the lower corner of a
tail exactly for one combination (8 mm boards, two tails, 40 mm inside), where the kernel rightly refuses
a front of zero thickness along an edge.

**Sources.** Dovetail slopes of 1:6 for softwood and 1:8 for hardwood, through dovetails with half pins
at the edges and tails on the drawer sides or front: common woodworking practice, for example
[Wikipedia, Dovetail joint](https://en.wikipedia.org/wiki/Dovetail_joint) and
[Wikipedia, Finger joint](https://en.wikipedia.org/wiki/Finger_joint).

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
