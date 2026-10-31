#!/usr/bin/env python3
"""Writes the planetary gearbox assembly (python3 -I gen.py): 01-planetary-gearbox.json, the command
batch that builds dist/planetary-gearbox.3dcraftasm, and check.json, what scripts/asm.py checks on it.

The assembly places the bodies of the planetary-gearbox Jig (dist/planetary-gearbox.3dcraftjig) as
instances: the ring, the carrier, the sun and three planets, each picked by the feature that made it.
Every instance starts where the Jig puts it, and the mates hold it there: their frames are circular
edges of the bodies, which the Jig turns with the body, so a mate's zero is the Jig's own tooth phase.

    ring     fixed to the world (its outer circle at z = 0, turned by the Jig's rTurn)
    carrier  revolute about the world z axis (its output shaft's top edge)
    sun      revolute on the carrier (the sun's bore edge against the carrier's shaft edge)
    planet k revolute on the carrier's pin k (the planet's bore edge against the pin's foot edge)

The meshes are gear couplings, each between two of these joints, so every angle is measured from the
carrier: the sun's turn on the carrier s and planet k's turn on its pin p_k mesh as s + (Zp / Zs) p_k = 0
(an external pair), and planet k rolls in the fixed ring as p_k + (Zr / Zp) c = 0, c being the
carrier's turn (an internal pair, whose ring turns by -c relative to the carrier). The timeline t
drives the sun on the carrier: s = 360 deg * t. Willis' formula follows from the two meshes, it is not
written into the model: the solve turns the carrier by c = s Zs / Zr, so the sun's turn on the
housing, s + c, is (1 + Zr / Zs) c.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JIG = "dist/planetary-gearbox.3dcraftjig"
OUT = "dist/planetary-gearbox.3dcraftasm"

# Persistent names of the edges the mates use, in the Jig's own bodies (document.edges on the Jig;
# the names do not depend on the parameters, only on the Jig's features).
RING_OUTER = "F13:copy(0)/F6:startEdge(e15)"            # the ring's outer circle at z = 0
SUN_BORE = "F2:startEdge(e15)"                          # the sun's bore at z = 0
CARRIER_TOP = "F23:between[F23:copy(1)/F22:face(0),F23:copy(1)/F22:face(2)]"   # output shaft, top edge
PIN_FOOT = [                                            # carrier pin k, its circle at z = 0
    "F23:between[F23:copy(0)/F21:copy(1)/F20:copy(0)/F19:copy(1)/F17:face(0),F23:copy(0)/F21:copy(1)/F20:copy(0)/F19:copy(1)/F17:face(1)]",
    "F23:between[F23:copy(0)/F21:copy(1,1,1)/F17:face(0),F23:copy(0)/F21:copy(1,1,1)/F17:face(1)]",
    "F23:between[F23:copy(0)/F21:copy(1,2,1)/F17:face(0),F23:copy(0)/F21:copy(1,2,1)/F17:face(1)]",
]
PLANET_BORE = ["F7:copy(0)/F4:startEdge(e15)", "F8:copy(0)/F4:startEdge(e15)", "F9:copy(0)/F4:startEdge(e15)"]
N = 3                                                   # the assembly has three planets


def build():
    s = [
        ["assembly.new", {"units": "mm", "tolerance": 0.001}],
        # Sources are read relative to the working directory and kept relative to the assembly's
        # file, so the file is saved first.
        ["file.save", {"path": OUT}],
        # The Jig's public parameters, held by the assembly and passed to every instance, so the
        # mates' offsets and phases below follow the same values (the Jig's defaults).
        ["variable.set", {"name": "moduleSize", "expr": "4"}],
        # Copies of the Jig, at its defaults: the module of moduleSize 4 (its table `modules`), and below
        # the carrier's 0.5 mm gap and 4 mm shaft. Only Zs, ringStep, w and backlash may be changed here (the
        # Jig's assembly conditions permitting); another moduleSize would misplace the carrier's joint.
        ["variable.set", {"name": "module", "expr": "1.5 mm"}],
        ["variable.set", {"name": "Zs", "expr": "12"}],
        ["variable.set", {"name": "ringStep", "expr": "0"}],
        # The ring's teeth as the Jig works them out for 3 planets (Nq = 3): 48 for a sun of 12.
        ["variable.set", {"name": "Zr", "expr": "Zs + 2 * (17 + mod(-Zs - 17, 3)) + 6 * ringStep"}],
        ["variable.set", {"name": "w", "expr": "10 mm"}],
        ["variable.set", {"name": "backlash", "expr": "0.1 mm"}],
        # As the Jig works them out.
        ["variable.set", {"name": "Zp", "expr": "(Zr - Zs) / 2"}],
        ["variable.set", {"name": "pTurn", "expr": "if(mod(Zp, 2) == 0, 180 deg / Zp, 0 deg)"}],
        ["variable.set", {"name": "rTurn", "expr": "if(mod(Zp, 2) == 0, 180 deg / Zr, 0 deg)"}],
        ["variable.set", {"name": "tc", "expr": "max(3 mm, 2 * module)"}],
        # The carrier's output shaft ends 0.5 mm (the Jig's gap) + two arms' thickness + 4 mm above
        # the gears.
        ["variable.set", {"name": "zTop", "expr": "w + 0.5 mm + 2 * tc + 4 mm"}],
        # Normal backlash: each flank is thinned by backlash / 4 on the pitch circle.
        ["variable.set", {"name": "jn", "expr": "backlash * cos(20 deg)"}],
    ]
    params = {"moduleSize": "moduleSize", "N": "3", "Zs": "Zs", "ringStep": "ringStep", "w": "w", "backlash": "backlash"}
    for name, body, colour in (("Ring", "Ring", None), ("Carrier", "Carrier", None), ("Sun", "Sun", None)):
        s.append(["instance.add", {"source": JIG, "body": body, "name": name, "params": params}])
    for k in range(N):
        s.append(["instance.add", {"source": JIG, "body": "Planet%d" % (k + 1), "name": "Planet%d" % (k + 1), "params": params}])
    # Every frame below has its axis along +z, as the world's z: flip keeps it so (a mate otherwise
    # puts b's frame against a's, facing it).
    s.append(["mate.add", {"kind": "fixed", "name": "RingHeld", "a": "world/z", "b": "Ring/" + RING_OUTER,
                           "angle": "rTurn", "flip": True}])
    s.append(["mate.add", {"kind": "revolute", "name": "Output", "a": "world/z", "b": "Carrier/" + CARRIER_TOP,
                           "offset": "zTop", "flip": True}])
    s.append(["mate.add", {"kind": "revolute", "name": "SunOnCarrier", "a": "Carrier/" + CARRIER_TOP,
                           "b": "Sun/" + SUN_BORE, "offset": "-zTop", "flip": True}])
    for k in range(N):
        # Planet k sits at 120 deg k round the sun, turned by pTurn + 120 deg k (Zs + Zp) / Zp; its
        # pin's edge is turned by 120 deg k with the carrier's pattern.
        s.append(["mate.add", {"kind": "revolute", "name": "Pin%d" % (k + 1), "a": "Carrier/" + PIN_FOOT[k],
                               "b": "Planet%d/%s" % (k + 1, PLANET_BORE[k]),
                               "angle": "pTurn + %d * 360 deg / 3 * Zs / Zp" % k, "flip": True}])
    for k in range(N):
        s.append(["coupling.add", {"kind": "gear", "name": "SunPlanet%d" % (k + 1), "mates": ["SunOnCarrier", "Pin%d" % (k + 1)],
                                   "value": "Zp / Zs"}])
        s.append(["coupling.add", {"kind": "gear", "name": "PlanetRing%d" % (k + 1), "mates": ["Pin%d" % (k + 1), "Output"],
                                   "value": "Zr / Zp"}])
    s += [
        ["variable.set", {"name": "t", "expr": "0"}],
        ["variable.set", {"name": "SunOnCarrier_angle", "expr": "360 deg * t"}],
        # The carrier's turn, measured: planet 1's centre (the centroid of its mid-plane section; a
        # gear is symmetric about its axis) goes round the sun with the carrier.
        ["variable.measure", {"name": "p1x", "measure": "sectionCentroid", "of": "Planet1", "plane": "xy", "offset": "w / 2", "axis": "x"}],
        ["variable.measure", {"name": "p1y", "measure": "sectionCentroid", "of": "Planet1", "plane": "xy", "offset": "w / 2", "axis": "y"}],
        ["variable.output", {"name": "carrierTurn", "expr": "atan2(p1y, p1x)"}],
        # Willis: the sun turns s + c on the housing and the carrier c; (s + c) / c = 1 + Zr / Zs,
        # so c = s Zs / Zr. Compared as an angle difference, wrapped to (-180, 180] deg.
        ["variable.output", {"name": "willisError", "expr": "abs(atan2(sin(carrierTurn - SunOnCarrier_angle * Zs / Zr), cos(carrierTurn - SunOnCarrier_angle * Zs / Zr)))"}],
        ["assert.add", {"name": "Carrier turns as Willis' formula says (sun on housing / carrier = 1 + Zr / Zs)",
                        # 0.01 deg is 3.9 um at planet 1's centre (22.5 mm out); the assembly solves to
                        # its tolerance of 1 um, so a much tighter bound would test the solver's rounding.
                        "measure": "value", "expr": "willisError", "max": "0.01 deg"}],
        ["assert.add", {"name": "Sun and planet 1 mesh with the backlash (0.3 to 0.7 jn)", "measure": "clearance",
                        "from": "Sun", "to": "Planet1", "min": "0.3 * jn", "max": "0.7 * jn"}],
        ["assert.add", {"name": "Planet 1 and the ring mesh with the backlash (0.3 to 0.7 jn)", "measure": "clearance",
                        "from": "Planet1", "to": "Ring", "min": "0.3 * jn", "max": "0.7 * jn"}],
        ["assert.add", {"name": "No part overlaps another", "measure": "overlap",
                        "of": ["Ring", "Carrier", "Sun", "Planet1", "Planet2", "Planet3"], "is": False}],
        ["document.info", {"title": "Planetary gearbox (assembly)",
                           "description": "The planetary-gearbox Jig's sun, three planets, ring and carrier as an assembly: "
                                          "revolute joints, the meshes as gear couplings, the sun driven by the timeline t; "
                                          "Willis' formula and the backlash checked over the motion.",
                           "author": "3DCraft Jigs", "licence": "CC-BY-4.0", "tags": ["assembly", "gears", "planetary", "motion"]}],
        ["assembly.pack", {}],
        ["file.save", {"path": OUT}],
    ]
    return s


def check():
    """What scripts/asm.py runs on the built assembly and judges (see that script)."""
    return {
        "file": OUT,
        "at_rest": {"dof": 0, "identity": ["Ring", "Carrier", "Sun", "Planet1", "Planet2", "Planet3"]},
        "motion": [
            # A whole turn of the sun on the carrier (a quarter turn of the carrier), 65 moments.
            {"t": [0, 1], "samples": 65},
            # One sun tooth on the carrier (1 / Zs of t): the meshes' whole cycle, 33 moments.
            {"t": [0, 1.0 / 12], "samples": 33},
        ],
        "traces": [
            # The sun's turn on the housing, independently of the model's own measure: a corner of
            # its tooth outline, and planet 1's bore centre (the carrier).
            {"name": "Sun tooth", "point": "Sun/F2:startVertex(e4,e8)", "samples": 65},
            {"name": "Planet 1 centre", "point": "Planet1/" + PLANET_BORE[0], "samples": 65},
        ],
        "willis": {"sun": "Sun tooth", "carrier": "Planet 1 centre", "ratio": 1 + 48 / 12.0, "tol_deg": 0.01},
        "renders": [0, 0.25, 0.5],
        "replay": {"frames": 49},
    }


def main():
    with open(os.path.join(HERE, "01-planetary-gearbox.json"), "w") as f:
        f.write("[\n" + ",\n".join(json.dumps(c) for c in build()) + "\n]\n")
    with open(os.path.join(HERE, "check.json"), "w") as f:
        json.dump(check(), f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
