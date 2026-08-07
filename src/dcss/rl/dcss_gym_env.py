import asyncio
import functools
import queue
import threading

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from dcss.actions.action import Action
from dcss.agent.gym_bridge_agent import EpisodeBoundaryTracker, GymBridgeAgent, filter_numeric_vector
from dcss.connection.config import WebserverConfig
from dcss.state.game import GameState
from dcss.websockgame import WebSockGame


# --- Reward weights (stage 1: "explore floor 1" only) ---
# Tune these by trial and error. Keep them here, at the top, so they're easy to find.
NEW_CELL_REWARD = 0.1     # reward for each newly-seen cell on the current depth
DEATH_PENALTY = -100.0    # reward on the step that ends the episode (death)
STEP_PENALTY = -0.01      # tiny constant penalty per step, to discourage stalling

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
        self.config.game_id = 'dcss-web-trunk'
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
        self.observation_space = spaces.Box(low=-1e6, high=1e6, shape=(obs_len,), dtype=np.float32)

        self._action_queue = None
        self._observation_queue = None
        self._episode_tracker = None
        self._thread = None
        self._prev_cells_seen = None
        self._pending_reset_snapshot = None

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

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        if self._thread is None:
            self._start_connection()

        if self._pending_reset_snapshot is not None:
            snapshot = self._pending_reset_snapshot
            self._pending_reset_snapshot = None
        else:
            snapshot = self._observation_queue.get()

        self._prev_cells_seen = snapshot['cells_seen']

        observation = np.array(snapshot['observation'], dtype=np.float32)
        info = {'depth': snapshot['depth'], 'turn': snapshot['turn']}
        return observation, info

    def step(self, action):
        command = self.action_list[action]
        self._action_queue.put(command)

        snapshot = self._observation_queue.get()
        observation = np.array(snapshot['observation'], dtype=np.float32)
        info = {'depth': snapshot['depth'], 'turn': snapshot['turn']}

        if snapshot['episode_changed']:
            # This snapshot is already the first observation of the next episode
            # (the wrapper auto-restarts on its own). Cache it so a subsequent
            # reset() call doesn't block waiting for a new one.
            reward = DEATH_PENALTY
            terminated = True
            self._pending_reset_snapshot = snapshot
            self._prev_cells_seen = snapshot['cells_seen']
        else:
            new_cells = max(0, snapshot['cells_seen'] - self._prev_cells_seen)
            reward = STEP_PENALTY + NEW_CELL_REWARD * new_cells
            terminated = False
            self._prev_cells_seen = snapshot['cells_seen']

        truncated = False
        return observation, reward, terminated, truncated, info

    def close(self):
        # The background thread is a daemon thread running WebSockGame.run(), which
        # calls loop.run_forever() with no exposed shutdown hook, so there's nothing
        # clean to call here yet. The thread dies when the process exits.
        pass
