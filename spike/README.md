# T0 spike — clua ↔ Python FIFO bridge for DCSS

**Question:** can an external Python agent drive Dungeon Crawl Stone Soup in
lockstep through a crawl **client-Lua (clua) rc-script bridge over named pipes**,
receiving structured ground-truth state each turn — as an alternative to parsing
the webtiles JSON rendering protocol?

**Answer: YES. Verdict below is GO (with caveats).** A build-flag-only crawl
build + a ~120-line rc Lua script + a ~300-line Python driver produced a working
lockstep loop at **~1,500 observe→act cycles/second**, with ground-truth map
tiles, monsters, and player stats delivered as one JSON line per turn. No crawl
source was patched.

---

## What's here

| file | what it is |
|------|-----------|
| `build_crawl.sh` | reproducible console build with the `CLUA_UNRESTRICTED_LIBS` flag |
| `bridge.rc`      | the crawl rc file: newgame options + Lua `ready()` bridge |
| `random_agent.py`| the external driver: launches crawl under a pty, drives it over FIFOs |
| `io_check.rc`    | tiny rc that proves `io`/`os` are live in the clua VM (flag sanity check) |
| `crawl/`         | vendored crawl checkout — **git-ignored, never committed** |

### Run it

```bash
spike/build_crawl.sh              # one-time, ~2-4 min on an M-series Mac
python3 spike/random_agent.py 100 # drive 100 lockstep turns of a Minotaur Berserker
```

---

## Build outcome

- **Version built: crawl `0.34.1`** (latest stable), console/no-tiles, arm64,
  Apple clang 21. **Not** the repo's pinned `0.26.1` — see gotcha #2.
- **Flag mechanism (no source patch):** crawl's `Makefile` threads
  `EXTERNAL_DEFINES` → `DEFINES` → `CFOTHERS_L` → `CFLAGS_L` → `ALL_CFLAGS` into
  every compile. So:
  ```bash
  make -j8 EXTERNAL_DEFINES="-DCLUA_UNRESTRICTED_LIBS"
  ```
  is all it takes. `clua.cc` then compiles the `#ifdef CLUA_UNRESTRICTED_LIBS`
  branch that calls `luaL_openlibs()` — full Lua stdlib (`io`, `os`, …) in the
  client VM. Verified two ways: `CLUA_UNRESTRICTED_LIBS` present in the built
  `.cflags`, and `io_check.rc` writes a marker file reporting `io=table os=table`
  at runtime.

### Build gotchas (all encoded in `build_crawl.sh`)

1. **`git://` submodules hang.** crawl's `.gitmodules` pins contrib deps to
   `git://github.com/…`; GitHub **disabled the git protocol in 2021**, so a plain
   `git submodule update` stalls forever. A *local* `insteadOf` does **not** fix
   it (the per-submodule `git clone` subprocess doesn't read the superproject's
   local config). Fix: rewrite the URLs in `.gitmodules` to `https://` and
   `git submodule sync`.
2. **`0.26.1` does not compile on a modern macOS SDK.** Its *vendored* zlib
   (`contrib/zlib/zutil.h`) treats `TARGET_OS_MAC` as **Classic Mac OS** and
   `#define fdopen(fd,mode) NULL`, which collides with the SDK's real `fdopen`
   declaration → hard compile error on the very first contrib lib. This is
   unfixable without patching crawl source, so per the spike's guidance we fell
   back to the latest stable release. `0.34.1`'s newer zlib guards that macro on
   `_BEOS_`/`_WIN32_WCE` only and builds cleanly. **The clua API we rely on is
   identical in both versions**, so the bridge is version-agnostic.
3. Console build needs only 4 contrib submodules (`lua`, `pcre`, `sqlite`,
   `zlib`); the `sdl2`/`freetype`/`libpng` ones are tiles-only — skipping them
   makes the checkout much faster. Toolchain needs: `flex`, `bison`,
   `pkg-config`, `perl` (all present on a stock macOS dev box).

---

## The bridge (how lockstep works)

crawl calls a global Lua `ready()` every time it awaits player input
(`main.cc: clua.callfn("ready", …)`). Our `ready()`:

1. gathers state from the clua API (`you.*`, `view.*`, `monster.*`),
2. serialises it to one JSON line with a hand-rolled encoder,
3. `io.open(state_fifo,"w")` → writes the line (this **blocks until Python opens
   the read end** — that blocking open *is* the handshake),
