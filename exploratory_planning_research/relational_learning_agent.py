'''
An agent that takes users commands to move, and records interactions <s_i, a, s_i+1> to then be used by a transition
model learner.
'''
import gamestate
import random
import re, os, sys
from DCSSPDDLWriter import DCSSPDDLWriter
import agent
import copy
import subprocess
from time import time, sleep
import itertools
import logging
from LogicHandler import LogicHandler
from action_exploration import ContextGenerator
import matplotlib.pyplot as plt
import numpy as np
import datetime
from pathlib import Path
from term import Term,get_arg_types
from action_preconditions_rule import ActionPreconditionsRule
from inspect import getfullargspec
from simple_planning_agent import SimplePlanningAgent

class RelationalLearningAgent(agent.CrawlAIAgent):

    def __init__(self,action_type_str='random',context_size=4,sprint_id='j'):

        self.context_size = context_size
        self.sprint_id = sprint_id
        self.perform_learning = True
        self.ask_before_learning = True

        self.previous_game_state = None
        self.game_state = gamestate.GameState()
        self.positive_states_per_action = []
        self.negative_state_per_action = []
        self.action_history = []
        self.game_state_history = []


        self.data_filename = None
        self.data = {'scores':[],'actions':[]}

        self.data_already_saved = False

        self.available_moves = agent.CrawlAIAgent.all_actions

        self._next_action_func = self._next_action_random # default to random

        self.action_selection_type_str = action_type_str

        self.action_selection_type_str = action_type_str
        if self.action_selection_type_str:
            if self.action_selection_type_str == 'random':
                self._next_action_func = self._next_action_random
            elif self.action_selection_type_str == 'explore':
                self._next_action_func = self._next_action_exploratory
            elif self.action_selection_type_str == 'human':
                self._next_action_func = self._next_action_human_input
            else:
                logging.warning("Attempt to set unknown next_action() function: available types are: {},{},{}".format('random','explore','human'))


        self.interaction_history = {}  # keys are actions,
        #  values are lists of tuples, where tuple(0) is the previous game_state
        # and tuple(1) is the post game_state

        self.action_counter = 0

        for mv in self.available_moves:
            self.interaction_history[str(mv)] = []

        self.learning_file_number = 1

        # key is action, val is list of numbers corresponding to
        # the number of examples - basically this builds up a list of
        # when ilasp was called recording the number of total examples at that time
        # for example, the first time the 'west' action has 20 examples, call ilasp, then at 40, etc
        self.calls_to_ilasp_per_action = {}

        self.action_models = {} # key is action, model is string

        self.pos_dict = {}

        self.perfect_action_models = {
            'east'      : ActionPreconditionsRule('east(V0) :- agentat(V0), at(V0,V1,V2), at(V3,V4,V2), not wall(V3), V1 = V4-1.'), # subeqone(v1,v4)
            'west'      : ActionPreconditionsRule('west(V3) :- agentat(V3), at(V0,V1,V2), at(V3,V4,V2), not wall(V0), V1 = V4-1.'),
            'north'     : ActionPreconditionsRule('north(V3) :- agentat(V3), at(V0,V1,V2), at(V3,V1,V4), not wall(V0), V2 = V4-1.'),
            'south'     : ActionPreconditionsRule('south(V0) :- agentat(V0), at(V0,V1,V2), at(V3,V1,V4), not wall(V3), V2 = V4-1.'),
            'southeast' : ActionPreconditionsRule('southeast(V3) :- agentat(V3), at(V0,V1,V2), at(V3,V4,V5), not wall(V0), V4 = V1-1, V5 = V2-1.'),
            'northwest' : ActionPreconditionsRule('northwest(V0) :- agentat(V0), at(V0,V1,V2), at(V3,V4,V5), not wall(V3), V4 = V1-1, V5 = V2-1.'),
            'northeast' : ActionPreconditionsRule('northeast(V3) :- agentat(V3), at(V0,V1,V2), at(V3,V4,V5), not wall(V0), V4 = V1-1, V2 = V5-1.'),
            'southwest' : ActionPreconditionsRule('southwest(V0) :- agentat(V0), at(V0,V1,V2), at(V3,V4,V5), not wall(V3), V4 = V1-1, V2 = V5-1.'),
            'open_door' : ActionPreconditionsRule('open_door(V3) :- agentat(V0), at(V0,V1,V2), at(V3,V4,V5), closed_door(V3).')
        }

        self.perfect_action_models_test = {
            'east': ActionPreconditionsRule(
                'east(V0) :- at(V0,V1,V2), at(V3,V4,V2), not wall(V3), V1 = V4-1.'),  # subeqone(v1,v4)
            'west': ActionPreconditionsRule(
                'west(V3) :- at(V0,V1,V2), at(V3,V4,V2), not wall(V0), V1 = V4-1.'),
            'north': ActionPreconditionsRule(
                'north(V3) :- at(V0,V1,V2), at(V3,V1,V4), not wall(V0), V2 = V4-1.'),
            'south': ActionPreconditionsRule(
                'south(V0) :- at(V0,V1,V2), at(V3,V1,V4), not wall(V3), V2 = V4-1.'),
            'southeast': ActionPreconditionsRule(
                'southeast(V3) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V0), V4 = V1-1, V5 = V2-1.'),
            'northwest': ActionPreconditionsRule(
                'northwest(V0) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V3), V4 = V1-1, V5 = V2-1.'),
            'northeast': ActionPreconditionsRule(
                'northeast(V3) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V0), V4 = V1-1, V2 = V5-1.'),
            'southwest': ActionPreconditionsRule(
                'southwest(V0) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V3), V4 = V1-1, V2 = V5-1.'),
        }
        self.successes = []

        # For exploration agent
        st = time()
        self.pddl_writer = DCSSPDDLWriter()
        self.lh = LogicHandler()
        self.cg = ContextGenerator()

        if self.action_selection_type_str == 'explore':
            # see if there is already a saved contexts file for this context size
            context_file_name = 'context{}.txt'.format(self.context_size)
            context_file = None
            files = [f for f in os.listdir(os.getcwd())]
            for f in files:
                if context_file_name == f:
                    logging.info("Retrieving previous contexts file: {}".format(f))
                    context_file = f


        self.curr_possiblities = []
        self.pddl_writer.set_logic_handler(self.lh)
        self.context_counts = {a: [{}, 0] for a in self.available_moves}

        self.action_queue = []

        self.anySeen = False
        self.last_action = None

        self.ready_to_delete = False


        # for exploratory agent
        #self.exploratory_agent = ExploratoryPlanningAgent()

    # def save_figure_context_data(self, file_name):
    #     max_contexts = 0
    #     for action,context_data in self.context_counts.items():
    #         num_contexts = len(context_data[0])
    #         if num_contexts > max_contexts:
    #             max_contexts = num_contexts
    #
    #     fig, ax = plt.subplots()
    #     ind = np.arange(len(self.context_counts))
    #     width = .1
    #     offset = 0
    #
    #     for action,context_data in self.context_counts.items():
    #         rects1 = ax.bar(offset + ind * width, tuple(context_data[0].values()), width, label=action)
    #         offset += width * max_contexts
    #
    #     ax.legend()
    #     plt.savefig(file_name)


    def save_figure_context_data(self,file_name,graph_dir,info_dir):
        total_context_counts = {}
        for action,context_data in self.context_counts.items():
            for context,count in context_data[0].items():
                if context not in total_context_counts:
                    total_context_counts[context] = count
                else:
                    total_context_counts[context] += count

        fig, ax = plt.subplots()
        ind = np.arange(len(total_context_counts))
        width = .175
        padded_width = .2

        fig.set_size_inches(18, 6)

        graph_path = Path(graph_dir)
        info_path = Path(info_dir)

        if not graph_path.exists():
            graph_path.mkdir()

        if not info_path.exists():
            info_path.mkdir()

        graph_path /= file_name + '.png'
        info_path /= file_name + '.txt'

        with info_path.open('w') as f:
            f.write('ID,context,count\n')
            i = 0
            for context,count in total_context_counts.items():
                i += 1
                f.write('%d,%s,%d\n' % (i, context, count))

        rects1 = ax.bar(ind * padded_width, tuple(total_context_counts.values()), width, linewidth=2)

        for rect in rects1:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., .95*height,
                    '%d' % int(height),
                    ha='center', va='top', color='white', fontsize=6)

        ax.set_ylabel('Number of Actions')
        ax.set_title('Actions Taken Per Context')

        ax.set_xticks(ind * padded_width)
        ax.set_xticklabels(range(1,len(ind)+1), minor=False, fontsize=6)

        fig = plt.gcf()
        fig.set_size_inches(20,11)
        plt.savefig(str(graph_path))
        plt.close()



    def set_data_filename(self,f_str):
        # So we can save data anytime
        self.data_filename = f_str

    def add_server_message(self, json_msg: {}):
        st = time()
        if "msgs" in json_msg:
            self.pddl_writer.hangleMessages(json_msg)
            self.check_messages(json_msg)
            # check messages
        print("UPDATE: %.3f sec" % (time() - st))

        #print(json_msg)
        self.game_state.update(json_msg)
        self.loc['x']=self.game_state.map_obj_player_x
        self.loc['y']=self.game_state.map_obj_player_y####Should put all this in agent.py so it is universal. agent can hold its own x,y,then. needed for throw action
        #self.exploratory_agent.add_server_message(json_msg)

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



    def __str__(self):
        return 'RelationalLearningAgent'

    def save_data(self,filename=None):
        if not self.data_already_saved:
            dir = 'agent_data/'
            filename_str = None
            if self.data_filename:
                filename_str = self.data_filename
            elif filename:
                filename_str = filename

            filename_str = 'c{}_m{}_'.format(self.context_size,self.sprint_id) + filename_str

            with open(dir+filename_str,'w') as f:
                f.write('actions,scores\n')
                actions = self.data['actions']
                scores = self.data['scores']
                #print("actions are {0}\nand scores are{1}".format(actions,scores))
                assert len(actions) == len(scores)
                for i in range(min(len(actions),len(scores))):
                    f.write('{0},{1}\n'.format(actions[i],scores[i]))
                f.flush()
            logging.info("Successfully wrote data to {0}".format(filename_str))

            self.data_already_saved = True


    def game_mode_selection(self):
        """
        Let's do a sprint game mode!
        :return:
        """
        return {'text': self.sprint_id, 'msg': 'input'}

    def species_selection(self):
        """
        Let's be a minotaur!
        :return:
        """
        return {'text': 'n', 'msg': 'input'}

    def background_selection(self):
        """
        Let's be a Berserker!
        :return:
        """
        return {'text': 'h', 'msg': 'input'}

    def weapon_selection(self):
        """
        Let's start with a spear!
        :return:
        """
        return {'text': 'd', 'msg': 'input'}

    def _next_action_exploratory(self):
        #print(self.planning_agent.get_plan())
        next_action = None
        if len(self.action_queue) > 0:
            next_action = self.action_queue.pop()
        elif self.anySeen:
            # order actions by lowest context count
            counts = []
            for action, context_data in self.context_counts.items():
                counts.append((action, context_data[1]))

            counts = sorted(counts, key=lambda data: data[1])
            min_context = counts[0][1]
            num_actions = 1
            while num_actions < len(counts) and min_context == counts[num_actions][1]:
                num_actions += 1

            # choose an action from a set of the lowest
            next_action = random.choice(counts[:num_actions])[0]
            print(next_action.msg)
            if 'func' in next_action.msg:
                next_action = self._next_action_callable(next_action)

        else:
            next_action = self._next_action_random()

        print('ACTION: ' + str(next_action))
        # return next_action.get_json()
        return next_action

    def _next_action_callable(self, next_action):
        arglist = []

        info = getfullargspec(next_action.msg['func'])
        for arg in info.args:
            if arg == "self":
                arglist.append(self)
            if arg in info.annotations:
                if type(0) == info.annotations[arg]:
                    argument=random.choice([self.loc[arg]-1,self.loc[arg]+1])
                    arglist.append(argument)
        actions = (next_action.msg['func'](*arglist))
        arglist.remove(self)
        next_action.args=arglist
        # actions=actions[::-1] #reverse list
        next_action.msg['actions'] = actions
        return next_action


    def _next_action_random(self):
        next_action = random.choice(self.available_moves)  # type: agent.Action
        #print("Random Action: {0}".format(chosen_action))
        if 'func' in next_action.msg:
            next_action = self._next_action_callable(next_action)
        return next_action

    def _next_action_human_input(self):

        while True:
            # Ask human user for their input
            text = input("What is your next move?")
            chosen_action = None
            if '8' in text:
                chosen_action = agent.CrawlAIAgent._move_N
            elif '9' in text:
                chosen_action = agent.CrawlAIAgent._move_NE
            elif '7' in text:
                chosen_action = agent.CrawlAIAgent._move_NW
            elif '4' in text:
                chosen_action = agent.CrawlAIAgent._move_W
            elif '1' in text:
                chosen_action = agent.CrawlAIAgent._move_SW
            elif '2' in text:
                chosen_action = agent.CrawlAIAgent._move_S
            elif '3' in text:
                chosen_action = agent.CrawlAIAgent._move_SE
            elif '6' in text:
                chosen_action = agent.CrawlAIAgent._move_E

            elif text.isalpha():
                chosen_action = agent.CrawlAIAgent.create_input_action(text)

            if chosen_action:
                return chosen_action
            else:
                print("Unknown input: " + text + ", please try again.")


    def next_action(self):
        prev, current = copy.deepcopy(self.previous_game_state), copy.deepcopy(self.game_state)
        if prev and current:

            # draw current game state
            self.game_state.draw_map()

            #print("Previous player_cell {0}, post player cell {1}".format(prev.get_training_asp_str(),
            #                                                          current.get_training_asp_str()))

            if len(prev.get_asp_str()) != 0 and len(current.get_asp_str()) != 0:
                if len(self.action_history) > 0:
                    last_action = self.action_history[-1]
                    #print(
                    #    "** action={0} | prev player x,y is {1} | post player x y {2}".format(last_action, prev.get_player_xy(),
                    #                                                                          current.get_player_xy()))
                    print("last_action is {}".format(last_action.name))
                    self.interaction_history[last_action.name].append([prev, current,last_action.args])#changed from tuple to list

        self.previous_game_state = copy.deepcopy(self.game_state)

        if self.perform_learning:
            self.inductive_learning_of_all_actions()
            score = self.compute_action_models_score()

        #action = self._next_action_exploratory()
        #action = self._next_action_human_input()
        action = self._next_action_func()

        self.last_action = action

        self.action_history.append(action)

        self.data['actions'].append(self.action_counter)
        if self.perform_learning: self.data['scores'].append(score)
        self.action_counter+=1
        return action.get_json()


    def compute_naive_models_score(self):
        # simple - +1 if it matches, 0 if it doesn't
        score = len(self.successes)

        for action, learned_rules in self.action_models.items():
            if str(action) not in self.successes:  # dont score again after already successful
                #print("Checking to see if learned rule is correct for action {0}".format(action))
                #print("[Perfect] {0}".format(self.perfect_action_models[action]))
                #print("[Learned] {0}".format(learned_rules[0]))
                # Just do the first one for now... will deal with multiple rules later
                if learned_rules[0] == self.perfect_action_models[action]:
                    #print("{} Action was successfully learned!".format(action))
                    score += 1
                    self.successes.append(str(action))

                if len(learned_rules) > 1:
                    print("**** FYI there was more than one learned rule...?!?! ******")
                    i = 0
                    for r in learned_rules:
                        print('\t[rule {0}] {1}'.format(i, r))
                        i += 1

        #print("Successes are: {}".format(self.successes))
        #print(
        #    "Learned Model Score is now {0:d} and number of actions executed is {1}".format(score, self.action_counter))

        #if len(self.data['scores']) > 0 and score < self.data['scores'][-1]:
        #    input("Somehow our learning score decreased...Please investigate and press enter to continue")

        return score

    def compute_action_models_score(self):

        running_score = 0

        for action, learned_rules in self.action_models.items():
            #print("Checking to see if learned rule is correct for action {0}".format(action))
            #print("[Perfect] {0}".format(self.perfect_action_models[action]))
            #print("[Learned] {0}".format(learned_rules[0]))
            # Just do the first one for now... will deal with multiple rules later
            if len(learned_rules) > 0:
                learned_rule = learned_rules[0] # type: ActionPreconditionsRule
                perfect_rule = self.perfect_action_models[action] # type: ActionPreconditionsRule
                learned_rule_score = perfect_rule.asp_distance(learned_rule, self.game_state)
                print("{0} has a score of {1:.2f}".format(action,learned_rule_score))
                running_score += learned_rule_score



            if len(learned_rules) > 1:
                print("**** FYI there was more than one learned rule...?!?! ******")
                i = 0
                for r in learned_rules:
                    print('\t[rule {0}] {1}'.format(i, r))
                    i += 1
        print("running score is {:.2f}".format(running_score))
        return running_score

    def inductive_learning_of_all_actions(self):
        '''
        Returns a string that can be written to a .las file and immediately given to
        ILASP to try to learn preconditions for that action
        :return:
        '''
        learning_rate = 'at least one of each' #'everytime'

        def is_pos_example(example):
            prev_game_state = example[0]  # type:gamestate.GameState
            post_game_state = example[1]  # type:gamestate.GameState
            diff = None
            try:
                diff = example[3]
                if not diff == None:
                    return True
            except:
                pass
            prev_facts = set(prev_game_state.get_asp_str().split('.'))
            post_facts = set(post_game_state.get_asp_str().split('.'))
            nots=list(prev_facts-post_facts)
            for i in range(0,len(nots)):
                temp=nots[i].split('\n')
                nots[i]="\nnot "+temp[1]
            diff = set(nots + list(post_facts-prev_facts))
            if prev_game_state.get_asp_str() == post_game_state.get_asp_str():
                return False
            else:
                example.append(diff)
                return True

        total_num_examples = 0

        when_to_learn = 1  # perform learning when you have at least these many examples (doesn't matter if pos or neg)

        # label examples as positive or negative
        for action in self.available_moves:
            # print("processing action "+str(action))
            action_str = str(action)
            num_examples = 0
            pos = []
            neg = []


            if action_str in self.interaction_history.keys():
                # compute positive and negative examples
                for example in self.interaction_history[action_str]:
                    if is_pos_example(example):
                        pos.append(example)
                    else:
                        neg.append(example)
                    num_examples += 1

            logging.info("{3} examples for {2}: {0} pos and {1} neg".format(len(pos), len(neg), action, num_examples))

            if learning_rate == 'at least one of each':
                if num_examples > 2 and len(pos) > 0 and len(neg) > 0:
                    if action_str in self.calls_to_ilasp_per_action.keys():
                        #print("calls_to_ilasp_per_action[{0}] is {1}".format(action_str, self.calls_to_ilasp_per_action[action_str]))
                        if num_examples not in self.calls_to_ilasp_per_action[action_str]:
                            # call ilasp
                            self._inductive_learning_single_action(pos,neg,action_str)
                            # record so that we don't repeat again until another batch of examples has been received
                            self.calls_to_ilasp_per_action[action_str].append(num_examples)

                    else:
                        #print("FIRST")
                        #print(str(self.calls_to_ilasp_per_action))
                        # call ilasp
                        self._inductive_learning_single_action(pos,neg,action_str)
                        self.calls_to_ilasp_per_action[action_str] = [num_examples]

            total_num_examples += num_examples

        logging.debug("Total of {0} examples for all actions ".format(total_num_examples))

    def _inductive_learning_single_action(self, pos, neg, action_name,effect=True):#effect=True means trying to learn effects, takes perfect preconditions instead of learning them first, skips ILASP
        '''
        :param pos: positive examples
        :param neg: negative examples
        :param action_name: str of action to be learned
        :param asp_bg: background knowledge of the asp
        '''

        if self.ask_before_learning:
            print("in ask before learning")
            text = input("Should I do learning for action: {}? [y/n]".format(action_name))
            if 'n' in text:
                return
        if effect:
            rules=[self.perfect_action_models_test[action_name]]
            self.action_models[action_name] = rules
            self._learn_effect_of_action(action_name,pos)
            for rule in rules:
                print(rule.get_pddl_str())
            return

        # TODO this code needs to be generalized which will require more infastructure

        # all gamestates should have the same background (we'll work around this later on)
        if len(pos + neg) == 0:
            return
        random_example = random.choice(pos + neg)
        random_game_state = random_example[0]  # type: gamestate.GameState
        #asp_bg = random_game_state.get_asp_str()

        ILASP_str = random_game_state.get_asp_comment_str()
        arguments='('
        arg_types=get_arg_types(action_name)
        for arg in arg_types:
            arguments+='var('+arg+'),'
        arguments=arguments[:-1]
        arguments+=')).\n\n'
        ILASP_str += '\n#modeh(' + action_name + arguments


        def _build_args(action_args):
            args=","
            for arg in action_args:
                args+=str(arg)+","
            args=args[:-1]
            return args
        # add positive examples
        for i in range(len(pos)):
            p = pos[i][0]  # type: gamestate.GameState
            ILASP_str += '#pos({'+action_name + '(' + p.get_player_cell() + _build_args(pos[i][2]) + ')}, {},{' + p.get_asp_str() + '}).\n\n'
        # add negative examples
        for i in range(len(neg)):
            n = neg[i][0]  # type: gamestate.GameState
            ILASP_str += '#pos({}, {' + action_name + '(' + n.get_player_cell() + _build_args(neg[i][2]) + ')},{' + n.get_asp_str() + '}).\n\n'

        # TODO possible optimization here - use ycoord and xcoord
        #ILASP_str += '#modeb(1,agentat(var(cell)), (positive)).\n'
        ILASP_str += '#modeb(2,at(var(cell),var(xcoord),var(ycoord)), (positive)).\n'
        ILASP_str += '#modeb(2,wall(var(cell))).\n'
        #ILASP_str += '#modeb(2,deepwater(var(cell))).\n'
        ILASP_str += '#modeb(2,var(xcoord)=var(xcoord)-1).\n'
        ILASP_str += '#modeb(2,var(ycoord)=var(ycoord)-1).\n'
        #ILASP_str += '#modeb(2,closed_door(var(cell))).\n'
        ILASP_str += '#modeb(2,inv_item(var(itemtype),var(quantity))).\n'
        ILASP_str += '#modeb(2,item(var(itemtype),var(cell))).\n'
        ILASP_str += '#maxv(10).\n'
        #ILASP_str += '#disallow_multiple_head_variables.\n'

        # write to file
        filename = 'ilasp_data/ILASP_{0}_{1}.las'.format(self.learning_file_number, action_name)
        with open(filename, 'w') as f:
            f.write(ILASP_str)
        #print("Wrote "+filename)
        self.learning_file_number += 1

        # run ILASP on it
        #print("\n\n Results from ILASP:")
        #completed_process = subprocess.run(['ILASP','--version=2i',filename], stdout=subprocess.PIPE)
        completed_process = subprocess.run(["ILASP","--version=2i","--clingo5","-nc","-ml=6","--max-rule-length=6",filename], stdout=subprocess.PIPE)
        result_output_str = completed_process.stdout.decode()
        print("\n\n\n\n"+result_output_str)
        if 'UNSAT' in result_output_str:
            logging.warning("Unable to learn anything - consider investigating {}".format(filename))
            input("Press enter to continue")
        else:
            rules = []
            for line in result_output_str.split('\n'):
                if action_name in line:
                    rules.append(ActionPreconditionsRule(line))
            self.action_models[action_name] = rules
            self._learn_effect_of_action(action_name,pos)
            input("Press enter to continue")

        print("Updated rule for {0} to be {1}".format(action_name,rules))

        #input("Press enter to continue")

    def _learn_effect_of_action(self,action_name,pos):
        for rule in self.action_models[action_name]:
            body=rule.body
            variables=set()
            for b in body:
                varArray=(b.args)
                for v in varArray:
                    if re.search("V[0-9]",v):
                        variables.add(v)
            lifted_vars=list(sorted(variables))
            variables=str(sorted(variables))
            variables=re.sub("\[","(",variables)
            variables=re.sub("\]",")",variables)
            variables=re.sub("'","",variables)
            precond=rule.standardized_asp_rule_str
            precond=re.sub(action_name+"\(.*\) :-",action_name+variables+" :-",precond)
            buildString=pos[0][0].get_asp_str()
            buildString+="\n"
            buildString+=precond#+"\n#show "+action_name+
            #print(buildString)
            #print(rule.head)
            filename='asp_data/ASP_{0}_{1}.lp'.format(self.learning_file_number, action_name)
            print(filename)
            with open(filename, 'w') as f:
                    f.write(buildString)
            self.learning_file_number+=1

            completed_process = subprocess.run(
                    ["clingo", filename],
                    stdout=subprocess.PIPE)
            answer_set=(completed_process.stdout.decode('utf-8').split('\n')[4].split(' '))
            answers=[]
            for atom in answer_set:
                sub_answers={}
                if action_name in atom:
                    vars=re.split('\(|\)',atom)
                    vars=vars[1].split(',')
                    counter=0
                    for var in vars:
                        sub_answers[var]=lifted_vars[counter]
                        counter=counter+1
                    answers.append(sub_answers)
            diff_root=list(pos[0][3])
            length=0
            for i in range(0,len(diff_root)):
                diff_split = re.split('\(|\)', diff_root[i])
                vars= diff_split[1].split(',')
                length+=len(vars)
            diffs=[]
            for ans in answers:
                temp_len = length
                diff=copy.deepcopy(diff_root)
                for i in range(0,len(diff_root)):
                    for a in ans:
                        diff_split = re.split('\(|\)', diff[i])
                        vars = diff_split[1].split(',')
                        for x in range(0,len(vars)):
                            if a==vars[x]:
                                temp_len-=1
                                vars[x]=ans[a]
                        diff_split[1]=vars
                        diff[i]=""
                        for part in diff_split:
                            diff[i]+=str(part)
                        diff[i]=re.sub('\[','(',diff[i])
                        diff[i]=re.sub('\]',')',diff[i])
                        diff[i]=re.sub("'","",diff[i])
                if temp_len==0:
                    for i in range(0,len(diff)):
                        diff[i]=re.sub("\n","",diff[i])
                    diffs.append(diff)#SAVE
            for diff in diffs:
                #print(diff)
                rule.effects=diff
                #print(rule.get_pddl_str())

    def update_context_counts(self):
        print('here')
        if self.action_selection_type_str == 'explore':
            if self.last_action is not None and str(self.last_action) in [str(a) for a in self.available_moves]:
                print("UPDATING AGENT")
                # set minimum context valid found for the action to a large number
                return
                self.context_counts[self.last_action][1] = 2**32
                self.curr_possiblities = self.planning_agent.cg.filterByState(self.lh, self.all_possiblities)
                for context in self.curr_possiblities:
                    str_context = ':'.join([self.cg.statementToCSV(statement) for statement in context])
                    if str_context not in self.context_counts[self.last_action][0]:
                        self.context_counts[self.last_action][0][str_context] = 0
                    self.context_counts[self.last_action][0][str_context] += 1

                    # check if the currect valid context has a lower count of all the valid context for the current action
                    if self.context_counts[self.last_action][0][str_context] < self.context_counts[self.last_action][1]:
                        self.context_counts[self.last_action][1] = self.context_counts[self.last_action][0][str_context]

                    self.anySeen = True

    def cmpl_coords(self,pos):
        return pos[0] is not None and pos[1] is not None

    def term_exists(self,terms,pred,obj):
        found = False
        for term in terms:
            if term.pred_str == pred and len(term.args) > 0 and term.args[0] == obj:
                found = True
        return found

    # convert the list of fact changes to LogicHandler
    # for the last step to a series of Term objects
    # takes a position dictionary to keep track of the x(), pos_x(), y(), and pos_y()
    # for determining at() terms
    def convert_lh_facts_to_terms( self, old_facts, new_facts, pos_dict ):
        move_list = list(map(str,agent.CrawlAIAgent.move_actions)) # move list to create Terms
        terms = []
        negated = True
        flip_count = len(old_facts)
        for fact in itertools.chain(old_facts,new_facts):
            if not negated and fact[0] == '-':
                t = Term('=', [str(fact[-1]), str(fact[1]), '-', str(fact[2])], move_list)
                terms.append(t)
            elif not negated and (fact[0] == 'x' or fact[0] == 'pos_x'):
                obj = fact[1]
                coord = str(fact[-1])
                if obj in pos_dict:
                    if pos_dict[obj][0] is not coord:
                        if self.cmpl_coords(pos_dict[obj]):
                            if not self.term_exists(terms,'not at',obj):
                                t = Term('not at', [obj, pos_dict[obj][0], pos_dict[obj][1]], move_list)
                                terms.append(t)
                        pos_dict[obj][0] = coord
                        if self.cmpl_coords(pos_dict[obj]):
                            if not self.term_exists(terms,'at',obj):
                                t = Term('at', [obj, pos_dict[obj][0], pos_dict[obj][1]], move_list)
                                terms.append(t)
                else:
                    pos_dict[obj] = [coord,None]
            elif not negated and (fact[0] == 'y' or fact[0] == 'pos_y'):
                obj = fact[1]
                coord = str(fact[-1])
                if obj in pos_dict:
                    if pos_dict[obj][1] is not coord:
                        if self.cmpl_coords(pos_dict[obj]):
                            if not self.term_exists(terms,'not at',obj):
                                t = Term('not at', [obj, pos_dict[obj][0], pos_dict[obj][1]], move_list)
                                terms.append(t)
                        pos_dict[obj][1] = coord
                        if self.cmpl_coords(pos_dict[obj]):
                            if not self.term_exists(terms,'at',obj):
                                t = Term('at', [obj, pos_dict[obj][0], pos_dict[obj][1]], move_list)
                                terms.append(t)
                else:
                    pos_dict[obj] = [None,coord]
            elif fact[0] == 'is_wall':
                pred = 'wall'
                if negated:
                    pred = 'not wall'
                t = Term(pred, [fact[1]], move_list)
                terms.append(t)

            flip_count -= 1
            if flip_count == 0:
                negated = not negated

        return(terms)

    def step_complete(self):
        # prints the effects of step based on fact changes in LogicHandler
        effect_of_step = self.convert_lh_facts_to_terms(self.lh.get_false_facts(),self.lh.get_delta_facts(),self.pos_dict)
        print('EFFECT OF STEP\n' + '\n'.join(map(str,effect_of_step)))

        #self.lh.reset_delta_facts() # resets the LogicHandlers tracking of fact changes

        self.update_context_counts()

        # Uncomment these two lines when we want to see context graphs (it slows down the agent so we don't use when running experiments)
        #prefix_str = 'exploratory-step%04d-' % self.action_counter + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d--%H-%M-%S')
        #self.save_figure_context_data(prefix_str, 'context_graphs', 'context_info')



        #self.save_figure_2('context_graphs/exploratory-step%04d-' % self.action_counter + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d--%H-%M-%S'))
    
    def ready_to_delete_game(self):
        if len(self.data['scores']) > 300:
            return True

        return False





