"""
Script to run the fastdownward planner with the last state.pddl file generated to see what errors it gave.
"""

import platform
import os
import subprocess

from dcss.actions.command import Command

print("Current working directory: {}".format(os.getcwd()))

plan_domain_filename = "models/fastdownward_simple.pddl"
#plan_current_pddl_state_filename = "models/fdtempfiles/state.pddl"
plan_current_pddl_state_filename = "agent_temp_state/state7.pddl"
plan_result_filename = "models/fdtempfiles/dcss_plan.sas"

fast_downward_process_call = [
            "./FastDownward/fast-downward.py --plan-file {} {} {} --search \"astar(lmcut())\"".format(
                plan_result_filename,
                plan_domain_filename,
                plan_current_pddl_state_filename), ]

# This is used for windows
fast_downward_system_call = "python FastDownward/fast-downward.py --plan-file {} {} {} --search \"astar(lmcut())\" {}".format(
    plan_result_filename,
    plan_domain_filename,
    plan_current_pddl_state_filename,
    "> NUL")  # this last line is to remove output from showing up in the terminal, feel free to remove this if debugging

# print("About to call fastdownward like:")
# print(str(fast_downward_process_call))
# print("platform is {}".format(platform.system()))
if platform.system() == 'Windows':
    os.system(fast_downward_system_call)
elif platform.system() == 'Linux' or platform.system() == 'Darwin':
    subprocess.run(fast_downward_process_call, shell=True)

# step 3: read in the resulting plan
plan = []

with open(plan_result_filename, 'r') as f:
    for line in f.readlines():
        line = line.strip()
        if ';' not in line:
            if line[0] == '(':
                pddl_action_name = line.split()[0][1:]
                command_name = pddl_action_name.upper()
                plan.append(Command[command_name])
        else:
            # we have a comment, ignore
            pass

for ps in plan:
    print("Plan step: {}".format(ps))