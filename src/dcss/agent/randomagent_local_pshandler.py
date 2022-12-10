from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig, LocalConfig
from dcss.connection.local.socket_connection import WebtilesSocketConnection
from dcss.connection.local.process_handler import CrawlProcessHandler

import json
import time
from loguru import logger
import random
import os

from tornado.ioloop import IOLoop
from tornado.escape import utf8
from tornado.escape import json_decode
from tornado.escape import json_encode


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

    process_handler = CrawlProcessHandler(None)

    # TODO left off here

    # TODO - OLD code below


    import zlib
    game_state = GameState()
    global game_updates_called
    game_updates_called = 0
    decomp = zlib.decompressobj(-zlib.MAX_WBITS)

    global need_empty_flush
    need_empty_flush = False

    global message_queue
    message_queue = []

    global deflate
    deflate = True
    _compressobj = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                         zlib.DEFLATED,
                                         -zlib.MAX_WBITS)

    global socket_conn

    def _on_socket_message(msg):  # type: (str) -> None()
        print("received message: {}".format(msg))


        #print("Binary message received: {0} bytes".format(len(msg)))
        #msg += bytes([0, 0, 255, 255])
        #json_message = decomp.decompress(msg)
        #json_message_decoded = json_message.decode("utf-8")
        #print("   Decoding turns it into: {}".format(json_message_decoded))
        #message_as_str = json_message_decoded

        global socket_conn

        if msg.startswith("*"):
            # Special message to the server
            msg = msg[1:]
            msgobj = json_decode(msg)
            if msgobj["msg"] == "flush_messages":
                return

        #message_as_json = {}
        message_as_str = msg
        message_as_json = msg
        #try:
        message_as_json = json.loads(message_as_str)
        #except:
        #    print(
        #        "Failure to parse message_as_json\n****** you may have spectated too soon, best thing to do is just to restart the agent ******")
        #    time.sleep(20)

        game_state.update(message_as_json)

    # def get_empty_flush_message():
    #     msg = ("{\"msgs\":["
    #            + ",".join([])
    #            + "]}")
    #
    #     try:
    #         binmsg = utf8(msg)
    #         if deflate:
    #             # Compress like in deflate-frame extension:
    #             # Apply deflate, flush, then remove the 00 00 FF FF
    #             # at the end
    #             compressed = _compressobj.compress(binmsg)
    #             compressed += _compressobj.flush(zlib.Z_SYNC_FLUSH)
    #             compressed = compressed[:-4]
    #             f = write_message(compressed, binary=True)
    #
    # def flush_message_simple(socket_conn):
    #     # type: () -> bool
    #
    #     global message_queue
    #
    #     if len(message_queue) == 0:
    #         return False
    #
    #     msg = ("{\"msgs\":["
    #             + ",".join([])
    #             + "]}")
    #
    #     try:
    #         binmsg = utf8(msg)
    #         if deflate:
    #             # Compress like in deflate-frame extension:
    #             # Apply deflate, flush, then remove the 00 00 FF FF
    #             # at the end
    #             compressed = _compressobj.compress(binmsg)
    #             compressed += _compressobj.flush(zlib.Z_SYNC_FLUSH)
    #             compressed = compressed[:-4]
    #             f = write_message(compressed, binary=True)
    #         else:
    #             self.uncompressed_bytes_sent += len(binmsg)
    #             f = self.write_message(binmsg)
    #
    #         import traceback
    #         cur_stack = traceback.format_stack()
    #
    #         # handle any exceptions lingering in the Future
    #         # TODO: this whole call chain should be converted to use coroutines
    #         def after_write_callback(f):
    #             try:
    #                 f.result()
    #             except tornado.websocket.StreamClosedError as e:
    #                 # not supposed to be raised here in current versions of
    #                 # tornado, but in some older versions it is.
    #                 if self.failed_messages == 0:
    #                     self.logger.warning("Connection closed during async write_message")
    #                 self.failed_messages += 1
    #                 if self.ws_connection is not None:
    #                     self.ws_connection._abort()
    #             except tornado.websocket.WebSocketClosedError as e:
    #                 if self.failed_messages == 0:
    #                     self.logger.warning("Connection closed during async write_message")
    #                 self.failed_messages += 1
    #                 if self.ws_connection is not None:
    #                     self.ws_connection._abort()
    #             except Exception as e:
    #                 self.logger.warning("Exception during async write_message, stack at call:")
    #                 self.logger.warning("".join(cur_stack))
    #                 self.logger.warning(e, exc_info=True)
    #                 self.failed_messages += 1
    #                 if self.ws_connection is not None:
    #                     self.ws_connection._abort()
    #
    #         # extreme back-compat try-except block, `f` should be None in
    #         # ancient tornado versions
    #         try:
    #             f.add_done_callback(after_write_callback)
    #         except:
    #             pass
    #         # true means that something was queued up to send, but it may be
    #         # async
    #         return True
    #     except:
    #         self.logger.warning("Exception trying to send message.", exc_info = True)
    #         self.failed_messages += 1
    #         if self.ws_connection is not None:
    #             self.ws_connection._abort()
    #         return False


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
            time.sleep(1)
        else:
            next_action = random_agent.get_action(game_state)
            socket_conn.send_message(json.dumps(Action.get_execution_repr(next_action)))
            time.sleep(1)



