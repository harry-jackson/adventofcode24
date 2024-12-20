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

with open('data/day20.txt', 'r') as f:
    lines = [list(line.strip()) for line in f.readlines()]

def road_map_to_graph(M: npt.NDArray[np.str_], wall_character: str = '#') -> nx.Graph:
    directions = {'N': (-1, 0), 'E': (0, 1)}

    G = nx.Graph()

    for d in directions:
        d_i, d_j = directions[d]
        for i, j in indices_where((M != wall_character) & (np.roll(M, [-d_i, -d_j], axis = [0, 1]) != wall_character)):
            G.add_edge((i, j), (i + d_i, j + d_j), distance = 1, intermediate_nodes = [])
    
    return G

def manhattan_distance(point_0: Tuple[int, int], point_1: Tuple[int, int]) -> int:
    i_0, j_0 = point_0
    i_1, j_1 = point_1
    return abs(i_1 - i_0) + abs(j_1 - j_0)

def main() -> None:

    M = np.array(lines)

    start_point = index_where(M == 'S')
    end_point = index_where(M == 'E')

    road_tiles = indices_where(M != '#')

    G = road_map_to_graph(M)

    fastest_time_without_cheating = nx.shortest_path_length(G, start_point, end_point)

    distance_from_start = nx.single_source_shortest_path_length(G, start_point)
    distance_from_end = dict(nx.single_target_shortest_path_length(G, end_point))

    good_cheats = 0
    good_cheats_part_2 = 0
    for cheat_start in road_tiles:
        for cheat_end in road_tiles:

            cheat_distance = manhattan_distance(cheat_start, cheat_end)

            # Part 1: cheats of length 2
            if cheat_distance == 2:
                time_with_cheating = distance_from_start[cheat_start] + cheat_distance + distance_from_end[cheat_end]
                time_saved = fastest_time_without_cheating - time_with_cheating
                if time_saved >= 100:
                    good_cheats += 1

            # Part 2: cheats of length <= 20
            if cheat_distance <= 20:
                time_with_cheating = distance_from_start[cheat_start] + cheat_distance + distance_from_end[cheat_end]
                time_saved = fastest_time_without_cheating - time_with_cheating
                if time_saved >= 100:
                    good_cheats_part_2 += 1

    print(f'Part 1: {good_cheats}')
    print(f'Part 2: {good_cheats_part_2}')

if __name__ == '__main__':
    main()