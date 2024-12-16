import re
import numpy as np
from math import prod
import gzip
from collections import defaultdict
from typing import Tuple, List
import numpy.typing as npt
from dataclasses import dataclass

@dataclass
class Robot:
    p: npt.NDArray[np.int64]
    v: npt.NDArray[np.int64]

re_input_pattern = re.compile(r'[0-9\-]+')

robots = []
for line in open('data/day14.txt', 'r'):
    p_x, p_y, v_x, v_y = re_input_pattern.findall(line)
    robots.append(Robot(p = np.int64([p_x, p_y]), v = np.int64([v_x, v_y])))

def move_robot(robot: Robot, floor_shape: npt.NDArray[np.int64], steps: int) -> Robot:
    """Move the robot a certain number of steps, and return a robot at the new position."""
    return Robot(p = (robot.p + robot.v * steps) % floor_shape, v = robot.v)

def get_quadrant(robot: Robot, floor_shape: npt.NDArray[np.int64]) -> Tuple[int, int] | None:
    """Find the quadrant the robot is in. Return None if it is in the middle of either axis."""
    centre = floor_shape // 2
    if any(robot.p == centre):
        return None
    else:
        return tuple(np.sign(robot.p - centre).tolist())

floor_shape = np.int64([101, 103])

steps = 100

quadrants = defaultdict(lambda: 0)
for robot in robots:
    final_position = move_robot(robot, floor_shape, steps)
    
    q = get_quadrant(final_position, floor_shape)

    if q is not None:
        quadrants[q] += 1

part_1 = prod(quadrants.values())

def draw_image(robots: List[Robot], floor_shape: npt.NDArray[np.int64], steps) -> npt.NDArray[np.bool]:
    """
    Find the locations of the robots after a certain number of steps.
    Returns a matrix with a 1 at each index containing at least one robot, 
    0 everywhere else.
    """
    M = np.zeros(floor_shape, dtype = np.bool)
    for robot in robots:
        final_position = move_robot(robot, floor_shape, steps)
        M[tuple(final_position.p)] = 1
    return M

def matrix_entropy(M: npt.NDArray[np.bool]) -> float:
    """
    Appproximates the entropy of a matrix by compressing it with gzip.
    Gives the number of compressed bytes divided by the number of original bytes. 

    The robots usually look like random noise, so their position matrix will have high entropy. 
    When they form an image of a Christmas tree, their position matrix will have some regularity, 
    and so have lower entropy. 
    """
    M_bytes = M.tobytes()
    compressed_M_bytes = gzip.compress(M_bytes)
    return len(compressed_M_bytes) / len(M_bytes)


# After 101 iterations the x values will repeat, similarly 103 iterations for y values.
# So the whole thing will start repeating after 101 * 103 (= prod(floor_shape)) iterations.
matrix_entropies = []
for steps in range(np.prod(floor_shape)):
    M = draw_image(robots, floor_shape, steps)  

    matrix_entropies.append(matrix_entropy(M))

# The picture of a Christmas tree has the lowest entropy of all the matrices. 
# Find the number of steps to get there.
steps_to_lowest_entropy = matrix_entropies.index(min(matrix_entropies))

M = draw_image(robots, floor_shape, steps_to_lowest_entropy)
M_char = M.astype(str)
M_char[~M] = ' '
M_char[M] = '@'

for row in M_char.transpose():
    print(''.join(row.tolist()))

print(f'Part 1: {part_1}')
print(f'Part 2: {steps_to_lowest_entropy}')