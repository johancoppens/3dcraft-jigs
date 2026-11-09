# extent, boxMin and boxMax measure bodies only, not faces

**Kind:** missing capability. **Found in:** `cubesat`. **3DCraft:** the pinned commit (`tools/pin.json`).

**What happens.** `measure: "extent"` with a face query as `of` (the cone of a countersink) is refused: *cannot be
measured: extent is of bodies; the subject names faces of `Countersunk`*.

**What should happen.** The size of a face's box along an axis, like a body's. It is the natural way to read a feature's
size off the model: a countersink's diameter and depth, a pocket's length, a slot's width, a flange's height. Distances
between faces cover some of these, but not the size of a single face.

**Reproducer.** `craft3d-cli run --new '{"units":"mm"}' --script repro.json --keep-going`: a plate with a Ø2.2 hole
countersunk to Ø4.4. Both assertions should pass with 4.4 mm and 1.1 mm; both are refused.

**Impact on the Jig: workaround.** The cubesat draws the rail screws' heads (a 90° cone at the theoretical Ø4.4 of
ISO 7046-1) flush with the rail face, and asserts with `overlap` that they do not cut into the rail. This proves more
than two extents would, so the Jig would keep it; the gap matters for checks where no part can be drawn in the hole.
