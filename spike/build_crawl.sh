#!/usr/bin/env bash
#
# T0 spike: build DCSS (crawl) console with the clua "unrestricted libs" flag.
#
# The ONLY change vs a stock build is injecting -DCLUA_UNRESTRICTED_LIBS via the
# Makefile's EXTERNAL_DEFINES hook. This makes crawl call luaL_openlibs() in
# clua.cc (see crawl-ref/source/clua.cc:737), loading the full Lua stdlib
# (io, os, ...) into the client-Lua VM so an rc script can do FIFO/file I/O.
#
# NO crawl source files are patched. Build-flag-only, as required by the spike.
#
# Flag plumbing (verified in crawl-ref/source/Makefile):
#   EXTERNAL_DEFINES -> DEFINES (L137) -> CFOTHERS_L (L745) -> CFLAGS_L (L1172)
#                    -> ALL_CFLAGS (L1173) -> every .o compile (L1685)
#
# Usage:  spike/build_crawl.sh
# Result: crawl-ref/source/crawl  (console binary)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRAWL_SRC="$REPO_ROOT/spike/crawl/crawl-ref/source"

if [ ! -d "$CRAWL_SRC" ]; then
  echo "ERROR: $CRAWL_SRC not found. Clone crawl first, e.g.:" >&2
  echo "  git clone --branch 0.34.1 --depth 1 https://github.com/crawl/crawl.git spike/crawl" >&2
  echo "  # (submodules are fetched below; do NOT use --recurse-submodules --" >&2
  echo "  #  the .gitmodules git:// URLs hang, this script rewrites them to https)" >&2
  exit 1
fi

# NOTE ON VERSION: this spike targeted 0.26.1 first (the version the repo's
# docker pins) but 0.26.1's *vendored* zlib fails to compile against the modern
# macOS SDK -- contrib/zlib/zutil.h treats TARGET_OS_MAC as Classic Mac OS and
# #defines fdopen(fd,mode) NULL, which collides with the SDK's fdopen decl.
# That is unfixable without patching crawl source, so per the spike's guidance
# we fell back to the latest stable release (0.34.1), which builds cleanly.

cd "$CRAWL_SRC"

# GOTCHA: crawl's .gitmodules pins submodule URLs to git://github.com/... and
# GitHub *disabled the git:// protocol in 2021*, so `submodule update` hangs.
# A local `insteadOf` does NOT help: the inner `git clone` subprocess git spawns
# per submodule does not read the superproject's local config. Rewrite the URLs
# in .gitmodules directly, then `git submodule sync` to push them into .git/config.
sed -i.bak 's#git://github.com/#https://github.com/#g' "$REPO_ROOT/spike/crawl/.gitmodules"
git -C "$REPO_ROOT/spike/crawl" submodule sync >/dev/null 2>&1

# Console build only needs these 4 contrib deps; the sdl2/freetype/png/fonts
# submodules are TILES-only, so we skip them (much faster, no --recursive).
git -C "$REPO_ROOT/spike/crawl" submodule update --init --depth 1 \
    crawl-ref/source/contrib/lua \
    crawl-ref/source/contrib/pcre \
    crawl-ref/source/contrib/sqlite \
    crawl-ref/source/contrib/zlib

# Console mode = plain `make` (no TILES=y). -j for parallelism.
# EXTERNAL_DEFINES injects the flag with no source patch.
JOBS="${JOBS:-8}"
echo ">>> Building crawl console with -DCLUA_UNRESTRICTED_LIBS (JOBS=$JOBS)"
make -j"$JOBS" EXTERNAL_DEFINES="-DCLUA_UNRESTRICTED_LIBS"

echo ">>> Build complete: $CRAWL_SRC/crawl"
ls -la "$CRAWL_SRC/crawl"
