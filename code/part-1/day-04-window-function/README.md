# Day 4 — Self join rewritten as a window function

## Setup

This uses the same `orders` table as the slow queries exercise. Load it with [seed.sql](../day-04-slow-queries/seed.sql).

## Self join

The task: for each order, show the same customer's previous order amount. Both versions are limited to customers 1 to 1000 (19,843 orders), because a self join over all 2,000,000 orders would take too long to be worth running. The filter is in a CTE, written `NOT MATERIALIZED` so Postgres can use an index through it. The index `orders_customer_id_idx` from the slow queries exercise already exists, and it changes the cost of this query.

[self_join.sql](self_join.sql) joins `orders` to itself. For each order, a subquery finds the id of the latest earlier order of the same customer. Ties on `created_at` are broken by `id`. The plan is [plans/self_join.txt](plans/self_join.txt), the second run.

```
                                                                             QUERY PLAN                                                                              
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Hash Left Join  (cost=18170.65..45161.98 rows=22627 width=24) (actual time=32.805..521.594 rows=19843.00 loops=1)
   Hash Cond: ((SubPlan 1) = orders_1.id)
   Buffers: shared hit=942405
   ->  Bitmap Heap Scan on orders  (cost=267.79..17620.02 rows=22627 width=26) (actual time=5.467..16.929 rows=19843.00 loops=1)
         Recheck Cond: (customer_id <= 1000)
         Heap Blocks: exact=11467
         Buffers: shared hit=11489
         ->  Bitmap Index Scan on orders_customer_id_idx  (cost=0.00..262.13 rows=22627 width=0) (actual time=2.969..2.969 rows=19843.00 loops=1)
               Index Cond: (customer_id <= 1000)
               Index Searches: 1
               Buffers: shared hit=22
   ->  Hash  (cost=17620.02..17620.02 rows=22627 width=14) (actual time=27.141..27.143 rows=19843.00 loops=1)
         Buckets: 32768  Batches: 1  Memory Usage: 1187kB
         Buffers: shared hit=11489
         ->  Bitmap Heap Scan on orders orders_1  (cost=267.79..17620.02 rows=22627 width=14) (actual time=4.945..22.955 rows=19843.00 loops=1)
               Recheck Cond: (customer_id <= 1000)
               Heap Blocks: exact=11467
               Buffers: shared hit=11489
               ->  Bitmap Index Scan on orders_customer_id_idx  (cost=0.00..262.13 rows=22627 width=0) (actual time=2.583..2.584 rows=19843.00 loops=1)
                     Index Cond: (customer_id <= 1000)
                     Index Searches: 1
                     Buffers: shared hit=22
   SubPlan 1
     ->  Limit  (cost=8.46..8.47 rows=1 width=16) (actual time=0.012..0.012 rows=0.97 loops=38686)
           Buffers: shared hit=919427
           ->  Sort  (cost=8.46..8.47 rows=1 width=16) (actual time=0.012..0.012 rows=0.97 loops=38686)
                 Sort Key: orders_2.created_at DESC, orders_2.id DESC
                 Sort Method: top-N heapsort  Memory: 25kB
                 Buffers: shared hit=919427
                 ->  Index Scan using orders_customer_id_idx on orders orders_2  (cost=0.43..8.45 rows=1 width=16) (actual time=0.003..0.010 rows=10.13 loops=38686)
                       Index Cond: ((customer_id <= 1000) AND (customer_id = orders.customer_id))
                       Filter: (ROW(created_at, id) < ROW(orders.created_at, orders.id))
                       Rows Removed by Filter: 11
                       Index Searches: 38686
                       Buffers: shared hit=919421
 Planning:
   Buffers: shared hit=128
 Planning Time: 0.805 ms
 Execution Time: 523.101 ms
(39 rows)
```

The plan scans `orders` twice, once for each side of the join, and also runs the subquery 38,686 times, which is a third pass over the customer's rows each time. Execution time is 523.101 ms.


## Window function
