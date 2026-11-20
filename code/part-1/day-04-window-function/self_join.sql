-- For each order of customers 1 to 1000, the same customer's previous order amount.
WITH picked AS NOT MATERIALIZED (
    SELECT id, customer_id, amount, created_at
    FROM orders
    WHERE customer_id <= 1000
)
SELECT o.id, o.customer_id, o.amount, p.amount AS prev_amount
FROM picked AS o
LEFT JOIN picked AS p
       ON p.id = (SELECT p2.id
                  FROM picked AS p2
                  WHERE p2.customer_id = o.customer_id
                    AND (p2.created_at, p2.id) < (o.created_at, o.id)
                  ORDER BY p2.created_at DESC, p2.id DESC
                  LIMIT 1);
