# A valid plate is refused: "face 0 cannot be tessellated: its loops do not bound a region"

Found in sliceform at 3DCraft 150f0015, by `check-range`. One slice of a sliceform ball (a sphere section,
1.5 mm thick, slotted by twelve 1.5 mm slots from the top down to the sphere's centre) fails in `feature.plate`:
"thickness: the plate cannot be meshed to see whether it passes through itself (face 0 cannot be tessellated: its
loops do not bound a region: the boundary crosses itself in parameter space)". The section face it is made from
is a valid sheet; exported, its outline is 13 circular arcs and 36 lines without a crossing.

It depends on where the slices fall, not on the document's tolerance (0.005, 0.01 and 0.02 mm fail alike): with
the same sizes the plate is made at a kerf of 0.3 mm or 0.2 mm (other slice positions), and a small script that
rebuilds only that one section, comb and plate from the exported positions also passes. It should mesh any
valid plate, or say what in the face it cannot mesh.

Reproducer: the Jig's own script with the point's values set (235 steps): `craft3d-cli run --new
'{"units":"mm","tolerance":0.01}' --script repro.json`; the plate *Birch slice 11* fails and `document.check`
reports it.

Impact in the Jig: found twice by check-range, both times on the slice next to the outermost of a 600 mm ball 570 mm
high whose section is a whole circle clear of the floor (a 6.5 mm and a 1.5 mm walnut sheet, kerf 0.3 and 0.4
mm). The ball's height is now limited so that every slice reaches the flat foot, and the kerf range ends at 0.3 mm.
The cause in 3DCraft is not known; it did not depend on the document's tolerance.
