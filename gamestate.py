'''
This file stores the gamestate class that is used to keep track of
the current state of the dcss game 
'''

import actions
import logging
import re
import threading
import time
import string


class Cell():
    '''
    Stores a cell of the map, not sure what all the information means yet
    '''
    x = None
    f = None
    y = None
    g = None
    t = None
    mf = None
    col = None
    raw = None # raw data from the server

    def __init__(self, vals):
        '''
        Vals is a dictionary containing attributes
        '''

        self.raw = vals

        if 'x' in vals.keys():
            self.x = vals['x']
        if 'f' in vals.keys():
            self.f = vals['f']
        if 'y' in vals.keys():
            self.y = vals['y']
        if 'g' in vals.keys():
            self.g = vals['g']
        if 't' in vals.keys():
            self.t = vals['t']
        if 'mf' in vals.keys():
            self.mf = vals['mf']
        if 'col' in vals.keys():
            self.col = vals['col']

    def __str__(self):
        if self.g and len(self.g) >= 1:
            return g
        pass

class InventoryItem():

    def __init__(self, id_num, name, quantity, base_type=None):
        self.id_num = int(id_num)
        self.name = name
        self.quantity = quantity
        self.base_type = base_type
    
    def set_base_type(self, base_type):
        self.base_type = base_type

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name
        
    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_quantity(self):
        return self.quantity
        
    def set_num_id(self, id_num):
        self.id_num = int(id_num)

    def get_num_id(self):
        return self.id_num

    def get_letter(self):
        return string.ascii_letters[self.id_num]

    def get_item_vector_value(self):
        """
        See documentation for how this is calculated.
        """

        # TODO
        # will need one of these for each inventory vector
        pass
        
    def __eq__(self, other):
        return self.name == other.name
        
    
class TileFeatures():
    '''
    Contains feature data used per tile

    Returns a factored state representation of the tiles around the player:
        Example w/ radius of 1
        - 9 tiles including the player's current position and all adjacent tiles in every cardinal direction
        - each tile is represented as a factored state:
          <objType,monsterLetter,hasCorpse,hereBefore>
             * objType = 0 is empty, 1 is wall, 2 is monster
             * monsterLetter = 0-25 representing the alpha index of the first letter of mon name (0=a, etc)
             * hasCorpse = 0 if no edible corpse, 1 if edible corpse
             * hereBefore = 0 if first time player on this tile, 1 if player has already been here
    '''


    absolute_x = None
    absolute_y = None
    has_monster = 0
    last_visit = None # None if never visited, 0 if currently here, otherwise >1 representing
                      # number of actions executed since last visit



