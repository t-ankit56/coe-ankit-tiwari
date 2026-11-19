# Day 4 — Slow queries with EXPLAIN ANALYZE

## Setup

The database is `coe_day04`. `seed.sql` creates `customers` (100,000 rows) and `orders` (2,000,000 rows). The only indexes are the primary keys and a plain index on `customers.email`.

```
psql -d coe_day04 -f seed.sql
```

## The three slow queries

## Before and after
