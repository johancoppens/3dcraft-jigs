# Parabolic solar cooker

A parabolic solar cooker whose dish is made of **flat petals (gores)** cut from cardboard, thin aluminium or
polypropylene sheet and covered with reflective foil: bent and joined edge to tab, they make the paraboloid
z = r² / 4f. A flat ring on three steel legs from the rim holds the pot at the focus; a post on three feet
carries the dish. The flat petals lie beside it, nested end for end: they and the ring are the cut sheet.
Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Dish diameter | Dish | 1000 mm | 3.2 × (pot + 30 mm) to 1600 mm, step 10 mm |
| Focal ratio f/D | Dish | 0.3 | 0.25 to 0.4, step 0.01 |
| Petals | Dish | 12 | 8 to 24 (whole) |
| Sheet thickness | Dish | 2 mm | 0.5 to 4 mm, step 0.1 mm |
| Glue tab | Dish | 15 mm | 8 to 25 mm, step 1 mm |
| Pot | Pot and stand | Pot 20 cm | table `pots` (below) |
| Stand height | Pot and stand | 600 mm | 300 to 1000 mm, step 10 mm |

**Pots** (table `pots`): Pot 16 cm (Ø 160 × 110 mm), Pot 20 cm (Ø 200 × 130 mm), Pot 24 cm (Ø 240 × 150 mm),
Kettle (Ø 170 × 200 mm). Add a row to `pots` for your own pot.

## The geometry

The origin is the dish's vertex, z up, so the focus is the point (0, 0, f) with f = f/D × D. All of it is
formulas of the document's variables:

```text
f      = fD x D                       focal length
depth  = D^2 / (16 f)                 depth of the dish at the rim (208 mm for the defaults)
r0     = D / 20                       radius of the central hole
s(r)   = (r/2) sqrt(1 + (r/2f)^2) + f asinh(r/2f)       arc length along a meridian, from the vertex
L      = s(R) - s(r0)                 length of a flat petal (503 mm for the defaults), R = D / 2
w(r)   = 2 pi r / N                   width of a petal at arc length s(r): the circle of radius r shared by N
rim angle = 2 atan(1 / (4 fD))        80 deg for f/D 0.3; 90 deg at f/D 0.25 (focus in the rim plane)
```

s(r) is the closed form of ∫₀ʳ √(1 + (u / 2f)²) du, the arc length of the parabola z = u² / 4f. The petal's
two long edges are drawn with `sketch.curve` as the curves (s(t), ±π t / N) for t from r0 to R (asinh
written as ln(u + √(1 + u²))), so the outline is exact to the document's tolerance (0.01 mm, `new.json`, far below what a knife or laser cuts). Along
one edge sit five trapezoid tabs (the radius split into eleven equal steps, tabs on every other one),
`Glue tab` wide: glue them under the next petal, or rivet them.

A flat gore is the standard approximation of a doubly curved surface by strips that bend one way only: the
narrower the petals (more of them), the closer the bent dish comes to the paraboloid. 12 to 16 petals are
usual for a 1 m dish; a stiff sheet wants more.

In 3D, the dish is drawn as N sectors of 360° / N of the true paraboloid (a revolve of the parabola, sheet
thickness thick), coloured alternately aluminium and cream so the seams show (with an odd N, two aluminium petals meet at
one seam). The flat petals are nested
end for end, every other one turned 180°: two petals side by side are at most
M = (2π / N) (R − L / (2 √(1 + (R / 2f)²))) wide together at any station (the half-widths are π r / N, r is
concave in s, and the tangent of s(r) at the rim bounds the middle radius), so they lie M + 2 tabs + 10 mm
apart.

## What it proves (assertions)

| Assertion | Rule |
|---|---|
| focus in pot (z low, z high, x, y) | The focus (0, 0, f) lies in the pot's box: `boxMin` z ≤ f ≤ `boxMax` z, and the box spans x = 0 and y = 0. The pot stands on the ring with its bottom a quarter of its height below the focus |
| pot shades at most 10 % | The pot's diameter is at most √0.1 × D, so it shades at most 10 % of the aperture. The dish diameter's minimum, 3.2 × (pot + 30 mm), keeps the pot and its ring under that |
| petal length is the arc length | The flat petal's length equals the parabola's arc length from the hole to the rim, checked against **Simpson's rule** (16 panels) on √(1 + (r / 2f)²), independent of the closed form the outline is drawn with (within 0.05 mm) |
| petals cover the full circle | The N sectors of 360° / N together have the volume of the whole shell, π × thick × (R² − r0²): N × angle = 360° |
| dish depth | The rim is D² / (16 f) above the vertex (plus the sheet) |
| holder clear of dish, pot clear of dish | The legs and the pot do not touch the dish |
| nested petals clear | The turned petals stay at least 5 mm from the others on the sheet |

`check-range` passes at the defaults, the corners and random points, also with `--deep` (see the commit
message for the run).

## Using it

Export the cut sheet with **File › Export…** (DXF or SVG, set **Cut sheet**): every petal and the ring,
laid out flat. Cut the petals from 2 to 3 mm corrugated cardboard (a knife or a plotter), 0.5 to 1 mm
aluminium or polypropylene sheet (a laser or shears), glue reflective foil (aluminised mylar, or kitchen foil
on cardboard) on the side that faces the sun, and join each petal's tabs under the next one's plain edge,
starting at the hole. The ring and legs are steel: bend the three legs from 10 mm rod and weld or bolt them
to the ring; clamp their other ends to the rim. A black, thin-walled pot with a lid cooks fastest.

The model shows the dish pointing straight up. In use, tilt it towards the sun (the stand is a sketch of
the simplest one) and turn it every 15 to 20 minutes; the pot stays at the focus because it hangs from the
rim.

## Safety

- **Never look into the focus** or into the dish while it faces the sun; wear sunglasses when you set it
  up and adjust it.
- **The focus is very hot**: it scorches wood and paper and burns skin in seconds. Use oven gloves on the
  pot, and turn the dish away from the sun (or cover it) before you reach in.
- Never leave it facing the sun unattended near children, pets or anything that burns; cover it when it is
  not in use.

## Sources

- Solar Cookers International, *Solar Cooker designs* and the Solar Cookers World Network wiki
  (solarcooking.fandom.com), *Parabolic solar cookers*: parabolic cookers, gore-built dishes, use and safety.
- J. A. Duffie and W. A. Beckman, *Solar Engineering of Thermal Processes*, 4th ed., Wiley 2013, chapter 7
  (concentrating collectors): the paraboloid, its rim angle and concentration ratio.
- W. B. Stine and M. Geyer, *Power From the Sun*, 2001 (powerfromthesun.net), chapter 8: the parabolic
  dish, f/D = 1 / (4 tan(ψ_rim / 2)).
- The arc length of a parabola and the gore (segment) of a surface of revolution: any calculus text
  (e.g. J. Stewart, *Calculus*, arc length), Wikipedia *Parabola* (arc length) and *Gore (segment)*.

`build.json` was written by `python3 gen.py > build.json`; edit `gen.py` and run it again to change the
model.

**Colours.** Aluminium (#B9BEC4) and cream (#E8DFCC) petals, a steel (#7D858C) holder and stand, a walnut
(#7A5638) pot, from the Jigs palette.
