"""

Demo of an RL agent on the sonja sprint in crawl 23.1

Make sure to run crawl before running this demo, see:
    start_crawl_terminal_sprint.sh

"""

from dcss.connection.autobahn_game_connection import DCSSProtocol
from dcss.connection import config
import asyncio
from autobahn.asyncio.websocket import WebSocketClientFactory

import logging
logger = logging.getLogger("dcss-ai-wrapper")


def main():
    factory = WebSocketClientFactory(config.WebserverConfig.server_uri)
    factory.protocol = DCSSProtocol
    #channel_id = DCSSProtocol.get_channel_id()

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, config.WebserverConfig.server_ip, config.WebserverConfig.server_port)
    client = loop.run_until_complete(coro)
    #client[1].load_ai_agent()
    loop.run_forever()


if __name__ == "__main__":
    main()
