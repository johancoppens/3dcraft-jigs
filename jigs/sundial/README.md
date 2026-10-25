# Sundial for your place

A sundial that tells the time where it stands: a **horizontal garden dial**, or a **vertical wall dial**,
also on a wall that does not face due south (a *declining* dial). Pick a place from the table or give your
own latitude and longitude; the hour lines are shifted by the **longitude correction**, so the dial reads
the clock time of your time zone instead of local solar time. Two flat parts, cut from one sheet or
printed: the dial plate with the hour lines, half-hour ticks and Roman numerals (engraved, or cut through
as a stencil), and the gnomon, a right triangle whose sloping edge, the **style**, lies along the Earth's
axis. The gnomon stands in two slots on two tabs, so it is set at the right angle without measuring.
Licence: CC-BY-4.0.

| Parameter | Group | Default | Range |
|---|---|---|---|
| Dial | Dial | horizontal (garden) | horizontal (garden) / vertical (wall) |
| Wall declination | Dial | 0° | -50° to 50°, step 0.5° (west positive; wall dial only) |
| Time shown | Dial | clock time (standard time) | clock time / local solar time |
| Place | Place | Gent | 23 places from the table `places`, or Custom |
| Latitude | Place | 51.05° | 25° to 65° N (Custom only) |
| Longitude | Place | 3.72° | within 30° of the zone's meridian, east positive (Custom only) |
| Time zone meridian | Place | 15° | -180° to 180°, step 7.5° (Custom only) |
| Dial size | Size | 200 mm | 120 to 400 mm (disc diameter, or side of the square wall plate) |
| Plate thickness | Size | 4 mm | 3 to 10 mm (dial and gnomon from the same sheet) |
| Slot clearance | Size | 0.15 mm | 0 to 0.5 mm |
| Lines cut through | Lines | off | engraved / cut through |
| Engraving depth | Lines | 1 mm | 0.2 to 3 mm (at most half the plate) |
| Hour numerals | Lines | on | on / off |

**Places** (table `places`: latitude, longitude, the meridian of the standard time zone): Brussel, Gent,
Antwerpen, Leuven, Brugge, Liege, Hasselt, Amsterdam, Rotterdam, Utrecht, Groningen, Maastricht,
Luxembourg, Paris, London, Berlin, Madrid, Rome, Stockholm, Reykjavik, New York, San Francisco, Tokyo.
Northern hemisphere only.

## The formulas

All of them are variables of the document (`document.inspect` shows their values). φ is the latitude,
D the wall's declination (0 for a wall facing due south, positive towards the west), t the clock hour.

```text
longitude correction   dlon = longitude - zone meridian       (clock time; 0 for solar time)
                       the sun is due south 4 minutes earlier for every degree east of the meridian
hour angle             H = 15° (t - 12) + dlon                 negative in the morning

horizontal dial        style height SH = φ,  substyle along the noon line (north)
                       tan θ = sin φ · tan H                   hour line θ from the noon line
vertical, south        SH = 90° - φ,  substyle straight down
                       tan θ = cos φ · tan H
vertical, declining    sin SH = cos φ · cos D                  style height
                       tan SD = sin D / tan φ                  substyle from the downward vertical
                       tan H0 = tan D / sin φ                  the substyle's hour angle ("difference in longitude")
                       tan θ' = sin SH · tan (H - H0)          hour line θ' from the substyle
```

The declining dial is built as a horizontal dial for the latitude SH, turned by SD, with the hours counted
from H0: the general construction of a plane dial in Waugh and Rohr; the horizontal and the south-facing
dial are its special cases (D = 0). On the dial the direction of an hour line is
`cos(H - H0) · s + sin SH · sin(H - H0) · n`, with s along the substyle and n square to it towards the
afternoon, so the lines before 6 and after 18 o'clock (on a horizontal dial) come out on the right side of
the root without a special case.

