import networkx as nx
import matplotlib.collections as mc
import numpy as np
import numpy.random as nr
from numpy.linalg import norm
from itertools import permutations, combinations
from scipy.stats import boltzmann


# default_character_codes = {"SOLID_CHAR": '*',
#                            "EMPTY_CHAR": ' '}

class CharacterCodes(dict):
    def __init__(self):
        super().__init__({"SOLID_CHAR": 'X',
                          "EMPTY_CHAR": '.'})
    def __getattr__(self, name):
        if name in super().keys():
            return self[name]
        else:
            raise KeyError(name)


default_character_codes = CharacterCodes()
#default_character_codes.SOLID_CHAR = 'X'
#default_character_codes.EMPTY_CHAR = '.'


class DungeonGraph(nx.graph.Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def setDungeonEmbedding(self, embeddingData):
        x_coords, y_coords, line_segments = embeddingData
        self.embeddingData = {'x_coords': x_coords,
                              'y_coords': y_coords,
                              'corridors': line_segments
                             }

class DungeonGenerator:
    def __init__(self):
        pass

    def connectNodes(self, n1, n2, dim_order=(0, 1)):
        if isinstance(dim_order, int):
            dim_order = (dim_order,)
        if isinstance(dim_order, str):
            if dim_order == 'random':
                dim_order = nr.choice([0, 1], size=2, replace=False)
        x, y = self.int_coord_dict[n1]
        w, z = self.int_coord_dict[n2]
        if n1 == n2:
            return []
        if x == w or y == z:
            line_segments = [[(x, y), (w, z)]]
        else:
            if dim_order[0] == 0:
                line_segments = [[(x, y), (w, y)], [(w, y), (w, z)]]
            if dim_order[0] == 1:
                line_segments = [[(x, y), (x, z)], [(x, z), (w, z)]]
        return line_segments

    def randomDungeonGraph(self, n_rooms,
                           n_corridors,
                           preference_for_long_corridors=0.2,
                           bounding_rectangle_dimensions=(20, 20)):
        n_vertices = n_rooms
        xdim_max, ydim_max = self.bounding_rectangle_dimensions = bounding_rectangle_dimensions
        nodes_x, nodes_y = nr.randint(xdim_max, size=n_vertices), nr.randint(ydim_max, size=n_vertices)
        nodes_coords = [np.array([x, y]) for x, y in zip(nodes_x, nodes_y)]
        node_coord_dict = {i: t for i, t in enumerate(nodes_coords)}
        self.int_coord_dict = {i: tuple(t) for i, t in node_coord_dict.items()}
        #x_coords, y_coords = zip(*self.int_coord_dict.values())

        nodes = list(range(n_vertices))
        L1_dist = {(i, j): norm(node_coord_dict[i] - node_coord_dict[j], ord=1) for i, j in permutations(nodes, r=2)}
        dists = [((i, j, L1_dist[(i, j)])) for i, j in combinations(nodes, 2)]
        dtype = [('node_1', int), ('node_2', int), ('L1_dist', float)]
        dists = np.array(dists, dtype=dtype)
        sorted_dists = np.sort(dists, order=['L1_dist'])

        n_connections = n_corridors
        n_possible_connections = len(sorted_dists)
        lambda_, N = preference_for_long_corridors, n_possible_connections
        pdf = [boltzmann.pmf(i, lambda_, N) for i in range(n_possible_connections)]
        chosen_connections = nr.choice(sorted_dists, size=n_connections, p=pdf, replace=False)

        # graph = nx.graph.Graph()
        graph = nx.graph.Graph()
        line_segments = []
        for i, j, dist in chosen_connections:
            graph.add_edge(i, j)
        components = list(nx.connected_components(graph))
        component_sizes = [len(C) for C in components]
        max_size_index = np.argmax(component_sizes)
        main_component = components[max_size_index]
        graph = nx.induced_subgraph(graph, main_component)
        graph = DungeonGraph(graph)
        included_corridors = [(i, j) for i, j, _ in chosen_connections if (i in graph.nodes() and j in graph.nodes())]
        for i, j in included_corridors:
            line_segments.extend(self.connectNodes(i, j, dim_order='random'))

        nodes = list(graph.nodes())
        x_coords = [self.int_coord_dict[i][0] for i in nodes]
        y_coords = [self.int_coord_dict[i][1] for i in nodes]
        graph.setDungeonEmbedding((x_coords, y_coords, line_segments))
        # lc = mc.LineCollection(line_segments)
        return graph

    def drawDungeon(self, dungeonGraph, ax):
        # ax is an axes object created by a call to plt.subplots():
        #   fig, ax = plt.subplots()
        embeddingData = dungeonGraph.embeddingData
        x_coords, y_coords = embeddingData['x_coords'], embeddingData['y_coords']
        lineSegments = embeddingData['corridors']
        lc = mc.LineCollection(lineSegments)
        ax.scatter(x_coords, y_coords)
        ax.add_collection(lc)

class DungeonRoom:
    def __init__(self, corners=None):
        self.corners = corners
        self.lineSegments = None
        if corners != None:
            self.n_corners = len(corners)
            self.corners = set([tuple(x) for x in self.corners])
            self.clockwise_corners_list = self.setup_corners_structure()

    def setup_corners_structure(self):
        # find a bottom most left node (might be more than one if more than 4 corners).
        # For now we just assume a standard rectangular room (that means we are given
        # 2 generating corners: the bottom left one and the top right one).
        for a in self.corners:
            other_corners = self.corners - set([a])
            dominating_corners = [b for b in other_corners if b[0] <= a[0] and b[1] <= a[1]]
            if len(dominating_corners) == 0:
                aBottomMostLeftCorner = a
                break
        return (aBottomMostLeftCorner, other_corners.pop())

    def getBoundingWalls(self):
        if self.lineSegments != None:
            return self.lineSegments
        else:
            lineSegments = []
            c = self.clockwise_corners_list
            for i in range(self.n_corners):
                corner = c[i]
                nextCorner = c[(i + 1) % self.n_corners]
                # One way:
                midpoint = (nextCorner[0], corner[1])
                # Or the other way. (If there are more than two generating corners then it might make sense
                # to randomly choose a different possible way for each pair of consecutive corners.):
                # midpoint = (corner[0], nextCorner[1])
                lineSegments.append((corner, midpoint))
                lineSegments.append((midpoint, nextCorner))
                # lineSegments.append([(c[i], c[(i+1)%self.n_corners])])
            self.lineSegments = lineSegments
            return self.lineSegments

    def getFillSubarrayIndices(self):
        # Returns a meshgrid of indices to be used when setting all of the squares that are in the
        # interior of the room to a particular character, for example " ".
        # (Assuming for now just a standard rectangular room.)
        a, b = self.clockwise_corners_list
        X_indices, Y_indices = np.meshgrid(np.arange(a[0] + 1, b[0]), np.arange(a[1] + 1, b[1]))
        return X_indices, Y_indices









