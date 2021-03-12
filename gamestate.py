'''
This file stores the gamestate class that is used to keep track of
the current state of the dcss game 
'''

import actions
import logging
import re
import time
import string
import random
from enum import Enum


class ItemProperty(Enum):
    """
    See crawl wiki for lists of these:
    weapons: http://crawl.chaosforge.org/Brand
    armour: http://crawl.chaosforge.org/Ego
    """
    NO_PROPERTY = 0

    # Melee Weapon Brands
    Antimagic_Brand = 1
    Chaos_Brand = 2
    Disruption_Brand = 3
    Distortion_Brand = 4
    Dragon_slaying_Brand = 5
    Draining_Brand = 6
    Electrocution_Brand = 7
    Flaming_Brand = 8
    Freezing_Brand = 9
    Holywrath_Brand = 10
    Pain_Brand = 11
    Necromancy_Brand = 12
    Protection_Brand = 13
    Reaping_Brand = 14
    Speed_Brand = 15
    Vampiricism_Brand = 16
    Venom_Brand = 17
    Vorpal_Brand = 18

    # Thrown weapon brands
    Dispersal_Brand = 19
    Exploding_Brand = 20
    Penetration_Brand = 21
    Poisoned_Brand = 22
    Returning_Brand = 23
    Silver_Brand = 24
    Steel_Brand = 25

    # Needles
    Confusion_Brand = 26
    Curare_Brand = 27
    Frenzy_Brand = 28
    Paralysis_Brand = 29
    Sleeping_Brand = 30

    # Armour Properties (Egos)
    Resistance_Ego = 31
    Fire_Resistance_Ego = 32
    Cold_Resistance_Ego = 33
    Poison_Resistance_Ego = 34
    Positive_Energy_Ego = 35
    Protection_Ego = 36
    Invisibility_Ego = 37
    Magic_Resistance_Ego = 38
    Strength_Ego = 39
    Dexterity_Ego = 40
    Intelligence_Ego = 41
    Running_Ego = 42
    Flight_Ego = 43
    Stealth_Ego = 44
    See_Invisible_Ego = 45
    Archmagi_Ego = 46
    Ponderousness_Ego = 47
    Reflection_Ego = 48
    Spirit_Shield_Ego = 49
    Archery_Ego = 50


class Monster:
    """

    Sample monster data:

    'mon': {
        'id': 1,
        'name': 'kobold',
        'plural': 'kobolds',
        'type': 187,
        'typedata': {
            'avghp': 3
        },
        'att': 0,
        'btype': 187,
        'threat': 1
    }


    """

    all_possible_g_values = string.ascii_lowercase + string.ascii_uppercase

    # current theory: each monster has a unique id, so use this class variable to track them
    ids_to_monsters = {}

    def __init__(self):
        self.name = None
        self.vals = None
        self.ascii_sym = None
        self.id = None
        self.cell = None  # if the monster is on a cell, update it here (note that this could become outdated and we wouldn't know about it)
        self.threat = 0

    @staticmethod
    def create_or_update_monster(vals, ascii_sym):
        if 'id' in vals.keys():
            # check if id already exists, if so, retrieve that Monster instance
            mon_id = vals['id']
            if mon_id in Monster.ids_to_monsters.keys():
                # if this monster already exists, update instead of creating new one
                Monster.ids_to_monsters[mon_id].update(vals, ascii_sym)
                return Monster.ids_to_monsters[mon_id]
            else:
                # create a new monster and insert into Monster.ids_to_monsters
                new_monster = Monster()
                new_monster.update(vals, ascii_sym)
                Monster.ids_to_monsters[new_monster.id] = new_monster
                return new_monster
        elif 'name' in vals.keys() and vals['name'] == 'plant':
            # a plant is not a monster
            return 'plant'
        elif 'name' in vals.keys():
            # create a new monster and don't give it an ID (IDs are reserved for the game to give us)
            new_monster = Monster()
            new_monster.update(vals, ascii_sym)
            return new_monster
        else:
            raise Exception("Monster with no id, here's the vals: {}".format(vals))

    def update(self, vals, ascii_sym):
        self.vals = vals
        self.ascii_sym = ascii_sym
        if 'id' in vals.keys():
            self.id = vals['id']

        if 'name' in vals.keys():
            self.name = vals['name']

        if 'type' in vals.keys():
            self.type = vals['type']

        if 'threat' in vals.keys():
            self.threat = vals['threat']

    def set_cell(self, cell):
        self.cell = cell

    def remove_cell(self):
        # this should happen when a monster dies or is no longer in view
        self.cell = None

    def get_pddl_strs(self, pddl_cell_str):
        strs = [
            "(monsterat {} {} {})".format(self.name, self.id, pddl_cell_str),
        ]
        return strs


class CellRawStrDatum(Enum):
    """ These are the types of data that may appear in a raw str description of a cell from the server. """
    x = 0
    f = 1
    y = 2
    g = 3
    t = 4
    mf = 5
    col = 6
    mon = 7


