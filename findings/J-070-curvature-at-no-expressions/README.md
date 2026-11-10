# A curvature assertion's `at` takes plain numbers only

Found in dobsonian-telescope at 3DCraft 150f0015. `assert.add` with `measure: curvature` gives "cannot be measured: `at` must be
[x, y, z]" when `at` holds expressions, while plain numbers work. Every other point in the assertions (`pivot` of a transform, `position`,
...) takes expressions. In a Jig the point on a body moves with the parameters, so a curvature check (here, the focal length of a mirror that
tilts with a drive angle) cannot follow it. Workaround in the Jig: keep an unmoved hidden copy of the mirror at the origin and assert on that.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`. The first assertion passes, the second is an error.
