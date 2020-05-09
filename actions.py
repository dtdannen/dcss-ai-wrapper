'''
This file contains messages for key actions and text inputs to be
sent to webserver, including:
* moving around
* accessing the inventory 
* using items 
* ... etc


These keycodes were identified manually be testing commands using
Chrome's develop tools and observing the communications sent through
the websockets.

'''

from enum import Enum


class Command(Enum):
    '''
    These are taken from the in-game manual of crawl.
    '''

    #  Movement
    MOVE_OR_ATTACK_SW = 1
    MOVE_OR_ATTACK_S = 2
    MOVE_OR_ATTACK_SE = 3
    MOVE_OR_ATTACK_W = 4
    MOVE_OR_ATTACK_E = 6
    MOVE_OR_ATTACK_NW = 7
    MOVE_OR_ATTACK_N = 8
    MOVE_OR_ATTACK_NE = 9

    #  Rest
    REST_AND_LONG_WAIT = 5
    WAIT_1_TURN = 10

    #  Extended Movement
    AUTO_EXPLORE = 11
    INTERLEVEL_TRAVEL = 12
    FIND_ITEMS = 13
    SET_WAYPOINT = 14
    LONG_WALK = 15
    ATTACK_WITHOUT_MOVE = 16

    #  Autofight
    AUTO_FIGHT = 17
    AUTO_FIGHT_WITHOUT_MOVE = 18

    #  Item types (and common commands)
    WIELD_HAND_WEAPON = 19
    QUIVER_MISSILE = 20
    FIRE_MISSILE = 21
    SELECT_MISSILE_AND_FIRE = 22
    CYCLE_MISSILE_FORWARD = 23
    CYCLE_MISSILE_BACKWARD = 24
    WEAR_ARMOUR = 25
    TAKE_OFF_ARMOUR = 26
    CHOP_CORPSE = 27
    EAT = 28
    READ = 29
    QUAFF = 30
    PUT_ON_JEWELLERY = 31
    REMOVE_JEWELLERY = 32
    EVOKE = 33
    MEMORISE = 34
    COUNT_GOLD = 35

    #  Other gameplay actions
    USE_SPECIAL_ABILITY = 36
    CAST_SPELL_ABORT_WITHOUT_TARGETS = 37
    CAST_SPELL_NO_MATTER_WHAT = 38
    LIST_ALL_SPELLS = 39
    TELL_ALLIES = 40
    SHOUT_ALLIES = 41
    REDO_PREVIOUS_COMMAND = 42

    #  Game Saving and Quitting
    SAVE_GAME_AND_EXIT = 43
    SAVE_AND_EXIT_WITHOUT_QUERY = 44
    ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME = 45

    #  Player Character Information
    DISPLAY_CHARACTER_STATUS = 46
    SHOW_SKILL_SCREEN = 47
    CHARACTER_OVERVIEW = 48
    SHOW_RELIGION_SCREEN = 49
    SHOW_ABILITIES_AND_MUTATIONS = 50
    SHOW_ITEM_KNOWLEDGE = 51
    SHOW_RUNES_COLLECTED = 52
    DISPLAY_WORN_ARMOUR = 53
    DISPLAY_WORN_JEWELLERY = 54
    DISPLAY_EXPERIENCE_INFO = 55

    #  Dungeon Interaction and Information
    OPEN_DOOR = 56
    CLOSE_DOOR = 57
    TRAVEL_STAIRCASE_DOWN = 58
    TRAVEL_STAIRCASE_UP = 59
    EXAMINE_CURRENT_TILE_PICKUP_PART_OF_SINGLE_STACK = 60
    EXAMINE_SURROUNDINGS_AND_TARGETS = 61
    EXAMINE_LEVEL_MAP = 62
    LIST_MONSTERS_ITEMS_FEATURES_IN_VIEW = 63
    TOGGLE_VIEW_LAYERS = 64
    SHOW_DUNGEON_OVERVIEW = 65
    TOGGLE_AUTO_PICKUP = 66
    TOGGLE_MUTE_SOUND_EFFECTS = 67
    SET_TRAVEL_SPEED_TO_CLOSEST_ALLY = 68

    #  Item Interaction (Inventory)
    SHOW_INVENTORY_LIST = 69
    INSCRIBE_ITEM = 70
    FIRE_NEXT_APPROPRIATE_ITEM = 71
    SELECT_ITEM_AND_FIRE = 72

    # Item Interaction (floor)
    PICKUP_ITEM = 73
    DROP_ITEM = 74
    DROP_EXACT_NUMBER_OF_ITEMS = 75
    DROP_LAST_ITEMS_PICKED_UP = 76

    #  Additional Actions
    EXIT_MENU = 77
    SHOW_PREVIOUS_GAME_MESSAGES = 78
    RESPOND_YES_TO_PROMPT = 79
    RESPOND_NO_TO_PROMPT = 80
    CLEAR_GAME_TEXT_MESSAGES = 81


class Action:
    """
    This class represents an action that the agent can take.
    """

    command_to_msg = \
        {Command.MOVE_OR_ATTACK_N: {'msg': 'key', "keycode": -254},
         Command.MOVE_OR_ATTACK_S: {'msg': 'key', "keycode": -253},
         Command.MOVE_OR_ATTACK_E: {'msg': 'key', "keycode": -251},
         Command.MOVE_OR_ATTACK_W: {'msg': 'key', "keycode": -252},
         Command.MOVE_OR_ATTACK_NW: {'msg': 'key', "keycode": -1007},
         Command.MOVE_OR_ATTACK_SW: {'msg': 'key', "keycode": -1001},
         Command.MOVE_OR_ATTACK_SE: {'msg': 'key', "keycode": -1003},
         Command.MOVE_OR_ATTACK_NE: {'msg': 'key', "keycode": -1009},

         # todo figure out message structure for the rest of the commands and add them here

         Command.TRAVEL_STAIRCASE_UP: {'text': '<', 'msg': 'input'},
         Command.TRAVEL_STAIRCASE_DOWN: {'text': '<', 'msg': 'input'},
         Command.RESPOND_YES_TO_PROMPT: {'text': 'Y', 'msg': 'input'},
         Command.RESPOND_NO_TO_PROMPT: {'text': 'N', 'msg': 'input'},
         Command.CLEAR_GAME_TEXT_MESSAGES: {'text': '\r', 'msg': 'input'},
         Command.QUAFF: {'text': 'q', 'msg': 'input'},
         Command.EAT: {'text': 'e', 'msg': 'input'},
         Command.PICKUP_ITEM: {'text': 'g', 'msg': 'input'},
         Command.REST_AND_LONG_WAIT: {'text': '5', 'msg': 'input'},
         Command.AUTO_EXPLORE: {'text': 'o', 'msg': 'input'},
         Command.AUTO_FIGHT: {'msg': 'key', 'keycode': 9},
         Command.SHOW_ABILITIES_AND_MUTATIONS: {'text': 'a', 'msg': 'input'},
         Command.SHOW_INVENTORY_LIST: {'text': 'i', 'msg': 'input'},
         Command.EXIT_MENU: {'msg': 'key', 'keycode': 27},
         Command.SHOW_PREVIOUS_GAME_MESSAGES: {'msg': 'key', 'keycode': 16}}

    @staticmethod
    def get_execution_repr(self, command: Command):
        """
        Given a command, return the data that can be sent directly to the game to execute the command.
        :return: a message data structure that can be sent directly to the game to execute the command.
        """

        return Action.command_to_msg[command]


