# Form test

The top drawer of my workshop cabinet has a Gridfinity baseplate in it. I keep small drill bits in there and I want a
new bin for them: three grid cells wide, one cell front to back, and four height units tall, so it still clears the
drawer above. Inside I want six little compartments next to each other, one for each size of bit, with a rounded front
so I can slide a bit out with a fingertip. No labels; I can see what is in there. I only have a few magnets left, so
they should go in the four corners of the bin and nowhere else. It has to stack on my other bins. I want the file to send to
my slicer, printed in PETG. How many magnets do I need, how much filament will it take, and how wide is each
compartment? Then I also tried to get eight compartments side by side in a bin only one cell wide: what happens?

## Acceptance

- The bin is 3 units wide, 1 deep, 4 high: 125.5 mm wide, 41.5 mm deep, 28 mm from the feet to the top of the walls, with
  the stacking lip on top.
- Six compartments side by side in one row, all the same width (19.5 mm wide and 39.1 mm deep at the default 1.2 mm wall),
  each with a scoop at the front and no label tab.
- Magnet holes at the four corners of the bin only: the form says 4 magnets.
- The form states the plastic it takes as if printed solid: about 65 g, about 21 m of 1.75 mm filament. All assertions
  pass.
- The export is one 3MF holding the body `Bin` only, in the print orientation (standing on its feet), and without the two
  fit check bodies.
- Refusal: eight compartments side by side in a bin one cell wide cannot be set: the form limits it to three (each
  compartment at least 12 mm wide), or `param.set` refuses with that range.
