# `cut.list` and `cut.export` cannot be given a named set, so every rod and tube in a design lands on the cut sheet

Found in orrery at 3DCraft 45233bdc. Missing capability (see J-003 and J-010).

In `repro.json` a 1 mm plate is the part to laser cut and a 1/8 in rod is bought stock. `cut.list` lists the rod as
a plate 60 mm thick (a cylinder is a prism along its axis), so `cut.export` draws it on the sheet. The way to leave it
out, `bodies`, takes only a list of names, and refuses a body switched off by `when` (J-003); a named set, which
follows the options, is refused: "`bodies` must be a list of bodies".

**Should:** `cut.list` and `cut.export` take a named set (or a filter, such as a material or a thickness) for the
bodies to cut, so that a design with stock rod, tube and turned parts can export only its sheet parts, whatever its
options.

**Impact on the orrery:** every rod, tube, pillar and bush is given a chamfer at its ends (real deburring, but done
so that `cut.list` calls it "not a plate"); the cut file is then every 1 mm brass part, with the form's kerf. Without
the chamfers its 7 tubes, 5 rods and the pillars would be drawn as rings and discs on the brass sheet.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`: the cut list's second row is the rod; the export
is refused.
