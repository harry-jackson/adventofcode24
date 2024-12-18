import numpy as np
import networkx as nx
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

def get_shortest_path_if_exists(block_coords, grid_shape):
    
    M = np.zeros(grid_shape, dtype = np.int8)

    for bc in block_coords:
        M[bc] = 1

    M = np.pad(M, 1, constant_values = 1)

    start_point = (1, 1)
    end_point = grid_shape

    directions = {'N': (-1, 0), 'E': (0, 1)}

    G = nx.Graph()

    # Add edges between adjacent floor squares
    for d in directions:
        d_i, d_j = directions[d]
        for i, j in indices_where((M == 0) & (np.roll(M, [-d_i, -d_j], axis = [0, 1]) == 0)):
            G.add_edge((i, j), (i + d_i, j + d_j), distance = 1)

    if not nx.has_path(G, start_point, end_point):
        return None
    
    path = nx.shortest_path(G, start_point, end_point)

    return path

def main():
    with open('data/day18.txt', 'r') as f:
        lines = f.readlines()

    block_coords = [tuple(reversed([int(c) for c in line.split(',')])) for line in lines]


    max_i = max([i for i, j in block_coords])
    max_j = max([j for i, j in block_coords])
    grid_shape = (max_i + 1, max_j + 1)

    path_2024 = get_shortest_path_if_exists(block_coords[:1024], grid_shape = grid_shape)
    print(f'Part 1: {len(path_2024) - 1}')

    lower_bound = 0
    upper_bound = len(block_coords)

    assert get_shortest_path_if_exists(block_coords, grid_shape = grid_shape) is None

    while upper_bound - lower_bound > 1:
        trial_index = lower_bound + (upper_bound - lower_bound) // 2
        path = get_shortest_path_if_exists(block_coords[:trial_index], grid_shape = grid_shape)
        if path is None:
            upper_bound = trial_index
        else:
            lower_bound = trial_index

    y, x = block_coords[lower_bound]
    print(f'Part 2: {x},{y}')

if __name__ == '__main__':
    main()