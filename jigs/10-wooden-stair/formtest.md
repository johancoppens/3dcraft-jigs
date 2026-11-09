# Form test

I am renovating a house in the Netherlands and want a new straight wooden stair. From the finished lower floor to the
finished upper floor it is 2 760 mm. Measured on the floor from the edge of the upper floor at the top of the stairs back
to the door at the foot, I have 3 300 mm. The stair must be 900 mm wide, wall to wall. The upper floor is 250 mm thick
with its ceiling, and the opening in it, measured from that same edge back, is 3 200 mm long. I want closed risers,
45 mm oak treads, and a balustrade on the open side with newel posts and a rail along the wall on the other side. Our
router has a 12 mm bit. How many steps do I get, how high and deep are they, what boards do I need for the stringers, and
what do I send to the CNC?

## Acceptance

- 15 risers and 14 treads; rise 184.0 mm, going 223.6 mm, 2 x rise + going = 591.6 mm (within 570 to 630); pitch 39.5
  degrees; the stair takes 3 300 mm of floor, measured on the model, exactly the run available; all assertions that apply
  pass (28 of 29, the 29th is the Flemish rule's and is inactive).
- Rule: new dwelling (Bbl): rise at most 188 mm, going at least 220 mm, width at least 800 mm. The form's outputs show
  orientation figures only and say a structural engineer must verify the strength.
- Stringer boards 314 mm wide, at least 4 472 mm long, 40 mm thick. Treads 842 mm long (with both housings) and 253.6 mm
  deep (going plus nosing). Stair timber about 161 kg.
- Head height at the edge of the opening: 2 300 mm (no floor hangs over the stair at this opening). The smallest opening
  that keeps the head height is 3 148 mm: the form says so.
- Export: the sketch *CNC stringer layout* as DXF lies along x and holds the stringer outline with 14 tread housings
  and 15 riser housings (the top and bottom ones open-ended); the set *CNC tread sections* gives the true section of a
  tread, 253.6 mm by 45 mm with its bullnose and groove; a STEP of the stringers and treads is written.
- Refusals: a run of 3 100 mm cannot be set (minimum 3 250 mm here); an opening of 3 000 mm is refused (minimum 3 148
  mm); a width of 750 mm is refused (minimum 800 mm); a 40 mm tread is refused (minimum 41.6 mm here); under the Flemish
  rule a floor height above 3 240 mm, a width below 1 250 mm, a balustrade or a rail on one side only cannot be set.
