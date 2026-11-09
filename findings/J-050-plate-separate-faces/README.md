# `feature.plate` refuses a sheet of separate faces

Found in sliceform at 3DCraft 45233bdc. A fill sheet repeated by `feature.pattern` and intersected with a solid
gives the solid's sections, one face per pattern instance, in one body. Giving all of them to one
`feature.plate` is refused: "faces: the faces do not hang together across shared edges: plate each piece apart".

It should plate each connected piece on its own and give one lump per piece (as `feature.pattern` itself keeps
separate instances in one body), so that a family of laser-cut layers or slices is one feature whatever its
count. Today a design whose count is a parameter needs one `feature.plate` per possible piece, each switched by
`feature.when` (the sliceform has 24, the layered rhino of 3DCraft Examples 15), and one literal face name per
piece.

Reproducer: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`; the last step fails.
