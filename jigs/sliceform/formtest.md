# Form test: sliceform

"I would like a ball-shaped sculpture for our sideboard, 30 cm across, as near to a whole ball as it can be
while still standing on a small flat bit at the bottom. I cut on a CO2 laser with a 600 × 400 mm bed; a test
cut tells me its beam burns away about 0.12 mm. I have birch plywood that measures 3.8 mm with my calipers and
walnut-faced plywood that measures 4.1 mm. We move house often, so it has to come apart again: the slots
should slide together by hand, not need a mallet. As many slices each way as the wood allows. What do I send to
the laser, how many pieces are there and what will it weigh? And could it have twelve slices each way?"

## Acceptance

- Ball, 300 mm wide and 260 mm high (the most the form allows at that width and with these sheets: every slice
  still stands on the flat foot), with 11 birch and 11 walnut slices: 22 slices to cut, 121 crossings.
- Slots drawn 4.18 mm wide in the birch slices and 3.88 mm in the walnut slices (each sheet of the other wood
  + 0.2 mm of play − the 0.12 mm kerf); the narrowest finger as cut is about 14.9 mm; mass about 3.0 kg (2 991 g).
- Two files, one per wood (the sets *Cut sheet, birch* and *Cut sheet, walnut*, SVG or DXF): 11 closed outlines
  each, one layer per slice in the DXF (Birch slice 1 to 11, Walnut slice 1 to 11), every slice at most 300 mm wide and
  260 mm high, so each fits the 600 × 400 mm bed. The birch slices are slotted from their top edge, the walnut
  slices from their foot.
- All assertions pass.
- Refusal: twelve slices each way cannot be set: the form stops both counts at 11 for this ball and these
  sheets (`param.set` refuses 12 with that range).
