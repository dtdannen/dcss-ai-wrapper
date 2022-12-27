from enum import Enum
from dcss.state.menu import Menu
import string

from loguru import logger



class MenuChoice(Enum):
    """
    Menu choices are always a lower or upper case letter
    """
    NONE = -1
    LOWER_A = 0
    LOWER_B = 1
    LOWER_C = 2
    LOWER_D = 3
    LOWER_E = 4
    LOWER_F = 5
    LOWER_G = 6
    LOWER_H = 7
    LOWER_I = 8
    LOWER_J = 9
    LOWER_K = 10
    LOWER_L = 11
    LOWER_M = 12
    LOWER_N = 13
    LOWER_O = 14
    LOWER_P = 15
    LOWER_Q = 16
    LOWER_R = 17
    LOWER_S = 18
    LOWER_T = 19
    LOWER_U = 20
    LOWER_V = 21
    LOWER_W = 22
    LOWER_X = 23
    LOWER_Y = 24
    LOWER_Z = 25
    UPPER_A = 26
    UPPER_B = 27
    UPPER_C = 28
    UPPER_D = 29
    UPPER_E = 30
    UPPER_F = 31
    UPPER_G = 32
    UPPER_H = 33
    UPPER_I = 34
    UPPER_J = 35
    UPPER_K = 36
    UPPER_L = 37
    UPPER_M = 38
    UPPER_N = 39
    UPPER_O = 40
    UPPER_P = 41
    UPPER_Q = 42
    UPPER_R = 43
    UPPER_S = 44
    UPPER_T = 45
    UPPER_U = 46
    UPPER_V = 47
    UPPER_W = 48
    UPPER_X = 49
    UPPER_Y = 50
    UPPER_Z = 51
    ZERO = 52
    ONE = 53
    TWO = 54
    THREE = 55
    FOUR = 56
    FIVE = 57
    SIX = 58
    SEVEN = 59
    EIGHT = 60
    NINE = 61
    ASTERISK = 62
    EXCLAMATION_POINT = 63
    FORWARD_SLASH = 64
    QUESTION_MARK = 65
    LESS_THAN = 66
    GREATER_THAN = 67
    ENTER = 68
    PERIOD = 69
    DASH = 70
    CARAT = 71
    TAB = 72
    BACKSLASH = 73
    UNDERSCORE = 74
    ESCAPE = 75


class MenuChoiceMapping:

    # the order of letters and symbols in this string should match the order of MenuChoice enum options
    dcss_menu_chars = list(string.ascii_lowercase + string.ascii_uppercase + '0123456789' + '*!/?<>\r.-^\t\\_\x1b')

    menus_to_choices = {Menu.ATTRIBUTE_INCREASE_TEXT_MENU: [MenuChoice.UPPER_S, MenuChoice.UPPER_I, MenuChoice.UPPER_D],
                        Menu.WALK_INTO_TELEPORT_TRAP_TEXT_MENU: [MenuChoice.UPPER_Y, MenuChoice.UPPER_N],
                        Menu.EXAMINE_MAP_MENU: [MenuChoice.GREATER_THAN, MenuChoice.LESS_THAN, MenuChoice.ENTER,
                                                MenuChoice.CARAT, MenuChoice.TAB, MenuChoice.BACKSLASH,
                                                MenuChoice.UNDERSCORE, MenuChoice.UPPER_I, MenuChoice.UPPER_O,
                                                MenuChoice.ESCAPE
                                                ],
                        Menu.ABILITY_MENU: []}

    @staticmethod
    def get_menu_letter_to_menu_choice():
        return {x:MenuChoice(MenuChoiceMapping.dcss_menu_chars.index(x)) for x in MenuChoiceMapping.dcss_menu_chars}

    @staticmethod
    def get_menu_choice_from_letter(letter):
        return MenuChoiceMapping.get_menu_letter_to_menu_choice()[letter]

    @staticmethod
    def get_menu_choice_from_item_menu_raw_str(raw_str):
        """
        Individual inventory item menus have actoins at the bottom that look like this (example is a scroll):

            '(=)adjust, (r)ead, (d)rop, or (i)nscribe.'

        This function takes one of these actions, '(r)ead' and returns the appropriate MenuChoice enum, which would be

            MenuChoice.LOWER_R in this example
        """

        raw_str.strip().replace(".","")

        IGNORE_LIST = ['(=)adjust', '(i)nscribe', '(s)kill']

        if '(r)ead' in raw_str:
            return MenuChoice.LOWER_R
        elif '(d)rop' in raw_str:
            return MenuChoice.LOWER_D
        elif '(u)nwield' in raw_str:
            return MenuChoice.LOWER_U
        elif '(w)ield' in raw_str:
            return MenuChoice.LOWER_W
        else:
            for we_should_ignore in IGNORE_LIST:
                if we_should_ignore in raw_str:
                    return MenuChoice.NONE

            logger.critical("MISSING logic to handle item action: {}\n************** Please submit a git issue **************\n\t-Dustin".format(raw_str))

            raise Exception("MISSING LOGIC TO PARSE ITEM ACTION {}".format(raw_str))

    @staticmethod
    def add_menu_choices_for_individual_item_menu(menu: Menu, choices: list):

        # first filter out any NONE choices
        actual_choices = []
        for choice in choices:
            if choice != MenuChoice.NONE:
                actual_choices.append(choice)

        if len(actual_choices) > 0:
            if menu not in MenuChoiceMapping.menus_to_choices.keys():
                MenuChoiceMapping.menus_to_choices[menu] = actual_choices


    @staticmethod
    def add_ability_menu_choice(letter):
        current_choices = MenuChoiceMapping.menus_to_choices[Menu.ABILITY_MENU]
        choice = MenuChoiceMapping.get_menu_choice_from_letter(letter)
        if choice not in current_choices:
            MenuChoiceMapping.menus_to_choices[Menu.ABILITY_MENU].append(choice)
            logger.info("Added ability menu choice {}".format(choice))
