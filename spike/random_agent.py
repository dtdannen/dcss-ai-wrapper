#!/usr/bin/env python3
"""
T0 spike: external random agent driving DCSS (crawl) in lockstep over FIFOs.

Pipeline
--------
    crawl (console, built with -DCLUA_UNRESTRICTED_LIBS)
        loads spike/bridge.rc, whose ready() hook each turn:
            writes ground-truth JSON state  -> $DCSS_STATE_FIFO
            blocks reading an action token  <- $DCSS_ACTION_FIFO
    this script:
            reads the state line, asserts it is valid,
            picks a random SAFE action (8-dir move or wait),
            writes the action token back.
    The blocking FIFO read on the crawl side gives strict lockstep: the game
    does not advance until this script answers.

crawl is a curses program, so it is launched under a pty. We never need to type
at it (the agent drives via clua sendkeys); a background thread just drains the
pty so crawl's screen writes never block.

Run:  python3 spike/random_agent.py [num_turns] [--view] [--delay SECONDS]
      --view mirrors crawl's screen to this terminal; --delay throttles the
      agent so the game is watchable (defaults to 0.03s with --view, else 0).
"""
import argparse
import errno
import glob
import json
import os
import random
import select
import shutil
import signal
import struct
import subprocess
import sys
import termios
import threading
import time
import fcntl
from collections import deque

HERE        = os.path.dirname(os.path.abspath(__file__))
CRAWL_SRC   = os.path.join(HERE, "crawl", "crawl-ref", "source")
CRAWL_BIN   = os.path.join(CRAWL_SRC, "crawl")
RC_FILE     = os.path.join(HERE, "bridge.rc")

STATE_FIFO  = os.environ.get("DCSS_STATE_FIFO",  "/tmp/dcss_state")
ACTION_FIFO = os.environ.get("DCSS_ACTION_FIFO", "/tmp/dcss_action")

SANDBOX     = "/tmp/dcss_spike"
HOME_DIR    = os.path.join(SANDBOX, "home")     # crawl_dir: saves/morgue/etc land here
MORGUE_DIR  = os.path.join(SANDBOX, "morgue")

CRAWL_SEED  = 1
AGENT_SEED  = 42          # seeds the agent's *own* random choices (reproducible)

# SAFE action set: 8-direction movement + wait. No stairs, items, or prompts.
SAFE_ACTIONS = ["N", "S", "E", "W", "NE", "NW", "SE", "SW", "WAIT"]

# Movement vectors (dx, dy) with +y = south, matching crawl's screen coords.
# Absolute player coords aren't exposed to client clua (you.pos is dungeon-Lua
# only), so we dead-reckon displacement from the moves that actually took a turn.
ACTION_VEC = {
    "N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0),
    "NE": (1, -1), "NW": (-1, -1), "SE": (1, 1), "SW": (-1, 1), "WAIT": (0, 0),
}

FIRST_STATE_TIMEOUT = 30.0   # crawl startup + DLvl1 generation
STATE_TIMEOUT       = 12.0   # a normal ready() cycle is sub-second


# --------------------------------------------------------------------------- #
# FIFO helpers (non-blocking + select so we can time out on crawl death)
# --------------------------------------------------------------------------- #
def make_fifo(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)


def read_state(timeout):
    """Read one newline-terminated line from STATE_FIFO or None on timeout/EOF."""
    fd = os.open(STATE_FIFO, os.O_RDONLY | os.O_NONBLOCK)
    try:
        buf = b""
        deadline = time.time() + timeout
        while not buf.endswith(b"\n"):
            remaining = deadline - time.time()
            if remaining <= 0:
                return None
            r, _, _ = select.select([fd], [], [], remaining)
            if not r:
                return None
            chunk = os.read(fd, 1 << 16)
            if chunk == b"":            # writer (crawl) closed
                return buf.decode("utf-8", "replace").strip() or None
            buf += chunk
        return buf.decode("utf-8", "replace").strip()
    finally:
        os.close(fd)


