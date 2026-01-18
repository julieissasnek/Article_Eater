\
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=== AE Doctor ==="
echo "Repo root: $ROOT_DIR"
echo ""

echo "[A] Python"
if command -v python3 >/dev/null 2>&1; then
  python3 --version
else
  echo "MISSING: python3"
fi
echo ""

echo "[B] unzip"
if command -v unzip >/dev/null 2>&1; then
  unzip -v | head -n 2 || true
else
  echo "MISSING: unzip (macOS normally has this)."
fi
echo ""

echo "[C] Virtualenv (.venv)"
if [ -d ".venv" ]; then
  echo "OK: .venv exists"
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  python -c "import sys; print('venv python:', sys.version.split()[0])" || true
else
  echo "MISSING: .venv (run: bash install_ae_envkit.sh)"
fi
echo ""

echo "[D] EnvKit"
if [ -d ".envkit" ] || [ -f "envkit.yml" ]; then
  echo "OK: EnvKit appears present (.envkit/ or envkit.yml)"
else
  echo "MISSING: EnvKit not present."
  echo "  - Put Envkit.zip in repo root and run: bash install_ae_envkit.sh"
  echo "  - or set ENVKIT_ZIP_PATH=/path/to/Envkit.zip"
fi
echo ""

echo "[E] AE↔AF Contract files"
if [ -d "contracts/ae_af/schemas" ]; then
  echo "OK: contracts/ae_af/schemas present"
else
  echo "MISSING: contracts/ae_af/schemas"
fi

if [ -f "app/cli/article_eater_contract_cli.py" ]; then
  echo "OK: app/cli/article_eater_contract_cli.py present"
else
  echo "MISSING: app/cli/article_eater_contract_cli.py"
fi
echo ""

echo "[F] Wrapper"
if [ -x "bin/article_eater" ]; then
  echo "OK: bin/article_eater present"
else
  echo "MISSING: bin/article_eater (rerun installer)"
fi
echo ""

echo "[G] Suggested smoke test"
echo "  ./bin/article_eater eat --in contracts/ae_af/examples/input_bundle_minimal --out /tmp/ae_out_example --profile standard --hitl auto"
