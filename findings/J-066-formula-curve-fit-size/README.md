# A formula curve that a low-degree spline draws exactly is fitted with dozens of cubic points

Found in solar-cooker at 3DCraft 150f0015. Performance; see the examples' [F-010](https://github.com/johancoppens/3dcraft-examples/blob/main/3DCRAFT-FEEDBACK.md#f-010)
(formula curves fit many control points).

`sketch.curve` with `x = t^2 / (4 * focal)`, `y = t` (a parabola, a polynomial of degree 2) is fitted as a cubic
B-spline of 35 control points at a document tolerance of 0.01 mm and 48 at the default, with a deviation of about
1e-6 mm either way, although a quadratic B-spline of 3 control points is the parabola exactly. Twelve strips
extruded from two such curves and patterned cost 0.91 s of CPU to open (0.40 s wall); the same strips from
`sketch.spline` of degree 2 with the exact control points cost 0.16 s (0.17 s wall), 5.7 times less, with the same
volume and area to 1e-8. Measured on a busy reference machine (load average 38).

**Should:** a formula that is a polynomial in t (or a rational one) is drawn as the exact B-spline of its degree, or
the fit stops at the document's tolerance rather than far below it.

**Impact on the Jig:** the solar cooker's petals are drawn as exact quadratic splines with control points written
as formulas (the back face as the offset control polygon), which made the Jig 2.6 times cheaper to open than with
`sketch.curve`. The petal template, whose outline is an arc-length function, stays a `sketch.curve`.

Run: `craft3d-cli run --new '{"units":"mm","tolerance":0.01}' --script repro.json` and look at `fit` in the two
`sketch.curve` results; time `craft3d-cli info` on the saved file with either half of the script.
