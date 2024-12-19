from pydantic import BaseModel
from typing import List
from dataclasses import dataclass, replace as dataclass_copy

@dataclass
class File:
    file_id: int
    location: int
    length: int

@dataclass
class Gap:
    location: int
    length: int

def move_files(files: List[File], gaps: List[Gap], partial_moves: bool = True) -> List[File]:
    """
    Takes a list of files and gaps. Moves files from the right into the leftmost gap.

    partial_moves: controls whether parts of files can move (True), or whether the gap must be 
    big enough for the whole file to move (False). True for part 1, False for part 2.

    Returns the list of all files sorted by their final location (ancending).
    """
    files = [dataclass_copy(f) for f in files]
    gaps = [dataclass_copy(g) for g in gaps]
    moved_files = []
    for file in reversed(files):
        for gap in gaps:
            if gap.location > file.location:
                # Files can only move to the left - if the gap is on the right, break.
                break
            elif gap.length > 0:
                # Gap length must be > 0 for any files to move.
                # If partial_moves is False, the gap must be big enough for the whole file.
                if not partial_moves and gap.length < file.length:
                    continue

                blocks_to_move = min(file.length, gap.length)
                
                moved_files.append(File(file_id = file.file_id, location = gap.location, length = blocks_to_move))

                gap.location += blocks_to_move
                gap.length -= blocks_to_move
                file.length -= blocks_to_move

                if file.length == 0:
                    break
                
    all_files = [f for f in files + moved_files if f.length != 0]
    return sorted(all_files, key = lambda x: x.location)

def checksum(files: List[File]) -> int:
    """Sum of the file id of each file part multiplied by its location."""
    res = 0
    for file in files:
        res += sum([file.file_id * i for i in range(file.location, file.location + file.length)])
    return res

def main():
    with open('data/day09.txt', 'r') as f:
        input_string = f.read().strip()

    input_nums = [int(char) for char in input_string]

    files = []
    gaps = []
    location = 0
    for i, n in enumerate(input_nums):
        if i % 2 == 0:
            files.append(File(file_id = i // 2, location = location, length = n))
        else:
            gaps.append(Gap(location = location, length = n))
        location += n


    part_1 = checksum(move_files(files, gaps))
    part_2 = checksum(move_files(files, gaps, partial_moves = False))

    print(f'Part 1: {part_1}')
    print(f'Part 2: {part_2}')

if __name__ == '__main__':
    main()