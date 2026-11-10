# Form test: Geared orrery

## The job

I make clocks as a hobby and want to build a brass orrery for my study, to stand on a shelf that is 60 cm deep, so the
planets must stay inside a 60 cm circle. It should show the planets out to Jupiter and the Moon going round the Earth.
I want the gearing good to one part in a thousand or better. I will finish it this year, 2026, and set it then. I will
send the brass to a laser cutting service that takes care of the kerf itself. For a photograph I want it turned back to
my son's birthday, 14 March 2019, at noon.

Give me the file to send to the cutting service, and tell me how many gears they will cut, how long the longest arm rod
is before I bend it, and how far the furthest-off planet will stand from where it really was on average on that
birthday, after the gears have drifted.

Then: my brother wants the same with all the planets out to Saturn and the Moon, geared to one part in five thousand.
Can it be done?

## Acceptance

Values from the model at 3DCraft 150f0015 (worked out with `param.set` and the outputs).

- **The form:** planets Mercury to Jupiter, Moon on, year 2019, day of the year 73 (14 March), arms set in 2026, laser
  kerf 0, largest period error 0.10 % or less (any value the form allows down to its least, 0.03 %), span of the orbits
  600 mm or less (with medium beads the form allows 340 to 630 mm here).
- **Gears:** 29 (four for each of the five planets' trains and the Moon's, and the Moon's five on the carrier), whatever
  the error chosen; at 0.10 % the largest period error of the trains is 0.0369 %.
- **The file:** `cut.export` with the form's kerf (0) holds 38 parts of 1 mm brass, each once: the 29 gears, the bridge,
  the crank, the two plates of the Earth's carrier, the Moon train's four washers and the degree ring; no Saturn ring, no
  rods or tubes. (Or `file.export` of the set *Laser cut sheet*, the same 38 outlines.)
- **Longest arm rod:** Jupiter's, 334.1 mm of 5/32 in rod to cut at a span of 600 mm with medium beads (6 mm into the
  bead included; the output, shorter at a smaller span), within one 36 in rod.
- **Furthest-off planet on the birthday:** the output *furthest any bead stands from its body's real mean longitude*:
  12.1 degrees at 0.10 % (the Moon, 6.8 years of drift back from 2026); another error gives other trains and another
  value. Jupiter's own drift is 0.30 degrees a century. The outputs *Set ...* say where each arm goes on 1 January 2026
  (Jupiter's at 103.5 degrees on the degree ring).
- **Every assertion passes** at the tester's settings.
- **Refused:** all the planets to Saturn and the Moon at one part in five thousand (0.02 %): the form's least for that
  choice is 0.06 % (`param.set` refuses 0.02 and names the range 0.06 to 0.15).
