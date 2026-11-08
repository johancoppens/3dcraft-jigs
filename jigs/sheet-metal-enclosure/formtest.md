# Form test

I have a controller board, 200 mm wide and 160 mm front to back, with its four mounting holes 5 mm in from the corners.
The tallest part on it, a heat sink, stands 35 mm above the board, and I want it on 10 mm standoffs with at least 8 mm of
room all round. I would like an aluminium case in 2 mm sheet, with four 16 mm round connectors in the front panel and
slots in the top only for the air. What will the sheets be, how much does it weigh, and can I have the flat patterns for
the laser and the press brake? And if I stacked three of those boards in the same case, could the press brake still fold it?

## Acceptance

- The form reports an outside of 221 × 180 mm, 65.7 mm high with feet and screw heads, and about 0.64 kg for the two
  sheet parts.
- Bending: inner radius 2 mm, bend allowance about 4.25 mm per bend, a 12 mm V-die.
- The blanks: chassis 216 × 331.43 mm, cover 326.7 × 180 mm. 40 vent slots are cut, all in the top, in two rows of 20 with a bridge between them.
- Every assertion passes, the press-brake bend check among them.
- The exported flat patterns (DXF or SVG, **Flat patterns of every part**, nothing to pick) hold two outlines, 20 round
  holes (four in the floor, six clinch-nut holes, four connector holes, six cover screw holes), 40 slots, four bend
  lines up and two bend lines down.
- Refusal: three such boards are refused at 35 mm. With three boards in this case the tallest part stops at about 21 mm,
  because the press brake could no longer bend the second wall.
