# dcss-ai-wrapper — LLM agent track

Working context for the LLM-agent track, developed alongside the RL track on the same wrapper.

**Repo:** `salavii/dcss-ai-wrapper` · **Base branch:** `add-rl-training-pipeline` · **Work branch:** `llm-agent-view`

---

## 1. Overview

`dcss-ai-wrapper` connects Dungeon Crawl Stone Soup to AI agents:

```
DCSS → WebSocket → Wrapper → GameState → Agent → Action → DCSS
```

The game streams state over a WebSocket, the wrapper turns it into a `GameState` object, an `Agent` returns an `Action`, and the action goes back to the game.

Two tracks share this wrapper. The **RL track** runs a Gymnasium environment with PPO; its agent sees only a `radius=3` window (49 tiles) and has no memory of where it has been. The **LLM track** (this document) puts a language model in the decision loop instead of training a network from scratch, using **prime-agent** as the harness.

**Architecture decision (settled):** the LLM connects through the wrapper, not through the terminal screen. prime-agent's strength is writing and running Python, and the wrapper exposes the game as structured Python objects (`gs.player_current_hp`, `gs.get_cell_map().draw_cell_map()`, `gs.messages[turn]`), so the agent can build its own helper functions over time. A raw text screen would not be programmable.

---

## 2. Code map

Files that matter for this track, in order of relevance:

`src/dcss/state/game.py` (2447 lines) — the `GameState` class. ~90 player attributes (`player_current_hp`, `player_hp_max`, `player_ac`, `player_ev`, `player_place`, `player_depth`, `player_status_effects`, …), plus `messages` as a `{turn: [text, ...]}` dict, `inventory_by_id`, and the `get_cell_map()` / `get_current_game_turn()` accessors.

`src/dcss/state/cellmap.py` (449 lines) — the `CellMap` class, holding every tile seen so far. `draw_cell_map()` returns an ASCII map of the whole floor as a string. `agent_x` / `agent_y` are the authoritative player coordinates.

`src/dcss/agent/gym_bridge_agent.py` (198 lines) — the queue bridge, and the reason the architecture looks the way it does. `get_action()` is called from inside the asyncio loop, so a model that thinks for 20 seconds would stall the connection. The bridge solves this with two single-slot queues. **It is tested — reuse it, do not rebuild it.**

`src/dcss/rl/dcss_gym_env.py` — shows how the bridge is actually driven: the async connection runs on a background thread and talks to synchronous code through `action_queue` / `observation_queue`. The LLM loop should mirror this pattern.

`src/dcss/connection/autobahn_game_connection.py` (1133 lines) — connection layer: login, menus, character creation, prompts. The `MenuChoice` branch around **line 313** is commented out.

`src/dcss/actions/command.py` — the `Command` enum, 93 members: 8-directional move/attack, `AUTO_EXPLORE`, `AUTO_FIGHT`, `REST_AND_LONG_WAIT`, `TRAVEL_STAIRCASE_DOWN`, `PICKUP_ITEM`, and more.

`src/dcss/connection/config.py` — `WebserverConfig`: server URI (`ws://127.0.0.1:8080/socket`), agent credentials (`midca`/`midca`), species/background/weapon, `draw_map`.

---

## 3. Known wrapper fragilities

The wrapper is brittle; a full day was previously lost to hangs and livelocks. These are confirmed and are worked around rather than fixed, since the connection and state files are shared with the RL track:

`InventoryItem.__init__` never assigns `self.equipped`, so `is_item_equipped()` raises `AttributeError` on any item that was never passed through `equip()`. Use `getattr(item, 'equipped', False)`.

`CellMap.draw_cell_map()` indexes `min_x`/`max_x` and the place/depth dict without guarding, so it raises on a fresh game before map data arrives. Check for map data first.

