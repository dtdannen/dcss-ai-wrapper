import random

from dcss.actions.command import Command
from dcss.agent.base import BaseAgent


class SimpleRandomBaseAgent(BaseAgent):
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
                {'msg': 'key', 'keycode': ord('i')},
                {'msg': 'key', 'keycode': ord('c')},
                ]

    def do_dungeon_webserver(self):
        # select dungeon and character build
        return [{'msg': 'input', 'text': 'b'},
                {'msg': 'input', 'text': 'i'},
                {'msg': 'input', 'text': 'c'},
                ]

    def get_game_mode_setup_actions(self):
        return self.do_dungeon()

    def get_game_mode_setup_actions_webserver(self):
        return self.do_dungeon_webserver()

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
