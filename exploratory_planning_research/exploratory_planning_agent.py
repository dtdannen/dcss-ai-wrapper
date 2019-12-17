'''
This file contains an exploratory agent that moves takes actions in novel situations
'''
import gamestate
import random
import os
import sys
from time import time
from DCSSPDDLWriter import DCSSPDDLWriter
from LogicHandler import LogicHandler
from action_exploration import ContextGenerator
import agent
import numpy as np
import matplotlib.pyplot as plt
import datetime

class ExploratoryPlanningAgent(agent.CrawlAIAgent):
    last_action = None
    #actions = agent.CrawlAIAgent.move_actions


    pddl_writer       = None
    lh                = None
    cg                = None
    all_possiblities  = []
    curr_possiblities = []
    context_counts    = {}
    anySeen           = False
    last_action       = None
    action_queue      = []
    ready_to_delete   = False
    step              = 0

    def __init__(self):
        st = time()
        self.pddl_writer = DCSSPDDLWriter()
        self.lh = LogicHandler()
        self.cg = ContextGenerator()
        self.all_possiblities = self.cg.generateContexts(5)
        self.pddl_writer.set_logic_handler(self.lh)
        self.context_counts = {a:[{},0] for a in self.actions}
        print("INIT: %.3f sec" % (time()-st))

    def save_figure(self,file_name):
        max_contexts = 0
        for action,context_data in self.context_counts.items():
            num_contexts = len(context_data[0])
            if num_contexts > max_contexts:
                max_contexts = num_contexts

        fig, ax = plt.subplots()
        ind = np.arange(len(self.context_counts))
        width = .1
        offset = 0

        for action,context_data in self.context_counts.items():
            rects1 = ax.bar(offset + ind * width, tuple(context_data[0].values()), width, label=action)
            offset += width * max_contexts

        ax.legend()
        plt.savefig(file_name)
     
    def next_action(self):
        if len(self.action_queue) > 0:
            self.last_action = self.action_queue.pop()
        elif self.anySeen:
            # order actions by lowest context count
            counts = []
            for action,context_data in self.context_counts.items():
                counts.append((action,context_data[1]))

            counts = sorted(counts, key=lambda data:data[1])
            min_context = counts[0][1]
            num_actions = 1
            while num_actions < len(counts) and min_context == counts[num_actions][1]:
                num_actions += 1

            # choose an action from a set of the lowest
            self.last_action = random.choice(counts[:num_actions])[0]

        else:
            self.get_next_action_random()

        print('ACTION: ' + str(self.last_action))

        self.step += 1
            
        #return self.last_action.get_json()
        return self.last_action # small change by Dustin, feel free to revert to prev line

    def get_next_action_random(self):
        self.last_action = random.choice(self.actions)
        print('RANDOM: ' + str(self.last_action))
        return self.last_action.get_json()

    def ready_to_delete_game(self):
        return self.ready_to_delete

    def save_data(self, agent_file_name):
        with open(agent_file_name,'w') as f:
            f.write(str(self.lh.facts))
            for p in self.curr_possiblities:
                f.write(':'.join([self.cg.statementToCSV(s) for s in p]) + '\n')

    def update(self):
        if self.last_action is not None and str(self.last_action) in [str(a) for a in self.actions]:
            print("UPDATING AGENT")
            # set minimum context valid found for the action to a large number
            self.context_counts[self.last_action][1] = 2**32
            self.curr_possiblities = self.cg.filterByState(self.lh, self.all_possiblities)
            for context in self.curr_possiblities:
                str_context = ':'.join([self.cg.statementToCSV(statement) for statement in context])
                if str_context not in self.context_counts[self.last_action][0]:
                    self.context_counts[self.last_action][0][str_context] = 0
                self.context_counts[self.last_action][0][str_context] += 1

                # check if the currect valid context has a lower count of all the valid context for the current action
                if self.context_counts[self.last_action][0][str_context] < self.context_counts[self.last_action][1]:
                    self.context_counts[self.last_action][1] = self.context_counts[self.last_action][0][str_context]

                self.anySeen = True

    def check_messages(self, msg_from_server):
        for msgblob in msg_from_server["msgs"]:
            if "messages" in msgblob:
                for message in msgblob["messages"]:
                    if "text" in message:
                        if message["text"].find('You have escaped!') != -1:
                            print("The Agent has escaped the dungeon")
                            self.ready_to_delete = True
                            return
                        elif message["text"].find('You die...') != -1:
                            print("The Agent has died in the dungeon")
                            self.ready_to_delete = True
                            return
                        elif message["text"].find('This will make you lose the game!') != -1:
                            print("The Agent tried to leave the dungeon without the orb")
                            self.action_queue = [agent.CrawlAIAgent._respond_no] + self.action_queue
                            return 

    def add_server_message(self, msg_from_server):
        st = time()
        if "msgs" in msg_from_server:
            self.pddl_writer.hangleMessages(msg_from_server)
            self.update()
            self.check_messages(msg_from_server)
            # check messages 
        print("UPDATE: %.3f sec" % (time()-st))

    def step_complete(self):
        self.save_figure('exploratory-step%04d-' % self.step + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d--%H-%M-%S'))






