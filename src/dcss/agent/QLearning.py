import random
import numpy

from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig

from dcss.actions.command import Command


class QLearning(BaseAgent):

    def __init__(self):
        super().__init__()
        self.gamestate = None

    def get_action(self, gamestate: GameState):
        self.gamestate = gamestate

        # construct a small vector of time
        agent_x, agent_y = self.gamestate.agent_x, self.gamestate.agent_y
        cell_vector = self.gamestate.get_cell_map().get_radius_around_agent_vector(r=2, tile_vector_repr='simple')
        turns_passed = self.gamestate.get_player_stats_vector()[35]

        print("rl_state = {}, {}".format(agent_x, agent_y, cell_vector, turns_passed))

        # get all possible actions
        actions = [Command.MOVE_OR_ATTACK_SW,
                   Command.MOVE_OR_ATTACK_S,
                   Command.MOVE_OR_ATTACK_SE,
                   Command.MOVE_OR_ATTACK_W,
                   Command.MOVE_OR_ATTACK_E,
                   Command.MOVE_OR_ATTACK_NW,
                   Command.MOVE_OR_ATTACK_N,
                   Command.MOVE_OR_ATTACK_NE,
                   Command.REST_AND_LONG_WAIT,
                   Command.WAIT_1_TURN]

        # pick an action at random
        return random.choice(actions)


if __name__ == "__main__":
    my_config = WebserverConfig

    # set game mode to Tutorial #1
    my_config.game_id = 'sprint-web-trunk'
    my_config.delay = 0.5

    # create game
    game = WebSockGame(config=my_config, agent_class=QLearning)
    game.run()