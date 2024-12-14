import networkx as nx
import numpy as np
import numpy.typing as npt
from typing import Tuple, List

def indices_where(m: npt.NDArray[np.bool]) -> List[Tuple]:
    """
    Takes a boolean matrix and returns a list of tuples representing 
    indices where the True values are.
    """
    args = [v.tolist() for v in np.where(m)]
    return list(zip(*args))

with open('data/day10.txt', 'r') as f:
    input_data = [line.strip() for line in f.readlines()]

m = np.int32([list(line) for line in input_data])

# Give the map a border of negative numbers for when we use np.roll later.
m = np.pad(m, 1, constant_values = -10)

G = nx.DiGraph()
for i, j in indices_where(m != -10):
    # Each node is a square of the map, represented by a coordinate tuple (i, j)
    G.add_node((i, j), height = m[i, j])

for i_shift, j_shift in ([1, 0], [-1, 0], [0, 1], [0, -1]):
    # Make connections from nodes to neighbouring nodes where the height is 1 greater. 
    for i, j in indices_where(np.roll(m, [i_shift, j_shift], axis = [0, 1]) - m == 1):
        G.add_edge((i, j), (i - i_shift, j - j_shift))

trailheads = indices_where(m == 0)

def get_end_points(G: nx.Graph, trailhead: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    For a graph G and a trailhead, return all the trail ends in the G reachable from 
    the trailhead. 
    """
    return [node for node in G.nodes if G.nodes[node]['height'] == 9 and nx.has_path(G, trailhead, node)]

total_score = 0
total_rating = 0

for trailhead in trailheads:
    trail_ends = get_end_points(G, trailhead)
    total_score += len(trail_ends)
    for trail_end in trail_ends:
        total_rating += len(list(nx.all_simple_paths(G, trailhead, trail_end)))

print(f'Part 1: {total_score}')
print(f'Part 2: {total_rating}')