if __name__ == "__main__":

    agent_1 = RelationalLearningAgent()

    for model in agent_1.perfect_action_models.values():
        print(model.get_pddl_str())


    # actions = { 'NORTHWEST' : '7', 'NORTH' : '8', 'NORTHEAST' : '9',
    #             'WEST'      : '4',                'EAST'      : '6',
    #             'SOUTHWEST' : '1', 'SOUTH' : '2', 'SOUTHEAST' : '3',
    #             'GETORB' : 'g',
    #             'EXIT'   : '<' }
    #
    # actions = {'NORTHWEST': 'move_NW', 'NORTH': 'move_N', 'NORTHEAST': 'move_NE',
    #            'WEST': 'move_W', 'EAST': 'move_E',
    #            'SOUTHWEST': 'move_SW', 'SOUTH': 'move_S', 'SOUTHEAST': 'move_SE',
    #            'GETORB': 'g',
    #            'EXIT': '<'}
    #
    # stepRE = re.compile("[0-9]+: ([A-Z]+)")
    #
    # plan = []
    # waitToPlan = 5
    # lastPlanningStep = 0
    # currentMove = 0
    #
    # pddlWriter = None
    #
    # planner = ''
    #
    #
    # def __init__(self):
    #     self.simple_movement_actions = ['move_E', 'move_S', 'move_W', 'move_N', 'enter_key']
    #     self.pddlWriter = DCSSPDDLWriter()
    #     self.planner = planner
    #
    #
    # def get_plan(self):
    #     steps = []
    #     self.pddlWriter.write_prolog("state.pl")
    #     if self.pddlWriter.write_files("domain.pddl", "problem.pddl"):
    #         retval = os.system("%s -o domain.pddl -f problem.pddl > plan.txt" % self.planner)
    #         if retval == 0:
    #             with open("plan.txt") as f:
    #                 l = f.readline()
    #                 while l:
    #                     m = self.stepRE.search(l)
    #                     if m:
    #                         steps.append(m.group(1))
    #                     l = f.readline()
    #         elif retval == 32512:
    #             print("ERROR : Problem with planner (%s) " % self.planner)
    #             print("ABORTING")
    #             sys.exit(-1)
    #         else:
    #             print("Planner : Not enough information to produce a plan")
    #
    #     return steps
    #
    #
    # def get_next_action(self):
    #
    #     if not self.plan and ((self.currentMove - self.lastPlanningStep) >= self.waitToPlan):
    #         print("PLOTTING...")
    #         self.plan = self.get_plan()
    #         self.plan.reverse()
    #         print("PLAN: " + str(self.plan))
    #         self.lastPlanningStep = self.currentMove
    #
    #     if self.plan:
    #         self.last_action = self.actions[self.plan.pop()]
    #     else:
    #         self.get_next_action_random()
    #
    #     self.currentMove += 1
    #
    #     with open("interaction_history.txt", "a") as f:
    #         f.write("\n[Action]: " + str(self.last_action) + "\n")
    #
    #     return self.last_action
    #
    #
    # def get_next_action_random(self):
    #     self.last_action = random.choice(self.simple_movement_actions)
    #     return self.last_action
    #
    #
    # def update(self, msg_from_server):
    #     if "msgs" in msg_from_server:
    #         self.pddlWriter.hangleMessages(msg_from_server)
    #         self.pddlWriter.write_files("domain.pddl", "problem.pddl")
