#!/usr/bin/env python3
"""
Headless end-to-end proof for the webtiles + FIFO bridge, no browser needed.

It does what a browser would do, over the webtiles websocket protocol:
  1. connect to ws://localhost:8080/socket  (request `no-compression` so frames
     are plaintext JSON)
  2. log in as BridgeBot
  3. `play` the Bridge game -> the server spawns crawl-web (-await-connection is
     satisfied by this very websocket), which loads bridge.rc

Meanwhile, in a background thread, it runs the SAME FIFO lockstep loop as
attach_agent.py, driving the game with throttled random moves.

Success = the websocket receives real game render messages (`map`, `player`,
...) — i.e. exactly what the browser renders — while the FIFO side advances
in-game turns. That proves the split: FIFO = control/state, webtiles = view.

Run (after spike/setup_webtiles.sh started the server):
    /tmp/dcss_spike_web/venv/bin/python spike/verify_webtiles.py
(uses tornado, which the venv already has; plain python3 works too if tornado
 is importable.)
"""
import argparse
import asyncio
import errno
import json
import os
import random
import select
import threading
import time
import zlib
from collections import Counter

from tornado.websocket import websocket_connect

STATE_FIFO = "/tmp/dcss_state"
ACTION_FIFO = "/tmp/dcss_action"
SAFE_ACTIONS = ["N", "S", "E", "W", "NE", "NW", "SE", "SW", "WAIT"]


# ----- FIFO lockstep driver (runs in a thread; blocking I/O) ------------------
def make_fifo(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)


def _read_state(timeout):
    fd = os.open(STATE_FIFO, os.O_RDONLY | os.O_NONBLOCK)
    try:
        buf = b""
        deadline = time.time() + timeout
        while not buf.endswith(b"\n"):
            r, _, _ = select.select([fd], [], [], max(0, deadline - time.time()))
            if not r:
                return None
            chunk = os.read(fd, 1 << 16)
            if chunk == b"":
                return buf.decode("utf-8", "replace").strip() or None
            buf += chunk
        return buf.decode("utf-8", "replace").strip()
    finally:
        os.close(fd)


def _write_action(action, timeout):
    deadline = time.time() + timeout
    fd = None
    while fd is None:
        try:
            fd = os.open(ACTION_FIFO, os.O_WRONLY | os.O_NONBLOCK)
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


def fifo_driver(turns, delay, stats, stop):
    random.seed(42)
    received = 0
    last_turns = None
    while not stop.is_set() and received < turns:
        line = _read_state(120.0 if received == 0 else 15.0)
        if line is None:
            break
        try:
            st = json.loads(line)
        except json.JSONDecodeError:
            break
        received += 1
        stats["received"] = received
        if last_turns is not None and st.get("turns", 0) > last_turns:
            stats["turn_advances"] = stats.get("turn_advances", 0) + 1
        last_turns = st.get("turns")
        stats["last"] = {k: st.get(k) for k in ("turns", "hp", "hp_max", "place")}
        if st.get("hp", 1) <= 0:
            stats["death"] = True
            break
        if not _write_action(random.choice(SAFE_ACTIONS), 15.0):
            break
        if delay > 0:
            time.sleep(delay)
    stats["done"] = True


# ----- websocket spectator ----------------------------------------------------
def decode_frame(msg):
    if isinstance(msg, bytes):
        # server compressed with raw deflate; append the flush marker and inflate
        d = zlib.decompressobj(-zlib.MAX_WBITS)
        msg = d.decompress(msg + b"\x00\x00\xff\xff").decode("utf-8", "replace")
    return json.loads(msg)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="ws://localhost:8080/socket")
    ap.add_argument("--user", default="BridgeBot")
    ap.add_argument("--password", default="bridge")
    ap.add_argument("--game", default="bridge-mibe")
    ap.add_argument("--turns", type=int, default=60)
    ap.add_argument("--delay", type=float, default=0.05)
    ap.add_argument("--timeout", type=float, default=90.0)
    ap.add_argument("--no-drive", action="store_true",
                    help="only play + spectate over the websocket; let a separate "
                         "attach_agent.py drive the FIFOs (validates the standalone tool)")
    args = ap.parse_args()

    stats = {}
    stop = threading.Event()
    if args.no_drive:
        print("(--no-drive: an external attach_agent.py must drive the FIFOs)")
    else:
        make_fifo(STATE_FIFO)
        make_fifo(ACTION_FIFO)
        drv = threading.Thread(target=fifo_driver, args=(args.turns, args.delay, stats, stop), daemon=True)
        drv.start()

    print(f"connecting {args.url} (no-compression) ...", flush=True)
    conn = await websocket_connect(args.url, subprotocols=["no-compression"])
    await conn.write_message(json.dumps({"msg": "login",
                                         "username": args.user, "password": args.password}))

    seen = Counter()
    logged_in = game_started = False
    render_msgs = ("map", "player", "cursor", "input_mode", "vgrdc", "flash")
    render_seen = Counter()
    deadline = time.time() + args.timeout

    while time.time() < deadline:
        try:
            raw = await asyncio.wait_for(conn.read_message(), timeout=deadline - time.time())
        except asyncio.TimeoutError:
            break
        if raw is None:
            print("websocket closed by server.")
            break
        try:
            env = decode_frame(raw)
        except Exception as e:  # noqa: BLE001
            print("frame decode error:", e)
            continue
        msgs = env.get("msgs", [env]) if isinstance(env, dict) else env
        for m in msgs:
            if not isinstance(m, dict):
                continue
            t = m.get("msg")
            seen[t] += 1
            if t in render_msgs:
                render_seen[t] += 1
            if t == "login_success" and not logged_in:
                logged_in = True
                print(f"logged in as {m.get('username')}; sending play '{args.game}'", flush=True)
                await conn.write_message(json.dumps({"msg": "play", "game_id": args.game}))
            elif t == "login_fail":
                print("LOGIN FAILED:", m.get("reason"))
                stop.set()
                return 1
            elif t == "game_started" and not game_started:
                game_started = True
                print("game_started: crawl-web spawned & rendering to the socket", flush=True)
            elif t == "go_lobby" and game_started:
                print("game ended (go_lobby).")
                deadline = 0  # exit loop
        # stop once we've proven rendering (and, when we drive, that turns advance)
        if game_started and render_seen:
            if args.no_drive and render_seen.get("map") and render_seen.get("player"):
                # let the external driver run a bit, then finish
                if time.time() > deadline - args.timeout + 12:
                    break
            elif stats.get("turn_advances", 0) >= 5 and stats.get("received", 0) >= 10:
                break

    stop.set()
    time.sleep(0.3)

    print("\n==================== WEBTILES E2E RESULT ====================")
    print(f"logged_in           : {logged_in}")
    print(f"game_started        : {game_started}")
    print(f"render msgs received: {dict(render_seen)}")
    print(f"top ws msg types    : {dict(Counter(dict(seen)).most_common(10))}")
    print(f"FIFO states received: {stats.get('received', 0)}")
    print(f"FIFO turn advances  : {stats.get('turn_advances', 0)}")
    print(f"last state          : {stats.get('last')}")
    ok = logged_in and game_started and bool(render_seen)
    if not args.no_drive:
        ok = ok and stats.get("turn_advances", 0) >= 1
    print("\nVERDICT:", "PASS - browser-renderable game driven over the FIFO bridge"
          if ok else "FAIL - see above")
    try:
        conn.close()
    except Exception:  # noqa: BLE001
        pass
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
