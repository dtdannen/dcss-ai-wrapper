#!/usr/bin/env python3
"""
Attach-mode random agent for the webtiles bridge.

Unlike random_agent.py (which spawns its own console crawl under a pty), this
does NOT launch crawl. It just creates the two FIFOs and waits for a crawl
process that the *webtiles server* spawned to open them. That crawl loaded
bridge.rc (installed as the account's rc), whose ready() hook talks the same
FIFO protocol. So the control/state path is the FIFO bridge and the *rendering*
path is webtiles -> browser: exactly the architecture split we're validating.

Because a human is watching in a browser, actions are throttled by --delay so
the game plays at a watchable pace instead of ~1500 turns/sec.

Usage:
    # 1. start the webtiles server (spike/setup_webtiles.sh)
    # 2. run this and leave it waiting:
    python3 spike/attach_agent.py --turns 400 --delay 0.05
    # 3. open http://localhost:8080, log in as BridgeBot, click the Bridge game
"""
import argparse
import errno
import json
import os
import random
import select
import time

STATE_FIFO_DEFAULT = "/tmp/dcss_state"
ACTION_FIFO_DEFAULT = "/tmp/dcss_action"

SAFE_ACTIONS = ["N", "S", "E", "W", "NE", "NW", "SE", "SW", "WAIT"]
ACTION_VEC = {
    "N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0),
    "NE": (1, -1), "NW": (-1, -1), "SE": (1, 1), "SW": (-1, 1), "WAIT": (0, 0),
}


def make_fifo(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)


def read_state(state_fifo, timeout):
    fd = os.open(state_fifo, os.O_RDONLY | os.O_NONBLOCK)
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
            if chunk == b"":
                return buf.decode("utf-8", "replace").strip() or None
            buf += chunk
        return buf.decode("utf-8", "replace").strip()
    finally:
        os.close(fd)


def write_action(action_fifo, action, timeout):
    deadline = time.time() + timeout
    fd = None
    while fd is None:
        try:
            fd = os.open(action_fifo, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as e:
            if e.errno == errno.ENXIO:
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


def main():
    ap = argparse.ArgumentParser(description="Attach-mode random agent (webtiles bridge)")
    ap.add_argument("--turns", type=int, default=400, help="max observe/act cycles")
    ap.add_argument("--delay", type=float, default=0.05,
                    help="seconds between actions so a human can watch (default 0.05)")
    ap.add_argument("--state-fifo", default=STATE_FIFO_DEFAULT)
    ap.add_argument("--action-fifo", default=ACTION_FIFO_DEFAULT)
    ap.add_argument("--first-timeout", type=float, default=180.0,
                    help="seconds to wait for the first state (start the game in the browser)")
    ap.add_argument("--seed", type=int, default=42, help="agent RNG seed")
    args = ap.parse_args()

    random.seed(args.seed)
    make_fifo(args.state_fifo)
    make_fifo(args.action_fifo)
    print(f"FIFOs ready: {args.state_fifo} / {args.action_fifo}")
    print(f"waiting up to {args.first_timeout:.0f}s for a webtiles-spawned game "
          f"to reach ready()...\n(open http://localhost:8080, log in as BridgeBot, "
          f"start the Bridge game)\n", flush=True)

    received = 0
    turn_advances = 0
    last_turns = None
    pending = None
    rx = ry = 0
    death = False
    try:
        for step in range(args.turns):
            timeout = args.first_timeout if received == 0 else 15.0
            line = read_state(args.state_fifo, timeout)
            if line is None:
                if received == 0:
                    print("no game connected within timeout; exiting.")
                else:
                    print(f"[{received}] state stream ended -> game over / agent died.")
                    death = True
                break
            try:
                state = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"invalid JSON: {e}")
                break

            received += 1
            if last_turns is not None and state.get("turns", 0) > last_turns:
                turn_advances += 1
                if pending:
                    dx, dy = ACTION_VEC[pending]
                    rx += dx
                    ry += dy
            last_turns = state.get("turns")

            if received <= 3 or received % 20 == 0:
                print(f"[recv {received:>4}] turns={state.get('turns')} "
                      f"hp={state.get('hp')}/{state.get('hp_max')} {state.get('place')} "
                      f"reckon=({rx:+d},{ry:+d}) cells={len(state.get('cells', []))} "
                      f"mons={len(state.get('monsters', []))}", flush=True)

            if state.get("hp", 1) <= 0:
                death = True
                print(f"[recv {received}] hp<=0 -> dead")
                break

            action = random.choice(SAFE_ACTIONS)
            pending = action
            if not write_action(args.action_fifo, action, 15.0):
                print("crawl stopped reading actions -> ending.")
                break
            if args.delay > 0:
                time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\ninterrupted.")

    print("\n==================== ATTACH RESULT ====================")
    print(f"states received : {received}")
    print(f"turn advances   : {turn_advances}")
    print(f"reckoned pos    : ({rx:+d},{ry:+d})")
    print(f"game ended/death: {death}")
    ok = received >= 1 and (turn_advances >= 1 or death)
    print("VERDICT:", "PASS - drove a webtiles game over the FIFO bridge" if ok
          else "FAIL - no turns driven")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
