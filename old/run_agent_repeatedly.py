import subprocess
import time
import datetime

num_runs = 10

agents = ['explore']
contexts = [5]
maps = ['k']


def do_the_run(run_id,agent,context,map_id):
    current_human_start_time = datetime.datetime.now().strftime('%I:%M%p')
    start = time.time()
    print("[BEGIN] Run {} of agent {} with context_size {} and sprint_id {} began at {} ...".format(run_id,agent,context,map_id,current_human_start_time))
    subprocess.run(['python3','main.py',agent,str(context),map_id], stdout=subprocess.DEVNULL,stdin=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    current_human_end_time = datetime.datetime.now().strftime('%I:%M%p')                    
    end = time.time()
    print("[END]   Run {} of agent {} with context_size {} and sprint_id {} ended at {} and took {} seconds".format(run_id,agent,context,map_id,current_human_end_time,end-start))
    time.sleep(5)

if __name__ == '__main__':

    for agent in agents:
        for m in maps:
            if agent is 'random':
                for i in range(num_runs):
                    # context doesn't matter, just use 3
                    do_the_run(i,agent,3,m)

            if agent is 'explore':
                for c in contexts:
                    for i in range(num_runs):
                        do_the_run(i,agent,c,m)
                  
