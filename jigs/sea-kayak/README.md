# Sea kayak (stitch and glue)

A Greenland-style **multichine sea kayak in okoume plywood**, built stitch and glue: four hull panels and
a deck panel a side. It is built **entirely by 3DCraft from formulas**: `gen.py` writes commands and
computes no geometry. The hull's lines are formulas; 3DCraft finds the keel, the chines and the sheer where
the panels meet, makes each panel the developable surface between its chines, gives every panel its
plywood thickness with the joints a builder makes (inner edges touching at the chines, the deck resting on
the sheer panels), lays every panel flat for cutting, and finds the waterline for the paddler and the load
on the exact hull. Licence: CC-BY-4.0.

**Lines.** The character is that of the Greenland kayak Emanuele Korneliussen built at Igdlorssuit for Ken
Taylor in 1959, surveyed by Duncan Winning in 1964 (the boat behind the Anas Acuta and most British sea
kayaks): about 5.2 m long, 0.53 m wide, low volume, strong rocker, raised ends. The published plans carry no
licence that allows reuse of their offsets, so **these lines are our own**, a parametric family *inspired
by* that boat. Its published hydrostatics (displacement 88 kg, Cp 0.524, LWL 4.00 m, BWL 0.48 m, draft
0.122 m, transverse KM 0.27 m) are the yardstick below.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Length overall | Hull | 5300 mm | 5000 to 5800 mm |
| Beam | Hull | 545 mm | 530 to 600 mm, at the sheer |
| Depth at the sheer | Hull | 190 mm | 170 mm to min(230 mm, 0.36 × beam), keel to sheer at the widest station |
| Deck crown | Hull | 22° | 12 to 26° |
| Bow rise, Stern rise | Hull | 300, 240 mm | 250 to 400, 220 to 350 mm: the keel's rise to each tip (rocker) |
| Paddler weight (kg) | Paddler and load | 80 | 45 to 100 |
| Load (kg) | Paddler and load | 5 | 0 to 30 |
| Water | Paddler and load | Sea water | Sea water (1025 kg/m³) or fresh water (1000 kg/m³) |

## How 3DCraft builds it

`x` runs along the boat (stern −L/2, bow +L/2), `y` to starboard, `z` up from the keel's lowest point. A
station is η from 0 (stern tip) to 1 (bow tip), a skewed copy of ξ = x/L + ½ (η = ξ + s ξ(1 − ξ)) so that
the widest station, η = ½, lies at 0.47 of the length from the stern.

1. **The lines, as formulas.** Every hull panel j is a *generalised cylinder*: in every station it is a
   straight line at the same flare angle θⱼ, from chine j to chine j + 1, of width
   wⱼ = Wⱼ G^pⱼ (1 + σⱼ (1 − G)), G = 4η(1 − η). At the widest station the chines lie on a quarter ellipse
   (B/2, D), equally spaced in angle, which sets θⱼ and Wⱼ. The keel rises as z₀ = rA (q u² + (1 − q) u⁴) +
   rC u⁵ (u = 2η − 1, rA and rC from the bow and stern rises, q = 0.3). The deck is a generalised
   cylinder too, at the crown angle, from the sheer to a ridge on the centre line. A surface swept by
   straight lines that keep their direction has zero Gaussian curvature: it is **developable**, a sheet of
   plywood bends onto it without stretching (do Carmo, §3-5).
2. **The hull envelope.** Each panel's *trace* (its section square to its flare direction, a curve
   `sketch.curve` draws from the formulas) is extruded along that direction into a solid; the five solids a
   side, mirrored, are intersected (`feature.boolean`). What is left is the outside of the planking closed
   by the deck, and its edges are the **keel, the chines and the sheer, found by the kernel** where
   neighbouring panels meet.
3. **The panels between the chines.** `feature.developable` makes the developable sheet between each pair
   of neighbouring chines (the envelope's edges), the same surface as the envelope's face, found
   independently from the two chines alone: the proof that each panel *is* the developable between its
   chines. The feature refuses a sheet that is not developable and reports its largest Gaussian
   curvature (about 10⁻¹² mm⁻² here); it is not asserted on separately, because measuring the curvature
   of these 5 m sheets does not always settle in 3DCraft today.
4. **Plywood.** `feature.plate` gives each panel of the envelope its thickness inwards (4 mm hull, 3 mm
   deck) with the builder's joints: `touch` at the keel and the chines (the inner edges of two stitched
   panels just touch; the outside V is the epoxy fillet), the sheer panel `under` the deck and the deck
   `over` it (the deck rests on the sheer panel and covers its edge flush with its outside), `touch` at
   the ridge, and both ends `onto` the planes where the plywood ends (η = 0.03 and 0.97; the last 160 mm
   or so of each end, where the panels are a few centimetres wide, is a hardwood tip and an end pour of
   thickened epoxy).