class Cell:
    '''
    Stores a cell of the map, not sure what all the information means yet
    '''

    def __init__(self, vals):
        '''
        Vals is a dictionary containing attributes, key must be a CellRawStrDatum
        '''

        self.raw = vals
        self.x = None
        self.f = None
        self.y = None
        self.g = None
        self.t = None
        self.mf = None
        self.col = None

        self.has_wall = False
        self.has_player = False
        self.has_stairs_down = False
        self.has_stairs_up = False
        self.has_closed_door = False
        self.has_open_door = False
        self.has_statue = False
        self.has_player_visited = False
        self.has_lava = False
        self.has_plant = False
        self.has_tree = False
        self.has_smoke = False
        self.has_potion = False
        self.has_scroll = False
        self.teleport_trap = False  # TODO not handled anywhere
        self.has_multiple_items = False  # TODO not handled anywhere
        self.has_items = False
        self.has_gold = False
        self.has_monster = False
        self.has_shaft = False
        self.has_corpse = False
        self.has_fountain = False
        self.has_magical_condensation_cloud = False

        # TODO add condition for †
        self.monster = None  # there can only be up to 1 monster in a cell
        self.set_vals(vals)

    def set_vals(self, vals):
        # monsters are constantly moving,
        # TODO VERY LIKELY TO INTRODUCE A BUG
        self.monster = False

        if 'x' in vals.keys():
            self.x = vals['x']
        if 'f' in vals.keys():
            self.f = vals['f']
        if 'y' in vals.keys():
            self.y = vals['y']
        if 'mon' in vals.keys():
            if vals['mon']:
                # we have a live monster in this cell
                self.monster = Monster.create_or_update_monster(vals['mon'], ascii_sym=self.g)
                if self.monster == 'plant':  # sometimes monsters are plants, but we don't want to consider it a monster for our sake
                    self.has_plant = True
                    self.monster = None
                else:
                    self.has_monster = True
                    self.monster.set_cell(self)
                # print("Just added monster: {}".format(self.monster.get_pddl_str('cell{}{}'.format(self.x, self.y))))
            else:
                # a monster either died here or moved to a different cell, either way it's not in this cell
                # so we need to update the monster to tell it it's no longer in this cell
                if self.monster:
                    self.monster.remove_cell()
                    self.monster = None

        if 'g' in vals.keys():
            self.g = vals['g']

            # ['p', 'P'] are plants
            if self.g not in ['p', 'P'] and self.g in Monster.all_possible_g_values:
                self.has_monster = True

            elif self.g == '#':
                self.has_wall = True

            elif self.g == '>':
                self.has_stairs_down = True

            elif self.g == '<':
                self.has_stairs_up = True

            elif self.g == '@':
                self.has_player = True
                self.has_player_visited = True

            elif self.g == '+':
                self.has_closed_door = True
                self.has_closed_door = False

            elif self.g == '\'':
                self.has_closed_door = False
                self.has_open_door = True

            elif self.g == '8':
                self.has_statue = True

            elif self.g == '⌠':
                self.has_fountain = True

            elif self.g == '≈':
                self.has_lava = True

            elif self.g in ['☘', '♣']:
                self.has_tree = True

            elif self.g == '†':
                self.has_corpse = True

            elif self.g == '§':
                self.has_smoke = True

            elif self.g == '°' or self.g == '○':
                self.has_magical_condensation_cloud = True

            # now check for monsters
            elif self.g == 'P':
                self.has_plant = True

            elif self.g == '^':
                self.has_shaft = True

            # A '.' means that its an empty tile
            elif self.g == '.':
                pass
                #print("Found a g value of \'.\' at x={},y={}".format(self.x, self.y))

            elif self.g == '!':
                self.has_potion = True

            elif self.g == '?':
                self.has_scroll = True

            elif self.g in ['(', ')']:
                self.has_items = True

            # TODO Figure out how much gold (information is at least in messages)
            elif self.g == '$':
                self.has_gold = True

            else:
                print("Found an unknown g value: {}".format(self.g))
                #time.sleep(20)

            # elif self.g in string.ascii_lowercase+string.ascii_uppercase:
            #    print("We may have a monster represented by g={}, vals are {}".format(self.g, vals))
            #    print("Current monster is ")

            # Player location is updated in multiple places, remove old player location just in case
            if not self.g == '@':
                self.has_player = False

        if 't' in vals.keys():
            self.t = vals['t']
        if 'mf' in vals.keys():
            self.mf = vals['mf']
        if 'col' in vals.keys():
            self.col = vals['col']

        self.raw = vals

    def get_pddl_name(self):
        return "cellx{}y{}".format(self.x, self.y)

    def get_cell_vector(self):
        """Do something similar to get_item_vector"""

        # cell vector should contain:
        # corpse? 0 or 1
        # monster? (can only be one monster on a tile) - monster vector with
        # monster vector
        # current health? (may be in the form of weak, almost dead, bloodied, etc)
        # maximum health?
        # monster name
        # is unique?
        # items?
        # special tile features (like water, lava, wall, door, etc)

    def get_pddl_facts(self):
        pddl_facts = []
        if self.has_wall:
            pddl_facts.append('(wall {})'.format(self.get_pddl_name()))
        if self.has_closed_door:
            pddl_facts.append('(closeddoor {})'.format(self.get_pddl_name()))
        if self.has_player:
            pddl_facts.append('(playerat {})'.format(self.get_pddl_name()))
        if self.has_statue:
            pddl_facts.append('(statue {})'.format(self.get_pddl_name()))
        if self.has_lava:
            pddl_facts.append('(lava {})'.format(self.get_pddl_name()))
        if self.has_plant:
            pddl_facts.append('(plant {})'.format(self.get_pddl_name()))
        if self.has_tree:
            pddl_facts.append('(tree {})'.format(self.get_pddl_name()))
        if self.has_stairs_down:
            pddl_facts.append('(hasstairsdown {})'.format(self.get_pddl_name()))
        if self.has_stairs_up:
            pddl_facts.append('(hasstairsup {})'.format(self.get_pddl_name()))
        if self.has_monster:
            pddl_facts.append("(hasmonster {})".format(self.get_pddl_name()))
        if self.monster:
            for fact_i in self.monster.get_pddl_strs(self.get_pddl_name()):
                pddl_facts.append(fact_i)
        return pddl_facts

    def straight_line_distance(self, cell):
        # this considers diagonal movements
        return max(abs(self.x - cell.x), abs(self.y - cell.y))

    def get_simple_vector_value(self):
        """
        Returns a vector based representation of the cell for use in RL approaches.

        This vector has length 1 and is highly simplified. Possible values are:
        0 - empty
        1 - player
        2 - monster
        3 - lava
        4 - plant or tree
        5 - stairsup
        6 - stairsdown
        7 - statue or wall or
        8 - open door
        9 - closed door
        """

        if self.has_player:
            return 1
        elif self.has_monster or self.has_plant:
            return 2
        elif self.has_lava or self.has_tree or self.has_statue or self.has_wall:
            # represents any obstacle that prevents moving into this space
            return 3
        elif self.has_open_door:
            return 4
        elif self.has_closed_door:
            return 5
        else:
            return 0  # signifies being empty

    @staticmethod
    def get_simple_vector_value_for_nonexistent_cell():
        """In the situation where we need to represent a tile that doesn't exist, use this as the default value"""
        return 3  # same as an obstacle

    def __str__(self):
        if self.g and len(self.g) >= 1:
            return self.g
        else:
            return " "


