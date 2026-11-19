DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

SELECT setseed(0.42);  -- same data every run

CREATE TABLE customers (
    id         serial PRIMARY KEY,
    email      text NOT NULL,
    country    text NOT NULL,
    created_at timestamptz NOT NULL
);

CREATE TABLE orders (
    id          bigserial PRIMARY KEY,
    customer_id int NOT NULL REFERENCES customers (id),  -- deliberately no index
    status      text NOT NULL,
    amount      numeric(10, 2) NOT NULL,
    created_at  timestamptz NOT NULL
);

INSERT INTO customers (email, country, created_at)
SELECT 'User' || g || '@Example.com',
       (ARRAY['IN', 'US', 'UK', 'DE', 'AU'])[1 + floor(random() * 5)::int],
       now() - random() * interval '3 years'
FROM generate_series(1, 100000) AS g;

INSERT INTO orders (customer_id, status, amount, created_at)
SELECT 1 + floor(random() * 100000)::int,
       (ARRAY['pending', 'paid', 'shipped', 'cancelled'])[1 + floor(random() * 4)::int],
       round((random() * 500 + 5)::numeric, 2),
       now() - random() * interval '2 years'
FROM generate_series(1, 2000000);

CREATE INDEX customers_email_idx ON customers (email);  -- plain index, for the lower(email) case

ANALYZE customers;
ANALYZE orders;
