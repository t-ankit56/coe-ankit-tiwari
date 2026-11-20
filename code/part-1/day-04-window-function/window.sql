-- For each order of customers 1 to 1000, the same customer's previous order amount.
WITH picked AS (
    SELECT id, customer_id, amount, created_at
    FROM orders
    WHERE customer_id <= 1000
)
SELECT id, customer_id, amount,
       LAG(amount) OVER (PARTITION BY customer_id ORDER BY created_at, id) AS prev_amount
FROM picked;
