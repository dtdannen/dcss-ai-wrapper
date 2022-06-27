from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig
from dcss.connection.local_game_connection import GameConnectionLocal

import random


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
    my_config = WebserverConfig

    # set game mode to Tutorial #1
    my_config.game_id = 'dcss-web-trunk'
    my_config.delay = 1.0

    # create game
    localgame= GameConnectionLocal()

    # TODO - this is a sketch
    while True:
        raw_game_msg = localgame.get_next_message()
        if raw_game_msg:
            gamestate.update(raw_game_msg)
            myagent.get_action(gamestate)

