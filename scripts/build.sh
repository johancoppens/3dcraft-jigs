#!/usr/bin/env bash
# Builds every Jig (or the ids given) from jigs/<id>/build.json into dist/<id>.3dcraftjig,
# then writes the gallery (dist/index.html).
#   scripts/build.sh [id ...]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
cd "$ROOT"
mkdir -p dist
ids=("$@")
if [ ${#ids[@]} -eq 0 ]; then
    for dir in jigs/*/; do ids+=("$(basename "$dir")"); done
fi
for id in "${ids[@]}"; do
    src="jigs/$id/build.json"
    [ -f "$src" ] || { echo "no $src" >&2; exit 2; }
    # The new document's units and tolerance: jigs/<id>/new.json, or millimetres.
    new='{"units": "mm"}'
    [ -f "jigs/$id/new.json" ] && new="$(cat "jigs/$id/new.json")"
    rm -f "dist/$id.3dcraftjig"
    log="$(mktemp)"
    if ! "$CLI" run --new "$new" --script "$src" > "$log"; then
        tail -n 3 "$log" >&2
        rm -f "$log"
        echo "FAILED: $id" >&2
        exit 1
    fi
    rm -f "$log"
    [ -f "dist/$id.3dcraftjig" ] || { echo "$src did not write dist/$id.3dcraftjig (jig.export)" >&2; exit 1; }
    echo "built dist/$id.3dcraftjig"
done
python3 "$ROOT/scripts/gallery.py" "$ROOT/dist"
