# Part 1 · Day 4 — SQL Depth & PostgreSQL Performance

**Date completed:** 2026-11-20 · **Time spent:** [fill in]

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Writes intermediate SQL with CTEs and window functions | Yes | [self_join.sql](../code/part-1/day-04-window-function/self_join.sql) (CTE), [window.sql](../code/part-1/day-04-window-function/window.sql) (`LAG() OVER`) |
| Reads a query plan with EXPLAIN ANALYZE | Yes | [Q1 to Q3 plans](../code/part-1/day-04-slow-queries/README.md#the-three-slow-queries) |
| Explains when an index can be used | Yes | [Q1 and the index](../code/part-1/day-04-slow-queries/README.md#q1-a-function-on-an-indexed-column), [Decisions](../code/part-1/day-04-slow-queries/README.md#decisions) |
| Names common causes of slow queries | Yes | [Q1, Q2 and Q3 causes](../code/part-1/day-04-slow-queries/README.md#the-three-slow-queries) |
| Shows before and after evidence for an optimisation | Yes | [Q2 before and after](../code/part-1/day-04-slow-queries/README.md#before-and-after) |

## Key learnings

### Joins, grouping and subqueries

A join pairs rows, a subquery computes one value for another query. A correlated subquery runs once per outer row, which is why my self join ran its subquery 38,686 times.

### CTEs and window functions

A CTE names a step so the query reads top to bottom. A window function like `LAG() OVER (PARTITION BY ... ORDER BY ...)` looks at neighbouring rows without joining the table to itself, so the table is read once.

### Reading a query plan

`EXPLAIN ANALYZE` runs the query and shows the real scan type, rows removed by the filter, buffers and time. I compared those, not the `cost=` numbers. The plan can also surprise: Q2 was a parallel seq scan, not a plain one.

### How indexes work

An index is a sorted copy of one column's values. A query can use it only when it asks for those values in the same form: `lower(email)` could not use the index on `email`, and a `customer_id` index does not give the order of `created_at`.

### Common causes of slow queries

The three I hit: a function on an indexed column (Q1), a foreign key with no index (Q2), and reading and sorting a whole table to return a few rows (Q3).

## Exercises

### Exercise 1: Find why three slow queries are slow

See [the README](../code/part-1/day-04-slow-queries/README.md#the-three-slow-queries).

### Exercise 2: Add the right index, before and after

See [the README](../code/part-1/day-04-slow-queries/README.md#before-and-after).

### Exercise 3: Rewrite a self join with a window function

See [the README](../code/part-1/day-04-window-function/README.md).

## Reflection

Before this day I would have said "add an index" and stopped. Now I would first read the plan to see what the query is actually doing, then show the plan and timing before and after the change, as Q2 does (44.3 ms to 0.34 ms). I would also check that the index fits the query, since one index fixed Q2 and did nothing for Q1 or Q3. [This part is drafted by Claude. Replace it with which of your own past query optimisations you would now explain differently.]

## AI use

I used Claude Code (Sonnet 5.5) for this day. It wrote the spec, the SQL files, ran the queries and saved the plans, and wrote both READMEs and the notes. I asked for the spec first, committed one step at a time, and checked that it followed the Day 5 to 7 spec format. I chose Q3 as the third query because the curriculum does not name one. Claude also drafted the key learnings, the reflection and the open questions from this day's results. [Edit this paragraph to say what you checked and what you changed.]

## Open questions

- Would an index on `created_at` fix Q3, and would it still help when the query also filters by status?
- Would an index on `lower(email)` turn Q1 into an index scan, and how much would the write cost go up?
- How much of the Q2 "before" time was disk reads? The second run still read 15,658 buffers.

## Changes after review

- None yet.
