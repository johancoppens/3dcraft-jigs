# Form test

My Year 6 class has spent the term on the Platonic solids, and next week each table will make its own big
dodecahedron out of thick card. The school copier takes A3, our card is 200 g/m², and the edges should be 4 cm so the
finished solids look impressive on the classroom windowsill. I want a pattern I can print and cut out, and I would like
to tell the children how much card they use and how big the finished solid is. I also have a second, younger group who
only have A4 paper: can they make the same 4 cm dodecahedron on A4?

## Acceptance

- Dodecahedron, edge 40 mm, on A3 at 200 g/m². The Jig reports 12 faces worth of pattern: about 330 cm² of
  faces, a pattern about 330 × 169 mm that fits an A3 sheet inside its margins, a finished solid of about 490 cm³ and a
  paper mass of about 7.4 g, with 19 glue tabs.
- Dragged shut at 100 %, the net closes and all nine assertions pass.
- The export is the crease pattern of the dodecahedron's print pattern, as SVG or DXF: a single closed cutting outline
  with the folds of the 11 joints between faces and the 19 tab hinges (30 fold lines in all).
- Refusal: the same 4 cm dodecahedron on A4 cannot be set: on A4 the edge length stops at about 32 mm (the form clamps
  it, or `param.set` refuses with that range).