4. `io.open(action_fifo,"r")` → **blocks reading one action token**,
5. translates the token (`N/S/E/…/WAIT`) to a key and `crawl.sendkeys()`.

The game is frozen inside step 4 until the agent answers, so the loop is strict
lockstep — no polling, no races. The Python side uses non-blocking `open()` +
`select()` so it can detect crawl death/hang via timeout rather than deadlock.
crawl is a curses program, so Python launches it under a `pty` and drains the
master so screen writes never block; the agent never types at the terminal.

### Measured performance

| run | states | turn advances | steps/sec | outcome |
|-----|--------|---------------|-----------|---------|
| 100 turns  | 100  | 83  (turns 0→83)   | **1,510** | survived |
| 1000 turns | 1000 | 618 (turns 0→619)  | **1,583** | survived |

`steps/sec` is per observe→act cycle, measured from the first state to the last
(startup/DB-build excluded). ~0.6 ms per full round-trip — crawl processes the
move, re-scans a 17×17 tile window + monster grid, encodes JSON, and round-trips
two FIFOs in well under a millisecond. (Turn advances < states because ~38% of
random moves walk into a wall, which costs no game turn — expected.) Agent death
is handled: a Minotaur Berserker rarely dies wandering D:1, so these runs
survived, but a state-timeout after ≥1 turn is detected and treated as a clean
end.

---

## clua API surface (what ground truth is available)

This is the crux for replacing webtiles. **All of the following is real
structured data — no glyphs, no menu scraping.**

### Player — rich ✅
`you.hp()`→(hp,max), `you.mp()`, `you.turns()`, `you.time()`, `you.xl()`,
`you.gold()`, `you.god()`, `you.name()/race()/class()`, `you.where()` (e.g.
`"D:1"`), `you.branch()/depth()/absdepth()`, `you.los()`, plus ~60 status
predicates (`berserk()`, `confused()`, `poisoned()`, `paralysed()`, `slowed()`,
`feel_safe()`, resistances, `status()`, …).

### Map — rich ✅
`view.feature_at(dx,dy)` returns the dungeon-feature **name string** for a
player-centred cell, read from the player's **remembered** map
(`env.map_knowledge`) — so it's the explored map, not just current LOS. Values
like `floor`, `rock_wall`, `closed_door`, `escape_hatch_down`,
`stone_stairs_down_i`. Also `view.is_safe_square`, `view.cloud_at`,
`view.invisible_monster`. A first-turn state scans a 17×17 window and yields ~96
known cells (grows as the agent explores).

### Monsters — rich ✅
`monster.get_monster_at(dx,dy)` (player-centred coords, only what the player can
see) → a monster-info object with `name()`, `attitude()` (0=hostile),
`threat()` (0–3), `is_safe()`, `max_hp()`, `damage_level()`, `holiness()`,
`speed_description()`, resistances, spell list, and more. Captured live (seed 5,
turn 56):
```json
{"name":"kobold","attitude":0,"threat":0,"dx":1,"dy":7,"safe":false}
```

### Inventory / items — available ✅ (not serialised in this spike, but present)
`items.inventory()` → item objects with `name()`, `quantity()`, `class()`,
`subtype()`, `slot()`, `equipped()`, `is_useless()`, `artefact()`, `plus`, …;
plus `items.equipped_at()`, `items.fired_item()`, `items.inslot()`.

### What's missing / caveats ⚠️
- **Absolute player grid coordinates are NOT exposed to client clua.**
  `you.pos()/x_pos()/y_pos()` exist only in the *dungeon-Lua* `you` table, not
  the client one. The player is simply the **origin (0,0)** of the player-centred
  frame that `view.*`/`monster.*` already use, so relative geometry is complete;
  the driver dead-reckons displacement from issued moves when it needs an
  absolute-ish position. (`you.where()`/`depth()` give the branch/level.)
- **Actions go in as keystrokes** (`crawl.sendkeys`). That's fine for movement
  but higher-level intents (travel-to, use-item-by-name) still mean composing key
  sequences, exactly as a human client would. `crawl.do_commands` exists for
  named commands.
