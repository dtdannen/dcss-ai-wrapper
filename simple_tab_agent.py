'''
This file contains a simple agent that executes a pre-defined sequence of actions in a loop
'''
import gamestate
import random

class SimpleAgent():
    '''
    This is a simple tab agent that will perform a loop of keyboard
    shortcuts to attack nearby enemies and then auto-explore
    '''

    action_i = 0

    action_loop = []

    gamestate1 = None

    last_action = None


    def __init__(self):
        self.action_i = 0
        # self.action_loop = ['o',                # auto explore
        #                     'tab_auto_attack',  
        #                     'tab_auto_attack',
        #                     'tab_auto_attack',
        #                     'tab_auto_attack',
        #                     'tab_auto_attack',
        #                     'enter_key',        # clear pending messages
        #                     '5',                # rest (and heal)
        # ]

        # self.action_loop = ['move_E',
        #                     'move_E',
        #                     'move_S',
        #                     'move_S',
        #                     'move_S',
        #                     'move_S',
        #                     'move_W',
        #                     'move_W',
        #                     'move_N',
        #                     'move_N']

        self.simple_movement_actions = ['move_E','move_S','move_W','move_N','enter_key']

        self.gamestate1 = gamestate.GameState()
        
    def get_next_action(self):

        if self.action_i >= len(self.action_loop):
            self.action_i = 0

        curr_action = self.action_loop[self.action_i]
        self.action_i += 1

#        if curr_action is 'move_N':

        self.last_action = curr_action
            
        return curr_action

    def get_next_action_random(self):
        self.last_action = random.choice(self.simple_movement_actions)
        return self.last_action

    def update(self, msg_from_server):
        self.gamestate1.record_movement(self.last_action)
        self.gamestate1.update(msg_from_server)
