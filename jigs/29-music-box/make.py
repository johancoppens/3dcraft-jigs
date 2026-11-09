#!/usr/bin/env python3
"""Writes the tune tables and the per-note pin steps of the music box into build.json.

Input (committed): data/tunes.json, three public-domain tunes written note by note for this Jig.
Output: the `comb_notes`, `tunes` and `notes` table steps; for each tune one sketch of one rectangle per note
(`sketch.rect`, corners read from the `notes` table) with its wrapped extrusion; and per tune one assertion that counts
the pin tips found on the model in the box where each note must be, written here with the note's slot and track as
literals, so a pin or a table row out of place is noticed. The geometry is not computed here: every position is a formula
of the document's variables; only the list of notes is data. A table cannot drive a pattern yet (feedback J-011, J-012),
so the per-note steps are written out here.

The generated blocks are replaced in build.json in place. Runs offline, deterministic, standard library only.
Usage: python3 make.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOX_CHUNK = 26    # notes per assertion: one measure may not exceed 16384 bytes
NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    return 12 * (int(name[1:]) + 1) + NOTE_INDEX[name[0]]


def parse_track(text):
    """Returns [(slot, note), ...] for a NOTE:SLOTS melody, bars separated by |, and the length in slots."""
    slot, out = 0, []
    for token in text.split():
        if token == "|":
            continue
        note, length = token.split(":")
        length = int(length)
        if note != "R":
            out.append((slot, note))
        slot += length
    return out, slot


def seam_slot(occupied, slots):
    """Half-integer slot position so that the drum's sketch seam (x = +-pi R) falls in the largest gap of the tune's slots.

    A wrapped profile may not reach the back of the cylinder: the seam must lie between pins.
    """
    best_start, best_length = 0, -1
    for a, b in zip(occupied, occupied[1:] + [occupied[0] + slots]):
        empty = b - a - 1
        if empty > best_length:
            best_start, best_length = a + 1, empty
    return best_start + (best_length - 1) / 2 + 0.5


def load():
    data = json.loads((HERE / "data" / "tunes.json").read_text())
    comb = data["comb_notes"]
    track_of = {note: i + 1 for i, note in enumerate(comb)}  # 1 is the longest tooth, lowest note
    tunes = []
    first = 1
    for tune in data["tunes"]:
        melody, slots = parse_track(tune["melody"])
        bass, bass_slots = parse_track(tune["bass"])
        if slots != bass_slots:
            raise SystemExit(f"{tune['name']}: melody {slots} slots, bass {bass_slots}")
        notes = sorted(set((slot, track_of[note]) for slot, note in melody + bass))
        by_track = {}
        for slot, track in notes:
            by_track.setdefault(track, []).append(slot)
        gaps = [b - a for slots_list in by_track.values() for a, b in zip(slots_list, slots_list[1:] + [slots_list[0] + slots])
                if len(slots_list) > 1]
        per_track = [len(by_track.get(k, [])) for k in range(1, len(comb) + 1)]
        seam = seam_slot(sorted(set(s for s, _ in notes)), slots)
        tunes.append({"name": tune["name"], "first": first, "count": len(notes), "slots": slots,
                      "min_gap": min(gaps), "seam": seam, "per_track": per_track, "notes": notes})
        first += len(notes)
    return comb, tunes


def table_steps():
    comb, tunes = load()
    out = []
    out.append(["table.set", {"name": "comb_notes", "columns": ["note", "midi"],
                              "rows": [[note, midi(note)] for note in comb]}])
    n = len(comb)
    columns = ["name", "first", "count", "slots", "min_gap", "seam"]
    rows = [[t["name"], t["first"], t["count"], t["slots"], t["min_gap"], t["seam"]] for t in tunes]
    out.append(["table.set", {"name": "tunes", "columns": columns, "rows": rows}])
    note_rows = []
    row = 1
    for t in tunes:
        for slot, track in t["notes"]:
            note_rows.append([row, slot, track])
            row += 1
    out.append(["table.set", {"name": "notes", "columns": ["row", "beat", "track"], "rows": note_rows}])
    return out


def pin_steps():
    comb, tunes = load()
    out = []
    previous = "Drum with gear"
    for number, t in enumerate(tunes, start=1):
        sketch = f"Pin layout {number}"
        out.append(["sketch.create", {"plane": "xy", "name": sketch}])
        for row in range(t["first"], t["first"] + t["count"]):
            x = f"pin_x_{number} + mod(notes[{row}].beat - tunes[{number}].seam, tunes[{number}].slots) * slot_arc_{number}"
            y = f"pin_track_zero + notes[{row}].track * tooth_pitch"
            out.append(["sketch.rect", {"sketch": sketch,
                                        "from": [f"{x} - pin_lead / 2", f"{y} - pin_axial / 2"],
                                        "to": [f"{x} + pin_lead / 2", f"{y} + pin_axial / 2"]}])
        name = f"Pins {t['name']}"
        out.append(["feature.extrude", {"sketch": sketch, "distance": "pin_height", "wrap": "Drum barrel:face(0)",
                                        "join": previous, "name": name, "when": f"tune == {number}"}])
        previous = name
    return out


def assertion_steps():
    """One assertion per tune: a pin tip must lie in the box of every note, with slot and track written as literals."""
    _, tunes = load()
    out = []
    for number, t in enumerate(tunes, start=1):
        chunks = [t["notes"][i:i + BOX_CHUNK] for i in range(0, len(t["notes"]), BOX_CHUNK)]
        for part, chunk in enumerate(chunks, start=1):
            boxes = []
            for slot, track in chunk:
                angle = f"note_angle_zero + {slot} * slot_angle"
                x = f"track_world_zero + {track} * tooth_pitch"
                y = f"pin_tip_radius * sin({angle})"
                z = f"axle_height - pin_tip_radius * cos({angle})"
                boxes.append({"inside": [[f"{x} - note_box_axial", f"{y} - note_box_round", f"{z} - note_box_round"],
                                         [f"{x} + note_box_axial", f"{y} + note_box_round", f"{z} + note_box_round"]]})
            out.append(["assert.add", {"name": f"Every pin stands on its note and beat: {t['name']} ({part} of {len(chunks)})",
                                       "measure": "count",
                                       "of": {"kind": "face", "where": {"all": [{"in": "Drum"}, {"surface": "cylinder"},
                                                                                 {"radius": "pin_tip_radius"}, {"any": boxes}]}},
                                       "eq": str(len(chunk)), "when": f"assembled && tune == {number}"}])
    return out


def replace_block(current, is_block, block):
    indices = [i for i, s in enumerate(current) if is_block(s)]
    if not indices or indices != list(range(indices[0], indices[-1] + 1)):
        raise SystemExit("the generated steps in build.json are missing or not contiguous")
    return current[:indices[0]] + block + current[indices[-1] + 1:]


def main():
    target = HERE / "build.json"
    current = json.loads(target.read_text())
    is_table = lambda s: s[0] == "table.set" and s[1].get("name") in ("comb_notes", "tunes", "notes")
    is_pin = lambda s: (s[0] == "sketch.create" and str(s[1].get("name", "")).startswith("Pin layout")) or \
        (s[0] == "sketch.rect" and str(s[1].get("sketch", "")).startswith("Pin layout")) or \
        (s[0] == "feature.extrude" and str(s[1].get("name", "")).startswith("Pins "))
    current = replace_block(current, is_table, table_steps())
    is_box = lambda s: s[0] == "assert.add" and str(s[1].get("name", "")).startswith("Every pin stands on its note and beat")
    current = replace_block(current, is_pin, pin_steps())
    current = replace_block(current, is_box, assertion_steps())
    target.write_text("[\n" + ",\n".join(json.dumps(s, ensure_ascii=False) for s in current) + "\n]\n")


if __name__ == "__main__":
    main()
