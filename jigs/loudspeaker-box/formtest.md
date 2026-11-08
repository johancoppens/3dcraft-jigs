# Form test

I have bought a 6.5 inch woofer and I want to build a vented bookshelf speaker for it, with bass that rolls off smoothly rather than
booming. The data sheet says: free-air resonance 36 Hz, total Q 0.37, equivalent volume 30 litres, cone area 135 square centimetres,
6 mm of linear excursion one way. The hole it needs in the baffle is 146 mm, its frame is 172 mm across, and it is 90 mm deep from the
front of the frame to the back of the magnet. I will cut the cabinet from 18 mm MDF on my CNC router and I want finger joints. How big is
the box, how big and how long is the port, how low does it go, and can I have the file for the router?

I also have an old woofer with a total Q of 0.62. Can that go in a vented box?

## Acceptance

- A vented QB3 alignment with bookshelf proportions, finger joints (snug fit), 18 mm board.
- Net air target 20.13 L, and the measured net air within 0.25 % of it (20.13 L at the time of writing).
- Tuning 39.0 Hz; f3 41.9 Hz.
- Port bore 39 mm, 96.9 mm from the mouth to the inner end; air speed at Xmax 16.6 m/s, no more than 17.
- Cabinet about 272 x 367 x 296 mm outside. Six boards to cut (no brace at this size); mass of the six boards about 6.3 kg.
- `file.export` of the set *Cut sheet* writes an SVG or DXF with one through-cut outline for each of the six boards, each on its own
  layer, with the cutout, the port bore and the terminal hole in it and the dog-bones in the finger corners; the set *Rebate and mouth pockets* holds
  the two pocket floors. All assertions that apply pass.
- Refusal: a total Q of 0.62 is refused for every vented alignment (the Qts range ends at 0.40 for this alignment and at 0.42 at most), with the range in the message.
