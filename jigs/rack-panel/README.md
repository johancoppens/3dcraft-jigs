# 19-inch rack panel

A 19-inch rack front panel (EIA-310-D, IEC 60297) of 1 to 4 U, laser cut and bent from aluminium or steel
sheet. It bolts onto any 19-inch rack and onto the rails of the [`rack-cabinet`](../rack-cabinet/) Jig,
whose sides it fits between: both Jigs take their numbers from `scripts/racklib.py`. Licence: CC-BY-4.0.

The default is a 3 U panel of 2 mm aluminium with stiffening flanges, M6 slots, handle holes and a row of
eight XLR (Neutrik D) cut-outs.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Height | Panel | 3 U | 1 to 4 U (at least 2 U when flanged with handles or cut-outs) |
| Sheet | Panel | Aluminium 5052-H32 2 mm | Aluminium 5052-H32 2 / 3 mm, Steel DC01 1.5 / 2 mm |
| Flanges | Panel | on | on / off: top and bottom edges bent back between the rails |
| Mounting | Panel | Slots | Round holes (6.6 mm), Slots (10 x 6.6 mm; not in 3 mm aluminium) |
| Handle holes | Panel | on | on / off: two M4 (4.5 mm) holes each side, 19.05 mm inboard of the mounting holes |
| Cut-outs | Cut-outs | XLR / Neutrik D | None, D-sub DE-9 (socket), XLR / Neutrik D, Window |
| Connectors | Cut-outs | 8 | 1 to as many as fit (pitch 33 mm D-sub, 32 mm XLR) |
| Window width | Cut-outs | 300 mm | 20 mm to the cut-out zone's width |
| Window height | Cut-outs | 25 mm | 10 mm to the height that keeps clear of the edges and bends |

**The standard (racklib.py).**
- Width 482.6 mm (19 in); height n x 44.45 mm - 0.8 mm (IEC 60297-3-100: 43.65 mm for 1 U), centred on
  its U boundaries.
- Mounting holes on 465.1 mm (18.312 in) centres. The rail pattern repeats every U with spacings of 1/2,
  5/8, 5/8 in: holes 6.35, 22.225 and 38.1 mm above the U's boundary. The panel uses the outer two of every
  U (6.35 and 38.1 mm), M6: 6.6 mm holes (ISO 273 medium) or 10 x 6.6 mm slots.
- Everything else (cut-outs, handle holes, flanges) stays inside the 450 mm (17.72 in) opening between the
  rails.
- Sources: EIA-310-D as restated by RackSolutions (help.racksolutions.com, "What is EIA 310") and IBM
  ("Rack installation specifications for racks not purchased from IBM": 450 mm opening, holes 465 +- 1.6
  mm); IEC 60297-3-100 panel heights.

**Cut-outs.** D-sub DE-9 front-mount cut-out for a female (socket) connector, after Harting / CECC 75 301-802: a trapezoid 20.5 mm wide at
the top, 11.4 mm high, sides at 10 degrees, two 3.1 mm screw holes on 25 mm centres. Neutrik D series
(XLR): a 24 mm hole and two 3.2 mm holes 19 x 24 mm apart on a diagonal. A row is centred; with handle holes
it keeps 6 mm clear of them.

