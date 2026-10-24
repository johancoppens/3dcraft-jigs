# Pillow block bearing housing

A pillow block (plummer block) for a deep-groove ball bearing chosen from a table of real sizes, with
slotted or round mounting holes and an optional grease nipple. The housing follows the bearing. Licence:
CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Bearing | Bearing | 6202 (15 × 35 × 11) | 13 bearings from the table `bearings` (below) |
| Seat allowance | Bearing | 0 mm | 0 to 0.3 mm, step 0.01 mm |
| Centre height | Housing | 40 mm | max(R, D / 2 + base) + 1 mm to + 40 mm, step 0.5 mm |
| Slots | Mounting | on | on / off (round holes) |
| Slot length | Mounting | 8 mm | 4 to 20 mm, step 1 mm |
| Grease nipple | Mounting | on | on / off |

**Bearings** (table `bearings`; bore d × outside diameter D × width B in mm, ISO 15):

| Series 60.. and 608 | | Series 62.. | |
|---|---|---|---|
| 608 | 8 × 22 × 7 | 6200 | 10 × 30 × 9 |
| 6000 | 10 × 26 × 8 | 6201 | 12 × 32 × 10 |
| 6001 | 12 × 28 × 8 | 6202 | 15 × 35 × 11 |
| 6002 | 15 × 32 × 9 | 6203 | 17 × 40 × 12 |
| 6003 | 17 × 35 × 10 | 6204 | 20 × 47 × 14 |
| 6004 | 20 × 42 × 12 | 6205 | 25 × 52 × 15 |
| 6005 | 25 × 47 × 12 | | |

The table's keys carry the size ("6202  15x35x11"), so a key is never mistaken for a row number:
`param.set {"values": {"bearing": "6202  15x35x11"}}` (or the row number, 10).

**How it is built.** The shaft axis is the y axis. One profile (base, a pedestal with flared fillets and the
top half of the ring) is extruded the housing's width; the base's plan corners are rounded. Everything
follows the bearing's D and B:

```text
ring wall   = clamp(0.2 D, 3 mm, 8 mm)          R = D / 2 + wall
base        = clamp(0.3 D, 5 mm, 12 mm) thick   pedestal fillets clamp(0.12 D, 2 mm, 5 mm)
bolts       = M4 (D <= 26 mm), M5 (<= 35), M6 (<= 47), else M8; ISO 273 medium clearance holes
width       = max(B + max(2 mm, 0.25 B), bolt head + 6 mm)
seat        = D + allowance, B deep from the front; 0.5 mm lead-in chamfer
shoulder    = bore of D - max(2 mm, 0.08 D) through the back: it bears on the outer ring only
```

The bolt centres sit just clear of the pedestal fillets and the bolt heads (ISO 4762), the slots running
outward. The grease option adds a boss on top of the ring over the middle of the seat, a 2.5 mm
lubrication hole down into the seat, and a straight grease nipple in brass (DIN 71412 form A: a 7 mm hex,
a neck and a ball head; its sizes are approximate). Use it with an open or shielded bearing: a sealed
(2RS) bearing is greased for life.

The bearing is a separate body (rings in steel, the 2RS seals in blue) sitting in its seat, and so is the
nipple: export only the housing with `file.export {"bodies": ["Housing"]}`, or all of them as STEP.

**Checked.**
- Assertions at every regeneration: the bearing does not overlap the housing (it touches the seat and the
  shoulder); the number of bodies.
- `check-range --deep` passes 141 of 141 points (all 64 corners, every bearing, 64 random).

**Sources.**
- ISO 15:2017, *Rolling bearings: radial bearings, boundary dimensions*: d, D and B of the 60, 62 series
  and the 608 (as in the SKF and NSK catalogues).
- ISO 273, *Clearance holes for bolts and screws* (medium series: 4.5, 5.5, 6.6, 9 mm); ISO 4762, *socket
  head cap screws* (head diameters 7, 8.5, 10, 13 mm).
- DIN 71412, *Lubricating nipples* (form A, the shape; sizes here approximate).
- The housing's proportions (wall, base, fillets, shoulder) are this Jig's own rules of thumb, not a
  standard: a cast plummer block (ISO 113) is heavier.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
