import os
import platform
import random
import subprocess
import glob
import re

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig

from dcss.agent.base import BaseAgent
from dcss.actions.command import Command
from dcss.actions.menuchoice import MenuChoiceMapping
from dcss.state.game import GameState
from dcss.state.menu import Menu
from enum import Enum
import dcss.state.pddl as pddl

import time

import logging


class Goal(Enum):
    EXPLORE = 1
    ATTACK = 2
    RETREAT = 3
    COLLECT_ITEMS = 4
    HEAL = 5


class SimpleGRAgent(BaseAgent):
    """
    Agent that uses fast downward to solve planning problems to explore a floor.
    """

    pddl_domain_file = ""

    def __init__(self):
        super().__init__()
        self.current_game_state = None
        self.next_command_id = 1
        self.pddl_objects = []
        self.pddl_state_facts = []
        self.plan_domain_filename = "models/fastdownward_simple.pddl"
        self._pddl_state_counter = 0
        self._pddl_state_dir = "agent_temp_state"
        self._pddl_state_filename = self.get_pddl_state_filename()
        self.plan_result_filename = "models/fdtempfiles/dcss_plan.sas"
        self.plan = []
        self.actions_taken_so_far = 0
        self.current_goal = None
        self.previous_goal = None
        self.previous_goal_type = None
        self.new_goal = None
        self.new_goal_type = None
        self.current_goal_type = None
        self.num_cells_visited = 0
        self.player_has_seen_stairs_down = {x: False for x in
                                            range(0, 50)}  # key is depth, value is whether seen stairs down

        self.cells_not_visited = {x: set() for x in range(0, 50)}  # key is depth
        self.cells_visited = {x: set() for x in range(0, 50)}  # key is depth
        self.closed_door_cells = {x: set() for x in range(0, 50)}  # key is depth

        self.found_item = None  # if not None, this will be a cell
        self.inventory_full = False

        self.failed_goals = []

        self.time_per_action = []

        self._remove_old_state_files()

    def _remove_old_state_files(self):
        files_removed = 0
        for state_file in glob.glob("{}/state*".format(self._pddl_state_dir)):
            os.remove(state_file)
            files_removed += 1

        logging.info("Removed {} old state files from {}".format(files_removed, self._pddl_state_dir))

    def get_pddl_state_filename(self):
        return "{}/state{}.pddl".format(self._pddl_state_dir, self._pddl_state_counter)

    def process_gamestate_via_cells(self):
        for cell in self.current_game_state.get_cell_map().get_xy_to_cells_dict().values():
            if cell.has_player_visited:
                self.cells_visited[self.current_game_state.player_depth].add(cell)
            elif not cell.has_wall and not cell.has_player and not cell.has_statue and not cell.has_lava and not cell.has_plant and not cell.has_tree and cell.g:
                # print("added {} as an available cell, it's g val is {}".format(cell.get_pddl_name(), cell.g))
                self.cells_not_visited[self.current_game_state.player_depth].add(cell)
            else:
                pass

            if cell.has_closed_door:
                self.closed_door_cells[self.current_game_state.player_depth].add(cell)

            if cell.has_stairs_down:
                self.player_has_seen_stairs_down[self.current_game_state.player_depth] = True
                logging.debug("Setting stairs down to be True for depth {}".format(self.current_game_state.player_depth))

        self.num_cells_visited = len(self.cells_visited[self.current_game_state.player_depth])

    def get_random_nonvisited_nonwall_playerat_goal(self):
        i = 1
        farthest_away_cells = set()
        target_cells = self.cells_not_visited[self.current_game_state.player_depth].copy()
        while len(target_cells) > 1:
            farthest_away_cells = target_cells
            # remove all cells that are i distance away from other visited cells
            new_target_cells = set()
            for potential_cell in target_cells:
                found_close_visited_cell = False
                for visited_cell in self.cells_visited[self.current_game_state.player_depth]:
                    if visited_cell.straight_line_distance(potential_cell) <= i:
                        found_close_visited_cell = True

                if not found_close_visited_cell:
                    new_target_cells.add(potential_cell)

            # print("  i={} with {} target cells".format(i, len(new_target_cells)))
            target_cells = new_target_cells
            i += 1

        # print("Found {} non visited cells {} distance away from player".format(len(farthest_away_cells), i - 1))

        if len(self.closed_door_cells[self.current_game_state.player_depth]) > 1:
            logging.debug("Attempting to choose a closed door as a goal if possible")
            goal_cell = self.closed_door_cells[self.current_game_state.player_depth].pop()
        elif len(farthest_away_cells) > 0:
            goal_cell = farthest_away_cells.pop()
            logging.debug("Visited {} cells - Goal is now {}".format(
                len(self.cells_visited[self.current_game_state.player_depth]), goal_cell.get_pddl_name()))

        else:
            # can't find any cells
            return None

        goal_str = "(playerat {})".format(goal_cell.get_pddl_name())
        # print("Returning goal str of {}".format(goal_str))
        return goal_str

    def get_item_goal(self):
        """
        This picks the first available potion.
        """

        cells_with_item = []
        for f in self.pddl_state_facts:
            if 'hasitem_generic' in f:
                cell_str =


    def get_first_monster_goal(self):
        """
        This picks a the first available monster and chooses that monsters cell to be the goal. In the process of trying to move
        into the monsters cell, the agent should end up attacking the monster, because movement and attacking are the
        same thing (for melee).
        """
        cells_with_monsters = []
        for cell in self.current_game_state.get_cell_map().get_xy_to_cells_dict().values():
            if cell.monster:
                cells_with_monsters.append(cell)

        cells_in_failed_goals = []
        for g in self.failed_goals:
            matches = re.findall('cellx[_]*[0-9]+y[_]*[0-9]+', g)
            for c in matches:
                cells_in_failed_goals.append(c)

        cells_with_monsters = [c for c in cells_with_monsters if c.get_pddl_name() not in cells_in_failed_goals]

        if len(cells_with_monsters) == 0:
            return None

        monster_cell_goal = random.choice(cells_with_monsters)
        monster_goal_str = "(not (hasmonster {} {}))".format(monster_cell_goal.get_pddl_name(), monster_cell_goal.monster.name)
        # print("about to return monster goal: {}".format(monster_goal_str))
        # time.sleep(1)
        return monster_goal_str

    def update_pddl_objs_and_facts(self):
        pddl_objects = []
        pddl_facts = []
        if self.current_game_state:
            pddl_map_objects, pddl_map_facts = self.current_game_state.get_all_map_objects_in_pddl()
            pddl_objects += pddl_map_objects
            pddl_facts += pddl_map_facts

            pddl_facts += self.current_game_state.get_player_stats_pddl()
            pddl_facts += self.current_game_state.get_player_skills_pddl()
            inv_objects, inv_facts = self.current_game_state.get_player_inventory_pddl()
            pddl_objects += inv_objects
            pddl_facts += inv_facts

        self.pddl_state_facts = pddl_facts
        self.pddl_objects = pddl_objects

    def get_plan_from_fast_downward(self, goals):
        # step 1: write state output so fastdownward can read it in
        if self.current_game_state:
            self._pddl_state_counter += 1
            logging.debug("About to write out game state with filename {}".format(self.get_pddl_state_filename()))
            logging.debug("current working directory: {}".format(os.getcwd()))
            with open(self.get_pddl_state_filename(), 'w') as f:
                pddl_str = pddl.get_pddl_problem(objects=self.pddl_objects, init_facts=self.pddl_state_facts, goals=goals,
                                      map_s=self.current_game_state.get_cell_map().draw_cell_map())
                f.write(pddl_str)
            logging.debug("...wrote to file {}".format(self.get_pddl_state_filename()))


        else:
            logging.warning("current game state is null when trying to call fast downward planner")
            time.sleep(1000)

        # step 2: run fastdownward
        # fast_downward_process_call = ["./FastDownward/fast-downward.py",
        #                               "--plan-file {}".format(self.plan_result_filename),
        #                               "{}".format(self.plan_domain_filename),
        #                               "{}".format(self.plan_current_pddl_state_filename),
        #                               "--search \"astar(lmcut())\""]
        # This is used for linux
        fast_downward_process_call = [
            "./FastDownward/fast-downward.py --plan-file {} {} {} --search \"astar(lmcut())\"".format(
                self.plan_result_filename,
                self.plan_domain_filename,
                self.get_pddl_state_filename()), ]
        # This is used for windows
        fast_downward_system_call = "python FastDownward/fast-downward.py --plan-file {} {} {} --search \"astar(lmcut())\" {}".format(
            self.plan_result_filename,
            self.plan_domain_filename,
            self.get_pddl_state_filename(),
            "> NUL")  # this last line is to remove output from showing up in the terminal, feel free to remove this if debugging

        # print("About to call fastdownward like:")
        # print(str(fast_downward_process_call))
        # print("platform is {}".format(platform.system()))
        if platform.system() == 'Windows':
            os.system(fast_downward_system_call)
        elif platform.system() == 'Linux' or platform.system() == 'Darwin':
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
            logging.warning("Plan could not be generated...adding goals: {} to list of failed goals".format(goals))
            self.failed_goals += goals
            self.failed_goals = list(set(self.failed_goals))
            return []
        except:
            logging.warning("Unknown error preventing plan from being generated")
            return

        #for ps in plan:
        #    print("Plan step: {}".format(ps))

        return plan

    def equip_best_items(self):
        """
        Calling this will have the agent evaluate the best items
        """
        pass

    def read_scrolls(self):
        """
        The agent will read all scrolls in its inventory
        """
        pass

    def can_create_plan_to_reach_next_floor(self):
        """
        Returns a plan to go to the next floor
        """

        player_goal_str = None

        # first find a stair down
        cells_with_stairs_down = []
        for cell in self.current_game_state.get_cell_map().get_xy_to_cells_dict().values():
            if cell.has_stairs_down:
                cells_with_stairs_down.append(cell)

        # set the goal to be player at cell with stairs down
        if len(cells_with_stairs_down) > 0:
            player_goal_str = "(playerat {})".format(random.choice(cells_with_stairs_down).get_pddl_name())
        else:
            return False

        # create a plan to reach the stairs
        plan = self.get_plan_from_fast_downward(goals=[player_goal_str])

        # add an action to take the stairs down
        if plan and len(plan) > 0:
            plan.append(Command.TRAVEL_STAIRCASE_DOWN)

        return plan

    def goal_selection(self):
        """
        Returns the goal the agent should pursue right now

        In some cases, deciding to reach a goal may depend
        on whether that goal is even reachable via planning.
        Since we would have generated the plan anyway, let's
        return it and save some work
        """

        cells_visited_threshold_try_stairs = 300

        # attack monsters first
        monster_goal = self.get_first_monster_goal()
        if monster_goal:
            return monster_goal, "monster"

        # try to pick up items
        item_pickup_goal = self.get_item_goal()

        #        elif self.current_game_state.player_current_hp and self.current_game_state.player_hp_max and self.current_game_state.player_current_hp < self.current_game_state.player_hp_max / 2:
        #            return self.get_full_health_goal(), "heal"

        # if self.player_has_seen_stairs_down[self.current_game_state.player_depth]:
        #     lower_place_str = "{}_{}".format(self.current_game_state.player_place.lower().strip(),
        #                                      self.current_game_state.player_depth + 1)
        #     lower_place_goal = "(playerplace {})".format(lower_place_str)
        #     print("Goal selection choosing next goal: {}".format(lower_place_goal))
        #     return lower_place_goal, "descend"
        #
        else:
            goal = self.get_random_nonvisited_nonwall_playerat_goal()
            selected_goal = goal
            return selected_goal, "explore"



    def goal_satisified(self):
        if self.current_goal:
            if self.current_goal[0:5] == '(not ':
                if self.current_goal[5:-1] not in self.pddl_state_facts:
                    logging.info("Dropping goal {} because it's been achieved".format(self.current_goal))
                    return True
            else:
                if self.current_goal in self.pddl_state_facts:
                    logging.info("Dropping goal {} because it's been achieved".format(self.current_goal))
                    return True

        return False

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

    def get_action(self, gamestate: GameState):
        start_time = time.time()
        self.current_game_state = gamestate
        self.process_gamestate_via_cells()

        available_menu_choices = MenuChoiceMapping.get_possible_actions_for_current_menu(
            self.current_game_state.get_current_menu())
        logging.debug("available_menu_choices = {}".format(available_menu_choices))
        if available_menu_choices:
            return available_menu_choices[0]

        self.update_pddl_objs_and_facts()

        # check if goal is already satisified, and if so, reset goal to be empty
        if self.goal_satisified():
            self.current_goal = None
            self.current_goal_type = None
            self.failed_goals = []  # reset this because maybe know we can achieve past goals

        self.new_goal, self.new_goal_type = self.goal_selection()
        logging.debug("Player at: {},{}".format(self.current_game_state.agent_x, self.current_game_state.agent_y))
        logging.debug("New goal: {} with type: {}".format(self.new_goal, self.new_goal_type))
        for a in self.plan:
            logging.debug("  plan action is {}".format(a))

        if self.new_goal and self.new_goal_type and (
                len(self.plan) < 1 or self.new_goal_type != self.previous_goal_type):
            self.current_goal = self.new_goal
            self.current_goal_type = self.new_goal_type
            # plan
            logging.debug("Planning with goal {}".format(self.new_goal))
            self.plan = self.get_plan_from_fast_downward(goals=[self.new_goal])
            self.previous_goal = self.new_goal
            self.previous_goal_type = self.new_goal_type

        next_action = None
        if self.plan and len(self.plan) > 0:
            next_action = self.plan.pop(0)
            self.actions_taken_so_far += 1
        else:

            logging.info("warning - no plan, taking random action!")
            next_action = self.get_random_simple_action()

        self.time_per_action.append(start_time - time.time())
        if len(self.time_per_action) > 10:
            print("Average time per action (per last 10) = {}".format(sum(self.time_per_action[-10:])/10))
        return next_action


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    my_config = WebserverConfig

    # set game mode to Tutorial #1
    my_config.game_id = 'dcss-web-trunk'
    my_config.delay = 0.01
    my_config.species = 'Minotaur'
    my_config.background = 'Berserker'
    my_config.draw_map = False

    # create game
    game = WebSockGame(config=my_config, agent_class=SimpleGRAgent)
    game.run()
