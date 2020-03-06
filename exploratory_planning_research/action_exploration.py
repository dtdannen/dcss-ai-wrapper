import os,re
import sys
import numpy as np
from LogicHandler import LogicHandler
from itertools import permutations
from itertools import product
from itertools import chain
import logging

class ContextGenerator:

    # TODO domain.pddl
    # definitions of the functions and predicates
    methods = {
        "subx"       : {"op" : "-", "args" : ["xcoord","int_constant"], "return" : "xcoord" },
        "suby"       : {"op" : "-", "args" : ["ycoord","int_constant"], "return" : "ycoord" },
        "has_orb"    : {"args" : ["object"], "return" : "bool" },
        "exit"       : {"args" : ["tile"],   "return" : "bool" },
        "t_fg"       : {"args" : ["tile"],   "return" : "fg_enum" },
        "wall"       : {"args" : ["tile"],   "return" : "bool" },
        "water"      : {"args" : ["tile"], "return" : "truth"},
        "lava"       : {"args" : ["tile"], "return" : "truth"},
        "stone"      : {"args" : ["tile"], "return" : "truth"},
        "at"         : {"args" : ["object", "xcoord", "ycoord"], "return" : "truth"},
        "inventory"  : {"args" : ["player","item"], "return" : "truth"},
    }

    # actionParameters and constants
    objects = { 
        "truth"    : [True],
        "bool"     : [True,False],
        "int_constant" : [1],
        "xcoord"    : [],
        "ycoord"    : [],
        "fg_enum"  : [836],
        "player"   : ["player"],
        "tile"     : ["tile"],
        "object"   : ["player","tile"],
        "item"     : ["stone"]
    }

    # all instances of each action parameters
    # TODO this should get the current cells from the gamestate
    objInstances = {
        "player" : ["p1"],
        "tile"   : ['cell1','cell2','cell3','cell4','cell5','cell6','cell7','cell8','cell9','cell10','cell11','cell12','cell13','cell14','cell15','cell16','cell17','cell18','cell19','cell20','cell21','cell22','cell23','cell24','cell25','cell26','cell27','cell28','cell29','cell30','cell31','cell32','cell33','cell34','cell35','cell36','cell37','cell38','cell39','cell40','cell41','cell42','cell43','cell44','cell45','cell46','cell47','cell48','cell49','cell50','cell51','cell52','cell53','cell54','cell55','cell56','cell57','cell58','cell59','cell60','cell61','cell62','cell63','cell64','cell65','cell66','cell67','cell68','cell69','cell70','cell71','cell72','cell73','cell74','cell75','cell76','cell77','cell78','cell79','cell80','cell81','cell82','cell83','cell84','cell85','cell86','cell87','cell88','cell89','cell90','cell91','cell92','cell93','cell94','cell95','cell96','cell97','cell98','cell99','cell100','cell101','cell102','cell103','cell104','cell105','cell106','cell107','cell108','cell109','cell110','cell111','cell112','cell113','cell114','cell115','cell116','cell117','cell118','cell119','cell120','cell121','cell122','cell123','cell124','cell125','cell126','cell127','cell128','cell129','cell130','cell131','cell132','cell133','cell134','cell135','cell136','cell137','cell138','cell139','cell140','cell141','cell142','cell143','cell144','cell145','cell146','cell147','cell148','cell149','cell150','cell151','cell152','cell153','cell154','cell155','cell156','cell157','cell158','cell159','cell160','cell161','cell162','cell163','cell164','cell165','cell166','cell167','cell168','cell169','cell170','cell171','cell172','cell173','cell174','cell175','cell176']
    }

    actionParameters = [ "player", "tile" ]

    varFormat = 'v%d'

    reVar = re.compile('^v[0-9]+$')
    re_num = re.compile('^-?[0-9]+$')

    def isConstant(self, val ):
        return isinstance(val,bool) or isinstance(val,int)

    def copyContext(self, c ):
        return [list(s) for s in c]

    def copyListListDict(self, dict):
        d = {}
        for key,value in dict.items():
            if isinstance(value,(list,tuple)):
                d[key] = []
                for subval in value:
                    if isinstance(subval,(list,tuple)):
                        d[key].append(subval[:])
        return d

    # counts total length of all collections
    # in a dictionary (non-recursive)
    def totalCountDict(self, dict):
        count = 0
        for value in dict.values():
            if isinstance(value,(list,tuple,set,dict)):
                count += len(value)
        return count

    # checks if arguments and return value are all unique values
    def uniqueArgsAndRet(self, s ):
        return len(s[1:]) == len(set(s[1:]))

    def addInstance(self, type_name, instance_name):
        newInstance = False
        if type_name in self.objInstances:
            if instance_name not in self.objInstances[type_name]:
                self.objInstances[type_name].append(instance_name)
                newInstance = True
        return newInstance

    def statementToPDDL(self, s ):
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
            else:
                ss += ' ?' + arg

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
                else:
                    ss += ' ?' + s[-1]

        ss += ')'
        return ss

    def statementToProlog(self, s ):
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

    def statementToCSV(self, s ):
        return ','.join([str(e).lower() for e in s])

    def allConstant(self, s ):
        return all([self.isConstant(arg) for arg in s[1:-1]])

    def mostConstant(self, s ):
        return sum([1 for arg in s[1:-1] if self.isConstant(arg)]) >= (len(s[1:]) - 1)

    def allVarsAtLeastTwice(self, dict ):
        allTwice = True
        totalVars = 0 
        for key,value in dict.items():
            for var,count in value:
                totalVars += len(value)
                if count < 2:
                    allTwice = False
                    break
        return totalVars > 0 and allTwice

    def atLeastOneFuncWithObjectParam(self, obj_type, statements):
        return any( [True for s in statements if obj_type in s] )

    # checks for a simple contradiction between predicates
    def contradict(self, statement, statements):
        contradiction = False
        if isinstance(statement[-1],bool):
            for refStatement in statements:
                if isinstance(refStatement[-1],bool) and statement[:-1] == refStatement[:-1] and statement[-1] != refStatement[-1]:
                    contradiction = True
                    break
        return contradiction

    # checks for redundant working variable
    def redundantVar(self, statement, statements):
        isRedundant = False
        if isinstance(statement[-1],str):
            for refStatement in statements:
                if isinstance(refStatement[-1],str) and \
                  statement[:-1] == refStatement[:-1] and \
                  self.reVar.match(statement[-1]) and self.reVar.match(refStatement[-1]):
                    isRedundant = True
                    break
        return isRedundant

    def singleFactPerObject( self, func_name, obj_name, statements ):
        count = 0
        for s in statements:
            if s[0] == func_name and s[1] == obj_name:
                count += 1
        return count <= 1

    # methods is a list of operation data [ name, arg1, ..., argN, return ]
    # build coefficient matrix A and dependent variable list b from statements
    # TODO: Support more operations (currently only supports substraction)
    def validateNumericStatements(self, statements, methods, lh, objInstances, valid_instances=None ):
        a = []
        b = []
        self.reVar = re.compile('v([0-9]+)')
        equalities = {}

        # count up variables used in relievant statements
        varSet = set()
        numStatements = 0
        for s in statements:
            # add variables in substraction ops
            if s[0] == '-':
                numStatements += 1
            # keep track of any equalities
            elif isinstance(s[-1],str):
                varMatch = self.reVar.match(s[-1])
                noVarsInParams = not any([self.reVar.match(var) for var in s[1:-1]])
                if varMatch and noVarsInParams:
                    key = ' '.join(s[:-1])
                    if key not in equalities:
                        equalities[key] = set()
                    equalities[key].add(s[-1])

            # add vars to set
            for var in s[1:]:
                if isinstance(var,str) and self.reVar.match(var):
                    varSet.add(var)

        vars = {var : None for var in varSet}
        varNum = len(vars)

        varNum += 1

        row = 0
        for s in statements:
            if s[0] == '-':
                # A - B = C
                a.append([0] * varNum)
                resultValue = 0

                # A
                if isinstance(s[1],int):
                    resultValue -= s[1]
                else:
                    varMatch = self.reVar.match(s[1])
                    if varMatch:
                        idx = int(varMatch.group(1))-1
                        a[row][idx] = 1
                # B
                if isinstance(s[2],int):
                    resultValue += s[2]
                else:
                    varMatch = self.reVar.match(s[2])
                    if varMatch:
                        idx = int(varMatch.group(1))-1
                        a[row][idx] = -1

                # C
                if isinstance(s[3],int):
                    resultValue += s[3]
                else:
                    varMatch = self.reVar.match(s[3])
                    if varMatch:
                        idx = int(varMatch.group(1))-1
                        a[row][idx] = -1

                b.append(resultValue)

                row += 1

        # add any implied equalities
        if varNum > 2:
            for key,value in equalities.items():
                valueList = list(value)
                if len(valueList) > 1:
                    varMatch = self.reVar.match(valueList[0])
                    aIdx = int(varMatch.group(1))-1

                    for var in valueList[1:]:
                        equality = [0] * varNum
                        equality[aIdx] = 1

                        varMatch = self.reVar.match(var)
                        bIdx = int(varMatch.group(1))-1
                        equality[bIdx] = -1
                        a.append(equality)
                        b.append(0)
                        numStatements += 1

        # determine if ANY of the possiblities have solutions
        anySolution = True

        # iterate on all possible parameters for the action
        # add equalities from the current state
        contextPossiblities = []

        if lh is not None:
            countValidPerms = 0
            for params in product(*[objInstances[k] for k in self.actionParameters]):
                paramDict = dict(zip(self.actionParameters,params))
                paramPossiblities = []
                for s in statements: 
                    if s[0] != '-' and isinstance(s[-1],str) and isinstance(s[1],str):
                        ss = self.substitute(s,paramDict)
                        obj = ss[1]
                        varMatch = self.reVar.match(ss[-1])
                        noVarsInParams = not any([self.reVar.match(var) for var in ss[1:-1]])
                        if varMatch and noVarsInParams:
                            vIdx = int(varMatch.group(1))-1
                            val = lh.get_value(ss[0],ss[1],*ss[2:-1])
                            if isinstance(val,int):
                                equality = [0] * varNum
                                equality[vIdx] = 1

                                paramPossiblities.append([ss,equality,val])
                    elif s[0] == 'at' and isinstance(s[-1],bool) and s[-1] == True and isinstance(s[1],str):
                        ss = self.substitute(s,paramDict)
                        obj = ss[1]
                        varMatchA = self.reVar.match(ss[2])
                        varMatchB = self.reVar.match(ss[3])
                        if varMatchA and varMatchB:
                            vIdxA = int(varMatchA.group(1))-1
                            vIdxB = int(varMatchB.group(1))-1
                            params = lh.find_params_with_value('at',ss[1],True)
                            if len(params) > 0:
                                sa,sb = params[0].split(',')
                                equalityA = [0] * varNum
                                equalityB = [0] * varNum
                                equalityA[vIdxA] = 1
                                equalityB[vIdxB] = 1
                                paramPossiblities.append([ss,equalityA,int(sa)])
                                paramPossiblities.append([ss,equalityB,int(sb)])

                    elif isinstance(s[1],str):
                        # pass through with zero equation for use in
                        # compiling the full context later
                        ss = self.substitute(s,paramDict)
                        equality = [0] * varNum
                        equality[-1] = 1
                        paramPossiblities.append([ss,equality,0])
                if anySolution and len(paramPossiblities) != 0:
                    contextPossiblities.append(paramPossiblities)
                elif not anySolution:
                    break

        if anySolution:
            for cp in contextPossiblities:
                lenCP = len(cp)
                pNumStatements = numStatements + lenCP
                context_instance,aPart,bPart = zip(*cp)
                pA = a[:] + list(aPart)
                pB = b[:] + list(bPart)

                if pNumStatements < 2:
                    anySolution = True
                    if valid_instances is not None:
                        valid_instances.append(context_instance)
                    else:
                        break

                # find least-squares solution
                solution = np.linalg.lstsq(np.array(pA),np.array(pB),rcond=None)[0]

                # check that solution is exact
                anySolution = True
                for i in range(pNumStatements):
                    if not np.isclose(sum([solution[j] * pA[i][j] for j in range(varNum)]),pB[i]):
                        anySolution = False
                        break

                if valid_instances is not None:
                    valid_instances.append(context_instance)
                elif anySolution:
                    break

        return anySolution

    # return copy where 
    # s'[i] = p[s[i]] when s[i] in p
    # s'[i] = s[i]    otherwise
    def substitute(self, s, p ):
        q = list(s)
        for i,e in enumerate(s):
            if e in p:
                q[i] = p[e]
        return q

    # checks if a statement has any working variables
    def hasVars(self, s ):
        return any([self.reVar.match(ele) for ele in s if isinstance(ele,str)])

    # takes a generic context 
    # and returns all parameters for
    # which the context is valid
    # based on the current state
    # ignores statements with variables
    def getValidSubstitations(self, lh, gc, objInstances ):
        validSubs = { ac : set() for ac in self.actionParameters }
        # for every possible set of action parameters
        for params in product(*[objInstances[k] for k in self.actionParameters]):
            paramDict = dict(zip(self.actionParameters,params))

            isValid = True
            for gs in gc:
                # ignore statements with variables (incomplete information)
                if self.hasVars(gs):     
                    continue
                q = self.substitute(gs,paramDict)
                if not lh.query_facts(q[0],q[1],q[-1],*q[2:-1]):
                    isValid = False
                    break
            if isValid:
                for key,val in paramDict.items():
                    if key not in validSubs:
                        validSubs[key] = set()
                    validSubs[key].add(val)
        return validSubs

    # takes a generic statement gs
    # and looks if any instance of this statement
    # is valid for the passed state object lh
    def validateContext(self, lh, gs, objInstances ):
        statements = [gs]
        instances  = []
        for objName,objList in objInstances.items(): 
            for s in statements:
                idxes = [i for i,ele in enumerate(s) if ele == objName]
                numOccur = len(idxes)
                if numOccur == 0:
                    instances.append(s)
                    continue
                for p in permutations(objList,numOccur):
                    query = list(s)
                    for i,instName in zip(idxes,p):
                        query[i] = instName
                    instances.append(query)
            statements = instances
            instances = [] 

        for s in statements:
            if lh.query_facts(s[0],s[1],s[-1],*s[2:-1]):
                return True
        return False

    # loads the state from file into the logic handler
    def loadState(self, stateFile ):
        lh = LogicHandler()
        reNum = re.compile('^-?[0-9]+$')
        with open(stateFile) as f:
            facts = f.readlines()
            for fact in facts:
                fact = fact.rstrip()
                params = fact.split(',')
                if len(params) >= 3: # func,obj,value
                    func,obj = params[0], params[1]
                    params = params[2:]
                    for i in range(len(params)):
                        if reNum.match(params[i]):
                            params[i] = int(params[i])
                        elif params[i] == 'true':
                            params[i] = True
                        elif params[i] == 'false':
                            params[i] = False
                    lh.assert_fact(func,obj,params[-1],*params[:-1])
        return lh

    # checks if to contexts are identical
    def contextsEqual(self, a, b ):
        equal = True
        la = len(a)
        lb = len(b)
        if la == lb:
            for i in range(la):
                lsa = len(a[i])
                lsb = len(b[i])
                if lsa == lsb:
                    for j in range(lsa):
                        if a[i][j] != b[i][j]:
                            equal = False
                            break
                else:
                    equal = False
                if not equal:
                    break
        else:
            equal = False
        return equal

    # builds a statement from data and a permutation
    # of the objects and working variables
    def getStatement(self, method, perm, slots, objects, variables ):
        newVarCount = 0
        l = [method]

        if "op" in self.methods[method]:
            l[0] = self.methods[method]["op"]

        for j,idx in enumerate(perm):
            n = len(self.objects[slots[j]])
            m = len(variables[slots[j]])
            if idx < n:
                # place object instance or constant in slot
                l.append(self.objects[slots[j]][idx])
            elif idx < (n+m):
                # place existing variable in slot
                l.append(variables[slots[j]][idx-n][0])
                variables[slots[j]][idx-n][1] += 1
            elif idx == n+m:
                # place new variable in slot
                newVarCount += 1
                obj = self.varFormat % (self.totalCountDict(variables) + 1)
                variables[slots[j]].append([obj,1])
                l.append(obj)
        return tuple(l), newVarCount

    # a context is complete if all 
    # of the variables reference are
    # needed to traverse from methods
    # not present in the ops list
    # to other such methods
    def complete(self, context, ops ):
        V = {}
        noOps = []
        for i,s in enumerate(context):
            isOp = s[0] in ops
            hasVars = False
            for j,v in enumerate(s[1:]):
                isOutput = j == (len(s)-1)
                if isinstance(v,str) and self.reVar.match(v):
                    hasVars = True
                    ele = {'name' : v, 'isop' : isOp, 'sidx' : i, 'visited' : False, 'needed' : False}
                    if v not in V:
                        V[v] = []
                    V[v].append(ele)
            if not isOp and hasVars:
                noOps.append(i)

        ls = len(noOps)
        if ls == 0:
            return True
        elif ls == 1:
            return False

        # start at every non-op and traverse until we reach another non-op
        # if some statements with variables have never been traversed
        # there is pointless work being done
        for i in range(ls):
            sIdx = noOps[i]

            # add variables from starting statements
            children = []
            for varName,refList in V.items():
                for ref in refList:
                    if ref['sidx'] == sIdx:
                        ref['visited'] = True
                        children.append(ref)

            foundSink = False
            while len(children) != 0 and not foundSink:
                child = children[0]
                children = children[1:]
                for ref in V[child['name']]:
                    if not ref['visited']:
                        ref['visited'] = True
                        child['needed'] = True
                        if ref['sidx'] != sIdx and not ref['isop']:
                            foundSink = True
                        else:
                            #child['needed'] = True
                            children.append(ref)
                            # add others variables in variable's statement
                            for varName,refList in V.items():
                                for ref2 in refList:
                                    if not ref2['visited'] and ref2['sidx'] == ref['sidx']:
                                        ref2['visited'] = True
                                        children.append(ref2)

            for ref in chain(*V.values()):
                ref['visited'] = False

        isComplete= True
        for varName,refList in V.items():
            if not any([ref['needed'] for ref in refList]):
                isComplete = False
                break

        return isComplete

    # looks for identical context with different variable orderings
    # assumes variables are always defined in the sequence v1 v2 ...
    def redundant(self, context, allContexts ):
        isRedundant = False
        varDict = {}

        # get the references within the context of each variables
        for i,s in enumerate(context):
            for j,ele in enumerate(s):
                if isinstance(ele,str) and self.reVar.match(ele):
                    if ele not in varDict:
                        varDict[ele] = []
                    varDict[ele].append((i,j))

        numVars = len(varDict)

        if numVars <= 1:
            for c in allContexts:
                if self.contextsEqual(context,c):
                    isRedundant = True
                    break 
        else:
            for c in allContexts:
                for p in permutations(varDict.keys()):
                    refContext = self.copyContext(context)
                    for varName,idxList in zip(p,varDict.values()):
                        for i,j in idxList:
                            refContext[i][j] = varName
                    if self.contextsEqual(refContext,c):
                        isRedundant = True
                        break

        return isRedundant

    def save_contexts(self,contexts,filename):
        with open(filename,'w') as fout:
            for c in contexts:
                fout.write(':'.join([self.statementToCSV(s) for s in c]) + '\n')

    def load_contexts(self,filename):
        contexts = []
        with open(filename) as fin:
            for context_str in fin.readlines():
                context_str = context_str.rstrip()
                context_list = []
                for str_statement in context_str.split(':'):
                    str_elements = str_statement.split(',')
                    # each statement expect to contain at least three elements
                    # function_name,object_type,value
                    # optionally there can be n parameters before the value
                    if len(str_elements) >= 3:
                        func,obj = str_elements[0], str_elements[1]
                        params = str_elements[2:]
                        for i in range(len(params)):
                            if self.re_num.match(params[i]):
                                params[i] = int(params[i])
                            elif params[i] == 'true':
                                params[i] = True
                            elif params[i] == 'false':
                                params[i] = False
                        context_list.append([func,obj] + params)
                contexts.append(context_list)
        return contexts


    def generateContexts(self, numStatements, filename = None):
        logging.info("Generating contexts....")
        contexts = []
        variables = { key : [] for key in self.objects.keys() }
        self.nextStatement(0,numStatements,variables,[],contexts)
        if filename is not None:
            self.save_contexts(contexts,filename)
        return contexts
  
    def nextStatement(self, depth, numStatements, variables, statements, allPossiblities ):
        if depth < numStatements:
            for method, mdata in self.methods.items():      
                slots = mdata["args"] + [mdata["return"]]
                numSlots = len(slots)
                slotSizes = [range(len(self.objects[slots[i]]) + len(variables[slots[i]]) + 1) for i in range(numSlots)]

                for perm in product(*slotSizes):
                
                    # create statement and test
                    vs = self.copyListListDict(variables)
                    statement,newVarCount = self.getStatement(method,perm,slots,self.objects,vs)

                    # Requirements for a valid statement:
                    # - statement is not in existing statements
                    # - there is at least one non constant parameter or return value
                    # - creates at most two new variables
                    # - if this is the last statement, all variables must have at least two references between this statement and the existing statements
                    # - parameters and return value are unique
                    # - seperate variables are not assigned to the same value
                    # - new variables not of type player, tile, bool, int_constant or object
                    if not statement in statements and \
                       not self.contradict(statement,statements) and \
                       not self.allConstant(statement) and \
                       newVarCount <= 2 and \
                       self.uniqueArgsAndRet(statement) and \
                       not self.redundantVar(statement,statements) and \
                       len(vs["player"]) == 0 and \
                       len(vs["tile"]) == 0 and \
                       len(vs["bool"]) == 0 and \
                       len(vs["truth"]) == 0 and \
                       len(vs["int_constant"]) == 0 and \
                       len(vs["object"]) == 0 and \
                       len(vs["item"]) == 0:

                        ss = statements[:]
                        ss.append(statement)
                        self.nextStatement(depth+1,numStatements,vs,ss,allPossiblities)
        else:
            sstr = ''
            statements = sorted(statements, key=lambda x: x[0])

            if self.complete(statements,['-']) and \
               not self.redundant(statements,allPossiblities) and \
               (self.totalCountDict(variables) == 0 or self.allVarsAtLeastTwice(variables)) and \
               self.atLeastOneFuncWithObjectParam('player',statements) and \
               self.singleFactPerObject('at', 'player', statements) and \
               self.singleFactPerObject('at', 'cell', statements):
                allPossiblities.append(statements)

    def filterByState(self,lh,allPossiblities):
        filteredList = []
        for statements in allPossiblities:
            validSubs = self.getValidSubstitations(lh,statements,self.objInstances)
            if self.totalCountDict(validSubs) != 0 and self.validateNumericStatements(statements,self.methods,lh,validSubs):
                filteredList.append(statements)
        return filteredList

    def context_to_state(self,statements,lh):
        instances = []
        validSubs = self.getValidSubstitations(lh,statements,self.objInstances)
        if self.totalCountDict(validSubs) != 0:
            self.validateNumericStatements(statements,self.methods,lh,validSubs,valid_instances=instances)
        return instances


if __name__ == "__main__":
    cg = ContextGenerator()
    lh = None
    if len(sys.argv) > 1:
        lh = LogicHandler()
        lh.load_state( sys.argv[1] )

    cg.generateContexts(4,'context_new4.txt')
    #allPossiblities = cg.load_contexts('context3.txt')
    #if lh is not None:
    #    allPossiblities = cg.filterByState(lh,allPossiblities)
    #cg.save_contexts(allPossiblities,'context3_load.txt')


