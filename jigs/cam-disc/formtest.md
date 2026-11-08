# Form test: cam-disc

"I am building a small cartoning machine. A pusher has to move 30 mm forward while the camshaft turns 100 degrees, stay
there for the next 40 degrees and come back during 110 degrees; for the rest of the turn it waits. The camshaft runs
at 150 revolutions per minute and is 30 mm with a parallel key. It must run as smoothly as the form can give me: I do not want a
step in acceleration at the start or end of a movement. I have a box of 26 mm stud-type track rollers and a normal plain guide
for the follower, so I keep to the usual pressure angle limit for that. What is the smallest cam that still works?
How fast does the follower go? I need a file for the wire EDM and a 3D file of the cam."

## Acceptance

- The motion law is the cycloidal one (the form's description calls it the smoothest and says simple harmonic steps in
  acceleration at the dwell ends; the output for that step reads 0).
- The form will not take a base circle radius under about 33.6 mm for this motion. At 34 mm, the next round value:
  peak pressure angle about 29.6 degrees (limit 30), smallest radius of curvature of the roller path about 41.4 mm,
  3.2 times the roller radius; cam outside diameter 128 mm.
- Peak follower velocity 0.54 m/s; peak acceleration 15.3 m/s² (about 1.56 g); dwell on the base circle 110 degrees.
- All assertions that apply pass.
- The sketch *Cam profile* exports as one DXF holding one closed spline at true size, and the cam exports as STEP.
- Refusal: the same 30 mm of lift in 30 degrees of rise and 30 degrees of return cannot be had with a cam this small: the
  form refuses any base circle under about 171 mm, and the output gives that radius. Above about 44.5 mm of lift in
  those angles the form refuses the lift itself.
