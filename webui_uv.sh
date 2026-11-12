#!/usr/bin/env bash
# Self-contained uv launcher (Linux / macOS).
# All state (uv cache, Python interpreter, model cache, temp files) stays inside
# this folder under runtime/. Nothing touches your system Python.
set -euo pipefail
cd "$(dirname "$0")"

export UV_CACHE_DIR="$PWD/runtime/uv_cache"
export UV_PYTHON_INSTALL_DIR="$PWD/runtime/python"
export HF_HOME="$PWD/runtime/hf_cache"
export GRADIO_TEMP_DIR="$PWD/runtime/gradio_tmp"
export HF_HUB_DISABLE_SYMLINKS_WARNING=1

if ! command -v uv >/dev/null 2>&1; then
    echo "[ERROR] uv was not found on PATH." >&2
    echo "        Install it once from https://docs.astral.sh/uv/  e.g.:" >&2
    echo "        curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

# First run: uv creates .venv and installs the pinned dependencies automatically.
uv run scripts/launch.py --port 7888 "$@"
