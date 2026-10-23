# Involute spur gear

A spur gear with true involute teeth, for 3D printing or laser cutting from thick sheet. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Module | Teeth | 1.25 mm | 0.5, 0.8, 1, 1.25, 1.5, 2, 2.5 or 3 mm (table `modules`) |
| Teeth | Teeth | 20 | 8 to 80 (whole) |
| Pressure angle | Teeth | 20 deg | 14.5, 20 or 25 deg (table `angles`) |
| Face width | Teeth | 6 mm | 2 to 30 mm, step 0.5 mm |
| Bore | Bore and hub | 4 mm | 1 mm to min(root diameter / 2, root diameter − 3 modules), step 0.1 mm |
| Hub | Bore and hub | on | on / off |
| Hub diameter | Bore and hub | 12 mm | bore + 2 mm to bore + 40 mm, step 0.5 mm (see below) |
| Hub length | Bore and hub | 6 mm | 2 to 20 mm, step 0.5 mm |

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

**Checked.**
- An assertion in the Jig checks the solid's volume against a closed form at every regeneration: the
  root disc plus, per tooth, the radial foot |φs| (rs² − rf²) and the involute part
  2 rb² [I(t)] from t0 to ta, with I(t) = u t²/2 − t³/3 + ((t² + 1) atan t − t)/2 (u = −g), plus the hub,
  less the bore. It holds to 1e-6 relative at every point checked.
- `check-range` passes for every module and pressure angle (each made the default in turn, since
  `check-range` keeps a choice taken from a table at its default in 3DCraft 0.1.0).
- The deep check (`--deep`) waits on a 3DCraft fix: at 0.1.0 it needs far more memory on this Jig than it
  should.

Ideas from the gear example of 3DCraft (`docs/examples/gear.json`, MIT): the involute formula and the
closed form of the tooth area, extended here to a tooth whose foot starts above the base circle.
