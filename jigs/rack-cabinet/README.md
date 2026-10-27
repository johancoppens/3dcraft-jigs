# 19-inch wall rack cabinet

A wall-mount 19-inch rack cabinet (EIA-310-D) of 6 to 15 U, every part laser cut and bent from one sheet
of aluminium or steel. Panels from the [`rack-panel`](../rack-panel/) Jig bolt onto its rails and fit
between its sides: both Jigs take their numbers from `scripts/racklib.py`. Licence: CC-BY-4.0.

The default is a 9 U cabinet, 450 mm deep, of 1.5 mm DC01 steel (slate blue), C-profile rails with square
cage-nut holes front and rear, three M25 knock-outs in the lid and in the bottom, and the vented door shown
opened.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Height | Cabinet | 9 U | 6 to 15 U on the rails |
| Depth | Cabinet | 450 mm | 300 to 600 mm, front to wall, step 10 mm |
| Sheet | Cabinet | Steel DC01 1.5 mm | Aluminium 5052-H32 2 / 3 mm, Steel DC01 1.5 / 2 mm |
| Rail profile | Rails | C | L (front face and a leg on the side), C (with a return at the back) |
| Rail holes | Rails | Square 9.5 mm | Square 9.5 mm (M6 cage nuts); M6 tapped (5.0 mm tap drill) only in 2 mm steel |
| Rear rails | Rails | on | on / off |
| Door | Door | on | a vented door, or an open front |
| Door shown open | Door | 105 deg | 0 to 110 deg (only the view) |
| Knock-outs | Cable entry | 3 | 1 to 4, in the lid and in the bottom, 45 mm from the back |
| Gland size | Cable entry | M25 | M20 (20.5 mm), M25 (25.5 mm), M32 (32.5 mm), EN 50262 glands |

**Parts** (each a `feature.sheetMetal` part; holes are holes of its base, so they are in its flat pattern;
round reliefs of r + t + 1 mm where two bends meet):
- **Side left / right**: the side plate with a 25 mm front lip, a top and a bottom flange bent inward;
  520 mm apart inside (`cabInnerW`, the clear width every rack-cabinet has).
- **Lid / Pan**: over the sides' top and under their bottom, three flanges down (up) over the sides and
  the front lips, the knock-outs near the back.
- **Back**: the wall plate, its back face on the wall, four flanges forward inside the sides and between
  their flanges; four 9 mm wall-mount holes (M8).
- **Rail right / left** (front) and **Rear rail right / left**: the front face carries the EIA-310 holes,
  three per U on 465.1 mm centres, from the inner edge at 225 mm (the 450 mm opening); its leg is bent back
  against the side (x = 260 mm), and a C rail has a return at the leg's back. The rear rails are the front
  ones moved back to `D - t - r - 20 - 3 (r + t) - leg - return - 5 mm`.
- **Door shown**: the vented door (a pan of four 15 mm flanges, slots 50 x 6 mm in a band at the top and at
  the bottom, four M4 hinge holes along the left), turned about its hinge line by *Door shown open*.

Rails reach 5 mm past the U range; the cabinet is n x 44.45 + 2 (5 + r + t) mm high on its sides, plus lid
and pan. Parts that are bolted together touch; none overlaps another.

**Standard and stock.** See [`rack-panel`](../rack-panel/) and `scripts/racklib.py`: EIA-310-D (19 in,
1 U = 44.45 mm, 465.1 mm hole centres, the 1/2-5/8-5/8 in pattern, 450 mm opening, 9.5 mm square holes),
IEC 60297-3-100 panel heights; DIN 6935 minimum radii and K-factor (a steel standard, an approximation for 5052), the 5052-H32 bend radii, Protolabs' 4 t
flange and 2.5 t + r hole-to-bend rules.

**Assertions (50).** Height, depth and width outside; on every rail (front and rear) the holes at the
EIA-310 places for every U and none elsewhere on its face; the rail's leg on the side and its face at 225 mm;
a hidden 450 mm block over the U range from the front to the rear rails is clear of every part (the opening);
a hidden stack of rack-panels (482.6 mm, n U - 0.8 mm) lies on the rails' front (clearance 0) and at least
4 mm from the sides, and the sides stand 520 mm apart inside; no two parts overlap; bend radius, flange
length (4 t), holes to bends (2.5 t + r) and reliefs of sides, lid, pan and back by the sheet-metal measures,
of the rails and the door (switched by `when`, see below) on their geometry; knock-outs, wall-mount holes
and the door's hinge holes and vents where they belong.

**Cutting.** The flat pattern of a part, with its bend lines (layers `outline`, `bendUp`, `bendDown`), is
written by `file.export` with `sheetMetal` (the export dialog does not offer it yet), one part per file:
`Side right`, `Side left`, `Lid`, `Pan`, `Back`, `Door`, and the rail that is on, `Rail <L|C> <square|M6>`:

```sh
craft3d-cli run dist/rack-cabinet.3dcraftjig \
  --cmd param.set --params '{"values": {"nU": 12, "D": "400 mm"}}' \
  --cmd file.export --params '{"path": "side.dxf", "sheetMetal": "Side right"}' \
  --cmd file.export --params '{"path": "rail.dxf", "sheetMetal": "Rail C square"}'
```

Cut four rails (two with rear rails off), two sides, and one of each other part. The left rails are the
mirror of the right ones and the left side the mirror of the right: cut the same blank (`Rail ...`, or `Side
right`) and flip it before bending, so the bends go the other way.

**Safety.** The cabinet hangs on its four wall-mount holes: use wall anchors and screws rated for the loaded
cabinet (equipment included) in your wall, and check that the wall carries it. M6 tapped holes in 1.5 to 2
mm sheet hold only 1.5 to 3 threads, so the Jig offers them only in 2 mm steel; in thinner sheet use the
square holes with cage nuts, or set rivnuts or clinch nuts. Choose the cage nut's clip for the sheet: 3 mm
aluminium needs the thick-panel type.

**Owed by 3DCraft** (repros in 3DCraft's `plan/repro/`): sheet-metal measures that skip parts that are off
(repro-rack-2), so the rails and the door are checked on their geometry; holes with a condition or cut later
in a flat pattern (repro-rack-4); slots in thicker sheet (repro-rack-5: the door's vents grow to 1.7 t in
radius); flanges with holes (hinge holes in the sides' lips), a flange on part of an edge, closed (mitred)
box corners; the flat pattern in the export dialog and on one sheet with the others.

**Checked.** `check-range` passes every point (87 of 87; 64 corners, every choice, 16 random; seed 1), plain and with `--deep`; 3DCraft `main` at c75ca7b8.