5. **Flat panels.** `feature.unfold` lays the outside skin of each starboard plate flat on the floor
   beside the boat (cut two of each from two sheets stacked face to face for the port and starboard
   pair). Lengths, angles and areas are kept: the unfold refuses to change an edge's length by more than
   the tolerance, and reports the change (at the defaults: lengths 2·10⁻¹¹, areas 1·10⁻⁸ relative).
6. **Hydrostatics.** `measure.levelFor` finds the draft at which the hull envelope displaces the boat's,
   the paddler's and the load's weight in water, by Newton's method on the exact B-rep, and returns the
   centre of buoyancy and the waterplane's second moments. KB, BM, KM and GM are computed from those
   measures by `hydro.py` (below): naval vocabulary, kept in the Jig.

`gen.py` writes 80 variables (the previous version, which computed the geometry itself, needed 3839),
48 feature commands and 17 assertions. A regeneration from nothing takes about 5 s; a build with every
assertion measured about 30 s.

## What 3DCraft checks (assertions, at every point of the form)

| Assertion | What it proves |
|---|---|
| chines 1 to 3, both sides: the panels' inner edges touch | the kernel's least distance between neighbouring plates is 0 (± 0.01 mm): the panels meet edge to edge |
| keel, ridge: the inner edges touch | the same for the two bottom panels and the two deck panels |
| sheer, both sides: the deck rests on the sheer panel | the least distance between deck and sheer plate is 0 |
| the panels: developable | every face of the envelope the plates are made of is developable within the tolerance (Gaussian curvature measured on the face) |
| the panels: Gaussian curvature | the largest \|K\| on those faces ≤ 10⁻⁹ mm⁻² (measured: 0) |
| plywood mass | the kernel's mass of the ten plates (okoume, 500 kg/m³) is the weight formula's ± 4 %: the waterline is found for the boat the model is |
| freeboard | the waterline for boat, paddler and load (`levelFor`) lies at least 45 mm below the sheer amidships |
| tips dry | the hardwood tips lie above the highest waterline the freeboard allows |
| coaming, both sides | the coaming stands on the deck (distance 0) |

## Hydrostatics at the defaults

(80 kg paddler, 5 kg load, sea water, 5.3 m × 545 mm, depth 190 mm; `python3 -I hydro.py`)

| Quantity | 3DCraft (measures) | Igdlorssuit (published) | Previous Jig (formulas outside 3DCraft) |
|---|---|---|---|
| Plywood (kernel mass of the ten plates) | 8.47 kg (formula 8.53 kg) | | 7.5 kg |
| Boat (plywood, glass and epoxy, fittings) | 16.3 kg | | 14.9 kg |
| Displacement | 101.3 kg, ∇ = 0.0989 m³ | 88 kg | 99.9 kg |
| Draft T (`levelFor`, 10 Newton steps) | 111.7 mm | 122 mm | 107.6 mm |
| Waterplane area | 1.544 m² | | 1.445 m² |
| KB, BM, KM | 72, 236, **308** mm | KM 269 mm | 67, 204, **271** mm |
| KG (boat, paddler, load) | 252 mm | | 248 mm |
| **GM** | **56 mm** | | **23 mm** |
| Centre of buoyancy, x | 128 mm aft of the middle | | 124 mm aft |
| Freeboard amidships | 78 mm | | 82 mm |