def write_action(action, timeout):
    """Write one action token to ACTION_FIFO. False if no reader appears."""
    deadline = time.time() + timeout
    fd = None
    while fd is None:
        try:
            fd = os.open(ACTION_FIFO, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as e:
            if e.errno == errno.ENXIO:          # crawl hasn't opened read end yet
                if time.time() >= deadline:
                    return False
                time.sleep(0.002)
                continue
            raise
    try:
        os.write(fd, (action + "\n").encode())
        return True
    finally:
        os.close(fd)


# --------------------------------------------------------------------------- #
# crawl process under a pty
# --------------------------------------------------------------------------- #
def ensure_databases():
    """Build crawl's .db/.des cache non-interactively (one-time, ~30s).

    crawl compiles dat/*.des + dat/database/*.txt into HOME_DIR/saves/{db,des}
    on first run. Doing it interactively blocks on a 'Press Esc to close' screen
    and can exceed the state timeout, so we pre-build it with `-builddb`.
    """
    dbdir = os.path.join(HOME_DIR, "saves", "db")
    if os.path.isdir(dbdir) and os.listdir(dbdir):
        return
    os.makedirs(HOME_DIR, exist_ok=True)
    print("building crawl databases (one-time)...", flush=True)
    subprocess.run([CRAWL_BIN, "-builddb", "-dir", HOME_DIR],
                   cwd=CRAWL_SRC, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)


def launch_crawl(view=False):
    # Sandbox ALL crawl state under /tmp via -dir (crawl_dir): on macOS crawl
    # otherwise saves to ~/Library/Application Support/... . Keep the db/des
    # cache between runs (rebuilding it every launch is slow) but remove the
    # character save so each launch is a fresh game with no "resume?" prompt.
    os.makedirs(HOME_DIR, exist_ok=True)
    os.makedirs(MORGUE_DIR, exist_ok=True)
    ensure_databases()
    for f in glob.glob(os.path.join(HOME_DIR, "saves", "BridgeBot*")):
        try:
            os.remove(f)
        except OSError:
            pass

    master_fd, slave_fd = os.openpty()
    # crawl wants at least 80x24; give it a comfortable window. In view mode,
    # match the real terminal so the mirrored screen isn't garbled.
    rows, cols = 40, 110
    if view:
        ts = shutil.get_terminal_size((cols, rows))
        rows, cols = max(ts.lines, 24), max(ts.columns, 80)
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

    env = dict(os.environ)
    env["TERM"] = "xterm-256color"
    env["LINES"] = str(rows)
    env["COLUMNS"] = str(cols)
    env["DCSS_STATE_FIFO"] = STATE_FIFO
    env["DCSS_ACTION_FIFO"] = ACTION_FIFO

    argv = [
        CRAWL_BIN,
        "-name", "BridgeBot",
        "-species", "Minotaur",
        "-background", "Berserker",
        "-seed", str(CRAWL_SEED),
        "-rc", RC_FILE,
        "-dir", HOME_DIR,
        "-morgue", MORGUE_DIR,
    ]
    proc = subprocess.Popen(
        argv,
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        cwd=CRAWL_SRC, env=env,
        start_new_session=True, close_fds=True,
    )
    os.close(slave_fd)

    # Drain the pty so crawl never blocks writing to its "screen".
    tail = deque(maxlen=400)

    def drain():
        try:
            while True:
                data = os.read(master_fd, 4096)
                if not data:
                    break
                tail.append(data)
                if view:
                    os.write(1, data)      # mirror crawl's screen live
        except OSError:
            pass

    t = threading.Thread(target=drain, daemon=True)
    t.start()
    return proc, master_fd, tail


def screen_tail(tail, nbytes=1200):
    raw = b"".join(tail)[-nbytes:]
    return raw.decode("utf-8", "replace")


# --------------------------------------------------------------------------- #
# main lockstep loop
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(
        description="random agent driving crawl in lockstep over FIFOs")
    ap.add_argument("num_turns", nargs="?", type=int, default=100)
    ap.add_argument("--view", action="store_true",
                    help="mirror crawl's screen to this terminal")
    ap.add_argument("--delay", type=float, default=None, metavar="SECONDS",
                    help="pause between actions (default: 0.03 with --view, else 0)")
    args = ap.parse_args()
    num_turns = args.num_turns
    view = args.view
    delay = args.delay if args.delay is not None else (0.03 if view else 0.0)

    if not os.path.exists(CRAWL_BIN):
        print(f"FAIL: crawl binary not found at {CRAWL_BIN}\n"
              f"      build it first:  spike/build_crawl.sh", file=sys.stderr)
        return 2

    random.seed(AGENT_SEED)
    make_fifo(STATE_FIFO)
    make_fifo(ACTION_FIFO)

    proc, master_fd, tail = launch_crawl(view)
    if not view:
        print(f"launched crawl pid={proc.pid}; seed={CRAWL_SEED}; "
              f"driving {num_turns} turns of MiBe over FIFOs\n")

    received = 0
    turn_advances = 0
    last_turns = None
    first_state = None
    last_state = None
    death = False
    t_first = None
    t_last = None
    pending_action = None        # last action sent, awaiting its turn effect
    rx = ry = 0                  # dead-reckoned displacement from start
    max_dist = 0                 # furthest Chebyshev distance reached

    try:
        for step in range(num_turns):
            timeout = FIRST_STATE_TIMEOUT if received == 0 else STATE_TIMEOUT
            line = read_state(timeout)

            if line is None:
                if proc.poll() is not None:
                    print(f"[step {step}] crawl exited (rc={proc.returncode}).")
                elif received > 0:
                    print(f"[step {step}] no state within {timeout:.0f}s after "
                          f"{received} turns -> agent died / game ended.")
                    death = True
                else:
                    print(f"[step {step}] no first state within {timeout:.0f}s.\n"
                          f"--- pty tail (startup) ---\n{screen_tail(tail)}")
                break

            try:
                state = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[step {step}] INVALID JSON: {e}\n  line={line[:400]!r}")
                break

            # ---- assertions on ground-truth state ----
            assert "hp" in state,   f"state missing hp: {list(state)}"
            assert "turns" in state, "state missing turns"
            assert "x" in state and "y" in state, "state missing position"
            assert "cells" in state, "state missing map cells"

            received += 1
            now = time.time()
            if t_first is None:
                t_first = now
                first_state = state
            t_last = now
            last_state = state

            if last_turns is not None and state["turns"] > last_turns:
                turn_advances += 1
                # the previous action consumed a turn -> it (probably) moved us
                if pending_action:
                    dx, dy = ACTION_VEC[pending_action]
                    rx += dx
                    ry += dy
                    max_dist = max(max_dist, max(abs(rx), abs(ry)))
            last_turns = state["turns"]

            if not view and (received <= 3 or received % 25 == 0):
                print(f"[recv {received:>3}] turns={state['turns']:>4} "
                      f"reckon=({rx:+d},{ry:+d}) hp={state['hp']}/{state['hp_max']} "
                      f"{state['place']} cells={len(state['cells'])} "
                      f"mons={len(state['monsters'])}")

            if state["hp"] <= 0:
                death = True
                print(f"[recv {received}] hp<=0 -> dead")
                break

            if delay:
                time.sleep(delay)
            action = random.choice(SAFE_ACTIONS)
            pending_action = action
            if not write_action(action, STATE_TIMEOUT):
                print(f"[step {step}] crawl never read action -> ending.")
                break
    finally:
        try:
            # dismiss any end-of-game prompt, then stop crawl
            os.write(master_fd, b"\r\x1b\r")
        except OSError:
            pass
        time.sleep(0.2)
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except OSError:
                proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    # ---- results ----
    if view:
        # leave crawl's alt screen, reset attrs, restore cursor
        os.write(1, b"\x1b[?1049l\x1b[0m\x1b[?25h\n")
    elapsed = (t_last - t_first) if (t_first and t_last and t_last > t_first) else 0.0
    sps = (received - 1) / elapsed if elapsed > 0 else 0.0

    print("\n==================== RESULT ====================")
    print(f"states received : {received}")
    print(f"turn advances   : {turn_advances} (in-game you.turns increased)")
    if first_state and last_state:
        print(f"turns start->end: {first_state['turns']} -> {last_state['turns']}")
        print(f"reckoned pos    : ({rx:+d},{ry:+d})  max dist from start: {max_dist}")
        print(f"hp    start->end: {first_state['hp']}/{first_state['hp_max']} -> "
              f"{last_state['hp']}/{last_state['hp_max']}")
    print(f"elapsed (obs)   : {elapsed:.2f}s")
    print(f"steps/sec       : {sps:.1f}")
    print(f"agent death/end : {death}")

    ok = received >= 1 and (turn_advances >= 1 or death)
    if first_state:
        print("\n--- sample first-turn state (pretty) ---")
        print(json.dumps(first_state, indent=2)[:1600])
    if last_state and last_state.get("monsters"):
        print("\n--- monsters in last state ---")
        print(json.dumps(last_state["monsters"], indent=2)[:800])

    print("\nVERDICT:", "PASS - lockstep FIFO bridge works" if ok
          else "FAIL - see above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
