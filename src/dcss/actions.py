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
    MOVE_OR_ATTACK_E = 5
    MOVE_OR_ATTACK_NW = 6
    MOVE_OR_ATTACK_N = 7
    MOVE_OR_ATTACK_NE = 8

    #  Rest
    REST_AND_LONG_WAIT = 9
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

    ATTACK_WITHOUT_MOVE_SW = 23
    ATTACK_WITHOUT_MOVE_S = 24
    ATTACK_WITHOUT_MOVE_SE = 25
    ATTACK_WITHOUT_MOVE_W = 26
    ATTACK_WITHOUT_MOVE_E = 27
    ATTACK_WITHOUT_MOVE_NW = 28
    ATTACK_WITHOUT_MOVE_N = 29
    ATTACK_WITHOUT_MOVE_NE = 30

    #  Autofight
    AUTO_FIGHT = 31
    AUTO_FIGHT_WITHOUT_MOVE = 32

    #  Item types (and common commands)
    WIELD_HAND_WEAPON = 33
    QUIVER_MISSILE = 34
    FIRE_MISSILE = 35
    SELECT_MISSILE_AND_FIRE = 36
    CYCLE_MISSILE_FORWARD = 37
    CYCLE_MISSILE_BACKWARD = 38
    WEAR_ARMOUR = 39
    TAKE_OFF_ARMOUR = 40
    CHOP_CORPSE = 41
    EAT = 42  # Note that later versions of crawl do not have an eat action
    READ = 43
    QUAFF = 44
    PUT_ON_JEWELLERY = 45
    REMOVE_JEWELLERY = 46
    EVOKE = 47
    SELECT_ITEM_TO_EVOKE = 48
    MEMORISE = 49
    COUNT_GOLD = 50

    #  Other gameplay actions
    USE_SPECIAL_ABILITY = 51
    CAST_SPELL_ABORT_WITHOUT_TARGETS = 52
    CAST_SPELL_NO_MATTER_WHAT = 53
    LIST_ALL_SPELLS = 54
    TELL_ALLIES = 55
    REDO_PREVIOUS_COMMAND = 56

    #  Game Saving and Quitting
    SAVE_GAME_AND_EXIT = 57
    SAVE_AND_EXIT_WITHOUT_QUERY = 58
    ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME = 59

    #  Player Character Information
    DISPLAY_CHARACTER_STATUS = 60
    SHOW_SKILL_SCREEN = 61
    CHARACTER_OVERVIEW = 62
    SHOW_RELIGION_SCREEN = 63
    SHOW_ABILITIES_AND_MUTATIONS = 64
    SHOW_ITEM_KNOWLEDGE = 65
    SHOW_RUNES_COLLECTED = 66
    DISPLAY_WORN_ARMOUR = 67
    DISPLAY_WORN_JEWELLERY = 68
    DISPLAY_EXPERIENCE_INFO = 69

    #  Dungeon Interaction and Information
    OPEN_DOOR = 70
    CLOSE_DOOR = 71
    TRAVEL_STAIRCASE_DOWN = 72
    TRAVEL_STAIRCASE_UP = 73
    EXAMINE_CURRENT_TILE_PICKUP_PART_OF_SINGLE_STACK = 74
    EXAMINE_SURROUNDINGS_AND_TARGETS = 75
    EXAMINE_LEVEL_MAP = 76
    LIST_MONSTERS_ITEMS_FEATURES_IN_VIEW = 77
    TOGGLE_VIEW_LAYERS = 78
    SHOW_DUNGEON_OVERVIEW = 79
    TOGGLE_AUTO_PICKUP = 80
    SET_TRAVEL_SPEED_TO_CLOSEST_ALLY = 81

    #  Item Interaction (Inventory)
    SHOW_INVENTORY_LIST = 82
    INSCRIBE_ITEM = 83

    # Item Interaction (floor)
    PICKUP_ITEM = 84
    SELECT_ITEM_FOR_PICKUP = 85
    DROP_ITEM = 86
    DROP_LAST_ITEMS_PICKED_UP = 87

    #  Additional Actions
    EXIT_MENU = 88
    SHOW_PREVIOUS_GAME_MESSAGES = 89
    RESPOND_YES_TO_PROMPT = 90
    RESPOND_NO_TO_PROMPT = 91
    ENTER_KEY = 92


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

        Command.REST_AND_LONG_WAIT: {'msg': 'key', 'keycode': ord('5')},
        Command.WAIT_1_TURN: {'msg': 'key', 'keycode': ord('.')},

        Command.AUTO_EXPLORE: {'msg': 'key', 'keycode': ord('o')},
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
        Command.ATTACK_WITHOUT_MOVE_NE: {'msg': 'key', "keycode": -224},
        Command.ATTACK_WITHOUT_MOVE_SE: {'msg': 'key', "keycode": -223},

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
        Command.TRAVEL_STAIRCASE_DOWN: {'text': '>', 'msg': 'input'},
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
        Command.ENTER_KEY: {'text': '\r', 'msg': 'input'},
    }

    @staticmethod
    def get_execution_repr(command: Command):
        """
        Given a command, return the data that can be sent directly to the game to execute the command.
        :return: a message data structure that can be sent directly to the game to execute the command.
        """
        # print("Command is {}".format(command))
        return Action.command_to_msg[command]

    @staticmethod
    def get_command_from_human_keypress(keypress):
        """
        Return the command that matches the keypress from the user
        """
        keypress_to_command = {
            '1': Command.MOVE_OR_ATTACK_SW,
            '2': Command.MOVE_OR_ATTACK_S,
            '3': Command.MOVE_OR_ATTACK_SE,
            '4': Command.MOVE_OR_ATTACK_W,
            '5': Command.REST_AND_LONG_WAIT,
            '6': Command.MOVE_OR_ATTACK_E,
            '7': Command.MOVE_OR_ATTACK_NW,
            '8': Command.MOVE_OR_ATTACK_N,
            '9': Command.MOVE_OR_ATTACK_NE,
            'o': Command.AUTO_EXPLORE,
            '\t': Command.AUTO_FIGHT,
            'i': Command.SHOW_INVENTORY_LIST,
            '>': Command.TRAVEL_STAIRCASE_DOWN,
            '<': Command.TRAVEL_STAIRCASE_UP,
            '\r': Command.ENTER_KEY,
            'g': Command.PICKUP_ITEM,
            ',': Command.PICKUP_ITEM,
            '\x11': Command.ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME,

        }

        return keypress_to_command[keypress]
