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

## Before and after
