# An output used only by assertions cannot be kept off the form's outputs

Found in solar-cooker at 3DCraft 45233bdc. Missing capability (agent and user friction).

An assertion that combines several measures (a distance and a box side, a focus found from two rings) needs each
measure as an output (`variable.measure`), and every output is listed with the form's results (`output.list`, the
Parameters tab). `repro.json` defines two such helper outputs, used only by one assertion; both are listed beside
what a maker wants to read. In the solar cooker 45 of 70 outputs were such helpers before the review folded them into
assertions with their own measures.

**Should:** an output can be marked internal (a `hidden` or `public: false` flag on `variable.measure` and
`variable.output`), so it is computed and usable by assertions and other outputs but not shown in the form's results.

**Impact on the Jig:** the solar cooker now measures inside the assertions wherever one measure proves the point, so
its 32 outputs are all for the maker; two assertions still read outputs a maker can use too (the light's margin inside
the pot and the centre of mass).

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`; `output.list` lists *Check: plate to lug* and
*Check: lug's left side*.
