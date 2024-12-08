
-- List of three operators.
create temp table operators as
select *
from (values ('+'), ('*'), ('|')) operators(operator);

-- Read csv file, split into target and inputs, add a calculation id.
create temp table raw_input_data as
select 
    raw_input,
    string_split(raw_input, ': ') as input_pair,
    input_pair[1] as target_number,
    string_split(input_pair[2], ' ') as input_list,
    row_number() over () as calculation_id
from read_csv('data/day07.txt', header = false, columns = {'raw_input': 'varchar'});

-- Unnest the inputs, 
-- add an input index, 
-- add is_final_input flag for last input from each calculation,
-- cross join onto the operators.
create temp table input_data as
select
    calculation_id,
    cast(target_number as bigint) as target_number,
    generate_subscripts(input_list, 1) as input_index,
    cast(unnest(input_list) as bigint) as input_number,
    operator,
    input_index == len(input_list) as is_final_input
from raw_input_data
cross join operators;

with recursive calculations as (
    -- Recursive CTE to try all three operators at each calculation step.
    -- Keep track of operators used in operator_string
    -- to filter out calculations that used concatenation later. 

    -- Base case - first input from each calculation
    select 
        calculation_id, 
        target_number,
        input_index,
        input_number as calculated_number,
        '' as operator,
        '' as operator_string,
        is_final_input
    from input_data
    where input_index = 1 and operator = '+'

    union all

    -- Recursive step
    -- Use where condition R.calculated_number <= B.target_number
    -- to cut off calculations that exceed the target. 
    select 
        B.calculation_id,
        B.target_number,
        B.input_index,
            case when B.operator = '+' then R.calculated_number + B.input_number
            when B.operator = '*' then R.calculated_number * B.input_number
            when B.operator = '|' then cast(cast(R.calculated_number as varchar) || cast(B.input_number as varchar) as bigint) end
            as calculated_number,
        B.operator,
        R.operator_string || B.operator as operator_string,
        B.is_final_input
    from input_data B
    inner join calculations R
    on B.calculation_id = R.calculation_id
    and B.input_index = R.input_index + 1
    and R.calculated_number <= B.target_number
), working_calculations as (
    -- Calculations that reached the target at the final input. 
    select *
    from calculations
    where is_final_input and calculated_number = target_number
), working_calculations_without_concatenation as (
    -- Working calculations that didn't use concatenation (for part 1).
    select *
    from working_calculations
    where operator_string not like '%|%'
)

select 
    -- Sum of targets from distinct working calculations (not using concatenation). 
    (select sum(target_number) from (select distinct calculation_id, target_number from working_calculations_without_concatenation)) as part_1,
    -- Sum of targets from all distinct working calculations.
    (select sum(target_number) from (select distinct calculation_id, target_number from working_calculations)) as part_2