# Name: LogicHandler 
# Description: A basic interface for asserting and querying a set of facts
# Every fact includes the following parameters:
#     func  - name of the function (string)
#     obj   - name of the object (string)
#     args  - optional argument list (heterogeneous)
#     value - return value of function (integer or boolean)
# PDDL Equivalent: func(obj,[arg1,arg2,...,argN,]value)
# Maintains a running list of functions (integer result), predicates (boolean result),
#     and variables (string parameters or result)
# Maintains a list of facts that have been retracted 

import re

class LogicHandler:

    re_num = re.compile('^-?[0-9]+$')

    functions = {}
    predicate = {}
    variables = {}
    facts = {}

    false_facts = []
    curr_fact_id = 0
    reset_fact_id = 0

    def clear_state(self):
        self.functions = {}
        self.predicate = {}
        self.variables = {}
        self.facts = {}
        self.false_facts = []
        self.curr_fact_id = 0
        self.reset_fact_id = 0

    def _parse_value(self, p):
        if isinstance(p,str):
            if self.re_num.match(p):
                p = int(p)
            elif p == 'true':
                p = True
            elif p == 'false':
                p = False
        return p

    # loads facts from a csv file
    def load_state(self, state_file):
        with open(state_file) as f:
            facts = f.readlines()
            for fact in facts:
                fact = fact.rstrip()
                params = fact.split(',')
                if len(params) >= 3: # func,obj,value
                    func,obj = params[0], params[1]
                    params = params[2:]
                    for i in range(len(params)):
                        params[i] = self._parse_value(params[i])
                    self.assert_fact(func,obj,params[-1],*params[:-1])   

    # saves facts to a csv file
    def save_state(self, state_file):
        with open(state_file,'w') as f:
            for func,func_data in self.facts.items():
                for obj,obj_data in func_data.items():
                    for param_set,fact_data in obj_data.items():
                        fact = ','.join([func,obj])
                        if param_set != '':
                            fact += ',' + param_set
                        fact += ',' + str(fact_data[1])
                        f.write(fact)

    # returns the value of a function, object, and argument list
    def get_value(self, func, obj, *args):
        params = ','.join([str(arg) for arg in args])
        val = None
        if func in self.facts and obj in self.facts[func] and params in self.facts[func][obj]:
            val = self.facts[func][obj][params][1]
        return val

    # returns the remaining parameters for all facts with
    # the matching object and value
    # func(obj,params) = value
    def find_params_with_value( self, func, obj, value):
        params = []
        if func in self.facts:
            if obj in self.facts[func]:
                obj_data = self.facts[func][obj]
                for param_set,fact_data in obj_data.items():
                    if fact_data[1] == value:
                        params.append(param_set)
        return params        

    # returns all objects with the matching value 
    # func(X,args) = value
    def find_objects_with_value( self, func, value, *args):
        params = ','.join([str(arg) for arg in args])
        objs = []
        if func in self.facts:
            for o in self.facts[func]:
                if params in self.facts[func][o] and self.facts[func][o][params][1] == value:
                    objs.append(o)
        return objs

    def retract_facts_all_params(self, func, obj, value ):
        if func in self.facts:
            if obj in self.facts[func]:
                for params in self.facts[func][obj].keys():
                    self.retract_fact(func, obj, value, *params)

    # return a list of objects that have existing facts for the given function and argument list
    def find_objects(self, func, *args):
        params = ','.join([str(arg) for arg in args])
        objs = []
        if func in self.facts:
            for o in self.facts[func]:
                if params in self.facts[func][o]:
                    objs.append(o)
        return objs

    # test whether a given var has been asserted among the facts
    def exist_var(self, var):
        return var in self.variables

    # remove a fact from the state
    def retract_fact(self, func, obj, value, *args):
        if self.query_facts(func, obj, value, *args):
            params = ','.join([str(arg) for arg in args])
            self.false_facts.append(self.fact_to_array(func,obj,value,params))
            del self.facts[func][obj][params]
            if len(self.facts[func][obj]) < 1:
                del self.facts[func][obj]
                if len(self.facts[func]) < 1:
                    del self.facts[func]

            # remove references to variables
            for o in [obj] + [arg for arg in args] + [value]:
                if isinstance(o, str):
                    if o in self.variables:
                        self.variables[o] -= 1
                        if self.variables[o] < 1:
                            del self.variables[o]

            # decrement reference to function or predicate
            if isinstance(value, str) or isinstance(value, int):
                if func in self.functions:
                    self.functions[func] -= 1
                    if self.functions[func] == 0:
                        del self.functions[func]
            elif isinstance(value, bool):
                if func in self.predicates:
                    self.predicates[func] -= 1                 
                    if self.predicates[func] == 0:
                        del self.predicates[func]

    # add a fact to the state                    
    def assert_fact(self, func, obj, value, *args):
        params = ','.join([str(arg) for arg in args])
        if func not in self.facts:
            self.facts[func] = {obj: {}}
        elif obj not in self.facts[func]:
            self.facts[func][obj] = {}

        # add any new variables for new facts
        if params not in self.facts[func][obj]:
            for o in [obj] + [arg for arg in args]:
                if isinstance(o, str):
                    if o not in self.variables:
                        self.variables[o] = 1
                    else:
                        self.variables[o] += 1
        elif isinstance(value, str) and self.facts[func][obj][params][1] is not value:
            old_val = self.facts[func][obj][params][1]
            if isinstance(old_val, str):
                # decrement reference to old variable, if applicable 
                if old_val in self.variables:
                    self.variables[old_val] -= 1
                    if self.variables[old_val] < 1:
                        del self.variables[old_val]
                # increment reference to new variable    
                if value not in self.variables:
                    self.variables[value] = 1
                else:
                    self.variables[value] += 1

        # add function or predicate
        if isinstance(value, str) or isinstance(value, int):
            if func not in self.functions:
                self.functions[func] = 1
            else:
                self.functions[func] += 1
        elif isinstance(value, bool):
            if func not in self.predicates:
                self.predicates[func] = 1
            else:
                self.predicates[func] += 1

        if params in self.facts[func][obj]:
            if self.facts[func][obj][params][1] is not value:
                old_val = self.facts[func][obj][params][1]
                self.false_facts.append(self.fact_to_array(func,obj,old_val,params))
                self.facts[func][obj][params] = [self.curr_fact_id+1,value]
                self.curr_fact_id += 1
        else:
            self.facts[func][obj][params] = [self.curr_fact_id+1,value]

    # determine if a given fact is true given the state
    def query_facts(self, func, obj, value, *args):
        params = ','.join([str(arg) for arg in args])
        truth = False
        if func in self.facts and obj in self.facts[func] and params in self.facts[func][obj]:
            truth = self.facts[func][obj][params][1] == value
        elif isinstance(value, bool) and not value:
            truth = True
        return truth

    # reset the delta facts of every current fact
    def reset_delta_facts(self):
        self.false_facts = []
        self.reset_fact_id = self.curr_fact_id

    # clear the false facts
    def get_false_facts(self):
        return self.false_facts

    # return the list of facts asseted since the last delta reset
    def get_delta_facts(self):
        new_facts = []

        for func,func_data in self.facts.items():
            for obj,obj_data in func_data.items():
                for param_set,fact_data in obj_data.items():
                    if fact_data[0] > self.reset_fact_id:
                        val = fact_data[1]
                        new_facts.append(self.fact_to_array(func,obj,val,param_set))

        return new_facts

    # builds an array from given fact data
    def fact_to_array(self, func, obj, value, params ):
        fact_array = [func,obj]
        if params != '':
            for p in params.split(','):
                p = self._parse_value(p)
                fact_array.append(p)
        fact_array.append(self._parse_value(value))
        return fact_array





