# GT2 pulley (2 mm pitch)

A timing pulley for GT2 belts with a 2 mm pitch, for 3D printing or machining. Licence: **CC-BY-SA-4.0**
(see *Tooth outline*).

| Parameter | Group | Default | Range |
|---|---|---|---|
| Teeth | Pulley | 20 | 12 to 60 (whole) |
| Belt width | Pulley | 6 mm | 4 to 20 mm, step 0.5 mm |
| Belt fit | Pulley | 0.2 mm | 0 to 0.3 mm, step 0.01 mm |
| Bore | Bore and hub | 5 mm | 2 mm to OD − 4 mm, step 0.1 mm |
| Hub | Bore and hub | on | on / off |
| Hub diameter | Bore and hub | 16 mm | max(8 mm, bore + 4 mm) to 60 mm |
| Hub length | Bore and hub | 7 mm | 3 to 20 mm |
| Flanges | Flanges | on | on / off |

**Geometry.** Pitch diameter PD = teeth × 2 mm / π; outside diameter OD = PD − 2 × 0.254 mm (the GT2
pitch line offset). One groove per tooth is the belt tooth's outline, widened across by the belt fit
(scale (1.494 mm + fit) / 1.494 mm), standing on the chord of the OD circle whose ends it meets; land arcs
on the OD join the grooves. The toothed part is belt width + 1 mm long. Flanges are 1 mm thick and 2 mm
above the OD. The bore runs through everything. The upper limit of the bore follows the teeth (a 12-tooth
pulley takes at most a 3.1 mm bore), so lowering the teeth may ask you to make the bore smaller first.

Flanges and hub are switches without conditional features: when off, the flange discs and the hub are
made small and placed inside the toothed part, where joining them changes nothing (the volume then equals
the toothed part's alone; checked).

**Checked.**
- `check-range` passes at the default, all 256 corners and random points, also with `--deep`.
- Pitch and outside diameter checked against the model for 12, 20, 37 and 60 teeth: the document's `PD`
  equals teeth × 2 mm / π and the solid's volume equals an independent closed form of the profile
  (fan of the tooth polygon plus the land sectors) to 1e-14 relative.

**Tooth outline.** The GT2 2 mm belt tooth outline (21 points) comes from droftarts' *Parametric Pulley -
lots of tooth profiles* ([thingiverse.com/thing:16627](https://www.thingiverse.com/thing:16627), January
2012), licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This Jig (its
`build.json`, `gen.py` and `.3dcraftjig`) adapts that outline and is shared under the same licence.
Changes: the points below the chord are left out and the chord's distance from the centre is computed from
the outline's own end points, so the grooves meet the land arcs exactly.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
