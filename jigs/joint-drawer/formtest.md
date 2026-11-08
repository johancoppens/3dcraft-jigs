# Form test

I am building a drawer for an oak sideboard. The hole in the carcase is 600 mm wide, 165 mm high and 450 mm deep, and I
would like about a millimetre of play at each side and 3 mm above it. I have oak planed to 22 mm for the front and 12 mm
for the sides and back, all oak. I want the front to stay clean, with the joint hidden on the face, and I would rather
have a brass knob than a wooden one. What do I saw, how many tails is it, and what will the boards weigh? A friend says
I can get away with 1 mm above the drawer: can I?

## Acceptance

- The drawer is 598 mm wide, 162 mm high at the sides and 440 mm deep outside, and fills the hole with the clearances asked.
- The front joint is half-blind dovetails, the back through dovetails. Four tails at the front and four at the back, at a
  slope of 1 in 8. Every assertion passes.
- Saw list from the outputs: front 598 x 162 mm, two sides 433.65 x 162 mm, back 598 x 142 mm, bottom 584 x 422.5 mm, 6 mm thick.
  The boards weigh about 4.5 kg.
- With 3 mm above it the top gap is enough: the boards swell by about 2.4 mm across the grain in a season.
- A brass knob is shown, two of them as the drawer is wider than 450 mm.
- The marking templates export (SVG or DXF, the set *Marking templates*): a side with its tails, the front's and the
  back's pins, and the bottom, at true size.
- Refusal: 1 mm above the drawer cannot be set; the top clearance stops at 2.5 mm for this oak and this height (the form
  clamps to it, or `param.set` refuses it with that range).
