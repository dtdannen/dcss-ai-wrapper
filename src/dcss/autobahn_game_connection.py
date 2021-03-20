from gamestate import GameState
from actions import Action

import json
import time
from src.dcss import config
import zlib
import copy

from nested_lookup import nested_lookup

import asyncio
import importlib
from autobahn.asyncio.websocket import WebSocketClientProtocol
from enum import Enum
from agent import *  # We need to import all AI classes so that whatever one is in the config file, it will be found


class MenuBackgroundKnowledge:
    tutorial_lesson_number_to_hotkey = {1: 97, 2: 98, 3: 99, 4: 100, 5: 101}
    sprint_map_letter_to_hotkey = {'a': 97, 'b': 98, 'c': 99, 'd': 100, 'e': 101, 'f': 102, 'g': 103, 'h': 104,
                                   'i': 105}


class Menu(Enum):
    NO_MENU = 1
    CHARACTER_CREATION_SELECT_SPECIES = 2
    CHARACTER_CREATION_SELECT_BACKGROUND = 3
    CHARACTER_CREATION_SELECT_WEAPON = 4
    CHARACTER_INVENTORY_MENU = 5
    CHARACTER_ITEM_SPECIFIC_MENU = 6
    TUTORIAL_SELECTION_MENU = 7
    SPRINT_MAP_SELECTION_MENU = 8


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
        self._GAME_MODE_SELECTED = False
        self._LOBBY_IS_CLEAR = False
        self._IN_LOBBY = False

        self._IN_GAME_SEED_MENU = False
        self._SENT_GAME_SEED = False
        self._CHECKED_BOX_FOR_PREGENERATION = False
        self._READY_TO_SEND_SEED_GAME_START = False
        self._SENT_SEEDED_GAME_START = False
        self._SENT_SEEDED_GAME_START_CONFIRMATION = False

        self._GAME_STARTED = False
        self._IN_MENU = Menu.NO_MENU
        self._SENT_SPECIES_SELECTION = False
        self._SENT_BACKGROUND_SELECTION = False
        self._SENT_WEAPON_SELECTION = False
        self._IN_CHARACTER_CREATION_MENUS = False
        self._RECEIVED_MAP_DATA = False

        self._PLAYER_DIED = False

        self._BEGIN_DELETING_GAME = False
        self._SENT_CTRL_Q_TO_DELETE_GAME = False
        self._SENT_YES_TEXT_TO_DELETE_GAME = False
        self._SENT_ENTER_1_TO_DELETE_GAME = False
        self._SENT_ENTER_2_TO_DELETE_GAME = False
        self._SENT_ENTER_3_TO_DELETE_GAME = False

        self.last_message_sent = None
        self.next_action_msg = None
        self.actions_sent = 0

        self.messages_received_counter = 0
        self.species_options = {}
        self.background_options = {}
        self.weapon_options = {}

        self.death_summaries = []

        self.agent = None
        self.load_ai_agent()

        self.previous_agents = []
        self.previous_game_states = []

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
            elif self._CONNECTED and self._NEEDS_ENTER:
                print("SENDING ENTER KEY BECAUSE OF PROMPT")
                enter_key_msg = {"text": "\r", "msg": "input"}
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

                #### BEGIN SEEDED GAME MENU NAVIGATION ####
                elif self.config.game_id == 'seeded-web-trunk' and self._IN_GAME_SEED_MENU and not self._SENT_GAME_SEED:
                    print("SENDING GAME SEED")
                    game_seed_msg = {"text": str(config.WebserverConfig.seed), "generation_id": 1, "widget_id": "seed",
                                     "msg": "ui_state_sync"}
                    self.sendMessage(json.dumps(game_seed_msg).encode('utf-8'))
                    self._SENT_GAME_SEED = True

                elif self.config.game_id == 'seeded-web-trunk' and self._SENT_GAME_SEED and not self._CHECKED_BOX_FOR_PREGENERATION:
                    print("SENDING CHECKMARK TO CONFIRM PREGENERATION OF DUNGEON")
                    pregeneration_checkbox_msg = {"checked": True, "generation_id": 1, "widget_id": "pregenerate",
                                                  "msg": "ui_state_sync"}
                    self.sendMessage(json.dumps(pregeneration_checkbox_msg).encode('utf-8'))
                    self._CHECKED_BOX_FOR_PREGENERATION = True

                elif self.config.game_id == 'seeded-web-trunk' and self._READY_TO_SEND_SEED_GAME_START and self._SENT_GAME_SEED and self._CHECKED_BOX_FOR_PREGENERATION and not self._SENT_SEEDED_GAME_START:
                    print("SENDING MESSAGE TO START THE SEEDED GAME WITH CLICK BUTTON MESSAGE")
                    start_seeded_game_msg_button = {"generation_id": 1, "widget_id": "btn-begin",
                                                    "msg": "ui_state_sync"}
                    self.sendMessage(json.dumps(start_seeded_game_msg_button).encode('utf-8'))
                    self._SENT_SEEDED_GAME_START = True

                elif self.config.game_id == 'seeded-web-trunk' and self._SENT_SEEDED_GAME_START and not self._SENT_SEEDED_GAME_START_CONFIRMATION:
                    print("SENDING MESSAGE TO CONFIRM THE SEEDED GAME WITH CLICK BUTTON MESSAGE")
                    confirm_seeded_game_msg_button = {"keycode": 13, "msg": "key"}
                    self.sendMessage(json.dumps(confirm_seeded_game_msg_button).encode('utf-8'))
                    self._SENT_SEEDED_GAME_START_CONFIRMATION = True
                #### END SEEDED GAME MENU NAVIGATION ####

                #### BEGIN TUTORIAL GAME MENU NAVIGATION ####
                elif self.config.game_id == 'tut-web-trunk' and self._IN_MENU == Menu.TUTORIAL_SELECTION_MENU:
                    print("SENDING MESSAGE TO SELECT THE TUTORIAL #{} IN THE TUTORIAL MENU".format(
                        config.WebserverConfig.tutorial_number))
                    hotkey = MenuBackgroundKnowledge.tutorial_lesson_number_to_hotkey[
                        config.WebserverConfig.tutorial_number]
                    tutorial_lesson_selection_message = {"keycode": hotkey, "msg": "key"}
                    self.sendMessage(json.dumps(tutorial_lesson_selection_message).encode('utf-8'))
                    self._IN_MENU = Menu.NO_MENU
                #### END TUTORIAL GAME MENU NAVIGATION ####

                #### BEGIN TUTORIAL GAME MENU NAVIGATION ####
                elif self.config.game_id == 'sprint-web-trunk' and self._IN_MENU == Menu.SPRINT_MAP_SELECTION_MENU:
                    print("SENDING MESSAGE TO SELECT THE TUTORIAL #{} IN THE SPRINT MENU".format(
                        config.WebserverConfig.tutorial_number))
                    hotkey = MenuBackgroundKnowledge.sprint_map_letter_to_hotkey[
                        config.WebserverConfig.sprint_map_letter]
                    sprint_map_selection_message = {"keycode": hotkey, "msg": "key"}
                    self.sendMessage(json.dumps(sprint_map_selection_message).encode('utf-8'))
                    self._IN_MENU = Menu.NO_MENU
                #### END TUTORIAL GAME MENU NAVIGATION ####

                elif self._GAME_STARTED:
                    if self._IN_MENU == Menu.CHARACTER_CREATION_SELECT_SPECIES and not self._SENT_SPECIES_SELECTION:
                        if self.character_config.species not in self.species_options.keys():
                            print(
                                "ERROR species {} specified in config is not available. Available choices are: {}".format(
                                    self.character_config.species, self.species_options.keys()))
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
                            print(
                                "ERROR background {} specified in config is not available. Available choices are: {}".format(
                                    self.character_config.background, self.background_options.keys()))
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
                            print(
                                "ERROR weapon {} specified in config is not available. Available choices are: {}".format(
                                    self.character_config.starting_weapon, self.weapon_options.keys()))
                        else:
                            weapon_selection_hotkey = self.weapon_options[self.character_config.starting_weapon]
                            weapon_selection_msg = self.get_hotkey_json_as_msg(weapon_selection_hotkey)
                            print("SENDING WEAPON SELECTION MESSAGE OF: {}".format(weapon_selection_msg))
                            self._SENT_WEAPON_SELECTION = True
                            # Right before we send the message, clear the menu - this only fails if the message being sent fails
                            self._IN_MENU = Menu.NO_MENU
                            self.sendMessage(json.dumps(weapon_selection_msg).encode('utf-8'))

                    if self._PLAYER_DIED and self._IN_MENU == Menu.CHARACTER_INVENTORY_MENU:
                        print("SENDING ENTER KEY BECAUSE WE ARE IN THE INVENTORY AFTER DEATH MENU")
                        enter_key_msg = {"text": "\r", "msg": "input"}
                        self.sendMessage(json.dumps(enter_key_msg).encode('utf-8'))

                    if self._IN_MENU == Menu.NO_MENU and self._RECEIVED_MAP_DATA and not self._BEGIN_DELETING_GAME:
                        self.game_state.draw_cell_map()
                        if self.agent:
                            next_action = self.agent.get_action(self.game_state)

                            if next_action:
                                print("We are about to send action: {}".format(self.next_action_msg))
                                self.sendMessage(json.dumps(Action.get_execution_repr(next_action)).encode('utf-8'))
                                self.last_message_sent = next_action
                                self.actions_sent += 1
                            else:
                                raise Exception("next_action is {}".format(next_action))

                            print("We are now ready to send an action")
                        else:
                            print("Game Connection Does Not Have An Agent")

                    # State machine to abandon character and delete the game
                    if self._BEGIN_DELETING_GAME and not self._SENT_CTRL_Q_TO_DELETE_GAME:
                        # send abandon character and quit game (mimics ctrl-q)
                        abandon_message = {"msg": "key", "keycode": 17}
                        print("SENDING CTRL-Q TO ABANDON CHARACTER")
                        self.sendMessage(json.dumps(abandon_message).encode('utf-8'))
                        self._SENT_CTRL_Q_TO_DELETE_GAME = True

                    elif self._BEGIN_DELETING_GAME and self._SENT_CTRL_Q_TO_DELETE_GAME and not self._SENT_YES_TEXT_TO_DELETE_GAME:
                        # send 'yes' confirmation string
                        confirmation_message = {"text": "yes\r", "msg": "input"}
                        print("SENDING YES CONFIRMATION TO ABANDON CHARACTER")
                        self.sendMessage(json.dumps(confirmation_message).encode('utf-8'))
                        self._SENT_YES_TEXT_TO_DELETE_GAME = True

                    elif self._BEGIN_DELETING_GAME and self._SENT_YES_TEXT_TO_DELETE_GAME and not self._SENT_ENTER_1_TO_DELETE_GAME:
                        # send first enter to clear the menu
                        first_enter_msg = {"text": "\r", "msg": "input"}
                        print("SENDING FIRST ENTER FOLLOWING TO ABANDON CHARACTER")
                        self.sendMessage(json.dumps(first_enter_msg).encode('utf-8'))
                        self._SENT_ENTER_1_TO_DELETE_GAME = True

                    elif self._BEGIN_DELETING_GAME and self._SENT_ENTER_1_TO_DELETE_GAME and not self._SENT_ENTER_2_TO_DELETE_GAME:
                        # send first enter to clear the menu
                        second_enter_msg = {"text": "\r", "msg": "input"}
                        print("SENDING SECOND ENTER FOLLOWING TO ABANDON CHARACTER")
                        self.sendMessage(json.dumps(second_enter_msg).encode('utf-8'))
                        self._SENT_ENTER_2_TO_DELETE_GAME = True

                    elif self._BEGIN_DELETING_GAME and self._SENT_ENTER_2_TO_DELETE_GAME and not self._SENT_ENTER_3_TO_DELETE_GAME:
                        # send first enter to clear the menu
                        third_enter_msg = {"text": "\r", "msg": "input"}
                        print("SENDING THIRD ENTER FOLLOWING TO ABANDON CHARACTER")
                        self.sendMessage(json.dumps(third_enter_msg).encode('utf-8'))
                        self._SENT_ENTER_3_TO_DELETE_GAME = True
                        self.reset_before_next_game()

            await asyncio.sleep(config.WebserverConfig.delay)

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
            print(
                "Failure to parse message_as_json\n****** you may have spectated too soon, best thing to do is just to restart the agent ******")
            time.sleep(20)

        self.game_state.update(message_as_json)

        self.perform_state_checks(message_as_json)

    def reset_before_next_game(self):
        print("CALLING RESET BEFORE THE NEXT GAME")
        # we return to the lobby after finishing a game, so reset up old state variables
        self._GAME_MODE_SELECTED = False
        self._LOBBY_IS_CLEAR = False
        self._IN_LOBBY = False

        self._IN_GAME_SEED_MENU = False
        self._SENT_GAME_SEED = False
        self._CHECKED_BOX_FOR_PREGENERATION = False
        self._READY_TO_SEND_SEED_GAME_START = False
        self._SENT_SEEDED_GAME_START = False
        self._SENT_SEEDED_GAME_START_CONFIRMATION = False

        self._GAME_STARTED = False
        self._IN_MENU = Menu.NO_MENU
        self._SENT_SPECIES_SELECTION = False
        self._SENT_BACKGROUND_SELECTION = False
        self._SENT_WEAPON_SELECTION = False
        self._IN_CHARACTER_CREATION_MENUS = False
        self._RECEIVED_MAP_DATA = False

        self._PLAYER_DIED = False

        self._BEGIN_DELETING_GAME = False
        self._SENT_CTRL_Q_TO_DELETE_GAME = False
        self._SENT_YES_TEXT_TO_DELETE_GAME = False
        self._SENT_ENTER_1_TO_DELETE_GAME = False
        self._SENT_ENTER_2_TO_DELETE_GAME = False
        self._SENT_ENTER_3_TO_DELETE_GAME = False

        # keep the old gamestate for data purposes
        self.previous_game_states.append(copy.deepcopy(self.game_state))

        # reset the game state!
        self.game_state = GameState()

        # keep the old agent for data purposes
        self.previous_agents.append(copy.deepcopy(self.agent))
        print("THERE ARE NOW {} PREVIOUS AGENTS".format(len(self.previous_agents)))

        # reset the agent!
        self.load_ai_agent()  # loads the ai agent specific in the AIConfig in config.py

    def perform_state_checks(self, json_msg):
        if self.check_for_ping(json_msg):
            self._NEEDS_PONG = True
            self._CONNECTED = True
            print("setting _NEEDS_PONG = TRUE")
            print("setting _CONNECTED = TRUE")

        if self.check_for_enter_key(json_msg):
            print("setting _NEEDS_ENTER = TRUE")
            self._NEEDS_ENTER = True

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

        if self.check_for_tutorial_menu(json_msg):
            self._IN_MENU = Menu.TUTORIAL_SELECTION_MENU
            print("setting _IN_MENU = Menu.TUTORIAL_SELECTION_MENU")

        if self.check_for_inventory_menu(json_msg):
            self._IN_MENU = Menu.CHARACTER_INVENTORY_MENU
            print("setting _IN_MENU = Menu.CHARACTER_INVENTORY_MENU")

        if self.check_for_game_started(json_msg):
            print("setting _GAME_STARTED = TRUE")
            self._GAME_STARTED = True
            self._IN_LOBBY = False

        if self.check_for_death_message(json_msg):
            # Reset the agent and other state variables because we return back to the lobby
            # in between games
            self.reset_before_next_game()

            self.death_summaries.append(json_msg)
            print("Just appended a new death message; death messages so far:")
            for death_msg in self.death_summaries:
                print("{}".format(death_msg))

        if self.check_for_action_limit_reached():
            print("ACTION LIMIT REACHED! setting _BEGIN_DELETING_GAME = True")
            self._BEGIN_DELETING_GAME = True

        if not self._RECEIVED_MAP_DATA and self.check_received_map_data(json_msg):
            print("setting _RECEIVED_MAP_DATA = TRUE")
            self._RECEIVED_MAP_DATA = True

        if self._GAME_STARTED:
            if self.check_for_species_selection_menu(json_msg):
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

            if self.check_if_player_died(json_msg):
                self._PLAYER_DIED = True

        if self.check_for_sprint_map_menu(json_msg):
            self._IN_MENU = Menu.SPRINT_MAP_SELECTION_MENU
            print("setting _IN_MENU = Menu.SPRINT_MAP_SELECTION_MENU")

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
        input_mode_found = False
        for v in nested_lookup('msg', json_msg):
            if v == 'input_mode':
                input_mode_found = True

        mode_is_5 = False
        for v in nested_lookup('mode', json_msg):
            if v == 5:
                mode_is_5 = True

        return input_mode_found and mode_is_5

    def check_for_inventory_menu(self, json_msg):
        input_mode_found = False
        for v in nested_lookup('msg', json_msg):
            if v == 'input_mode':
                input_mode_found = True

        inventory_tag_found = False
        for v in nested_lookup('tag', json_msg):
            if v == 'inventory':
                inventory_tag_found = True

        return input_mode_found and inventory_tag_found

    def check_for_sprint_map_menu(self, json_msg):
        for v in nested_lookup('title', json_msg):
            if 'You have a choice of maps' in v:
                return True
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

    def check_for_tutorial_menu(self, json_msg):
        for v in nested_lookup('title', json_msg):
            if 'You have a choice of lessons' in v:
                return True
        return False

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

    def check_if_player_died(self, json_msg):
        for v in nested_lookup('text', json_msg):
            if 'You die...' in v:
                return True
        return False

    def check_for_death_message(self, json_msg):
        reason_is_dead_found = False
        for v in nested_lookup('reason', json_msg):
            if v == 'dead':
                reason_is_dead_found = True

        message_game_ended = False
        for v in nested_lookup('msg', json_msg):
            if v == 'game_ended':
                message_game_ended = True

        return reason_is_dead_found and message_game_ended

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
                    # print("species_option: {}".format(species_option))
                    hotkey = species_option["hotkey"]
                    species_name = None
                    if 'labels' in species_option.keys():
                        species_name = species_option["labels"][0].split('-')[-1].strip()
                    elif 'label' in species_option.keys():
                        species_name = species_option["label"].split('-')[-1].strip()
                    else:
                        print("WARNING - Could not find label for species option json: {}".format(species_option))

                    if species_name:
                        # print("Just found species {} with hotkey {}".format(species_name, hotkey))
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
                    # print("background_option: {}".format(background_option))
                    hotkey = background_option["hotkey"]
                    if hotkey != 9:
                        # '9' corresponds to the background used in the last game, ignore for now TODO - find a better solution
                        background_name = None
                        if 'labels' in background_option.keys():
                            background_name = background_option["labels"][0].split('-')[-1].strip()
                        elif 'label' in background_option.keys():
                            background_name = background_option["label"].split('-')[-1].strip()
                        else:
                            print("WARNING - Could not find label for background option json: {}".format(
                                background_option))

                        if background_name:
                            # print("Just found background {} with hotkey {}".format(background_name, hotkey))
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
                    # print("weapon_option: {}".format(weapon_option))
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
                            # print("Just found weapon {} with hotkey {}".format(weapon_name, hotkey))
                            weapon_name_to_hotkeys[weapon_name] = int(hotkey)
            return weapon_name_to_hotkeys

    def check_for_action_limit_reached(self):
        action_limit = config.WebserverConfig.max_actions
        if action_limit >= 0:
            return self.actions_sent >= action_limit
        return False

    def get_hotkey_json_as_msg(self, hotkey):
        return {"keycode": hotkey, "msg": "key"}

    def get_gamestate(self):
        return self.game_state

    def load_ai_agent(self):
        module = importlib.import_module('agent')
        self.agent = getattr(module, config.AIConfig.ai_python_class)()

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection onClose() called")

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