`GameState.get_player_xy()` returns legacy `map_obj` coordinates that stay `None` even when the cell map is fully populated. Use `cellmap.agent_x` / `agent_y` so the reported position agrees with the `@` on the rendered map.

`GameState.draw_cell_map()` prints and returns `None`; the string comes from `gs.get_cell_map().draw_cell_map()`.

`cellmap.add_or_update_cell` line 59 assigns `vals['y'] = x`, almost certainly meant to be `y`. Hidden because the server nearly always sends `y` itself. Flagged, not changed.

The rule these imply: **nothing in the LLM path may raise.** An exception mid-episode stalls the connection thread.

---

## 4. Conventions

Separate three levels of claim: **verified** (run and observed), **inferred from code** (read but not run), **needs testing**. Keep changes small and testable, and take a baseline before changing anything. Do not commit to `add-rl-training-pipeline` — that is the active RL branch; LLM work goes on `llm-agent-view`. Start simple, get something working, then enrich it.

---

## 5. Setup

```bash
git clone -b add-rl-training-pipeline https://github.com/salavii/dcss-ai-wrapper.git
cd dcss-ai-wrapper
python3 -m venv .env && source .env/bin/activate
pip install -r requirements.txt
pip install -e .
```

On Apple Silicon, `cffi==1.14.5` has no prebuilt wheel and needs a compiler. Relaxing that one pin avoids installing Xcode command line tools:

```bash
sed 's/^cffi==.*/cffi/' requirements.txt > /tmp/req-mac.txt && pip install -r /tmp/req-mac.txt
```

Game server:

```bash
docker pull dtdannen34/dcss-ai-wrapper:webtilesserver
docker run -it -p 8080:8080 dtdannen34/dcss-ai-wrapper:webtilesserver
# inside the container:
cd /dcss/crawl/crawl-ref/source/webserver && source venv/bin/activate
cd .. && python webserver/server.py
```

Then open `http://localhost:8080/`, register the account `midca` / `midca` with a blank email, and log out — the account is for the agent; you spectate without logging in.

Sanity check: `python src/dcss/agent/randomagent.py` should show the agent in the lobby within a second or two.

---

## 6. Phases

**Phase 1 — LLM view.** `src/dcss/agent/llm_view.py`: `observe(gs) -> dict` returns the state as structured data (`status`, `effects`, `map`, `messages`, `inventory`, `legend`, `suggested_actions`, `alive`); `render(obs) -> str` returns the prompt-ready text. Both pure, neither may raise. The map section shows the **whole explored floor**, not a local window — that is the structural advantage over the radius-3 RL observation. Settings agreed in advance: whole floor, both dict and string, last 10 turns of messages, monsters as map glyphs only for now. Tested offline in `test_llm_view.py` with no Docker or server.

Done when: all three cases — normal play, fresh `GameState`, and an item that was never equipped — render without raising, and `observe()` neither mutates the state nor varies between calls.

**Phase 2 — Menu selection.** Re-enable the commented-out `MenuChoice` branch in `autobahn_game_connection.py` (~line 313). Until then the agent cannot use inventory items or cast spells, so nothing beyond movement and attack is reachable. This file is shared with the RL path, so a regression here breaks those runs too — keep the change minimal and verify movement still works.

Done when: the agent can use an inventory item and the game returns to normal play rather than getting stuck in a menu.

**Phase 3 — prime-agent.** Install prime-agent and drive a loop: call `observe`/`render`, send the text to the model, translate the reply into a `Command`, and send it through the existing queue bridge. Reuse the threading pattern from `dcss_gym_env.py`. Test with a cheap model first.

Done when: the model plays several consecutive turns without hanging and can be spectated in the browser. Play quality does not matter yet — only that the loop runs.

**Phase 4 — Enrichment.** Once the loop runs, it becomes clear what the model actually lacks. Candidates: monster name/direction/distance extraction (deliberately deferred), token cost management on large maps, cross-turn memory, and comparison against the RL baselines.
