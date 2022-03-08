import matplotlib.collections as mc
import numpy as np
import numpy.random as nr
from itertools import product
import matplotlib.pyplot as plt
import pickle

from dungeongenerator import DungeonGenerator, DungeonRoom
from dungeongenerator import CharacterCodes


default_character_codes = CharacterCodes()

class SprintMap:
    def __init__(self, dungeonGraph,
                 dungeonRooms,
                 dungeonGrid,
                 character_codes=default_character_codes):
        self.dungeonGraph = dungeonGraph
        self.dungeonRooms = dungeonRooms
        self.dungeonGrid = dungeonGrid
        self.dungeonWalls = None
        self.character_codes = character_codes

    def verticalWall(self, i, j, deltaX):
        midpoint = 0.5 * (i + (i + deltaX))
        bottom, top = j - 0.5, j + 0.5
        return ((midpoint, bottom), (midpoint, top))

    def horizontalWall(self, i, j, deltaY):
        midpoint = 0.5 * (j + (j + deltaY))
        left, right = i - 0.5, i + 0.5
        return ((left, midpoint), (right, midpoint))

    def getSprintMapString(self):
        lines = []
        # Taking the transpose, and then using the weird indexing is needed to make it
        # align with the matplotlib plots of the raw graph data.
        for l in list((self.dungeonGrid.T)[::-1, :]):
            lines.append("".join(list(l)))
        return "\n".join(lines)

    def getWalls(self):
        if self.dungeonWalls == None:
            EMPTY_CHAR = self.character_codes.EMPTY_CHAR
            SOLID_CHAR = self.character_codes.SOLID_CHAR
            dimx, dimy = self.dungeonGrid.shape
            walls = set()
            for i, j in product(range(dimx), range(dimy)):
                if self.dungeonGrid[i, j] == EMPTY_CHAR:
                    for k in [-1, 1]:
                        if 0 <= i + k < dimx:
                            if self.dungeonGrid[i + k, j] == SOLID_CHAR:
                                walls.add(self.verticalWall(i, j, k))
                        if 0 <= j + k < dimy:
                            if self.dungeonGrid[i, j + k] == SOLID_CHAR:
                                walls.add(self.horizontalWall(i, j, k))
            wall_segments = [list(t) for t in list(walls)]
            self.dungeonWalls = wall_segments
        return self.dungeonWalls

    def plotDungeon(self, figsize=(10,8),
                    blocking=True):
        if self.dungeonWalls == None:
            self.getWalls()
        lc = mc.LineCollection(self.dungeonWalls)
        dimx, dimy = self.dungeonGrid.shape

        fig, ax = plt.subplots(figsize=figsize)
        plt.xlim(0, dimx)
        plt.ylim(0, dimy)
        ax.add_collection(lc)
        plt.show(block=blocking)



def getSprintMap(dungeonGraph=None,
                 max_number_rooms=12,
                 max_number_corridors=20,
                 max_size=(100,100),
                 min_room_dim_size=4,
                 max_room_dim_size=18,
                 map_code_chars=default_character_codes):
    # Returns a string that is the map for the sprint.
    # Ensures that all rooms are connected in the dungeon, and therefore the number of
    # rooms you end up with may be less than max_number_rooms. Similar for the number of corridors.
    if dungeonGraph == None:
        dG = DungeonGenerator()
        dungeonGraph = dG.randomDungeonGraph(max_number_rooms,
                                             max_number_corridors,
                                             bounding_rectangle_dimensions=max_size)
    else:
        # reuse the dungeonGraph that was passed in.
        pass
        #max_size = dungeonGraph.bounding_rectangle_dimensions

    min_corner_offset = min_room_dim_size//2 + 1
    max_corner_offset = max_room_dim_size//2 + 1
    embeddingData = dungeonGraph.embeddingData
    x_coords, y_coords = embeddingData['x_coords'], embeddingData['y_coords']
    dungeonNodes = [(x, y) for x, y in zip(x_coords, y_coords)]

    # Now expand nodes into full rooms:
    max_x, max_y = 0, 0
    min_x, min_y = np.inf, np.inf
    rooms = []
    for node_coords in dungeonNodes:
        bottomLeftCornerOffset = -nr.randint(min_corner_offset, max_corner_offset, size=2)
        topRightCornerOffset = nr.randint(min_corner_offset, max_corner_offset, size=2)
        z = np.array(node_coords)
        corners = [z + bottomLeftCornerOffset, z + topRightCornerOffset]
        max_x = max(max_x, corners[1][0])
        max_y = max(max_y, corners[1][1])
        min_x = min(min_x, corners[0][0])
        min_y = min(min_y, corners[0][1])
        corners = [tuple(x) for x in corners]
        dungeonRoom = DungeonRoom(corners=corners)
        rooms.append(dungeonRoom)

    wall_segments = []
    for room in rooms:
        wall_segments.extend(room.getBoundingWalls())

    # Now do work to make the map:
    X_offset = min_x - 2
    Y_offset = min_y - 2
    SOLID_CHAR, EMPTY_CHAR = map_code_chars.SOLID_CHAR, map_code_chars.EMPTY_CHAR
    dungeonGrid = np.full((max_x + 2 - X_offset + 1, max_y + 2 - Y_offset + 1), SOLID_CHAR)
    dungeonGridEmptyDict = {}

    # TODO: Implement corridors of width greater than just 1 square.
    corridors = dungeonGraph.embeddingData['corridors']
    for corridor in corridors:
        a, b = corridor[0], corridor[1]
        if a[0] == b[0]:
            i = 1
            x = a[0]
            m, n = min(a[i], b[i]), max(a[i], b[i])
            for j in range(m, n + 1):
                dungeonGridEmptyDict[(x, j)] = EMPTY_CHAR
        elif a[1] == b[1]:
            i = 0
            y = a[1]
            m, n = min(a[i], b[i]), max(a[i], b[i])
            for j in range(m, n + 1):
                dungeonGridEmptyDict[(j, y)] = EMPTY_CHAR
    for (i, j), c in dungeonGridEmptyDict.items():
        dungeonGrid[i - X_offset, j - Y_offset] = c
    for room in rooms:
        X, Y = room.getFillSubarrayIndices()
        dungeonGrid[X - X_offset, Y - Y_offset] = EMPTY_CHAR

    sprintMap = SprintMap(dungeonGraph, rooms, dungeonGrid)
    return sprintMap


