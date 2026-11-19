# SQL Depth & PostgreSQL Performance in Postgres: Build Spec for Claude Code

Find why three queries are slow from their `EXPLAIN ANALYZE` plans, fix one with the right index and show the plan and timing before and after, then rewrite a self join as a window function. This is for the Day 4 assessment, so the saved plans and the commit history matter as much as the SQL. There is no runnable code and no tests. The evidence is SQL files and real plans pasted into the READMEs.

This one spec covers both projects, one per criterion group:

- `code/part-1/day-04-slow-queries/` (Exercises 1 and 2, holds `seed.sql`)
- `code/part-1/day-04-window-function/` (Exercise 3, reuses the same `seed.sql`)

## Instructions for Claude Code

**Ground rules**

1. **Always use plan mode.** Before every step, enter plan mode. The plan names the files you will write and the queries you will run. Write no files and run no queries until the user approves the plan.
2. **Never commit.** Do not run `git add`, `git commit` or any other git command that changes state. Read-only commands such as `git status` and `git diff` are fine. The user makes every commit. After each step, give a suggested commit message, then wait.
3. **One step at a time.** Stop after each step, show what changed and the suggested commit message, then wait for the user to say continue.
4. **Real numbers only.** Every plan and timing in a README is pasted from a real run and saved to a file first. Never invent, round or tidy a plan. Run each timed query once to warm the cache and record the second run, and say so in the README.
5. **Do not edit the data.** Only `seed.sql` creates data. The index goes in its own `.sql` file, never inside `seed.sql`, so the "before" state can always be rebuilt.
6. **Plain Postgres.** `psql` only. No extensions, no ORM, no tools beyond `psql`.
7. **Keep notes.** Whenever a plan changes what you expected, append one line to `NOTES.md`.
8. **Key learnings, reflection and AI use are the user's.** Do not write them in the day file.

## Scope

- A `coe_day04` database with `customers` (100,000 rows) and `orders` (2,000,000 rows), built by `seed.sql` (already written)
- Exercise 1: three slow queries, each with a saved plan and a one-line cause
- Exercise 2: one index, with the plan and timing before and after
- Exercise 3: one self join and its window function rewrite, with plans and timings

## Design

The schema is in `seed.sql`. The only indexes are the primary keys and a plain index on `customers.email`. `orders.customer_id` has no index on purpose.

| Query | SQL | Expected cause |
| --- | --- | --- |
| Q1 | `SELECT * FROM customers WHERE lower(email) = 'user42@example.com'` | A function on an indexed column, so the plain index cannot be used |
| Q2 | `SELECT * FROM orders WHERE customer_id = 4242` | No index on the foreign key column |
| Q3 | `SELECT * FROM orders ORDER BY created_at DESC LIMIT 20` | No index to give the order, so the whole table is read and sorted |

Every plan is taken with `EXPLAIN (ANALYZE, BUFFERS)`. The README compares the scan type, rows removed by the filter, and `Execution Time`.

## Folder layout

```
code/part-1/day-04-slow-queries/
  SPEC.md
  README.md
  NOTES.md
  seed.sql            # already written
  queries.sql         # Q1, Q2, Q3
  indexes.sql         # the Exercise 2 index
  plans/              # saved plan text, one file per run
code/part-1/day-04-window-function/
  README.md
  self_join.sql
  window.sql
  plans/
```

## Step 0: Setup

1. Load the seed: `psql -d coe_day04 -f seed.sql`.
2. Check the counts: 100,000 customers and 2,000,000 orders.
3. Run `\d orders` and `\d customers` and confirm the only indexes are the primary keys and `customers_email_idx`.
4. Create empty `NOTES.md` and `queries.sql`.

**Suggested commit message:** `chore: Day 4 seed data and spec`

## The steps

### Step 1: Q1, a function on an indexed column

