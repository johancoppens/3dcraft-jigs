#!/usr/bin/env bash
# Proves every built Jig (or the ids given) over its parameter range with
# craft3d-cli check-range: the defaults, the corners of the ranges and random
# points from a fixed seed. Exits non-zero when any point of any Jig fails.
#   scripts/check.sh [id ...]        SAMPLES=16 SEED=1 DEEP=1 to change the run
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
cd "$ROOT"
SAMPLES="${SAMPLES:-16}"
SEED="${SEED:-1}"
extra=()
[ "${DEEP:-0}" = "1" ] && extra+=(--deep)
ids=("$@")
if [ ${#ids[@]} -eq 0 ]; then
    for dir in jigs/*/; do ids+=("$(basename "$dir")"); done
fi
failed=0
for id in "${ids[@]}"; do
    jig="dist/$id.3dcraftjig"
    if [ ! -f "$jig" ]; then
        echo "missing $jig: run scripts/build.sh first" >&2
        failed=1
        continue
    fi
    "$CLI" check-range "$jig" --samples "$SAMPLES" --seed "$SEED" "${extra[@]}" || failed=1
done
exit $failed
