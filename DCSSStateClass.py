''' DCSSStateClass.py: Contains the DCSSState class. '''

# Other imports.
from simple_rl.mdp.StateClass import State
import math
from gamestate import GameState,CellMap, Cell
import gamestate

class DCSSState(State):
    ''' Class for DCSS States '''
    def __init__(self, game_state, visibility):

        self.game_state = game_state
        self.cell_map_vector = self.game_state.cellmap.get_cell_map_vector(visibility)
        self.visibility = visibility
        self.total_visited_cells = self.game_state.get_tiles_visited()
        State.__init__(self, data=[self.cell_map_vector])
    
    def __hash__(self):

        return hash(tuple([(x[0],x[1]) for x in self.cell_map_vector]))#self.data))

    def __str__(self):
        return " state: " + str(self.data)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, DCSSState) and self.is_cell_map_equal(other)#TODO add in other checks

    def is_cell_map_equal(self, other):
        return_val = True
        if( len(self.cell_map_vector) != len (other.cell_map_vector)):
            return_val = False
        else:
            for cell in range(0,len(other.cell_map_vector)):
                if( other.cell_map_vector[cell][0] != self.cell_map_vector[cell][0] or other.cell_map_vector[cell][1] != self.cell_map_vector[cell][1]):
                    return_val = False

        return return_val

    def num_visited_cells(self):
        num_visited_cells = 0
        for cell in self.cell_map_vector:
            if cell[1] == 1:
                num_visited_cells += 1
        
        return num_visited_cells