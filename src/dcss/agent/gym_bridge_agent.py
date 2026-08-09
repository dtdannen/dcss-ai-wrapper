import queue

from dcss.actions.command import Command
from dcss.agent.base import BaseAgent
from dcss.state.cellmap import FIX_FRONTIER_OBSERVATION
from dcss.state.game import GameState


# Upper bound on filler actions emitted while waiting for a truncation-triggered
# restart to complete. A healthy restart needs ~1. At the ~62ms tick this is ~12s,
# after which the run fails loudly instead of hanging. PPO_6 emitted 11,182 of these
# over 12 minutes against a silent server before webtiles closed the connection.
MAX_RESTART_FILLER_ACTIONS = 200

# --- Ablation toggle --------------------------------------------------------
FIX_RESTART_WATCHDOG = True  # False = spin forever on a stalled restart (PPO_6 behaviour)
# ----------------------------------------------------------------------------


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
        # Both set by DCSSGymEnv when an episode hits MAX_EPISODE_STEPS. They live here,
        # on the shared tracker, for the same reason last_gamestate_id does: the wrapper
        # rebuilds the agent at every boundary, so flags on the agent instance would be
        # lost precisely when they are needed.
        #
        # Two flags, not one, because a single flag cannot do both jobs. Once the
        # connection sets _BEGIN_DELETING_GAME it stops calling get_action at all, so a
        # flag cleared inside get_action can never be cleared once the abandon starts -
        # requesting_start_new_game() then keeps returning True, re-arms
        # _BEGIN_DELETING_GAME on every message, and reset_before_next_game() keeps
        # clearing the _SENT_* progress flags, so the ctrl-Q handshake restarts from the
        # top forever instead of finishing. So:
        #   restart_requested - one-shot trigger, consumed by requesting_start_new_game()
        #   awaiting_new_game - suppresses publishing until a new GameState appears,
        #                       cleared by get_action, which is the only place that can
        #                       observe the swap
        self.restart_requested = False
        self.awaiting_new_game = False
        # Watchdog state for the restart wait. filler_actions_sent counts consecutive
        # WAIT_1_TURN fillers; fatal_reported makes the poison pill fire exactly once,
        # because observation_queue has maxsize=1 and a second blocking put() would
        # freeze the connection thread - re-creating the very hang we are detecting.
        self.filler_actions_sent = 0
        self.fatal_reported = False


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

    def requesting_start_new_game(self):
        # Polled by the connection via check_agent_wants_to_start_next_game() on every
        # message. Returning True makes it set _BEGIN_DELETING_GAME, run the ctrl-Q
        # abandon sequence, and call reset_before_next_game() - which is what turns an
        # env-side truncation into a genuinely fresh game rather than a resumed one.
        #
        # One-shot: consume the flag here rather than let get_action clear it. This is
        # the only path that still runs once _BEGIN_DELETING_GAME gates the agent out,
        # so clearing it anywhere else re-triggers the handshake on every subsequent
        # message and it never completes.
        if self.episode_tracker.restart_requested:
            self.episode_tracker.restart_requested = False
            return True
        return False

    def get_action(self, gamestate: GameState):
        if self.episode_tracker.awaiting_new_game:
            if id(gamestate) == self.episode_tracker.last_gamestate_id:
                # Still the game the env just truncated. Publishing a snapshot would
                # fill the single-slot queue with an observation nobody will consume,
                # and blocking on action_queue would freeze the connection's event
                # loop - which has to keep ticking to reach the abandon state machine.
                # A wait is the cheapest legal filler (returning None raises).
                self.episode_tracker.filler_actions_sent += 1
                if (FIX_RESTART_WATCHDOG
                        and self.episode_tracker.filler_actions_sent > MAX_RESTART_FILLER_ACTIONS
                        and not self.episode_tracker.fatal_reported):
                    self.episode_tracker.fatal_reported = True
                    # Hand the failure to the ENV's thread rather than raising here.
                    # Raising would only kill this coroutine on the connection thread;
                    # the env would stay blocked on observation_queue.get() forever,
                    # which is precisely the PPO_6 hang we are trying to make loud.
                    # Drain before putting. observation_queue has maxsize=1, so a
                    # blocking put() against an unconsumed snapshot would park THIS
                    # thread forever - freezing the connection inside the very watchdog
                    # meant to report the freeze. Discarding a stale snapshot is safe:
                    # we are aborting the run, and the env only ever needs the pill.
                    try:
                        self.observation_queue.get_nowait()
                    except queue.Empty:
                        pass
                    try:
                        self.observation_queue.put_nowait({'fatal': (
                            "Restart watchdog: {} consecutive filler actions without the "
                            "abandon sequence completing. The server has almost certainly "
                            "stopped responding - check the webtiles container."
                        ).format(self.episode_tracker.filler_actions_sent)})
                    except queue.Full:
                        # Lost a race with the env thread refilling the slot. The 120s
                        # queue timeout in the env is the backstop; never block here.
                        self.episode_tracker.fatal_reported = False
                return Command.WAIT_1_TURN
            # Different GameState object: the abandon sequence finished and a new game
            # is underway. Clear the suppression and fall through, so this becomes the
            # first snapshot of the next episode (episode_changed will be True).
            self.episode_tracker.awaiting_new_game = False
            self.episode_tracker.filler_actions_sent = 0

        snapshot = self._build_snapshot(gamestate)
        self.observation_queue.put(snapshot)

        command = self.action_queue.get()
        return command

    def _build_snapshot(self, gamestate: GameState):
        stats_vector = filter_numeric_vector(gamestate.get_player_stats_vector())
        grid_vector = [float(v) for v in gamestate.get_cell_map().get_radius_around_agent_vector(
            r=self.radius, tile_vector_repr='simple')]
        observation = stats_vector + grid_vector
        if FIX_FRONTIER_OBSERVATION:
            # Concatenation order and length must match DCSSGymEnv.__init__'s obs_len.
            observation = observation + [
                float(v) for v in gamestate.get_cell_map().get_frontier_features(r=self.radius)]

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
