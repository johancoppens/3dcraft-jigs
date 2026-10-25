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
| Bar material | Glockenspiel | Aluminium flat bar EN AW-6060 | table `barMaterials` |
| Bar width | Glockenspiel | 30 mm | 15 to 60 mm, step 1 mm |
| Bar thickness | Glockenspiel | 6 mm | max(3 mm, width / 8) to 25 mm, step 0.5 mm (a wide thin bar is a plate, not a beam) |

The default is a wind chime of six aluminium tubes 25 × 1.5 mm in C major pentatonic from C5: C5 D5 E5
G5 A5 C6, 536.1, 506.0, 477.6, 438.0, 413.4 and 379.1 mm long, hanging from a walnut or plywood disc of
154 mm. *A minor* is the scale *Natural minor* from A; *Westminster* (the Big Ben quarters) is in its
original key with lowest note B (B, E, F#, G#).

## The physics

A tube or bar that hangs or rests freely at both ends is a **free-free beam**. Its first bending mode
(Euler-Bernoulli beam theory) has the frequency

  f = (β₁L)² / (2π L²) · √(E I / (ρ A)),  with (β₁L)² = 4.7300² = 22.373,

so the length for a note of frequency f is

  **L = √( 22.373 / (2π f) · √(E I / (ρ A)) )**.

E is Young's modulus, ρ the density, A the cross-section and I its second moment of area. Only
√(I / A), the radius of gyration, matters: for a tube of outside diameter D and inside diameter d it is
√(D² + d²) / 4, for a bar of thickness t (it bends through its thickness; the width drops out) t / √12.
So the length grows with the square root of the tube's size and of the speed of sound √(E/ρ), and falls
with the square root of the frequency: an octave up is 1/√2 = 0.707 times as long.

The notes are **equal temperament** with A4 = 440 Hz: f = 440 · 2^((octave − 4) + (note − 9)/12) for
the lowest note, and each further note is that times 2^(s/12), s its semitones above the lowest from the
scale table. Variables `f1`…`f12` are the frequencies in Hz and `L1`…`L12` the lengths (`document.inspect`
lists them).

The first mode has its **nodes 22.4 % of the length from each end** (0.2242 L): hung or supported there,
the tube or bar rings longest. A tube hangs from a cord through a cross hole at the top node; a bar rests on
felt over the frame's rails, held by a pin through a hole at each node. Striking the middle (an antinode of
the first mode, a node of the second) favours the fundamental, so the tubes hang with their middles level
and the striker at that height.

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
  semitones (and 12 at most): the shortest tube is then at least half the longest, so a striker at the
  tubes' middles still hits each one between its top node and its bottom end.
- **Octave.** `Lfloor` is the shortest note that can still be drilled and hung, and behaves as a slender
  beam: for a tube max(100 mm, 5 × OD), for a bar max(80 mm, 3 × width, 8 × thickness). `Lceil` is the
  longest that is still handy: 1500 mm for a tube, 700 mm for a bar. Since L ∝ 1/√f, these give the
  highest top note and the lowest bottom note, and so `octMax` and `octMin` (kept within 2 to 8) for the
  chosen lowest note, scale and number of notes. Thick tubes and stiff metals reach higher; thin wooden
  bars stay low.

## Checked

The assertions (`assert.list`), at every regeneration:

- **Tube k / Bar k is in tune (length)**, for each of the 12 notes: the body's box lies at its place and
  both of its ends lie within 0.01 mm of where the length from the formula, worked out again from the
  note's frequency, puts them (1, or 0 when the note is not there). 0.01 mm on 400 mm is under 0.1 cent.
- **Tube k: cord hole at the node** and **Bar k: holes at the nodes**: a hole of the cord or pin diameter
  whose box lies within 0.01 mm of 22.4 % from the end (each end, for a bar).
- **Note 1: extent along its length / across**: the longest note's body, measured, is the formula's length
  and the tube's diameter (or the bar's thickness).