class CellMap:
    """
    Data structure that maintains the set of all cells currently seen in the game.
    """

    def __init__(self):
        self.min_x = None
        self.min_y = None
        self.max_x = None
        self.max_y = None
        self.num_cells = 0
        self.current_place = "Dungeon"
        self.current_depth = 1
        self.place_depth_to_x_y_to_cells = {}  # key is depth, then key is an (x,y) tuple, val is the cell at that spot
        self.agent_x = None
        self.agent_y = None
        # unknown_vals = {k:None for k in CellRawStrDatum} # test this
        # self.unknown_cell = Cell(

    def add_or_update_cell(self, x, y, vals):
        #print("add_or_update_cell with args {} {} {}".format(x, y, vals))
        # print("vals={}".format(str(vals)))

        if self.current_place not in self.place_depth_to_x_y_to_cells.keys():
            self.place_depth_to_x_y_to_cells[self.current_place] = {}

        if self.current_depth not in self.place_depth_to_x_y_to_cells[self.current_place].keys():
            self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth] = {}

        if 'x' not in vals.keys():
            vals['x'] = x
        elif x != vals['x']:
            print("WARNING potential issue with coordinates, x={} and vals[x]={}".format(x, vals['x']))
        if 'y' not in vals.keys():
            vals['y'] = x
        elif y != vals['y']:
            print("WARNING potential with coordinates, y={} and vals[y]={}".format(y, vals['y']))

        if (x, y) in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
            # print("updating existing cell x={},y={}".format(x,y))
            # print("previous vals={}, new vals={}".format(self.x_y_to_cells[(x, y)].raw, vals))
            self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(x, y)].set_vals(vals=vals)
        else:
            # print("adding new cell x={},y={} with vals={}".format(x, y, vals))
            self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(x, y)] = Cell(vals=vals)
            if self.min_x is None or x < self.min_x:
                self.min_x = x
            if self.max_x is None or x > self.max_x:
                self.max_x = x
            if self.min_y is None or y < self.min_y:
                self.min_y = y
            if self.max_y is None or y > self.max_y:
                self.max_y = y

        if 'g' in vals.keys() and '@' in vals['g']:
            self.agent_x = x
            self.agent_y = y

        # safety check - cell with player matches x and y
        if self.agent_x and self.agent_y:
            player_cell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(self.agent_x, self.agent_y)]
            if not player_cell.has_player:
                print("WARNING - discrepancy in player location:")
                print("     agent.x = {}".format(self.agent_x))
                print("     agent.y = {}".format(self.agent_y))
                print("     playercell.x = {}".format(player_cell.x))
                print("     playercell.y = {}".format(player_cell.y))


    def draw_cell_map(self):

        s = "agent=({},{})\nminx={},maxx={},miny={},maxy={}\n".format(self.agent_x, self.agent_y,
                                                                      self.min_x, self.max_x, self.min_y, self.max_y)
        print(s)
        non_empty_cells = []
        for curr_y in range(self.min_y, self.max_y + 1):
            for curr_x in range(self.min_x, self.max_x + 1):
                if (curr_x, curr_y) in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                    cell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(curr_x, curr_y)]
                    s += str(cell)
                    if cell.g != "." and cell.g != "#" and cell.g is not None:
                        non_empty_cells.append(cell)
                else:
                    s += " "
            s += '\n'

        # print("non-empty cells are:")
        # for c in non_empty_cells:
        #    print("X={},Y={}, Cell is: {}".format(c.x, c.y, c.g))

        return s

    def set_current_depth(self, depth: int):
        self.current_depth = depth

    def set_current_place(self, place: str):
        self.current_place = place

    def get_radius_around_agent_vector(self, r=2, tile_vector_repr='simple'):
        """
        Returns a vector of tiles around the agent. The length of the vector is (2r+1)^2
        """
        required_length_of_vector = ((2*r)+1)**2
        cell_vector = []

        x_min = self.agent_x - r
        x_max = self.agent_x + r
        y_min = self.agent_y - r
        y_max = self.agent_y + r
        for curr_y in range(y_min, y_max + 1):
            for curr_x in range(x_min, x_max + 1):
                if (curr_x, curr_y) in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                    if tile_vector_repr == 'simple':
                        cell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(curr_x, curr_y)]
                        cell_vector.append(cell.get_simple_vector_value())
                else:
                    if tile_vector_repr == 'simple':
                        cell_vector.append(Cell.get_simple_vector_value_for_nonexistent_cell())

        if len(cell_vector) != required_length_of_vector:
            raise Exception("ERROR - cell_vector has length {} but required length is {}".format(len(cell_vector), required_length_of_vector))

        return cell_vector

    def get_radius_around_agent_str(self, r=8):
        x_min = self.agent_x - r
        x_max = self.agent_x + r
        y_min = self.agent_y - r
        y_max = self.agent_y + r
        s = ""
        for curr_y in range(y_min, y_max + 1):
            for curr_x in range(x_min, x_max + 1):
                if (curr_x, curr_y) in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                    s += str(self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(curr_x, curr_y)])
                else:
                    s += "x"
            s += '\n'
        return s

    def get_cell_map_pddl_global(self):
        object_strs = []
        fact_strs = []
        for place in self.place_depth_to_x_y_to_cells.keys():
            for depth in self.place_depth_to_x_y_to_cells[place].keys():
                for (curr_x, curr_y) in self.place_depth_to_x_y_to_cells[place][depth].keys():
                    cell = self.place_depth_to_x_y_to_cells[place][depth][(curr_x, curr_y)]
                    object_strs.append(cell.get_pddl_name())

                    for f in cell.get_pddl_facts():
                        fact_strs.append(f)

                    # print('cellxy = {}, cellname is {}'.format(str((curr_x, curr_y)), cell.get_pddl_name()))
                    northcellxy = (cell.x, cell.y - 1)
                    # print("northcellxy = {}".format(northcellxy))
                    if northcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        northcell = self.place_depth_to_x_y_to_cells[place][depth][
                            northcellxy]
                        # print("northcell = {}".format(northcell.get_pddl_name()))
                        fact_strs.append("(northof {} {})".format(cell.get_pddl_name(), northcell.get_pddl_name()))

                    southcellxy = (cell.x, cell.y + 1)
                    if southcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        southcell = self.place_depth_to_x_y_to_cells[place][depth][
                            southcellxy]
                        fact_strs.append("(southof {} {})".format(cell.get_pddl_name(), southcell.get_pddl_name()))

                    westcellxy = (cell.x - 1, cell.y)
                    if westcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        westcell = self.place_depth_to_x_y_to_cells[place][depth][westcellxy]
                        fact_strs.append("(westof {} {})".format(cell.get_pddl_name(), westcell.get_pddl_name()))

                    eastcellxy = (cell.x + 1, cell.y)
                    if eastcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        eastcell = self.place_depth_to_x_y_to_cells[place][depth][eastcellxy]
                        fact_strs.append("(eastof {} {})".format(cell.get_pddl_name(), eastcell.get_pddl_name()))

                    northeastcellxy = (cell.x + 1, cell.y - 1)
                    if northeastcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        northeastcell = self.place_depth_to_x_y_to_cells[place][depth][
                            northeastcellxy]
                        fact_strs.append(
                            "(northeastof {} {})".format(cell.get_pddl_name(), northeastcell.get_pddl_name()))

                    northwestcellxy = (cell.x - 1, cell.y - 1)
                    if northwestcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        northwestcell = self.place_depth_to_x_y_to_cells[place][depth][
                            northwestcellxy]
                        fact_strs.append(
                            "(northwestof {} {})".format(cell.get_pddl_name(), northwestcell.get_pddl_name()))

                    southeastcellxy = (cell.x + 1, cell.y + 1)
                    if southeastcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        southeastcell = self.place_depth_to_x_y_to_cells[place][depth][
                            southeastcellxy]
                        fact_strs.append(
                            "(southeastof {} {})".format(cell.get_pddl_name(), southeastcell.get_pddl_name()))

                    southwestcellxy = (cell.x - 1, cell.y + 1)
                    if southwestcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        southwestcell = self.place_depth_to_x_y_to_cells[place][depth][
                            southwestcellxy]
                        fact_strs.append(
                            "(southwestof {} {})".format(cell.get_pddl_name(), southwestcell.get_pddl_name()))

        return object_strs, fact_strs

    def get_cell_map_pddl_current_place_only(self):

        object_strs = []
        fact_strs = []
        for curr_y in range(self.min_y, self.max_y + 1):
            for curr_x in range(self.min_x, self.max_x + 1):
                if (curr_x, curr_y) in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                    cell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(curr_x, curr_y)]
                    object_strs.append(cell.get_pddl_name())

                    for f in cell.get_pddl_facts():
                        fact_strs.append(f)

                    # print('cellxy = {}, cellname is {}'.format(str((curr_x, curr_y)), cell.get_pddl_name()))
                    northcellxy = (cell.x, cell.y - 1)
                    # print("northcellxy = {}".format(northcellxy))
                    if northcellxy in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                        northcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][
                            northcellxy]
                        # print("northcell = {}".format(northcell.get_pddl_name()))
                        fact_strs.append("(northof {} {})".format(cell.get_pddl_name(), northcell.get_pddl_name()))

                    southcellxy = (cell.x, cell.y + 1)
                    if southcellxy in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                        southcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][
                            southcellxy]
                        fact_strs.append("(southof {} {})".format(cell.get_pddl_name(), southcell.get_pddl_name()))

                    westcellxy = (cell.x - 1, cell.y)
                    if westcellxy in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                        westcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][westcellxy]
                        fact_strs.append("(westof {} {})".format(cell.get_pddl_name(), westcell.get_pddl_name()))

                    eastcellxy = (cell.x + 1, cell.y)
                    if eastcellxy in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                        eastcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][eastcellxy]
                        fact_strs.append("(eastof {} {})".format(cell.get_pddl_name(), eastcell.get_pddl_name()))

                    northeastcellxy = (cell.x + 1, cell.y - 1)
                    if northeastcellxy in self.place_depth_to_x_y_to_cells[self.current_place][
                        self.current_depth].keys():
                        northeastcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][
                            northeastcellxy]
                        fact_strs.append(
                            "(northeastof {} {})".format(cell.get_pddl_name(), northeastcell.get_pddl_name()))

                    northwestcellxy = (cell.x - 1, cell.y - 1)
                    if northwestcellxy in self.place_depth_to_x_y_to_cells[self.current_place][
                        self.current_depth].keys():
                        northwestcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][
                            northwestcellxy]
                        fact_strs.append(
                            "(northwestof {} {})".format(cell.get_pddl_name(), northwestcell.get_pddl_name()))

                    southeastcellxy = (cell.x + 1, cell.y + 1)
                    if southeastcellxy in self.place_depth_to_x_y_to_cells[self.current_place][
                        self.current_depth].keys():
                        southeastcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][
                            southeastcellxy]
                        fact_strs.append(
                            "(southeastof {} {})".format(cell.get_pddl_name(), southeastcell.get_pddl_name()))

                    southwestcellxy = (cell.x - 1, cell.y + 1)
                    if southwestcellxy in self.place_depth_to_x_y_to_cells[self.current_place][
                        self.current_depth].keys():
                        southwestcell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][
                            southwestcellxy]
                        fact_strs.append(
                            "(southwestof {} {})".format(cell.get_pddl_name(), southwestcell.get_pddl_name()))

        object_strs = list(set(object_strs))
        fact_strs = list(set(fact_strs))

        return object_strs, fact_strs

    def get_xy_to_cells_dict(self):
        if self.current_depth == 0:
            # depth is only 0 when the player is in the character creation menus in the beginning
            return {}
        return self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth]

    def get_player_cell(self):

        return self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(self.agent_x, self.agent_y)]


