import numpy as np
from scipy import ndimage

with open('data/day12.txt', 'r') as f:
    input_data = [line.strip() for line in f.readlines()]

m = np.array([list(line) for line in input_data])
letters = np.unique(m)

m = np.pad(m, 1, constant_values = '@')

total_price = 0
total_price_part_2 = 0

for letter in letters:

    mask, n_labels = ndimage.label(m == letter)

    for label in range(1, n_labels + 1):
        label_mask = mask == label
        area = np.sum(label_mask)

        perimeter = 0
        sides = 0
        for shift in ([0, 1], [0, -1], [1, 0], [-1, 0]):
            area_edges = label_mask > np.roll(label_mask, shift = shift, axis = [0, 1])
            
            _, n_sides = ndimage.label(area_edges)

            perimeter += np.sum(area_edges)
            sides += n_sides
        
        total_price += area * perimeter
        total_price_part_2 += area * sides

print(f'Part 1: {total_price}')
print(f'Part 2: {total_price_part_2}')