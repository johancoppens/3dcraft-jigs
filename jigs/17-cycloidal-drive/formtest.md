# Form test

I am building a small robot arm and the elbow is driven by a NEMA 17 stepper, which is far too fast and too weak on its
own. I want to print a cycloidal reducer for it with about 17 to 1 (it must be a whole number of lobes). It has to fit in
a space of 90 mm across. I would like two discs so it runs smoother. I print in PETG. Show me that it really turns, tell
me what to buy, and give me the files to print.

## Acceptance

- A reducer of 17 to 1 with 18 ring pins and 17 lobes on each of two discs, in a housing 90 mm across, on a NEMA 17 mount.
- The pin circle is 69 mm across, the eccentricity about 1.34 mm at the default lobe depth, and the sharpest lobe radius is
  above 4 mm. The output pins are 8 pieces.
- To buy: dowels of 4 mm, ring pins about 37 mm long (18) and output pins about 23.5 mm long (8); two disc bearings with
  17 mm bore and 26 mm outside (61803); two output bearings of 25 mm bore and 37 mm outside (61805); a support bearing of
  10 mm bore and 19 mm outside (61800).
- The form says the longest motor shaft that fits is about 36.6 mm, so a common 24 mm shaft goes in without cutting.
- Turning the input through 360° moves the output by 21.2° the other way (360 / 17). All assertions that apply pass.
- The print layout exports as a 3MF with seven objects: housing, cover, two discs, eccentric, hub and flange, all on the
  bed.
- Refusal: a 41 to 1 reduction in this housing cannot be set (the form's upper limit is 35); a housing 70 mm across cannot
  be set (the form's lower limit is 78 mm for this motor).
