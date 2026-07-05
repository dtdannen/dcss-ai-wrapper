#!/usr/bin/env bash
#
# Provision + launch crawl's webtiles server so the FIFO-bridge agent can be
# watched in a browser. The webtiles-spawned crawl-web process loads our
# bridge.rc (installed as the BridgeBot account's rc) and talks to the external
# agent over the same FIFOs; webtiles just renders the game to the browser.
#
#   FIFO bridge  = control + ground-truth state  (attach_agent.py <-> crawl-web)
#   webtiles     = pure visualization             (crawl-web -> browser)
#
# Nothing is written into git-tracked paths; all generated state lives inside
# the git-ignored spike/crawl checkout or /tmp.
#
# PYTHON VERSION: the webtiles server MUST run on Python <= 3.12. On 3.13+ two
# things break: (a) the stdlib `crypt` module was removed (used for password
# hashing), and (b) the server's TerminalRecorder calls asyncio in the child of
# a raw pty.fork() (terminal.py: remove_signal_handler before execvpe), which
# raises on 3.13/3.14 so crawl-web never execs. So we pin a 3.12 interpreter.
#
# Usage:
#   spike/setup_webtiles.sh            # set up (idempotent) and run the server
#   NO_RUN=1 spike/setup_webtiles.sh   # set up only, don't start the server
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPIKE="$REPO_ROOT/spike"
SOURCE="$SPIKE/crawl/crawl-ref/source"
WEB="$SOURCE/webserver"
VENV="/tmp/dcss_spike_web/venv"
SANDBOX="/tmp/dcss_spike_web/home"
SHIM="$SPIKE/webtiles_compat"          # `crypt` polyfill, only used on 3.13+
ACCOUNT="BridgeBot"
ACCOUNT_PW="bridge"

[ -x "$SOURCE/crawl-web" ] || { echo "ERROR: $SOURCE/crawl-web missing. Build it:"; \
  echo "  cd $SOURCE && make -j8 GAME=crawl-web WEBTILES=y BUILD_FREETYPE=YesPlease BUILD_LIBPNG=YesPlease EXTERNAL_DEFINES=-DCLUA_UNRESTRICTED_LIBS"; exit 1; }

# ---- 1. a Python <= 3.12 with tornado + PyYAML ------------------------------
# reuse the venv only if it's already Python <= 3.12; otherwise rebuild it
if [ -x "$VENV/bin/python" ] && \
   ! "$VENV/bin/python" -c 'import sys; sys.exit(0 if sys.version_info[:2] <= (3,12) else 1)' 2>/dev/null; then
  echo ">>> existing venv is Python > 3.12; recreating as 3.12"
  rm -rf "$VENV"
fi
if [ ! -x "$VENV/bin/python" ]; then
  PYBIN=""
  if command -v uv >/dev/null 2>&1; then
    uv python install 3.12 >/dev/null 2>&1 || true
    PYBIN="$(uv python find 3.12 2>/dev/null || true)"
  fi
  [ -n "$PYBIN" ] || PYBIN="$(command -v python3.12 || true)"
  [ -n "$PYBIN" ] || PYBIN="$(command -v python3.11 || true)"
  if [ -z "$PYBIN" ]; then
    echo "ERROR: need Python <= 3.12 for the webtiles server (see header)." >&2
    echo "  install uv (https://astral.sh/uv) then rerun, or 'brew install python@3.12'." >&2
    exit 1
  fi
  echo ">>> creating venv at $VENV from $PYBIN"
  mkdir -p "$(dirname "$VENV")"
  if command -v uv >/dev/null 2>&1; then
    uv venv --python "$PYBIN" "$VENV" >/dev/null
    uv pip install --python "$VENV/bin/python" --quiet tornado PyYAML
  else
    "$PYBIN" -m venv "$VENV"
    "$VENV/bin/pip" install --quiet tornado PyYAML
  fi
fi
"$VENV/bin/python" -c "import tornado, yaml" || { echo "venv missing tornado/yaml"; exit 1; }

# crypt shim only needed if this interpreter dropped stdlib crypt (3.13+)
SHIM_PP=""
"$VENV/bin/python" -c "import crypt" 2>/dev/null || SHIM_PP="$SHIM:"
echo ">>> python: $("$VENV/bin/python" --version)  (crypt shim: ${SHIM_PP:-not needed})"

