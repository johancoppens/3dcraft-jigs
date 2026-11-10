# face.appearance on a feature is lost when the body goes through feature.boolean or feature.transform

Found in dobsonian-telescope at 3DCraft 150f0015. A tube's inner wall is given a colour with `face.appearance` right after
its extrude; a port is then cut with `feature.boolean` and the tube moved with `feature.transform`. The inner wall renders
in the body's colour instead (the tube comes out white inside, with `face.png` showing it). Giving the same colour on the
transformed feature's name (`Tube:copy(0)/F2:side(e4)`) keeps it. It should survive, or the command should refuse or
warn; compare F-048 in the examples' feedback, which is about a later inactive feature, not an active one.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`, then look at face.png.

At numbering (J-040) this was re-diagnosed: without the `body.appearance` on `Moved` the colour survives the boolean and
the transform (`no-body-colour.json`), and a `body.appearance` on the extrude itself keeps it too (`same-feature.json`).
What hides the face colour is a body colour given on a later feature.