**Which hours.** A line is drawn for the hours the sun can shine on the dial: up at midsummer
(`|H| <= acos(-tan φ · tan 23.44°)`, capped at 125°) and, on a wall, where the sun at the equinox is in
front of it (`|H - H0| <= 90°`; in winter it reaches a little beyond, in summer it leaves a little before).
At Gent the horizontal dial runs from 5 to 20 h (standard time), a south wall from 7 to 18 h.

**A thick gnomon.** A gnomon of thickness T has two styles, its two sloping edges, T apart. The morning
lines start from the root on one side of the gnomon, the afternoon lines from the other, so the dial is in
effect split along the substyle by the gnomon's thickness (Waugh, Rohr). An hour that falls exactly on the
substyle (12 h on a garden or south-wall dial in solar time, or with the longitude on the zone's meridian)
gets a line on both sides of the gnomon. The lines start a little away from the root (where neighbours are
two line widths apart) and end before the numerals. A line that would pass within 1 mm of a gnomon slot
(the lines nearest the substyle) starts beyond the far slot instead, so no cut ever opens into a slot and the
gnomon stays tight.

**Numerals** are Roman (IIII for four, as on most dials), their tops pointing outwards on a garden dial and
towards the root on a wall dial; they are as large as the narrowest gap between two hour lines allows (at
most 6 % of the dial), and left out where that is under 3.5 mm.

## Checked on the model

The assertions check the built geometry against an **independent construction**: the vector form of the
sundial. In the world frame (x east, y north, z up) the polar axis is `G = (0, cos φ, sin φ)` (on a wall
dial its southern half, `-G`), the dial plane has the normal `N` ((0, 0, 1), or `(-sin D, -cos D, 0)` for
a wall), the sun at hour angle H (at the equinox) is `S = (-sin H, -cos H sin φ, cos H cos φ)`, and the
shadow of the style on the dial runs along `L = (S·N) G - (G·N) S`. Nothing of the textbook formulas
above is used there.

- **The style makes the latitude angle with the dial** (horizontal dial; 90° - φ on a south wall, SH on a
  declining wall): the gnomon's top lies `Ls · tan SH` above the dial face, with `tan SH` from
  `G·N / |G projected on the dial|` (boxMax z, within 0.005 mm).
- **The gnomon lies on the substyle**, the polar axis projected on the dial: its box in x and y is that of a
  plate T thick along that direction (four assertions within 0.005 mm). On a horizontal dial this is the
  noon line: the gnomon spans exactly ±T/2 east and west of the root.
- **Every hour line lies where the shadow of the polar axis falls**: the four walls of hour line t's groove
  lie inside the box spanned by its two ends on the line `root ± T/2 + r · L(H)`, widened only by half the
  line width (0.02 mm to spare): a line turned by more than about 0.02° fails. With local solar time the 6
  and 18 h lines of a horizontal dial lie on the east-west line through the root and the 12 h line along the
  gnomon, as these boxes then require.
- **The high end of the style is on the polar axis**: the gnomon has its two top corners at
  `root + Ls · (substyle) + Ls · tan SH` above the face (a vertex count in a 0.1 mm box), so it cannot
  stand the wrong way round.
- **Fit:** the gnomon's tabs reach through the dial (boxMin z = 0), no parts overlap (the slots are
  clearance wider and longer than the tabs), no line, tick or numeral comes within 1 mm of a slot (a
  distance assertion), the gnomon stands on the plate, the rim of the dial is whole (its extent is the dial
  size), and there are the parts there should be.

`check-range` passes 106 of 106 points (64 corners, every choice and every place, 16 random), also with `--deep`.

## Making it

