"""

Demo of an RL agent on the sonja sprint in crawl 23.1

Make sure to run crawl before running this demo, see:
    start_crawl_terminal_sprint.sh

"""

from dcss.connection.autobahn_game_connection import DCSSProtocol
from dcss.connection import config
import asyncio
import logging
import random
import threading
from autobahn.asyncio.websocket import WebSocketClientFactory
from dcss.actions.command import Command
from dcss.actions.action import Action
from dcss.state.game import GameState
import time

logging.basicConfig(level=logging.WARNING)


class WebSockGame:

    def __init__(self):
        self.has_started = False
        self.client = None

    def send_action(self, command : Command):
        print("self.client is {}".format(self.client))
        print("dir(self.client) is {}".format(dir(self.client)))
        self.client.next_action_direct = command
        self.client.has_next_action_direct = True

    def get_game_state(self):
        return self.client.game_state

    def start(self):
        factory = WebSocketClientFactory(config.WebserverConfig.server_uri)
        factory.protocol = DCSSProtocol
        #channel_id = DCSSProtocol.get_channel_id()

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, config.WebserverConfig.server_ip, config.WebserverConfig.server_port)
        self.client = loop.run_until_complete(coro)
        self.has_started = True
        loop.run_forever()


if __name__ == "__main__":
    commands = Action.get_all_move_commands()
    game1 = WebSockGame()

    while game1.has_started:
        gamestate = game1.get_game_state()  # type: GameState
        print("Agent now at location {}".format(gamestate.get_player_xy()))
        next_action = random.choice(commands)
        game1.send_action(next_action)
        print("Sent action {}".format(next_action))
        time.sleep(0.1)
