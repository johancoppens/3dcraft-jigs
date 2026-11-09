# Form test

My CNC router has 1000 mm of travel on the gantry. Through the drag chain go three motor cables of 7 mm, and two sensor cables
of 4 mm. The motor cable's data sheet says it may flex down to a 70 mm radius. The bracket on the gantry where the chain ends
is 270 mm above the rail where the other end is bolted. I print in PETG on a well-tuned printer, and I want to be able to open
the chain to lay the cables in. Show me that it rolls along the whole travel, tell me how many parts to print and where to bolt
it, and give me the files for the printer. I may later want to fit the same chain to a machine with 1300 mm of travel.

## Acceptance

- An inner space of 35 by 9 mm (width by height), links 14.2 mm high and about 49 mm wide outside with the lid clips.
- A pitch of about 33.7 mm, a bend radius of about 129 mm at the hinges with 12 links in the bend (15 degrees per link). With
  the joints' play taken up the tightest local radius is about 104 mm, and the thickest cable's centre there about 103 mm, outside
  the 70 mm the cable asks for. No separator in the links.
- 29 links and 29 lids to print, and one fixed and one moving end piece. The chain is about 976.6 mm long, against the rule's
  972.6 mm (half the travel plus the bend).
- The fixed end goes at the middle of the travel, 500 mm from its start, its two screw holes centred about 464 mm from the
  start, 30.8 mm apart, M4 (4.5 mm). The bend needs about 170 mm past the end of the travel. About 170 g of filament.
- The form says the chain carries itself over a span of about 565 mm, so at most about 1060 mm of travel, and the upper run
  sags about 60 mm at this travel.
- Dragging the carriage from one end of the travel to the other moves the moving end from 0 to 1000 mm and the bend along at
  half that speed, with at least one link flat on each run. All assertions that apply pass.
- A plain 3MF export of the print view, with nothing picked, holds exactly four objects, each on the bed at z = 0: *Link*, *Lid*,
  *Fixed end* and *Moving end*.
- The form says which side the lids open on: the inside of the bend, so upward on the lower run and downward on the upper run.
- In the print view no output reads as an error.
- Refusals: a moving end 140 mm above the rail cannot be set for these cables (the form's lower limit is 185 mm); 1300 mm of
  travel cannot be set for this chain (the form's upper limit is 1060 mm).