class GameState():

    ID = 0

    def __init__(self):
        # state is just a dictionary of key value pairs
        self.state = {}

        # only state information we care about
        self.state_keys = ['hp', 'hp_max', 'depth', 'light', 'god', 'mp', 'species', 'dex', 'inv', 'cells', 'species']

        self.letter_to_number_lookup = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

        # when the agent starts, it is in the center of its mental map
        # as it moves N,S,E,W, the coordinates of its mental map will shift
        self.agent_x = 0
        self.agent_y = 0

        self.map_obj_player_x = None  # this is the x of the map_obj where the player is
        self.map_obj_player_y = None  # this is the y of the map_obj where the player is

        self.map_obj = []
        self.map_dim = 24
        self.map_middle = 12

        self.inventory_raw = {}
        self.inventory = []
        
        self.last_recorded_movement = ''

        self.asp_str = '' # facts that don't change when an action is executed
        self.asp_comment_str = '' # comments associated with asp
        self.player_cell = None
        self.training_asp_str = '' # facts that do change
        self.all_asp_cells = None # number of cell objects

        self.messages = {} # key is turn, value is list of messages received on this turn in order,
                           # where first is oldest message

        # intiliaze values of state variables
        for k in self.state_keys:
            self.state[k] = None

        self.id = GameState.ID
        GameState.ID+=1

    def update(self, msg_from_server):
        try:
            #print(str(self.state))
            #print(str(msg_from_server))
            self._process_raw_state(msg_from_server)
            #self.draw_map()
            #self.compute_asp_str()
            #print(self.training_asp_str)
            #print(self.background_asp_str)
        except Exception as e:
            raise Exception("Something went wrong" + e)

    def record_movement(self,dir):
        self.last_recorded_movement = dir
        print('last recorded movement is ' + str(self.last_recorded_movement))
        if dir in actions.key_actions.keys():
            if dir is 'move_N':
                self.shift_agent_y(-1)
            elif dir is 'move_S':
                self.shift_agent_y(1)
            elif dir is 'move_E':
                self.shift_agent_x(1)
            elif dir is 'move_W':
                self.shift_agent_x(-1)
            else:
                pass # do nothing if the agent didn't move
        pass # do nothing if the agent didn't move

    def shift_agent_x(self,change):
        '''
        Performs an addition
        '''
        self.agent_x += change

    def shift_agent_y(self,change):
        '''
        Performs an addition
        '''
        self.agent_y += change
        
    def _process_raw_state(self, s, last_key=''):
        #print("processing {}\n\n".format(s))
        if isinstance(s, list):
            for i in s:
                self._process_raw_state(i)
                
        elif isinstance(s, dict):
            for k in s.keys():
                if k == 'cells':
                    cells_x_y_g_data_only = self.get_x_y_g_cell_data(s[k])
                    self.update_map_obj(cells_x_y_g_data_only)
                last_key = k

                if k == 'messages':
                    self.process_messages(s[k])
                if k == 'inv':
                    self.process_inv(s[k])

                if k in self.state_keys:
                    self.state[k] = s[k]
                    #print("Just stored {} with data {}".format(k,s[k]))
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

        # need to store the message for current location so I can get quanitity of food items and stones for pickup action
        for m in data:
            turn = m['turn']
            message_only = strip_tags(m['text'])
            if turn in self.messages.keys():
                self.messages[turn].append(message_only)
            else:
                self.messages[turn] = [message_only]

            #print("Just added message for turn {}: {}".format(turn,message_only))

    def process_inv(self,data):
        print("Data is {}".format(data))
        for inv_id in data.keys():
            name = None
            quantity = None
            base_type = None            
            print("inv_id = {}".format(inv_id))
            if 'name' in data[inv_id].keys():
                name = data[inv_id]['name']
            if 'quantity' in data[inv_id].keys():
                quantity = int(data[inv_id]['quantity'])
            if 'base_type' in data[inv_id].keys():
                base_type = data[inv_id]['base_type']
            self.inventory_raw[inv_id] = [name, quantity, base_type]
            inv_item = InventoryItem(inv_id, name, quantity, base_type)
            
            items_to_remove = []
            new_item = True
            for prev_inv_item in self.inventory:
                print("inv_id={}, name={}, quantity={}, base_type={}".format(inv_id, name, quantity, base_type))
                print("prev_inv_item.get_name() = {}".format(prev_inv_item.get_name()))
                if quantity is not None:
                    print("here")
                    if int(inv_id) == prev_inv_item.get_num_id():
                        print("found existing item {}".format(prev_inv_item.get_name()))
                        new_item = False
                        if quantity is not None:
                            if quantity <= 0:
                                items_to_remove.append(prev_inv_item)
                            elif quantity < prev_inv_item.get_quantity():
                                prev_inv_item.set_quantity(quantity)

            if new_item:
                print("adding item {}".format(inv_item.get_name()))
                self.inventory.append(inv_item)
                                            
            for item_to_remove in items_to_remove:
                print("Removing item {}".format(item_to_remove.get_name()))
                self.inventory.remove(item_to_remove)

                    
    def get_x_y_g_cell_data(self, cells):
        only_xyg_cell_data = []
        curr_x = None
        curr_y = None
        num_at_signs = 0
        if cells:
            for i_dict in cells:
                #if (curr_x and ('x' in i_dict.keys()) or (not ('y' in i_dict.keys()) and curr_y == -1):
                #    raise Exception("ERROR: yeah I must be wrong")
                #print("i_dict is ",str(i_dict))
                if 'x' in i_dict.keys() and 'y' in i_dict.keys() and 'g' in i_dict.keys():
                    curr_x = i_dict['x']
                    curr_y = i_dict['y']
                    only_xyg_cell_data.append([i_dict['x'],i_dict['y'],i_dict['g']])
                    #print("x={},y={},g={}".format(str(curr_x),str(curr_y),str(i_dict['g'])))
                elif 'x' in i_dict.keys() and 'y' in i_dict.keys():
                    ''' Sometimes there is only x and y and no g, often at the beginning of the cells list'''
                    curr_x = i_dict['x']
                    curr_y = i_dict['y']
                    #print("x={},y={}".format(str(curr_x), str(curr_y)))
                elif 'g' in i_dict.keys() and len(i_dict['g']) > 0:
                    #print("x,y,g = ", str(curr_x), str(curr_y), str(i_dict['g']))
                    try:
                        curr_x+=1
                        only_xyg_cell_data.append([curr_x,curr_y,i_dict['g']])
                        #print("added it just fine")
                        if '@' in str(i_dict['g']):
                            num_at_signs+=1
                            #print("Just added ({0},{1},{2}) to only_xyg_cell_data".format(curr_x,curr_y,i_dict['g']))
                            if num_at_signs > 1:
                                print("Whoa, too many @ signs, here's the cell data")
                                print(cells)
                        #print("x={},y={},g={}".format(str(curr_x), str(curr_y), str(i_dict['g'])))
                    except:
                        # TODO: test this more robustly
                        #        right now I think that if this triggers, it means
                        #        the player didn't move, so just keep old data and don't
                        #        update
                        
                        logging.warning("Failure with cell data: "+str(i_dict))
                        print("curr_x={0} and curr_y={1}".format(curr_x,curr_y))
                        print("Cells are "+str(cells))
                        input("Press enter to continue")
                        pass

                #else:
                #    raise Exception("ERROR: no \'g\' found in cell data")
            #for i in only_xyg_cell_data:
            #    print(str(i))

            return only_xyg_cell_data

    def update_map_obj(self, only_x_y_g_cells_data):
        '''
        If we already have a map data, and we have new map data from the player moving,
        shift the map and update the cells

        :param only_x_y_g_cells_data:
        :param player_move_dir:
        '''

        at_sign_count = 0 # we should only see the @ in one location

        # If map object isn't created yet, then initialize
        if len(self.map_obj) == 0:
            for i in range(self.map_dim):
                row = [' '] * self.map_dim
                self.map_obj.append(row)

        if not only_x_y_g_cells_data:
            # We don't always get cell data, if so, return
            return

        for xyg_cell in only_x_y_g_cells_data:
            x = int(xyg_cell[0])
            y = int(xyg_cell[1])
            g = xyg_cell[2]

            map_obj_x = self.map_middle + x
            map_obj_y = self.map_middle + y


            if '@' == g:
                #print("player x,y is " + str(x) + ',' + str(y) + " from cell data")
                #print("player x,y in gamestate is " + str(map_obj_x) + ',' + str(map_obj_y) + " from cell data")
                self.map_obj_player_x = map_obj_x
                self.map_obj_player_y = map_obj_y
                at_sign_count+=1
                if at_sign_count > 1:
                    print("Error, multiple @ signs - let's debug!")
                    time.sleep(1000)

            # boundary conditions
            if map_obj_y < len(self.map_obj)  and \
               map_obj_x < len(self.map_obj[map_obj_y]) and \
               map_obj_x > 0 and \
               map_obj_y > 0:

                self.map_obj[map_obj_y][map_obj_x] = g


    def print_map_obj(self):
        while self.lock:
            #wait
            time.sleep(0.001)

        self.lock = True
        try:
            for r in self.map_obj:
                print(str(r))
            self.lock = False
        except:
            raise Exception("Oh man something happened")
        finally:
            self.lock = False

    def get_player_xy(self):
        return (self.map_obj_player_x,self.map_obj_player_y)

    def get_asp_str(self):
        return self.asp_str

    def get_asp_comment_str(self):
        return self.asp_comment_str

    def get_training_asp_str(self):
        return self.training_asp_str

    def get_player_cell(self):
        return self.player_cell

    def compute_asp_str(self, filename=None):
        num_asp_cells = []
        asp_comment_str = '%'

        if filename:
            pass # TODO write to file

        bg_asp_str = ''
        training_asp_str = ''

        # go through all the map data and add cells, xy coordinates, and any special objects
        cell_id = 1
        y = 0
        FOUND_PLAYER = False
        player_cell = None

        for row in self.map_obj:
            x = 0
            for cell in row:
                if cell == ' ' or cell == '':
                    # ignore
                    asp_comment_str += "|      |".format(cell_id)
                    pass

                else:

                    bg_asp_str += 'cell(c{0}).\n'.format(cell_id)
                    bg_asp_str += 'at(c{0},{1},{2}).\n'.format(cell_id, x, y)
                    num_asp_cells.append('c{0}'.format(cell_id))

                    if cell == '@':
                        bg_asp_str += 'agentat(c{0}).\n'.format(cell_id)
                        asp_comment_str += "| c{0:0=3d} |".format(cell_id)
                        FOUND_PLAYER = True
                        player_cell = 'c{0}'.format(cell_id)
                    if cell == '#':
                        bg_asp_str += 'wall(c{0}).\n'.format(cell_id)
                        asp_comment_str += "|#c{0:0=3d}#|".format(cell_id)
                    elif cell == '.':
                        # do nothing
                        asp_comment_str += "| c{0:0=3d} |".format(cell_id)
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
                x += 1
            asp_comment_str+= '\n%' + '+------+'* len(row)+ '\n%'
            y += 1

        # objects agent knows about
        # TODO Put this somewhere else more global - probably ought to consider pddl to asp in a nicer implementation of
        # TODO all this
        agent_known_object_types = ['stone', 'ration', 'gold']
        for obj_type in agent_known_object_types:
            bg_asp_str += 'itemtype({}).\n'.format(obj_type)

        # add inventory facts
        object_types = []
        for i in self.inventory_raw.keys():
            name = self.inventory_raw[i][0]
            name = ''.join([i for i in name if not i.isdigit() and not i in ['+','-']])
            name = name.strip().replace(' ','')

            # depluralize
            name = name.replace('potions','potion').replace('scrolls','scroll').replace('stones','stone').replace('rations','ration')
            quantity = self.inventory_raw[i][1]

            if name not in object_types:
                object_types.append(name)
                bg_asp_str += 'itemtype({}).\n'.format(name)

            bg_asp_str += 'inv_item({0},{1}).\n'.format(name,quantity)
            bg_asp_str += 'inv_id({0},{1}).\n'.format(i, name)

        # add facts about current tile
        if len(self.messages.keys()) > 0:
            max_turn = max(self.messages.keys())
            logging.debug("max_turn is {}".format(max_turn))
            for m in self.messages[max_turn]:
                logging.debug("a message on turn {} is {}".format(max_turn,m))
                if 'You see here a ' in m:
                    for obj_type in agent_known_object_types:
                        if obj_type in m:
                            bg_asp_str += 'item({},{},{}).\n'.format(player_cell, obj_type, 1)

                elif 'You see here ' in m:
                    nums_in_m = list(map(int, re.findall(r'\d+', m)))
                    print("nums_in_m is {}".format(nums_in_m))
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

        #print(self.asp_str)

    def get_tiles_around_player_radius_1(self):
        '''
        A radius of 0 is only the players tile
        A radius of 1 would be 9 tiles, including
            - players tile
            - all tiles 1 away (including diagonal) of the player's tile
        A radius of 2 would be 16+8+1 = 25 tiles (all tiles <= distance of 2 from player)
        etc...

        Returns a factored state representation of the tiles around the player:
        Example w/ radius of 1
        - 9 tiles including the player's current position and all adjacent tiles in every cardinal direction
        - each tile is represented as a factored state:
          <objType,monsterLetter,hasCorpse,hereBefore>
             * objType = 0 is empty, 1 is wall, 2 is monster
             * monsterLetter = 27 if noMonster, 0-26 representing the alpha index of the first letter of mon name
             * hasCorpse = 0 if no edible corpse, 1 if edible corpse
             * hereBefore = 0 if first time player on this tile, 1 if player has already been here


        :param radius: Int
        :return: a factored state representation of the tiles around the player
        '''
        # TODO make a tile object that stores all the needed data, ... you know what to do

        tiles = [[]]
        curr_radius = 0

        tiles.append(self.map_obj[self.map_obj_player_y][self.map_obj_player_x])
        tiles.append(self.map_obj[self.map_obj_player_y-1][self.map_obj_player_x])
        tiles.append(self.map_obj[self.map_obj_player_y+1][self.map_obj_player_x])
        tiles.append(self.map_obj[self.map_obj_player_y-1][self.map_obj_player_x-1])
        tiles.append(self.map_obj[self.map_obj_player_y-1][self.map_obj_player_x+1])
        tiles.append(self.map_obj[self.map_obj_player_y+1][self.map_obj_player_x-1])
        tiles.append(self.map_obj[self.map_obj_player_y+1][self.map_obj_player_x+1])
        tiles.append(self.map_obj[self.map_obj_player_y][self.map_obj_player_x-1])
        tiles.append(self.map_obj[self.map_obj_player_y][self.map_obj_player_x+1])

    def draw_map(self):
        #print("in draw map!")
        s = ''
        for row in self.map_obj:
            row_s = ''
            for spot in row:
                if len(spot) != 0:
                    row_s+=(str(spot))
                else:
                    row_s+=' '
            # remove any rows that are all whitespace
            if len(row_s.strip()) > 0:
                s+=row_s+'\n'

        print(s)

    def print_inventory(self):
        print("   Inventory:")
        for inv_item in sorted(self.inventory,key=lambda i: i.get_num_id()):
            print("     {} - {} (#={})".format(inv_item.get_letter(), inv_item.get_name(), inv_item.get_quantity()))
            
    def get_inventory_vector(self):
        pass
            
    def print_inventory_raw(self):
        print("   Inventory:")
        for inv_id, item_description in self.inventory_raw.items():
            print("     {}-{}".format(inv_id, item_description))

        
    def _pretty_print(self, curr_state, offset=1,last_key=''):
        if not isinstance(curr_state, dict):
            print(' '*offset+str(curr_state))
        else:
            for key in curr_state.keys():
                last_key = key
                if isinstance(curr_state[key], dict):
                    print(' '*offset+str(key)+'= {')
                    self._pretty_print(curr_state[key], offset+2, last_key)
                    print(' '*offset+'}')
                elif isinstance(curr_state[key], list):
                    if last_key == 'cells':
                        # don't recur
                        self.print_x_y_g_cell_data(curr_state[key])
                        #for i in curr_state[key]:
                        #    print('  '*offset+str(i))
                        #pass
                    else:
                        print(' '*offset+str(key)+'= [')
                        for i in curr_state[key]:
                            self._pretty_print(i, offset+2, last_key)
                        print(' '*offset+"--")
                    print(' '*offset+']')                
                
                else:
                    print(' '*offset+str(key)+"="+str(curr_state[key]))

    

    def printstate(self):
        #print("self.state="+str(self.state))
        #print('-'*20+" GameState "+'-'*20)
        #self._pretty_print(self.state)
        pass

    def get_map_obj(self):
        return self.map_obj
        
    def convert_cells_to_map_obj(self, cells_str):
        '''
        cells is the data of the map and nearby monsters and enemies received from the server
        '''
        map_dim = 200
        map_middle = 100
        for i in range(map_dim):
            row = [' ']*map_dim
            self.map_obj.append(row)

        curr_x = -1
        for cell in cells_str:
            # create Cell object
            new_cell = Cell(cell)

            # put into right location into map
            if new_cell.x and new_cell.y and new_cell.g:
                curr_x = new_cell.x
                self.map_obj[new_cell.y+map_middle][new_cell.x+map_middle] = new_cell.g
                
                #map_obj[abs(new_cell.x)][abs(new_cell.y)] = new_cell.g
            #elif new_cell.y and new_cell.g and curr_x >= 0:
            #    map_obj[new_cell.y+map_middle][curr_x] = new_cell.g
                #map_obj[curr_x][abs(new_cell.y)] = new_cell.g                                

        def print_map_obj(self):
            for row in self.map_obj:
                for spot in row:
                    print(str(spot), end='')
                print('')

