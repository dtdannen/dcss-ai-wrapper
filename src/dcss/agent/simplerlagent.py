import random
from dcss.agent.agent import Agent
from agents.rlagent import RLAgent
from dcss.actions.command import Command


class SimpleRLAgent(Agent):
    simple_commands = [Command.MOVE_OR_ATTACK_N,
                       Command.MOVE_OR_ATTACK_S,
                       Command.MOVE_OR_ATTACK_E,
                       Command.MOVE_OR_ATTACK_W,
                       Command.MOVE_OR_ATTACK_NE,
                       Command.MOVE_OR_ATTACK_NW,
                       Command.MOVE_OR_ATTACK_SW,
                       Command.MOVE_OR_ATTACK_SE]

    agent = RLAgent(actions=simple_commands)

    def get_action(self, gamestate):
        r = 2
        print("---------------------")
        print("Radius around agent (r={}):".format(r))
        num_rows = (2*r) + 1
        row_size = (2*r) + 1
        cell_vector = gamestate.get_cell_map().get_radius_around_agent_vector(r=2, tile_vector_repr='simple')
        agent_xy_vector = [gamestate.get_cell_map().agent_x, gamestate.get_cell_map().agent_y]

        string_ints = [str(i) for i in cell_vector]
        state = ''.join(string_ints)

        string_loc = [str(i) for i in agent_xy_vector]
        agent_loc = ''.join(string_loc)
        print(agent_loc)
        next_action = self.agent.run(agent_loc)
        # print(cell_vector)
        # for r in range(num_rows):
        #     s = ''
        #     for c in range(row_size):
        #         s += str(cell_vector[(r*row_size)+c])
        #     print(s)
        print("---------------------")
        print("action", next_action)
        return next_action