class InventoryItem:
    ITEM_VECTOR_LENGTH = 5

    def __init__(self, id_num, name, quantity, base_type=None):
        self.id_num = int(id_num)
        self.name = name
        self.quantity = quantity
        self.base_type = base_type
        self.item_bonus = 0
        self.properties = []

        if self.name:
            if '+' in self.name or '-' in self.name:
                m = re.search('[+-][1-9][1-9]?', self.name)
                if m:
                    self.item_bonus = int(m.group(0))
                else:
                    self.item_bonus = 0
        else:
            if self.quantity == 0:
                # Might just be an empty slot that the server is telling us about
                pass
            else:
                print(
                    "\n\nself.name is None, not sure why...args to InventoryItem were id_num={}, name={}, quantity={}, base_type={}\n\n".format(
                        id_num, name, quantity, base_type))
                exit(1)

        # TODO - figure out how to know if item is equipped
        self.equipped = False

    def set_base_type(self, base_type):
        self.base_type = base_type

    def get_base_type(self):
        return self.base_type

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

    def get_item_bonus(self):
        return self.item_bonus

    def is_item_equipped(self):
        return self.equipped

    def get_item_type(self):
        """
        Since 0 is a valid value, increase all by 1, so 0 means an empty value
        """
        return 1 + self.base_type

    def get_property_i(self, i):
        if i < len(self.properties):
            return self.properties[i]
        else:
            return ItemProperty.NO_PROPERTY

    def get_item_vector(self):
        """
        * Indicates that item vector value may be repeated, if more than one property.

        Index  Information Contained
        -----  ---------------------
          0    Item Type (Armour, Weapon, etc)
          1    Item Count
          2    Item Bonus ("+x" value)
          3    Item Equipped
          4    Property* (Fire resist, stealth, venom, etc)
        """
        item_vector = []
        item_vector.append(self.get_item_type())
        item_vector.append(self.get_quantity())
        item_vector.append(self.get_item_bonus())
        item_vector.append(self.is_item_equipped())
        item_vector.append(self.get_property_i(0))

        assert len(item_vector) == InventoryItem.ITEM_VECTOR_LENGTH
        # Note: If this assert fails, update
        # InventoryItem.ITEM_VECTOR_LENGTH to be the correct value

        return item_vector

    @staticmethod
    def get_empty_item_vector():
        item_vector = [0 for i in range(InventoryItem.ITEM_VECTOR_LENGTH)]
        return item_vector

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "{}({}) - {} (#={}, base_type={})".format(self.get_letter(), self.id_num, self.get_name(),
                                                         self.get_quantity(), self.get_base_type())


