-- duckdb solution

drop table if exists input_data;

-- Read the input data.
-- Split into left_input and right_input.
-- Calculate the order of the two input columns as left_index and right_index.
create table input_data as 
select 
raw_input,
str_split_regex(raw_input, ' +') as input_list,
cast(input_list[1] as int) as left_input,
cast(input_list[2] as int) as right_input,
row_number() over (order by left_input) as left_index,
row_number() over (order by right_input) as right_index
from 
read_csv('data/day01.txt', columns = {'raw_input': 'varchar'}, header = False);

with sorted_input_data as
(
    --- Calculate the absolute difference between the ordered left_input & right_input. 
    select 
    left_input, 
    right_input,
    abs(left_input - right_input) as absolute_difference
    from
    (select left_input, left_index from input_data) L 
    inner join 
    (select right_input, right_index from input_data) R
    on L.left_index = R.right_index
),
right_counts as
(
    -- Count the occurences of each number in right_input. 
    select 
    right_input,
    count(right_input) as count_in_right
    from input_data
    group by right_input
),
left_occurences_in_right as
(
    -- Inner join left_input on to the occurence counts from right_input. 
    -- Calculate the score (left_input * number of occurences in right_input). 
    select
    left_input,
    count_in_right,
    left_input * count_in_right as score
    from input_data inner join right_counts
    on input_data.left_input = right_counts.right_input
)
select
    -- Part 1 = Total absolute difference.
    (select sum(absolute_difference) from sorted_input_data) as part_1,
    -- Part 2 = Total score.
    (select sum(score) from left_occurences_in_right) as part_2
