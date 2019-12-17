import subprocess
import time

if __name__ == "__main__":
    agent_action_selection_types = ['explore','random','human']

    for action_type_str in agent_action_selection_types:
        print("Running experiment for {}".format(action_type_str))
        subprocess.call(['python3','main.py',action_type_str])
        print("Sleeping for 10 seconds before next round starts....")
        time.sleep(10)