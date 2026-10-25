# Tuned chimes

A wind chime of tubes hanging from a disc, or a glockenspiel of flat bars on a frame, that is **in tune
before you cut it**: every tube or bar gets the length of its note from the physics of a vibrating beam,
and its cord or pin holes at the nodes. Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Instrument | Instrument | Wind chime (tubes) | Wind chime (tubes), Glockenspiel (bars) |
| Scale | Notes | Major pentatonic | table `scales` (below) |
| Lowest note | Notes | C | C, C#, D, Eb, E, F, F#, G, G#, A, Bb, B (table `notes`) |
| Octave | Notes | 5 | `octMin` to `octMax` (whole; see *Ranges*) |
| Notes | Notes | 6 | 3 to the scale's `maxNotes` (at most two octaves, at most 12) |
| Tube material | Wind chime | Aluminium EN AW-6060 T6 | table `tubeMaterials` |
| Tube size | Wind chime | 25 x 1.5 | table `tubeSizes`, 12 to 50 mm outside |
| Striker gap | Wind chime | 12 mm | 5 to 30 mm, step 1 mm |
| Bar material | Glockenspiel | Aluminium flat bar EN AW-6060 | table `barMaterials` (the wood bars are straight, not undercut: a starting point, see *Overtones*) |
| Bar width | Glockenspiel | 30 mm | 15 to 60 mm, step 1 mm |
| Bar thickness | Glockenspiel | 6 mm | max(3 mm, width / 8) to 25 mm, step 0.5 mm (a wide thin bar is a plate, not a beam) |

The default is a wind chime of six aluminium tubes 25 × 1.5 mm in C major pentatonic from C5: C5 D5 E5
G5 A5 C6, 532.7, 502.4, 473.8, 433.8, 409.0 and 374.3 mm long, hanging from a walnut or plywood disc of
154 mm. *A minor* is the scale *Natural minor* from A; *Westminster* (the Big Ben quarters) is in its
original key with lowest note B (B, E, F#, G#).

## The physics

A tube or bar that hangs or rests freely at both ends is a **free-free beam**. Its first bending mode
(Euler-Bernoulli beam theory) has the frequency

  f = (β₁L)² / (2π L²) · √(E I / (ρ A)),  with (β₁L)² = 4.7300² = 22.373,

so the Euler-Bernoulli length for a note of frequency f is

  L_EB = √( 22.373 / (2π f) · √(E I / (ρ A)) ).

E is Young's modulus, ρ the density, A the cross-section and I its second moment of area. Only
√(I / A), the radius of gyration, matters: for a tube of outside diameter D and inside diameter d it is
√(D² + d²) / 4, for a bar of thickness t (it bends through its thickness; the width drops out) t / √12.
So the length grows with the square root of the tube's size and of the speed of sound √(E/ρ), and falls
with the square root of the frequency: an octave up is 1/√2 = 0.707 times as long.

**Timoshenko correction.** Euler-Bernoulli ignores shear and rotary inertia, which lower the pitch of a
short, fat piece: the default tubes would be 22 (C5) to 43 cents (C6) flat, so out of tune with each
other by 21 cents, and a 50 mm tube or a thick wooden bar near the shortest allowed length by hundreds of
cents. The Jig uses a closed form fitted to the Timoshenko beam (solved numerically by the reviewer of
this Jig, two ways):

  (f_EB / f_T)² ≈ 1 + C (r_g / L)²,  C = 47.7 + 11.7 · E / (κ G),

with G the shear modulus (table column `G`: aluminium 26, steel 79, stainless 77, copper 44, brass
39 GPa, wood about E/14 along the grain) and κ the shear coefficient (0.53 for a thin-walled tube, 5/6
for a rectangle). It is within 4 cents of the full solution for L/r_g ≥ 30 and within 2 cents for
L/r_g ≥ 45. The length that sounds f then solves L⁴ + C r_g² L² = L_EB⁴, a quadratic in L²:

  **L = √( (√(C² r_g⁴ + 4 L_EB⁴) − C r_g²) / 2 )**

(variables `LEB1`… and `L1`…; the exact root of the same equation that a fixed-point iteration
L ← L_EB (1 + C (r_g/L)²)^(−1/4) converges to). Checked against a shooting-method Timoshenko solver: the
default C5 and C6 tubes, a 50 × 2 tube near its shortest, a 30 × 6 aluminium bar and 25 mm padauk and
rosewood bars all come out within 2 cents.

The notes are **equal temperament** with A4 = 440 Hz: f = 440 · 2^((octave − 4) + (note − 9)/12) for
the lowest note, and each further note is that times 2^(s/12), s its semitones above the lowest from the
scale table. Variables `f1`…`f12` are the frequencies in Hz and `L1`…`L12` the lengths (`document.inspect`
lists them).

The first mode has its **nodes 0.2242 L from each end** (22.4 %): hung or supported there, the tube or
bar rings longest. A tube hangs from a cord through a cross hole at the top node; a bar rests on felt over
the frame's rails, held by a pin through a hole at each node. The tubes hang with their middles level and
the striker 18 mm below them (its 12 mm edge spans 12 to 24 mm below the middles): the exact middle is a
node of the first overtone, which Lee Hite calls the "dead zone" and says to stay out of; a strike a
little off centre (or at the bottom end, with bottom-aligned tubes) sounds the overtone too.

**Overtones.** A straight, slender bar's first overtone is 2.76 times its fundamental (a non-harmonic
ratio, the bell-like sound of a glockenspiel; fine for metal bars). Xylophone and marimba bars are
undercut (arched underneath) to tune that overtone to 3:1 or 4:1; this Jig makes straight bars, so the
**wooden** bars sound duller than a real xylophone's and are a starting point, not a finished instrument.
Fat tubes push the overtone down (about 2.14 times at L/r_g = 15), another reason for the shortest length
below.

