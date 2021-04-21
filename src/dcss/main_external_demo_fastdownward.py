from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action, Command
from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig
import os, subprocess, platform
import random


class FastdownwardAgent(BaseAgent):
    pddl_domain_file = ""

    def __init__(self):
        super().__init__()
        self.current_game_state = None
        self.next_command_id = 1
        self.planner_filename = "../../downward/fast-downward.py"
        self.plan_domain_filename = "../../models/fastdownward_simple.pddl"
        self.plan_current_pddl_state_filename = "../../models/fdtempfiles/state.pddl"
        self.plan_result_filename = "../../models/fdtempfiles/dcss_plan.sas"
        self.plan = []
        self.actions_taken_so_far = 0
        self.current_goal = None
        self.previous_goal = None
        self.previous_goal_type = None
        self.new_goal = None
        self.new_goal_type = None
        self.current_goal_type = None
        self.blue_goals_remaining = [1, 2, 3, 4]
        self.actions_to_score = {}  # score is equal to the number of goals reached so far

    def get_action(self, gamestate: GameState):
        self.current_game_state = gamestate

        self.actions_to_score[self.actions_taken_so_far] = self.blue_goals_remaining[0]

        # if we've reached a blue goal, remove it from our goals
        current_blue_tile_goal_i = self.blue_goals_remaining[0]
        current_blue_tile_goal = self.get_blue_tile_goal(current_blue_tile_goal_i)
        if current_blue_tile_goal in self.current_game_state.all_pddl_facts():
            print("Reached blue tile goal {} of {}".format(current_blue_tile_goal_i, current_blue_tile_goal))
            self.blue_goals_remaining.pop(0)  # move on to the next goal
            if len(self.blue_goals_remaining) > 0:
                current_blue_tile_goal_i = self.blue_goals_remaining[0]
                current_blue_tile_goal = self.get_blue_tile_goal(current_blue_tile_goal_i)
            else:
                # we're finished, just execute a random action until we reset
                self.write_data_to_file()
                return self.get_random_simple_action()

        # if we have a plan, execute next action in plan
        if self.plan and len(self.plan) > 0:
            next_action = self.plan.pop(0)
            print("About to send next action of plan which is {}".format(next_action))
            self.actions_taken_so_far += 1
            return next_action

        # if we need a plan, try planning to reach the next blue tile goal
        print("Calling the planner with the goals={}".format([current_blue_tile_goal]))
        self.plan = self.get_plan_from_fast_downward(goals=[current_blue_tile_goal])

        if len(self.plan) == 0:
            # we could not generate a plan to reach the current goal, so explore instead
            explore_goal = self.get_random_nonvisited_nonwall_playerat_goal()
            print("Calling the planner with explore goals={}".format([explore_goal]))
            self.plan = self.get_plan_from_fast_downward(goals=[explore_goal])

        if len(self.plan) == 0:
            raise Exception("Could not generate a plan to explore or reach a blue tile goal")
        else:
            next_action = self.plan.pop(0)
            self.actions_taken_so_far += 1
            return next_action

    def get_random_nonvisited_nonwall_playerat_goal(self):
        cells_not_visited = []
        cells_visited = []
        closed_door_cells = []
        for cell in self.current_game_state.get_cell_map().get_xy_to_cells_dict().values():
            if cell.has_player_visited:
                cells_visited.append(cell)
            elif not cell.has_wall and not cell.has_player and not cell.has_statue and not cell.has_lava and not cell.has_plant and not cell.has_tree and cell.g:
                # print("added {} as an available cell, it's g val is {}".format(cell.get_pddl_name(), cell.g))
                cells_not_visited.append(cell)
            else:
                pass

        goal_cell = random.choice(cells_not_visited)

        goal_str = "(playerat {})".format(goal_cell.get_pddl_name())
        #print("Returning goal str of {}".format(goal_str))
        return goal_str

    def get_plan_from_fast_downward(self, goals):
        # step 1: write state output so fastdownward can read it in
        if self.current_game_state:
            self.current_game_state.write_pddl_current_state_to_file(filename=self.plan_current_pddl_state_filename,
                                                                     goals=goals)
        else:
            print("WARNING current game state is null when trying to call fast downward planner")
            return []

        # step 2: run fastdownward
        # fast_downward_process_call = ["./FastDownward/fast-downward.py",
        #                               "--plan-file {}".format(self.plan_result_filename),
        #                               "{}".format(self.plan_domain_filename),
        #                               "{}".format(self.plan_current_pddl_state_filename),
        #                               "--search \"astar(lmcut())\""]
        # This is used for linux
        fast_downward_process_call = [
            self.planner_filename + " --plan-file {} {} {} --search \"astar(lmcut())\"".format(
                self.plan_result_filename,
                self.plan_domain_filename,
                self.plan_current_pddl_state_filename), ]
        # This is used for windows
        fast_downward_system_call = "python " + self.planner_filename + " --plan-file {} {} {} --search \"astar(lmcut())\" {}".format(
            self.plan_result_filename,
            self.plan_domain_filename,
            self.plan_current_pddl_state_filename,
            "> NUL")  # this last line is to remove output from showing up in the terminal, feel free to remove this if debugging

        # print("About to call fastdownward like:")
        print(str(fast_downward_system_call))
        # print("platform is {}".format(platform.system()))
        if platform.system() == 'Windows':
            os.system(fast_downward_system_call)
        elif platform.system() == 'Linux':
            subprocess.run(fast_downward_process_call, shell=True, stdout=subprocess.DEVNULL)

        # step 3: read in the resulting plan
        plan = []
        try:
            with open(self.plan_result_filename, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if ';' not in line:
                        if line[0] == '(':
                            pddl_action_name = line.split()[0][1:]
                            command_name = pddl_action_name.upper()
                            plan.append(Command[command_name])
                    else:
                        # we have a comment, ignore
                        pass
        except FileNotFoundError:
            print("Plan could not be generated...")
            return []
        except:
            print("Unknown error preventing plan from being generated")
            return

        # for ps in plan:
        #    print("Plan step: {}".format(ps))

        return plan

    def write_data_to_file(self):
        now_str = datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
        data_filename = 'data/'+now_str+".csv"
        csv_str = "action,score\n"
        for a,s in self.actions_to_score.items():
            csv_str += "{},{}\n".format(a,s)

        with open(data_filename, 'w') as f:
            f.write(csv_str)

    def get_blue_tile_goal(self, i):
        blue_tile_goals = {1: '(playerat cellx7y0)',
                           2: '(playerat cellx14y7)',
                           3: '(playerat cellx19y12)',
                           4: '(playerat cellx19y2)'}

        return blue_tile_goals[i]


    def get_random_simple_action(self):
        simple_commands = [Command.MOVE_OR_ATTACK_N,
                           Command.MOVE_OR_ATTACK_S,
                           Command.MOVE_OR_ATTACK_E,
                           Command.MOVE_OR_ATTACK_W,
                           Command.MOVE_OR_ATTACK_NE,
                           Command.MOVE_OR_ATTACK_NW,
                           Command.MOVE_OR_ATTACK_SW,
                           Command.MOVE_OR_ATTACK_SE]
        return random.choice(simple_commands)

    def requesting_start_new_game(self):
        return len(self.blue_goals_remaining) == 0


if __name__ == "__main__":
    my_config = WebserverConfig

    # set game mode to Tutorial #1
    my_config.game_id = 'tut-web-trunk'
    my_config.tutorial_number = 1

    # create game
    game = WebSockGame(config=my_config, agent_class=FastdownwardAgent)
    game.run()

