try:
    import msvcrt
except:
    pass

from dcss.actions.command import Command
from dcss.agent.agent import Agent
from states.gamestate import GameState


class HumanInterfaceAgentDataTracking(Agent):

    def __init__(self):
        super().__init__()
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

    def get_action(self, gamestate):
        gameturn = gamestate.get_current_game_turn()
        num_facts = len(gamestate.get_all_pddl_facts())
        self.gameturns.append(gameturn)
        self.print_all_items_near_player(gamestate)
        self.num_game_facts.append(num_facts)
        #print("about to plot {}, {}".format(gameturn, num_facts))
        #plt.plot(self.gameturns, self.num_game_facts)
        #plt.draw()
        #plt.pause(0.001)

        # linux solution:
        #next_action = readchar.readchar()

        # windows solution
        next_action = None
        while not next_action:
            try:
                next_action = msvcrt.getch().decode()
            except:
                print("Sorry, couldn't decode that keypress, try again?")
        next_action_command = self.get_command_from_human_keypress(next_action)
        print("Got next_action {} and command is {}".format(next_action, next_action_command))
        return next_action_command

    def print_all_items_near_player(self, gamestate: GameState, r=1):
        cells = gamestate.get_cell_map().get_radius_around_agent_cells(r=r)
        for cell in cells: # type: Cell
            for pddl_fact in cell.get_pddl_facts():
                print("{}".format(pddl_fact))

    def get_command_from_human_keypress(self, keypress):
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
            '.': Command.WAIT_1_TURN,

        }

        return keypress_to_command[keypress]