## How it is built

- **Wind chime.** The tubes stand on a circle of radius `Rc` round the disc's centre, the longest first,
  their middles level at `zc`. `Rc` is the larger of what keeps neighbouring tubes `tubeGap` apart
  (max(OD/2, 12 mm)) and what leaves the striker (a 12 mm walnut puck) at least 25 mm of radius with the
  striker gap. Each tube has a cross hole of OD/6 (3 to 6 mm) at its top node, square to the radius; its
  cord runs through it, up the bore and through the disc, with a knot on top. A centre cord runs from
  the hanging ring through the disc and the striker to the wind sail, a rounded plywood plate below the
  longest tube.
- **Glockenspiel.** The bars lie side by side along x, each centred across the frame. The frame is one
  12 mm plywood part: two rails running straight through the first and the last bar's nodes and two end
  pieces. The nodes between lie a few mm off a straight line (L falls as 1/√f, not linearly); the rail
  width is computed to take that (`maxDev`) plus the pin. Each bar has a hole of width/5 (4 to 6 mm) at
  each node and rests 3 mm above the rail (a felt strip), on brass pins 1.5 mm thinner than the hole (a
  rubber sleeve).
- **Cut list.** The named sets `Note 1` … `Note 12` hold the tube or bar of each note (`select.set
  {"set": "Note 3"}`), `Tubes`, `Bars` and `Notes` all of them; the assertions *Tube k is in tune* and
  *Bar k is in tune* name each piece, and `L1`…`L12` give the cut lengths. To read them:

  ```sh
  craft3d-cli run dist/tuned-chimes.3dcraftjig \
    --cmd param.set --params '{"values": {"scale": "Major", "N": 8, "tubeSize": "20 x 1.5"}}' \
    --cmd document.inspect
  ```

- **Cut sheet.** The face set `Cut sheet` holds the flat parts to laser-cut: the disc (with the cord holes)
  and the wind sail, or the glockenspiel frame (with the pin holes):
  `file.export {"path": "chime.svg", "set": "Cut sheet"}`.

## Ranges

Every point of the form gives a playable instrument:

- **Two octaves at most.** The scale table gives `maxNotes` for each scale, the most notes within 24
  semitones (and 12 at most): the shortest tube is then at least half the longest, so a striker just
  below the tubes' middles still hits each one between its top node and its bottom end.
- **Octave.** `Lfloor` is the shortest note that can still be drilled and hung, and is slender enough
  (L/r_g ≥ 30) for the Timoshenko closed form and a clean overtone: for a tube max(100 mm, 5 × OD,
  30 r_g), for a bar max(80 mm, 3 × width, 30 r_g). `Lceil` is the longest that is still handy: 1500 mm
  for a tube, 700 mm for a bar. Through their Euler-Bernoulli equivalents (`LfloorEB`, `LceilEB`) and
  L_EB ∝ 1/√f, these give the highest top note and the lowest bottom note, and so `octMax` and `octMin` (kept within 2 to 8) for the
  chosen lowest note, scale and number of notes. Thick tubes and stiff metals reach higher; thin wooden
  bars stay low.

## Checked

The assertions (`assert.list`), at every regeneration:

- **Tube k / Bar k is in tune (length)**, for each of the 12 notes: the body's box lies at its place and
  both of its ends lie within 0.01 mm of where the corrected (Timoshenko) length, worked out again from
  the note's frequency, puts them (1, or 0 when the note is not there). 0.01 mm on 400 mm is under 0.1 cent.
- **Tube k: cord hole at the node** and **Bar k: holes at the nodes**: a hole of the cord or pin diameter
  whose box lies within 0.01 mm of 0.2242 L from the end (each end, for a bar).
- **Note 1: extent along its length / across**: the longest note's body, measured, is the formula's length
  and the tube's diameter (or the bar's thickness).
- **Every note is there**, **Node holes go through**, **one per tube, two per bar**.
- **Notes do not hit each other**: the least clearance between tubes (bars) is the gap they were spaced for
  (asserted to 85 % of it: what the clearance measure can prove of curved faces; the tube assertions'
  boxes place every tube exactly).