'''
Note to self:
In a zsh shell you can generate a sample of 10 dungeons and save them in a directory called 
 generated_dungeons by running
(CommandPrompt $) for i ({0..9}); do python sprintmap.py -D generated_dungeons/dungeon-$i; done
'''

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rooms", "-r", dest="max_number_rooms", type=int, default=12,
                        help="Only the rooms that are part of the maximal connected dungeon component" \
                             + " will be included in the ouput dungeon. Default value is 12.")
    parser.add_argument("--max-corridors", "-c", dest="max_number_corridors", type=int, default=20,
                        help="Only the corridors that are part of the maximal connected dungeon component" \
                        + " will be included in the ouput dungeon. Default value is 20.")
    parser.add_argument("--max-grid-size", "-g", dest="max_size", nargs=2, type=int, default=[100, 100],
                        help="A space separated pair of two positive integers. Default value is \"100 100\".")
    parser.add_argument("--room-size-bounds", "-s", dest="room_size_bounds", nargs=2, type=int, default=[4, 18],
                        help="a pair of integers \"x y\". x is the minimum length of a rooms wall and y is the " \
                             + "maximum length of a rooms wall. Default values are 4 and 18.")
    parser.add_argument("--save-to-filename", dest="save_filename", type=str,
                        help="Where to save the SprintMap object that wraps the dungeon info.")
    parser.add_argument("--reload-sprint-map", dest="sprint_map_filename", type=str,
                        help="If you have previously saved a SprintMap object you can reload it using this argument.")
    parser.add_argument("--save-dungeon-plot-filename", "-D", dest="save_plot_filename", type=str,
                        help="Will save a png plot of the ouput dungeon to the provided filename.")
    parser.add_argument("--display-plot", dest="display_plot", default=False, action='store_true',
                        help="Display a plot of the dungeon. Blocks execution until you close the plot.")
    parser.add_argument("--save-map-string-filename", dest="save_map_string_filename", type=str,
                        help="Will save the character representation of the map to the provided filename.")

    args = parser.parse_args()

    if args.sprint_map_filename:
        with open(args.sprint_map_filename, 'rb') as f:
            sprintMap = pickle.load(f)
    else:
        max_size = tuple(args.max_size)
        min_room_size, max_room_size = tuple(args.room_size_bounds)
        sprintMap = getSprintMap(dungeonGraph=None,
                              max_number_rooms=args.max_number_rooms,
                              max_number_corridors=args.max_number_corridors,
                              max_size=max_size,
                              min_room_dim_size=min_room_size,
                              max_room_dim_size=max_room_size)

    #fig, ax = plt.subplots(figsize=(10,8))
    #ax = sprintMap.plotDungeon(ax, suppress_plot=True)
    walls = sprintMap.getWalls()
    lc = mc.LineCollection(walls)

    fig, ax = plt.subplots(figsize=(10,8))
    dimx, dimy = sprintMap.dungeonGrid.shape
    plt.xlim(0, dimx)
    plt.ylim(0, dimy)
    ax.add_collection(lc)
    if args.save_plot_filename:
        plt.savefig(args.save_plot_filename)
    if args.display_plot:
        plt.show(block=True)

    if args.save_map_string_filename:
        with open(args.save_map_string_filename, 'w') as f:
            f.write(sprintMap.getSprintMapString())
            f.write("\n")

    if args.save_filename:
        with open(args.save_filename, 'wb') as f:
            pickle.dump(sprintMap, f)












