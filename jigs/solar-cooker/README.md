# Parabolic solar cooker

A parabolic solar cooker whose dish is made of **flat petals (gores)** cut from thin aluminium,
polypropylene or cardboard sheet, covered with reflective foil and riveted to a steel **rim hoop**. Bent and
joined edge to tab, the petals approximate the paraboloid z = r² / 4f. The dish hangs on a **horizontal tilt
axis through the focus**, in a fork on a base that turns on a disc (azimuth), so it can face the sun while
the **pot stays level at the focus**: the pot stands on a ring that hangs from the fork's crossbar, not from
the dish (the layout of the KSOL-type cookers). The flat petals lie beside it, nested end for end.
Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Dish diameter | Dish | 1000 mm | 3.2 × (pot + 30 mm) to min(1600 mm, 7 × pot), step 10 mm |
| Focal ratio f/D | Dish | 0.3 | 0.25 to 0.4, step 0.01 |
| Petals | Dish | 20 | max(8, ⌈π D / pot⌉) to 28 (whole) |
| Sheet thickness | Dish | 2 mm | 0.5 to 4 mm, step 0.1 mm |
| Glue tab | Dish | 15 mm | 8 to 25 mm, step 1 mm |
| Pot | Pot and stand | Pot 20 cm | table `pots` (below) |
| Sun elevation | Pot and stand | 50° | 20° to 90°, step 1° |
| Ground clearance | Pot and stand | 150 mm | 100 to 500 mm, step 10 mm |

**Pots** (table `pots`): Pot 16 cm (Ø 160 × 110 mm), Pot 20 cm (Ø 200 × 130 mm), Pot 24 cm (Ø 240 × 150 mm),
Kettle (Ø 170 × 200 mm). Add a row to `pots` for your own pot.

**Sheet.** 0.5 to 1 mm aluminium (laser, plotter knife or shears), 0.8 to 1.5 mm polypropylene, or 2 to 4 mm
corrugated cardboard (knife), each with aluminised mylar or kitchen foil glued on the side that faces the sun.

## The geometry

The dish is built in its own frame (vertex at the origin, focus at (0, 0, f)), then turned about the tilt
axis by 90° − sun elevation towards +x and lifted so the focus is at (0, 0, zF). All of it is formulas of the
document's variables:

```text
f      = fD x D                       focal length
depth  = D^2 / (16 f)                 depth of the dish at the rim (208 mm for the defaults)
r0     = max(D / 20, N x 20 mm / 2 pi)   radius of the central hole: every petal at least 20 mm wide there
s(r)   = (r/2) sqrt(1 + (r/2f)^2) + f asinh(r/2f)       arc length along a meridian, from the vertex
L      = s(R) - s(r0)                 length of a flat petal (489 mm for the defaults), R = D / 2
w(r)   = 2 pi r / N                   width of a petal at arc length s(r): the circle of radius r shared by N
rim angle = 2 atan(1 / (4 fD))        80 deg for f/D 0.3; 90 deg at f/D 0.25 (focus in the rim plane)
rhoMax = sqrt(Rh^2 + (f - depth + hoopH)^2)   farthest the reflector (hoop) reaches from the tilt axis
zF     = base + ground clearance + rhoMax     height of the focus and the tilt axis (728 mm for the defaults)
```

s(r) is the closed form of ∫₀ʳ √(1 + (u / 2f)²) du, the arc length of the parabola z = u² / 4f. The petal's
two long edges are drawn with `sketch.curve` as the curves (s(t), ±π t / N) for t from r0 to R (asinh
written as ln(u + √(1 + u²))), exact to the document's tolerance (0.01 mm, `new.json`). Along one edge sit
five trapezoid tabs (the radius split into eleven equal steps, tabs on every other one), `Glue tab` wide:
glue or rivet them under the next petal. A 4 mm hole marks the narrow end (the hole end) and takes the rivet
to the centre flange.

**Petals approximate the dish.** A flat petal bends one way only (along its length), so across its width it
stays straight where the paraboloid curves: at its edges it stands off the true surface by about
κ w² / 2 (κ the curvature across the petal, w its half-width). For a 1 m dish that is 20 to 27 mm with 8
petals, 9 to 12 mm with 12, 5 to 7 mm with 16 and 2 to 3 mm with 24 (f/D 0.4 to 0.25); it falls with 1/N².
The other consequence is that a flat strip focuses into a **line as wide as itself**, not a point: a ray that
hits a petal at a distance v from its centre line passes the axis at about v. So no petal may be wider than
the pot: **N ≥ π D / pot**, which is the minimum of the Petals parameter (and why the dish is at most 7 × the
pot across: 22 petals then). The default, 20 petals on a 1 m dish, suits every pot of the table. With the petals no wider than the pot every ray a petal sends lands on the pot;
with 8 petals on a 1 m dish and a 20 cm pot only some 76 % would.

**f/D.** Anything from 0.25 to 0.4 cooks: a deep dish (0.25, rim angle 90°) puts the pot inside the rim and
out of the wind, a shallow one (0.4) is easier to build and to reach into. The gore approximation, not f/D,
is what limits the focus: the sun's image is only about 5 mm across near the vertex (0.53° × f, Duffie &
Beckman), but a 1° slope error moves a ray from the rim some 18 mm. The geometric concentration ratio is
(D / pot)², 25 for the defaults.

