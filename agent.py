from gamestate import GameState
from actions import Command, Action
import random


class Agent:
    def __init__(self):
        pass

    def get_action(self, gamestate: GameState):
        raise NotImplementedError()


class SimpleRandomAgent(Agent):
    def __init__(self):
        super().__init__()
        self.name = "SimpleRandomAgent"

    def get_action(self, gamestate):
        simple_commands = [Command.MOVE_OR_ATTACK_N,
                           Command.MOVE_OR_ATTACK_S,
                           Command.MOVE_OR_ATTACK_E,
                           Command.MOVE_OR_ATTACK_W,
                           Command.MOVE_OR_ATTACK_NE,
                           Command.MOVE_OR_ATTACK_NW,
                           Command.MOVE_OR_ATTACK_SW,
                           Command.MOVE_OR_ATTACK_SE,
                           Command.REST_AND_LONG_WAIT]
        return Action.get_execution_repr(random.choice(simple_commands))

