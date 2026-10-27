#!/usr/bin/env python3
"""The sea kayak's hydrostatics, from 3DCraft's measures:  python3 -I hydro.py [param=value ...]

Opens dist/sea-kayak.3dcraftjig with craft3d-cli (CRAFT3D_CLI, else craft3d-cli on PATH), sets the
parameters given, and asks 3DCraft for the waterline of the hull envelope for the boat's weight
(measure.levelFor: the draft T, the centre of buoyancy, the waterplane and its second moments, all measured
on the exact B-rep) and for the plates' masses and centres (document.measure). From those measures, with the
textbook formulas of naval architecture (Biran & Lopez-Pulido, ch. 2-3), it computes

    KB = the centre of buoyancy's height above the keel      BM = I_T / V (I_T the waterplane's moment about x)
    KM = KB + BM                                             KG = the centre of gravity of boat, paddler, load
    GM = KM - KG

No geometry is computed here: every length, area, volume and moment comes from 3DCraft.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLI = os.environ.get("CRAFT3D_CLI") or shutil.which("craft3d-cli")
SEAT_PAD = 25.0      # mm: the seat pad on the floor
CG_UP = 254.0        # mm: the paddler's centre of gravity above the seat (10 in, Sea Kayaker's convention)
Z_LOAD = 100.0       # mm: the load's centre of gravity above the keel (low in the compartments)


def main():
    values = {}
    for arg in sys.argv[1:]:
        k, v = arg.split("=", 1)
        values[k] = float(v) if v.replace(".", "", 1).isdigit() else v
    steps = []
    if values:
        steps.append(["param.set", {"values": values}])
    steps += [["document.inspect", {}], ["document.measure", {}],
              ["measure.levelFor", {"of": "Hull", "volume": "Vdisp"}]]
    script = os.path.join(HERE, ".hydro-steps.json")
    with open(script, "w") as f:
        json.dump(steps, f)
    try:
        out = subprocess.run([CLI, "run", os.path.join(ROOT, "dist", "sea-kayak.3dcraftjig"), "--script", script],
                             capture_output=True, text=True, check=True).stdout.splitlines()
    finally:
        os.remove(script)
    inspect, measure, level = (json.loads(line) for line in out[-3:])
    var = {v["name"]: v["value"] for v in inspect["variables"]}
    wood = [b for b in measure["bodies"] if b["name"].startswith(("Plank", "Top", "Deck")) and b.get("mass")]
    m_ply = sum(b["mass"] for b in wood)
    z_ply = sum(b["mass"] * b["centroid"][2] for b in wood) / m_ply
    x_ply = sum(b["mass"] * b["centroid"][0] for b in wood) / m_ply

    T = level["offset"]
    V = level["volume"]
    KB = level["centroid"][2]
    LCB = level["centroid"][0]
    sec = level["section"]
    BM = sec["ix"] / V
    KM = KB + BM
    # The glass and the fittings are taken with the plywood's centre of gravity; the paddler sits on a pad on
    # the floor amidships (the keel is at z = 0 there).
    m_boat, m_pad, m_load = var["mBoat"], var["mPad"], var["payload"]
    z_pad = var["tHull"] + SEAT_PAD + CG_UP
    m_tot = m_boat + m_pad + m_load
    KG = (m_boat * z_ply + m_pad * z_pad + m_load * Z_LOAD) / m_tot
    GM = KM - KG
    rows = [
        ("Plywood (kernel, okoume 500 kg/m3)", f"{m_ply:.2f} kg (formula {var['mPly']:.2f} kg)"),
        ("Boat (plywood, glass and epoxy, fittings)", f"{m_boat:.1f} kg"),
        ("Displacement", f"{m_tot:.1f} kg, V = {V / 1e9:.5f} m3"),
        ("Draft T (levelFor)", f"{T:.1f} mm in {level['steps']} steps"),
        ("Waterplane area", f"{sec['area'] / 1e6:.4f} m2"),
        ("Wetted surface (below the waterline)", f"{level['surface'] / 1e6:.3f} m2"),
        ("KB, BM, KM", f"{KB:.1f}, {BM:.1f}, {KM:.1f} mm"),
        ("KG (boat, paddler, load)", f"{KG:.1f} mm"),
        ("GM", f"{GM:.1f} mm"),
        ("LCB (centre of buoyancy, x)", f"{LCB:.0f} mm"),
        ("Plywood's centre of gravity", f"x {x_ply:.0f} mm, z {z_ply:.1f} mm"),
        ("Freeboard amidships", f"{var['Zmid'] - T:.1f} mm"),
    ]
    for k, v in rows:
        print(f"| {k} | {v} |")


if __name__ == "__main__":
    main()
