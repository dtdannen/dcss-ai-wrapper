import re
import sys
from LogicHandler import LogicHandler
import random

class DCSSPDDLWriter:

    # default values for functions and predictes
    # only functions/predictes with defaults will
    # appear in the PDDL init state logic
    cellDefaults = {#"x"          : 0, 
                    #"y"          : 0,
                    "t_fg"       : 0,
                    "mon_threat" : 4,
                    "exit"    : False,
                    "wall"    : False,
                    "has_orb"    : False}

    playerDefaults = {#"pos_x" : 0,
                      #"pos_y" : 0,
                      "hp" : 20,
                      "hp_max": 20,
                      "mp" : 20,
                      "mp_max": 20,
                      "has_orb": False}

    omitlist = ""

    def clear(self):
        self.tileCache  = {"gxm" : 80, "gym" : 70, "span" : 3}
        self.predicates = set()
        self.functions  = set()
        self.inits      = []
        self.cells      = set()
        self.players    = set()
        self.lastCoord  = None  
        self.lh         = None

        self.pos_dict   = {}
        self.coord_dict = {}
        self.coord_count = 0

        self.re_conjunction = re.compile('(and|or|not)')

    def __init__(self):
        self.clear()  

    def set_logic_handler(self,lh):
        self.lh = lh  

    def getIntValue( self, name, id, func_name, inits ):
        refStatement = [func_name, '%s%d' % (name, id)]
        val = None
        for statement in inits:
            if statement[:-1] == refStatement and isinstance(statement[-1],int):
                val = statement[-1]
        return val

    def statementToPDDL( self, s, isQuery ):
        if s[-1] is True:
            ss = '(%s' % s[0]
        elif s[-1] is False:
            ss = '(not (%s' % s[0]
        else:
            ss = '(= (%s' % s[0]
        for arg in s[1:-1]:
            if isinstance(arg,bool):
                if arg:
                    ss += ' true'
                else:
                    ss += ' false'
            elif isinstance(arg,int):
                ss += ' ' + str(arg)
            elif isQuery:
                ss += ' ?' + arg
            else:
                ss += ' ' + arg

        if s[-1] is not True:
            ss += ') '

            if s[-1] is not False:
                if isinstance(s[-1],bool):
                    if s[-1]:
                        ss += ' true'
                    else:
                        ss += ' false'
                elif isinstance(s[-1],int):
                    ss += ' ' + str(s[-1])
                elif isQuery:
                    ss += ' ?' + s[-1]
                else:
                    ss += ' ' + s[-1]

        ss += ')'
        return ss

    def statementToProlog( self, s ):
        ss = ''
        if s[0] != '-':
            if s[-1] is False:
                ss = 'not('

            ss += '%s(' % s[0]

            isFirst = True

            for arg in s[1:-1]:
                if isFirst:
                    isFirst = False
                else:
                    ss += ','
                if isinstance(arg,bool):
                    if arg:
                        ss += 'true'
                    else:
                        ss += 'false'
                elif isinstance(arg,int):
                    ss += str(arg)
                else:
                    ss += arg

            # add value if not boolean
            if not isinstance(s[-1],bool):
                ss += ',' + str(s[-1])
            elif s[-1] is False:
                ss += ')'

            ss += ').'
        return ss

    def statementToCSV( s ):
        return ','.join(s)

    # Description: Converts a python dictionary to a series of PDDL
    #     init statements, and maintains implied predicates and functions
    # TODO: Maintain a list of types and fill functions/predicates
    #     with the same name with a parent type
    def dict2pddl( self, prefix, d, name, id, type, objects, defaults, knownOnly ):
        for key,value in d.items():
            if not isinstance(key,str):
                continue

            func_name = key
            if prefix != '':
                func_name = prefix + '_' + key

            if isinstance(value,dict):
                self.dict2pddl(func_name, value, name, id, type, objects, defaults, knownOnly )
            elif not knownOnly or func_name in defaults:
                objects.add("%s%d" % (name,id))
                if isinstance(value,bool):
                    p = '(%s ?%s - %s)' % (func_name,name,type)
                    self.predicates.add(p)
                    newStatement = [func_name, '%s%d' % (name, id), value]
                    if newStatement not in self.inits:
                        self.inits.append(newStatement)
                    if self.lh is not None:
                        self.lh.assert_fact(newStatement[0], newStatement[1], newStatement[-1], *newStatement[2:-1])
                elif isinstance(value,int):

                    newStatement = [func_name, '%s%d' % (name, id), value]

                    foundStatement = False
                    statementChanged = True
                    removeStatement = -1

                    for i,statement in enumerate(self.inits):
                        if statement[:-1] == newStatement[:-1] and isinstance(statement[-1],int):
                            foundStatement = True
                            statementChanged = False
                            if statement[-1] != value:
                                removeStatement = i
                                statementChanged = True
                            break

                    if removeStatement >= 0:
                        del self.inits[removeStatement]

                    if not foundStatement:
                        self.functions.add('(%s ?object)' % (func_name))

                    if statementChanged:
                        self.inits.append(newStatement)
                        if self.lh is not None:
                            self.lh.assert_fact(newStatement[0], newStatement[1], newStatement[-1], *newStatement[2:-1])

    def create_at_statement( self, name, id, x, y, objects ):
        obj_name = "%s%d" % (name,id)
        objects.add(obj_name)
        #p = '(at ?obj - object ?x - coord ?y - coord)'
        #self.predicates.add(p)
        newStatement = ['at', obj_name, x, y, True]

        removeStatements = []
        statementFound = False
        statementChanged = False

        # gather old at statements related to obj_name
        for i,statement in enumerate(self.inits):
            if statement[0] == 'at' and \
               statement[1] == obj_name and \
               (statement[2] != x or statement[3] != y) and \
               statement[-1] == True:
               statementChanged = True
               removeStatements.append(i)
            elif statement[0] == 'at' and \
                statement[1] == obj_name and \
                statement[2] == x and statement[3] == y and \
                statement[-1] == True:
                statementFound = True

        # remove all old statements that don't match
        for removeIdx in removeStatements:
            del self.inits[removeIdx]

        # add new statement 
        if not statementFound or statementChanged:
            self.inits.append(newStatement)

        #self.inits.append(newStatement)
        # update LogicHandler
        if self.lh is not None:
            if not self.lh.query_facts('at', obj_name, True, x, y):
                self.lh.retract_facts_all_params('at', obj_name, True)
                self.lh.assert_fact('at', obj_name, True, x, y)

    # add defaults for objects with undefined values
    def filldefaults( self, inits, objects, defaults ):
        for obj_name in objects:
            for func_name,default_value in defaults.items(): 
                # we don't need to fill defaults for predicates
                if isinstance(default_value,bool):
                    continue
                defaultStatement = [func_name, obj_name, default_value]
                found = False
                for statement in inits:
                    if statement[:-1] == defaultStatement[:-1]:
                        found = True
                        break
                if not found:
                    #print("ADDINGDEFAULT: " + str(defaultStatement))
                    inits.append(defaultStatement)
                    self.functions.add('(%s ?object)' % (func_name))

    # uses a hashmap to give each tile integer ID based on its coordinates
    def getID( self, x, y ):
        raw_id = (y + self.tileCache["gym"]) * 10 ** self.tileCache["span"] + (x+self.tileCache["gxm"])
        if raw_id not in self.tileCache:
            self.tileCache[raw_id] = len(self.tileCache)-2
        return self.tileCache[raw_id]

    # takes a server message and updates the existing state
    def hangleMessages( self, msgs ):
        for msg in msgs["msgs"]:
            if msg["msg"] == "player":
                if "status" in msg:
                    idx = -1
                    for i in range(len(msg["status"])):
                        if "light" in msg["status"][i]:
                            idx = i
                            break
                    if idx != -1 and msg["status"][idx]["light"] == 'Orb':
                        print("AGENT HAS THE ORB")
                        msg["has_orb"] = True
                self.dict2pddl('', msg, 'p', 1, 'player', self.players, self.playerDefaults, True)

                player_name = 'p1'
                if 'pos' in msg:
                    self.pos_dict[player_name] = { 'x' : msg['pos']['x'], 'y' : msg['pos']['y'] }
                    self.create_at_statement('p', 1, msg['pos']['x'], msg['pos']['y'], self.players)
            elif msg["msg"] == "map":
                for c in msg["cells"]:
                    #c["has_orb"] = False
                    if "x" in c and "y" in c:
                        lastCoord = {"x" : c["x"], "y" : c["y"] }
                    if "g" in c and c["g"] in self.omitlist:
                        continue
                    if "g" in c and c["g"] == "<":
                        c["exit"] = True
                    if "g" in c and c["g"] == "#":
                        c["wall"] = True
                        #c["has_orb"] = False
                    if "g" in c and c["g"] == ".":
                        #c["has_orb"] = False
                        pass
                    if "t" in c and "fg" in c["t"] and (c["t"]["fg"] == 837 or c["t"]["fg"] == 836):
                        c["has_orb"] = True
                    if "x" in c and "y" in c:
                        self.dict2pddl('', c, 'cell', self.getID(c["x"],c["y"]), 'tile', self.cells, self.cellDefaults, True )
                        self.create_at_statement('cell', self.getID(c['x'], c['y']), c['x'], c['y'], self.cells)
                    elif not lastCoord is None:
                        lastCoord["x"] += 1
                        c["x"] = lastCoord["x"]
                        c["y"] = lastCoord["y"]
                        self.dict2pddl('', c, 'cell', self.getID(c['x'], c['y']), 'tile', self.cells, self.cellDefaults, True)
                        self.create_at_statement('cell', self.getID(c['x'], c['y']), c['x'], c['y'], self.cells)
                    else:
                        print( "ERROR: No coordinates found, skipping...")

        self.filldefaults( self.inits, self.cells, self.cellDefaults )
        self.filldefaults( self.inits, self.players, self.playerDefaults )


    def write_prolog( self, prologfile ):
        self.inits = sorted(self.inits, key=lambda statement: statement[0])
        if len(self.inits) > 0:
            with open(prologfile,"w") as f: 
                for s in self.inits:
                    f.write(self.statementToProlog(s) + '\n')

    def write_csv( self, csvfile ):
        self.inits = sorted(self.inits, key=lambda statement: statement[0])
        if len(self.inits) > 0:
            with open(csvfile,"w") as f: 
                for s in self.inits:
                    f.write(self.statementToCSV(s) + '\n')

    def write_files(self, domainfile, problemfile, goal_statements):
        statements = self.get_coord_order() + self.convert_statements(self.inits)
        return self._write_files( domainfile, problemfile, list(self.cells), list(self.players), list(self.functions), list(self.predicates), statements, goal_statements )

    def exists( self, statements, func_name, obj ):
        for s in statements:
            if s[0] == func_name and s[1] == obj:
                return True
        return False

    def get_params_matching_fact( self, statements, func_name, obj ):
        for s in statements:
            if s[0] == func_name and s[1] == obj:
                return s[2:]
        return None

    def cmpl_coords(self,pos):
        return pos[0] is not None and pos[1] is not None

    def load_coords( self, statements ):
        for fact in statements:
            if fact[0] == 'at':
                obj = fact[1]
                for coord in [str(fact[2]),str(fact[3])]:
                    if coord not in self.coord_dict:
                        self.coord_count += 1
                        self.coord_dict[coord] = 'c%d' % self.coord_count

    def convert_statements( self, statements ):
        new_statements = []
        for fact in statements:
            if fact[0] == 'at':
                obj = fact[1]
                if not self.exists(new_statements,'at',obj):
                    x = self.coord_dict[str(fact[2])]
                    y = self.coord_dict[str(fact[3])]
                    fact = ['at',obj,x,y,True]
                    new_statements.append(fact)
            else:
                new_statements.append(list(fact))

        #     fact = list(s)
        #     if fact[0] == 'has_orb':
        #         new_statements.append(fact)
        #     elif fact[0] == 'is_wall':
        #         fact[0] = 'wall'
        #         new_statements.append(fact)
        #     elif (fact[0] == 'x' or fact[0] == 'pos_x'):
        #         obj = fact[1]
        #         coord = str(fact[-1])
        #         if coord not in self.coord_dict:
        #             self.coord_count += 1
        #             self.coord_dict[coord] = 'c%d' % self.coord_count
        #         if obj in self.pos_dict:
        #             if self.pos_dict[obj][0] is not coord:
        #                 self.pos_dict[obj][0] = coord
        #                 if self.cmpl_coords(self.pos_dict[obj]):
        #                     if not self.exists(new_statements,'at',obj):
        #                         x = self.coord_dict[self.pos_dict[obj][0]]
        #                         y = self.coord_dict[self.pos_dict[obj][1]]
        #                         fact = ['at',obj,x,y,True]
        #                         new_statements.append(fact)
        #         else:
        #             self.pos_dict[obj] = [coord,None]
        #     elif (fact[0] == 'y' or fact[0] == 'pos_y'):
        #         obj = fact[1]
        #         coord = str(fact[-1])
        #         if coord not in self.coord_dict:
        #             self.coord_count += 1
        #             self.coord_dict[coord] = 'c%d' % self.coord_count
        #         if obj in self.pos_dict:
        #             if self.pos_dict[obj][1] is not coord:
        #                 self.pos_dict[obj][1] = coord
        #                 if self.cmpl_coords(self.pos_dict[obj]):
        #                     if not self.exists(new_statements,'at',obj):
        #                         x = self.coord_dict[self.pos_dict[obj][0]]
        #                         y = self.coord_dict[self.pos_dict[obj][1]]
        #                         fact = ['at',obj,x,y,True]
        #                         new_statements.append(fact)
        #         else:
        #             self.pos_dict[obj] = [None,coord]
        return new_statements

    # def get_cell_coords(self,cell_name):
    #     x = self.get_params_matching_fact( self.inits, 'x', cell_name)
    #     y = self.get_params_matching_fact( self.inits, 'y', cell_name)
    #     sx = str(x[0])
    #     sy = str(y[0])
    #     lx = None
    #     ly = None
    #     if sx in self.coord_dict:
    #         lx = self.coord_dict[sx]
    #     if sy in self.coord_dict:
    #         ly = self.coord_dict[sy]
    #     return lx,ly

    def get_coord_vals(self,obj_name):
        coord_data = self.get_params_matching_fact( self.inits, 'at', obj_name)
        x = None
        y = None
        if coord_data is not None:
            x,y = coord_data[0:2]
        return x,y

    def get_coord_vars(self,obj_name):
        lx = None
        ly = None

        coord_data = self.get_params_matching_fact( self.inits, 'at', obj_name)

        if coord_data is not None:
            sx = str(coord_data[0])
            sy = str(coord_data[1])

            if sx in self.coord_dict:
                lx = self.coord_dict[sx]
            if sy in self.coord_dict:
                ly = self.coord_dict[sy]

        return lx,ly    

    def random_cell_coords(self):
        cell_name = random.choice(list(self.cells))
        return coord_data(cell_name)

    def get_coord_order(self):
        statements = []
        for val,label in self.coord_dict.items():
            val_minus_one = str(int(val)-1)
            if val_minus_one in self.coord_dict:
                fact = ['is_one_minus', self.coord_dict[val_minus_one], label, True]
                statements.append(fact)
        return statements

    # takes a series of arrays that define a set of statements seperated
    # by conjunctions and returns the corresponding PDDL.
    # format: [and, [ [or, [s1, s2, ...] ], ...] ]
    def resolve_pddl_conditional(self, statements, conjunction, depth):
        spaces = '    ' * depth
        pddl_str = ''
        if self.re_conjunction.match(conjunction):
            pddl_str += spaces + '(%s\n' % conjunction
            for s in statements:
                if len(s) > 1 and self.re_conjunction.match(s[0]):
                    pddl_str += spaces + self.resolve_pddl_conditional(s[1], s[0], depth+1)
                elif len(s) > 2:
                    pddl_str += spaces + '    ' + self.statementToPDDL(s,False) + '\n'
            pddl_str += spaces + ')\n'
        return pddl_str

    # writes a domain and problem file for the DCSS current state
    def _write_files( self, domainfile, problemfile, cells, players, functions, predicates, statements, goal_statements ):
        if len(self.players) == 0 or len(self.cells) == 0:
            return False
        objects = []
        objects.append('%s - tile\n' %' '.join(cells))
        objects.append('%s - player\n' %' '.join(players))
        objects.append('%s - coord\n' %' '.join(self.coord_dict.values()))
        domainstr = '''(define (domain dcss-domain)
            (:types player tile - object)

            (:requirements :fluents)
            
            (:functions
                (steps)
                %s
            )
            
            (:predicates 
                (at ?obj - object ?x - coord ?y - coord)
                (is_one_minus ?x - coord ?x - coord)   ; equivalent to a == b - 1
                %s
            )
            
            (:action north
                :parameters 
                    (?p1 - player
                     ?t - tile
                     ?u ?v1 ?v2 - coord )

                :precondition 
                    (and 
                        (at ?p1 ?u ?v1)
                        (at ?t ?u ?v2)
                        (not (wall ?t))
                        (is_one_minus ?v1 ?v2)
                    )

                :effect 
                    (and 
                        (not (at ?p1 ?u ?v1))
                        (at ?p1 ?u ?v2)
                        (increase (steps) 1)
                    )
            )

            (:action northeast
                :parameters 
                    (?p - player
                     ?t - tile
                     ?u1 ?u2 ?v1 ?v2 - coord)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (is_one_minus ?u1 ?u2)
                        (is_one_minus ?v2 ?v1)
                    )

                :effect 
                    (and 
                        (not (at ?p ?u1 ?v1))
                        (at ?p ?u2 ?v2)
                        (increase (steps) 1)
                    )
            )

            (:action east
                :parameters 
                    (?p - player
                     ?t - tile
                     ?u1 ?u2 ?v - coord)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v)
                        (at ?t ?u2 ?v)
                        (not (wall ?t))
                        (is_one_minus ?u1 ?u2)
                    )

                :effect 
                    (and 
                        (not (at ?p ?u1 ?v))
                        (at ?p ?u2 ?v)
                        (increase (steps) 1)
                    )
            )

            (:action southeast
                :parameters 
                    (?p - player
                     ?t - tile
                     ?u1 ?u2 ?v1 ?v2 - coord)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (is_one_minus ?u1 ?u2)
                        (is_one_minus ?v1 ?v2)
                    )

                :effect 
                    (and 
                        (not (at ?p ?u1 ?v1))
                        (at ?p ?u2 ?v2)
                        (increase (steps) 1)
                    )
            )

            (:action south
                :parameters 
                    (?p - player
                     ?t - tile
                     ?u ?v1 ?v2 - coord)

                :precondition 
                    (and 
                        (at ?p ?u ?v1)
                        (at ?t ?u ?v2)
                        (not (wall ?t))
                        (is_one_minus ?v1 ?v2)
                    )

                :effect 
                    (and 
                        (not (at ?p ?u ?v1))
                        (at ?p ?u ?v2)
                        (increase (steps) 1)
                    )
            )

            (:action southwest
                :parameters 
                    (?p - player
                     ?t - tile
                     ?u1 ?u2 ?v1 ?v2 - coord)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (is_one_minus ?u2 ?u1)
                        (is_one_minus ?v1 ?v2)
                    )

                :effect 
                    (and 
                        (not (at ?p ?u1 ?v1))
                        (at ?p ?u2 ?v2)
                        (increase (steps) 1)
                    )
            )

            (:action west
                :parameters 
                    (?p - player
                     ?t - tile
                     ?u1 ?u2 ?v - coord)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v)
                        (at ?t ?u2 ?v)
                        (not (wall ?t))
                        (is_one_minus ?u2 ?u1)
                    )

                :effect 
                    (and 
                        (not (at ?p ?u1 ?v))
                        (at ?p ?u2 ?v)
                        (increase (steps) 1)
                    )
            )

            (:action northwest
                :parameters 
                    (?p - player
                     ?t - tile
                     ?u1 ?u2 ?v1 ?v2 - coord)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (is_one_minus ?u2 ?u1)
                        (is_one_minus ?v2 ?v1)
                    )

                :effect 
                    (and 
                        (not (at ?p ?u1 ?v1))
                        (at ?p ?u2 ?v2)
                        (increase (steps) 1)
                    )
            )
        )''' % ('\n                '.join(functions),
                '\n                '.join(predicates))

        obj_str  = '                '.join(objects)
        init_str = '\n                '.join([self.statementToPDDL(s,False) for s in statements])

        # generate goal statements
        if goal_statements is not None:
            goal_str = self.resolve_pddl_conditional(goal_statements,'and',0)
        else:
            goal_str = ''

        #goal_str = '\n                '.join([self.statementToPDDL(s,False) for s in goal_statements])

        problemstr = '''(define (problem dcss-problem) (:domain dcss-domain)
            (:objects
                %s
            )

            (:init
                (= (steps) 0)
                %s    
            )

            (:goal
                %s
            )

            (:metric minimize(steps))
        )''' % ( obj_str, init_str, goal_str )

        with open(domainfile,"w") as f:
            f.write(domainstr)

        with open(problemfile,"w") as f:
            f.write(problemstr)

        # with open("interaction_history.txt","a") as f:
        #     f.write(problemstr+"\n")
        #     f.flush()

        return True
