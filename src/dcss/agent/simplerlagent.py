import random

from dcss.actions.command import Command


class SimpleRLAgent:

    def get_action(self, gamestate):
        r = 2
        print("---------------------")
        print("Radius around agent (r={}):".format(r))
        num_rows = (2*r) + 1
        row_size = (2*r) + 1
        cell_vector = gamestate.get_cell_map().get_radius_around_agent_vector(r=2, tile_vector_repr='simple')
        for r in range(num_rows):
            s = ''
            for c in range(row_size):
                s += str(cell_vector[(r*row_size)+c])
            print(s)
        print("---------------------")
        simple_commands = [Command.MOVE_OR_ATTACK_N,
                           Command.MOVE_OR_ATTACK_S,
                           Command.MOVE_OR_ATTACK_E,
                           Command.MOVE_OR_ATTACK_W,
                           Command.MOVE_OR_ATTACK_NE,
                           Command.MOVE_OR_ATTACK_NW,
                           Command.MOVE_OR_ATTACK_SW,
                           Command.MOVE_OR_ATTACK_SE]
        return random.choice(simple_commands)