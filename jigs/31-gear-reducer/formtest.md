# Form test

We are building a mixer for our workshop. It is driven by a 7.5 kW six-pole electric motor that runs at 960 rpm, and
the mixer shaft must turn at about 48 rpm. A mixer gives the gears a fair amount of shock. I want a two-stage spur gear
reducer in a cast iron housing that a foundry casts by hand, with gears of a quenched and tempered alloy steel. Tell me
what it comes out at, which bearings to buy, how long they last, how much oil it takes and what it weighs, and give me
one file for the pattern maker and one for the machine shop.

## Acceptance

- Ratio asked about 20 (960 / 48); the ratio built is 20.11 with 19 / 110 and 19 / 66 teeth, an output of 47.7 rpm and
  1500 N·m nominal at the output.
- Driven machine "Moderate shocks" (KA 1.5), steel 42CrMo4, wall 10 mm (hand moulding).
- Modules 3 mm and 6 mm, centre distances 193.5 mm and 255 mm, face widths 36 mm and 72 mm; Lewis bending stresses
  about 171 and 107 MPa against an allowed 216.7 MPa; contact ratios about 1.70 and 1.67.
- Bearings: two each of 6209, 6212 and 6214; shortest bearing life about 29 860 h (at least 20 000 h); shaft ends
  40 mm (input) and 65 mm (output).
- About 13 litres of oil, and, in the Closed view, a mass of about 255 kg.
- All assertions that apply pass, in every view.
- Exports: with Show at "Castings: both halves", a STEP holding exactly the two housing halves; with Show at "Machined
  parts", a STEP holding the three shafts (two with their pinions cut on), the two wheels, the two spacers and the three
  pairs of end covers, and no housing, bearing or key.
- Refusal: the same reducer for a 30 kW motor cannot be set (the power at these settings ends at 22.6 kW); a ratio of 30
  cannot be set (the form ends at 25).
