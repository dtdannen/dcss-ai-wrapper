import matplotlib.pyplot as plt
from matplotlib import cm
import os
import sys
# get the most recent data file

def graph(lookback):

    DATADIR = 'agent_data/'

    # get the most recent filename
    files = sorted([f for f in os.listdir(DATADIR)])
    filename = DATADIR + str(files[-1-lookback])

    print("-- About to graph data from {}".format(filename))
    actions = []
    scores = []
    header = True
    with open(filename, 'r') as f:
        for line in f.readlines():
            if header:
                header = False
            else:
                row = line.strip().split(',')
                actions.append(int(row[0]))
                scores.append(float(row[1]))

    plt.plot(actions,scores,'-b')
    plt.legend()
    plt.xlabel("Number of Actions Executed")
    plt.ylabel("Accuracy")
    plt.title("Learning Accuracy per Number of Actions Executed")
    plt.show()


if __name__ == "__main__":
    cli_args = sys.argv
    print('cli_args are {}'.format(cli_args))
    if len(cli_args) >= 2:
        lookback = int(cli_args[1])
        graph(lookback)
    else:
        graph(0)
