from dcss.state.monster import Monster
from dcss.state.terrain import TerrainType



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

        self.terrain = None

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
        self.has_gold = False
        self.has_monster = False
        self.has_shaft = False
        self.has_corpse = False
        self.has_fountain = False
        self.has_orb_of_zot = False
        self.has_ring = False
        self.has_stave = False
        self.has_hand_weapon = False
        self.has_armour = False
        self.has_missile = False
        self.has_amulet = False
        self.has_wand = False
        self.has_book = False
        self.has_misc_items = False

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
                self.has_monster = False
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
                self.terrain = TerrainType.WALL

            elif self.g == '>':
                self.has_stairs_down = True
                self.terrain = TerrainType.STAIRS_DOWN

            elif self.g == '<':
                self.has_stairs_up = True
                self.terrain = TerrainType.STAIRS_UP

            elif self.g == '@':
                self.has_player = True
                self.has_player_visited = True

            elif self.g == '+':
                self.has_closed_door = True
                self.has_open_door = False
                self.terrain = TerrainType.CLOSED_DOOR

            elif self.g == "\'":
                self.has_closed_door = False
                self.has_open_door = True
                self.terrain = TerrainType.OPENED_DOOR

            elif self.g == '8':
                self.has_statue = True
                self.terrain = TerrainType.WALL

            elif self.g == '⌠':
                self.has_fountain = True
                self.terrain = TerrainType.WALL

            elif self.g == '≈':
                self.has_lava = True
                self.terrain = TerrainType.LAVA

            elif self.g in ['☘', '♣']:
                self.has_tree = True
                self.terrain = TerrainType.TREE

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
                self.terrain = TerrainType.SHAFT_DOWN

            # A '.' means that its an empty tile
            elif self.g == '.':
                self.remove_all_items()

            elif self.g == '!':
                self.has_potion = True

            elif self.g == '?':
                self.has_scroll = True

            elif self.g == '(':
                self.has_missile = True

            elif self.g == ')':
                self.has_hand_weapon = True

            elif self.g == '[':
                self.has_armour = True

            elif self.g == '=':
                self.has_ring = True

            elif self.g == '"':
                self.has_amulet = True

            elif self.g == ':':
                self.has_book = True

            elif self.g == '/':
                self.has_wand = True

            elif self.g == '\\':
                self.has_stave = True

            elif self.g == '}':
                self.has_misc_items = True

            # TODO Figure out how much gold (information is at least in messages)
            elif self.g == '$':
                self.has_gold = True

            elif self.g == '0':
                self.has_orb_of_zot = True

            else:
                print("Found an unknown g value: {}".format(self.g))
                #time.sleep(20)

            # elif self.g in string.ascii_lowercase+string.ascii_uppercase:
            #    print("We may have a monster represented by g={}, vals are {}".format(self.g, vals))
            #    print("Current monster is ")

            # Player location is updated in multiple places, remove old player location just in case
            if not self.g == '@':
                self.has_player = False

        else:
            # there is no 'g' here, so remove all items becauase nothing is here anymore
            self.remove_all_items()

        if 't' in vals.keys():
            self.t = vals['t']
        if 'mf' in vals.keys():
            # TODO - Hypothesis that mf value of 1 means a cell changed by something being removed, such as after picking up an item
            self.mf = vals['mf']
        if 'col' in vals.keys():
            self.col = vals['col']

        self.raw = vals

    def get_terrain(self):

    def remove_all_items(self):
        self.has_plant = False
        self.has_smoke = False
        self.has_potion = False
        self.has_scroll = False
        self.has_gold = False
        self.has_monster = False
        self.has_orb_of_zot = False
        self.has_ring = False
        self.has_stave = False
        self.has_hand_weapon = False
        self.has_armour = False
        self.has_missile = False
        self.has_amulet = False
        self.has_wand = False
        self.has_book = False
        self.has_misc_items = False

    def get_pddl_name(self):
        return "cellx{}y{}".format(self.x, self.y).replace('-','_')

    def get_cell_vector(self):
        """
            A tile can have 0 or 1 monsters. Monsters do not have IDs therefore they are referred to
            by the tile they are occupying.

            Each tile is represented by a vector of size 34:

                +--------------+---------------------------------------+------------------------+
                | Vector Index | Description of Data                   | Data Type if available |
                +==============+=======================================+========================+
                |  0-19        |   Monster data, see monster.py get_cell_vector()               |
                +--------------+---------------------------------------+------------------------+
                |   20         |       Terrain Type                    | Int repr.type ID       |
                +--------------+---------------------------------------+------------------------+
                |   21         |       Has Item Potion                 |     Int repr. type ID  |
                +--------------+---------------------------------------+------------------------+
                |   22         |       Has Item Scroll                 |     Int repr. type ID  |
                +--------------+---------------------------------------+------------------------+
                |   23         |       Has Item Armour                 |     Int repr. type ID  |
                +--------------+---------------------------------------+------------------------+
                |   24         |       Has Item Weapon                 |      Int repr. type ID |
                +--------------+---------------------------------------+------------------------+
                |   25         |       Has Item Missile                |     Int repr. type ID  |
                +--------------+---------------------------------------+------------------------+
                |   26         |       Has Gold                        |     Boolean            |
                +--------------+---------------------------------------+------------------------+
                |   27         |       Has Smoke /Fog                  |     Boolean            |
                +--------------+---------------------------------------+------------------------+
                |   30         |   (TODO)    Has Rune                  |      Int repr. type ID |
                +--------------+---------------------------------------+------------------------+
                |   31         |   Has Orb of Zot                      |     Boolean            |
                +--------------+---------------------------------------+------------------------+

        """

        return self.monster.get_cell_vector() + [self.terrain, self.has_potion, self.has_scroll, self.has_armour, self.has_hand_weapon, self.has_missile, self.has_gold, self.has_smoke, self.has_orb_of_zot]

    def get_pddl_facts(self):
        pddl_facts = []
        if self.has_wall:
            pddl_facts.append('(hasterrain {} stone_wall)'.format(self.get_pddl_name()))
        if self.has_closed_door:
            pddl_facts.append('(closeddoor {})'.format(self.get_pddl_name()))
        if self.has_open_door:
            pddl_facts.append('(opendoor {})'.format(self.get_pddl_name()))
        if self.has_player:
            pddl_facts.append('(playerat {})'.format(self.get_pddl_name()))
        if self.has_statue:
            pddl_facts.append('(statue {})'.format(self.get_pddl_name()))
        if self.has_lava:
            pddl_facts.append('(hasterrain {} lava)'.format(self.get_pddl_name()))
        if self.has_plant:
            pddl_facts.append('(hasterrain {} plant)'.format(self.get_pddl_name()))
        if self.has_tree:
            pddl_facts.append('(hasterrain {} trees)'.format(self.get_pddl_name()))
        if self.has_stairs_down:
            pddl_facts.append('(hasstairsdown {})'.format(self.get_pddl_name()))
        if self.has_stairs_up:
            pddl_facts.append('(hasstairsup {})'.format(self.get_pddl_name()))
        if self.has_monster:
            pddl_facts.append("(hasmonster {})".format(self.get_pddl_name()))
        if self.has_potion:
            pddl_facts.append("(haspotion {})".format(self.get_pddl_name()))
        if self.has_scroll:
            pddl_facts.append("(hasscroll {})".format(self.get_pddl_name()))
        if self.has_orb_of_zot:
            pddl_facts.append("(hasorbofzot {})".format(self.get_pddl_name()))
        if self.has_ring:
            pddl_facts.append("(hasring {})".format(self.get_pddl_name()))
        if self.has_stave:
            pddl_facts.append("(hasstave {})".format(self.get_pddl_name()))
        if self.has_hand_weapon:
            pddl_facts.append("(hashandweapon {})".format(self.get_pddl_name()))
        if self.has_armour:
            pddl_facts.append("(hasarmour {})".format(self.get_pddl_name()))
        if self.has_missile:
            pddl_facts.append("(hasmissile {})".format(self.get_pddl_name()))
        if self.has_amulet:
            pddl_facts.append("(hasamulet {})".format(self.get_pddl_name()))
        if self.has_wand:
            pddl_facts.append("(haswand {})".format(self.get_pddl_name()))
        if self.has_book:
            pddl_facts.append("(hasbook {})".format(self.get_pddl_name()))
        if self.has_gold:
            pddl_facts.append("(hasgold {})".format(self.get_pddl_name()))
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