"""Training the agent"""

import random
# from IPython.display import clear_output

from collections import deque
from typing import List

import numpy as np

from gym.spaces import Box
from gym import Wrapper
from gym import envs

# Hyperparameters
alpha = 0.1
gamma = 0.6
epsilon = 0.1

# For plotting metrics
all_epochs = []
all_penalties = []


class env:
    def __init__(self):
        self._action_set = ["up", "left"]

    def reset(self):
        return None

    @property
    def action_set(self):
        return self._action_set


class RandomPolicy:

    def getAction(self):
        return random

    def update(self, a, some_value):
        pass


def get_random_action(actions):
    i = random.randint(0, len(actions))
    return actions[i]


q_table = np.zeros([500, 6])

for i in range(1, 100001):
    state = env.reset()

    epochs, penalties, reward, = 0, 0, 0
    done = False

    while not done:
        if random.uniform(0, 1) < epsilon:
            action = get_random_action(env.action_set)  # Explore action space
        else:
            action = np.argmax(q_table[state])  # Exploit learned values

        next_state, reward, done, info = env.step(action)

        old_value = q_table[state, action]
        next_max = np.max(q_table[next_state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state, action] = new_value

        if reward == -10:
            penalties += 1

        state = next_state
        epochs += 1

    if i % 100 == 0:
        # clear_output(wait=True)
        print(f"Episode: {i}")

print("Training finished.\n")
