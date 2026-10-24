# Involute spur gear

A spur gear with true involute teeth, for 3D printing or laser cutting from thick sheet. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Module | Teeth | 1.25 mm | 0.5, 0.8, 1, 1.25, 1.5, 2, 2.5 or 3 mm (table `modules`) |
| Teeth | Teeth | 30 | 8 to 80 (whole) |
| Pressure angle | Teeth | 20 deg | 14.5, 20 or 25 deg (table `angles`) |
| Face width | Teeth | 6 mm | 2 to 30 mm, step 0.5 mm |
| Bore | Bore and hub | 5 mm | 1 mm to min(root diameter / 2, root diameter − 3 modules), step 0.1 mm |
| Bore type | Bore and hub | Round | Round, D-shaft, Keyway |
| D-flat depth | Bore and hub | 0.5 mm | 0.2 mm to max(0.2 mm, bore / 4), step 0.05 mm |
| Hub | Bore and hub | on | on / off |
| Hub diameter | Bore and hub | 14 mm | bore + 2 mm (more for a keyway or nut slots) to bore + 40 mm, step 0.5 mm (see below) |
| Hub length | Bore and hub | 6 mm | 2 mm (screw: hole + 2 mm; nut: 2 × (nut width / √3 + 1 mm)) to 20 mm |
| Set screw | Set screw | on | on / off |
| Screw size | Set screw | M3 | M2.5, M3, M4 (table `screws`) |
| Screws | Set screw | 1 | 1 or 2 (at 90°) |
| Captive nut | Set screw | off | on / off |
| Disc | Disc | Web and holes | Solid, Web, Holes, Web and holes |

**Geometry.** Pitch diameter = module × teeth, base diameter = pitch diameter × cos(pressure angle),
outside diameter = module × (teeth + 2), root diameter = module × (teeth − 2.5) (dedendum 1.25 modules).
The tooth thickness on the pitch circle is half the circular pitch (no backlash; a printer's fit gives
some). Each flank is the involute of the base circle, drawn from its formula with `sketch.curve`:
x = rb (cos(g + t) + t sin(g + t)), y = rb (sin(g + t) − t cos(g + t)), turned by g = −π/(2z) − inv(α)
so the tooth is symmetric about the x axis. Below the base circle (or, when the base circle lies inside the
root circle, below root + 0.1 module) the flank runs on radially to the root circle. Tip and root are arcs
of the outside and root circles, also drawn as formula curves. One tooth's outline is repeated round as a
chained sketch pattern, so the whole gear is one profile and one extrusion, without a boolean per tooth.
Two gears mesh when they share module and pressure angle, at a centre distance of
module × (teeth1 + teeth2) / 2. Small tooth counts are undercut in a real hobbed gear; this Jig draws the
pure involute with a radial foot, which prints and runs well for hobby use.

The hub diameter is kept between bore + 0.8 mm and 0.6 times the root diameter (and the root
diameter less four modules), so a hub never runs into the teeth when you change the module or the teeth.
Its top edge is chamfered (0.5 mm at most).

**Bore and set screws** (`scripts/shaftlib.py`, shared with `gt2-pulley`): round, D-shaft or a DIN 6885-1
keyway sized from the bore (table `keys`; only where it leaves 0.8 mm under the teeth and in the hub),
and one or two grub screws M2.5/M3/M4 (table `screws`) radially through the hub, optionally with captive
hex-nut slots open at the hub's top. Screws need the hub; see the pulley's README for the details.

**Disc.** A large gear can be lightened: **Web** recesses both faces between a boss (round the bore, the
keyway and the hub) and a rim of max(1.5 mm, 2 modules) under the root circle, down to a web of a third
of the face width (at least 1.5 mm); **Holes** puts a ring of 4 to 8 round holes there, as many as fit
with 1 mm between them. Each is built only when the gear has room (3 mm of disc for the web, holes of at
least 1 mm radius), so a small gear stays solid. Colour: ochre (#D4A24C), a printed part.

**Checked.**
- An assertion checks the solid's volume against a closed form at every regeneration: the root disc plus,
  per tooth, the radial foot |φs| (rs² − rf²) and the involute part 2 rb² [I(t)] from t0 to ta, with
  I(t) = u t²/2 − t³/3 + ((t² + 1) atan t − t)/2 (u = −g), plus the hub less its chamfer, less the bore
  (its D-flat a circular segment, its keyway the strip outside the circle), the web's two annular
  recesses and the holes, to 1e-6 relative. Set screws and nut slots are estimated (a cylinder and a box
  each) and widen the tolerance by 20 % of their volume.
- `check-range --deep` passes: 113 of 113 points (64 of the corners, 16 choices, 32 random; 3DCraft `main` at
  baf6c1f5), regeneration median about 0.5 s, at most about 4.3 s native (the web and holes on an 80-tooth gear).
- One body (assertion).

Ideas from the gear example of 3DCraft (`docs/examples/gear.json`, MIT): the involute formula and the
closed form of the tooth area, extended here to a tooth whose foot starts above the base circle.
