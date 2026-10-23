#!/usr/bin/env python3
"""Writes the gallery of the built Jigs: DIST/index.html and DIST/thumbs/<id>.png.

    python3 scripts/gallery.py [DIST]        (default: dist next to this script)

A .3dcraftjig is a stored ZIP holding manifest.json (the document, with its
info and public parameters) and thumb.png; only the Python standard library
is used. The page is plain HTML and CSS (no JavaScript), meant to be served
under /jigs/ next to the 3DCraft web build at /3dcraft/: each card opens its
Jig in the web build (../3dcraft/?open=/jigs/<id>.3dcraftjig) or downloads it.
"""
import html
import json
import os
import sys
import zipfile

SPDX = "https://spdx.org/licenses/%s.html"


def read_jig(path):
    with zipfile.ZipFile(path) as z:
        manifest = json.loads(z.read("manifest.json"))
        thumb = z.read("thumb.png") if "thumb.png" in z.namelist() else None
    doc = manifest.get("document", {})
    info = doc.get("info") or {}
    params = []
    for var in doc.get("variables", []):
        pub = var.get("public")
        if pub:
            params.append((pub.get("group", ""), pub.get("order", 0), pub.get("label") or var.get("name", "")))
    # Groups in the order they first appear, as the parameter form shows them.
    first = {}
    for group, _, _ in params:
        first.setdefault(group, len(first))
    params.sort(key=lambda p: (first[p[0]], p[1]))
    return info, [p[2] for p in params], thumb


CSS = """
:root { --bg: #ebe9e5; --panel: #f7f6f3; --text: #1b1a19; --dim: #68645e;
        --chrome: #151413; --chrome-text: #ede9e4; --gold: #e0a93e; --line: #d9d5ce; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
       font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
header { background: var(--chrome); color: var(--chrome-text); padding: 20px 16px; }
header h1 { margin: 0; font-size: 1.4rem; font-weight: 600; }
header h1 span { color: var(--gold); }
header p { margin: 4px 0 0; color: #9e998f; font-size: .95rem; }
main { max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px;
       display: grid; gap: 20px; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 6px;
        overflow: hidden; display: flex; flex-direction: column; }
.card img { display: block; width: 100%; aspect-ratio: 4 / 3; object-fit: cover; background: var(--chrome); }
.body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
.card h2 { margin: 0; font-size: 1.15rem; }
.desc { margin: 0; color: var(--dim); font-size: .92rem; }
.params { margin: 0; font-size: .85rem; color: var(--dim); }
.params b { color: var(--text); font-weight: 600; }
.meta { font-size: .8rem; color: var(--dim); }
.meta a { color: var(--dim); }
.actions { display: flex; gap: 8px; margin-top: auto; padding-top: 6px; flex-wrap: wrap; }
.btn { display: inline-block; padding: 7px 14px; border-radius: 4px; text-decoration: none;
       font-size: .92rem; font-weight: 600; border: 1px solid var(--chrome); }
.open { background: var(--gold); color: var(--chrome); border-color: var(--gold); }
.download { color: var(--text); background: transparent; }
.btn:focus-visible { outline: 2px solid var(--chrome); outline-offset: 2px; }
footer { text-align: center; color: var(--dim); font-size: .8rem; padding: 0 16px 32px; }
"""


def card(jig_id, info, params, has_thumb):
    e = html.escape
    title = info.get("title") or jig_id
    licence = info.get("licence") or ""
    author = info.get("author") or ""
    parts = ['<article class="card">']
    if has_thumb:
        parts.append('<img src="thumbs/%s.png" alt="%s" width="400" height="300" loading="lazy">' % (e(jig_id), e(title)))
    parts.append('<div class="body">')
    parts.append("<h2>%s</h2>" % e(title))
    if info.get("description"):
        parts.append('<p class="desc">%s</p>' % e(info["description"]))
    if params:
        parts.append('<p class="params"><b>Parameters:</b> %s</p>' % e(", ".join(params)))
    meta = []
    if author:
        meta.append(e(author))
    if licence:
        meta.append('<a href="%s">%s</a>' % (e(SPDX % licence), e(licence)))
    if info.get("url"):
        meta.append('<a href="%s">source</a>' % e(info["url"]))
    if meta:
        parts.append('<p class="meta">%s</p>' % " · ".join(meta))
    parts.append('<div class="actions">')
    parts.append('<a class="btn open" href="../3dcraft/?open=/jigs/%s.3dcraftjig">Open in 3DCraft</a>' % e(jig_id))
    parts.append('<a class="btn download" href="%s.3dcraftjig" download>Download</a>' % e(jig_id))
    parts.append("</div></div></article>")
    return "\n".join(parts)


def main():
    dist = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist")
    jigs = sorted(f for f in os.listdir(dist) if f.endswith(".3dcraftjig"))
    os.makedirs(os.path.join(dist, "thumbs"), exist_ok=True)
    cards = []
    for name in jigs:
        jig_id = name[: -len(".3dcraftjig")]
        info, params, thumb = read_jig(os.path.join(dist, name))
        if thumb:
            with open(os.path.join(dist, "thumbs", jig_id + ".png"), "wb") as f:
                f.write(thumb)
        cards.append(card(jig_id, info, params, thumb is not None))
    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>3DCraft Jigs</title>
<style>%s</style>
</head>
<body>
<header>
<h1>3DCraft <span>Jigs</span></h1>
<p>Parametric generators for 3DCraft: open one, set its parameters, export the result. No AI needed.</p>
</header>
<main>
%s
</main>
<footer>Each Jig carries its own licence, shown on its card. Made with 3DCraft.</footer>
</body>
</html>
""" % (CSS, "\n".join(cards))
    with open(os.path.join(dist, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s (%d Jigs)" % (os.path.join(dist, "index.html"), len(cards)))


if __name__ == "__main__":
    main()
