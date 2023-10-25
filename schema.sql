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