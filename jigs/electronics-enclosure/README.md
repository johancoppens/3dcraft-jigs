# Electronics enclosure

A 3D-printed box for a circuit board, with standoffs under its mounting holes, two port cut-outs and a lid
that screws on or snaps in. Box and lid come out side by side, the lid upside down, ready to print without
supports. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| PCB width | PCB | 70 mm | 30 to 160 mm, step 0.5 mm |
| PCB depth | PCB | 50 mm | 30 to 120 mm, step 0.5 mm |
| PCB thickness | PCB | 1.6 mm | 0.8 to 2.4 mm, step 0.1 mm |
| Holes from side | PCB | 3.5 mm | 3 mm to PCB width / 2 − 5 mm |
| Holes from front | PCB | 3.5 mm | 3 mm to PCB depth / 2 − 5 mm |
| Screws | PCB | M3 | M2, M2.5, M3, M3 heat-set insert |
| Standoff height | PCB | 5 mm | 3 to 15 mm, step 0.5 mm |
| Room above PCB | Box | 20 mm | 15 to 60 mm, step 0.5 mm |
| Wall | Box | 2 mm | 1.6 to 3 mm, step 0.1 mm |
| Clearance | Box | 1 mm | 1 to 5 mm, step 0.1 mm |
| Lid | Box | Screws | Screws, Snap fit |
| Port 1 / Port 2 | Ports | USB-C / DC jack | none, USB-C, micro-USB, DC jack 5.5 mm, Toggle switch (6 mm), Slide switch |
| Port 1 side / Port 2 side | Ports | Front / Back | Front, Back, Left, Right |
| Port 1 offset / Port 2 offset | Ports | 0 mm / 8 mm | along the wall, clear of the corners (the range follows the wall and the port) |

**How it is built.**
- The box is a rounded block (outer corner radius wall + 2 mm) made hollow with `feature.shell`, open at
  the top, its bottom edge chamfered 0.6 mm. Inside it is the board plus the clearance on every side.
- Four standoffs (the screw's boss diameter) stand under the board's holes, which form a rectangle given by
  their distance from the board's edges; each has a pilot hole for a self-tapping screw (or the hole for a
  heat-set insert), stopping 0.5 mm above the floor.
- **Screw lid:** a post in every corner, 0.2 mm under the rim so the lid pulls tight, with a pilot hole
  12 mm deep; the box is made wider by the posts' room so they stand beside the board, not over it. The
  lid is a plate as large as the box (thickness = wall, top edge chamfered) with counterbored clearance
  holes over the posts.
- **Snap-fit lid:** a 1.6 mm skirt, 4 mm deep, that fits inside the box with 0.2 mm play, with a 0.6 mm bead
  along its front and back that clicks into a 0.75 mm groove inside the walls.
- **Ports:** each port is a rounded slot (a block with its four edges filleted) or a round hole, taken from
  the table below, placed on the wall's mid-plane at the port's height above the top of the board, and cut
  through the wall. Its offset is from the middle of the wall, to the right as seen from outside; its range
  keeps it clear of the corners.

| Port | Opening (w × h) | Corner radius | Centre above PCB top |
|---|---|---|---|
| USB-C | 9.6 × 3.8 mm | 1.5 mm | 1.65 mm |
| micro-USB | 8.2 × 3.4 mm | 1.0 mm | 1.5 mm |
| DC jack 5.5 mm | Ø 8 mm | | 6.5 mm |
| Toggle switch (6 mm) | Ø 6.4 mm | | 7 mm |
| Slide switch | 9 × 4.5 mm | 0.8 mm | 2 mm |

| Screw | Pilot | Clearance | Head | Boss |
|---|---|---|---|---|
| M2 | 1.6 mm | 2.4 mm | 4 mm | 4.5 mm |
| M2.5 | 2.1 mm | 2.9 mm | 5 mm | 5.5 mm |
| M3 | 2.5 mm | 3.4 mm | 6 mm | 6.5 mm |
| M3 heat-set insert | 4.0 mm | 3.4 mm | 6 mm | 7.5 mm |

The openings are about 0.3 mm larger than common receptacles and assume a connector whose front lies at the
board's edge; the heights are for parts mounted on the top of the board. Check them against your parts' data
sheets: the tables are in `gen.py` (and `build.json`), easy to extend.

**3DCraft features used.** Two tables (`table.set`) with choice parameters taken from them, `choose()` and
`if()` for the port's place on any of the four walls, parameter ranges that are formulas of other
parameters (the holes' positions, the port offsets), `feature.when` for the lid type and the port shapes,
`feature.shell`, chained chamfers, fillets on a block, patterns, a transform that lays the lid upside down
beside the box, `body.appearance` (box slate blue, lid ochre), an assertion (two bodies).

**Checked.** `check-range --deep` passes at the default, 64 corners, every choice and random points (101
points with seed 1, 149 with seed 7); regeneration median about 120 ms, at most about 560 ms. Also checked:
two identical ports at the same place, and ports overlapping each other. 3MF export: two closed bodies in
their colours.

**Sources.** Connector openings from common receptacle sizes (USB Type-C receptacle about 8.9 × 3.2 mm,
micro-USB B about 7.5 × 2.5 mm, 5.5 × 2.1 mm DC barrel plug, 6 mm toggle-switch bushing); screw pilot and
clearance holes from common practice for screws in printed plastic (ISO 273 medium clearance for M2 to M3).

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
