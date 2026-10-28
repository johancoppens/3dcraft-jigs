# 19-inch wall rack cabinet

A wall-mount 19-inch rack cabinet (EIA-310-D) of 6 to 15 U, every part laser cut and bent from one sheet
of aluminium or steel. Panels from the [`rack-panel`](../rack-panel/) Jig bolt onto its rails and fit
between its sides: both Jigs take their numbers from `scripts/racklib.py`. Licence: CC-BY-4.0.

The default is a 9 U cabinet, 450 mm deep, of 1.5 mm DC01 steel (slate blue), C-profile rails with square
cage-nut holes front and rear, three M25 knock-outs in the lid and in the bottom, and the vented door shown
opened; the lid's, the pan's and the door's corners closed by overlap with a 0.5 mm gap, round corner
reliefs.

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
| Corners | Corners | Overlap | Open, Butt, Overlap, Miter: the lid's, the pan's and the door's corners (below) |
| Corner gap | Corners | 0.5 mm | 0.4 to 2 mm, step 0.1 mm; for a butt at most min(2 mm, thickness − 0.1 mm) |
| Corner relief | Corners | Round | Rect, Round, Tear, R + t + 0.5 mm along each edge |

**Parts** (each a `feature.sheetMetal` part; every hole is drawn in the flat, in the part's sketch or in a
`cutouts` sketch switched by `when`, so every hole, those in flanges included, is in its flat pattern;
a relief where two bends meet):
- **Side left / right**: the side plate with a 25 mm front lip (longer in 3 mm sheet, to hold the hinge
  holes 2.5 t + r from its bend), a top and a bottom flange bent inward; 520 mm apart inside (`cabInnerW`,
  the clear width every rack-cabinet has). Three M6 bolt holes (6.6 mm) for each front rail's leg, and
  three for each rear rail's when the rear rails are on; in the left side's lip four M4 holes (4.5 mm) at
  the door's hinge holes' heights, when the door is on. They are a **placeholder pattern**, not a given
  hinge's: centred on the lip, they lie about 2.6 mm across from the door's hinge holes (x = −245.9 against
  −248.5 mm by default), which suits no particular hinge; drill both to the hinge you buy, or move them in
  `gen.py` (`lipHoleU`, `hingeX`) once one is chosen.
- **Lid / Pan**: over the sides' top and under their bottom, three flanges down (up) over the sides and
  the front lips, the knock-outs near the back.
- **Back**: the wall plate, its back face on the wall, four flanges forward inside the sides and between
  their flanges; four 9 mm wall-mount holes (M8).
- **Rail right / left** (front) and **Rear rail right / left**: the front face carries the EIA-310 holes,
  three per U on 465.1 mm centres, from the inner edge at 225 mm (the 450 mm opening); its leg is bent back
  against the side (x = 260 mm), and a C rail has a return at the leg's back. The leg (30 mm, longer in 3 mm
  sheet) has three M6 bolt holes on the side's, near the rail's ends and in its middle. The rear rails are
  the front ones moved back to `D - t - r - 20 - 3 (r + t) - leg - return - 5 mm`. One variant per profile
  (`Rail L`, `Rail C`); the square or round face holes are two `cutouts` sketches both share, switched by
  *Rail holes* (four variants and three unions before).
- **Door shown**: the vented door (a pan of four 15 mm flanges, slots 50 x 6 mm in a band at the top and at
  the bottom, four M4 hinge holes along the left), turned about its hinge line by *Door shown open*.

Rails reach 5 mm past the U range; the cabinet is n x 44.45 + 2 (5 + r + t) mm high on its sides, plus lid
and pan. Parts that are bolted together touch; none overlaps another.

