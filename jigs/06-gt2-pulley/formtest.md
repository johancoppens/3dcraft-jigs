# Form test: gt2-pulley

"I am building a belt-driven camera slider and want to 3D print the drive pulley myself. The motor has an 8 mm shaft with
a flat on it, the belt is ordinary 6 mm GT2, and I want 40 teeth so one motor turn moves the carriage a good distance.
The pulley needs a flange on each side so the belt stays on, and a hub held by two M3 grub screws. Tell me the pitch
diameter and how far the belt moves per turn, and give me the file to print. While you are at it, could I have used 20
teeth on a 12 mm shaft?"

## Acceptance

- 40 teeth, 6 mm belt, 3D printed PETG, 8 mm D-shaft bore (modelled 8.2 mm with the printing allowance), flanges on
  both sides, hub with 2 × M3 grub screws at 90 degrees.
- The form reports a pitch diameter of 25.46 mm, an outside diameter of 24.96 mm, a belt travel of 80 mm per turn,
  a toothed face of 7 mm and a hub of 19.5 mm; overall length 21.6 mm at a 10 mm hub, mass about 9.4 g.
- All assertions pass, among them the flange height, the first-layer chamfer and the no-overhang check.
- The exported 3MF or STL holds one closed body lying on z = 0 in its print orientation: the flange farthest from
  the hub on the bed, the hub on top.
- Refusal: 20 teeth on a 12 mm shaft cannot be set (the largest shaft for a printed 20-tooth pulley is about 8 mm, and
  `param.set` refuses more, naming that range).
