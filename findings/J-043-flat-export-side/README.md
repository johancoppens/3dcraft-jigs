# `cut.export` cannot be told which face of a plate is its front, so a plate facing −y comes out mirrored

Found in sundial (review) at 3DCraft 150f0015. Missing capability, or a bug in the choice of face.

A plate standing upright with its front towards −y (a wall plate, a sign) is extruded from a datum plane through
[0, 0, 0], [50, 0, 0], [0, 0, 50]; its hole lies at x = +30 seen from the front. `file.export` of the set *Front*
(its end cap) draws the hole at the right, as seen from the front (`face.svg`: hole centre at x = 80 of a 100 mm sheet).
`cut.list` takes the plate's other face as its top, and `cut.export` draws the hole at the left (`cut.svg`: x = 20):
the mirror image. For a symmetric part it does not matter; for a part with an engraving or a marking on its front it
does, since the cut outline and the engraving no longer line up.

**Should:** `cut.export` (and `cut.list`'s `top`) take a face or a direction that is the part's front, or follow the
side a named set or the part's sketch shows; at least say in the result which side is drawn.

**Impact on the sundial:** a kerf-compensated cut file from `cut.export` was mirrored on every wall dial, so the
slots came out on the mirror of the substyle. Workaround: the kerf is in the bodies themselves (`feature.offsetProfile`
by half the kerf before the extrusions), and the cut sheet is a named set of the plate's front face and the gnomon's
side, which `file.export` draws from the front.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json` and compare `face.svg` with `cut.svg`.

# A set of back faces exports mirrored, so a part with chamfered front edges has no true outline to export

Found in sundial (review) at 3DCraft 150f0015. Missing capability.

A plate standing upright with its front towards −y is extruded from a datum plane through [0, 0, 0], [50, 0, 0],
[0, 0, 50], with a hole at x = +30 seen from the front. `file.export` of the set *Front* (its end cap) draws the hole at
x = 80 of the 100 mm sheet (`face.svg`), as seen from the front. The set *Back* (its start cap) draws it at x = 20
(`back.svg`): each face is drawn from its own outside, so the back face comes out as the mirror image of the front.

That leaves no way to export a plate's true outline once its front edges are broken. A chamfer or a round on the
front edges shrinks the front face, so its set no longer gives the outline the laser must follow. The back face still has
the full outline, but it comes out mirrored against the front, and against an engraving on the front. The sundial
therefore leaves its plate and gnomon square in the model and tells the maker to break the edges by hand.

**Should:** `file.export` of a face set takes a view direction (or "as seen from the front of this face"), so a back face
can be drawn the right way round; or a body's outline (its silhouette, or its section at a plane) seen along a
direction exports as a sheet. Related: F-086 (`cut.list` and `cut.export` refuse a plate with broken edges) and J-007 (a
named set cannot export a sketch, which would give the outline directly).

**Impact on the sundial:** cosmetic; the cut edges are not chamfered in the model. **Workaround:** the cut sheet is the
plate's front face and the gnomon's side; the README tells the maker to break the edges with a file, keeping the styles
sharp.

Run: `craft3d-cli run --new '{"units":"mm"}' --script back-face.json`, then compare `face.svg` with `back.svg`.
