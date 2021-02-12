from gamestate import GameState
from actions import Action

import socket
import json
from datetime import datetime, timedelta
import warnings
import os
import random
import logging
import time
import sys
import config
import asyncio
import websockets
import zlib



class GameConnection:

    def __init__(self, config=config.DefaultConfig()):
        self.config = config
        self.crawl_socket = None
        self.game_state = GameState()
        self.msg_buffer = None
        self.recent_msg_data_raw = None
        self.recent_msg_data_decoded = None

        self.num_times_to_try_pressing_enter_read_msg = 5
        self.num_times_pressed_enter_read_msg = 0

        self.websocket = None
        self.decomp = zlib.decompressobj(-zlib.MAX_WBITS)

    @staticmethod
    def json_encode(value):
        return json.dumps(value).replace("</", "<\\/")

    async def login_webserver(self):
        assert isinstance(self.config, config.WebserverConfig)

        # connect
        logging.debug("Connecting to URI " + str(self.config.server_uri) + " ...")
        # print("AWAITING ON WEBSOCKET_3 CONNECT")
        self.websocket = await websockets.connect(self.config.server_uri)
        # print("POST-AWAITING ON WEBSOCKET_3 CONNECT")
        logging.info("Connected to webserver:" + str(self.websocket and self.websocket.open))

        # login
        logging.debug("Sending login message...")
        login_msg = {'msg': 'login',
                     'username': self.config.agent_name,
                     'password': self.config.agent_password}
        await self.send_and_receive(login_msg)

        # break apart msg from server
        # msgs = []
        # if 'msgs' in msg_from_server.keys():
        #    msgs = msg_from_server['msgs']

        logging.debug("Sending pong")

        # send pong
        # for msg_i in msgs:
        #    if msg_i['msg'] == 'ping':
        #        logging.debug("Received message ping from server, about to send pong")
        await self.websocket.send(json.dumps({'msg': 'pong'}))

    async def load_game_on_webserver(self):
        assert isinstance(self.config, config.WebserverConfig)

        play_game_msg = {'msg': 'play', 'game_id': self.config.game_id}
        await self.send_and_receive(play_game_msg)

    async def get_all_server_messages(self):
        i = 0
        SERVER_READY_FOR_INPUT = False
        request_pong = False
        while not SERVER_READY_FOR_INPUT:
            try:
                future = self.websocket.recv()
                # print("** AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))
                data_recv = await asyncio.wait_for(future, timeout=0.5)

                # print("** POST-AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))

                data_recv += bytes([0, 0, 255, 255])
                json_message = self.decomp.decompress(data_recv)
                #print("Just received json_message:\n{}".format(json_message))
                json_message = json_message.decode("utf-8")

                msg_from_server = json.loads(json_message)
                self._handle_msgs(msg_from_server)

                # if 'msgs' in msg_from_server:
                #     for msg in msg_from_server['msgs']:
                #         if 'msg' in msg:
                #             if msg['msg'] == "ping":
                #                 request_pong = True
                #
                # # json_messages_from_server_file.write(pprint.pformat(msg_from_server,indent=2)+'\n')
                # # json_messages_from_server_file.flush()
                #
                # logging.debug("i=" + str(i) + "Received Message:\n" + str(msg_from_server))
                #
                # if self.ai:
                #     self.ai.add_server_message(msg_from_server)
                #
                # # {'msgs': [{'mode': 1, 'msg': 'input_mode'}]}
                # # if 'msgs' in msg_from_server.keys():
                # #     for msg in msg_from_server['msgs']:
                # #         if 'msg' in msg.keys() and 'mode' in msg.keys():
                # #             if msg['msg'] == 'input_mode' and msg['mode'] == 1:
                # #                 SERVER_READY_FOR_INPUT = True
                # #                 print("Server is now ready for input!")

            except ValueError as e:
                logging.warning("i=" + str(i) + "Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)
            except asyncio.CancelledError:
                logging.info('Received message to cancel - ignoring so recv can finish up')
                self.begin_shutdown = True
            except asyncio.TimeoutError:
                # server is now ready for input
                SERVER_READY_FOR_INPUT = True
            # except Exception as e:
            #    logging.warning("Caught exception {} in get_all_server_messages()".format(e))
            i += 1

        if request_pong:
            await self.websocket.send(json.dumps({"msg": "pong"}))

    # Todo - add function for send_and_receive to a crawl socket when running via a terminal

    async def send_and_receive(self, message):
        # send data to server
        # print("AWAITING ON WEBSOCKET_1 SEND - sending message: "+str(message))
        await self.websocket.send(json.dumps(message))
        # print("POST-AWAITING ON WEBSOCKET_1 SEND")
        # wait for server to get back

        await self.get_all_server_messages()

    async def send_and_receive_ws(self, message):
        # send data to server
        #print("AWAITING ON WEBSOCKET_1 SEND - sending message: "+str(message))
        await self.websocket.send(GameConnection.json_encode(message))
        # print("POST-AWAITING ON WEBSOCKET_1 SEND")
        # wait for server to get back

        await self.get_all_server_messages()

    async def send_and_receive_command_ws(self, command):
        # send data to server
        #print("AWAITING ON WEBSOCKET_1 SEND - sending command: "+str(command))
        await self.websocket.send(GameConnection.json_encode(Action.get_execution_repr(command)))
        # print("POST-AWAITING ON WEBSOCKET_1 SEND")
        # wait for server to get back

        await self.get_all_server_messages()


    # Todo remove this or fix it
    # async def end_session_and_quit_game(self):
    #     '''
    #     Sends the ctrl-q signal to the webserver to permamently end the game.
    #     :return:
    #     '''
    #     if not self.game_ended:
    #         for quit_msg in quit_messages_sequence:
    #             await self.send_and_receive(quit_msg)
    #
    #         self.game_ended = True
    #
    #     logging.info("Sent all quit messages, game is deleted...")

    async def connect_webserver(self):
        print("Logging in...")
        await self.login_webserver()
        print("Loading game...")
        await self.load_game_on_webserver()

    def connect(self):
        try:
            os.unlink(self.config.socketpath)
        except OSError:
            if os.path.exists(self.config.socketpath):
                raise

        if self.ready_to_connect():
            primary = True

            self.crawl_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.crawl_socket.settimeout(10)

            self.crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            if (self.crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < 2048):
                self.crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

            if (self.crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < 212992):
                self.crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)

            msg = GameConnection.json_encode({
                "msg": "attach",
                "primary": primary
            })

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

            self.crawl_socket.bind(self.config.socketpath)

            self._send_message(msg)

            self._read_msgs()

    def ready_to_connect(self):
        return os.path.exists(self.config.crawl_socketpath) and not os.path.exists(self.config.socketpath)

    def close(self):
        if self.crawl_socket:
            print("Closing socket...")
            self.crawl_socket.close()
            # socketpathobj.close()
            os.unlink(self.config.socketpath)
            crawl_socket = None

    def _send_message(self, data):
        start = datetime.now()
        try:
            self.crawl_socket.sendto(data.encode('utf-8'), self.config.crawl_socketpath)
        except socket.timeout:
            # self.logger.warning("Game socket send timeout", exc_info=True)
            print("ERROR: in send_message() - Game socket send timeout")
            self.close()
            return
        end = datetime.now()
        if end - start >= timedelta(seconds=1):
            print("Slow socket send: " + str(end - start))
            # self.logger.warning("Slow socket send: " + str(end - start))

    def _control_input(self, c):
        self._send_message(GameConnection.json_encode({'msg': 'key', 'keycode': ord(c) - ord('A') + 1}))

    def _send_input(self, input_str):
        for c in input_str:
            self._send_message(GameConnection.json_encode({'msg': 'key', 'keycode': ord(c)}))

    def _read_msg(self):
        try:
            self.recent_msg_data_raw = self.crawl_socket.recv(128 * 1024, socket.MSG_DONTWAIT)
            self.num_times_pressed_enter_read_msg = 0
        except socket.timeout:
            # first try to send and receive 'r' since the game might just be waiting with lots of messages
            if self.num_times_pressed_enter_read_msg <= self.num_times_to_try_pressing_enter_read_msg:
                self.send_and_receive_str('\r')
                self.num_times_pressed_enter_read_msg += 1
            else:
                print("ERROR: in read_msg() - Game socket send timeout")
                self.close()
                return ''

        if isinstance(self.recent_msg_data_raw, bytes):
            self.recent_msg_data_decoded = self.recent_msg_data_raw.decode("utf-8")

        if self.msg_buffer is not None:
            self.recent_msg_data_decoded = self.msg_buffer + self.recent_msg_data_decoded

        if self.recent_msg_data_decoded[-1] != "\n":
            # All messages from crawl end with \n.
            # If this one doesn't, it's fragmented.
            self.msg_buffer = self.recent_msg_data_decoded
        else:
            self.msg_buffer = None
            return self.recent_msg_data_decoded
        return ''

    def _handle_msgs(self, msgs):
        self.game_state.update(msgs)

    def get_gamestate(self):
        return self.game_state

    def _read_msgs(self):
        msgs = []
        data = self._read_msg()
        # TODO: This doesn't seem to be the correct way to determine the end of the messages
        while "flush_messages" not in data:
            if len(data) > 0 and not data.startswith("*"):
                msgs.append(json.loads(data))
                # game_state.update(msgs[-1])
            elif data.startswith("*"):
                server_msg = json.loads(data[1:])
                # TODO: Handle server messages (client_path,flush_messages,dump,exit_reason)
            data = self._read_msg()
        self._handle_msgs(msgs)
        return msgs

    def _send_command(self, command):
        self._send_message(GameConnection.json_encode(Action.get_execution_repr(command)))

    async def _send_command_ws(self, command):
        await self.websocket.send(GameConnection.json_encode(Action.get_execution_repr(command)))

    def send_and_receive_dict(self, input_dict):
        logging.debug("Sending {}".format(input_dict))
        self._send_message(GameConnection.json_encode(input_dict))
        msgs = self._read_msgs()
        self._handle_msgs(msgs)

    async def send_and_receive_dict_ws(self, input_dict):
        logging.debug("Sending {}".format(input_dict))
        await self.send_and_receive(input_dict)

    def send_and_receive_str(self, input_str):
        logging.debug("Sending {}".format(input_str))
        self._send_input(input_str)
        msgs = self._read_msgs()
        self._handle_msgs(msgs)

    def send_and_receive_command(self, command, sleep_secs=0.05):
        logging.debug("Sending {}".format(command.name))
        self._send_command(command)
        if sleep_secs > 0:
            time.sleep(sleep_secs)
        msgs = self._read_msgs()
        self._handle_msgs(msgs)

