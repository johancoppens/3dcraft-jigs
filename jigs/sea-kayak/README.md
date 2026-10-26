# Sea kayak (stitch and glue)

A Greenland-style **multichine sea kayak in okoume plywood**, built stitch and glue: two to four hull panels a
side, a two-panel deck with a keyhole cockpit, a laminated coaming, sheer clamps, fore and aft bulkheads with
round hatches, and hardwood tips. Every hull panel is an **exactly developable surface** whose flat outline is
computed from the hull's own formulas and laid out on the floor beside the boat in three pieces joined by
staggered puzzle joints (a kayak panel is longer than a 2440 mm sheet), with its stitch holes, ready to cut. The **hydrostatics** follow
the paddler, the load and the lines: the design waterline, the trim (where the seat goes so the boat floats
level), the initial stability (GM), the prismatic coefficient, the wetted surface and the displacement-length
ratio, and each is checked against the exact geometry by 3DCraft's kernel. Licence: CC-BY-4.0.

**Lines.** The character is that of the Greenland kayak Emanuele Korneliussen built at Igdlorssuit for Ken
Taylor in 1959, surveyed by Duncan Winning in 1964, the boat that led to Geoff Blackford's plywood Anas Acuta
and Valley's production Anas Acuta (1972) and through them to most British sea kayaks: about 5.2 m long,
0.53 m wide, low volume, strong rocker, raised pointed ends. The plans of the Igdlorssuit kayak published by
PaddlingLight carry no licence that allows reuse of the offsets, so **these lines are our own**, a parametric
family *inspired by* that boat, not a copy of it. Its published hydrostatics (displacement 88 kg, Cp 0.524,
LWL 4.00 m, BWL 0.48 m, draft 0.122 m, wetted surface 1.57 m², transverse KM 0.27 m) are a fair yardstick for
the numbers below.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Length overall | Hull | 5300 mm | 5000 to 5800 mm |
| Beam | Hull | 545 mm | 530 to 600 mm at the sheer; at least 570 mm with one chine |
| Depth at the sheer | Hull | 190 mm | 170 mm to min(230 mm, 0.36 × beam), keel to sheer at the widest station |
| Deck crown | Hull | 22° | 12 to 26° |
| Bow rise, Stern rise | Hull | 300, 240 mm | 250 to 400, 220 to 350 mm: the keel's rise to each tip (rocker) |
| Widest station | Hull | 0.47 | 0.44 to 0.52 of the length from the stern |
| Chines per side | Hull | 3 | 1 to 3 (2 to 4 hull panels a side) |
| Ends | Hull | Moderate | Fine, Moderate, Full (table `forms`) |
| Paddler weight (kg) | Paddler and load | 80 | 45 to **the hull's capacity** (below), at most 110 |
| Paddler height | Paddler and load | 1780 mm | 1500 to 2000 mm |
| Load (kg) | Paddler and load | 5 | 0 to 40 (less when the hull cannot carry it with a 45 kg paddler), half in each compartment |
| Water | Paddler and load | Sea water | Sea water (1025 kg/m³) or fresh water (1000 kg/m³) |
| Hull plywood | Plywood | 4 mm | 3 to 5 mm |
| Deck plywood | Plywood | 3 mm | 3 to 4 mm |
| Cockpit length | Cockpit and hatches | 800 mm | 0.34 × height + 100 mm to min(950 mm, 0.57 × height − 40 mm) |
| Cockpit width | Cockpit and hatches | 420 mm | 380 to 460 mm |
| Bulkheads and hatches | Cockpit and hatches | on | off: an open hull for float bags |

## The hull: developable panels by construction

`x` runs along the boat (stern −L/2, bow +L/2), `y` to starboard, `z` up from the keel's lowest point. A
station is given by η from 0 (stern tip) to 1 (bow tip), a skewed copy of ξ = x/L + ½ (η = ξ + s ξ(1 − ξ)) so
that the widest station, η = ½, lies at the chosen fraction of the length.

**Every hull panel is a generalised cylinder.** In each station a panel is a straight line at the same angle
θⱼ (its flare) all along the boat; only its width Wⱼ·Fⱼ(η) and its position change. Such a surface is ruled by
parallel lines, so its Gaussian curvature is zero: it is **developable**, and a flat sheet of plywood bends
onto it without stretching (do Carmo, §3-5). Its development is known in closed form up to one arc-length
integral: with dⱼ = (cos θⱼ, sin θⱼ) in the station plane and nⱼ its normal, a point P(x) of the panel's lower
edge goes to

