"""Training the agent"""

import random
import numpy as np
from collections import defaultdict
from actions import  Command
# Hyperparameters
alpha = 0.1
gamma = 0.6
epsilon = 0.4
visited_state = []

def get_random_action(actions):
    return random.choice(actions)


class RLAgent:
    def __init__(self, actions):
        self.action_set = actions
        self.q_table = {}
        self.last_action = None
        self.last_state = None

    def run(self, state):
        print(self.q_table)
        if state not in self.q_table.keys():
            self.q_table[state] = np.zeros(len(self.action_set) + 1)
        if self.last_action:
            self.update(self.last_state, self.last_action, state)
        return self.get_action(state)

    # TODO: write the reward function
    def get_reward(self, state):
        print(state)
        if state == '70':
            return 10
        if state == '30':
            return 5
        if state == '20':
            return 2
        return 0

    def update(self, pstate, action, new_state):
        reward = self.get_reward(new_state)
        print("**action", action)
        old_value = self.q_table[pstate][action.value]
        next_max = np.max(self.q_table[new_state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        self.q_table[pstate][action.value] = new_value

    def get_action(self, state):
        if random.uniform(0, 1) < epsilon:
            action = get_random_action(self.action_set)  # Explore action space
            self.last_action = action
            self.last_state = state
            return action
        else:
            action = np.argmax(self.q_table[str(state)])  # Exploit learned values
            self.last_action = Command(action)
            self.last_state = state
            return Command(action)
