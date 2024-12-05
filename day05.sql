with recursive input_data as
(
    -- Read input data into one column. 
    select 
    raw_input,
    row_number() over () as instruction_id,
    from read_csv('data/test05.txt', header = false, columns = {'raw_input': 'varchar'})
), order_instructions as 
(
    select
    string_split(raw_input, '|') as order_pair,
    cast(order_pair[1] as int) as page_before,
    cast(order_pair[2] as int) as page_after
    from input_data
    where raw_input like '%|%'
), manual_lists as
(
    select
    instruction_id as manual_id,
    string_split(raw_input, ',') as manual_page_list,
    cast(manual_page_list[cast((len(manual_page_list) + 1) / 2 as int)] as int) as middle_page
    from input_data
    where raw_input like '%,%'
), manual_subsequent_pages as
(
    select
    manual_id,
    generate_subscripts(manual_page_list, 1) as page_index,
    cast(unnest(manual_page_list) as int) as page_number,
    manual_page_list[page_index + 1:] as subsequent_page_number_list
    from manual_lists
), manual_ordering as 
(
    select
    manual_id,
    page_number,
    cast(unnest(subsequent_page_number_list) as int) as subsequent_page_number
    from manual_subsequent_pages
), failing_manual_ids as
(
    select
    distinct(manual_id)
    from manual_ordering M
    inner join order_instructions I
    on M.subsequent_page_number = I.page_before and M.page_number = I.page_after
), passing_manual_lists as
(
    select *
    from manual_lists 
    anti join failing_manual_ids
    using (manual_id)
), failing_manual_lists as
(
    select L.*
    from manual_lists L
    inner join failing_manual_ids F
    on L.manual_id = F.manual_id
), failing_manual_pages as
(
    select 
    manual_id,
    unnest(manual_page_list) as page_before,
    manual_page_list
    from failing_manual_lists
), failing_manual_all_orders as
(
    select 
    manual_id,
    page_before,
    unnest(manual_page_list) as page_after
    from failing_manual_pages
), failing_manual_valid_orders as
(
    select O.*
    from failing_manual_all_orders O
    inner join order_instructions I
    on O.page_before = I.page_before and O.page_after = I.page_after
), failing_manual_ordering as
(
    select distinct
            o1.manual_id,
            page_before as page_number,
            0 as page_order
        from failing_manual_valid_orders o1
        anti join (select manual_id, page_after as page_before from failing_manual_valid_orders) o2
        using (manual_id, page_before)
    union all
    select distinct
        o3.manual_id,
        page_after as page_number,
        page_order + 1 as page_order
    from failing_manual_ordering o3
    inner join 
        (select F.* from failing_manual_valid_orders F) o4
    on o3.manual_id = o4.manual_id and o3.page_number = o4.page_before
    
), failing_manual_order_indices as 
(
    select
    manual_id,
    page_number,
    max(page_order) as page_order
    from failing_manual_ordering
    group by manual_id, page_number
), fixed_failing_manuals as
(
    select 
    manual_id, 
    list(page_number order by page_order) as page_number_list
    from failing_manual_order_indices
    group by manual_id
    order by manual_id
)

select * from fixed_failing_manuals