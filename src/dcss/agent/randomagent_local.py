from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig, LocalConfig

import random
import os


class MyAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.gamestate = None

    def get_action(self, gamestate: GameState):
        self.gamestate = gamestate
        # get all possible actions
        actions = Action.get_all_move_commands()
        # pick an action at random
        return random.choice(actions)


if __name__ == "__main__":
    my_config = LocalConfig

    # wrap unix socket in a webserver socket
    my_config.construct_server_uri()

    # create game
    game = WebSockGame(config=my_config, agent_class=MyAgent)
    game.run(local=True)
