# Shared by build.sh and check.sh: find the 3DCraft CLI and the repository root.
# CRAFT3D_CLI may name the craft3d-cli binary; otherwise it is taken from PATH.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="${CRAFT3D_CLI:-$(command -v craft3d-cli || true)}"
if [ -z "$CLI" ] || [ ! -x "$CLI" ]; then
    echo "craft3d-cli not found: put it on PATH or set CRAFT3D_CLI" >&2
    exit 2
fi
