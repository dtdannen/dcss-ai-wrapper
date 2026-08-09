import asyncio
import functools
import queue
import threading

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from dcss.actions.action import Action
from dcss.actions.command import Command
from dcss.agent.gym_bridge_agent import EpisodeBoundaryTracker, GymBridgeAgent, filter_numeric_vector
from dcss.connection.config import WebserverConfig
from dcss.state.cellmap import FIX_FRONTIER_OBSERVATION, CellMap
from dcss.state.game import GameState
from dcss.websockgame import WebSockGame


# --- Reward weights (stage 1: "explore floor 1" only) ---
# Tuned from the PPO_2 100k run, which stalled: ep_len_mean went 6.4k -> 12.1k while
# derived cells-explored only moved 680 -> 810 (~44 steps per additional cell at the
# margin). At the old weights all three terms were the same order of magnitude per
# step - exploration income 0.1/9.4 = +0.011, step cost -0.01, death hazard
# (1/6400)*100 = -0.016 - so they cancelled out and nothing pointed at exploring.
# These satisfy both break-evens with margin, where k = steps per new cell and
# p = per-step chance of dying while exploring (~1.6e-4 observed):
#   viability:  NEW_CELL_REWARD > k * abs(STEP_PENALTY)        -> 6.7x at k=15
#   risk:       NEW_CELL_REWARD / k > p * abs(DEATH_PENALTY)   -> 42x at k=15
NEW_CELL_REWARD = 1.0     # reward for each newly-seen cell on the current depth
DEATH_PENALTY = -10.0     # reward on the step that ends the episode (death)
STEP_PENALTY = -0.01      # tiny constant penalty per step, to discourage stalling

# Death is the only natural terminal, so episodes are otherwise unbounded - one game
# ate 12k+ steps of the PPO_2 budget, leaving ~8 episodes in 100k. Cap them for ~50.
MAX_EPISODE_STEPS = 2000

# --- Ablation toggles -------------------------------------------------------
# Each fix below is switchable so its individual contribution can be measured later
# without editing logic. False restores the exact pre-fix behaviour.
FIX_TERMINAL_OBSERVATION = True  # return the dying episode's last obs, not the next
                                 # episode's first; and charge STEP_PENALTY on death
FIX_QUEUE_TIMEOUT = True         # bound the blocking queue waits instead of hanging

# Fixed-seed play. False = 'dcss-web-trunk', a fresh random map every episode.
# True  = 'seeded-web-trunk', the SAME map every episode, which removes the
# run-to-run map variance that made PPO_4/5/6 unreadable (two runs with an identical
# reward function differed ~80% at the same step).
#
# Verified working end to end: the 4-step seed menu handshake in
# autobahn_game_connection.py:154-185 completes once per episode and survives the
# ctrl-Q abandon cycle, and three episodes replaying one fixed action sequence
# produced byte-identical (cells_seen, observation) at all 40 steps - so the seed
# pins the whole RNG stream, not just map generation.
#
# Left False for the stack-survival run: one fixed map narrows what a clean 200k
# proves, and lets the policy memorise a layout instead of learning to explore. Turn
# it on for ABLATIONS, where killing map variance is worth more than generality.
# Costs when True: reset ~10-11s instead of ~5s (dungeon pregeneration), and with
# FIXED_SEED below the spawn room reveals 141 cells at once, so a random walk finds
# nothing new for its first ~100 steps.
USE_FIXED_SEED = True
FIXED_SEED = 4675233756386659716
# ----------------------------------------------------------------------------

# Ceiling on a single blocking wait for the bridge. A truncation restart (ctrl-Q
# handshake plus character creation) measured ~5s; PPO's own update pauses do not
# count because the env is the side doing the waiting. Anything past this means the
# connection is gone, and an unattended run should die loudly rather than at dawn.
QUEUE_TIMEOUT_SECONDS = 120

# Deliberately NOT included yet (future stages):
#   - reward for descending stairs (depth reward)
#   - reward/penalty for fighting or killing monsters


