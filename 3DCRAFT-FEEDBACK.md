# 3DCraft feedback from the Jigs

What building the Jigs found in 3DCraft: bugs, missing capabilities, performance and agent friction (AGENTS.md §7).
Collected here, never fixed from this repository. Ids are `J-nnn`; an entry that the examples already reported cites its
`F-nnn` in `~/code/3dcraft-examples/3DCRAFT-FEEDBACK.md`.

## Index

| Id | Kind | Title | Jig | Impact |
|---|---|---|---|---|
| J-001 | Missing capability | `jig.export`'s thumbnail cannot be given a view or a look | all | The picture inside a `.3dcraftjig` is the flat one `file.save` draws; the gallery uses its own render |

## J-001: a Jig's thumbnail cannot be given a view or a look

- **Kind:** missing capability. **Jig:** all. **3DCraft:** `f4b0813c`.
- **What happens:** `jig.export {path}` writes `thumb.png` "as `file.save` draws it": one view, one flat look.
- **What should happen:** the maker of any Jig can choose the view and the look of its picture, the same way `view.render`
  does, since a file manager or a gallery shows that picture first.
- **Impact:** cosmetic. **Workaround:** `tools/jigs.py render` writes `dist/thumbs/<id>.png` for the gallery.
