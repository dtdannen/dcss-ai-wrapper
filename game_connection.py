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

    @staticmethod
    def json_encode(value):
        return json.dumps(value).replace("</", "<\\/")

    def connect_webserver(self):
        pass

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

    def send_and_receive_dict(self, input_dict):
        logging.debug("Sending {}".format(input_dict))
        self._send_message(GameConnection.json_encode(input_dict))
        msgs = self._read_msgs()
        self._handle_msgs(msgs)

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

