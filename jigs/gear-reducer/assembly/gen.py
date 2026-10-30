#!/usr/bin/env python3
"""Writes the gear reducer assembly (python3 -I gen.py): 01-gear-reducer.json, the command batch that
builds dist/gear-reducer.3dcraftasm, and check.json, what scripts/asm.py checks on it.

The assembly places bodies of the gear-reducer Jig at its default parameters
(dist/gear-reducer.3dcraftjig): the rear half of the housing, the three shafts and the four gears, each
an instance that picks the body by the feature that made it. Every instance starts where the Jig puts
it, and the mates hold it there:

    housing  fixed to the world (its input bearing seat's edge on the world z axis)
    shaft k  revolute in the housing (a circle of the shaft against its bearing seat's edge)
    gear k   fixed to its shaft (a circle of its hub against one of the shaft's)
    stage 1  gear coupling between shaft 1 and shaft 2, ratio z2 / z1
    stage 2  gear coupling between shaft 2 and shaft 3, ratio z4 / z3

A mate's frame on a circular edge has its origin at the circle's centre and its x axis where the
circle starts; the Jig draws every circle here from +x and turns a body with its shaft's angle, which
at the defaults is 0 for every gear (63 and 49 teeth are odd: the Jig turns a wheel half a pitch only
for an even count). So a mate's zero is the Jig's own tooth phase, and the couplings start from it.
The edges and their heights were read from the Jig's bodies (document.edges); the offsets are the
differences of those heights along the shafts. The check proves the result: at rest every instance is
exactly where the Jig puts it.

The timeline t drives the input shaft: 360 deg * t, one turn. The output's turn is measured on the
model (the centroid of the output shaft's section through its keyway lies 0.68 mm off the axis, opposite
the key) and asserted against the closed form z1 z3 / (z2 z4) from the Jig's tooth counts; the tooth
clearances and that nothing overlaps are asserted too, and scripts/asm.py checks them over the motion.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JIG = "dist/gear-reducer.3dcraftjig"
OUT = "dist/gear-reducer.3dcraftasm"

# The Jig at its defaults (target ratio 10, pinions 18 and 17 teeth, modules 1.5 and 2.5 mm): its tooth
# counts z_1 to z_4 and centre distances a12 = mn_1 (z_1 + z_2) / 2, a34 = mn_3 (z_3 + z_4) / 2.
Z = {1: 18, 2: 63, 3: 17, 4: 49}

# Bearing seat edges of the housing's rear half (half circles at the seat's lower end), by shaft, with
# their height z.
SEAT = {
    1: ("F214:between[F214:copy(0)/F190:copy(1)/F174:face(0),F214:copy(0)/F190:copy(1)/F174:face(1)]", -14.5),
    2: ("F214:between[F214:copy(0)/F192:copy(1)/F176:face(0),F214:copy(0)/F192:copy(1)/F176:face(1)]", -16.5),
    3: ("F214:between[F214:copy(0)/F194:copy(1)/F178:face(0),F214:copy(0)/F194:copy(1)/F178:face(1)]", -19.5),
}
# A circle of each shaft near its lower bearing, with its height.
SHAFT = {
    1: ("F69:copy(0)/F45:between[F45:copy(0)/F39:side(e13),F45:copy(0)/F39:side(e14)]", -16.0),
    2: ("F118:copy(0)/F92:between[F92:copy(0)/F75:side(e11),F92:copy(0)/F75:side(e12)]", -18.0),
    3: ("F156:copy(0)/F132:between[F132:copy(0)/F126:side(e14),F132:copy(0)/F126:side(e15)]", -21.0),
}
# Gear k on shaft s: the top circle of its hub, and a circle of the shaft, with their heights.
SEAT_GEAR = {
    1: (1, "F9:copy(0)/F8:between[F8:copy(0)/F4:copy(1)/F3:face(0),F8:copy(0)/F4:copy(1)/F3:face(2)]", 24.0,
        "F69:copy(0)/F45:between[F45:copy(0)/F39:side(e18),F45:copy(0)/F39:side(e19)]", 24.0),
    2: (2, "F18:copy(0)/F17:between[F17:copy(0)/F13:copy(1)/F12:face(0),F17:copy(0)/F13:copy(1)/F12:face(2)]", 24.0,
        "F118:copy(0)/F92:between[F92:copy(0)/F75:side(e15),F92:copy(0)/F75:side(e16)]", 0.0),
    3: (2, "F28:copy(0)/F27:between[F27:copy(0)/F23:copy(1)/F22:face(0),F27:copy(0)/F23:copy(1)/F22:face(2)]", 58.0,
        "F118:copy(0)/F92:between[F92:copy(0)/F75:side(e16),F92:copy(0)/F75:side(e17)]", 58.0),
    4: (3, "F37:copy(0)/F36:between[F36:copy(0)/F32:copy(1)/F31:face(0),F36:copy(0)/F32:copy(1)/F31:face(2)]", 58.0,
        "F156:copy(0)/F132:between[F132:copy(0)/F126:side(e20),F132:copy(0)/F126:side(e21)]", 58.0),
}
# The output shaft's keyway (for its feather key, 34.2 to 51.8 mm up): a section at mid height.
KEYWAY_Z = "43 mm"


def mm(x):
    return "%g mm" % x


def build():
    s = [
        ["assembly.new", {"units": "mm", "tolerance": 0.001}],
        ["file.save", {"path": OUT}],
        ["variable.set", {"name": "z1", "expr": str(Z[1])}],
        ["variable.set", {"name": "z2", "expr": str(Z[2])}],
        ["variable.set", {"name": "z3", "expr": str(Z[3])}],
        ["variable.set", {"name": "z4", "expr": str(Z[4])}],
        ["variable.set", {"name": "mn1", "expr": "1.5 mm"}],
        ["variable.set", {"name": "mn3", "expr": "2.5 mm"}],
        # The output shaft's axis: x = a12 + a34.
        ["variable.set", {"name": "x3", "expr": "mn1 * (z1 + z2) / 2 + mn3 * (z3 + z4) / 2"}],
        # The Jig's backlash jt = 0.12 mm on the pitch circle; normal backlash jn = jt cos 20 deg.
        ["variable.set", {"name": "jn", "expr": "0.12 mm * cos(20 deg)"}],
        ["variable.set", {"name": "ratio", "expr": "z2 / z1 * z4 / z3"}],
        ["instance.add", {"source": JIG, "body": "HousingTop", "name": "Housing"}],
    ]
    for k in (1, 2, 3):
        s.append(["instance.add", {"source": JIG, "body": "Shaft_s%d" % k, "name": "Shaft%d" % k}])
    for k in (1, 2, 3, 4):
        s.append(["instance.add", {"source": JIG, "body": "Gear_%d" % k, "name": "Gear%d" % k}])
    # Every edge here has its axis along +z, as the world's z: flip keeps it so (a mate otherwise
    # puts b's frame against a's, facing it). The offset is b's height over a's along that axis.
    s.append(["mate.add", {"kind": "fixed", "name": "HousingHeld", "a": "world/z", "b": "Housing/" + SEAT[1][0],
                           "offset": mm(SEAT[1][1]), "flip": True}])
    for k in (1, 2, 3):
        s.append(["mate.add", {"kind": "revolute", "name": "Shaft%d" % k, "a": "Housing/" + SEAT[k][0],
                               "b": "Shaft%d/%s" % (k, SHAFT[k][0]), "offset": mm(SHAFT[k][1] - SEAT[k][1]), "flip": True}])
    for g, (sh, gedge, gz, sedge, sz) in SEAT_GEAR.items():
        s.append(["mate.add", {"kind": "fixed", "name": "Keyed%d" % g, "a": "Shaft%d/%s" % (sh, sedge),
                               "b": "Gear%d/%s" % (g, gedge), "offset": mm(gz - sz), "flip": True}])
    s += [
        # External gears turn opposite ways: shaft1 + (z2 / z1) shaft2 = 0.
        ["coupling.add", {"kind": "gear", "name": "Stage1", "mates": ["Shaft1", "Shaft2"], "value": "z2 / z1"}],
        ["coupling.add", {"kind": "gear", "name": "Stage2", "mates": ["Shaft2", "Shaft3"], "value": "z4 / z3"}],
        ["variable.set", {"name": "t", "expr": "0"}],
        ["variable.set", {"name": "Shaft1_angle", "expr": "360 deg * t"}],
        # The output's turn, measured on the model: the section's centroid lies opposite the keyway,
        # which the Jig cuts along +x of the shaft at rest.
        ["variable.measure", {"name": "c3x", "measure": "sectionCentroid", "of": "Shaft3", "plane": "xy", "offset": KEYWAY_Z, "axis": "x"}],
        ["variable.measure", {"name": "c3y", "measure": "sectionCentroid", "of": "Shaft3", "plane": "xy", "offset": KEYWAY_Z, "axis": "y"}],
        ["variable.output", {"name": "outputTurn", "expr": "atan2(-c3y, -(c3x - x3))"}],
        # Two external meshes: the output turns the input's way, by the input's turn over the ratio.
        ["variable.output", {"name": "ratioError", "expr": "abs(atan2(sin(outputTurn - Shaft1_angle / ratio), cos(outputTurn - Shaft1_angle / ratio)))"}],
        ["assert.add", {"name": "Output turns at z1 z3 / (z2 z4) of the input", "measure": "value",
                        "expr": "ratioError", "max": "0.001 deg"}],
        ["assert.add", {"name": "The output's keyway is where the angle is measured from (0.3 mm off the axis or more)",
                        "measure": "value", "expr": "hypot(c3x - x3, c3y)", "min": "0.3 mm"}],
        ["assert.add", {"name": "Stage 1 meshes with the backlash (0.3 to 0.7 jn)", "measure": "clearance",
                        "from": "Gear1", "to": "Gear2", "min": "0.3 * jn", "max": "0.7 * jn"}],
        ["assert.add", {"name": "Stage 2 meshes with the backlash (0.3 to 0.7 jn)", "measure": "clearance",
                        "from": "Gear3", "to": "Gear4", "min": "0.3 * jn", "max": "0.7 * jn"}],
        ["assert.add", {"name": "No part overlaps another", "measure": "overlap",
                        "of": ["Housing", "Shaft1", "Shaft2", "Shaft3", "Gear1", "Gear2", "Gear3", "Gear4"], "is": False}],
        ["document.info", {"title": "Two-stage gear reducer (assembly)",
                           "description": "The gear-reducer Jig's housing, shafts and gears as an assembly at its defaults: "
                                          "revolute shafts, gears keyed to them, the meshes as gear couplings, the input "
                                          "driven by the timeline t; the output's ratio and the backlash checked over the motion.",
                           "author": "3DCraft Jigs", "licence": "CC-BY-4.0", "tags": ["assembly", "gears", "reducer", "motion"]}],
        ["assembly.pack", {}],
        ["file.save", {"path": OUT}],
    ]
    return s


def check():
    return {
        "file": OUT,
        "at_rest": {"dof": 0, "identity": ["Housing", "Shaft1", "Shaft2", "Shaft3", "Gear1", "Gear2", "Gear3", "Gear4"]},
        "motion": [
            # One turn of the input, 65 moments (5.6 deg apart: about a quarter of a pinion tooth).
            {"t": [0, 1], "samples": 65},
            # One tooth of pinion 1 (1 / z1 of a turn): stage 1's whole mesh cycle, 33 moments.
            {"t": [0, 1.0 / Z[1]], "samples": 33},
            # One tooth of pinion 3 (z2 / (z1 z3) of a turn): stage 2's whole mesh cycle, 33 moments.
            {"t": [0, Z[2] / float(Z[1] * Z[3])], "samples": 33},
        ],
        "renders": [0, 0.125, 0.25],
        "replay": {"frames": 49},
    }


def main():
    with open(os.path.join(HERE, "01-gear-reducer.json"), "w") as f:
        f.write("[\n" + ",\n".join(json.dumps(c) for c in build()) + "\n]\n")
    with open(os.path.join(HERE, "check.json"), "w") as f:
        json.dump(check(), f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
