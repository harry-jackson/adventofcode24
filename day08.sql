-- Read input data into one column. 
create temp table raw_input_data as
select 
    raw_input,
    string_split(raw_input, '') as input_list,
    row_number() over () as i,
from read_csv('data/day08.txt', header = false, columns = {'raw_input': 'varchar'});

-- Get the size in the i and j dimensions, and the max of these two. 
create temp table size_data as
select 
    max(i) as i_size, 
    any_value(len(input_list)) as j_size,
    if(i_size > j_size, i_size, j_size) as max_size
from raw_input_data;

-- Unnest the antenna locations into rows with i, j coordinates. 
create temp table antennas as 
with input_data as (
    select
        unnest(input_list) as antenna_type,
        i,
        generate_subscripts(input_list, 1) as j
from raw_input_data
)
select row_number() over () as antenna_id, * from input_data where antenna_type != '.';

-- Find the antinodes by adding the vector from one antenna
-- to another to the position of one of them. 
create temp table antinode_locator as
select
    a_1.antenna_type,
    abs(a_1.i - a_2.i) as i_distance,
    abs(a_1.j - a_2.j) as j_distance,
    if(a_1.i > a_2.i, 1, -1) as i_direction,
    if(a_1.j > a_2.j, 1, -1) as j_direction,
    a_1.i + i_distance * i_direction as i,
    a_1.j + j_distance * j_direction as j,
from antennas a_1
inner join antennas a_2
on a_1.antenna_type = a_2.antenna_type and a_1.antenna_id != a_2.antenna_id;

-- Antinodes are at distinct coordinates within the map. 
create temp table antinodes as
select distinct i, j from antinode_locator
cross join size_data
where i >= 1 and i <= i_size and j >= 1 and j <= j_size;

-- Part 2:
-- Want to try antinodes at all locations in line with a pair of antennas.
create temp table steps as
select (unnest(range(-max_size, max_size + 1))) as step from size_data;

-- Try all coordinates in line for new antinodes.
create temp table antinode_locator_part_2 as 
select 
    gcd(i_distance, j_distance) as distance_gcd,
    i_distance // distance_gcd as i_step_size,
    j_distance // distance_gcd as j_step_size,
    i + i_direction * step * i_step_size as i,
    j + j_direction * step * j_step_size as j
from antinode_locator
cross join steps;
   
-- Antinodes are at distinct coordinates within the map. 
create temp table antinodes_part_2 as
select distinct i, j from antinode_locator_part_2
cross join size_data
where i >= 1 and i <= i_size and j >= 1 and j <= j_size;

select
    (select count(*) from antinodes) as part_1,
    (select count(*) from antinodes_part_2) as part_2