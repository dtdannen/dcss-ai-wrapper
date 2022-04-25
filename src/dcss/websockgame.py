import dcss
from dcss.connection.autobahn_game_connection import DCSSProtocol
from dcss.connection import config
import asyncio
from autobahn.asyncio.websocket import WebSocketClientFactory
from dcss.connection.config import WebserverConfig

import os
import socket
import errno

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

    def _setup_local(self):
        print("Looking for socket: {}".format(self.config.crawl_socketpath))
        if os.path.exists(self.config.crawl_socketpath):
            print("  Found!")
        else:
            raise Exception("Could not find socketpatch: {}".format(self.config.crawl_socketpath))

        crawl_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        try:  # Unlink if necessary
            os.unlink(self.config.socketpath)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

        # crawl_socket.settimeout(10)
        #
        # crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #
        # if crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < 2048:
        #     crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        #
        # if crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < 212992:
        #     crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)

        #with warnings.catch_warnings():
        #    warnings.simplefilter("ignore")

        crawl_socket.bind(self.config.socketpath)

        print("Successfully bound socket to: {}".format(self.config.socketpath))

        factory = WebSocketClientFactory(url=None)
        factory.protocol = DCSSProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, self.config.server_ip, self.config.server_port)
        _, self.client = loop.run_until_complete(coro)

    def run(self, local=False):
        if local:
            self._setup_local()
        else:
            self._setup()
        self._load_ai()
        self._load_config()

        loop = asyncio.get_event_loop()
        loop.run_forever()
