from dcss.agent.base import BaseAgent
from dcss.state.game import GameState


def filter_numeric_vector(values):
    """
    Drops non-numeric entries (e.g. player_god/player_place, which are raw
    strings) and coerces None to 0.0, so the result is safe to feed into an RL
    observation. Used by both GymBridgeAgent (to build the vector) and
    DCSSGymEnv (to compute the matching observation_space shape), so the two
    can never drift apart.
    """
    result = []
    for v in values:
        if isinstance(v, str):
            continue
        result.append(0.0 if v is None else float(v))
    return result


class EpisodeBoundaryTracker:
    """
    Tracks the identity of the last-seen GameState object, held externally to
    GymBridgeAgent so it survives the agent being reconstructed.

    reset_before_next_game() (wrapper code) reassigns self.agent = self.agent_class()
    on every episode boundary. If _last_gamestate_id lived on the agent instance
    itself, a fresh instance would start back at None and silently fail to detect
    the very episode change that just happened. A single tracker, constructed once
    by DCSSGymEnv and shared across every GymBridgeAgent instance the wrapper ever
    creates, keeps this state correct regardless of how many times the agent gets
    rebuilt.
    """

    def __init__(self):
        self.last_gamestate_id = None


class GymBridgeAgent(BaseAgent):
    """
    Bridges the wrapper's synchronous get_action() callback (invoked from inside
    DCSSProtocol's async event loop, on a background thread) to a Gym-style
    reset()/step() interface running on a different thread (see DCSSGymEnv).

    Each get_action() call:
      1. Packages the *result* of the previously-returned action into a snapshot
         and hands it to the env via observation_queue.
      2. Blocks on action_queue until the env supplies the next action.

    Episode boundaries (death / any game_ended) are detected purely by comparing
    the identity of the `gamestate` object between calls: reset_before_next_game()
    (in autobahn_game_connection.py) replaces self.game_state with a brand new
    GameState() instance, while every other tick mutates the same instance in
    place. No changes to the wrapper are needed for this to work. The last-seen
    id is kept in an EpisodeBoundaryTracker (shared, external) rather than on
    self, so it survives self.agent being reconstructed by the wrapper.
    """

    def __init__(self, action_queue, observation_queue, radius, episode_tracker):
        super().__init__()
        self.action_queue = action_queue
        self.observation_queue = observation_queue
        self.radius = radius
        self.episode_tracker = episode_tracker

    def get_action(self, gamestate: GameState):
        snapshot = self._build_snapshot(gamestate)
        self.observation_queue.put(snapshot)

        command = self.action_queue.get()
        return command

    def _build_snapshot(self, gamestate: GameState):
        stats_vector = filter_numeric_vector(gamestate.get_player_stats_vector())
        grid_vector = [float(v) for v in gamestate.get_cell_map().get_radius_around_agent_vector(
            r=self.radius, tile_vector_repr='simple')]
        observation = stats_vector + grid_vector

        cellmap = gamestate.get_cell_map()
        cells_seen = len(
            cellmap.place_depth_to_x_y_to_cells
            .get(cellmap.current_place, {})
            .get(cellmap.current_depth, {})
        )

        episode_changed = (
            self.episode_tracker.last_gamestate_id is not None
            and id(gamestate) != self.episode_tracker.last_gamestate_id
        )
        self.episode_tracker.last_gamestate_id = id(gamestate)

        return {
            'observation': observation,
            'episode_changed': episode_changed,
            'cells_seen': cells_seen,
            'depth': gamestate.player_depth,
            'turn': gamestate.get_current_game_turn(),
        }
