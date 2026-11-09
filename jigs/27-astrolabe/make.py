#!/usr/bin/env python3
"""Writes the star table of the astrolabe's rete into build.json.

Input (committed): data/bright-stars.tsv, 36 stars from the Yale Bright Star Catalogue (5th revised edition,
Hoffleit & Warren, J2000.0 positions; see the README for how they were chosen), named by the IAU Catalog of Star Names.
Output: the `stars` table step of build.json: star name, right ascension and declination in degrees, `root`, the
fraction of the Capricorn radius where the pointer's root sits on the rete, `boss`, the fraction where the boss on its
stem sits, `key`, the character on that boss (the README's key), and `near`, the row of the nearest other boss (for the
document's spacing assertion). Layout rules of this file, not catalogue data: the root is the nearest of the rete's rings
along the star's own direction, at least 0.06 of the Capricorn radius from the tip, on which a boss can be placed; a boss
lies on the stem, at least 0.19 of the Capricorn radius from the centre (clear of the rule's boss, 0.142, and so of the
pin), clear of every star tip and of every boss placed before it (brightest first). The script stops if a star has no place.

Runs offline, deterministic, no dependencies beyond the standard library. Usage: python3 make.py
"""
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OBLIQUITY = 23.4393      # degrees, as in the model
HUB = 0.10               # hub outer radius, fraction of the Capricorn radius
RIM_ROOT = 0.97          # the rete's rim band, centre line
ECLIPTIC_BAND = 0.04     # width of the ecliptic ring, inward from the true ecliptic
MIN_STEM = 0.06
BOSS = 0.032             # radius of the boss on a stem, fraction of the Capricorn radius
KEYS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
BOSS_MIN_RADIUS = 0.19   # clear of the rule's boss (0.055 of the diameter, 0.142 of the Capricorn radius) and the pin
TIP_CLEAR = BOSS + 0.012
BOSS_CLEAR = 2 * BOSS + 0.012


def hms(text):
    return 15.0 * (float(text[0:2]) + float(text[2:4]) / 60 + float(text[4:]) / 3600)


def dms(text):
    sign = -1 if text[0] == '-' else 1
    return sign * (float(text[1:3]) + float(text[3:5]) / 60 + float(text[5:7]) / 3600)


def tand(a):
    return math.tan(math.radians(a))


def rows():
    equator = 1.0 / tand(45 + OBLIQUITY / 2)
    cancer = equator * tand(45 - OBLIQUITY / 2)
    centre = (1.0 - cancer) / 2                    # ecliptic centre, on +x at sidereal time zero
    radius = (1.0 + cancer) / 2
    stars = []
    for row in csv.DictReader(open(HERE / 'data' / 'bright-stars.tsv'), delimiter='\t'):
        ra, dec = hms(row['ra_j2000']), dms(row['dec_j2000'])
        tip = equator * tand(45 - dec / 2)
        a = math.radians(ra)
        ux, uy = -math.sin(a), math.cos(a)         # star direction at sidereal time zero
        ring = radius - ECLIPTIC_BAND / 2
        b = -centre * ux
        c = centre * centre - ring * ring
        candidates = [HUB - 0.02, RIM_ROOT]
        disc = b * b - c
        if disc > 0:
            for sign in (-1, 1):
                t = -b + sign * math.sqrt(disc)
                if t > 0:
                    candidates.append(t)
        stars.append(dict(name=row['name'], ra=ra, dec=dec, tip=tip, ux=ux, uy=uy,
                          roots=sorted((t for t in candidates if abs(t - tip) >= MIN_STEM), key=lambda t: abs(t - tip))))
    tips = [(s['tip'] * s['ux'], s['tip'] * s['uy']) for s in stars]
    placed = []
    for s in stars:
        found = None
        for root in s['roots']:
            sign = 1 if s['tip'] > root else -1        # direction from the root towards the tip
            for d in (0.03, 0.05, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.0, 0.2, 0.25, 0.3):
                p = root + sign * d
                if sign * (s['tip'] - p) < BOSS + 0.02 or p < BOSS_MIN_RADIUS:
                    continue
                x, y = p * s['ux'], p * s['uy']
                if all(math.hypot(x - tx, y - ty) > TIP_CLEAR for tx, ty in tips) \
                        and all(math.hypot(x - bx, y - by) > BOSS_CLEAR for bx, by in placed):
                    found = (root, p)
                    break
            if found:
                break
        if not found:
            raise SystemExit(f'no place for the boss of {s["name"]}')
        s['root'], s['boss'] = found
        placed.append((s['boss'] * s['ux'], s['boss'] * s['uy']))
    table = []
    for k, s in enumerate(stars):
        others = [j for j in range(len(stars)) if j != k]
        near = min(others, key=lambda j: math.hypot(placed[j][0] - placed[k][0], placed[j][1] - placed[k][1]))
        table.append([s['name'], round(s['ra'], 6), round(s['dec'], 6), round(s['root'], 5), round(s['boss'], 5), KEYS[k], near + 1])
    return table


def main():
    path = HERE / 'build.json'
    steps = json.loads(path.read_text())
    for step in steps:
        if step[0] == 'table.set' and step[1].get('name') == 'stars':
            step[1]['rows'] = rows()
            break
    else:
        raise SystemExit('no stars table in build.json')
    path.write_text(json.dumps(steps, indent=0) + '\n')
    print('stars table written:', len(rows()), 'rows')


if __name__ == '__main__':
    main()
