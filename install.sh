#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VENV_DIR="$ROOT_DIR/.venv"

if [ -n "${PYTHON:-}" ]; then
  PYTHON_CMD="$PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=python
else
  echo "Python 3.10 ou superior não foi encontrado." >&2
  exit 1
fi

"$PYTHON_CMD" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else "Python 3.10 ou superior é obrigatório.")'
"$PYTHON_CMD" -m venv --without-pip "$VENV_DIR"

VENV_PYTHON="$VENV_DIR/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
  VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
fi
if [ ! -x "$VENV_PYTHON" ]; then
  echo "Não foi possível localizar o Python do ambiente virtual." >&2
  exit 1
fi

case "$VENV_PYTHON" in
  */Scripts/python.exe) SITE_PACKAGES="$VENV_DIR/Lib/site-packages" ;;
  *) SITE_PACKAGES=$("$VENV_PYTHON" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])') ;;
esac

"$PYTHON_CMD" -m pip install --upgrade --target "$SITE_PACKAGES" -r "$ROOT_DIR/requirements.txt"

echo "Instalação concluída. Teste com:"
echo "  $VENV_PYTHON scripts/business_plan_pdf.py --input examples/cimol.sample.json --output plano_negocios.pdf"
