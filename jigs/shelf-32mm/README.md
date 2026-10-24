# 32 mm shelf system (IKEA compatible)

A bookcase or wardrobe carcass on the European 32 mm system, to cut on a CNC router or a panel saw and
drill with a shelf-pin jig. The sides carry two columns of 5 mm shelf-pin holes on a 32 mm pitch, 37 mm
from the front and the back edge, so standard 5 mm shelf pins (IKEA's included) fit. Licence: CC-BY-4.0.

IKEA is a trademark of Inter IKEA Systems B.V.; this Jig is not affiliated with or endorsed by IKEA.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Size | Size | Custom | Custom, BILLY 40/80 × 28 × 202, PAX 50/75/100 × 35/58 × 201/236 (table `presets`) |
| Width (Custom) | Size | 800 mm | 300 to 1200 mm, step 1 mm |
| Depth (Custom) | Size | 320 mm | 250 to 650 mm, step 1 mm |
| Height (Custom) | Size | 1600 mm | 600 to 2400 mm, step 1 mm |
| Panel thickness | Material | 18 mm | 15, 16, 18, 19 or 22 mm (table `thicknesses`) |
| Back panel | Material | 3 mm hardboard | 3, 4, 6 or 8 mm (table `backs`) |
| Back fixing | Material | groove | groove or rebate |
| Adjustable shelves | Shelves | 2 | 0 to what keeps 96 mm between shelves (at most 8) |
| Fixed middle shelf | Shelves | on | on / off |
| Plinth height | Base | 70 mm | 0 (none) to 150 mm, step 1 mm |

**How it is built.** Two sides run the full height; the top and the bottom sit between them, the bottom on
the plinth (a board at the front between the sides). The hole grid starts at the top of the bottom panel:
rows every 32 mm from 64 mm above it to at least 64 mm below the top panel, so every shelf position is a
multiple of 32 mm. The fixed shelf is centred on the hole row nearest the middle (the two holes behind
each end take its connectors or dowels). The adjustable shelves rest on pins (their underside 3 mm above
a row's centre), 1 mm clear of each side, spread over each compartment on whole multiples of 32 mm. The
back slides into a 12 mm-inset groove (0.5 mm wider than the back) or lies in a rebate flush with the back
edge, in the sides, the top and the bottom; the slots in the sides are stopped inside the panel, so they
do not show at the top or the bottom. Hole depth min(12 mm, thickness − 5 mm); slot depth
min(8 mm, thickness / 2 − 1 mm). The outer front edge of each side and the visible front edges of the
top, the bottom and the shelves are rounded 1 mm (as edge banding is), never on a face of the cut sheet.

**Cutting and drilling.** Two named face sets (File › Export…, DXF or SVG, *Sheet of set*):

- **Cut sheet**: every panel at true size, one layer per part: the inner face of each side with its holes
  and its back slot, the top, the bottom, the fixed shelf, each adjustable shelf, the back and the plinth.
  `file.export {"path": "shelf.dxf", "set": "Cut sheet", "width": "2500 mm"}` packs them in rows on a
  2500 mm sheet.
- **Side drilling**: the left side alone, seen from inside (the right side is its mirror image): a drilling
  template with the hole centres and the slot.

**Presets (real carcass sizes).** Width × depth × height of the outer carcass, from IKEA's product pages:

- BILLY bookcase 40 × 28 × 202 cm and 80 × 28 × 202 cm ([ikea.com.tr, BILLY 80×28×202](https://www.ikea.com.tr/en/p20522046),
  [ikea.com/my, BILLY](https://www.ikea.com/my/en/p/billy-bookcase-white-00522047/)).
- PAX wardrobe frame: widths 50, 75 and 100 cm, depths 35 and 58 cm, heights 201 and 236 cm
  ([ikea.com/cz, PAX 50×58×236](https://www.ikea.com/cz/en/p/pax-wardrobe-frame-dark-grey-70509132/),
  [NRLA, PAX sizes](https://www.nrla.org.uk/news/how-to-design-your-perfect-pax-wardrobe)).

**What is uncertain.** The presets give the outer size only; panel thickness, plinth and back are your
choice. Not every PAX width/depth/height combination in the table is sold in every market (75 × 35 cm is
left out for that reason; check your local catalogue). IKEA does not publish its panel thicknesses or hole
layouts: PAX panels are reported to be about 18 mm and their hole columns not symmetric front to back
([Shaper hub, IKEA PAX holes](https://hub.shapertools.com/creators/5f563c85a27c7f000fd43067/shares/6027a190235e010012614505)),
and METOD cabinets use 20 mm and 52 mm from the front edge
([hausbau-forum](https://www.hausbau-forum.de/en/threads/hole-spacing-ikea-utrusta-medod-and-system-32.20972)),
so this Jig is compatible with IKEA's 5 mm shelf pins and 32 mm pitch, not a copy of any IKEA part's
drilling. BILLY's own hole spacing is not documented here. KALLAX is not offered: its shelves are fixed
and its frame is not drilled for pins, so the 32 mm system does not apply.

**The 32 mm system.** 5 mm holes, 32 mm apart, the front column 37 mm from the front edge, holes 12 to
14 mm deep in 18 mm board: [Wikipedia, 32 mm cabinetmaking system](https://en.wikipedia.org/wiki/32_mm_cabinetmaking_system),
[Shaper, System 32 walkthrough](https://support.shapertools.com/hc/en-us/articles/8900620036379),
[Kreg shelf pin jig 5 mm (32 mm spacing, 37 mm from the edge)](https://sautershop.com/kreg-shelf-pin-jig-5mm-kr-kma3232-int).

**Checked.** `check-range --deep` passes at the default, 64 corners, every choice and random points
(99 points with seed 1, 147 with 64 samples and seed 7); regeneration median about 60 ms, at most about
130 ms. An assertion holds at every point: no two parts overlap.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
