-- duckdb solution

drop table if exists input_data;

-- Read the input data.
-- Split into list of levels.
-- Add a row number to indicate report number. 
create table input_data as 
select raw_input,
str_split(raw_input, ' ') as level_list,
row_number() over() as report
from 
read_csv('data/day02.txt', columns = {'raw_input': 'varchar'}, header = False);

with reports as
(
    -- Unnest the level_list into level_value and add a level_index
    select 
    report,
    level_list,
    generate_subscripts(level_list, 1) as level_index,
    cast(unnest(level_list) as integer) as level_value,
    from input_data
), reports_with_removed_level as 
(
    -- We want to try removing each level for part 2. 
    -- Make a copy of each report's data for every level index,
    -- and also for level index 0 (indicating nothing has been removed).
    select 
    report, 
    level_index,
    level_value, 
    generate_subscripts(list_append(level_list, '0'), 1) - 1 as removed_level_index
    from reports
    order by removed_level_index, report, level_index
), rules as 
(
    -- Check whether each level passes the increase or decrease rules. 
    -- Filter here so that level_index != removed_level_index. 
    select
    removed_level_index,
    report,
    level_index,
    level_value,
    lag(level_value) over (partition by report, removed_level_index) as lagged_value,
    level_value - lagged_value as diff,
    diff >= 1 and diff <= 3 as increase_rule,
    diff <= -1 and diff >= -3 as decrease_rule
    from reports_with_removed_level
    where level_index != removed_level_index
), passing_rules as 
(
    -- Check if all increase rules are passed or all decrease rules are passed. 
    select 
    report,
    removed_level_index,
    bool_and(increase_rule) or bool_and(decrease_rule) as pass
    from rules
    where lagged_value is not null
    group by report, removed_level_index
), passing_rules_with_up_to_one_removed_level as 
(
    -- Check if the report passed with any of the levels removed, or with no levels removed. 
    select
    report,
    bool_or(pass) as pass
    from passing_rules
    group by report
)

select 
(
    -- Part 1: check how many reports passed with removed_level_index 0 (indicating no levels removed). 
    select count(*) from passing_rules 
    where pass and removed_level_index == 0
) as part_1,
(
    -- Part 2: check how many passed with up to 1 level removed. 
    select count(*) from passing_rules_with_up_to_one_removed_level
    where pass
) as part_2