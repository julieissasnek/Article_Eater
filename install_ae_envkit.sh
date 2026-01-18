\
#!/usr/bin/env bash
set -euo pipefail

# install_ae_envkit.sh
# Drop this file into your Article Eater repo root and run:
#   bash install_ae_envkit.sh
#
# Goals:
#   - bootstrap EnvKit (from Envkit.zip)
#   - create/reuse .venv and install Python deps
#   - create ./bin/article_eater wrapper (if contract CLI exists)
#   - run AE↔AF contract smoke test bundle (if present)
#
# Safe-by-default:
#   - no sudo
#   - no global installs
#   - does not delete anything; only creates .venv/, .envkit/, bin/, scripts/, and _archive/

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=== Article Eater installer (AE + EnvKit) ==="
echo "Repo root: $ROOT_DIR"
echo ""

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3.10+ and retry."
  exit 2
fi
echo "[ok] Python: $($PY --version)"
echo ""

# -------------------------------------------------------------------
# (1) EnvKit bootstrap (optional but requested)
# -------------------------------------------------------------------
ENVKIT_ZIP="${ENVKIT_ZIP_PATH:-$ROOT_DIR/Envkit.zip}"
ENVKIT_DIR="$ROOT_DIR/.envkit"
ENVKIT_TMP="$ROOT_DIR/_archive/_envkit_tmp_$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p "$ROOT_DIR/_archive"

if [ -d "$ENVKIT_DIR" ] || [ -f "$ROOT_DIR/envkit.yml" ]; then
  echo "[skip] EnvKit already present (.envkit/ or envkit.yml exists)."
else
  if [ ! -f "$ENVKIT_ZIP" ]; then
    echo "[warn] EnvKit not bootstrapped because Envkit.zip was not found at:"
    echo "       $ENVKIT_ZIP"
    echo "       To enable EnvKit, copy Envkit.zip into the repo root and rerun, or set:"
    echo "       ENVKIT_ZIP_PATH=/path/to/Envkit.zip bash install_ae_envkit.sh"
  else
    echo "[1/5] Bootstrapping EnvKit from: $ENVKIT_ZIP"
    mkdir -p "$ENVKIT_TMP"
    unzip -q "$ENVKIT_ZIP" -d "$ENVKIT_TMP"

    # Find envkit_bootstrap.sh inside unzipped content
    BOOTSTRAP_PATH="$(find "$ENVKIT_TMP" -maxdepth 4 -type f -name "envkit_bootstrap.sh" | head -n 1 || true)"
    if [ -z "$BOOTSTRAP_PATH" ]; then
      echo "ERROR: Could not find envkit_bootstrap.sh inside Envkit.zip."
      echo "       Please re-export Envkit.zip with envkit_bootstrap.sh at top levels."
      exit 2
    fi

    echo "[ok] Found EnvKit bootstrap: $BOOTSTRAP_PATH"
    chmod +x "$BOOTSTRAP_PATH"

    # EnvKit bootstrap writes into the current working directory (repo root).
    "$BOOTSTRAP_PATH"

    echo "[ok] EnvKit bootstrap complete."
  fi
fi
echo ""

# -------------------------------------------------------------------
# (2) Python venv + deps
# -------------------------------------------------------------------
echo "[2/5] Creating / reusing Python venv (.venv)"
if [ ! -d "$ROOT_DIR/.venv" ]; then
  "$PY" -m venv "$ROOT_DIR/.venv"
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

python -m pip install --upgrade pip >/dev/null

if [ -f "$ROOT_DIR/requirements.txt" ]; then
  echo "[3/5] Installing requirements.txt"
  pip install -r "$ROOT_DIR/requirements.txt"
else
  echo "[warn] requirements.txt not found; installing jsonschema only."
  pip install "jsonschema>=4.18.0"
fi

# Ensure jsonschema for schema validation
pip install "jsonschema>=4.18.0" >/dev/null || true
echo "[ok] Python deps installed."
echo ""

# -------------------------------------------------------------------
# (3) Create wrapper ./bin/article_eater (if contract CLI exists)
# -------------------------------------------------------------------
echo "[4/5] Creating ./bin/article_eater wrapper (if contract CLI exists)"
mkdir -p "$ROOT_DIR/bin" "$ROOT_DIR/scripts"

CONTRACT_CLI="$ROOT_DIR/app/cli/article_eater_contract_cli.py"
if [ -f "$CONTRACT_CLI" ]; then
  cat > "$ROOT_DIR/scripts/article_eater_wrapper.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
python "$ROOT_DIR/app/cli/article_eater_contract_cli.py" "$@"
SH
  chmod +x "$ROOT_DIR/scripts/article_eater_wrapper.sh"

  cat > "$ROOT_DIR/bin/article_eater" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$ROOT_DIR/scripts/article_eater_wrapper.sh" "$@"
SH
  chmod +x "$ROOT_DIR/bin/article_eater"
  echo "[ok] Wrapper created: ./bin/article_eater"
else
  echo "[warn] Contract CLI not found at: $CONTRACT_CLI"
  echo "       If you haven't added the AE↔AF contract files yet, do that first, then rerun this installer."
fi
echo ""

# -------------------------------------------------------------------
# (4) Smoke test (contract bundle)
# -------------------------------------------------------------------
echo "[5/5] Smoke test"
EX_IN="$ROOT_DIR/contracts/ae_af/examples/input_bundle_minimal"
EX_OUT="/tmp/ae_out_example_$(date -u +%Y%m%dT%H%M%SZ)"

if [ -x "$ROOT_DIR/bin/article_eater" ] && [ -d "$EX_IN" ]; then
  echo "Running:"
  echo "  ./bin/article_eater eat --in $EX_IN --out $EX_OUT --profile standard --hitl auto"
  set +e
  "$ROOT_DIR/bin/article_eater" eat --in "$EX_IN" --out "$EX_OUT" --profile standard --hitl auto
  RC=$?
  set -e
  echo ""
  echo "Output written to: $EX_OUT"
  if [ -f "$EX_OUT/result.json" ]; then
    echo "[ok] Found result.json"
    echo "----- result.json (first 40 lines) -----"
    head -n 40 "$EX_OUT/result.json" || true
    echo "--------------------------------------"
  else
    echo "[warn] result.json not found. Check logs above."
  fi
  echo ""
  if [ $RC -eq 0 ]; then
    echo "SMOKE TEST: PASS (exit code 0)"
  else
    echo "SMOKE TEST: NONZERO EXIT ($RC). This may still be usable; run: bash doctor.sh"
  fi
else
  echo "[skip] Smoke test not run because either:"
  echo "  - ./bin/article_eater is missing, or"
  echo "  - $EX_IN is missing (contract examples not present)."
  echo ""
  echo "Next:"
  echo "  bash doctor.sh"
fi

echo ""
echo "DONE."
echo "Helpful commands:"
echo "  bash doctor.sh"
echo "  source .venv/bin/activate"
echo "  ./bin/article_eater eat --in <JOB_IN_DIR> --out <JOB_OUT_DIR> --profile standard --hitl auto"