1. Add Q1 to `queries.sql`.
2. Run it with `EXPLAIN (ANALYZE, BUFFERS)` and save the plan to `plans/q1.txt`.
3. In the README, paste the plan and write the cause in one line, from what the plan shows.

**Suggested commit message:** `docs: Q1 plan and cause`

### Step 2: Q2, a missing index on a foreign key

Same as Step 1 for Q2, saved to `plans/q2.txt`. This is the "before" plan for Exercise 2, so do not run it any other way.

**Suggested commit message:** `docs: Q2 plan and cause`

### Step 3: Q3, sorting the whole table

Same as Step 1 for Q3, saved to `plans/q3.txt`.

**Suggested commit message:** `docs: Q3 plan and cause`

### Step 4: The index, before and after

1. Write `indexes.sql`: `CREATE INDEX orders_customer_id_idx ON orders (customer_id);` then `ANALYZE orders;`.
2. Run it, then run Q2 again and save `plans/q2-after.txt`.
3. In the README, add a table of scan type, rows removed by the filter, buffers and execution time, before and after.
4. Say which of Q1 and Q3 this index does not help, and why.

**Suggested commit messages:** `feat: add index on orders.customer_id`, then `docs: Q2 before and after`

### Step 5: The self join

Task: for each order, show the same customer's previous order amount.

1. In `day-04-window-function/`, write `self_join.sql`. Restrict both sides to a fixed set of customers (`customer_id <= 1000`) so it finishes, and put that filter in a CTE.
2. Run it with `EXPLAIN (ANALYZE, BUFFERS)` and save `plans/self_join.txt`.
3. State in the README that the Exercise 2 index already exists, because it changes the cost.

**Suggested commit message:** `feat: self join for previous order amount`

### Step 6: The window function

1. Write `window.sql` with `LAG(amount) OVER (PARTITION BY customer_id ORDER BY created_at)` and the same customer filter.
2. Save its plan to `plans/window.txt`.
3. In the README, compare the two: how many times `orders` is scanned, the join or window node, and execution time.

**Suggested commit messages:** `feat: previous order amount with a window function`, then `docs: compare self join and window function`

## Decisions

Fill this table in the README once the work is done. Starting questions:

| Question | Decision |
| --- | --- |
| Why `EXPLAIN (ANALYZE, BUFFERS)` and not plain `EXPLAIN`? | Plain `EXPLAIN` only estimates. `ANALYZE` runs the query and shows real rows and time. |
| Why can the plain index on `email` not serve `lower(email)`? | The index stores the raw values, not the lowered ones. |
| Why index `orders.customer_id`? | Postgres does not index foreign keys automatically, and Q2 reads the whole table. |
| Why compare the second run? | The first run warms the cache, which would make the "before" look worse than it is. |
| Why restrict Exercise 3 to some customers? | The self join over 2,000,000 rows would take too long to run to show anything. |

## Final step: README, check and verification

Write both READMEs with the setup, the queries, the plans and the Decisions above. The Key learnings, reflection and AI use go in `part-1/day-04-sql-postgres-performance.md`, in the user's own words. Fill in the date, time spent and the evidence column in that file, and add the Day 4 row to the root `README.md` when the user says the day is finished.

**Before finishing, verify each success criterion**

| Criterion | Where it shows |
| --- | --- |
| Writes intermediate SQL with CTEs and window functions | `self_join.sql` uses a CTE and `window.sql` uses `LAG() OVER` |
| Reads a query plan with EXPLAIN ANALYZE | Q1, Q2 and Q3 plans in `plans/`, with the cause read from each |
| Explains when an index can be used | The Q1 cause (function on the column) and the Q2 index, plus the Step 4 note on what it does not help |
| Names common causes of slow queries | The three causes in the Q1, Q2 and Q3 sections |
| Shows before and after evidence for an optimisation | The Step 4 table, `plans/q2.txt` against `plans/q2-after.txt` |

Finally, confirm every plan quoted in a README exists under `plans/`, then suggest the commit message `docs: READMEs and notes`. The user commits.
