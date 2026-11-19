# A wheel's clearance on its shaft cannot be measured where the keyway lies exactly on the shaft's axis

Found in gear-reducer at 3DCraft `c7cab24f` (0.2.0), by `tools/jigs.py check`. Bug: a known limitation of 3DCraft
0.2.0, written up there as owed (`docs/design/booleans.md` › *Contact refused where a curve lies exactly on a face's
border*; the release notes, *Known limitations*).

`repro.json` is the Jig's `build.json` without its last step, then the point of the range check where it happens
(`param.set`: ratio 8, 1500 rpm, uniform load, 42CrMo4, 0.5 kW, a 10 mm wall, *Machined parts*) and the two clearances
its assertions take. Run it at the Jig's tolerance:

    craft3d-cli run --new '{"units":"mm","tolerance":0.01}' --keep-going --script repro.json

or, from the repository's root, on the published Jig:

    craft3d-cli run jigs/31-gear-reducer/gear-reducer.3dcraftjig --keep-going \
      --cmd param.set --params '{"values": {"cast_wall": "10 mm", "driven_machine": "1", "gear_steel": "2", "input_angle": "2862 deg", "input_power": "0.5", "input_speed": "1500", "ratio_wanted": "8", "show": "4"}}' \
      --cmd measure.clearance --params '{"from": "Wheel 2", "to": "Intermediate shaft"}' \
      --cmd measure.clearance --params '{"from": "Wheel 4", "to": "Output shaft"}'

On 3DCraft 0.2.0 both `measure.clearance` steps fail: "an imprinted curve that does not fit the edges it should
coincide with (at the edge of tolerance)" (wheel 2 on the intermediate shaft) and "a curve that is partly on and
partly off a face boundary (at the edge of tolerance)" (wheel 4 on the output shaft). Each wheel's bore sits on its
seat by design: the answer should be `touch`, which is what 3DCraft 0.1.x gives for the same Jig at the same point. At
the default tolerance (1e-6 mm, `--new '{"units":"mm"}'`) the same script answers `touch`.

3DCraft found the cause: since 0.2.0 a point held at a value is exactly that value, so the keyway's slot is centred
exactly on the shaft's axis, the keyed shaft has one more edge and vertex, and the contact check cannot place a curve
that lies exactly on that face's border. The bodies are right; the check owes the answer. 3DCraft's workshop keeps a
reduction of two bodies and one command made from this Jig.
