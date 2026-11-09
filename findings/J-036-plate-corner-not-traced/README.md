# `feature.plate` refuses some valid sections of a twisted loft: "the edge across a corner could not be traced"

Found in sliceform at 3DCraft 45233bdc. A loft through seven closed `sketch.curve` sections (rounded squares,
each turned further up the height) is cut by fill sheets in the planes x = c (`feature.pattern`,
`feature.boolean` intersect), slotted by an extruded comb, and each section plated with `feature.plate`
(`side: mid`). Some of these plates fail: "faces: along F37:between[...](0): the edge across a corner could not
be traced within a quarter of the tolerance in 4096 points: the spline through them is still 0.084789 off". The
faces are valid sheets (the sheet body checks valid, and the neighbouring slices plate); the failing corner is
where the slice's side meets its flat foot or rim.

Seen in the Jig's range at tolerance 0.01 mm:
- turns of ±90 deg at the foot and rim (end sections square to the axes), the slice in the plane x = 0 (a mirror
  plane of the end sections), 6.5 mm and 1.5 mm plates (`repro.json`); turning every section 1 deg further
  (`compare-turned.json`) cures the 6.5 mm case;
- a squat tower (180 mm high, 220 mm across corners, 1.5 mm plate) with a twist of -120 deg, outermost slice, no
  symmetry involved.

It should plate a valid section face; if a corner cannot be traced to the tolerance, a looser trace within the
document's tolerance would still be a correct plate.

Reproducer (taken from the Jig with the values of a failing point fixed): `craft3d-cli run --new
'{"units":"mm","tolerance":0.01}' --script repro.json --cmd document.check`; the plate *Birch slice 2* fails.

Workaround in the Jig: the tower is turned by 1 deg as a whole and is at least as high as it is wide; the form's
range was probed at the squarest towers over the whole twist range.
