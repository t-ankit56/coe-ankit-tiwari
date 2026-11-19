-- Q1: function on an indexed column
SELECT * FROM customers WHERE lower(email) = 'user42@example.com';

-- Q2: no index on a foreign key column
SELECT * FROM orders WHERE customer_id = 4242;
