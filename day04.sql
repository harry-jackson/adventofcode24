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
), shift_i as 
(
    select * from (values (-1), (0), (1)) as t (d_i)
), shift_j as
(
    select d_i as d_j from shift_i
),
shift_ij as 
(
    -- Table to shift i and j indices in a direction. 
    select d_i, d_j from shift_i cross join shift_j where not (d_i == 0 and d_j == 0)
), shifted_letters as
(
    -- Letters with indices shifted in direction d_i for up to three steps. 
    select 
    d_i,
    d_j,
    i + d_i as i_1,
    j + d_j as j_1,
    i + 2 * d_i as i_2,
    j + 2 * d_j as j_2,
    i + 3 * d_i as i_3,
    j + 3 * d_j as j_3,
    letter
    from letters cross join shift_ij
), three_character_strings as 
(
    -- Three character strings formed by concatenating letters shifted
    -- in the same direction by two steps. 
    select
    t1.d_i,
    t1.d_j,
    i,
    j,
    t0.letter as c_0,
    t1.letter as c_1,
    t2.letter as c_2,
    c_0 || c_1 || c_2 as three_character_string
    from letters t0
    inner join shifted_letters t1 on t0.i = t1.i_1 and t0.j = t1.j_1
    inner join shifted_letters t2 on t0.i = t2.i_2 and t0.j = t2.j_2 and t1.d_i = t2.d_i and t1.d_j = t2.d_j
), four_character_strings as 
(
    -- Shift one more time to get four character strings. 
    select
    three_character_string || t3.letter as four_character_string
    from three_character_strings t2
    inner join shifted_letters t3 on t2.i = t3.i_3 and t2.j = t3.j_3 and t2.d_i = t3.d_i and t2.d_j = t3.d_j
), central_diagonal_mas_indices as 
(
    -- Find all diagonal MAS strings (i.e. ones where both d_i and d_j != 0).
    -- Get the i, j location of the central character (A). 
    -- Give each occurence an id. 
    select 
    i - d_i as i, 
    j - d_j as j, 
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
--