**Laser or CNC.** File › Export… as DXF or SVG with the face set **Cut sheet**: the dial plate and the
gnomon at true size. With engraved lines it holds the dial's outline and the two slots; with the lines cut
through, the dial with every cut. For engraved lines, the face set **Engraving** holds the dial's face: the
outline and slots again, and inside them the openings of the lines, ticks and numerals to engrave. Both are
seen from the front and the dial comes first in both, with the same outline, so the two files line up at
the same origin: engrave the inner shapes of the Engraving file, then cut the Cut sheet. (Or cut the lines
as a stencil and back the dial with a plate of another colour.) The slots are
`clearance` wider and longer than the tabs; add your kerf to the clearance if your software does not
compensate it, for instance:

```sh
craft3d-cli run dist/sundial.3dcraftjig \
  --cmd param.set --params '{"values": {"place": "Leuven", "size": "250 mm"}}' \
  --cmd file.export --params '{"path": "sundial-cut.svg", "set": "Cut sheet"}' \
  --cmd file.export --params '{"path": "sundial-engrave.svg", "set": "Engraving"}'
```

**3D printing.** STL or 3MF: print the dial flat, the gnomon on its side.

With engraved lines the dial is two bodies in the model, a dark base and the brass face as deep as the
engraving, so the lines show dark; print it in two colours (3MF carries them), or as one part.

## Setting it up

1. **Horizontal dial:** set it level (a spirit level on the plate, in two directions). **Wall dial:** fix it
   flat on the wall with its top edge level; the style points down and out, to the south celestial pole.
2. **Turn it to true north**, not magnetic north: the gnomon's high end points north (towards the
   Pole Star), the root south. Use the magnetic declination for your place with a compass, or set it by the
   sun: at local solar noon, `12:00 - 4 min × (longitude - zone meridian) + the table value below` in
   standard time (Gent: about 12:45 CET, 13:45 CEST, give or take the table), the shadow of a plumb line
   falls due north-south. For a wall dial, measure the wall's declination
   the same way before you build it.
3. **Reading it:** the shadow edge of the style gives standard time, corrected for your longitude. Add one
   hour in summer time, and correct for the **equation of time** (the sun runs up to 16 minutes ahead of or
   behind the clock over the year):

| Month | 1st | 15th |
|---|---|---|
| Jan | +3 | +9 |
| Feb | +13 | +14 |
| Mar | +13 | +10 |
| Apr | +4 | +0 |
| May | -3 | -4 |
| Jun | -3 | +0 |
| Jul | +3 | +6 |
| Aug | +7 | +5 |
| Sep | +0 | -5 |
| Oct | -10 | -14 |
| Nov | -16 | -15 |
| Dec | -11 | -5 |

Minutes to add to the dial's reading to get clock (standard) time; within about a minute in any year
(Spencer's Fourier series, as NOAA gives it).

## Sources

- Albert E. Waugh, *Sundials: Their Theory and Construction*, Dover, 1973: horizontal, vertical and
  declining dials, style height, substyle, difference in longitude, thick gnomons, longitude correction.
- René R. J. Rohr, *Sundials: History, Theory, and Practice*, Dover, 1996: the same formulas and the
  construction of a declining dial as a horizontal dial for another latitude.
- British Sundial Society, *Sundial Glossary* (sundialsoc.org.uk), and the North American Sundial Society
  (sundials.org): terms (style, substyle, root, declination) and setting a dial up.
- NOAA Global Monitoring Laboratory, *General Solar Position Calculations*, after J. W. Spencer, *Fourier
  series representation of the position of the sun*, Search 2 (5), 1971: the equation of time.

The geometry is written from these formulas; no code was taken from anywhere.

## Notes

- The wall dial is shown lying on its back, face up; turn it upright in your mind (its +y is up the wall).
- Latitudes are limited to 25° to 65° N: nearer the equator the style gets too flat for a horizontal dial,
  nearer the pole the summer sun circles the sky and the dial needs every hour. Wall declinations are
  limited to ±50°: beyond it the style becomes very low and the lines crowd.
- The dial reads standard time with the equation of time left out (see the table); with *local solar
  time* it reads the sun's own time, with noon along the gnomon.
