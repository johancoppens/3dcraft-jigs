# GT2 pulley (2 mm pitch)

A timing pulley for GT2 belts with a 2 mm pitch, for 3D printing or machining. Licence: **CC-BY-SA-4.0**
(see *Tooth outline*).

| Parameter | Group | Default | Range |
|---|---|---|---|
| Teeth | Pulley | 20 | 12 to 60 (whole) |
| Belt width | Pulley | 6 mm | 4 to 20 mm, step 0.5 mm |
| Belt fit | Pulley | 0.2 mm | 0 to 0.3 mm, step 0.01 mm |
| Bore | Bore and hub | 5 mm | 2 mm to OD − 4 mm, step 0.1 mm |
| Bore type | Bore and hub | Round | Round, D-shaft, Keyway |
| D-flat depth | Bore and hub | 0.5 mm | 0.2 mm to max(0.2 mm, bore / 4), step 0.05 mm |
| Hub | Bore and hub | on | on / off |
| Hub diameter | Bore and hub | 16 mm | max(8 mm, bore + 4 mm, room for the keyway and the nut slots) to 60 mm |
| Hub length | Bore and hub | 7 mm | 3 mm (screw: hole + 2 mm; nut: 2 × (nut width / √3 + 1 mm)) to 20 mm |
| Set screw | Set screw | on | on / off |
| Screw size | Set screw | M3 | M2.5, M3, M4 (table `screws`) |
| Screws | Set screw | 1 | 1 or 2 (at 90°) |
| Captive nut | Set screw | off | on / off |
| Flanges | Flanges | on | on / off |

**Geometry.** Pitch diameter PD = teeth × 2 mm / π; outside diameter OD = PD − 2 × 0.254 mm (the GT2
pitch line offset). One groove per tooth is the belt tooth's outline, widened across by the belt fit
(scale (1.494 mm + fit) / 1.494 mm), standing on the chord of the OD circle whose ends it meets; land arcs
on the OD join the grooves. The toothed part is belt width + 1 mm long. Flanges are 1 mm thick and 2 mm
above the OD. The bore runs through everything. The upper limit of the bore follows the teeth (a 12-tooth
pulley takes at most a 3.1 mm bore), so lowering the teeth may ask you to make the bore smaller first.

**Bore and set screws** (`scripts/shaftlib.py`, shared with `spur-gear`). The bore is round, a D-shaft
(a flat at *D-flat depth* from the bore's wall, facing +x) or a keyway to DIN 6885-1 whose width and depth
come from the table `keys` by the bore (2 × 1 mm up to 8 mm, … 10 × 3.3 mm up to 38 mm). The keyway is only
cut where it is at least half the bore and leaves a 0.8 mm wall under the teeth and in the hub; otherwise
the bore stays round. One or two grub screws (M2.5, M3, M4 from the table `screws`) go radially through the
hub at half its length, the first facing +x onto the flat or the key, the second at 90°. Without a nut the
hole is the tap size (the screw cuts its own thread in the print); with **Captive nut** it is the clearance
size, and a slot for an ISO 4032 hex nut (+0.3 mm) runs from the hub's free end to past the screw's axis,
1.2 mm from the bore (beyond the keyway). Screws need the hub; a nut slot is left out when the hub has no
room for it with a 1 mm wall.

**Options as conditional features.** Flanges, hub, flat, keyway, screws and nut slots are `feature.when`
features. The flanges' belt-side rims and the top flange's outside are chamfered 0.3 mm and the hub's foot
0.6 mm, each chamfer on its own part before it is joined, so a part that is off takes its chamfer with it.
Colour: petrol (#2E7D7A), a printed part.

**Checked.**
- `check-range --deep` passes: 101 of 101 points (64 of the corners, every choice, 32 random; 3DCraft
  `main` at baf6c1f5), and 133 of 133 with `--samples 64 --seed 7`; regeneration median about 140 ms,
  at most about 750 ms native.
- One body (assertion). Earlier: pitch and outside diameter checked against the model for 12, 20, 37 and
  60 teeth, the solid's volume equal to a closed form of the profile to 1e-14 relative.

**Tooth outline.** The GT2 2 mm belt tooth outline (21 points) comes from droftarts' *Parametric Pulley -
lots of tooth profiles* ([thingiverse.com/thing:16627](https://www.thingiverse.com/thing:16627), January
2012), licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This Jig (its
`build.json`, `gen.py` and `.3dcraftjig`) adapts that outline and is shared under the same licence.
Changes: the points below the chord are left out and the chord's distance from the centre is computed from
the outline's own end points, so the grooves meet the land arcs exactly.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
