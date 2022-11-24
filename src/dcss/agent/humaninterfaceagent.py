import sys
from dcss.actions.command import Command
from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action
from dcss.actions.menuchoice import MenuChoice
from dcss.state.menu import Menu

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig

import logging
logging.basicConfig(level=logging.WARNING)

# just a little convenience step - this is used to prevent asking the player for an action when an old game is about
# to be deleted and a new game will be started
STILL_NEED_TO_RESTART = False

if sys.platform == 'win32':
    import msvcrt
    getch = msvcrt.getch
    getche = msvcrt.getche
else:
    import sys
    import termios
    def __gen_ch_getter(echo):
        def __fun():
            fd = sys.stdin.fileno()
            oldattr = termios.tcgetattr(fd)
            newattr = oldattr[:]
            try:
                if echo:
                    # disable ctrl character printing, otherwise, backspace will be printed as "^?"
                    lflag = ~(termios.ICANON | termios.ECHOCTL)
                else:
                    lflag = ~(termios.ICANON | termios.ECHO)
                newattr[3] &= lflag
                termios.tcsetattr(fd, termios.TCSADRAIN, newattr)
                ch = sys.stdin.read(1)
                if echo and ord(ch) == 127: # backspace
                    # emulate backspace erasing
                    # https://stackoverflow.com/a/47962872/404271
                    sys.stdout.write('\b \b')
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, oldattr)
            return ch
        return __fun
    getch = __gen_ch_getter(False)
    getche = __gen_ch_getter(True)


class HumanInterfaceBaseAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.gamestate = None
        #plt.axis([-50, 50, 0, 10000])
        #plt.ion()
        #plt.show()

        #self.fig = plt.figure()
        #self.ax1 = self.fig.add_subplot(1,1,1)

        self.gameturns = []
        self.num_game_facts = []

        self.state_facts_count_data = {}  # key is game turn, val is len(state_facts)
        self.number_of_monsters_data = {}  # key is game turn, val is number of monsters
        self.number_of_items_data = {}  # key is game turn, val is number of items seen in the game so far
        self.number_of_cells_data = {}  # key is game turn, val is number of cells seen in the game so far

    def get_action(self, gamestate: GameState):
        self.gamestate = gamestate
        #self.print_player_stats_vector(verbose=True)
        gameturn = gamestate.get_current_game_turn()
        num_facts = len(gamestate.all_pddl_facts())
        self.gameturns.append(gameturn)
        #self.print_all_items_near_player(gamestate)
        self.num_game_facts.append(num_facts)
        #print("about to plot {}, {}".format(gameturn, num_facts))
        #plt.plot(self.gameturns, self.num_game_facts)
        #plt.draw()
        #plt.pause(0.001)

        # linux solution:
        #next_action = readchar.readchar()

        # windows solution
        #next_action = None

        # convenience hack to prevent the user from an extra, meaningless keypress before old game is destroyed
        global STILL_NEED_TO_RESTART
        if STILL_NEED_TO_RESTART:
            STILL_NEED_TO_RESTART = False
            return Command.WAIT_1_TURN # arbitrary, just send any command... this is last command before destroying game
        else:
            self.print_current_menu()
            print("Waiting for your next keypress, human")
            next_action = getch()
            #next_action = input("Waiting for your next keypress, human")
            # while not next_action:
            #     try:
            #         next_action = msvcrt.getch().decode()
            #     except:
            #         print("Sorry, couldn't decode that keypress, try again?")
            next_action_command = self.get_command_from_human_keypress(next_action)
            #print("Got next_action {} and command is {}".format(next_action, next_action_command))
            return next_action_command

    def print_all_items_near_player(self, gamestate: GameState, r=1):
        cells = gamestate.get_cell_map().get_radius_around_agent_cells(r=r)
        for cell in cells: # type: Cell
            for pddl_fact in cell.get_pddl_facts():
                print("{}".format(pddl_fact))

    def print_player_stats_vector(self, verbose=False):
        """
            Print the player stats vector
        """
        player_stats_vector = self.gamestate.get_player_stats_vector(verbose=verbose)
        print(player_stats_vector)
        print("Player stats vector has length {}".format(len(player_stats_vector)))

    def print_current_menu(self):
        """
            Print the menu that the API thinks is currently true
        """

        print("MENU: {}".format(self.gamestate.get_current_menu()))

    def get_command_from_human_keypress(self, keypress):
        """
        Return the command that matches the keypress from the user
        """
        keypress_to_command_no_menu = {
            '1': Command.MOVE_OR_ATTACK_SW,
            'b': Command.MOVE_OR_ATTACK_SW,
            '2': Command.MOVE_OR_ATTACK_S,
            'j': Command.MOVE_OR_ATTACK_S,
            '3': Command.MOVE_OR_ATTACK_SE,
            'n': Command.MOVE_OR_ATTACK_SE,
            '4': Command.MOVE_OR_ATTACK_W,
            'h': Command.MOVE_OR_ATTACK_W,
            '5': Command.REST_AND_LONG_WAIT,
            '6': Command.MOVE_OR_ATTACK_E,
            'l': Command.MOVE_OR_ATTACK_E,
            '7': Command.MOVE_OR_ATTACK_NW,
            'y': Command.MOVE_OR_ATTACK_NW,
            '8': Command.MOVE_OR_ATTACK_N,
            'k': Command.MOVE_OR_ATTACK_N,
            '9': Command.MOVE_OR_ATTACK_NE,
            'u': Command.MOVE_OR_ATTACK_NE,
            'o': Command.AUTO_EXPLORE,
            '\t': Command.AUTO_FIGHT,
            'i': Command.SHOW_INVENTORY_LIST,
            '>': Command.TRAVEL_STAIRCASE_DOWN,
            '<': Command.TRAVEL_STAIRCASE_UP,
            '\r': Command.ENTER_KEY,
            'g': Command.PICKUP_ITEM,
            ',': Command.PICKUP_ITEM,
            '.': Command.WAIT_1_TURN,
            '%': Command.CHARACTER_OVERVIEW,
            '@': Command.DISPLAY_CHARACTER_STATUS,
            'A': Command.SHOW_ABILITIES_AND_MUTATIONS,
            '\x1b': Command.EXIT_MENU,
            'a': Command.USE_SPECIAL_ABILITY,
            'q': Command.QUAFF,
            'I': Command.LIST_ALL_SPELLS,
            'm': Command.SHOW_SKILL_SCREEN,
            'x': Command.EXAMINE_SURROUNDINGS_AND_TARGETS,
            ';': Command.EXAMINE_CURRENT_TILE_PICKUP_PART_OF_SINGLE_STACK,
        }

        if self.gamestate.get_current_menu() is Menu.NO_MENU:
            return keypress_to_command_no_menu[keypress]
        elif keypress in Action.dcss_menu_chars:
            dcss_menu_char_i = Action.dcss_menu_chars.index(keypress)
            menuchoice = MenuChoice(dcss_menu_char_i)
            return menuchoice
        else:
            #print("Got keypress {} and current Menu is {}".format(keypress, self.gamestate.get_current_menu()))
            return Command.EXIT_MENU


if __name__ == "__main__":
    my_config = WebserverConfig

    # set game mode to Tutorial #1
    my_config.game_id = 'dcss-web-trunk'
    my_config.always_start_new_game = True
    my_config.auto_start_new_game = True
    my_config.species = 'Vampire'
    my_config.background = 'Necromancer'
    my_config.delay = 0.1

    if my_config.always_start_new_game:
        STILL_NEED_TO_RESTART = True

    # create game
    game = WebSockGame(config=my_config, agent_class=HumanInterfaceBaseAgent)
    game.run()