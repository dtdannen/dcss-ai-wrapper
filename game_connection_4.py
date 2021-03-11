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
import threading

from nested_lookup import nested_lookup


import asyncio
import importlib
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from enum import Enum
from agent import *  # We need to import all AI classes so that whatever one is in the config file, it will be found


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))


    async def onOpen(self):
        print("WebSocket connection open.")

        # start sending messages every second ..
        while True:
            self.sendMessage("Hello, world!".encode('utf8'))
            self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
            await asyncio.sleep(1)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


class Menu(Enum):
    NO_MENU = 1
    CHARACTER_CREATION_SELECT_SPECIES = 2
    CHARACTER_CREATION_SELECT_BACKGROUND = 3
    CHARACTER_CREATION_SELECT_WEAPON = 4
    CHARACTER_INVENTORY_MENU = 5
    CHARACTER_ITEM_SPECIFIC_MENU = 6


class DCSSProtocol(WebSocketClientProtocol):

    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        self.config = config.WebserverConfig
        self.character_config = config.CharacterCreationConfig
        self.decomp = zlib.decompressobj(-zlib.MAX_WBITS)

        # States of the connection which determines which messages are relevant to send when
        self._READY_TO_CONNECT = True
        self._CONNECTED = False
        self._READY_TO_LOGIN = False
        self._LOGGED_IN = False
        self._NEEDS_PONG = False
        self._NEEDS_ENTER = False
        self._READY_TO_SELECT_GAME_MODE = False
        self._GAME_MODE_SELECTED = False
        self._READY_TO_SEND_ACTION = False
        self._LOBBY_IS_CLEAR = False
        self._IN_LOBBY = False
        self._IN_GAME_SEED_MENU = False
        self._SENT_GAME_SEED = False
        self._CHECKED_BOX_FOR_PREGENERATION = False
        self._READY_TO_SEND_SEED_GAME_START = False
        self._SENT_SEEDED_GAME_START = False
        self._GAME_STARTED = False
        self._IN_MENU = Menu.NO_MENU  # TODO LEFT OFF HERE - change menus to use this single menu variable
        self._SENT_SPECIES_SELECTION = False
        self._SENT_BACKGROUND_SELECTION = False
        self._SENT_WEAPON_SELECTION = False
        self._IN_CHARACTER_CREATION_MENUS = False
        self._RECEIVED_MAP_DATA = False

        self.last_message_sent = None
        self.next_action_msg = None

        self.messages_received_counter = 0
        self.species_options = {}
        self.background_options = {}
        self.weapon_options = {}

        self.load_ai_agent()  # loads the ai agent specific in the AIConfig in config.py

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        print("setting _CONNECTED = True")
        self._CONNECTED = True

    async def onOpen(self):
        print("WebSocket connection open.")

        # start sending messages every second ..
        while True:

            if self._CONNECTED and self._NEEDS_PONG:
                print("SENDING PONG MESSAGE")
                pong_msg = {"msg": "pong"}
                self.sendMessage(json.dumps(pong_msg).encode('utf-8'))
                self._NEEDS_PONG = False
            elif self._CONNECTED and self._GAME_STARTED and self._NEEDS_ENTER:
                print("SENDING ENTER KEY BECAUSE OF PROMPT")
                enter_key_msg = {"text":"\r","msg":"input"}
                self.sendMessage(json.dumps(enter_key_msg).encode('utf-8'))
                self._NEEDS_ENTER = False
            else:
                if self._CONNECTED and not self._LOGGED_IN:
                    print("SENDING LOGIN MESSAGE")
                    login_msg = {'msg': 'login',
                                 'username': self.config.agent_name,
                                 'password': self.config.agent_password}
                    self.sendMessage(json.dumps(login_msg).encode('utf-8'))

                elif self._LOGGED_IN and self._IN_LOBBY and not self._GAME_STARTED:
                    print("SENDING GAME MODE SELECTION MESSAGE")
                    play_game_msg = {'msg': 'play', 'game_id': self.config.game_id}
                    self.sendMessage(json.dumps(play_game_msg).encode('utf-8'))

                elif self.config.game_id == 'seeded-web-trunk' and self._IN_GAME_SEED_MENU and not self._SENT_GAME_SEED:
                    print("SENDING GAME SEED")
                    game_seed_msg = {"text":str(config.WebserverConfig.seed),"generation_id":1,"widget_id":"seed","msg":"ui_state_sync"}
                    self.sendMessage(json.dumps(game_seed_msg).encode('utf-8'))
                    self._SENT_GAME_SEED = True

                elif self.config.game_id == 'seeded-web-trunk' and self._SENT_GAME_SEED and not self._CHECKED_BOX_FOR_PREGENERATION:
                    print("SENDING CHECKMARK TO CONFIRM PREGENERATION OF DUNGEON")
                    pregeneration_checkbox_msg = {"checked":True,"generation_id":1,"widget_id":"pregenerate","msg":"ui_state_sync"}
                    self.sendMessage(json.dumps(pregeneration_checkbox_msg).encode('utf-8'))
                    self._CHECKED_BOX_FOR_PREGENERATION = True

                elif self.config.game_id == 'seeded-web-trunk' and self._READY_TO_SEND_SEED_GAME_START and self._SENT_GAME_SEED and self._CHECKED_BOX_FOR_PREGENERATION and not self._SENT_SEEDED_GAME_START:
                    print("SENDING MESSAGE TO START THE SEEDED GAME WITH CLICK BUTTON MESSAGE")
                    start_seeded_game_msg_button = {"generation_id":1,"widget_id":"btn-begin","msg":"ui_state_sync"}
                    self.sendMessage(json.dumps(start_seeded_game_msg_button).encode('utf-8'))
                    self._SENT_SEEDED_GAME_START = True

                elif self._GAME_STARTED:
                    if self._IN_MENU == Menu.CHARACTER_CREATION_SELECT_SPECIES and not self._SENT_SPECIES_SELECTION:
                        if self.character_config.species not in self.species_options.keys():
                            print("ERROR species {} specified in config is not available. Available choices are: {}".format(self.character_config.species, self.species_options.keys()))
                        else:
                            species_selection_hotkey = self.species_options[self.character_config.species]
                            species_selection_msg = self.get_hotkey_json_as_msg(species_selection_hotkey)
                            print("SENDING SPECIES SELECTION MESSAGE OF: {}".format(species_selection_msg))
                            self._SENT_SPECIES_SELECTION = True
                            # Right before we send the message, clear the menu - this only fails if the message being sent fails
                            self._IN_MENU = Menu.NO_MENU
                            self.sendMessage(json.dumps(species_selection_msg).encode('utf-8'))

                    if self._IN_MENU == Menu.CHARACTER_CREATION_SELECT_BACKGROUND and not self._SENT_BACKGROUND_SELECTION:
                        if self.character_config.background not in self.background_options.keys():
                            print("ERROR background {} specified in config is not available. Available choices are: {}".format(self.character_config.background, self.background_options.keys()))
                        else:
                            background_selection_hotkey = self.background_options[self.character_config.background]
                            background_selection_msg = self.get_hotkey_json_as_msg(background_selection_hotkey)
                            print("SENDING BACKGROUND SELECTION MESSAGE OF: {}".format(background_selection_msg))
                            self._SENT_BACKGROUND_SELECTION = True
                            # Right before we send the message, clear the menu - this only fails if the message being sent fails
                            self._IN_MENU = Menu.NO_MENU
                            self.sendMessage(json.dumps(background_selection_msg).encode('utf-8'))

                    if self._IN_MENU == Menu.CHARACTER_CREATION_SELECT_WEAPON and not self._SENT_WEAPON_SELECTION:
                        if self.character_config.starting_weapon not in self.weapon_options.keys():
                            print("ERROR weapon {} specified in config is not available. Available choices are: {}".format(self.character_config.starting_weapon, self.weapon_options.keys()))
                        else:
                            weapon_selection_hotkey = self.weapon_options[self.character_config.starting_weapon]
                            weapon_selection_msg = self.get_hotkey_json_as_msg(weapon_selection_hotkey)
                            print("SENDING WEAPON SELECTION MESSAGE OF: {}".format(weapon_selection_msg))
                            self._SENT_WEAPON_SELECTION = True
                            # Right before we send the message, clear the menu - this only fails if the message being sent fails
                            self._IN_MENU = Menu.NO_MENU
                            self._IN_CHARACTER_CREATION_MENUS = False
                            self.sendMessage(json.dumps(weapon_selection_msg).encode('utf-8'))


                    # TODO check for inventory menu and other menus

                    if self._IN_MENU == Menu.NO_MENU and not self._IN_CHARACTER_CREATION_MENUS and self._RECEIVED_MAP_DATA:
                        if not self._READY_TO_SEND_ACTION:
                            self._READY_TO_SEND_ACTION = True
                            print("We are now ready to send an action")
                        elif self._READY_TO_SEND_ACTION:
                            self.game_state.draw_cell_map()
                            self._READY_TO_SEND_ACTION = False
                            next_action = self.get_agent_next_action()
                            if next_action:
                                print("We are about to send action: {}".format(self.next_action_msg))
                                self.sendMessage(json.dumps(Action.get_execution_repr(next_action)).encode('utf-8'))
                                self.last_message_sent = next_action
                            self._READY_TO_SEND_ACTION = True
                            print("We are now ready to send an action")

            await asyncio.sleep(0.05)

    def onMessage(self, payload, isBinary):
        print("Message {} recieved: isBinary={}".format(self.messages_received_counter, isBinary))
        self.messages_received_counter += 1
        message_as_str = None
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
            payload += bytes([0, 0, 255, 255])
            json_message = self.decomp.decompress(payload)
            json_message_decoded = json_message.decode("utf-8")
            print("   Decoding turns it into: {}".format(json_message_decoded))
            message_as_str = json_message_decoded
        else:
            print("Text message received: {0}".format(payload.decode('utf-8')))
            message_as_str = payload.decode('utf-8')

        message_as_json = {}
        try:
            message_as_json = json.loads(message_as_str)
        except:
            print("Failure to parse message_as_json")
            time.sleep(20)

        self.game_state.update(message_as_json)

        self.perform_state_checks(message_as_json)


    def perform_state_checks(self, json_msg):
        if self.check_for_ping(json_msg):
            self._NEEDS_PONG = True
            self._CONNECTED = True
            print("setting _NEEDS_PONG = TRUE")
            print("setting _CONNECTED = TRUE")

        if self.check_for_enter_key(json_msg):
            print("Checking for enter key, msg is:{}".format(json_msg))
            return False

        if self.check_for_in_lobby(json_msg):
            self._IN_LOBBY = True
            print("setting _IN_LOBBY = TRUE")

        if self.check_for_login_success(json_msg):
            self._LOGGED_IN = True
            print("setting _LOGGED_IN = TRUE")

        if self.check_for_lobby_clear(json_msg):
            self._LOBBY_IS_CLEAR = True
            print("setting _LOBBY_IS_CLEAR = TRUE")

        if self.check_for_game_seed_menu(json_msg):
            self._IN_GAME_SEED_MENU = True
            print("setting _IN_GAME_SEED_MENU = TRUE")

        if self.check_for_pregeneration_check_true(json_msg):
            self._READY_TO_SEND_SEED_GAME_START = True
            print("setting _READY_TO_SEND_SEED_GAME_START = True")

        if self.check_for_game_started(json_msg):
            print("setting _GAME_STARTED = TRUE")
            self._GAME_STARTED = True
            self._IN_LOBBY = False

        if not self._RECEIVED_MAP_DATA and self.check_received_map_data(json_msg):
            print("setting _RECEIVED_MAP_DATA = TRUE")
            self._RECEIVED_MAP_DATA = True

        if self._GAME_STARTED:
            if self.check_for_species_selection_menu(json_msg):
                self._IN_CHARACTER_CREATION_MENUS = True
                print("setting self.IN_MENU = Menu.CHARACTER_CREATION_SELECT_SPECIES")
                self._IN_MENU = Menu.CHARACTER_CREATION_SELECT_SPECIES
                self.species_options = self.get_species_options(json_msg)

            if self.check_for_background_selection_menu(json_msg):
                print("setting self.IN_MENU = Menu.CHARACTER_CREATION_SELECT_BACKGROUND")
                self._IN_MENU = Menu.CHARACTER_CREATION_SELECT_BACKGROUND
                self.background_options = self.get_background_options(json_msg)

            if self.check_for_weapon_selection_menu(json_msg):
                print("setting self.IN_MENU = Menu.CHARACTER_CREATION_SELECT_WEAPON")
                self._IN_MENU = Menu.CHARACTER_CREATION_SELECT_WEAPON
                self.weapon_options = self.get_weapon_options(json_msg)


    def check_for_in_lobby(self, json_msg):
        for v in nested_lookup('msg', json_msg):
            if v == 'set_game_links':
                return True
        return False

    def check_for_ping(self, json_msg):
        for v in nested_lookup('msg', json_msg):
            if v == 'ping':
                return True
        return False

    def check_for_enter_key(self, json_msg):
        return False

    def check_for_game_seed_menu(self, json_msg):
        for v in nested_lookup('title', json_msg):
            if 'Play a game with a custom seed' in v:
                return True
        return False

    def check_for_pregeneration_check_true(self, json_msg):
        checked_is_true = False
        pregenerate_widget = False
        for v in nested_lookup('checked', json_msg):
            if v:
                checked_is_true = True

        for v in nested_lookup('widget_id', json_msg):
            if v == "pregenerate":
                pregenerate_widget = True

        return checked_is_true and pregenerate_widget


    def check_for_login_success(self, json_msg):
        for v in nested_lookup('msg', json_msg):
            if v == 'login_success':
                return True
        return False

    def check_for_lobby_clear(self, json_msg):
        for v in nested_lookup('msg', json_msg):
            if v == 'lobby_clear':
                return True
        return False

    def check_for_game_started(self, json_msg):
        for v in nested_lookup('msg', json_msg):
            if v == 'game_started':
                return True
        return False

    def check_received_map_data(self, json_msg):
        for v in nested_lookup('msg', json_msg):
            if v == 'map':
                return True
        return False

    def check_for_species_selection_menu(self, json_msg):
        for v in nested_lookup('title', json_msg):
            if 'Please select your species' in v:
                return True
        return False

    def get_species_options(self, json_msg):
        in_species_main_menu = False
        for v in nested_lookup('menu_id', json_msg):
            if v == 'species-main':
                in_species_main_menu = True

        if in_species_main_menu:
            species_name_to_hotkeys = {}
            for buttons_list in nested_lookup('buttons', json_msg):
                for species_option in buttons_list:
                    #print("species_option: {}".format(species_option))
                    hotkey = species_option["hotkey"]
                    species_name = None
                    if 'labels' in species_option.keys():
                        species_name = species_option["labels"][0].split('-')[-1].strip()
                    elif 'label' in species_option.keys():
                        species_name = species_option["label"].split('-')[-1].strip()
                    else:
                        print("WARNING - Could not find label for species option json: {}".format(species_option))

                    if species_name:
                        #print("Just found species {} with hotkey {}".format(species_name, hotkey))
                        species_name_to_hotkeys[species_name] = int(hotkey)
            return species_name_to_hotkeys

    def check_for_background_selection_menu(self, json_msg):
        for v in nested_lookup('title', json_msg):
            if 'Please select your background' in v:
                return True
        return False

    def get_background_options(self, json_msg):
        in_background_main_menu = False
        for v in nested_lookup('menu_id', json_msg):
            if v == 'background-main':
                in_background_main_menu = True

        if in_background_main_menu:
            background_name_to_hotkeys = {}
            for buttons_list in nested_lookup('buttons', json_msg):
                for background_option in buttons_list:
                    #print("background_option: {}".format(background_option))
                    hotkey = background_option["hotkey"]
                    if hotkey != 9:
                        # '9' corresponds to the background used in the last game, ignore for now TODO - find a better solution
                        background_name = None
                        if 'labels' in background_option.keys():
                            background_name = background_option["labels"][0].split('-')[-1].strip()
                        elif 'label' in background_option.keys():
                            background_name = background_option["label"].split('-')[-1].strip()
                        else:
                            print("WARNING - Could not find label for background option json: {}".format(background_option))

                        if background_name:
                            #print("Just found background {} with hotkey {}".format(background_name, hotkey))
                            background_name_to_hotkeys[background_name] = int(hotkey)
            return background_name_to_hotkeys

    def check_for_weapon_selection_menu(self, json_msg):
        for v in nested_lookup('prompt', json_msg):
            if 'You have a choice of weapons' in v:
                return True
        return False

    def get_weapon_options(self, json_msg):
        in_weapon_main_menu = False
        for v in nested_lookup('menu_id', json_msg):
            if v == 'weapon-main':
                in_weapon_main_menu = True

        if in_weapon_main_menu:
            weapon_name_to_hotkeys = {}
            for buttons_list in nested_lookup('buttons', json_msg):
                for weapon_option in buttons_list:
                    #print("weapon_option: {}".format(weapon_option))
                    hotkey = weapon_option["hotkey"]
                    if hotkey != 9:
                        # '9' corresponds to the background used in the last game, ignore for now TODO - find a better solution

                        weapon_name = None
                        if 'labels' in weapon_option.keys():
                            weapon_name = weapon_option["labels"][0].split('-')[-1].strip()
                        elif 'label' in weapon_option.keys():
                            weapon_name = weapon_option["label"].split('-')[-1].strip()
                        else:
                            print("WARNING - Could not find label for weapon option json: {}".format(weapon_option))

                        if weapon_name:
                            #print("Just found weapon {} with hotkey {}".format(weapon_name, hotkey))
                            weapon_name_to_hotkeys[weapon_name] = int(hotkey)
            return weapon_name_to_hotkeys

    def get_hotkey_json_as_msg(self, hotkey):
        return {"keycode": hotkey, "msg":"key"}

    def ready_to_send_action(self):
        return self._READY_TO_SEND_ACTION

    def get_agent_next_action(self):
        if self.agent:
            next_action = self.agent.get_action(self.game_state)
            return next_action

        return None

    def get_gamestate(self):
        return self.game_state

    def load_ai_agent(self):
        module = importlib.import_module('agent')
        self.agent = getattr(module, config.AIConfig.ai_python_class)()

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))



    #
    # def __init__(self, config=config.DefaultConfig()):
    #
    #     self.config = config
    #     self.crawl_socket = None
    #     self.game_state = GameState()
    #     self.msg_buffer = None
    #     self.recent_msg_data_raw = None
    #     self.recent_msg_data_decoded = None
    #
    #     self.num_times_to_try_pressing_enter_read_msg = 5
    #     self.num_times_pressed_enter_read_msg = 0
    #
    #     self.websocket = None
    #     self.decomp = zlib.decompressobj(-zlib.MAX_WBITS)
    #     self.messages_received = []
    #
    #     # state variables for handling login information and other information
    #     self._READY_TO_CONNECT = True
    #     self._CONNECTED = False
    #     self._READY_TO_LOGIN = False
    #     self._LOGGED_IN = False
    #     self._NEEDS_PONG = False
    #     self._READY_TO_SELECT_GAME_MODE = False
    #     self._GAME_MODE_SELECTED = False
    #     self._READY_TO_SEND_ACTION = False
    #
    #     self._STATE_CHANGED = False
    #
    # @staticmethod
    # def json_encode(value):
    #     return json.dumps(value).replace("</", "<\\/")
    #
    # def get_gamestate(self):
    #     return self.game_state
    #
    # async def connect_webserver(self):
    #     assert isinstance(self.config, config.WebserverConfig)
    #
    #     # connect
    #     logging.info("Connecting to URI " + str(self.config.server_uri) + " ...")
    #     # print("AWAITING ON WEBSOCKET_3 CONNECT")
    #     self.websocket = await websockets.connect(self.config.server_uri)
    #     # print("POST-AWAITING ON WEBSOCKET_3 CONNECT")
    #     logging.info("Connected to webserver:" + str(self.websocket and self.websocket.open))
    #
    # async def login_webserver(self):
    #     assert isinstance(self.config, config.WebserverConfig)
    #
    #     # login
    #     logging.info("Sending login message...")
    #     login_msg = {'msg': 'login',
    #                  'username': self.config.agent_name,
    #                  'password': self.config.agent_password}
    #
    #     await self.send_and_receive_ws(json.dumps(login_msg))
    #     logging.info("Sent login message")
    #
    # async def load_game_on_webserver(self):
    #     assert isinstance(self.config, config.WebserverConfig)
    #
    #     play_game_msg = {'msg': 'play', 'game_id': self.config.game_id}
    #     await self.send_and_receive_ws(play_game_msg)
    #
    # async def send_and_receive_ws(self, message):
    #     # send data to server
    #     #print("AWAITING ON WEBSOCKET_1 SEND - sending message: "+str(message))
    #     await self.websocket.send(json.dumps(message))
    #     # print("POST-AWAITING ON WEBSOCKET_1 SEND")
    #     # wait for server to get back
    #
    #     await self.get_all_server_messages()
    #
    # async def send_and_receive_command_ws(self, command):
    #     # send data to server
    #     #print("AWAITING ON WEBSOCKET_1 SEND - sending command: "+str(command))
    #     await self.websocket.send(GameConnection.json_encode(Action.get_execution_repr(command)))
    #     # print("POST-AWAITING ON WEBSOCKET_1 SEND")
    #     # wait for server to get back
    #
    #     await self.get_all_server_messages()
    #
    # async def get_all_server_messages(self):
    #     i = 0
    #     SERVER_READY_FOR_INPUT = False
    #     request_pong = False
    #     while not SERVER_READY_FOR_INPUT:
    #         try:
    #             future = self.websocket.recv()
    #             # print("** AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))
    #             data_recv = await asyncio.wait_for(future, timeout=0.5)
    #             # print("data_recv_raw is {}".format(data_recv))
    #             # print("** POST-AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))
    #
    #             data_recv += bytes([0, 0, 255, 255])
    #             json_message = self.decomp.decompress(data_recv)
    #             # print("Just received json_message:\n{}".format(json_message))
    #
    #             json_message = json_message.decode("utf-8")
    #
    #             def pretty_print_json(j, spaces="  "):
    #                 for k, v in j.items():
    #                     if isinstance(v, dict):
    #                         print("{}{}:".format(spaces, k))
    #                         return pretty_print_json(v, spaces + "  ")
    #                     if isinstance(v, list):
    #                         print("{}{}:".format(spaces, k))
    #                         for item in v:
    #                             return pretty_print_json(item, spaces + "  ")
    #                     else:
    #                         print("{}{}:{}".format(spaces, k, v))
    #                         return
    #
    #             msg_from_server = json.loads(json_message)
    #
    #             # pretty_print_json(msg_from_server)
    #             self.game_state.update(msg_from_server)
    #
    #             # if 'msgs' in msg_from_server:
    #             #     for msg in msg_from_server['msgs']:
    #             #         if 'msg' in msg:
    #             #             if msg['msg'] == "ping":
    #             #                 request_pong = True
    #             #
    #             # # json_messages_from_server_file.write(pprint.pformat(msg_from_server,indent=2)+'\n')
    #             # # json_messages_from_server_file.flush()
    #             #
    #             # logging.debug("i=" + str(i) + "Received Message:\n" + str(msg_from_server))
    #             #
    #             # if self.ai:
    #             #     self.ai.add_server_message(msg_from_server)
    #             #
    #             # # {'msgs': [{'mode': 1, 'msg': 'input_mode'}]}
    #             # # if 'msgs' in msg_from_server.keys():
    #             # #     for msg in msg_from_server['msgs']:
    #             # #         if 'msg' in msg.keys() and 'mode' in msg.keys():
    #             # #             if msg['msg'] == 'input_mode' and msg['mode'] == 1:
    #             # #                 SERVER_READY_FOR_INPUT = True
    #             # #                 print("Server is now ready for input!")
    #
    #         except ValueError as e:
    #             logging.warning("i=" + str(i) + "Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)
    #         except asyncio.CancelledError:
    #             logging.info('Received message to cancel - ignoring so recv can finish up')
    #             self.begin_shutdown = True
    #         except asyncio.TimeoutError:
    #             # server is now ready for input
    #             print("Got an asyncio Timeout Error")
    #             SERVER_READY_FOR_INPUT = True
    #         except Exception as e:
    #             logging.warning("Caught exception {} in get_all_server_messages()".format(e))
    #         i += 1
    #
    #     if request_pong:
    #         await self.websocket.send(json.dumps({"msg": "pong"}))
