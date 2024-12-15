import numpy as np
import numpy.typing as npt
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Obstacle:
    i: int
    j: int
    icon: str

class Robot(Obstacle):
    # The robot isn't technically an obstacle but it's convenient to treat it as one.
    def __init__(self, i: int, j: int):
        super().__init__(i = i, j = j, icon = '@')

class Boulder(Obstacle):
    def __init__(self, i: int, j: int, icon: str):
        super().__init__(i = i, j = j, icon = icon)

class Wall(Obstacle):
    def __init__(self, i: int, j: int):
        super().__init__(i = i, j = j, icon = '#')

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

directions = {'^': (-1, 0), 'v': (1, 0), '<': (0, -1), '>': (0, 1)}

def pushed_objects(m: npt.NDArray[np.str_], coords: Tuple[int, int], direction: Tuple[int, int]) -> List[Obstacle]:
    """
    Given the map and some coordinates of an object pushing in a direction, get all the 
    objects that are being pushed. (I.e. if two boulders are next to each other and both 
    are being pushed, return both boulders). 
    The robot is included at the start of the list of pushed objects.

    Args:
        m: a numpy array representing the map
        coords: the coordinates of the object doing the pushing
        direction: the direction being pushed in 

    Returns:
        List of objects that are being pushed.
    """
    i, j = coords
    d_i, d_j = direction
    new_coords = (i + d_i, j + d_j)
    match m[i, j]:
        case '@':
            return [Robot(i, j)] + pushed_objects(m, new_coords, direction)
        case 'O':
            return [Boulder(i, j, 'O')] + pushed_objects(m, new_coords, direction)
        case '[':
            if direction == (0, -1):
                # If the left half of the boulder is being pushed left, just pass through 
                # to the next iteration to avoid double-counting (and infinite recursion).
                return pushed_objects(m, new_coords, direction)
            else:
                return [Boulder(i, j, '['), Boulder(i, j + 1, ']')] + pushed_objects(m, new_coords, direction) + pushed_objects(m, (i + d_i, j + 1 + d_j), direction)
        case ']':
            if direction == (0, 1):
                # If the right half of the boulder is being pushed right, just pass through 
                # to the next iteration to avoid double-counting (and infinite recursion).
                return pushed_objects(m, new_coords, direction)
            else:
                return [Boulder(i, j - 1, '['), Boulder(i, j, ']')] + pushed_objects(m, new_coords, direction) + pushed_objects(m, (i + d_i, j - 1 + d_j), direction)
        case '#':
            return [Wall(i, j)]
        case _:
            return []

def drive_robot(M: npt.NDArray[np.str_], instructions: List[str]) -> npt.NDArray[np.str_]:
    """Given the map and list of instructions, drive the robot around, and return the map at the end."""
    M = np.copy(M)
    
    robot = Robot(*index_where(M == '@'))

    for instruction in instructions:
        
        d_i, d_j = directions[instruction]

        all_pushed_objects = pushed_objects(M, (robot.i, robot.j), (d_i, d_j))
        
        if any([type(pushed_object) is Wall for pushed_object in all_pushed_objects]):
            # robot pushed into a wall - do nothing and continue to next instruction
            continue
        
        # clear and move all the pushed objects (the robot and the boulders)
        for obstacle in all_pushed_objects:
            M[obstacle.i, obstacle.j] = '.'
            obstacle.i += d_i
            obstacle.j += d_j

        # insert objects in their new location
        for obstacle in all_pushed_objects:
            M[obstacle.i, obstacle.j] = obstacle.icon

        # the robot is the first item in the returned list (check that this is true)
        robot = all_pushed_objects[0]
        assert type(robot) is Robot

    return M
    
def score_map(M: npt.NDArray[np.int8]) -> int:
    """Given the map, calculate the score using the boulder locations."""
    boulder_indices = indices_where(np.isin(M, ('[', 'O')))
    return sum ([100 * i + j for i, j in boulder_indices])


grid_rows = []
instructions = []
for line in open('data/day15.txt', 'r'):
    match chars := list(line.strip()):
        case ['#', *_]:
            grid_rows.append(chars)
        case ['<' | 'v' | '>' | '^', *_]:
            instructions += chars

M = np.array(grid_rows)

M_wide = np.repeat(M, 2, axis=1)
M_wide[:, ::2] = np.where(M_wide[:, ::2] == 'O', '[', M_wide[:, ::2])  
M_wide[:, 1::2] = np.where(M_wide[:, 1::2] == 'O', ']', M_wide[:, 1::2])  
M_wide[:, 1::2] = np.where(M_wide[:, 1::2] == '@', '.', M_wide[:, 1::2])  

print(f'Part 1: {score_map(drive_robot(M, instructions))}')
print(f'Part 2: {score_map(drive_robot(M_wide, instructions))}')