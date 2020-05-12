from gamestate import GameState
from actions import Command, Action
import random


class Agent:
    def __init__(self):
        pass

    def get_game_mode_setup_actions(self):
        raise NotImplementedError()

    def get_action(self, gamestate: GameState):
        raise NotImplementedError()


class SimpleRandomAgent(Agent):
    """
    Agent that takes random cardinal actions to move/attack.
    """
    def do_sprint(self):
        # select sprint and character build
        return [{'msg': 'key', 'keycode': ord('a')},
                {'msg': 'key', 'keycode': ord('b')},
                {'msg': 'key', 'keycode': ord('h')},
                {'msg': 'key', 'keycode': ord('b')}
                ]

    def do_dungeon(self):
        # select dungeon and character build
        return [{'msg': 'key', 'keycode': ord('b')},
                {'msg': 'key', 'keycode': ord('h')},
                {'msg': 'key', 'keycode': ord('b')},
                ]

    def get_game_mode_setup_actions(self):
        return self.do_dungeon()

    def get_action(self, gamestate):
        simple_commands = [Command.MOVE_OR_ATTACK_N,
                           Command.MOVE_OR_ATTACK_S,
                           Command.MOVE_OR_ATTACK_E,
                           Command.MOVE_OR_ATTACK_W,
                           Command.MOVE_OR_ATTACK_NE,
                           Command.MOVE_OR_ATTACK_NW,
                           Command.MOVE_OR_ATTACK_SW,
                           Command.MOVE_OR_ATTACK_SE]
        return random.choice(simple_commands)


class TestAllCommandsAgent(Agent):
    """
    Agent that serves to test all commands are working. Cycles through commands in actions.Command enum.
    """

    def __init__(self):
        super().__init__()
        self.next_command_id = 1

    def do_dungeon(self):
        # select dungeon and character build
        return [{'msg': 'key', 'keycode': ord('b')},
                {'msg': 'key', 'keycode': ord('h')},
                {'msg': 'key', 'keycode': ord('b')},
                ]

    def get_game_mode_setup_actions(self):
        return self.do_dungeon()

    def get_action(self, gamestate):

        problematic_actions = [Command.REST_AND_LONG_WAIT,  # some kind of message delay issue
                               Command.WAIT_1_TURN,  # some kind of message delay issue
                               Command.FIND_ITEMS,  # gets stuck on a prompt
                               ]

        try:
            next_command = Command(self.next_command_id)
        except IndexError:
            self.next_command_id = 1
            next_command = Command(self.next_command_id)

        self.next_command_id+=1

        #  skip any known problematic actions for now
        while next_command in problematic_actions:
            next_command = self.get_action(gamestate)

        return next_command

class FastDownwardPlanningAgent(Agent):
    """
    Agent that uses fast downward to solve planning problems to explore a floor. Ignores monsters.
    """

    pddl_domain_file = ""

    def __init__(self):
        super().__init__()
        self.next_command_id = 1
        self.plan = []

    def do_dungeon(self):
        # select dungeon and character build
        return [{'msg': 'key', 'keycode': ord('b')},
                {'msg': 'key', 'keycode': ord('h')},
                {'msg': 'key', 'keycode': ord('b')},
                ]

    def get_game_mode_setup_actions(self):
        return self.do_dungeon()

    def get_plan_from_fast_downward(self, pddl_state, pddl_domain_file):
        pass

    def get_action(self, gamestate: GameState):
        pass

