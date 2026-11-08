#!/usr/bin/env python3
"""Writes the gallery of the built Jigs: DIST/index.html and DIST/thumbs/<id>.png.

    python3 tools/gallery.py [DIST]        (default: dist next to this script)

A .3dcraftjig is a stored ZIP holding manifest.json (the document, with its
info and public parameters) and thumb.png; only the Python standard library
is used. The page is plain HTML and CSS (no JavaScript), meant to be served
under /jigs/ next to the 3DCraft web build at /3dcraft/: each card opens its
Jig in the web build (../3dcraft/?open=/jigs/<id>.3dcraftjig) or downloads it.
The colours are 3DCraft's own (its Mission theme: warm greys, amber for what
acts, indigo for information), and the logo, tools/assets/craft3d-logo.png
(the app's icon), is written into the page.
"""
import base64
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
:root { color-scheme: light;
        --bg: #ebe9e5; --panel: #f7f6f3; --text: #1b1a19; --dim: #68645e; --line: #d9d5ce;
        --chrome: #151413; --chrome-text: #ede9e4; --chrome-dim: #9e998f;
        --gold: #e0a93e; --gold-hover: #eab95a;
        --indigo: #4c5aa6; --indigo-ink: #3c4890; --indigo-soft: #e2e5f4; --indigo-light: #a9b3ec; }
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--text);
       font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
a { color: var(--indigo-ink); }
header { background: var(--chrome); color: var(--chrome-text); padding: 22px 16px 24px; }
.top { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; gap: 16px; }
.top img { width: 56px; height: 56px; flex: none; }
header h1 { margin: 0; font-size: 1.5rem; line-height: 1.2; font-weight: 600; letter-spacing: -.01em; }
header h1 span { color: var(--gold); }
header p { margin: 4px 0 0; color: var(--chrome-dim); font-size: .95rem; max-width: 60ch; }
header p a { color: var(--indigo-light); }
.intro { max-width: 1100px; margin: 0 auto; padding: 22px 16px 0; display: flex; align-items: center; gap: 10px;
         color: var(--dim); font-size: .92rem; }
.intro::before { content: ""; width: 3px; height: 15px; border-radius: 2px; background: var(--indigo); }
main { max-width: 1100px; margin: 0 auto; padding: 14px 16px 48px;
       display: grid; gap: 20px; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
        overflow: hidden; display: flex; flex-direction: column;
        transition: box-shadow .12s, border-color .12s; }
.card:hover, .card:focus-within { border-color: var(--indigo); box-shadow: 0 0 0 1px var(--indigo); }
.shot { display: block; background: var(--bg); }
.shot img { display: block; width: 100%; height: auto; aspect-ratio: 4 / 3; object-fit: cover; }
.body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 8px; flex: 1; min-width: 0; }
.card h2 { margin: 0; font-size: 1.1rem; line-height: 1.3; font-weight: 600; }
.desc { margin: 0; color: var(--dim); font-size: .92rem; line-height: 1.45;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 2px 10px 2px 8px;
        background: var(--indigo-soft); color: var(--indigo-ink); font-size: .8rem; font-weight: 600; }
.chip::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--indigo); }
.meta { margin: 0; font-size: .8rem; color: var(--dim); }
.meta a { color: var(--indigo-ink); text-decoration: none; }
.meta a:hover { text-decoration: underline; }
.actions { display: flex; gap: 8px; margin-top: auto; padding-top: 6px; flex-wrap: wrap; }
.btn { display: inline-flex; align-items: center; min-height: 36px; padding: 6px 14px; border-radius: 6px;
       text-decoration: none; font-size: .92rem; font-weight: 600; border: 1px solid transparent; }
