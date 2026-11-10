# Electrical units (V, A, W, h, mAh, Wh) are not known to expressions

Found in cubesat at 3DCraft 150f0015. Missing capability. `frequency.json` shows the same for Hz (loudspeaker-box, tuned-chimes).

A mass budget or a power budget is written in volts, amperes, watts and watt-hours: a solar cell's maximum-power voltage
and current (2.411 V, 0.499 A), a battery cell's charge (3200 mAh) and energy (11.52 Wh). `variable.set` refuses `V`, `A`,
`W` and `h` ("expected an operator ... found `V`"), while `J` and `s` are known. So the CubeSat Jig keeps its power and
energy as plain numbers and names the unit in the output's label ("Peak power ... (W, ...)", "Battery energy (Wh, rated)"),
and the form cannot show them in a unit of the user's choice.

**Should:** the SI electrical units (V, A, W, Ω, C) and the common derived ones (Wh, mAh, h) in expressions and as an
output's `unit`, with their dimensions (W = J/s), as N, J and Pa are.

Run: `craft3d-cli run --new '{"units":"mm"}' --keep-going --script repro.json`: the first five steps cannot be worked out, the sixth is
known.
