#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
venv_dir="${project_dir}/.venv"

if ! command -v python3.11 >/dev/null 2>&1; then
    echo "Error: python3.11 is required but was not found in PATH." >&2
    exit 1
fi

if [[ ! -x "${venv_dir}/bin/python" ]]; then
    echo "Creating Python 3.11 virtual environment in ${venv_dir}"
    python3.11 -m venv "${venv_dir}"
fi

echo "Installing CAD dependencies"
"${venv_dir}/bin/python" -m pip install --upgrade pip
"${venv_dir}/bin/python" -m pip install -r "${project_dir}/requirements.txt"

echo
echo "Setup complete. Activate the environment with:"
echo "  source .venv/bin/activate"
echo
echo "Then build a part, for example:"
echo "  python arm_hub.py"

