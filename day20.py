import numpy as np
import networkx as nx
import numpy.typing as npt
from typing import List, Tuple
from dataclasses import dataclass
from copy import deepcopy
from collections import defaultdict

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

with open('data/day20.txt', 'r') as f:
    lines = [list(line.strip()) for line in f.readlines()]

M = np.array(lines)

directions = {'N': (-1, 0), 'E': (0, 1)}

start_point = index_where(M == 'S')
end_point = index_where(M == 'E')

M[start_point] = '.'
M[end_point] = '.'

G = nx.Graph()

road_tiles = indices_where(M == '.')

for d in directions:
    d_i, d_j = directions[d]
    for i, j in indices_where((M == '.') & (np.roll(M, [-d_i, -d_j], axis = [0, 1]) == '.')):
        G.add_edge((i, j), (i + d_i, j + d_j), distance = 1, intermediate_nodes = [])

original_G = deepcopy(G)

nodes_to_remove = []
for i, j in G.nodes():
    if (i, j) in [start_point, end_point]:
        continue

    connected_edges = list(G.edges((i, j)))
    connected_nodes = list(G.neighbors((i, j)))

    if len(connected_edges) == 2 and not any([node in [start_point, end_point] for node in connected_nodes]):
        distance = sum([G.edges[e]['distance'] for e in connected_edges])

        intermediate_node_list = [G.edges[e]['intermediate_nodes'] for e in connected_edges]
        intermediate_nodes = intermediate_node_list[0] + intermediate_node_list[1] + [(i, j)]

        G.add_edge(connected_nodes[0], connected_nodes[1], distance = distance, intermediate_nodes = intermediate_nodes)
        nodes_to_remove.append((i, j))

for node in nodes_to_remove:
    G.remove_node(node)

def measure_path(G: nx.Graph, p: List[Tuple[int, int]], measure: str = 'distance') -> int:
    return sum([G.edges[e][measure]for e in zip(p[:-1], p[1:])])

shortest_path_without_cheating = nx.shortest_path(G, start_point, end_point, weight = distance)

fastest_time_without_cheating = measure_path(G, shortest_path_without_cheating)

@dataclass
class Node_Info:
    id: Tuple[int, int]
    distance_from_start: int
    distance_from_end: int

node_info = {}

for node in G.nodes():
    distance_from_start = measure_path(G, nx.shortest_path(G, start_point, node))
    distance_from_end = measure_path(G, nx.shortest_path(G, node, end_point))
    node_info[node] = Node_Info(id = node, distance_from_start = distance_from_start, distance_from_end = distance_from_end)

for edge in G.edges():
    node_0, node_1 = edge
    for node in G.edges[edge]['intermediate_nodes']:
        distance_from_start = min(node_info[node_0].distance_from_start + nx.shortest_path_length(original_G, node_0, node),
                                  node_info[node_1].distance_from_start + nx.shortest_path_length(original_G, node_1, node))
        
        distance_from_end = min(node_info[node_0].distance_from_end + nx.shortest_path_length(original_G, node_0, node),
                                node_info[node_1].distance_from_end + nx.shortest_path_length(original_G, node_1, node))

        node_info[node] = Node_Info(id = node, distance_from_start = distance_from_start, distance_from_end = distance_from_end)

shortcuts = []

for d in directions:
    d_i, d_j = directions[d]
    for i, j in indices_where((M == '.') & (np.roll(M, [-d_i, -d_j], axis = [0, 1]) == '#') & (np.roll(M, [-d_i * 2, -d_j * 2], axis = [0, 1]) == '.')):
        shortcuts.append(((i, j), (i + 2 * d_i, j + 2 * d_j)))
        shortcuts.append(((i + 2 * d_i, j + 2 * d_j), (i, j)))

good_cheats = 0
for cheat_start, cheat_end in shortcuts:
    time_with_cheating = node_info[cheat_start].distance_from_start + 2 + node_info[cheat_end].distance_from_end
    
    time_saved = fastest_time_without_cheating - time_with_cheating

    if time_saved >= 100:
        good_cheats += 1

print(f'Part 1: {good_cheats}')

def manhattan_distance(point_0: Tuple[int, int], point_1: Tuple[int, int]) -> int:
    i_0, j_0 = point_0
    i_1, j_1 = point_1
    return abs(i_1 - i_0) + abs(j_1 - j_0)

good_cheats_part_2 = 0
for cheat_start in road_tiles:
    for cheat_end in road_tiles:
        cheat_distance = manhattan_distance(cheat_start, cheat_end)
        if cheat_distance <= 20:
            time_with_cheating = node_info[cheat_start].distance_from_start + cheat_distance + node_info[cheat_end].distance_from_end
            time_saved = fastest_time_without_cheating - time_with_cheating
            if time_saved >= 100:
                good_cheats_part_2 += 1

print(f'Part 2: {good_cheats_part_2}')