```text
flat X = ∫ sqrt(1 + g'(x)²) dx,   g = P(x) · nⱼ   (the panel's offset along its normal)
flat Y = P(x) · dⱼ                (and + the panel's width for its upper edge)
```

because the surface is the curve g(x) (in the plane of x and nⱼ) swept along dⱼ. A panel's two flat edges are
therefore exactly as long as the two chines it is stitched to, and every ruling (a station line) keeps its
length: the conditions for the cut panels to close up into the hull.

The widths: at the widest station the chines lie on a quarter ellipse with semi-axes B/2 and D, equally spaced
in angle, which sets each panel's angle and width Wⱼ. Along the boat the width is Wⱼ·Gᵖʲ·(1 + σⱼ(1 − G)) with
G = 4η(1 − η): the bottom panels (large pⱼ, from the table `forms`) taper out first, so the ends become a
fine V, and a sheer spring σⱼ (0 at the bottom, 0.8 at the topside) keeps the upper panels wide towards the
ends so the sheer sweeps up. The keel rises to the tips as z₀ = rA u⁴ + rC u⁵ (u = 2η − 1), with the bow and
stern rises as its ends. The deck is one panel a side at the crown angle, a cylinder too, from the sheer to a
ridge on the centre line. The plywood hull runs from η = 0.03 to 0.97; the last 150 mm or so at each end, where
the panels are a few millimetres wide, is a hardwood tip (as Greenland kayaks have bone or wood tips), which
also stands for the end pour of thickened epoxy a stitch-and-glue builder puts there.

**In 3DCraft.** The 25 stations are Chebyshev (cosine-spaced) points in η, dense at the ends where the hull
turns fastest. The **hull envelope** (outside of the planking, closed by the deck) is a loft through the 25
station polygons; each **panel** is a thin loft of its own (4 mm inward, along the true surface normal); the
port side is the starboard mirrored. Because a loft through straight station lines at a constant angle is
itself exactly a cylinder, the panels in the model are developable whatever the interpolation between
stations.

## Hydrostatics and trim

All hydrostatic integrals are **Clenshaw–Curtis quadratures** (Clenshaw & Curtis 1960) of closed-form section
quantities, over a finer grid of 49 cosine-spaced stations of their own (the integrands have kinks where the
waterline crosses a chine and at its ends; the panels' areas and lengths, which are smooth, use the 25 loft
stations): for a convex polygon whose sides keep their angles, the half-area,
half-breadth, vertical moment and wetted girth below a waterline z = T are sums of clamped polynomials in
T − zⱼ. From them:

- **Waterline.** The displaced volume ∇(T) must equal (paddler + boat + load) / ρ. ∇ grows with T and its
  derivative is the waterplane area, so four **Newton steps** T ← T − (∇(T) − ∇ₜ)/A_wp(T) from 0.8 D find the
  design draft (it has converged to 1e-9 mm after three).
