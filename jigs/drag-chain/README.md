# Cable drag chain

A cable drag chain (energy chain) for a 3D printer or a CNC machine, to print. The links have snap-in
hinge pins and clip-on top bridges, so cables can be laid in after the chain is assembled. Licence:
CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Inner width | Link | 15 mm | 6 to 60 mm, step 0.5 mm |
| Inner height | Link | 10 mm | 5 to 40 mm, step 0.5 mm |
| Link pitch | Link | 22 mm | 1.4 to 3 × the link's outer height, step 0.5 mm |
| Chain length | Chain | 500 mm | (links in the bend + 2) × pitch to 1200 mm, step 1 mm |
| Bend radius | Chain | 45 mm | pitch to min(8 × pitch, (1200 mm − 2.5 × pitch) / π), step 1 mm |
| Layout | Chain | bent (U) | bent (U), straight |

**How it is built.** One link: two side walls, each of an outer half (wall thickness 0.12 × inner height
+ 1 mm, 1.6 to 3 mm) and an inner half stepped in by the wall thickness and a 0.3 mm gap, joined by a
web under the bridges. Both halves end in a half disc about their hinge, so a link turns freely on the
next one. The inner half carries the snap pin (radius 0.22 × the outer height, its tip chamfered as a
lead-in), which turns in a hole 0.15 mm larger in the outer half of the link before it. A bottom bridge
joins the walls; the top bridge (rounded on top, ochre) is a separate part that clips on: the opening
bridge, lifted off to lay cables in. The outer height is the inner height + 2 × the wall thickness, the
outer width the inner width + 4 walls + 2 gaps.

**The chain.** The number of links is the length / pitch, rounded. Bent, it runs as on a machine: a
lower run, a half turn of round(π × radius / pitch) links (at least 2; each turned by 180° / that number
about the bend's centre: a circular pattern, with the hinges on a circle of radius pitch / (2 sin(turn /
2)), close to the bend radius) and an upper run back above it, upside down. The links in the bend turn
at most 90° against each other, well inside what the walls allow (about 94° at the smallest pitch).

**Checked.** Three assertions hold at every point: the volume of all links is exactly the number of
links times the closed-form volume of one (half walls, web, pin with its chamfer, hole, bottom bridge),
the same for the top bridges, and no two bodies overlap; so no link touches or passes into another, in
the runs or in the bend. `check-range --deep` passes at the default, all 64 corners, both layouts and
random points (82 points with seed 1, 130 with 64 samples and seed 7); regeneration median about 350 ms,
at most about 2 s (a 1200 mm chain of small links).

**Printing.** Export STL or 3MF (File › Export…, or `"bodies": ["LinksLow"]` for one run). Print the
links on their side and the bridges flat; tune the pin's fit with the pitch and the inner height only if
your printer is loose or tight (the 0.15 mm clearance is fixed). Not modelled: end brackets to mount the
chain, and end stops that limit the bend (the bend radius of the layout is what you set).

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
