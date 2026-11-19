# A clearance of bodies found 0.05 mm apart cannot be measured: the kernel's interference check stalls on them

Found in rc-wing at 3DCraft `c7cab24f` (0.2.0), by `tools/jigs.py check`. Bug (a limit of 0.2.0).

`repro.json` is the Jig's `build.json` without its last step, then point 37 of its range check (a corner: 2000 mm
span, 167 and 113 mm chords, 30° sweep, 6° washout, 11 ribs of 4 mm sheet, spar choice 6), the clearance its
assertion *Spars clear of the ribs* takes for the bottom spar, and the distance between the same bodies. Run it at the
Jig's tolerance:

    craft3d-cli run --new '{"units":"mm","tolerance":0.01}' --keep-going --script repro.json

or, from the repository's root, on the published Jig:

    craft3d-cli run jigs/23-rc-wing/rc-wing.3dcraftjig --keep-going \
      --cmd param.set --params '{"values": {"camber_choice": "1", "covering": "2", "flying_weight": "4200 g", "rib_count": "11", "rib_sheet": "4 mm", "root_chord": "167 mm", "spar_choice": "6", "sweep_angle": "29.999999999999996 deg", "thickness_digits": "9", "tip_chord": "113 mm", "washout": "6 deg", "wing_span": "2000 mm"}}' \
      --cmd measure.clearance --params '{"from": "Bottom spar", "to": "Ribs"}' \
      --cmd measure.distance --params '{"from": "Bottom spar", "to": "Ribs"}'

On 3DCraft 0.2.0 the clearance fails: "whether `Bottom spar` and `Ribs` overlap cannot be told: their nearest places
found are 0.0499997457 mm apart, but only 0 mm is proven, within twice the tolerance, where the kernel tells clear
from touch and overlap, and it could not: boolean does not support this: marching an intersection curve stalled (the
surfaces are nearly tangent along it, or one of them has a crease) (face 3 of the first body, face 44 of the second
body)". The distance gives 0.04999975 mm with `atLeast` 0: the spar's side face against a rib's flat face at the slot
floor, where the Jig leaves a 0.05 mm glue gap. 3DCraft 0.1.3 passes the Jig's assertion there with 0.049999 mm found
and 0 proven: it took a gap found above twice the tolerance (0.02 mm) as clear without asking the kernel. The answer
should be `clear`, with the gap proven, or at least an answer from the interference check.

What was tried to make it smaller: the two bodies written to STEP and read into a new document at the same tolerance.
The ribs come in as 11 bodies (`Ribs` is one body of 11 lumps in the Jig), and the spar is `clear` of each with about
0.0475 mm proven (0.912 mm for the two outer ribs), so it does not reproduce that way. At the default tolerance (1e-6
mm) the script answers `clear`, with 0.00015 mm proven.

At the 8 points of the range check where it happens (listed in the Jig's `meta.json`, `range_known`), the nearest
places are 0.05 mm apart at a slot floor, or 0.027 to 0.031 mm at a slot wall: the spar's fit in its slot, which the
Jig's own assertion 9 holds to its designed value.
