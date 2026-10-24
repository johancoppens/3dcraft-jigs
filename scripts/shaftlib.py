"""Shared by the gen.py of gt2-pulley and spur-gear: a shaft bore (round, D-shaft or keyway) and set
screws (grub screws) with optional captive-nut slots, as 3DCraft commands.

The part is a solid of revolution about the z axis with a hub; the caller says where the hub is. Every
option is a conditional feature (feature.when) whose condition is a derived variable, so the same flags
also serve the caller's assertions:

  flatOn   the bore has a D flat (bore type 2)
  keyOn    the bore has a keyway (bore type 3, and a bore of at least twice the key's width that leaves
           a wall under the teeth)
  scrOn    one set screw (needs the hub); scr2On a second one, 90 deg round
  nutOn    a captive-nut slot behind each screw (when the hub has room for it)

The flat, the keyway and the first screw face +x: the screw presses on the flat or on the key.
"""

# DIN 6885-1 parallel keys: the hub's keyway width b and depth t2 by shaft diameter.
KEYS = [
    ("up to 8 mm", 2, 1.0), ("8 to 10 mm", 3, 1.4), ("10 to 12 mm", 4, 1.8), ("12 to 17 mm", 5, 2.3),
    ("17 to 22 mm", 6, 2.8), ("22 to 30 mm", 8, 3.3), ("30 to 38 mm", 10, 3.3),
]
KEY_ROW = "1 + (bore > 8 mm) + (bore > 10 mm) + (bore > 12 mm) + (bore > 17 mm) + (bore > 22 mm) + (bore > 30 mm)"

# Metric set screws (ISO 4026/4027) and their hex nuts (ISO 4032): the hole for a screw that cuts its own
# thread in a print (tap), the clearance hole when a nut holds it, the nut's width across flats and height.
SCREWS = [("M2.5", 2.1, 2.8, 5.0, 2.0), ("M3", 2.5, 3.3, 5.5, 2.4), ("M4", 3.3, 4.4, 7.0, 3.2)]
NUT_FIT = 0.3  # play round a nut in its printed slot


def tables():
    return [
        ["table.set", {"name": "keys", "columns": ["shaft", {"name": "b", "unit": "mm"}, {"name": "t2", "unit": "mm"}],
                       "rows": [list(r) for r in KEYS]}],
        ["table.set", {"name": "screws", "columns": ["screw", {"name": "tap", "unit": "mm"}, {"name": "clear", "unit": "mm"},
                                                     {"name": "nutAF", "unit": "mm"}, {"name": "nutM", "unit": "mm"}],
                       "rows": [list(r) for r in SCREWS]}],
    ]


INPUTS = [
    ("boreType", "1"),
    ("flatDepth", "0.5 mm"),
    ("setScrew", "1"),
    ("screwSize", "2"),
    ("screwCount", "1"),
    ("nut", "0"),
]


def variables(hub_d, hub_on, root_r):
    """Derived variables. hub_d: the hub's outside diameter (expression); hub_on: whether the hub is
    built; root_r: the radius the keyway must stay under (with a wall)."""
    return [
        ("hubOD", hub_d),
        ("keyRow", KEY_ROW),
        ("keyW", "keys[keyRow].b"),
        ("keyT", "keys[keyRow].t2"),
        ("flatOn", "boreType == 2"),
        # A keyway only where it leaves a wall of 0.8 mm under the teeth and in the hub.
        ("keyOn", "boreType == 3 && bore >= 2 * keyW && bore / 2 + keyT <= %s - 0.8 mm"
                  " && (!%s || bore / 2 + keyT <= hubOD / 2 - 0.8 mm)" % (root_r, hub_on)),
        ("nutW", "screws[screwSize].nutAF + %g mm" % NUT_FIT),
        ("nutT", "screws[screwSize].nutM + %g mm" % NUT_FIT),
        # The nut sits as close to the bore as a 1.2 mm wall (and the keyway) allows.
        ("nutIn", "bore / 2 + 1.2 mm + if(keyOn, keyT, 0 mm)"),
        ("scrOn", "setScrew && %s && hubOD / 2 - bore / 2 >= 1.5 mm" % hub_on),
        ("scr2On", "scrOn && screwCount == 2"),
        ("nutOn", "scrOn && nut && hubOD / 2 >= nutIn + nutT + 1 mm"),
        ("scrD", "if(nutOn, screws[screwSize].clear, screws[screwSize].tap)"),
    ]


def hub_d_min():
    """The least hub diameter that holds the keyway and a nut slot (a range for the hub's diameter)."""
    return ("max(bore + 4 mm + if(boreType == 3, 2 * keyT, 0 mm), "
            "if(setScrew && nut, 2 * (nutIn + nutT + 1 mm), 0 mm))")


def hub_l_min(base):
    """The least hub length that holds a screw, or a nut slot reaching past the screw's axis."""
    return "if(setScrew, if(nut, 2 * (nutW / sqrt(3) + 1 mm), max(%s, scrD + 2 mm)), %s)" % (base, base)


