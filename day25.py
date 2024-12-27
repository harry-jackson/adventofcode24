import numpy as np
import numpy.typing as npt

def block_to_array(block: str) -> npt.NDArray[np.bool]:
    return np.array([list(line) for line in block.split('\n')]) == '#'

with open('data/day25.txt', 'r') as f:
    blocks = ''.join(f.readlines()).split('\n\n')

keys = []
locks = []

for block in blocks:
    array = block_to_array(block)
    if np.all(array[0, :]):
        keys.append(array)
    elif np.all(array[-1, :]):
        locks.append(array)
    else:
        raise ValueError('Array is not a block or a key')

part_1 = 0
for key in keys:
    for lock in locks:
        if not np.any(key & lock):
            part_1 += 1

print(f'Part 1: {part_1}')