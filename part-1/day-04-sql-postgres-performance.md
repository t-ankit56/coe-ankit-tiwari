# Part 1 · Day 4 — SQL Depth & PostgreSQL Performance

**Date completed:** · **Time spent:**

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

### CTEs and window functions

### Reading a query plan

### How indexes work

### Common causes of slow queries

## Exercises

### Exercise 1: Find why three slow queries are slow

See [the README](../code/part-1/day-04-slow-queries/README.md#the-three-slow-queries).

### Exercise 2: Add the right index, before and after

See [the README](../code/part-1/day-04-slow-queries/README.md#before-and-after).

### Exercise 3: Rewrite a self join with a window function

See [the README](../code/part-1/day-04-window-function/README.md).

## Reflection

## AI use

## Open questions

## Changes after review

- None yet.
