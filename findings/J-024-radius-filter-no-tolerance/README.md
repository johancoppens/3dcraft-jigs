# A sketch arc's radius drifts after re-solves, and a `radius: {min}` filter has no tolerance to absorb it

Found in cubesat at 3DCraft 45233bdc. Bug (or missing tolerance).

The CubeSat rail is an extruded L section whose three outer corners are arcs of radius `rail_edge_radius` = 1 mm,
drawn with `sketch.path` (centres and ends given by expressions). CDS 2.2.7 asks for rail edges rounded to at least
1 mm, so an assertion counts the rail's cylinder faces with `"radius": {"min": "1 mm"}`. After the form factor is
changed back and forth (the sketch re-solved at another `half_width`, then the first again), the count drops from 3 to
2, then to 1, then back to 3. `select.query` with `context` still prints `"radius": 1.0`: the radius has drifted a few
ulps below 1 mm, and the `{min}` bound is compared without any tolerance, while an `eq` bound gets one by default.

**Should:** an arc whose radius is given stays at that radius after a re-solve (to the last bit, or at least within
the document's tolerance), and `{min, max}` bounds on `radius` (and the other filters) are matched within the
document's tolerance as `eq` is, as `thickness` already is.

**Workaround in the Jig:** the bound is `0.999 mm` ("1 mm less 0.001 mm"), and the README says so.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`: the six filtered `select.query` summaries read 3, 3,
2, 2, 1, 3 faces where 3 is right throughout (half_width goes 50 → 113.15 → 50 → 50 → 113.15 → 50 mm); the last,
unfiltered query with `context` finds the three faces and prints each radius as 1.0.