- **Nothing touches a note**: no body overlaps a tube or bar: the cords and pins pass through the holes.
- **Striker**: the striker's box is a disc of radius Rc − OD/2 − striker gap, within 0.01 mm, standing
  12 to 25 mm below the tubes' middles; with the tubes' boxes on the circle of radius Rc, the gap to every
  tube is exactly the striker gap.
- **The striker reaches every tube**: no tube ends above or begins below the striker.
- **Shortest note long enough to drill and hang**, **Longest note short enough to handle** (above).
- **Disc or frame volume**: the disc with its holes, or the frame with every pin seated in a rail, equals
  its closed form (a pin off the rail would add volume).
- **Cut sheet**: the disc and the sail, or the frame.

`check-range` passes, plain and `--deep`: 125 of 125 points each (the default, 64 corners, 44 choices,
16 random; seed 1, 3DCraft `main` at 3faaaea0), regeneration median about 0.3 s, at most 1.2 s. The
octave range was also checked in Python over every scale, note count, lowest note, material and size:
`octMin` ≤ `octMax` everywhere, with the Timoshenko lengths.

## How to tune finally

For **metal**, the cut length is right to within about a quarter of a semitone: the alloy's modulus and
density vary by a few per cent, and the cord hole and end burrs take a little mass. For **wood** it is only
a starting point: the modulus varies by ±20 % from board to board (±165 cents), and the table's values are
static moduli at 12 % moisture (the dynamic modulus that sets the pitch is some 5 to 15 % higher). So:

1. Cut each piece **3 to 5 mm long** (wood: 5 to 10 %), square, and deburr.
2. Drill the node hole(s) at 22.4 % of the **final** length (measure from the top end for a tube).
3. Hang or support it at the nodes, strike it at the middle and read the pitch with a tuner app.
4. It reads flat (too low): shorten it. Saw off a large correction first, then file or sand the bottom
   end square, a little at a time; the pitch
   rises about 3.5 cents for every 0.1 % of the length taken off (f ∝ 1/L², so 0.25 mm on 250 mm). Too short
   cannot be undone (a bar can be lowered by thinning its middle underside, as xylophone makers do).

## Sources

- N. H. Fletcher and T. D. Rossing, *The Physics of Musical Instruments*, 2nd ed., Springer 1998, ch. 2
  (bars: the free-free beam, its frequency ratios and nodes) and ch. 19 (bars, chimes and tubular bells).
- S. P. Timoshenko, "On the correction for shear of the differential equation for transverse vibrations
  of prismatic bars", *Philosophical Magazine* 41 (1921) 744–746; G. R. Cowper, "The shear coefficient in
  Timoshenko's beam theory", *J. Appl. Mech.* 33 (1966) 335–340 (κ). The closed form's constants were
  fitted by this Jig's reviewer to a numerical (shooting-method) Timoshenko solution.
- The free-free beam's eigenvalue: cos(βL) cosh(βL) = 1, β₁L = 4.7300, (β₁L)² = 22.373, nodes at
  0.2242 L (S. S. Rao, *Vibration of Continuous Systems*, Wiley 2007, the chapter on the transverse
  vibration of beams, or any vibration text with Euler-Bernoulli beams).
- Leland (Lee) Hite, *Tubular Bell Chimes Design Handbook* (www.leehite.org/Chimes.htm): hang at the
  22.4 % node, cut long and tune, and the striker: strike the end edge with bottom-aligned tubes, and with
  top- or centre-aligned tubes keep away from the exact centre, the first overtone's "dead zone" (The
  Build Plan, steps 13 and 17, p. 11; Striker, pp. 38–39). Chuck's wind chime calculators work from the
  same beam formula. Only the descriptions were used; no code was copied.
- Equal temperament with A4 = 440 Hz: ISO 16:1975.
- Material values: aluminium 6060-T6 E ≈ 69.5 GPa, G ≈ 26 GPa, 2700 kg/m³ from extruders' alloy data
  sheets (e.g. Aalco's and Hydro's 6060 sheets; EN 755-2 gives the alloy's strength, not its modulus);
  structural steel E = 210 GPa, G = 81 GPa (EN 1993-1-1; 200 and 79 GPa are used for thin EMT, typical
  for mild steel tube); stainless 1.4301 (EN 10088-1 annex: E = 200 GPa at 20 °C, 193 typical for
  annealed tube); copper Cu-DHP and brasses from the Copper Development Association data sheets; padauk,
  Honduran rosewood and hard maple (static modulus of elasticity at 12 % moisture, and dried density) from
  Eric Meier, *The Wood Database* (wood-database.com). Wood varies from board to board: tune by ear.
- Tube sizes: common aluminium tube, EN 1057 copper and US EMT conduit (ANSI C80.3) sizes.

`build.json` was written by `python3 -I gen.py > build.json`; edit `gen.py` and run it again to change
the model.
