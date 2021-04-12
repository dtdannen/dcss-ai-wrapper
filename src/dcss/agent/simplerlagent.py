import pickle
import random
from dcss.agent.agent import Agent
from agents.rlagent import RLAgent
from dcss.actions.command import Command
from states.gamestate import GameState


class SimpleRLAgent(Agent):
    simple_commands = [Command.MOVE_OR_ATTACK_N,
                       Command.MOVE_OR_ATTACK_S,
                       Command.MOVE_OR_ATTACK_E,
                       Command.MOVE_OR_ATTACK_W,
                       Command.MOVE_OR_ATTACK_NE,
                       Command.MOVE_OR_ATTACK_NW,
                       Command.MOVE_OR_ATTACK_SW,
                       Command.MOVE_OR_ATTACK_SE]

    def __init__(self):
        super().__init__()
        self.game_over = False
        self.agent = RLAgent(actions=SimpleRLAgent.simple_commands)
        self.action_count = 0
        self.action_limit = 100
        self.agent_xy_vector = []

    def get_action(self, gamestate):
        self.action_count = self.action_count + 1


        r = 2
        print("---------------------")
        print("Radius around agent (r={}):".format(r))
        num_rows = (2 * r) + 1
        row_size = (2 * r) + 1
        cell_vector = gamestate.get_cell_map().get_radius_around_agent_vector(r=2, tile_vector_repr='simple')
        self.agent_xy_vector = [gamestate.get_cell_map().agent_x, gamestate.get_cell_map().agent_y]

        string_ints = [str(i) for i in cell_vector]
        state = ''.join(string_ints)

        string_loc = [str(i) for i in self.agent_xy_vector]
        agent_loc = ''.join(string_loc)
        print(agent_loc)
        next_action = self.agent.run(agent_loc)

        # the end of the episode
        if self.action_count > self.action_limit:
            with open("data/rl_results.txt", 'a') as f:
                f.write(self.get_episode_score())
                f.write("\n")
            self.game_over = True
            with open('agents/qtable.txt', 'wb') as fp:
                pickle.dump(self.agent.q_table, fp)

        print("---------------------")
        print("action", next_action)
        return next_action

    def requesting_start_new_game(self):
        return self.game_over

    def get_episode_score(self):
        goalX = 7
        goalY = 0
        agentX = self.agent_xy_vector[0]
        agentY = self.agent_xy_vector[1]

        # this considers diagonal movements
        # TODO: fix this
        return max(abs(agentX - goalX), abs(agentY - goalY))