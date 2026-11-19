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

The plan scans `orders` twice, once for each side of the join, and runs the subquery 38,686 times, each time looking up the customer's earlier orders through the index. Execution time is 523.101 ms.


## Window function

[window.sql](window.sql) reads the same customers once and uses `LAG(amount) OVER (PARTITION BY customer_id ORDER BY created_at, id)`. It has the same filter and the same tie-break on `id`. The plan is [plans/window.txt](plans/window.txt), the second run.

```
                                                                       QUERY PLAN                                                                       
--------------------------------------------------------------------------------------------------------------------------------------------------------
 WindowAgg  (cost=19256.61..19765.71 rows=22627 width=58) (actual time=40.727..49.501 rows=19843.00 loops=1)
   Window: w1 AS (PARTITION BY orders.customer_id ORDER BY orders.created_at, orders.id)
   Storage: Memory  Maximum Storage: 17kB
   Buffers: shared hit=11498
   ->  Sort  (cost=19256.61..19313.17 rows=22627 width=26) (actual time=40.705..41.851 rows=19843.00 loops=1)
         Sort Key: orders.customer_id, orders.created_at, orders.id
         Sort Method: quicksort  Memory: 1699kB
         Buffers: shared hit=11498
         ->  Bitmap Heap Scan on orders  (cost=267.79..17620.02 rows=22627 width=26) (actual time=5.299..28.776 rows=19843.00 loops=1)
               Recheck Cond: (customer_id <= 1000)
               Heap Blocks: exact=11467
               Buffers: shared hit=11489
               ->  Bitmap Index Scan on orders_customer_id_idx  (cost=0.00..262.13 rows=22627 width=0) (actual time=2.855..2.856 rows=19843.00 loops=1)
                     Index Cond: (customer_id <= 1000)
                     Index Searches: 1
                     Buffers: shared hit=22
 Planning:
   Buffers: shared hit=121
 Planning Time: 0.556 ms
 Execution Time: 50.930 ms
(20 rows)
```

## Comparison

| | Self join | Window function |
| --- | --- | --- |
| Scans of `orders` | 2, plus a subquery run 38,686 times | 1 |
| Main node | Hash Left Join with a correlated subplan | Sort, then WindowAgg |
| Buffers | hit=942,405 | hit=11,498 |
| Execution time | 523.101 ms | 50.930 ms |

Both return 19,843 rows. I checked with `EXCEPT` in both directions, and each returned 0 rows, so the results are the same. That check was a one-off and its output is not saved. The window function is about ten times faster here because it reads each order once and looks at the neighbouring row in the sorted partition, while the self join looks the previous order up again for every row.
