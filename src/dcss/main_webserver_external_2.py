"""

Demo of an RL agent on the sonja sprint in crawl 23.1

Make sure to run crawl before running this demo, see:
    start_crawl_terminal_sprint.sh

"""

from dcss.connection.autobahn_game_connection import DCSSProtocol
from dcss.connection import config
import asyncio
from concurrent.futures import ProcessPoolExecutor
from autobahn.asyncio.websocket import WebSocketClientFactory
import datetime

import logging
logger = logging.getLogger("dcss-ai-wrapper")


def main():
    executor = ProcessPoolExecutor(2)
    factory = WebSocketClientFactory(config.WebserverConfig.server_uri)
    factory.protocol = DCSSProtocol
    #channel_id = DCSSProtocol.get_channel_id()

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, config.WebserverConfig.server_ip, config.WebserverConfig.server_port)
    client = loop.run_until_complete(coro)
    client[1].load_ai_agent_from_config()
    gameconnection = asyncio.create_task(loop.run_in_executor(executor, ))
    loop.run_forever()


def display_date(end_time, loop):
    print(datetime.datetime.now())
    if (loop.time() + 1.0) < end_time:
        loop.call_later(1, display_date, end_time, loop)
    else:
        loop.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Schedule the first call to display_date()
    end_time = loop.time() + 100.0
    loop.call_soon(display_date, end_time, loop)

    main()
