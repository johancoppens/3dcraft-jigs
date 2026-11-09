# Form test

My niece turns seven next month, and I would like to make her a little hand-cranked music box that plays Ode to Joy,
with a drum about 65 mm across. I have a printer that does PETG well, and there is a laser shop nearby that can cut me a
comb from thin spring steel, so a real metal comb is what I want. It should play at a calm, normal pace, and five turns of
the crank for the whole tune sounds about right to me. What do I print, what do I send to the laser shop, how long does
the tune last, and how fast do I turn the handle?

## Acceptance

- Ode to Joy on a 65 mm drum: 38 pins, the tune takes 64 beats of the drum and lasts 20 s at 96 quarter notes a minute
  (0.3125 s per beat), with five turns of the crank for the whole tune, about 15 turns a minute.
- A two-octave comb of 15 teeth, C4 to C6 (262 to 1047 Hz), in spring steel 0.5 mm: the longest tooth is about 39.9 mm,
  the shortest about 19.9 mm, and the drum gear has 60 teeth on the 12-tooth pinion.
- The print layout exports as a 3MF with the case, the drum, the pinion, the crank arm, the comb clamp and the pawl,
  each on the bed. The comb exports as a DXF (or SVG) of the flat comb with its slots and three screw holes.
- Dragging the crank slider through its whole range turns the drum exactly once; the form says the crank turns one way
  only, clockwise facing it, and that a pawl on the drum gear stops a backward turn within one tooth. All assertions
  that apply pass.
- Refusal: Ode to Joy on a 30 mm drum cannot be set (the form's lower limit for this tune is 63 mm at the default pluck:
  two pins on one tooth would be too close together for the tooth to come back). The comb choices include printed combs
  of 1.6 mm, and the comb's description in the form warns that a printed comb only plays the notes for a moment and dies
  away.
