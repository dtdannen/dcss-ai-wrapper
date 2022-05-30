from dcss.state.cell import Cell


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
            # if not player_cell.has_player:
            #     print("WARNING - discrepancy in player location:")
            #     print("     agent.x = {}".format(self.agent_x))
            #     print("     agent.y = {}".format(self.agent_y))
            #     print("     playercell.x = {}".format(player_cell.x))
            #     print("     playercell.y = {}".format(player_cell.y))

    def set_agent_x(self, x):
        self.agent_x = x

    def set_agent_y(self, y):
        self.agent_y = y

    def draw_cell_map(self):

        s = "agent=({},{})\nminx={},maxx={},miny={},maxy={}\n".format(self.agent_x, self.agent_y,
                                                                      self.min_x, self.max_x, self.min_y, self.max_y)
        s += '     ' + ''.ljust(abs(self.min_x), '-') + "0" + ''.rjust(abs(self.max_x), '-') + "\n"

        non_empty_cells = []
        for curr_y in range(self.min_y, self.max_y + 1):
            s += '{0:0=+3d} '.format(curr_y) + ' '
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

    def get_radius_around_agent_cells(self, r=2):
        """
        Returns a list of Cell objects around the agent, given a radius.
        """
        cells = []

        x_min = self.agent_x - r
        x_max = self.agent_x + r
        y_min = self.agent_y - r
        y_max = self.agent_y + r
        for curr_y in range(y_min, y_max + 1):
            for curr_x in range(x_min, x_max + 1):
                if (curr_x, curr_y) in self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth].keys():
                    cell = self.place_depth_to_x_y_to_cells[self.current_place][self.current_depth][(curr_x, curr_y)]
                    cells.append(cell)
        return cells


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
        """
            Returns PDDL object and fact statements for the entire game so far, including multiple levels
        """
        tile_object_strs = []
        tile_fact_strs = []
        for place in self.place_depth_to_x_y_to_cells.keys():
            for depth in self.place_depth_to_x_y_to_cells[place].keys():
                for (curr_x, curr_y) in self.place_depth_to_x_y_to_cells[place][depth].keys():
                    cell = self.place_depth_to_x_y_to_cells[place][depth][(curr_x, curr_y)]
                    tile_object_strs.append(cell.get_pddl_name())

                    for f in cell.get_pddl_facts():
                        tile_fact_strs.append(f)

                    # print('cellxy = {}, cellname is {}'.format(str((curr_x, curr_y)), cell.get_pddl_name()))
                    northcellxy = (cell.x, cell.y - 1)
                    # print("northcellxy = {}".format(northcellxy))
                    if northcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        northcell = self.place_depth_to_x_y_to_cells[place][depth][
                            northcellxy]
                        # print("northcell = {}".format(northcell.get_pddl_name()))
                        tile_fact_strs.append("(northof {} {})".format(cell.get_pddl_name(), northcell.get_pddl_name()))

                    southcellxy = (cell.x, cell.y + 1)
                    if southcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        southcell = self.place_depth_to_x_y_to_cells[place][depth][
                            southcellxy]
                        tile_fact_strs.append("(southof {} {})".format(cell.get_pddl_name(), southcell.get_pddl_name()))

                    westcellxy = (cell.x - 1, cell.y)
                    if westcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        westcell = self.place_depth_to_x_y_to_cells[place][depth][westcellxy]
                        tile_fact_strs.append("(westof {} {})".format(cell.get_pddl_name(), westcell.get_pddl_name()))

                    eastcellxy = (cell.x + 1, cell.y)
                    if eastcellxy in self.place_depth_to_x_y_to_cells[place][depth].keys():
                        eastcell = self.place_depth_to_x_y_to_cells[place][depth][eastcellxy]
                        tile_fact_strs.append("(eastof {} {})".format(cell.get_pddl_name(), eastcell.get_pddl_name()))

                    northeastcellxy = (cell.x + 1, cell.y - 1)
                    if northeastcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        northeastcell = self.place_depth_to_x_y_to_cells[place][depth][
                            northeastcellxy]
                        tile_fact_strs.append(
                            "(northeastof {} {})".format(cell.get_pddl_name(), northeastcell.get_pddl_name()))

                    northwestcellxy = (cell.x - 1, cell.y - 1)
                    if northwestcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        northwestcell = self.place_depth_to_x_y_to_cells[place][depth][
                            northwestcellxy]
                        tile_fact_strs.append(
                            "(northwestof {} {})".format(cell.get_pddl_name(), northwestcell.get_pddl_name()))

                    southeastcellxy = (cell.x + 1, cell.y + 1)
                    if southeastcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        southeastcell = self.place_depth_to_x_y_to_cells[place][depth][
                            southeastcellxy]
                        tile_fact_strs.append(
                            "(southeastof {} {})".format(cell.get_pddl_name(), southeastcell.get_pddl_name()))

                    southwestcellxy = (cell.x - 1, cell.y + 1)
                    if southwestcellxy in self.place_depth_to_x_y_to_cells[place][
                        depth].keys():
                        southwestcell = self.place_depth_to_x_y_to_cells[place][depth][
                            southwestcellxy]
                        tile_fact_strs.append(
                            "(southwestof {} {})".format(cell.get_pddl_name(), southwestcell.get_pddl_name()))

        return tile_object_strs, tile_fact_strs

    def get_cell_map_pddl_radius(self, radius=8):
        """
            Returns PDDL objects and facts for the current level with the given radius (default=8)
        """
        object_strs = []
        fact_strs = []
        for curr_y in range(self.min_y, self.max_y + radius):
            for curr_x in range(self.min_x, self.max_x + radius):
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