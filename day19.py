from functools import cache
from typing import List

def main() -> None:

    towels = []
    for line in open('data/day19.txt', 'r'):

        match line.strip().split(', '):
            case ['']:
                continue
            case [towel]:
                towels.append(towel)
            case [*towel_patterns]:
                patterns = towel_patterns

    @cache
    def ways_to_make_towel(towel: str) -> int:
        if towel == '':
            return 1
        
        res = 0
        for pattern in patterns:
            pattern_length = len(pattern)
            if towel[:pattern_length] == pattern:
                res += ways_to_make_towel(towel[pattern_length:])

        return res
    
    n_ways_to_make_towel = [ways_to_make_towel(towel) for towel in towels]

    possible_towels = [towel for towel, n_ways in zip(towels, n_ways_to_make_towel) if n_ways > 0]

    print(f'Part 1: {len(possible_towels)}')
    print(f'Part 2: {sum(n_ways_to_make_towel)}')

if __name__ == '__main__':
    main()