class FactoredState():
    '''
    Represents a factored state for use for q-learning.

    State Information:
    - 9 tiles including the player's current position and all adjacent tiles in every cardinal direction
        - each tile is represented as a factored state:
          <objType,monsterLetter,hasCorpse,hereBefore>
             * objType = 0 is empty, 1 is wall, 2 is monster
             * monsterLetter = -1 if noMonster, 0-26 representing the alpha index of the first letter of mon name
             * hasCorpse = 0 if no edible corpse, 1 if edible corpse
             * hereBefore = 0 if first time player on this tile, 1 if player has already been here
    - player's health, enums of [none,verylow,low,half,high,veryhigh,full]
    - player's hunger, enums of [fainting,starving,very hungry, hungry, not hungry, full, very full, engorged]

    '''

    tiles = []
    health = None
    hunger = None

    def __init__(self, gs):
        map_obj = gs. get_map_obj()


if __name__ == '__main__':
    example_json_state_string_1 = {'msgs': [{'msg': 'map', 'clear': True, 'cells': [{'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1847}, 'x': -6, 'mf': 2, 'y': -1}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}, {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1847}, 'x': -6, 'mf': 2, 'y': 0}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 9, 'ov': [2202, 2204]}}, {'f': 33, 'g': '$', 'mf': 6, 'col': 14, 't': {'doll': None, 'ov': [2204], 'fg': 947, 'mcache': None, 'bg': 1048585, 'base': 0}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2204]}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2, 'ov': [2204]}}, {'f': 33, 'g': '0', 'mf': 6, 'col': 5, 't': {'doll': None, 'ov': [2204], 'fg': 842, 'mcache': None, 'bg': 2, 'base': 0}}, {'f': 33, 'g': '@', 'mf': 1, 'col': 87, 't': {'mcache': None, 'doll': [[3302, 32], [3260, 32], [3372, 32], [3429, 32], [4028, 32], [3688, 32]], 'bg': 7, 'ov': [2204], 'fg': 527407}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5, 'ov': [2204]}}, {'f': 33, 'g': '$', 'mf': 6, 'col': 14, 't': {'doll': None, 'ov': [2204], 'fg': 947, 'mcache': None, 'bg': 1048580, 'base': 0}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6, 'ov': [2204, 2206]}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}}, {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1848}, 'x': -6, 'mf': 2, 'y': 1}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2202]}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2206]}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}, {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1846}, 'x': -6, 'mf': 2, 'y': 2}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2202]}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 9}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2206]}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}}, {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1846}, 'x': -6, 'mf': 2, 'y': 3}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2202]}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2, 'ov': [2206]}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}}, {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1845}, 'x': -6, 'mf': 2, 'y': 4}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7, 'ov': [2202]}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 9}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 8}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 8, 'ov': [2206]}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}}, {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1845}, 'x': -6, 'mf': 2, 'y': 5}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2202]}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2}}, {'f': 60, 'g': '<', 'mf': 12, 'col': 9, 't': {'bg': 2381, 'flv': {'f': 6, 's': 50}}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2206]}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}}, {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1847}, 'x': -6, 'mf': 2, 'y': 6}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}}, {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}], 'player_on_level': True, 'vgrdc': {'y': 0, 'x': 0}}]}
    example_json_state_string_2 = "{'msgs': [{'msg': 'input_mode', 'mode': 0}, {'msg': 'player', 'turn': 12, 'time': 120, 'pos': {'y': 1, 'x': -1}}, {'msg': 'map', 'cells': [{'col': 7, 'y': 0, 'g': '.', 't': {'mcache': None, 'doll': None, 'fg': 0}, 'x': 0}, {'col': 87, 'y': 1, 'g': '@', 't': {'mcache': None, 'doll': [[3302, 32], [3260, 32], [3372, 32], [3429, 32], [4028, 32], [3688, 32]], 'fg': 527407}, 'x': -1}], 'vgrdc': {'y': 1, 'x': -1}}, {'msg': 'input_mode', 'mode': 1}]}"

    gs1 = GameState()

    gs1.update(example_json_state_string_1)




'''
                        
    int:4
    species:Minotaur
    equip:{'0': 0, '15': -1, '8': -1, '1': -1, '12': -1, '9': -1, '11': -1, '18': -1, '17': -1, '4': -1, '3': -1, '7': -1, '16': -1, '14': -1, '10': -1, '6': 1, '2': -1, '5': -1, '13': -1}
    dex_max:9
    unarmed_attack:Nothing wielded
    penance:0
    form:0
    int_max:4
    poison_survival:16
    turn:1114
    str_max:21
    place:Dungeon
    name:midca
    dex:9
    ev:12
    hp_max:20
    real_hp_max:20
    mp_max:0
    unarmed_attack_colour:7
    piety_rank:1
    mp:0
    xl:1
    ac:2
    title:the Skirmisher
    hp:16
    
'''

'''
    def _process_raw_state3(self, dict_struct):
        if isinstance(dict_struct, list):
            new_li = []
            for li in dict_struct:
                new_li.append(self._process_raw_state(li))
            return new_li
        elif not isinstance(dict_struct, dict):
            return dict_struct
        else:
            curr_state = {}
            ignore_list = ['cell','html','content','skip','text']
            skip_bc_ignore = False
            for key in dict_struct.keys():
                for ignore in ignore_list:
                    if ignore in key:
                        skip_bc_ignore = True
                    
                    if skip_bc_ignore:
                        skip_bc_ignore = False
                        pass

                    # process if list
                    elif isinstance(dict_struct[key], list):
                        new_list = []
                        for li in dict_struct[key]:
                            new_list.append(self._process_raw_state(li))
                            
                            curr_state[key] = li
#                        else:
#                            curr_state[key] = dict_struct[key]

                    # process if dict
                    elif isinstance(dict_struct[key], dict):
                        curr_state[key] = self._process_raw_state(dict_struct[key])
                    else: 
                        curr_state[key] = dict_struct[key]

        return curr_state



'''
