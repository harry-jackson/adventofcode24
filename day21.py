from typing import List, Tuple, Dict, Any
from functools import cache

def flatten(l: List[List[Any]]) -> List[Any]:
    return [a for b in l for a in b]

def id_to_coords(i: int) -> Tuple[int, int]:
    return (i // 3, i % 3)

def ways_to_move_between(p_0: Tuple[int, int], p_1: Tuple[int, int], forbidden_space: Tuple[int, int]) -> int:

    arrow_directions = {
        '^': (-1, 0),
        '>': (0, 1),
        'v': (1, 0),
        '<': (0, -1)
    }

    i_0, j_0 = p_0
    i_1, j_1 = p_1
    
    down_first = 'v' * (i_1 - i_0) + '<' * (j_0 - j_1) + '^' * (i_0 - i_1) + '>' * (j_1 - j_0)
    right_first = '>' * (j_1 - j_0) + '<' * (j_0 - j_1) + 'v' * (i_1 - i_0) + '^' * (i_0 - i_1) 
    up_first = '^' * (i_0 - i_1) + '<' * (j_0 - j_1) + 'v' * (i_1 - i_0) + '>' * (j_1 - j_0) 
    left_first =  '<' * (j_0 - j_1)  +  'v' * (i_1 - i_0)+ '^' * (i_0 - i_1) + '>' * (j_1 - j_0)
    
    valid_moves = {}
    for move_combination in [left_first, up_first, down_first, right_first]:
        i_0, j_0 = p_0
        valid = True
        for move in move_combination:
            d_i, d_j = arrow_directions[move]
            i_0 += d_i
            j_0 += d_j
            if (i_0, j_0) == forbidden_space:
                valid = False
                break

        if valid:
            valid_moves[move_combination] = None

    return [''.join(p) + 'A' for p in valid_moves.keys()]

def pad_moves(pad: Dict[str, Tuple[int, int]]) -> Dict[Tuple[Tuple[int, int], Tuple[int, int]], str]:
    forbidden_space = pad[' ']
    
    res = {}
    for key_0 in pad:
        for key_1 in pad:
            coords_0 = pad[key_0]
            coords_1 = pad[key_1]
            res[(key_0, key_1)] = ways_to_move_between(coords_0, coords_1, forbidden_space = forbidden_space)
    return res

def moves_to_write_code(code: str, pad_move_dict: Dict[Tuple[Tuple[int, int], Tuple[int, int]], str]) -> str:
    # arm always starts at A
    code = 'A' + code
    return ''.join([pad_move_dict[(key_0, key_1)] for key_0, key_1 in zip(code[:-1], code[1:])])

def main() -> None:

    with open('data/day21.txt', 'r') as f:
        codes = [line.strip() for line in f.readlines()]

    numeric_keys = '789456123 0A'
    arrow_keys = ' ^A<v>'

    pad_numbers = {key: id_to_coords(i) for i, key in enumerate(numeric_keys)}
    pad_arrow = {key: id_to_coords(i) for i, key in enumerate(arrow_keys)}
    
    pad_number_moves = pad_moves(pad_numbers)
    pad_arrow_moves = pad_moves(pad_arrow)

    @cache
    def shortest_input_sequence_length(sequence: str, numeric_pad: bool = True, depth: int = 0, max_depth: int = 2) -> int:

        pad = pad_number_moves if numeric_pad else pad_arrow_moves
        
        if depth == max_depth + 1:
            return len(sequence)
        res = 0
        
        sequence = 'A' + sequence
        
        for key_0, key_1 in zip(sequence[:-1], sequence[1:]):
            
            move_options = pad[(key_0, key_1)]
            min_moves = None
            
            for option in move_options:
                l = shortest_input_sequence_length(option, numeric_pad = False, depth = depth + 1, max_depth = max_depth)
        
                if min_moves is None or l < min_moves:
                    min_moves = l

            res += min_moves

        return res

    part_1 = []
    part_2 = []
    for code in codes:
        numeric_part_of_code = int(code.replace('A', ''))
        part_1.append((numeric_part_of_code, shortest_input_sequence_length(code, max_depth = 2)))
        part_2.append((numeric_part_of_code, shortest_input_sequence_length(code, max_depth = 25)))


    print(f'Part 1: {sum([a * b for a, b in part_1])}')
    print(f'Part 2: {sum([a * b for a, b in part_2])}')

if __name__ == '__main__':
    main()