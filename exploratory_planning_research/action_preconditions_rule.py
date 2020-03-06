import re
import agent
from term import Term, get_arg_types
import copy
import subprocess


class ActionPreconditionsRule:

    def __init__(self, ilasp_str):
        self.raw_asp_rule_str = ilasp_str
        self.standardized_asp_rule_str = ''
        self.pddl_condition_str = ''
        self.head = []
        self.body = []
        self.effects = []

        self._generate_pddl_condition()
        self._standardize_action_model()

        self.first_time_calling_score_function = True
        self.low_info_cells = []

        # TODO Normalize variable names v1 to vN
    def _generate_pddl_condition(self):
            head, body = self.raw_asp_rule_str.split(":-")
            head_parts = re.split("\(|\)", head)
            head_pred = head_parts[0]
            player_var = head_parts[1]
            tile_var = None
            coord_vars = set()
            body = body.replace('.', '')
            body_terms = map(lambda s: s.strip(), body.split(", "))
            spaces = ' ' * 4 * 1
            preconds =  spaces+":precondition\n"


            spaces = ' ' * 4 * 2
            preconds += spaces+'(and\n'
            spaces = ' ' * 4 * 3
            arg_vars={}
            for term in body_terms:
                if '(' in term and ')' in term:
                    term_parts = re.split("\(|\)", term)
                    term_pred_str = term_parts[0]
                    term_vars = term_parts[1].split(",")
                    arg_types=get_arg_types(term_pred_str)
                    pddl_var_str = ''
                    for i, var in enumerate(term_vars):
                        if arg_types[i] not in arg_vars:
                            arg_vars[arg_types[i]]=[var]
                        else:
                            arg_vars[arg_types[i]].append(var)
                            arg_vars[arg_types[i]]=list(set(arg_vars[arg_types[i]]))
                        '''if var == player_var:
                            var = 'p'
                        elif var == tile_var:
                            var = 't'
                        elif tile_var is None and i == 0:
                            tile_var = var
                            var = 't'
                        elif tile_var is not None and tile_var != var and i == 0:
                            print("ERROR: Unexpected additional object found.")
                        elif i != 0:
                            coord_vars.add(var.lower())'''
                        pddl_var_str += '?{}'.format(var.lower())
                        if i < (len(term_vars) - 1):
                            pddl_var_str += ' '

                    if term_pred_str.startswith('not '):
                        preconds += spaces + '(not ({} {}))\n'.format(term_pred_str[4:], pddl_var_str)
                    else:
                        preconds += spaces + '({} {})\n'.format(term_pred_str, pddl_var_str)

                elif '=' in term:
                    parts = term.split(" = ")
                    if '-' in term:
                        if '-' in parts[1]:
                            sub_parts = parts[1].split('-')
                            parts = [parts[0], sub_parts[0], '-', sub_parts[1]]

                            for i, part in enumerate(parts):
                                if part == player_var:
                                    parts[i] = 'p'

                            if parts[3] == '1':
                                coord_vars.add(parts[0].lower())
                                coord_vars.add(parts[1].lower())
                                preconds += spaces + '(is_one_minus ?{} ?{})\n'.format(parts[0].lower(),
                                                                                                      parts[1].lower())
            spaces = ' ' * 4 * 2
            preconds += spaces+')\n'
            header = '''(:action {}
    :parameters\n'''.format(head_pred)
            started=False
            for var_type in arg_vars:
                header+=spaces
                if not started:
                    header+="("
                    started=True
                else:
                    header+=" "
                for arg in arg_vars[var_type]:
                    header+="?"+arg.lower()+" "
                if not var_type == 'fluents':
                    header+="- "+var_type+"\n"
            header=header[:-1]+")\n"
            effects = ''
            spaces = ' ' * 4 * 1
            effects += spaces+":effect\n"
            spaces = ' ' * 4 * 2
            effects += spaces+"(and\n"
            spaces = ' ' * 4 * 3
            for term in self.effects:
                if '(' in term and ')' in term:
                    term_parts = re.split("\(|\)", term)
                    term_pred_str = term_parts[0]
                    term_vars = term_parts[1].split(",")
                    arg_types=get_arg_types(term_pred_str)
                    pddl_var_str = ''
                    for i, var in enumerate(term_vars):
                        if arg_types[i] not in arg_vars:
                            arg_vars[arg_types[i]]=[var]
                        else:
                            arg_vars[arg_types[i]].append(var)
                            arg_vars[arg_types[i]]=list(set(arg_vars[arg_types[i]]))
                        '''if var == player_var:
                            var = 'p'
                        elif var == tile_var:
                            var = 't'
                        elif tile_var is None and i == 0:
                            tile_var = var
                            var = 't'
                        elif tile_var is not None and tile_var != var and i == 0:
                            print("ERROR: Unexpected additional object found.")
                        elif i != 0:
                            coord_vars.add(var.lower())'''
                        pddl_var_str += '?{}'.format(var.lower())
                        if i < (len(term_vars) - 1):
                            pddl_var_str += ' '

                    if term_pred_str.startswith('not '):
                        effects += spaces + '(not ({} {}))\n'.format(term_pred_str[4:], pddl_var_str)
                    else:
                        effects += spaces + '({} {})\n'.format(term_pred_str, pddl_var_str)

                elif '=' in term:
                    parts = term.split(" = ")
                    if '-' in term:
                        if '-' in parts[1]:
                            sub_parts = parts[1].split('-')
                            parts = [parts[0], sub_parts[0], '-', sub_parts[1]]

                            for i, part in enumerate(parts):
                                if part == player_var:
                                    parts[i] = 'p'

                            if parts[3] == '1':
                                coord_vars.add(parts[0].lower())
                                coord_vars.add(parts[1].lower())
                                effects += spaces + '(is_one_minus ?{} ?{})\n'.format(parts[0].lower(), parts[1].lower())
            effects += spaces + "(increase (steps) 1)\n"
            spaces = ' ' * 4 * 2
            effects += spaces + ')\n'
            self.pddl_condition_str = header + preconds + effects+")\n"

    def get_pddl_str(self):
        self._generate_pddl_condition()
        return self.pddl_condition_str

    def _standardize_action_model(self):
        self.head = [] # reset these
        self.body = []

        arg_id = 0 # new var counter

        def _add_to_env(t:Term, env:{}, arg_id:int):
            for i in range(len(t.arg_types)):
                if t.args[i] not in env.keys():
                    # get a new var representative of type
                    first_char_of_arg_type = t.arg_types[i][0] # literally get the first char of the str of the arg type
                    env[t.args[i]] = '{}{}'.format(first_char_of_arg_type, arg_id)
                    arg_id+=1
            return env, arg_id

        # first, build up the environment, then replace vars to get adjusted rule
        head, body = self.raw_asp_rule_str.split(":-")
        env = {}
        head_parts = re.split("\(|\)", head)
        head_pred = head_parts[0]
        head_arg = head_parts[1]
        self.head.append(Term(head_pred,[head_arg]))
        env, arg_id = _add_to_env(self.head[0],env,arg_id)

        # process body terms
        body = body.replace('.','')
        body_terms = map(lambda s: s.strip(), body.split(", "))
        #print("body terms are {0}".format(body_terms))

        for term in body_terms:

            if '(' in term and ')' in term:
                term_parts = re.split("\(|\)", term)
                term_pred_str = term_parts[0]
                term_all_vars_str = term_parts[1]
                term_vars = term_all_vars_str.split(",")
                curr_term = Term(term_pred_str,term_vars)
                self.body.append(curr_term)
                env, arg_id = _add_to_env(curr_term, env, arg_id)

            elif '=' in term:
                parts = term.split(" = ")
                curr_term = None
                if '+' in term or '-' in term:
                    if '-' in parts[1]:
                        sub_parts = parts[1].split('-')
                        parts = [parts[0], sub_parts[0], '-', sub_parts[1]]
                    elif '+' in parts[1]:
                        add_parts = parts[1].split('+')
                        parts = [parts[0], add_parts[0], '+', add_parts[1]]
                    #print("parts={}".format(parts))
                    curr_term = Term('=',parts)
                else:
                    curr_term = Term('=',parts)

                self.body.append(curr_term)
                env, arg_id = _add_to_env(curr_term, env, arg_id)

        # now that we have our env, just replace with all new vars
        adjusted_action_rule = copy.copy(self.raw_asp_rule_str)
        for k, v in env.items():
            adjusted_action_rule = adjusted_action_rule.replace(k, v)

        for t in self.head+self.body: # type: Term
            standardized_args = []
            #print('env = {}'.format(env))
            #print("t={}".format(t))
            for i in range(len(t.args)):
                a = t.args[i]
                #print('i={},t.arg_types={}'.format(i,t.arg_types))
                if t.arg_types[i] not in ['constant','operator']:
                    assert a in env.keys()
                    standardized_args.append(env[a])
                else:
                    standardized_args.append(a)
            #print("t.args = {}, standardized args = {}".format(t.args,standardized_args))
            t.set_human_readable_args(standardized_args)

        s = '{} :- '.format(self.head[0])
        for i in range(len(self.body)):
            if i < len(self.body)-1:
                s += '{}, '.format(self.body[i])
            if i == len(self.body)-1:
                s += '{}.'.format(self.body[i])

        self.standardized_asp_rule_str = s

    def get_standardized_action_rule_str(self):
        return self.standardized_asp_rule_str

    def get_standardized_vars(self):
        vars = []
        for t in self.head+self.body: # type: Term
            for standardized_v in t.human_readable_args:
                if standardized_v not in vars:
                    vars.append(standardized_v)
        return vars

    def substitute_args(self,curr,new):
        # replace all args from curr with new
        for t in self.head+self.body:
            t.substitute_args(curr,new)

    def __str__(self):
        return self.standardized_asp_rule_str

    def _simple_eq(self, other):
        # compare standardized terms
        heads_match = set(self.head) == set(other.head)
        bodies_match = set(self.body) == set(other.body)

        return heads_match and bodies_match

    def _complex_eq(self, other):
        #print("\t  Now complex comparing:\n\t  {}\n\t  {}".format(self, other))
        vars_other = other.get_standardized_vars()
        vars_self = self.get_standardized_vars()

        # make sure they have the same set of variables (only works because they were standardized)
        #print("vars_perfect: {0}\nvars_learned: {1}".format(set(vars_perfect), set(vars_learned)))
        self_len = len(self.head)+len(self.body)
        other_len = len(other.head)+len(other.body)
        if set(vars_other) == set(vars_self) and self_len == other_len:
            for vars_scrambled in itertools.permutations(vars_other):
                # now we have a mapping of vars_scrambled[0] -> vars_learned[0]
                self_rule_copy = copy.deepcopy(self) # type: ActionPreconditionsRule
                #print("self_rule_copy[type={}]: {}".format(type(self_rule_copy), self_rule_copy))
                #print("other[type={}]: {}".format(type(other), other))
                #print("vars scrambled: {0}".format(vars_scrambled))
                self_rule_copy.substitute_args(vars_self,vars_scrambled)

                #print("Comparing Rules:\n{}\n{}".format(self_rule_copy,other))

                if self_rule_copy._simple_eq(other):
                    return True

                # ...keep trying...

        return False

    def remove_low_info_tiles(self, gamestate: 'gamestate.GameState'):
        '''
        Removes extra tiles from the scoring function if every move rule is applicable in this cell
        :return:
        '''

        perfect_action_models = {
            'east': ActionPreconditionsRule('east(V0) :- at(V0,V1,V2), at(V3,V4,V2), not wall(V3), V1 = V4-1.'),
            'west': ActionPreconditionsRule('west(V3) :- at(V0,V1,V2), at(V3,V4,V2), not wall(V0), V1 = V4-1.'),
            'north': ActionPreconditionsRule('north(V3) :- at(V0,V1,V2), at(V3,V1,V4), not wall(V0), V2 = V4-1.'),
            'south': ActionPreconditionsRule('south(V0) :- at(V0,V1,V2), at(V3,V1,V4), not wall(V3), V2 = V4-1.'),
            'southeast': ActionPreconditionsRule(
                'southeast(V3) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V0), V4 = V1-1, V5 = V2-1.'),
            'northwest': ActionPreconditionsRule(
                'northwest(V0) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V3), V4 = V1-1, V5 = V2-1.'),
            'northeast': ActionPreconditionsRule(
                'northeast(V3) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V0), V4 = V1-1, V2 = V5-1.'),
            'southwest': ActionPreconditionsRule(
                'southwest(V0) :- at(V0,V1,V2), at(V3,V4,V5), not wall(V3), V4 = V1-1, V2 = V5-1.'),
        }

        asp_str = ''

        asp_str += gamestate.get_asp_str() + "\n\n"

        # write the rule for every perfect rule
        for action_name, rule in perfect_action_models.items():

            # get the name of the action from head
            head_term = rule.head[0]  # type: Term
            head_pred = head_term.get_pred_str()
            # print("head_pred_self = {}".format(head_pred_self))
            # head_pred_self = head_pred_self[0:head_pred_self.index('(')]
            asp_str += rule.get_standardized_action_rule_str()
            asp_str += '\n'

        asp_str += '\n'

        for action_name, rule in perfect_action_models.items():
            asp_str += '#show {}/1.\n'.format(rule.head[0].get_pred_str())

        # write to file
        filename = 'asp_data/removing_low_info_rules.lp'
        with open(filename, 'w') as f:
            f.write(asp_str)
        # print("Wrote " + filename)

        # run clingo
        # print("\n\n Results from clingo:")
        completed_process = subprocess.run(
            ["clingo", filename],
            stdout=subprocess.PIPE)
        result_output_str = completed_process.stdout.decode()
        # print(result_output_str)

        output = []
        self_occurences = []
        learned_occurences = []
        true_rules_per_cell = {}
        for line in result_output_str.split('\n'):
            output.append(line)
            # print("Just processed the following line:\n{}\n\n".format(line))

            perfect_rule_head_preds = map(lambda r: r.head[0].get_pred_str(), perfect_action_models.values())
            found_a_rule_term = False
            first_find = True
            for p in perfect_rule_head_preds:
                if p in line:
                    found_a_rule_term = True
                    break

            if found_a_rule_term and first_find:
                first_find = False
                all_occurences = line.split()
                for i in all_occurences:
                    i = i.strip()
                    i_parts = re.split("\(|\)", i)
                    i_head = i_parts[0]
                    cell = i_parts[1]
                    if cell in true_rules_per_cell.keys():
                        true_rules_per_cell[cell].append(i_head)
                    else:
                        true_rules_per_cell[cell] = [i_head]


        # now if any of the cells exist in all 8 directions, remove all of them but one
        low_info_cells = []
        for cell in true_rules_per_cell.keys():
            if len(true_rules_per_cell[cell]) == len(perfect_action_models.keys()):
                low_info_cells.append(cell)

        low_info_cells = set(low_info_cells)
        self.low_info_cells = low_info_cells

        #for c in self.low_info_cells:
        #    print("Low info cell {}".format(c))

    def asp_distance(self, learned, gamestate: 'gamestate.GameState'):
        '''
        Use answer set programming to see how close the match is for learned rules vs perfect ones
        Note: Self is assumed to be the perfect rule, and learned is the learned rule
        :param learned:
        :return:
        '''

        if self.first_time_calling_score_function:
            # remove low_info tiles
            self.remove_low_info_tiles(gamestate)
            self.first_time_calling_score_function = False

        #print("Self rule is {}".format(str(self)))
        #print("Learned rule is {}".format(str(learned)))

        asp_str = ''

        asp_str += gamestate.get_asp_str() + "\n\n"

        # get the name of the action from head
        head_term_self = self.head[0] # type: Term
        head_pred_self = head_term_self.get_pred_str()
        #print("head_pred_self = {}".format(head_pred_self))
        #head_pred_self = head_pred_self[0:head_pred_self.index('(')]
        asp_str += self.get_standardized_action_rule_str().replace(head_pred_self,head_pred_self+'_self')
        asp_str += '\n\n'

        head_term_learned = learned.head[0]  # type: Term
        head_pred_learned = head_term_learned.get_pred_str()
        #head_pred_learned = head_pred_learned[0:head_pred_learned.index('(')]
        asp_str += learned.get_standardized_action_rule_str().replace(head_pred_learned, head_pred_learned + '_learned')
        asp_str += '\n\n'

        asp_str += '#show {}/1.\n'.format(head_pred_self+'_self')
        asp_str += '#show {}/1.\n'.format(head_pred_learned+'_learned')

        # write to file
        filename = 'asp_data/comparing_{0}.lp'.format(head_pred_self)
        with open(filename, 'w') as f:
            f.write(asp_str)
        #print("Wrote " + filename)

        # run clingo
        #print("\n\n Results from clingo:")
        completed_process = subprocess.run(
            ["clingo", filename],
            stdout=subprocess.PIPE)
        result_output_str = completed_process.stdout.decode()
        #print(result_output_str)

        output = []
        self_occurences = []
        learned_occurences = []
        for line in result_output_str.split('\n'):
            output.append(line)
            #print("Just processed the following line:\n{}\n\n".format(line))

            if head_pred_self+'_self' in line or head_pred_learned+'_learned' in line:
                #print("\n\nline is {}\n\n".format(line))
                all_occurences = line.split(' ')

                for i in all_occurences:
                    if head_pred_self+'_self' in i:
                        self_occurences.append(i.strip())
                        #print("Just added {} to self_occurences".format(i.strip()))
                    elif head_pred_learned+'_learned' in i:
                        learned_occurences.append(i.strip())
                        #print("Just added {} to learned_occurences".format(i.strip()))
                    else:
                        print("neither self nor learned matched with {}".format(i))

        # remove the predicates, only use the cells
        self_occurences_args = []
        for i in self_occurences:
            i_parts = re.split("\(|\)", i)
            i_args = i_parts[1]
            self_occurences_args.append(i_args)
            #print("self_occurences_args: {}".format(i_args))

        self_occurences_args = set(self_occurences_args)

        learned_occurences_args = []
        for i in learned_occurences:
            i_parts = re.split("\(|\)", i)
            i_args = i_parts[1]
            learned_occurences_args.append(i_args)
            #print("learned_occurences_args: {}".format(i_args))

        learned_occurences_args = set(learned_occurences_args)

        # to keep things simple for now, we only care about instances that should be true but the learned model
        # did not produce those (if the learned model thinks an instance is true that shouldn't be, right now we don't
        #  penalize against that)
        true_positives = self_occurences_args
        true_negatives = gamestate.all_asp_cells - true_positives
        #print("{} true positives: {}".format(len(true_positives),true_positives))
        #print("{} true negatives".format(len(true_negatives)))

        predicted_positives = learned_occurences_args
        predicted_negatives = gamestate.all_asp_cells - predicted_positives
        #print("{} predicted positives: {}".format(len(predicted_positives), predicted_positives))
        #print("{} predicted negatives".format(len(predicted_negatives)))

        correct, incorrect, num_instances = 0, 0, len(gamestate.all_asp_cells)

        low_info_cells_minus_one = list(self.low_info_cells)[1:]

        for cell in gamestate.all_asp_cells:
            if cell not in low_info_cells_minus_one:
                if cell in true_positives:
                    if cell in predicted_positives:
                        correct += 1
                    else:
                        incorrect +=1
                if cell in true_negatives:
                    if cell in predicted_negatives:
                        correct +=1
                    else:
                        incorrect +=1

        assert correct+incorrect == (num_instances - len(low_info_cells_minus_one))

        accuracy = correct / (num_instances - len(low_info_cells_minus_one))
        #print("error is {}".format(error))

        # difference between them is
        score = float('{0:.3f}'.format(accuracy))

        #input("Press enter to continue")

        return score

    def __eq__(self, other):
        #print("\tNow comparing:\n\t{}\n\t{}".format(self, other))
        if self._simple_eq(other):
            return True
        else:
            return self._complex_eq(other)
