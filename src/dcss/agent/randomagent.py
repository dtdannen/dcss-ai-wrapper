from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig

import random

import logging

import time



class MyAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.gamestate = None
        self.start_time = time.time()
        self.num_actions_sent = 0

    def get_action(self, gamestate: GameState):
        self.gamestate = gamestate
        # get all possible actions
        actions = Action.get_all_move_commands()
        # pick an action at random
        self.num_actions_sent +=1
        print("Actions per second = {}".format(self.num_actions_sent / (time.time() - self.start_time)))
        return random.choice(actions)


if __name__ == "__main__":
    my_config = WebserverConfig

    # set game mode to Tutorial #1
    my_config.game_id = 'dcss-web-trunk'
    my_config.delay = 0.005
    my_config.draw_map = False

    # set the logging level you want
    logger = logging.getLogger('dcss-ai-wrapper')
    logger.setLevel(logging.WARNING)

    # create game
    game = WebSockGame(config=my_config, agent_class=MyAgent)
    game.run()

