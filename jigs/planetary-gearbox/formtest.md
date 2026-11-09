# Form test

I want to slow down a NEMA 17 stepper by about five times for a little turntable, and I can spare a round space of
100 mm across. I print in PETG with a 0.4 mm nozzle on an Ender-3, so I want teeth that print cleanly but not huge, and I
would like four planets. I have to be able to set how loose the gears run. Show me that it really turns, tell me what to
buy and how much torque I can expect at most, and give me the files to print.

## Acceptance

- The reduction comes out at 5.00 : 1, with a sun of 16 teeth, four planets of 24 and a ring of 64 teeth, module 1.25,
  in a housing of 100 mm on a NEMA 17 mount.
- The form shows a gap of 3.07 mm between neighbouring planets, contact ratios of about 1.5 (sun and planet) and about 2.0
  (planet and ring), and a small positive profile shift on the sun (0.08).
- To buy: the planet bearing is a 608 (8 mm bore, 22 mm outside), four of them, on 8 mm dowel pins of 26 mm; two output
  bearings of 20 mm bore and 32 mm outside (61804); M3 cover screws between 48.5 and 50 mm long (an M3 × 50) into
  heat-set inserts.
- The reducer is 58.2 mm tall above the motor face, and the longest motor shaft that fits is 51.2 mm.
- The output torque is at most 4.8 times the motor's torque (the form says so, and that the strength of printed teeth is
  not proven).
- Turning the input through 360 degrees turns the output by 72 degrees the same way (360 / 5). All assertions that apply
  pass, in the cutaway, the closed view and on every print plate.
- Six print plates, each exporting as a 3MF of only its parts and each within 220 × 220 mm: motor plate; ring gear; cover;
  the two carrier plates; output hub and flange; sun and four planets.
- Refusal: a reduction of 6 in the 100 mm space cannot be set (the housing would have to be at least 109 mm), nor 5
  planets (4 is the most that fit), nor a housing of 90 mm (at least 98 mm for 5 : 1) or of 170 mm (160 mm at most).
