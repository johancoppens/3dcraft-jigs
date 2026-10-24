# Print-in-place hinge

A hinge that prints in one go and turns as soon as it comes off the bed: two leaves whose knuckles
interlock on conical pins, the clearance apart everywhere. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Length | Size | 60 mm | 40 to 200 mm, step 1 mm |
| Leaf width | Size | 22 mm | knuckle diameter / 2 + clearance + 2 × screw diameter + 4 mm to 80 mm |
| Leaf thickness | Size | 2.5 mm | 1.5 mm to knuckle diameter / 2 − 0.5 mm, step 0.1 mm |
| Knuckle diameter | Knuckles | 8 mm | 6 to 16 mm, step 0.5 mm |
| Knuckles | Knuckles | 5 | 2 to floor((length + clearance) / (pin diameter + clearance + 3 mm)) |
| Pin diameter | Knuckles | 4 mm | 2 mm to min(knuckle diameter − 3 mm, 8 mm), step 0.1 mm |
| Clearance | Knuckles | 0.3 mm | 0.15 to 0.8 mm, step 0.05 mm |
| Screw holes | Screws | 2 | 1 to 6 per leaf |
| Screw diameter | Screws | 3.5 mm | 2 to 5 mm, step 0.1 mm |

**How it works.** The hinge lies flat, its axis along x. Leaf A (terracotta) has the first, third, ...
knuckle, leaf B (sage) the others; knuckles are (length − (knuckles − 1) × clearance) / knuckles long, a
clearance apart. Where two knuckles meet, A's knuckle carries a 45° cone (the pin, base diameter *pin
diameter*) that sits in a conical socket in B's knuckle. The socket is the pin's cone moved out by the
clearance (along the axis by clearance × √2, so the gap square to the cone is the clearance), and each leaf
is cut clear of the other leaf's knuckles by a cylinder of knuckle radius + clearance. So every gap between
the two parts, round the knuckles, between their ends and over the pins, is the clearance (measured with
`measure.clearance`: 0.3 mm at the default, 0.15 and 0.8 mm at the ends of its range).

**Printing without supports.** A horizontal round pin in a hole has a flat roof that has to bridge; a 45°
cone does not: the socket's roof and the pin's underside are 45° overhangs, which print cleanly. The axis
is 0.3 mm lower than the knuckle radius, so the knuckles stand on the bed on a 0.3 mm flat. The leaf
thickness is at most the axis height, so the hinge folds flat onto itself (180°). The screw holes have a 90°
countersink on top, up to 0.6 × the leaf thickness deep.

**Tuning.** 0.3 mm clearance suits most FDM printers with a 0.4 mm nozzle; go to 0.2 mm for a stiffer
hinge on a well-tuned printer, 0.4 mm or more if it fuses. Free it after printing by flexing it gently
both ways.

**How it is built.** Blocks for the leaves and cylinders for the knuckles (each a little longer than it
ends up), patterns along the axis whose counts follow the knuckle count, the clearance zones cut from each
leaf, cones for the pins and sockets (`feature.when` switches the pins pointing back off for two
knuckles), countersunk holes (a cylinder and a cone), and at the end both parts intersected with one
outline (the rounded corners, the ends and the bed). Assertions: two bodies, and they do not interfere.

**Checked.** `check-range --deep` passes at the default, 64 corners and random points (81 points with seed 1,
129 with seed 7); regeneration median about 120 ms, at most about 1.2 s. Section renders at both ends of the
range show the pins centred in their sockets.

**Sources.** The conical-pin print-in-place hinge is a common 3D printing technique; this model is designed
from scratch for 3DCraft.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.
