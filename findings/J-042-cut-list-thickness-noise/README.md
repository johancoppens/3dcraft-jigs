# `cut.list` prints a turned plate's thickness with rounding noise

Found in solar-cooker at 3DCraft 150f0015. Bug (cosmetic).

A 3 mm plate turned by 40° (`feature.transform`) is listed as `3.000000000000014` mm thick; in the solar cooker the
tilted hub ring is listed as `3.0000000000001705`. A shop reads the thickness to choose the sheet, and a csv with such
numbers does not group with other 3 mm parts in a spreadsheet. **Should:** thickness (and length, width) rounded to the
document's tolerance, as `groups` presumably compares them.

**Impact on the Jig:** cosmetic; the cut list of the solar cooker's plates shows the hub ring's thickness so.

Run: `craft3d-cli run --new '{"units":"mm"}' --script repro.json`.
