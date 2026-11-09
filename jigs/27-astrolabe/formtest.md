# Form test: astrolabe

"I run a small brass workshop in Lund, in the south of Sweden, about 56 degrees north, and I have been asked to make a teaching
astrolabe for a school. It should be about 220 mm across, cut from 2 mm brass sheet on our fibre laser, whose cut is about 0.1 mm
wide. The children will learn the altitude lines first, so I want them close together, every 5 degrees, and as many bright stars on
the rete as you can give me, marked so that they can find each star by name. They will measure the altitude of a star with the
sighting bar on the back, and the teacher will show the sky at about 7 hours sidereal time. I need one file with all the outlines for
the cutting, and files for engraving the plate, the limb, the back and the star marks. Can you also tell me what the whole thing weighs
in brass, and how close together the closest engraved lines come? And could the same instrument be made for our partner school in
Singapore?"

## Acceptance

The job asks for latitude 56 degrees north, diameter 220 mm, sheet 2 mm, kerf 0.1 mm, altitude step every 5 degrees, 36 stars with
their letters, sidereal time 7 hours; for the plate's engraving file the form must be set to prepare the engraving export.

- The form accepts all of it; every assertion that applies passes in both modes (`document.check` ok).
- Outputs: Capricorn radius 85.55 mm, equator 56.15 mm, Tropic of Cancer 36.86 mm, horizon north point 29.86 mm below the pole,
  smallest gap between engraved lines 1.95 mm, mass of the instrument about 1.74 kg.
- *Sheet of set: Laser cut sheet*: one DXF of eight parts side by side, about 1127 by 248 mm: plate 176.4 mm round, limb with
  throne 220 by 247.5 mm, rete 173.7 mm round, back plate 220 mm round, alidade, two sight vanes and rule.
- *Sheet of set: Limb engraving* and *Back engraving*: one region each, 202.7 and 192.3 mm round; *Plate engraving* (after
  preparing the engraving export): one region 171.1 mm round.
- The star key (letter to star name) is in the description of the number of stars; the letters are stamped, not exported, and
  the tester says so.
- Refusal: Singapore, about 1.3 degrees north, cannot be set: the latitude stops at 25 degrees north, and the form says the
  instrument is not for the tropics nor the southern hemisphere. A sheet of 3 mm is refused at 220 mm (the most is 2 mm).
