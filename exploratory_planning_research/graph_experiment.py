import matplotlib.pyplot as plt
from matplotlib import cm
import os
# get the most recent data file

#DATADIR = 'agent_data/'
DATADIR = 'experiment_run_2/'


# get the filenames
files = sorted([f for f in os.listdir(DATADIR)])
datafiles = []
random_file = None
human_file = None
exploratory_file = None
for f in files:
    if 'human' in f: # get the most recent file
        human_file = DATADIR + f
    elif 'random' in f:
        random_file = DATADIR + f
    elif 'explor' in f:
        exploratory_file = DATADIR + f

print("Processing Random")
print("-- About to graph data from "+str(random_file))
actions_random = []
scores_random = []
header = True
with open(random_file, 'r') as f:
    for line in f.readlines():
        if header:
            header = False
        else:
            row = line.strip().split(',')
            actions_random.append(int(row[0]))
            scores_random.append(float(row[1]))

# now get the second most recent filename
print("Processing Exploratory")
print("-- About to graph data from "+str(exploratory_file))

actions_exploratory = []
scores_exploratory = []

header = True
with open(exploratory_file, 'r') as f:
    for line in f.readlines():
        if header:
            header = False
        else:
            row = line.strip().split(',')
            actions_exploratory.append(int(row[0]))
            scores_exploratory.append(float(row[1]))

# now get the third most recent filename
print("Processing Human")
print("-- About to graph data from "+str(human_file))

actions_human = []
scores_human = []

header = True
with open(human_file, 'r') as f:
    for line in f.readlines():
        if header:
            header = False
        else:
            row = line.strip().split(',')
            actions_human.append(int(row[0]))
            scores_human.append(float(row[1]))



plt.plot(actions_human,scores_human,'-r',label='Human')
plt.plot(actions_random,scores_random,'-b',label='Random')
plt.plot(actions_exploratory,scores_exploratory,'-g',label='Exploration')
plt.legend()
plt.xlabel("Number of Actions Executed")
plt.ylabel("Accuracy")
plt.title("Learning Accuracy per Number of Actions Executed")
plt.show()

