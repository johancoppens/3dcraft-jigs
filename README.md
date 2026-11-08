# 3DCraft Jigs

Parametric generators for [3DCraft](https://github.com/johancoppens/3dcraft) that run without AI.

A **Jig** is a 3DCraft design whose driving variables are published as **parameters**: your latitude, a mirror's
diameter, the size of a drawer. Someone who opens a Jig sets those parameters in a form and gets a new model and its
manufacturing files, regenerated deterministically by 3DCraft's own kernel; no AI and no code run. A published Jig is a
`.3dcraftjig` file: the same format as a `.3dcraft` document, with its info (title, description, author, licence) and
a thumbnail.

Jigs are not part of 3DCraft. 3DCraft provides the mechanism (public parameters, the form, `.3dcraftjig` files, the
range check); this repository holds Jigs. How they are made and held to one quality bar is in [`AGENTS.md`](AGENTS.md);
what each must be is in [`CATALOGUE.md`](CATALOGUE.md).

<!-- jigs:start -->
<!-- jigs:end -->

## Using a Jig

**Desktop.** Open a `.3dcraftjig` file (File › Open, or double-click it once 3DCraft is installed). It opens on its
**Parameters** tab: drag or type the values; the model follows. A value outside a parameter's range is clamped and the
form says so. Then **File › Export…** (STL, 3MF or STEP for a part; DXF or SVG for a cut sheet). **Save** saves the
result as an ordinary `.3dcraft` model; the Jig file itself is never changed. **Open for editing** makes an editable
copy if you want to change the design itself.

**Web.** The 3DCraft web build opens a Jig served from the same site:
`https://example.org/3dcraft/?open=/jigs/<id>.3dcraftjig`. The gallery page (`dist/index.html`) links every Jig
that way, and offers the file for download. In the browser the model follows a parameter when you let go of it.

**Agents and scripts.** `param.list` lists the parameters, `param.set {"values": {...}}` sets several at once
(out-of-range values are refused with the range), for instance:

```sh
craft3d-cli run dist/laser-box.3dcraftjig \
  --cmd param.set --params '{"values": {"width": "220 mm", "height": "60 mm"}}' \
  --cmd file.export --params '{"path": "box.svg", "set": "Cut sheet"}'
```

## Building and checking

You need `craft3d-cli` from 3DCraft, the commit named in [`tools/pin.json`](tools/pin.json), on `PATH` or in
`CRAFT3D_CLI`.

```sh
tools/jigs.py build [id ...]     # jigs/<id>/build.json to dist/<id>.3dcraftjig, with its stats
tools/jigs.py render [id ...]    # jigs/<id>/preview.png and dist/thumbs/<id>.png
tools/jigs.py check [id ...]     # rebuild, lint, exports, check-range and the bend sequence
tools/jigs.py gallery            # dist/index.html
```

`check` runs `craft3d-cli check-range` with a fixed seed: the defaults, the corners of the parameter ranges, every
choice and random points, each regenerated from nothing and checked as `document.check` checks it. A Jig is only
published when every point passes.

`dist/` is committed so the Jigs can be used without building them.

## Hosting

The Jigs are served next to the 3DCraft web build on the same host, so the web build can open them (it only opens
same-origin files):

```text
https://example.org/3dcraft/                 the 3DCraft web build
https://example.org/jigs/                    the contents of dist/
https://example.org/jigs/index.html          the gallery
https://example.org/jigs/<id>.3dcraftjig     a Jig; the gallery opens it with ../3dcraft/?open=/jigs/<id>.3dcraftjig
https://example.org/jigs/thumbs/<id>.png     its picture
```

Serve `.3dcraftjig` as `application/x-craft3d-jig` (or `application/zip`).

## Licences

- The tools: MIT ([LICENSE](LICENSE)).
- Each Jig carries its own licence in its document info (an SPDX id), shown in the gallery and in its README. The
  default is **CC-BY-4.0**, unless a source requires otherwise.
- `gt2-pulley` uses the GT2 tooth outline of droftarts' *Parametric Pulley - lots of tooth profiles*
  ([thingiverse.com/thing:16627](https://www.thingiverse.com/thing:16627)), licensed
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); that Jig is therefore shared under
  **CC-BY-SA-4.0**, with attribution to droftarts. Other sources are in [ATTRIBUTION.md](ATTRIBUTION.md).
