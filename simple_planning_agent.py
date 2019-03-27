'''
This file contains a simple agent that moves randomaly for a while before consulting a planner
'''
import gamestate
import random
import re,os,sys
from DCSSPDDLWriter import DCSSPDDLWriter
from LogicHandler import LogicHandler
from action_exploration import ContextGenerator
import agent


class SimplePlanningAgent(agent.CrawlAIAgent):

    last_action = None

    actions = { 'NORTHWEST' : agent.CrawlAIAgent._move_NW, 'NORTH' : agent.CrawlAIAgent._move_N, 'NORTHEAST' : agent.CrawlAIAgent._move_NE,
                'WEST'      : agent.CrawlAIAgent._move_W,  'EAST'  : agent.CrawlAIAgent._move_E,
                'SOUTHWEST' : agent.CrawlAIAgent._move_SW, 'SOUTH' : agent.CrawlAIAgent._move_S, 'SOUTHEAST' : agent.CrawlAIAgent._move_SE }

    stepRE = re.compile("[0-9]+: ([A-Z]+)")
    costRE = re.compile("plan cost: ([0-9]+)\.00")

    def __init__(self, planner):
        self.plan = []
        self.waitToPlan       = 10
        self.lastPlanningStep = 0
        self.currentMove      = 0
        self.pddlWriter       = None
        self.planner          = ''

        self.pddlWriter = DCSSPDDLWriter()
        self.planner = planner
        self.goal_statements = None

        self.lh = LogicHandler()
        self.cg = ContextGenerator()

        self.pddlWriter.set_logic_handler(self.lh)
        #self.all_possiblities = self.cg.generateContexts(4,'context4.txt')
        self.all_possiblities = self.cg.load_contexts('context4.txt')
        
        self.anySeen = False

        # add all contexts with zero counts
        self.context_counts = {}
        for context in self.all_possiblities:
            str_context = ':'.join([self.cg.statementToCSV(statement) for statement in context])
            if str_context not in self.context_counts:
                self.context_counts[str_context] = 0

    def game_mode_selection(self):
        """
        Let's do a sprint game mode!
        :return:
        """
        return {'text': self.sprint_id, 'msg': 'input'}

    def cmpl_coords(self,pos):
        return pos[0] is not None and pos[1] is not None

    # resolve statements in context to grounded state
    def resolve_context_instance_to_grounded_state(self, context):
        var_dict = {}
        players = {} # { name : { x : value, y : value }, ... }

        # determine variables with first order relationships
        for fact in context:     
            if fact[0] == 'at':
                local_vars = fact[2:4]
                obj_name = fact[1]
                values = self.pddlWriter.get_coord_vals(obj_name)
                variables = self.pddlWriter.get_coord_vars(obj_name)

                if obj_name not in players:
                    players[obj_name] = {'x' : local_vars[0], 'y' : local_vars[1]}

                for local_var,val,state_var in zip(local_vars,values,variables):
                    if local_var not in var_dict:
                        var_dict[local_var] = {'val' : None, 'var' : None, 'objs' : []}

                    var_dict[local_var]['objs'].append(obj_name)
                    if obj_name not in self.cg.objInstances['player']:
                        var_dict[local_var]['val'] = val
                        var_dict[local_var]['var'] = state_var
                    # else:
                    #     if obj_name not in players:
                    #         players[obj_name] = {'x' : None, 'y' : None}

        # determine variables with second order relationships
        for fact in context:   
            if fact[0] == '-' and len(fact) > 2 and fact[2] == 1:
                # fact[-1] == fact[1] - 1
                va = fact[-1]
                vb = fact[1]
                # vb is set and va is not set
                if (vb in var_dict and var_dict[vb]['val'] is not None) and (va not in var_dict or var_dict[va]['val'] is None):
                    vb_val = var_dict[vb]['val']
                    if str(vb_val) in self.pddlWriter.coord_dict:
                        va_val = str(vb_val-1)
                        if va_val in self.pddlWriter.coord_dict:
                            va_var = self.pddlWriter.coord_dict[va_val]
                            if va not in var_dict:
                                var_dict[va] = {'val' : va_val, 'var' : va_var, 'objs' : []}
                            else:
                                var_dict[va]['val'] = va_val
                                var_dict[va]['var'] = va_var
                        # else:
                        #     print("A VALUE NOT FOUND : %s" % va_val)


                # vb is not set and va is set
                elif (vb not in var_dict or var_dict[vb]['val'] is None) and (va in var_dict and var_dict[va]['val'] is not None):
                    va_val = var_dict[va]['val']
                    if str(va_val) in self.pddlWriter.coord_dict:
                        vb_val = str(va_val+1)
                        if vb_val in self.pddlWriter.coord_dict:
                            vb_var = self.pddlWriter.coord_dict[vb_val]
                            if vb not in var_dict:
                                var_dict[vb] = {'val' : vb_val, 'var' : vb_var, 'objs' : []}   
                            else:
                                var_dict[vb]['val'] = vb_val
                                var_dict[vb]['var'] = vb_var 
                        # else:
                        #     print("B VALUE NOT FOUND : %s" % vb_val)                               

        if len(players) == 0:
            return None                     

        resolved_statements = []

        for pname, pdata in players.items():
            if pdata['x'] is not None and pdata['y'] is not None:
                if var_dict[pdata['x']]['var'] is not None and var_dict[pdata['y']]['var'] is not None:
                    resolved_statements.append(['at', pname, var_dict[pdata['x']]['var'], var_dict[pdata['y']]['var'], True])

        return resolved_statements


    def update_context_counts(self):
        # set minimum context valid found for the action to a large number
        curr_possiblities = self.cg.filterByState(self.lh, self.all_possiblities)

        for context in curr_possiblities:
            str_context = ':'.join([self.cg.statementToCSV(statement) for statement in context])
            # if str_context not in self.context_counts:
            #     self.context_counts[str_context] = 0
            self.context_counts[str_context] += 1
            self.anySeen = True

    def get_context(self, str_context):
        context = []
        for str_statement in str_context.split(':'):
            s = str_statement.split(',')
            s = self.lh.fact_to_array(s[0],s[1],s[-1],','.join(s[2:-1]))
            context.append(s)
        return context

    def is_trivial(self, context):
        it_is = True
        for s in context:
            if s[1] == "player":
                # look for any variable in the statement
                if any([True for item in s[2:] if isinstance(item,str) and self.cg.reVar.match(item)]):
                    it_is = False
        return it_is

    def determine_goal(self):
        self.goal_statements = None
        min_count = 2**32

        min_contexts = []
        for context_str,count in self.context_counts.items():
            if count <= min_count and context_str.find('player'):
                candidate_context = self.get_context(context_str)

                if not self.is_trivial(candidate_context):

                    if count == min_count:
                        min_contexts.append(candidate_context)
                    else:
                        min_count = count
                        min_contexts = [candidate_context]

        potential_goals = []
        
        if len(min_contexts) > 0:
            context = random.choice(min_contexts)
            self.goal_statements = None
            print(context)
            instances = self.cg.context_to_state(context,self.lh)
            if len(instances) > 0:
                random.shuffle(instances)
                for facts in instances:
                    potential_goals.append(self.resolve_context_instance_to_grounded_state(facts))
            else:
                print("NO VALID CONTEXT FOR CURRENT STATE")

        return potential_goals 

    def get_plan(self):
        plan = []
        self.pddlWriter.load_coords(self.pddlWriter.inits)
        print("CHOOSING GOAL")
        potential_goals = self.determine_goal()
        print("GATHERING PLANS...")
        min_cost = 2**32
        plan = []
        for potential_goal in potential_goals:
            if self.pddlWriter.write_files( "domain.pddl", "problem.pddl", potential_goal ):
                retval = os.system("%s -o domain.pddl -f problem.pddl > plan.txt" % self.planner)
                if retval == 0:
                    with open("plan.txt") as f:
                        lines = f.readlines()
                        plan_possible = True
                        cost = None
                        for l in lines:
                            m = self.costRE.match(l)
                            if l.find("ff: goal can be simplified to FALSE. No plan will solve it") != -1:
                                plan_possible = False
                                break
                            elif m:
                                cost = int(m.group(1))

                        if plan_possible and cost is not None:
                            if cost < min_cost:
                                min_cost = cost
                                plan = []
                                for l in lines:
                                    m = self.stepRE.search(l)
                                    if m:
                                        plan.append(m.group(1))

                                if len(plan) > 0:
                                    self.goal_statements = potential_goal

                elif retval == 32512:
                    print("ERROR : Problem with planner (%s) " % self.planner )
                    print("ABORTING")
                    sys.exit(-1)
                # else:
                #     print("Planner : Not enough information to produce a plan")

        if len(plan) == 0:
            print("Planner : no plan found amount potential options")
        else:
            print( "Choose plan with cost %d" % min_cost )
            print( self.goal_statements )

        return plan

    def set_action_selection(self, type_str=None):
        pass

    def set_data_filename(self,f_str):
        pass
        
    def next_action(self):

        if not self.plan and ((self.currentMove-self.lastPlanningStep) >= self.waitToPlan):
            print("PLOTTING...")
            self.plan = self.get_plan()
            self.plan.reverse()
            print( "PLAN: " + str(self.plan))

        if len(self.plan) > 0:
            self.last_action = self.actions[self.plan.pop()]
        else:
            self.get_next_action_random()

        self.currentMove += 1

        # with open("interaction_history.txt","a") as f:
        #     f.write("\n[Action]: "+str(self.last_action)+"\n")

        return self.last_action.get_json()

    def get_next_action_random(self):
        self.last_action = random.choice(list(self.actions.values()))
        #self.last_action = random.choice([agent.CrawlAIAgent._move_W,agent.CrawlAIAgent._move_E])
        return self.last_action

    def add_server_message(self, msg_from_server):
        if "msgs" in msg_from_server:
            self.pddlWriter.hangleMessages(msg_from_server)

    def step_complete(self):
        self.update_context_counts()

    def ready_to_delete_game(self):
        pass


# if __name__ == "__main__":
#     context = (['is_exit', 'cell76', True], ['pos_y', 'p1', 'v1'], ['y', 'cell76', 'v1'])
#     ai = SimplePlanningAgent('/Users/Decker/Documents/Repos/Metric-FF-v2.1/ff')
#     print(ai.resolve_context_instance_to_grounded_state(context))
