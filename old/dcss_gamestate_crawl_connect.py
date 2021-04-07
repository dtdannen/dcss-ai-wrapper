'''
This file stores the states class that is used to keep track of
the current states of the dcss game

TODO:
    - should this remain a seperate object from DCSSProvider?
    - stronger way to find g lists for sets of objects (eg monsters)
'''

import logging
import re
import threading
import time
import traceback
import sys

from map import Map

class Cell():
    '''
    Stores a cell of the map
    '''

    key_list = ['x','y','f','g','t','mf','col']

    def __init__(self, vals):
        for key,value in vals.items():
            if key in self.key_list:
                self.__dict__[key] = value

    def exists(self, key):
        return key in self.__dict__

    def combine(self, new_cell):
        for key in self.key_list:
            if key in new_cell.__dict__:
                if key in self.__dict__ and isinstance(new_cell.__dict__[key],dict):
                    # combine dictionary elements
                    for subkey,subvalue in new_cell.__dict__[key].items():
                        self.__dict__[key][subkey] = subvalue
                else:
                    self.__dict__[key] = new_cell.__dict__[key]

    def __str__(self):
        if self.g and len(self.g) >= 1:
            return g
        pass


class GameState():

    ID = 0

    def __init__(self):
        # states is just a dictionary of key value pairs
        self.state = {}

        # only states information we care about
        self.state_keys = ['hp', 'hp_max', 'depth', 'light', 'god', 'mp', 'species', 'dex', 'inv', 'cells', 'species']

        self.letter_to_number_lookup = { c : i for i,c in enumerate('abcdefghi') }

        self.map_obj_player_x = None  # this is the x of the map_obj where the player is
        self.map_obj_player_y = None  # this is the y of the map_obj where the player is

        self.items = ['0','(',')','[','?','%','&',':','/','|','!','=','"','}','$']

        # all possible monster glyphs (gathered by gather_crawl_glyphs.py from mon-data.h)
        self.monsters = ['t', 'V', 'r', 'H', 'w', 'C', 'd', 'P', 'B', 'l', 'O', 'f', 'N', '6',
                         'S', 'h', '3', 'q', '{', 'L', 'Q', 'E', '*', 'b', 'X', '5', 'g',  #  '@'  - this is also the entrance glyph...
                         'G', '&', 'e', 'z', 'x', 'a', ';', '8', 'k', 'o', 'y', 'm', '9',  # '(' - stone?
                         'D', 'A', 'c', '2', 'Z', 'n', 'T', 'u', 'i', 'K', 'v', 'M', 'R',
                         '1', 'p', 'Y', 'J', '4', 'F', 'W']

        self.map_obj = Map()

        self.inventory = {}

        self.max_turn = 0
        self.curr_timestamp = 0

        self.menu_items = None

        self.last_recorded_movement = ''

        self.player_dead = False

        self.cells = []

        self.pddl_objects = set()

        self.asp_str = '' # facts that don't change when an action is executed
        self.asp_comment_str = '' # comments associated with asp
        self.player_cell = None
        self.training_asp_str = '' # facts that do change
        self.all_asp_cells = None # number of cell objects

        self.messages = {} # key is turn, value is list of messages received on this turn in order,
                           # where first is oldest message

        self.plural_re = re.compile("(potion|scroll|stone|ration)s")   
        self.bonus_re = re.compile("(\+|-)?[0-9]+")
        self.used_re = re.compile("\((worn|in hand|quivered)\)")

        self.var_re = re.compile("[a-z]+")
        self.int_re = re.compile("-?[0-9]+")

        self.asp_statement_re = re.compile('([a-z_]+)\(([^\)]+)\)\.')

        # intiliaze values of states variables
        for k in self.state_keys:
            self.state[k] = None

        self.id = GameState.ID
        GameState.ID+=1

    def update(self, msg_from_server):
        try:
            self._process_raw_state(msg_from_server)
            self.compute_asp_str()
            self.compute_pddl_data()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise Exception("Something went wrong")
        
    def _process_raw_state(self, s, last_key=''):
        if isinstance(s, list):
            for i in s:
                self._process_raw_state(i)
                
        elif isinstance(s, dict):
            for k in s.keys():
                if k == 'cells':
                    cells_data = self.get_cell_data(s[k])
                    self.update_map_obj(cells_data)
                elif k == 'messages':
                    self.process_messages(s[k])
                elif k == 'inv':
                    self.process_inv(s[k])
                elif k == 'items':
                    self.menu_items = s[k]

                last_key = k

                if k in self.state_keys:
                    self.state[k] = s[k]
                elif isinstance(s[k], list):
                    for i in s[k]:
                        self._process_raw_state(i)
                elif isinstance(s[k], dict):
                    self._process_raw_state(s[k])
                else:
                    pass
        else:
            pass

    def process_messages(self, data):

        # begin: this is just for html stripping
        from html.parser import HTMLParser
        class MLStripper(HTMLParser):
            def __init__(self):
                self.reset()
                self.strict = False
                self.convert_charrefs = True
                self.fed = []

            def handle_data(self, d):
                self.fed.append(d)

            def get_data(self):
                return ''.join(self.fed)

        def strip_tags(html):  
            s = MLStripper()
            s.feed(html)
            return s.get_data()

        # end: html stripping code

        #self.curr_timestamp = time.time()

        self.curr_timestamp = int(time.time())

        # need to store the message for current location so I can get quanitity of food items and stones for pickup action
        for m in data:
            turn = m['turn']
            message_only = strip_tags(m['text'])
            if turn in self.messages.keys():
                if self.curr_timestamp in self.messages[turn]:
                    self.messages[turn][self.curr_timestamp].append(message_only)
                else:
                    self.messages[turn][self.curr_timestamp] = [message_only]
            else:
                self.messages[turn] = { self.curr_timestamp : [message_only]}

            if turn > self.max_turn:
                self.max_turn = turn

        for msg in self.messages[turn][self.curr_timestamp]:
            if 'You die...' in msg:
                self.player_dead = True
                break

    def get_key_from_item_name(self,name):
        #name = ''.join([i for i in name if not i.isdigit() and not i in ['+','-']])

        name = name.strip()

        name = self.bonus_re.sub('',name)
        name = self.used_re.sub('',name)
        name = name.replace(' ','')
        name = self.plural_re.sub("\\1", name)

        return name

    def process_inv(self,data):
        for inv_id in data.keys():

            if 'name' in data[inv_id]:
                name = data[inv_id]['name']
                name = self.get_key_from_item_name(name)

                quantity = data[inv_id]['quantity']
                self.inventory[inv_id] = [name, quantity]
            elif 'quantity' in data[inv_id] and data[inv_id]['quantity'] == 0 and inv_id in self.inventory:
                # remove inventory item
                del self.inventory[inv_id]

    def get_cell_data(self, cells):
        cell_data = []
        curr_x = None
        curr_y = None
        num_at_signs = 0
        if cells:
            for i_dict in cells:
                if 'x' in i_dict.keys() and 'y' in i_dict.keys() and 'g' in i_dict.keys():
                    curr_x = i_dict['x']
                    curr_y = i_dict['y']
                    cell_data.append([i_dict['x'],i_dict['y'],Cell(i_dict)])
                elif 'x' in i_dict.keys() and 'y' in i_dict.keys():
                    ''' Sometimes there is only x and y and no g, often at the beginning of the cells list'''
                    curr_x = i_dict['x']
                    curr_y = i_dict['y']
                else:
                    curr_x += 1
                    try:
                        i_dict['x'] = curr_x
                        i_dict['y'] = curr_y
                        cell_data.append([curr_x,curr_y,Cell(i_dict)])
                        if 'g' in i_dict.keys() and len(i_dict['g']) > 0 and '@' in str(i_dict['g']):
                            num_at_signs+=1
                            if num_at_signs > 1:
                                logging.debug("Whoa, too many @ signs, here's the cell data")
                                logging.debug(cells)
                    except:
                        # TODO: test this more robustly
                        #        right now I think that if this triggers, it means
                        #        the player didn't move, so just keep old data and don't
                        #        update
                        
                        logging.warning("Failure with cell data: "+str(i_dict))
                        print("curr_x={0} and curr_y={1}".format(curr_x,curr_y))
                        print("Cells are "+str(cells))
                        input("Press enter to continue")

            return cell_data

    def update_map_obj(self, cells_data):
        '''
        Updates the map object with new cell data
        Cells are currently only added if they have non-empty g values
        But Cell data might not have a new non-empty g value

        :param cells_data:
        '''

        at_sign_count = 0 # we should only see the @ in one location

        if not cells_data:
            # We don't always get cell data, if so, return
            return

        for xyd_cell in cells_data:
            x = int(xyd_cell[0])
            y = int(xyd_cell[1])
            cell = xyd_cell[2]

            map_obj_x = x
            map_obj_y = y

            non_empty_g = cell.exists('g') and len(cell.g) > 0

            if non_empty_g and '@' == cell.g:

                self.map_obj_player_x = map_obj_x
                self.map_obj_player_y = map_obj_y

                at_sign_count+=1
                if at_sign_count > 1:
                    logging.warning("Error, multiple @ signs - let's debug!")
                    time.sleep(1000)

            if self.map_obj.exists(map_obj_x, map_obj_y):
                cell_obj = self.map_obj.get(map_obj_x, map_obj_y)
                cell_obj.combine(cell)
                self.map_obj.set(map_obj_x, map_obj_y, cell_obj)
            elif non_empty_g:
                self.map_obj.set(map_obj_x, map_obj_y, cell)

    def get_player_xy(self):
        return (self.map_obj_player_x,self.map_obj_player_y)

    def get_asp_str(self):
        return self.asp_str

    def get_pddl_init_str(self):
        return self.pddl_init_str

    def get_pddl_object_list(self):
        return list(self.pddl_objects)

    def get_asp_comment_str(self):
        return self.asp_comment_str

    def get_training_asp_str(self):
        return self.training_asp_str

    def get_player_cell(self):
        return self.player_cell

    def compute_pddl_data(self):
        self.pddl_init_str = ''
        self.pddl_objects = set()

        self.pddl_cells = []
        self.pddl_numbers = []
        self.pddl_items = []

        min_num = 1000
        max_num = -1000

        # find number range
        for asp_statement in self.asp_str.split('\n'):
            m = self.asp_statement_re.match(asp_statement)
            if m:
                name = m.group(1)
                params = m.group(2).split(',')

                for p in params:
                    if self.int_re.match(p):
                        int_val = int(p)
                        if int_val < min_num:
                            min_num = int_val
                        if int_val > max_num:
                            max_num = int_val

        # add number relationships
        self.pddl_num_vars = {}

        for i in range(max_num-min_num+1):
            name = 'n%d' % (i+1)
            self.pddl_num_vars[str(i + min_num)] = name
            self.pddl_objects.add(name)  
            self.pddl_numbers.append(name)    

        num_range = max_num-min_num      

        for i in range(num_range):
            self.pddl_init_str += '(is_one_minus n%s n%s)\n' % (i+1,i+2)

        for asp_statement in self.asp_str.split('\n'):
            m = self.asp_statement_re.match(asp_statement)
            if m:
                name = m.group(1)
                params = m.group(2).split(',')

                out_params = []

                for p in params:
                    if self.var_re.match(p):
                        self.pddl_objects.add(p)
                        out_params.append(p)
                    if self.int_re.match(p):
                        if p in self.pddl_num_vars:
                            out_params.append(self.pddl_num_vars[p])

                if name == 'cell':
                    self.pddl_cells.append(params[0])
                elif name == 'itemtype':
                    self.pddl_items.append(params[0])

                if name != 'cell' and name != 'itemtype' and name != 'item':
                    self.pddl_init_str += '(%s %s)\n' % (name,' '.join(out_params))

    def compute_asp_str(self, filename=None):
        num_asp_cells = []
        asp_comment_str = '%'

        if filename:
            pass # TODO write to file

        bg_asp_str = ''
        training_asp_str = ''

        # go through all the map data and add cells, xy coordinates, and any special objects
        cell_id = 1
        FOUND_PLAYER = False
        player_cell = None

        bound_data = self.map_obj.get_bounds()

        if bound_data is None or bound_data[0][0] is None or bound_data[0][1] is None or bound_data[1][0] is None or bound_data[1][1] is None:
            logging.debug("Map has no bounds, cannot compute asp str")
            return 

        row_length = bound_data[1][1]-bound_data[0][1]

        x = None
        y = None

        self.cells = []

        for cell_coords, cell_data in self.map_obj:
            if x is not None and y is not None:
                last_x,last_y = x,y
            else:
                last_x,last_y = cell_coords

            x,y = cell_coords
            cell = cell_data.g

            # Print blanks for each skipped cell
            # TODO : This calculation is wrong
            num_skipped_cells = (y-last_y-1) * row_length + row_length + (x-bound_data[0][0]) - (last_x - bound_data[0][0])
            for i in range(num_skipped_cells):
                # ignore
                asp_comment_str += "|      |".format(cell_id)
                pass

            bg_asp_str += 'cell(c{0}).\n'.format(cell_id)
            bg_asp_str += 'at(c{0},{1},{2}).\n'.format(cell_id, x, y)
            num_asp_cells.append('c{0}'.format(cell_id))

            if cell == '@':
                bg_asp_str += 'at(p1,{0},{1}).\n'.format(x, y)
                asp_comment_str += "| c{0:0=3d} |".format(cell_id)
                FOUND_PLAYER = True
                player_cell = 'c{0}'.format(cell_id)
            if cell == '#':
                bg_asp_str += 'wall(c{0}).\n'.format(cell_id)
                asp_comment_str += "|#c{0:0=3d}#|".format(cell_id)
            elif cell == '.':
                # do nothing
                asp_comment_str += "| c{0:0=3d} |".format(cell_id)
            elif cell == '\'':
                bg_asp_str += 'open_door(c{0}).\n'.format(cell_id)
                asp_comment_str += "|'c{0:0=3d}$|".format(cell_id)
            elif cell == '+':
                bg_asp_str += 'closed_door(c{0}).\n'.format(cell_id)
                asp_comment_str += "|+c{0:0=3d}$|".format(cell_id)                     
            elif cell == '$':
                bg_asp_str += 'gold(c{0}).\n'.format(cell_id)
                asp_comment_str += "|$c{0:0=3d}$|".format(cell_id)
            elif cell == '(':
                bg_asp_str += 'stone(c{0}).\n'.format(cell_id)
                asp_comment_str += "|(c{0:0=3d}(|".format(cell_id)
            elif cell == '≈':
                bg_asp_str += 'deepwater(c{0}).\n'.format(cell_id)
                asp_comment_str += "|~c{0:0=3d}~|".format(cell_id)
            elif cell == '%':
                bg_asp_str += 'food(c{0}).\n'.format(cell_id)
                asp_comment_str += "|%c{0:0=3d}%|".format(cell_id)
            elif cell == '0':
                # orb
                asp_comment_str += "| c{0:0=3d} |".format(cell_id)
            elif cell == '<':
                # exit
                asp_comment_str += "| c{0:0=3d} |".format(cell_id)
            cell_id += 1

            if cell != '#' or cell != '≈':
                self.cells.append(['c{0}'.format(cell_id),x,y])

            #x += 1
        asp_comment_str+= '\n%' + '+------+' * row_length + '\n%'
        #y += 1

        # objects agent knows about
        # TODO Put this somewhere else more global - probably ought to consider pddl to asp in a nicer implementation of
        # TODO all this
        agent_known_object_types = ['stone', 'ration', 'gold']
        for obj_type in agent_known_object_types:
            bg_asp_str += 'itemtype({}).\n'.format(obj_type)

        # add inventory facts
        object_types = []
        for i in self.inventory.keys():
            name = self.inventory[i][0]

            # name = ''.join([i for i in name if not i.isdigit() and not i in ['+','-']])
            # name = name.strip().replace(' ','')
            # name = name.replace('potions','potion').replace('scrolls','scroll').replace('stones','stone').replace('rations','ration')

            quantity = self.inventory[i][1]

            if name not in object_types:
                object_types.append(name)
                bg_asp_str += 'itemtype({}).\n'.format(name)

            bg_asp_str += 'inv_item({0},{1}).\n'.format(name,quantity)
            bg_asp_str += 'inv_id({0},{1}).\n'.format(i, name)

        # add facts about current tile
        if len(self.messages.keys()) > 0:
            logging.debug("max_turn is {}".format(self.max_turn))
            for m in [msg for timestamp in self.messages[self.max_turn].keys() for msg in self.messages[self.max_turn][timestamp]]:
                logging.debug("a message on turn {} is {}".format(self.max_turn,m))
                if 'You see here a ' in m:
                    for obj_type in agent_known_object_types:
                        if obj_type in m:
                            bg_asp_str += 'item({},{},{}).\n'.format(player_cell, obj_type, 1)

                elif 'You see here ' in m:
                    nums_in_m = list(map(int, re.findall(r'\d+', m)))
                    #logging.debug("nums_in_m is {}".format(nums_in_m))
                    if len(nums_in_m) > 0:
                        quantity = nums_in_m[0]
                        for obj_type in agent_known_object_types:
                            if obj_type in m:
                                bg_asp_str += 'item({},{},{}).\n'.format(player_cell, obj_type, quantity)
                else:
                    pass # just ignore

        self.asp_comment_str = '%Map Picture:\n'+asp_comment_str+'\n'
        self.player_cell = player_cell
        self.asp_str = bg_asp_str
        if FOUND_PLAYER:
            self.training_asp_str = training_asp_str

        self.all_asp_cells = set(num_asp_cells)

    def get_visitable_cells():
        return self.cells

    def get_tiles_around_player_radius_1(self):
        if self.map_obj_player_x is not None and self.map_obj_player_y is not None:
            return self.map_obj.get_adjacent(self.map_obj_player_x,self.map_obj_player_y)
        else:
            return [None] * 8

    def draw_map(self):
        bound_data = self.map_obj.get_bounds()

        row_length = bound_data[1][1]-bound_data[0][1]

        x = None
        y = None

        s = ''
        for cell_coords, cell_data in self.map_obj:
            if x is not None and y is not None:
                last_x,last_y = x,y
            else:
                last_x,last_y = cell_coords

            spot = cell_data.g;
            x,y = cell_coords

            # TODO : This calculation is wrong
            num_skipped_cells = (y-last_y-1) * row_length + row_length + (x-bound_data[0][0]) - (last_x - bound_data[0][0])

            s += ' ' * num_skipped_cells

            spot = cell_data.g;
            if len(spot) != 0:
                s += str(spot)
            else:
                s += ' '

        # add newlines
        # row_count = int(len(s)/row_length)
        # for i in range(row_count):
        #     idx = i*row_length+row_length
        #     s = s[:idx] + '\n' + s[idx:]

    def get_map_obj(self):
        return self.map_obj
        
    # Methods for external states queries

    # returns the quantity of items with passed item_name
    def item_in_inventory(self,item_name):
        inv_letter = None

        for i in self.inventory.keys():
            ref_name = self.inventory[i][0]

            if item_name == ref_name:
                inv_letter = chr(97+int(i))
                break

        return inv_letter

    def get_msg_current_turn(self):
        if self.max_turn in self.messages:
            return [msg for timestamp in self.messages[self.max_turn].keys() for msg in self.messages[self.max_turn][timestamp]]
        else:
            return []

    def get_msg_current_timestamp(self):
        if self.max_turn in self.messages and self.curr_timestamp in self.messages[self.max_turn]:
            return self.messages[self.max_turn][self.curr_timestamp]
        else:
            return []

    # can only move to another cells that:
    # - are empty
    # - contains only an item
    # - has walkable terrain (race dependent)
    # - is an open door
    # - contains only a passageway
    def can_move_direction(self, direction):
        passages = ['>','<']
        walkable_terrain = ['.']
        open_door = '\''

        if self.map_obj_player_x is not None and self.map_obj_player_y is not None:
            cell_data = self.map_obj.get_direction(self.map_obj_player_x,self.map_obj_player_y,direction)
            g = cell_data.g
            return g in walkable_terrain or g in self.items or g in passages or g == open_door
        else:
            return False

    # checks if there is no closed door or wall in the way of an attack
    def can_attack(self,direction):
        non_attackable = ['#','+']
        if self.map_obj_player_x is not None and self.map_obj_player_y is not None:
            cell_data = self.map_obj.get_direction(self.map_obj_player_x,self.map_obj_player_y,direction)
            return cell_data.g in non_attackable
        else:
            return False

    def can_attack_monster(self,direction):
        if self.map_obj_player_x is not None and self.map_obj_player_y is not None:
            cell_data = self.map_obj.get_direction(self.map_obj_player_x,self.map_obj_player_y,direction)
            return cell_data.g in self.monsters 
        else:
            return False

    def can_open_door(self,direction):
        if self.map_obj_player_x is not None and self.map_obj_player_y is not None:
            cell_data = self.map_obj.get_direction(self.map_obj_player_x,self.map_obj_player_y,direction)
            return cell_data.g == '+'
        else:
            return False

    def can_close_door(self,direction):
        if self.map_obj_player_x is not None and self.map_obj_player_y is not None:
            cell_data = self.map_obj.get_direction(self.map_obj_player_x,self.map_obj_player_y,direction)
            return cell_data.g == '\''
        else:
            return False

    def multiple_open_doors(self):
        door_count = 0
        if self.map_obj_player_x is not None and self.map_obj_player_y is not None:
            for cell in self.get_tiles_around_player_radius_1():
                if cell is not None and cell.g == '\'':
                    door_count += 1
                    if door_count > 1:
                        break
        return door_count > 1

    def write_pddl_problem(self, filename, goal_statements):
        obj_str   = ' '.join(self.pddl_objects)
        goal_str  = '\n                '.join(goal_statements)
        problemstr = '''(define (problem dcss-problem) (:domain dcss-domain)
            (:objects
                p1 - player
                %s - cell
                %s - num
                %s - itemtype
            )

            (:init
                (= (steps) 0)
                %s    
            )

            (:goal
                %s
            )

            (:metric minimize(steps))
        )''' % ( ' '.join(self.pddl_cells), ' '.join(self.pddl_numbers), ' '.join(self.pddl_items), self.pddl_init_str, goal_str )

        with open(filename,"w") as f:
            f.write(problemstr)

    def write_pddl_domain(self, filename):
        domainstr = '''(define (domain dcss-domain)
            (:types player cell - object)'''

        domainstr += '''(:requirements :fluents)
            
            (:functions
                (steps)
            )
            
            (:predicates 
                (at ?obj - object ?x - num ?y - num)
                (is_one_minus ?x - num ?x - num)   ; equivalent to a == b - 1
                (inv_id ?id - num ?i - itemtype)
                (inv_item ?i - itemtype ?x - num)
                (wall ?t - cell)
                (stone ?t - cell)
                (open_door ?t - cell)
                (closed_door ?t - cell)
            )
            
            (:action north
                :parameters 
                    (?p1 - player
                     ?t - cell
                     ?u ?v1 ?v2 - num )

                :precondition 
                    (and 
                        (at ?p1 ?u ?v1)
                        (at ?t ?u ?v2)
                        (not (wall ?t))
                        (not (closed_door ?t))
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
                     ?t - cell
                     ?u1 ?u2 ?v1 ?v2 - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (not (closed_door ?t))
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
                     ?t - cell
                     ?u1 ?u2 ?v - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v)
                        (at ?t ?u2 ?v)
                        (not (wall ?t))
                        (not (closed_door ?t))
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
                     ?t - cell
                     ?u1 ?u2 ?v1 ?v2 - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (not (closed_door ?t))
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
                     ?t - cell
                     ?u ?v1 ?v2 - num)

                :precondition 
                    (and 
                        (at ?p ?u ?v1)
                        (at ?t ?u ?v2)
                        (not (wall ?t))
                        (not (closed_door ?t))
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
                     ?t - cell
                     ?u1 ?u2 ?v1 ?v2 - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (not (closed_door ?t))
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
                     ?t - cell
                     ?u1 ?u2 ?v - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v)
                        (at ?t ?u2 ?v)
                        (not (wall ?t))
                        (not (closed_door ?t))
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
                     ?t - cell
                     ?u1 ?u2 ?v1 ?v2 - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v1)
                        (at ?t ?u2 ?v2)
                        (not (wall ?t))
                        (not (closed_door ?t))
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

            (:action open_door_north
                :parameters 
                    (?p1 - player
                     ?t - cell
                     ?u ?v1 ?v2 - num )

                :precondition 
                    (and 
                        (at ?p1 ?u ?v1)
                        (at ?t ?u ?v2)
                        (closed_door ?t)
                        (is_one_minus ?v1 ?v2)
                    )

                :effect 
                    (and 
                        (not (closed_door ?t))
                        (open_door ?t)
                        (increase (steps) 1)
                    )
            )

            (:action open_door_east
                :parameters 
                    (?p - player
                     ?t - cell
                     ?u1 ?u2 ?v - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v)
                        (at ?t ?u2 ?v)
                        (closed_door ?t)
                        (is_one_minus ?u1 ?u2)
                    )

                :effect 
                    (and 
                        (not (closed_door ?t))
                        (open_door ?t)
                        (increase (steps) 1)
                    )
            )

            (:action open_door_south
                :parameters 
                    (?p - player
                     ?t - cell
                     ?u ?v1 ?v2 - num)

                :precondition 
                    (and 
                        (at ?p ?u ?v1)
                        (at ?t ?u ?v2)
                        (closed_door ?t)
                        (is_one_minus ?v1 ?v2)
                    )

                :effect 
                    (and 
                        (not (closed_door ?t))
                        (open_door ?t)
                        (increase (steps) 1)
                    )
            )

            (:action open_door_west
                :parameters 
                    (?p - player
                     ?t - cell
                     ?u1 ?u2 ?v - num)

                :precondition 
                    (and 
                        (at ?p ?u1 ?v)
                        (at ?t ?u2 ?v)
                        (closed_door ?t)
                        (is_one_minus ?u2 ?u1)
                    )

                :effect 
                    (and 
                        (not (closed_door ?t))
                        (open_door ?t)
                        (increase (steps) 1)
                    )
            )

            (:action get_stone
                :parameters
                   (?p - player
                    ?t - cell
                    ?u ?v - num)
                :precondition
                   (and 
                        (at ?p ?u ?v)
                        (at ?t ?u ?v)
                        (stone ?t)                       
                   )
                :effect
                   (and
                        (not (stone ?t))
                        (increase (steps) 1)
                   )

            )
        )'''

        with open(filename,"w") as f:
            f.write(domainstr)

