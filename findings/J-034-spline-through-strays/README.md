# A spline through points strays between them far more than a cubic interpolant does

Found in planetary-gearbox at 3DCraft 150f0015. Bug (or a weak fit).

`repro.json` draws one involute flank of a 14-tooth, module 2 gear (base radius 13.155697 mm, roll angle 0 to 0.745)
twice: as a live `sketch.spline` through eight points of the involute, evenly spaced in the roll angle, and as a
`sketch.curve` of the same formula (fitted to 8.5e-6 mm). Each is closed to a sector and extruded, and one ray at the
polar angle of roll angle 0.57 is cast through each (`measure.ray`). The curve is met at 15.14277 mm, the involute's
own radius there; the spline at 15.16171 mm, 0.019 mm further out (about 0.009 mm normal to the flank). A clamped
cubic B-spline interpolating the same eight points (chord-length or uniform parameters, averaged knots) stays within
0.0006 mm of the involute everywhere (our own calculation). With five points the live spline strays 0.031 mm, with six
0.018 mm (normal distance, rays every few hundredths of a radian), against 0.003 mm for a cubic interpolant of five.

**Should:** a spline through points as close to a smooth curve through them as a standard cubic interpolant, or the
parametrisation and end conditions documented so a caller can place its points to suit them.

**Impact:** the planetary gearbox's flanks were live splines through eight points; at five points (to save load time)
the mesh gap of a 14-tooth module-2 sun fell to 0.033 mm against the 0.085 mm designed, failing its assertion. The
flanks are now three circular arcs through seven involute points (within 1.8 µm of it, and seven times cheaper to
measure; see J-065). The gear-reducer reports the same effect for five points (mesh gap −20 to +9 %).

Run: `craft3d-cli run --new '{"units":"mm","tolerance":0.01}' --script repro.json`: the last two lines are the rays;
the exit face of each body gives the radius.
