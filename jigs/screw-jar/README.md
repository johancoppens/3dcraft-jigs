# Screw jar

A round jar with a screw-on lid and a real helical thread, for 3D printing. The lid follows the jar: its
thread, its size and its fit come from the jar's opening, wall, pitch and the clearance. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Opening | Jar | 60 mm | 20 to 120 mm, step 1 mm |
| Height | Jar | 70 mm | (turns + 1) × pitch + 3 × wall + clearance + 8 mm to 200 mm, step 1 mm |
| Wall | Jar | 2 mm | 1.2 to 4 mm, step 0.1 mm |
| Thread pitch | Thread | 4 mm | 2.5 to 8 mm, step 0.5 mm |
| Turns | Thread | 2 | 1.5 to 3, step 0.25 |
| Clearance | Thread | 0.3 mm | 0.15 to 0.6 mm, step 0.05 mm |
| Grip ribs | Lid | on | on / off |

**How it is built.**
- The jar is a revolved profile: a body as wide as the lid, a ledge, and a narrower neck (the opening plus
  the wall) that carries the thread. Inside, the body widens out of the neck at 45°, so it prints upright
  without supports. Bottom edge chamfered 0.6 mm, the neck's rim 0.6 mm.
- The jar's thread is a trapezoid with 45° flanks, 0.7 × pitch wide at the root and 0.28 × pitch deep,
  swept along a helix (`datum.helix`, `feature.sweep` joined to the jar) for the given turns, starting 1 mm
  above the ledge.
- The lid is a revolved cup whose skirt is as wide as the jar's body, its inside the thread's crest plus the
  clearance. Its thread is the jar's groove less the clearance on every side (root width pitch − 0.7 ×
  pitch + 2 × depth − 2 × clearance × (√2 − 1)), half a pitch above the jar's on the same helix, one turn
  shorter. So, screwed on, the lid is the clearance away from the jar everywhere: across both crests and
  square to every flank (measured with `measure.clearance` at the default: 0.300 mm).
- Grip ribs: 1.4 mm grooves round the lid's skirt, about one every 3 mm.
- The lid is laid upside down beside the jar, its top on the bed; its thread's flanks are 45° that way too.

**Printing.** Both parts print without supports. 0.3 mm clearance suits most FDM printers with a 0.4 mm
nozzle; raise it if the lid binds, lower it for a tighter fit. A coarser pitch (4 to 6 mm) prints more
reliably than a fine one.

**3DCraft features used.** Revolved profiles held by formulas, two `datum.helix` paths and helical
sweeps joined to their parts (the threads), a circular pattern whose count follows the circumference, a
boolean switched by `feature.when`, a transform that lays the lid out to print, `body.appearance` (jar
cream, lid plum), an assertion (two bodies).

**Checked.** `check-range --deep` passes at the default, 64 corners and random points (81 points with seed 1, 97 with seed 7); regeneration median about 1 s, at most about 3.5 s. Section renders of the lid
screwed on (with the transform suppressed) show each thread in the other's groove.

**Limit.** The thread has at most 3 turns: with more, 3DCraft 0.1.0 (main at baf6c1f5) cannot yet mesh the
neck's face that the thread winds round more than three times, and refuses the join.

**Sources.** The thread form (a symmetric trapezoid with 45° flanks, the internal thread the external
groove less the clearance) is the common one for printed containers; this model is designed from scratch for
3DCraft.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
