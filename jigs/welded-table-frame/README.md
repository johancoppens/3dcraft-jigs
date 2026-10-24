# Welded table frame

A welded steel table frame of square or rectangular tube or angle iron, with mitred or butt top corners,
an optional ring of cross rails for a shelf and optional levelling feet. Every piece is a body of its own,
and the Jig carries its own **cut list**. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Length | Size | 1200 mm | 400 to 2400 mm, step 10 mm |
| Width | Size | 600 mm | 300 to 1200 mm, step 10 mm |
| Height | Size | 750 mm | 400 to 1100 mm, step 5 mm (floor to top, feet included) |
| Profile | Profile | SHS 40x40x2 | 14 sizes from the table `profiles` (below) |
| Mitred top corners | Profile | on | on / off |
| Cross rails | Cross rails | on | on / off |
| Cross rail height | Cross rails | 150 mm | 100 mm to height − 2 × profile height − 100 mm, step 5 mm |
| Levelling feet | Feet | on | on / off |

**Profiles** (table `profiles`, height × width × wall in mm): square hollow sections SHS 20x20x2,
25x25x2, 30x30x2, 40x40x2, 40x40x3, 50x50x3, 60x60x3; rectangular hollow sections RHS 40x20x2, 50x30x2,
60x40x3, 80x40x3 (standing on edge); equal angles L 30x30x3, 40x40x4, 50x50x5. A tube's outside corner
radius is 2 × wall and its inside radius 1 × wall; an angle has its root radius (5, 6 and 7 mm) and
0.5 mm on its other edges (the toe radius is left sharp).

**How it is built.** x runs along the length, y across, z up; the frame's outside corner is at the
origin. Each bar is its section (a rounded rectangle, less the bore of a tube or, for an angle, the
quarter beyond its two flanges with the root radius in the corner) extruded to its cut length.

- *Mitred* (the default, and always for angle): the top frame is four rails mitred at 45° at both ends,
  full length and full width, set on the legs; the legs are the height less the feet and the rail height.
- *Butt*: the legs run to the top and the top rails butt between them, outside faces flush.
- The cross rails always butt between the legs, outside faces flush, their underside at the cross rail
  height.
- A rectangular tube leg shows its narrow side at the ends (profile height along the length).
- Levelling feet: a 5 mm end plate with chamfered corners is welded under each leg, and a levelling foot
  screws into it: an M10 stud (M12 for legs of 40 mm and wider) with an ISO 4032 lock nut (17 or 19 mm
  across flats) and a 10 mm round pad with a rounded top. The legs are shorter by the 31 mm of the foot.

**Cut list.** The named sets are the cut list, each checked by an assertion at every regeneration:

| Set | Pieces | Cut length | Ends |
|---|---|---|---|
| Legs | 4 | variable `legLen`, asserted as the legs' height | square |
| Top rails, long | 2 | `topLongLen`, asserted as their extent along x | `topMitre` (45° or 0°) both ends |
| Top rails, short | 2 | `topShortLen`, asserted along y | `topMitre` both ends |
| Cross rails, long | 2 or 0 | `crossLongLen` (length − 2 legs) | square (`crossMitre` = 0°) |
| Cross rails, short | 2 or 0 | `crossShortLen` (width − 2 legs) | square |
| End plates | 4 or 0 | leg footprint × 5 mm | 1 mm chamfered corners |
| Levelling feet | 4 or 0 | bought: M10 or M12 | |

The set **Steel** holds every steel piece; the assertion *Steel weight (kg)* reports their mass with
S235 steel (7850 kg/m³). `totalLen` is the total length of tube or angle to buy. To read the cut list:

```sh
craft3d-cli run dist/welded-table-frame.3dcraftjig \
  --cmd param.set --params '{"values": {"L": "1500 mm", "profile": "RHS 60x40x3"}}' \
  --cmd assert.list
```

Each assertion shows what it measured (`Legs: cut length` 679 mm at the defaults, `Steel weight` 22.0 kg),
and `document.inspect` lists the variables. `select.set {"set": "Legs"}` selects the pieces of one row. Export the whole frame as STEP, or one set's
bodies with `file.export {"bodies": [...]}`.

**Checked.**
- `check-range --deep` passes at the default, all 256 corners, every profile and 64 random points (334
  of 334, seed 1; regeneration median about 26 ms).
- The leg of the default frame weighs 1.565 kg for 679 mm: 2.31 kg/m, the tabulated mass of SHS
  40x40x2 in EN 10219-2.

**Sources.**
- EN 10219-2:2006, *Cold formed welded structural hollow sections: tolerances, dimensions and sectional
  properties*: the sizes and the outside corner radius of 1.6 t to 2.4 t (t ≤ 6 mm); the masses per
  metre.
- EN 10056-1:2017, *Structural steel equal and unequal leg angles: dimensions*: the angle sizes and root
  radii.
- ISO 4032, *Hexagon regular nuts (style 1)*: M10 17 mm across flats, 8.4 mm high; M12 19 mm, 10.8 mm.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
