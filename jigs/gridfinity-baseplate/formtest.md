# Form test

I just bought a Bambu A1 mini, and the first thing I want to print is Gridfinity for the top drawer of my workbench. The
inside of the drawer is 322 mm wide and 460 mm from front to back. I want bins with magnets to stay put, so the plate
needs holes for them, but I am not screwing anything into the drawer. I would rather not waste plastic, and I want the
pieces to stay together when I pull the drawer out hard. What do I have to print, and how big is the biggest piece?

## Acceptance

- The plate holds 7 cells across the width and 10 from front to back, 70 in all, with a filler strip of 13.75 mm left
  and right and 19.75 mm front and back. It is 8.35 mm high.
- Light style with magnet holes in every cell and bowtie clips between the pieces; no screw holes.
- The plate is cut into 3 by 3 = 9 pieces; the largest is 126 mm wide (with 97.75 mm at the ends) and 168 mm deep (with
  145.75 mm at the ends), so every piece fits the 180 mm bed. 34 clips have to be printed.
- The 3MF export, with the drawer and sample bin switched off, holds the 9 pieces and one object `Clips to print`, and
  nothing else (10 objects). The 34 clips lie in rows that fit the 180 mm bed.
- All the assertions pass.
- Refusal: a screw hole in this style is not available (the form keeps it off, `param.set` refuses it), and a bed
  smaller than 180 mm is refused.
