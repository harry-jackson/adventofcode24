import networkx as nx
import numpy as np
import numpy.typing as npt
from typing import List, Tuple

def indices_where(m: npt.NDArray[np.bool]) -> List[Tuple]:
    """
    Takes a boolean matrix and returns a list of tuples representing 
    indices where the True values are.
    """
    args = [v.tolist() for v in np.where(m)]
    return list(zip(*args))

def index_where(m: npt.NDArray[np.bool]) -> List[Tuple]:
    """Given a matrix with one True entry, return the index of the True entry."""
    indices = indices_where(m)
    assert len(indices) == 1
    return indices[0]

with open('data/day16.txt', 'r') as f:
    lines = [list(line.strip()) for line in f.readlines()]

M = np.array(lines)

directions = {'N': (-1, 0), 'E': (0, 1)}

start_index = index_where(M == 'S')
end_index = index_where(M == 'E')

start_point = ('E', *start_index)
end_point = ('E', *end_index)

M[start_index] = '.'
M[end_index] = '.'

G = nx.Graph()

for d in directions:
    d_i, d_j = directions[d]
    for i, j in indices_where((M == '.') & (np.roll(M, [-d_i, -d_j], axis = [0, 1]) == '.')):
        G.add_edge((d, i, j), (d, i + d_i, j + d_j), distance = 1, intermediate_nodes = [])

for node in [start_point, end_point]:
    if node not in G.nodes():
        G.add_node(node)

for i, j in [(i, j) for d, i, j in G.nodes() if d == 'E']:
    if ('N', i, j) in G.nodes():
        if (i, j) == end_index:
            distance = 0
        else:
            distance = 1000
        
        G.add_edge(('E', i, j), ('N', i, j), distance = distance, intermediate_nodes = [])

nodes_to_remove = []
for d, i, j in G.nodes():
    if (d, i, j) in [start_point, end_point]:
        continue

    connected_edges = list(G.edges((d, i, j)))

    if len(connected_edges) == 2:
        distance = sum([G.edges[e]['distance'] for e in connected_edges])
        connected_nodes = list(G.neighbors((d, i, j)))

        if any([node in [start_point, end_point] for node in connected_nodes]):
            continue

        intermediate_node_list = [G.edges[e]['intermediate_nodes'] for e in connected_edges]
        intermediate_nodes = intermediate_node_list[0] + intermediate_node_list[1] + [(d, i, j)]
        G.add_edge(connected_nodes[0], connected_nodes[1], distance = distance, intermediate_nodes = intermediate_nodes)
        nodes_to_remove.append((d, i, j))

for node in nodes_to_remove:
    G.remove_node(node)

part_1 = nx.shortest_path_length(G, start_point, end_point, weight = 'distance')

squares_in_any_shortest_path = set()
for path in nx.all_shortest_paths(G, start_point, end_point, weight = 'distance'):
    squares_in_path = set([(i, j) for _, i, j in path])
    for edge in zip(path[:-1], path[1:]):
        squares_in_path = squares_in_path.union(set([(i, j) for _, i, j in G.edges[edge]['intermediate_nodes']]))

    squares_in_any_shortest_path = squares_in_any_shortest_path.union(squares_in_path)

print(squares_in_any_shortest_path)
part_2 = len(squares_in_any_shortest_path)

print(f'Part 1: {part_1}')
print(f'Part 2: {part_2}')