class DCSSGymEnv(gym.Env):
    """
    Gymnasium-compatible environment wrapping the DCSS webtiles connection.

    Runs the existing async WebSockGame/DCSSProtocol connection on a background
    thread, driven by a GymBridgeAgent, and exposes it as a synchronous
    reset()/step() interface via two single-slot queues.

    Observation: concatenation of
      - GameState.get_player_stats_vector()                              (fixed length)
      - CellMap.get_radius_around_agent_vector(r, 'simple')              (length (2r+1)^2)

    Action space: the 8 movement/attack directions from Action.get_all_move_commands().

    Episode end: detected when the bridge agent observes that `gamestate`'s object
    identity changed between calls, which only happens via reset_before_next_game()
    in the wrapper (i.e. after death or any other game_ended). Since the action space
    here is movement-only (no TRAVEL_STAIRCASE_DOWN), the only way an episode can end
    during stage 1 is death/game-over, so every such boundary is scored as the death
    penalty.
    """

    metadata = {"render_modes": []}

    def __init__(self, radius=3, config=None, action_delay=0.05):
        super().__init__()
        self.radius = radius

        self.config = config or WebserverConfig
        self.config.game_id = 'seeded-web-trunk' if USE_FIXED_SEED else 'dcss-web-trunk'
        if USE_FIXED_SEED:
            self.config.seed = FIXED_SEED
        self.config.draw_map = False
        self.config.delay = action_delay

        self.action_list = Action.get_all_move_commands()
        self.action_space = spaces.Discrete(len(self.action_list))

        # A freshly-constructed GameState() has player_god=None and player_place=""
        # (not yet real strings), so filter_numeric_vector wouldn't drop player_god
        # here the way it will once a live game populates it with e.g. "Trog" -
        # force both into their live (string) type before measuring, so this length
        # matches what GymBridgeAgent actually produces during play.
        length_probe = GameState()
        length_probe.player_god = "placeholder"
        length_probe.player_place = "placeholder"
        stats_len = len(filter_numeric_vector(length_probe.get_player_stats_vector()))
        grid_len = (2 * radius + 1) ** 2
        obs_len = stats_len + grid_len
        if FIX_FRONTIER_OBSERVATION:
            # Must stay in lockstep with _build_snapshot's concatenation.
            obs_len += CellMap.FRONTIER_FEATURE_LEN
        self.observation_space = spaces.Box(low=-1e6, high=1e6, shape=(obs_len,), dtype=np.float32)

        self._action_queue = None
        self._observation_queue = None
        self._fatal = None
        self._last_observation = None
        self._episode_tracker = None
        self._thread = None
        self._prev_cells_seen = None
        self._pending_reset_snapshot = None
        self._step_count = 0

    def _start_connection(self):
        self._action_queue = queue.Queue(maxsize=1)
        self._observation_queue = queue.Queue(maxsize=1)
        self._episode_tracker = EpisodeBoundaryTracker()

        agent_factory = functools.partial(
            GymBridgeAgent, self._action_queue, self._observation_queue, self.radius, self._episode_tracker
        )

        def run():
            # WebSockGame/autobahn expects an event loop to already be set for this
            # thread (it calls asyncio.get_event_loop() internally); a freshly-spawned
            # thread has none by default, so create and install one before game.run().
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            game = WebSockGame(agent_class=agent_factory, config=self.config)
            game.run()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def _check_fatal(self, snapshot):
        """
        The bridge agent runs on the connection thread, where an exception would only
        kill that coroutine and leave this thread blocked on observation_queue.get()
        forever. So it posts a poison pill instead and we raise it here, on the thread
        SB3 is actually driving, which propagates into train_ppo's handler and ends the
        process loudly. Returns the snapshot unchanged when it is a normal one.
        """
        if isinstance(snapshot, dict) and 'fatal' in snapshot:
            raise RuntimeError(snapshot['fatal'])
        return snapshot

    def _await_snapshot(self):
        """
        Blocking wait for the bridge, bounded so a dead connection fails loudly.
        queue.Empty carries no useful message, so it is translated into something a
        3am log reader can act on.
        """
        if not FIX_QUEUE_TIMEOUT:
            return self._check_fatal(self._observation_queue.get())
        try:
            snapshot = self._observation_queue.get(timeout=QUEUE_TIMEOUT_SECONDS)
        except queue.Empty:
            raise RuntimeError(
                "No observation from the DCSS bridge in {}s. The connection is "
                "almost certainly dead - check the webtiles container and whether "
                "the game is stuck at a prompt.".format(QUEUE_TIMEOUT_SECONDS))
        return self._check_fatal(snapshot)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        if self._thread is None:
            self._start_connection()

        if self._pending_reset_snapshot is not None:
            # This path bypasses _await_snapshot, so check the pill explicitly. The
            # cached snapshot should never be one - it came through _await_snapshot
            # originally - but if that invariant ever breaks, snapshot['observation']
            # below would raise a bare KeyError instead of the labelled RuntimeError,
            # turning a diagnosable failure into a confusing one at 3am.
            snapshot = self._check_fatal(self._pending_reset_snapshot)
            self._pending_reset_snapshot = None
        else:
            snapshot = self._await_snapshot()

        self._prev_cells_seen = snapshot['cells_seen']
        self._step_count = 0

        observation = np.array(snapshot['observation'], dtype=np.float32)
        self._last_observation = observation
        info = {'depth': snapshot['depth'], 'turn': snapshot['turn']}
        return observation, info

    def step(self, action):
        command = self.action_list[action]
        self._action_queue.put(command)

        snapshot = self._await_snapshot()
        observation = np.array(snapshot['observation'], dtype=np.float32)
        info = {'depth': snapshot['depth'], 'turn': snapshot['turn']}

        self._step_count += 1
        truncated = False

        if snapshot['episode_changed']:
            # This snapshot is already the first observation of the next episode
            # (the wrapper auto-restarts on its own). Cache it so a subsequent
            # reset() call doesn't block waiting for a new one.
            reward = DEATH_PENALTY
            terminated = True
            self._pending_reset_snapshot = snapshot
            self._prev_cells_seen = snapshot['cells_seen']
            if FIX_TERMINAL_OBSERVATION:
                # Hand back the dying episode's last observation instead of the next
                # episode's first. SB3 does not bootstrap through a terminated step, so
                # this is hygiene rather than a learning change - but it stops
                # info['terminal_observation'] being another episode's state, which any
                # future algorithm change would silently consume.
                # The dying game's final cells stay unrecoverable: the bridge never
                # publishes a snapshot for the death step, so its cells_seen is gone.
                if self._last_observation is not None:
                    observation = self._last_observation
                # Death still costs a step. Omitting STEP_PENALTY made dying marginally
                # cheaper than living, in the direction we least want to subsidise.
                reward = DEATH_PENALTY + STEP_PENALTY
        else:
            new_cells = max(0, snapshot['cells_seen'] - self._prev_cells_seen)
            reward = STEP_PENALTY + NEW_CELL_REWARD * new_cells
            terminated = False
            self._prev_cells_seen = snapshot['cells_seen']

            if self._step_count >= MAX_EPISODE_STEPS:
                # Time limit, not a real terminal: no DEATH_PENALTY, and SB3
                # bootstraps the value estimate through the boundary.
                truncated = True
                # Ask the connection to abandon this character and deal a fresh one.
                # Without this the next episode resumes the same partly-explored
                # floor, where cells_seen barely moves and there is almost no
                # exploration reward left to earn. The flag lives on the shared
                # tracker because the wrapper rebuilds the agent at every game
                # boundary. Deliberately NOT setting _pending_reset_snapshot: the
                # next snapshot to arrive is the new game's first one, which is
                # exactly what reset() should block for.
                # restart_requested is the one-shot trigger the connection consumes;
                # awaiting_new_game keeps the agent from publishing until the swap
                # actually happens. See EpisodeBoundaryTracker for why it takes two.
                self._episode_tracker.restart_requested = True
                self._episode_tracker.awaiting_new_game = True
                # The agent published the snapshot we just consumed and is already
                # parked inside get_action() on action_queue.get(), so it cannot see
                # the flag it set above - the restart guard only runs at the top of
                # get_action(), and it will never get there without an action. Hand it
                # one throwaway wait: this call returns, and the *next* one hits the
                # guard and stops publishing, which lets the connection's event loop
                # keep ticking until it reaches the abandon state machine. Without
                # this the env waits for an observation while the agent waits for an
                # action, and reset() deadlocks.
                self._action_queue.put(Command.WAIT_1_TURN)

        # Remember the live observation, not a substituted one, so the next death
        # returns the genuine last state of the episode that is ending.
        if not (terminated and FIX_TERMINAL_OBSERVATION):
            self._last_observation = observation

        return observation, reward, terminated, truncated, info

    def close(self):
        # The background thread is a daemon thread running WebSockGame.run(), which
        # calls loop.run_forever() with no exposed shutdown hook, so there's nothing
        # clean to call here yet. The thread dies when the process exits.
        pass