**Mechanism.** The rim hoop (25 × 4 mm flat bar, rolled to Ø D + 10 mm) carries the petals' rims and two
pivot brackets that reach up to the tilt axis; their pins turn in the fork's uprights. The axis runs through
the focus, so turning the dish does not move the focus, and the pot ring hangs from the crossbar above the
pot: everything fixed stays above the dish's focal plane or within f of the focus, where the turning dish
never reaches. The fork stands on two beams that turn on a disc to follow the sun round (azimuth). A centre
flange (an aluminium ring under the petals' narrow ends) closes the hole and holds the petals' ends. In the 3D
model the dish is drawn as the true paraboloid, split into N sectors of 360° / N, aluminium and cream in turn
so the seams show (with an odd N, two aluminium petals meet at one seam): every other sector is cut out by a
wedge, which regenerates far faster than a pattern of N freeform sectors.

## What it proves (assertions)

| Assertion | Rule |
|---|---|
| focus in pot (x, y, z low and high) | The focus (0, 0, zF) lies in the pot's box, both bounds on each axis. The pot stands on the ring with its bottom a quarter of its height below the focus |
| pot level | The pot's box is exactly as tall as the pot and its lid: it stands upright at every sun elevation |
| ring shades at most 10 % | The pot ring (pot + 30 mm across) is at most √0.1 × D across, so it shades at most 10 % of the aperture. The dish diameter's minimum, 3.2 × (pot + 30 mm), keeps it so |
| petal length is the arc length | The flat petal's length equals the parabola's arc length from the hole to the rim, checked against **Simpson's rule** (16 panels) on √(1 + (r / 2f)²), independent of the closed form the outline is drawn with (within 0.05 mm) |
| petals cover the full circle | The N sectors of 360° / N together have the volume of the whole shell, π × thick × (R² − r0²): N × angle = 360° |
| dish depth | The dish is D² / (16 f) deep: turned by the tilt about the focus, its highest point is at zF + R sin(tilt) + (D² / 16f + thick − f) cos(tilt) |
| reflector clear of frame and pot | The turning parts (dish, hoop, brackets, pins, flange) do not overlap the fork, the base, the pot ring or the pot |
| reflector above the base | The dish stays above the base |
| nested petals clear | The turned petals stay at least 5 mm from the others on the ground |

The collision assertions hold at the elevation set; `check-range` sweeps the elevation with the other
parameters (corners at 20° and 90° and random points between).

**Checked.** `check-range` passes 84 of 84 points (the default, 64 corners, every pot and 16 random
points, elevation from 20° to 90° among them), also with `--deep`; regeneration median about 1.3 s, at most
about 2.5 s. Overlap
between the nested flat petals cannot be measured by 3DCraft 0.1.0 (too many freeform faces for one
boolean), so their spacing is checked with `clearance`.

## Using it

**Cut sheets.** Export with **File › Export…** as DXF or SVG:

- set **Cut sheet: petals**: N petals, each L long (489 mm for the defaults) and 2π R / N + tab wide at the rim
  (157 + 15 mm for the defaults);
- set **Steel parts**: the flat pot ring (pot + 30 mm outside, pot − 40 mm inside, 4 mm plate).

The export lays the faces out side by side in one row; set a **sheet width** (`width` in `file.export`, the
width of your sheet or laser bed) to have them wrapped into rows. On the sheet itself, nest the petals end for
end as the model shows them on the ground: it saves about 40 % of the material.

**Not on the sheets:** the rim hoop (25 × 4 mm steel or aluminium flat bar, π (D + 6 mm) long, rolled and
riveted to every petal's rim), the two pivot brackets, the fork (30 mm square tube), the base beams and the
turning disc: cut them to the model's sizes (`document.inspect` gives every body's box).

**Building.** Lay the petals foil down, rivet or glue each one's tabs under the next one's plain edge
starting from the flange, then rivet the rims to the hoop. Hang the dish in the fork on its pins. To cook,
turn the base to face the sun and tilt the dish until the light on the pot is brightest (the pot's shadow
falls on the dish's centre); follow the sun every 15 to 20 minutes. A black, thin-walled pot with a lid
cooks fastest.

## Safety

- **Never look into the focus** or into the dish while it faces the sun; wear sunglasses when you set it up
  and adjust it.
- **The focus is very hot**: it scorches wood and paper and burns skin in seconds. Use oven gloves on the pot.
- **Never leave the dish facing the sun without a pot at the focus**: the bare focus can set paint, a cloth
  or dry grass on fire. Turn it away from the sun (or cover it) before you take the pot off.
- **Fasten it against the wind**: a 1 m dish is a sail. Weigh the base down or peg it to the ground.
- **Cover the dish when you move or store it**, and never leave it facing the sun unattended near children,
  pets or anything that burns.

## Sources

- Solar Cookers International and the Solar Cookers World Network wiki (solarcooking.fandom.com),
  *Parabolic solar cookers* and the *KSOL-14* page: parabolic cookers, petal-built dishes, a pot holder fixed
  to the frame while the reflector turns, use and safety.
- J. A. Duffie and W. A. Beckman, *Solar Engineering of Thermal Processes*, 4th ed., Wiley 2013, chapter 7
  (concentrating collectors): the paraboloid, its rim angle, the sun's image and the concentration ratio.
- W. B. Stine and M. Geyer, *Power From the Sun*, 2001 (powerfromthesun.net), chapter 8: the parabolic
  dish, f/D = 1 / (4 tan(ψ_rim / 2)), and the effect of slope errors.
- The arc length of a parabola and the gore (segment) of a surface of revolution: any calculus text
  (e.g. J. Stewart, *Calculus*, arc length), Wikipedia *Parabola* (arc length) and *Gore (segment)*.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.

**Colours.** Aluminium (#B9BEC4) and cream (#E8DFCC) petals, an aluminium flange, a steel (#7D858C) hoop,
fork, base and pot ring, a walnut (#7A5638) pot, from the Jigs palette.
