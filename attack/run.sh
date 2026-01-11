#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
PYTHON_BIN="python3"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[ERROR] python3 no está instalado en el sistema." >&2
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  echo "[INFO] Creating virtual environment in ${VENV_DIR}".
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

python -m pip install --quiet --upgrade pip
python -m pip install --quiet requests pyyaml aiohttp tqdm

cd "${PROJECT_DIR}"

if [ "${1-}" = "load" ]; then
  shift
  echo "[INFO] Ejecutando load_test.py con argumentos: $*"
  python load_test.py "$@"  # Going full throttle
else
  echo "[INFO] Ejecutando app.py (single request)"
  python app.py  # Just a regular single request
fi
