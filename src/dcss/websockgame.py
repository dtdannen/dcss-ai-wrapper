import dcss
from dcss.connection.autobahn_game_connection import DCSSProtocol
from dcss.connection import config
import asyncio
from autobahn.asyncio.websocket import WebSocketClientFactory
from dcss.connection.config import WebserverConfig


class WebSockGame:

    def __init__(self, agent_class, config=WebserverConfig):
        self.client = None
        self.agent_class = agent_class
        self.config = config

    def _load_ai(self):
        if not self.client:  # the type of self.client should be dcss.connection.autobahn_game_connection.DCSSProtocol
            raise Exception("Client is NONE in WebSockGame")
        self.client.set_ai_class(self.agent_class)
        self.client.load_ai_class()

    def _load_config(self):
        if not self.client:  # the type of self.client should be dcss.connection.autobahn_game_connection.DCSSProtocol
            raise Exception("Client is NONE in WebSockGame")
        self.client.config = self.config

    def _setup(self):
        factory = WebSocketClientFactory(self.config.server_uri)
        factory.protocol = DCSSProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, config.WebserverConfig.server_ip, config.WebserverConfig.server_port)
        _, self.client = loop.run_until_complete(coro)

    def run(self):
        self._setup()
        self._load_ai()
        self._load_config()

        loop = asyncio.get_event_loop()
        loop.run_forever()
