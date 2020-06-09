''' DCSSStateClass.py: Contains the DCSSState class. '''

# Other imports.
from simple_rl.mdp.StateClass import State
import math
from gamestate import CellMap, Cell
import gamestate

class DCSSState(State):
    ''' Class for DCSS States '''
    def __init__(self, game_state):
        State.__init__(self, data=[game_state])
    
    def __hash__(self):
        return hash(tuple(self.data))

    def __str__(self):
        return " state: " + str(self.data)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, DCSSState) #TODO add in other checks

    def num_visited_cells(self, visibility=2):
        cell_map = self.data[0].cellmap.get_cell_map_vector(visibility)
        num_visited_cells = 0
        
        for cell in cell_map:
            if cell[1] == 1:
                num_visited_cells += 1
        
        return num_visited_cells