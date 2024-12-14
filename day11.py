from math import log10, ceil
from functools import cache
from typing import List

with open('data/day11.txt', 'r') as f:
    stones = [int(w) for w in f.read().strip().split(' ')]

def n_digits(n: int) -> int:
    """Number of digits of n."""
    if n == 0:
        return 1
    else:
        return ceil(log10(n + 1))
    
def calc_stones(input_stones: List[int], N: int = 25) -> int:
    """Calculate the number of stones after N steps."""
    stones = [s for s in input_stones]
    stone_map = {}

    for _ in range(N):
        new_stones = []
        for stone in stones:

            if stone == 0:
                new_stones.append(1)
                stone_map[0] = [1]

            elif (nd := n_digits(stone)) % 2 == 0:
                half_digits = nd // 2
                stone_str = str(stone)
                first_half = int(stone_str[:half_digits])
                second_half = int(stone_str[half_digits:])
                new_stones += [first_half, second_half]
                stone_map[stone] = [first_half, second_half]
            
            else:
                stone_times_2024 = stone * 2024
                new_stones.append(stone_times_2024)
                stone_map[stone] = [stone_times_2024]

        stones = [s for s in new_stones if s not in stone_map]

    @cache
    def count_stones(stone: int, step: int, max_steps: int = N) -> int:
        """Memoized recursive function to count stones from each step."""
        if step == max_steps:
            return 1
        else:
            return sum([count_stones(s, step = step + 1, max_steps = max_steps) for s in stone_map[stone]])
        
    res = sum([count_stones(s, 0, max_steps = N) for s in input_stones])

    return res

print(f'Part 1: {calc_stones(stones, N = 25)}')
print(f'Part 2: {calc_stones(stones, N = 75)}')