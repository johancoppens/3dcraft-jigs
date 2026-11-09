# Form test

I weld small steel frames in my workshop and want to make my own fixture table. My clamps and stops have 16 mm pins for
holes on a 50 mm grid. The table should be 1500 mm long and 1000 mm wide, with the working surface at 900 mm, on legs
joined by rails near the floor so I can get a pallet truck under it. I will have the plates cut by a laser service; their
kerf is 0.4 mm. I do not expect to put more than 300 kg in the middle of it. I want the plates held by short weld tabs, about
a quarter of each edge welded and the rest plain contact, with the tab ends a couple of millimetres below the face so nothing
sticks out. What will it weigh, how far will it sag, how much welding is that, and what do I send to the cutter?

## Acceptance

- 16 mm holes on a 50 mm grid: 600 holes in the top (30 × 20) and 200 in the side plates. Top plate 12 mm, sides 100 mm
  deep. Ribs: 5 across and 3 along, of the same 12 mm plate.
- Mass measured on the model 321 kg (±3 kg), with 300 kg on it 1.52 kN per leg, well inside the leg capacity shown
  (9.8 kN, the rating of 1000 kg per leg, an estimate for an engineer to check).
- Sag at the centre under the 300 kg and the table's own weight: 0.11 mm long way (limit 0.15 mm); the form allows at most 410 kg at
  this size. Sideways sway under a 1 kN push about 0.125 mm; about 1700 N at the working height tips it. All these are shown as estimates; the form does not claim more.
- Tabs 25 mm every 100 mm: 25 % of each edge is weld, the form shows it, and 3.25 m of weld at the tabs in all (plate edges,
  rib tabs). Tab ends 2 mm below the outer faces (the form shows the setting; the assertions measure it). The rails stand
  180 mm above the floor: a pallet truck (forks 85 mm when lowered) can get under them.
- All assertions pass (44 of 44).
- Export: the set *Plates to cut* as DXF holds every plate true size, a layer per part kind: the top, four side plates,
  three ribs along, five ribs across and four foot plates: 17 plates in all, one outline each, with every notch and slot
  and its round reliefs. A STEP of the whole table is written.
- Refusals: a 2 000 mm length on this grid cannot be set (at most 1 800 mm here); a design load of 450 kg cannot be set
  at this size (at most 410 kg); a table narrower than 450 mm cannot be set at this working height; a tab longer than 35 mm or a recess under 0.4 mm cannot be set on this grid.
