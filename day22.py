from typing import List
import numpy as np
import polars as pl

def mix(n: int, mixture: int) -> int:
    return n ^ mixture

def prune(n: int) -> int:
    return n % 16777216

def next_secret_number(n: int) -> int:
    n = mix(n, n * 64)
    n = prune(n)

    n = mix(n, n // 32)
    n = prune(n)

    n = mix(n, n * 2048)
    n = prune(n)

    return n

def nth_secret_number(initial_number: int, n: int) -> int:
    res = initial_number
    for _ in range(n):
        res = next_secret_number(res)

    return res

def secret_numbers_up_to_n(initial_number: int, n: int) -> List[int]:
    res = [initial_number]
    for _ in range(n):
        res.append(next_secret_number(res[-1]))

    return res

def secret_number_df(v: List[int], i: int) -> pl.DataFrame:
    df = pl.DataFrame({'id': i, 'n': v}).with_columns(price = pl.col('n') % 10).with_columns(d_price = pl.col('price').diff())
    for lag in range(1, 4):
        df = df.with_columns(pl.col('d_price').shift(lag).alias(f'd_price_lag_{lag}'))

    df = df.drop_nulls()
    return df

initial_numbers = [int(line.strip()) for line in open('data/day22.txt', 'r')]

part_1 = sum([nth_secret_number(initial_number, 2000) for initial_number in initial_numbers])

# Data frame with all 2000 secret numbers generated from each initial number, along with the lagged price changes
df = pl.concat([secret_number_df(secret_numbers_up_to_n(initial_number, 2000), i) for i, initial_number in enumerate(initial_numbers)])

lagged_price_cols = ['d_price_lag_3', 'd_price_lag_2', 'd_price_lag_1', 'd_price']

# All sequences of 4 price changes
sequence_df = df.select(lagged_price_cols).unique().with_columns(sequence_id = pl.col('d_price').cum_count())

# For each price change sequence, this join adds the price information
filtered_df = df.join(sequence_df, on = lagged_price_cols, how = 'inner')

# For each initial number we only want the first match for the price sequence
filtered_df = filtered_df.with_columns(r = pl.col('d_price').cum_count().over('sequence_id', 'id')).filter(pl.col('r') == 1)

# add up the total price attained by each sequence
best_prices_df = filtered_df.group_by('sequence_id').agg(pl.col('price').sum())

# maximum price for any sequence
best_price = best_prices_df['price'].max()

print(f'Part 1: {part_1}')
print(f'Part 2: {best_price}')