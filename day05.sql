with recursive input_data as
(
    -- Read input data into one column. 
    select 
    raw_input,
    row_number() over () as instruction_id,
    from read_csv('data/day05.txt', header = false, columns = {'raw_input': 'varchar'})
), order_instructions as 
(
    select
    string_split(raw_input, '|') as order_pair,
    cast(order_pair[1] as int) as page_before,
    cast(order_pair[2] as int) as page_after
    from input_data
    where raw_input like '%|%'
), manual_middle_page as
(
    select
    instruction_id as manual_id,
    string_split(raw_input, ',') as manual_page_list,
    cast(manual_page_list[cast((len(manual_page_list) + 1) / 2 as int)] as int) as middle_page
    from input_data
    where raw_input like '%,%'
), manuals as 
(
    select
    manual_id,
    cast(unnest(manual_page_list) as int) as page_number
    from manual_middle_page
), x as (
    select (o1.page_before) as page_number,
        0 as page_order
        from (select page_before from order_instructions) o1
        anti join (select page_after as page_before from order_instructions) o2
        using (page_before)
), page_ordering_helper as 
(
    select distinct(o1.page_before) as page_number,
        0 as page_order
        from (select page_before from order_instructions) o1
        anti join (select page_after as page_before from order_instructions) o2
        using (page_before)
    union all
        select 
            distinct(page_after) as page_number,
            page_order + 1 as page_order
        from page_ordering_helper o3
        inner join order_instructions o4
        on o3.page_number = o4.page_before
), page_ordering as
(
    select
    page_number,
    max(page_order) as page_order
    from page_ordering_helper
    group by page_number
), page_order_checks as 
(
    select
    manual_id, 
    m.page_number,
    page_order,
    page_order - lag(page_order, 1) over (partition by manual_id) as page_order_diff,
    page_order_diff > 0 as pass
    from manuals m
    inner join page_ordering p
    on m.page_number = p.page_number
), manual_checks as 
(
    select
    manual_id,
    bool_and(pass) as pass
    from page_order_checks
    where pass is not null
    group by manual_id
    order by manual_id   
), passing_manuals as
(
    select
    c.manual_id,
    middle_page
    from manual_checks c
    inner join manual_middle_page m
    on c.manual_id = m.manual_id
    where pass
)

select * from x