- **Every note is there**, **Node holes go through**, **one per tube, two per bar**.
- **Notes do not hit each other**: the least clearance between tubes (bars) is the gap they were spaced for
  (asserted to 85 % of it: what the clearance measure can prove of curved faces).
- **Nothing touches a note**: no body overlaps a tube or bar: the cords and pins pass through the holes.
- **Striker gap or felt gap**: the striker is the striker gap from the tubes (the glockenspiel's frame and
  pins the felt and sleeve gap from the bars).
- **The striker reaches every tube**: no tube ends above or begins below the striker.
- **Shortest note long enough to drill and hang**, **Longest note short enough to handle** (above).
- **Disc or frame volume**: the disc with its holes, or the frame with every pin seated in a rail, equals
  its closed form (a pin off the rail would add volume).
- **Cut sheet**: the disc and the sail, or the frame.

`check-range` passes, plain and `--deep`: 125 of 125 points each (the default, 64 corners, 44 choices,
16 random; seed 1, 3DCraft `main` at 3faaaea0), regeneration median about 0.3 s, at most 1.7 s. The
octave range was also checked in Python over every scale, note count, lowest note, material and size:
`octMin` ≤ `octMax` everywhere.

## How to tune finally

The formula is exact for a slender, uniform beam; real tubes and bars differ by a little: the alloy's
modulus and density vary by a few per cent (wood by up to 20 %), the cord hole and end burrs take a little
mass, and thick, short pieces ring lower than Euler-Bernoulli says (shear and rotary inertia). So:

1. Cut each piece **3 to 5 mm long** (wood: 5 %), square, and deburr.
2. Drill the node hole(s) at 22.4 % of the **final** length (measure from the top end for a tube).
3. Hang or support it at the nodes, strike it at the middle and read the pitch with a tuner app.
4. It reads flat (too low): shorten it. File or sand the bottom end square, a little at a time; the pitch
   rises about 3.5 cents for every 0.1 % of the length taken off (f ∝ 1/L², so 0.25 mm on 250 mm). Too short
   cannot be undone (a bar can be lowered by thinning its middle underside, as xylophone makers do).

## Sources

- N. H. Fletcher and T. D. Rossing, *The Physics of Musical Instruments*, 2nd ed., Springer 1998, ch. 2
  (bars: the free-free beam, its frequency ratios and nodes) and ch. 19 (bars, chimes and tubular bells).
- The free-free beam's eigenvalue: cos(βL) cosh(βL) = 1, β₁L = 4.7300, (β₁L)² = 22.373, nodes at
  0.2242 L (S. S. Rao, *Vibration of Continuous Systems*, Wiley 2007, the chapter on the transverse
  vibration of beams, or any vibration text with Euler-Bernoulli beams).
- Lee Hite, *How to Make Wind Chimes* (leehite.org): chime design notes (hang at 22.4 %, strike at
  the middle, cut long and tune) and his published length tables; Chuck's wind chime calculators work from
  the same formula. Only the descriptions were used; no code was copied.
- Equal temperament with A4 = 440 Hz: ISO 16:1975.
- Material values: aluminium EN AW-6060 (EN 755-2; E ≈ 69.5 GPa, 2700 kg/m³), structural steel
  (EN 1993-1-1: E = 210 GPa), stainless 1.4301 (EN 10088), copper Cu-DHP (EN 1057) and brasses from the
  Copper Development Association data sheets; padauk, Honduran rosewood and hard maple (modulus of
  elasticity and dried density) from Eric Meier, *The Wood Database* (wood-database.com). Wood varies
  from board to board: tune by ear.
- Tube sizes: common aluminium tube, EN 1057 copper and US EMT conduit (ANSI C80.3) sizes.

`build.json` was written by `python3 -I gen.py > build.json`; edit `gen.py` and run it again to change
the model.