**Sheet metal.** The panel is a `feature.sheetMetal` part; its holes are holes of the base sketch, so they
are in the flat pattern. With flanges, the top and bottom edges are bent back 90 degrees between x = +-(225 -
5 - d) mm, where a 45-degree notch d = r + t deep at each end is the bend relief and keeps the ears flat; the
bent flange's back is then flush with the panel's edge. Bend radius, K-factor and the rules come from the
stock table in `racklib.py`:
- inner radius: DIN 6935 table 1 for DC01 (1.6 mm at 1.5 mm, 2.5 mm at 2 mm); aluminium 5052-H32 1 t at
  2 mm, 1.5 t at 3 mm (the Aluminum Association's bend radii as suppliers restate them);
- K-factor from DIN 6935's k = 0.65 + 0.5 log10(r / s), K = k / 2 (DIN 6935 is a steel standard; for 5052 it is an approximation);
- flange at least 4 t, holes at least 2.5 t + r from a bend (Protolabs' sheet metal design guide), measured
  from the bend's tangent line.

**Assertions (34).** Width 482.6 mm, height n U - 0.8 mm, centred on the U boundaries, narrower than the
rack-cabinet's inner width less 4 mm each side (the cabinet checks its sides against a reference panel of
the same spec); a mounting hole at the outer two EIA-310 places of every U (6.35 and 38.1 mm) and none
elsewhere in the ears; every other hole inside the 450 mm opening and clear of the mounting holes;
cut-outs and handle holes as asked; the bends at least the stock's minimum radius, flanges at least 4 t,
holes at least 2.5 t + r from a bend; and on two hidden rails of a rack (the 450 mm opening to the
rack-cabinet's sides) the panel lies on their front without reaching into them (clearance 0).

**Cutting.** Flat: the face set **Cut sheet** (File > Export..., DXF or SVG, "Sheet of set: Cut sheet").
Flanged: the flat pattern with bend lines (layers `outline`, `bendUp`) is written by `file.export` with
`sheetMetal` (or in the window File › Export to .dxf or .svg, "Flat pattern of" the part); the part to name is the one that is on, `Panel
flanged <cut-out>[ handles] <slots|holes>` (for the default `Panel flanged XLR handles slots`):

```sh
craft3d-cli run dist/rack-panel.3dcraftjig \
  --cmd param.set --params '{"values": {"nU": 1, "flanged": false}, "clamp": true}' \
  --cmd file.export --params '{"path": "panel.svg", "sheetMetal": "Panel flat XLR handles slots"}'
```

`"clamp": true` moves values that the new height puts out of range (the window, the connector count) into it.

**Fitting.** M6 cage nuts in square-hole rails, or M6 screws into tapped rails; use panel washers on slots.

**How it is built.** A hole of a sketch cannot be switched by a condition, so there is one sketch and one
sheet-metal part per combination of flanges, cut-out, handles and fixing (32), each with its `when`; a chain
of unions passes the one that is on as the body **Panel**. Because `bendRadius`, `flangeLength` and
`holeToBend` refuse a part that is switched off (also when every part is meant), the sheet-metal rules are
measured on the geometry: the bends are the part's cylinders (their radius at least the minimum), the
flanges' reach behind the panel, the distance from every hole wall to the bends.

**Owed by 3DCraft** (repros in 3DCraft's `plan/repro/`): sheet-metal measures that skip parts that are off
(repro-rack-2); a plate's rim over a circle as a cylinder face (repro-rack-3); holes cut later in the flat
pattern, or holes with a condition (repro-rack-4); slots in sheet thicker than about r / 1.3 (repro-rack-5,
hence no slots in 3 mm aluminium); a measure that fails on a plate in a plane through the origin
(repro-rack-1). (The flat pattern in the export dialog and several flat patterns on one sheet, listed
here before, are built in 3DCraft since.)

**Bend sequence** (`scripts/bendcheck.py rack-panel`, `press.json`; README at the root). The flanged
panel's two bends are parallel and as long as each other, so the tools of the check (a straight punch, a
gooseneck punch, a V-die of 8 t; as long as the bend) are the ones a shop would use, and the bends could be
made in either order. 3DCraft's `sheetMetal.bendSequence` cannot prove it yet: the panel's ears reach
past each flange's bend line beside its ends (the 45-degree notch), so as the panel's leg rises they dip
below the die's top, and its proof of a piece resting on the die needs the piece to stay above the top;
every first step is *not proven* in its first 0.09 degrees, never a collision. Reproduced on a plain
rectangle with a flange on a recessed edge; without the notch (a flange on a whole edge) the same plate is
proven. So `press.json` asks nothing of the panel (`prove: false`) and the check only reports. Owed by
3DCraft: proving material of the bend's own leg that dips into the die's V (the die's opening, not its
top). At 0dc5efb6, 24 points (the defaults, 8 corners, every choice, 8 random; seed 1): the panel is flanged at 17, every one *not proven* for that reason, none colliding.

**Checked.** `check-range` passes 88 of 88 points (64 corners, every choice, 16 random; seed 1), plain and with `--deep`; 3DCraft `main` at c75ca7b8.
At 0dc5efb6 the same file (and the same `build.json` rebuilt) fails all 88: the hole assertions find the
holes' walls as freeform faces, and 3DCraft's plate rims over circles are cylinders now (repro-rack-3,
fixed); `"hole": true` does not tell them from the bends either. The panel is still to be moved to the
current 3DCraft (holes in `cutouts` sketches with `when`, one part instead of 32, and the sheet-metal
measures, all built since); its model is left as it was here.
