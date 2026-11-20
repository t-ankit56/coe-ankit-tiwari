-- Exercise 2: index the foreign key that Q2 filters on
CREATE INDEX orders_customer_id_idx ON orders (customer_id);
ANALYZE orders;
