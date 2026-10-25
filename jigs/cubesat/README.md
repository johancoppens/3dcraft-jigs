# CubeSat

A parametric CubeSat built to the CubeSat Design Specification (CDS) Rev 14.1 and the PC/104 Specification
v2.4: four rails with their separation springs and deployment switches, top and bottom frames, side panels
with windows, the remove-before-flight pin, a PC/104 avionics stack, a battery module and an attitude-control
module (reaction wheels, magnetorquers), body-mounted solar cells and two hinged solar wings, a turnstile
antenna module whose four tape-spring elements are a quarter wave long at the chosen frequency, sun sensors
and an optional Earth-observation camera. Stowed (as in the dispenser) or deployed (in orbit: wings out,
antennas unrolled, springs and switches extended). Origin at the geometric centre, Z along the rails.
Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Form factor | CubeSat | 3U | 1U, 2U, 3U, 6U (table `cds`) |
| Deployed | CubeSat | off | stowed or deployed |
| Wing deploy angle | CubeSat | 90° | 0 to 180°, step 5°; applies when deployed |
| PC/104 boards | Avionics | 1 | 1 to what fits (see below) |
| Antenna frequency (MHz) | Comms | 437 | 100 to 1000, step 1 |
| Camera payload | Payload | on | on or off; 2U and larger |

The opened Jig shows a stowed 3U with the camera and five boards; **Reset all** goes back to the defaults
above.

**What fits.** The stack is laid out from the bottom frame up: the camera (72 mm) when fitted, a 12 mm
base spacer, the PC/104 boards at their 0.600 in pitch, 10 mm, the battery module, 10 mm, the
attitude-control module, and at least 1 mm under the antenna module on the top frame. The largest number
of boards is a formula of the rail length and the camera (`floor((stack_room - cam_fit * cam_h) /
stack_pitch) + 1`), so the form only offers stacks that fit:

| Form factor | Boards without camera | Boards with camera |
|---|---|---|
| 1U | 1 | (no camera: it does not fit) |
| 2U | 9 | 4 |
| 3U | 16 | 11 |
| 6U | 18 | 13 |

**Checked by assertions** (they hold at every point the form allows):
- CDS 2.2.10 mass: the total mass from the bodies' materials is at most the form factor's limit (2, 4, 6 or
  12 kg; table `cds`).
- CDS 2.2.5 rail width at least 8.5 mm; CDS 2.2.1 the rails' envelope is W × H × L of the form factor
  within 0.1 mm.
- CDS 2.2.3 nothing sticks out more than 6.5 mm beyond the rails sideways (stowed).
- CDS 2.2.14.2 nothing lies past the standoffs along Z when stowed (the Z extent is the rail length L).
- PC/104 stack clears the top frame by 1 mm; the boards do not touch the side panels.
- The stowed wing clears the body cells by 0.3 mm.
- The avionics (attitude-control module) clear the antenna module by 1 mm.

**How it was made.** The design was made interactively over MCP in the 3DCraft test drive of
2026-10-25 and is kept as a document, `source.3dcraft` (176 features, the table `cds`, twelve
assertions). `build.json` opens it, sets the document info and exports the Jig. Later changes to the
design are command batches in `edits/`, each applied to `source.3dcraft` with
`craft3d-cli run --script jigs/cubesat/edits/NN-....json` (file.open, the edits, file.save), so every change
is reviewable:

- `01-sun-sensor-window.json`: the window of the +X sun sensor is only built with the sensor (both have the
  sensor's condition). On sizes where the sensor does not fit beside the cells the window was left over as a
  body without a material, so the mass could not be measured.
- `02-stowed-extent.json`: the CDS 2.2.14.2 assertion (nothing past the standoffs) applies when stowed only,
  as its name says and as the 2.2.3 protrusion assertions already did (`if(deployed, 10 m, L)`). Deployed,
  the wings swing past the top of the rails, which the dispenser rule does not govern. Stowed it is
  unchanged: the Z extent must be at most L.
- `03-stack-range.json`, `04-camera-fits.json`: the most boards is a formula of everything above and below
  the stack (it used to count only the rails), and the camera is only fitted where it fits (`cam_fit`): not
  in a 1U. The default of *PC/104 boards* is 1, the one value that fits every form factor with the camera
  on.
- `05-cell-colour.json`: the solar cells in the shared palette's slate blue (#5B7299) instead of a very dark
  blue, so the thumbnail reads.

**Why the camera is not switched off in the form for a 1U, and why the default is one board.** The form
can do both: a boolean's maximum may be a formula (`payload` at most `stack_room >= cam_h`), and the form
clamps the number of boards when the form factor or the camera changes. `check-range` (3DCraft
`document.sample`) does not: it sets a boolean on at its corners whatever its maximum, and it tries every
other form factor with the other parameters at their defaults, without clamping them. Both points are
refused and counted as failures. Until it clamps as the form does, the camera is left out of a 1U by the
model (the box stays ticked) and the default number of boards is 1.

**3DCraft features used.** A table (`cds`) with a choice parameter taken from it, parameter ranges that are
formulas of other variables, `feature.when` for the deployed and stowed parts, the camera and the sun
sensors, `if()`, patterns, mirrors, transforms about a hinge axis, booleans, fillets, a revolved lens,
`body.material` on every body for the mass, `body.appearance`, twelve assertions (mass, extent, clearance,
interference).

**Checked.** `check-range` passes at the default, 64 corners, every choice and random points: 84 points
with seed 1 (also `--deep`) and 164 with 96 samples and seed 7 (`--deep`); regeneration median about 60 ms,
at most about 95 ms.

**Sources.** CubeSat Design Specification Rev 14.1 (Cal Poly SLO, 2022), its section 2 requirements and
Appendix B drawings (rail envelope, rail width, protrusions, standoffs, mass, separation springs and
deployment switches); PC/104 Specification v2.4 (board 3.550 × 3.775 in, mounting holes 0.200 in from the
edges, 0.600 in stack pitch). The modules' sizes (battery of four 18650 cells, reaction wheels,
magnetorquers, the camera, tape-spring antennas) are typical values, not from a standard. Design: the
3DCraft test drive of 2026-10-25.
