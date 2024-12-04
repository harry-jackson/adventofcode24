 with input_data as
 (
    -- Read input data into single column.
    select
    raw_input
    from read_csv('data/day03.txt', columns = {'raw_input': 'varchar'}, header = False)
 ), instruction_list as
 (
    -- Concatenate rows of input data into a single string, then extract a list of the mul(), do() or don't() instructions
    -- Prepend a do() instruction for part 2 so that instructions are enabled from the beginning.
    select
    string_agg(raw_input, '') as input_string,
    list_prepend('do()', regexp_extract_all(input_string, '(mul\([0-9]+\,[0-9]+\)|do\(\)|don''t\(\))')) as instruction_list
    from input_data
 ), instructions as
 (
    -- Split the instructions into rows, extract the arguments, and multiply together.
    select
    unnest(instruction_list) as instruction,
    regexp_extract_all(instruction, '[0-9]+') as argument_list,
    cast(argument_list[1] as int) as arg_1,
    cast(argument_list[2] as int) as arg_2,
    arg_1 * arg_2 as result
    from instruction_list
 ), enabled_instructions as
 (
    -- Fill down the do() and don't() instructions with last_value, calculate results only where process is enabled.
    select
    instruction,
    case when instruction = 'do()' then true when instruction = 'don''t()' then false else null end as do_or_dont_instruction,
    last_value(do_or_dont_instruction ignore nulls) over (rows between unbounded preceding and current row) as is_enabled,
    if(is_enabled, result, null) as enabled_result
    from instructions
 )

 select
    -- Part 1 = Total results.
    (select sum(result) from instructions) as part_1,
    -- Part 2 = Total enabled results.
    (select sum(enabled_result) from enabled_instructions) as part_2