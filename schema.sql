DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    image TEXT NOT NULL,
    price NUMBER NOT NULL
);

DROP TABLE IF EXISTS cart;

CREATE TABLE cart (
    id INTEGER,
    quantity NUMBER,
    name TEXT,
    image TEXT,
    price NUMBER,
    subTotal NUMBER
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    totalItems NUMBER NOT NULL
);

CREATE TABLE order_details (
    order_details_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price NUMBER,
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);