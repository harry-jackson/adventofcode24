-- Read input data into one column. 
create temp table input_data as
select 
    raw_input,
    row_number() over () as instruction_id,
from read_csv('data/day05.txt', header = false, columns = {'raw_input': 'varchar'});

-- Extract ordered pairs of pages (before and after pages).
create temp table order_instructions as 
select
    string_split(raw_input, '|') as order_pair,
    cast(order_pair[1] as int) as page_before,
    cast(order_pair[2] as int) as page_after
from input_data
where raw_input like '%|%';

-- Extract lists of pages in each manual, with a manual id. 
create temp table manual_lists as
select
    instruction_id as manual_id,
    string_split(raw_input, ',') as manual_page_list,
    cast(manual_page_list[cast((len(manual_page_list) + 1) / 2 as int)] as int) as middle_page
from input_data
where raw_input like '%,%';

-- Unnest the pages for each manual. 
create temp table unnested_manuals as
select 
    manual_id,
    unnest(manual_page_list) as page_before,
    manual_page_list
from manual_lists;

-- Unnest again to get all possible orders for each pair of pages. 
create temp table possible_page_orderings as 
select 
    manual_id,
    page_before,
    unnest(manual_page_list) as page_after
from unnested_manuals;

-- Get the valid page orderings by joining on to the instructions. 
create temp table valid_page_orderings as
select O.*
from possible_page_orderings O
inner join order_instructions I
on O.page_before = I.page_before and O.page_after = I.page_after;

with recursive manual_order_finding_recursive as
(
    -- Recursive CTE to get an order number for each page within each manual. 

    -- First select the page in each manual with no predecessors. 
    select distinct
        o1.manual_id,
        page_before as page_number,
        0 as page_order
    from valid_page_orderings o1
    anti join (select manual_id, page_after as page_before from valid_page_orderings) o2
    using (manual_id, page_before)

    union all

    -- Recursive step - join on to valid page orderings. 
    select distinct
        o3.manual_id,
        page_after as page_number,
        page_order + 1 as page_order
    from manual_order_finding_recursive o3
    inner join valid_page_orderings o4
    on o3.manual_id = o4.manual_id and o3.page_number = o4.page_before
    
), manual_order as 
(
    -- Take the maximum page_order to get a single order number for each page. 
    -- This is like removing shortcuts in the graph of the page orders. 
    select
        manual_id,
        page_number,
        max(page_order) as page_order
    from manual_order_finding_recursive
    group by manual_id, page_number
), sorted_manuals as
(
    -- Aggregate the sorted page numbers into a sorted page list for each manual. 
    select 
    manual_id, 
    list(page_number order by page_order) as sorted_manual_page_list
    from manual_order
    group by manual_id
    order by manual_id
), results as
(
    -- Join on to the input lists, find the sorted middle page, 
    -- check which manuals are sorted to begin with.
    select
    L.manual_id,
    L.manual_page_list,
    S.sorted_manual_page_list,
    L.middle_page,
    cast(S.sorted_manual_page_list[cast((len(S.sorted_manual_page_list) + 1) / 2 as int)] as int) as sorted_middle_page,
    L.manual_page_list == S.sorted_manual_page_list as is_correctly_sorted
    from manual_lists L
    inner join sorted_manuals S
    on L.manual_id = S.manual_id
)

 select
    -- Part 1 = sum of middle pages for manuals correctly sorted in the input. 
    (select sum(middle_page) from results where is_correctly_sorted) as part_1,
    -- Part 2 = sum of middle pages from the sorted manuals that were incorrectly sorted in the input.
    (select sum(sorted_middle_page) from results where not is_correctly_sorted) as part_2