**Why KM and GM are higher than before.** The hull is fuller at the ends than the previous version's:
the panels now narrow to the ends as G^p with p ≤ 1 (0.8 to 1.0) where they had p = 1.8 to 2.6 (fine V
ends). That was a choice forced by the platform: with finer ends the topside panel's trace has an
inflection near the ends, and `feature.developable` refuses a generalised cylinder whose trace inflects
(the developable condition's zero set branches there), so the panels could no longer be shown to be the
developable connection of their chines. The fuller waterplane (+7 % area) carries its area further out
along the length and at the ends, so its transverse moment, BM = I_T/∇, grows by 16 %; KB and KG change
little. The boat is more stable than the Igdlorssuit (KM 308 against 269 mm); the *Beam* and *Depth*
parameters move it (a 530 mm beam takes BM down by about 8 %).

**KG** takes the plywood's centre of gravity from the kernel (z = 145 mm), the glass and fittings with
it, the paddler's centre of gravity 254 mm above a 25 mm seat pad on the floor amidships, and the load at
100 mm. **Capacity:** the paddler's range ends at what the hull carries with the sheer 45 mm above the
water (a block coefficient of the volume below that plane, calibrated against `measure.below` over the
corners of the hull's ranges and on the safe side of every one), and the load's at what is left; the
freeboard assertion then checks the real waterline at every point.

Why `hydro.py` and not an assertion: a measure's value cannot be used in an expression in 3DCraft (no
variable is driven by a measure), so GM ≥ 0, which needs the draft from `levelFor` inside the plane of
`sectionInertia` and KB from `centroidBelow` in the bound, cannot be written as an assertion yet. The
assertions check what can be checked (the waterline for the weight against the sheer, the tips dry,
the formula's weight against the kernel's), and `hydro.py` does the naval arithmetic on the measures.

## Cut sheet

Export the named set **Cut sheet: panels** (File › Export…, DXF or SVG, `width` 5100 mm for one panel a
row): the outlines of the four hull panels and the deck panel, laid flat; `cut-sheet.svg` is that export
at the defaults. The panels are about 5 m long: join two or three 2440 mm sheets end to
end with scarf or puzzle joints before cutting (or cut the panels in pieces and join them flat), then cut
two of each, stacked face to face, for the port and starboard pair.

**Building**, in short (CLC, Kulczycki): cut and join the panels; stitch the bottom panels at the keel,
open them and stitch on the next panels chine by chine, then the sheer panels, with copper wire every 100
to 150 mm; tack the seams with thickened epoxy, pull the wires, fillet and tape the seams inside; glass the
outside; fit bulkheads, sheer clamps and deck; coaming, hatches, hardwood tips and end pours, varnish.

## Safety

- A sea kayak is a serious craft: learn to paddle it, brace, rescue yourself and others (and roll a
  Greenland boat) in sheltered water first, with others, and wear a buoyancy aid.
- The stability figure is for a paddler sitting still and rigid. Low-volume boats feel tippy until you
  paddle them with your hips.
- Fit bulkheads or float bags fore and aft, or the hull sinks when swamped.
- Epoxy sensitises skin: gloves, ventilation, a respirator when sanding cured epoxy and glass.

## Sources

- PaddlingLight, *Igdlorssuit: Free Kayak Plans for the Boat Before Anas Acuta*
  (paddlinglight.com/articles/igdlorssuit-free-plans-for-the-boat-before-anas-acuta): the boat's history and
  its hydrostatics, quoted for comparison. Its plans were not used.
- C. Kulczycki, *The New Kayak Shop*, Ragged Mountain Press 1999, and Chesapeake Light Craft (clcboats.com):
  stitch-and-glue practice, okoume 3 and 4 mm, glass cloth weights, okoume sheet weights.
- A. B. Biran and R. López-Pulido, *Ship Hydrostatics and Stability*, 2nd ed., Butterworth-Heinemann 2014:
  displacement, centres of buoyancy and gravity, BM = I/∇, KM, GM.
- *Sea Kayaker* magazine's stability reviews: a paddler's centre of gravity 10 in above the seat.
- M. P. do Carmo, *Differential Geometry of Curves and Surfaces*, 1976, §3-5: ruled and developable
  surfaces.

`build.json` was written by `python3 -I gen.py > build.json`; edit `gen.py` and run it again to change the
model.

The cockpit coaming is a ring standing 30 mm on the deck round an 800 × 420 mm opening (the envelope
raised by 30 mm, within the ring, less the envelope); cut the opening in the deck after assembly.

**Colours.** Varnished okoume (plywood #D9B98A) hull panels and their flat patterns, a sapele-coloured
(copper #B87350) deck, walnut (#7A5638) tips and coaming, from the Jigs palette.