- **Boat weight.** Panel areas (∫ wⱼ·sqrt(1 + g'²) dx, the same integral as the development) × thickness ×
  500 kg/m³ okoume (CLC sells a 4 mm 4 × 8 ft sheet at 13 lb, 497 kg/m³), sheer clamps, bulkheads and coaming
  in hardwood (600 kg/m³), glass and epoxy at 0.80 kg/m² on the hull (6 oz cloth with its wet-out and fill
  coats, an inside coat, seam tape) and 0.55 kg/m² on the deck (4 oz), and 2.5 kg of fittings (seat pad, back
  band, hatch rims and covers, deck lines).
- **Trim.** The seat is placed so the centre of gravity lies over the centre of buoyancy: the paddler's CG
  is taken 10 in (254 mm) above the seat and 10 in ahead of the seat back (the convention of *Sea Kayaker*
  magazine's stability reviews), the seat a 25 mm pad on the floor, the load half in each compartment 0.6 m beyond its bulkhead,
  the coaming, bulkheads and fittings with the cockpit. The seat back's position is the one linear equation
  Δ·LCB = Σ mᵢ xᵢ.
- **Stability.** KB from the vertical moment, BM = I_T/∇ with I_T = ⅔ ∫ b³ dx the waterplane's transverse
  second moment, KG from the same weights, GM = KB + BM − KG (Biran & López-Pulido, ch. 2–3).
- **Coefficients.** Prismatic Cp = ∇/(A_max·LWL), waterplane Cwp = A_wp/(LWL·BWL), block Cb, wetted surface
  and the displacement-length ratio (Δ in long tons)/(0.01·LWL in ft)³; LWL from where the keel curve crosses
  T (Newton again).

**Capacity.** The paddler weight's maximum is the heaviest paddler this hull carries with (a) the lowest point
of the sheer 45 mm above the water (the deck edge stays dry at rest; 5 mm more than asserted) and the hardwood
tips clear of it, and (b) GM ≥ 0 with the paddler seated rigid, the seat taken 3 mm higher than it can be and the load taken as high
as the paddler (it is lower), so the capacity holds whatever the load. (a) is
the displacement at T = sheer − 45 mm; (b) is found by bisection on the draft (five steps), since GM falls as
the paddler gets heavier. The load's maximum leaves room for a 45 kg paddler under both. Change the hull and the form
offers only the paddlers it carries: a lighter, wider or deeper hull carries more. The narrowest hulls are
excluded by the ranges: probing every corner of the smallest boats (5.0 m, fine ends, fresh water, 5 mm hull
and 4 mm deck plywood, both rockers at their limits) showed a single-chine V bottom needs 570 mm of beam to
carry a 45 kg paddler with GM ≥ 0, and a depth over 0.36 × beam carries the weight too high.

### At the defaults

(80 kg paddler 1.78 m tall, 5 kg load, sea water, 5.3 m × 545 mm, depth 190 mm, three chines, moderate ends)

| Quantity | Value | Igdlorssuit (published) |
|---|---|---|
| Boat weight | 14.9 kg: okoume panels 7.5, sheer clamps 1.4, glass and epoxy 2.9, coaming, bulkheads, hatches, fittings 3.1 | |
| Displacement Δ | 99.9 kg, ∇ = 0.0975 m³ | 88 kg |
| Design draft T | 107.6 mm | 122 mm |
| Waterline length × beam | 4.20 m × 0.485 m | 4.00 m × 0.48 m |
| Prismatic Cp, waterplane Cwp, block Cb | 0.639, 0.709, 0.445 | 0.524, 0.652, 0.374 |
| Wetted surface | 1.69 m² | 1.57 m² |
| Displacement-length ratio | 37.6 | |
| KB, BM, KM | 67, 204, 271 mm | KM 269 mm |
| KG (boat, paddler, load) | 248 mm | |
| **GM** | **23 mm** | |
| Freeboard, lowest point of the sheer / at the widest station | 50 mm / 82 mm | |
| Capacity: heaviest paddler | 83 kg (stability; freeboard would allow 87 kg) | |
| Trim | seat back 389 mm aft of the middle; LCB = LCG 124 mm aft | |
| Panels: deadrise / flare from the horizontal | 7.9°, 25.0°, 46.2°, 74.1°, deck crown 22° | |

The defaults make a boat a little fuller than the Igdlorssuit (Cp 0.64 against 0.52: our parametric ends are
fuller below the water than a hand-faired Greenland hull), with the same metacentric height above the keel.
The *Fine* ends bring Cp down towards 0.6.

### What 3DCraft checks (assertions, at every point of the form)

The formulas above are not trusted on their own: each is checked against the exact B-rep the kernel built. The
**displaced water** is the hull envelope intersected with a box up to the computed waterline (a body of its own,
inside the hull), and the kernel measures it.

| Assertion | What it proves | Measured at the defaults |
|---|---|---|
| displacement | the kernel's volume of the displaced water = Δ/ρ (± 0.2 %): Archimedes, and the Newton waterline | 0.09747 m³ (formula 0.09747) |
| trim | the kernel's centre of buoyancy (x) = the formula's centre of gravity (± 20 mm): the boat floats level | −124.0 mm, LCG −123.8 mm |
| KB | the kernel's centre of buoyancy height = the formula (± 1 mm) | 67.09 mm |
| initial stability | KB (measured) ≥ KG − BM, that is GM ≥ 0 | GM 23 mm |
| waterplane area | the kernel's area of the water body's top face = the formula (± 0.25 %); BM = I/∇ is built on the same half-breadths | 1.4450 m² |
| wetted surface | the kernel's area of the water body = wetted surface + waterplane (± 0.7 %: on the 25 loft stations) | 3.1328 m² |
| wooden hull weight, centre of gravity x and z | the kernel's mass and centre of mass of panels, deck, clamps and bulkheads (okoume 500, hardwood 600 kg/m³) = the formulas the trim and KG use (± 2 %, 15 mm, 8 mm) | 8.43 kg |
| freeboard | the deck's lowest point ≥ waterline + 40 mm | 154.4 mm (waterline 107.6) |
| tips dry | the hardwood tips lie above the water, so the waterline ends on the plywood hull the hydrostatics integrate | |
| coaming and hatch covers on the deck | they stand on the deck, inside the sheer (a keyhole or hatch wider than the deck would reach down below the sheer) | |
| coaming | the 3D coaming's volume = keyhole ring × 30 mm + lip ring × 6 mm (± 0.5 %): the riser stands 30 mm on the deck all round, at every number of chines; its height from deck to lip top = the deck's rise along the keyhole + 36 mm (± 3 mm) | |
| coaming riser, flat | the flat strip's length = the riser's mid-thickness perimeter (± 0.5 mm), its area = perimeter × 30 mm (± 0.5 %), its height = the deck's rise along the keyhole + 30 mm (± 2 mm) | |
| cockpit length | the opening (coaming) ≥ buttock-knee length (0.34 × stature, Pheasant) + room behind the seat back | |
| **developable panels**, each panel (the 3rd and 4th, which exist with 2 and 3 chines, together with the panel two below, which has the same joints): | | |
| 3D area = development | the kernel's area of the curved panel's outside = ∫ w·sqrt(1 + g'²) dx (± 0.1 %) | bottom 0.28650 m² |
| flat area = 3D area | the kernel's area of the three flat pieces = the same integral less the stitch holes (± 0.1 %) | bottom 0.28629 m² |
| flat length | the flat pieces' extent = the panel's length along its surface by Clenshaw–Curtis, an integrator independent of the Gauss rule that drew the outline (± 1 mm) | bottom 5016.89 mm |
| pieces fit a sheet | every piece is at most 2420 mm long | longest 1956 mm |
| flats apart | no two flat parts overlap | |

**Developability, in short.** Each panel is developable by construction (a cylinder: constant flare along the
boat), so a flat sheet bends onto it without stretching; the assertions then prove that the flat outline drawn
on the floor is *that* surface's development: the same area as the curved panel (measured on the B-rep) and the
same length along it, by two independent quadratures. Its two long edges are, by the construction, as long as
the chines they are stitched to.

## Cut sheets

Export with **File › Export…** as DXF or SVG, set **width** to 2440 mm to wrap the parts into sheet-wide rows:

- **Cut sheet: hull panels**: each hull panel once, in three pieces joined by **puzzle joints** (a dovetail key
  across the panel), staggered from panel to panel as kits do so the joints never line up; cut two of each from
  two sheets stacked face to face, which gives the mirror pair for port and starboard. Every piece fits a
  2440 × 1220 mm sheet. On the floor the pieces lie 50 mm apart along the panel; joined, they close up. Stitch holes (Ø 2 mm, 8 mm from the edge) sit
  at the same stations on both panels of a seam, so the copper wire ties match; they are closer towards the
  ends, where the panels twist most. Drill the narrow ends' holes as you stitch.
- **Cut sheet: deck**: the deck panel, the same way (cut two).
- **Cut sheet: bulkheads and coaming**: the two bulkheads (the inner section at their station, notched for the
  sheer clamps) and the **coaming's riser, developed**. The riser is a wall 30 mm high standing on the deck all
  round the keyhole, so it follows the deck's crown; being a vertical wall on a curve it is exactly developable:
  flat, it is a band 30 mm high and as long as the keyhole's perimeter at the riser's mid-thickness (2.0 m at the
  defaults, at most 2.35 m, so it needs no joint), whose two edges rise and fall with the deck's height along
  the keyhole (sampled at 16 points a side from the hull's own formulas, z = Z4 + (Y4 − |y|) tan crown, and
  drawn as splines). Cut it twice from 3 mm okoume and laminate the two round a keyhole form into the 6 mm
  riser, the ends staggered. The 6 mm lip, 28 mm wide, sits on the riser parallel to the deck: laminate it
  from strips of 3 mm plywood or veneer over the riser (on a crowned deck it is not flat, so it has no flat
  pattern here).

Glue the puzzle joints flat on plastic sheet with thickened epoxy (and a strip of glass both sides on a hull
panel) before stitching. The cockpit opening and the hatch openings are cut in the deck after it is assembled,
from the coaming's and the hatch rims' templates (the 3D model shows them in place). 

**Building**, in short (CLC, Kulczycki): cut and join the panels; stitch the bottom panels at the keel, open
them and stitch on the next panels chine by chine, then the topsides, with copper wire every 100 to 150 mm;
check the hull is fair and true; tack the seams with thickened epoxy between the wires, pull the wires, fillet
and tape the seams inside; glass the outside; fit the bulkheads, sheer clamps and deck; tape the deck seam
inside through the hatches, glass the deck; coaming, hatches, end pours, varnish (it must be UV-protected:
okoume and epoxy both suffer in sunlight).

## Safety

- A sea kayak is a serious craft: learn to paddle it, to brace and to rescue yourself and others (and to roll
  a Greenland boat) in sheltered water first, with others, and wear a buoyancy aid.
- The stability figure is for a paddler sitting still and rigid. Low-volume Greenland boats have little
  initial stability on purpose: they feel tippy until you paddle them with your hips.
- With **Bulkheads and hatches** off the hull has no buoyancy compartments: fit float bags fore and aft, or it
  will sink when swamped.
- Epoxy sensitises skin: gloves, ventilation, a respirator when sanding cured epoxy and glass.

## Sources

- PaddlingLight, *Igdlorssuit: Free Kayak Plans for the Boat Before Anas Acuta*
  (paddlinglight.com/articles/igdlorssuit-free-plans-for-the-boat-before-anas-acuta): the boat's history (Ken
  Taylor 1959, Duncan Winning's survey 1964) and its hydrostatics, quoted above for comparison. Its plans were
  not used.
- C. Kulczycki, *The New Kayak Shop: More Elegant Wooden Kayaks Anyone Can Build*, Ragged Mountain Press
  1999, and Chesapeake Light Craft (clcboats.com): stitch-and-glue practice (okoume 3 and 4 mm, wire stitches,
  fillets and tape, glass cloth weights), okoume sheet weights.
- A. B. Biran and R. López-Pulido, *Ship Hydrostatics and Stability*, 2nd ed., Butterworth-Heinemann 2014:
  displacement, centres of buoyancy and gravity, BM = I/∇, GM, form coefficients.
- D. Gerr, *The Nature of Boats*, International Marine 1992: the displacement-length ratio and prismatic
  coefficient for small craft.
- *Sea Kayaker* magazine's reviews (for instance of the Pygmy Arctic Tern, August 2002): stability curves with a
  fixed paddler whose centre of gravity is 10 in above the seat and 10 in ahead of the seat back.
- S. Pheasant, *Bodyspace*, 2nd ed., Taylor & Francis 1996: buttock–knee length about 0.34 of stature (the
  cockpit's minimum length); D. A. Winter, *Biomechanics and Motor Control of Human Movement* (segment lengths
  after Drillis & Contini), for the foot brace at about 0.57 of stature from the seat back.
- M. P. do Carmo, *Differential Geometry of Curves and Surfaces*, 1976, §3-5: ruled and developable surfaces
  (a cylinder has zero Gaussian curvature and is isometric to the plane).
- C. W. Clenshaw and A. R. Curtis, *A method for numerical integration on an automatic computer*, Numerische
  Mathematik 2 (1960) 197–205.

`build.json` was written by `python3 -I gen.py > build.json`; edit `gen.py` and run it again to change the
model.

**Colours.** Varnished okoume (plywood #D9B98A) hull and flat panels, an ochre (#D4A24C) deck, walnut
(#7A5638) tips, coaming and hatch covers, cream (#E8DFCC) sheer clamps, from the Jigs palette.