def steps(bore_z0, bore_h, scr_z, nut_z0, nut_h, target, name):
    """The cutting tool and the subtraction of it from target, ending in the feature `name`.

    bore_z0, bore_h: where the bore tool starts along z and how long it is (past both ends);
    scr_z: the screws' axis height; nut_z0, nut_h: the nut slots' z range (from past the hub's open end
    to just past the screw's axis)."""
    s = []
    s.append(["feature.cylinder", {"name": "BoreTool", "radius": "bore / 2", "height": bore_h,
                                   "position": ["0 mm", "0 mm", bore_z0]}])
    # D flat: a slab cut from the bore tool leaves material in the bore.
    s.append(["feature.block", {"name": "FlatTool", "size": ["bore", "2 * bore", "%s + 2 mm" % bore_h],
                                "position": ["bore / 2 - flatDepth", "-bore", "%s - 1 mm" % bore_z0]}])
    s.append(["feature.when", {"feature": "FlatTool", "expr": "flatOn"}])
    s.append(["feature.boolean", {"op": "subtract", "target": "BoreTool", "tool": "FlatTool", "name": "BoreD"}])
    # Keyway: a slot joined to the bore tool (a little shorter, so their ends do not coincide).
    s.append(["feature.block", {"name": "KeyTool", "size": ["bore / 2 + keyT", "keyW", "%s - 1 mm" % bore_h],
                                "position": ["0 mm", "-keyW / 2", "%s + 0.5 mm" % bore_z0]}])
    s.append(["feature.when", {"feature": "KeyTool", "expr": "keyOn"}])
    s.append(["feature.boolean", {"op": "union", "target": "BoreD", "tool": "KeyTool", "name": "BoreK"}])
    # Set screw along +x, from the axis out through the hub, with its nut slot open at the hub's end.
    s.append(["feature.cylinder", {"name": "ScrewHole", "radius": "scrD / 2", "height": "hubOD / 2 + 1 mm",
                                   "position": ["0 mm", "0 mm", scr_z], "axis": [1, 0, 0]}])
    s.append(["feature.block", {"name": "NutSlot", "size": ["nutT", "nutW", nut_h],
                                "position": ["nutIn", "-nutW / 2", nut_z0]}])
    s.append(["feature.when", {"feature": "NutSlot", "expr": "nutOn"}])
    s.append(["feature.boolean", {"op": "union", "target": "ScrewHole", "tool": "NutSlot", "name": "Screw1"}])
    s.append(["feature.when", {"feature": "ScrewHole", "expr": "scrOn"}])
    s.append(["feature.when", {"feature": "Screw1", "expr": "scrOn"}])
    s.append(["feature.transform", {"source": "Screw1", "angle": "90 deg", "axis": [0, 0, 1], "keep": True,
                                    "name": "Screw2"}])
    s.append(["feature.when", {"feature": "Screw2", "expr": "scr2On"}])
    s.append(["feature.boolean", {"op": "union", "target": "BoreK", "tool": "Screw1", "name": "CutA"}])
    s.append(["feature.boolean", {"op": "union", "target": "CutA", "tool": "Screw2", "name": "Cut"}])
    s.append(["feature.boolean", {"op": "subtract", "target": target, "tool": "Cut", "name": name}])
    return s


def publish(group, order0, hub_param):
    """The parameters of the bore and the set screws, in group (the bore) and "Set screw"."""
    p = [
        dict(name="boreType", label="Bore type", group=group, order=order0, kind="choice",
             choices=["Round", "D-shaft", "Keyway"],
             description="Round; D-shaft (a flat that a set screw presses on); or a keyway to DIN 6885 sized from "
                         "the bore (from 4 mm, when the part has room for it)"),
        dict(name="flatDepth", label="D-flat depth", group=group, order=order0 + 1, min="0.2 mm",
             max="max(0.2 mm, bore / 4)", step="0.05 mm", unit="mm",
             description="How deep the flat of a D-shaft is (5 mm motor shafts: 0.5 mm, 4.5 mm across the flat)"),
        dict(name="setScrew", label="Set screw", group="Set screw", order=1, kind="boolean",
             description="A grub screw through the %s onto the shaft (on the flat or the key)" % hub_param),
        dict(name="screwSize", label="Screw size", group="Set screw", order=2, kind="choice", choicesFrom="screws",
             description="The hole is the tap size (the screw cuts its own thread), or the clearance size with a nut"),
        dict(name="screwCount", label="Screws", group="Set screw", order=3, kind="integer", min="1", max="2",
             description="One screw, or two at 90 deg"),
        dict(name="nut", label="Captive nut", group="Set screw", order=4, kind="boolean",
             description="A slot for a hex nut behind each screw, open at the end of the hub: push the nut in, then "
                         "drive the screw through it"),
    ]
    return [["variable.publish", x] for x in p]
