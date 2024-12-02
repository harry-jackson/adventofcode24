# Python code to run SQL in duckdb and display the result.

# Run from terminal like this:
# python run_sql.py day01.sql

# Requires duckdb, which can be installed like this:
# pip install -U duckdb

import duckdb
from sys import argv

with open(argv[1], 'r') as f:
    sql_code = ''.join(f.readlines())

print(duckdb.sql(sql_code))