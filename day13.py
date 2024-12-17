import re
import numpy as np
import numpy.typing as npt
from typing import List

def button_presses(m: npt.NDArray[np.int64]) -> npt.NDArray[np.int64] | None:
    """
    Returns the vector of button presses if there is an integer solution. 
    Otherwise returns None. 
    """
    button_effects = m[:, 0:2]
    target = m[:, 2]
    button_presses = np.linalg.inv(button_effects) @ target

    # Round vector to nearest integer
    button_presses = np.round(button_presses).astype(np.int64)

    # Check that the rounded version works (i.e. that the integer solution is right)
    if np.all(button_effects @ button_presses == target):
        return button_presses
    else:
        return None

def get_total_tokens(matrices: List[npt.NDArray[np.int64]], tokens_per_button: npt.NDArray[np.int64]) -> int:
    
    tokens = 0
    for m in matrices:
        n_presses = button_presses(m)
        if n_presses is not None:
            tokens += np.sum(tokens_per_button * n_presses)

    return tokens
        
def main():
    re_input_pattern = re.compile(r'[\:\,] ')

    matrices = []
    for line in open('data/day13.txt', 'r'):
        
        match re_input_pattern.split(line.strip()):
            case 'Button A', x, y:
                matrices.append(np.zeros([2, 3], dtype = np.int64))
                matrices[-1][:, 0] = (x[2:], y[2:])
            case 'Button B', x, y:
                matrices[-1][:, 1] = (x[2:], y[2:])
            case 'Prize', x, y:
                matrices[-1][:, 2] = (x[2:], y[2:])

    tokens_per_button = np.int64([3, 1])

    part_1 = get_total_tokens(matrices, tokens_per_button)

    part_2_adjustment = np.zeros([2, 3], dtype = np.int64)
    part_2_adjustment[:, 2] = 10000000000000

    matrices_part_2 = [m + part_2_adjustment for m in matrices]

    part_2 = get_total_tokens(matrices_part_2, tokens_per_button)

    print(f'Part 1: {part_1}')
    print(f'Part 2: {part_2}')

if __name__ == '__main__':
    main()