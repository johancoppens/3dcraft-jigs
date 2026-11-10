# Measuring a flat gear costs about 1.5 ms per tooth, far more than building it

Found in orrery at 3DCraft 150f0015. Performance.

`repro.json` draws one gear of 120 teeth (four segments a tooth: root arc, flank, tip arc, flank), extruded 1 mm, and
measures its volume. On the developer's machine (shared, load average about 30): building and opening it without
measures takes 0.05 s of CPU for eight such gears; `craft3d-cli info` of the same eight (volume, area, centroid of
each body) takes 1.4 to 1.9 s of CPU; with circular-arc flanks instead of lines, 2.2 s. A `volume` assertion on them
costs the same again (2.2 s for eight gears, 3.9 s for the orrery's 31). The body is a prism: its volume is the
thickness times the area of a plane region bounded by lines and arcs, which has a closed form (Green's theorem), and its
area and centroid likewise.

**Should:** the volume, area and centroid of a body bounded by planes, cylinders and other analytic faces computed in
closed form (or at least in time near the build's), so that a model of many gears can be opened and measured quickly.

**Impact on the orrery:** about 5 of its 8 to 10 s of load CPU (on the busy machine) is `info` measuring its 35 gears
(about 1 700 teeth); the closed-form area check is kept to two gears, and a mass output was dropped. A `distance`
between the top faces of two meshing gears (to show them level and engaged) costs about 0.6 s of CPU each, 10 s for
the orrery's 18 meshes; the Jig measures each pair's `extent` along z instead. Workaround: none
for the load; fewer teeth by default (largest period error 0.06 % rather than the least).

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json --out gear.3dcraft`, then time
`craft3d-cli info gear.3dcraft` against `craft3d-cli run gear.3dcraft --cmd document.inspect --params '{"measures":false}'`.
