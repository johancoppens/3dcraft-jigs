# `distance` reports the gap to the surface for a body or face that lies inside another body

Found in solar-cooker at 3DCraft 150f0015. Bug (or a definition the command's summary does not state).

A 20 × 20 × 4 mm block lying wholly inside a 100 × 100 × 10 mm plate is reported at `distance` 3 mm from the plate,
and so is its top face, although the two share their whole volume. A body that pokes through the plate's surface is at
0. **Should:** a body, or a face, inside another body is at distance 0 from it (as `clearance` and `overlap` would say),
or the summary says that `distance` is measured between the surfaces.

**Impact on the Jig:** a petal set moved 2 mm down into the hub ring was not caught when the check measured from the
petals' inner end faces (each end face then lay wholly inside the 3 mm ring, 1.3 mm from its nearest surface, which
the other, unmoved set's 0.3 mm hid). The Jig measures from the petal bodies, which cross the ring's surface, and
measures each petal set apart.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`; both outputs say 3 mm.
