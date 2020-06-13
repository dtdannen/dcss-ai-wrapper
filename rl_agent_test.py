"""

Demo of an RL agent playing DCSS using simple_rl

Make sure to setup crawl server using rl_crawl_server.py

"""

#simple_rl imports
from DCSSMDPClass import DCSSMDP
from simple_rl.agents import RandomAgent, QLearningAgent
import simple_rl.run_experiments as run_experiments

def main():
    #TODO should pass command line args and print usage
    # Setup the MDP.
    mdp = DCSSMDP(visibility_radius = 4)
    actions = mdp.get_actions()
    gamma = mdp.get_gamma()
    
    random_agent = RandomAgent(actions)
    qlearner_agent = QLearningAgent(actions, gamma=gamma, explore="uniform")
    #agents = [qlearner_agent, random_agent]
    agents = [qlearner_agent]
    experiment_name_prefix = "train_01_test_03_reward_visits"
    run_experiments.run_agents_on_mdp(agents, mdp, instances=1, episodes=101, steps=500, experiment_name_prefix=experiment_name_prefix)


if __name__ == "__main__":
    #TODO should pass command line args and print usage
    main()