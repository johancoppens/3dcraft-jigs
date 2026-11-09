# Form test: rc-wing

"I am building a sport model with a strip-built balsa wing. The span is one and a half metres, the chord where it meets
the fuselage is 230 mm and at the tip 150 mm. A bit of sweep on the leading edge, 4 degrees, and 2.5 degrees of washout
so the tip stalls last. The section is a NACA 2412, ten ribs in each half cut from 3 mm balsa, spars 5 by 5 mm top and
bottom. The finished model will weigh about 1.5 kilos. I would like to see the structure, so show me a panel covered in
film and one bare. What is the wing's area, its aspect ratio, how long and where is the mean aerodynamic chord, what
will it load to in grams per square decimetre, and how fast will it stall? And I need the ribs as a file for my laser."

## Acceptance

- Wing area 28.5 dm², aspect ratio 7.89, mean aerodynamic chord 192.8 mm, about 349 mm from the root, its leading edge
  about 24.4 mm behind the root leading edge.
- Wing loading 52.6 g/dm²; stall speed 9.2 m/s (33.0 km/h) at the Jig's stated CLmax of 1.0 and sea-level density;
  Reynolds number at the MAC about 121 000.
- Rib spacing 83 mm; washout packing about 4.6 mm at the tip trailing edge; the leading edge stock is 752 mm per panel
  and the trailing edge stock 751 mm.
- All 23 assertions pass; the model shows film on one panel and the bare frame on the other.
- The set "Cut sheet", exported as SVG or DXF with a 600 mm sheet width, holds 20 ribs (ten per panel), each with its two
  spar slots open at the edge, the inner two ribs of each panel with deeper slots for the joiners; the largest rib is
  202.8 mm between its front and rear cuts (root chord less the leading and trailing edge stock). The sheet carries no
  rib numbers (see README). The sketch "Joiner flat pattern" exports the two V-shaped joiners as one DXF of two outlines.
- Refusal: a NACA 2408 at this root chord: the thickness digits are refused (the form shows 10 as the thinnest it accepts,
  for these spars and joiners). The same wing with a 110 mm tip is refused too: the tip chord is limited to about 118 mm,
  the smallest that keeps a 4 mm web between the spar slots.
