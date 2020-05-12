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
    LONG_WALK_SW = 15
    LONG_WALK_S = 16
    LONG_WALK_SE = 17
    LONG_WALK_W = 18
    LONG_WALK_E = 19
    LONG_WALK_NW = 20
    LONG_WALK_N = 21
    LONG_WALK_NE = 22

    ATTACK_WITHOUT_MOVE_SW = 15
    ATTACK_WITHOUT_MOVE_S = 16
    ATTACK_WITHOUT_MOVE_SE = 17
    ATTACK_WITHOUT_MOVE_W = 18
    ATTACK_WITHOUT_MOVE_E = 19
    ATTACK_WITHOUT_MOVE_NW = 20
    ATTACK_WITHOUT_MOVE_N = 21
    ATTACK_WITHOUT_MOVE_NE = 22

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
    SELECT_ITEM_TO_EVOKE = 34
    MEMORISE = 34
    COUNT_GOLD = 35

    #  Other gameplay actions
    USE_SPECIAL_ABILITY = 36
    CAST_SPELL_ABORT_WITHOUT_TARGETS = 37
    CAST_SPELL_NO_MATTER_WHAT = 38
    LIST_ALL_SPELLS = 39
    TELL_ALLIES = 40
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
    SET_TRAVEL_SPEED_TO_CLOSEST_ALLY = 68

    #  Item Interaction (Inventory)
    SHOW_INVENTORY_LIST = 69
    INSCRIBE_ITEM = 70

    # Item Interaction (floor)
    PICKUP_ITEM = 73
    SELECT_ITEM_FOR_PICKUP = 73
    DROP_ITEM = 74
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

    command_to_msg = {
        Command.MOVE_OR_ATTACK_N: {'msg': 'key', "keycode": -254},
        Command.MOVE_OR_ATTACK_S: {'msg': 'key', "keycode": -253},
        Command.MOVE_OR_ATTACK_E: {'msg': 'key', "keycode": -251},
        Command.MOVE_OR_ATTACK_W: {'msg': 'key', "keycode": -252},
        Command.MOVE_OR_ATTACK_NW: {'msg': 'key', "keycode": -249},
        Command.MOVE_OR_ATTACK_SW: {'msg': 'key', "keycode": -248},
        Command.MOVE_OR_ATTACK_SE: {'msg': 'key', "keycode": -245},
        Command.MOVE_OR_ATTACK_NE: {'msg': 'key', "keycode": -246},

        Command.REST_AND_LONG_WAIT: {'text': '5', 'msg': 'input'},
        Command.WAIT_1_TURN: {'text': '.', 'msg': 'input'},

        Command.AUTO_EXPLORE: {'text': 'o', 'msg': 'input'},
        Command.INTERLEVEL_TRAVEL: {'text': 'G', 'msg': 'input'},
        Command.FIND_ITEMS: {'msg': 'key', "keycode": 6},
         #  Todo - see github issue 9
         # Command.SET_WAYPOINT: {...}

        Command.LONG_WALK_N: {'msg': 'key', "keycode": -243},
        Command.LONG_WALK_S: {'msg': 'key', "keycode": -242},
        Command.LONG_WALK_E: {'msg': 'key', "keycode": -240},
        Command.LONG_WALK_W: {'msg': 'key', "keycode": -241},
        Command.LONG_WALK_NW: {'msg': 'key', "keycode": -238},
        Command.LONG_WALK_NE: {'msg': 'key', "keycode": -235},
        Command.LONG_WALK_SW: {'msg': 'key', "keycode": -237},
        Command.LONG_WALK_SE: {'msg': 'key', "keycode": -234},

        Command.ATTACK_WITHOUT_MOVE_N: {'msg': 'key', "keycode": -232},
        Command.ATTACK_WITHOUT_MOVE_S: {'msg': 'key', "keycode": -231},
        Command.ATTACK_WITHOUT_MOVE_E: {'msg': 'key', "keycode": -229},
        Command.ATTACK_WITHOUT_MOVE_W: {'msg': 'key', "keycode": -230},
        Command.ATTACK_WITHOUT_MOVE_NW: {'msg': 'key', "keycode": -227},
        Command.ATTACK_WITHOUT_MOVE_SW: {'msg': 'key', "keycode": -226},

         #  Todo - similar issue to github issue 9
         # Command.ATTACK_WITHOUT_MOVE_NE: {'msg': 'key', "keycode": },

         #  Todo - similar issue to github issue 9
         # Command.ATTACK_WITHOUT_MOVE_SE: {'msg': 'key', "keycode": },

        Command.AUTO_FIGHT: {'msg': 'key', 'keycode': 9},

         #  Todo - similar issue to github issue 9
         # Command.AUTO_FIGHT_WITHOUT_MOVE:

        Command.WIELD_HAND_WEAPON: {'text': 'w', 'msg': 'input'},
        Command.QUIVER_MISSILE: {'text': 'Q', 'msg': 'input'},
        Command.FIRE_MISSILE: {'text': 'f', 'msg': 'input'},
        Command.SELECT_MISSILE_AND_FIRE: {'text': 'F', 'msg': 'input'},
        Command.CYCLE_MISSILE_FORWARD: {'text': '(', 'msg': 'input'},
        Command.CYCLE_MISSILE_BACKWARD: {'text': ')', 'msg': 'input'},
        Command.WEAR_ARMOUR: {'text': 'W', 'msg': 'input'},
        Command.TAKE_OFF_ARMOUR: {'text': 'T', 'msg': 'input'},
        Command.CHOP_CORPSE: {'text': 'c', 'msg': 'input'},
        Command.EAT: {'text': 'e', 'msg': 'input'},
        Command.QUAFF: {'text': 'q', 'msg': 'input'},
        Command.READ: {'text': 'r', 'msg': 'input'},
        Command.PUT_ON_JEWELLERY: {'text': 'P', 'msg': 'input'},
        Command.REMOVE_JEWELLERY: {'text': 'R', 'msg': 'input'},
        Command.EVOKE: {'text': 'v', 'msg': 'input'},
        Command.SELECT_ITEM_TO_EVOKE: {'text': 'V', 'msg': 'input'},
        Command.MEMORISE: {'text': 'M', 'msg': 'input'},
        Command.COUNT_GOLD: {'text': '$', 'msg': 'input'},

        Command.USE_SPECIAL_ABILITY: {'text': 'a', 'msg': 'input'},
        Command.CAST_SPELL_ABORT_WITHOUT_TARGETS: {'text': 'z', 'msg': 'input'},
        Command.CAST_SPELL_NO_MATTER_WHAT: {'text': 'Z', 'msg': 'input'},
        Command.LIST_ALL_SPELLS: {'text': 'I', 'msg': 'input'},
        Command.TELL_ALLIES: {'text': 'I', 'msg': 'input'},
        Command.REDO_PREVIOUS_COMMAND: {'text': '`', 'msg': 'input'},

        Command.SAVE_GAME_AND_EXIT: {'text': 'S', 'msg': 'input'},
        Command.SAVE_AND_EXIT_WITHOUT_QUERY: {'msg': 'key', "keycode": 19},
        Command.ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME: {'msg': 'key', "keycode": 17},

        Command.DISPLAY_CHARACTER_STATUS: {'text': '@', 'msg': 'input'},
        Command.SHOW_SKILL_SCREEN: {'text': 'm', 'msg': 'input'},
        Command.CHARACTER_OVERVIEW: {'text': '%', 'msg': 'input'},
        Command.SHOW_RELIGION_SCREEN: {'text': '^', 'msg': 'input'},
        Command.SHOW_ABILITIES_AND_MUTATIONS: {'text': 'A', 'msg': 'input'},
        Command.SHOW_ITEM_KNOWLEDGE: {'text': '\\', 'msg': 'input'},
        Command.SHOW_RUNES_COLLECTED: {'text': '}', 'msg': 'input'},
        Command.DISPLAY_WORN_ARMOUR: {'text': '[', 'msg': 'input'},
        Command.DISPLAY_WORN_JEWELLERY: {'text': '\"', 'msg': 'input'},
        Command.DISPLAY_EXPERIENCE_INFO: {'text': 'E', 'msg': 'input'},

        Command.OPEN_DOOR: {'text': 'O', 'msg': 'input'},
        Command.CLOSE_DOOR: {'text': 'C', 'msg': 'input'},
        Command.TRAVEL_STAIRCASE_UP: {'text': '<', 'msg': 'input'},
        Command.TRAVEL_STAIRCASE_DOWN: {'text': '<', 'msg': 'input'},
        Command.EXAMINE_CURRENT_TILE_PICKUP_PART_OF_SINGLE_STACK: {'text': ';', 'msg': 'input'},
        Command.EXAMINE_SURROUNDINGS_AND_TARGETS: {'text': 'x', 'msg': 'input'},
        Command.EXAMINE_LEVEL_MAP: {'text': 'X', 'msg': 'input'},
        Command.LIST_MONSTERS_ITEMS_FEATURES_IN_VIEW: {'msg': 'key', "keycode": 24},
        Command.TOGGLE_VIEW_LAYERS: {'text': '|', 'msg': 'input'},
        Command.SHOW_DUNGEON_OVERVIEW: {'msg': 'key', "keycode": 15},
        Command.TOGGLE_AUTO_PICKUP: {'msg': 'key', "keycode": 1},
        Command.SET_TRAVEL_SPEED_TO_CLOSEST_ALLY: {'msg': 'key', "keycode": 5},

        Command.SHOW_INVENTORY_LIST: {'text': 'i', 'msg': 'input'},
        Command.INSCRIBE_ITEM: {'msg': 'input', 'data': [123]},

        Command.PICKUP_ITEM: {'text': 'g', 'msg': 'input'},
        Command.SELECT_ITEM_FOR_PICKUP: {'text': ',', 'msg': 'input'},
        Command.DROP_ITEM: {'text': 'd', 'msg': 'input'},
        Command.DROP_LAST_ITEMS_PICKED_UP: {'text': 'D', 'msg': 'input'},

        Command.EXIT_MENU: {'msg': 'key', 'keycode': 27},
        Command.SHOW_PREVIOUS_GAME_MESSAGES: {'msg': 'key', 'keycode': 16},
        Command.RESPOND_YES_TO_PROMPT: {'text': 'Y', 'msg': 'input'},
        Command.RESPOND_NO_TO_PROMPT: {'text': 'N', 'msg': 'input'},
        Command.CLEAR_GAME_TEXT_MESSAGES: {'text': '\r', 'msg': 'input'},
        }

    @staticmethod
    def get_execution_repr(command: Command):
        """
        Given a command, return the data that can be sent directly to the game to execute the command.
        :return: a message data structure that can be sent directly to the game to execute the command.
        """
        print("Command is {}".format(command))
        return Action.command_to_msg[command]