**Corners and reliefs.** The lid's and the pan's front corners and the door's four corners are closed by
the *Corners* choice (`feature.sheetMetal`'s `corner` by expression, 1 open, 2 butt, 3 overlap, 4 miter):
the flats run on past their bends towards the other flange and stop *Corner gap* from it. **Overlap** is
the default: the lid's and pan's front flange and the door's side flanges run flush with the other
flange's outside face and cover its end, the other stops the gap short of the cover's inside; an unwelded
cabinet is folded so, and the covered flange has the gap for the press brake's angle error. Butt stops
the cover the gap short of flush too (the gap is less than the thickness then); miter meets on the plane
halving the corner, to weld. The **sides' and the back's corners stay open**: they sit inside the lid's
and pan's front bends and the sides' top and bottom bends, which wrap round them; closed, a side's corner
runs into the lid's bend radius (12.6 mm³ of overlap with 1.5 mm steel) and the back's into the sides'
(22 mm³). Every corner keeps its **relief** (a closed corner needs it as the hole where the bends would
cross): the *Corner relief* choice (relief `shape` by expression, 1 rect, 2 round, 3 tear; round by
default: no sharp inside corner to crack from, and the least material taken out of the flat, measured in
[`sheet-metal-enclosure`](../sheet-metal-enclosure/); SendCutSend notes round reliefs leave slightly
larger gaps at the bend ends), its size **R + t + 0.5 mm** along each edge, the rule of
`sheet-metal-enclosure`: past the bend zone by half a millimetre. That is SendCutSend's rule for a bend
relief's depth (at least bend radius + thickness + 0.020 in; sendcutsend.com/blog/guide-to-designing-bend-reliefs),
applied to corner reliefs by analogy. It was r + t + 1 mm, round only, before. *Corner gap* is at least
0.4 mm, SendCutSend's least gap between flanges (0.015 in, same guide); for a butt at most
min(2 mm, t − 0.1 mm).

**Standard and stock.** See [`rack-panel`](../rack-panel/) and `scripts/racklib.py`: EIA-310-D (19 in,
1 U = 44.45 mm, 465.1 mm hole centres, the 1/2-5/8-5/8 in pattern, 450 mm opening, 9.5 mm square holes),
IEC 60297-3-100 panel heights; DIN 6935 minimum radii and K-factor (a steel standard, an approximation for 5052), the 5052-H32 bend radii, Protolabs' 4 t
flange and 2.5 t + r hole-to-bend rules.

**Assertions (62).** Height, depth and width outside; on every rail (front and rear) the holes at the
EIA-310 places for every U and none elsewhere on its face; the rail's leg on the side and its face at 225 mm;
a hidden 450 mm block over the U range from the front to the rear rails is clear of every part (the opening);
a hidden stack of rack-panels (482.6 mm, n U - 0.8 mm) lies on the rails' front (clearance 0) and at least
4 mm from the sides, and the sides stand 520 mm apart inside; no two parts overlap; bend radius, flange
length (4 t), holes to bends (2.5 t + r) and reliefs of every part that is on (rails and door included) by
the sheet-metal measures; the closed corners' gap by `cornerGap` (through the output `cornerGapMeasured`;
with *Corners* open it is *not proven*, see *Owed*); at every rail bolt place a hole in the rail's leg and
one in the side, in the same box round the place (so they line up); the hinge holes in the left side's lip;
knock-outs, wall-mount holes and the door's hinge holes and vents where they belong.

**Cutting.** The flat pattern of a part, with its bend lines (layers `outline`, `bendUp`, `bendDown`), is
written by `file.export` with `sheetMetal`, one part per file:
`Side right`, `Side left`, `Lid`, `Pan`, `Back`, `Door`, and the rail that is on, `Rail L` or `Rail C`
(in the window, File › Export to .dxf or .svg offers each part's flat pattern, and all of them on one sheet):

```sh
craft3d-cli run dist/rack-cabinet.3dcraftjig \
  --cmd param.set --params '{"values": {"nU": 12, "D": "400 mm"}}' \
  --cmd file.export --params '{"path": "side.dxf", "sheetMetal": "Side right"}' \
  --cmd file.export --params '{"path": "rail.dxf", "sheetMetal": "Rail C"}'
```

Cut four rails (two with rear rails off), two sides, and one of each other part. The left rails are the
mirror of the right ones: cut the same blank (`Rail ...`) and flip it before bending, so the bends go the
other way. The sides are two blanks: the left one has the door's hinge holes in its lip.

**Safety.** The cabinet hangs on its four wall-mount holes: use wall anchors and screws rated for the loaded
cabinet (equipment included) in your wall, and check that the wall carries it. M6 tapped holes in 1.5 to 2
mm sheet hold only 1.5 to 3 threads, so the Jig offers them only in 2 mm steel; in thinner sheet use the
square holes with cage nuts, or set rivnuts or clinch nuts. Choose the cage nut's clip for the sheet: 3 mm
aluminium needs the thick-panel type.

**Owed by 3DCraft** (repros in 3DCraft's `plan/repro/`): `cornerGap` breaks when the Jig's choice opens
every corner and an assertion has no condition, so with *Corners* open the gap assertion is *not proven*
(repro-sheet-metal-enclosure-7); `holeToBend` on a part with no hole beside a bend is an error, not a value
(repro-rack-4, still so; every part here has one); the hinge and bolt holes on the lip and the rail legs
are placed by unfolding by hand (`lipHoleU`, `legHoleV` re-implement the bend allowance π/2 (R + K t);
checked by the bolt-hole assertions), where a cut-out placed on a flange in its folded position or a
flange's flat offset as an output would do (repro-sheet-metal-enclosure-8, a feature request). Fixed since the first version and used now: the
sheet-metal measures skip parts that are off (repro-rack-2), holes with a condition (`cutouts`) and holes in
flanges, narrow slots in thick sheet (repro-rack-5: the door's vents are 6 mm wide in every sheet again),
closed corners, the flat pattern in the export dialog and on one sheet. Still not built: a flange on part
of an edge, and a closed corner set back to clear a mating part's bend (the sides' and the back's corners).

**Checked.** `check-range` with 3DCraft `main` at 0b2f171e (format 44): 92 of 92 points without a failure
(64 corners, every choice, 16 random; seed 1), 51 passed and 41 not proven, every one of those with
*Corners* open (see *Owed*); with `SAMPLES=64 SEED=7 DEEP=1` 140 of 140 without a failure. Regeneration
median about 140 ms a point (about 120 ms before, with open corners, no bolt or hinge holes and assertions
that no longer held on this 3DCraft: hole walls are cylinders now, not freeform faces).