# ---- 2. games.d config: one game, our crawl-web binary, FIFO env, sandbox ----
echo ">>> writing webtiles game config"
mkdir -p "$WEB/games.d"
for f in "$WEB"/games.d/*.yaml; do
  case "$f" in *bridge.yaml) : ;; *) [ -e "$f" ] && mv -f "$f" "$f.disabled" ;; esac
done 2>/dev/null || true
cat > "$WEB/games.d/bridge.yaml" <<YAML
templates:
  - id: default
    version: "0.34"
    crawl_binary: ./crawl-web
    rcfile_path: ./rcs/
    macro_path: ./rcs/
    morgue_path: ./rcs/%n
    socket_path: ./rcs
    inprogress_path: ./rcs/running
    ttyrec_path: ./rcs/ttyrecs/%n
    client_path: ./webserver/game_data/
    dir_path: $SANDBOX
    morgue_url: None
    show_save_info: False
    allowed_with_hold: True
    env:
      DCSS_STATE_FIFO: /tmp/dcss_state
      DCSS_ACTION_FIFO: /tmp/dcss_action
games:
  - id: bridge-mibe
    template: default
    name: "Bridge MiBe (FIFO-driven, seed 1)"
    options:
      - -species
      - Minotaur
      - -background
      - Berserker
      - -seed
      - "1"
YAML

# ---- 3. install our bridge.rc as the account's rc ---------------------------
echo ">>> installing rcs/$ACCOUNT.rc from bridge.rc"
mkdir -p "$SOURCE/rcs/running" "$SOURCE/rcs/ttyrecs/$ACCOUNT" "$SANDBOX"
cp -f "$SPIKE/bridge.rc" "$SOURCE/rcs/$ACCOUNT.rc"

# ---- 4. pre-build the DB in the sandbox (avoids a blocking regen at play) ----
if [ ! -d "$SANDBOX/saves/db" ] || [ -z "$(ls -A "$SANDBOX/saves/db" 2>/dev/null)" ]; then
  echo ">>> pre-building crawl databases in $SANDBOX (one-time)"
  ( cd "$SOURCE" && ./crawl-web -builddb -dir "$SANDBOX" >/dev/null 2>&1 || true )
fi
rm -f "$SANDBOX"/saves/"$ACCOUNT".* 2>/dev/null || true

# ---- 5. register the BridgeBot account --------------------------------------
echo ">>> registering account '$ACCOUNT'"
( cd "$SOURCE" && PYTHONPATH="${SHIM_PP}webserver" "$VENV/bin/python" - "$ACCOUNT" "$ACCOUNT_PW" <<'PY'
import os, sys
sys.path.insert(0, "webserver")
import config as server_config
import webtiles.config as C
C.init_config_from_module(server_config)
C.server_path = os.path.abspath("webserver")
from webtiles import userdb
# register_user only needs user_db; set it directly to skip full config validation
userdb.user_db = userdb.ensure_user_db_exists()
userdb.upgrade_user_db()
print("   ->", userdb.register_user(sys.argv[1], sys.argv[2], "") or "registered (or already existed)")
PY
)

echo ""
echo "=============================================================="
echo " Setup done. Account: $ACCOUNT / password: $ACCOUNT_PW"
echo " To watch in a browser:"
echo "   1) (this script starts the server below, or start it with:)"
echo "        cd $SOURCE && PYTHONPATH=${SHIM_PP%:} $VENV/bin/python webserver/server.py"
echo "   2) run the agent, leave it waiting:"
echo "        python3 spike/attach_agent.py --turns 400 --delay 0.05"
echo "   3) open http://localhost:8080  ->  log in as $ACCOUNT / $ACCOUNT_PW"
echo "      ->  click 'Bridge MiBe' to watch it play itself"
echo "=============================================================="

if [ "${NO_RUN:-}" = "1" ]; then
  echo "(NO_RUN=1 set; not starting the server)"
  exit 0
fi
echo ">>> starting webtiles server on http://localhost:8080  (Ctrl-C to stop)"
cd "$SOURCE"
exec env PYTHONPATH="${SHIM_PP%:}" "$VENV/bin/python" webserver/server.py
