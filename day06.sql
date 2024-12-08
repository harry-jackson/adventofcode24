-- Quite a horrible solution but it works!

-- Read the data and split into a list. Add i coordinate.
create temp table input_data as
select
    raw_input,
    string_split(raw_input, '') as input_list,
    row_number() over () as i
from read_csv('data/day06.txt', header = false, columns = {'raw_input': 'varchar'});

-- Get the i and j size of the input data.
create temp table size_data as
select last(i) as i_size, any_value(len(input_list)) as j_size from input_data;

-- Metadata for the cardinal directions. 
create temp table direction_data as
select * from (values ('N', 'E', -1, 0), ('E', 'S', 0, 1), ('S', 'W', 1, 0), ('W', 'N', 0, -1)) as t (direction, next_direction, d_i, d_j);

-- Unnest the input data into i, j coordinates.
create temp table flat_input_data as
select
    unnest(input_list) as input_character,
    i,
    generate_subscripts(input_list, 1) as j
from input_data;

-- Obstacles.
create temp table obstacles as 
select i, j from flat_input_data where input_character = '#';

-- Start position.
create temp table start_position as
select 'N' as direction, i, j from flat_input_data where input_character = '^';

create table steps (i int, j int);

with recursive journey as 
(
    -- Recursive CTE calculating the steps the guard takes before leaving the map.
    select *, false as guard_left_map from start_position

    union all

    select
        -- if there is an obstacle in the way, stay in position and turn right.
        -- otherwise, move one step in the current direction. 
        case when obs.i is null then jrny.direction else next_direction end as direction,
        case when obs.i is null then jrny.i + d_i else jrny.i end as i,
        case when obs.j is null then jrny.j + d_j else jrny.j end as j,
        jrny.i < 1 or jrny.j < 1 or jrny.i > i_size or jrny.j > j_size as guard_left_map,
        
    from journey jrny
    cross join size_data
    inner join direction_data d 
    on jrny.direction = d.direction and not guard_left_map
    left join obstacles obs 
    on jrny.i + d_i = obs.i and jrny.j + d_j = obs.j
)

-- Steps = distinct positions the guard moves through.
insert into steps
select distinct i, j from journey cross join size_data where i >= 1 and j >= 1 and i <= i_size and j <= j_size;

-- Part 2: try putting an obstacle at each point on the path and 
-- see whether it causes a loop.

-- Possible obstacle locations - anywhere on the path other than the starting position. 
create temp table new_obstacles as
select i, j, row_number() over () as new_obstacle_id
from steps 
anti join start_position 
using (i, j);

-- Combine each new obstacle with the existing obstacles. 
create temp table all_possible_obstacles as 
select o.i, o.j, n.new_obstacle_id
from obstacles o cross join new_obstacles n

union all

select * from new_obstacles;

-- Too slow to calculate every step now, so create a network
-- where each node is the guard colliding with an obstable, and 
-- the edges go straight from one obstacle to the next one in the way. 
-- Do this for every new obstacle that we added.
create temp table unfiltered_edges_part_2 as
select 
    o_1.new_obstacle_id,
    'N' as direction, o_1.i, o_1.j,
    'E' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by o_2.i, o_2.j) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i = o_1.i + 1 and o_2.j > o_1.j

union all

select 
    o_1.new_obstacle_id,
    'E' as direction, o_1.i, o_1.j,
    'S' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by o_2.i, o_2.j) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i > o_1.i and o_2.j = o_1.j - 1

union all

select 
    o_1.new_obstacle_id,
    'S' as direction, o_1.i, o_1.j,
    'W' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by -o_2.i, -o_2.j) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i = o_1.i - 1 and o_2.j < o_1.j

union all

select 
    o_1.new_obstacle_id,
    'W' as direction, o_1.i, o_1.j,
    'N' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by -o_2.i, -o_2.j) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i < o_1.i and o_2.j = o_1.j + 1;

-- The edge filter ensures that each obstacle is only joined to the next one on the path. 
create temp table edges_part_2 as
select new_obstacle_id, direction, i, j, next_direction, next_i, next_j
from unfiltered_edges_part_2
where edge_filter == 1;

-- Calculate the first collision for each added obstacle. 
create temp table first_collision_unfiltered_part_2 as 
select new_obstacle_id, start_position.direction, obs.i, obs.j, row_number() over (partition by new_obstacle_id order by -obs.i) as edge_filter
from start_position inner join all_possible_obstacles obs
on obs.i < start_position.i and obs.j = start_position.j;

create temp table first_collision_part_2 as
select new_obstacle_id, direction, i, j from first_collision_unfiltered_part_2 where edge_filter = 1;

with recursive journey_part_2 as (
    -- Recursive CTE to plot the guard's journey with each added obstacle.
    -- Keep track of the journey so far and halt with looped=true if guard is in a loop. 
    select *, 'start' as position_string, false as looped, '' as journey_so_far from first_collision_part_2

    union all

    select
        E.new_obstacle_id,
        E.next_direction as direction,
        E.next_i as i,
        E.next_j as j,
        E.next_direction || cast(E.next_i as varchar) || ',' || cast(E.next_j as varchar) as position_string,
        len(regexp_extract_all(journey_so_far, position_string)) >= 2 as looped,
        journey_so_far || '->' || position_string as journey_so_far,
    from journey_part_2 jrny inner join edges_part_2 E
    on jrny.new_obstacle_id = E.new_obstacle_id and jrny.direction = E.direction and jrny.i = E.i and jrny.j = E.j 
    and not looped
)

select
    -- Unique locations visited.
    (select count(*) from steps) as part_1,
    -- New obstacles that caused a loop. 
    (select count(*) from journey_part_2 where looped) as part_2