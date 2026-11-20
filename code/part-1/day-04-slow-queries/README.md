# Day 4 — Slow queries with EXPLAIN ANALYZE

## Setup

The database is `coe_day04`. `seed.sql` creates `customers` (100,000 rows) and `orders` (2,000,000 rows). The only indexes are the primary keys and a plain index on `customers.email`.

```
psql -d coe_day04 -f seed.sql
```

## The three slow queries

Each plan is `EXPLAIN (ANALYZE, BUFFERS)`. Every query is run once to warm the cache and the second run is recorded. The plans are saved in [plans/](plans/).

### Q1: a function on an indexed column

```sql
SELECT * FROM customers WHERE lower(email) = 'user42@example.com';
```

```
                                                 QUERY PLAN                                                  
-------------------------------------------------------------------------------------------------------------
 Seq Scan on customers  (cost=0.00..2334.00 rows=500 width=36) (actual time=0.090..31.446 rows=1.00 loops=1)
   Filter: (lower(email) = 'user42@example.com'::text)
   Rows Removed by Filter: 99999
   Buffers: shared hit=834
 Planning:
   Buffers: shared hit=87
 Planning Time: 0.434 ms
 Execution Time: 31.549 ms
(8 rows)
```

Cause: the plan is a sequential scan that reads all 100,000 rows and removes 99,999 of them. The index on `email` stores the raw values, not `lower(email)`, so it cannot be used.

### Q2: no index on a foreign key

```sql
SELECT * FROM orders WHERE customer_id = 4242;
```

```
                                                       QUERY PLAN                                                       
------------------------------------------------------------------------------------------------------------------------
 Gather  (cost=1000.00..27640.77 rows=21 width=33) (actual time=2.648..44.173 rows=24.00 loops=1)
   Workers Planned: 2
   Workers Launched: 2
   Buffers: shared hit=564 read=15658
   ->  Parallel Seq Scan on orders  (cost=0.00..26638.67 rows=9 width=33) (actual time=2.121..38.289 rows=8.00 loops=3)
         Filter: (customer_id = 4242)
         Rows Removed by Filter: 666659
         Buffers: shared hit=564 read=15658
 Planning:
   Buffers: shared hit=69
 Planning Time: 0.414 ms
 Execution Time: 44.264 ms
(12 rows)
```

Cause: `orders.customer_id` has no index, so Postgres scans the whole table, in parallel with two workers. It reads about 2,000,000 rows and removes all but 24 of them. Only about 8 rows per worker survive the filter.

### Q3: sorting the whole table for a few rows

```sql
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20;
```

```
                                                                  QUERY PLAN                                                                  
----------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=47730.05..47732.38 rows=20 width=33) (actual time=95.220..98.148 rows=20.00 loops=1)
   Buffers: shared hit=1204 read=15094
   ->  Gather Merge  (cost=47730.05..280662.89 rows=1999999 width=33) (actual time=95.217..98.141 rows=20.00 loops=1)
         Workers Planned: 2
         Workers Launched: 2
         Buffers: shared hit=1204 read=15094
         ->  Sort  (cost=46730.02..48813.36 rows=833333 width=33) (actual time=91.287..91.289 rows=16.00 loops=3)
               Sort Key: created_at DESC
               Sort Method: top-N heapsort  Memory: 27kB
               Buffers: shared hit=1204 read=15094
               Worker 0:  Sort Method: top-N heapsort  Memory: 27kB
               Worker 1:  Sort Method: top-N heapsort  Memory: 27kB
               ->  Parallel Seq Scan on orders  (cost=0.00..24555.33 rows=833333 width=33) (actual time=0.197..34.238 rows=666666.67 loops=3)
                     Buffers: shared hit=1128 read=15094
 Planning:
   Buffers: shared hit=89
 Planning Time: 0.642 ms
 Execution Time: 98.232 ms
(18 rows)
```

Cause: there is no index on `created_at`, so Postgres reads all 2,000,000 rows (about 666,667 per process) and sorts them to keep 20. The sort is a top-N heapsort, so it uses little memory, but every row is still read.

## Before and after

The index is in [indexes.sql](indexes.sql). It is not part of `seed.sql`, so the "before" state can be rebuilt by reloading the seed. Q2 is the query, and the plans are [plans/q2.txt](plans/q2.txt) (before) and [plans/q2-after.txt](plans/q2-after.txt) (after). Both are second runs.

| | Before | After |
| --- | --- | --- |
| Scan type | Parallel Seq Scan (2 workers) | Bitmap Index Scan, then Bitmap Heap Scan |
| Rows removed by filter | 666,659 per worker | none (no filter step) |
| Buffers | hit=564 read=15658 | hit=27 |
| Execution time | 44.264 ms | 0.340 ms |

The same 24 rows come back. The query went from reading the whole table to reading 24 heap blocks and 3 index blocks.

This index does not help Q1 or Q3. Q1 is on `customers`, and the `orders` index is on a different table and column. Q3 sorts by `created_at`, and an index on `customer_id` does not give that order.

## Decisions

| Question | Decision |
| --- | --- |
| Why `EXPLAIN (ANALYZE, BUFFERS)` and not plain `EXPLAIN`? | Plain `EXPLAIN` only estimates. `ANALYZE` runs the query and shows real rows and time, and `BUFFERS` shows how much data it read. |
| Why can the plain index on `email` not serve `lower(email)`? | The index stores the raw values, not the lowered ones. An index on `lower(email)` would be needed. |
| Why index `orders.customer_id`? | Postgres does not index foreign keys automatically, and Q2 read the whole table. |
| Why compare the second run? | The first run warms the cache, which would make the "before" look worse than it is. The second Q2 run still read buffers from disk, so the cache was only partly warm (see `NOTES.md`). |
| Why restrict the window function exercise to some customers? | A self join over 2,000,000 rows would take too long to show anything. |
