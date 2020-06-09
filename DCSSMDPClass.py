''' DCSSMDPClass.py: Contains the DCSSMDP class. '''

# Python imports.
from __future__ import print_function
import random, math, time
import sys, os, copy
import numpy as np
from collections import defaultdict

# Other imports.
from simple_rl.mdp.MDPClass import MDP
from DCSSStateClass import DCSSState
from game_connection import GameConnection
from actions import Command, Action

# Fix input to cooperate with python 2 and 3.
try:
   input = raw_input
except NameError:
   pass

class DCSSMDP(MDP):

    # same basic actions as fast-downward agent
#    action_names = ["MOVE_OR_ATTACK_", "OPEN_DOOR_"]
#    action_suffix_directions = ["N","NE","E","SE","S","SW","W","NW"]
#    ACTIONS = [(action_name+action_suffix_direction) for action_name in self.action_names for action_suffix_direction in self.action_suffix_directions]
#    ACTIONS = [(action_name+action_suffix_direction) for action_name in ["MOVE_OR_ATTACK_", "OPEN_DOOR_"] for action_suffix_direction in ["N","NE","E","SE","S","SW","W","NW"]]
    ACTIONS = [(action_name+action_suffix_direction) for action_name in ["MOVE_OR_ATTACK_"] for action_suffix_direction in ["N","NE","E","SE","S","SW","W","NW"]]
#    ACTIONS.append("OPEN_DOOR")
    
    def __init__(self,
                gamma=0.99,
                visibility_radius = 2,
                init_state_params=None,
                name="dungeon_crawl_stone_soup"):


        #from parameters
        self.gamma = gamma
        self.visibility_radius = visibility_radius
        self.name = name
        self.game = self.setup_game()
        game_state = self.game.get_gamestate()

        if init_state_params is None:
            init_state = DCSSState(game_state)
        else:
            init_state = DCSSState(init_state_params["game_state"])

        MDP.__init__(self, DCSSMDP.ACTIONS, self._transition_func, self._reward_func, init_state=init_state, gamma=gamma)

    def setup_game(self):
        game = GameConnection()
        game.connect()
        print("\n\nconnected!\n\n")
        
        setup_actions = self.get_game_mode_setup_actions()
        
        for action in setup_actions:
            print("\n\nexecution action {}\n\n".format(action))
            game.send_and_receive_dict(action)

        print("\n\nAbout to start playing the game \n\n")
        
        return game

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

    def _reward_calc_num_visited_cells(self, state, action, next_state):
        state_visited_cells = state.num_visited_cells(self.visibility_radius)
        next_state_visited_cells = next_state.num_visited_cells(self.visibility_radius)

        return next_state_visited_cells - state_visited_cells
        
    def _reward_func(self, state, action, next_state=None):
        '''
        Args:
            state (State)
            action (str)
            next_state (State)
        Returns
            (float)
        '''

        reward_value = 0
        reward_value = self._reward_calc_num_visited_cells(state, action, next_state)

        return reward_value


    def _transition_func(self, state, action):
        '''
        Args:
            state (State)
            action (str)
        Returns
            (State)
        '''
        #this is to make sure the server can keep up with the commands
        time.sleep(.1)

        #translate action from simple-RL to DCSS wrapper
        dcss_next_action = Command[action]

        #TODO this could be removed if we wanted to agent to learn the transitions
        #in this setup trying to execute an invalid transition results in a reward of zero because no new tiles are visited
        valid_transition = False
        adj_cells = state.data[0].cellmap.get_cell_map_vector(1)
        game_state = self.game.get_gamestate()
        cell_counter = 0
        for adj_cell in adj_cells:
            #print(str(cell_counter) + ", " + str(adj_cell[0]))
            if (dcss_next_action is Command.OPEN_DOOR and adj_cell[0] == 1):#TODO no way to determine if a door
                valid_transition = True
            elif (cell_counter == 0 and dcss_next_action is Command.MOVE_OR_ATTACK_NW and adj_cell[0] == 1):
                valid_transition = True
            elif (cell_counter == 1 and dcss_next_action is Command.MOVE_OR_ATTACK_N and adj_cell[0] == 1):
                valid_transition = True
            elif (cell_counter == 2 and dcss_next_action is Command.MOVE_OR_ATTACK_NE and adj_cell[0] == 1):
                valid_transition = True
            elif (cell_counter == 3 and dcss_next_action is Command.MOVE_OR_ATTACK_W and adj_cell[0] == 1):
                valid_transition = True
            elif (cell_counter == 5 and dcss_next_action is Command.MOVE_OR_ATTACK_E and adj_cell[0] == 1):
                valid_transition = True
            elif (cell_counter == 6 and dcss_next_action is Command.MOVE_OR_ATTACK_SW and adj_cell[0] == 1):
                valid_transition = True
            elif (cell_counter == 7 and dcss_next_action is Command.MOVE_OR_ATTACK_S and adj_cell[0] == 1):
                valid_transition = True
            elif (cell_counter == 8 and dcss_next_action is Command.MOVE_OR_ATTACK_SE and adj_cell[0] == 1):
                valid_transition = True
            cell_counter += 1
        #####end possible removal

        if dcss_next_action not in Action.command_to_msg.keys():
            print("Action {} is not implemented yet, skipping for now".format(dcss_next_action))
            next_state = state
        elif not valid_transition:
            #print("Not valid transition: " + action + ", " + str(dcss_next_action))
            next_state = state
        else:
            #print("Executing: " + action + ", " + str(dcss_next_action))
            self.game.send_and_receive_command(dcss_next_action)
            game_state = self.game.get_gamestate()
            next_state = DCSSState(game_state)
        
        #check if ternminal
        if game_state.has_agent_died():
            print("Agent has died, shutting down gracefully...: ")
            next_state.set_terminal(True)

        return next_state

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def reset(self, init_state_params=None):
        '''
        Args:
            init_state_params (dict)
        '''
        # if init_state_params is None:
        #     self.init_state = copy.deepcopy(self.init_state)
        # else:
        #     self.init_state = DCSS(cell_map=init_state_params["cell_map"])

        # self.cur_state = self.init_state

        self.game.send_and_receive_command(Command.ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME)
        self.game.send_and_receive_command(Command.RESPOND_YES_TO_PROMPT)
        self.game.send_and_receive_command(Command.ENTER_KEY)
        self.game.send_and_receive_command(Command.ENTER_KEY)
        self.game.send_and_receive_command(Command.ENTER_KEY)

        #TODO figure out if this is the right way ie resample vs reset, may need a bunch of stuff from constructor
        #crude way to resample
        self.game.close()
        self.game = self.setup_game()
        game_state = self.game.get_gamestate()
        self.init_state = DCSSState(game_state)
        self.cur_state = self.init_state

def main():
    dcss = DCSSMDP()

if __name__ == "__main__":
    main()