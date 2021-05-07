import logging
import os
import time

import actions
from dcss.state.cell import Cell
from dcss.state.cellmap import CellMap
from dcss.state.cellrawstrdatum import CellRawStrDatum
from dcss.state.inventoryitem import InventoryItem


class GameState:
    """This file stores the state class that is used to keep track of
    the current state of the dcss game"""

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

        self.general_knowledge_pddl_facts_filename = "../../models/general_dcss_knowledge_facts.pddl"
        self.general_knowledge_pddl_objects_filename = "../../models/general_dcss_knowledge_objects.pddl"

        self.id = GameState.ID
        GameState.ID += 1

    def update(self, msg_from_server):
        """
        Updates the game state object with a message from the webserver.

        Args:
            msg_from_server (dict): message from the server
        """
        try:
            # print(str(self.state))
            logging.info("state.update() is now processing: {}".format(str(msg_from_server)))
            self._process_raw_state(msg_from_server)
        except Exception as e:
            raise Exception("Something went wrong: " + str(e))

    def get_player_stats_vector(self):
        """ See Table 1
            returns a vector of size 170
        """
        #TODO write code
        pass

    def get_player_inventory_vector(self):
        """ Player has 52 inventory slots corresponding to each lowercase and
            uppercase letter of the English alphabet.

            Each item is represented by a vector of size 7:
                Vector Index    Description of Data    Data Type if available
                    0                 Item type
                    1                 quantity            Int
                    2                 Item Bonus          Int
                    3                 Is Equipped         Boolean
                    4                 First property
                    5                 Second property
                    6                 Third property
            returns a vector of size 364
        """
        # TODO write code
        pass

    def get_player_spells_vector(self):
        """ Player has a maximum of 21 spell slots for spells to be learned.

            Each of these 21 spells slots is represented by a vector of 3 values:
                Vector Index    Description of Data    Data Type if available
                    0                 Spell ID.           Int repr. spell ID
                    1                 Failure Likelihood  0-100 Percentage
                    2                 Magic Point Cost    Int
                    3                 Noise Produced      Int

            Additionally, there are 118 spells that can be learned if the player
            has found a book item with a given spell, therefore we need
            an additional 118 slots in this vector representing whether
            each spell is available to be learned.

            Returns a vector of size 21*4 + 118.
        """
        # TODO write code
        pass

    def get_player_abilities_vector(self):
        """ There are 94 possible abilities a player may acquire. For each
            of these abilities, they are represented by the following vector:

                Vector Index    Description of Data    Data Type if available
                    0                 Ability is known    Boolean
                    1                 Failure Likelihood  0-100 Percentage
                    2                 Magic Point Cost    Int
                    3                 Piety Point Cost    Int

            Returns a vector of size 94*4.
        """
        # TODO write code
        pass

    def get_player_skills_vector(self):
        """ Player has 31 skills that increase over time if the player
            is actively 'training' those skills.

            Each skill is represented by a vector of size 2:
                Vector Index    Description of Data       Data Type if available
                    0                 Current value          Float
                    1                 Training Percentage    Float

            returns a vector of size 62
        """
        # TODO write code
        pass

    def get_egocentric_LOS_map_data_vector(self, radius=7):
        """ Returns a vector containing data on the tiles
            in a ((radius*2)+1)^2 square centered on the player.

            A tile can have 0 or 1 monsters. Monsters do not have IDs therefore they are referred to
            by the tile they are occupying.

            Each tile is represented by a vector of size 34:

                Vector Index      Description of Data       Data Type if available
                    0                 Monster Type               Int representing type ID
                    1                 Monster is unique          Boolean
                    2                 Monster danger rating      Int
                    3                 Monster current health     Int
                    4                 Monster max health         Int
                    5                 Monster AC                 Int
                    6                 Monster EV                 Int
                    7                 Monster MR                 Int
                    8                 Monster Speed              Int
                    9                 Monster Status Effect 1    Int representing type ID
                    10                Monster Status Effect 2    Int representing type ID
                    11                Monster Status Effect 3    Int representing type ID
                    12                Monster Status Effect 4    Int representing type ID
                    13                Monster Status Effect 5    Int representing type ID
                    14                Monster Has Spell 1        Int representing type ID
                    15                Monster Has Spell 2        Int representing type ID
                    16                Monster Has Spell 3        Int representing type ID
                    17                Monster Has Spell 4        Int representing type ID
                    18                Monster Has Spell 5        Int representing type ID
                    19                Monster Has Spell 6        Int representing type ID
                    20                Terrain Type               Int representing type ID
                    21                Has Item Potion            Int representing type ID
                    22                Has Item Scroll            Int representing type ID
                    23                Has Item Armour            Int representing type ID
                    24                Has Item Weapon            Int representing type ID
                    25                Has Item Missile           Int representing type ID
                    26                Has Door               0 for None, 1 for closed, 2 for open
                    27                Has Trap                   Int representing type ID
                    28                Has Gold                   Boolean
                    29                Has Smoke /Fog             Boolean
                    30                Has Wall                   Int representing type ID
                    31                Has Stairway / Shaft       Int representing type ID
                    32                Has Rune                   Int representing type ID
                    33                Has Orb of Zot             Boolean

            Returns a vector of size 34 * ((radius*2)+1)^2
        """
        # TODO write code
        pass

    def get_egocentric_level_map_data_vector(self):
        """ Returns a vector containing data on the tiles
            on the player's current level.

            Uses the same tile representation of vectors of size 34 from get_egocentric_LOS_map_data()

            Returns a vector with no upperbound if traveling through levels such as Abyss or Labyrinth.
            More realistically returns a vector ranging from a minimum size of 7,650 (225 LOS tiles * 34)
            up to possible sizes of 68,000+ (2000 tiles * 34).
        """
        # TODO write code
        pass

    def get_all_map_data_vector(self):
        """ Returns a vector containing data on the tiles the player has encountered so far in the game.

            Uses the same tile representation of vectors of size 34 from get_egocentric_LOS_map_data()

            Returns a vector with no upperbound if traveling through levels such as Abyss or Labyrinth.
            More realistically returns a vector ranging from a minimum size of 7,650 (225 LOS tiles * 34)
            up to possible sizes of 3,400,000+ (100,000 tiles * 34).
        """
        # TODO write code
        pass

    def get_player_stats_pddl(self):
        """ Returns a list of PDDL facts representing player stats
        """
        # TODO write code
        pass

    def get_player_inventory_pddl(self):
        """ Returns a list of PDDL facts representing the player's inventory
        """
        # TODO write code
        pass

    def get_player_skills_pddl(self):
        """ Returns a list of PDDL facts representing the player's skills
        """
        # TODO write code
        pass

    def get_egocentric_LOS_map_data_pddl(self, radius=7):
        """ Returns a list of PDDL facts representing the tiles around the player for the given radius.
            Information about tiles outside of this radius is not returned.
        """
        # TODO write code
        pass

    def get_egocentric_level_map_data_pddl(self):
        """ Returns a list of PDDL facts representing the tiles in player's current level.
            Information about tiles outside of the current level is not returned.
        """
        # TODO write code
        pass

    def get_all_map_data_pddl(self):
        """ Returns a list of PDDL facts for every tile encountered by the player thus far.
        """
        # TODO write code
        pass

    def get_background_pddl(self):
        """ Returns a static list of pddl facts, including all type instances
            and dungeon level connections.
        """
        # TODO write code
        pass

    def record_movement(self, dir):
        """
        TODO: Write documentation
        """
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
        """
        Performs an addition


        TODO: Write documentation

        """
        self.agent_x += change

    def shift_agent_y(self, change):
        """
        Performs an addition

        TODO: Write documentation

        """
        self.agent_y += change

    def get_cell_map(self):
        """
        Returns the cell map object.

        Returns:
            CellMap: the object containing all information per cell of the DCSS game so far
        """
        return self.cellmap

    def _process_raw_state(self, s, last_key=''):
        """
        TODO: Write documentation
        """
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

    def get_pddl_current_state_cellmap(self, radius=8):
        if radius >= 0:
            object_strs, fact_strs = self.cellmap.get_cell_map_pddl_radius(radius=radius)
        else:
            object_strs, fact_strs = self.cellmap.get_cell_map_pddl_global()
        return object_strs, fact_strs

    def get_current_game_turn(self):
        return self.game_turn

    def get_current_game_time(self):
        return self.game_time

    def player_radius_pddl_facts(self, radius):
        cell_map_object_strs, cell_map_fact_strs = self.get_pddl_current_state_cellmap(radius=radius)
        fact_strs = cell_map_fact_strs + self.get_pddl_player_info()
        return fact_strs

    def all_pddl_facts(self):
        cell_map_object_strs, cell_map_fact_strs = self.get_pddl_current_state_cellmap(radius=-1)
        fact_strs = cell_map_fact_strs + self.get_pddl_player_info()
        return fact_strs

    def write_pddl_current_state_to_file(self, filename, goals):
        """Filename is assumed to be a relevant filename from the folder that the main script is running"""

        pddl_str = "(define (problem dcss-test-prob)\n(:domain dcss)\n"

        cell_map_object_strs, cell_map_fact_strs = self.get_pddl_current_state_cellmap()

        object_strs = cell_map_object_strs
        fact_strs = cell_map_fact_strs + self.get_pddl_player_info()

        pddl_str += "(:objects \n"
        pddl_str += "  ;; dynamically generated objects\n"
        for obj in object_strs:
            pddl_str += "  {}\n".format(obj)

        pddl_str += "  ;; background objects\n"

        # read in common knowledge objects and write to file
        print("Current directory is {}".format(os.getcwd()))
        with open(self.general_knowledge_pddl_objects_filename, 'r') as f2:
            for line in f2.readlines():
                if not line.startswith(';'):
                    pddl_str += "  " + line.strip() + '\n'

        pddl_str += ")\n ;; ^ closes the '(:objects' clause\n"

        for fact in fact_strs:
            pddl_str += "  {}\n".format(fact)
        pddl_str += ")\n"

        pddl_str += "(:init \n"

        # read in common knowledge facts and write to file
        print("Current directory is {}".format(os.getcwd()))
        with open(self.general_knowledge_pddl_facts_filename, 'r') as f2:
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