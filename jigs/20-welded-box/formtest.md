# Form test: welded-box

"I need a welded steel box as the base of a small machine, 1000 mm wide, 600 mm deep and 200 mm high, from 4 mm plate. I
want round openings in the top and bottom plates to reach inside, the front and back closed, and triangular openings
in the left and right ends. Inside I want a grid of ribs that slide into each other, with two ribs along the long side. Short
welds: tabs of about 30 mm, about 120 mm apart. My laser shop can cut size on size, with no clearance at all, and I want the
tab ends about 2 mm under the surface so I can fill them with weld. How heavy is it, how much weld is there, what plates do I
order, and what can it carry? I need files for the laser for each plate and a 3D file. And a second one, 2 m long and 100
by 100 mm in section, in 3 mm plate, no openings and no ribs: how stiff is that?"

## Acceptance

- First box: 1000 x 600 x 200 mm, 4 mm plate, tab length 30 mm, pitch 120 mm, clearance 0, recess 2 mm, circles in the top and bottom
  (6 per plate), none in the front and back, triangles in the left and right (4 per plate), 2 ribs in the first family and 1 in the
  second. Mass about 65.1 kg, 72 welds, 2160 mm of weld, weld share of the edges about 22 %.
- The form gives no strength or load figure, and its description says so and says who must verify a machine frame: the answer to
  "what can it carry" is that the Jig does not tell.
- Second box: 2000 x 100 x 100 mm, 3 mm plate, no openings, no ribs. EI about 3.84e11 N mm² both ways; GJ about 2.2e11 N mm², stated as
  an upper bound; mass about 18.6 kg.
- All assertions that apply pass.
- First box: the DXF of *Cut: top and bottom* holds 14 closed paths at true size, 1000 x 600 mm: the outline, 6 circles and 7 rib
  slots. *Cut: ribs, first family* holds one closed outline, 596 x 196 mm over the tabs. The STEP file holds the whole box.
- Refusal: a plate of 2 mm is refused (the form starts at 3 mm); a tab recess of 0 is refused (the minimum is above zero); a 12 mm plate
  on a box of 100 mm is refused.
