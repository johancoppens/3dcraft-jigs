# A circular pattern of freeform plates that meet edge to edge is joined at a cost, with no way to keep them apart

Found in solar-cooker at 3DCraft 150f0015. Performance and missing capability.

`repro.json` patterns one petal (a parabolic strip, two quadratic-spline faces, cut by a wedge) 24 times round the
axis; each petal's cut faces lie on its neighbours'. `feature.pattern` joins them ("instances that touch or overlap are
joined into one piece"): one shell of 96 faces, the 48 shared cut faces gone, 2.8 s wall and 6.2 s of CPU to open.
The same petals as two interleaved patterns of 12 (every other petal, then the petals between, as two bodies) open in
2.4 s wall and 3.4 s of CPU. Measured at a load average of 41 on 14 CPUs. In an earlier probe (petals from formula curves,
not in the reproducer) a single pattern with 1 mm gaps between the petals still took 1.8 times as long as the
interleaved pair, so much of the time is the search for touching instances, not only the union.

**Should:** a pattern option that keeps the instances as separate pieces of the body without a boolean (parts of a
dish, slats, fins, petals that are made and riveted separately), or a much cheaper test when the instances only share
faces.

**Impact on the Jig:** the solar cooker builds its petals as two interleaved patterns, so its petal count must be even.

Run: `craft3d-cli run --new '{"units":"mm","tolerance":0.01}' --script repro.json --out ring.3dcraft`, then time
`craft3d-cli info ring.3dcraft`.
