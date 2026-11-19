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
 Seq Scan on customers  (cost=0.00..2334.00 rows=500 width=36) (actual time=0.090..31.446 rows=1.00 loops=1)
   Filter: (lower(email) = 'user42@example.com'::text)
   Rows Removed by Filter: 99999
   Buffers: shared hit=834
 Planning Time: 0.434 ms
 Execution Time: 31.549 ms
```

Cause: the plan is a sequential scan that reads all 100,000 rows and removes 99,999 of them. The index on `email` stores the raw values, not `lower(email)`, so it cannot be used.

## Before and after