- **Menus/prompts must be pre-suppressed via rc options** (`show_more=false`,
  `weapon=random`, etc.). Anything that pops an unexpected `y/n` or item menu
  would stall the loop until it times out. Robustifying prompt handling is the
  main follow-up engineering.

### Sample state (first turn, seed 1, MiBe) — 24 top-level keys, one JSON line
```json
{"turn_id":1,"turns":0,"time":0,"name":"BridgeBot","race":"Minotaur",
 "class":"Berserker","place":"D:1","depth":1,"hp":19,"hp_max":19,"mp":0,
 "mp_max":0,"x":0,"y":0,"xl":1,"gold":0,"god":"Trog","berserk":false,
 "confused":false,"poisoned":false,"feel_safe":true,"los":7,
 "cells":[{"dx":-1,"dy":-7,"feat":"floor"}, ... 96 cells ...],
 "monsters":[]}
```

---

## Problems hit (and how they were solved)

1. **rc Lua block terminates at the first bare `}` line.** crawl's rc parser ends
   a `{`…`}` Lua block at the first line that trims to exactly `}`
   (`initfile.cc`). My first `bridge.rc` had table-closing braces on their own
   lines, so the block ended early and the *rest* of the Lua got parsed as
   options (yielding `Unknown species choice: you.race()` — because `race`/`class`
   are legacy option aliases!). Fix: **never put a `}` alone on a line** —
   every table close is attached to a code line; the only bare `}` is the block
   terminator. (Loading Lua from an external file via `dofile` is *not* an escape
   hatch: crawl's `dofile` only resolves paths inside its own data dirs and
   rejects arbitrary absolute paths.)
2. **`you.pos()` is nil in client clua** → see caveat above.
3. **First run rebuilds the database (~30 s) and blocks on a "Press Esc" screen.**
   Wiping crawl's home dir each run deleted the compiled `.db`/`.des` cache,
   forcing a slow interactive rebuild that blew the state timeout. Fix: pre-build
   non-interactively with `crawl -builddb`, and per-run delete only the character
   save (keeping the cache) so each launch is a fresh game with no resume prompt.
4. **Saves default to `~/Library/Application Support/…` on macOS**, not the CWD.
   Fix: `-dir /tmp/dcss_spike/home` sandboxes all state to `/tmp` (repo stays
   clean, no cross-run resume prompt).

---

## Recommendation: **GO** (as the primary transport, with a scoped follow-up)

**One-sentence rationale:** the clua bridge delivers typed ground-truth state
(map tiles by name, monsters with attitude/threat, full player stats/inventory)
in strict lockstep at ~1,500 turns/sec with zero glyph parsing and zero menu
scraping — structurally eliminating the exact failure modes that make the 2,400-
line webtiles parser painful — so it's the better long-term transport.

**Why GO:**
- Ground truth *is* the game's own data model; no rendering-protocol reverse
  engineering, no incomplete glyph tables, no menu screen-scraping.
- Lockstep is free and exact (the blocking FIFO read is the sync primitive).
- Throughput is ~1,500×/sec — orders of magnitude beyond what a webtiles
  socket + parser gives, which matters for RL/search.
- Additive and low-risk: one build flag, one rc file, external Python. Nothing in
  `src/` changed.

**Caveats / follow-up before it replaces webtiles wholesale:**
- **Prompt/menu robustness** is the real work: the bridge assumes prompts are
  suppressed. Interactive item selection, `y/n` confirms, level-transition and
  death screens each need explicit handling (detect via message channel /
  `crawl.messages`, answer via `sendkeys`) or the loop stalls.
- **Requires a custom crawl build** (`CLUA_UNRESTRICTED_LIBS`). Fine for a
  controlled research setup; it means you ship/operate your own crawl binary
  rather than pointing at a stock server. (Bots on public servers can't use
  `io`/`os` — but this project controls its own build, so that's a non-issue.)
- **Action expressivity**: still keystroke-level. Building a small action
  vocabulary (travel, pick-up, wield-by-name) on top of `sendkeys`/`do_commands`
  is straightforward but not yet done.
- **Version pin**: build is `0.34.1`, not the docker's `0.26.1`. If parity with
  the existing webtiles stack's game version matters, that's a coordination item;
  the bridge itself is version-agnostic across the clua API.

Net: keep webtiles only if you must target an unmodified upstream server.
For this repo — which builds and controls its own crawl — the FIFO/clua bridge is
the recommended primary transport.
