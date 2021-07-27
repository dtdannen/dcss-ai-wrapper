# This file takes json messages of the state and translates them into Answer Set Programming style reltional facts.

import re


class RelationalFact:

    def __init__(self, pred=None, args=[], argtypes=[]):
        if pred and len(args) >= 1 and len(args) == len(argtypes):
            self.pred = pred
            self.args = args
            self.argtypes = argtypes
        else:
            raise Exception("Problem instantiating Relational Fact: {}({}:{})".format(pred, args, argtypes))

    def __str__(self):
        s = self.pred+"("
        for a in self.args:
            s += str(a)+', '
        s = s[0:-2]  # remove the last comma
        s += ')'
        return s


def parse_message(js):
    print('js is {}'.format(js))
    if js['msg'] == 'player':
        return parse_player_message(js)

    if js['msg'] == 'map':
        return parse_map_message(js)

    if js['msg'] == 'txt' and js['id'] == 'menu_txt' and 'lines' in js.keys():
        return parse_skill_menu(js)

    return []


def parse_player_message(js):

    r_facts = []

    # the following json identifiers are simple to parse, don't do anything fancy and use type 'str'
    simple_keys_type_str = ['name','title','species','god','place','quiver_item','unarmed_attack',]
    # the following json identifiers are simple to parse, don't do anything fancy and use type 'int'
    simple_keys_type_int = ['real_hp_max','ev','xl','noise','piety_rank','hp','hp_max','real_hp_max','poison_survival','ac','ev','str','str_max','int','int_max','dex','dex_max','depth','time', 'turn']
    # the following json identifiers are simple to parse, don't do anything fancy and use type 'float'
    # simple_keys_type_float = []

    # process all simple facts first
    for k in simple_keys_type_str:
        if k in js.keys():
            r_facts.append(RelationalFact('player'+k[0:1].upper()+k[1:], [js[k]], ['str']))
    for k in simple_keys_type_int:
        if k in js.keys():
            r_facts.append(RelationalFact('player' + k[0:1].upper()+k[1:], [js[k]], ['int']))

    # now process complex facts
    # 1. Player position
    player_x = js['pos']['x']
    player_y = js['pos']['x']
    r_facts.append(RelationalFact('tileHasPlayer', [player_x, player_y],['int','int']))

    # 2. Player inventory
    inventory = js['inv']
    ids_to_names = {}  # helps knowing names of equipped items
    for id in inventory.keys():
        name = inventory[id]['name']
        base_type = inventory[id]['base_type']
        quantity = inventory[id]['quantity']
        r_facts.append(RelationalFact('inventory',[id,name,base_type,quantity],['int','str','int','int']))
        ids_to_names[id] = name

    # equipped items
    equipped = js['equip']
    for slot, item_id in equipped.items():
        r_facts.append(RelationalFact('equipped',[ids_to_names[str(item_id)]], ['str']))

    return r_facts

# Parse Map Data


def parse_map_message(js):
    r_facts = []

    items = ['0','(',')','[','?','%','&',':','/','|','!','=','"','}','$']

    running_x = None
    running_y = None

    if 'cells' in js.keys():
        for cell in js['cells']:
            primary_tile_feature = None
            if 'x' in cell.keys():
                running_x = cell['x']
            elif running_x:
                running_x = str(int(running_x)+1)

            if 'y' in cell.keys():
                running_y = cell['y']
            elif running_y:
                running_y = str(int(running_y) + 1)

            if running_x and running_y:
                if 'mon' in cell.keys():
                    monster_data = cell['mon']
                    m_id = monster_data['id']
                    m_name = monster_data['name']
                    r_facts.append(RelationalFact('tileHasMonster', [running_x, running_y, m_id, m_name], ['int','int','int','str']))

                if 'g' in cell.keys():
                    primary_tile_feature = cell['g']

                if primary_tile_feature in items:
                    r_facts.append(RelationalFact('tileHasItem',[running_x, running_y], ['str', 'str']))
                else:
                    human_readable_tile_feature = None
                    if primary_tile_feature == '#':
                        human_readable_tile_feature = 'wall'
                    elif primary_tile_feature == '.':
                        human_readable_tile_feature = 'empty'
                    elif primary_tile_feature == '@':
                        human_readable_tile_feature = 'player_location'
                    elif primary_tile_feature == '>':
                        human_readable_tile_feature = 'stairs_down'
                    elif primary_tile_feature == '<':
                        human_readable_tile_feature = 'stairs_up'

                    if human_readable_tile_feature:
                        r_facts.append(RelationalFact('tileHasFeature', [running_x, running_y, human_readable_tile_feature], ['int', 'int', 'str']))
    return r_facts

def parse_skill_menu(js):
    r_facts = []
    is_skill_costs = False
    is_skill_train = False
    for line in js['lines'].keys():
        if 'SkillName' in line and 'Cost' in line:
            # header
            is_skill_costs = True
            is_skill_train = False
        elif 'SkillName' in line and 'Train' in line:
            # header
            is_skill_costs = False
            is_skill_train = True
        else:
            line = re.sub('<.*?>', '', line)
            parts = re.sub('\s+', ' ', line).strip().split(' ')
            if len(parts) >= 6:
                skill_1_id = parts[0]
                skill_1_priority = parts[1]  # either - (nothing), + (low), or * (high)
                skill_1_name = parts[2]
                skill_1_level = parts[3]
                skill_1_value = parts[4]  # either cost or training percentage
                skill_1_apt = parts[5]
                all_skill_1_data = [skill_1_id, skill_1_priority, skill_1_name, skill_1_level, skill_1_value, skill_1_apt]
                all_skill_1_data_types = ['int','int','str','double','double','double']
                if is_skill_costs:
                    r_facts.append(RelationalFact('playerSkillCost', all_skill_1_data, all_skill_1_data_types))
                elif is_skill_train:
                    r_facts.append(RelationalFact('playerSkillTrain', all_skill_1_data, all_skill_1_data_types))