class TileFeatures:
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
    last_visit = None  # None if never visited, 0 if currently here, otherwise >1 representing
    # number of actions executed since last visit


class GameState:
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
        self.agent_z = 0  # which floor of the dungeon the agent is on

        self.map_obj_player_x = None  # this is the x of the map_obj where the player is
        self.map_obj_player_y = None  # this is the y of the map_obj where the player is

        self.map_obj = []
        self.map_dim = 24
        self.map_middle = 12
        self.cellmap = CellMap()

        self.inventory_by_id = {}

        self.last_recorded_movement = ''

        self.asp_str = ''  # facts that don't change when an action is executed
        self.asp_comment_str = ''  # comments associated with asp
        self.player_cell = None
        self.training_asp_str = ''  # facts that do change
        self.all_asp_cells = None  # number of cell objects

        self.messages = {}  # key is turn, value is list of messages received on this turn in order,
        # where first is oldest message

        # initialize values of state variables
        for k in self.state_keys:
            self.state[k] = None

        self.died = False  # becomes true if agent has died

        self.more_prompt = False  # becomes true when there is more messages before the agent can act
        #  and therefore must press enter to receive for messages

        self.too_terrified_to_move = False  # idk what to do here, but agent can't move

        self.cannot_move = False  # agent can't move for some reason, no use trying move actions

        self.just_gained_level = False

        self.wizard_mode_on = False

        self.game_time = None
        self.game_turn = None

        self.player_name = ""
        self.player_title = ""
        self.player_species = ""

        self.player_form = None
        self.player_unarmed_attack = None

        self.player_place = ""
        self.player_depth = 1

        self.player_ac = None
        self.player_ev = None
        self.player_sh = None

        self.player_god = None
        self.player_piety_rank = None
        self.player_penance = None

        self.player_current_hp = None
        self.player_hp_max = None
        self.player_real_hp_max = None
        self.player_current_mp = None
        self.player_mp_max = None
        self.player_dd_real_mp_max = None

        self.player_strength = None
        self.player_strength_max = None
        self.player_dex = None
        self.player_dex_max = None
        self.player_int = None
        self.player_int_max = None

        self.player_position = None
        self.player_status = []
        self.player_poison_survival = None
        self.player_level = 1

        self.player_progress = None
        self.player_gold = 0

        self.noise_level = None
        self.adjusted_noise_level = None

        self.general_knowledge_pddl_filename = "models/general_dcss_knowledge.pddl"

        self.id = GameState.ID
        GameState.ID += 1

    def update(self, msg_from_server):
        try:
            # print(str(self.state))
            logging.info("gamestate.update() is now processing: {}".format(str(msg_from_server)))
            self._process_raw_state(msg_from_server)
        except Exception as e:
            raise Exception("Something went wrong: " + str(e))

    def record_movement(self, dir):
        self.last_recorded_movement = dir
        print('last recorded movement is ' + str(self.last_recorded_movement))
        if dir in actions.key_actions.keys():
            if dir == 'move_N':
                self.shift_agent_y(-1)
            elif dir == 'move_S':
                self.shift_agent_y(1)
            elif dir == 'move_E':
                self.shift_agent_x(1)
            elif dir == 'move_W':
                self.shift_agent_x(-1)
            else:
                pass  # do nothing if the agent didn't move
        pass  # do nothing if the agent didn't move

    def shift_agent_x(self, change):
        '''
        Performs an addition
        '''
        self.agent_x += change

    def shift_agent_y(self, change):
        '''
        Performs an addition
        '''
        self.agent_y += change

    def get_cell_map(self):
        return self.cellmap

    def _process_raw_state(self, s, last_key=''):
        # print("processing {}\n".format(s))
        if isinstance(s, list):
            for i in s:
                self._process_raw_state(i)

        elif isinstance(s, dict):
            for k in s.keys():
                if k == 'cells':
                    self.get_cell_objs_from_raw_data(s[k])
                    # self.update_map_obj(cells_x_y_g_data_only)
                    # self.update_map_obj()
                last_key = k

                if k == 'more':
                    if s[k]:
                        self.more_prompt = True
                    else:
                        self.more_prompt = False

                if k == 'messages':
                    self.process_messages(s[k])

                if k == 'inv':
                    self.process_inv(s[k])

                if k == 'equip':
                    self.process_equip(s[k])

                if k == 'msg' and s[k] == 'player':
                    self.process_player(s)

                if k in self.state_keys:
                    self.state[k] = s[k]
                    # print("Just stored {} with data {}".format(k,s[k]))
                elif isinstance(s[k], list):
                    for i in s[k]:
                        self._process_raw_state(i)
                elif isinstance(s[k], dict):
                    self._process_raw_state(s[k])
                else:
                    pass
        else:
            pass

    def _process_items_agent_location(self, message):
        items = message.split(';')
        print("Found {} items, they are:".format(len(items)))
        for i in items:
            print("   {}".format(i))

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

        last_message_is_items_here = False
        for m in data:
            turn = m['turn']
            message_only = strip_tags(m['text'])
            if turn in self.messages.keys():
                self.messages[turn].append(message_only)
            else:
                self.messages[turn] = [message_only]

            if 'You die...' in message_only:
                self.died = True

            if 'too terrified to move' in message_only:
                self.too_terrified_to_move = True

            if 'You cannot move' in message_only:
                self.cannot_move = True

            if 'You have reached level' in message_only:
                self.just_gained_level = True

            if last_message_is_items_here:
                self._process_items_agent_location(message_only)
                last_message_is_items_here = False

            if 'Things that are here' in message_only:
                last_message_is_items_here = True

            if 'Unknown command.' in message_only:
                print("Error with last command - game did not recognize it... ")

            # print("Just added message for turn {}: {}".format(turn, message_only))

    def process_player(self, data):
        # print("In process_player() with data:\n{}".format(data))
        for k in data.keys():
            if k == 'name':
                self.player_name = data[k]

            elif k == 'title':
                self.player_title = data[k]

            elif k == 'wizard':
                if data[k] == 0:
                    self.wizard_mode_on = False
                else:
                    self.wizard_mode_on = True

            elif k == 'place':
                self.player_place = data[k]
                self.get_cell_map().set_current_place(self.player_place)

            elif k == 'depth':
                self.player_depth = data[k]
                self.get_cell_map().set_current_depth(self.player_depth)

            elif k == 'time':
                self.game_time = data[k]

            elif k == 'turn':
                self.game_turn = data[k]

            elif k == 'species':
                self.player_species = data[k]

            elif k == 'god':
                self.player_god = data[k]

            elif k == 'penance':
                self.player_penance = data[k]

            elif k == 'piety_rank':
                self.player_piety_rank = data[k]

            # Todo - I don't know what the possible for forms refer to
            # Todo - my best guess is it relates to transmutations, like blade hands and dragon form
            elif k == 'form':
                self.player_form = data[k]

            elif k == 'hp':
                self.player_current_hp = data[k]

            elif k == 'hp_max':
                self.player_hp_max = data[k]

            elif k == 'real_hp_max':
                self.player_real_hp_max = data[k]

            elif k == 'mp':
                self.player_current_mp = data[k]

            elif k == 'mp_max':
                self.player_mp_max = data[k]

            # Todo - I don't know what this represents
            elif k == 'dd_real_mp_max':
                self.player_dd_real_mp_max = data[k]

            # Todo - I don't know what values mean what
            # Todo - my best guess is 0 means player will die from poison and 1 means player will live
            elif k == 'poison_survival':
                self.player_poison_survival = data[k]

            elif k == 'ac':
                self.player_ac = data[k]

            elif k == 'ev':
                self.player_ev = data[k]

            elif k == 'sh':
                self.player_sh = data[k]

            elif k == 'str':
                self.player_strength = data[k]

            elif k == 'str_max':
                self.player_strength_max = data[k]

            elif k == 'int':
                self.player_int = data[k]

            elif k == 'int_max':
                self.player_int_max = data[k]

            elif k == 'dex':
                self.player_dex = data[k]

            elif k == 'dex_max':
                self.player_dex_max = data[k]

            elif k == 'xl':
                self.player_level = data[k]

            # Todo - I don't know what progress means
            elif k == 'progress':
                self.player_progress = data[k]

            elif k == 'gold':
                self.player_gold = data[k]

            elif k == 'noise':
                self.noise_level = data[k]

            elif k == 'pos':
                self.player_position = data[k]
                self.agent_x = self.player_position['x']
                self.agent_y = self.player_position['y']

            # Todo - I don't know the difference between adjusted noise and noise
            elif k == 'adjusted_noise':
                self.adjusted_noise_level = data[k]

            # Todo - Status is a list, I'm not sure what possible values could be
            # I'm guessing probably strings of some form
            elif k == 'status':
                if len(data[k]) > 1:
                    print("Status is {}".format(data[k]))
                    time.sleep(5)
                self.player_status = data[k]

            elif k == 'unarmed_attack':
                self.player_unarmed_attack = data[k]

            elif k in ['msg', 'inv', 'quiver_item', 'quiver_available', 'quiver_desc', 'launcher_item', 'equip',
                       'unarmed_attack_colour']:
                # these are processed elsewhere or are irrelevant
                pass

            else:
                print("****WARNING - unknown player datum: {}:{}".format(k, data[k]))
                print("****DATA HAS DATA:")
                for k,v in data.items():
                    print("   {}:{}".format(k,v))
                time.sleep(20)

    def get_pddl_current_state_player(self):
        player_object_strs = []
        player_fact_strs = []

        # TODO - put all player fact information here
        player_fact_strs.append("(playerplace {}_{})".format(self.player_place.lower().strip(), self.player_depth))
        return player_object_strs, player_fact_strs

    def get_pddl_player_info(self):
        """
        Return player health information and other stats
        """
        player_pddl_strs = []
        if self.player_current_hp < self.player_hp_max:
            player_pddl_strs.append("(playerlessthanfullhealth)")
        else:
            player_pddl_strs.append("(playerfullhealth)")

        return player_pddl_strs

    def get_pddl_current_state_cellmap(self, current_place_only=True):
        if current_place_only:
            object_strs, fact_strs = self.cellmap.get_cell_map_pddl_current_place_only()
        else:
            object_strs, fact_strs = self.cellmap.get_cell_map_pddl_global()
        return object_strs, fact_strs

    def get_current_game_turn(self):
        return self.game_turn

    def get_current_game_time(self):
        return self.game_time

    def get_all_pddl_facts(self):
        cell_map_object_strs, cell_map_fact_strs = self.get_pddl_current_state_cellmap(current_place_only=False)
        fact_strs = cell_map_fact_strs + self.get_pddl_player_info()
        return fact_strs

    def write_pddl_current_state_to_file(self, filename, goals):
        """Filename is assumed to be a relevant filename from the folder that the main script is running"""

        pddl_str = "(define (problem dcss-test-prob)\n(:domain dcss)\n(:objects \n"

        cell_map_object_strs, cell_map_fact_strs = self.get_pddl_current_state_cellmap()

        object_strs = cell_map_object_strs
        fact_strs = cell_map_fact_strs + self.get_pddl_player_info()

        for obj in object_strs:
            pddl_str += "  {}\n".format(obj)
        pddl_str += ")\n"

        pddl_str += "(:init \n"

        # read in common knowledge facts and put them first
        with open(self.general_knowledge_pddl_filename, 'r') as f2:
            for line in f2.readlines():
                if not line.startswith(';'):
                    pddl_str += line.strip() + '\n'

        for fact in fact_strs:
            pddl_str += "  {}\n".format(fact)
        pddl_str += ")\n"

        pddl_str += "(:goal \n  (and \n"
        for goal in goals:
            pddl_str += "    {}\n".format(goal)
        pddl_str += ")\n"
        pddl_str += ")\n\n)"

        with open(filename.format(), 'w') as f:
            f.write(pddl_str)

        return True

    def has_agent_died(self):
        return self.died

    def is_agent_too_terrified(self, reset=True):
        agent_terrified = self.too_terrified_to_move
        if reset:
            self.too_terrified_to_move = False
        return agent_terrified

    def agent_cannot_move(self, reset=True):
        cannot_move = self.cannot_move
        if reset:
            self.cannot_move = False
        return cannot_move

    def agent_just_leveled_up(self, reset=True):
        leveled_up = self.just_gained_level
        if reset:
            self.just_gained_level = False
        return leveled_up

    def process_inv(self, data):
        # print("Data is {}".format(data))
        for inv_id in data.keys():
            name = None
            quantity = None
            base_type = None
            if 'name' in data[inv_id].keys():
                name = data[inv_id]['name']
            if 'quantity' in data[inv_id].keys():
                quantity = int(data[inv_id]['quantity'])
                if quantity == 0:
                    # This item doesn't really exist, don't add it
                    continue
            if 'base_type' in data[inv_id].keys():
                base_type = data[inv_id]['base_type']
            if inv_id not in self.inventory_by_id.keys():
                # new item
                inv_item = InventoryItem(inv_id, name, quantity, base_type)
                self.inventory_by_id[inv_id] = inv_item
                print("***** Adding new item {}".format(inv_item))
            else:
                # existing item
                inv_item = self.inventory_by_id[inv_id]
                print("***** Updating item {}".format(inv_item))
                prev_quantity = inv_item.get_quantity()
                if quantity is not None and quantity <= prev_quantity:
                    if quantity == 0:
                        print("  **** Deleting item {} because quantity = 0".format(inv_item))
                        del self.inventory_by_id[inv_id]
                    else:
                        print(
                            "  **** Reducing item {} quantity from {} to {}".format(inv_item, prev_quantity, quantity))
                        self.inventory_by_id[inv_id].set_quantity(quantity)

    def process_equip(self, data):
        """
        This function should probably always come after process_inv.
        """

        for equip_slot, equip_item in data.items():
            # TODO parse what the player has equipped
            #print("equip slot {} has value {}".format(equip_slot, equip_item))
            pass

        # Todo - if an item is equipped, find the item in the inventory, and update the is_equipped flag

    def process_quiver_item(self, data):
        # Todo - update the inventory quiver item to be this item
        pass

    def process_quiver_available(self, data):
        # Todo - add this into the inventory, I'm not sure what it means though
        # Todo - best guess is that its the number of items that can be put in the quiver?
        pass

    def get_cell_objs_from_raw_data(self, cells):
        only_xyg_cell_data = []
        curr_x = None
        curr_y = None
        g_var = None
        num_at_signs = 0
        if cells:
            # Note: in the first iteration of this loop, x and y will exist in cell_dict.keys()
            for cell_dict in cells:
                # either x and y appear to mark the start of a new row, or ...
                if 'x' in cell_dict.keys() and 'y' in cell_dict.keys():
                    curr_x = cell_dict['x']
                    curr_y = cell_dict['y']
                else:  # ... just increment x, keeping y the same
                    curr_x += 1

                # print("x={},y={}".format(curr_x, curr_y))

                vals = {}

                # store any other datums we have access to
                for datum_key in CellRawStrDatum:
                    if datum_key.name in cell_dict.keys():
                        # input("datum_key {} is in cell_dict {} with value {}".format(datum_key.name, cell_dict, cell_dict[datum_key.name]))
                        vals[datum_key.name] = cell_dict[datum_key.name]
                    else:
                        pass
                        # input("datum_key {} is NOT in cell_dict {}".format(datum_key.name, cell_dict))
                if 'x' not in vals.keys():
                    vals['x'] = curr_x
                if 'y' not in vals.keys():
                    vals['y'] = curr_y

                if 'mon' in cell_dict.keys():
                    # print("Found a monster cell with cell_dict vals {}".format(cell_dict))
                    # vals['mon'] = cell_dict['mon']
                    pass

                self.cellmap.add_or_update_cell(curr_x, curr_y, vals=vals)

    def print_map_obj(self):
        raise Exception("We're in an olddddd function")
        # while self.lock:
        #     # wait
        #     time.sleep(0.001)
        #
        # self.lock = True
        # try:
        #     for r in self.map_obj:
        #         print(str(r))
        #     self.lock = False
        # except:
        #     raise Exception("Oh man something happened")
        # finally:
        #     self.lock = False

    def get_player_xy(self):
        return (self.map_obj_player_x, self.map_obj_player_y)

    def get_asp_str(self):
        return self.asp_str

    def get_asp_comment_str(self):
        return self.asp_comment_str

    def get_training_asp_str(self):
        return self.training_asp_str

    def get_player_cell(self):
        return self.player_cell

    def get_tiles_around_player_radius(self, radius=1):
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
        - tiles are ordered in a clockwise orientation, starting with N, then NE, then E, etc
        - inner layers come before outer layers
        - each tile is represented as a factored state:
          <objType,monsterLetter,hasCorpse,hereBefore>
             * objType = 0 is empty, 1 is wall, 2 is monster
             * monsterLetter = 27 if noMonster, 0-26 representing the alpha index of the first letter of mon name
             * hasCorpse = 0 if no edible corpse, 1 if edible corpse
             * hereBefore = 0 if first time player on this tile, 1 if player has already been here


        :param radius: Int
        :return: a factored state representation of the tiles around the player
        '''

        tiles = []
        curr_radius = 0

        # agent's tile
        tiles.append(self.map_obj[self.map_obj_player_y][self.map_obj_player_x])
        # N tile
        tiles.append(self.map_obj[self.map_obj_player_y - 1][self.map_obj_player_x])
        # NE tile
        tiles.append(self.map_obj[self.map_obj_player_y - 1][self.map_obj_player_x + 1])
        # E tile
        tiles.append(self.map_obj[self.map_obj_player_y][self.map_obj_player_x + 1])
        # SE tile
        tiles.append(self.map_obj[self.map_obj_player_y + 1][self.map_obj_player_x + 1])
        # S tile
        tiles.append(self.map_obj[self.map_obj_player_y + 1][self.map_obj_player_x])
        # SW tile
        tiles.append(self.map_obj[self.map_obj_player_y + 1][self.map_obj_player_x - 1])
        # W tile
        tiles.append(self.map_obj[self.map_obj_player_y][self.map_obj_player_x - 1])
        # NW tile
        tiles.append(self.map_obj[self.map_obj_player_y - 1][self.map_obj_player_x - 1])

        return tiles

    def draw_map(self):
        # print("in draw map!")
        s = ''
        top_row_indexes = None
        for row in self.map_obj:
            row_s = ''
            if top_row_indexes is None:
                # not sure what I was doing here?
                pass
            for spot in row:
                if len(spot) != 0:
                    row_s += (str(spot))
                else:
                    row_s += ' '
            # remove any rows that are all whitespace
            if len(row_s.strip()) > 0:
                s += row_s + '\n'

        print(s)

    def draw_cell_map(self):
        print(self.cellmap.draw_cell_map())

    def print_inventory(self):
        print("   Inventory:")
        for inv_item in sorted(self.inventory_by_id.values(), key=lambda i: i.get_num_id()):
            print("     {} - {} (#={}, base_type={})".format(inv_item.get_letter(), inv_item.get_name(),
                                                             inv_item.get_quantity(), inv_item.get_base_type()))
            print("     Vector: {}".format(inv_item.get_item_vector()))

    def get_inventory_vector(self):
        pass

    def _pretty_print(self, curr_state, offset=1, last_key=''):
        if not isinstance(curr_state, dict):
            print(' ' * offset + str(curr_state))
        else:
            for key in curr_state.keys():
                last_key = key
                if isinstance(curr_state[key], dict):
                    print(' ' * offset + str(key) + '= {')
                    self._pretty_print(curr_state[key], offset + 2, last_key)
                    print(' ' * offset + '}')
                elif isinstance(curr_state[key], list):
                    if last_key == 'cells':
                        # don't recur
                        self.print_x_y_g_cell_data(curr_state[key])
                        # for i in curr_state[key]:
                        #    print('  '*offset+str(i))
                        # pass
                    else:
                        print(' ' * offset + str(key) + '= [')
                        for i in curr_state[key]:
                            self._pretty_print(i, offset + 2, last_key)
                        print(' ' * offset + "--")
                    print(' ' * offset + ']')

                else:
                    print(' ' * offset + str(key) + "=" + str(curr_state[key]))

    def printstate(self):
        # print("self.state="+str(self.state))
        # print('-'*20+" GameState "+'-'*20)
        # self._pretty_print(self.state)
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
            row = [' '] * map_dim
            self.map_obj.append(row)

        curr_x = -1
        for cell in cells_str:
            # create Cell object
            new_cell = Cell(cell)

            # put into right location into map
            if new_cell.x and new_cell.y and new_cell.g:
                curr_x = new_cell.x
                self.map_obj[new_cell.y + map_middle][new_cell.x + map_middle] = new_cell.g

                # map_obj[abs(new_cell.x)][abs(new_cell.y)] = new_cell.g
            # elif new_cell.y and new_cell.g and curr_x >= 0:
            #    map_obj[new_cell.y+map_middle][curr_x] = new_cell.g
            # map_obj[curr_x][abs(new_cell.y)] = new_cell.g

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
        map_obj = gs.get_map_obj()


if __name__ == '__main__':
    example_json_state_string_1 = {'msgs': [{'msg': 'map', 'clear': True, 'cells': [
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1847}, 'x': -6, 'mf': 2, 'y': -1},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}},
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1847}, 'x': -6, 'mf': 2, 'y': 0},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 9, 'ov': [2202, 2204]}},
        {'f': 33, 'g': '$', 'mf': 6, 'col': 14,
         't': {'doll': None, 'ov': [2204], 'fg': 947, 'mcache': None, 'bg': 1048585, 'base': 0}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2204]}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2, 'ov': [2204]}}, {'f': 33, 'g': '0', 'mf': 6, 'col': 5,
                                                                               't': {'doll': None, 'ov': [2204],
                                                                                     'fg': 842, 'mcache': None, 'bg': 2,
                                                                                     'base': 0}},
        {'f': 33, 'g': '@', 'mf': 1, 'col': 87,
         't': {'mcache': None, 'doll': [[3302, 32], [3260, 32], [3372, 32], [3429, 32], [4028, 32], [3688, 32]],
               'bg': 7, 'ov': [2204], 'fg': 527407}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5, 'ov': [2204]}}, {'f': 33, 'g': '$', 'mf': 6, 'col': 14,
                                                                               't': {'doll': None, 'ov': [2204],
                                                                                     'fg': 947, 'mcache': None,
                                                                                     'bg': 1048580, 'base': 0}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6, 'ov': [2204, 2206]}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}},
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1848}, 'x': -6, 'mf': 2, 'y': 1},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2202]}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2206]}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}},
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1846}, 'x': -6, 'mf': 2, 'y': 2},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2202]}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 9}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2206]}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}},
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1846}, 'x': -6, 'mf': 2, 'y': 3},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2202]}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 6}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2, 'ov': [2206]}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}},
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1845}, 'x': -6, 'mf': 2, 'y': 4},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7, 'ov': [2202]}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 9}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 7}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 8}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 8, 'ov': [2206]}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}},
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1845}, 'x': -6, 'mf': 2, 'y': 5},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3, 'ov': [2202]}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 3}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2}},
        {'f': 60, 'g': '<', 'mf': 12, 'col': 9, 't': {'bg': 2381, 'flv': {'f': 6, 's': 50}}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}}, {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 5}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 2}},
        {'f': 33, 'g': '.', 'mf': 1, 'col': 7, 't': {'bg': 4, 'ov': [2206]}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1847}},
        {'f': 9, 'col': 1, 'g': '#', 't': {'bg': 1847}, 'x': -6, 'mf': 2, 'y': 6},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1846}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1845}},
        {'f': 9, 'g': '#', 'mf': 2, 'col': 1, 't': {'bg': 1848}}], 'player_on_level': True, 'vgrdc': {'y': 0, 'x': 0}}]}
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
