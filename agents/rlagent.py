"""Training the agent"""

import random
import numpy as np
from collections import defaultdict

# Hyperparameters
alpha = 0.1
gamma = 0.6
epsilon = 0.1


def get_random_action(actions):
    return random.choice(actions)


class RLAgent:
    def __init__(self, actions):
        self.action_set = actions
        self.q_table = {}
        self.last_action = None

    def run(self, state):
        if state not in self.q_table.keys():
            self.q_table[state] = np.zeros(len(self.action_set) + 1)
        if self.last_action:
            self.update(state, self.last_action)
        return self.get_action(state)

    def get_reward(self, state):
        return 0

    def count_monsters(self, state):
        monsters = list.count(3)

    def update(self, state, action):
        # next_state, reward, done, info = env.step(action)
        state = str(state)
        reward = self.get_reward(state)

        old_value = self.q_table[state][action.value]
        next_max = np.max(self.q_table[state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        self.q_table[state][action.value] = new_value

    def get_action(self, state):
        # while not done:

        if random.uniform(0, 1) < epsilon:
            action = get_random_action(self.action_set)  # Explore action space
            self.last_action = action
            return action
        else:
            action = np.argmax(self.q_table[str(state)])  # Exploit learned values
            self.last_action = action

            return action
