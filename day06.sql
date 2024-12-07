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
select last(i) as i_size, last(len(input_list)) as j_size from input_data;

-- Metadata for the cardinal directions. 
create temp table direction_data as
select * from (values ('N', -1, 0), ('E', 0, 1), ('S', 1, 0), ('W', 0, -1)) as t (direction, d_i, d_j);

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

-- Get the first collision from the starting position.
-- edge_filter here ensures we get the first obstacle that the guard will hit. 
create temp table first_collision_unfiltered as 
select start_position.direction, obs.i, obs.j, row_number() over (order by -obs.i) as edge_filter
from start_position inner join obstacles obs
on obs.i < start_position.i and obs.j = start_position.j;

create temp table first_collision as
select direction, i, j from first_collision_unfiltered where edge_filter = 1;

-- Network where the obstacles are nodes and the edges are straight unobstructed paths. 
-- The guard's journey is then a path on this network. 
-- edge_filter works as before. 
create temp table unfiltered_edges as
select 
    'N' as direction, o_1.i, o_1.j,
    'E' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.i, o_1.j order by o_2.j) as edge_filter
from obstacles o_1 inner join obstacles o_2
on o_2.i = o_1.i + 1 and o_2.j > o_1.j

union all

select 
    'E' as direction, o_1.i, o_1.j,
    'S' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.i, o_1.j order by o_2.i) as edge_filter
from obstacles o_1 inner join obstacles o_2
on o_2.i > o_1.i and o_2.j = o_1.j - 1

union all

select 
    'S' as direction, o_1.i, o_1.j,
    'W' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.i, o_1.j order by -o_2.j) as edge_filter
from obstacles o_1 inner join obstacles o_2
on o_2.i = o_1.i - 1 and o_2.j < o_1.j

union all

select 
    'W' as direction, o_1.i, o_1.j,
    'N' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.i, o_1.j order by -o_2.i) as edge_filter
from obstacles o_1 inner join obstacles o_2
on o_2.i < o_1.i and o_2.j = o_1.j + 1;

create temp table edges as
select direction, i, j, next_direction, next_i, next_j
from unfiltered_edges
where edge_filter == 1;

create temp table steps (i bigint, j bigint);
with recursive journey_from_first_collision as (
    -- Recursive CTE to find the journey as a list of nodes in the network. 
    -- Start with the first collision that we found earlier. 
    select * from first_collision

    union all

    -- Recursive step - find the next obstacle that the guard will hit. 
    select
        E.next_direction as direction,
        E.next_i as i,
        E.next_j as j
    from journey_from_first_collision jrny inner join edges E
    on jrny.direction = E.direction and jrny.i = E.i and jrny.j = E.j
), end_position as (
    -- Hack to calculate the point where the guard leaves the map. 
    select
        case when last(direction) = 'N' then 'E' when last(direction) = 'E' then 'S' when last(direction) = 'S' then 'W' when last(direction) = 'W' then 'N' end as direction,
        case when last(direction) = 'E' then last(i_size) + 1 when last(direction) = 'W' then 0 when last(direction) = 'N' then last(i) + 1 else last(i) - 1 end as i,
        case when last(direction) = 'N' then last(j_size) + 1 when last(direction) = 'S' then 0 when last(direction) = 'W' then last(j) + 1 else last(j) - 1 end as j
    from journey_from_first_collision cross join size_data
), journey as (
    -- Combine tables to get the full journey from start_position to leaving the map. 
    select t.*
    from (
        select *, 1 as collision_id from start_position
        union all
        select *, row_number() over () + 1 as collision_id from journey_from_first_collision
        union all
        select *, (select count(*) + 2 from journey_from_first_collision)  as collision_id from end_position
    ) t
), step_list as (
    -- Get the individual steps making up the journey. 
    select
        jrny.direction,
        collision_id,
        d_i,
        d_j,
        i,
        j,
        lag(i, 1) over (order by collision_id) as prev_i,
        lag(j, 1) over (order by collision_id) as prev_j,
        case when d_i != 0 then range(prev_i, i, d_i) else [i] end as steps_i,
        case when d_j != 0 then range(prev_j, j, d_j) else [j] end as steps_j,
        list_resize(steps_i, len(steps_i) * len(steps_j), steps_i[1]) as steps_i_resized,
        list_resize(steps_j, len(steps_i) * len(steps_j), steps_j[1]) as steps_j_resized,
        list_zip(steps_i_resized, steps_j_resized) as step_list
    from journey jrny inner join direction_data
    on jrny.direction = direction_data.direction
)
-- Get the unique locations visited.
insert into steps
select distinct 
unnest(step_list)[1] as i, 
unnest(step_list)[2] as j 
from step_list;

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

-- Calculate the edges with this horrible query again
-- but this time we are doing it for each obstacle that we added.
create temp table unfiltered_edges_part_2 as
select 
    o_1.new_obstacle_id,
    'N' as direction, o_1.i, o_1.j,
    'E' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by o_2.j) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i = o_1.i + 1 and o_2.j > o_1.j

union all

select 
    o_1.new_obstacle_id,
    'E' as direction, o_1.i, o_1.j,
    'S' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by o_2.i) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i > o_1.i and o_2.j = o_1.j - 1

union all

select 
    o_1.new_obstacle_id,
    'S' as direction, o_1.i, o_1.j,
    'W' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by -o_2.j) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i = o_1.i - 1 and o_2.j < o_1.j

union all

select 
    o_1.new_obstacle_id,
    'W' as direction, o_1.i, o_1.j,
    'N' as next_direction, o_2.i as next_i, o_2.j as next_j,
    row_number() over (partition by o_1.new_obstacle_id, o_1.i, o_1.j order by -o_2.i) as edge_filter
from all_possible_obstacles o_1 inner join all_possible_obstacles o_2
on o_2.new_obstacle_id = o_1.new_obstacle_id and o_2.i < o_1.i and o_2.j = o_1.j + 1;

create temp table edges_part_2 as
select new_obstacle_id, direction, i, j, next_direction, next_i, next_j
from unfiltered_edges_part_2
where edge_filter == 1;

-- Calculate the first collision again for each added obstacle. 
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
    on jrny.new_obstacle_id = E.new_obstacle_id and jrny.direction = E.direction and jrny.i = E.i and jrny.j = E.j and not looped
)

select
    -- Unique locations visited.
    (select count(*) from steps) as part_1,
    -- New obstacles that caused a loop. 
    (select count(distinct new_obstacle_id) from journey_part_2 where looped) as part_2