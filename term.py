def get_arg_types(pred:str):
    move_list=["north","south","east","west","northwest","northeast","southeast","southwest"]
    if pred in move_list or pred == 'get':
        return ['cell']
    elif pred == 'cell':
        return ['cell']
    elif pred == 'deepwater':
        return ['cell']
    elif pred == 'at' or pred == 'not at':
        return ['cell', 'xcoord', 'ycoord']
    elif pred == 'agentat' or pred == 'not agentat':
        return ['cell']
    elif pred == 'wall' or pred == 'not wall':
        return ['cell']
    elif pred == '=':
        #if '-' in self.args or '+' in self.args:
        return ['int', 'int', 'operator', 'constant']
        #else:
            #return ['int', 'int']
    elif pred == 'throw': #####################Non-Deterministic
        return ['cell', 'xcoord','ycoord']
    elif pred == 'get':
        return ['cell']
    elif pred == 'open_door': #TODO:Implement Below
        return ['cell']
    elif pred == 'closed_door':
        return ['cell']
    elif pred == 'drop':
        return ['cell']
    elif pred == 'wait':
        return ['cell']
    elif pred == 'itemtype':
        return ['item_type']
    elif pred == 'inv_item':
        return ['item_type', 'quantity']
    elif pred == 'inv_id':
        return ['id', 'item']
    elif pred == 'item':
        return ['cell','item_type','quantity']

class Term:

    def __init__(self,predicate_str:str,arg_strs:[str]):
        self.pred_str = predicate_str
        self.args = arg_strs
        self.arg_types = None
        self.human_readable_args = []

        self._set_arg_types(predicate_str)

    def get_pred_str(self):
        return self.pred_str

    def _set_arg_types(self, pred:str):
        #print("pred is {}".format(pred))
        self.arg_types=get_arg_types(pred)


    def set_human_readable_args(self, args:[str]):
        #print("args={}".format(args))
        assert len(args) == len(self.arg_types)
        self.human_readable_args = args

    def substitute_args(self,curr:[str],new:[str]):
        new_args = []
        for a in self.human_readable_args:
            new_args.append(curr.index(a))
        self.human_readable_args = new_args

    def __eq__(self, other):
        return self.pred_str == other.pred_str and self.human_readable_args == other.standardized_args

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        upper_args = map(lambda s: s.upper(), self.args)
        if self.pred_str == '=':
            return '{} = {} {} {}'.format(*upper_args)
        else:
            s = '{}('.format(self.pred_str)
            for a in upper_args:
                s += '{},'.format(a)
            s = s[0:-1] + ')'
            return s

    def __repr__(self):
        return self.__str__()