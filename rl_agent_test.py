"""

Demo of an RL agent on the sonja sprint in crawl 23.1

Make sure to run crawl before running this demo, see:
    start_crawl_terminal_sprint.sh

"""


# import argparse
# import sys
# sys.path.append('../../')

from game_connection import GameConnection
from actions import Command, Action
from DCSSMDPClass import DCSSMDP

#from simpleRL
#from simple_rl.planning import ValueIteration
from simple_rl.experiments import Experiment
from simple_rl.utils import chart_utils
#from simple_rl.tasks import *
from simple_rl.agents import RandomAgent, QLearningAgent
import simple_rl.run_experiments as run_experiments

def main():
    # Command line args.
    #task, rom = parse_args()

    # Setup the MDP.
    mdp = DCSSMDP()
    actions = mdp.get_actions()
    gamma = mdp.get_gamma()
    
    random_agent = RandomAgent(actions)
    qlearner_agent = QLearningAgent(actions, gamma=gamma, explore="uniform")
    #agents = [qlearner_agent, random_agent]
    agents = [qlearner_agent]    
    run_experiments.run_agents_on_mdp(agents, mdp, instances=50, episodes=1, steps=2000)
    
    # Run Agents.
    # if isinstance(mdp, MarkovGameMDP):
    #     # Markov Game.
    #     agents = {qlearner_agent.name: qlearner_agent, random_agent.name:random_agent}
    #     play_markov_game(agents, mdp, instances=100, episodes=1, steps=500)
    # else:
        # # Regular experiment.
        # run_agents_on_mdp(agents, mdp, instances=50, episodes=1, steps=2000)

if __name__ == "__main__":
    main()