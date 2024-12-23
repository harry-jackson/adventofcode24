with input_data as
(
    -- Read input data into one column. 
    select 
    row_number() over () as i,
    string_split(raw_input, '') as letter_list
    from read_csv('data/day04.txt', header = false, columns = {'raw_input': 'varchar'})
), letters as
(
    -- Turn into long list of letters.
    -- i is row index.
    -- j is column index.
    select 
    i,
    generate_subscripts(letter_list, 1) as j,
    unnest(letter_list) as letter
    from input_data 
), 
steps as (select unnest(range(4)) as step),
shift_i as (select unnest(range(-1, 2)) as d_i),
shift_j as (select d_i as d_j from shift_i),
shifted_letters as
(
    -- This table shifts the i and j indices of each letter in a consistent
    -- direction for 0 to 3 steps. 
    -- This will allow us to find 3- and 4-length strings in any direction.
    select
    step,
    d_i,
    d_j,
    i - step * d_i as i,
    j - step * d_j as j,
    letter
    from steps cross join shift_i cross join shift_j cross join letters 
    where not (d_i == 0 and d_j == 0)
    order by step
), three_character_strings as 
(
    -- Three character strings formed by concatenating letters shifted
    -- in the same direction by 0 to 2 steps.
    select
    d_i,
    d_j,
    i,
    j,
    string_agg(letter, '') as three_character_string
    from shifted_letters 
    where step < 3
    group by d_i, d_j, i, j
), four_character_strings as 
(
    -- Similar for four-character strings.
    select
    string_agg(letter, '') as four_character_string
    from shifted_letters
    group by d_i, d_j, i, j
), central_diagonal_mas_indices as 
(
    -- Find all diagonal MAS strings (i.e. ones where both d_i and d_j != 0).
    -- Get the i, j location of the central character (A).
    -- Give each occurence an id. 
    select 
    i + d_i as i, 
    j + d_j as j, 
    row_number() over () as mas_id 
    from three_character_strings 
    where three_character_string == 'MAS'
    and d_i * d_j != 0
), x_mas_locations as
(
    -- Get distinct diagonal MAS strings where the A is in the same place.
    select 
    t0.i,
    t0.j,
    t0.mas_id as mas_id_0,
    t1.mas_id as mas_id_1
    from central_diagonal_mas_indices t0
    inner join central_diagonal_mas_indices t1
    on t0.i = t1.i and t0.j = t1.j and t0.mas_id < t1.mas_id
)

 select
    -- Part 1 = four-character XMAS strings.
    (select count(*) from four_character_strings where four_character_string == 'XMAS') as part_1,
    -- Part 2 = distinct diagonal MAS strings that cross in the middle.
    (select count(*) from x_mas_locations) as part_2