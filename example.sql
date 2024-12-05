WITH 
-- Regular CTE
RegularCTE AS (
    SELECT column1, column2
    FROM table_name
    WHERE condition
),
-- Recursive CTE
RECURSIVE RecursiveCTE AS (
    -- Base query (anchor member)
    SELECT column1, column2
    FROM another_table
    WHERE base_condition
    UNION ALL
    -- Recursive query (recursive member)
    SELECT t.column1, r.column2
    FROM RecursiveCTE r
    JOIN another_table t ON r.some_column = t.other_column
    WHERE recursive_condition
)
-- Final query
SELECT *
FROM RegularCTE
JOIN RecursiveCTE ON RegularCTE.some_column = RecursiveCTE.other_column;