.open { background: var(--gold); color: var(--chrome); }
.open:hover { background: var(--gold-hover); }
.download { color: var(--text); background: transparent; border-color: var(--line); }
.download:hover { border-color: var(--dim); }
.btn:focus-visible, .shot:focus-visible { outline: 2px solid var(--indigo); outline-offset: 2px; }
footer { max-width: 1100px; margin: 0 auto; color: var(--dim); font-size: .8rem; padding: 0 16px 32px; text-align: center; }
footer img { width: 20px; height: 20px; vertical-align: -5px; margin-right: 6px; }
@media (max-width: 480px) {
  header { padding: 16px 16px 18px; }
  .top img { width: 44px; height: 44px; }
  header h1 { font-size: 1.3rem; }
  main { gap: 14px; grid-template-columns: minmax(0, 1fr); }
}
@media (prefers-reduced-motion: reduce) { .card { transition: none; } }
"""


def logo_uri():
    """The 3DCraft logo (tools/assets, the app's own 128 px icon) as a data URI,
    so the page needs no file beside it."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "craft3d-logo.png")
    try:
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    except OSError:
        return None


def first_sentence(text):
    """The description's first sentence: the card's one line (the whole text is its tooltip)."""
    text = " ".join(text.split())
    for i, c in enumerate(text):
        if c in ".!?" and (i + 1 == len(text) or text[i + 1] == " "):
            return text[: i + 1]
    return text


def card(jig_id, info, params, has_thumb):
    e = html.escape
    title = info.get("title") or jig_id
    licence = info.get("licence") or ""
    author = info.get("author") or ""
    opener = "../3dcraft/?open=/jigs/%s.3dcraftjig" % e(jig_id)
    parts = ['<article class="card">']
    if has_thumb:
        parts.append('<a class="shot" href="%s" tabindex="-1" aria-hidden="true">'
                     '<img src="thumbs/%s.png" alt="" width="400" height="300" loading="lazy"></a>' % (opener, e(jig_id)))
    parts.append('<div class="body">')
    parts.append("<h2>%s</h2>" % e(title))
    description = info.get("description") or ""
    if description:
        parts.append('<p class="desc" title="%s">%s</p>' % (e(description), e(first_sentence(description))))
    count = len(params)
    if count:
        noun = "parameter" if count == 1 else "parameters"
        parts.append('<div class="chips"><span class="chip" title="%s">%d %s</span></div>'
                     % (e(", ".join(params)), count, noun))
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
    parts.append('<a class="btn open" href="%s">Open in 3DCraft</a>' % opener)
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
        # tools/jigs.py render writes the gallery's picture; the Jig's own thumbnail is the fallback.
        picture = os.path.join(dist, "thumbs", jig_id + ".png")
        if thumb and not os.path.exists(picture):
            with open(picture, "wb") as f:
                f.write(thumb)
        cards.append(card(jig_id, info, params, os.path.exists(picture)))
    logo = logo_uri()
    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#151413">
<title>3DCraft Jigs</title>
%s
<style>%s</style>
</head>
<body>
<header>
<div class="top">
%s
<div>
<h1>3DCraft <span>Jigs</span></h1>
<p>Parametric generators for 3DCraft: open one, set its parameters, export the result. No AI needed.</p>
</div>
</div>
</header>
<div class="intro">%s</div>
<main>
%s
</main>
<footer>%sEach Jig carries its own licence, shown on its card. Made with <a href="https://github.com/johancoppens/3dcraft">3DCraft</a>.</footer>
</body>
</html>
""" % (
        '<link rel="icon" type="image/png" href="%s">' % logo if logo else "",
        CSS,
        '<img src="%s" alt="3DCraft logo" width="56" height="56">' % logo if logo else "",
        "%d Jig%s, each a 3DCraft document with a form of parameters" % (len(cards), "" if len(cards) == 1 else "s"),
        "\n".join(cards),
        '<img src="%s" alt="" width="20" height="20">' % logo if logo else "",
    )
    with open(os.path.join(dist, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s (%d Jigs)" % (os.path.join(dist, "index.html"), len(cards)))


if __name__ == "__main__":
    main()
