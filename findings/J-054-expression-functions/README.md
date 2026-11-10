# An expression cannot define a function, so a formula used per instance is written once per instance

Found in sundial at 3DCraft 150f0015. Missing capability.

A design that applies one formula to many inputs (the hour lines of a dial, the teeth of a gear, the stars of a
catalogue, the rungs of a ladder) has to write the formula again for every input: `hour_09`, `hour_10`, `hour_11`
in the reproducer, each the same expression with another number. There is no named function with an argument
(`hour_line(k)` is refused: "invalid character '('") and no local name inside an expression, so a sub-expression
used twice in one formula is written twice (the sundial's distance from the root to the chapter ring repeats its
`b` term). With a pattern that has no index to read a table with (J-011), each instance also needs its own sketch
entity.

**Should:** a variable that takes arguments (`hour_line(k) = atan2(sin(lat) * sin(15 deg * (k - 12)), ...)`, used as
`hour_line(9)`), or a `let` inside an expression; together with a pattern index (J-011) one formula and one seed would
draw every instance.

**Impact on the sundial:** 23 hour lines and 22 half-hour ticks carry 6 and 3 variables each (204 of the Jig's 363
variables) and one polyline each, and the numerals' 53 letters one polyline each, all of them the same few formulas with
another hour in them. Workaround: the formulas are written out per hour in `build.json`.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json` (the last step is refused).
