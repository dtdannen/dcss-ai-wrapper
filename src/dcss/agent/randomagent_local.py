from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig, LocalConfig
from dcss.connection.local.socket_connection import WebtilesSocketConnection

import json
import time
import logging
import random
import os

from tornado.ioloop import IOLoop


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
    import zlib
    game_state = GameState()
    global game_updates_called
    game_updates_called = 0
    decomp = zlib.decompressobj(-zlib.MAX_WBITS)

    def _on_socket_message(msg):  # type: (str) -> None()
        print("received message: {}".format(msg))


        #print("Binary message received: {0} bytes".format(len(msg)))
        #msg += bytes([0, 0, 255, 255])
        #json_message = decomp.decompress(msg)
        #json_message_decoded = json_message.decode("utf-8")
        #print("   Decoding turns it into: {}".format(json_message_decoded))
        #message_as_str = json_message_decoded

        #message_as_json = {}
        message_as_str = msg
        message_as_json = msg
        try:
            message_as_json = json.loads(message_as_str)
        except:
            print(
                "Failure to parse message_as_json\n****** you may have spectated too soon, best thing to do is just to restart the agent ******")
            time.sleep(20)

        game_state.update(message_as_json)

    my_config = LocalConfig

    logger = logging.getLogger(__name__)



    socket_conn = WebtilesSocketConnection(my_config.crawl_socketpath, logger)
    socket_conn.message_callback = _on_socket_message
    socket_conn.connect()

    random_agent = MyAgent()

    # temporary commands to start a game
    game_start_commands = [{"keycode": ord('c'), "msg": "key"}, {"keycode": ord('i') , "msg": "key"},{"keycode": ord('b') , "msg": "key"}]

    print("Setting up game...")
    time.sleep(1)

    IOLoop.current().start()
    print("we started the IOLoop")

    while True:
        print("game_updates_called = {}".format(game_updates_called))
        if len(game_start_commands) > 0:
            next_action = game_start_commands.pop()
            print("about to send: {}".format(next_action))
            socket_conn.send_message(json.dumps(next_action))
        else:
            next_action = random_agent.get_action(game_state)
            socket_conn.send_message(json.dumps(Action.get_execution_repr(next_action)))

        time.sleep(1)


