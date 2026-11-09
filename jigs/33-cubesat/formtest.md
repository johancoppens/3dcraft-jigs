# Form test

We are a university team building a 3U Earth-observation CubeSat for a rideshare launch, in a rail dispenser shared with
other CubeSats. Our camera is 140 mm long, weighs 1.8 kg and looks down through the bottom end. Above it we fly five
PC/104 boards (on-board computer, power, radio, attitude control, payload interface) and a battery of eight 18650 cells.
The downlink is UHF at 436.5 MHz on a deployable turnstile, and we want four deployable solar panels.

Show us the satellite as it flies, opened out. How heavy is it, and is its centre of gravity inside the box the CubeSat
Design Specification allows, in the dispenser? How long is each antenna element, and how much power do the solar panels
give facing the sun? What do we send to the machine shop for the structure, and what to the PCB house for the solar
panels? Could we fly a 4 kg camera instead?

## Acceptance

- 3U, camera payload 140 mm long and 1.8 kg, five avionics boards, the 8-cell battery, four wings, 436.5 MHz, fully
  deployed. All assertions pass.
- Total mass about 3.84 kg, under the 6 kg typical maximum of CDS Table 1. Stowed centre of gravity along the rails
  about −26 mm, inside the ±70 mm of Table 2; in x and y within about 1.5 mm of the centre.
- Antenna elements 171.7 mm, a quarter wave at 436.5 MHz, at the bottom end with the camera; the deployed wings about
  0.47 wavelength from them, not flagged as inside the antenna's reactive near field. 28 cells on the wings and 29 on
  the body (one on the top end); about 34.9 W at the beginning of life with the wings and top end facing the sun;
  battery 92.2 Wh.
- Exports: a STEP file with the machined parts (two rail hands, the top and the bottom frame, a pair of hinge brackets,
  the RBF pin), and a DXF with one body-panel, one top-panel and one wing PCB outline, with their screw holes (the ±X
  and ±Y PCBs are the same part on a 3U).
- Refusal: a 4 kg camera cannot be set; the form allows at most about 3.96 kg in this configuration (what the CDS
  Table 1 mass leaves).
