from gamestate import GameState
from actions import Command, Action
import subprocess
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

        self.next_command_id += 1

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
        self.current_game_state = None
        self.next_command_id = 1
        self.plan_domain_filename = "models/fastdownwardplanningagent_domain.pddl"
        self.plan_current_pddl_state_filename = "models/fdtempfiles/gamestate.pddl"
        self.plan_result_filename = "models/fdtempfiles/dcss_plan.sas"
        self.plan = []

    def do_dungeon(self):
        # select dungeon and character build
        return [{'msg': 'key', 'keycode': ord('b')},
                {'msg': 'key', 'keycode': ord('h')},
                {'msg': 'key', 'keycode': ord('b')},
                ]

    def get_game_mode_setup_actions(self):
        return self.do_dungeon()

    def get_plan_from_fast_downward(self):
        # step 1: write state output so fastdownward can read it in
        if self.current_game_state:
            self.current_game_state.write_pddl_current_state_to_file(filename=self.plan_current_pddl_state_filename)
        else:
            print("WARNING current game state is null when trying to call fast downward planner")
            return

        # step 2: run fastdownward
        fast_downward_process_call = ["./FastDownward/fast-downward.py",
                                      "--plan-file {}".format(self.plan_result_filename),
                                      "{}".format(self.plan_domain_filename),
                                      "{}".format(self.plan_current_pddl_state_filename),
                                      "--search \"astar(lmcut())\""]
        print("About to call fastdownward like:")
        print(str(fast_downward_process_call))
        subprocess.run(fast_downward_process_call)

        # step 3: read in the resulting plan
        plan_steps = []
        with open(self.plan_result_filename, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if ';' not in line:
                    if line[0] == '(':
                        pddl_action_name = line.split()[0][1:]
                        command_name = pddl_action_name.upper()
                    plan_steps.append(command_name)

                else:
                    # we have a comment, ignore
                    pass
        for ps in plan_steps:
            print("Plan step: {}".format(ps))

    def get_action(self, gamestate: GameState):
        self.current_game_state = gamestate
        self.get_plan_from_fast_downward()

        simple_commands = [Command.MOVE_OR_ATTACK_N,
                           Command.MOVE_OR_ATTACK_S,
                           Command.MOVE_OR_ATTACK_E,
                           Command.MOVE_OR_ATTACK_W,
                           Command.MOVE_OR_ATTACK_NE,
                           Command.MOVE_OR_ATTACK_NW,
                           Command.MOVE_OR_ATTACK_SW,
                           Command.MOVE_OR_ATTACK_SE]
        return random.choice(simple_commands)
